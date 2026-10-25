"""Result-blind ranking and separately identified research tickets; no Production authority."""
import hashlib,json,math
from pathlib import Path
from datetime import datetime

FEATURES=('HPI','SSI','CFI','RFI','BVI','JTI','CSI','TRI','BWI','GCI','PRI','KGI','VMI','DCR','TPI','ZAI_WIN','ZAI_PLACE','SRI','F3S','T3I')
ID='JRA-CONDITIONAL-RANK-20261018-R1'
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def vectors(runners):
 ids=[str(r['runner_id']) for r in runners]
 if len(ids)!=len(set(ids)):raise ValueError('RANK_DUPLICATE_RUNNER')
 vals={str(r['runner_id']):[r['canonical_components'][k]['value'] for k in FEATURES] for r in runners}
 if any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=100 for row in vals.values() for v in row):raise ValueError('RANK_FULL20_REQUIRED')
 means=[sum(v[j] for v in vals.values())/len(vals) for j in range(len(FEATURES))]
 scales=[max(1.,math.sqrt(sum((v[j]-means[j])**2 for v in vals.values())/len(vals))) for j in range(len(FEATURES))]
 return {h:[(v[j]-means[j])/scales[j] for j in range(len(FEATURES))] for h,v in vals.items()}
def compare(request,model):
 if model.get('sha256')!=sha({k:v for k,v in model.items() if k!='sha256'}):raise ValueError('RANK_MODEL_HASH')
 if model.get('candidate_id')!=ID or model.get('features')!=list(FEATURES):raise ValueError('RANK_MODEL_SCHEMA')
 cutoff=datetime.fromisoformat(request['prediction_cutoff'].replace('Z','+00:00'))
 generated=datetime.fromisoformat(model['created_at'].replace('Z','+00:00'))
 source_time=datetime.fromisoformat(request['source_snapshot']['source_freeze_at'].replace('Z','+00:00'))
 if generated.tzinfo is None or cutoff.tzinfo is None or generated>=source_time or source_time>cutoff:raise ValueError('RANK_MODEL_NOT_AVAILABLE_BEFORE_SOURCE')
 if any(datetime.fromisoformat(r['result_captured_at'].replace('Z','+00:00'))>=generated for r in model['training_manifest']):raise ValueError('RANK_TRAIN_RESULT_AFTER_MODEL_FREEZE')
 if request['race_id'] in {x['race_id'] for x in model['training_manifest']}:raise ValueError('RANK_TRAIN_TARGET_OVERLAP')
 if not request['race_id'].startswith('KM-JRA-'):raise ValueError('RANK_JRA_ONLY')
 x=vectors(request['runners']);scores={}
 for role,w in model['coefficients'].items():
  if role not in ('W','P2','P3') or len(w)!=len(FEATURES) or any(type(v) not in (float,int) or not math.isfinite(v) for v in w):raise ValueError('RANK_WEIGHTS')
  scores[role]={h:sum(a*b for a,b in zip(v,w)) for h,v in x.items()}
 if set(scores)!=set(('W','P2','P3')):raise ValueError('RANK_ROLES_REQUIRED')
 rankings={role:sorted(values,key=lambda h:(-values[h],int(h))) for role,values in scores.items()}
 # Exclusion is conditional on each hypothetical head/pair, never the actual result.
 p2={h:[s for s in rankings['P2'] if s!=h] for h in x}
 third={h+'>'+s:[t for t in rankings['P3'] if t not in (h,s)] for h in x for s in x if h!=s}
 baseline={str(h):list(v) for h,v in ((request.get('static_prediction') or {}).get('roles') or {}).items()}
 widths={role:sum(role in roles for roles in baseline.values()) for role in ('W','P2','P3')}
 out={'candidate_id':ID,'race_id':request['race_id'],'model_policy_sha256':policy_sha(model),'reference_role_widths':widths,'baseline_roles':baseline,'model_sha256':model['sha256'],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'training_manifest_sha256':sha(model['training_manifest']),'source_sha256':request['source_snapshot_sha256'],
 'runner_universe_sha256':sha(sorted(x)),'prediction_cutoff':request['prediction_cutoff'],
 'scores':scores,'role_rankings':rankings,'head_local_p2':p2,'pair_conditioned_third':third,
 'calibrated_probabilities':False,'production_effect':'NONE','tickets_created':0,'promotion':'HOLD',
 'scope':'RANK_ONLY; no automatic Role, Ticket or Capital substitution','sha256':None}
 out.pop('sha256');out['sha256']=sha(out);return out

