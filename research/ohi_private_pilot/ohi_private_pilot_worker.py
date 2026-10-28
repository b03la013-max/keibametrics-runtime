"""Thin private OHI R1 pilot: inherited SOURCE/calculation only, private S3 and log relay.

This file is a deployment candidate with local boundary tests, not an active worker.
No Production endpoint is invoked. It refuses the wrong actor/date, a public
GitHub log destination, missing private bindings, or a late/stale SOURCE.
"""
from __future__ import annotations
import argparse,base64,hashlib,io,json,os,re,sys,tempfile,traceback,zipfile
from datetime import datetime,timezone,timedelta
from pathlib import Path

TARGET_DAY='2026-10-28';RACE_NO=1
RACE_ID='2026102820110301'
BOOTSTRAP_KEY='bootstrap/OHI_FIXED_INPUTS_20261028_TRANSPORT_R2.zip'
BOOTSTRAP_SHA='cb58d1947e4cdb7685de3d26d80b90209f2f81b48fb2628846858b0190a032f9'
BOOTSTRAP_BYTES=171281
MAX_BUCKET_BYTES=1_000_000_000
STAGE='ACTOR_BINDING'
PROJECT='25ce549e-de35-4138-9c8f-490e407c7b81'
ENVIRONMENT='90201e32-e372-465b-8e80-a205a39ba440'
SERVICE='f6d3c60e-34f2-43fa-9247-a71f7b209bf9'
MODEL='1706af57e008bd158214f70edc77b0f2eb59c220c828202f71ef770ad25b3a84'
MODEL_BYTES='4740fb6b31ce80e248d2eaedeeec00c512bebd87b598385f08fb0d2e2f0481d6'
ENGINE='9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421'
PARAMS='d8c027ee5bcc8fd3d2c248e8059b341776be38910e833d7589f09ab817c161f5'
JST=timezone(timedelta(hours=9))

def digest(b):return hashlib.sha256(b).hexdigest()
def seal(d):return {**d,'sha256':digest(json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())}
def validate_record(d):
 if d.get('sha256')!=seal({k:v for k,v in d.items()if k!='sha256'})['sha256']:raise ValueError('PRIVATE_RECORD_SHA_MISMATCH')
 return d
def stage(name):
 global STAGE
 STAGE=name

def require_execution_window(now):
 if now.tzinfo is None:raise ValueError('PRIVATE_PILOT_TIMEZONE_REQUIRED')
 local=now.astimezone(JST)
 if local.date().isoformat()!=TARGET_DAY:raise ValueError('PRIVATE_PILOT_EXACT_DATE_NOT_ACTIVE')
 if local.hour<14:raise ValueError('PRIVATE_PILOT_BEFORE_SINGLE_RUN_WINDOW')
 if local>=datetime(2026,10,28,14,25,tzinfo=JST):raise ValueError('PRIVATE_PILOT_CUTOFF_PASSED')
 # The captured official Program's cutoff is still independently enforced.

def require_resource_limits(root=Path('/sys/fs/cgroup')):
 try:
  if (root/'cpu.max').is_file():
   quota,period=(root/'cpu.max').read_text().split()
   memory=int((root/'memory.max').read_text())
  else:
   quota=(root/'cpu/cpu.cfs_quota_us').read_text().strip()
   period=(root/'cpu/cpu.cfs_period_us').read_text().strip()
   memory=int((root/'memory/memory.limit_in_bytes').read_text())
  quota,period=int(quota),int(period)
 except (OSError,ValueError):raise ValueError('PRIVATE_PILOT_RESOURCE_LIMITS_UNVERIFIED') from None
 if quota<=0 or period<=0 or quota>period or not 0<memory<=512*1024*1024:
  raise ValueError('PRIVATE_PILOT_RESOURCE_LIMITS_EXCEED_APPROVAL')
 return {'vCPU_limit':quota/period,'memory_limit_bytes':memory,'verified_from_cgroup':True}

def require_race(race):
 if (race.get('race_date'),race.get('race_no'),race.get('provider_race_id'))!=(TARGET_DAY,RACE_NO,RACE_ID):
  raise ValueError('PRIVATE_PILOT_OFFICIAL_RACE_ID_CONFLICT')

