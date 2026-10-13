"""Systematic first-race pre-start PAPER pilot, never Production/purchase.

SOURCE and all failures are saved. No race is replaced with a successful one.
"""
import argparse,base64,datetime as dt,gzip,hashlib,json,re,subprocess,sys,unicodedata,urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'runtime'))
from local_physical.source_acquisition import _decode,_html_text
from local_physical.nar_source_manifest import LOCAL_BABA_CODES,VENUE_NAMES
from local_aki_columns import sha

def build_intent(source,plan_path):
    a=source['artifact'];context=a['source_race_context']; ev=a['normalized_evidence']
    snapshots=[s for s in a['sources'] if s['source_class'].startswith('OFFICIAL_RACE_CARD')]
    if len(snapshots)!=1: raise ValueError('OFFICIAL_RACE_CARD_SCOPE_REQUIRED')
    s=snapshots[0];raw=gzip.decompress(base64.b64decode(s['raw_gzip_b64']))
    if hashlib.sha256(raw).hexdigest()!=s['raw_sha256']:raise ValueError('RACE_CARD_RAW_HASH_MISMATCH')
    text=unicodedata.normalize('NFKC',_html_text(_decode(raw,s.get('content_type') or '')))
    # Distances in historical runner rows must not be mistaken for race header.
    header=text[:text.find('着別') if '着別' in text else 5000]
    course=re.search(r'(ダート|芝)\s*(\d{3,4})\s*m[^\n]*?[（(](.*?)[)）]',header,re.S)
    if not course:raise ValueError('OFFICIAL_CURRENT_RACE_DISTANCE_REQUIRED')
    post=(ev.get('start_time') or {}).get('value')
    if not post:raise ValueError('OFFICIAL_CURRENT_POST_REQUIRED')
    date=str(context['race_date']).replace('/','-');no=int(context['race_no']);v=context['venue_id']
    jst=dt.timezone(dt.timedelta(hours=9));scheduled=dt.datetime.fromisoformat(date+'T'+post+':00').replace(tzinfo=jst)
    if scheduled<=dt.datetime.now(jst):raise ValueError('PRESTART_PILOT_ALREADY_POST')
    name=re.search(r'第\s*'+str(no)+r'\s*競走\s*(.*?)\s*(?:ダート|芝)',header,re.S)
    title=' '.join(name.group(1).split()) if name else ''
    rows=a['active_runner_universe']['runners']
    required=json.loads((ROOT/'mapping/local_full_numerical_mapping_v1.0_production_20261008.json').read_text())['required_indices']
    return {'family_id':'LOCAL','race_id':source['receipt']['race_id'],'venue_id':v,'race_date':date,'race_no':no,
        'aki_temporal_mode':'FORWARD_PAPER','prospective_evaluation_plan':str(plan_path.relative_to(ROOT)),
        'scheduled_post_at':scheduled.isoformat(),'prediction_cutoff':a['prediction_cutoff'],
        'temporal_mode':'PAPER_PRE_RACE','required_indices':required,'run_count':20000,'seed':1,
        'race':{'venue':VENUE_NAMES[v],'venue_id':v,'race_no':no,'race_date':date,'name':title,'class':title,
                'distance':int(course.group(2)),'distance_m':int(course.group(2)),
                'surface':'DIRT' if course.group(1)=='ダート' else 'TURF',
                'direction':'LEFT' if '左' in course.group(3) else 'RIGHT' if '右' in course.group(3) else 'UNKNOWN',
                'runner_count':len(rows)},'runners':rows,'purchase_authority':False,'production_authority':False,
        'snapshot_phase':'EARLY_PRESTART / CURRENT_STATE_INFORMATION_MAY_BE_MISSING / PAPER_ONLY',
        'observed_field_status':a.get('runner_status_manifest')}

