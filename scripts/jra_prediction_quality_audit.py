"""Full20 diagnostics and time-separated research fit; Oct18 is never forward OOS."""
import sys,json,math,statistics,hashlib,re
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
from jra_conditional_rank_shadow import FEATURES,ID,sha,vectors,compare
from jra_role_learning_shadow import build_shadow,settle_shadow,ticket_key
from jra_production_postresult import settle_final
from jra_20261018_formal_review import metrics

def load(p):return json.loads(p.read_text())
def ranks(values):
 return {h:1+sum(v>x for v in values.values())+(sum(v==x for v in values.values())-1)/2 for h,x in values.items()}
def corr(a,b):
 if len(a)<3:return None
 ma=statistics.mean(a);mb=statistics.mean(b);den=math.sqrt(sum((x-ma)**2 for x in a)*sum((x-mb)**2 for x in b))
 return sum((x-ma)*(y-mb) for x,y in zip(a,b))/den if den else None

def records():
 rows=[]
 for p in sorted((ROOT/'runtime/final_artifacts').glob('KM-JRA-*.json')):
  rid=p.stem;qp=ROOT/'runtime/requests'/(rid+'-LIVE-R1-FORMAL.json');rp=ROOT/'runtime/results'/p.name
  if not qp.exists() or not rp.exists():continue
  q=load(qp);f=load(p);r=load(rp)
  if q.get('temporal_mode')!='FORMAL-PRE-RACE':continue
  if r.get('frozen_prediction_ref',{}).get('immutable_final_sha256')!=f['sha256']:raise ValueError('FINAL_RESULT_BINDING')
  rows.append({'race_id':rid,'day':rid.split('-')[3],'venue':rid.split('-')[2],'q':q,'f':f,'r':r,
   'runners':q['runners'],'top3':list(map(str,r['official_result']['top3'])),'finish':list(map(str,r['official_result']['finish_order'])),'no_bet':False})
 for p in sorted((ROOT/'runtime/jra_no_bet_terminals').glob('*20261018*')):
  t=load(p);q=t['failure_report']['prepared_numerical_request'];rid=t['race_id']
  lp=ROOT/'runtime/jra_no_bet_learning'/p.name
  if not lp.exists():raise ValueError('CANONICAL_NO_BET_LEARNING_REQUIRED')
  l=load(lp)
  if l['sha256']!=sha({k:v for k,v in l.items() if k!='sha256'}) or l['decision_lineage_sha256']!=t['sha256']:raise ValueError('NO_BET_LEARNING_BINDING')
  rows.append({'race_id':rid,'day':'20261018','venue':rid.split('-')[2],'q':q,'runners':q['runners'],'top3':l['official_top3'],'finish':[], 'no_bet':True,'learning':l})
 return rows

def bvi_ablation(row):
 from copy import deepcopy
 from jra_index_provenance_builder import materialize_index_provenance
 minimal={'runners':[{'runner_id':str(r['runner_id'])} for r in row['runners']],
          'index_provenance_ledger':deepcopy(row['q']['index_provenance_ledger'])}
 baseline=materialize_index_provenance(minimal)
 expected={str(r['runner_id']):r['canonical_components'] for r in row['runners']}
 err=max(abs(r['canonical_components'][i]['value']-expected[str(r['runner_id'])][i]['value']) for r in baseline['runners'] for i in FEATURES)
 if err>2e-6:raise ValueError('REGISTERED_FORMULA_REPLAY_DIVERGENCE')
 for item in minimal['index_provenance_ledger']['runners'].values():
  item['base_indices']['BVI']['value']=50.0
 alternate=materialize_index_provenance(minimal)
 result={'race_id':row['race_id'],'max_formula_replay_error':err,'ablation':'IN_MEMORY_BVI_SCALAR_50_SENSITIVITY; not a Production ledger or forecast','rank_changes':{}}
 for idx,role,h in zip(('ZAI_WIN','ZAI_PLACE','T3I'),('W','P2','P3'),row['top3']):
  old=ranks({str(r['runner_id']):r['canonical_components'][idx]['value'] for r in baseline['runners']})
  new=ranks({str(r['runner_id']):r['canonical_components'][idx]['value'] for r in alternate['runners']})
  result['rank_changes'][role]={'with_bvi':old[h],'scalar_50':new[h]}
 return result