def hold_event(error):
 # Report actual failure location without logging credentials, URLs or Raw.
 location=STAGE
 functions={'numerical':'INDICES_29','feature_pack':'OWNERS','predict_conditioned_owner':'OWNERS',
            'simulate':'KRS','build_candidate_krs':'KRS','selection':'MEC_CAPITAL_TICKETS',
            'build_mec_plan':'MEC','resolve_capital_policy':'CAPITAL','render_ticket_tree':'ALL_TICKETS_RENDER'}
 for frame in traceback.extract_tb(error.__traceback__):
  if frame.name in functions:location=functions[frame.name]
 candidate=getattr(error,'receipt',{})
 candidate=candidate.get('code','') if isinstance(candidate,dict) else ''
 if not isinstance(candidate,str):candidate=''
 if not candidate and isinstance(error,ValueError):candidate=str(error).split(':',1)[0]
 code=candidate if re.fullmatch(r'(?:PRIVATE_|FIXED_|OHI_|SOURCE_|NANKAN_)[A-Z0-9_]{1,100}',candidate or '') else 'PILOT_EXTERNAL_OR_SOURCE_HOLD'
 return {'schema':'KM_OHI_PRIVATE_PILOT_HOLD_V1','date':TARGET_DAY,'race_no':RACE_NO,'race_id':RACE_ID,
         'stage':location,'error_type':type(error).__name__,'error_code':code,'new_Production_or_OOS':0}
def require_actor(env,now):
 if env.get('GITHUB_ACTIONS','').lower()=='true':raise ValueError('PRIVATE_BODY_PUBLIC_GITHUB_LOG_FORBIDDEN')
 if (env.get('RAILWAY_PROJECT_ID'),env.get('RAILWAY_ENVIRONMENT_ID'),env.get('RAILWAY_SERVICE_ID'))!=(PROJECT,ENVIRONMENT,SERVICE):raise ValueError('PRIVATE_PILOT_ACTOR_NOT_BOUND')
 if now.astimezone(JST).date().isoformat()!=TARGET_DAY:raise ValueError('PRIVATE_PILOT_EXACT_DATE_NOT_ACTIVE')
 if not all(env.get(k)for k in ['OHI_S3_ENDPOINT','OHI_S3_BUCKET','OHI_S3_ACCESS_KEY_ID','OHI_S3_SECRET_ACCESS_KEY','OHI_FIXED_CODE_ROOT','OHI_FIXED_ASSET_ROOT','OHI_FIXED_CONTRACT_PATH','OHI_BOOTSTRAP_KEY','OHI_BOOTSTRAP_SHA256']):raise ValueError('PRIVATE_PILOT_BINDINGS_MISSING')
 if not env['OHI_S3_ENDPOINT'].startswith('https://'):raise ValueError('PRIVATE_STORE_TLS_REQUIRED')

def safe_extract(data,destination):
 destination=Path(destination).resolve();destination.mkdir(parents=True,exist_ok=True,mode=0o700)
 with zipfile.ZipFile(io.BytesIO(data))as z:
  if z.testzip()is not None:raise ValueError('PRIVATE_ARCHIVE_CRC_MISMATCH')
  if len(z.infolist())>5000 or sum(x.file_size for x in z.infolist())>200_000_000:raise ValueError('PRIVATE_ARCHIVE_LIMIT')
  names=set()
  for item in z.infolist():
   p=Path(item.filename)
   if item.filename in names or p.is_absolute()or'..'in p.parts or ((item.external_attr>>16)&0o170000)==0o120000:raise ValueError('PRIVATE_ARCHIVE_PATH_CONFLICT')
   names.add(item.filename);out=destination/p
   if item.is_dir():out.mkdir(parents=True,exist_ok=True,mode=0o700);continue
   out.parent.mkdir(parents=True,exist_ok=True,mode=0o700);out.write_bytes(z.read(item));out.chmod(0o600)
 return destination

