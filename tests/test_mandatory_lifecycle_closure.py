"""C1 mechanical regression only. Fixtures never enter any OOS ledger.

Owner protocol tests deliberately use a test authority and stub semantic owner;
there is NO executable Production owner in current R36. These tests are not a
live one-shot or real KRS integration acceptance.
"""
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from runtime import formal_execution_orchestrator as o
from runtime import family_authority_guard as g
from runtime import execution_store as store


def intent():
    return {"family_id":"LOCAL","race_id":"MECHANICAL-RACE-A","execution_id":"LOCAL-MECHANICAL-A",
            "venue_id":"FNB","race_date":"2099-01-01","race_no":1,
            "prediction_cutoff":"2099-01-01T11:00:00+09:00",
            "scheduled_post_at":"2099-01-01T12:00:00+09:00", "degraded_execution":True}


def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x))


def artifacts(p,req):
    _,authority=g.load_authority()
    contract=g.load_lifecycle_contract(authority)
    for sid,name in g._STAGE_PROOFS.items():
        write(p/name,{"status":"PASS","fixture":"MECHANICAL_ONLY"})
    write(p/'lifecycle_context.json',{"status":"PASS","current_authority_manifest":authority['manifest_id'],"prediction_cutoff":req['prediction_cutoff']})
    write(p/'runner_universe_diagnostic.json',{'official_active_ids':['1','2','3'],'request_ids':['1','2','3']})
    write(p/'numerical_materialization_summary.json',{
        'full_terminalization':True,'full_numerical_calculation':False,
        'numerical_authority_preflight':{'full_numerical_authority':False},
        'numeric_coverage':{'required_count':3,'calculated_count':0,'ruled_hold_count':3,
                            'ruled_neutral_count':0,'not_applicable_count':0,'unresolved_count':0}})
    proofs={}
    for sid,phase in [('SIGNED_SOURCE_RECEIPT','SOURCE'),('PRE_KRS','PRE_KRS'),('KRS_EXECUTE','KRS_RUN'),('SIGNED_FINAL','FINAL'),('SIGNED_RESULT','RESULT')]:
        write(p/g._STAGE_PROOFS[sid],{'receipt':{'phase':phase,'race_id':req['race_id'],'errors':[]},
            'signature':'TEST-NOT-A-CRYPTOGRAPHIC-PROOF','artifact':{'formal_ready':True,'required_source_manifest':[{'fixture':True}],'raw_source_bundle_sha256':'fixture','normalized_evidence':{'fixture':True}}})
        proofs[phase]=True
    write(p/'receipt_verifications.json',proofs)
    write(p/'source_verification.json',{'verified':True,'valid':True})
    write(p/'mec_plan.json',{'precompression_semantic_universe':{'fixture':'semantic'}})
    write(p/'mec_verification.json',{'mec_verified':True})
    write(p/'canonical_ticket.json',{'finalized':True,'tickets':[],'frozen_at':'2099-01-01T11:20:00+09:00','no_bet':True})
    write(p/'static_prediction_freeze.json',{'static_prediction_frozen':True,'static_prediction':{'ranking':[1,2,3]},'source_receipt_sha256':'fixture'})
    write(p/'mandatory_stage_manifest.json',{'complete':True,'execution_id':req['execution_id']})
    write(p/'final_before_post_verification.json',{'verified':True,'execution_id':req['execution_id']})
    write(p/'result_summary.json',{'verified':True,'race_id':req['race_id'],'execution_id':req['execution_id'],'pfs':None})
    write(p/'learning_state.json',{'race_id':req['race_id'],'execution_id':req['execution_id'],'final_receipt_sha256':'fixture','learning_event':{'fixture':True}})
    write(p/'forward_tracker_terminal.json',{'status':'HOLD','execution_id':req['execution_id'],'reason':'MECHANICAL_NO_OOS'})
    return contract


@pytest.mark.parametrize('status',['AWAITING_FROZEN_PREDICTION','SOURCE_PASS','RUNNING','BLOCKED','FORMAL_INCOMPLETE','DEADLINE_HOLD'])
def test_partial_states_never_cli_completion_success(status):
    assert o.completion_exit_code({'status':status})==2


def test_success_label_requires_completion_proof():
    assert o.completion_exit_code({'status':'FULL_LIFECYCLE_EXECUTION_PASS'})==2
    assert o.completion_exit_code({'status':'ALREADY_COMPLETE','completion':{'complete':False}})==2


@pytest.mark.parametrize('stage',[s['stage_id'] for s in g.load_lifecycle_contract(g.load_authority()[1])['stages'] if s['pre_race_required']])
def test_every_missing_mandatory_stage_prevents_full_pass(tmp_path,stage):
    req=intent(); artifacts(tmp_path,req)
    (tmp_path/g._STAGE_PROOFS[stage]).unlink()
    gate=g.verify_execution_completion(tmp_path,req)
    assert gate['complete'] is False
    assert stage in gate['missing_or_held_stages']