def verify_fit_rows(rows):
 """Bind research labels/features to existing canonical history before fitting.

 Self-declared manifest hashes do not authenticate a detached top3 or runner view.
 This is content validation, not a fresh verification of historical signatures.
 """
 from jra_shadow_checkpoint import verify_frozen_inputs
 ids=[row['race_id'] for row in rows]
 if not rows or len(ids)!=len(set(ids)):raise ValueError('RESEARCH_FIT_EMPTY_OR_DUPLICATE_RACE')
 for row in rows:
  rid=row['race_id'];q=row['q'];f=row['f'];result=row['r']
  if not re.fullmatch(r'KM-JRA-[A-Z]{3}-20[0-9]{6}-R[0-9]{2}',rid):raise ValueError('RESEARCH_FIT_RACE_ID')
  if (row.get('no_bet') or row.get('day',rid.split('-')[3])!=rid.split('-')[3]
      or row.get('venue',rid.split('-')[2])!=rid.split('-')[2]
      or any(obj.get('race_id')!=rid for obj in (q,f,result))
      or row['runners']!=q['runners'] or row['top3']!=list(map(str,result['official_result']['top3']))
      or len(row['top3'])!=3 or len(set(row['top3']))!=3
      or not set(row['top3'])<={str(h['runner_id']) for h in q['runners']}
      or q['source_snapshot_sha256']!=f['source_snapshot_sha256']
      or f['sha256']!=sha({k:v for k,v in f.items() if k!='sha256'})
      or result['frozen_prediction_ref']['immutable_final_sha256']!=f['sha256']):
   raise ValueError('RESEARCH_FIT_FROZEN_LABEL_INPUT_BINDING')
  canonical_final=load(ROOT/'runtime/final_artifacts'/f'{rid}.json')
  canonical_result=load(ROOT/'runtime/results'/f'{rid}.json')
  canonical_request=load(ROOT/'runtime/requests'/f'{rid}-LIVE-R1-FORMAL.json')
  if sha(q)!=sha(canonical_request) or sha(f)!=sha(canonical_final) or sha(result)!=sha(canonical_result):
   raise ValueError('RESEARCH_FIT_CANONICAL_HISTORY_BINDING')
  verify_frozen_inputs(ROOT,q,f)

def fit(rows):
 verify_fit_rows(rows)
 import numpy as np
 coeff={}
 for j,role in enumerate(('W','P2','P3')):
  deltas=[];weights=[]
  for row in rows:
   x=vectors(row['runners']);target=row['top3'][j];excluded=set(row['top3'][:j]);others=[h for h in x if h not in excluded and h!=target]
   for h in others:deltas.append(np.array(x[target])-np.array(x[h]));weights.append(1/len(others)/len(rows))
  a=np.array(deltas);wt=np.array(weights);w=np.zeros(len(FEATURES))
  # Fixed, strong L2, no outcome-dependent tuning. Race-balanced pairwise loss.
  for _ in range(500):
   z=np.clip(a@w,-40,40);grad=-(a.T@(wt/(1+np.exp(z))))+w
   w-=.15*grad
  coeff[role]=w.tolist()
 model={'candidate_id':ID,'features':list(FEATURES),'coefficients':coeff,'l2':1.,'iterations':500,'step':.15,
 'created_at':datetime.now(timezone.utc).isoformat(),'designed_after_known_results':True,
 'training_manifest':[{'race_id':r['race_id'],'source_sha256':r['q']['source_snapshot_sha256'],'final_sha256':r['f']['sha256'],'result_sha256':sha(r['r']),'result_captured_at':r['r']['official_result']['captured_at']} for r in rows],
 'training_dates':sorted({r['day'] for r in rows}),'automatic_promotion':False,'minimum_forward_distinct_races':60,'minimum_forward_days':3,'minimum_forward_venues':2,
 'no_auto_ticket_conversion':True,'scores_are_probabilities':False,'status':'RESEARCH_FROZEN_RANK_ONLY; NO PRODUCTION AUTHORITY'}
 model['sha256']=sha(model);return model

