"""Local Git and mocked official responses; no public HTTP or Runtime calls."""
import datetime as dt
from email.message import Message
import json
from pathlib import Path
import subprocess
import sys
from urllib.error import HTTPError

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime/jra_source_runtime'))
import jra_race_day_autopilot as a

DATE='2026-10-31'
NOW=dt.datetime(2026,10,31,10,0,tzinfo=a.JST)
RID='KM-JRA-TKY-20261031-R01'
RACES=[{'race_no':1,'post_time':'10:40','title':'Official fixture'}]


@pytest.fixture(autouse=True)
def no_connected_cli(monkeypatch):
    monkeypatch.delenv('GH_TOKEN',raising=False)
    monkeypatch.delenv('GITHUB_TOKEN',raising=False)


def denied(index=0,code=403):
    headers=Message();headers['Date']=f'Sat, 31 Oct 2026 01:{index//60:02d}:{index%60:02d} GMT'
    exc=HTTPError('https://www.jra.go.jp/keiba/calendar2026/2026/10/1031.html',code,
                  'Forbidden' if code==403 else 'Server error',headers,None)
    exc.official_request={'url':exc.url,'method':'GET','phase':'CONNECT_TLS_OR_RESPONSE_HEADERS','attempt':index+1}
    return exc


def fail(exc):
    def raise_it(*args,**kwargs):raise exc
    return raise_it


def git(root,*args):
    result=subprocess.run(['git',*args],cwd=root,text=True,capture_output=True)
    assert result.returncode==0,result.stderr
    return result.stdout.strip()


def repository(tmp_path):
    remote=tmp_path/'remote.git';git(tmp_path,'init','--bare','--initial-branch=main',str(remote))
    worker=tmp_path/'worker';git(tmp_path,'clone',str(remote),str(worker))
    git(worker,'config','user.name','test');git(worker,'config','user.email','test@example.invalid')
    (worker/'initial').write_text('baseline')
    git(worker,'add','initial');git(worker,'commit','-m','baseline');git(worker,'push','-u','origin','main')
    return remote,worker


def failure_tick(root,index=0,code=403):
    return a.tick(root,DATE,NOW+dt.timedelta(seconds=index),default_all=True,cache={},
        meetings=fail(denied(index,code)),resolver_runs=[],dispatch=lambda *args:pytest.fail('DENIED_DISPATCH'))


def test_t1_one_actual_git_commit_for_100_equivalent_403_observations(tmp_path):
    remote,worker=repository(tmp_path);counts=[];first=None
    for index in range(100):
        rows=failure_tick(worker,index)
        assert rows[0]['source_fault']['http_status']==403
        assert rows[0]['source_fault']['official_non_meeting_proven'] is False
        a._commit(worker,DATE)
        counts.append(int(git(remote,'rev-list','--count','main')))
        path=worker/f'runtime/jra_race_day_status/{DATE}.json'
        if first is None:first=path.read_bytes()
        assert path.read_bytes()==first
    assert counts==[2]*100  # baseline + first real failure revision, then zero
    assert len(git(remote,'log','--format=%s','main').splitlines())==2


def test_t2_fresh_scheduled_run_recovers_without_a_permanent_denial_hold(tmp_path):
    remote,worker=repository(tmp_path);failure_tick(worker);a._commit(worker,DATE)
    sent=[]
    out=a.tick(worker,DATE,NOW,default_all=True,cache={},meetings=lambda d:['東京'],
        resolve=lambda *args:('official-key',RACES),dispatch=lambda *args:sent.append(args),
        publish=lambda:a._commit(worker,DATE),resolver_runs=[])
    assert sent and out[0]['status']=='DISPATCH'
    schedule=json.loads((worker/f'runtime/jra_race_day_plan/{DATE}.schedule.json').read_text())
    assert DATE+':ALL' not in schedule and schedule[RID]['post']=='2026-10-31T10:40:00+09:00'
    again=a.tick(worker,DATE,NOW,default_all=True,cache={},meetings=lambda d:['東京'],
        resolve=lambda *args:('official-key',RACES),dispatch=lambda *args:sent.append(args),resolver_runs=[])
    assert len(sent)==1 and again[0]['status']=='ALREADY_DISPATCHED'