class PrivateStore:
 def __init__(self,env):
  import boto3
  from botocore.config import Config
  self.bucket=env['OHI_S3_BUCKET'];self.client=boto3.client('s3',endpoint_url=env['OHI_S3_ENDPOINT'],aws_access_key_id=env['OHI_S3_ACCESS_KEY_ID'],aws_secret_access_key=env['OHI_S3_SECRET_ACCESS_KEY'],region_name=env.get('OHI_S3_REGION','auto'),config=Config(connect_timeout=15,read_timeout=30,retries={'max_attempts':2}))
 def get(self,key):
  from botocore.exceptions import ClientError
  try:
   stream=self.client.get_object(Bucket=self.bucket,Key=key)['Body']
   try:data=stream.read(200_000_001)
   finally:stream.close()
   if len(data)>200_000_000:raise ValueError('PRIVATE_STORE_OBJECT_LIMIT')
   return data
  except ClientError as e:
   if e.response.get('Error',{}).get('Code')in ['NoSuchKey','404']:return None
   raise
 def latest_record(self,prefix):
  rows=self.client.list_objects_v2(Bucket=self.bucket,Prefix=prefix+'records/',MaxKeys=1000)
  if rows.get('IsTruncated'):raise ValueError('PRIVATE_HISTORY_LIST_LIMIT')
  keys=sorted(x['Key']for x in rows.get('Contents',[])if x['Key'].endswith('.json'))
  return self.get(keys[-1])if keys else None
 def put_new_and_read(self,key,data):
  # Dedicated research bucket only; a truncated inventory cannot prove capacity.
  rows=self.client.list_objects_v2(Bucket=self.bucket,MaxKeys=1000)
  if rows.get('IsTruncated'):raise ValueError('PRIVATE_BUCKET_CAPACITY_UNVERIFIED')
  if sum(x['Size']for x in rows.get('Contents',[]))+len(data)>MAX_BUCKET_BYTES:
   raise ValueError('PRIVATE_BUCKET_APPROVED_SIZE_EXCEEDED')
  # A conditional create prevents overwriting any old frozen object.
  self.client.put_object(Bucket=self.bucket,Key=key,Body=data,IfNoneMatch='*',ContentType='application/octet-stream')
  actual=self.get(key)
  if actual!=data:raise ValueError('PRIVATE_STORE_ACTUAL_BYTE_READBACK_MISMATCH')
  return {'key':key,'bytes':len(data),'sha256':digest(actual),'actual_object_GET':True}

def claim_single_run(store,prefix,now,env):
 stage('SINGLE_RUN_CLAIM')
 claim=seal({'purpose':'ONE_APPROVED_PRIVATE_EXECUTION_NOT_COMPLETION','date':TARGET_DAY,
             'race_no':RACE_NO,'race_id':RACE_ID,'claimed_at':now.isoformat(),
             'project_id':PROJECT,'environment_id':ENVIRONMENT,'service_id':SERVICE,
             'deployment_id':env.get('RAILWAY_DEPLOYMENT_ID'),'prediction_calculated':False})
 try:
  return store.put_new_and_read(prefix+'single-run/execute-claim.json',
         (json.dumps(claim,sort_keys=True)+'\n').encode())
 except Exception as exc:
  response=getattr(exc,'response',{})
  code=(response.get('Error')or{}).get('Code') if isinstance(response,dict) else None
  status=(response.get('ResponseMetadata')or{}).get('HTTPStatusCode') if isinstance(response,dict) else None
  if code in ('PreconditionFailed','ConditionalRequestConflict','412')or status==412:
   raise ValueError('PRIVATE_PILOT_EXECUTION_ALREADY_CLAIMED') from None
  raise
 # The claim is never replaced, removed or automatically retried, even on failure.

def protected_work_binding(env):
 stage('PROTECTED_WORK_BINDINGS')
 names=('OHI_PROTECTED_WORK_ARCHIVE_KEY','OHI_PROTECTED_WORK_ARCHIVE_SHA256',
        'OHI_PROTECTED_WORK_ARCHIVE_BYTES','OHI_PROTECTED_WORK_ORIGINAL_SHA256')
 values=[env.get(name)for name in names]
 if not all(values):raise ValueError('PRIVATE_PROTECTED_WORK_BINDINGS_INCOMPLETE')
 key,archive_sha,size,prediction_sha=values
 if not re.fullmatch('[0-9a-f]{64}',archive_sha)or not re.fullmatch('[0-9a-f]{64}',prediction_sha):
  raise ValueError('PRIVATE_PROTECTED_WORK_BINDINGS_INVALID')
 try:size=int(size)
 except (TypeError,ValueError):raise ValueError('PRIVATE_PROTECTED_WORK_BINDINGS_INVALID') from None
 if not 0<size<=200_000_000:raise ValueError('PRIVATE_PROTECTED_WORK_BINDINGS_INVALID')
 return key,archive_sha,size,prediction_sha