def run_one(v,plan_path,out_root):
    plan=json.loads(plan_path.read_text());date=plan['pilot_date'];race_id=f'KM-LOCAL-AKI-FORWARD-{v}-{date.replace("-","")}-R01'
    out=out_root/v;out.mkdir(parents=True,exist_ok=True)
    endpoint=json.loads((ROOT/'profiles/current_execution_gateway.json').read_text())['families']['LOCAL']['external_endpoint']
    def save(name,value):
        p=out/(name+'.json');encoded=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
        if p.exists() and p.read_text()!=encoded:raise ValueError('IMMUTABLE_FORWARD_PILOT_CONFLICT:'+name)
        p.write_text(encoded);return value
    def call(path,payload,name,timeout=180):
        p=out/(name+'.json')
        if p.exists():return json.loads(p.read_text())
        req=urllib.request.Request(endpoint+path,data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=timeout) as r:obj=json.load(r)
        return save(name,obj)
    try:
        q=dict(family_id='LOCAL',race_id=race_id,venue_id=v,race_date=date,race_no=1,
               prediction_cutoff=plan['pilot_source_cutoff'],include_odds=True,require_active_runner_universe=True,
               include_same_day_results=True)
        manifest=call('/source/manifest/local',q,'manifest')
        source=call('/source/acquire',manifest,'source_receipt')
        att=json.loads((ROOT/'evidence/local_aki_columns_20261012/destination_verification.json').read_text())
        key=Ed25519PublicKey.from_public_bytes(base64.b64decode(att['health']['receipt_public_key_b64']))
        raw=json.dumps(source['receipt'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        key.verify(base64.b64decode(source['signature']),raw)
        if sha(source['artifact'])!=source['receipt']['artifact_sha256'] or hashlib.sha256(raw).hexdigest()!=source['receipt_sha256']:
            raise ValueError('FORWARD_SIGNED_SOURCE_DIGEST_INVALID')
        verify=call('/source/verify',source,'source_verification',60)
        if source['receipt']['status']!='SOURCE_FROZEN' or verify.get('valid') is not True:
            return save('terminal',{'status':'HOLD_SOURCE_NOT_FROZEN','source_errors':source['artifact'].get('errors'),
                        'venue_id':v,'race_id':race_id,'unknown_future_oos_count':0,'purchase_authority':False})
        intent=save('intent',build_intent(source,plan_path))
        canonical=ROOT/'runtime/executions'/race_id/'SOURCE/runs/20261013-forward-pilot'
        canonical.mkdir(parents=True,exist_ok=True)
        p=canonical/'source_receipt_envelope.json'
        encoded=json.dumps(source,ensure_ascii=False,indent=2)+'\n'
        if p.exists() and p.read_text()!=encoded:raise ValueError('CANONICAL_FORWARD_SOURCE_CONFLICT')
        p.write_text(encoded)
        command=[sys.executable,str(ROOT/'runtime/formal_execution_orchestrator.py'),'--intent',str(out/'intent.json'),
            '--aki-paper-forward','--frozen-source',str(p),'--run-id',race_id,'--output',str(out/'single_entry_report.json')]
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=720)
        report=json.loads((out/'single_entry_report.json').read_text())
        return save('terminal',{'status':report['status'],'exit_code':result.returncode,'venue_id':v,'race_id':race_id,
            'report_path':str((out/'single_entry_report.json').relative_to(ROOT)),
            'source_path':str(p.relative_to(ROOT)),'intent_path':str((out/'intent.json').relative_to(ROOT)),
            'scheduled_post_at':intent['scheduled_post_at'],'prediction_cutoff':intent['prediction_cutoff'],
            'unknown_future_oos_count':0,'purchase_authority':False})
    except Exception as e:
        return save('terminal',{'status':'HOLD_FORWARD_PILOT','venue_id':v,'race_id':race_id,
            'error_type':type(e).__name__,'reason':str(e),'unknown_future_oos_count':0,'purchase_authority':False})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--plan',required=True);a=p.parse_args()
    plan_path=Path(a.plan).resolve();plan=json.loads(plan_path.read_text())
    root=ROOT/'research/local_aki_forward_20261013';root.mkdir(exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(lambda v:run_one(v,plan_path,root),plan['pilot_venues']))
    report={'profile':plan['profile'],'status':'PREREGISTERED_FIRST_RACE_PILOT / ALL_HOLDS_RETAINED',
            'results':results,'unknown_future_oos_count':0,'purchase_authority':False}
    (root/'pilot_status.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))
