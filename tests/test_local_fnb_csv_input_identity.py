"""Whole prepare/compile revalidation counterexample; no real KRS or approval."""
from copy import deepcopy
from datetime import timedelta
import json

from runtime import local_fnb_csv_research_runtime as runtime
from runtime import local_fnb_csv_signed_capture as signed
from runtime import local_fnb_csv_source_admission as admission
from tests.test_local_fnb_csv_signed_capture import fixture,NOW


def owner_decision(request):
    decision={'profile':'KM-FNB-FIXED-CONTEXT-PRIVATE-OWNER-EXECUTION-DECISION-20261103-R1',
        'decision':'APPROVED_FIXED_MODEL_PRIVATE_NONPRODUCTION_RESEARCH_USE',
        'model_id':'KM-FNB-CONTEXT-PARETO-STATIC-RESEARCH-v0.1-20261103','model_version':'0.1',
        'model_code_sha256':runtime.common.MODEL_SHA,'model_profile_sha256':runtime.common.MODEL_PROFILE_SHA,
        'authorization_observed_at':(NOW-timedelta(days=1)).isoformat(),
        'authority_evidence':{'type':'DIRECT_USER_INSTRUCTION_IN_CURRENT_CHAT','request_id':'SYNTHETIC_ONLY',
            'owner_identity_confirmed_by_direct_instruction':True,'record_is_crypto_signature':False},
        'permitted_scope':{'classification':runtime.common.PRESTART_CLASSIFICATION,'family_id':'LOCAL',
            'venue_id':'FNB','purpose':'WHOLLY_PRIVATE_NONCOMMERCIAL_RESEARCH',
            'races_by_date':{request['race_date']:[request['race_no']]}},
        'selection_policy':'EXISTING_ORIGINAL_STRICT_MEC_ONLY_NEW_PROTECTION_POLICY_NOT_ADOPTED'}
    for key in ('production_owner_adoption','production_scope_changed','numerical_policy_changed',
        'signing_key_created_or_changed','independent_BC_authorized_by_this_record','actual_purchase_authorized'):
        decision[key]=False
    return decision


def test_same_signed_source_prepared_and_compiled_twice_does_not_redispatch_krs(tmp_path,monkeypatch):
    fake,binding,request,envelope,trust,resign=fixture(tmp_path)
    clock=[NOW]
    monkeypatch.setattr(runtime,'_clock',lambda:clock[0])
    monkeypatch.setattr(runtime.common,'_actual_clock',lambda:clock[0])
    owner_path=tmp_path/'synthetic_owner_decision.json'
    owner_raw=runtime.common.encoded(owner_decision(request));owner_path.write_bytes(owner_raw)
    original_pinned=runtime.common._pinned
    monkeypatch.setattr(runtime.common,'_pinned',lambda path,pin: b'SYNTHETIC' if str(path) in
        ('SYNTHETIC_ENGINE','SYNTHETIC_MAP') else original_pinned(path,pin))
    calls=[]
    def synthetic_engine(value,**kwargs):
        calls.append(deepcopy(value));folder=kwargs['destination'];folder.mkdir(parents=True,exist_ok=True)
        output={'summary':[{'horse_no':h['horse_no'],'name':h['name'],
            'SSR-W':0.5,'SSR-P2':0.5,'SSR-P3':0.0,'SSR-T3':1.0} for h in value['horses']]}
        input_raw=runtime.common.encoded(value);output_raw=runtime.common.encoded(output)
        (folder/'execution_input.json').write_bytes(input_raw);(folder/'execution_output.json').write_bytes(output_raw)
        return {'status':'SYNTHETIC_ENGINE_NOT_ACTUAL_KRS','new_engine_execution':True,
            'engine_sha256':runtime.common.ENGINE_SHA,'parameter_map_sha256':runtime.common.MAP_SHA,
            'run_count':5000,'seed':1,'execution_input_sha256':runtime.common.digest(input_raw),
            'output_sha256':runtime.common.digest(output_raw)}
    monkeypatch.setattr(runtime.common,'execute_krs',synthetic_engine)
    def prepare_and_run(trace,freeze=None):
        prepared=signed.prepare_qualified_csv(envelope,request,binding=binding,
            freeze_at=freeze or (NOW-timedelta(seconds=2)).isoformat(),clock=lambda:clock[0],repo_root=fake)
        # Trace changes are not frozen SOURCE facts. Keep the actual signed
        # candidate/raw/freeze/Active set and numerical policy unchanged.
        prepared['assessment']['verified_at']=trace
        prepared['assessment']['sha256']=admission.sha({k:v for k,v in prepared['assessment'].items() if k!='sha256'})
        result=runtime.run_qualified(prepared['assessment'],prepared['request'],
            binding=prepared['consumer_binding'],source_receipt=prepared['source_receipt'],
            private_root=tmp_path/'executions',engine='SYNTHETIC_ENGINE',params='SYNTHETIC_MAP',
            owner_decision_path=owner_path,owner_decision_sha256=runtime.common.digest(owner_raw),
            assessment_original_bytes=runtime.common.encoded(prepared['assessment']),
            source_receipt_original_bytes=json.dumps(prepared['source_receipt'],indent=2 if trace=='first' else None).encode())
        return result
    first=prepare_and_run('first')
    clock[0]=NOW+timedelta(seconds=1)
    second=prepare_and_run('second')
    assert len(calls)==1
    assert second['completion_reused'] is True and second['new_engine_executions_this_call']==0
    assert second['output_directory']==first['output_directory']
    assert second['numerical_original_sha256']==first['numerical_original_sha256']
    assert second['selection_complete'] is False and second['computed_no_bet'] is False
    # A real SOURCE-bound freeze revision is still a distinct execution.
    third=prepare_and_run('third',freeze=(NOW-timedelta(seconds=1)).isoformat())
    assert len(calls)==2 and third['completion_reused'] is False
    assert third['output_directory']!=first['output_directory']


def test_qualified_identity_keeps_raw_signature_active_rights_and_policy_changes():
    source={'source_candidate':{'source_freeze_at':'frozen','active_runner_universe':['1','2'],
        'permission_evidence':{'owner_adoption_sha256':'a'*64}},'sha256':'trace','verified_at':'time1'}
    receipt={'signature':'signature','artifact':{'raw_sha256':'b'*64}}
    def identity(numeric=None,assessment=None,envelope=None,admission_value=None):
        originals={'csv_source_assessment.json':runtime._source_original(assessment or source,None,'SYNTHETIC'),
            'csv_source_receipt_envelope.json':runtime._source_original(envelope or receipt,None,'SYNTHETIC')}
        return runtime._qualified_identity(numeric or {'runners':[],'csv_research_consumer':{
            'actual_generated_at':'time1','assessment_sha256':'trace1'}},
            admission_value or {'profile_sha256':'c'*64,'verified_at':'time1'},originals)
    base=identity()
    changed=deepcopy(source);changed.update(verified_at='time2',sha256='othertrace')
    assert identity(assessment=changed)==base
    for key,value in [('source_freeze_at','otherfreeze'),('active_runner_universe',['1']),
                      ('permission_evidence',{'owner_adoption_sha256':'f'*64})]:
        changed=deepcopy(source);changed['source_candidate'][key]=value
        assert identity(assessment=changed)!=base
    assert identity(envelope={'signature':'other','artifact':receipt['artifact']})!=base
    assert identity(envelope={'signature':'signature','artifact':{'raw_sha256':'f'*64}})!=base
    assert identity(admission_value={'profile_sha256':'f'*64})!=base