def protected_work_original(store,env,root,readback):
 key,archive_sha,size,prediction_sha=protected_work_binding(env)
 stage('PROTECTED_WORK_ORIGINAL_READBACK')
 data=store.get(key)
 if data is None or len(data)!=size or digest(data)!=archive_sha:raise ValueError('PRIVATE_PROTECTED_WORK_ARCHIVE_SHA_CONFLICT')
 folder=safe_extract(data,Path(root)/'protected-work')
 manifest=json.loads((folder/'SHA_Manifest.json').read_text())
 if manifest.get('race_id')!=RACE_ID or manifest.get('prediction_sha256')!=prediction_sha:
  raise ValueError('PRIVATE_PROTECTED_WORK_MANIFEST_IDENTITY_CONFLICT')
 inventory=manifest.get('files')
 if not isinstance(inventory,list)or not inventory:raise ValueError('PRIVATE_PROTECTED_WORK_MANIFEST_INVALID')
 names=set()
 for entry in inventory:
  relative=entry['path'];path=Path(relative)
  if relative in names or path.is_absolute()or'..'in path.parts:raise ValueError('PRIVATE_PROTECTED_WORK_MANIFEST_PATH_CONFLICT')
  names.add(relative);raw=(folder/path).read_bytes()
  if type(entry['bytes'])is not int or len(raw)!=entry['bytes']or digest(raw)!=entry['SHA256']:
   raise ValueError('PRIVATE_PROTECTED_WORK_MEMBER_SHA_CONFLICT')
 actual={str(p.relative_to(folder))for p in folder.rglob('*')if p.is_file()}
 if actual!=names|{'SHA_Manifest.json'}:raise ValueError('PRIVATE_PROTECTED_WORK_MANIFEST_INVENTORY_CONFLICT')
 original=folder/'original';source=folder/'source';frozen,body=readback(original)
 require_race(frozen['race'])
 if frozen['sha256']!=prediction_sha or frozen.get('classification')!='OHI_SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS':
  raise ValueError('PRIVATE_PROTECTED_WORK_PREDICTION_CONFLICT')
 observation=validate_record(json.loads((source/'observation.json').read_text()))
 if observation.get('race')!=frozen['race']or observation['sha256']!=frozen['source_sha256']:
  raise ValueError('PRIVATE_PROTECTED_WORK_SOURCE_CONFLICT')
 record=seal({'classification':frozen['classification'],'date':TARGET_DAY,'race_no':RACE_NO,'race_id':RACE_ID,
              'prediction_sha256':frozen['sha256'],'source_sha256':frozen['source_sha256'],
              'freeze_at':frozen['freeze_at'],'cutoff':frozen['race']['prediction_cutoff'],
              'mode':'PROTECTED_WORK_ORIGINAL_READBACK','origin_actor':'CHATGPT_WORK',
              'archive':{'key':key,'bytes':len(data),'sha256':digest(data),'actual_object_GET':True},
              'body_sha256':digest(body.encode()),'body_bytes':len(body.encode()),
              'current_source_verified':False,'new_KRS_calls':0,'new_prestart_credit':0,
              'manifest_payload_members_verified':len(names),'Production_changes':0,'OOS_credit':0})
 return original,source,record

def body_events(body,record,limit=1200):
 if not isinstance(limit,int) or limit<=0:raise ValueError('PRIVATE_DELIVERY_CHUNK_SIZE_INVALID')
 validate_record(record)
 if (record.get('date'),record.get('race_no'),record.get('race_id'))!=(TARGET_DAY,RACE_NO,RACE_ID):raise ValueError('PRIVATE_DELIVERY_RECORD_RACE_CONFLICT')
 delivery_id=digest((record['sha256']+':'+datetime.now(timezone.utc).isoformat()).encode())
 raw=body.encode('utf-8');parts=[raw[i:i+limit]for i in range(0,len(raw),limit)]
 if not raw or record.get('body_bytes')!=len(raw) or record.get('body_sha256')!=digest(raw):raise ValueError('PRIVATE_DELIVERY_RECORD_BODY_CONFLICT')
 yield {'schema':'KM_OHI_PRIVATE_DELIVERY_BEGIN_V1','date':TARGET_DAY,'race_no':RACE_NO,'race_id':RACE_ID,'delivery_id':delivery_id,'parts':len(parts),'bytes':len(raw),'body_sha256':digest(raw),'record':record}
 for i,part in enumerate(parts):yield {'schema':'KM_OHI_PRIVATE_BODY_CHUNK_V1','date':TARGET_DAY,'race_no':RACE_NO,'race_id':RACE_ID,'delivery_id':delivery_id,'part':i,'parts':len(parts),'body_sha256':digest(raw),'utf8_part_b64':base64.b64encode(part).decode('ascii')}
 yield {'schema':'KM_OHI_PRIVATE_DELIVERY_END_V1','date':TARGET_DAY,'race_no':RACE_NO,'race_id':RACE_ID,'delivery_id':delivery_id,'parts':len(parts),'body_sha256':digest(raw)}