def role_metrics(rows,model):
 out=[]
 for row in rows:
  x=vectors(row['runners']);rr={role:ranks({h:sum(a*b for a,b in zip(v,model['coefficients'][role])) for h,v in x.items()}) for role in ('W','P2','P3')}
  base={role:ranks({str(r['runner_id']):r['canonical_components'][idx]['value'] for r in row['runners']}) for role,idx in zip(('W','P2','P3'),('ZAI_WIN','ZAI_PLACE','T3I'))}
  out.append({'race_id':row['race_id'],'learned_actual_role_ranks':{role:rr[role][h] for role,h in zip(('W','P2','P3'),row['top3'])},'production_index_role_ranks':{role:base[role][h] for role,h in zip(('W','P2','P3'),row['top3'])}})
 return {'race_count':len(out),'races':out,'mean_rank':{kind:{role:statistics.mean(r[kind][role] for r in out) for role in ('W','P2','P3')} for kind in ('learned_actual_role_ranks','production_index_role_ranks')},'paired_uncertainty':rank_uncertainty(out),'conditioning_limit':'Role-specific scores; head/pair conditioning is exclusion only, not learned interaction', 'classification':'RETROSPECTIVE_TIME_SEPARATED_NOT_FORWARD_OOS; specification designed after results'}

def rank_uncertainty(data):
 import random
 rng=random.Random(20261018);out={}
 for role in ('W','P2','P3'):
  delta=[r['learned_actual_role_ranks'][role]-r['production_index_role_ranks'][role] for r in data]
  boot=sorted(statistics.mean(rng.choices(delta,k=len(delta))) for _ in range(2000))
  out[role]={'mean_rank_delta':statistics.mean(delta),'paired_race_bootstrap_95pct':[boot[49],boot[1949]],
   'note':'Exploratory, post-result specification, no multiplicity correction; not confirmatory improvement.'}
 return out

def equal_budget(tickets,budget):
 # Outcome-blind largest-remainder allocation in integer 100-yen units.
 # No candidate can invent a ticket or silently change the common budget.
 if type(budget) is not int or budget<0 or budget%100:raise ValueError('COMMON_BUDGET_MUST_BE_INTEGER_100_YEN')
 if any(type(t['stake']) is not int or t['stake']<=0 or t['stake']%100 for t in tickets):raise ValueError('SOURCE_STAKE_INVALID')
 if not tickets or budget==0:return []
 units=budget//100;total=sum(t['stake'] for t in tickets);alloc=[units*t['stake']//total for t in tickets]
 order=sorted(range(len(tickets)),key=lambda i:(-(units*tickets[i]['stake']%total),i))
 for i in order[:units-sum(alloc)]:alloc[i]+=1
 return [{**t,'stake':100*n} for t,n in zip(tickets,alloc) if n]