# Separate research ticket policy. Rank-only R1 never substitutes Production tickets.
EXPOSURE_POLICY={'candidate_id':'JRA-RANK-EQUAL-EXPOSURE-20261018-R1',
 'ordering':'sum of W rank, head-excluded P2 rank and pair-excluded P3 rank; numeric selection tie-break',
 'trio':'minimum ordinal sum over distinct orientations',
 'exposure':'same bet-type count and original stake multiset; no new capital',
 'purchase_authority':False,'automatic_promotion':False}
def policy_sha(model):
 return sha({'candidate_id':ID,'features':model['features'],'l2':model['l2'],'iterations':model['iterations'],'step':model['step'],
  'loss':'race-balanced target-versus-other pairwise logistic, fixed L2',
  'normalization':'within-race mean/std with scale floor 1',
  'conditioning':'exclude head for P2 and pair for Third; no learned interaction',
  'capture':'match frozen Production column widths for diagnostics only',
  'minimum_forward_distinct_races':model['minimum_forward_distinct_races'],'minimum_forward_days':model['minimum_forward_days'],'minimum_forward_venues':model['minimum_forward_venues'],
  'automatic_promotion':False})

def _validate_rank_universe(rank):
 rr=rank['role_rankings'];universe=set(rr['W'])
 if len(universe)<3 or any(not isinstance(h,str) or not h.isdigit() or not 1<=int(h)<=18 or str(int(h))!=h for h in universe):raise ValueError('EXPOSURE_RUNNER_UNIVERSE')
 if set(rr)!=set(('W','P2','P3')) or any(len(v)!=len(universe) or set(v)!=universe for v in rr.values()):raise ValueError('EXPOSURE_ROLE_UNIVERSE')
 if rank['runner_universe_sha256']!=sha(sorted(universe)):raise ValueError('EXPOSURE_UNIVERSE_HASH')
 if rank['head_local_p2']!={h:[s for s in rr['P2'] if s!=h] for h in universe}:raise ValueError('EXPOSURE_HEAD_P2_UNIVERSE')
 if rank['pair_conditioned_third']!={h+'>'+s:[t for t in rr['P3'] if t not in (h,s)] for h in universe for s in universe if h!=s}:raise ValueError('EXPOSURE_PAIR_THIRD_UNIVERSE')
 return universe