def assemble_body(events):
 begins=[e for e in events if e.get('schema')=='KM_OHI_PRIVATE_DELIVERY_BEGIN_V1'];ends=[e for e in events if e.get('schema')=='KM_OHI_PRIVATE_DELIVERY_END_V1'];chunks=[e for e in events if e.get('schema')=='KM_OHI_PRIVATE_BODY_CHUNK_V1']
 if len(begins)!=1 or len(ends)!=1:raise ValueError('PRIVATE_DELIVERY_BOUNDARIES_MISSING_OR_DUPLICATE')
 begin,end=begins[0],ends[0];n=begin['parts'];ids=[e['part']for e in chunks]
 if type(n)is not int or n<1:raise ValueError('PRIVATE_DELIVERY_PART_COUNT_INVALID')
 if any(type(i)is not int for i in ids)or sorted(ids)!=list(range(n))or len(ids)!=len(set(ids)):raise ValueError('PRIVATE_DELIVERY_CHUNKS_INCOMPLETE_OR_DUPLICATE')
 if any(e.get('date')!=TARGET_DAY or e.get('race_no')!=RACE_NO or e.get('race_id')!=RACE_ID or e['body_sha256']!=begin['body_sha256']or e['parts']!=n or e['delivery_id']!=begin['delivery_id'] for e in [begin,*chunks,end]):raise ValueError('PRIVATE_DELIVERY_IDENTITY_CONFLICT')
 raw=b''.join(base64.b64decode(e['utf8_part_b64'],validate=True)for e in sorted(chunks,key=lambda e:e['part']))
 if len(raw)!=begin['bytes']or digest(raw)!=begin['body_sha256']:raise ValueError('PRIVATE_DELIVERY_BODY_SHA_MISMATCH')
 record=validate_record(begin['record'])
 if (record.get('date'),record.get('race_no'),record.get('race_id'))!=(TARGET_DAY,RACE_NO,RACE_ID):raise ValueError('PRIVATE_DELIVERY_RECORD_RACE_CONFLICT')
 if record.get('body_bytes')!=len(raw) or record.get('body_sha256')!=digest(raw):raise ValueError('PRIVATE_DELIVERY_RECORD_BODY_CONFLICT')
 return raw.decode('utf-8'),record

def zip_original(original,source,body,*,fresh_source=None):
 buf=io.BytesIO()
 with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED)as z:
  for label,folder in [('prediction',original),('source',source)]:
   for p in sorted(folder.rglob('*')):
    if p.is_file():z.write(p,label+'/'+str(p.relative_to(folder)))
  if fresh_source is not None and fresh_source!=source:
   for p in sorted(fresh_source.rglob('*')):
    if p.is_file():z.write(p,'current-source-check/'+str(p.relative_to(fresh_source)))
  z.writestr('delivery/complete-answer.txt',body.encode())
 return buf.getvalue()

def verify_fixed_inputs(env):
 code=Path(env['OHI_FIXED_CODE_ROOT']).resolve();assets=Path(env['OHI_FIXED_ASSET_ROOT']).resolve()
 contract=json.loads(Path(env['OHI_FIXED_CONTRACT_PATH']).read_text())
 if contract['prediction_code_ref']!='d61f5c563238be2c812ef4bf912bd5b872b84fed':raise ValueError('FIXED_CODE_REF_CONFLICT')
 if len(contract['prediction_dependency_sha256'])!=17:raise ValueError('FIXED_DEPENDENCY_COUNT_CONFLICT')
 for relative,expected in contract['prediction_dependency_sha256'].items():
  if digest((code/relative).read_bytes())!=expected:raise ValueError('FIXED_DEPENDENCY_SHA_CONFLICT:'+relative)
 model=assets/'existing_conditioned_owner_retrained.json';engine=assets/'KRS-Engine_v1.1.0_PORTABLE.py';params=code/'runtime/local_physical/parameter_map_v0.1-provisional.json'
 if digest(model.read_bytes())!=MODEL_BYTES or digest(engine.read_bytes())!=ENGINE or digest(params.read_bytes())!=PARAMS:raise ValueError('FIXED_PRIVATE_ASSET_SHA_CONFLICT')
 model_data=json.loads(model.read_text())
 if model_data.get('sha256')!=MODEL or seal({k:v for k,v in model_data.items()if k!='sha256'})['sha256']!=MODEL:raise ValueError('FIXED_MODEL_CANONICAL_SHA_CONFLICT')
 return code,model,engine,params