def run():
 rows=records();day=[r for r in rows if r['day']=='20261018'];train=[r for r in rows if r['day']<'20261018'];model=fit(train)
 assert len(day)==36 and sum(len(r['runners']) for r in day)==450
 index={};paircorr=defaultdict(list);featuredeps=Counter();featurevalues=defaultdict(list);auditrows=[];bvistatus=Counter();bvisamples=[];changes=Counter();context_transitions=Counter()
 for row in day:
  allrank={idx:ranks({str(r['runner_id']):r['canonical_components'][idx]['value'] for r in row['runners']}) for idx in FEATURES}
  for idx in FEATURES:
   st=index.setdefault(idx,{'W':[],'P2':[],'P3':[],'normalized_role_rank':{'W':[],'P2':[],'P3':[]},'finish_spearman':[],'constant_races':0,'missing_cells':0})
   for role,h in zip(('W','P2','P3'),row['top3']):
    st[role].append(allrank[idx][h]);st['normalized_role_rank'][role].append((allrank[idx][h]-1)/(len(row['runners'])-1))
   vals={str(r['runner_id']):r['canonical_components'][idx]['value'] for r in row['runners']};st['constant_races']+=len(set(vals.values()))==1
   ids=[h for h in row['finish'] if h in vals];c=corr([allrank[idx][h] for h in ids],list(range(1,len(ids)+1)))
   if c is not None:st['finish_spearman'].append(c)
  for i,a in enumerate(FEATURES):
   for b in FEATURES[i+1:]:
    c=corr(list(allrank[a].values()),list(allrank[b].values()))
    if c is not None:paircorr[a+'|'+b].append(c)
  history=row['q'].get('source_snapshot',{}).get('jra_official_horse_history',{}).get('runners',{});ctx=row['q'].get('source_snapshot',{}).get('jra_race_context',{})
  for r in row['runners']:
   h=str(r['runner_id']);deps=defaultdict(list);parts=[]
   for idx,cell in r['canonical_components'].items():
    for c in cell.get('components',[]):deps[c['feature']].append(idx);parts.append({'index':idx,**{k:c.get(k) for k in ('feature','weight','category_score','weighted_contribution','feature_rule_id')}})
   for f,inds in deps.items():
    if len(set(inds))>1:featuredeps[f+'|'+'|'.join(sorted(set(inds)))]+=1
   cell=r['canonical_components']['BVI'];status='DCR_ONLY' if not cell.get('components') else 'MEASURED_PLUS_DCR' if cell.get('adjustments') else 'MEASURED';bvistatus[status]+=1
   for c in cell.get('components',[]):
    ns=re.search(r'offspring=(\d+)',c['source_fact']);mean=re.search(r'normalized_finish=([0-9.]+)',c['source_fact'])
    if ns and mean:
     n=int(ns[1]);v=float(mean[1]);bvisamples.append({'race_id':row['race_id'],'runner_id':h,'feature':c['feature'],'independent_offspring_reported':n,'raw_normalized_finish':v,'partial_pool_sensitivity':(n*v+20*.5)/(n+20),'prior_strength':20,'classification':'SENSITIVITY_ONLY_NOT_BAYESIAN_POSTERIOR_OR_PRODUCTION','identity_eligibility':'OFFICIAL_ID_NOT_INDEPENDENTLY_REVERIFIED'})
   features=r.get('evidence_features') or {};missing=[f for f in ('pedigree_surface','pedigree_distance','same_course_fit','distance_fit') if f not in features]
   for f,v in features.items():featurevalues[f].append({'category':v.get('category'),'observed_count':v.get('observation_count')})
   prior=(history.get(h) or {}).get('runs') or [];prior=next((x for x in prior if x.get('distance_m') and x.get('surface')),None)
   if prior:
    context_transitions['surface_changed' if prior['surface']!=ctx.get('surface') else 'same_surface']+=1
    if ctx.get('distance_m'):context_transitions['distance_'+('extended' if ctx['distance_m']>prior['distance_m'] else 'shortened' if ctx['distance_m']<prior['distance_m'] else 'same')]+=1
   auditrows.append({'race_id':row['race_id'],'venue':row['venue'],'runner_id':h,'name':r.get('name'),'no_bet':row['no_bet'],'actual_role':next((role for role,x in zip(('W','P2','P3'),row['top3']) if h==x),None),
    'indices':{i:r['canonical_components'][i]['value'] for i in FEATURES},'index_ranks':{i:allrank[i][h] for i in FEATURES},'feature_contributions':parts,'feature_evidence_sha256':sha(features),'feature_input_path':('runtime/jra_no_bet_terminals/'+row['race_id']+'-LIVE-R1.json#/failure_report/prepared_numerical_request/runners' if row['no_bet'] else 'runtime/requests/'+row['race_id']+'-LIVE-R1-FORMAL.json#/runners'),'feature_categories':{k:v.get('category') for k,v in features.items()},'missing_feature_ids':missing,
    'roles':row.get('f',{}).get('static_prediction',{}).get('roles',{}).get(h),'context':ctx,'previous_run':prior,'bvi_class':status})
 for idx,st in index.items():
  for role in ('W','P2','P3'):
   vals=st[role];norm=st['normalized_role_rank'][role];st[role]={'races':len(vals),'mean_midrank':statistics.mean(vals),'median_midrank':statistics.median(vals),'top3_midrank_count':sum(v<=3 for v in vals),'mrr':statistics.mean(1/v for v in vals),'mean_normalized_rank':statistics.mean(norm),'target_pairwise_concordance':1-statistics.mean(norm)}
  del st['normalized_role_rank']
  vals=st['finish_spearman'];st['mean_within_race_finish_spearman']=statistics.mean(vals) if vals else None;st['finish_spearman_races']=len(vals);del st['finish_spearman']
 capital=defaultdict(list);aki=[];krs=Counter()
 from itertools import permutations
 for row in day:
  if row['no_bet']:continue
  f,q,r=row['f'],row['q'],row['r'];budget=f['final_ticket']['total_investment'];s=build_shadow(q,f,historical=True,observed_at=f['final_freeze_timestamp']);settled=settle_shadow(s,r)
  if budget<=0:continue
  from post_result_learning import build_post_result_review
  ev=build_post_result_review(r,f)['krs']['post_result_evaluation']
  for key in ('unique_rescue_role_count','unique_harm_role_count','false_pair_addition_count','false_exact_addition_count','proposal_width'):krs[key]+=ev.get(key,0)
  krs['false_role_additions']+=len(ev['false_role_additions'])
  krs['added_capital']+=settled['arms']['KRS_ACTIONABLE']['added_capital']
  krs['false_positive_cost']+=settled['arms']['KRS_ACTIONABLE']['false_positive_cost']
  krs['added_ticket_return']+=settled['arms']['KRS_ACTIONABLE']['added_ticket_return']
  market=q['source_snapshot'].get('jra_official_market_observation',{}).get('runners',[])
  for name,top in [('STATIC_TOP3_BOX',f['static_prediction']['ranking'][:3]),('MARKET_TOP3_BOX',[x['runner_id'] for x in sorted(market,key=lambda x:x.get('popularity_rank',999))[:3]])]:
   if len(top)!=3:continue
   top=list(map(int,top));tickets=[{'bet_type':k,'selection':list(t),'stake':100} for k,n in [('EXACTA',2),('TRIFECTA',3)] for t in permutations(top,n)]+[{'bet_type':'TRIO','selection':sorted(top),'stake':100}]
   s['arms'][name]={'tickets':tickets}
  for name,a in s['arms'].items():
   tickets=equal_budget(a['tickets'],budget)
   if not tickets:continue
   ff={'final_ticket':{'tickets':tickets,'total_investment':budget}};z=settle_final(ff,r['official_result'])
   capital[name].append({'race_id':row['race_id'],'post_at':f['scheduled_post_at'],'investment':budget,'return':z['total_payout'],'pfs':z['pfs'],'formal_final':False,'first_material_failure':'RESEARCH','tickets':tickets,'baseline_keys_omitted':len({ticket_key(t) for t in f['final_ticket']['tickets']}-{ticket_key(t) for t in tickets})})
  a=f['static_prediction'].get('aki_jra_v21',{});roles=f['static_prediction']['roles'];aki.append({'race_id':row['race_id'],'aki_total':a.get('total'),'asi':a.get('axes',{}).get('ASI'),'miss_W':'W' not in roles.get(row['top3'][0],[]),'top3_all_outside':all(not roles.get(h) for h in row['top3'])})
 report={'profile':'JRA-FULL20-QUALITY-20261018-R1','races':36,'runners':450,'index_cells':9000,'formal_finals':34,'no_bet':2,
 'index_performance':index,'index_correlations':{k:{'mean_within_race_rank_correlation':statistics.mean(v),'races':len(v)} for k,v in paircorr.items()},
 'shared_feature_dependencies':dict(featuredeps),'shared_dependency_is_not_automatically_implementation_bug':True,
 'feature_category_counts':{f:dict(Counter(v['category'] for v in vals)) for f,vals in featurevalues.items()},'context_transitions':dict(context_transitions),'context_limit':'NO-BET prepared requests lack full context; class/surface causal effects not isolated', 'source_provenance_binding':'frozen requests and canonical results; predictive association is not causal feature value',
 'bvi':{'registered_formula_and_scalar_ablation':[bvi_ablation(row) for row in day],'classes':dict(bvistatus),'partial_pool_sensitivity':bvisamples,'direct_ZAI_WIN_or_PLACE_term':False,'incremental_predictive_improvement':'UNKNOWN; current-index association is not ablation','unaccepted_research_runs_used':0,'blood_b_new_collection':False},
 'all_runner_audit':auditrows,'krs_incremental_31_invested':{**dict(krs),'rescue_density_roles_per_proposal':krs['unique_rescue_role_count']/krs['proposal_width'],'harm_semantics':'Potential Static-correct Role non-confirmation, not Production ticket deletion','production_harm':False},'aki':aki,'equal_budget_capital':{name:{'metrics':metrics(data),'races':data,'classification':'EXPLORATORY_INTEGER_STAKE_EQUAL_BUDGET; not forward OOS','baseline_semantics_not_necessarily_preserved':True} for name,data in capital.items()},
 'rank_model_sha256':model['sha256'],'audit_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'rank_model_evaluation':role_metrics(day,model),'rank_model_training_races':len(train),'training_days':model['training_dates'],
 'training_label_trust':'Canonical RESULT bound to signed FINAL; historical RESULT receipts not independently reverified in this fit',
 'forward_coverage_limit':'Rank freeze is currently attached only to successful Formal FINAL; NO-BET rank forecast is not frozen by this path',
 'rank_design_limits':'41 races over 3 dates; selected-completion cohort, 20 correlated features, strong fixed L2, no hyperparameter search or performance-based promotion',
 'production_policy_changed':False,'forward_oos':'PENDING_UNKNOWN_FUTURE_FREEZE','actual_purchase':'UNVERIFIED'}
 report['sha256']=sha(report);return report,model
if __name__=='__main__':
 report,model=run();out=ROOT/'evidence/jra_p0_20261018';out.mkdir(exist_ok=True)
 import gzip
 payload=json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
 (out/'PREDICTION_QUALITY.json.gz').write_bytes(gzip.compress(payload,compresslevel=9,mtime=0))
 summary={k:v for k,v in report.items() if k not in ('all_runner_audit',)}
 summary['full_report_sha256']=summary.pop('sha256')
 summary['bvi']={k:v for k,v in report['bvi'].items() if k!='partial_pool_sensitivity'}
 summary['bvi']['partial_pool_sensitivity_rows']=len(report['bvi']['partial_pool_sensitivity'])
 for name,x in summary['equal_budget_capital'].items():x.pop('races')
 summary['sha256']=sha(summary)
 (out/'PREDICTION_QUALITY_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 p=ROOT/'research/jra_conditional_rank/model.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(model,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 print(json.dumps({'races':report['races'],'model':report['rank_model_evaluation']['mean_rank'],'training_races':report['rank_model_training_races']},indent=2))
