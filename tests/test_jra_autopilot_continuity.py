import datetime as dt
import json
import sys
import subprocess
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime/jra_source_runtime'))
from jra_race_day_autopilot import tick,merge_dispatch_state,loop_finished,_commit
from jra_race_day_resolver import JST


def test_all_36_races_continue_after_one_api_failure(tmp_path):
    races=[{'race_no':i,'post_time':f'{9+i//2:02d}:{i%2*30:02d}','title':f'R{i}'} for i in range(1,13)]
    sent=[]
    failed=False
    def dispatch(v,n,d,k):
        nonlocal failed
        if v=='東京' and n==3 and not failed:
            failed=True
            raise subprocess.TimeoutExpired('gh',30)
        sent.append((v,n))
    errors=[]
    for minute in range(8*60,17*60,2):
        now=dt.datetime(2026,10,12,minute//60,minute%60,tzinfo=JST)
        out=tick(tmp_path,'2026-10-12',now,default_all=True,
                 meetings=lambda d:['東京','京都','中山'],resolve=lambda d,v:('x',races),dispatch=dispatch)
        errors.extend(x for x in out if x['status']=='DISPATCH_FAILED')
    assert failed and len(errors)==1
    assert len(sent)==len(set(sent))==36
    assert len(json.loads((tmp_path/'runtime/jra_race_day_plan/2026-10-12.state.json').read_text()))==36


def test_bounded_worker_handoff_and_monotonic_dispatch_union():
    now=dt.datetime(2026,10,12,14,50,tzinfo=JST)
    with patch('jra_race_day_autopilot.time.monotonic',return_value=1801):
        assert loop_finished(now,'17:30',0,1800)
        assert not loop_finished(now,'17:30',100,1800)
    a={'R1':{'dispatched_at':'09:01'},'_result_runner_dispatched':['A']}
    b={'R2':{'dispatched_at':'09:02'},'R1':{'dispatched_at':'09:03'},'_result_runner_dispatched':['B']}
    merged=merge_dispatch_state(a,b)
    assert merged['R1']['dispatched_at']=='09:01'
    assert merged['R2']==b['R2']
    assert merged['_result_runner_dispatched']==['A','B']


def test_real_git_status_conflict_is_rebuilt_without_losing_dispatches(tmp_path):
    def git(root,*args):
        r=subprocess.run(['git',*args],cwd=root,text=True,capture_output=True)
        assert r.returncode==0,r.stderr
        return r.stdout
    remote=tmp_path/'remote.git';subprocess.run(['git','init','--bare','-q',str(remote)],check=True)
    a=tmp_path/'a';b=tmp_path/'b'
    for root in [a,b]:
        subprocess.run(['git','clone','-q',str(remote),str(root)],check=True)
        git(root,'config','user.email','test@example.test');git(root,'config','user.name','test')
    git(a,'checkout','-b','main')
    date='2026-10-12';state=f'runtime/jra_race_day_plan/{date}.state.json';sched=f'runtime/jra_race_day_plan/{date}.schedule.json'
    for p,value in [(state,{}),(sched,{}),(f'runtime/jra_race_day_status/{date}.json',{}),(f'runtime/jra_race_day_status/{date}.md','old')]:
        path=a/p;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))
    git(a,'add','.');git(a,'commit','-qm','initial');git(a,'push','-u','origin','main')
    git(b,'fetch','origin');git(b,'checkout','-b','main','origin/main')
    (a/state).write_text(json.dumps({'R1':{'dispatched_at':'09:01'}}));git(a,'add','.');git(a,'commit','-qm','remote dispatch');git(a,'push','origin','main')
    (b/state).write_text(json.dumps({'R2':{'dispatched_at':'09:02'}}))
    _commit(b,date)
    git(a,'pull','--ff-only')
    value=json.loads((a/state).read_text())
    assert set(value)=={'R1','R2'}
    assert not (b/'.git/rebase-merge').exists()


def test_index_reports_actual_handoff_error_and_does_not_block_ready_request(tmp_path):
    from jra_race_day_autopilot import race_status
    rid='KM-JRA-TKY-20261012-R03';eid=rid+'-LIVE-R1'
    intent=tmp_path/'runtime/jra_formal_intents'/f'{eid}.json';intent.parent.mkdir(parents=True);intent.write_text('{}')
    gap=tmp_path/'runtime/exact_gaps'/f'{eid}.json';gap.parent.mkdir(parents=True)
    q={'first_blocked_stage':None,'auto_handoff_error':'AKI_SINGLE_HEAD_FORBIDDEN',
       'verified_full_index_count':220,'required_index_count':220,'production_full_pipeline_ready':True}
    gap.write_text(json.dumps(q))
    now=dt.datetime(2026,10,12,10,0,tzinfo=JST)
    out=race_status(tmp_path,rid,{}, {},now)
    assert out['state']=='PRODUCTION_BLOCKED'
    assert out['first_blocked_stage']=='PRODUCTION_AKI_COLUMN_SELECTION'
    assert out['execution_error']=='AKI_SINGLE_HEAD_FORBIDDEN'
    q['auto_handoff_error']=None;gap.write_text(json.dumps(q))
    out=race_status(tmp_path,rid,{}, {},now)
    assert out['state']=='DISPATCHED_RUNNING'
    assert out['awaiting_stage']=='EXTERNAL_FORMAL_FINAL'
