"""Synthetic ingress/recovery tests. No LIVE, signer or prediction API calls."""
from datetime import datetime, timedelta
import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from runtime import local_race_day_dispatcher as d
from runtime.local_physical.source_acquisition import snapshot_from_bytes

NOW = datetime.fromisoformat('2026-10-15T17:45:00+09:00')


def snapshot(spec, html):
    return snapshot_from_bytes(spec, html.encode(), final_url=spec['url'], status_code=200,
                               headers={'content-type':'text/html;charset=utf-8'})


def fake_fetch(spec, cutoff):
    if spec['source_class'] == 'OFFICIAL_DAY_MENU':
        html = ''.join(f'<a href="DebaTable?k_babaCode=21&amp;k_raceDate=2026%2F10%2F15&amp;k_raceNo={n}">{n}R</a>' for n in (1,2))
    elif spec['source_class']=='OFFICIAL_ACTIVE_BETTING_UNIVERSE':
        html='<table><tr><td>テスト</td><td>テスト二</td></tr></table>'
    else:
        n = 1 if spec['url'].endswith('No=1') else 2
        html = ''.join(f'<a href="DebaTable?k_babaCode=21&amp;k_raceDate=2026%2F10%2F15&amp;k_raceNo={x}">{x}R</a>' for x in (1,2))
        html += f'2026年10月15日（木） 川　崎 第{n}競走 18:{"15" if n==1 else "45"}発走<table><tr><td>枠番</td><td>馬番</td><td>競走馬</td></tr><tr><td>1</td><td>1</td><td>テスト</td></tr><tr><td>2</td><td>2</td><td>テスト二</td></tr></table>'
    return snapshot(spec, html)


def plan():
    return d.discover('KAW','2026-10-15',120, now=NOW, fetch=fake_fetch)


def approval(p):
    from runtime.family_authority_guard import resolve_current_authority
    from runtime.execution_gateway import family_config
    return dict(family_id='LOCAL',venue_id='KAW',race_date='2026-10-15',
                current_authority_manifest=resolve_current_authority(now=NOW)[1]['manifest_id'],
                destination=family_config('LOCAL')['external_endpoint'].rstrip('/'),
                plan_sha256=p['plan_sha256'], enabled=True, owner_approval_ref='SYNTHETIC_TEST_ONLY',
                scheduled_execution_authorized=True, existing_runtime_usage_cost_authorized=True,
                data_scope='INTENT_SOURCE_STATIC_PRE_KRS_KRS_FINAL_RESULT_SETTLEMENT',race_numbers=[1,2],
                start_lead_seconds=3600, minimum_remaining_seconds=300,
                activation_phase='D', max_dispatches=2, cost_control_ref='SYNTHETIC_NOT_BILLING_APPROVAL',
                phase_b_acceptance_ref='SYNTHETIC',phase_c_acceptance_ref='SYNTHETIC',
                human_review_ref='SYNTHETIC',full_day_activation_ref='SYNTHETIC')


def run(root,p,a,state,**kwargs):
    return d.tick(root,p,a,state,now=NOW,
        authorize=lambda a,p,r,n:d.authorization(a,p,d.ROOT,n),**kwargs)


def test_official_all_races_identity_runners_and_no_freeze():
    p=plan()
    assert len(p['races'])==2 and not p['prediction_freeze']
    assert p['races'][0]['execution_id']=='KM-LOCAL-KAW-20261015-R01-LIVE-R1'
    assert p['races'][0]['observed_active_runner_universe']['runner_count']==2
    assert p['races'][0]['fields']['prediction_cutoff']=='2026-10-15T18:13:00+09:00'


@pytest.mark.parametrize('kind', ['missing','gap','wrong_venue','wrong_date','wrong_time','http','sha'])
def test_discovery_fail_closed(kind):
    def fetch(spec,cutoff):
        s,e=fake_fetch(spec,cutoff)
        html=d.raw_html(s)
        if kind=='missing': html='NO OFFICIAL MEETINGS EVIDENCE'
        if kind=='gap': html=html.replace('k_raceNo=1','k_raceNo=3')
        if kind=='wrong_venue': html=html.replace('川　崎','浦和')
        if kind=='wrong_date': html=html.replace('2026年10月15日','2026年10月16日')
        if kind=='wrong_time': html=html.replace('18:15','NOT_PUBLISHED')
        s,e=snapshot(spec,html)
        if kind=='http': s['http_status']=502
        if kind=='sha': s['raw_sha256']='0'*64
        return s,e
    with pytest.raises(ValueError): d.discover('KAW','2026-10-15',120,now=NOW,fetch=fetch)


