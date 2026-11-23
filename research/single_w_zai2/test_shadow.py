import copy,hashlib,io,json,os,subprocess,sys,zipfile
from pathlib import Path
from unittest.mock import patch
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import shadow,worker
PIN='302304c1a82f87b5509236b3e499fb15e9d80c43'
def original(path):return json.loads(subprocess.check_output(['git','show',PIN+':'+path],cwd=shadow.ROOT))
def fixture(rid):
 f=original('runtime/final_artifacts/'+rid+'.json')
 eid=f['final_prediction_package']['execution_stage_manifest']['SIGNED_SOURCE_RECEIPT_VERIFIED']['execution_id']
 paths=subprocess.check_output(['git','ls-tree','-r','--name-only',PIN,'runtime/executions/'+eid+'/SOURCE'],cwd=shadow.ROOT,text=True).splitlines()
 envelopes=[original(p) for p in paths if p.endswith('/source_receipt_envelope.json')]
 matches=[x for x in envelopes if x['artifact']['source_snapshot_sha256']==f['source_snapshot_sha256']]
 assert len(matches)==1
 return f,matches[0]['artifact']
def test_all_33_actual_frozen_paid_inputs_replay_without_mutation_or_result_selection():
 groups={('TKY','20261031'):(1,2,3,7,8,9,10,11,12),('KYO','20261031'):(1,2,3,7,8,9,10,11,12),
         ('TKY','20261101'):(1,2,3,8,9,10),('KYO','20261101'):(1,2,3,7,8,9,10,11,12)}
 n=eligible=multiple=0
 for (v,d),numbers in groups.items():
  for number in numbers:
   rid=f'KM-JRA-{v}-{d}-R{number:02d}';f,s=fixture(rid);saved=copy.deepcopy((f,s))
   x=shadow.build(f,s);y=shadow.build(f,s);assert x==y and (f,s)==saved
   assert x['oos_credit']==0
   n+=1
   if x['eligible']:
    eligible+=1;assert x['added_W']==x['ZAI_WIN_rank'][1]['runner_id'] or x['added_W'] is None
    assert shadow.ticket_set(x['S0']['tickets'])==shadow.ticket_set(f['final_ticket']['tickets'])
    assert x['full20_value_digest']==shadow.digest(shadow.values(f))
    assert x['S1_KRS_receipt'] is None and x['S1']['stake_yen']<=10000
   else:multiple+=1
 assert (n,eligible,multiple)==(33,24,9)
def test_source_binding_tamper_and_outcome_argument_are_rejected():
 f,s=fixture('KM-JRA-KYO-20261101-R09');bad=copy.deepcopy(s);bad['source_snapshot_sha256']='0'*64
 with pytest.raises(ValueError,match='IDENTITY_MISMATCH'):shadow.build(f,bad)
 with pytest.raises(TypeError):shadow.build(f,s,actual_top3=[6,2,4])
def test_ZAI_ties_follow_production_numeric_runner_order():
 assert shadow.canonical_zai_rank({'10':{'ZAI_WIN':80},'2':{'ZAI_WIN':80},'1':{'ZAI_WIN':90}})==['1','2','10']
def test_unexpected_MEC_error_is_not_a_legal_zero_investment():
 req={'static_prediction':{'roles':{}},'pair_dispositions':[],'third_dispositions':[]}
 with patch.object(shadow,'build_mec_plan',side_effect=shadow.MECError('RUNNER_UNIVERSE_REFERENCE_MISMATCH:9')):
  with pytest.raises(shadow.MECError,match='RUNNER_UNIVERSE'):shadow._portfolio(req,10000)
def test_missing_third_cannot_be_manufactured_by_the_global_P3_floor():
 req={'static_prediction':{'roles':{'1':['W'],'2':['P2'],'3':['P3']}},
      'pair_dispositions':[{'head':'1','second':'2','status':'PURCHASE'}],'third_dispositions':[]}
 with pytest.raises(ValueError,match='REGISTERED_THIRD_DISPOSITION_MISSING'):shadow._portfolio(req,10000)
def test_missing_registered_pair_is_not_a_fabricated_pair_or_legal_no_bet():
 f,s=fixture('KM-JRA-KYO-20261101-R12');x=shadow.build(f,s)
 assert x['S1']['status']=='NO_MATERIAL_HEAD_CONNECTION'
 assert not any(p['head']==x['added_W'] and p['status'] in {'PURCHASE','PROTECT'} for p in x['S1_pairs'])
 official=original('runtime/results/'+f['race_id']+'.json')['official_result']
 c=shadow.compare_result(x,official);assert c['S1']['not_formed'] and not c['S1']['no_bet']
 score=shadow.scorecard([{'race_id':f['race_id'],'scheduled_post_at_original':f['scheduled_post_at'],'comparison':c}])
 assert score['financially_matched_races']==0 and score['S1_not_formed_races']==1
 assert score['S0']['PFS'] is None and score['S1']['PFS'] is None
 c['S0']['profitable']=True
 score=shadow.scorecard([{'race_id':f['race_id'],'scheduled_post_at_original':f['scheduled_post_at'],'comparison':c}])
 assert score['S0']['profitable']==0
 assert 'same_actual_investment_cap' in score
