"""Default-off isolated GHA reader/publisher; writes one research branch only."""
from __future__ import annotations
import argparse,base64,hashlib,io,json,os,re,subprocess,sys,zipfile
from datetime import datetime,timedelta,timezone
from pathlib import Path
from urllib.parse import quote
from shadow import ROOT,AUTHORITY,EXPERIMENT,build,compare_result,scorecard,digest,fingerprint,time

REPO='b03la013-max/keibametrics-runtime'
BRANCH='research/jra-single-w-zai2-frozen-v1'
RACE=re.compile(r'KM-JRA-[A-Z]{3}-\d{8}-R\d{2}')
def api(path,method='GET',body=None,raw=False,missing=False):
 if not path.startswith(('git/','contents/','actions/')):raise ValueError('RESEARCH_API_SCOPE')
 cmd=['gh','api','--method',method,'repos/'+REPO+'/'+path]
 if body is not None:cmd+=['--input','-']
 p=subprocess.run(cmd,input=None if body is None else json.dumps(body).encode(),capture_output=True)
 if p.returncode:
  if missing and b'HTTP 404' in p.stderr:return None
  raise RuntimeError('GITHUB_RESEARCH_API_FAILED:'+method+':'+path.split('/')[0])
 return p.stdout if raw else json.loads(p.stdout)
def read_json(path,ref=BRANCH):
 v=api('contents/'+path+'?ref='+quote(ref,safe=''),missing=True)
 return json.loads(base64.b64decode(v['content'])) if v else None
def saved_rows(prefix):
 v=api('contents/'+prefix+'?ref='+quote(BRANCH,safe=''),missing=True) or []
 return [read_json(x['path']) for x in v if x.get('type')=='file' and RACE.fullmatch(Path(x['name']).stem)]