@pytest.mark.parametrize('key,value',[('family_id','JRA'),('venue_id','OHI'),('race_date','2026-10-16'),
    ('destination','https://example.org'),('plan_sha256','bad'),('scheduled_execution_authorized',False),
    ('existing_runtime_usage_cost_authorized',False),('race_numbers',[3]),('enabled',False)])
def test_no_scope_or_cost_approval_inference(tmp_path,key,value):
    p=plan();a=approval(p);a[key]=value
    with pytest.raises(ValueError): run(tmp_path,p,a,{})


def test_durable_claim_precedes_dispatch_multiple_races_no_result_wait(tmp_path):
    p=plan();a=approval(p);state={}; events=[]
    def publish(): events.append(('persist',json.loads(json.dumps(state))))
    def send(fields):
        assert events[-1][0]=='persist'
        assert events[-1][1]['races'][d.build(fields,now=NOW)['execution_id']]['claimed_at']
        events.append(('send',fields['race_no']))
        return {'acknowledged':True,'run_id':None}
    result=run(tmp_path,p,a,state,execute=True,publish=publish,health=lambda:{'status':'PASS'},send=send)
    assert [x[1] for x in events if x[0]=='send']==[1,2]
    send=Mock(side_effect=AssertionError('NO DUPLICATE'))
    run(tmp_path,p,a,result,execute=True,publish=publish,send=send)
    send.assert_not_called()


def test_uncertain_dispatch_never_retry_and_other_race_continues(tmp_path):
    p=plan();a=approval(p);state={};calls=[]
    def send(fields):
        calls.append(fields['race_no'])
        if fields['race_no']==1: raise TimeoutError('DISPATCH_TIMEOUT')
        return {'acknowledged':True}
    run(tmp_path,p,a,state,execute=True,publish=lambda:None,health=lambda:{'status':'PASS'},send=send)
    assert calls==[1,2]
    assert state['races'][p['races'][0]['execution_id']]['status'].startswith('HOLD_AMBIGUOUS')
    run(tmp_path,p,a,state,execute=True,publish=lambda:None,send=Mock(side_effect=AssertionError()))
    assert calls==[1,2]


def test_publish_failure_no_dispatch(tmp_path):
    p=plan(); send=Mock()
    run(tmp_path,p,approval(p),{},execute=True,health=lambda:{'status':'PASS'},send=send,
        publish=Mock(side_effect=RuntimeError('GIT_CONFLICT')))
    send.assert_not_called()


def test_deadline_runtime_outage_dry_run_and_existing_checkpoint(tmp_path):
    p=plan();a=approval(p);send=Mock()
    state=run(tmp_path,p,a,{},execute=False,send=send)
    assert all(x['status'].startswith('DRY_RUN') for x in state['races'].values())
    send.assert_not_called()
    a['minimum_remaining_seconds']=1700
    state=run(tmp_path,p,a,{},execute=False)
    assert state['races'][p['races'][0]['execution_id']]['status'].startswith('DEADLINE_HOLD')
    a['minimum_remaining_seconds']=300
    state=run(tmp_path,p,a,{},execute=True,publish=lambda:None,health=Mock(side_effect=ValueError('RUNTIME_DOWN')),send=send)
    assert all(x['status']=='HOLD_PRE_DISPATCH' for x in state['races'].values())
    send.assert_not_called()
    existing=tmp_path/'runtime/executions'/p['races'][0]['execution_id'].replace('-LIVE-R1','-LIVE-R2')
    existing.mkdir(parents=True)
    state=run(tmp_path,p,a,{},execute=False)
    assert state['races'][p['races'][0]['execution_id']]['status'].startswith('EXISTING_RACE')


