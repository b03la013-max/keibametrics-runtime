"""Reuse saved signed inputs and existing selector/settlement/measurements.
New arms are post-event regression, never edits to original OOS.
"""
import json, sys, gzip, hashlib, copy, argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'runtime'))
from aki_adaptive_oos_tracker import scan_execution_store
from local_fullnumerical_production import materialize_production
from local_aki_columns import build,decision,verify,sha
from mec_r4_shadow import settle_ticket_list
from family_conversion_diagnostics import measure_capital_conversion
from pfs_grand_review import _aggregate,_robustness,capital_arms
parser=argparse.ArgumentParser()
parser.add_argument('--candidate-mode',choices=['HEAD_LOCAL_VNEXT_R1','HEAD_LOCAL_VNEXT_R2'],default='HEAD_LOCAL_VNEXT_R1')
parser.add_argument('--out',default='research/aki_vnext_20261014')
parser.add_argument('--cohort22',action='store_true',help='Separate recovered 22-race historical cohort; never overwrite frozen17')
parser.add_argument('--residual-audit',action='store_true',help='Audit all four frozen/replay selections; no new policy or Forward registration')
parser.add_argument('--verify-external',action='store_true',help='Reverify original 17 SOURCE/PRE_KRS/KRS/FINAL/RESULT on the current canonical Runtime')
args=parser.parse_args()
if args.cohort22 and (not args.residual_audit or not args.out.startswith('research/aki_market_20261015/')):
 parser.error('COHORT22_REQUIRES_SEPARATE_MARKET_RESEARCH_OUTPUT')
if args.residual_audit and args.out in {'research/aki_vnext_20261014','research/aki_winner_repair_20261014'}:
 parser.error('RESIDUAL_AUDIT_REQUIRES_SEPARATE_OUTPUT; historical observations immutable')
if args.candidate_mode!='HEAD_LOCAL_VNEXT_R1' and args.out=='research/aki_vnext_20261014':
 parser.error('NEW_ARM_REQUIRES_SEPARATE_OUTPUT; original observations immutable')
OUT=ROOT/args.out;OUT.mkdir(parents=True,exist_ok=True)
def load(p):return json.loads(p.read_text())
def capture(tickets,top):
 pair={tuple(t['selection'][:2]) for t in tickets if t['bet_type'] in {'EXACTA','TRIFECTA'}}
 exact={tuple(t['selection']) for t in tickets if t['bet_type']=='TRIFECTA'}
 return {'winner':any(t['selection'][0]==top[0] for t in tickets if t['bet_type']!='TRIO'),
         'pair':tuple(top[:2]) in pair,'exact':tuple(top) in exact,
         'pair_count':len(pair),'exact_count':len(exact),
         'nonwinning_tickets':sum(not ((t['selection']==top[:2]) if t['bet_type']=='EXACTA' else sorted(t['selection'])==sorted(top) if t['bet_type']=='TRIO' else t['selection']==top) for t in tickets)}
