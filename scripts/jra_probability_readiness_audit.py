"""Chronological research audit reusing the existing role fitter; never changes Production."""
import json,sys,math,re,statistics,hashlib
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'scripts'),str(ROOT/'research/jra_conditional_rank')]
from jra_prediction_quality_audit import records,fit,ranks
from jra_conditional_rank_shadow import sha
from probability_shadow import ID,POLICY,scores,distribution,fit_temperatures,measures,ece,conditional_nll,fit_ood,ood_score,instant
from jra_role_learning_shadow import support,EVIDENCE_GROUPS,market_disagreement


def manifest(row):return {'race_id':row['race_id'],'source_sha256':row['q']['source_snapshot_sha256'],'final_sha256':row['f']['sha256'],'result_sha256':sha(row['r']),'result_captured_at':row['r']['official_result']['captured_at'],'source_freeze_at':row['q']['source_snapshot']['source_freeze_at'],'prediction_cutoff':row['q']['prediction_cutoff'],'scheduled_post_at':row['f']['scheduled_post_at']}
def aggregate(items):
 if not items:return None
 return {**{key:statistics.mean(x[key] for x in items) for key in ('log_loss','brier_sum','rank_mid','top1_correct','top1_confidence')},'ece_5bin':ece(items),'races':len(items),'ece_definition':'top1 confidence/accuracy fixed equal-width bins; sparse-bin sensitivity; no calibration proof'}

def classification(row):
 if row['no_bet']:return 'NO_BET_NO_FINAL'
 return 'FUNDED_FINAL' if row['f']['final_ticket']['total_investment']>0 else 'ZERO_INVESTMENT_FINAL_PAPER'

def evaluate(row,model,ood):
 sc=scores(row['runners'],model['rank_model']);actual=row['top3'];d=distribution(sc,model['temperatures']);unit=distribution(sc,{r:1. for r in ('W','P2','P3')})
 roles={};unconditioned={};oracle={}
 for i,role in enumerate(('W','P2','P3')):
  roles[role]=measures(d['marginals'][role],actual[i]);unconditioned[role]=measures(unit['marginals'][role],actual[i])
  raw=ranks(sc[role]);kept={h:v for h,v in sc[role].items() if h not in actual[:i]};cond=ranks(kept)
  oracle[role]={'raw_rank':raw[actual[i]],'oracle_exclusion_rank':cond[actual[i]],'exclusion_rank_gain':raw[actual[i]]-cond[actual[i]],'within_context_order_change':False}
 top=max(d['ordered_joint'],key=lambda key:(d['ordered_joint'][key],tuple(-int(h) for h in key.split('>'))));pair=max(((h,s) for h in d['head_p2'] for s in d['head_p2'][h]),key=lambda hs:d['marginals']['W'][hs[0]]*d['head_p2'][hs[0]][hs[1]])
 out={'race_id':row['race_id'],'venue':row['venue'],'class':classification(row),'source_sha256':row['q'].get('source_snapshot_sha256'),'request_sha256':sha(row['q']),
 'final_sha256':row.get('f',{}).get('sha256'),'result_sha256':sha(row['r']) if row.get('r') else None,'actual_top3':actual,'marginal_roles':roles,'unit_temperature_marginal_roles':unconditioned,
 'production_index_ranks':{role:ranks({str(h['runner_id']):h['canonical_components'][index]['value'] for h in row['runners']})[actual[i]] for i,(role,index) in enumerate(zip(('W','P2','P3'),('ZAI_WIN','ZAI_PLACE','T3I')))},'oracle_conditioning_diagnostic':oracle,'conditional_nll':conditional_nll(sc,actual,model['temperatures']),
 'pair_log_loss':-math.log(d['marginals']['W'][actual[0]])-math.log(d['head_p2'][actual[0]][actual[1]]),
 'exact_log_loss':sum(conditional_nll(sc,actual,model['temperatures']).values()),
 'top1_pair':list(pair),'top1_pair_capture':list(pair)==actual[:2],'top1_exact':top.split('>'),'top1_exact_capture':top.split('>')==actual,
 'joint_sum':sum(d['ordered_joint'].values()),'prediction_input_result_blind':True}
 if not row['no_bet']:
  q=row['q'];f=row['f'];old=q['static_prediction']['roles'];m=market_disagreement(q,f);conflict=[]
  for h in row['runners']:
   positive=support(h);groups=[g for g,fs in EVIDENCE_GROUPS.items() if set(fs)&set(positive)]
   if 'W' not in old.get(str(h['runner_id']),[]) and len(positive)>=2 and len(groups)>=2:conflict.append(str(h['runner_id']))
  disagree=[r['runner_id'] for r in m['rows'] if r['market_rank'] is not None and r['market_rank']<=3 and r['rank_gap'] is not None and r['rank_gap']>=4 and 'W' not in old.get(r['runner_id'],[])]
  score=ood_score(row,ood);out['risk_diagnostics']={'aki':q['static_prediction']['aki_jra_v21']['total'],'winner_outside_W':'W' not in old.get(actual[0],[]),
   'independent_evidence_conflict_horses':conflict,'evidence_independence_proven':False,'market_disagreement_horses':disagree,'market_captured_at':m['captured_at'],
   'ood_score':score,'ood_flag':None if ood['threshold'] is None else score>ood['threshold'],'flags':{'evidence':bool(conflict),'market':bool(disagree),'ood':None if ood['threshold'] is None else score>ood['threshold']}}
 return out