def exposure_portfolio(rank,final):
 """An outcome-blind, separately identified Shadow with exactly matched exposure."""
 from collections import Counter
 _validate_rank_universe(rank)
 if rank.get('sha256')!=sha({k:v for k,v in rank.items() if k!='sha256'}):raise ValueError('EXPOSURE_RANK_HASH')
 if final.get('sha256')!=sha({k:v for k,v in final.items() if k!='sha256'}):raise ValueError('EXPOSURE_FINAL_HASH')
 if (rank.get('race_id')!=final['race_id'] or rank['source_sha256']!=final['source_snapshot_sha256']
   or rank['prediction_cutoff']!=final['prediction_cutoff']
   or set(rank['role_rankings']['W'])!=set(map(str,final['static_prediction']['ranking']))):raise ValueError('EXPOSURE_BASELINE_BINDING')
 base=final['final_ticket']['tickets'];groups={k:[t for t in base if t['bet_type']==k] for k in ('EXACTA','TRIO','TRIFECTA')}
 if sum(map(len,groups.values()))!=len(base):raise ValueError('EXPOSURE_UNSUPPORTED_BET')
 if any(type(t['stake']) is not int or t['stake']<=0 or t['stake']%100 for t in base):raise ValueError('EXPOSURE_STAKE_INVALID')
 if sum(t['stake'] for t in base)!=final['final_ticket']['total_investment']:raise ValueError('EXPOSURE_BUDGET_INVALID')
 orders={k:{} for k in groups};p2=rank['head_local_p2'];third=rank['pair_conditioned_third']
 for wr,h in enumerate(rank['role_rankings']['W'],1):
  for sr,s in enumerate(p2[h],1):
   orders['EXACTA'][(int(h),int(s))]=wr+sr
   for tr,t in enumerate(third[h+'>'+s],1):
    key=(int(h),int(s),int(t));value=wr+sr+tr;orders['TRIFECTA'][key]=value
    trio=tuple(sorted(key));orders['TRIO'][trio]=min(value,orders['TRIO'].get(trio,value))
 tickets=[]
 for kind,original in groups.items():
  order=sorted(orders[kind],key=lambda sel:(orders[kind][sel],sel))
  if len(original)>len(order):raise ValueError('EXPOSURE_UNIVERSE_CAPACITY')
  # Original relative stake order is frozen; no outcome or payout is consulted.
  tickets += [{'bet_type':kind,'selection':list(sel),'stake':t['stake']} for sel,t in zip(order,original)]
 out={'candidate_id':EXPOSURE_POLICY['candidate_id'],'policy_sha256':sha(EXPOSURE_POLICY),'policy':dict(EXPOSURE_POLICY),
  'race_id':final['race_id'],'baseline_final_sha256':final['sha256'],'rank_comparison_sha256':rank['sha256'],
  'model_sha256':rank['model_sha256'],'model_policy_sha256':rank['model_policy_sha256'],
  'source_sha256':rank['source_sha256'],'runner_universe_sha256':rank['runner_universe_sha256'],'prediction_cutoff':rank['prediction_cutoff'],
  'tickets':tickets,'ticket_count':len(tickets),'required_capital':sum(t['stake'] for t in tickets),
  'bet_type_counts':dict(Counter(t['bet_type'] for t in tickets)),'added_capital':0,
  'production_effect':'NONE','purchase_authority':False,'automatic_promotion':False}
 out['sha256']=sha(out);return out

def evaluate_comparison(rank,actual):
 """Separate literal predicted chain, matched-width capture and oracle diagnostics."""
 actual=list(map(str,actual));rr=rank['role_rankings'];w=rr['W'][0];s=rank['head_local_p2'][w][0];t=rank['pair_conditioned_third'][w+'>'+s][0]
 widths=rank.get('reference_role_widths') or {'W':0,'P2':0,'P3':0};old=rank.get('baseline_roles') or {}
 capture={role:h in rr[role][:widths[role]] for role,h in zip(('W','P2','P3'),actual)}
 pair=capture['W'] and actual[1] in rank['head_local_p2'][actual[0]][:widths['P2']]
 exact=pair and actual[2] in rank['pair_conditioned_third'][actual[0]+'>'+actual[1]][:widths['P3']]
 migrations={role:[h for h in rr[role][:widths[role]] if 'P3' in old.get(h,[]) and role not in old.get(h,[])] for role in ('W','P2')}
 return {'candidate_id':rank['candidate_id'],'model_sha256':rank['model_sha256'],'model_policy_sha256':rank['model_policy_sha256'],
  'actual_role_ranks':{role:rr[role].index(h)+1 for role,h in zip(('W','P2','P3'),actual)},
  'oracle_head_local_p2_rank':rank['head_local_p2'][actual[0]].index(actual[1])+1,
  'oracle_pair_conditioned_third_rank':rank['pair_conditioned_third'][actual[0]+'>'+actual[1]].index(actual[2])+1,
  'oracle_conditioning_is_diagnostic_not_predicted_exact_capture':True,
  'predicted_chain':[w,s,t],'top1_ordered_pair_capture':[w,s]==actual[:2],'top1_exact_capture':[w,s,t]==actual,
  'matched_width_role_capture':capture,'matched_width_conditional_pair_capture':pair,'matched_width_conditional_exact_capture':exact,
  'p3_migrations_all_qualifying_horses':migrations,
  'actual_winner_migration_rescue':actual[0] in migrations['W'],'actual_second_migration_rescue':actual[1] in migrations['P2'],
  'tickets_or_capital_created':False}