def test_direct_numerical_and_signature_dependencies_are_pinned():
 assert {'runtime/jra_aki_capital_preflight.py','runtime/jra_production_postresult.py',
         'runtime/jra_static_owner_executable.py','runtime/jra_delivery.py'}<=set(shadow.POLICY_FILES)
def witness_fixture():
 r={'race_id':'KM-JRA-TKY-20261107-R01','workflow_run_id':123,'workflow_run_attempt':1,'research_cutoff':'2026-11-07T01:00:00+00:00',
    'scheduled_post_at_original':'2026-11-07T01:01:00+00:00','frozen_at':'2026-11-07T00:59:56.5+00:00',
    'production_final_signed_at':'2026-11-07T00:55:00+00:00','S0':{'tickets':[{'bet_type':'EXACTA','selection':[1,2],'stake':100}]},
    'S1':{'tickets':[{'bet_type':'TRIO','selection':[1,2,3],'stake':100}]}}
 r['sha256']=shadow.digest(r)
 stream=io.BytesIO()
 with zipfile.ZipFile(stream,'w') as z:
  z.writestr(r['race_id']+'.json',json.dumps(r))
  z.writestr('publication.json',json.dumps({'workflow_run_id':123,'research_commit':'c'*40,'race_ids':[r['race_id']]}))
 raw=stream.getvalue();meta={'name':'jra-single-w-zai2-public-coupons-123-1','workflow_run':{'id':123},'expired':False,'created_at':'2026-11-07T00:59:58Z','digest':'sha256:'+hashlib.sha256(raw).hexdigest()}
 return r,meta,raw
def completion(r):return {'run_id':r['workflow_run_id'],'job_id':456,'name':'Archive complete public Shadow coupons','status':'completed','conclusion':'success','completed_at':'2026-11-07T00:59:59Z'}
def zip_changed(r):
 r['sha256']=shadow.digest({k:v for k,v in r.items() if k!='sha256'});stream=io.BytesIO()
 with zipfile.ZipFile(stream,'w') as z:
  z.writestr(r['race_id']+'.json',json.dumps(r))
  z.writestr('publication.json',json.dumps({'workflow_run_id':r['workflow_run_id'],'research_commit':'c'*40,'race_ids':[r['race_id']]}))
 return stream.getvalue()
def test_independent_server_storage_accepts_full_coupons_not_local_git_clocks():
 r,m,b=witness_fixture();assert worker.validate_witness(r,m,b,completion(r))
 for override in ({'created_at':'2026-11-07T01:00:00Z'},{'expired':True},{'workflow_run':{'id':999}},{'digest':'sha256:'+'0'*64}):
  with pytest.raises(ValueError):worker.validate_witness(r,{**m,**override},b,completion(r))
def test_partial_or_changed_coupon_and_forged_author_clock_are_rejected():
 r,m,b=witness_fixture();r['S1']['tickets']=[]
 with pytest.raises(ValueError,match='HASH'):worker.validate_witness(r,m,b,completion(r))
 r['sha256']=shadow.digest({k:v for k,v in r.items() if k!='sha256'})
 with pytest.raises(ValueError,match='COUPON'):worker.validate_witness(r,m,b,completion(r))
 r,m,b=witness_fixture();r['git_author_at']='2020-01-01T00:00:00Z';r['sha256']=shadow.digest({k:v for k,v in r.items() if k!='sha256'})
 with pytest.raises(ValueError,match='SERVER_TIME'):worker.validate_witness(r,{**m,'created_at':'2026-11-07T01:01:00Z'},b,completion(r))
def test_default_off_and_main_write_rejected_before_any_api_call():
 with patch.dict(os.environ,{'GITHUB_REPOSITORY':worker.REPO},clear=True),pytest.raises(ValueError,match='OWNER_DESIGN_ACK'):worker.assert_activation(shadow.ROOT)
 with patch.object(worker,'BRANCH','main'),patch.object(worker,'api') as api,pytest.raises(ValueError,match='MAIN_WRITE'):worker.publish({})
 api.assert_not_called()
