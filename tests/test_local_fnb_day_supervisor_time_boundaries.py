"""Independent time/CLI/receipt boundary checks; all Actor fixtures synthetic."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

import pytest

from runtime import local_fnb_day_supervisor as s
from test_local_fnb_day_supervisor import plan, activation, binding, completion, NOW


@pytest.mark.parametrize('known_cutoff',[False,True])
def test_past_post_without_actor_is_time_terminal_without_invented_cutoff(tmp_path,known_cutoff):
    p=plan()
    for r in p['races']:
        r['scheduled_post_at']=(NOW-timedelta(minutes=1)).isoformat()
        r['prediction_cutoff']=(NOW-timedelta(minutes=2)).isoformat() if known_cutoff else None
        r['start_at']=None
    state=s.tick(p,tmp_path,execute=True,clock=lambda:NOW)
    assert all(c['status']=='MISSED_WINDOW' for c in state['races'].values())
    assert [c['prediction_cutoff'] for c in state['races'].values()]==[r['prediction_cutoff'] for r in p['races']]
    assert state['counts']['dispatched']==state['counts']['no_bet_races']==0


def test_expiry_after_owner_qualification_prevents_claim(tmp_path):
    p=plan(); b=binding(tmp_path); late=[False]
    def authorize(**kw):
        late[0]=True
        return True
    b['authorize_race']=authorize
    state=s.tick(p,tmp_path,binding=b,activation=activation(),execute=True,
                 clock=lambda:s.stamp(p['races'][0]['prediction_cutoff']) if late[0] else NOW)
    assert state['races']['5']['code']=='CUTOFF_EXPIRED_DURING_PREFLIGHT'
    assert 'claim' not in state['races']['5']
    assert 5 not in b['sent']


def test_ambiguous_actor_exception_is_not_retried_and_later_race_runs(tmp_path):
    b=binding(tmp_path); calls=[]
    def execute(**kw):
        n=kw['race']['race_no']; calls.append(n)
        if n==5:raise TimeoutError('SYNTHETIC_AMBIGUOUS_ACK')
        return {'status':'ACK','run_id':'synthetic-six'}
    b['execute_race']=execute
    for _ in range(2):
        state=s.tick(plan(),tmp_path,binding=b,activation=activation(),execute=True,clock=lambda:NOW)
    assert calls==[5,6]
    assert state['counts']['dispatched']==2
    assert state['counts']['verified_prestart_originals']==0


def test_no_bet_and_result_counts_are_revoked_on_current_original_loss(tmp_path):
    b=binding(tmp_path,complete=True)
    s.tick(plan(),tmp_path,binding=b,activation=activation(),execute=True,clock=lambda:NOW)
    for n in (5,6):
        b['available'][n]['computed_no_bet']=True
        b['available'][n]['stages']['TICKET'].update(status='COMPUTED_NO_BET',ticket_count=0,total_investment=0,reason='SYNTHETIC_POLICY_ZERO_TICKETS')
    state=s.tick(plan(),tmp_path,binding=b,activation=activation(),execute=True,clock=lambda:NOW)
    assert state['counts']['no_bet_races']==2
    checkpoint=tmp_path/'FNB_2026-11-03_DAY_CHECKPOINT.json'
    prior=json.loads(checkpoint.read_bytes())
    prior['races']['5']['result_learning']={'status':'OLD_CACHE_NOT_CURRENT_PROOF'}
    checkpoint.write_bytes(s.encoded(prior))
    (tmp_path/'5_body.md').write_text('current-original-corrupted')
    state=s.tick(plan(),tmp_path,binding=b,activation=activation(),execute=True,clock=lambda:NOW)
    assert state['counts']['no_bet_races']==1
    assert state['counts']['verified_result_learning_races']==0
    assert 'result_learning' not in state['races']['5']


def test_same_body_recipient_ack_is_required_for_delivery(tmp_path):
    b=binding(tmp_path,complete=True)
    s.tick(plan(),tmp_path,binding=b,activation=activation(),execute=True,clock=lambda:NOW)
    wrong=[False]
    def inspect(**kw):
        c=kw['completion']
        data={'race_id':kw['race']['race_id'],'body_sha256':'0'*64 if wrong[0] else c['body_original']['sha256'],
              'recipient_ack_verified':True,'received_at':NOW.isoformat()}
        raw=s.encoded(data); name=f"{kw['race']['race_no']}_ack.json"; (tmp_path/name).write_bytes(raw)
        return {'recipient_ack_verified':True,'original':{'path':name,'sha256':hashlib.sha256(raw).hexdigest()}}
    b['inspect_delivery']=inspect
    state=s.tick(plan(),tmp_path,binding=b,activation=activation(),execute=True,clock=lambda:NOW)
    assert state['counts']['verified_prestart_recipient_deliveries']==2
    wrong[0]=True
    state=s.tick(plan(),tmp_path,binding=b,activation=activation(),execute=True,clock=lambda:NOW)
    assert state['counts']['verified_prestart_recipient_deliveries']==0
    assert all(c['code']=='RECIPIENT_ACK_RECEIPT_IDENTITY_OR_CLOCK_MISMATCH' for c in state['races'].values())


def test_cli_observation_can_run_outside_repository(tmp_path,monkeypatch,capsys):
    p=plan(); f=tmp_path/'reference-plan.json'; f.write_bytes(s.encoded(p))
    monkeypatch.chdir(tmp_path)
    assert s.main(['--discovery-json',str(f),'--private-root',str(tmp_path/'private')])==0
    output=json.loads(capsys.readouterr().out)
    assert output['counts']['discovered']==2 and output['counts']['dispatched']==0


def test_cli_rejects_execute_without_exact_existing_binding_before_store_creation(tmp_path,capsys):
    f=tmp_path/'p.json'; f.write_bytes(s.encoded(plan()))
    with pytest.raises(SystemExit) as exc:
        s.main(['--discovery-json',str(f),'--private-root',str(tmp_path/'private'),'--execute'])
    assert exc.value.code==2
    assert '--execute requires --binding' in capsys.readouterr().err
    assert not (tmp_path/'private').exists()


def test_unapproved_bounded_worker_cannot_start(tmp_path):
    with pytest.raises(ValueError,match='EXACT_WORKER_DURATION_APPROVAL_REQUIRED'):
        s.supervise(day='2026-11-03',private_root=tmp_path,binding=binding(tmp_path),
                    activation=activation(),worker_seconds=60,clock=lambda:NOW)
    assert not (tmp_path/'FNB_2026-11-03_DAY_CHECKPOINT.json').exists()


def test_process_death_after_send_keeps_attempt_budget_consumed(tmp_path):
    b=binding(tmp_path); calls=[]; a=activation();a['max_dispatches']=1
    def dies(**kw):
        calls.append(kw['race']['race_no'])
        persisted=json.loads((tmp_path/'FNB_2026-11-03_DAY_CHECKPOINT.json').read_bytes())
        assert persisted['races']['5']['dispatch_count']==1
        raise SystemExit('SYNTHETIC_PROCESS_DEATH_AFTER_EXTERNAL_SEND')
    b['execute_race']=dies
    with pytest.raises(SystemExit):
        s.tick(plan(),tmp_path,binding=b,activation=a,execute=True,clock=lambda:NOW)
    state=s.tick(plan(),tmp_path,binding=b,activation=a,execute=True,clock=lambda:NOW)
    assert calls==[5]
    assert state['races']['6']['code']=='APPROVED_DISPATCH_BUDGET_EXHAUSTED'


@pytest.mark.parametrize('stage',['SOURCE','NUMERICAL','STATIC','KRS','SAVE'])
def test_non_ticket_stages_cannot_claim_computed_no_bet(tmp_path,stage):
    p=plan(); c=completion(tmp_path,p['races'][0]);c['stages'][stage]['status']='COMPUTED_NO_BET'
    with pytest.raises(ValueError,match='FULL_PIPELINE_STAGE_NOT_VERIFIED_'+stage):
        s.verify_prediction(tmp_path,p['races'][0],c,NOW)


def test_flag_alone_cannot_create_no_bet_acceptance(tmp_path):
    p=plan(); c=completion(tmp_path,p['races'][0]);c['computed_no_bet']=True
    with pytest.raises(ValueError,match='VERIFIED_ZERO_TICKET_REASON'):
        s.verify_prediction(tmp_path,p['races'][0],c,NOW)


def test_zero_ticket_label_with_positive_investment_cannot_count_as_no_bet(tmp_path):
    p=plan(); c=completion(tmp_path,p['races'][0]);c['computed_no_bet']=True
    c['stages']['TICKET'].update(status='COMPUTED_NO_BET',ticket_count=0,total_investment=100,reason='SYNTHETIC_INCONSISTENT_STAKE')
    with pytest.raises(ValueError,match='VERIFIED_ZERO_TICKET_REASON'):
        s.verify_prediction(tmp_path,p['races'][0],c,NOW)


def test_expired_resume_authority_preserves_readback_but_blocks_mutation(tmp_path):
    b=binding(tmp_path,complete=True)
    s.tick(plan(),tmp_path,binding=b,activation=activation(),execute=True,clock=lambda:NOW)
    b['delivered'].clear();b['authorize_race']=lambda **kw:False
    state=s.tick(plan(),tmp_path,binding=b,activation=activation(),execute=True,clock=lambda:NOW)
    assert state['counts']['verified_prestart_originals']==2
    assert b['delivered']==[]
    assert all(c['activation_hold']=='CURRENT_RESUME_SOURCE_OWNER_AUTHORITY_NOT_VERIFIED' for c in state['races'].values())
