"""Thin private OHI R1 pilot: inherited SOURCE/calculation only, private S3 and log relay.

This file is a deployment candidate with local boundary tests, not an active worker.
No Production endpoint is invoked. It refuses the wrong actor/date, a public
GitHub log destination, missing private bindings, or a late/stale SOURCE.
"""
from __future__ import annotations
import base64,hashlib,io,json,os,shutil,sys,tempfile,zipfile
from datetime import datetime,timezone,timedelta
from pathlib import Path

TARGET_DAY='2026-10-28';RACE_NO=1
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
  try:return self.client.get_object(Bucket=self.bucket,Key=key)['Body'].read()
  except ClientError as e:
   if e.response.get('Error',{}).get('Code')in ['NoSuchKey','404']:return None
   raise
 def latest_record(self,prefix):
  rows=self.client.list_objects_v2(Bucket=self.bucket,Prefix=prefix+'records/',MaxKeys=1000)
  if rows.get('IsTruncated'):raise ValueError('PRIVATE_HISTORY_LIST_LIMIT')
  keys=sorted(x['Key']for x in rows.get('Contents',[])if x['Key'].endswith('.json'))
  return self.get(keys[-1])if keys else None
 def put_new_and_read(self,key,data):
  # A conditional create prevents overwriting any old frozen object.
  self.client.put_object(Bucket=self.bucket,Key=key,Body=data,IfNoneMatch='*',ContentType='application/octet-stream')
  actual=self.get(key)
  if actual!=data:raise ValueError('PRIVATE_STORE_ACTUAL_BYTE_READBACK_MISMATCH')
  return {'key':key,'bytes':len(data),'sha256':digest(actual),'actual_object_GET':True}

def body_events(body,record,limit=1200):
 delivery_id=digest((record['sha256']+':'+datetime.now(timezone.utc).isoformat()).encode())
 raw=body.encode('utf-8');parts=[raw[i:i+limit]for i in range(0,len(raw),limit)]
 yield {'schema':'KM_OHI_PRIVATE_DELIVERY_BEGIN_V1','date':TARGET_DAY,'race_no':RACE_NO,'delivery_id':delivery_id,'parts':len(parts),'bytes':len(raw),'body_sha256':digest(raw),'record':record}
 for i,part in enumerate(parts):yield {'schema':'KM_OHI_PRIVATE_BODY_CHUNK_V1','date':TARGET_DAY,'race_no':RACE_NO,'delivery_id':delivery_id,'part':i,'parts':len(parts),'body_sha256':digest(raw),'utf8_part_b64':base64.b64encode(part).decode('ascii')}
 yield {'schema':'KM_OHI_PRIVATE_DELIVERY_END_V1','date':TARGET_DAY,'race_no':RACE_NO,'delivery_id':delivery_id,'parts':len(parts),'body_sha256':digest(raw)}