tracker=scan_execution_store(ROOT/'runtime/executions');assert tracker['eligible_races']==(22 if args.cohort22 else 17) and not tracker['errors']
rows=[]
for old in tracker['settled_rows']:
 rid=old['race_id'];folder=ROOT/'runtime/executions'/rid
 fp=next((folder/'FORMAL').rglob('final_receipt_envelope.json'));rp=next((folder/'RESULT').rglob('result_receipt_envelope.json'));f=load(fp);result=load(rp)
 intent_path=ROOT/'runtime/formal_intents'/f'{rid}.json'
 if not intent_path.exists():
  rows.append({'race_id':rid,'status':'BLOCKED','reason':'ORIGINAL_INTENT_MISSING'});continue
 req=load(intent_path);source=load(fp.parent/'source_receipt_envelope.json')['artifact'];req['source_snapshot_sha256']=source['source_snapshot_sha256']
 q=materialize_production(source,req,req['required_indices']);old262=build(q,source);old262d=decision(q,old262)
 q['aki_column_candidate']=args.candidate_mode;selected=build(q,source);assert verify(q,source,selected)['status']=='PASS';d=decision(q,selected)
 top=result['artifact']['automatic_post_result_review']['official_top3'];official=result['artifact']['official_result'];facts={'official_result':{**official,'top3':top}}
 a=f['artifact']['final_ticket']['tickets'];b=load(fp.parent/'aki_adaptive_purchase_shadow_pre_result.json')['candidate_tickets']
 c=d['paper_tickets'] if selected['status']!='NO_BET' else []
 # Existing WIDE arm changes stakes alone. No ticket added/removed; equal
 # actual spend to the saved baseline, with integer 100-yen allocation.
 freeze=f['artifact']['final_freeze_timestamp'];budget=sum(t['stake'] for t in a)
 hypothetical={'final_freeze_timestamp':freeze,'final_ticket':{'tickets':c}}
 capital=capital_arms(hypothetical,budget,request=q,generated_at=freeze,scheduled_post_at=req['scheduled_post_at'])
 wide=capital['arms']['WIDE'];dt=wide.get('tickets');arms={}
 for name,tickets in [('A_PRODUCTION',a),('B_ORIGINAL_AKI',b),('PR262_REFERENCE',old262d['paper_tickets']),('C_SELECTION',c),('D_CAPITAL_ONLY',dt)]:
  if tickets is None:arms[name]={'status':'HOLD','reason':wide.get('reason')};continue
  settlement=settle_ticket_list(tickets,facts);settlement['hit_but_loss']=settlement['return']>0 and settlement['profit_loss']<0;settlement.update(capture(tickets,top));settlement['tickets']=tickets;settlement['ticket_count']=len(tickets)
  settlement['measurement']=measure_capital_conversion(req,f['artifact']['final_ticket'],f['artifact']['final_prediction_package'],f['artifact']['final_prediction_package']['krs_prediction_utility_shadow'],candidate_tickets=tickets)
  arms[name]=settlement
 capital_pair_losses=copy.deepcopy(selected['conditional_audit']['excluded_pairs'])
 for x in capital_pair_losses:
  x['removed_capital']=sum(t['stake'] for t in a if t['bet_type']!='TRIO' and [str(v) for v in t['selection'][:2]]==[str(x['head']),str(x['second'])])
 rows.append({'race_id':rid,'date':old['race_day'],'venue':'KAW' if '-KAW-' in rid else 'OHI','top3':top,'conditional_capture':{'head_local_pair':any((str(x['head']),str(x['second']))==tuple(map(str,top[:2])) for x in selected['pair_dispositions']), 'pair_conditioned_third':any((str(x['head']),str(x['second']),str(x['third']))==tuple(map(str,top)) for x in selected['third_dispositions'])}, 'selection':selected,'conversion_audit':d.get('conversion_audit'),'arms':arms,
  'distance':(req.get('race') or {}).get('distance'), 'column_capture':{c:str(top[i]) in selected['columns'][c]['selected'] for i,c in enumerate(['W','P2','P3'])}, 'candidate_policy_sha256':selected['policy_sha256'], 'candidate_selection_sha256':selected['sha256'], 'static_freeze_preserved':q['static_prediction']==req['static_prediction'], 'signed_final_time_A_B':f['receipt']['timestamp'], 'signed_final_time_C_D':None, 'capital_virtual_timestamp_not_candidate_final':True, 'source_sha256':source['source_snapshot_sha256'],'original_final_ref':f['receipt_sha256'],'original_result_ref':result['receipt_sha256'],
  'original_actual_krs_runs':load(fp.parent/'krs_receipt_envelope.json')['artifact']['actual_run_count'],
  'scope':'A/B_FROZEN_HISTORICAL_OOS; C/D/PR262_POST_EVENT_REGRESSION_ONLY','actual_purchase_pfs':None,'candidate_forward_oos_count':0})
 if args.candidate_mode=='HEAD_LOCAL_VNEXT_R2':
  rows[-1]['reference_selection']=old262
  rows[-1]['original_aki_shadow']=load(fp.parent/'aki_adaptive_purchase_shadow_pre_result.json')
 rows[-1]['post_result_capital_pair_losses']=capital_pair_losses
def cohort(rr):
 out={}
 for name in ['A_PRODUCTION','B_ORIGINAL_AKI','PR262_REFERENCE','C_SELECTION','D_CAPITAL_ONLY']:
  valid=[r for r in rr if r.get('arms',{}).get(name,{}).get('status')=='SETTLED']
  rec=[{'race_id':r['race_id'],'date':r['date'],**r['arms'][name]} for r in valid]
  out[name]={'aggregate':_aggregate(rec),'robustness':_robustness(rec),'eligible':len(rec),'holds':len(rr)-len(rec),
   'full_loss_count':sum(x['return']==0 and x['investment']>0 for x in rec),
   'capture':{k:sum(x[k] for x in rec) for k in ['winner','pair','exact']},'ticket_count':sum(x['ticket_count'] for x in rec)}
 return out