def test_t3_a_different_http_failure_and_real_claim_metadata_remain_material(tmp_path):
    remote,worker=repository(tmp_path)
    failure_tick(worker);a._commit(worker,DATE)
    failure_tick(worker,1,500);a._commit(worker,DATE)
    assert int(git(remote,'rev-list','--count','main'))==3
    path=worker/f'runtime/jra_race_day_plan/{DATE}.state.json'
    for name,value in [('claimed_at','2026-10-31T10:01:00+09:00'),('dispatched_at','2026-10-31T10:02:00+09:00'),
                       ('acknowledgement',{'run_id':'real-fixture'}),('source_freeze_at','2026-10-31T09:58:00+09:00'),
                       ('final_receipt_sha256','a'*64),('temporal_eligible',False)]:
        state=json.loads(path.read_text());state.setdefault(RID,{})[name]=value
        path.write_text(json.dumps(state));before=int(git(remote,'rev-list','--count','main'))
        a._commit(worker,DATE)
        assert int(git(remote,'rev-list','--count','main'))==before+1,name


def frozen_clock(monkeypatch,at=NOW):
    class Clock(dt.datetime):
        @classmethod
        def now(cls,tz=None):return at.astimezone(tz) if tz else at.replace(tzinfo=None)
    monkeypatch.setattr(a._dt,'datetime',Clock)


def worker_main(root,monkeypatch,meetings,*,at=NOW,budget=1800,resolve=None):
    frozen_clock(monkeypatch,at)
    monkeypatch.setattr(a,'resolve_meetings',meetings)
    monkeypatch.setattr(a,'resolve_day',resolve or (lambda *args:('official-key',RACES)))
    monkeypatch.setattr(a,'_rebase_generated',lambda *args:True)
    monkeypatch.setattr(a,'_commit',lambda *args:None)
    monkeypatch.setattr(a.time,'sleep',lambda *args:pytest.fail('UNEXPECTED_WORKER_RETRY'))
    output=root/'outputs';monkeypatch.setenv('GITHUB_OUTPUT',str(output))
    result=a.main(['--repo-root',str(root),'--date',DATE,'--all-races-default',
                   '--loop-until','17:30','--max-loop-seconds',str(budget)])
    return result,output.read_text()


def test_t4_confirmed_nonmeeting_cli_and_publish_only_stop_cleanly_without_files(tmp_path,monkeypatch):
    result,output=worker_main(tmp_path,monkeypatch,lambda date:[])
    assert result==0 and 'continue_worker=false' in output
    assert not list((tmp_path/'runtime').rglob('*.json'))
    assert a.main(['--repo-root',str(tmp_path),'--date',DATE,'--publish-only'])==0
    assert not list((tmp_path/'runtime').rglob('*.json'))


def test_t5_failure_or_invalid_response_never_becomes_no_meetings(tmp_path):
    for index,response in enumerate([None,fail(denied())]):
        root=tmp_path/str(index)
        rows=a.tick(root,DATE,NOW,default_all=True,
                    meetings=response if callable(response) else lambda d:response,
                    resolver_runs=[],dispatch=lambda *args:pytest.fail('NO_SOURCE_DISPATCH'))
        assert rows and rows[0]['status'].startswith('OFFICIAL_CALENDAR_UNAVAILABLE')
        assert rows[0]['source_fault']['official_non_meeting_proven'] is False
        assert (root/f'runtime/jra_race_day_status/{DATE}.json').is_file()


def test_t1_worker_access_is_once_and_workflow_denial_cannot_chain(tmp_path,monkeypatch):
    calls=[]
    def meetings(date):calls.append(date);raise denied()
    result,output=worker_main(tmp_path,monkeypatch,meetings)
    assert result==0 and calls==[DATE] and 'continue_worker=false' in output
    import yaml
    workflow=yaml.safe_load((ROOT/'.github/workflows/km-jra-race-day-autopilot.yml').read_text())
    steps=workflow['jobs']['autopilot']['steps']
    day=next(s for s in steps if s.get('id')=='day')
    chain=next(s for s in steps if s.get('name','').startswith('Continue with fresh worker'))
    assert day['name'].startswith('Plan every official race')
    assert "steps.day.outputs.continue_worker == 'true'" in chain['if']
    assert "steps.day.outcome == 'success'" in chain['if']


def plan(root):
    path=root/f'runtime/jra_race_day_plan/{DATE}.json';path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'entries':[{'venue':'東京','races':[1]},{'venue':'京都','races':[1]}]}))


def test_t6_t7_denied_venue_does_not_stop_healthy_dispatch_or_retry_inside_worker(tmp_path):
    plan(tmp_path);calls=[];sent=[];cache={}
    def resolve(date,venue):
        calls.append(venue)
        if venue=='京都':raise denied()
        return 'official-key',RACES
    for i in range(3):
        cache,_=a._refresh_worker_cache(cache,NOW,NOW+dt.timedelta(minutes=i))
        out=a.tick(tmp_path,DATE,NOW,cache=cache,resolve=resolve,
                   dispatch=lambda *args:sent.append(args),resolver_runs=[])
    assert calls.count('京都')==calls.count('東京')==1
    assert len(sent)==1 and sent[0][0]=='東京'
    assert any(r['source_fault']['http_status']==403 for r in out if r.get('source_fault'))