def assemble_body(events):
 begins=[e for e in events if e.get('schema')=='KM_OHI_PRIVATE_DELIVERY_BEGIN_V1'];ends=[e for e in events if e.get('schema')=='KM_OHI_PRIVATE_DELIVERY_END_V1'];chunks=[e for e in events if e.get('schema')=='KM_OHI_PRIVATE_BODY_CHUNK_V1']
 if len(begins)!=1 or len(ends)!=1:raise ValueError('PRIVATE_DELIVERY_BOUNDARIES_MISSING_OR_DUPLICATE')
 begin,end=begins[0],ends[0];n=begin['parts'];ids=[e['part']for e in chunks]
 if sorted(ids)!=list(range(n))or len(ids)!=len(set(ids)):raise ValueError('PRIVATE_DELIVERY_CHUNKS_INCOMPLETE_OR_DUPLICATE')
 if any(e['date']!=TARGET_DAY or e['race_no']!=RACE_NO or e['body_sha256']!=begin['body_sha256']or e['parts']!=n or e['delivery_id']!=begin['delivery_id'] for e in [*chunks,end]):raise ValueError('PRIVATE_DELIVERY_IDENTITY_CONFLICT')
 raw=b''.join(base64.b64decode(e['utf8_part_b64'],validate=True)for e in sorted(chunks,key=lambda e:e['part']))
 if len(raw)!=begin['bytes']or digest(raw)!=begin['body_sha256']:raise ValueError('PRIVATE_DELIVERY_BODY_SHA_MISMATCH')
 return raw.decode('utf-8'),validate_record(begin['record'])

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
 for relative,expected in contract['prediction_dependency_sha256'].items():
  if digest((code/relative).read_bytes())!=expected:raise ValueError('FIXED_DEPENDENCY_SHA_CONFLICT:'+relative)
 model=assets/'existing_conditioned_owner_retrained.json';engine=assets/'KRS-Engine_v1.1.0_PORTABLE.py';params=code/'runtime/local_physical/parameter_map_v0.1-provisional.json'
 if digest(model.read_bytes())!=MODEL_BYTES or digest(engine.read_bytes())!=ENGINE or digest(params.read_bytes())!=PARAMS:raise ValueError('FIXED_PRIVATE_ASSET_SHA_CONFLICT')
 model_data=json.loads(model.read_text())
 if model_data.get('sha256')!=MODEL or seal({k:v for k,v in model_data.items()if k!='sha256'})['sha256']!=MODEL:raise ValueError('FIXED_MODEL_CANONICAL_SHA_CONFLICT')
 return code,model,engine,params