def test_not_ready_remains_honest_degraded_with_all_terminal_stages(tmp_path):
    req=intent();artifacts(tmp_path,req)
    gate=g.verify_execution_completion(tmp_path,req)
    assert gate['complete']
    assert gate['execution_class']=='FULL-LIFECYCLE-DEGRADED-NUMERICAL'
    assert gate['numeric_coverage']['ruled_hold_count']==3
    assert gate['numeric_coverage']['calculated_count']==0
    assert not gate['numerical_authority_ready']
    req['require_full_numerical_authority']=True
    assert not g.verify_execution_completion(tmp_path,req)['complete']


def test_numeric_counter_forgery_cannot_erase_hold(tmp_path):
    req=intent();artifacts(tmp_path,req)
    n=json.loads((tmp_path/'numerical_materialization_summary.json').read_text())
    n['numeric_coverage']['calculated_count']=3  # retain HOLD, totals no longer reconcile
    write(tmp_path/'numerical_materialization_summary.json',n)
    assert not g.verify_execution_completion(tmp_path,req)['complete']


@pytest.mark.parametrize('missing',['static_prediction_freeze.json','final_receipt_envelope.json','source_receipt_envelope.json'])
def test_r09_r10_r11_missing_capture_or_final_or_source(tmp_path,missing):
    req=intent();artifacts(tmp_path,req);(tmp_path/missing).unlink()
    assert not g.verify_execution_completion(tmp_path,req)['complete']


def test_partial_source_cannot_complete(tmp_path):
    req=intent();artifacts(tmp_path,req)
    x=json.loads((tmp_path/'source_receipt_envelope.json').read_text());x['artifact']['formal_ready']=False
    write(tmp_path/'source_receipt_envelope.json',x)
    assert not g.verify_execution_completion(tmp_path,req)['complete']


def test_shadow_missing_nonblocking_production(tmp_path):
    req=intent();artifacts(tmp_path,req)
    write(tmp_path/'local_forward_measurement_failure.json',{'status':'SHADOW_CAPTURE_FAILED'})
    assert g.verify_execution_completion(tmp_path,req)['complete']
    (tmp_path/'krs_receipt_envelope.json').unlink()
    write(tmp_path/'candidate_krs_receipt_envelope.json',{'status':'EXECUTED'})
    assert not g.verify_execution_completion(tmp_path,req)['complete']


def test_deadline_hold_explicit():
    req=intent();req['scheduled_post_at']='2000-01-01T12:00:00+09:00'
    with pytest.raises(o.FormalOrchestrationError,match='DEADLINE_HOLD'):
        o.check_deadline(req)


def test_r36_transport_only_fallback_reuses_same_semantics(monkeypatch):
    req=intent();req['static_prediction']={'ranking':[1,2,3]};req['static_prediction_frozen']=True
    calls=[]
    def run(r,phase,**kw):
        calls.append(copy.deepcopy(r))
        if len(calls)==1:
            raise o.FormalOrchestrationError(json.dumps({'failure_class':'RUNTIME_TRANSPORT','code':'TIMEOUT'}))
        return {'status':'PASS'}
    monkeypatch.setattr(o,'run_phase',run)
    monkeypatch.setattr(o,'bind_formal_request_to_source',lambda r:r)
    assert o.run_formal_with_fallback(req,'FORMAL')['status']=='PASS'
    assert calls[1]['execution_id']==calls[0]['execution_id']
    assert calls[1]['static_prediction']==calls[0]['static_prediction']
    assert calls[1]['entry_transport_fallback']['external_safety_bypass'] is False


@pytest.mark.parametrize('failure',['TEMPORAL_GUARD','NUMERICAL_AUTHORITY_OR_MATERIALIZATION','FINALIZATION'])
def test_safety_failure_never_legacy_retried(monkeypatch,failure):
    calls=[]
    def run(*args,**kw):
        calls.append(1);raise o.FormalOrchestrationError(json.dumps({'failure_class':failure}))
    monkeypatch.setattr(o,'run_phase',run)
    with pytest.raises(o.FormalOrchestrationError):o.run_formal_with_fallback(intent(),'FORMAL')
    assert len(calls)==1


def test_result_and_learning_gate_research_hold_nonblocking(tmp_path):
    req=intent();artifacts(tmp_path,req)
    assert g.verify_execution_completion(tmp_path,req,phase='RESULT')['complete']
    (tmp_path/'learning_state.json').unlink()
    assert not g.verify_execution_completion(tmp_path,req,phase='RESULT')['complete']