def test_plan_mutation_and_wrong_day_rejected(tmp_path):
    p=plan();a=approval(p);p['races'][0]['fields']['race_no']=9
    with pytest.raises(ValueError,match='SHA'): run(tmp_path,p,a,{})
    p=plan()
    with pytest.raises(ValueError,match='CURRENT_LOCAL_DAY'):
        d.tick(tmp_path,p,approval(p),{},now=NOW+timedelta(days=1))


def test_workflow_remains_opt_in_and_uses_existing_single_entry():
    import yaml
    w=yaml.load((d.ROOT/'.github/workflows/km-local-race-key-entry.yml').read_text(),Loader=yaml.BaseLoader)
    job=w['jobs']['local-day']
    assert "vars.KM_LOCAL_AUTONOMOUS_ENABLED == 'true'" in job['if']
    assert job['permissions']['actions']=='write'
    assert w['permissions']['actions']=='read'
    assert set(w['on']['workflow_dispatch']['inputs'])==set(d.FIELDS)
    assert w['jobs']['result']['needs']==['resolve','entry']


def test_deadline_crossed_while_persisting_never_sends(tmp_path):
    p=plan();a=approval(p);send=Mock()
    result=run(tmp_path,p,a,{},execute=True,publish=lambda:None,health=lambda:{'status':'PASS'},
               send=send,clock=lambda:NOW+timedelta(hours=2))
    send.assert_not_called()
    assert all(x['status']=='HOLD_PRE_DISPATCH' for x in result['races'].values())


def test_existing_result_wait_does_not_block_other_race(tmp_path):
    p=plan();a=approval(p);eid=p['races'][0]['execution_id']
    (tmp_path/'runtime/executions'/eid/'SOURCE').mkdir(parents=True)
    sent=[]
    result=run(tmp_path,p,a,{},execute=True,publish=lambda:None,health=lambda:{'status':'PASS'},
               send=lambda f:sent.append(f['race_no']) or {'acknowledged':True})
    assert sent==[2]
    assert result['races'][eid]['status'].startswith('EXISTING_RACE')


def test_same_race_key_in_noncanonical_filename_not_redispatched(tmp_path):
    p=plan();folder=tmp_path/'runtime/race_key_requests';folder.mkdir(parents=True)
    (folder/'previous-owner-name.json').write_text(json.dumps(p['races'][0]['fields']))
    state=run(tmp_path,p,approval(p),{},execute=False)
    assert state['races'][p['races'][0]['execution_id']]['status'].startswith('EXISTING_RACE')


def test_missing_odds_never_labels_declared_runners_official_active():
    def fetch(spec,cutoff):
        if spec['source_class']=='OFFICIAL_ACTIVE_BETTING_UNIVERSE':
            raise ValueError('OFFICIAL_ODDS_UNAVAILABLE')
        return fake_fetch(spec,cutoff)
    p=d.discover('KAW','2026-10-15',120,now=NOW,fetch=fetch)
    assert all(r['observed_active_runner_universe'] is None for r in p['races'])
    assert all(r['active_universe_status']=='UNKNOWN_PENDING_FRESH_SIGNED_SOURCE' for r in p['races'])
    assert all(r['dispatch_requires_fresh_signed_source'] for r in p['races'])


def test_official_odds_cancellation_reuses_existing_runner_parser():
    def fetch(spec,cutoff):
        if spec['source_class']=='OFFICIAL_ACTIVE_BETTING_UNIVERSE':
            return snapshot(spec,'<table><tr><td>1</td><td>1</td><td>テスト</td></tr><tr><td>2</td><td>2</td><td>テスト二 出走取消</td></tr></table>')
        return fake_fetch(spec,cutoff)
    p=d.discover('KAW','2026-10-15',120,now=NOW,fetch=fetch)
    assert all(r['observed_active_runner_universe']['runner_count']==1 for r in p['races'])
    assert all(r['declared_runner_universe']['runner_count']==2 for r in p['races'])


def test_limited_phase_does_not_dispatch_unapproved_race(tmp_path):
    p=plan(); a=approval(p); a.update(race_numbers=[2],max_dispatches=1,activation_phase='B')
    send=Mock(return_value={'acknowledged':True})
    state=run(tmp_path,p,a,{},execute=True,publish=lambda:None,health=lambda:{'status':'PASS'},send=send)
    assert send.call_count==1 and send.call_args.args[0]['race_no']==2
    assert state['races'][p['races'][0]['execution_id']]['status']=='NOT_AUTHORIZED_FOR_THIS_PHASE'


