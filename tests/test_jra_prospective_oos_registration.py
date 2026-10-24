"""Real frozen inputs; synthetic provider metadata exercises prospective binding only."""
from copy import deepcopy
from datetime import datetime, timedelta
import io
import json
import hashlib
import base64
import sys
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from jra_role_learning_shadow import (CANDIDATE_ID,POLICY,digest,verify_actions_artifact,
    _preregistration_proof,persist_shadow_result,write_status,actions_pre_result_witness,OOS_SCOPE,
    _registration_scope,snapshot_preregistration_owner_approvals)
from jra_conditional_rank_shadow import ID,EXPOSURE_POLICY,policy_sha
from jra_shadow_checkpoint import pack,execute,restore,CODES,MODEL,validate


def raw_zip(files):
    data=io.BytesIO()
    with zipfile.ZipFile(data,'w') as z:
        for path,body in files.items():z.writestr(path,body if isinstance(body,bytes) else json.dumps(body))
    return data.getvalue()


def resnapshot_registration(s,proof,files,reg,*,refresh_approval=False):
    reg['sha256']=digest({k:v for k,v in reg.items() if k!='sha256'})
    s['oos_preregistration']=reg;s['oos_preregistration_sha256']=digest(reg)
    if refresh_approval:
        owner=proof['owner_approval'];body=_registration_scope(reg)[1]
        owner['record']['body']=json.dumps({'decision':'APPROVE_PROSPECTIVE_SHADOW_PREREGISTRATION',
            'candidate_id':reg['candidate_id'],'scope_sha256':body,'approved_head_sha':owner['approved_head_sha']})
        owner['code_sha256']={p:reg[k] for p,k in zip((*CODES,'runtime/jra_shadow_checkpoint.py'),
            ('sidecar_code_sha256','rank_code_sha256','checkpoint_code_sha256'))}
    files['runtime/jra_race_day_plan/2026-10-24.json']['forward_oos_preregistration']=reg
    files['oos-owner-approval-proofs.json']={reg.get('owner_approval_ref'):deepcopy(proof['owner_approval'])}
    proof['archive']=raw_zip(files);proof['artifact']['digest']='sha256:'+hashlib.sha256(proof['archive']).hexdigest()


