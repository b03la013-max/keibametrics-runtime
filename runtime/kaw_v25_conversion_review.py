"""Opt-in KAW review arm. Reuses frozen selectors; never mutates tickets.

A lost material cell creates a review obligation, not purchase authority.
No outcome, pseudo-probability, threshold fitting or automatic capital changes.
"""
from copy import deepcopy
from collections import defaultdict
import hashlib,json,datetime as dt
PROFILE='KAW-v2.5-20261013-CONVERSION-REVIEW-v1'
DISPOSITIONS={'STRUCTURAL-INELIGIBLE','EVIDENCE-RANKED-LOWER','BUDGET-NONSELECTED','UNRESOLVED-REVIEW'}
def sha(obj):return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def when(x):
 t=dt.datetime.fromisoformat(str(x).replace('Z','+00:00'))
 if t.tzinfo is None:raise ValueError('NAIVE_TIME')
 return t

def build_review(req,artifact,shadow,*,generated_at,decisions=(),market=None):
 if req.get('family_id')!='LOCAL' or req.get('venue_id')!='KAW':raise ValueError('KAW_SCOPE_REQUIRED')
 if when(generated_at)>=when(req['scheduled_post_at']):raise ValueError('REVIEW_AFTER_POST')
 if req.get('post_result_after_final') is not None:raise ValueError('OUTCOME_INPUT_FORBIDDEN')
 if shadow.get('sha256')!=sha({k:v for k,v in shadow.items() if k!='sha256'}):raise ValueError('SELECTOR_DIGEST_INVALID')
 original=deepcopy(artifact);chosen=shadow.get('candidate_tickets',[]);fpp=artifact['final_prediction_package']
 pairkeys={tuple(map(str,t['selection'][:2])) for t in chosen if t['bet_type'] in {'EXACTA','TRIFECTA'}}
 exactkeys={tuple(map(str,t['selection'])) for t in chosen if t['bet_type']=='TRIFECTA'}
 baseline=artifact['final_ticket']['tickets'];basepairs={tuple(map(str,t['selection'][:2])) for t in baseline if t['bet_type'] in {'EXACTA','TRIFECTA'}}
 rules={}
 for d in decisions:
  key=tuple(map(str,d['cell']))
  if key in rules:raise ValueError('DUPLICATE_REVIEW_CELL')
  if d['disposition'] not in DISPOSITIONS or not d.get('evidence_refs') or not d.get('reason'):raise ValueError('UNSUPPORTED_DISPOSITION')
  if when(d['observed_at'])>when(req['prediction_cutoff']):raise ValueError('DECISION_EVIDENCE_AFTER_CUTOFF')
  if d['disposition']=='BUDGET-NONSELECTED' and not d.get('budget_receipt_ref'):raise ValueError('BUDGET_RECEIPT_REQUIRED')
  if d['disposition']=='EVIDENCE-RANKED-LOWER' and not d.get('comparison_cell'):raise ValueError('PAIR_SPECIFIC_COMPARISON_REQUIRED')
  rules[key]=deepcopy(d)
 cells=[]
 for pair in req.get('pair_dispositions',[]):
  key=(str(pair['head']),str(pair['second']))
  # Preserve both material and semantic-only independent mechanisms for review.
  if pair.get('status') not in {'PURCHASE','SEMANTIC_ONLY','PROTECT'}:continue
  worlds=[{k:t.get(k) for k in ['head','second','third','status','reason']} for t in req.get('third_dispositions',[]) if (str(t['head']),str(t['second']))==key]
  if key not in pairkeys:
   cells.append({'cell':list(key),'type':'HEAD_LOCAL_P2','baseline_material':key in basepairs,'baseline_status':pair['status'],'pre_result_reason':pair.get('reason'),'lost_third_worlds':worlds,'decision':rules.get(key,{'disposition':'UNRESOLVED-REVIEW','reason':'NO_PAIR_SPECIFIC_EXCLUSION_RECEIPT'})})
 # Pair-Trio intersections and protected third decisions are reviewed separately.
 trios={tuple(sorted(map(str,t['selection']))) for t in baseline if t['bet_type']=='TRIO'}
 for t in req.get('third_dispositions',[]):
  key=tuple(str(t[x]) for x in ['head','second','third'])
  if (t.get('status') in {'PROTECT','SEMANTIC_ONLY'} or (key[:2] in basepairs and tuple(sorted(key)) in trios)) and key not in exactkeys:
   cells.append({'cell':list(key),'type':'PAIR_CONDITIONED_THIRD','baseline_status':t['status'],'pre_result_reason':t.get('reason'),'cross_ticket_continuity':key[:2] in basepairs and tuple(sorted(key)) in trios,'decision':rules.get(key,{'disposition':'UNRESOLVED-REVIEW','reason':'NO_PAIR_LOCAL_EXACT_DISPOSITION'})})
 known={tuple(c['cell']) for c in cells}
 if set(rules)-known:raise ValueError('UNKNOWN_REVIEW_CELL')
 exposures={name:defaultdict(int) for name in ['head','pair','third','bet_type','tier']}
 for t in chosen:
  ids=list(map(str,t['selection']));stake=t['stake'];bt=t['bet_type'];exposures['bet_type'][bt]+=stake;exposures['tier'][t.get('mec_tier','UNCLASSIFIED')]+=stake
  if bt!='TRIO':
   exposures['head'][ids[0]]+=stake;exposures['pair']['>'.join(ids[:2])]+=stake
   if bt=='TRIFECTA':exposures['third']['>'.join(ids)]+=stake
 total=sum(t['stake'] for t in chosen);core=exposures['tier'].get('CORE',0)
 market_status='HOLD_PRICE_COVERAGE_MISSING';recoverability=[]
 if market is not None:
  if market.get('race_id')!=req['race_id'] or when(market['observed_at'])>when(req['prediction_cutoff']) or not market.get('source_ref'):raise ValueError('MARKET_TEMPORAL_OR_IDENTITY_INVALID')
  prices=market.get('ticket_decimal_prices',{})
  for t in chosen:
   if t.get('mec_tier')!='CORE':continue
   k=t['bet_type']+':'+'>'.join(map(str,t['selection']));price=prices.get(k)
   if isinstance(price,(int,float)) and price>0:recoverability.append({'ticket':k,'snapshot_gross':t['stake']*price,'total_capital':total,'not_probability_or_ev':True})
  corecount=sum(t.get('mec_tier')=='CORE' for t in chosen)
  if corecount and len(recoverability)==corecount:market_status='SNAPSHOT_ONLY / NOT_GUARANTEED_RETURN'
 unknown=[{'runner_id':rid,'reason':reason,'roles':fpp.get('roles',{}).get(rid,[])} for rid,reason in fpp.get('uncertainty',{}).items() if 'UNKNOWN' in str(reason) or 'INSUFFICIENT' in str(reason)]
 out={'profile':PROFILE,'race_id':req['race_id'],'status':'CANDIDATE / NON-PRODUCTION','generated_at':generated_at,'selector_sha256':shadow['sha256'],'source_snapshot_sha256':fpp.get('source_snapshot_sha256'),'cells':cells,'unresolved_count':sum(c['decision']['disposition']=='UNRESOLVED-REVIEW' for c in cells),'candidate_action':'PAPER_REVIEW_REQUIRED' if cells else 'PAPER','candidate_tickets':deepcopy(chosen),'exposure':{k:dict(v) for k,v in exposures.items()},'core_density':core/total if total else None,'market_status':market_status,'core_recoverability':recoverability,'unknown_role_review':unknown,'production_effect':'NONE','automatic_promotion':False,'purchase_authority':False,'actual_pfs':None,'forecast_probabilities':None,'economic_policy_changed':False}
 assert artifact==original
 out['sha256']=sha(out);return out