@pytest.mark.parametrize('changes',[
    {'activation_phase':None}, {'activation_phase':'C'}, {'activation_phase':'B'},
    {'activation_phase':'D','phase_b_acceptance_ref':None,'phase_c_acceptance_ref':None},
    {'max_dispatches':0}, {'max_dispatches':True}, {'max_dispatches':3},
    {'cost_control_ref':None}, {'race_numbers':[1,1]}, {'race_numbers':[True,2]}])
def test_phase_or_cost_gap_blocks_before_side_effect(tmp_path,changes):
    p=plan(); a=approval(p); a.update(changes); send=Mock(); publish=Mock()
    with pytest.raises(ValueError):
        run(tmp_path,p,a,{},execute=True,publish=publish,send=send,health=lambda:{'status':'PASS'})
    send.assert_not_called(); publish.assert_not_called()


def test_ambiguous_claim_consumes_budget_across_ticks(tmp_path):
    p=plan(); a=approval(p); a['max_dispatches']=1; send=Mock(side_effect=TimeoutError())
    state=run(tmp_path,p,a,{},execute=True,publish=lambda:None,health=lambda:{'status':'PASS'},send=send)
    assert send.call_count==1
    assert state['races'][p['races'][1]['execution_id']]['status']=='HOLD_DISPATCH_BUDGET_EXHAUSTED'
    run(tmp_path,p,a,state,execute=True,publish=lambda:None,reconcile=lambda *args:None,send=send)
    assert send.call_count==1


def test_phase_a_requires_no_live_approval_or_runtime(monkeypatch):
    p=plan()
    monkeypatch.setattr(d,'dispatch',Mock(side_effect=AssertionError('NO DISPATCH')))
    monkeypatch.setattr(d,'runtime_ready',Mock(side_effect=AssertionError('NO RUNTIME')))
    report=d.inspect_plan(d.ROOT,p,NOW)
    assert report['target_races']==2 and report['dispatch_count']==0
    assert report['new_signed_artifacts']==0


def test_corrupt_race_checkpoint_does_not_abort_other_approved_race(tmp_path):
    p=plan(); first=p['races'][0]['execution_id']; sent=[]
    pointer=tmp_path/'runtime/executions'/first/'SOURCE/LATEST.json'
    pointer.parent.mkdir(parents=True); pointer.write_text('{broken')
    state=run(tmp_path,p,approval(p),{},execute=True,publish=lambda:None,
              health=lambda:{'status':'PASS'},send=lambda f:sent.append(f['race_no']) or {'acknowledged':True})
    assert sent==[2]
    assert state['races'][first]['status']=='HOLD_CHECKPOINT_INTEGRITY'
    assert state['races'][first]['first_failure_observation']['code']=='EXECUTION_STORE_POINTER_INVALID'
    assert state['races'][first]['first_failure_observation']['observed_at']==NOW.isoformat()


def test_checkpoint_observer_reuses_store_manifest_integrity(tmp_path):
    from runtime.execution_store import persist_phase, ExecutionStoreError
    src=tmp_path/'src';src.mkdir()
    (src/'source_receipt_envelope.json').write_text(json.dumps({'receipt_sha256':'original'}))
    saved=persist_phase('race','SOURCE','one',src,root=tmp_path/'runtime/executions')
    (Path(saved['path'])/'source_receipt_envelope.json').write_text(json.dumps({'receipt_sha256':'changed'}))
    with pytest.raises(ExecutionStoreError,match='FILE_HASH_MISMATCH'):
        d.checkpoint_status(tmp_path,'race')


def test_claim_without_final_becomes_deadline_terminal_without_resend(tmp_path):
    p=plan();a=approval(p);first=p['races'][0]['execution_id']
    claim={'claimed_at':NOW.isoformat(),'acknowledgement':{'acknowledged':True}}
    state={'races':{first:claim}};send=Mock()
    d.tick(tmp_path,p,a,state,now=NOW+timedelta(hours=2),execute=True,
           authorize=lambda a,p,r,n:d.authorization(a,p,d.ROOT,n),publish=lambda:None,
           reconcile=lambda *a:None,send=send)
    assert state['races'][first]['status']=='FINAL_DEADLINE_EXPIRED'
    assert state['races'][first]['claimed_at']==NOW.isoformat()
    assert state['races'][first]['first_failure_observation']['stage']=='SIGNED_FINAL_DEADLINE'
    send.assert_not_called()


