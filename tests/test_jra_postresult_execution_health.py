"""Offline failure injection; no official URL, Runtime, or signature creation."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import urllib.error

import pytest
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime')]
import jra_postresult_health as h
import jra_static_owner_forward_oos as s
import jra_candidate_postresult_closedloop as candidate

NOW=datetime(2026,10,28,4,tzinfo=timezone.utc)


def pre(root,race=1,**changes):
    rid=f'KM-JRA-TKY-20261028-R{race:02d}'
    obj={'profile':s.PROFILE,'owner_profile':s.OWNER_PROFILE,'race_id':rid,
         'frozen_at':'2026-10-28T00:00:00+00:00','prediction_cutoff':'2026-10-28T01:00:00+00:00',
         'scheduled_post_at':'2026-10-28T02:00:00+00:00','race_date':'2026-10-28',
         'race_no':race,'meeting_key':'0520260401','policy_fingerprint':'policy',
         'production_authority':False,'candidate_only':True,'ranking':['1','2','3'],
         'market_ranking':['3','2','1'],'source_snapshot_sha256':'a'*64}
    obj.update(changes);obj['sha256']=s.sha(obj)
    path=root/'runtime/jra_static_owner_forward_oos'/rid/'pre_result.json'
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj))
    return path,obj


def isolate(monkeypatch):
    monkeypatch.setattr(s,'fingerprint',lambda root:'policy')
    monkeypatch.setattr(s.subprocess,'check_output',lambda *a,**kw:'2026-10-28T00:30:00+00:00')
    monkeypatch.setattr(candidate,'verify_official_result',lambda *a:{'top3':['1','2','3']})


def evidence():
    return {'parsed':{},'text':'MOCK RESULT VERIFIED BY ISOLATED PARSER',
            'sha256':'b'*64,'captured_at':NOW.isoformat()}


def test_static_failure_retains_race_and_stage_and_does_not_stop_other_race(tmp_path,monkeypatch):
    isolate(monkeypatch);p1,_=pre(tmp_path,1);p2,_=pre(tmp_path,2)
    originals={p:p.read_bytes() for p in [p1,p2]};calls=[]
    def fetch(day,key,race):
        calls.append(race)
        if race==1:raise ValueError('JRA_RESULT_DAY_TOKEN_NOT_FOUND')
        return evidence()
    report=s.settle_pending(tmp_path,now=NOW,fetch=fetch)
    assert calls==[1,2]
    bad,good=report['processed']
    assert bad['race_id']==p1.parent.name and bad['status']=='BLOCKED_SOURCE'
    assert bad['first_failed_stage']=='FETCH_OFFICIAL_RESULT' and not bad['persisted']
    assert good['status']=='SETTLED' and good['persisted']
    assert p2.with_name('result_evaluation.json').exists()
    assert not p1.with_name('result_evaluation.json').exists()
    assert report['execution_health']=='PARTIAL_BLOCKED' and h.health_exit_code(report)==2
    assert report['scorecard']['eligible_settled_races']==1
    assert originals=={p:p.read_bytes() for p in originals}


def test_static_all_pending_is_not_a_settlement_success(tmp_path,monkeypatch):
    isolate(monkeypatch);pre(tmp_path,1);pre(tmp_path,2)
    def pending(*args):raise candidate.PendingOfficialResult('OFFICIAL_RESULT_NOT_YET_PUBLISHED')
    report=s.settle_pending(tmp_path,now=NOW,fetch=pending)
    assert report['execution_health']=='PENDING_OFFICIAL_RESULT'
    assert report['counts']=={'PENDING_OFFICIAL_RESULT':2} and h.health_exit_code(report)==0
    assert not list(tmp_path.rglob('result_evaluation.json'))
    assert report['scorecard']['eligible_settled_races']==0


@pytest.mark.parametrize('broken',['json','hash','binding'])
def test_corrupt_existing_result_is_isolated_without_overwrite(tmp_path,monkeypatch,broken):
    isolate(monkeypatch);p1,obj=pre(tmp_path,1);pre(tmp_path,2)
    old=s.evaluate(obj,['1','2','3'],result_sha256='b'*64,observed_at=NOW.isoformat(),
        git_commit_at='2026-10-28T00:30:00+00:00')
    if broken=='hash':old['sha256']='0'*64
    if broken=='binding':old['frozen_sha256']='0'*64;old['sha256']=s.sha({k:v for k,v in old.items() if k!='sha256'})
    target=p1.with_name('result_evaluation.json');target.write_text('{' if broken=='json' else json.dumps(old))
    raw=target.read_bytes();calls=[]
    report=s.settle_pending(tmp_path,now=NOW,fetch=lambda *args:calls.append(args[-1]) or evidence())
    assert calls==[2] and target.read_bytes()==raw
    assert report['processed'][0]['status']=='BLOCKED_RESULT_INTEGRITY'
    assert report['processed'][1]['status']=='SETTLED'


def test_existing_frozen_rules_run_before_any_http(tmp_path,monkeypatch):
    isolate(monkeypatch)
    pre(tmp_path,1,profile='OLD_EXPLORATORY_POLICY')
    pre(tmp_path,2,frozen_at='2026-10-28T03:00:00+00:00')
    p,_=pre(tmp_path,3);obj=json.loads(p.read_text());obj['ranking']=['3','2','1'];p.write_text(json.dumps(obj))
    report=s.settle_pending(tmp_path,now=NOW,fetch=lambda *args:pytest.fail('UNQUALIFIED_HTTP'))
    assert [x['status'] for x in report['processed']]==['NOT_ELIGIBLE','NOT_ELIGIBLE','BLOCKED_RESULT_INTEGRITY']
    assert report['scorecard']['eligible_settled_races']==0


def test_static_immutable_conflict_does_not_remove_other_success(tmp_path,monkeypatch):
    isolate(monkeypatch);pre(tmp_path,1);pre(tmp_path,2)
    actual=s.save_immutable
    def save(path,obj):
        if 'R01' in str(path):raise ValueError('STATIC_OWNER_IMMUTABLE_RECORD_CONFLICT')
        return actual(path,obj)
    monkeypatch.setattr(s,'save_immutable',save)
    report=s.settle_pending(tmp_path,now=NOW,fetch=lambda *args:evidence())
    assert report['processed'][0]['first_failed_stage']=='SAVE_IMMUTABLE_RESULT'
    assert report['processed'][0]['status']=='BLOCKED_RESULT_INTEGRITY'
    assert report['processed'][1]['persisted'] is True


def test_static_rerun_reuses_original_without_http(tmp_path,monkeypatch):
    isolate(monkeypatch);p,_=pre(tmp_path)
    s.settle_pending(tmp_path,now=NOW,fetch=lambda *args:evidence())
    target=p.with_name('result_evaluation.json');raw=target.read_bytes()
    report=s.settle_pending(tmp_path,now=NOW,fetch=lambda *args:pytest.fail('DUPLICATE_HTTP'))
    assert report['processed'][0]['status']=='ALREADY_SETTLED' and target.read_bytes()==raw
    assert report['execution_health']=='SUCCESS_NO_NEW_SETTLEMENT'


@pytest.mark.parametrize('dead_heat',[
    {'top3':['1','2','3'],'dead_heat':True},
    {'top3':['1','2','3'],'top3_orders':[['1','2','3'],['1','3','2']]},
])
def test_static_does_not_convert_tie_representative_order_into_new_oos(tmp_path,monkeypatch,dead_heat):
    isolate(monkeypatch);p1,_=pre(tmp_path,1);p2,_=pre(tmp_path,2)
    before={p:p.read_bytes() for p in [p1,p2]}
    monkeypatch.setattr(candidate,'verify_official_result',lambda parsed,*args:
        dead_heat if parsed['race_no']==1 else {'top3':['1','2','3']})
    def fetch(day,key,race_no):
        observed=evidence();observed['parsed']={'race_no':race_no};return observed
    report=s.settle_pending(tmp_path,now=NOW,fetch=fetch)
    held,normal=report['processed']
    assert held['status']=='NOT_ELIGIBLE' and held['oos_eligible'] is False
    assert held['error_code']=='STATIC_OWNER_DEAD_HEAT_METRICS_UNSUPPORTED'
    assert held['first_failed_stage']=='EVALUATE_STATIC_OWNER_RESULT'
    assert not p1.with_name('result_evaluation.json').exists()
    assert normal['status']=='SETTLED' and p2.with_name('result_evaluation.json').exists()
    assert report['scorecard']['eligible_settled_races']==1
    assert before=={p:p.read_bytes() for p in before}


@pytest.mark.parametrize('change',[
    {'race_date':'2026-10-27'}, {'meeting_key':'0820260401'}, {'race_no':2},
])
def test_static_bound_race_identity_is_checked_before_official_http(tmp_path,monkeypatch,change):
    isolate(monkeypatch);p,_=pre(tmp_path,1,**change);raw=p.read_bytes()
    report=s.settle_pending(tmp_path,now=NOW,fetch=lambda *args:pytest.fail('CROSS_RACE_HTTP'))
    row=report['processed'][0]
    assert row['status']=='BLOCKED_RESULT_INTEGRITY' and row['first_failed_stage']=='VERIFY_RESULT_TARGET'
    assert report['scorecard']['eligible_settled_races']==0 and p.read_bytes()==raw


def test_static_budget_preserves_success_and_defers_qualified_races_to_existing_schedule(tmp_path,monkeypatch):
    isolate(monkeypatch)
    paths=[pre(tmp_path,n)[0] for n in (1,2,3)]
    original={p:p.read_bytes() for p in paths};calls=[]
    ticks=iter([0,0,180,181])
    report=s.settle_pending(tmp_path,now=NOW,budget_seconds=180,monotonic=lambda:next(ticks),
        fetch=lambda *args:calls.append(args[-1]) or evidence())
    assert calls==[1]
    assert report['counts']=={'SETTLED':1,'NOT_RUN_BUDGET':2}
    assert report['execution_health']=='PARTIAL_BUDGET' and h.health_exit_code(report)==0
    assert report['scorecard']['eligible_settled_races']==1
    assert all(row['resume_condition']=='NEXT_EXISTING_SCHEDULE' for row in report['processed'][1:])
    assert all(not paths[n].with_name('result_evaluation.json').exists() for n in (1,2))
    again=s.settle_pending(tmp_path,now=NOW,budget_seconds=180,monotonic=lambda:0,
        fetch=lambda *args:calls.append(args[-1]) or evidence())
    assert calls==[1,2,3] and again['scorecard']['eligible_settled_races']==3
    assert original=={p:p.read_bytes() for p in original}


def test_static_zero_budget_is_not_no_due_or_an_eligibility_change(tmp_path,monkeypatch):
    isolate(monkeypatch);pre(tmp_path,1,profile='OLD_EXPLORATORY_POLICY');pre(tmp_path,2)
    report=s.settle_pending(tmp_path,now=NOW,budget_seconds=0,monotonic=lambda:0,
        fetch=lambda *args:pytest.fail('BUDGET_HTTP'))
    assert [row['status'] for row in report['processed']]==['NOT_ELIGIBLE','NOT_RUN_BUDGET']
    assert report['execution_health']=='PARTIAL_BUDGET' and report['scorecard']['eligible_settled_races']==0
    assert report['processed'][0]['error_code']=='STATIC_OWNER_WRONG_POLICY_COHORT'
    assert 'oos_eligible' not in report['processed'][1]


def test_new_race_is_not_starved_by_old_source_failure_or_invalid_id_date(tmp_path,monkeypatch):
    isolate(monkeypatch)
    def dated(day,folder_day=None):
        p,obj=pre(tmp_path)
        compact=folder_day or day.replace('-','')
        rid='KM-JRA-TKY-'+compact+'-R01'
        obj.update(race_id=rid,race_date=day,frozen_at=day+'T00:00:00+00:00',
            prediction_cutoff=day+'T01:00:00+00:00',scheduled_post_at=day+'T02:00:00+00:00')
        obj['sha256']=s.sha({k:v for k,v in obj.items() if k!='sha256'})
        target=p.parent.parent/rid/p.name;target.parent.mkdir();target.write_text(json.dumps(obj))
        p.unlink();p.parent.rmdir();return target
    old=dated('2026-10-24');new=dated('2026-10-31');invalid=dated('2026-10-24','20261340')
    originals={p:p.read_bytes() for p in (old,new,invalid)}
    def witness(*args,**kwargs):
        reference=args[0][-1]
        return ('2026-10-31' if '20261031' in reference else '2026-10-24')+'T00:30:00+00:00'
    monkeypatch.setattr(s.subprocess,'check_output',witness)
    calls=[];now=datetime(2026,11,1,4,tzinfo=timezone.utc)
    def fetch(day,key,race):
        calls.append(day)
        if day=='2026-10-24':raise ValueError('JRA_RESULT_DAY_TOKEN_NOT_FOUND')
        observed=evidence();observed['captured_at']=now.isoformat();return observed
    ticks=iter([0,0,180])
    report=s.settle_pending(tmp_path,now=now,budget_seconds=180,monotonic=lambda:next(ticks),fetch=fetch)
    assert calls==['2026-10-31']
    assert [r['race_id'] for r in report['processed']]==[new.parent.name,old.parent.name,invalid.parent.name]
    assert [r['status'] for r in report['processed']]==['SETTLED','NOT_RUN_BUDGET','BLOCKED_RESULT_INTEGRITY']
    assert new.with_name('result_evaluation.json').exists() and not old.with_name('result_evaluation.json').exists()
    assert originals=={p:p.read_bytes() for p in originals}


def test_candidate_scheduled_failure_is_not_hidden_by_other_success(tmp_path,monkeypatch):
    now=datetime.now(timezone.utc)
    for number in [1,2]:
        d=tmp_path/f'runtime/source_candidate_oos/KM-JRA-TKY-20261028-R{number:02d}'
        d.mkdir(parents=True);(d/'pre_result.json').write_text(json.dumps({'scheduled_post_at':(now-timedelta(minutes=2)).isoformat(),'sha256':'frozen'}))
    def process(root,rid):
        if rid.endswith('R01'):raise ValueError('JRA_RESULT_DAY_TOKEN_NOT_FOUND')
        return 'SETTLED_RECOMMENDATION'
    monkeypatch.setattr(candidate,'process',process)
    out=tmp_path/'health.json'
    assert candidate.main(['--repo-root',str(tmp_path),'--health-out',str(out)])==2
    report=json.loads(out.read_text());assert len(report['processed'])==2
    assert report['counts']=={'BLOCKED_SOURCE':1,'SETTLED':1}
    assert report['processed'][0]['first_failed_stage']=='PROCESS_CANDIDATE_RESULT'


def report_file(path,lane,rows):
    path.write_text(json.dumps(h.build_execution_health(lane,rows)));return str(path)


def test_aggregate_does_not_count_request_or_zero_oos_as_verified_settlement(tmp_path):
    f=report_file(tmp_path/'p.json','PRODUCTION',[{'race_id':'R1','status':'RESULT_REQUEST_WRITTEN','persisted':True}])
    b=tmp_path/'bvi.json';b.write_text(json.dumps({'race_failures':[],'eligible_settled_races':0}))
    report=h.aggregate_execution_health({'production':f},{'production':'0','bvi':'0'},bvi_report=b)
    assert report['execution_health']=='PENDING_OFFICIAL_RESULT'
    assert report['counts']['RESULT_REQUEST_WRITTEN']==1
    assert report['signed_result_receipt_verified_by_health'] is False
    assert report['processed'][1]['new_oos_credit_from_execution_health']==0


def test_aggregate_catches_swallowed_bvi_failure_and_unexpected_lane_exit(tmp_path):
    f=report_file(tmp_path/'c.json','CANDIDATE',[{'race_id':'R1','status':'ALREADY_SETTLED'}])
    b=tmp_path/'b.json';b.write_text(json.dumps({'race_failures':[{'race_id':'R2','reason':'BVI_FORWARD_FROZEN_HASH_INVALID'}]}))
    report=h.aggregate_execution_health({'candidate':f},{'candidate':'0','bvi':'0'},bvi_report=b)
    assert report['execution_health']=='PARTIAL_BLOCKED' and h.health_exit_code(report)==2
    assert report['processed'][1]['race_id']=='R2'
    report=h.aggregate_execution_health({'candidate':f},{'candidate':'2'})
    assert h.health_exit_code(report)==2 and report['processed'][-1]['status']=='FAILURE_INTERNAL'


def test_missing_health_and_failed_persistence_are_not_success(tmp_path):
    report=h.aggregate_execution_health({'production':str(tmp_path/'absent')},{'production':'0'},step_outcomes={'persistence':'failure'})
    assert h.health_exit_code(report)==2 and report['material_failure_count']==2


def test_unhandled_fixed_bvi_typeerror_is_visible_without_changing_pinned_code(tmp_path):
    f=report_file(tmp_path/'p.json','PRODUCTION',[{'race_id':'R1','status':'RESULT_REQUEST_WRITTEN','persisted':True}])
    b=tmp_path/'bvi.json';b.write_text('')
    report=h.aggregate_execution_health({'production':f},{'production':'0','bvi':'1'},bvi_report=b)
    assert report['execution_health']=='PARTIAL_BLOCKED' and h.health_exit_code(report)==2
    row=report['processed'][-1]
    assert row['first_failed_stage']=='BVI_ENV_SETTLEMENT'
    assert row['status']=='FAILURE_INTERNAL' and row['upstream_stderr_ref'].endswith('bvi.stderr.txt')
    assert report['processed'][0]['persisted'] is True


def git(root,*args):
    return subprocess.check_output(['git',*args],cwd=root,text=True).strip()


def test_same_blocked_100_observations_make_one_actual_git_commit(tmp_path):
    git(tmp_path,'init','--initial-branch=main');git(tmp_path,'config','user.name','test');git(tmp_path,'config','user.email','test@example.invalid')
    signed=tmp_path/'signed-original.json';signed.write_bytes(b'IMMUTABLE ORIGINAL BYTES\n')
    git(tmp_path,'add','signed-original.json');git(tmp_path,'commit','-m','baseline')
    deltas=[];before=1;first=None
    for index in range(100):
        row={'race_id':'R1','status':'BLOCKED_SOURCE','error_code':'HTTP403','persisted':False,
             'source_fault':{'http_status':403,'url':'https://www.jra.go.jp/MOCK','attempt':index+1,
                 'response_headers':{'Date':str(index)},'observed_at':str(index)},
             'source_ref':'a'*64,'first_observed_at':str(index)}
        report=h.build_execution_health('STATIC_OWNER',[row],observed_at=str(index))
        target=tmp_path/'health.json';h.write_execution_health(target,report)
        if first is None:first=target.read_bytes()
        assert target.read_bytes()==first
        git(tmp_path,'add','health.json')
        if subprocess.run(['git','diff','--cached','--quiet'],cwd=tmp_path).returncode:
            git(tmp_path,'commit','-m','first observation only')
        count=int(git(tmp_path,'rev-list','--count','HEAD'));deltas.append(count-before);before=count
    assert deltas==[1]+[0]*99 and signed.read_bytes()==b'IMMUTABLE ORIGINAL BYTES\n'


@pytest.mark.parametrize('field,value',[
    ('source_ref','b'*64),('dispatch_claim_token','claim'),('acknowledgement',{'run_id':'new'}),
    ('source_freeze_at','2026-10-28T00:00:00Z'),('final_receipt_sha256','f'*64),
    ('signature_revoked',True),('temporal_eligible',False)])
def test_material_fields_are_never_observation_clock_noise(tmp_path,field,value):
    old=h.build_execution_health('STATIC_OWNER',[{'race_id':'R1','status':'BLOCKED_SOURCE'}])
    target=tmp_path/'h.json';h.write_execution_health(target,old);raw=target.read_bytes()
    new=deepcopy(old);new['processed'][0][field]=value;h.write_execution_health(target,new)
    assert target.read_bytes()!=raw


def test_public_http_diagnostics_reuse_pr344_without_cookie_or_auth(tmp_path):
    exc=urllib.error.HTTPError('https://www.jra.go.jp/MOCK',403,'Forbidden',
        {'Date':'first','Set-Cookie':'PRIVATE','Authorization':'PRIVATE'},None)
    exc.official_request={'url':exc.url,'method':'POST','phase':'READ_BODY','attempt':1}
    exc.official_navigation=[{'url':exc.url,'fetched_at':'first','raw_sha256':'a'*64,
        'response_headers':{'Date':'first','Cookie':'PRIVATE'}}]
    row=h.failure_row('R1',exc,'FETCH_OFFICIAL_RESULT')
    assert row['source_fault']['http_status']==403
    assert row['source_fault']['source_accepted'] is False
    assert 'PRIVATE' not in json.dumps(row)
    p=tmp_path/'health.json';report=h.build_execution_health('STATIC_OWNER',[row]);h.write_execution_health(p,report);old=p.read_bytes()
    changed=deepcopy(report);changed['processed'][0]['official_navigation'][0]['fetched_at']='later'
    changed['processed'][0]['official_navigation'][0]['response_headers']['Date']='later'
    h.write_execution_health(p,changed);assert p.read_bytes()==old
    changed['processed'][0]['official_navigation'][0]['raw_sha256']='b'*64
    h.write_execution_health(p,changed);assert p.read_bytes()!=old


def test_workflows_preserve_good_lanes_then_upload_and_enforce_health():
    for name in ['km-jra-candidate-auto-postresult-closedloop.yml','km-jra-production-postresult.yml']:
        text=(ROOT/'.github/workflows'/name).read_text();obj=yaml.safe_load(text)
        steps=next(iter(obj['jobs'].values()))['steps']
        ids={x.get('id'):x for x in steps if x.get('id')}
        assert 'continue-on-error' not in text
        assert '--health-out runtime_out/postresult/' in ids['execute']['run']
        assert '|| status=$?' in ids['execute']['run']
        assert '!cancelled()' in ids['persist']['if']
        assert steps[-1]['run']=='test "${{ steps.health.outputs.exit_code }}" = "0"'
        assert steps[-2]['uses']=='actions/upload-artifact@v4'
        assert steps[-2]['if']=='always()' and ids['health']['if']=='always()'