def test_t7_healthy_plan_keeps_bounded_handoff_when_only_one_venue_is_denied(tmp_path,monkeypatch):
    plan(tmp_path)
    path=tmp_path/f'runtime/jra_race_day_plan/{DATE}.json'
    config=json.loads(path.read_text());config['entries'][0]['races'].append(2);path.write_text(json.dumps(config))
    monkeypatch.setattr(a,'_gh_dispatch',lambda *args:{'run_id':'mock'})
    def resolve(date,venue):
        if venue=='京都':raise denied()
        return 'official-key',RACES+[{'race_no':2,'post_time':'11:40','title':'Healthy future race'}]
    result,output=worker_main(tmp_path,monkeypatch,lambda d:['東京','京都'],budget=0,resolve=resolve)
    assert result==0 and 'continue_worker=true' in output


@pytest.mark.parametrize('remote_change',['ack','claim','intent'])
def test_t9_publish_race_recheck_prevents_duplicate_dispatch(tmp_path,remote_change):
    path=tmp_path/f'runtime/jra_race_day_plan/{DATE}.json';path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'entries':[{'venue':'東京','races':[1]}]}))
    state_path=path.with_name(DATE+'.state.json');sent=[]
    def publish():
        state=json.loads(state_path.read_text())
        if remote_change=='ack':state[RID].update(dispatched_at=NOW.isoformat(),dispatch_state='DISPATCH_ACKNOWLEDGED')
        elif remote_change=='claim':state[RID]['dispatch_claim_token']='another-published-worker'
        else:
            target=tmp_path/'runtime/jra_formal_intents'/(RID+'-LIVE-R1.json')
            target.parent.mkdir(parents=True);target.write_text('{}')
        state_path.write_text(json.dumps(state))
    out=a.tick(tmp_path,DATE,NOW,resolve=lambda *args:('official',RACES),resolver_runs=[],
               publish=publish,dispatch=lambda *args:sent.append(args))
    assert not sent and out[0]['status']=='ALREADY_DISPATCHED'


def test_t9_concurrent_equivalent_failure_preserves_one_remote_revision(tmp_path):
    remote,first=repository(tmp_path);second=tmp_path/'second';git(tmp_path,'clone',str(remote),str(second))
    git(second,'config','user.name','test');git(second,'config','user.email','test@example.invalid')
    failure_tick(first,0);failure_tick(second,1)
    a._commit(first,DATE);a._commit(second,DATE)
    assert int(git(remote,'rev-list','--count','main'))==2
    assert not (second/'.git/rebase-merge').exists()


def test_t13_claim_publication_cannot_send_after_existing_window_closes(tmp_path,monkeypatch):
    path=tmp_path/f'runtime/jra_race_day_plan/{DATE}.json';path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'entries':[{'venue':'東京','races':[1]}]}));clock=[0];sent=[]
    monkeypatch.setattr(a.time,'monotonic',lambda:clock[0])
    def publish():clock[0]=601  # ten minute lead remaining to window close
    out=a.tick(tmp_path,DATE,NOW,resolve=lambda *args:('official',RACES),resolver_runs=[],
        publish=publish,dispatch=lambda *args:sent.append(args))
    assert not sent and out[0]['status']=='MISSED_WINDOW'
    state=json.loads(path.with_name(DATE+'.state.json').read_text())
    assert state[RID]['temporal_eligible'] is False and not state[RID]['retry_eligible']


def test_t13_worker_budget_handoff_never_exceeds_day_deadline(tmp_path,monkeypatch):
    result,output=worker_main(tmp_path,monkeypatch,lambda d:['東京'],
        at=NOW.replace(hour=17,minute=30),budget=0)
    assert result==0 and 'continue_worker=false' in output


