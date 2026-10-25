"""Fixed-model retrospective diagnostics. Never creates a historical OOS freeze."""
import json,sys,statistics,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'));sys.path.insert(0,str(ROOT/'scripts'))
from jra_prediction_quality_audit import records,ranks
from jra_conditional_rank_shadow import FEATURES,ID,sha,vectors,policy_sha,exposure_portfolio,evaluate_comparison
from jra_role_learning_shadow import support,EVIDENCE_GROUPS,market_disagreement
from jra_production_postresult import settle_final

def retrospective_rank(row,model):
 # Deliberately NOT compare(): this model did not exist before these past cutoffs.
 # No timestamp is backdated and this output is never written to live sidecars.
 q=row['q'];x=vectors(row['runners'])
 scores={role:{h:sum(a*b for a,b in zip(v,weights)) for h,v in x.items()} for role,weights in model['coefficients'].items()}
 rr={role:sorted(s,key=lambda h:(-s[h],int(h))) for role,s in scores.items()};base=(q.get('static_prediction') or {}).get('roles',{})
 out={'candidate_id':ID,'race_id':row['race_id'],'model_sha256':model['sha256'],'model_policy_sha256':policy_sha(model),
  'classification':'POST_RESULT_EXPLORATION_NOT_FORWARD_OOS','oos_eligible':False,'source_sha256':q.get('source_snapshot_sha256'),
  'runner_universe_sha256':sha(sorted(x)),'prediction_cutoff':q['prediction_cutoff'],'model_created_at':model['created_at'],
  'role_rankings':rr,'scores':scores,'baseline_roles':base,'reference_role_widths':{r:sum(r in roles for roles in base.values()) for r in ('W','P2','P3')},
  'head_local_p2':{h:[s for s in rr['P2'] if s!=h] for h in x},
  'pair_conditioned_third':{h+'>'+s:[t for t in rr['P3'] if t not in (h,s)] for h in x for s in x if h!=s}}
 out['sha256']=sha(out);return out

def attribution(row,rank,model,role,target):
 x=vectors(row['runners']);head=rank['role_rankings'][role][0]
 parts=[{'feature':f,'weighted_target_minus_top_score':(x[target][i]-x[head][i])*model['coefficients'][role][i],
  'coefficient':model['coefficients'][role][i],'target_standardized_value':x[target][i]} for i,f in enumerate(FEATURES)]
 return {'target':target,'top_ranked':head,'score_margin':rank['scores'][role][target]-rank['scores'][role][head],
  'parts':sorted(parts,key=lambda p:p['weighted_target_minus_top_score']),
  'interpretation':'ASSOCIATIONAL_LINEAR_SCORE_DECOMPOSITION_NOT_CAUSAL_EVIDENCE'}

def summary(rows):
 rows=sorted([r for r in rows if r['investment']>0],key=lambda r:(r['post_at'],r['race_id']))
 inv=sum(r['investment'] for r in rows);ret=sum(r['return'] for r in rows);equity=peak=dd=streak=longest=0
 for r in rows:
  equity+=r['return']-r['investment'];peak=max(peak,equity);dd=max(dd,peak-equity);streak=streak+1 if r['return']==0 else 0;longest=max(streak,longest)
 best=sorted(rows,key=lambda r:(-r['return'],r['race_id']))
 return {'invested_races':len(rows),'investment':inv,'return':ret,'pfs':100*ret/inv if inv else None,
  'largest_returns_excluded':{str(k):{'removed_races':[r['race_id'] for r in best[:k]],'pfs':100*sum(r['return'] for r in best[k:])/sum(r['investment'] for r in best[k:]) if sum(r['investment'] for r in best[k:]) else None} for k in (1,2,3)},
  'max_drawdown':dd,'max_zero_return_streak':longest,'actual_purchase':'UNVERIFIED'}