report={'candidate_mode':args.candidate_mode,'selector_file_sha256':hashlib.sha256((ROOT/'runtime/local_aki_columns.py').read_bytes()).hexdigest(),'status':'CANDIDATE / HISTORICAL_REGRESSION','rows':rows,('recovered22_and_replay' if args.cohort22 else 'original17_and_replay'):cohort(rows),
 'kaw13_eight':cohort([r for r in rows if r.get('date')=='2026-10-13' and r.get('venue')=='KAW']),
 'candidate_forward_oos':0,'venue_distance':{venue:{str(distance):cohort([r for r in rows if r.get('venue')==venue and r.get('distance')==distance]) for distance in sorted({r.get('distance') for r in rows if r.get('venue')==venue},key=str)} for venue in ['KAW','OHI']},'capital_D':'EXISTING_WIDE_INTEGER_EQUAL_SPEND_ABLATION / NO_EV / NOT_OPTIMALITY_CLAIM',
 'economic_price_gate':'HOLD / NO_PRESTART_TICKET_PRICE_PANEL','equal_ticket':'PENDING_LEGAL_PREDEFINED_MATCHED_ARM / NO_PROPORTIONAL_RESCALE',
 'production_effect':'NONE','no_bet_opportunity_cost':'RESULT_ONLY_COMPARISON / NOT_CAUSAL_OR_FORWARD'}
