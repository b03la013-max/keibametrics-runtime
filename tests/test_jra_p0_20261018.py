"""Race intake and observed LOCAL failure modes, without changing prediction policy."""
from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime')]
from jra_race_day_registration import build_registrations, persist_registrations, verify_registration
from jra_race_day_autopilot import tick, request_postresult_worker
from jra_official_pdf import apply_official_detail_status
from jra_autopilot_start import resolve_start
from jra_delivery import signed_payload, verify_signed_final, build_publication, canonical_bytes
from jra_production_postresult import _sha, settle_final, ProductionPostResultError


def cohort():
    discovery=json.loads((ROOT/'evidence/jra_p0_20261018/official_discovery.json').read_text())
    authority=json.loads((ROOT/'profiles/KM_FAMILY_CURRENT_AUTHORITY_20261012_R51.json').read_text())
    return build_registrations(discovery,authority,observed_at='2026-10-17T00:00:00+09:00')


def test_official_36_intakes_do_not_trigger_source_or_claim_execution(tmp_path):
    plan,records=cohort()
    assert persist_registrations(tmp_path,plan,records)==36
    assert sum(r['planned_required_cells'] for r in records.values())==9000
    assert sum(r['executed_cells'] for r in records.values())==0
    assert not (tmp_path/'runtime/jra_formal_intents').exists()
    assert {r['runner_universe_status'] for r in records.values()}=={'PENDING_OFFICIAL_PDF'}
    assert len(plan['cohort']['race_ids'])==36
    r=next(iter(records.values()))
    verify_registration(r,plan,race_id=r['race_id'],official_post=datetime.fromisoformat(r['intake_intent']['scheduled_post_at']))
    r['executed_cells']=20
    with pytest.raises(ValueError,match='HASH_MISMATCH'):
        verify_registration(r,plan,race_id=r['race_id'],official_post=datetime.now().astimezone())


def small_plan(root):
    path=root/'runtime/jra_race_day_plan/2026-10-18.json';path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'entries':[{'venue':'東京','races':[1,2]}]}))


def test_dispatch_claim_published_before_send_and_timeout_does_not_duplicate(tmp_path):
    small_plan(tmp_path);events=[]
    statefile=tmp_path/'runtime/jra_race_day_plan/2026-10-18.state.json'
    def publish():
        state=json.loads(statefile.read_text());events.append(('publish',len(state)))
    def send(*args):
        state=json.loads(statefile.read_text())
        rid=f'KM-JRA-TKY-20261018-R{args[1]:02}'
        assert state[rid]['dispatch_state']=='CLAIMED_NOT_ACKNOWLEDGED'
        events.append(('send',args[1]))
        if args[1]==1:raise subprocess.TimeoutExpired('gh',30)
        return {'returncode':0}
    opts=dict(resolve=lambda *args:('meeting',[{'race_no':i,'post_time':'10:00'} for i in [1,2]]),dispatch=send,publish=publish)
    when=datetime.fromisoformat('2026-10-18T09:10:00+09:00')
    tick(tmp_path,'2026-10-18',when,**opts)
    tick(tmp_path,'2026-10-18',when,**opts)
    assert [x for x in events if x[0]=='send']==[('send',1),('send',2)]
    state=json.loads(statefile.read_text())
    assert state['KM-JRA-TKY-20261018-R01']['dispatch_state']=='HOLD_AMBIGUOUS_DISPATCH_NO_AUTOMATIC_RETRY'
    assert state['KM-JRA-TKY-20261018-R02']['dispatch_state']=='DISPATCH_ACKNOWLEDGED'


def test_unpublished_claim_cannot_send(tmp_path):
    small_plan(tmp_path)
    def publish():raise OSError('offline')
    out=tick(tmp_path,'2026-10-18',datetime.fromisoformat('2026-10-18T09:10:00+09:00'),
             resolve=lambda *args:('meeting',[{'race_no':i,'post_time':'10:00'} for i in [1,2]]),
             dispatch=lambda *args:pytest.fail('unpublished dispatch'),publish=publish)
    assert {r['status'] for r in out}=={'CLAIM_PUBLISH_FAILED_NO_SEND'}


