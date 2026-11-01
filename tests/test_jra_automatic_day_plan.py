"""Offline DatePlan lifecycle cases, never unknown-future Live credit."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'runtime'), str(ROOT/'runtime/jra_source_runtime')]
import jra_race_day_autopilot as autopilot
import jra_race_day_resolver as resolver
from jra_race_day_registration import sha, verify_registration

DAY = '2026-11-08'
NOW = dt.datetime.fromisoformat(DAY+'T08:00:00+09:00')


def card(venue, *, jump=False):
    rows=[]
    for number in range(1,13):
        title='障害3歳以上未勝利' if jump and number==4 else '3歳以上1勝クラス'
        surface='芝→ダート' if jump and number==4 else '芝'
        rows.append({'race_no':number, 'post_time':f'{9+(number+1)//2:02d}:{45 if number%2 else 55:02d}',
            'surface':surface,'distance_m':3000 if jump and number==4 else 1600,
            'field_size':12,'title':title,
            'raw':f'{9+(number+1)//2}時{45 if number%2 else 55}分 {title} {surface}1,600m12頭'})
    return resolver.venue_code(venue)+'20260501', rows


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    import socket, urllib.request
    def deny(*a,**k):raise AssertionError('DAY_PLAN_TEST_EXTERNAL_IO_FORBIDDEN')
    monkeypatch.setattr(socket.socket,'connect',deny)
    monkeypatch.setattr(urllib.request,'urlopen',deny)
    monkeypatch.setattr(urllib.request.OpenerDirector,'open',deny)
    for name in ('observed_formal_runs','observed_source_runs','observed_resolver_runs'):
        monkeypatch.setattr(autopilot,name,lambda *a,**k:[])


@pytest.fixture
def runtime(tmp_path):
    directory=tmp_path/'profiles';directory.mkdir()
    authority={'manifest_id':'KM-FAMILY-CURRENT-AUTHORITY-20261012-R51',
        'status':'CURRENT-AUTHORITY','effective_at':'2026-10-12T00:00:00+09:00',
        'family_scoped_authority':{'JRA':{'production_static_owner_activation':{
            'status':'OWNER_AUTHORIZED_UNVALIDATED','fixture_only':True}}}}
    (directory/'KM_FAMILY_CURRENT_AUTHORITY_20261012_R51.json').write_text(json.dumps(authority))
    return tmp_path


def create(root,cache=None,**kwargs):
    return autopilot.ensure_day_plan(root,DAY,NOW,default_all=True,cache={} if cache is None else cache,
        meetings=kwargs.pop('meetings',lambda d:['東京','京都']),
        resolve=kwargs.pop('resolve',lambda d,v:card(v,jump=v=='京都')),**kwargs)


def read_plan(root):
    return json.loads((root/f'runtime/jra_race_day_plan/{DAY}.json').read_text())


def tick(root,cache,when=NOW,**kwargs):
    return autopilot.tick(root,DAY,when,default_all=False,cache=cache,resolver_runs=[],
        resolve=lambda d,v:pytest.fail('unnecessary duplicate official resolve'),**kwargs)


def test_missing_plan_uses_official_cache_to_create24_manage23_register_without_source(runtime,monkeypatch):
    cache={};calls=[]
    monkeypatch.setenv('GITHUB_RUN_ID','OFFLINE_FIXTURE_NOT_A_LIVE_RUN')
    assert create(runtime,cache,resolve=lambda d,v:(calls.append(v),card(v,jump=v=='京都'))[1])
    plan=read_plan(runtime)
    assert calls==['東京','京都']
    assert len(plan['management_race_ids'])==24 and plan['cohort']['race_count']==23
    assert plan['scope_exclusions'][0]['race_id']=='KM-JRA-KYO-20261108-R04'
    assert plan['automatic_generation']['workflow_run_id']=='OFFLINE_FIXTURE_NOT_A_LIVE_RUN'
    assert plan['automatic_generation']['day_level_unattended_acceptance']=='NOT_ESTABLISHED_BY_PLAN_CREATION_ALONE'
    assert sha(plan['automatic_generation']['source_discovery'])==plan['cohort']['source_discovery_sha256']
    records=list((runtime/f'runtime/jra_race_registrations/{DAY}').glob('*.json'))
    assert len(records)==23
    for path in records:
        record=json.loads(path.read_text())
        verify_registration(record,plan,race_id=record['race_id'],
            official_post=dt.datetime.fromisoformat(record['intake_intent']['scheduled_post_at']))
        assert record['executed_cells']==0 and record['source_executed'] is False
    rows=tick(runtime,cache)
    assert len(rows)==23  # Scope rows live in the24-entry schedule, never dispatch entries.
    schedule=json.loads((runtime/f'runtime/jra_race_day_plan/{DAY}.schedule.json').read_text())
    assert len(schedule)==24 and schedule['KM-JRA-KYO-20261108-R04']['status']=='SCOPE_HOLD'
    assert not (runtime/'runtime/jra_formal_intents').exists()


def test_existing_human_plan_is_not_rewritten_or_credited_as_day_autonomy(runtime):
    path=runtime/f'runtime/jra_race_day_plan/{DAY}.json';path.parent.mkdir(parents=True)
    original='{ "entries": [{"venue":"東京", "races":[1]}], "human_note":"keep" }\n'.encode()
    path.write_bytes(original)
    assert create(runtime,meetings=lambda d:pytest.fail('existing plan must bypass bootstrap'))
    assert path.read_bytes()==original and not (runtime/'runtime/jra_race_registrations').exists()


def test_existing_automatic_plan_and_records_are_byte_stable_on_resume(runtime):
    assert create(runtime)
    before={str(p):p.read_bytes() for p in (runtime/'runtime').rglob('*.json')}
    assert create(runtime,meetings=lambda d:pytest.fail('no new discovery for immutable plan'))
    assert before=={str(p):p.read_bytes() for p in (runtime/'runtime').rglob('*.json')}


def test_bootstrap_is_not_enabled_without_the_existing_all_races_option(runtime):
    assert autopilot.ensure_day_plan(runtime,DAY,NOW,default_all=False,cache={},
        meetings=lambda d:pytest.fail('new unapproved calendar call'))
    assert not (runtime/'runtime').exists()


@pytest.mark.parametrize('surface',[None,'','UNKNOWN','AW'])
def test_unknown_type_is_held_while_known_flat_siblings_keep_registration(runtime,surface):
    def resolve(d,v):
        key,rows=card(v,jump=False)
        if v=='東京':rows[1]['surface']=surface;rows[1]['raw']='10時55分 競走種別未確認 12頭'
        return key,rows
    cache={};assert create(runtime,cache,resolve=resolve)
    plan=read_plan(runtime);held=plan['scope_exclusions'][0]
    assert plan['cohort']['race_count']==23
    assert held['race_type']=='UNKNOWN' and held['reason']=='OFFICIAL_RACE_TYPE_UNKNOWN'
    assert held['race_id'] not in plan['cohort']['race_ids']
    tick(runtime,cache)
    schedule=json.loads((runtime/f'runtime/jra_race_day_plan/{DAY}.schedule.json').read_text())
    assert schedule[held['race_id']]['status']=='SCOPE_HOLD'


@pytest.mark.parametrize('field,value',[('field_size',None),('field_size',0),('post_time','99:00'),('raw','')])
def test_incomplete_race_header_does_not_block_complete_siblings(runtime,field,value):
    def resolve(d,v):
        key,rows=card(v,jump=False)
        if v=='東京':rows[0][field]=value
        return key,rows
    cache={};assert create(runtime,cache,resolve=resolve)
    plan=read_plan(runtime);assert plan['cohort']['race_count']==23
    held=plan['scope_exclusions'][0];assert held['status']=='SOURCE_HOLD'
    tick(runtime,cache)
    schedule=json.loads((runtime/f'runtime/jra_race_day_plan/{DAY}.schedule.json').read_text())
    assert schedule[held['race_id']]['status']=='SOURCE_HOLD'


def test_unresolved_venue_does_not_create_partial_intake_or_touch_existing_claims(runtime):
    directory=runtime/'runtime/jra_race_day_plan';directory.mkdir(parents=True)
    state=directory/f'{DAY}.state.json';original=b'{"existing":{"dispatch_state":"DISPATCH_ACKNOWLEDGED"}}\n';state.write_bytes(original)
    def resolve(d,v):
        if v=='京都':raise ValueError('partial official venue')
        return card(v)
    assert create(runtime,resolve=resolve) is False
    assert state.read_bytes()==original
    assert not (directory/f'{DAY}.json').exists()
    assert not (runtime/'runtime/jra_race_registrations').exists()
    assert autopilot.tick(runtime,DAY,NOW,default_all=False,dispatch=lambda *a:pytest.fail('no approved plan'))==[]


def test_calendar403_uses_existing_stable_fault_and_recovers_only_on_new_worker_cache(runtime):
    import urllib.error
    cache={};calls=[]
    def denied(d):calls.append(d);raise urllib.error.HTTPError('https://www.jra.go.jp/',403,'denied',{},None)
    assert create(runtime,cache,meetings=denied) is False
    path=runtime/f'runtime/jra_race_day_plan/{DAY}.schedule.json';first=path.read_bytes()
    assert create(runtime,cache,meetings=lambda d:pytest.fail('latched403')) is False
    assert calls==[DAY] and path.read_bytes()==first
    assert create(runtime,{})
    assert DAY+':ALL' not in json.loads(path.read_text())


def test_official_no_meetings_is_not_a_fake_empty_registered_plan(runtime):
    cache={};assert create(runtime,cache,meetings=lambda d:[])
    assert not (runtime/'runtime').exists()


@pytest.mark.parametrize('kind',['duplicates','nonsequence','boolnumber','badmeeting'])
def test_bad_official_identity_or_universe_never_creates_intake(runtime,kind):
    def resolve(d,v):
        key,rows=card(v)
        if kind=='nonsequence':rows[2]['race_no']=4
        if kind=='boolnumber':rows[0]['race_no']=True
        if kind=='badmeeting':key='0820250501'
        return key,rows
    assert create(runtime,meetings=(lambda d:['東京','東京']) if kind=='duplicates' else lambda d:['東京'],resolve=resolve) is False
    assert not (runtime/f'runtime/jra_race_day_plan/{DAY}.json').exists()
    assert not (runtime/'runtime/jra_formal_intents').exists()


def test_generated_plan_and_registration_are_published_before_due_claim_without_resend(runtime):
    cache={};assert create(runtime,cache)
    # First Tokyo post10:45 in this fixture; window opens09:50.
    when=dt.datetime.fromisoformat(DAY+'T09:55:00+09:00');sent=[];events=[]
    def publish():
        plan=read_plan(runtime)
        for rid in plan['cohort']['race_ids']:
            assert (runtime/f'runtime/jra_race_registrations/{DAY}/{rid}.json').exists()
        events.append('PUBLISH')
    def send(*args):assert events;sent.append(args);return {'returncode':0}
    tick(runtime,cache,when,dispatch=send,publish=publish)
    before=copy.deepcopy(sent)
    tick(runtime,cache,when,dispatch=send,publish=publish)
    assert sent==before and sent
    assert 'KM-JRA-KYO-20261108-R04' not in json.loads((runtime/f'runtime/jra_race_day_plan/{DAY}.state.json').read_text())


def test_unpublished_generated_plan_never_dispatches_and_does_not_touch_plan_bytes(runtime):
    cache={};assert create(runtime,cache)
    original=(runtime/f'runtime/jra_race_day_plan/{DAY}.json').read_bytes()
    def fail():raise RuntimeError('Git publication refused')
    rows=tick(runtime,cache,dt.datetime.fromisoformat(DAY+'T09:55:00+09:00'),publish=fail,
        dispatch=lambda *a:pytest.fail('generated Plan/claim was not published'))
    assert any(r['status']=='CLAIM_PUBLISH_FAILED_NO_SEND' for r in rows)
    assert (runtime/f'runtime/jra_race_day_plan/{DAY}.json').read_bytes()==original


def test_commit_contains_generated_plan_and_all_registrations_in_same_existing_transaction(runtime,monkeypatch):
    cache={};assert create(runtime,cache);tick(runtime,cache)
    calls=[]
    def run(argv,**kwargs):
        calls.append(argv)
        return SimpleNamespace(returncode=1 if argv[:4]==['git','diff','--cached','--quiet'] else 0,stdout='',stderr='')
    monkeypatch.setattr(autopilot.subprocess,'run',run)
    monkeypatch.setattr(autopilot,'_rebase_generated',lambda *a:True)
    autopilot._commit(runtime,DAY)
    added=next(x for x in calls if x[:2]==['git','add'])
    assert f'runtime/jra_race_day_plan/{DAY}.json' in added
    assert len([x for x in added if x.startswith('runtime/jra_race_registrations/')])==23
    assert any(x[:2]==['git','commit'] for x in calls)


def test_existing_cli_prepares_plan_before_regular_tick_and_leaves_no_new_dispatcher(runtime,monkeypatch):
    class FixedPlanClock(dt.datetime):
        @classmethod
        def now(cls,tz=None):
            return NOW.astimezone(tz) if tz else NOW.replace(tzinfo=None)
    monkeypatch.setattr(autopilot._dt,'datetime',FixedPlanClock)
    events=[];original_tick=autopilot.tick
    monkeypatch.delenv('GITHUB_OUTPUT',raising=False)
    monkeypatch.setattr(autopilot,'resolve_meetings',lambda d:['東京','京都'])
    monkeypatch.setattr(autopilot,'resolve_day',lambda d,v:card(v,jump=v=='京都'))
    monkeypatch.setattr(autopilot,'_gh_dispatch',lambda *a:pytest.fail('future fixture must not dispatch'))
    monkeypatch.setattr(autopilot,'_commit',lambda *a:events.append('existing_git_publish'))
    def checked_tick(*a,**kwargs):
        assert read_plan(runtime)['cohort']['race_count']==23
        events.append('tick_after_plan')
        return original_tick(*a,**kwargs)
    monkeypatch.setattr(autopilot,'tick',checked_tick)
    assert autopilot.main(['--repo-root',str(runtime),'--date',DAY,'--all-races-default'])==0
    assert events==['tick_after_plan','existing_git_publish']
    assert not (runtime/'runtime/jra_autopilot_start_requests').exists()


def test_existing_cli_never_uses_ephemeral_all_races_fallback_after_failed_bootstrap(runtime,monkeypatch):
    import urllib.error
    monkeypatch.delenv('GITHUB_OUTPUT',raising=False)
    def fail(d):raise urllib.error.HTTPError('https://www.jra.go.jp/',403,'denied',{},None)
    monkeypatch.setattr(autopilot,'resolve_meetings',fail)
    monkeypatch.setattr(autopilot,'_commit',lambda *a:None)
    monkeypatch.setattr(autopilot,'_gh_dispatch',lambda *a:pytest.fail('no bootstrap authority'))
    original=autopilot.tick
    def checked_tick(*a,**kwargs):
        assert kwargs['default_all'] is False
        return original(*a,**kwargs)
    monkeypatch.setattr(autopilot,'tick',checked_tick)
    assert autopilot.main(['--repo-root',str(runtime),'--date',DAY,'--all-races-default'])==0
    assert not (runtime/f'runtime/jra_race_day_plan/{DAY}.json').exists()


def git(root,*args):
    return subprocess.run(['git',*args],cwd=root,check=True,text=True,capture_output=True).stdout.strip()


def local_origin(root):
    git(root,'-c','init.templateDir=','init','--initial-branch=main')
    git(root,'config','user.name','OFFLINE FIXTURE')
    git(root,'config','user.email','fixture@example.invalid')
    git(root,'config','core.hooksPath','/dev/null')
    git(root,'config','commit.gpgSign','false')
    git(root,'add','profiles')
    git(root,'commit','-m','fixture baseline')
    origin=root.parent/(root.name+'-origin.git')
    git(root,'-c','init.templateDir=','init','--bare',str(origin))
    git(root,'remote','add','origin',str(origin))
    git(root,'push','-u','origin','main')
    return origin


def test_real_local_git_publishes_plan_registration_status_together_and_repeat_adds_no_commit(runtime):
    origin=local_origin(runtime)
    cache={};assert create(runtime,cache);tick(runtime,cache)
    autopilot._commit(runtime,DAY)
    first=git(runtime,'rev-parse','HEAD')
    paths=git(runtime,'diff-tree','--no-commit-id','--name-only','-r',first).splitlines()
    assert f'runtime/jra_race_day_plan/{DAY}.json' in paths
    assert len([x for x in paths if x.startswith('runtime/jra_race_registrations/')])==23
    assert len(paths)==28
    assert git(runtime,'--git-dir',str(origin),'rev-parse','main')==first
    autopilot._commit(runtime,DAY)
    assert git(runtime,'rev-parse','HEAD')==first


def test_conflicting_concurrent_plan_creation_fails_closed_without_overwriting_winner(runtime,monkeypatch):
    origin=local_origin(runtime)
    cache={};assert create(runtime,cache);tick(runtime,cache)
    # A second local clone stands in for a competing publisher; no GitHub/API.
    other=runtime.parent/(runtime.name+'-other')
    git(runtime,'-c','init.templateDir=','clone','--branch','main',str(origin),str(other))
    git(other,'config','user.name','OFFLINE FIXTURE')
    git(other,'config','user.email','fixture@example.invalid')
    git(other,'config','core.hooksPath','/dev/null')
    git(other,'config','commit.gpgSign','false')
    path=other/f'runtime/jra_race_day_plan/{DAY}.json';path.parent.mkdir(parents=True)
    original=b'{"entries":[],"existing_owner_plan":"immutable"}\n';path.write_bytes(original)
    git(other,'add',str(path.relative_to(other)));git(other,'commit','-m','other fixture plan');git(other,'push')
    monkeypatch.setattr(autopilot.time,'sleep',lambda *a:None)
    with pytest.raises(RuntimeError,match='PUBLISH_RETRIES_EXHAUSTED'):autopilot._commit(runtime,DAY)
    actual=subprocess.run(['git','--git-dir',str(origin),'show',f'main:runtime/jra_race_day_plan/{DAY}.json'],
        check=True,capture_output=True).stdout
    assert actual==original


@pytest.mark.parametrize('tokens,ok',[(['01','02','03'],True),(['01','02','04'],False)])
def test_resolver_requires_exact_navigation_ordinals_not_only_equal_row_count(monkeypatch,tokens,ok):
    import jra_pedigree_harvest
    key='0520260501';d8=DAY.replace('-','')
    nav='pw01drl00'+key+d8+'/aa'
    rows=''.join(f'<tr><td>{10+i}時00分 3歳以上1勝クラス 芝1,600m12頭</td></tr>' for i in range(3))
    page='<table>'+rows+'</table>'+''.join('pw01dde01'+key+x+d8 for x in tokens)
    class Client:
        def __init__(self,**kwargs):pass
        def get(self,*a):return "doAction('/JRADB/accessD.html','entry')"
        def post(self,path,token):return nav if token=='entry' else page
    monkeypatch.setattr(jra_pedigree_harvest,'_Client',Client)
    if ok:assert [r['race_no'] for r in resolver.resolve_day(DAY,'東京')[1]]==[1,2,3]
    else:
        with pytest.raises(ValueError,match='RACE_ORDINALS_UNRESOLVED'):resolver.resolve_day(DAY,'東京')


@pytest.mark.parametrize('change,status', [({'surface':None},'SCOPE_HOLD'),
    ({'raw':None},'SOURCE_HOLD'),({'post_time':None},'SOURCE_HOLD')])
def test_refreshed_official_row_cannot_bypass_automatic_plan_scope_or_header_gate(runtime,change,status):
    cache={};assert create(runtime,cache)
    plan_bytes=(runtime/f'runtime/jra_race_day_plan/{DAY}.json').read_bytes()
    records={p.name:p.read_bytes() for p in (runtime/f'runtime/jra_race_registrations/{DAY}').glob('*.json')}
    cache['days']['東京'][1][0].update(change)
    sent=[]
    rows=tick(runtime,cache,dt.datetime.fromisoformat(DAY+'T09:55:00+09:00'),
              dispatch=lambda *a:sent.append(a),publish=lambda:None)
    row=next(r for r in rows if r['race_id']=='KM-JRA-TKY-20261108-R01')
    assert row['status']==status
    assert not any(args[:2]==('東京',1) for args in sent)
    assert sent  # Independent eligible siblings continue through the existing dispatcher.
    assert (runtime/f'runtime/jra_race_day_plan/{DAY}.json').read_bytes()==plan_bytes
    assert {p.name:p.read_bytes() for p in (runtime/f'runtime/jra_race_registrations/{DAY}').glob('*.json')}==records
    state=json.loads((runtime/f'runtime/jra_race_day_plan/{DAY}.state.json').read_text())
    assert 'KM-JRA-TKY-20261108-R01' not in state


@pytest.mark.parametrize('pipeline', ['FINAL','NO_BET','INTENT','AMBIGUOUS_CLAIM'])
@pytest.mark.parametrize('change', [{'surface':None},{'post_time':None}])
def test_refreshed_header_hold_preserves_existing_pipeline_status_and_artifact_bytes(runtime,pipeline,change):
    cache={};assert create(runtime,cache);tick(runtime,cache)
    rid='KM-JRA-TKY-20261108-R01';eid=rid+'-LIVE-R1'
    state_path=runtime/f'runtime/jra_race_day_plan/{DAY}.state.json'
    paths=[]
    if pipeline=='FINAL':
        path=runtime/'runtime/final_artifacts'/(rid+'.json');body={'sha256':'f'*64}
    elif pipeline=='NO_BET':
        path=runtime/'runtime/jra_no_bet_terminals'/(eid+'.json');body={}
        intent=runtime/'runtime/jra_formal_intents'/(eid+'.json');intent.parent.mkdir(parents=True)
        intent.write_text('{}');paths.append(intent)
    elif pipeline=='INTENT':
        path=runtime/'runtime/jra_formal_intents'/(eid+'.json');body={}
    else:
        path=state_path;body={rid:{'dispatch_state':'HOLD_AMBIGUOUS_DISPATCH_NO_AUTOMATIC_RETRY',
            'claimed_at':DAY+'T09:54:00+09:00','dispatch_claim_token':'fixture-existing-claim'}}
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(body));paths.append(path)
    original={p:p.read_bytes() for p in paths}
    old_state=json.loads(state_path.read_text()).get(rid)
    schedule_path=state_path.with_name(DAY+'.schedule.json')
    schedule=json.loads(schedule_path.read_text());before=autopilot.race_status(runtime,rid,schedule[rid],json.loads(state_path.read_text()),NOW)
    cache['days']['東京'][1][0].update(change)
    sent=[]
    rows=tick(runtime,cache,dt.datetime.fromisoformat(DAY+'T09:55:00+09:00'),
              dispatch=lambda *a:sent.append(a),publish=lambda:None)
    assert next(r for r in rows if r['race_id']==rid)['status']=='ALREADY_DISPATCHED'
    assert not any(args[:2]==('東京',1) for args in sent) and sent
    schedule=json.loads(schedule_path.read_text());state=json.loads(state_path.read_text())
    after=autopilot.race_status(runtime,rid,schedule[rid],state,NOW)
    assert after['state']==before['state']
    assert after['current_official_row_hold']['status'] in {'SCOPE_HOLD','SOURCE_HOLD'}
    assert state.get(rid)==old_state
    for p,b in original.items():
        if p!=state_path:assert p.read_bytes()==b


def test_bootstrap_time_is_included_in_actual_dispatch_deadline(runtime,monkeypatch):
    start=dt.datetime.fromisoformat(DAY+'T09:55:00+09:00')
    after=dt.datetime.fromisoformat(DAY+'T10:16:00+09:00')
    clock=[start];elapsed=[0.0]
    class Clock(dt.datetime):
        @classmethod
        def now(cls,tz=None):return clock[0]
    monkeypatch.setattr(autopilot._dt,'datetime',Clock)
    monkeypatch.setattr(autopilot.time,'monotonic',lambda:elapsed[0])
    monkeypatch.delenv('GITHUB_OUTPUT',raising=False)
    monkeypatch.setattr(autopilot,'resolve_meetings',lambda d:['東京','京都'])
    def resolve(d,v):
        result=card(v,jump=v=='京都')
        if v=='京都':clock[0]=after;elapsed[0]=21*60.0
        return result
    monkeypatch.setattr(autopilot,'resolve_day',resolve)
    monkeypatch.setattr(autopilot,'_commit',lambda *a:None)
    sent=[];monkeypatch.setattr(autopilot,'_gh_dispatch',lambda *a:sent.append(a) or {'run_id':'OFFLINE_FIXTURE'})
    assert autopilot.main(['--repo-root',str(runtime),'--date',DAY,'--all-races-default'])==0
    assert not any(args[:2]==('東京',1) for args in sent)
    status=json.loads((runtime/f'runtime/jra_race_day_status/{DAY}.json').read_text())
    assert next(r for r in status['races'] if r['race_id']=='KM-JRA-TKY-20261108-R01')['state']=='MISSED_WINDOW'
    assert read_plan(runtime)['automatic_generation']['observed_at']==after.isoformat()


@pytest.mark.parametrize('pipeline', ['FINAL','NO_BET','INTENT','AMBIGUOUS_CLAIM'])
def test_new_header_hold_becomes_advisory_when_canonical_pipeline_arrives_later(runtime,pipeline):
    cache={};assert create(runtime,cache);tick(runtime,cache)
    rid='KM-JRA-TKY-20261108-R01';eid=rid+'-LIVE-R1'
    when=dt.datetime.fromisoformat(DAY+'T09:55:00+09:00')
    cache['days']['東京'][1][0]['surface']=None
    tick(runtime,cache,when,dispatch=lambda *a:None,publish=lambda:None)
    schedule_path=runtime/f'runtime/jra_race_day_plan/{DAY}.schedule.json'
    state_path=schedule_path.with_name(DAY+'.state.json')
    schedule=json.loads(schedule_path.read_text());assert schedule[rid]['status']=='SCOPE_HOLD'
    if pipeline=='FINAL':
        path=runtime/'runtime/final_artifacts'/(rid+'.json');body={'sha256':'f'*64};expected='FINAL'
    elif pipeline=='NO_BET':
        path=runtime/'runtime/jra_no_bet_terminals'/(eid+'.json');body={};expected='EVIDENCE_NO_BET'
        intent=runtime/'runtime/jra_formal_intents'/(eid+'.json');intent.parent.mkdir(parents=True)
        intent.write_text('{}')
    elif pipeline=='INTENT':
        path=runtime/'runtime/jra_formal_intents'/(eid+'.json');body={};expected='DISPATCHED_RUNNING'
    else:
        path=state_path;body=json.loads(path.read_text());expected='HOLD_AMBIGUOUS_DISPATCH_NO_AUTOMATIC_RETRY'
        body[rid]={'dispatch_state':expected,'dispatch_claim_token':'arriving-existing-claim','claimed_at':when.isoformat()}
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(body,ensure_ascii=False,sort_keys=True,indent=1)+'\n')
    original=path.read_bytes()
    tick(runtime,cache,when,dispatch=lambda *a:pytest.fail('no new or duplicate intake'),publish=lambda:None)
    schedule=json.loads(schedule_path.read_text());state=json.loads(state_path.read_text())
    assert 'status' not in schedule[rid]
    assert schedule[rid]['current_official_row_hold']['status']=='SCOPE_HOLD'
    assert autopilot.race_status(runtime,rid,schedule[rid],state,when)['state']==expected
    assert path.read_bytes()==original


def test_advisory_transition_never_clears_an_unrelated_existing_hold(runtime):
    cache={};assert create(runtime,cache);tick(runtime,cache)
    rid='KM-JRA-TKY-20261108-R01';schedule_path=runtime/f'runtime/jra_race_day_plan/{DAY}.schedule.json'
    schedule=json.loads(schedule_path.read_text())
    schedule[rid].update(status='NUMERICAL_HOLD',scope_hold_reason='FORMAL_NUMERICAL_EVIDENCE_UNAVAILABLE',
        current_official_row_hold={'status':'SCOPE_HOLD','reason':'OFFICIAL_RACE_TYPE_UNKNOWN'})
    schedule_path.write_text(json.dumps(schedule))
    final=runtime/'runtime/final_artifacts'/(rid+'.json');final.parent.mkdir(parents=True)
    final.write_text(json.dumps({'sha256':'f'*64}));cache['days']['東京'][1][0]['surface']=None
    tick(runtime,cache,dispatch=lambda *a:pytest.fail('fixture before window'))
    after=json.loads(schedule_path.read_text())[rid]
    assert after['status']=='NUMERICAL_HOLD' and after['scope_hold_reason']=='FORMAL_NUMERICAL_EVIDENCE_UNAVAILABLE'



def test_prebootstrap_rebase_time_cannot_backdate_plan_observation(runtime,monkeypatch):
    start=dt.datetime.fromisoformat(DAY+'T08:00:00+09:00')
    after=dt.datetime.fromisoformat(DAY+'T08:01:00+09:00')
    clock=[start];elapsed=[0.0]
    class Clock(dt.datetime):
        @classmethod
        def now(cls,tz=None):return clock[0]
    monkeypatch.setattr(autopilot._dt,'datetime',Clock)
    monkeypatch.setattr(autopilot.time,'monotonic',lambda:elapsed[0])
    monkeypatch.delenv('GITHUB_OUTPUT',raising=False)
    def rebase(*a):clock[0]=after;elapsed[0]=60.0;return True
    monkeypatch.setattr(autopilot,'_rebase_generated',rebase)
    monkeypatch.setattr(autopilot,'resolve_meetings',lambda d:['東京','京都'])
    monkeypatch.setattr(autopilot,'resolve_day',lambda d,v:card(v,jump=v=='京都'))
    monkeypatch.setattr(autopilot,'_commit',lambda *a:None)
    monkeypatch.setattr(autopilot,'request_postresult_worker',lambda *a,**k:None)
    monkeypatch.setattr(autopilot,'_gh_dispatch',lambda *a:pytest.fail('fixture before window'))
    assert autopilot.main(['--repo-root',str(runtime),'--date',DAY,'--all-races-default',
                          '--loop-until','17:30','--max-loop-seconds','0'])==0
    plan=read_plan(runtime)
    assert plan['automatic_generation']['observed_at']==after.isoformat()
    assert plan['cohort']['registered_at']==after.isoformat()


@pytest.mark.parametrize('old_origin',[None,'schedule','state'])
def test_scope_projection_preserves_observed_temporal_history_without_new_miss(runtime,old_origin):
    cache={};assert create(runtime,cache)
    plan_path=runtime/f'runtime/jra_race_day_plan/{DAY}.json';original_plan=plan_path.read_bytes()
    rid='KM-JRA-KYO-20261108-R04';schedule_path=plan_path.with_name(DAY+'.schedule.json')
    old_temporal='MISSED_WINDOW' if old_origin else None
    state_path=plan_path.with_name(DAY+'.state.json')
    if old_origin=='schedule':
        schedule_path.write_text(json.dumps({rid:{'status':old_temporal,'legacy_evidence':'kept'}}))
    if old_origin=='state':
        state_path.write_text(json.dumps({rid:{'dispatch_state':'MISSED_WINDOW','claimed_at':NOW.isoformat()}},
                                        sort_keys=True,indent=1)+'\n')
        original_state=state_path.read_bytes()
    for repeat in range(2):
        tick(runtime,cache,dispatch=lambda *a:pytest.fail('fixture before intake'))
        row=json.loads(schedule_path.read_text())[rid]
        status=autopilot.race_status(runtime,rid,row,{},NOW)
        assert row['status']==status['state']=='SCOPE_HOLD'
        assert status['scope_decision']['race_type']=='JUMP'
        assert status['temporal_status']==old_temporal
        assert status['dispatch_eligibility']['eligible'] is False
        assert status['dispatch_eligibility']['blocking_stage']=='SCOPE'
        if old_origin=='schedule':assert row['legacy_evidence']=='kept'
        if old_origin=='state':assert state_path.read_bytes()==original_state
        assert plan_path.read_bytes()==original_plan
