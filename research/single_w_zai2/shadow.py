"""One preregistered W overlay; no model, SOURCE, Engine or Production writer."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime
import hashlib,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'runtime'))
from jra_aki_v21 import _select,select_columns,materialize
from jra_aki_v21_features import compile_features
from minimum_efficient_coverage import build_mec_plan,validate_mec_plan,MECError
from capital_policy import resolve_capital_policy

EXPERIMENT='JRA-SINGLE-W-ZAI2-SHADOW-v1-20261101'
AUTHORITY='KM-FAMILY-CURRENT-AUTHORITY-20261012-R51'
POLICY_FILES=('runtime/jra_aki_v21.py','runtime/jra_aki_v21_features.py',
 'runtime/jra_aki_capital_preflight.py','runtime/jra_production_postresult.py',
 'runtime/jra_candidate_postresult_closedloop.py','runtime/jra_presentation.py','runtime/jra_delivery.py',
 'runtime/execution_store.py','runtime/jra_pedigree_corpus.py','runtime/family_authority_guard.py',
 'runtime/jra_static_owner_executable.py',
 'profiles/KM_FAMILY_CURRENT_AUTHORITY_20261012_R51.json',
 'profiles/family_runtime_contracts_20261008_R28.json','profiles/family_scope_ownership_20260928_R1.json',
 'evidence/jra_bvi_phase3_20261017/runtime_health.json',
 'runtime/minimum_efficient_coverage.py','runtime/capital_policy.py',
 'profiles/jra_aki_v21_components_20261011_v1.json','profiles/jra_aki_v21_columns_20261011_v1.json',
 'research/single_w_zai2/shadow.py','research/single_w_zai2/worker.py',
 '.github/workflows/km-jra-single-w-zai2-shadow.yml')
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def time(x):
 d=datetime.fromisoformat(str(x).replace('Z','+00:00'))
 if d.tzinfo is None:raise ValueError('SHADOW_CLOCK_TIMEZONE_REQUIRED')
 return d
def fingerprint(root=ROOT):
 return digest({p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in POLICY_FILES})
def values(final):
 rows=final['final_prediction_package']['index_provenance_replay']['runners']
 return {str(r):{**v['base_final_values'],**{k:x['value'] for k,x in v['derived_index_trace'].items()}} for r,v in rows.items()}
def ticket_set(tickets):
 return sorted((t['bet_type'],tuple(sorted(t['selection'])) if t['bet_type']=='TRIO' else tuple(t['selection']),t['stake']) for t in tickets)
def public_tickets(tickets):return [{k:deepcopy(t[k]) for k in ('bet_type','selection','stake')} for t in tickets]
def canonical_zai_rank(vv):
 from jra_static_owner_executable import _rank
 return _rank([{'runner_id':r,'canonical_components':{'ZAI_WIN':{'value':v['ZAI_WIN']}}} for r,v in vv.items()],'ZAI_WIN')
def _portfolio(req,budget):
 req=deepcopy(req)
 req['capital_policy']={'mode':'HARD_RACE_BUDGET','max_race_capital':budget,'insufficient_action':'NO_BET'}
 p3={r for r,cols in req['static_prediction']['roles'].items() if 'P3' in cols}
 existing={(str(t['head']),str(t['second']),str(t['third'])) for t in req['third_dispositions']}
 for pair in req['pair_dispositions']:
  if pair['status'] not in {'PURCHASE','PROTECT'}:continue
  h,s=str(pair['head']),str(pair['second'])
  if any((h,s,t) not in existing for t in p3-{h,s}):
   raise ValueError('SHADOW_REGISTERED_THIRD_DISPOSITION_MISSING:'+h+'>'+s)
 try:
  # Existing MEC terminalization is retained. No new compatible Pair/Third
  # evidence is synthesized by this experiment.
  mec=build_mec_plan(req,None,strict_head_closure=True,min_stake=100)
  if not validate_mec_plan(mec)['mec_verified']:raise ValueError('SHADOW_MEC_INVALID')
 except MECError as exc:
  if not str(exc).startswith('ACTIVE_W_WITHOUT_MATERIAL_PAIR_CLOSURE:'):raise
  return {'status':'NO_MATERIAL_HEAD_CONNECTION','reason':str(exc),'tickets':[],
          'stake_yen':0,'required_mec_yen':None,'pfs':None,'budget_yen':budget}
 capital=resolve_capital_policy(req,mec)
 tickets=[] if capital['no_bet'] else mec['tickets']
 return {'status':'SHADOW_NO_BET' if capital['no_bet'] else 'SHADOW_TICKETS',
         'capital':capital,'required_mec_yen':mec['minimum_required_capital'],
         'tickets':public_tickets(tickets),'stake_yen':sum(t['stake'] for t in tickets),
         'budget_yen':budget,'ticket_count':len(tickets),'mec_sha256':mec['sha256']}
def build(final,source,*,root=ROOT):
 """Pure research projection from the signed FINAL's actual numeric trace.

 Signatures are verified by the Worker, not by a caller-supplied PASS boolean.
 This computation never grants purchase, signature or OOS authority.
 """
 from jra_production_postresult import verify_final
 verify_final(final)
 rid=final['race_id'];fpp=final['final_prediction_package']
 if (final.get('family_id')!='JRA' or source.get('race_id')!=rid
     or source.get('source_snapshot_sha256')!=final['source_snapshot_sha256']):
  raise ValueError('SHADOW_SOURCE_FINAL_IDENTITY_MISMATCH')
 ctx=source.get('jra_race_context') or {}
 if (not str(ctx.get('raw_race_context') or '').strip() or ctx.get('race_type') in {'UNKNOWN','JUMP'}
     or '障害' in str(ctx.get('raw_race_context','')) or ctx.get('surface') not in {'芝','ダ','ダート'}):
  raise ValueError('SHADOW_FLAT_SCOPE_NOT_PROVEN')
 ft=final['final_ticket'];capital=final['capital_policy_decision']
 if ft.get('no_bet') or capital.get('no_bet') or capital.get('paper_only') or capital.get('decision') not in {'EXECUTE_FULL_MEC','EXECUTE_RECOMMENDATION_PORTFOLIO'} or ft['total_investment']<=0:
  return {'race_id':rid,'classification':'NOT_ELIGIBLE_PAPER_OR_NO_BET','eligible':False,'oos_credit':0}
 policy=json.loads((root/'profiles/jra_aki_v21_components_20261011_v1.json').read_text())
 registry=json.loads((root/'profiles/jra_aki_v21_columns_20261011_v1.json').read_text())
 if fpp['aki_compiler_receipt']['policy_sha256']!=digest(policy['feature_compiler_policy']) or fpp['aki_column_selection']['registry_sha256']!=digest(registry):
  raise ValueError('SHADOW_REGISTERED_RULE_PIN_MISMATCH')
 vv=values(final);roles=final['static_prediction']['roles']
 active={str(x['runner_id']) for x in source['jra_official_runner_universe']['runners'] if x.get('status','ACTIVE')=='ACTIVE'}
 if active!=set(vv) or active!=set(roles):raise ValueError('SHADOW_ACTIVE_UNIVERSE_MISMATCH')
 if any(set(v)!=set(policy['feature_compiler_policy']['required_indices']) or any(type(x) not in (int,float) or not math.isfinite(x) or not 0<=x<=100 for x in v.values()) for v in vv.values()):raise ValueError('SHADOW_FROZEN_FULL20_INVALID')
 rank=canonical_zai_rank(vv)
 heads=[r for r in rank if 'W' in roles[r]]
 if len(heads)!=1:return {'race_id':rid,'classification':'CONTROL_MULTIPLE_W','eligible':False,'oos_credit':0}
 original=deepcopy(final['static_prediction'])
 # The provenance says numeric projection, not an original signed request.
 rows=[{'runner_id':r,'canonical_components':{k:{'value':v,'rule_id':'FROZEN_FINAL_NUMERIC_PROJECTION',
       'mapping_version':'SHADOW_PROJECTION_NOT_PRODUCTION_MAPPING',
       'source_fact':'Read from immutable FINAL '+final['sha256'],
       'evidence_refs':['SIGNED_FINAL:'+final['sha256']]} for k,v in vv[r].items()}} for r in rank]
 req={'family_id':'JRA','race_id':rid,'source_snapshot_sha256':final['source_snapshot_sha256'],
      'prediction_cutoff':final['prediction_cutoff'],'runners':rows,'static_prediction':original}
 compiled=compile_features(req,deepcopy(source),policy['feature_compiler_policy'])
 _,calculation=materialize(compiled,policy,registry_hash=digest(policy))
 baseline=select_columns(req,compiled,calculation,registry,registry_hash=digest(registry))
 if baseline['static_prediction']['roles']!=roles or baseline['aki_column_selection']['columns']!=fpp['aki_column_selection']['columns']:
  raise ValueError('SHADOW_S0_REGISTERED_ROLE_REPLAY_MISMATCH')
 for k in ('role_registry','pair_dispositions','third_dispositions','purchased_heads'):
  baseline[k]=deepcopy(final[k])
 baseline['aki_information_gate']=deepcopy(fpp.get('aki_information_gate',{}))
 baseline['head_nonselection_reasons']={};baseline['orientation_exclusions']=deepcopy(final.get('orientation_exclusions',[]))
 s0check=_portfolio(baseline,10000)
 if ticket_set(s0check['tickets'])!=ticket_set(ft['tickets']):raise ValueError('SHADOW_S0_CANONICAL_TICKET_REPLAY_MISMATCH')
 second=rank[1];s1=deepcopy(baseline);already=second in heads
 absent=[]
 if not already:
  s1['purchased_heads']=heads+[second]
  s1['static_prediction']['roles'][second]=list(dict.fromkeys(roles[second]+['W']))
  for row in s1['role_registry']:
   if row['runner_id']==second and row['column']=='W':row.update(status='CORE',reason='SINGLE_DECLARED_SHADOW_W_INTERVENTION',production_authority=False)
  # The sole intervention is accepting this W head. All Pair/Third facts,
  # thresholds, P2/P3 membership and ordered-vs-set rules remain unchanged.
  cols=fpp['aki_column_selection']['columns'];facts=compiled['aki_selection_features']
  cutoff=time(source['prediction_cutoff']);sh=source['source_snapshot_sha256']
  for p2 in cols['P2']:
   if p2==second:continue
   key=second+'>'+p2;pair=facts['pairs'].get(key)
   if pair is None:absent.append(key);continue
   matches=_select(pair,registry['pairs'],cutoff=cutoff,source_hash=sh)
   ordered=facts['runners'][p2]['P2']['category']=='MAIN'
   s1['pair_dispositions'].append({'head':second,'second':p2,'status':('PURCHASE' if ordered else 'PROTECT') if matches else 'SEMANTIC_ONLY','reason':'REGISTERED_PAIR_EVIDENCE','rule_matches':matches})
   if not matches:continue
   for p3 in cols['P3']:
    if p3 in {second,p2}:continue
    tkey=key+'>'+p3;third=facts['thirds'].get(tkey)
    if third is None:absent.append(tkey);continue
    tm=_select(third,registry['thirds'],cutoff=cutoff,source_hash=sh)
    core=ordered and facts['runners'][p3]['P3']['category']=='MAIN'
    s1['third_dispositions'].append({'head':second,'second':p2,'third':p3,'status':('PURCHASE' if core else 'PROTECT') if tm else 'SEMANTIC_ONLY','reason':'REGISTERED_THIRD_EVIDENCE','rule_matches':tm})
 for row in s1['role_registry']+s1['pair_dispositions']+s1['third_dispositions']:row['production_authority']=False
 out={'experiment':EXPERIMENT,'race_id':rid,'classification':'UNSIGNED_RESEARCH_SHADOW_NOT_FORMAL_FINAL',
      'eligible':True,'production_effect':'NONE','purchase_authority':False,'oos_credit':0,
      'source_snapshot_sha256':final['source_snapshot_sha256'],'final_sha256':final['sha256'],
      'final_receipt_sha256':final['final_receipt_sha256'],'authority':AUTHORITY,
      'scheduled_post_at_original':final['scheduled_post_at'],'production_final_freeze':final['final_freeze_timestamp'],
      'production_final_signed_at':final['final_receipt']['receipt']['timestamp'],
      'full20_value_digest':digest(vv),'original_W':heads,'added_W':None if already else second,
      'S0_ASI':final['static_prediction']['aki_jra_v21']['axes']['ASI'],
      'ZAI_WIN_rank':[{ 'runner_id':r,'value':vv[r]['ZAI_WIN']} for r in rank],
      'S0':{'tickets':public_tickets(ft['tickets']),'stake_yen':ft['total_investment'],'roles':deepcopy(roles),
            'pairs':deepcopy(final['pair_dispositions']),'thirds':deepcopy(final['third_dispositions'])},
      'S1':_portfolio(s1,10000),'S1_at_S0_actual_cap':_portfolio(s1,ft['total_investment']),
      'S1_roles':deepcopy(s1['static_prediction']['roles']),
      'S1_pairs':deepcopy(s1['pair_dispositions']),'S1_thirds':deepcopy(s1['third_dispositions']),
      'missing_registered_combinations':absent,'S1_KRS_receipt':None,
      'KRS_basis':'No new Engine; original S0 receipt never rebound to S1.',
      'rule_policy_sha256':fingerprint(root)}
 out['sha256']=digest(out)
 return out

def compare_result(record,official):
 """Unsigned analytical settlement; the Worker verifies signed RESULT first."""
 from jra_production_postresult import settle_final
 orders=official.get('top3_orders') or [official['top3']]
 winners={str(o[0]) for o in orders};rank=[r['runner_id'] for r in record['ZAI_WIN_rank']]
 out={}
 for arm in ('S0','S1','S1_at_S0_actual_cap'):
  spec=record[arm];roles=spec.get('roles') or record['S1_roles']
  pairs=spec.get('pairs') if arm=='S0' else record['S1_pairs']
  thirds=spec.get('thirds') if arm=='S0' else record['S1_thirds']
  columns={c:{r for r,cols in roles.items() if c in cols} for c in ('W','P2','P3')}
  fake={'final_ticket':{'tickets':spec['tickets'],'total_investment':spec['stake_yen'],'no_bet':not spec['stake_yen']},'capital_policy_decision':{'decision':'EXECUTE_FULL_MEC'}}
  complete=arm=='S0' or spec.get('status') in {'SHADOW_TICKETS','SHADOW_NO_BET'}
  settlement=(settle_final(fake,official) if complete else {
    'status':'NOT_FORMED_NOT_FORMAL_NO_BET','total_investment':0,'effective_investment':0,
    'total_payout':None,'refund':0,'profit_loss':None,'pfs':None,'winning_tickets':[]})
  winning={t['bet_type'] for t in settlement['winning_tickets']}
  out[arm]={'settlement':settlement,'financially_comparable':complete,
   'portfolio_state':spec.get('status','FROZEN_PRODUCTION_TICKETS'),
   'WinnerRank':min(rank.index(w)+1 for w in winners),
   'W_hit':bool(winners&columns['W']),
   'P2_hit':any(str(o[1]) in columns['P2'] for o in orders),
   'P3_hit':any(str(o[2]) in columns['P3'] for o in orders),
   'Ordered_Pair':any(p['status']=='PURCHASE' and any([int(p['head']),int(p['second'])]==o[:2] for o in orders) for p in pairs),
   'Exact':any(t['status']=='PURCHASE' and any([int(t['head']),int(t['second']),int(t['third'])]==o for o in orders) for t in thirds),
   'candidate_width':{c:len(s) for c,s in columns.items()},'ticket_count':len(spec['tickets']),
   'bet_coverage':bool(winning),'hit_but_loss':complete and bool(winning) and settlement['profit_loss']<0,
   'profitable':complete and settlement['profit_loss']>0,
   'no_bet':spec.get('status')=='SHADOW_NO_BET','not_formed':not complete,
   'EXACTA_hit':'EXACTA' in winning,'TRIO_hit':'TRIO' in winning,'TRIFECTA_hit':'TRIFECTA' in winning}
 out['added_W_winner_rescue']=not out['S0']['W_hit'] and out['S1']['W_hit']
 out['added_W_connected_winner_rescue']=out['added_W_winner_rescue'] and any(
  p['head']==record['added_W'] and p['status'] in {'PURCHASE','PROTECT'} for p in record['S1_pairs'])
 out['false_W_addition']=record['added_W'] is not None and record['added_W'] not in winners
 out['investment_change_yen']=record['S1']['stake_yen']-record['S0']['stake_yen']
 out['lost_existing_hit']=out['S0']['bet_coverage'] and not out['S1']['bet_coverage']
 return out

def scorecard(evaluations):
 rows=sorted(evaluations,key=lambda r:(r['scheduled_post_at_original'],r['race_id']))
 if len({r['race_id'] for r in rows})!=len(rows):raise ValueError('DUPLICATE_SHADOW_RACE')
 out={'eligible_races':len(rows),'judgement_before_30':'NOT_ALLOWED','automatic_promotion':False,'fixed_BVI_D_credit':0}
 matched=[r for r in rows if all(r['comparison'][a]['financially_comparable'] for a in ('S0','S1'))]
 out['financially_matched_races']=len(matched)
 out['S1_not_formed_races']=len(rows)-len(matched)
 out['metric_population']='ALL_ELIGIBLE_RACES'
 out['financial_population']='MATCHED_COMPLETE_S0_S1_ONLY'
 def tally(arm,cohort):
  values=[r['comparison'][arm] for r in rows]
  matched_values=[r['comparison'][arm] for r in cohort]
  settlements=[r['comparison'][arm]['settlement'] for r in cohort]
  stake=sum(s['effective_investment'] for s in settlements);payout=sum(s['total_payout'] for s in settlements)
  cumulative=peak=drawdown=0
  for s in settlements:
   cumulative+=s['profit_loss'];peak=max(peak,cumulative);drawdown=max(drawdown,peak-cumulative)
  return {'investment_yen':sum(s['total_investment'] for s in settlements),'effective_investment_yen':stake,
   'payout_yen':payout,'PFS':100*payout/stake if stake else None,'max_drawdown_yen':drawdown,
   'largest_payout_dependency':max((s['total_payout'] for s in settlements),default=0)/payout if payout else None,
   'financial_ticket_count':sum(r['comparison'][arm]['ticket_count'] for r in cohort),
   **{k:sum(x[k] for x in matched_values) for k in ('ticket_count','bet_coverage','hit_but_loss','profitable','no_bet')},
   'all_eligible_diagnostics':{k:sum(x[k] for x in values) for k in ('W_hit','P2_hit','P3_hit','Ordered_Pair','Exact','not_formed')},
   'W_hit_rate_all_eligible':sum(x['W_hit'] for x in values)/len(values) if values else None,
   'NO_BET_rate_matched':sum(x['no_bet'] for x in matched_values)/len(cohort) if cohort else None,
   'black_race_rate_matched':sum(x['profitable'] for x in matched_values)/len(cohort) if cohort else None}
 for arm in ('S0','S1'):out[arm]=tally(arm,matched)
 same_stake=[r for r in rows if all(r['comparison'][a]['financially_comparable'] for a in ('S0','S1_at_S0_actual_cap'))]
 out['same_actual_investment_cap']={'financially_matched_races':len(same_stake),
   'S0':tally('S0',same_stake),'S1':tally('S1_at_S0_actual_cap',same_stake)}
 out['ASI_strata']={}
 for label,predicate in [('75_OR_MORE',lambda x:x>=75),('LESS_THAN_75',lambda x:x<75)]:
  group=[r for r in rows if r.get('S0_ASI') is not None and predicate(r['S0_ASI'])]
  out['ASI_strata'][label]={'races':len(group),'S0_W_hit':sum(r['comparison']['S0']['W_hit'] for r in group),
                          'S1_W_hit':sum(r['comparison']['S1']['W_hit'] for r in group)}
 return out