def prereg_approval(p):
    return {**approval(p), 'preregister_authorized_races': True,
            'preregistration_approval_ref': 'SYNTHETIC_OWNER_REVIEW'}


def test_approved_races_register_before_window_without_source_or_dispatch(tmp_path):
    p=plan(); a=prereg_approval(p); state={}; send=Mock(); health=Mock(); saved=[]
    d.tick(tmp_path,p,a,state,now=NOW-timedelta(hours=3),execute=True,
           authorize=lambda a,p,r,n:d.authorization(a,p,d.ROOT,n),
           publish=lambda:saved.append(json.loads(json.dumps(state))),send=send,health=health)
    assert len(list((tmp_path/'runtime/race_key_requests').glob('*.json')))==2
    assert len(saved)==1
    for race in p['races']:
        registration=state['races'][race['execution_id']]['registration']
        assert registration['status']=='REGISTERED_REQUEST_INTENT_NOT_FROZEN_STATIC'
        assert registration['request_intent']['execution_phase']=='SOURCE'
        assert registration['official_plan_sha256']==p['plan_sha256']
    assert not (tmp_path/'runtime/formal_intents').exists()
    send.assert_not_called(); health.assert_not_called()


def test_preregistered_race_can_dispatch_once_and_resume_without_duplicate(tmp_path):
    p=plan(); a=prereg_approval(p); state={}; send=Mock(return_value={'acknowledged':True})
    kwargs=dict(authorize=lambda a,p,r,n:d.authorization(a,p,d.ROOT,n),
                execute=True,publish=lambda:None,health=lambda:{'status':'PASS'},
                send=send,reconcile=lambda *a:None)
    d.tick(tmp_path,p,a,state,now=NOW-timedelta(hours=3),**kwargs)
    assert all(c.get('registration') for c in state['races'].values())
    # Simulate worker exit and a later worker reading its published state.
    state=json.loads(json.dumps(state))
    d.tick(tmp_path,p,a,state,now=NOW,**kwargs)
    d.tick(tmp_path,p,a,state,now=NOW+timedelta(minutes=1),**kwargs)
    assert send.call_count==2


def test_unapproved_race_is_discovered_but_not_registered(tmp_path):
    p=plan(); a=prereg_approval(p); a.update(race_numbers=[2],max_dispatches=1,activation_phase='B')
    state={}
    d.tick(tmp_path,p,a,state,now=NOW-timedelta(hours=3),execute=True,
           authorize=lambda a,p,r,n:d.authorization(a,p,d.ROOT,n),publish=lambda:None)
    assert [x.name for x in (tmp_path/'runtime/race_key_requests').glob('*.json')]==[p['races'][1]['race_key']+'.json']
    assert state['registration_coverage']['approved_target_count']==1
    assert state['registration_coverage']['discovered_count']==2


def test_preregistration_key_tamper_is_held_without_overwrite_or_send(tmp_path):
    p=plan(); a=prereg_approval(p); state={}; send=Mock(return_value={'acknowledged':True})
    kwargs=dict(authorize=lambda a,p,r,n:d.authorization(a,p,d.ROOT,n),
                execute=True,publish=lambda:None,health=lambda:{'status':'PASS'},send=send)
    d.tick(tmp_path,p,a,state,now=NOW-timedelta(hours=3),**kwargs)
    key=tmp_path/'runtime/race_key_requests'/(p['races'][0]['race_key']+'.json')
    altered={**p['races'][0]['fields'],'prediction_cutoff':'2026-10-15T18:14:00+09:00'}
    key.write_text(json.dumps(altered))
    d.tick(tmp_path,p,a,state,now=NOW,**kwargs)
    assert json.loads(key.read_text())==altered
    assert send.call_count==1 and send.call_args.args[0]['race_no']==2
    assert state['registration_coverage']['missing_execution_ids']==[p['races'][0]['execution_id']]