def test_failed_before_dispatch_retries_in_window_but_ambiguous_claim_does_not(tmp_path):
    small_plan(tmp_path)
    when=datetime.fromisoformat('2026-10-18T09:10:00+09:00')
    options=dict(resolve=lambda *args:('meeting',[{'race_no':i,'post_time':'10:00'} for i in [1,2]]))
    def offline():raise OSError('claim not published; dispatch not called')
    tick(tmp_path,'2026-10-18',when,publish=offline,
         dispatch=lambda *args:pytest.fail('unpublished dispatch'),**options)
    sent=[]
    tick(tmp_path,'2026-10-18',when,publish=lambda:None,dispatch=lambda *args:sent.append(args),**options)
    assert len(sent)==2
    tick(tmp_path,'2026-10-18',when,publish=lambda:None,
         dispatch=lambda *args:pytest.fail('duplicate dispatch'),**options)
    state=tmp_path/'runtime/jra_race_day_plan/2026-10-18.state.json'
    d=json.loads(state.read_text())
    for value in d.values():
        value.pop('dispatched_at',None)
        value['dispatch_state']='CLAIMED_NOT_ACKNOWLEDGED'
    state.write_text(json.dumps(d))
    tick(tmp_path,'2026-10-18',when,publish=lambda:None,
         dispatch=lambda *args:pytest.fail('ambiguous dispatch must not retry'),**options)


def test_failed_before_dispatch_never_retries_after_window(tmp_path):
    small_plan(tmp_path)
    state=tmp_path/'runtime/jra_race_day_plan/2026-10-18.state.json'
    state.write_text(json.dumps({'KM-JRA-TKY-20261018-R01':{'dispatch_state':'CLAIM_PUBLISH_FAILED_NO_SEND'}}))
    out=tick(tmp_path,'2026-10-18',datetime.fromisoformat('2026-10-18T09:50:00+09:00'),
             resolve=lambda *args:('meeting',[{'race_no':i,'post_time':'10:00'} for i in [1,2]]),
             publish=lambda:None,dispatch=lambda *args:pytest.fail('late dispatch'))
    assert all(x['status']=='MISSED_WINDOW' for x in out)


def test_one_corrupt_final_cannot_block_independent_result_worker(tmp_path):
    small_plan(tmp_path);p=tmp_path/'runtime/final_artifacts';p.mkdir(parents=True)
    (p/'KM-JRA-TKY-20261018-R01.json').write_text('bad json')
    (p/'KM-JRA-TKY-20261018-R02.json').write_text(json.dumps({'scheduled_post_at':'2026-10-18T10:00:00+09:00'}))
    sent=[]
    when=datetime.fromisoformat('2026-10-18T10:30:00+09:00')
    assert request_postresult_worker(tmp_path,'2026-10-18',when,publish=lambda:sent.append('claim'),send=lambda:sent.append('send'))=='ACKNOWLEDGED'
    assert sent==['claim','send']
    assert request_postresult_worker(tmp_path,'2026-10-18',when,publish=lambda:None,send=lambda:pytest.fail('repeat'))=='RECENT_RESULT_WORKER_REQUEST'


def test_official_cancel_and_exclude_preserve_declared_proof():
    rows=[{'horse_no':i,'name':f'horse{i}'} for i in [1,2,3]]
    artifact={'jra_official_runner_universe':{'runners':rows,'runner_count':3}}
    declared={'runners':[{**r,'status':s} for r,s in zip(rows,['ACTIVE','CANCELLED','EXCLUDED'])],
              'source_id':'official','source_snapshot_sha256':'f'*64}
    active={'runners':[rows[0]]}
    out=apply_official_detail_status(deepcopy(artifact),declared,active)
    assert out['jra_declared_runner_universe']['runner_count']==3
    assert out['jra_official_runner_universe']['runner_count']==1
    with pytest.raises(ValueError,match='ACTIVE_DECLARED'):
        apply_official_detail_status(deepcopy(artifact),declared,{'runners':[{**rows[0],'name':'wrong'}]})
    with pytest.raises(ValueError,match='IDENTITY_MISMATCH'):
        apply_official_detail_status(deepcopy(artifact),{**declared,'runners':declared['runners'][:2]},active)


def test_push_start_uses_requested_date_and_rejects_premature_source(tmp_path):
    rel='runtime/jra_autopilot_start_requests/2026-10-18.json'
    p=tmp_path/rel;p.parent.mkdir(parents=True);p.write_text(json.dumps({'race_date':'2026-10-18','mode':'tick'}))
    assert resolve_start(event='push',changed=[rel],root=tmp_path,today='2026-10-18')=={'race_date':'2026-10-18','mode':'tick'}
    with pytest.raises(ValueError,match='MUST_BE_RACE_DAY'):
        resolve_start(event='push',changed=[rel],root=tmp_path,today='2026-10-17')