def test_t8_t14_existing_final_readback_and_result_handoff_survive_calendar_denial(tmp_path,monkeypatch):
    schedule=tmp_path/f'runtime/jra_race_day_plan/{DATE}.schedule.json';schedule.parent.mkdir(parents=True)
    schedule.write_text(json.dumps({RID:{'post':'2026-10-31T09:00:00+09:00','venue':'東京','race_no':1}}))
    final=tmp_path/'runtime/final_artifacts'/(RID+'.json');final.parent.mkdir(parents=True)
    frozen={'race_id':RID,'sha256':'a'*64,'final_receipt_sha256':'b'*64,
            'scheduled_post_at':'2026-10-31T09:00:00+09:00',
            'final_ticket':{'tickets':[{'bet_type':'EXACTA','selection':[1,2],'stake':100}],
                            'total_investment':100,'no_bet':False}}
    raw=json.dumps(frozen).encode();final.write_bytes(raw)
    sends=[];original=a.request_postresult_worker
    def result_worker(root,date,now,*,publish):
        return original(root,date,now,publish=publish,send=lambda:sends.append(date))
    monkeypatch.setattr(a,'request_postresult_worker',result_worker)
    result,output=worker_main(tmp_path,monkeypatch,fail(denied()))
    assert result==0 and sends==[DATE] and 'continue_worker=false' in output
    row=next(r for r in json.loads((tmp_path/f'runtime/jra_race_day_status/{DATE}.json').read_text())['races'] if r['race_id']==RID)
    assert row['state']=='FINAL' and row['immutable_final_sha256']=='a'*64
    assert row['ticket_count']==1 and final.read_bytes()==raw


def test_t6_all_calendar_denied_keeps_only_approved_independent_routing(tmp_path,monkeypatch):
    path=tmp_path/f'runtime/jra_race_day_plan/{DATE}.json';path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'all_races':True,'entries':[{'venue':'東京','races':[1,2]}]}))
    schedule={}
    for number,time in [(1,'10:40'),(2,'11:40')]:
        schedule[f'KM-JRA-TKY-20261031-R{number:02d}']={
            'post':f'{DATE}T{time}:00+09:00','venue':'東京','race_no':number,'title':'Existing approved target'}
    path.with_name(DATE+'.schedule.json').write_text(json.dumps(schedule))
    calls=[];sent=[]
    def meetings(date):calls.append(date);raise denied()
    monkeypatch.setattr(a,'_gh_dispatch',lambda *args:sent.append(args) or {'run_id':'fresh-canonical-resolver-only'})
    result,output=worker_main(tmp_path,monkeypatch,meetings,budget=0,
        resolve=lambda *args:pytest.fail('DENIED_CALENDAR_MUST_NOT_BE_RETRIED_LOCALLY'))
    assert result==0 and calls==[DATE] and len(sent)==1
    assert sent[0][:2]==('東京',1) and 'continue_worker=true' in output
    saved=json.loads(path.with_name(DATE+'.schedule.json').read_text())
    assert saved[RID]['routing_basis']=='EXISTING_APPROVED_PLAN_FRESH_RESOLVER_REQUIRED'
    assert saved[RID]['source_accepted'] is False
    assert not (tmp_path/'runtime/final_artifacts').exists()
    assert not (tmp_path/'runtime/executions').exists()


def test_t6_a_stale_schedule_alone_cannot_authorize_dispatch_or_chaining(tmp_path,monkeypatch):
    path=tmp_path/f'runtime/jra_race_day_plan/{DATE}.schedule.json';path.parent.mkdir(parents=True)
    path.write_text(json.dumps({RID:{'post':f'{DATE}T10:40:00+09:00','venue':'東京','race_no':1,
        'dispatch_window_close':f'{DATE}T10:10:00+09:00'}}))
    monkeypatch.setattr(a,'_gh_dispatch',lambda *args:pytest.fail('STALE_SCHEDULE_DISPATCH'))
    result,output=worker_main(tmp_path,monkeypatch,fail(denied()))
    assert result==0 and 'continue_worker=false' in output


def test_t3_all_settled_and_acknowledged_targets_do_not_chain(tmp_path,monkeypatch):
    final=tmp_path/'runtime/final_artifacts'/(RID+'.json');final.parent.mkdir(parents=True)
    final.write_text(json.dumps({'race_id':RID,'scheduled_post_at':f'{DATE}T10:40:00+09:00'}))
    result=tmp_path/'runtime/results'/(RID+'.json');result.parent.mkdir(parents=True)
    result.write_text(json.dumps({'race_id':RID,'settlement':{'status':'SETTLED'}}))
    before=(final.read_bytes(),result.read_bytes())
    code,output=worker_main(tmp_path,monkeypatch,lambda d:['東京'],at=NOW.replace(hour=11,minute=30))
    assert code==0 and 'continue_worker=false' in output
    assert (final.read_bytes(),result.read_bytes())==before