def test_preregistration_publish_failure_prevents_every_dispatch(tmp_path):
    p=plan(); send=Mock()
    with pytest.raises(RuntimeError,match='IMMUTABLE_CONFLICT'):
        run(tmp_path,p,prereg_approval(p),{},execute=True,
            publish=Mock(side_effect=RuntimeError('IMMUTABLE_CONFLICT')),send=send)
    send.assert_not_called()


def test_transient_preflight_recovers_but_fingerprint_mismatch_stays_held(tmp_path):
    p=plan(); a=prereg_approval(p); state={}; sent=[]; calls={1:0,2:0}
    def health():
        # R1: transient read failure; R2: incompatible deployment.
        if not calls[1]:
            calls[1]+=1; raise TimeoutError('DNS_TIMEOUT')
        if not calls[2]:
            calls[2]+=1; raise ValueError('RUNTIME_FINGERPRINT_HOLD:WRONG_SIGNER')
        return {'status':'PASS'}
    kwargs=dict(execute=True,publish=lambda:None,health=health,
                send=lambda f:sent.append(f['race_no']) or {'acknowledged':True},reconcile=lambda *a:None)
    run(tmp_path,p,a,state,**kwargs)
    run(tmp_path,p,a,state,**kwargs)
    assert sent==[1]
    assert state['races'][p['races'][1]['execution_id']]['status']=='HOLD_GUARD_OWNER_RECOVERY_REQUIRED'
    assert state['races'][p['races'][0]['execution_id']]['first_failure_observation']['code']=='DNS_TIMEOUT'


def test_bounded_worker_crosses_windows_with_independent_races(tmp_path):
    p=plan(); a=prereg_approval(p)
    a.update(worker_seconds=3600,worker_duration_approval_ref='SYNTHETIC_DURATION')
    clock=[NOW-timedelta(minutes=40)]; sent=[]; state={}
    def step():
        return d.tick(tmp_path,p,a,state,now=clock[0],execute=True,
            authorize=lambda a,p,r,n:d.authorization(a,p,d.ROOT,n),publish=lambda:None,
            health=lambda:{'status':'PASS'},send=lambda f:sent.append((f['race_no'],clock[0])) or {'acknowledged':True},
            reconcile=lambda *a:None)
    d.run_worker(a,step,clock=lambda:clock[0],sleep=lambda s:clock.__setitem__(0,clock[0]+timedelta(seconds=s)))
    assert [n for n,t in sent]==[1,2]
    assert sent[0][1]==NOW-timedelta(minutes=30) and sent[1][1]==NOW
    assert all(c.get('claimed_at') for c in state['races'].values())


@pytest.mark.parametrize('changes',[{'worker_seconds':True},{'worker_seconds':21001},
    {'worker_seconds':60},{'preregistration_approval_ref':None}])
def test_new_worker_and_registration_require_explicit_review(tmp_path,changes):
    p=plan(); a=prereg_approval(p); a.update(changes); send=Mock(); publish=Mock()
    with pytest.raises(ValueError):run(tmp_path,p,a,{},execute=True,send=send,publish=publish)
    send.assert_not_called(); publish.assert_not_called()


def test_official_discovery_read_retries_dns_but_preserves_original_failure():
    calls=[]
    def fetch(spec,cutoff):
        calls.append(spec['source_id'])
        if len(calls)==1:raise ValueError('SOURCE_DNS_RESOLUTION_FAILED:temporary test failure')
        return fake_fetch(spec,cutoff)
    p=d.discover('KAW','2026-10-15',120,now=NOW,fetch=fetch)
    observed=p['discovery_read_attempts']
    assert len(p['races'])==2 and calls[0]==calls[1]
    assert observed[0]['error']=='SOURCE_DNS_RESOLUTION_FAILED:temporary test failure'
    assert observed[0]['attempt']==1 and observed[1]['attempt']==2


def test_official_discovery_signature_guard_is_never_retried():
    calls=[]
    def fetch(spec,cutoff):
        calls.append(spec['source_id'])
        raise ValueError('SOURCE_RAW_HASH_MISMATCH')
    with pytest.raises(ValueError,match='HASH_MISMATCH'):
        d.discover('KAW','2026-10-15',120,now=NOW,fetch=fetch)
    assert len(calls)==1