def publish(files):
 """Single non-force update; conflicts/unknown replies stop, never replay writes."""
 if BRANCH=='main' or not BRANCH.startswith('research/'):raise ValueError('MAIN_WRITE_FORBIDDEN')
 for p in files:
  if not re.fullmatch(r'(frozen|witness|evaluation)/KM-JRA-[A-Z]{3}-\d{8}-R\d{2}\.json',p):raise ValueError('RESEARCH_PATH_FORBIDDEN')
 ref=api('git/ref/heads/'+BRANCH,missing=True)
 parent=ref['object']['sha'] if ref else None
 pending={}
 for p,v in files.items():
  old=read_json(p,parent) if parent else None
  if old is not None:
   if old!=v:raise ValueError('IMMUTABLE_SHADOW_CONFLICT:'+p)
  else:pending[p]=v
 if not pending:return parent
 tree_body={'tree':[{'path':p,'mode':'100644','type':'blob','content':json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n'} for p,v in pending.items()]}
 if parent:
  commit=api('git/commits/'+parent);tree_body['base_tree']=commit['tree']['sha']
  existing=api('git/trees/'+commit['tree']['sha']+'?recursive=1')
  if existing.get('truncated') or any(x['type']=='blob' and not re.fullmatch(r'(frozen|witness|evaluation)/KM-JRA-[A-Z]{3}-\d{8}-R\d{2}\.json',x['path']) for x in existing['tree']):raise ValueError('RESEARCH_BRANCH_CONTAINS_NONPUBLIC_CONTENT')
 # An orphan public-only branch never inherits main's Raw/complete bodies.
 tree=api('git/trees','POST',tree_body)
 new=api('git/commits','POST',{'message':'research: immutable single-W shadow evidence [skip ci]','tree':tree['sha'],'parents':[parent] if parent else []})
 if ref:api('git/refs/heads/'+BRANCH,'PATCH',{'sha':new['sha'],'force':False})
 else:api('git/refs','POST',{'ref':'refs/heads/'+BRANCH,'sha':new['sha']})
 return new['sha']
def assert_activation(root):
 if os.environ.get('GITHUB_REPOSITORY')!=REPO:raise ValueError('SHADOW_REPOSITORY_REQUIRED')
 if os.environ.get('KM_SINGLE_W_POLICY_ACK')!=fingerprint(root) or not os.environ.get('KM_SINGLE_W_OWNER_ACK_REF'):raise ValueError('OWNER_DESIGN_ACK_REQUIRED')
 from family_authority_guard import resolve_current_authority
 _,authority=resolve_current_authority(root)
 if authority['manifest_id']!=AUTHORITY:raise ValueError('SHADOW_AUTHORITY_CHANGED')
def signed_inputs(root,final):
 from jra_presentation import archived_trust
 from jra_delivery import verify_signed_final
 from execution_store import resolve_phase
 from jra_pedigree_corpus import _verified_source,_attested
 health,contract=archived_trust(final,root=root);verify_signed_final(final,health,contract)
 stage=final['final_prediction_package']['execution_stage_manifest']['SIGNED_SOURCE_RECEIPT_VERIFIED']
 phase=resolve_phase(stage['execution_id'],'SOURCE',root=root/'runtime/executions')
 if phase is None:raise ValueError('SHADOW_SOURCE_CHECKPOINT_MISSING')
 p=phase['run_dir']/'source_receipt_envelope.json';verified=_verified_source(p)
 if not verified or verified['source_snapshot_sha256']!=final['source_snapshot_sha256'] or not _attested(p,signer='km-jra-source-first-runner.yml',not_after=time(final['prediction_cutoff'])):raise ValueError('SHADOW_SOURCE_SIGNATURE_OR_OIDC_FAILED')
 envelope=json.loads(p.read_text())
 if envelope['receipt_sha256']!=stage['receipt_sha256']:raise ValueError('SHADOW_SOURCE_RECEIPT_MISMATCH')
 return envelope['artifact'],envelope['receipt_sha256']
def upload_completion(record):
 jobs=api('actions/runs/'+str(record['workflow_run_id'])+'/attempts/'+str(record['workflow_run_attempt'])+'/jobs?per_page=100')['jobs']
 matches=[{'run_id':job['run_id'],'job_id':job['id'],**step}
          for job in jobs if job['name']=='shadow' for step in job['steps']
          if step['name']=='Archive complete public Shadow coupons'
          and step.get('status')=='completed' and step.get('conclusion')=='success']
 if len(matches)!=1:raise ValueError('UPLOAD_FINALIZE_SERVER_WITNESS_PENDING')
 return matches[0]
def validate_witness(record,artifact,archive,upload_step):
 """Independent server-created artifact with exact, reconstructible coupon."""
 if record.get('sha256')!=digest({k:v for k,v in record.items() if k!='sha256'}):raise ValueError('FREEZE_HASH_INVALID')
 if (artifact.get('expired') or artifact.get('workflow_run',{}).get('id')!=record['workflow_run_id']
     or artifact.get('name')!=f"jra-single-w-zai2-public-coupons-{record['workflow_run_id']}-{record['workflow_run_attempt']}"):
  raise ValueError('ARTIFACT_RUN_OR_EXPIRY')
 created=time(artifact['created_at'])
 post=time(record['scheduled_post_at_original']);cutoff=post-timedelta(seconds=60)
 frozen=time(record['frozen_at']);signed=time(record['production_final_signed_at'])
 if time(record['research_cutoff'])!=cutoff or not signed<=frozen<cutoff:
  raise ValueError('SHADOW_ORIGINAL_POST_CUTOFF_BINDING_FAILED')
 # Server second precision is an interval; its entire interval must be safe.
 if created+timedelta(seconds=1)>cutoff or frozen>created:raise ValueError('SERVER_TIME_ORDER_UNRESOLVED')
 if (upload_step.get('run_id')!=record['workflow_run_id'] or upload_step.get('status')!='completed'
     or upload_step.get('conclusion')!='success'
     or upload_step.get('name')!='Archive complete public Shadow coupons'
     or not upload_step.get('completed_at')):raise ValueError('UPLOAD_FINALIZE_SERVER_WITNESS_REQUIRED')
 finished=time(upload_step['completed_at'])
 if finished<created or finished+timedelta(seconds=1)>cutoff:raise ValueError('UPLOAD_FINISHED_AFTER_RESEARCH_CUTOFF')
 if artifact.get('digest')!='sha256:'+hashlib.sha256(archive).hexdigest():raise ValueError('ARTIFACT_ARCHIVE_SHA_MISMATCH')
 with zipfile.ZipFile(io.BytesIO(archive)) as z:
  names=[n for n in z.namelist() if n.endswith('/'+record['race_id']+'.json') or n==record['race_id']+'.json']
  if len(names)!=1 or json.loads(z.read(names[0]))!=record:raise ValueError('ARTIFACT_COMPLETE_COUPON_MISMATCH')
  manifests=[n for n in z.namelist() if Path(n).name=='publication.json']
  if len(manifests)!=1:raise ValueError('ARTIFACT_PUBLICATION_MANIFEST_REQUIRED')
  manifest=json.loads(z.read(manifests[0]))
  if (manifest.get('workflow_run_id')!=record['workflow_run_id'] or record['race_id'] not in manifest.get('race_ids',[])
      or not re.fullmatch(r'[a-f0-9]{40}',manifest.get('research_commit',''))):raise ValueError('ARTIFACT_PUBLICATION_BINDING_FAILED')
 return manifest
def verified_storage(record,artifact_id):
 meta=api('actions/artifacts/'+str(artifact_id));archive=api('actions/artifacts/'+str(artifact_id)+'/zip',raw=True)
 step=upload_completion(record);manifest=validate_witness(record,meta,archive,step)
 if read_json('frozen/'+record['race_id']+'.json',manifest['research_commit'])!=record:raise ValueError('SHADOW_COMMIT_CONTENT_MISMATCH')
 return {'race_id':record['race_id'],'freeze_sha256':record['sha256'],'research_commit':manifest['research_commit'],
  'artifact_id':artifact_id,'artifact_digest':meta['digest'],'artifact_created_at':meta['created_at'],
  'upload_job_id':step['job_id'],'upload_completed_at':step['completed_at'],
  'workflow_run_id':record['workflow_run_id'],'storage_verified':True,'oos_credit':0}
def storage_or_recover(record):
 old=read_json('witness/'+record['race_id']+'.json')
 if old:
  checked=verified_storage(record,old['artifact_id'])
  if checked!=old:raise ValueError('SHADOW_STORAGE_WITNESS_CONFLICT')
  return checked
 # A crash or not-yet-visible upload completion never recreates a coupon.
 # Recover only the existing server-timed exact original archive.
 arts=api('actions/runs/'+str(record['workflow_run_id'])+'/artifacts?per_page=100')['artifacts']
 target=f"jra-single-w-zai2-public-coupons-{record['workflow_run_id']}-{record['workflow_run_attempt']}"
 matches=[a for a in arts if a['name']==target and not a['expired']]
 if len(matches)!=1:raise ValueError('SHADOW_STORAGE_WITNESS_PENDING')
 checked=verified_storage(record,matches[0]['id']);publish({'witness/'+record['race_id']+'.json':checked})
 return checked
def validate_frozen_binding(record,final,source,source_receipt,*,root=ROOT):
 if (record['final_sha256']!=final['sha256'] or record['source_receipt_sha256']!=source_receipt
     or record['scheduled_post_at_original']!=final['scheduled_post_at']
     or record['production_final_signed_at']!=final['final_receipt']['receipt']['timestamp']
     or record['production_final_freeze']!=final['final_freeze_timestamp']):
  raise ValueError('SHADOW_SIGNED_FINAL_CLOCK_OR_SOURCE_BINDING_FAILED')
 expected=build(final,source,root=root)
 if not expected['eligible'] or any(record.get(k)!=v for k,v in expected.items() if k!='sha256'):
  raise ValueError('SHADOW_PREREGISTERED_COUPON_REPLAY_MISMATCH')
 return True
def freeze(root,out):
 now=datetime.now(timezone.utc);day=now.astimezone(timezone(timedelta(hours=9))).strftime('%Y%m%d')
 old={x['race_id']:x for x in saved_rows('frozen')};valid=reserved=0
 for r in old.values():
  if r['rule_policy_sha256']!=fingerprint(root):raise ValueError('SHADOW_COHORT_POLICY_CHANGED')
  try:storage_or_recover(r);valid+=1;reserved+=1
  except ValueError as exc:
   # Retention expiry or an unavailable archive never reopens a used slot.
   # Only an originally unverified, conclusively invalid freeze may release it.
   witness=read_json('witness/'+r['race_id']+'.json')
   evaluated=read_json('evaluation/'+r['race_id']+'.json')
   previously_verified=(witness and witness.get('storage_verified') is True and witness.get('freeze_sha256')==r['sha256'])
   previously_evaluated=(evaluated and evaluated.get('freeze_sha256')==r['sha256'])
   proven_invalid={'FREEZE_HASH_INVALID','SHADOW_ORIGINAL_POST_CUTOFF_BINDING_FAILED',
     'SERVER_TIME_ORDER_UNRESOLVED','UPLOAD_FINISHED_AFTER_RESEARCH_CUTOFF'}
   if previously_verified or previously_evaluated or str(exc) not in proven_invalid:reserved+=1
  except RuntimeError:reserved+=1
 records=[];holds=[]
 for p in sorted((root/'runtime/final_artifacts').glob('KM-JRA-*-'+day+'-R*.json')):
  if reserved+len(records)>=30:break
  if p.stem in old:continue
  f=json.loads(p.read_text());cutoff=time(f['scheduled_post_at'])-timedelta(seconds=60)
  if now>=cutoff:continue
  try:
   source,sr=signed_inputs(root,f);record=build(f,source,root=root)
   if not record['eligible']:continue
   record.pop('sha256',None);record.update(frozen_at=datetime.now(timezone.utc).isoformat(),research_cutoff=cutoff.isoformat(),
     source_receipt_sha256=sr,code_git_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
     workflow_run_id=int(os.environ['GITHUB_RUN_ID']),workflow_run_attempt=int(os.environ['GITHUB_RUN_ATTEMPT']),
     upstream_run_id=int(os.environ['KM_UPSTREAM_RUN_ID']),owner_ack_ref=os.environ['KM_SINGLE_W_OWNER_ACK_REF'])
   if time(record['frozen_at'])>=cutoff:raise ValueError('SHADOW_RESEARCH_WINDOW_EXPIRED')
   record['sha256']=digest(record);records.append(record)
  except Exception as exc:holds.append({'race_id':p.stem,'status':'TECHNICAL_HOLD','code':str(exc).split(':',1)[0][:100]})
 files={'frozen/'+r['race_id']+'.json':r for r in records}
 if records:
  commit=publish(files)
  for r in records:
   target=out/'frozen'/ (r['race_id']+'.json');target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
  (out/'publication.json').write_text(json.dumps({'research_commit':commit,'race_ids':[r['race_id'] for r in records],'workflow_run_id':int(os.environ['GITHUB_RUN_ID'])}))
 print(json.dumps({'freeze_records':len(records),'technical_holds':holds,'oos_credit':0,'production_change':False}))
def witness(out,artifact_id):
 manifest=json.loads((out/'publication.json').read_text())
 files={}
 for rid in manifest['race_ids']:
  record=read_json('frozen/'+rid+'.json',manifest['research_commit'])
  files['witness/'+rid+'.json']=verified_storage(record,artifact_id)
 publish(files)
 print(json.dumps({'independent_storage_verified':len(files),'oos_credit':0}))
def evaluate(root):
 from execution_store import resolve_phase
 from jra_presentation import archived_trust,_receipt
 from jra_production_postresult import settle_final
 files={};holds=[]
 for r in saved_rows('frozen'):
  rid=r['race_id']
  if read_json('evaluation/'+rid+'.json') is not None:continue
  rp=root/'runtime/results'/(rid+'.json')
  if not rp.exists():continue
  try:
   w=storage_or_recover(r)
   if w['freeze_sha256']!=r['sha256']:raise ValueError('SHADOW_WITNESS_MISSING')
   final=json.loads((root/'runtime/final_artifacts'/(rid+'.json')).read_text());source,sr=signed_inputs(root,final)
   validate_frozen_binding(r,final,source,sr,root=root)
   if final['sha256']!=r['final_sha256']:raise ValueError('SHADOW_FINAL_REVISION_CONFLICT')
   stage=final['final_prediction_package']['execution_stage_manifest']['SIGNED_SOURCE_RECEIPT_VERIFIED'];phase=resolve_phase(stage['execution_id'],'RESULT',root=root/'runtime/executions')
   if phase is None:raise ValueError('SIGNED_RESULT_PENDING')
   req=json.loads(rp.read_text());saved=json.loads((phase['run_dir']/'result_request.json').read_text());env=json.loads((phase['run_dir']/'result_receipt_envelope.json').read_text())
   health,_=archived_trust(final,root=root);receipt=_receipt(env,health['receipt_signer'],rid,'RESULT')
   if saved!=req or receipt['artifact_sha256']!=digest(req) or req['frozen_prediction_ref']['immutable_final_sha256']!=r['final_sha256']:raise ValueError('RESULT_RECEIPT_BINDING_FAILED')
   official=req['official_result'];base=settle_final(final,official)
   if any(base[k]!=req['settlement'][k] for k in ('total_investment','total_payout','refund','pfs')):raise ValueError('SIGNED_SETTLEMENT_REPLAY_MISMATCH')
   comparison=compare_result(r,official);entry={'race_id':rid,'experiment':EXPERIMENT,'classification':'INDEPENDENT_SHADOW_OOS_RESULT_NOT_PRODUCTION_LEARNING',
     'freeze_sha256':r['sha256'],'result_receipt_sha256':env['receipt_sha256'],'official_top3':official['top3'],
     'scheduled_post_at_original':r['scheduled_post_at_original'],'S0_ASI':r['S0_ASI'],'comparison':comparison,
     'S0_W_hit':comparison['S0']['W_hit'],'S1_W_hit':comparison['S1']['W_hit'],
     'added_W_winner_rescue':comparison['added_W_winner_rescue'],
     'code_policy_sha256':r['rule_policy_sha256'],'signed_shadow_result':False,'fixed_BVI_D_credit':0,'actual_purchase':'UNVERIFIED'}
   entry['sha256']=digest(entry);files['evaluation/'+rid+'.json']=entry
  except Exception as exc:holds.append({'race_id':rid,'status':'PENDING_OR_BLOCKED','code':str(exc).split(':',1)[0][:100]})
 if files:publish(files)
 all_results=saved_rows('evaluation')
 print(json.dumps({'joined':len(files),'holds':holds,'scorecard':scorecard(all_results),'production_learning_changes':0,'fixed_BVI_D_credit':0}))
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['freeze','witness','evaluate']);p.add_argument('--out',default='runtime_out/single_w_zai2');p.add_argument('--artifact-id',type=int);a=p.parse_args()
 assert_activation(ROOT);out=ROOT/a.out
 if not out.resolve().is_relative_to((ROOT/'runtime_out').resolve()):raise ValueError('PRIVATE_OR_SOURCE_OUTPUT_FORBIDDEN')
 out.mkdir(parents=True,exist_ok=True)
 {'freeze':lambda:freeze(ROOT,out),'witness':lambda:witness(out,a.artifact_id),'evaluate':lambda:evaluate(ROOT)}[a.mode]()
if __name__=='__main__':main()