def run():
 model=json.loads((ROOT/'research/jra_conditional_rank/model.json').read_text());assert model['sha256']==sha({k:v for k,v in model.items() if k!='sha256'})
 rows=[r for r in records() if r['day']=='20261018'];out=[];base_cash=[];shadow_cash=[];low=[]
 for row in rows:
  rank=retrospective_rank(row,model);ev=evaluate_comparison(rank,row['top3']);q=row['q'];roles=(q.get('static_prediction') or {}).get('roles',{});actual=row['top3']
  cap={role:role in roles.get(h,[]) for role,h in zip(('W','P2','P3'),actual)}
  item={'race_id':row['race_id'],'venue':row['venue'],'no_bet':row['no_bet'],'request_content_sha256':sha(q),'source_sha256':q.get('source_snapshot_sha256'),'baseline_final_sha256':row.get('f',{}).get('sha256'),'official_result_content_sha256':sha(row['r']) if row.get('r') else None,'no_bet_learning_sha256':row.get('learning',{}).get('sha256'),'rank_comparison_sha256':rank['sha256'],'evaluation':ev,'baseline_role_capture':cap,
   'baseline_index_actual_midrank':{role:ranks({str(r['runner_id']):r['canonical_components'][idx]['value'] for r in row['runners']})[h] for role,idx,h in zip(('W','P2','P3'),('ZAI_WIN','ZAI_PLACE','T3I'),actual)},
   'winner_score_attribution':attribution(row,rank,model,'W',actual[0])}
  if row['race_id']=='KM-JRA-TKY-20261018-R12':item['p2_score_attribution']=attribution(row,rank,model,'P2',actual[1])
  if not row['no_bet']:
   f=row['f'];p=exposure_portfolio(rank,f);official=row['r']['official_result'];b=settle_final(f,official);s=settle_final({'final_ticket':{'tickets':p['tickets'],'total_investment':p['required_capital']}},official)
   from jra_role_learning_shadow import ticket_key
   old={ticket_key(t):t['stake'] for t in f['final_ticket']['tickets']};new={ticket_key(t):t['stake'] for t in p['tickets']}
   plus=[{**t,'stake':t['stake']-old.get(ticket_key(t),0)} for t in p['tickets'] if t['stake']>old.get(ticket_key(t),0)]
   minus=[{**t,'stake':t['stake']-new.get(ticket_key(t),0)} for t in f['final_ticket']['tickets'] if t['stake']>new.get(ticket_key(t),0)]
   def settle(ts):return settle_final({'final_ticket':{'tickets':ts,'total_investment':sum(t['stake'] for t in ts)}},official)
   plus_result=settle(plus);minus_result=settle(minus)
   item['portfolio']={'investment':p['required_capital'],'ticket_count':p['ticket_count'],'baseline_return':b['total_payout'],'shadow_return':s['total_payout'],
    'same_budget_and_point_count':p['required_capital']==f['final_ticket']['total_investment'] and p['ticket_count']==len(f['final_ticket']['tickets']),
    'added_capital':0,'redeployed_capital':sum(t['stake'] for t in plus),'false_positive_cost':sum(t['stake'] for t in plus)-sum(t['stake'] for t in plus_result['winning_tickets']),
    'increased_allocation_return':plus_result['total_payout'],'decreased_allocation_return':minus_result['total_payout'],
    'net_payout_increment':s['total_payout']-b['total_payout'],'policy_sha256':p['policy_sha256']}
   cash={'race_id':row['race_id'],'venue':row['venue'],'post_at':f['scheduled_post_at'],'investment':p['required_capital']}
   base_cash.append({**cash,'return':b['total_payout']});shadow_cash.append({**cash,'return':s['total_payout']})
   aki=q['static_prediction']['aki_jra_v21']['total']
   if p['required_capital']>0 and aki<=20:
    market=market_disagreement(q,f);m={r['runner_id']:r for r in market['rows']};diagnostics=[]
    for horse in row['runners']:
     h=str(horse['runner_id']);positive=support(horse);groups=[g for g,features in EVIDENCE_GROUPS.items() if set(positive)&features]
     diagnostics.append({'runner_id':h,'selected_W':'W' in roles.get(h,[]),'positive_observed_features':positive,'distinct_groups':groups,
       'supported_non_W':len(positive)>=2 and len(groups)>=2 and 'W' not in roles.get(h,[]),'market_disagreement':m.get(h)})
    low.append({'race_id':row['race_id'],'aki':aki,'actual_winner':actual[0],'winner_outside_W':not cap['W'],'axes':q['static_prediction']['aki_jra_v21']['axes'],'compiler_receipt':q.get('aki_compiler_receipt'),
      'winner_static_rank':f['static_prediction']['ranking'].index(int(actual[0]))+1 if isinstance(f['static_prediction']['ranking'][0],int) else f['static_prediction']['ranking'].index(actual[0])+1,
      'market_captured_at':market['captured_at'],'all_horse_evidence_diagnostics':diagnostics})
  out.append(item)
 report={'classification':'POST_RESULT_EXPLORATION_NOT_FORWARD_OOS','production_effect':'NONE','source_races':36,'no_bet_races':2,
  'model_sha256':model['sha256'],'model_policy_sha256':policy_sha(model),'model_created_at':model['created_at'],
  'aki_mechanism':{'code':'runtime/jra_aki_v21_features.py','observed':'Separation/density, axis groups, tail threats and rank-discordance derive from the same Full20 dependency; source_conflict is SOURCE conflicts, not model-market disagreement. Shared misranking can therefore produce low risk. Not a calibrated coverage probability.','production_repair':'No formal rule deviation established; thresholds unchanged; all-horse supported-non-W and market-gap diagnostics only'},'krs_negative_control':{'added_capital':60700,'added_losing_stake':59400,'evidence':'PREDICTION_QUALITY_SUMMARY.json; potential proposals do not imply paid rescue'},'conditioning_limit':'P2/Third exclusion only; no learned head/pair interaction. Oracle ranks are not actual predicted pair/exact capture.',
  'races':out,'role_metrics':{v:{'races':len([r for r in out if not r['no_bet'] and (v=='ALL' or r['venue']==v)]),'baseline_capture':{role:sum(r['baseline_role_capture'][role] for r in out if not r['no_bet'] and (v=='ALL' or r['venue']==v)) for role in ('W','P2','P3')},'matched_width_shadow_capture':{role:sum(r['evaluation']['matched_width_role_capture'][role] for r in out if not r['no_bet'] and (v=='ALL' or r['venue']==v)) for role in ('W','P2','P3')},'top1_pair_capture':sum(r['evaluation']['top1_ordered_pair_capture'] for r in out if not r['no_bet'] and (v=='ALL' or r['venue']==v)),'top1_exact_capture':sum(r['evaluation']['top1_exact_capture'] for r in out if not r['no_bet'] and (v=='ALL' or r['venue']==v))} for v in ('ALL','TKY','KYO','NGT')},'capital':{'production':summary(base_cash),'rank_equal_exposure_shadow':summary(shadow_cash),
   'by_venue':{v:{'production':summary([r for r in base_cash if r['venue']==v]),'shadow':summary([r for r in shadow_cash if r['venue']==v])} for v in ('TKY','KYO','NGT')},
   'false_positive_reallocated_cost':sum(r.get('portfolio',{}).get('false_positive_cost',0) for r in out),
   'redeployed_capital':sum(r.get('portfolio',{}).get('redeployed_capital',0) for r in out),
   'decreased_allocation_return':sum(r.get('portfolio',{}).get('decreased_allocation_return',0) for r in out)},
  'low_aki':{'invested_races':len(low),'winner_outside_W':sum(r['winner_outside_W'] for r in low),'races':low,
   'interpretation':'Internal score agreement is not calibrated external winner coverage. Supported non-W flags are correlated evidence conflicts, not proof of independent evidence or admission rules.'},
  'positive_controls':[{'race_id':r['race_id'],'portfolio':r.get('portfolio'),'production_artifact_unchanged':True} for r in out if r['race_id'] in ['KM-JRA-TKY-20261018-R11','KM-JRA-KYO-20261018-R02','KM-JRA-KYO-20261018-R04','KM-JRA-KYO-20261018-R10']],
  'forward_oos':{'eligible_races':0,'learning_actual_next_race_consumption':0,'status':'PENDING_NEW_PRE_CUTOFF_PROVIDER_WITNESS; not deployed or activated'},
  'bvi':{'measured':414,'mixed':12,'dcr_only':24,'hierarchical_bayes':'NOT_IMPLEMENTED; official IDs, independent sample counts and time-eligible labels required; no 408 admission'},
  'promotion':'HOLD; no performance improvement proven in unknown future races'}
 report['audit_code_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();report['rank_runtime_code_sha256']=hashlib.sha256((ROOT/'runtime/jra_conditional_rank_shadow.py').read_bytes()).hexdigest();report['sha256']=sha(report)
 dest=ROOT/'evidence/jra_p0_20261018/CONDITIONAL_FAILURE_ANALYSIS.json';dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('races','low_aki','positive_controls')},ensure_ascii=False))
if __name__=='__main__':run()
