import ast
import copy
from pathlib import Path
from types import SimpleNamespace
import pytest
from runtime import formal_execution_orchestrator as o


def request():
    return {'family_id':'LOCAL','race_id':'TEST','phase':'RESULT',
            'finish_order':[7,3,9],'result_available_at':'2026-09-30T12:00:00Z',
            'payouts':{'TRIFECTA':1000}}


def test_canonical_run_id_is_not_an_actions_integer():
    source=Path('runtime/local_result_from_signed_final.py').read_text()
    tree=ast.parse(source)
    node=next(n for n in tree.body if isinstance(n,ast.If)
              and 'run_id=int(run_id)' in ast.get_source_segment(source,n).replace(' ',''))
    for mode,raw,expected in [('CANONICAL_EXECUTION_STORE','123-formal','123-formal'),
                              ('EXECUTION_ID_AUTO_RESOLVE','123',123),
                              ('EXPLICIT_BACKWARD_COMPAT','123',123)]:
        ns={'resolution_mode':mode,'run_id':raw}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual conversion>','exec'),ns)
        assert ns['run_id']==expected


def test_result_plan_never_requires_static_or_reacquires_source(monkeypatch):
    monkeypatch.setattr(o,'resolve_phase',lambda e,p: {'run_dir':Path('/unused')} if p=='FORMAL' else None)
    monkeypatch.setattr(o,'run_phase',lambda *a,**k: pytest.fail('plan executes'))
    assert o.orchestrate(request(),run_id='x',github_sha=None,plan_only=True)['phases']==['RESULT']


def test_result_dispatch_uses_existing_executor(monkeypatch,tmp_path):
    monkeypatch.setattr(o,'ROOT',tmp_path)
    monkeypatch.setattr(o,'persist_phase',lambda *a,**k: {'manifest':{'run_id':a[2]}})
    calls=[]
    def run(cmd,**kwargs):
        calls.append(cmd)
        (tmp_path/'out'/'result_receipt_envelope.json').write_text('{}')
        return SimpleNamespace(returncode=0,stdout='',stderr='')
    monkeypatch.setattr(o.subprocess,'run',run)
    r=request();r['execution_id']='E'
    out=o.run_phase(r,'RESULT',run_id='x',github_sha=None,runtime_out=tmp_path/'out',tmp_root=tmp_path/'tmp')
    assert calls[0][2]=='runtime.local_result_from_signed_final'
    assert out['run_id']=='x-result'
    assert (tmp_path/'tmp/E/result_out/result_checkpoint_basis.json').exists()


def test_result_immutable_retry(monkeypatch):
    r=request(); augmented=copy.deepcopy(r);augmented['execution_id']=o.derive_execution_id(r)
    monkeypatch.setattr(o,'resolve_phase',lambda e,p:{'run_dir':Path('/unused')})
    monkeypatch.setattr(o,'_load_checkpoint_json',lambda *a:{'request_sha256':o._sha_obj(augmented)})
    monkeypatch.setattr(o,'run_phase',lambda *a,**k:pytest.fail('retry reruns result'))
    out=o.orchestrate(r,run_id='x',github_sha=None)
    # Stored RESULT request identity alone is not complete Settlement/Learning proof.
    assert out['status']=='FORMAL_INCOMPLETE'
    assert o.completion_exit_code(out)!=0
    r['payouts']['TRIFECTA']=2000
    with pytest.raises(o.FormalOrchestrationError,match='REQUEST_MISMATCH'):
        o.orchestrate(r,run_id='x',github_sha=None)


def test_result_missing_final_cannot_recompute(monkeypatch):
    monkeypatch.setattr(o,'resolve_phase',lambda *a:None)
    with pytest.raises(o.FormalOrchestrationError,match='EXISTING_FORMAL'):
        o.orchestrate(request(),run_id='x',github_sha=None)


def test_result_override_cannot_switch_lineage(monkeypatch):
    monkeypatch.setattr(o,'resolve_phase',lambda *a:{})
    r=request();r['source_run_id']=100;r['legacy_handoff_override']=True
    with pytest.raises(ValueError,match='AMBIGUOUS_LEGACY'):
        o.orchestrate(r,run_id='x',github_sha=None)


def test_explicit_source_analysis_is_not_full_lifecycle_completion(monkeypatch):
    monkeypatch.setattr(o,'resolve_phase',lambda *a:None)
    calls=[]
    monkeypatch.setattr(o,'run_phase',lambda r,p,**k:calls.append(p) or {'phase':p,'status':'PASS'})
    r={'family_id':'LOCAL','race_id':'TEST','phase':'SOURCE','analysis_only':True}
    out=o.orchestrate(r,run_id='x',github_sha=None)
    assert calls==['SOURCE']
    assert out['status']=='SOURCE_PASS'
    assert o.completion_exit_code(out)!=0


def test_source_resume_compatible(monkeypatch):
    monkeypatch.setattr(o,'resolve_phase',lambda *a:{'run_dir':Path('/unused')})
    monkeypatch.setattr(o,'source_checkpoint_compatibility',lambda *a:{'status':'PASS'})
    monkeypatch.setattr(o,'run_phase',lambda *a,**k:pytest.fail('duplicate acquisition'))
    out=o.orchestrate({'family_id':'LOCAL','race_id':'TEST','phase':'SOURCE','analysis_only':True},run_id='x',github_sha=None)
    assert out['status']=='SOURCE_PASS'
    assert o.completion_exit_code(out)!=0