def example(tmp_path,*,active=True):
    rid='KM-JRA-TKY-20261024-R03'
    q=json.loads((ROOT/'runtime/requests'/(rid+'-LIVE-R1-FORMAL.json')).read_text())
    f=json.loads((ROOT/'runtime/final_artifacts'/(rid+'.json')).read_text())
    result=json.loads((ROOT/'runtime/results'/(rid+'.json')).read_text())
    for name in (*CODES,MODEL,'runtime/jra_shadow_checkpoint.py','mapping/jra_base_index_evidence_mapping_v1.0_20260921.json'):
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/name).read_bytes())
    model=json.loads((tmp_path/MODEL).read_text())
    reg={'candidate_id':'JRA-CONDITIONAL-RANK-20261025-R2','model_candidate_id':ID,
         'sidecar_candidate_id':CANDIDATE_ID,'portfolio_candidate_id':EXPOSURE_POLICY['candidate_id'],
         'current_authority_manifest':q['current_authority_manifest'],'target_race_ids':[rid],
         'active':active,'status':'OWNER_APPROVED_PREREGISTRATION' if active else 'PREPARED',
         'owner_approval_ref':'https://github.com/b03la013-max/keibametrics-runtime/pull/332#issuecomment-987' if active else None,
         'registered_at':'2026-10-23T11:58:00Z','minimum_forward_distinct_races':60,
         'minimum_forward_days':3,'minimum_forward_venues':2,'no_automatic_promotion':True,
         'eligibility_scope':OOS_SCOPE,
         'production_effect':'NONE','actual_purchase_authority':False,'notification_authority':False,
         'sidecar_code_sha256':hashlib.sha256((tmp_path/CODES[0]).read_bytes()).hexdigest(),
         'rank_code_sha256':hashlib.sha256((tmp_path/CODES[1]).read_bytes()).hexdigest(),
         'checkpoint_code_sha256':hashlib.sha256((tmp_path/'runtime/jra_shadow_checkpoint.py').read_bytes()).hexdigest(),
         'model_sha256':model['sha256'],'model_policy_sha256':policy_sha(model),
         'portfolio_policy_sha256':digest(EXPOSURE_POLICY),'role_policy_fingerprint':digest(POLICY)}
    reg['sha256']=digest(reg)
    pointer={'run_id':456,'artifact_id':789,'run_attempt':1}
    plan={'race_date':q['race_date'],'forward_oos_preregistration':reg,'forward_oos_preregistration_witness':pointer}
    path=tmp_path/'runtime/jra_race_day_plan'/(q['race_date']+'.json');path.parent.mkdir(parents=True);path.write_text(json.dumps(plan))
    c=pack(tmp_path,q,f,created_at=f['final_freeze_timestamp'])
    shadow=execute(tmp_path,c,verify_final=lambda x:None,clock=lambda:f['final_freeze_timestamp'])
    shadow['actions_freeze_context']={'repository':'b03la013-max/keibametrics-runtime','run_id':'123','run_attempt':'1','head_sha':'a'*40}
    shadow['sha256']=digest({k:v for k,v in shadow.items() if k!='sha256'})
    # Producer starts AFTER SOURCE. Registration is proved by the earlier CI.
    source=datetime.fromisoformat(q['source_snapshot']['source_freeze_at'])
    run={'id':123,'run_attempt':1,'repository':{'full_name':'b03la013-max/keibametrics-runtime'},
         'head_repository':{'full_name':'b03la013-max/keibametrics-runtime'},'head_branch':'main','head_sha':'a'*40,
         'path':'.github/workflows/km-formal-request-runner.yml','event':'workflow_dispatch','conclusion':'success',
         'created_at':(source+timedelta(seconds=1)).isoformat()}
    archive=raw_zip({rid+'/role_learning_shadow.json':shadow,rid+'/shadow_input.json':c})
    artifact={'id':1,'name':'krs-utility-123','expired':False,'workflow_run':{'id':123,'head_sha':'a'*40},
              'created_at':shadow['observed_at'],'updated_at':shadow['observed_at'],'digest':'sha256:'+hashlib.sha256(archive).hexdigest()}
    prior_run={**run,'id':456,'head_sha':'b'*40,'path':'.github/workflows/km-jra-learning-binding-audit.yml','event':'push','created_at':'2026-10-23T12:00:00Z'}
    prior_files={'runtime/jra_race_day_plan/'+q['race_date']+'.json':plan}
    prior_files.update({p:(tmp_path/p).read_bytes() for p in (*CODES,'runtime/jra_shadow_checkpoint.py',MODEL)})
    # Synthetic authenticated-provider metadata, never a real Owner approval claim.
    owner={'endpoint':'issues/comments/987','approved_head_sha':'c'*40,
        'record':{'id':987,'html_url':reg['owner_approval_ref'],'user':{'login':'b03la013-max'},
                  'issue_url':'https://api.github.com/repos/b03la013-max/keibametrics-runtime/issues/332',
                  'created_at':'2026-10-23T11:55:00Z','updated_at':'2026-10-23T11:55:00Z'},
        'code_sha256':{p:reg[k] for p,k in zip((*CODES,'runtime/jra_shadow_checkpoint.py'),
                         ('sidecar_code_sha256','rank_code_sha256','checkpoint_code_sha256'))},
        'model_sha256':model['sha256'],'model_policy_sha256':policy_sha(model)}
    owner['record']['body']=json.dumps({'decision':'APPROVE_PROSPECTIVE_SHADOW_PREREGISTRATION',
        'candidate_id':reg['candidate_id'],'scope_sha256':_registration_scope(reg)[1],'approved_head_sha':'c'*40})
    prior_files['oos-owner-approval-proofs.json']={reg['owner_approval_ref']:owner} if active else {}
    prior_archive=raw_zip(prior_files)
    prior_artifact={'id':789,'name':'jra-learning-mechanical-456','expired':False,'workflow_run':{'id':456,'head_sha':'b'*40},
                    'created_at':'2026-10-23T12:01:00Z','updated_at':'2026-10-23T12:01:00Z',
                    'digest':'sha256:'+hashlib.sha256(prior_archive).hexdigest()}
    proof={'run':prior_run,'artifact':prior_artifact,'archive':prior_archive,'owner_approval':owner,'owner_approval_record':owner['record']}
    return q,f,result,c,shadow,run,artifact,archive,proof,prior_files


