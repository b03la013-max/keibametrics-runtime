"""Result-only official observations; never a pre-start SOURCE replacement."""
import json,sys,urllib.request,datetime as dt,base64,hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
from local_physical.nar_source_manifest import _result_source,LOCAL_BABA_CODES
from formal_execution_orchestrator import parse_official_result_snapshot
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
BASE=ROOT/'evidence/kaw_v25_20261013';BASE.mkdir(parents=True,exist_ok=True)
ENDPOINT='https://witnessstrictimage-production.up.railway.app'
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def call(path,payload=None):
 req=urllib.request.Request(ENDPOINT+path,data=None if payload is None else json.dumps(payload,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=180) as r:return json.load(r)
health=call('/health');(BASE/'runtime_health.json').write_text(json.dumps(health,indent=2)+'\n')
key=Ed25519PublicKey.from_public_bytes(base64.b64decode(health['receipt_public_key_b64']))
def acquire(target):
 date,r=target;rid=f'KM-LOCAL-KAW-{date.replace("-","")}-R{r:02}-V25-RESULT-AUDIT';p=BASE/f'{date}-R{r:02}-official.json'
 try:
  if p.exists():e=json.loads(p.read_text())
  else:
   spec=_result_source('KAW',LOCAL_BABA_CODES['KAW'],date.replace('-','/'),r);spec['required']=True
   e=call('/source/acquire',{'family_id':'LOCAL','race_id':rid,'venue_id':'KAW','race_date':date,'race_no':r,'prediction_cutoff':(dt.datetime.now(dt.timezone.utc)+dt.timedelta(minutes=20)).isoformat(),'sources':[spec]})
   p.write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n')
  key.verify(base64.b64decode(e['signature']),json.dumps(e['receipt'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
  assert e['receipt_sha256']==digest(e['receipt']) and e['receipt']['artifact_sha256']==digest(e['artifact'])
  assert e['receipt']['race_id']==rid and e['receipt']['status']=='SOURCE_FROZEN'
  c=e['artifact']['source_race_context'];assert c['venue_id']=='KAW' and str(c['race_date']).replace('/','-')==date and int(c['race_no'])==r
  raw=e['artifact']['sources'][0];order,payouts=parse_official_result_snapshot(raw,c,[str(x) for x in range(1,19)],top3_only=True)
  return {'date':date,'race_no':r,'status':'VERIFIED','path':str(p.relative_to(ROOT)),'source_receipt_sha256':e['receipt_sha256'],'raw_sha256':raw['raw_sha256'],'official_result':{'finish_order':order,'payouts':payouts,'source':raw['final_url']},'observed_at':raw['fetched_at'],'scope':'POST_RESULT_OBSERVATION_ONLY'}
 except Exception as exc:return {'date':date,'race_no':r,'status':'HOLD','reason':type(exc).__name__+':'+str(exc)}
with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(acquire,[(d,r) for d in ['2026-10-12','2026-10-13'] for r in range(1,13)]))
(BASE/'official_observations.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print(json.dumps([{k:v for k,v in r.items() if k in ['date','race_no','status','reason']} for r in rows]))
