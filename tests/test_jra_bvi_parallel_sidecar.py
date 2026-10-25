"""Synthetic operational boundaries only; never real SOURCE or Forward OOS."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("parallel_sidecar", ROOT / "scripts/jra_bvi_parallel_sidecar.py")
s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)


def fixture(tmp_path):
    eid = "KM-JRA-TKY-20990101-R01-LIVE-R1"
    request = {"family_id":"JRA", "race_id":"KM-JRA-TKY-20990101-R01", "execution_id":eid,
        "prediction_cutoff":"2099-01-01T00:45:00+00:00", "scheduled_post_at":"2099-01-01T00:50:00+00:00",
        "race_date":"2099-01-01", "temporal_mode":"FORMAL-PRE-RACE", "source_snapshot_sha256":"a"*64,
        "run_count":5000, "runners":[{"runner_id":"1"},{"runner_id":"2"}]}
    intent = {k:request[k] for k in ("family_id","race_id","execution_id","prediction_cutoff","scheduled_post_at")}
    folder = tmp_path / "runtime/jra_formal_intents"; folder.mkdir(parents=True)
    (folder / "one.json").write_text(json.dumps(intent))
    return intent, request, eid


def parent():
    return {"id":123, "repository":{"full_name":s.REPO}, "head_repository":{"full_name":s.REPO},
        "head_branch":"main", "head_sha":"b"*40, "path":".github/workflows/km-jra-formal-single-entry.yml"}


def own_job():
    return {'name':'pedigree-forward-shadow','started_at':s.utcnow().isoformat()}


def artifact_metadata(eid, raw, **patch):
    row={"id":99,"name":f"km-jra-single-entry-{eid}-123","workflow_run":{"id":123},
        "created_at":"2098-12-31T23:00:00Z","size_in_bytes":len(raw),
        "digest":"sha256:"+s.digest(raw),"expired":False}
    row.update(patch)
    return {"total_count":1,"artifacts":[row]}


def test_prewarm_verifies_real_gate_interfaces_but_never_predicts_or_calls_krs(tmp_path, monkeypatch):
    intent, request, eid=fixture(tmp_path)
    q=tmp_path/'q.json';q.write_text(json.dumps(request))
    src=tmp_path/'s.json';source={"race_id":request['race_id'],"source_snapshot_sha256":"a"*64,
        "jra_official_race_card_detail":{"runners":[{"sire":"S","damsire":"DS"}]}}
    src.write_text(json.dumps({"artifact":source}));seen=[]
    monkeypatch.setattr(s.frozen,'_verified_source',lambda p:{"race_id":request['race_id'],"source_snapshot_sha256":"a"*64})
    def attest(p, **kw):
        seen.append(('attest',p,kw));return True
    monkeypatch.setattr(s.frozen,'_attested',attest)
    import jra_execution_maturity_bridge
    monkeypatch.setattr(jra_execution_maturity_bridge,'verify_formal_request_binding',lambda *a:{"status":"PASS"})
    def corpus(root, **kw):
        assert kw['exclude_race_id']==request['race_id']
        assert kw['required_sires']=={'S'} and kw['required_damsires']=={'DS'}
        assert s.frozen.time(kw['prediction_cutoff'])<=s.frozen.time(request['prediction_cutoff'])
        seen.append(('corpus',root,kw));return {'manifest_sha256':'c'*64}
    monkeypatch.setattr(s.frozen,'build_corpus',corpus)
    for name in ('freeze','compare','call','execute_diagnostic_downstream'):
        monkeypatch.setattr(s.frozen,name,lambda *a,**k:pytest.fail('prewarm cannot predict/KRS'))
    report={};hint=s.prewarm(q,src,intent,eid,report,root=tmp_path)
    assert [x[0] for x in seen]==['attest','corpus']
    assert seen[0][2]['not_after']==s.frozen.time(request['prediction_cutoff'])
    assert hint['predictions_created']==hint['external_krs_calls']==0
    assert hint['authority'].startswith('NON_AUTHORITATIVE_HINT')


@pytest.mark.parametrize('patch',[{'source_snapshot_sha256':'0'*64},{'race_id':'WRONG'},None])
def test_unverified_prewarm_never_warms_corpus(tmp_path,monkeypatch,patch):
    intent,request,eid=fixture(tmp_path);q=tmp_path/'q.json';q.write_text(json.dumps(request));p=tmp_path/'s.json';p.write_text('{}')
    monkeypatch.setattr(s.frozen,'_verified_source',lambda p:patch)
    monkeypatch.setattr(s.frozen,'_attested',lambda *a,**k:False)
    monkeypatch.setattr(s.frozen,'build_corpus',lambda *a,**k:pytest.fail('Unverified input'))
    with pytest.raises((ValueError,KeyError),match='PREWARM_SOURCE_UNVERIFIED|race_id'):
        s.prewarm(q,p,intent,eid,{},root=tmp_path)


def completed_artifact(tmp_path):
    intent,request,eid=fixture(tmp_path);folder=tmp_path/'download';folder.mkdir()
    (folder/'jra_single_entry_formal_request.json').write_text(json.dumps(request))
    sd=folder/'jra_single_entry_source_checkpoint';sd.mkdir();(sd/'source_receipt_envelope.json').write_text('{"artifact":"SYNTHETIC"}')
    summary={'status':'FULL_FORMAL_E2E_PASS','race_id':request['race_id'],'family_id':'JRA',
        'temporal_formality':'FORMAL-PRE-RACE','acceptance_only':False,'source_snapshot_sha256':'a'*64,
        'execution_stage_manifest':{'synthetic':{'status':'PASS'}},'all_mandatory_stages_verified':True,
        'all_mandatory_pre_race_stages_verified':True,
        'manifest':{'required_count':40,'calculated_count':40,'ruled_hold_count':0,'not_applicable_count':0,'unresolved_count':0},
        'pre_krs':{'verified':True,'receipt_sha256':'d'*64},
        'krs':{'verified':True,'receipt_sha256':'e'*64,'requested_run_count':5000,'actual_run_count':5000},
        'final':{'verified':True,'receipt_sha256':'f'*64,'receipt_timestamp':'2099-01-01T00:40:00Z','immutable_artifact_sha256':'c'*64}}
    from jra_single_entry_outcome import verify_formal_completion_summary
    check=verify_formal_completion_summary(summary,request)
    cd=folder/'canonical_formal';cd.mkdir();(cd/'formal_execution_summary.json').write_text(json.dumps(summary))
    (folder/'jra_formal_completion_verification.json').write_text(json.dumps(check))
    fd=tmp_path/'runtime/final_artifacts';fd.mkdir(parents=True);(fd/(request['race_id']+'.json')).write_text(json.dumps({'final_receipt_sha256':'f'*64}))
    hint={'request_file_sha256':s.digest((folder/'jra_single_entry_formal_request.json').read_bytes()),
        'source_file_sha256':s.digest((sd/'source_receipt_envelope.json').read_bytes())}
    return folder,intent,request,eid,hint


@pytest.mark.parametrize('mutation',['request','source','receipt','summary','no_completion'])
def test_hint_never_substitutes_for_successful_exact_parent_artifact(tmp_path,mutation):
    folder,intent,request,eid,hint=completed_artifact(tmp_path)
    if mutation in ('request','source'):hint[mutation+'_file_sha256']='0'*64
    if mutation=='receipt':
        p=tmp_path/'runtime/final_artifacts'/(request['race_id']+'.json');p.write_text('{"final_receipt_sha256":"wrong"}')
    if mutation=='summary':
        p=folder/'canonical_formal/formal_execution_summary.json';d=json.loads(p.read_text());d['acceptance_only']=True;p.write_text(json.dumps(d))
    if mutation=='no_completion':(folder/'jra_formal_completion_verification.json').unlink()
    with pytest.raises((ValueError,FileNotFoundError)):
        s.bind_parent_input(folder,intent,eid,hint,{},root=tmp_path)


def test_completed_original_artifact_binds_receipts_and_exact_prewarm_bytes(tmp_path):
    folder,intent,request,eid,hint=completed_artifact(tmp_path);report={}
    q,p,out=s.bind_parent_input(folder,intent,eid,hint,report,root=tmp_path)
    assert out==request and report['parent_input']['warm_hint_matched']
    assert report['parent_input']['signed_final_receipt_sha256']=='f'*64
    # This is content binding only; canonical freeze remains the signer/gate.
    assert 'HINT_ALONE_NEVER_SUFFICIENT' in report['parent_input']['acceptance']


@pytest.mark.parametrize('patch',[{'workflow_run':{'id':999}},{'created_at':'2099-01-01T01:00:00Z'},{'digest':'sha256:'+'0'*64}])
def test_artifact_wrong_run_time_or_provider_digest_rejected(tmp_path,monkeypatch,patch):
    _,request,eid=fixture(tmp_path);raw=io.BytesIO()
    with zipfile.ZipFile(raw,'w') as z:z.writestr('example.json','{}')
    blob=raw.getvalue()
    monkeypatch.setattr(s,'gh_json',lambda *a:artifact_metadata(eid,blob,**patch))
    monkeypatch.setattr(s.subprocess,'check_output',lambda *a,**k:blob)
    with pytest.raises(ValueError,match='ARTIFACT_IDENTITY_OR_TIME|PROVIDER_HASH'):
        s.download_parent_artifact(123,eid,s.frozen.time(request['prediction_cutoff']),tmp_path/'out')


def test_duplicate_named_parent_artifacts_are_not_current_input(tmp_path,monkeypatch):
    _,request,eid=fixture(tmp_path);data=artifact_metadata(eid,b'');data['artifacts']*=2
    monkeypatch.setattr(s,'gh_json',lambda *a:data)
    with pytest.raises(ValueError,match='UNIQUE_PARENT_ARTIFACT'):
        s.download_parent_artifact(123,eid,s.frozen.time(request['prediction_cutoff']),tmp_path/'out')


def test_parent_failure_or_wait_limit_cannot_trigger_prediction(tmp_path,monkeypatch):
    _,_,_=fixture(tmp_path)
    def api(path):
        if path.endswith('/123'):return parent()
        return {'total_count':2,'jobs':[own_job(),{'name':'orchestrate','status':'completed','conclusion':'failure'}]}
    monkeypatch.setattr(s,'gh_json',api)
    monkeypatch.setattr(s,'verify_fixed_model',lambda *a,**kw:None)
    monkeypatch.setattr(s,'download_parent_artifact',lambda *a:pytest.fail('Failed parent'))
    monkeypatch.setattr(s.frozen,'freeze',lambda *a,**k:pytest.fail('Failed parent'))
    report={};s.run(123,'runtime/jra_formal_intents/one.json','b'*40,report,root=tmp_path)
    assert report['status']=='PENDING; PRODUCTION_PARENT_NOT_SUCCESSFUL'
    values=iter([0,901]);monkeypatch.setattr(s.clock,'monotonic',lambda:next(values))
    report={};s.run(123,'runtime/jra_formal_intents/one.json','b'*40,report,root=tmp_path)
    assert report['status']=='PENDING; PARENT_WAIT_BUDGET_OR_CUTOFF_EXPIRED'


def test_warm_then_parent_complete_then_original_freeze_without_clock_override(tmp_path,monkeypatch):
    intent,request,eid=fixture(tmp_path);events=[];jobs=iter(['in_progress','completed']);own=own_job()
    def api(path):
        if path.endswith('/123'):return parent()
        status=next(jobs);return {'jobs':[own,{'name':'orchestrate','status':status,'conclusion':'success' if status=='completed' else None}]}
    monkeypatch.setattr(s,'gh_json',api);monkeypatch.setattr(s,'refresh_main',lambda *a:events.append('read_main'))
    monkeypatch.setattr(s,'verify_fixed_model',lambda *a,**kw:events.append('verify_fixed_model_bytes'))
    monkeypatch.setattr(s.clock,'sleep',lambda *a:events.append('wait'))
    monkeypatch.setattr(s,'warm_hint',lambda *a,**k:events.append('signature_caches_only') or {'hint':True})
    monkeypatch.setattr(s,'download_parent_artifact',lambda *a:events.append('original_run_artifact') or {'parent_run_id':123})
    monkeypatch.setattr(s,'bind_parent_input',lambda *a,**k:events.append('bind_all_original_bytes') or (tmp_path/'q',tmp_path/'source',request))
    monkeypatch.setattr(s,'verify_parent_final',lambda *a,**k:events.append('verify_actual_final_signature'))
    monkeypatch.setattr(s.sys,'addaudithook',lambda hook:events.append('denial_only_job_budget_gate'))
    def freeze(q,p,out,**kw):
        assert set(kw)=={'environment_model_path'}  # No now, deadline or stop override.
        events.append('canonical_freeze');return {'sha256':'c'*64}
    monkeypatch.setattr(s.frozen,'freeze',freeze)
    report={};s.run(123,'runtime/jra_formal_intents/one.json','b'*40,report,root=tmp_path)
    assert events.index('signature_caches_only')<events.index('wait')<events.index('original_run_artifact')<events.index('canonical_freeze')
    assert events.index('bind_all_original_bytes')<events.index('verify_actual_final_signature')<events.index('canonical_freeze')
    assert report['status'].endswith('INDEPENDENT_WITNESS_STILL_REQUIRED')
    assert 'canonical_freeze_started_at' in report
    assert s.frozen.time(report['active_deadline'])-s.frozen.time(report['active_started_at'])<=s.timedelta(minutes=15)


def test_job_budget_observer_can_only_deny_original_timeout_launches():
    from datetime import timedelta
    report={};gate=s.job_budget_gate(s.utcnow()+timedelta(seconds=449),report)
    # Local/GitHub warming and unrelated resources are not simulation calls.
    gate('urllib.Request',('https://api.github.com/repos/example',))
    gate('irrelevant-event',())
    with pytest.raises(ValueError,match='ORIGINAL_RPC'):
        gate('urllib.Request',('https://quorumprobe-production.up.railway.app/krs/execute',))
    assert report['job_budget_rejection']['required_seconds']==450
    gate('urllib.Request',('https://quorumprobe-production.up.railway.app/verify',))
    with pytest.raises(ValueError):
        s.job_budget_gate(s.utcnow()+timedelta(seconds=59),{})(
            'urllib.Request',('https://quorumprobe-production.up.railway.app/verify',))


@pytest.mark.parametrize('mutation',[None,'signature','payload','source','receipt','future'])
def test_genuine_parent_final_required_before_canonical_entry(tmp_path,monkeypatch,mutation):
    from base64 import b64encode
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    from jra_delivery import signed_payload, canonical_bytes
    _,request,_=fixture(tmp_path);key=Ed25519PrivateKey.generate()
    contract={'external_endpoint':'https://synthetic.invalid','engine_sha256':'engine','parameter_map_sha256':'params'}
    health={'status':'READY','engine':{'sha256':'engine'},'parameter_map':{'sha256':'params'},
        'receipt_signer':{'ready':True,'key_id':'test','public_key_b64':b64encode(
            key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)).decode()}}
    final={k:request[k] for k in ('family_id','race_id','temporal_mode','source_snapshot_sha256','prediction_cutoff','scheduled_post_at')}
    final.update(final_freeze_timestamp=s.utcnow().isoformat(),final_prediction_package={},
        final_ticket={'no_bet':False,'tickets':[]},krs_run_receipt={})
    receipt={'phase':'FINAL','status':'PASS','race_id':request['race_id'],'errors':[],
        'timestamp':(s.utcnow()-s.timedelta(seconds=1)).isoformat(),'artifact_sha256':s.frozen.sha(signed_payload(final))}
    if mutation=='future':receipt['timestamp']=(s.utcnow()+s.timedelta(minutes=1)).isoformat()
    envelope={'receipt':receipt,'receipt_sha256':s.frozen.sha(receipt),'signer_key_id':'test','signature_alg':'Ed25519',
        'signature':b64encode(key.sign(canonical_bytes(receipt))).decode()}
    final.update(final_receipt=envelope,final_receipt_sha256=envelope['receipt_sha256'])
    report={'parent_input':{'signed_final_receipt_sha256':final['final_receipt_sha256']}}
    if mutation=='signature':envelope['signature']=b64encode(b'0'*64).decode()
    if mutation=='payload':final['final_ticket']['no_bet']=True
    if mutation=='source':final['source_snapshot_sha256']='0'*64
    if mutation=='receipt':report['parent_input']['signed_final_receipt_sha256']='0'*64
    final['sha256']=s.frozen.sha(final)
    path=tmp_path/'runtime/final_artifacts'/(request['race_id']+'.json');path.parent.mkdir(parents=True);path.write_text(json.dumps(final))
    profile=tmp_path/'contract.json';profile.write_text(json.dumps({'families':{'JRA':contract}}))
    authority={'effective_at':'2020-01-01T00:00:00Z','common_family_components':{'family_runtime_contracts_profile':'contract.json'}}
    monkeypatch.setattr(s.frozen,'resolve_current_authority',lambda *a,**k:(tmp_path/'authority.json',authority))
    monkeypatch.setattr(s.urllib.request,'urlopen',lambda url,**kw:io.StringIO(json.dumps(health)))
    monkeypatch.setattr(s.frozen,'freeze',lambda *a,**k:pytest.fail('No canonical work during signature gate'))
    if mutation:
        with pytest.raises((ValueError,InvalidSignature)):
            s.verify_parent_final(request,report,root=tmp_path)
        assert 'parent_final_verified' not in report
    else:
        s.verify_parent_final(request,report,root=tmp_path)
        assert report['parent_final_verified']['signature_verified']
        assert report['parent_final_verified']['external_krs_calls']==0


def test_fixed_model_five_code_files_and_production_prefix_are_unchanged():
    report={};s.verify_fixed_model(report)
    assert report['fixed_model_sha256']==s.MODEL_SHA
    assert report['fixed_model_and_bound_implementation_changed'] is False
    publication=json.loads((ROOT/s.MODEL).read_text())
    assert all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest for name,digest in publication['code_file_sha256'].items())
    workflow=(ROOT/'.github/workflows/km-jra-formal-single-entry.yml').read_text()
    prefix=workflow.split('\n  pedigree-forward-shadow:')[0]
    original=s.subprocess.check_output(['git','show','b0a377ae06a2d3d15bc47863585e18388e4fea46:.github/workflows/km-jra-formal-single-entry.yml'],cwd=ROOT,text=True)
    assert prefix==original.split('\n  pedigree-forward-shadow:')[0]
    sidecar=workflow.split('\n  pedigree-forward-shadow:')[1]
    assert 'timeout-minutes: 30' in sidecar and 'needs: orchestrate' not in sidecar
    assert "steps.admission.outputs.admitted == 'true'" in sidecar
    assert 'BVI_ENV_PREDICTION_INDEPENDENT_TIMESTAMP_NOT_PRE_CUTOFF' in sidecar


def test_provider_timing_is_observational_and_never_admits_sample(monkeypatch):
    paths=[]
    def api(path):
        paths.append(path)
        if '/attempts/2/jobs' in path:return {'jobs':[{'name':'pedigree-forward-shadow','id':100,'steps':[
            {'name':'Existing witness','status':'completed','conclusion':'success','started_at':'2026-10-25T00:00:01Z','completed_at':'2026-10-25T00:00:04Z'},
            {'name':'Timing now','status':'in_progress','started_at':'2026-10-25T00:00:04Z'}]}]}
        return {'artifacts':[{'name':'jra-pedigree-env-pre-cutoff-123-2','id':99,'created_at':'2026-10-25T00:00:04Z','digest':'sha256:synthetic'}]}
    monkeypatch.setattr(s,'gh_json',api)
    report=s.delivery_timing(123,2)
    assert report['steps'][0]['wall_seconds']==3
    assert report['steps'][1]['wall_seconds'] is None
    assert report['existing_witness_metadata'][0]['id']==99
    assert 'NOT_A_NEW_WITNESS_OR_OOS_ADMISSION' in report['scope']
    assert len(paths)==2


def test_expired_actual_job_wait_budget_stops_even_if_parent_succeeded(tmp_path,monkeypatch):
    fixture(tmp_path)
    monkeypatch.setattr(s,'verify_fixed_model',lambda *a,**kw:None)
    def api(path):
        if path.endswith('/123'):return parent()
        return {'jobs':[{'name':'pedigree-forward-shadow','started_at':(s.utcnow()-s.timedelta(minutes=16)).isoformat()},
            {'name':'orchestrate','status':'completed','conclusion':'success'}]}
    monkeypatch.setattr(s,'gh_json',api)
    monkeypatch.setattr(s,'download_parent_artifact',lambda *a:pytest.fail('Expired provider wait'))
    report={};s.run(123,'runtime/jra_formal_intents/one.json','b'*40,report,root=tmp_path)
    assert report['status']=='PENDING; PARENT_WAIT_BUDGET_OR_CUTOFF_EXPIRED'


def test_different_original_event_sha_rejected(tmp_path,monkeypatch):
    fixture(tmp_path);monkeypatch.setattr(s,'gh_json',lambda *a:parent())
    with pytest.raises(ValueError,match='PARENT_RUN_INVALID'):
        s.run(123,'runtime/jra_formal_intents/one.json','0'*40,{},root=tmp_path)


def test_fixed_model_replacement_rejected(tmp_path):
    path=tmp_path/s.MODEL;path.parent.mkdir(parents=True);path.write_bytes((ROOT/s.MODEL).read_bytes()+b' ')
    with pytest.raises(ValueError,match='FIXED_MODEL_OR_CODE_CHANGED'):
        s.verify_fixed_model({},root=tmp_path)