def test_real_freeze_connects_distinct_cohort_without_relabelling_model(tmp_path):
    q,f,result,c,s,run,a,data,proof,_=example(tmp_path)
    before=deepcopy((q,f,result))
    assert c['oos_preregistration']==s['oos_preregistration']
    assert s['oos_candidate_id']=='JRA-CONDITIONAL-RANK-20261025-R2'
    assert s['candidate_id']==CANDIDATE_ID and s['conditional_rank_comparison']['candidate_id']==ID
    assert datetime.fromisoformat(run['created_at'])>datetime.fromisoformat(s['source_freeze_at'])
    w=verify_actions_artifact(s,run,a,data,(ROOT/CODES[0]).read_bytes(),registration_proof=proof)
    assert w['verified'] and w['preregistration_verified']
    assert w['preregistration']['archive_and_pins_verified'] and w['preregistration']['owner_approval_verified']
    assert w['preregistration']['candidate_id']==s['oos_candidate_id']
    assert (q,f,result)==before


def test_producer_archive_without_earlier_registration_proof_is_not_oos(tmp_path):
    _,_,_,_,s,run,a,data,_,_=example(tmp_path)
    w=verify_actions_artifact(s,run,a,data,(ROOT/CODES[0]).read_bytes())
    assert w['verified'] and not w['preregistration_verified']


def test_prior_registration_cannot_hide_an_altered_actual_prediction_input(tmp_path):
    _,_,_,c,s,run,a,_,proof,_=example(tmp_path)
    s['prediction_input_sha256']='0'*64
    s['sha256']=digest({k:v for k,v in s.items() if k!='sha256'})
    data=raw_zip({s['race_id']+'/role_learning_shadow.json':s,s['race_id']+'/shadow_input.json':c})
    a['digest']='sha256:'+hashlib.sha256(data).hexdigest()
    with pytest.raises(ValueError,match='CHECKPOINT_BINDING'):
        verify_actions_artifact(s,run,a,data,(ROOT/CODES[0]).read_bytes(),registration_proof=proof)


@pytest.mark.parametrize('proof_available',[True,False])
def test_provider_read_path_loads_exact_prior_run_and_archive(tmp_path,proof_available):
    _,_,_,_,s,run,a,data,proof,_=example(tmp_path)
    a['size_in_bytes']=len(data)
    payloads={'actions/runs/123/attempts/1':run,
              'actions/runs/123/artifacts?per_page=100':{'artifacts':[a]},
              'actions/runs/456/attempts/1':proof['run'],
              'actions/artifacts/789':proof['artifact'],
              'actions/artifacts/789/zip':proof['archive'],
              'actions/artifacts/1/zip':data,'issues/comments/987':proof['owner_approval']['record']}
    for head in (run['head_sha'],'c'*40):
        for name in (*CODES,'runtime/jra_shadow_checkpoint.py',MODEL):
            payloads['contents/'+name+'?ref='+head]={
                'content':base64.b64encode((ROOT/name).read_bytes()).decode()}
    calls=[]
    def read_only_api(args,**kwargs):
        assert args[:4]==['gh','api','--hostname','github.com']
        assert args[4].startswith('repos/b03la013-max/keibametrics-runtime/')
        path=args[4].split('/',3)[3];calls.append(path)
        assert len(args)==5 and kwargs['timeout'] in (10,30)
        if not proof_available and path=='actions/runs/456/attempts/1':raise OSError('synthetic unavailable prior archive')
        body=payloads[path]
        return body if isinstance(body,bytes) else json.dumps(body).encode()
    with patch('jra_role_learning_shadow.subprocess.check_output',side_effect=read_only_api):
        w=actions_pre_result_witness(s)
    assert w['verified'] and w['preregistration_verified'] is proof_available
    assert 'actions/runs/456/attempts/1' in calls and 'actions/artifacts/1/zip' in calls
    assert ('actions/artifacts/789/zip' in calls) is proof_available


def test_existing_ci_owner_snapshot_uses_only_authenticated_read_paths(tmp_path):
    *_,proof,_=example(tmp_path)
    owner=proof['owner_approval'];calls=[]
    def api(args,**kwargs):
        assert args[:4]==['gh','api','--hostname','github.com'] and len(args)==5
        path=args[4].split('/',3)[3];calls.append(path)
        if path=='issues/comments/987':return json.dumps(owner['record']).encode()
        assert path.endswith('?ref='+'c'*40)
        name=path[len('contents/'):].split('?')[0]
        return json.dumps({'content':base64.b64encode((ROOT/name).read_bytes()).decode()}).encode()
    with patch('jra_role_learning_shadow.subprocess.check_output',side_effect=api):
        saved=snapshot_preregistration_owner_approvals(tmp_path,tmp_path/'owner.json')
    assert list(saved.values())==[owner] and len(calls)==5