def main():
 now=datetime.now(timezone.utc);require_actor(os.environ,now);store=PrivateStore(os.environ)
 probe=(json.dumps({'purpose':'PRIVATE_STORE_PREFLIGHT_NOT_PREDICTION','date':TARGET_DAY,'race_no':RACE_NO,'created_at':now.isoformat()},sort_keys=True)+'\n').encode()
 store.put_new_and_read('OHI/'+TARGET_DAY+'/R01/store-probes/'+digest(probe)+'.json',probe)
 seed=store.get(os.environ['OHI_BOOTSTRAP_KEY'])
 if seed is None or digest(seed)!=os.environ['OHI_BOOTSTRAP_SHA256']:raise ValueError('PRIVATE_FIXED_BOOTSTRAP_SHA_CONFLICT')
 target=Path(os.environ['OHI_FIXED_CODE_ROOT']).resolve().parent
 if target!=Path('/opt/km-inputs'):raise ValueError('PRIVATE_FIXED_BOOTSTRAP_PATH_NOT_BOUND')
 safe_extract(seed,target);inventory=json.loads((target/'INPUT_SHA256_Manifest.json').read_text())
 for entry in inventory['files']:
  p=target/entry['path']
  if p.stat().st_size!=entry['bytes']or digest(p.read_bytes())!=entry['SHA256']:raise ValueError('PRIVATE_FIXED_BOOTSTRAP_MEMBER_SHA_CONFLICT')
 code,model,engine,params=verify_fixed_inputs(os.environ)
 sys.path[:0]=[str(code),str(code/'runtime')]
 from runtime.ohi_single_race_research import capture,run,readback,revision_decision,write,render,check_source_time
 os.chdir(code)
 root=Path(tempfile.mkdtemp(prefix='km-ohi-private-pilot-')).resolve();root.chmod(0o700);prefix='OHI/2026-10-28/R01/';old_record_bytes=store.latest_record(prefix);prior=None
 if old_record_bytes:
  old_record=validate_record(json.loads(old_record_bytes));b=store.get(old_record['archive']['key'])
  if b is None or digest(b)!=old_record['archive']['sha256']:raise ValueError('PRIVATE_EXISTING_ARCHIVE_SHA_CONFLICT')
  safe_extract(b,root/'prior');prior=root/'prior/prediction';old,_=readback(prior)
  if old['race']['race_date']!=TARGET_DAY or old['race']['race_no']!=RACE_NO or old['sha256']!=old_record['prediction_sha256']:raise ValueError('PRIVATE_EXISTING_ORIGINAL_OTHER_RACE')
 source=root/'current-source'
 try:
  obs=capture(TARGET_DAY,RACE_NO,str(source),source_contract='v2');write(source/'observation.json',obs)
 except Exception:
  if prior:
   frozen,body=readback(prior)
   body='過去Freezeの完成原本。今回の最新SOURCE再照合は未成立。最新性・新規発走前成功を保証しません。\n\n'+body
   fallback=seal({**{k:v for k,v in old_record.items()if k!='sha256'},'mode':'PAST_FREEZE_READBACK_SOURCE_RECHECK_FAILED','body_sha256':digest(body.encode()),'body_bytes':len(body.encode()),'current_source_verified':False,'new_prestart_credit':0})
   for event in body_events(body,fallback):print(json.dumps(event,ensure_ascii=False,separators=(',',':')),flush=True)
   return 3
  raise
 decision=None
 if prior:
  decision=revision_decision(prior,obs,source_dir=source);write(source/'revision-decision.json',decision)
 if decision and decision['decision']=='REUSE_FROZEN_ORIGINAL':
  frozen,body=readback(prior);original=prior;calculation_source=root/'prior/source';mode='REUSE_WITH_SEPARATE_FRESH_SOURCE_CHECK';new_KRS=0
 else:
  original=root/'prediction';frozen=run(obs,str(original),str(model),str(engine),str(params),source_dir=str(source));frozen,body=readback(original);calculation_source=source;mode='NEW_PRESTART_IMMUTABLE_ORIGINAL';new_KRS=2
 check_source_time(obs,'BEFORE_PRIVATE_PERSISTENCE')
 if frozen['classification']!='OHI_SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS':raise ValueError('PRIVATE_CLASSIFICATION_CONFLICT')
 if any(not x['receipt']['actual_engine_executed']or x['receipt']['runs']!=5000 or x['receipt']['seed']!=1 for x in frozen['krs'].values()):raise ValueError('FIXED_KRS_RECEIPT_CONFLICT')
 # Keep the completed body intact. Fresh checks do not become a new old Freeze.
 if decision:body='最新SOURCE照合（旧Freezeを変更しない）：'+json.dumps(decision,ensure_ascii=False)+'\n\n'+body
 archive=zip_original(original,calculation_source,body,fresh_source=source);archive_key=prefix+'revisions/'+frozen['sha256']+'/'+digest(archive)+'.zip';arch=store.put_new_and_read(archive_key,archive)
 record=seal({'classification':frozen['classification'],'date':TARGET_DAY,'race_no':RACE_NO,'prediction_sha256':frozen['sha256'],'source_sha256':frozen['source_sha256'],'freeze_at':frozen['freeze_at'],'cutoff':frozen['race']['prediction_cutoff'],'fresh_observation_sha256':obs['sha256'],'fresh_source_receipt_times':[r['fetched_at']for r in obs['receipts']],'current_source_verified':True,'mode':mode,'new_KRS_calls':new_KRS,'archive':arch,'body_sha256':digest(body.encode()),'body_bytes':len(body.encode()),'Production_changes':0,'OOS_credit':0})
 # Every record is immutable; latest is selected from the timestamped record journal.
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 store.put_new_and_read(prefix+'records/'+stamp+'-'+record['sha256']+'.json',(json.dumps(record,ensure_ascii=False,sort_keys=True)+'\n').encode())
 check_source_time(obs,'PRIVATE_DELIVERY_EMIT');events=list(body_events(body,record));reconstructed,rec=assemble_body(events)
 if reconstructed!=body:raise ValueError('PRIVATE_LOCAL_RELAY_BODY_CONFLICT')
 for event in events:print(json.dumps(event,ensure_ascii=False,separators=(',',':')),flush=True)
 # A private outbox/log emit is not a claim of chat screen delivery or user ACK.
 return 0

if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as e:
  # Never dump Raw, keys, model contents, or HTTP response bodies to logs.
  print(json.dumps({'schema':'KM_OHI_PRIVATE_PILOT_HOLD_V1','date':TARGET_DAY,'race_no':RACE_NO,'error_type':type(e).__name__,'error_code':str(e)if isinstance(e,ValueError)and str(e).startswith(('PRIVATE_','FIXED_','OHI_'))else'PILOT_EXTERNAL_OR_SOURCE_HOLD','new_Production_or_OOS':0}),flush=True)
  raise SystemExit(2)