def test_cutoff_cannot_be_extended_past_original_post_even_with_valid_zip_hash():
 r,m,b=witness_fixture();r['frozen_at']='2026-11-07T01:02:00Z';r['research_cutoff']='2026-11-08T01:00:00Z'
 b=zip_changed(r);m.update(created_at='2026-11-07T01:03:00Z',digest='sha256:'+hashlib.sha256(b).hexdigest())
 with pytest.raises(ValueError,match='POST_CUTOFF_BINDING'):worker.validate_witness(r,m,b,completion(r))
def test_upload_creation_does_not_prove_upload_finished_before_cutoff():
 r,m,b=witness_fixture();step=completion(r);step['completed_at']='2026-11-07T01:00:01Z'
 with pytest.raises(ValueError,match='UPLOAD_FINISHED'):worker.validate_witness(r,m,b,step)
def test_final_time_and_preregistered_coupon_are_rebound_to_signed_inputs():
 f,s=fixture('KM-JRA-KYO-20261101-R09');r=shadow.build(f,s);r['source_receipt_sha256']='a'*64
 assert worker.validate_frozen_binding(r,f,s,'a'*64)
 for k,value in [('scheduled_post_at_original','2030-01-01T00:00:00Z'),('production_final_signed_at','2030-01-01T00:00:00Z')]:
  bad=copy.deepcopy(r);bad[k]=value
  with pytest.raises(ValueError,match='SIGNED_FINAL_CLOCK'):worker.validate_frozen_binding(bad,f,s,'a'*64)
 bad=copy.deepcopy(r);bad['S1']['tickets']=[]
 with pytest.raises(ValueError,match='COUPON_REPLAY'):worker.validate_frozen_binding(bad,f,s,'a'*64)
def test_immutable_existing_record_conflict_is_never_overwritten():
 with patch.object(worker,'api',return_value={'object':{'sha':'a'*40}}),patch.object(worker,'read_json',return_value={'old':True}),pytest.raises(ValueError,match='IMMUTABLE_SHADOW'):worker.publish({'frozen/KM-JRA-TKY-20261107-R01.json':{'new':True}})
def test_new_public_branch_is_orphan_and_never_copies_main_raw():
 calls=[]
 def client(path,method='GET',body=None,**kw):
  calls.append((path,method,body))
  if method=='GET':return None
  return {'sha':'c'*40}
 with patch.object(worker,'api',side_effect=client):worker.publish({'frozen/KM-JRA-TKY-20261107-R01.json':{'public_coupon':True}})
 assert not any('main' in p for p,_,_ in calls)
 tree=next(b for p,_,b in calls if p=='git/trees');assert 'base_tree' not in tree
 commit=next(b for p,_,b in calls if p=='git/commits');assert commit['parents']==[]
def test_no_cron_no_production_hook_and_fork_write_gate():
 workflow=(shadow.ROOT/'.github/workflows/km-jra-single-w-zai2-shadow.yml').read_text()
 assert 'cron:' not in workflow and 'schedule:' not in workflow
 assert 'head_repository.full_name == github.repository' in workflow and "head_branch == 'main'" in workflow
 assert 'vars.KM_SINGLE_W_POLICY_ACK' in workflow and 'vars.KM_SINGLE_W_OWNER_ACK_REF' in workflow
 assert 'persist-credentials: false' in workflow and 'ref: main' in workflow

@pytest.mark.parametrize('stored_kind',['witness','evaluation'])
def test_thirty_used_slots_survive_artifact_expiry_without_new_freeze(tmp_path,stored_kind):
 policy=shadow.fingerprint(shadow.ROOT)
 old=[{'race_id':f'KM-JRA-TKY-20261107-R{i:02d}','sha256':str(i),'rule_policy_sha256':policy} for i in range(30)]
 finals=tmp_path/'runtime/final_artifacts';finals.mkdir(parents=True)
 day=worker.datetime.now(worker.timezone.utc).astimezone(worker.timezone(worker.timedelta(hours=9))).strftime('%Y%m%d')
 (finals/f'KM-JRA-TKY-{day}-R01.json').write_text(json.dumps({'scheduled_post_at':'2030-01-01T00:00:00Z'}))
 def stored(path,*args):
  rid=Path(path).stem;r=next(r for r in old if r['race_id']==rid)
  if path.startswith(stored_kind+'/'):return {'freeze_sha256':r['sha256'],'storage_verified':True}
 with patch.object(worker,'saved_rows',return_value=old),patch.object(worker,'fingerprint',return_value=policy),\
      patch.object(worker,'storage_or_recover',side_effect=ValueError('ARTIFACT_RUN_OR_EXPIRY')),\
      patch.object(worker,'read_json',side_effect=stored),patch.object(worker,'signed_inputs') as inputs,patch.object(worker,'publish') as writes:
  worker.freeze(tmp_path,tmp_path/'out')
 inputs.assert_not_called();writes.assert_not_called()