@pytest.mark.parametrize('field,value',[
    ('active',False),('owner_approval_ref',None),('sidecar_code_sha256','0'*64),
    ('model_sha256','0'*64),('model_policy_sha256','0'*64),('role_policy_fingerprint','0'*64),
    ('model_candidate_id','WRONG'),('candidate_id',ID),('target_race_ids',[]),
    ('minimum_forward_days',2),('minimum_forward_distinct_races',59),('minimum_forward_venues',1),
    ('notification_authority',True),('actual_purchase_authority',True),
    ('eligibility_scope','ALL_ROLE_LEARNING_ARMS')])
def test_unapproved_mismatched_or_relaxed_registration_is_ineligible(tmp_path,field,value):
    *_,s,run,a,data,proof,files=example(tmp_path)
    reg=deepcopy(s['oos_preregistration']);reg[field]=value;reg['sha256']=digest({k:v for k,v in reg.items() if k!='sha256'})
    s['oos_preregistration']=reg;s['oos_preregistration_sha256']=digest(reg)
    assert not _preregistration_proof(s,proof)['verified']


@pytest.mark.parametrize('change',['late','wrong_digest','branch','head','code','duplicate'])
def test_independent_registration_archive_binding_failures(tmp_path,change):
    _,_,_,_,s,_,_,_,proof,files=example(tmp_path)
    if change=='late':proof['artifact']['created_at']=proof['artifact']['updated_at']=s['source_freeze_at']
    elif change=='wrong_digest':proof['artifact']['digest']='sha256:'+'0'*64
    elif change=='branch':proof['run']['head_branch']='unapproved'
    elif change=='head':proof['artifact']['workflow_run']['head_sha']='c'*40
    elif change=='code':
        files['runtime/jra_shadow_checkpoint.py']=b'wrong';proof['archive']=raw_zip(files)
        proof['artifact']['digest']='sha256:'+hashlib.sha256(proof['archive']).hexdigest()
    else:
        stream=io.BytesIO(proof['archive'])
        with pytest.warns(UserWarning,match='Duplicate name'):
            with zipfile.ZipFile(stream,'a') as z:z.writestr('runtime/jra_race_day_plan/2026-10-24.json',json.dumps(files['runtime/jra_race_day_plan/2026-10-24.json']))
        proof['archive']=stream.getvalue();proof['artifact']['digest']='sha256:'+hashlib.sha256(proof['archive']).hexdigest()
    assert not _preregistration_proof(s,proof)['verified']


def test_checkpoint_resume_keeps_original_registration_and_rejects_replacement(tmp_path):
    q,f,_,c,s,_,_,_,_,_=example(tmp_path)
    changed=deepcopy(c);changed['oos_preregistration']['candidate_id']='JRA-CHANGED-R3'
    changed['sha256']=digest({k:v for k,v in changed.items() if k!='sha256'})
    with pytest.raises(ValueError,match='PREREGISTRATION_HASH'):validate(tmp_path,changed)
    # Later live plan changes do not mutate the stored checkpoint or old model.
    plan=tmp_path/'runtime/jra_race_day_plan/2026-10-24.json';plan.write_text('{}')
    assert validate(tmp_path,c)==c
    with pytest.raises(ValueError,match='WITNESS'):
        altered=deepcopy(s);altered['oos_preregistration_witness']['artifact_id']+=1
        altered['sha256']=digest({k:v for k,v in altered.items() if k!='sha256'})
        restore(tmp_path,c,altered,witness=lambda s:{'verified':True})