def prepare_bootstrap(store,env):
 stage('BOOTSTRAP_GET_AND_SHA')
 if env['OHI_BOOTSTRAP_KEY']!=BOOTSTRAP_KEY or env['OHI_BOOTSTRAP_SHA256']!=BOOTSTRAP_SHA:
  raise ValueError('PRIVATE_TRANSPORT_R2_BINDING_CONFLICT')
 seed=store.get(BOOTSTRAP_KEY)
 if seed is None or len(seed)!=BOOTSTRAP_BYTES or digest(seed)!=BOOTSTRAP_SHA:raise ValueError('PRIVATE_FIXED_BOOTSTRAP_SHA_CONFLICT')
 target=Path(env['OHI_FIXED_CODE_ROOT']).resolve().parent
 if (target,Path(env['OHI_FIXED_CODE_ROOT']).resolve(),Path(env['OHI_FIXED_ASSET_ROOT']).resolve(),Path(env['OHI_FIXED_CONTRACT_PATH']).resolve())!=(Path('/opt/km-inputs'),Path('/opt/km-inputs/code'),Path('/opt/km-inputs/assets'),Path('/opt/km-inputs/forward-contract.json')):
  raise ValueError('PRIVATE_FIXED_BOOTSTRAP_PATH_NOT_BOUND')
 stage('BOOTSTRAP_ALL_MEMBERS')
 safe_extract(seed,target);inventory=json.loads((target/'INPUT_SHA256_Manifest.json').read_text())
 if len(inventory['files'])!=25:raise ValueError('PRIVATE_TRANSPORT_R2_INVENTORY_CONFLICT')
 with zipfile.ZipFile(io.BytesIO(seed))as z:
  if set(z.namelist())!={x['path']for x in inventory['files']}|{'INPUT_SHA256_Manifest.json'}:
   raise ValueError('PRIVATE_TRANSPORT_R2_INVENTORY_CONFLICT')
 for entry in inventory['files']:
  p=target/entry['path']
  if p.stat().st_size!=entry['bytes']or digest(p.read_bytes())!=entry['SHA256']:raise ValueError('PRIVATE_FIXED_BOOTSTRAP_MEMBER_SHA_CONFLICT')
 stage('FIXED_ASSET_SHA')
 paths=verify_fixed_inputs(env)
 return paths,{'actual_object_GET':True,'bytes':len(seed),'sha256':digest(seed),'payload_members_verified':25,
               'fixed_dependencies_verified':17,'model_canonical_sha256':MODEL,'engine_sha256':ENGINE,'parameter_map_sha256':PARAMS}

def delivery_body(frozen,body):
 # Presentation-only correction of a legacy unconditional missing-weight line.
 # prediction/answer.md, its manifest, its Freeze and every number stay intact.
 body=body.replace('馬体重・当日馬場は未観測で、','当日情報は原本SOURCE時点の観測であり、')
 rows=['','保存済みSOURCEの馬体重（元Freeze時点。現在の鮮度を意味しません）：',
       '|馬番・馬名|馬体重kg|増減kg|','|---|---:|---:|']
 for f in frozen['all_runners']:
  weight=f.get('current_body_weight');change=f.get('current_body_weight_change')
  rows.append(f"|{f['runner_id']} {f['name']}|{weight if weight is not None else 'UNKNOWN'}|{change if change is not None else 'UNKNOWN'}|")
 return body+'\n'+'\n'.join(rows)+'\n'