def test_unknown_contract_stage_is_not_silently_skipped(monkeypatch,tmp_path):
    req=intent();c=artifacts(tmp_path,req);c['stages'].append({'stage_id':'UNMAPPED_NEW_MANDATORY','pre_race_required':True})
    monkeypatch.setattr(g,'load_lifecycle_contract',lambda a:c)
    assert 'UNMAPPED_NEW_MANDATORY' in g.verify_execution_completion(tmp_path,req)['missing_or_held_stages']


@pytest.mark.parametrize('race',['R07-LIVE-R2','R08-LIVE-R1','R12-LIVE-R2'])
def test_historical_positive_controls_policy_content_preserved(race):
    # Offline immutable artifact integrity only; NOT new lifecycle acceptance.
    eid='LOCAL-KM-LOCAL-FNB-20261001-'+race+'-EXEC'
    formal=store.resolve_phase(eid,'FORMAL')
    assert formal
    fin=o._load_checkpoint_json(formal,'final_receipt_envelope.json')
    assert fin['receipt']['status']=='PASS'
    assert fin['artifact']['final_ticket']['finalized']
    assert fin['artifact']['minimum_efficient_coverage']['profile']
    assert store.resolve_phase(eid,'RESULT')


def test_fresh_process_store_two_races_and_duplicate_protection(tmp_path):
    # Real immutable store / completion evaluator, processes restarted at each step.
    # Synthetic stages, no External Runtime, no live KRS or OOS increment.
    root=tmp_path/'store';req=intent();out=tmp_path/'A';artifacts(out,req)
    script='''import json,sys
from pathlib import Path
from runtime.execution_store import persist_phase,resolve_phase
from runtime.family_authority_guard import verify_execution_completion
req=json.loads(sys.argv[1]);root=Path(sys.argv[2]);out=Path(sys.argv[3]);phase=sys.argv[4]
gate=verify_execution_completion(out,req,phase=phase);assert gate['complete'],gate
persist_phase(req['execution_id'],phase,'fixture-'+phase,out,root=root)
assert resolve_phase(req['execution_id'],phase,root=root)
print(gate['execution_class'])
'''
    for phase in ['FORMAL','RESULT','RESULT']:
        subprocess.run([sys.executable,'-c',script,json.dumps(req),str(root),str(out),phase],check=True,capture_output=True)
    reqB={**req,'race_id':'MECHANICAL-RACE-B','execution_id':'LOCAL-MECHANICAL-B'};outB=tmp_path/'B';artifacts(outB,reqB)
    subprocess.run([sys.executable,'-c',script,json.dumps(reqB),str(root),str(outB),'FORMAL'],check=True,capture_output=True)
    assert store.resolve_phase(req['execution_id'],'RESULT',root=root)
    assert store.resolve_phase(reqB['execution_id'],'RESULT',root=root) is None
    changed=tmp_path/'changed';artifacts(changed,req)
    write(changed/'learning_state.json',{'different':True})
    with pytest.raises(store.ExecutionStoreError,match='IMMUTABLE_RUN_CONFLICT'):
        store.persist_phase(req['execution_id'],'RESULT','fixture-RESULT',changed,root=root)


def test_one_intent_invokes_internal_owner_then_formal_without_static_operator_input(monkeypatch,tmp_path):
    # Orchestrator contract unit test with an explicitly mechanical owner stub.
    req=intent();calls=[]
    monkeypatch.setattr(o,'resume_plan',lambda *args:{'action':'RUN_SOURCE_THEN_FORMAL','resume_from':'SOURCE','checkpoints':{}})
    monkeypatch.setattr(o,'validate_request_context',lambda r:{'status':'PASS'})
    monkeypatch.setattr(o,'run_phase',lambda r,phase,**kw:calls.append(phase) or {'status':'PASS','phase':phase})
    def owner(r,**kw):
        assert 'static_prediction' not in r
        calls.append('PREDICTION_OWNER')
        return {**r,'static_prediction':{'ranking':[1,2,3],'status':'FROZEN'},'static_prediction_frozen':True}
    monkeypatch.setattr(o,'execute_prediction_owner',owner)
    monkeypatch.setattr(o,'bind_formal_request_to_source',lambda r:r)
    monkeypatch.setattr(o,'run_formal_with_fallback',lambda r,phase,**kw:calls.append(phase) or {'status':'PASS','phase':phase})
    monkeypatch.setattr(o,'verify_execution_completion',lambda *args,**kw:{'complete':True,'execution_class':'FULL-LIFECYCLE-DEGRADED-NUMERICAL'})
    report=o.orchestrate(req,run_id='mechanical',github_sha='fixture',runtime_out=tmp_path/'out',tmp_root=tmp_path/'tmp')
    assert calls==['SOURCE','PREDICTION_OWNER','FORMAL']
    assert report['status']=='FULL_LIFECYCLE_EXECUTION_PASS'
    assert 'static_prediction' not in req