def test_result_qualification_and_tracker_do_not_pool_legacy_records(tmp_path):
    _,_,result,_,s,run,a,data,proof,_=example(tmp_path)
    pre=tmp_path/'runtime/role_rescue_shadow'/(s['race_id']+'.json');pre.write_text(json.dumps(s))
    verified=verify_actions_artifact(s,run,a,data,(ROOT/CODES[0]).read_bytes(),registration_proof=proof)
    with patch('jra_role_learning_shadow.actions_pre_result_witness',return_value=verified):out=persist_shadow_result(tmp_path,result)
    assert out['oos_eligible'] and out['oos_candidate_id']==s['oos_candidate_id']
    assert out['oos_eligibility_scope']==OOS_SCOPE and out['role_learning_arms_oos_eligible'] is None
    p=tmp_path/'runtime/role_rescue_shadow_results'/(s['race_id']+'.json');before=p.read_bytes()
    with patch('jra_role_learning_shadow.actions_pre_result_witness',side_effect=AssertionError('must reuse original')):
        assert persist_shadow_result(tmp_path,result)==out
    assert p.read_bytes()==before
    bad=deepcopy(result);bad['official_result']['top3']=list(reversed(bad['official_result']['top3']))
    with pytest.raises(ValueError,match='IMMUTABLE'):persist_shadow_result(tmp_path,bad)
    legacy={k:v for k,v in out.items() if k not in ('oos_candidate_id','oos_preregistration_sha256','preregistration_verified')}
    legacy['race_id']='KM-JRA-KYO-20261024-R01';legacy['persistence_witness']={'verified':True}
    legacy['sha256']=digest({k:v for k,v in legacy.items() if k!='sha256'})
    (p.parent/(legacy['race_id']+'.json')).write_text(json.dumps(legacy))
    tracker=write_status(tmp_path/'runtime/role_rescue_shadow_status.json')
    assert tracker['forward_oos_verified_races']==1 and tracker['legacy_recorded_eligible_races']==1
    assert tracker['cohorts']['LEGACY_UNREGISTERED']['forward_oos_verified_races']==0
    assert tracker['cohorts'][s['oos_candidate_id']]['forward_oos_verified_races']==1
    assert all(not c['automatic_promotion'] for c in tracker['cohorts'].values())


def test_provider_witness_alone_never_qualifies_a_new_result(tmp_path):
    _,_,result,_,s,_,_,_,_,_=example(tmp_path,active=False)
    pre=tmp_path/'runtime/role_rescue_shadow'/(s['race_id']+'.json');pre.write_text(json.dumps(s))
    with patch('jra_role_learning_shadow.actions_pre_result_witness',return_value={'verified':True,'preregistration_verified':False}):
        out=persist_shadow_result(tmp_path,result)
    assert not out['oos_eligible']


def test_registration_date_and_target_extension_do_not_change_pin_identity(tmp_path):
    _,_,_,_,s,_,_,_,proof,files=example(tmp_path)
    original=_preregistration_proof(s,proof)
    assert original['verified']
    reg=deepcopy(s['oos_preregistration']);reg['registered_at']='2026-10-23T11:59:00Z'
    reg['target_race_ids'].append('KM-JRA-KYO-20261025-R01')
    resnapshot_registration(s,proof,files,reg,refresh_approval=True)
    extended=_preregistration_proof(s,proof)
    assert extended['verified'] and extended['registration_sha256']!=original['registration_sha256']
    assert extended['pin_fingerprint']==original['pin_fingerprint']


def test_even_same_candidate_id_has_different_fingerprint_when_executed_code_changes(tmp_path):
    _,_,_,_,s,_,_,_,proof,files=example(tmp_path)
    original=_preregistration_proof(s,proof)
    files[CODES[0]]+=b'\n# Synthetic different code bytes for pin-identity regression.\n'
    code_sha=hashlib.sha256(files[CODES[0]]).hexdigest()
    reg=deepcopy(s['oos_preregistration']);reg['sidecar_code_sha256']=code_sha
    s['code_sha256']=code_sha
    resnapshot_registration(s,proof,files,reg,refresh_approval=True)
    changed=_preregistration_proof(s,proof)
    assert original['verified'] and changed['verified']
    assert changed['candidate_id']==original['candidate_id'] and changed['pin_fingerprint']!=original['pin_fingerprint']