def main(*,execute=False):
 now=datetime.now(timezone.utc);stage('ACTOR_BINDING');require_actor(os.environ,now)
 resources=None
 if execute:
  stage('SINGLE_RUN_TIME_WINDOW');require_execution_window(now)
  stage('RESOURCE_LIMITS');resources=require_resource_limits()
  # This fixed R1 already has a completed Work original. Missing references
  # cannot turn it into a new race or consume the single approved run claim.
  protected_work_binding(os.environ)
 stage('PRIVATE_STORE_PREFLIGHT');store=PrivateStore(os.environ);prefix=f'OHI/{TARGET_DAY}/R{RACE_NO:02d}/'
 claim_receipt=None
 if execute:
  # The immutable claim also proves private PUT/GET, before any other run write.
  claim_receipt=claim_single_run(store,prefix,now,os.environ);probe_receipt=claim_receipt
 else:
  probe=(json.dumps({'purpose':'PRIVATE_STORE_PREFLIGHT_NOT_PREDICTION','date':TARGET_DAY,'race_no':RACE_NO,'created_at':now.isoformat()},sort_keys=True)+'\n').encode()
  probe_receipt=store.put_new_and_read(prefix+'store-probes/'+digest(probe)+'.json',probe)
 (code,model,engine,params),bootstrap=prepare_bootstrap(store,os.environ)
 if not execute:
  print(json.dumps({'schema':'KM_OHI_PRIVATE_BOOTSTRAP_READY_V1','date':TARGET_DAY,'race_no':RACE_NO,'race_id':RACE_ID,
                    'bootstrap':bootstrap,'private_store_probe':probe_receipt,'prediction_calculated':False,'new_KRS_calls':0,
                    'relay_completed':False,'Production_changes':0,'OOS_credit':0}),flush=True)
  return 0
 sys.path[:0]=[str(code),str(code/'runtime')]
 from runtime.ohi_single_race_research import capture,run,readback,revision_decision,write,render,check_source_time
 os.chdir(code)
 root=Path(tempfile.mkdtemp(prefix='km-ohi-private-pilot-')).resolve();root.chmod(0o700)
 prior,prior_source,old_record=protected_work_original(store,os.environ,root,readback)
 stage('EXISTING_PRIVATE_ORIGINAL_READBACK');old_record_bytes=store.latest_record(prefix)
 if old_record_bytes:
  old_record=validate_record(json.loads(old_record_bytes));b=store.get(old_record['archive']['key'])
  if (old_record.get('date'),old_record.get('race_no'))!=(TARGET_DAY,RACE_NO)or old_record.get('race_id')not in (None,RACE_ID):raise ValueError('PRIVATE_EXISTING_ORIGINAL_OTHER_RACE')
  if b is None or len(b)!=old_record['archive']['bytes']or digest(b)!=old_record['archive']['sha256']:raise ValueError('PRIVATE_EXISTING_ARCHIVE_SHA_CONFLICT')
  safe_extract(b,root/'prior');prior=root/'prior/prediction';old,_=readback(prior)
  prior_source=root/'prior/source'
  require_race(old['race'])
  if old['race']['race_date']!=TARGET_DAY or old['race']['race_no']!=RACE_NO or old['sha256']!=old_record['prediction_sha256']:raise ValueError('PRIVATE_EXISTING_ORIGINAL_OTHER_RACE')
 source=root/'current-source'
 stage('OFFICIAL_SOURCE')
 try:
  obs=capture(TARGET_DAY,RACE_NO,str(source),source_contract='v2');write(source/'observation.json',obs)
  require_race(obs['race'])
 except Exception as exc:
  if prior:
   print(json.dumps(hold_event(exc)),flush=True)
   frozen,body=readback(prior)
   body='過去Freezeの完成原本。今回の最新SOURCE再照合は未成立。最新性・新規発走前成功を保証しません。\n\n'+body
   fallback=seal({**{k:v for k,v in old_record.items()if k!='sha256'},'race_id':RACE_ID,'mode':'PAST_FREEZE_READBACK_SOURCE_RECHECK_FAILED','body_sha256':digest(body.encode()),'body_bytes':len(body.encode()),'current_source_verified':False,'new_KRS_calls':0,'new_prestart_credit':0})
   for event in body_events(body,fallback):print(json.dumps(event,ensure_ascii=False,separators=(',',':')),flush=True)
   return 3
  raise
 decision=None
 stage('MATERIAL_REVISION_CHECK')
 if prior:
  decision=revision_decision(prior,obs,source_dir=source);write(source/'revision-decision.json',decision)
 if decision and decision['decision']=='REUSE_FROZEN_ORIGINAL':
  frozen,body=readback(prior);original=prior;calculation_source=prior_source;mode='REUSE_WITH_SEPARATE_FRESH_SOURCE_CHECK';new_KRS=0
 else:
  stage('FIXED_INDICES_OWNERS_KRS_MEC_CAPITAL')
  original=root/'prediction';frozen=run(obs,str(original),str(model),str(engine),str(params),source_dir=str(source));frozen,body=readback(original);calculation_source=source;mode='NEW_PRESTART_IMMUTABLE_ORIGINAL';new_KRS=2
 stage('COMPLETED_ORIGINAL_READBACK');require_race(frozen['race'])
 check_source_time(obs,'BEFORE_PRIVATE_PERSISTENCE')
 if frozen['classification']!='OHI_SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS':raise ValueError('PRIVATE_CLASSIFICATION_CONFLICT')
 if set(frozen['krs'])!={'BASELINE','OHI_FIXED_CANDIDATE'} or any(not x['receipt']['actual_engine_executed']or x['receipt']['runs']!=5000 or x['receipt']['seed']!=1 for x in frozen['krs'].values()):raise ValueError('FIXED_KRS_RECEIPT_CONFLICT')
 original_body_sha=digest(body.encode());body=delivery_body(frozen,body)
 # Keep all calculated rows/tickets. Fresh checks do not become a new old Freeze.
 if decision:body='最新SOURCE照合（旧Freezeを変更しない）：'+json.dumps(decision,ensure_ascii=False)+'\n\n'+body
 stage('PRIVATE_ORIGINAL_PUT_GET')
 archive=zip_original(original,calculation_source,body,fresh_source=source);archive_key=prefix+'revisions/'+frozen['sha256']+'/'+digest(archive)+'.zip';arch=store.put_new_and_read(archive_key,archive)
 record=seal({'classification':frozen['classification'],'date':TARGET_DAY,'race_no':RACE_NO,'race_id':RACE_ID,'prediction_sha256':frozen['sha256'],'source_sha256':frozen['source_sha256'],'freeze_at':frozen['freeze_at'],'cutoff':frozen['race']['prediction_cutoff'],'fresh_observation_sha256':obs['sha256'],'fresh_source_receipt_times':[r['fetched_at']for r in obs['receipts']],'current_source_verified':True,'mode':mode,'new_KRS_calls':new_KRS,'archive':arch,'body_sha256':digest(body.encode()),'body_bytes':len(body.encode()),'original_rendered_body_sha256':original_body_sha,'delivery_presentation_only':True,'actor':{'project_id':PROJECT,'environment_id':ENVIRONMENT,'service_id':SERVICE,'deployment_id':os.environ.get('RAILWAY_DEPLOYMENT_ID')},'resource_limits':resources,'bootstrap':bootstrap,'single_run_claim':claim_receipt,'prior_original_origin':old_record.get('origin_actor',old_record.get('prior_original_origin','RAILWAY_RESEARCH_WORKER'))if old_record else None,'protected_Work_original_sha256':os.environ.get('OHI_PROTECTED_WORK_ORIGINAL_SHA256'),'relation_to_Work_original':'SAME_RACE_SEPARATE_ACTOR_NOT_AN_OVERWRITE','Production_changes':0,'OOS_credit':0})
 # Every record is immutable; latest is selected from the timestamped record journal.
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 stage('PRIVATE_RECORD_PUT_GET');store.put_new_and_read(prefix+'records/'+stamp+'-'+record['sha256']+'.json',(json.dumps(record,ensure_ascii=False,sort_keys=True)+'\n').encode())
 stage('COMPLETE_BODY_RELAY')
 check_source_time(obs,'PRIVATE_DELIVERY_EMIT');events=list(body_events(body,record));reconstructed,rec=assemble_body(events)
 if reconstructed!=body:raise ValueError('PRIVATE_LOCAL_RELAY_BODY_CONFLICT')
 for event in events:print(json.dumps(event,ensure_ascii=False,separators=(',',':')),flush=True)
 # A private outbox/log emit is not a claim of chat screen delivery or user ACK.
 return 0

