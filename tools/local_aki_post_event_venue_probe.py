"""Seven additional real LOCAL venue inputs: POST-EVENT transport diagnostics.

These freshly retrieved historical pages/auxiliary profiles are NOT original
pre-start snapshots. They must never enter PFS validation or future OOS.
"""
import base64,datetime as dt,gzip,hashlib,json,re,subprocess,sys,unicodedata,urllib.request
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
from local_physical.nar_source_manifest import VENUE_NAMES
from local_physical.source_acquisition import _decode,_html_text
from local_aki_columns import sha
TARGETS={'URW':'2026-09-23','SON':'2026-10-09','HIM':'2026-02-26','KSM':'2026-10-09','KCH':'2026-10-11','SAG':'2026-10-12','MIZ':'2026-09-27'}
CUTOFF=(dt.datetime.now(dt.timezone.utc)+dt.timedelta(minutes=40)).isoformat()
ENGINE_ADMISSION=threading.Lock()


def run(v,date):
    root=ROOT/'research/local_aki_post_event_venue_probe_20261013'/v;root.mkdir(parents=True,exist_ok=True)
    att=json.loads((ROOT/'evidence/local_aki_columns_20261012/destination_verification.json').read_text());endpoint=att['endpoint']
    race_id=f'KM-LOCAL-AKI-POST-EVENT-{v}-{date.replace("-","")}-R01'
    def save(name,obj):
        p=root/(name+'.json');text=json.dumps(obj,ensure_ascii=False,indent=2)+'\n'
        if p.exists() and p.read_text()!=text:raise ValueError('POST_EVENT_IMMUTABLE_CONFLICT:'+name)
        p.write_text(text);return obj
    def call(path,payload,name):
        p=root/(name+'.json')
        if p.exists():return json.loads(p.read_text())
        req=urllib.request.Request(endpoint+path,data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=180) as response:obj=json.load(response)
        return save(name,obj)
    try:
        manifest=call('/source/manifest/local',dict(family_id='LOCAL',race_id=race_id,venue_id=v,race_date=date,race_no=1,
             prediction_cutoff=CUTOFF,include_odds=True,require_active_runner_universe=True,include_same_day_results=True),'manifest')
        source=call('/source/acquire',manifest,'source_receipt');a=source['artifact']
        raw=json.dumps(source['receipt'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        key=Ed25519PublicKey.from_public_bytes(base64.b64decode(att['health']['receipt_public_key_b64']));key.verify(base64.b64decode(source['signature']),raw)
        if sha(a)!=source['receipt']['artifact_sha256'] or hashlib.sha256(raw).hexdigest()!=source['receipt_sha256']:raise ValueError('POST_EVENT_SOURCE_DIGEST_INVALID')
        verified=call('/source/verify',source,'source_verification')
        if source['receipt']['status']!='SOURCE_FROZEN' or verified.get('valid') is not True:
            return save('terminal',{'status':'HOLD_SOURCE','venue_id':v,'race_date':date,'errors':a.get('errors'),
                    'scope':'POST_EVENT_TECHNICAL_ONLY','unknown_future_oos_count':0})
        cards=[s for s in a['sources'] if s['source_class'].startswith('OFFICIAL_RACE_CARD')]
        if len(cards)!=1:raise ValueError('OFFICIAL_RACE_CARD_SCOPE_REQUIRED')
        card=cards[0];body=gzip.decompress(base64.b64decode(card['raw_gzip_b64']))
        if hashlib.sha256(body).hexdigest()!=card['raw_sha256']:raise ValueError('OFFICIAL_RAW_DIGEST_INVALID')
        text=unicodedata.normalize('NFKC',_html_text(_decode(body,card['content_type'])));compact=re.sub(r'\s+','',text)
        y,m,d=map(int,date.split('-'))
        if f'{y}年{m}月{d}日' not in compact[:3000] or VENUE_NAMES[v]+'第1競走' not in compact[:3000]:raise ValueError('OFFICIAL_HEADER_IDENTITY_MISMATCH')
        header=text[:text.find('着別')];course=re.search(r'(ダート|芝)\s*(\d{3,4})\s*m[^\n]*?[（(](.*?)[)）]',header,re.S)
        start=(a['normalized_evidence'].get('start_time') or {}).get('value')
        if not course or not start:raise ValueError('OFFICIAL_COURSE_OR_POST_REQUIRED')
        post=dt.datetime.fromisoformat(date+'T'+start+':00').replace(tzinfo=dt.timezone(dt.timedelta(hours=9)))
        if dt.datetime.fromisoformat(a['source_freeze_at'])<=post:raise ValueError('POST_EVENT_DIAGNOSTIC_SCOPE_MISMATCH')
        name=re.search(r'第\s*1\s*競走\s*(.*?)\s*(?:ダート|芝)',header,re.S);title=' '.join(name.group(1).split()) if name else ''
        rows=a['active_runner_universe']['runners'];required=json.loads((ROOT/'mapping/local_full_numerical_mapping_v1.0_production_20261008.json').read_text())['required_indices']
        intent=save('intent',{'family_id':'LOCAL','race_id':race_id,'venue_id':v,'race_date':date,'race_no':1,
             'scheduled_post_at':post.isoformat(),'prediction_cutoff':a['prediction_cutoff'],'required_indices':required,
             'temporal_mode':'POST_EVENT_TECHNICAL_REPLAY','source_temporal_qualification':'RETRIEVED_AFTER_EVENT / AUXILIARY_LOOKAHEAD_RISK / NOT_PFS_VALIDATION',
             'run_count':20000,'seed':1,'runners':rows,
             'race':{'venue':VENUE_NAMES[v],'venue_id':v,'race_date':date,'race_no':1,'name':title,'class':title,
              'distance':int(course.group(2)),'distance_m':int(course.group(2)),'surface':'DIRT' if course.group(1)=='ダート' else 'TURF',
              'direction':'LEFT' if '左' in course.group(3) else 'RIGHT' if '右' in course.group(3) else 'UNKNOWN','runner_count':len(rows)},
             'purchase_authority':False,'production_authority':False,'performance_evaluation_eligible':False})
        canonical=ROOT/'runtime/executions'/race_id/'SOURCE/runs/20261013-post-event-diagnostic';canonical.mkdir(parents=True,exist_ok=True)
        p=canonical/'source_receipt_envelope.json';encoded=json.dumps(source,ensure_ascii=False,indent=2)+'\n'
        if p.exists() and p.read_text()!=encoded:raise ValueError('POST_EVENT_CANONICAL_SOURCE_CONFLICT')
        p.write_text(encoded)
        # SOURCE fetches stay parallel. This batch admits one Runtime engine
        # job at a time; no simulation count or selection is reduced.
        with ENGINE_ADMISSION:
            result=subprocess.run([sys.executable,str(ROOT/'runtime/formal_execution_orchestrator.py'),'--intent',str(root/'intent.json'),
                  '--aki-paper-replay','--frozen-source',str(p),'--run-id',race_id,'--output',str(root/'single_entry_report.json')],cwd=ROOT,capture_output=True,text=True,timeout=720)
        report=json.loads((root/'single_entry_report.json').read_text())
        return save('terminal',{'status':report['status'],'venue_id':v,'race_date':date,'race_id':race_id,'exit_code':result.returncode,
             'source_path':str(p.relative_to(ROOT)),'report_path':str((root/'single_entry_report.json').relative_to(ROOT)),
             'scope':'POST_EVENT_TECHNICAL_REPLAY / NOT_ORIGINAL_PRESTART / NOT_PFS_VALIDATION',
             'unknown_future_oos_count':0,'purchase_authority':False})
    except Exception as e:
        return save('terminal',{'status':'HOLD_POST_EVENT_DIAGNOSTIC','venue_id':v,'race_id':race_id,'race_date':date,
             'reason':str(e),'error_type':type(e).__name__,'unknown_future_oos_count':0,'scope':'POST_EVENT_TECHNICAL_ONLY'})

if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(lambda item:run(*item),TARGETS.items()))
    root=ROOT/'research/local_aki_post_event_venue_probe_20261013'
    report={'status':'ALL_ATTEMPTS_RETAINED / TRANSPORT_ONLY / NOT_HISTORICAL_PERFORMANCE',
        'rows':rows,'unknown_future_oos_count':0,'purchase_authority':False}
    (root/'probe_status.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