def test_one_candidate_id_cannot_pool_different_code_model_policy_pins(tmp_path):
    _,_,result,_,s,run,a,data,proof,_=example(tmp_path)
    pre=tmp_path/'runtime/role_rescue_shadow'/(s['race_id']+'.json');pre.write_text(json.dumps(s))
    w=verify_actions_artifact(s,run,a,data,(ROOT/CODES[0]).read_bytes(),registration_proof=proof)
    with patch('jra_role_learning_shadow.actions_pre_result_witness',return_value=w):out=persist_shadow_result(tmp_path,result)
    # A second immutable record has its own matching witness/registration, but a different pinned bundle.
    other=deepcopy(out);other['race_id']='KM-JRA-KYO-20261025-R01'
    other['oos_pin_fingerprint']='d'*64
    other['persistence_witness']['preregistration']['pin_fingerprint']='d'*64
    other['oos_preregistration_sha256']='e'*64
    other['persistence_witness']['preregistration']['registration_sha256']='e'*64
    other['sha256']=digest({k:v for k,v in other.items() if k!='sha256'})
    p=tmp_path/'runtime/role_rescue_shadow_results'/(other['race_id']+'.json');p.write_text(json.dumps(other))
    tracker=write_status(tmp_path/'runtime/role_rescue_shadow_status.json')
    assert tracker['forward_oos_verified_races']==0 and tracker['legacy_recorded_eligible_races']==0
    assert tracker['unqualified_recorded_claims']==2
    cohort=tracker['cohorts'][s['oos_candidate_id']]
    assert cohort['eligibility_status']=='COHORT_PIN_CONFLICT' and len(cohort['pin_fingerprints'])==2
    assert not cohort['automatic_promotion'] and cohort['days']==[]


@pytest.mark.parametrize('change',['missing','self_asserted_true','fake_ref','wrong_actor','wrong_scope','late','wrong_head_pins','edited_after_archive','missing_archived_snapshot','null_body','null_user'])
def test_archive_and_pins_do_not_substitute_for_owner_scope_approval(tmp_path,change):
    _,_,_,_,s,_,_,_,proof,files=example(tmp_path)
    reg=deepcopy(s['oos_preregistration']);owner=proof['owner_approval']
    if change=='missing':proof.pop('owner_approval_record')
    elif change=='self_asserted_true':proof['owner_approval_record']={'verified':True}
    elif change=='fake_ref':
        reg['owner_approval_ref']='SYNTHETIC_TEST_OWNER_REF_NOT_REAL_APPROVAL'
        resnapshot_registration(s,proof,files,reg)
    elif change=='wrong_actor':owner['record']['user']['login']='unapproved-user'
    elif change=='wrong_scope':
        body=json.loads(owner['record']['body']);body['scope_sha256']='0'*64;owner['record']['body']=json.dumps(body)
    elif change=='late':owner['record']['updated_at']='2026-10-24T12:00:00Z'
    elif change=='wrong_head_pins':owner['code_sha256'][CODES[0]]='0'*64
    elif change=='edited_after_archive':owner['record']['body']+='\n'
    elif change=='missing_archived_snapshot':files.pop('oos-owner-approval-proofs.json')
    elif change=='null_body':owner['record']['body']=None
    elif change=='null_user':owner['record']['user']=None
    if change in {'wrong_actor','wrong_scope','late','wrong_head_pins','null_body','null_user'}:
        resnapshot_registration(s,proof,files,reg)
    if change=='missing_archived_snapshot':
        proof['archive']=raw_zip(files);proof['artifact']['digest']='sha256:'+hashlib.sha256(proof['archive']).hexdigest()
    got=_preregistration_proof(s,proof)
    assert got['archive_and_pins_verified'] and not got['verified'] and not got['owner_approval_verified']


@pytest.mark.parametrize('state',['APPROVED','PENDING','DISMISSED','CHANGES_REQUESTED'])
def test_owner_review_must_remain_approved_and_match_earlier_archived_scope(tmp_path,state):
    _,_,_,_,s,_,_,_,proof,files=example(tmp_path)
    reg=deepcopy(s['oos_preregistration'])
    reg['owner_approval_ref']=reg['owner_approval_ref'].replace('issuecomment-','pullrequestreview-')
    owner=proof['owner_approval'];owner['endpoint']='pulls/332/reviews/987'
    owner['record']={'id':987,'html_url':reg['owner_approval_ref'],'user':{'login':'b03la013-max'},
        'pull_request_url':'https://api.github.com/repos/b03la013-max/keibametrics-runtime/pulls/332',
        'state':state,'commit_id':owner['approved_head_sha'],'submitted_at':'2026-10-23T11:55:00Z',
        'body':owner['record']['body']}
    proof['owner_approval_record']=owner['record']
    resnapshot_registration(s,proof,files,reg)
    got=_preregistration_proof(s,proof)
    assert got['archive_and_pins_verified'] and got['verified'] is (state=='APPROVED')
