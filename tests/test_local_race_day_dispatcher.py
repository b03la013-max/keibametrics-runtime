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
    else:
        n = 1 if spec['url'].endswith('No=1') else 2
        html = ''.join(f'<a href="DebaTable?k_babaCode=21&amp;k_raceDate=2026%2F10%2F15&amp;k_raceNo={x}">{x}R</a>' for x in (1,2))
        html += f'2026年10月15日（木） 川　崎 第{n}競走 18:{"15" if n==1 else "45"}発走<table><tr><td>枠番</td><td>馬番</td><td>競走馬</td></tr><tr><td>1</td><td>1</td><td>テスト</td></tr></table>'
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
                start_lead_seconds=3600, minimum_remaining_seconds=300)


def run(root,p,a,state,**kwargs):
    return d.tick(root,p,a,state,now=NOW,
        authorize=lambda a,p,r,n:d.authorization(a,p,d.ROOT,n),**kwargs)


def test_official_all_races_identity_runners_and_no_freeze():
    p=plan()
    assert len(p['races'])==2 and not p['prediction_freeze']
    assert p['races'][0]['execution_id']=='KM-LOCAL-KAW-20261015-R01-LIVE-R1'
    assert p['races'][0]['observed_active_runner_universe']['runner_count']==1
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
    ('existing_runtime_usage_cost_authorized',False),('race_numbers',[1]),('enabled',False)])
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