def cli(argv=None):
 parser=argparse.ArgumentParser(description='Private R2 bootstrap check by default; explicitly arm the single prestart run.')
 mode=parser.add_mutually_exclusive_group()
 mode.add_argument('--bootstrap-only',action='store_true',help='Verify private PUT/GET and all R2 inputs; no SOURCE or calculation.')
 mode.add_argument('--execute',action='store_true',help='Run only 2026-10-28 14:00 <= JST < 14:25 with verified resource limits.')
 mode.add_argument('--execute-child',action='store_true',help=argparse.SUPPRESS)
 args=parser.parse_args(argv)
 if args.execute:
  # The process group belongs exclusively to this pilot, including Engine children.
  # The parent has a real wall-clock deadline; worker threads cannot delay shutdown.
  import signal,subprocess
  now=datetime.now(timezone.utc);stage('SINGLE_RUN_TIME_WINDOW');require_execution_window(now)
  timeout=(datetime(2026,10,28,14,25,tzinfo=JST)-now).total_seconds()
  process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--execute-child'],start_new_session=True)
  try:return process.wait(timeout=timeout)
  except subprocess.TimeoutExpired:
   try:os.killpg(process.pid,signal.SIGTERM)
   except ProcessLookupError:pass
   try:process.wait(timeout=5)
   except subprocess.TimeoutExpired:
    try:os.killpg(process.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    process.wait()
   stage('PILOT_WALL_CLOCK_DEADLINE');raise ValueError('PRIVATE_PILOT_CUTOFF_PASSED') from None
 return main(execute=args.execute_child)

if __name__=='__main__':
 try:raise SystemExit(cli())
 except Exception as e:
  # Never dump Raw, keys, model contents, or HTTP response bodies to logs.
  print(json.dumps(hold_event(e)),flush=True)
  raise SystemExit(2)

