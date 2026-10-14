"""Evidence-derived KAW audit. Historical reviews are REGRESSION, never new OOS."""
import json,sys,base64,hashlib,gzip,datetime as dt
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from mec_r4_shadow import settle_ticket_list
from kaw_v25_conversion_review import build_review,sha
from aki_adaptive_purchase_shadow import verify_signed_final_binding
from family_authority_guard import load_authority
from local_fullnumerical_production import materialize_production
BASE=ROOT/'research/kaw_v25_20261013';BASE.mkdir(parents=True,exist_ok=True)
health=json.loads((ROOT/'evidence/kaw_v25_20261013/runtime_health.json').read_text());key=Ed25519PublicKey.from_public_bytes(base64.b64decode(health['receipt_public_key_b64']))
def load(p):return json.loads(p.read_text())
def signed(p,phase,rid):
 e=load(p);key.verify(base64.b64decode(e['signature']),json.dumps(e['receipt'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
 if e['receipt_sha256']!=sha(e['receipt']) or e['receipt']['artifact_sha256']!=sha(e['artifact']) or e['receipt']['phase']!=phase or e['receipt']['race_id']!=rid:raise ValueError('SIGNED_BINDING_INVALID:'+str(p))
 return e
observations=load(ROOT/'evidence/kaw_v25_20261013/official_observations.json');official={(r['date'],r['race_no']):r for r in observations}
rows=[];errors=[]
for day in ['20261012','20261013']:
 for r in range(1,13):
  date=f'{day[:4]}-{day[4:6]}-{day[6:]}'
  rid=f'KM-LOCAL-KAW-{day}-R{r:02}-LIVE-R1';intentpath=ROOT/'runtime/formal_intents'/f'{rid}.json';intent=load(intentpath) if intentpath.exists() else None
  row={'race_id':rid,'date':date,'race_no':r,'status':'UNCONFIRMED / NO_SIGNED_FINAL','formal_pfs':None,'actual_purchase_pfs':None,'official_observation':official[(date,r)],'evidence':[],'axis':'EXECUTION','first_material_failure':'UNCONFIRMED','dominant_pfs_loss_owner':'UNKNOWN','counterfactual_scope':'REGRESSION_ONLY / NOT_FORWARD_OOS'}
  if intent:
   row.update(intent_path=str(intentpath.relative_to(ROOT)),intent_sha256=sha(intent),scheduled_post_at=intent['scheduled_post_at'],prediction_cutoff=intent['prediction_cutoff'],notes=intent.get('notes'),static=intent.get('static_prediction'),distance=intent['race'].get('distance'))
   if not list((ROOT/'runtime/executions'/rid).rglob('final_receipt_envelope.json')):row.update(status='STATIC_INTENT_ONLY / NO_SIGNED_FINAL',first_material_failure='EXECUTION_TEMPORAL_FAILURE',dominant_pfs_loss_owner='EXECUTION_RESULT',missing=['Signed SOURCE checkpoint absent from main; DEADLINE_HOLD:SOURCE_INCOMPLETE corroborated by evidence/kaw_v25_20261013/failed_job_extracts.json; Intent notes are not runtime receipts'])
  finals=list((ROOT/'runtime/executions'/rid).rglob('final_receipt_envelope.json'))
  if finals:
   try:
    if len(finals)!=1:raise ValueError('AMBIGUOUS_FINAL')
    fpath=finals[0];directory=fpath.parent;f=signed(fpath,'FINAL',rid)
    if f['receipt']['status']!='PASS':raise ValueError('FINAL_NOT_PASS')
    if dt.datetime.fromisoformat(f['receipt']['timestamp'])>=dt.datetime.fromisoformat(intent['scheduled_post_at']):raise ValueError('FINAL_AFTER_POST')
    source=signed(directory/'source_receipt_envelope.json','SOURCE',rid);pre=signed(directory/'pre_krs_receipt_envelope.json','PRE_KRS',rid);krs=signed(directory/'krs_receipt_envelope.json','KRS_RUN',rid)
    if f['artifact']['source_receipt_sha256']!=source['receipt_sha256'] or f['artifact']['krs_receipt_sha256']!=krs['receipt_sha256'] or pre['artifact']['source_receipt_sha256']!=source['receipt_sha256'] or pre['artifact']['input_sha256']!=krs['artifact']['input_sha256'] or krs['artifact']['actual_run_count']!=intent['run_count']:raise ValueError('SOURCE_KRS_FINAL_LINEAGE')
    if source['receipt']['status']!='SOURCE_FROZEN' or dt.datetime.fromisoformat(source['artifact']['source_freeze_at'])>dt.datetime.fromisoformat(intent['prediction_cutoff']):raise ValueError('SOURCE_TEMPORAL_INVALID')
    for raw_source in source['artifact']['sources']:
     if raw_source.get('raw_gzip_b64') and hashlib.sha256(gzip.decompress(base64.b64decode(raw_source['raw_gzip_b64']))).hexdigest()!=raw_source['raw_sha256']:raise ValueError('SOURCE_RAW_HASH_INVALID')
    fpp=f['artifact']['final_prediction_package']
    if fpp['ranking']!=intent['static_prediction']['ranking'] or fpp['roles']!=intent['static_prediction']['roles']:raise ValueError('STATIC_FINAL_IDENTITY_INVALID')
    q=materialize_production(source['artifact'],intent,intent['required_indices'])
    recorded=load(directory/'index_provenance_manifest.json')
    recalculated=[dict(x) for runner in q['runners'] for x in runner.get('index_provenance',[])]
    # Inspect implementation output rows without manufacturing missing evidence.
    recalculated_values={(str(runner['runner_id']),name):v['value'] for runner in q['runners'] for name,v in runner.get('candidate_indices',{}).items()}
    for x in recorded['rows']:
     ident=(str(x['runner_id']),x['index'])
     if ident not in recalculated_values or recalculated_values[ident]!=x['value']:raise ValueError('NUMERICAL_RECALCULATION_MISMATCH:'+str(ident))
    resultpaths=list((ROOT/'runtime/executions'/rid/'RESULT').rglob('result_receipt_envelope.json'))
    if len(resultpaths)!=1:raise ValueError('MISSING_OR_AMBIGUOUS_RESULT')
    result=signed(resultpaths[0],'RESULT',rid)
    if result['receipt']['status']!='PASS' or result['artifact']['frozen_refs']['final_receipt_sha256']!=f['receipt_sha256']:raise ValueError('RESULT_FINAL_LINEAGE')
    obs=official[(date,r)]
    if obs['status']!='VERIFIED':raise ValueError('FRESH_OFFICIAL_RESULT_HOLD')
    facts=obs['official_result'];facts['top3']=facts['finish_order'][:3]
    if result['artifact']['official_result']['finish_order'][:3]!=facts['top3'] or result['artifact']['official_result']['payouts']!=facts['payouts']:raise ValueError('FRESH_OFFICIAL_RESULT_MISMATCH')
    tickets=f['artifact']['final_ticket']['tickets'];settle=settle_ticket_list(tickets,{'official_result':facts})
    old=result['artifact']['settlement']
    if settle['investment']!=old['investment'] or settle['return']!=old['return']:raise ValueError('INDEPENDENT_SETTLEMENT_MISMATCH')
    sh=load(directory/'aki_adaptive_purchase_shadow_pre_result.json');verify_signed_final_binding(f,sh);ass=settle_ticket_list(sh['candidate_tickets'],{'official_result':facts})
    # Replays a pre-result review from frozen inputs, explicitly after-event diagnostics.
    review=build_review(intent,f['artifact'],sh,generated_at=sh['generated_at'])
    (BASE/f'{rid}-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
    top=facts['top3'];pair=next((p for p in intent.get('pair_dispositions',[]) if [int(p['head']),int(p['second'])]==top[:2]),None);third=next((p for p in intent.get('third_dispositions',[]) if [int(p['head']),int(p['second']),int(p['third'])]==top),None)
    after=result['artifact']['automatic_post_result_review'];first=after['failure_localization']['first_material_failure'];owner='CAPITAL' if first=='CAPITAL_EFFICIENCY' else 'PREDICTION_ROLE' if first.startswith('PREDICTION_ROLE') else 'PAIR_EXACT_CONNECTION' if first in ['ORDERED_PAIR_CONVERSION','EXACT_ORIENTATION'] else 'NONE_REALIZED_PFS_POSITIVE' if settle['profit_loss']>=0 else 'UNKNOWN'
    row.update(status='VERIFIED / FROZEN-RECOMMENDATION',formal_pfs=settle['pfs'],settlement=settle,aki_settlement=ass,final_receipt_sha256=f['receipt_sha256'],source_receipt_sha256=source['receipt_sha256'],result_receipt_sha256=result['receipt_sha256'],final_signed_at=f['receipt']['timestamp'],krs_actual_runs=krs['artifact']['actual_run_count'],krs_input_mode=pre['artifact']['krs_input_mode'],first_material_failure=first,dominant_pfs_loss_owner=owner,role_capture=after['prediction']['role_capture'],krs_incremental_utility=after['krs'],correct_pair_decision=pair,correct_third_decision=third,review_sha256=review['sha256'],unresolved_review_count=review['unresolved_count'],aki_axes=sh['aki_axes'],aki_columns=sh['pair_local_columns'],market_sanity=review['market_status'],numeric_coverage=load(directory/'lifecycle_completion.json')['numeric_coverage'],evidence=[str(p.relative_to(ROOT)) for p in [fpath,directory/'source_receipt_envelope.json',directory/'pre_krs_receipt_envelope.json',directory/'krs_receipt_envelope.json',resultpaths[0]]])
   except Exception as e:row.update(status='HOLD_INTEGRITY',reason=type(e).__name__+':'+str(e));errors.append({'race_id':rid,'reason':row['reason']})
  rows.append(row)
def summary(rr,arm):
 ss=[r[arm] for r in rr if arm in r];i=sum(s['investment'] for s in ss);v=sum(s['return'] for s in ss)
 return {'races':len(ss),'investment':i,'return':v,'profit_loss':v-i,'pfs':v/i*100 if i else None,'hit_but_loss':sum(bool(s['hit_types']) and s['profit_loss']<0 for s in ss)}
# Independently re-settle original 17-race cohort; never rewrite tracker.
tracker=load(ROOT/'runtime/aki_adaptive_oos_status.json');cohort=[]
for entry in tracker['settled_rows']:
 rid=entry['race_id']
 try:
  fp=list((ROOT/'runtime/executions'/rid).rglob('final_receipt_envelope.json'));rp=list((ROOT/'runtime/executions'/rid/'RESULT').rglob('result_receipt_envelope.json'))
  if len(fp)!=1 or len(rp)!=1:raise ValueError('COHORT_PATH_AMBIGUOUS')
  f=signed(fp[0],'FINAL',rid);res=signed(rp[0],'RESULT',rid)
  if res['artifact']['frozen_refs']['final_receipt_sha256']!=f['receipt_sha256'] or entry['final_receipt_sha256']!=f['receipt_sha256']:raise ValueError('COHORT_FINAL_LINEAGE')
  sh=load(fp[0].parent/'aki_adaptive_purchase_shadow_pre_result.json');verify_signed_final_binding(f,sh)
  facts=res['artifact']['official_result'];facts['top3']=facts['finish_order'][:3]
  ps=settle_ticket_list(f['artifact']['final_ticket']['tickets'],{'official_result':facts});ass=settle_ticket_list(sh['candidate_tickets'],{'official_result':facts})
  if (ps['investment'],ps['return'],ass['investment'],ass['return'])!=(entry['production']['investment'],entry['production']['return'],entry['adaptive']['investment'],entry['adaptive']['return']):raise ValueError('COHORT_SETTLEMENT')
  cohort.append({'race_id':rid,'settlement':ps,'aki_settlement':ass,'status':'VERIFIED','final_receipt_sha256':f['receipt_sha256'],'result_receipt_sha256':res['receipt_sha256']})
 except Exception as exc:cohort.append({'race_id':rid,'status':'HOLD','reason':str(exc)})
p,a=load_authority();report={'status':'REGRESSION / CANDIDATE / NO_AUTO_PROMOTION','main_head':'7353e18a6af03208641187291771aa45641ee83e','current_authority':a['manifest_id'],'rows':rows,'integrity_errors':errors,'oct13_eight':{'production':summary([r for r in rows if r['date']=='2026-10-13'],'settlement'),'aki':summary([r for r in rows if r['date']=='2026-10-13'],'aki_settlement')},'original_17':{'rows':cohort,'production':summary(cohort,'settlement'),'aki':summary(cohort,'aki_settlement'),'errors':[r for r in cohort if r['status']=='HOLD']},'new_candidate_forward_oos_count':0,'actual_purchase_pfs':None,'production_promotion':False}
(BASE/'day_regression.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k in ['oct13_eight','integrity_errors']},ensure_ascii=False));print('17',report['original_17']['production'],report['original_17']['aki'],report['original_17']['errors'])
