import copy
import json
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from family_conversion_diagnostics import build_diagnostics, bind_to_trace, settle_diagnostics, forward_status, _sha
from test_family_conversion_diagnostics import request


def fixture():
    req=request()
    req.update(race_id='KM-LOCAL-OHI-20990101-R01',oos_eligible=True,acceptance_only=False)
    tickets={'tickets':[
        {'bet_type':'TRIO','selection':[7,2,8],'stake':100},
        {'bet_type':'EXACTA','selection':[7,2],'stake':100},
        {'bet_type':'TRIFECTA','selection':[7,2,6],'stake':100},
    ]}
    d=build_diagnostics(req,tickets,req['static_prediction'],{},'2099-01-01T11:00:00+09:00','basis')
    fin={'artifact':{'race_id':req['race_id'],'ticket_transport_trace':bind_to_trace({},d)},
         'receipt':{'phase':'FINAL','status':'PASS'},'receipt_sha256':'signed-final'}
    result={'race_id':req['race_id'],'finish_order':[7,2,8],
            'result_available_at':'2099-01-01T12:05:00+09:00',
            'payouts':{'TRIO':200,'EXACTA':100,'TRIFECTA':1000}}
    authority={'status':'PASS','verified_signed_result':True,'verification_ref':'official',
               'result_receipt_sha256':'signed-result','result_artifact_sha256':'result'}
    return req,d,fin,result,authority


def settle(d,fin,result,authority):
    return settle_diagnostics(d,fin,result,authority,final_signature_verified=True)


def test_paired_arms_settlement_and_no_production_mutation():
    req,d,fin,result,auth=fixture(); before=copy.deepcopy(fin)
    out=settle(d,fin,result,auth)
    assert fin==before
    assert out['oos_eligible']
    assert out['arms']['SET_ONLY']['investment']==100
    assert out['arms']['SET_PAIR']['investment']==200
    assert out['arms']['SELECTIVE_EXACT']['return']==1300
    assert out['first_failure']=='EXACT_CONTINUITY'
    assert out['diagnostic_outcomes']['selective_exact_hit']
    assert d['forward_arms']['PRODUCTION_BASELINE_R3']['tickets']==[
        {'bet_type':'TRIO','selection':[7,2,8],'stake':100},
        {'bet_type':'EXACTA','selection':[7,2],'stake':100},
        {'bet_type':'TRIFECTA','selection':[7,2,6],'stake':100}]


def test_structural_exclusions_override_protection_and_purchased_exacts_obey_same_selector():
    req,d,fin,result,auth=fixture()
    req['third_dispositions']=[{'head':7,'second':2,'third':8,'status':'EXCLUDE','reason':'STRUCTURAL_HARD'}]
    d=build_diagnostics(req,{'tickets':[{'bet_type':'TRIFECTA','selection':[7,2,6],'stake':100}]},req['static_prediction'],{},'2099-01-01T11:00:00+09:00','basis')
    exacts=[t['selection'] for t in d['forward_arms']['SELECTIVE_EXACT']['tickets'] if t['bet_type']=='TRIFECTA']
    assert [7,2,8] not in exacts
    assert [7,2,6] in exacts
    assert all(x['exact']!=[7,2,6] for x in d['selective_exact_candidates'])


@pytest.mark.parametrize('change',['acceptance','disabled','late','historical','unverified','missing_payout'])
def test_ineligible_never_credits_oos(change):
    req,d,fin,result,auth=fixture()
    if change=='acceptance':result['acceptance_only']=True
    if change=='disabled':d['request_oos_allowed']=False
    if change=='late':d['generated_at']='2099-01-01T12:01:00+09:00'
    if change=='historical':
        d['generated_at']='2026-10-05T11:00:00+09:00'
        d['scheduled_post_at']='2026-10-05T12:00:00+09:00'
        result['result_available_at']='2026-10-05T12:05:00+09:00'
    if change=='unverified':auth['verified_signed_result']=False
    if change=='missing_payout':result['payouts'].pop('TRIFECTA')
    d['sha256']=_sha({k:v for k,v in d.items() if k!='sha256'})
    fin['artifact']['ticket_transport_trace']=bind_to_trace({},d)
    assert not settle(d,fin,result,auth)['oos_eligible']