def detection(rows):
 out={}
 for flag in ('evidence','market','ood'):
  a=[r['risk_diagnostics'] for r in rows if r.get('risk_diagnostics') and r['risk_diagnostics']['flags'][flag] is not None]
  tp=sum(x['flags'][flag] and x['winner_outside_W'] for x in a);fp=sum(x['flags'][flag] and not x['winner_outside_W'] for x in a);fn=sum(not x['flags'][flag] and x['winner_outside_W'] for x in a);tn=sum(not x['flags'][flag] and not x['winner_outside_W'] for x in a)
  out[flag]={'n':len(a),'tp':tp,'fp':fp,'fn':fn,'tn':tn,'sensitivity':tp/(tp+fn) if tp+fn else None,'specificity':tn/(tn+fp) if tn+fp else None,'precision':tp/(tp+fp) if tp+fp else None,'calibrated_error_probability':False}
 return out

def run():
 data=records();train=[r for r in data if r['day']<'20261017' and not r['no_bet']];cal=[r for r in data if r['day']=='20261017' and not r['no_bet']];test=[r for r in data if r['day']=='20261018']
 assert (len(train),len(cal),len(test))==(19,22,36)
 assert len({r['race_id'] for r in data})==len(data)
 for earlier,later in ((train,cal),(cal,[r for r in test if not r['no_bet']])):
  assert max(instant(r['r']['official_result']['captured_at']) for r in earlier)<min(instant(r['q']['source_snapshot']['source_freeze_at']) for r in later)
 rank=fit(train);rank['training_manifest']=[manifest(r) for r in train];rank['candidate_id']='JRA-TEMPORAL-RANK-REFIT-20261018-R1';rank['sha256']=sha({k:v for k,v in rank.items() if k!='sha256'})
 temps,losses=fit_temperatures(cal,rank);ood=fit_ood(train,cal)
 model={'candidate_id':ID,'rank_model':rank,'temperatures':temps,'calibration_manifest':[manifest(r) for r in cal],
  'created_at':datetime.now(timezone.utc).isoformat(),'policy_sha256':sha(POLICY),'policy':POLICY,'calibration_grid_losses':losses,'ood':ood,
  'status':'EXPLORATORY_REFIT_AND_TEMPERATURE_MAPPING; NOT_FORWARD_CALIBRATED','designed_after_oct18_results':True,'production_effect':'NONE','ev_kelly_authority':False,'oos_eligible':False}
 model['sha256']=sha(model);mp=ROOT/'research/jra_conditional_rank/probability_candidate.json';mp.write_text(json.dumps(model,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 rows=[evaluate(r,model,ood) for r in test];formal=[r for r in rows if r['class']!='NO_BET_NO_FINAL'];funded=[r for r in formal if r['class']=='FUNDED_FINAL'];low=[r for r in funded if r['risk_diagnostics']['aki']<=20]
 pedigree=defaultdict(list);missing_ids=0;horse_names={};bvi_samples=0
 for row in test:
  for h in row['runners']:
   hname=h.get('name');horse_names.setdefault(hname,set()).add(row['race_id'])
   history=((row['q'].get('source_snapshot') or {}).get('jra_official_horse_history') or {}).get('runners',{}).get(str(h['runner_id']),{})
   if not history.get('horse_id'):missing_ids+=1
   for part in h['canonical_components']['BVI'].get('components',[]):
    text=part.get('source_fact','');match=re.search(r'offspring=(\d+); runs=(\d+)',text)
    if match:pedigree[part.get('feature')].append(tuple(map(int,match.groups())));bvi_samples+=1
 audit_summary=json.loads((ROOT/'evidence/jra_p0_20261018/PREDICTION_QUALITY_SUMMARY.json').read_text())
 all_names={key:{h.get('name') for r in split for h in r['runners']} for key,split in [('train',train),('calibration',cal),('test',test)]}
 sampling=[]
 for day in sorted({r['day'] for r in data}):
  observed=[r for r in data if r['day']==day];iso=day[:4]+'-'+day[4:6]+'-'+day[6:];plan=ROOT/'runtime/jra_race_day_plan'/(iso+'.schedule.json');sched=json.loads(plan.read_text()) if plan.exists() else {};universe={k for k in sched if k.startswith('KM-JRA-')};ids={r['race_id'] for r in observed}
  sampling.append({'date':day,'observed_classes':dict(Counter(classification(r) for r in observed)),'official_schedule_races':len(universe),'scheduled_without_canonical_labeled_final_or_no_bet':len(universe-ids),'failure_labels_imputed':False})
 inventory={
 'role_rank_learning':{'status':'IMPLEMENTED','path':'runtime/jra_conditional_rank_shadow.py','limit':'Predictive performance UNVALIDATED in unknown future'},
 'winner_conditioned_p2_pair_third':{'status':'PARTIAL','path':'runtime/jra_conditional_rank_shadow.py','limit':'Exclusion-only context; no learned interactions; oracle rank gain is structural'},
 'probability_calibration':{'status':'PARTIAL','path':'research/jra_conditional_rank/probability_shadow.py','limit':'New temperature mapping with chronological test; not verified calibration or purchase authority'},
 'joint_coverage_calibration':{'status':'IMPLEMENTED','path':'research/adaptive_width/selector.py','limit':'Calibrates index-set coverage; not win probability'},
 'scenario_prediction':{'status':'IMPLEMENTED','path':'existing External KRS Physics / parameter_map','limit':'SSR remains uncalibrated; no Physics change'},
 'aki_independent_error_detection':{'status':'PARTIAL','path':'existing evidence/market diagnostics + new research OOD','limit':'Shared inputs and tiny validation cohort; no threshold change'},
 'bvi_hierarchical_model':{'status':'MISSING','path':'runtime/jra_pedigree_corpus.py','limit':'Continuous aggregate normalized_finish and repeated/overlapping runs are not independent binomial labels; official identity/grouped raw samples required'},
 'probability_ev_portfolio_optimization':{'status':'MISSING','path':'existing exposure portfolio and PAPER budget views','limit':'No validated joint probabilities or ticket-level same-time payout model; EV/Kelly ineligible'},
 'learning_closed_loop':{'status':'PARTIAL','path':'runtime/jra_role_learning_shadow.py / post_result_learning.py','limit':'Input bindings/chronology exist; live consumption0; fixed rank model does not consume Learning numerics'},
 'new_candidate_forward_connection':{'status':'UNVALIDATED','path':'probability_shadow.forecast(request, model)','limit':'Callable research adapter only; not merged, not attached to Formal Runner, not added to pinned72 cohort'}}
 report={'profile':'JRA-PREDICTIVE-STRUCTURE-AUDIT-20261018','inventory':inventory,'classification':'RETROSPECTIVE_CHRONOLOGICAL_EXPLORATION_NOT_FORWARD_OOS','production_effect':'NONE',
  'data_split':{'rank_train':len(train),'temperature_calibration':len(cal),'heldout_formal_final':len(formal),'heldout_no_bet_separate':len(rows)-len(formal),'date_order':'train Oct11/12, calibration Oct17, test Oct18','training_venues':dict(Counter(r['venue'] for r in train)),'calibration_venues':dict(Counter(r['venue'] for r in cal)),'result_before_next_source_checked':True,'design_after_test_results_known':True,'label_signature_trust':'Canonical FINAL/RESULT binding inherited; no fresh cryptographic verification of all historical training receipts'},
  'candidate_model_sha256':model['sha256'],'temperatures':temps,'roles':{role:{'temperature':aggregate([r['marginal_roles'][role] for r in formal]),'unit_temperature':aggregate([r['unit_temperature_marginal_roles'][role] for r in formal]),'production_index_mean_rank':statistics.mean(r['production_index_ranks'][role] for r in formal)} for role in ('W','P2','P3')},
  'joint':{'mean_pair_nll':statistics.mean(r['pair_log_loss'] for r in formal),'mean_exact_nll':statistics.mean(r['exact_log_loss'] for r in formal),'top1_pair_capture':sum(r['top1_pair_capture'] for r in formal),'top1_exact_capture':sum(r['top1_exact_capture'] for r in formal),'denominator':len(formal),'interaction_learning':'NOT_IMPLEMENTED_INSUFFICIENT_CONTEXT_DIVERSE_DATA','oracle_exclusion_mean_gain':{role:statistics.mean(r['oracle_conditioning_diagnostic'][role]['exclusion_rank_gain'] for r in formal) for role in ('W','P2','P3')}},
  'venue':{v:{role:aggregate([r['marginal_roles'][role] for r in formal if r['venue']==v]) for role in ('W','P2','P3')} for v in ('TKY','KYO','NGT')},
  'aki_detection':{'all_funded':detection(funded),'low_aki_20':detection(low),'low_aki_count':len(low),'low_aki_errors':sum(r['risk_diagnostics']['winner_outside_W'] for r in low),'ood':ood,'scope':'Post-result diagnostic design; flags not automatic candidate admission, rescue or calibrated risk'},
  'bvi':{'inherited_frozen_450_classes':audit_summary['bvi']['classes'],'sample_features':{k:{'reports':len(v),'offspring_min':min(x[0] for x in v),'offspring_max':max(x[0] for x in v),'run_min':min(x[1] for x in v),'run_max':max(x[1] for x in v)} for k,v in pedigree.items()},
   'runners_without_explicit_official_horse_id':missing_ids,'hierarchical_model_fit':'NOT_PERFORMED; no invented integer successes from continuous normalized_finish; no pooling of overlapping feature counts; no 408 admission','same_condition_historical_ablation':'Reuse PREDICTION_QUALITY_SUMMARY.bvi, not a Bayesian posterior or unknown-future utility'},
  'selection_bias':{'cohorts':sampling,'train_calibration_final_only':True,'generalization_to_failed_intake':'UNKNOWN','test_names_repeated_across_distinct_races':{k:sorted(v) for k,v in horse_names.items() if k and len(v)>1},'train_calibration_name_overlap':len(all_names['train']&all_names['calibration']),'train_test_name_overlap':len(all_names['train']&all_names['test']),'name_is_not_verified_permanent_horse_id':True,'horse_cluster_independence_not_proven':True,'metric_unit':'distinct canonical race','cross_race_independence':'UNVERIFIED'},
  'capital':{'ev_kelly_eligible':False,'reason':'Temperature mapping not forward validated; no joint ticket payout/risk model at matched market time','new_tickets_or_money':0,'same_exposure_comparison':'Unchanged main309 policy; reuse CONDITIONAL_FAILURE_ANALYSIS.capital','no_bet_opportunity_cost':'UNKNOWN; canonical rank freeze currently needs FINAL; NO-BET numeric diagnostics are separate'},
  'learning':{'live_consumption_proven':0,'existing_guard':'State SHA/effective_time/source freeze/cutoff/id constraints; no historic backdate','rank_numeric_effect':'NONE in existing fixed model','candidate_change':'No Production learning policy modified'},
  'next_72':{'plan_change':False,'candidate_activation':False,'existing_model_changed':False,'new_merge':False,'new_deploy':False,'new_candidate_oos':'PENDING_OWNER_APPROVAL_AND_SEPARATE_PRE_RESULT_REGISTRATION; existing72 retains original model/code pins'},'races':rows}
 report['code_sha256']={'audit':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'probability_shadow':hashlib.sha256((ROOT/'research/jra_conditional_rank/probability_shadow.py').read_bytes()).hexdigest()};report['sha256']=sha(report)
 dest=ROOT/'evidence/jra_p0_20261018/PREDICTIVE_STRUCTURE_AUDIT.json';dest.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 print(json.dumps({k:report[k] for k in ('data_split','temperatures','roles','joint','aki_detection','selection_bias')},ensure_ascii=False))
if __name__=='__main__':run()
