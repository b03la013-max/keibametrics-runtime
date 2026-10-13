"""Reuse existing signed OOS tracker, loss owners and robustness measurements."""
import json,sys,urllib.request,datetime as dt,subprocess,hashlib,gzip,copy
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
from aki_adaptive_oos_tracker import scan_execution_store
from family_conversion_diagnostics import measure_capital_conversion
from family_pfs_improvement import build_pfs_improvement_assessment
from family_pfs_promotion_gate import evaluate_promotion_gate
from pfs_grand_review import _aggregate,_robustness
from family_authority_guard import load_authority
BASE=ROOT/'research/family_conversion_20261013';EV=ROOT/'evidence/family_conversion_20261013';BASE.mkdir(parents=True,exist_ok=True);EV.mkdir(parents=True,exist_ok=True)
ENDPOINT='https://witnessstrictimage-production.up.railway.app'
def load(p):return json.loads(p.read_text())
def call(path,payload=None):
 req=urllib.request.Request(ENDPOINT+path,data=None if payload is None else json.dumps(payload,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=90) as r:return json.load(r)
health=call('/health');(EV/'runtime_health.json').write_text(json.dumps(health,indent=2)+'\n')
tracker=scan_execution_store(ROOT/'runtime/executions');(EV/'independent_17_tracker.json').write_text(json.dumps(tracker,ensure_ascii=False,indent=2)+'\n')
assert tracker['errors']==[] and tracker['eligible_races']==17
rows=[];verification=[]
for row in tracker['settled_rows']:
 rid=row['race_id'];fp=list((ROOT/'runtime/executions'/rid/'FORMAL').rglob('final_receipt_envelope.json'));rp=list((ROOT/'runtime/executions'/rid/'RESULT').rglob('result_receipt_envelope.json'));assert len(fp)==len(rp)==1
 f=load(fp[0]);result=load(rp[0]);d=fp[0].parent;intent=load(ROOT/'runtime/formal_intents'/f'{rid}.json') if (ROOT/'runtime/formal_intents'/f'{rid}.json').exists() else None
 if intent is None:
  # Formal request is a separate durable artifact in older execution stores.
  candidates=list(d.glob('*request*.json'));intent=next((load(p) for p in candidates if 'pair_dispositions' in load(p)),None)
 if intent is None:intent={'family_id':'LOCAL','race_id':rid,'pair_dispositions':[],'third_dispositions':[],'static_prediction':{}}
 sh=load(d/'aki_adaptive_purchase_shadow_pre_result.json');a=f['artifact'];utility=a['final_prediction_package']['krs_prediction_utility_shadow'];post=result['artifact']['automatic_post_result_review'];top=post['official_top3']
 baseline=measure_capital_conversion(intent,a['final_ticket'],a['final_prediction_package'],utility);candidate=measure_capital_conversion(intent,a['final_ticket'],a['final_prediction_package'],utility,candidate_tickets=sh['candidate_tickets'])
 assessment=build_pfs_improvement_assessment(post)
 pairs={tuple(t['selection'][:2]) for t in sh['candidate_tickets'] if t['bet_type'] in {'EXACTA','TRIFECTA'}}
 exacts={tuple(t['selection']) for t in sh['candidate_tickets'] if t['bet_type']=='TRIFECTA'}
 timing={n:load(d/name)['receipt']['timestamp'] for n,name in [('SOURCE','source_receipt_envelope.json'),('PRE_KRS','pre_krs_receipt_envelope.json'),('KRS_RUN','krs_receipt_envelope.json'),('FINAL','final_receipt_envelope.json')]}
 latency=(dt.datetime.fromisoformat(timing['FINAL'])-dt.datetime.fromisoformat(timing['SOURCE'])).total_seconds()
 row['timing']=timing;row['source_to_final_seconds']=latency
 row['aki_pair_precision_postresult']=int(tuple(top[:2]) in pairs)/len(pairs) if pairs else None
 row['aki_exact_precision_postresult']=int(tuple(top) in exacts)/len(exacts) if exacts else None
 row['materiality_evidence_available']=bool(intent.get('pair_dispositions'))
 prod=row['production'];ad=row['adaptive'];get=lambda tickets,bt,ids:any(t['bet_type']==bt and ((sorted(t['selection'])==sorted(ids)) if bt=='TRIO' else list(t['selection'])==ids) for t in tickets)
 rows.append({'timing':row['timing'],'source_to_final_seconds':row['source_to_final_seconds'],'aki_pair_precision_postresult':row['aki_pair_precision_postresult'],'aki_exact_precision_postresult':row['aki_exact_precision_postresult'],'materiality_evidence_available':row['materiality_evidence_available'],'race_id':rid,'date':row['race_day'],'family_id':'LOCAL','venue':'KAW' if '-KAW-' in rid else 'OHI','first_material_failure':post['failure_localization']['first_material_failure'],'dominant_pfs_loss_owner':assessment['dominant_pfs_loss_owner'],'learning_route':assessment.get('learning_routes',assessment.get('routes')),'production':prod,'adaptive':ad,'baseline_measurement':baseline,'candidate_measurement':candidate,'role_capture':post['prediction']['role_capture'],'static_ranking':post['prediction']['ranking'],'winner_rank':post['prediction']['ranking'].index(str(top[0]))+1,'krs_incremental_utility':post['krs'],'aki_axes':sh['aki_axes'],'aki_pair_capture':get(sh['candidate_tickets'],'EXACTA',top[:2]),'aki_exact_capture':get(sh['candidate_tickets'],'TRIFECTA',top),'false_additions_postresult':{'production_ticket_nonwinning_count':len(a['final_ticket']['tickets'])-sum(get([t],t['bet_type'],top[:2] if t['bet_type']=='EXACTA' else top) for t in a['final_ticket']['tickets']),'note':'POST_RESULT_ONLY / NOT_SELECTION_INPUT'},'receipt_refs':{'final':f['receipt_sha256'],'result':result['receipt_sha256']},'scope':'ORIGINAL_FROZEN_OOS_ARM / NEW_MEASUREMENT_IS_RETROSPECTIVE','new_candidate_oos_count':0,'actual_purchase_pfs':None})
 verification.extend([(rid,'FINAL',f),(rid,'RESULT',result)])
def verify(item):
 rid,phase,e=item;p=EV/f'{rid}-{phase}-external-verify.json'
 try:
  out=load(p) if p.exists() else call('/verify',e)
  p.write_text(json.dumps(out,indent=2)+'\n');return {'race_id':rid,'phase':phase,'receipt_sha256':e['receipt_sha256'],'valid':out.get('valid') is True,'path':str(p.relative_to(ROOT))}
 except Exception as exc:return {'race_id':rid,'phase':phase,'valid':False,'reason':str(exc)}
with ThreadPoolExecutor(max_workers=4) as pool:v=list(pool.map(verify,verification))
(EV/'external_verification_status.json').write_text(json.dumps(v,indent=2)+'\n')
def records(rr,arm):return [{'race_id':r['race_id'],'date':r['date'],'investment':r[arm]['investment'],'return':r[arm]['return'],'profit_loss':r[arm]['profit_loss'],'hit_but_loss':r[arm]['return']>0 and r[arm]['profit_loss']<0} for r in rr]
def summarize(rr):return {a:{'aggregate':_aggregate(records(rr,a)),'robustness':_robustness(records(rr,a))} for a in ('production','adaptive')}
_,authority=load_authority();report={'profile':'KM-FAMILY-PREDICTION-TO-CAPITAL-EXECUTION-CORRECTNESS-20261013-CANDIDATE','status':'CANDIDATE / NON-PRODUCTION','current_authority':authority['manifest_id'],'rows':rows,'original_17':summarize(rows),'kaw_13_eight':summarize([r for r in rows if r['date']=='2026-10-13' and r['venue']=='KAW']),'external_verified_receipts':sum(x['valid'] for x in v),'external_holds':[x for x in v if not x['valid']],'new_candidate_forward_oos':0,'equal_budget':'PENDING_FROZEN_COMPARATOR / NO_LINEAR_RESCALE_CLAIM','equal_ticket':'PENDING_FROZEN_COMPARATOR','no_bet_opportunity_cost':'NO_ABSTENTIONS_IN_ORIGINAL_17 / EXECUTION_FAILURE_NOT_NO_BET','static_only_ticket_pfs':'N/A / NO_FROZEN_STATIC_ONLY_TICKET_ARM','promotion_gate':evaluate_promotion_gate({'eligible_races':0,'distinct_days':0}),'family_scope':{'LOCAL':'REAL_SIGNED_REGRESSION','JRA':'COMMON_MEASUREMENT_MECHANICS_ONLY / NO_LOCAL_SELECTOR_IMPORT','BAN':'COMMON_MEASUREMENT_MECHANICS_ONLY / NO_LOCAL_SELECTOR_IMPORT'},'production_policy_changed':False}
raw=subprocess.check_output(['git','show','origin/codex/kaw-v25-regression-20261013:research/kaw_v25_20261013/day_regression.json'],cwd=ROOT)
report['kaw_all_24_statuses']=[{k:x.get(k) for k in ['race_id','status','first_material_failure','dominant_pfs_loss_owner','formal_pfs']} for x in json.loads(raw)['rows']]
report['pr263_dependency']={'commit':'3107a9ff5f5217372a34734ba3ceb8af8741a0b6','day_report_sha256':hashlib.sha256(raw).hexdigest(),'retrospective_only':True}
full=json.dumps(report,ensure_ascii=False,indent=2).encode()+b'\n'
archive=gzip.compress(full,mtime=0);(BASE/'full_report.json.gz').write_bytes(archive)
(EV/'full_report_manifest.json').write_text(json.dumps({'gzip_sha256':hashlib.sha256(archive).hexdigest(),'json_sha256':hashlib.sha256(full).hexdigest(),'path':'research/family_conversion_20261013/full_report.json.gz','all_decision_cells_preserved':True},indent=2)+'\n')
report=copy.deepcopy(report)
for row in report['rows']:
 for arm in ['baseline_measurement','candidate_measurement']:
  m=row[arm];m['full_detail_ref']='full_report.json.gz#'+row['race_id']+'/'+arm
  m['continuity_cell_count']=len(m.pop('pair_third_continuity'))
  losses=m['material_pair_losses'];m['material_pair_loss_count']=len(losses)
  m['material_pair_losses']=[{k:x[k] for k in ['head','second','prediction_materiality','removed_oriented_capital','exclusion_reason']} for x in losses]
(BASE/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'external_verified':report['external_verified_receipts'],'holds':report['external_holds'],'17':report['original_17'],'8':report['kaw_13_eight']},ensure_ascii=False))
