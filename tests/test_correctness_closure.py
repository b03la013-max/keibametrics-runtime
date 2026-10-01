"""Structural fixtures only; never write the real OOS tracker."""
import ast, json, os, subprocess, sys, copy
from pathlib import Path
import pytest
from runtime.execution_gateway import result_route, ExecutionGatewayError

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from common_exact_continuity_shadow import build_shadow, bind_shadow_to_trace, settle_shadow, verify_signed_final_binding, _sha
from common_exact_continuity_oos_tracker import build_status


def sample(rid='R1'):
    q={'race_id':rid,'temporal_mode':'FORMAL-PRE-RACE','scheduled_post_at':'2099-01-01T12:00:00+09:00',
       'oos_policy':{'acceptance_only':False,'request_oos_eligible':True},
       'pair_dispositions':[{'head':'7','second':'2','status':'PURCHASE'}],
       'static_prediction':{'roles':{'8':['P3']}}}
    sh=build_shadow(q,{'tickets':[]},{'roles':q['static_prediction']['roles']},{},'2099-01-01T02:00:00Z','B')
    fin={'receipt':{'phase':'FINAL','status':'PASS','artifact_sha256':'A'},'receipt_sha256':'F',
         'artifact':{'ticket_transport_trace':bind_shadow_to_trace({},sh)}}
    return sh,fin


def common_result_block():
    s=(ROOT/'runtime/local_result_from_signed_final.py').read_text()
    tree=ast.parse(s)
    return next(n for n in tree.body if isinstance(n,ast.Try) and 'common_exact_path' in ast.get_source_segment(s,n))


def execute_common(tmp_path,monkeypatch,rid='R1',failure=None):
    monkeypatch.chdir(tmp_path)
    (tmp_path/'runtime_result_in').mkdir(exist_ok=True);(tmp_path/'runtime_out').mkdir(exist_ok=True)
    sh,fin=sample(rid)
    if failure=='hash':sh['arms']['CONTINUITY_ALL'].append('1>2>3')
    if failure=='binding':fin['artifact']['ticket_transport_trace']={}
    path=tmp_path/'runtime_result_in/common_exact_continuity_shadow_pre_result.json';path.write_text(json.dumps(sh))
    production={'receipt':{'status':'PASS'},'artifact':{'pfs':80}}
    ns={'acceptance_only':False,'os':os,'json':json,'common_exact_path':str(path),
        'verify_common_exact_continuity_binding':verify_signed_final_binding,
        'settle_common_exact_continuity_shadow':settle_shadow,
        'write_common_exact_continuity_oos_status':lambda:build_status(),
        'fin':fin,'req':{'finish_order':[7,2,8]},'payouts':{} if failure=='payout' else {'TRIFECTA':1000},
        'total_investment':1000,'total_return':800,'rid':rid,'run_id':'run-formal','artifact_name':'FINAL',
        'res':production,'shared_result_authority':{'status':'HOLD_RESULT_AUTHORITY','verified_signed_result':False}}
    exec(compile(ast.Module(body=[common_result_block()],type_ignores=[]),'<actual RESULT shadow>','exec'),ns)
    assert ns['res']==production
    return ns


@pytest.mark.parametrize('failure',['hash','binding','payout'])
def test_shadow_failure_does_not_block_production(tmp_path,monkeypatch,failure):
    execute_common(tmp_path,monkeypatch,failure=failure)
    diag=json.loads((tmp_path/'runtime_out/common_exact_continuity_shadow_failure.json').read_text())
    assert diag['production_effect']=='NONE'
    assert diag['status']==('SHADOW_HOLD' if failure=='payout' else 'SHADOW_REJECTED')
    assert not (tmp_path/'runtime/common_exact_continuity_shadow_results/R1.json').exists()


def test_valid_shadow_persists_across_fresh_checkout(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path)
    subprocess.run(['git','init','-q'],check=True)
    subprocess.run(['git','config','user.email','fixture@example.invalid'],check=True)
    subprocess.run(['git','config','user.name','Fixture'],check=True)
    assert build_status()['eligible_races']==0
    for rid in ['R1','R2']:
        p=tmp_path/'runtime/family_result_requests';p.mkdir(parents=True,exist_ok=True)
        (p/(rid+'.json')).write_text(json.dumps({'race_id':rid,'official_result_verified':True}))
        execute_common(tmp_path,monkeypatch,rid)
        # Replay the actual workflow's common-ledger staging statements.
        workflow=(ROOT/'.github/workflows/km-local-result-from-signed-final.yml').read_text()
        section=workflow.split('      - name: Persist LOCAL forward measurement ledgers',1)[1].split('      - name:',1)[0]
        stage='\n'.join(l for l in section.splitlines() if 'git add runtime/common_exact' in l)
        assert stage.count('git add')==4
        subprocess.run(['bash','-c',stage],check=True)
        subprocess.run(['git','add','runtime/family_result_requests'],check=True)
        subprocess.run(['git','commit','-qm',rid],check=True)
        clone=tmp_path/('clone'+rid)
        subprocess.run(['git','clone','-q',str(tmp_path),str(clone)],check=True)
        code='import sys;sys.path.insert(0,'+repr(str(ROOT/'runtime'))+');from common_exact_continuity_oos_tracker import build_status;print(build_status()["eligible_races"])'
        actual=int(subprocess.check_output([sys.executable,'-c',code],cwd=clone,text=True))
        assert actual==int(rid[-1])
    execute_common(tmp_path,monkeypatch,'R2')
    assert build_status()['eligible_races']==2


@pytest.mark.parametrize('r,expected',[
    ({'family_id':'LOCAL','race_id':'R'},'CANONICAL'),
    ({'family_id':'LOCAL','race_id':'R','source_run_id':123,'artifact_name':'stale'},'CANONICAL'),
    ({'family_id':'LOCAL','race_id':'R','legacy_handoff_override':True,'source_run_id':123,'artifact_name':'FINAL'},'LEGACY'),
])
def test_normalized_route(r,expected):assert result_route(r)==expected


@pytest.mark.parametrize('r',[
    {'legacy_handoff_override':True,'source_run_id':123},
    {'legacy_handoff_override':True,'artifact_name':'FINAL'},
    {'legacy_handoff_override':True,'source_run_id':'123-formal','artifact_name':'FINAL'},
])
def test_ambiguous_result_never_falls_back(r):
    with pytest.raises(ExecutionGatewayError):result_route({'family_id':'LOCAL','race_id':'R',**r})


def test_deleted_request_is_not_selected(tmp_path):
    subprocess.run(['git','init','-q',str(tmp_path)],check=True)
    def git(*a):return subprocess.check_output(['git',*a],cwd=tmp_path,text=True)
    git('config','user.email','fixture@example.invalid');git('config','user.name','Fixture')
    p=tmp_path/'runtime/family_result_requests';p.mkdir(parents=True);(p/'gone.json').write_text('{}')
    git('add','.');git('commit','-qm','add');(p/'gone.json').unlink();git('add','.');git('commit','-qm','delete')
    sha=git('rev-parse','HEAD').strip()
    assert git('diff-tree','--no-commit-id','--diff-filter=AM','--name-only','-r',sha)==''
    w=(ROOT/'.github/workflows/km-local-result-from-signed-final.yml').read_text()
    assert '--diff-filter=AM' in w and 'skip=true' in w