def test_source_checkpoint_auto_resume_calls_owner_without_reacquisition(monkeypatch,tmp_path):
    req=intent();calls=[]
    monkeypatch.setattr(o,'resume_plan',lambda *args:{'action':'RESUME_FORMAL','resume_from':'FORMAL','checkpoints':{'source':{'status':'COMPLETE'}}})
    monkeypatch.setattr(o,'resolve_phase',lambda *args:None)
    monkeypatch.setattr(o,'validate_request_context',lambda r:{'status':'PASS'})
    def owner(r,**kw):
        calls.append('OWNER')
        raise o.FormalOrchestrationError('PRODUCTION_PREDICTION_OWNER_NOT_REGISTERED')
    monkeypatch.setattr(o,'execute_prediction_owner',owner)
    monkeypatch.setattr(o,'run_phase',lambda *args,**kw:pytest.fail('SOURCE reacquired'))
    report=o.orchestrate(req,run_id='mechanical',github_sha='fixture',runtime_out=tmp_path/'out',tmp_root=tmp_path/'tmp')
    assert calls==['OWNER']
    assert report['status']=='BLOCKED'
    assert report['resume_from']=='PREDICTION'


def test_authority_pinned_owner_protocol_uses_real_production_materializer(monkeypatch,tmp_path):
    # Executes a test-only program through the owner protocol; real Production
    # materialization stays all HOLD. This is NOT a registered Production owner.
    req=intent();source_dir=tmp_path/'source'
    source_env={'receipt':{'race_id':req['race_id']},'receipt_sha256':'fixture-receipt',
                'artifact':{'formal_ready':True,'source_snapshot_sha256':'fixture-snapshot',
                            'active_runner_universe':{'runner_count':3,'runners':[{'runner_id':str(i),'name':f'fixture-{i}'} for i in [1,2,3]]}}}
    write(source_dir/'source_receipt_envelope.json',source_env)
    write(source_dir/'source_verification.json',{'verified':True,'valid':True})
    source={'run_dir':source_dir,'latest':{'manifest_sha256':'fixture-manifest'},'manifest':{'run_id':'fixture-source'}}
    owner=tmp_path/'owner.py'
    owner.write_text('''import json,sys
x=json.load(sys.stdin)
assert x['production_numeric_coverage']['calculated_count']==0
assert x['production_numeric_coverage']['ruled_hold_count']>0
print(json.dumps({'basis':x['basis'],'prediction_semantics':{
 'static_prediction':{'ranking':[1,2,3]},
 'venue_prediction_context':{'fixture':'NOT_PRODUCTION'},
 'role_registry':[{'runner_id':'1','column':'W','status':'CORE'}]}}))
''')
    _,authority=g.load_authority();authority=copy.deepcopy(authority)
    authority['family_scoped_authority']['LOCAL']['production_prediction_owner']={
        'production_authorized':True,'entrypoint':'owner.py',
        'sha256':hashlib.sha256(owner.read_bytes()).hexdigest(),
        'production_policy_sha256':'TEST-AUTHORITY-NOT-PRODUCTION'}
    (tmp_path/'mapping').mkdir()
    registry=o.ROOT/'mapping/local_base_index_mapping_registry_v1.0_20260922.json'
    (tmp_path/'mapping'/registry.name).write_bytes(registry.read_bytes())
    monkeypatch.setattr(o,'ROOT',tmp_path)
    monkeypatch.setattr(o,'load_authority',lambda:(Path('TEST-AUTHORITY'),authority))
    monkeypatch.setattr(o,'resolve_phase',lambda *args:source)
    monkeypatch.setattr(o,'persist_phase',lambda eid,phase,rid,out,**kw:store.persist_phase(eid,phase,rid,out,root=tmp_path/'store',**kw))
    result=o.execute_prediction_owner(req,run_id='fixture',github_sha='fixture',tmp_root=tmp_path/'tmp')
    assert result['static_prediction_frozen'] is True
    assert result['numeric_coverage']['calculated_count']==0
    assert result['numeric_coverage']['ruled_hold_count']==87
    assert result['numerical_authority_preflight']['full_numerical_authority'] is False
    assert store.resolve_phase(req['execution_id'],'PREDICTION',root=tmp_path/'store')
    owner.write_text('CHANGED_IMPLEMENTATION')
    with pytest.raises(o.FormalOrchestrationError,match='HASH_MISMATCH'):
        o.execute_prediction_owner(req,run_id='fixture2',github_sha='fixture',tmp_root=tmp_path/'tmp')