def test_signature_identity_and_content_tamper_fail_closed():
    req,d,fin,result,auth=fixture()
    with pytest.raises(AssertionError,match='SIGNATURE_UNVERIFIED'):
        settle_diagnostics(d,fin,result,auth)
    bad=copy.deepcopy(result);bad['race_id']='other'
    with pytest.raises(AssertionError,match='RACE_ID_MISMATCH'):settle(d,fin,bad,auth)
    d['forward_arms']['SET_ONLY']['tickets'][0]['stake']=999
    with pytest.raises(AssertionError,match='CONTENT_HASH_MISMATCH'):settle(d,fin,result,auth)


def test_fixed_cohort_normalization_drawdown_and_gates(tmp_path):
    req,d,fin,result,auth=fixture()
    row=settle(d,fin,result,auth)
    for i in range(31):
        r=copy.deepcopy(row);r['race_id']=str(i);r['generated_at']=f'2099-01-{1+i//10:02d}T11:{i%10:02d}:00+09:00'
        r['sha256']=_sha({k:v for k,v in r.items() if k!='sha256'})
        (tmp_path/f'{i}.json').write_text(json.dumps(r))
    status=forward_status(str(tmp_path))
    assert status['eligible_races']==30
    assert status['first_failure_counts']=={'EXACT_CONTINUITY':30}
    assert status['normalized_comparison']['equal_budget_aggregates']['SET_ONLY']['investment']==3000
    assert status['normalized_comparison']['equal_ticket_aggregates']['SELECTIVE_EXACT']['ticket_count_total']==30
    assert status['promotion_gate']['SET_ONLY']['decision']=='REVIEW_ELIGIBLE'
    assert not status['automatic_promotion']
    assert all(x['explicit_promotion_declaration_required'] for x in status['promotion_gate'].values())
    (tmp_path/'corrupt.json').write_text('{}')
    assert not forward_status(str(tmp_path))['promotion_gate']['SET_ONLY']['checks']['no_integrity_holds']


def test_authority_inheritance_and_existing_arms_untouched():
    old=json.loads((ROOT/'profiles/KM_FAMILY_CURRENT_AUTHORITY_20261005_R40.json').read_text())
    new=json.loads((ROOT/'profiles/KM_FAMILY_CURRENT_AUTHORITY_20261006_R41.json').read_text())
    assert new['predecessor']==old['manifest_id']
    assert new['family_scoped_authority']==old['family_scoped_authority']
    for k in ('mec','capital_policy'):assert new['common_family_components'][k]==old['common_family_components'][k]
    from local_mec_r5_shadow import ARM_ORDER
    assert ARM_ORDER==['SET_ONLY','SET_PAIR']+[f'SET_PAIR_EXACT_TOP{k}' for k in range(3,9)]


def test_result_runner_persists_retry_and_holds_conflicting_rewrite(tmp_path,monkeypatch):
    req,d,fin,result,auth=fixture()
    monkeypatch.chdir(tmp_path)
    (tmp_path/'runtime_result_in').mkdir();(tmp_path/'runtime_out').mkdir()
    (tmp_path/'runtime_result_in/family_conversion_diagnostics_pre_result.json').write_text(json.dumps(d))
    # Exercise the actual RESULT hook with the signature/result authority
    # already verified by the existing upstream lifecycle.
    source=(ROOT/'runtime/local_result_from_signed_final.py').read_text()
    block=source.split('# Reuse the signed RESULT authority and existing persistence lifecycle.\n',1)[1].split('# LOCAL-specific MEC-R5 candidate',1)[0]
    context={'json':json,'fin':fin,'req':result,'rid':result['race_id'],
             'shared_result_authority':auth,'final_ver':{'verified':True}}
    exec(compile(block,'conversion_result_hook','exec'),context)
    target=tmp_path/'runtime/family_conversion_measurements'/f"{result['race_id']}.json"
    first=target.read_bytes()
    assert json.loads(first)['oos_eligible']
    exec(compile(block,'conversion_result_hook','exec'),context)
    assert target.read_bytes()==first
    result['payouts']['TRIO']=999
    exec(compile(block,'conversion_result_hook','exec'),context)
    assert target.read_bytes()==first
    failure=json.loads((tmp_path/'runtime_out/family_conversion_failure.json').read_text())
    assert 'IMMUTABLE_MEASUREMENT_CONFLICT' in failure['error']
