"""Short resumable worker: process only already-signed future PAPER FINALs.

The inherited zero-capital result handler labels research projection REPLAY;
this independent temporal classifier derives forward observation status only
from signed pre-start receipts and the preregistration bound in signed FINAL.
It never changes a prediction, re-runs KRS, or promotes Production.
"""
import argparse,base64,datetime as dt,gzip,hashlib,json,re,sys,unicodedata,urllib.request
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'runtime'))
from local_aki_columns import sha,verify
from local_fullnumerical_production import materialize_production
from local_physical.nar_source_manifest import _result_source,LOCAL_BABA_CODES,VENUE_NAMES
from local_physical.source_acquisition import _decode,_html_text
from tools.local_aki_external_postresult import run as settle_paper


def validate_forward_freeze(intent,source,final,selection,plan):
    att=json.loads((ROOT/'evidence/local_aki_columns_20261012/destination_verification.json').read_text())
    key=Ed25519PublicKey.from_public_bytes(base64.b64decode(att['health']['receipt_public_key_b64']))
    for e,phase,status in [(source,'SOURCE','SOURCE_FROZEN'),(final,'FINAL','PASS')]:
        raw=json.dumps(e['receipt'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        key.verify(base64.b64decode(e['signature']),raw)
        if sha(e['artifact'])!=e['receipt']['artifact_sha256'] or hashlib.sha256(raw).hexdigest()!=e['receipt_sha256']:
            raise ValueError('FORWARD_SIGNED_FREEZE_DIGEST_INVALID')
        if e['receipt']['phase']!=phase or e['receipt']['status']!=status or e['receipt']['race_id']!=intent['race_id']:
            raise ValueError('FORWARD_SIGNED_FREEZE_SCOPE_INVALID')
    parse=lambda x:dt.datetime.fromisoformat(x.replace('Z','+00:00'))
    fpp=final['artifact']['final_prediction_package'];registration=fpp.get('prospective_registration') or {}
    expected={'profile':plan['profile'],'registered_at':plan['registered_at'],'plan_sha256':sha(plan),
        'scheduled_post_at':intent['scheduled_post_at'],'prediction_cutoff':intent['prediction_cutoff'],
        'source_freeze_at':source['artifact']['source_freeze_at']}
    if fpp.get('temporal_mode')!='FORWARD_PAPER' or registration!=expected:
        raise ValueError('FORWARD_PREREGISTRATION_FINAL_BINDING_INVALID')
    if not (parse(plan['registered_at'])<parse(source['artifact']['source_freeze_at'])<=parse(intent['prediction_cutoff'])<parse(intent['scheduled_post_at'])):
        raise ValueError('FORWARD_TIME_ORDER_INVALID')
    if parse(final['receipt']['timestamp'])>=parse(intent['scheduled_post_at']):
        raise ValueError('FORWARD_FINAL_AFTER_POST')
    if fpp.get('purchase_authority') is not False or final['artifact']['final_ticket']['tickets']:
        raise ValueError('FORWARD_PAPER_PURCHASE_BOUNDARY_INVALID')
    if final['artifact']['source_receipt_sha256']!=source['receipt_sha256']:
        raise ValueError('FORWARD_FINAL_SOURCE_LINEAGE_INVALID')
    cards=[s for s in source['artifact']['sources'] if s['source_class'].startswith('OFFICIAL_RACE_CARD')]
    if len(cards)!=1:raise ValueError('FORWARD_OFFICIAL_CARD_SCOPE_INVALID')
    raw=gzip.decompress(base64.b64decode(cards[0]['raw_gzip_b64']))
    if hashlib.sha256(raw).hexdigest()!=cards[0]['raw_sha256']:raise ValueError('FORWARD_OFFICIAL_CARD_DIGEST_INVALID')
    text=re.sub(r'\s+','',unicodedata.normalize('NFKC',_html_text(_decode(raw,cards[0]['content_type']))))
    year,month,day=map(int,intent['race_date'].split('-'))
    if (f'{year}年{month}月{day}日' not in text[:3000] or
            VENUE_NAMES[intent['venue_id']]+f'第{intent["race_no"]}競走' not in text[:3000]):
        raise ValueError('FORWARD_OFFICIAL_CARD_IDENTITY_INVALID')
    # Prediction-affecting hashes, not inherited research display labels,
    # determine whether independently recalculated selection is unchanged.
    for name in ['runtime/local_aki_columns.py','profiles/local_aki_columns_20261012_R1.json',
                 'mapping/local_full_numerical_mapping_v1.0_production_20261008.json',
                 'mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json']:
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=plan['implementation_hashes'][name]:
            raise ValueError('FORWARD_FROZEN_PREDICTOR_CHANGED:'+name)
    q=materialize_production(source['artifact'],dict(intent,source_snapshot_sha256=source['artifact']['source_snapshot_sha256']),intent['required_indices'])
    verify(q,source['artifact'],selection)
    if fpp['aki_selection']!=selection:raise ValueError('FORWARD_SELECTION_FINAL_MISMATCH')
    return q


def validate_krs_chain(directory,intent,final):
    att=json.loads((ROOT/'evidence/local_aki_columns_20261012/destination_verification.json').read_text())
    key=Ed25519PublicKey.from_public_bytes(base64.b64decode(att['health']['receipt_public_key_b64']))
    pre=json.loads((directory/'pre_krs_receipt.json').read_text());krs=json.loads((directory/'krs_receipt.json').read_text())
    for e,phase,status in [(pre,'PRE_KRS','PASS'),(krs,'KRS_RUN','EXECUTED')]:
        raw=json.dumps(e['receipt'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        key.verify(base64.b64decode(e['signature']),raw)
        if (sha(e['artifact'])!=e['receipt']['artifact_sha256'] or hashlib.sha256(raw).hexdigest()!=e['receipt_sha256']
            or e['receipt']['phase']!=phase or e['receipt']['status']!=status or e['receipt']['race_id']!=intent['race_id']):
            raise ValueError('FORWARD_KRS_CHAIN_INVALID')
    if (final['artifact']['krs_receipt_sha256']!=krs['receipt_sha256'] or krs['artifact']['actual_run_count']<20000 or
        krs['artifact']['input_sha256']!=pre['artifact']['input_sha256'] or
        krs['artifact']['input_sha256']!=sha(json.loads((directory/'krs_input.json').read_text()))):
        raise ValueError('FORWARD_KRS_INPUT_OR_COUNT_INVALID')


def run_case(terminal,plan,now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    if 'report_path' not in terminal or terminal.get('exit_code')!=0:
        return dict(terminal,status='PILOT_HOLD_RETAINED / NO_OOS_PROMOTION')
    parse=lambda x:dt.datetime.fromisoformat(x.replace('Z','+00:00'))
    if now<parse(terminal['scheduled_post_at']):
        return {'race_id':terminal['race_id'],'status':'WAITING_OFFICIAL_RESULT / NOT_YET_POST','unknown_future_oos_count':0}
    intent=json.loads((ROOT/terminal['intent_path']).read_text())
    report=json.loads((ROOT/terminal['report_path']).read_text());acceptance=report['external_acceptance'];directory=ROOT/acceptance['path']
    source=json.loads((ROOT/terminal['source_path']).read_text());final=json.loads((directory/'final_receipt.json').read_text())
    selection=json.loads((directory/'selection.json').read_text())
    try:
        q=validate_forward_freeze(intent,source,final,selection,plan)
        validate_krs_chain(directory,intent,final)
        finished=directory/'forward_evaluation.json'
        if finished.exists():return json.loads(finished.read_text())
        att=json.loads((ROOT/'evidence/local_aki_columns_20261012/destination_verification.json').read_text());endpoint=att['endpoint']
        context=source['artifact']['source_race_context'];spec=_result_source(context['venue_id'],LOCAL_BABA_CODES[context['venue_id']],str(context['race_date']).replace('-','/'),int(context['race_no']))
        spec['required']=True
        request={'family_id':'LOCAL','race_id':intent['race_id'],**context,'prediction_cutoff':(now+dt.timedelta(minutes=10)).isoformat(),
                 'sources':[spec],'temporal_mode':'RESULT_ONLY_FORWARD_PAPER','prediction_authority':False}
        # Unpublished snapshots are attempts, not immutable successful results;
        # a later worker may retrieve a new official snapshot without new KRS.
        stamp=now.strftime('%Y%m%dT%H%M%S');attempt=directory/'result_attempts'/stamp;attempt.mkdir(parents=True,exist_ok=True)
        (attempt/'request.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n')
        req=urllib.request.Request(endpoint+'/source/acquire',data=json.dumps(request,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=180) as response:original=json.load(response)
        original_path=attempt/'source_receipt.json';original_path.write_text(json.dumps(original,ensure_ascii=False,indent=2)+'\n')
        if original['receipt']['status']!='SOURCE_FROZEN':raise ValueError('FORWARD_RESULT_SOURCE_HOLD')
        if parse(original['artifact']['sources'][0]['fetched_at'])<parse(intent['scheduled_post_at']):
            raise ValueError('FORWARD_RESULT_OBSERVATION_BEFORE_POST')
        result=settle_paper(directory/'acceptance.json',original_path)
        snapshot=json.loads((directory/'replay_result_receipt.json').read_text())['artifact']
        order=snapshot['official_result']['finish_order'];settlement=json.loads((directory/'paper_settlement.json').read_text())
        proof={'status':'FROZEN_UNKNOWN_FUTURE_PAPER_OBSERVED / NOT_PROMOTION_READY',
             'execution_id':acceptance['execution_id'],'race_id':intent['race_id'],'venue_id':intent['venue_id'],
             'source_receipt_sha256':source['receipt_sha256'],'final_receipt_sha256':final['receipt_sha256'],
             'result_receipt_sha256':result['result_receipt_sha256'],'plan_sha256':sha(plan),
             'source_freeze_at':source['artifact']['source_freeze_at'],'final_signed_at':final['receipt']['timestamp'],
             'scheduled_post_at':intent['scheduled_post_at'],'registered_at':plan['registered_at'],
             'official_top3':order[:3],'role_capture':{c:str(order[i]) in selection['columns'][c]['selected'] for i,c in enumerate(['W','P2','P3'])},
             'paper_settlement':settlement,'numerical_coverage':q['numeric_coverage'],
             'unknown_future_oos_count':1,'production_promotion_eligible':False,
             'production_comparator':'MISSING / NO_MATCHED_FUTURE_SUPERIORITY_CLAIM',
             'inherited_zero_capital_handler_scope':'REPLAY_LABEL_RETAINED; independent classification uses signed pre-start FINAL FORWARD_PAPER + chronology',
             'real_purchase':False,'actual_investment':0,'actual_pfs':None,'additional_krs_runs':0}
        finished.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');return proof
    except Exception as e:
        return {'race_id':terminal['race_id'],'status':'WAITING_OR_HOLD_OFFICIAL_RESULT','reason':str(e),
                'error_type':type(e).__name__,'unknown_future_oos_count':0,'additional_krs_runs':0}


def run():
    root=ROOT/'research/local_aki_forward_20261013';plan=json.loads((ROOT/'profiles/local_aki_prospective_evaluation_20261013_R2.json').read_text())
    pilot=json.loads((root/'pilot_status.json').read_text());rows=[run_case(t,plan) for t in pilot['results']]
    summary={'status':'FUTURE_PAPER_RESULT_WORKER_CHECKPOINT','rows':rows,
       'unknown_future_oos_count':sum(r['unknown_future_oos_count'] for r in rows),
       'all_five_terminal_results':all(r['status'].startswith('FROZEN_UNKNOWN') or r['status'].startswith('PILOT_HOLD') for r in rows),
       'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'purchase_authority':False,'production_promotion':False}
    (root/'result_worker_status.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    return summary

if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False))