raw=json.dumps(report,ensure_ascii=False,indent=2).encode();(OUT/'full_report.json.gz').write_bytes(gzip.compress(raw,mtime=0))
summary={k:v for k,v in report.items() if k!='rows'};summary['rows']=[{k:r[k] for k in ['race_id','date','venue','distance','top3','conditional_capture','column_capture','candidate_policy_sha256','candidate_selection_sha256','static_freeze_preserved','signed_final_time_A_B','signed_final_time_C_D','capital_virtual_timestamp_not_candidate_final','source_sha256','original_final_ref','original_result_ref'] if k in r} | {'status':r.get('status','VERIFIED_REGRESSION'),'arms':{n:{k:v for k,v in a.items() if k not in ['tickets','measurement']} for n,a in r.get('arms',{}).items()}} for r in rows]
summary['full_json_sha256']=hashlib.sha256(raw).hexdigest();summary['full_gzip_sha256']=hashlib.sha256((OUT/'full_report.json.gz').read_bytes()).hexdigest();(OUT/'report.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print('VERIFIED_HISTORICAL_COHORT_'+str(len(rows))+'; FORWARD_C_D=0')

if args.candidate_mode=='HEAD_LOCAL_VNEXT_R2' and not args.cohort22:
 # Keep original R1 observations immutable; compare the new replay separately.
 previous_path=ROOT/'research/aki_vnext_20261014/full_report.json.gz'
 previous=json.loads(gzip.decompress(previous_path.read_bytes()))
 previous_rows={r['race_id']:r for r in previous['rows']}
 comparisons=[]
 for row in rows:
  old=previous_rows[row['race_id']]
  assert row['source_sha256']==old['source_sha256']
  for arm in ['A_PRODUCTION','B_ORIGINAL_AKI','PR262_REFERENCE']:
   for key in ['investment','return','ticket_count','winner','pair','exact']:
    assert row['arms'][arm][key]==old['arms'][arm][key]
  key=lambda t:(t['bet_type'],tuple(t['selection']))
  before={key(t):t for t in old['arms']['C_SELECTION']['tickets']}
  after={key(t):t for t in row['arms']['C_SELECTION']['tickets']}
  comparisons.append({'race_id':row['race_id'],'source_sha256':row['source_sha256'],
   'top3_post_result_observation':row['top3'],
   'original_aki_shadow':row['original_aki_shadow'],
   'PR262_reference_selection':row['reference_selection'],
   'R1_W':old['selection']['columns']['W'],'R2_W':row['selection']['columns']['W'],
   'R1_W_diagnostic':old['selection']['column_diagnostics']['W'],
   'R2_W_diagnostic':row['selection']['column_diagnostics']['W'],
   'runner_axes':row['selection']['runner_axes'],
   'eligible_role_scores':row['selection']['eligible_role_scores'],
   'static_freeze':load(ROOT/'runtime/formal_intents'/f"{row['race_id']}.json")['static_prediction'],
   'R2_conditional_audit':row['selection']['conditional_audit'],
   'added_tickets':[after[k] for k in after.keys()-before.keys()],
   'removed_tickets':[before[k] for k in before.keys()-after.keys()],
   'additional_capital':row['arms']['C_SELECTION']['investment']-old['arms']['C_SELECTION']['investment'],
   'additional_nonwinning_tickets':row['arms']['C_SELECTION']['nonwinning_tickets']-old['arms']['C_SELECTION']['nonwinning_tickets'],
   'arms':{**{name:{k:v for k,v in a.items() if k not in ['tickets','measurement']} for name,a in row['arms'].items()},
           'PR265_C_R1':{k:v for k,v in old['arms']['C_SELECTION'].items() if k not in ['tickets','measurement']}}})
 comparison={'status':'VERIFIED_HISTORICAL_REGRESSION / PERFORMANCE_ACCEPTANCE_FAILED',
  'prior_observation_gzip_sha256':hashlib.sha256(previous_path.read_bytes()).hexdigest(),
  'new_arm':'HEAD_LOCAL_VNEXT_R2','old_R1_aggregate':previous['original17_and_replay'],
  'new_R2_aggregate':report['original17_and_replay'],'rows':comparisons,
  'forward_admission':'REJECTED','new_preregistered_arms':0,'genuine_forward_count':0,
  'rejection_reasons':['KAW_R06_ORIGINAL_EXACT_SUCCESS_NOT_RETAINED','KAW_R07_SUCCESS_RETAINED_WITH_LARGER_CAPITAL','KAW_R09_WINNER_STILL_EXCLUDED','R2_PFS_LOWER_THAN_R1','R2_DRAWDOWN_HIGHER_THAN_R1'],
  'equal_budget':'EXISTING_WIDE_INTEGER_ALLOCATION_POST_EVENT_ONLY',
  'equal_ticket':'PENDING_NO_FROZEN_MATCHED_POLICY; NO_SYNTHETIC_SCALING',
  'no_bet_opportunity_cost':'ALL_17_BET; NO_ABSTENTION_COUNTERFACTUAL_POLICY',
  'next_step':'Resolve residual P2/model-choice evidence before any new forward admission; retain original AKI comparator.'}
 (OUT/'comparison.json.gz').write_bytes(gzip.compress((json.dumps(comparison,ensure_ascii=False,indent=2)+'\n').encode(),mtime=0))

if args.residual_audit:
 if args.candidate_mode!='HEAD_LOCAL_VNEXT_R2':
  raise ValueError('RESIDUAL_AUDIT_REQUIRES_R2_COMPARISON_NOT_FORWARD_ADMISSION')
 previous=json.loads(gzip.decompress((ROOT/'research/aki_vnext_20261014/full_report.json.gz').read_bytes()))
 if args.cohort22:
  for row in rows:
   if any(x['race_id']==row['race_id'] for x in previous['rows']):continue
   folder=ROOT/'runtime/executions'/row['race_id'];fp=next((folder/'FORMAL').rglob('final_receipt_envelope.json'))
   req=load(ROOT/'runtime/formal_intents'/f"{row['race_id']}.json");source=load(fp.with_name('source_receipt_envelope.json'))['artifact']
   req['source_snapshot_sha256']=source['source_snapshot_sha256'];q=materialize_production(source,req,req['required_indices']);q['aki_column_candidate']='HEAD_LOCAL_VNEXT_R1'
   selection=build(q,source);tickets=decision(q,selection)['paper_tickets'];result=load(next((folder/'RESULT').rglob('result_receipt_envelope.json')))
   facts={'official_result':{**result['artifact']['official_result'],'top3':row['top3']}}
   settled=settle_ticket_list(tickets,facts);settled.update(capture(tickets,row['top3']),tickets=tickets,ticket_count=len(tickets),hit_but_loss=settled['return']>0 and settled['profit_loss']<0)
   f=load(fp)['artifact'];settled['measurement']=measure_capital_conversion(req,f['final_ticket'],f['final_prediction_package'],{},candidate_tickets=tickets)
   previous['rows'].append({'race_id':row['race_id'],'selection':selection,'arms':{'C_SELECTION':settled}})
 old_rows={r['race_id']:r for r in previous['rows']}
 def failure(req, selected, tickets, top, arm):
  h,s,t=map(str,top)
  role_ids={c:{str(x['runner_id']) for x in req['role_registry'] if x['column']==c}
            for c in ['W','P2','P3']}
  upstream={c:v in role_ids[c] for c,v in zip(['W','P2','P3'],[h,s,t])}
  pair=next((x for x in req['pair_dispositions'] if (str(x['head']),str(x['second']))==(h,s)),None)
  third=next((x for x in req['third_dispositions'] if (str(x['head']),str(x['second']),str(x['third']))==(h,s,t)),None)
  if arm=='ORIGINAL_AKI':
   columns=selected['selected_role_columns'];pairs=selected['pair_local_columns']['seconds_by_head']
   thirds=selected['pair_local_columns']['thirds_by_pair']
   local_pair=s in {str(x) for x in pairs.get(h,[])}
   local_third=t in {str(x) for x in thirds.get(h+'>'+s,[])}
  else:
   columns={c:x['selected'] for c,x in selected['columns'].items()}
   local_pair=any((str(x['head']),str(x['second']))==(h,s) for x in selected['pair_dispositions'])
   local_third=any((str(x['head']),str(x['second']),str(x['third']))==(h,s,t) for x in selected['third_dispositions'])
  selected_third=(next((x for x in selected.get('third_dispositions',[]) if
      (str(x['head']),str(x['second']),str(x['third']))==(h,s,t)),None) if arm!='ORIGINAL_AKI' else None)
  column={c:v in {str(x) for x in columns.get(c,[])} for c,v in zip(['W','P2','P3'],[h,s,t])}
  purchased=capture(tickets,top)
  if not upstream['W']:first='PREDICTION_WINNER_ROLE_MISSING'
  elif not column['W']:first='AKI_WINNER_SELECTION_LOSS'
  elif not upstream['P2']:first='PREDICTION_P2_ROLE_MISSING'
  elif not pair or pair.get('status') not in {'PURCHASE','PROTECT'}:first='UPSTREAM_ORDERED_PAIR_NOT_MATERIAL'
  elif not local_pair:first='HEAD_LOCAL_P2_SELECTION_LOSS'
  elif not upstream['P3']:first='PREDICTION_P3_ROLE_MISSING'
  elif not local_third:first='PAIR_CONDITIONED_THIRD_SELECTION_LOSS'
  elif not purchased['exact'] and third and third.get('status')=='PURCHASE' and selected_third and selected_third.get('status')!='PURCHASE':first='EXACT_ORIENTATION_DOWNGRADED_BY_SELECTOR'
  elif not purchased['exact'] and third and third.get('status')=='PROTECT':first='PROTECT_NOT_EXACT_ORIENTED'
  elif not purchased['pair'] or not purchased['exact']:first='MEC_TICKET_CONVERSION_LOSS'
  else:first='CORRECT_ORDER_CAPTURED'
  return {'upstream_role_capture':upstream,'selected_column_capture':column,
          'selected_outside_upstream_role_universe':{c:sorted({str(x) for x in columns.get(c,[])}-role_ids[c],key=int) for c in ['W','P2','P3']},
          'head_local_pair_capture':local_pair,'pair_conditioned_third_capture':local_third,
          'ticket_capture':purchased,'first_material_selection_failure':first,
          'pre_result_pair_evidence':pair,'pre_result_third_evidence':third,
          'selected_third_disposition':selected_third,
          'no_result_input_to_selector':True,'market_price_authority':'HOLD_MISSING_PRESTART_TICKET_PRICE_PANEL',
          'false_addition_measurement':'NONWINNING_TICKETS_POST_RESULT_OBSERVATION_NOT_PROVEN_PRESTART_ERROR'}
 audited=[]
 for row in rows:
  rid=row['race_id'];req=load(ROOT/'runtime/formal_intents'/f'{rid}.json');old=old_rows[rid]
  arms={}
  for name,selected,tickets,settled in [
      ('ORIGINAL_AKI',row['original_aki_shadow'],row['arms']['B_ORIGINAL_AKI']['tickets'],row['arms']['B_ORIGINAL_AKI']),
      ('PR262_REFERENCE',row['reference_selection'],row['arms']['PR262_REFERENCE']['tickets'],row['arms']['PR262_REFERENCE']),
      ('PR265_R1',old['selection'],old['arms']['C_SELECTION']['tickets'],old['arms']['C_SELECTION']),
      ('PR265_R2',row['selection'],row['arms']['C_SELECTION']['tickets'],row['arms']['C_SELECTION'])]:
   arms[name]=failure(req,selected,tickets,row['top3'],name)
   arms[name]['economic_outcome']={k:settled[k] for k in ['investment','return','profit_loss','pfs','hit_but_loss','ticket_count','nonwinning_tickets']}
   arms[name]['dominant_loss_owner']=('CAPITAL_DILUTION' if settled['hit_but_loss'] else
       arms[name]['first_material_selection_failure'] if settled['return']==0 else 'NO_LOSS_OBSERVED')
   arms[name]['capital_exposure']=settled['measurement']
  audited.append({'race_id':rid,'source_sha256':row['source_sha256'],'static_prediction_sha256':sha(req['static_prediction']),
      'original_final_ref':row['original_final_ref'],'original_result_ref':row['original_result_ref'],
      'post_result_top3_observation':row['top3'],'date':row['date'],'venue':row['venue'],'distance':row['distance'],'race_class':(req.get('race') or {}).get('class','UNKNOWN'),
      'arms':arms,'scope':'FROZEN_HISTORICAL_OOS_A_B; REFERENCE_R1_R2_POST_EVENT_REPLAY',
      'actual_purchase_pfs':None,'forward_count_for_new_code':0})
 audit={'status':'VERIFIED_HISTORICAL_RESIDUAL_AUDIT','rows':audited,'genuine_forward_count':0,
        'new_selection_candidate':'NONE / EVIDENCE_INSUFFICIENT','R1_forward_admission':'REJECTED','R2_forward_admission':'REJECTED',
        'selector_code_sha256':hashlib.sha256((ROOT/'runtime/local_aki_columns.py').read_bytes()).hexdigest(),
        'required_new_evidence':['PRESTART_TICKET_PRICE_PANEL','INDEPENDENT_CONDITIONAL_STAGE_PATH_DISCRIMINATION',
          'SAME_SOURCE_PRODUCTION_AND_ORIGINAL_AKI_COMPARATORS','FROZEN_LEGAL_EQUAL_BUDGET_EQUAL_TICKET_POLICY'],
        'production_effect':'NONE'}
 # Reuse the existing outcome-independent integer matched comparator. These
 # are retrospective experimental controls, never modified historical FINALs
 # or a claim that randomly ranked subsets are economically optimal.
 from tools.local_aki_matched_comparison import portfolio,NAMESPACE
 matched={name:[] for name in ['equal_budget_full_coverage','equal_budget_equal_count']}
 budget_rows=[]
 for row in rows:
  old=old_rows[row['race_id']];top=row['top3']
  arms={'PRODUCTION':row['arms']['A_PRODUCTION']['tickets'],
        'ORIGINAL_AKI':row['arms']['B_ORIGINAL_AKI']['tickets'],
        'PR262_REFERENCE':row['arms']['PR262_REFERENCE']['tickets'],
        'PR265_R1':old['arms']['C_SELECTION']['tickets'],'PR265_R2':row['arms']['C_SELECTION']['tickets']}
  req=load(ROOT/'runtime/formal_intents'/f"{row['race_id']}.json")
  result=load(next((ROOT/'runtime/executions'/row['race_id']/'RESULT').rglob('result_receipt_envelope.json')))
  facts={'official_result':{**result['artifact']['official_result'],'top3':top}}
  identity=(req['venue_id'],row['date'],req['race_no'])
  for mode in matched:
   units=(max if mode=='equal_budget_full_coverage' else min)(len(t) for t in arms.values())
   if units<=0:
    matched[mode].append({'race_id':row['race_id'],'status':'HOLD_EMPTY_ARM'});continue
   observations={}
   for name,tickets in arms.items():
    controlled=portfolio(tickets,identity,units,count=units if mode=='equal_budget_equal_count' else None)
    settled=settle_ticket_list(controlled,facts);settled['hit_but_loss']=settled['return']>0 and settled['profit_loss']<0
    observations[name]={'tickets':controlled,'settlement':settled,
                        'capture':capture(controlled,top)}
   matched[mode].append({'race_id':row['race_id'],'date':row['date'],'budget':100*units,'arms':observations})
  scenarios=[]
  for name,selected in [('PR262_REFERENCE',row['reference_selection']),('PR265_R1',old['selection']),('PR265_R2',row['selection'])]:
   for budget in [0,2000,5000,10000]:
    scenario=copy.deepcopy(req);scenario['capital_policy']={'mode':'HARD_RACE_BUDGET','max_race_capital':budget,'insufficient_action':'NO_BET'}
    d=decision(scenario,selected);settled=settle_ticket_list(d['paper_tickets'],facts)
    baseline=settle_ticket_list(arms[name],facts)
    scenarios.append({'arm':name,'budget':budget,'authority':'EXPLICIT_PAPER_SCENARIO_NOT_USER_BUDGET',
                      'capital':d['capital'],'paper_tickets':d['paper_tickets'],'settlement':settled,
                      'foregone_return_post_result':baseline['return'] if not d['paper_tickets'] else 0,
                      'avoided_stake_post_result':baseline['investment'] if not d['paper_tickets'] else 0,
                      'no_price_or_probability_optimality_claim':True})
  budget_rows.append({'race_id':row['race_id'],'scenarios':scenarios})
 audit['matched_comparison']={'scope':'POST_EVENT_COUNTERFACTUAL_ONLY_NOT_SELECTION_POLICY_OR_FORWARD',
       'existing_namespace':NAMESPACE,'no_proportional_scaling':True,'modes':matched,'aggregate':{}}
 for mode,controlled in matched.items():
  audit['matched_comparison']['aggregate'][mode]={}
  for name in arms:
   rec=[{'race_id':r['race_id'],'date':r['date'],**r['arms'][name]['settlement']} for r in controlled if 'arms' in r]
   audit['matched_comparison']['aggregate'][mode][name]={'aggregate':_aggregate(rec),'robustness':_robustness(rec)}
 audit['capital_paper_budget_scenarios']=budget_rows
 audit['cohort_size']=len(audited)
 audit['failure_counts']={arm:{failure:sum(r['arms'][arm]['first_material_selection_failure']==failure for r in audited) for failure in sorted({r['arms'][arm]['first_material_selection_failure'] for r in audited})} for arm in audited[0]['arms']}
 audit['capture_counts']={arm:{k:sum(r['arms'][arm]['ticket_capture'][k] for r in audited) for k in ['winner','pair','exact']} for arm in audited[0]['arms']}
 summary_arms={}
 for arm in audited[0]['arms']:
  rr=[{'race_id':x['race_id'],'date':x['date'],**x['arms'][arm]['economic_outcome']} for x in audited]
  summary_arms[arm]={'aggregate':_aggregate(rr),'robustness':_robustness(rr),'capture':audit['capture_counts'][arm],
   'failure_counts':audit['failure_counts'][arm],
   'upstream_role_capture':{c:sum(x['arms'][arm]['upstream_role_capture'][c] for x in audited) for c in ['W','P2','P3']},
   'selected_column_capture':{c:sum(x['arms'][arm]['selected_column_capture'][c] for x in audited) for c in ['W','P2','P3']},
   'local_capture':{c:sum(x['arms'][arm][c] for x in audited) for c in ['head_local_pair_capture','pair_conditioned_third_capture']},
   'ticket_count':sum(x['ticket_count'] for x in rr),'full_loss':sum(x['return']==0 and x['investment']>0 for x in rr),
   'realized_nonwinning_tickets_not_proven_prestart_errors':sum(x['nonwinning_tickets'] for x in rr)}
 groups={dim:{key:{arm:_aggregate([{'race_id':x['race_id'],'date':x['date'],**x['arms'][arm]['economic_outcome']} for x in audited if str(x[dim])==key]) for arm in summary_arms} for key in sorted({str(x[dim]) for x in audited})} for dim in ['venue','distance','race_class']}
 summary={'cohort':'RECOVERED_22_FROZEN_HISTORICAL_A_B; REFERENCE_R1_R2_REPLAY' if args.cohort22 else 'FROZEN_17_HISTORICAL_A_B; REFERENCE_R1_R2_REPLAY',
  'arms':summary_arms,'production':cohort(rows)['A_PRODUCTION'],'groups':groups,'matched_aggregate':audit['matched_comparison']['aggregate'],
  'budget_scenarios':sum(len(x['scenarios']) for x in budget_rows),
  'no_bet_scenarios':sum(s['capital']['decision']=='NO_BET' for x in budget_rows for s in x['scenarios']),
  'capital_no_actual_bet_flag_is_not_paper_abstention':True,'new_candidate_count':0,'new_forward_count':0,'actual_purchase_pfs':None}
 (OUT/'failure_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 (OUT/'residual_audit.json.gz').write_bytes(gzip.compress(json.dumps(audit,ensure_ascii=False,indent=2).encode(),mtime=0))
 print('RESIDUAL_AUDIT_'+str(len(rows))+'; NEW_SELECTION_CANDIDATES=0; FORWARD=0')

if args.verify_external:
 if not args.residual_audit:raise ValueError('EXTERNAL_VERIFICATION_REQUIRES_SEPARATE_RESIDUAL_AUDIT_OUTPUT')
 import base64,datetime as dt,urllib.request
 from concurrent.futures import ThreadPoolExecutor
 from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
 endpoint=load(ROOT/'profiles/current_execution_gateway.json')['families']['LOCAL']['external_endpoint']
 anchor=load(ROOT/'evidence/local_aki_columns_20261012/destination_verification.json')['health']['receipt_public_key_b64']
 public=Ed25519PublicKey.from_public_bytes(base64.b64decode(anchor))
 def verify_envelope(job):
  rid,phase,path=job;e=load(path);rec=e['receipt'];raw=json.dumps(rec,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
  public.verify(base64.b64decode(e['signature']),raw)
  if hashlib.sha256(raw).hexdigest()!=e['receipt_sha256'] or sha(e['artifact'])!=rec['artifact_sha256']:
   raise ValueError('SIGNED_DIGEST_MISMATCH:'+rid+':'+phase)
  if rec['race_id']!=rid or rec['phase']!=phase:raise ValueError('SIGNED_IDENTITY_MISMATCH')
  raw_count=0
  if phase=='SOURCE':
   for source in e['artifact']['sources']:
    if source.get('raw_gzip_b64'):
     if hashlib.sha256(gzip.decompress(base64.b64decode(source['raw_gzip_b64']))).hexdigest()!=source['raw_sha256']:
      raise ValueError('OFFICIAL_RAW_HASH_MISMATCH')
     raw_count+=1
  request=urllib.request.Request(endpoint+'/verify',data=json.dumps(e,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(request,timeout=120) as response:result=json.load(response)
  if result.get('valid') is not True:raise ValueError('CURRENT_RUNTIME_VERIFY_FAILED:'+rid+':'+phase)
  return {'race_id':rid,'phase':phase,'receipt_ref':e['receipt_sha256'],'artifact_sha256':rec['artifact_sha256'],
          'offline_signature_verified':True,'official_raw_hash_count':raw_count,'live_verify':result,
          'observed_at':dt.datetime.now(dt.timezone.utc).isoformat()}
 jobs=[]
 for row in rows:
  rid=row['race_id'];formal=next((ROOT/'runtime/executions'/rid/'FORMAL').rglob('final_receipt_envelope.json')).parent
  for phase,name in [('SOURCE','source'),('PRE_KRS','pre_krs'),('KRS_RUN','krs'),('FINAL','final')]:
   jobs.append((rid,phase,formal/(name+'_receipt_envelope.json')))
  jobs.append((rid,'RESULT',next((ROOT/'runtime/executions'/rid/'RESULT').rglob('result_receipt_envelope.json'))))
 verified=[]
 try:
  with ThreadPoolExecutor(max_workers=4) as pool:
   for result in pool.map(verify_envelope,jobs):verified.append(result)
  result={'status':'PASS','verified_envelopes':len(verified),'rows':verified,'endpoint':endpoint,
          'public_trust_anchor_b64':anchor,'new_krs_runs':0,'old_original_krs_runs':sum(r['original_actual_krs_runs'] for r in rows),
          'new_forward_count':0}
 except Exception as error:
  result={'status':'BLOCKED_OR_PARTIAL','verified_envelopes':len(verified),'rows':verified,'error':str(error),'new_forward_count':0}
 (OUT/'current_external_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 if result['status']!='PASS':raise RuntimeError('EXTERNAL_VERIFICATION_PARTIAL:'+str(result['error']))
 print('LIVE_VERIFY_'+str(len(verified))+'_PASS; NEW_KRS=0_IN_VERIFICATION')