def test_t14_non_navigation_holds_are_not_hidden_by_an_existing_final(tmp_path):
    final=tmp_path/'runtime/final_artifacts'/(RID+'.json');final.parent.mkdir(parents=True)
    raw=b'{"race_id":"KM-JRA-TKY-20261031-R01","sha256":"frozen"}'
    final.write_bytes(raw)
    for hold in ('HOLD_PREREGISTRATION_INTEGRITY','NOT_ON_OFFICIAL_CARD'):
        row=a.race_status(tmp_path,RID,{'status':hold},{},NOW)
        assert row['state']==hold and 'immutable_final_sha256' not in row
    assert final.read_bytes()==raw


def test_t6_cohort_registration_is_not_a_new_formal_intake_when_calendar_is_denied(tmp_path):
    from jra_race_day_registration import build_registrations,persist_registrations,sha
    authority=json.loads((ROOT/'profiles/KM_FAMILY_CURRENT_AUTHORITY_20261012_R51.json').read_text())
    discovery={'status':'DISCOVERED','race_date':DATE,'venues':[{'venue':'東京','venue_id':'TKY',
        'meeting_key':'0520260401','races':[{'race_no':1,'post_time':'10:40','field_size':3,
        'surface':'芝','distance_m':1600,'raw':'MOCK ROUTING ONLY NOT OFFICIAL SOURCE'}]}]}
    config,records=build_registrations(discovery,authority,observed_at=NOW.isoformat())
    config['all_races']=True;config['plan_sha256']=sha({k:v for k,v in config.items() if k!='plan_sha256'})
    for record in records.values():
        record['plan_sha256']=config['plan_sha256'];record['sha256']=sha({k:v for k,v in record.items() if k!='sha256'})
    persist_registrations(tmp_path,config,records)
    schedule=tmp_path/f'runtime/jra_race_day_plan/{DATE}.schedule.json'
    schedule.write_text(json.dumps({RID:{'post':f'{DATE}T10:40:00+09:00','venue':'東京','race_no':1}}))
    before={p:p.read_bytes() for p in (tmp_path/'runtime/jra_race_registrations').rglob('*.json')}
    out=a.tick(tmp_path,DATE,NOW,meetings=fail(denied()),resolver_runs=[],
        resolve=lambda *args:pytest.fail('NO_LOCAL_CALENDAR_RETRY'),dispatch=lambda *args:None)
    row=next(r for r in json.loads((tmp_path/f'runtime/jra_race_day_status/{DATE}.json').read_text())['races'] if r['race_id']==RID)
    assert row['plan_registration_verified'] is True and row['registered_intake'] is False
    assert row['fresh_source_accepted'] is False
    index=json.loads((tmp_path/f'runtime/jra_race_day_status/{DATE}.json').read_text())
    assert index['cohort_metrics']['registered_intakes']==0
    assert before=={p:p.read_bytes() for p in before}
    assert not (tmp_path/'runtime/executions').exists()


@pytest.mark.parametrize('failure',['add','diff','commit','ahead'])
def test_t9_git_failure_cannot_be_reported_as_published_or_send_a_resolver(tmp_path,monkeypatch,failure):
    remote,worker=repository(tmp_path)
    path=worker/f'runtime/jra_race_day_plan/{DATE}.json';path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'entries':[{'venue':'東京','races':[1]}]}))
    actual_run=a.subprocess.run;commands=[];sent=[]
    def faulty(command,*args,**kwargs):
        commands.append(command)
        target=(failure=='add' and command[:2]==['git','add'] or
                failure=='diff' and command[:4]==['git','diff','--cached','--quiet'] or
                failure=='commit' and command[:2]==['git','commit'] or
                failure=='ahead' and command[:2]==['git','rev-list'])
        if target:return subprocess.CompletedProcess(command,128,'','injected Git publication failure')
        if failure=='ahead' and command[:4]==['git','diff','--cached','--quiet']:
            return subprocess.CompletedProcess(command,0,'','')
        return actual_run(command,*args,**kwargs)
    monkeypatch.setattr(a.subprocess,'run',faulty)
    out=a.tick(worker,DATE,NOW,resolve=lambda *args:('official',RACES),resolver_runs=[],
        publish=lambda:a._commit(worker,DATE),dispatch=lambda *args:sent.append(args))
    assert sent==[] and out[0]['status']=='CLAIM_PUBLISH_FAILED_NO_SEND'
    state=json.loads(path.with_name(DATE+'.state.json').read_text())
    assert state[RID]['dispatch_state']=='CLAIM_PUBLISH_FAILED_NO_SEND'
    assert 'dispatched_at' not in state[RID]
    assert not any(c[:2]==['git','push'] for c in commands)
    monkeypatch.setattr(a.subprocess,'run',actual_run)
    assert int(git(remote,'rev-list','--count','main'))==1
    assert not (worker/'runtime/executions').exists()
