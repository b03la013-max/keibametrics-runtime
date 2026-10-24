"""Replay existing race records offline; never create a pre-race prediction."""
from copy import deepcopy
import base64
import gzip
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime')]
from jra_candidate_postresult_closedloop import verify_official_result
from jra_production_postresult import build_settlement_correction, settle_final, verify_final
from jra_same_day_results import parse_result_detail
from source_acquisition import _decode, _html_text
from jra_production_no_bet_terminal import verify_no_bet_terminal
from jra_role_learning_shadow import build_shadow, digest
from post_result_learning import build_post_result_review


def read(relative):
    return json.loads((ROOT/relative).read_text())


def test_existing_33_frozen_final_settlements_reproduce_original_series():
    paths=sorted((ROOT/'runtime/final_artifacts').glob('*20261024*.json'))
    assert len(paths)==33
    for path in paths:
        raw=path.read_bytes();final=json.loads(raw);verify_final(final)
        result=read('runtime/results/'+path.name)
        before=deepcopy(result)
        replay=settle_final(final,result['official_result'])
        for key in ('total_investment','total_payout','refund','profit_loss','pfs'):
            assert replay[key]==pytest.approx(result['settlement'][key]),(path.name,key)
        assert replay['actual_pfs_status']=='NOT_VERIFIED'
        assert path.read_bytes()==raw and result==before


def test_existing_stored_review_hashes_remain_exact():
    paths=sorted((ROOT/'runtime/reviews_auto').glob('*20261024*AUTO.json'))
    assert len(paths)>=13
    for path in paths:
        old=json.loads(path.read_bytes());rid=old['race_id']
        result=read('runtime/results/'+rid+'.json')
        final=read('runtime/final_artifacts/'+rid+'.json')
        assert build_post_result_review(result,final)['sha256']==old['sha256'],rid


def test_kyoto_7_refund_comes_from_existing_exact_official_bytes():
    rid='KM-JRA-KYO-20261024-R07'
    final=read('runtime/final_artifacts/'+rid+'.json')
    original=read('runtime/results/'+rid+'.json')
    snapshot=read('runtime/executions/KM-JRA-KYO-20261024-R11-LIVE-R1/SOURCE/runs/40067122397/source_receipt_envelope.json')
    sources=[s for s in snapshot['artifact']['sources'] if s.get('source_id')=='JRA-OFFICIAL-SAME-DAY-R07-DETAIL']
    assert len(sources)==1
    source=sources[0]
    raw=gzip.decompress(base64.b64decode(source['raw_gzip_b64']))
    assert hashlib.sha256(raw).hexdigest()==source['raw_sha256']=='931013bf8357cfa410c1d5dd549b6873ef1e51513eb99abd04e4ee0dc89b9685'
    parsed=parse_result_detail(raw,source['content_type'])
    universe=[str(r['horse_no']) for r in parsed['runners']+parsed['non_finishers']]
    official=verify_official_result(parsed,_html_text(_decode(raw,source['content_type'])),universe)
    assert official['refund_runner_ids']==[7]
    assert official['non_finishers'][0]['finish_status']=='EXCLUDED'
    assert official['non_finishers'][0]['horse_name']=='リーチグローリー'
    evidence={'sha256':source['raw_sha256'],'url':source['final_url'],'captured_at':source['fetched_at']}
    correction=build_settlement_correction(final,original,official,evidence,
                                          audited_at='2026-10-24T09:00:00+00:00')
    s=correction['corrected_settlement']
    assert len(s['refunded_tickets'])==12 and len(s['winning_tickets'])==1
    assert (s['total_investment'],s['refund'],s['effective_investment'],s['total_payout'],s['profit_loss'])==(1500,1200,300,2000,1700)
    assert s['pfs']==pytest.approx(666.6666666666666)
    assert correction['original_settlement']['refund']==0
    assert correction['signed_result_correction']=='NOT_ISSUED'
    assert read('runtime/results/'+rid+'.json')==original


def test_three_aki_no_bet_decisions_are_zero_exposure_and_separate_from_final():
    paths=sorted((ROOT/'runtime/jra_no_bet_terminals').glob('*20261024*.json'))
    assert len(paths)==3
    ids=[]
    for path in paths:
        terminal=json.loads(path.read_bytes())
        verify_no_bet_terminal(terminal,require_live=True)
        ids.append(terminal['race_id'])
        assert terminal['total_investment']==0 and terminal['tickets']==[]
        assert terminal['decision_reason'].startswith('AKI_')
        assert not (ROOT/'runtime/final_artifacts'/(terminal['race_id']+'.json')).exists()
    assert set(ids)=={'KM-JRA-NGT-20261024-R01','KM-JRA-KYO-20261024-R04','KM-JRA-TKY-20261024-R05'}


def test_legacy_static_barrier_is_not_misread_as_computation_clock():
    rid='KM-JRA-TKY-20261018-R10'
    request=read('runtime/requests/'+rid+'-LIVE-R1-FORMAL.json')
    final=read('runtime/final_artifacts/'+rid+'.json')
    final['static_freeze_timestamp']=request['prediction_cutoff']
    final['sha256']=digest({k:v for k,v in final.items() if k!='sha256'})
    shadow=build_shadow(request,final,observed_at=final['final_freeze_timestamp'])
    assert shadow['oos_eligible'] is False
    request['static_computed_at']=request['prediction_cutoff']
    with pytest.raises(ValueError,match='COMPUTATION_CHRONOLOGY_INVALID'):
        build_shadow(request,final,observed_at=final['final_freeze_timestamp'])