def signed_fixture():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    from base64 import b64encode
    key=Ed25519PrivateKey.generate()
    contract={'engine_sha256':'engine','parameter_map_sha256':'jra-param'}
    health={'status':'READY','engine':{'sha256':'engine'},'parameter_map':{'sha256':'jra-param'},
            'receipt_signer':{'ready':True,'key_id':'test','public_key_b64':b64encode(key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)).decode()}}
    final={'family_id':'JRA','temporal_mode':'FORMAL-PRE-RACE','race_id':'KM-JRA-TKY-20261018-R01',
           'scheduled_post_at':'2026-10-18T10:00:00+09:00','final_freeze_timestamp':'2026-10-18T09:50:00+09:00',
           'final_prediction_package':{'execution_stage_manifest':{'PRE_KRS':{'status':'PASS'}}},
           'final_ticket':{'no_bet':False,'tickets':[{'bet_type':'EXACTA','selection':[1,2],'stake':100}],
                           'total_investment':100},'krs_run_receipt':{'seed':1}}
    receipt={'phase':'FINAL','status':'PASS','race_id':final['race_id'],'timestamp':'2026-10-18T09:51:00+09:00',
             'errors':[],'artifact_sha256':_sha(signed_payload(final))}
    final['final_receipt']={'receipt':receipt,'receipt_sha256':_sha(receipt),'signer_key_id':'test','signature_alg':'Ed25519',
                            'signature':b64encode(key.sign(canonical_bytes(receipt))).decode()}
    final['final_receipt_sha256']=_sha(receipt)
    final['final_prediction_package']['execution_stage_manifest']['FINAL_VERIFIED']={'status':'PASS'}
    final['sha256']=_sha(final)
    return final,health,contract


def test_signed_tree_binding_and_publication_are_not_user_receipt():
    final,health,contract=signed_fixture()
    record,tree=build_publication(final,health=health,contract=contract,published_at='2026-10-18T09:52:00+09:00',run_url='test')
    assert record['ticket_count']==1 and record['total_investment']==100
    assert record['rendered_before_post'] and record['published_at'] is None
    assert record['user_received_at'] is None and not record['user_delivery_verified']
    final['final_ticket']['tickets'][0]['selection']=[2,1]
    final['sha256']=_sha({k:v for k,v in final.items() if k!='sha256'})
    with pytest.raises(ValueError,match='SIGNED_TICKET_PAYLOAD_MISMATCH'):
        verify_signed_final(final,health,contract)


@pytest.mark.parametrize('amount',[True,'100',float('nan'),float('inf'),-1])
def test_invalid_settlement_numbers_are_not_coerced(amount):
    final,_,_=signed_fixture()
    with pytest.raises(ProductionPostResultError,match='PAYOUT_INVALID'):
        settle_final(final,{'top3':[1,2,3],'payouts':{'EXACTA':{'selection':[1,2],'per_100_yen':amount}}})


def test_real_cohort_36_races_isolated_dispatch_and_official_time_update(tmp_path):
    plan,records=cohort();persist_registrations(tmp_path,plan,records)
    discovery=json.loads((ROOT/'evidence/jra_p0_20261018/official_discovery.json').read_text())
    official={v['venue']:(v['meeting_key'],deepcopy(v['races'])) for v in discovery['venues']}
    # The official row may move the post; immutable intake identity remains fixed.
    official['東京'][1][0]['post_time']='09:50'
    attempts=[]
    def send(venue,race,*rest):
        attempts.append((venue,race))
        if (venue,race)==('京都',5):raise subprocess.TimeoutExpired('gh',30)
        return {'returncode':0}
    for minute in range(8*60,17*60,5):
        when=datetime.fromisoformat(f'2026-10-18T{minute//60:02}:{minute%60:02}:00+09:00')
        tick(tmp_path,'2026-10-18',when,resolve=lambda date,venue:official[venue],dispatch=send,publish=lambda:None)
    assert len(attempts)==len(set(attempts))==36
    index=json.loads((tmp_path/'runtime/jra_race_day_status/2026-10-18.json').read_text())
    assert index['cohort_metrics']['denominator']==36
    assert index['cohort_metrics']['dispatch_acknowledged']==35
    assert index['cohort_metrics']['final_artifacts_present']==0
    schedule=json.loads((tmp_path/'runtime/jra_race_day_plan/2026-10-18.schedule.json').read_text())
    assert schedule['KM-JRA-TKY-20261018-R01']['registration_reconciliation']['post_changed']
