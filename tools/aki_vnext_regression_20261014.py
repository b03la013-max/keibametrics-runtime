"""Reuse saved signed inputs and existing selector/settlement/measurements.
New arms are post-event regression, never edits to original OOS.
"""
import json, sys, gzip, hashlib, copy, argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
from aki_adaptive_oos_tracker import scan_execution_store
from local_fullnumerical_production import materialize_production
from local_aki_columns import build,decision,verify,sha
from mec_r4_shadow import settle_ticket_list
from family_conversion_diagnostics import measure_capital_conversion
from pfs_grand_review import _aggregate,_robustness,capital_arms
parser=argparse.ArgumentParser()
parser.add_argument('--candidate-mode',choices=['HEAD_LOCAL_VNEXT_R1','HEAD_LOCAL_VNEXT_R2'],default='HEAD_LOCAL_VNEXT_R1')
parser.add_argument('--out',default='research/aki_vnext_20261014')
args=parser.parse_args()
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
tracker=scan_execution_store(ROOT/'runtime/executions');assert tracker['eligible_races']==17 and not tracker['errors']
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
 for x in selected['conditional_audit']['excluded_pairs']:
  x['removed_capital']=sum(t['stake'] for t in a if t['bet_type']!='TRIO' and [str(v) for v in t['selection'][:2]]==[str(x['head']),str(x['second'])])
 rows.append({'race_id':rid,'date':old['race_day'],'venue':'KAW' if '-KAW-' in rid else 'OHI','top3':top,'conditional_capture':{'head_local_pair':any((str(x['head']),str(x['second']))==tuple(map(str,top[:2])) for x in selected['pair_dispositions']), 'pair_conditioned_third':any((str(x['head']),str(x['second']),str(x['third']))==tuple(map(str,top)) for x in selected['third_dispositions'])}, 'selection':selected,'conversion_audit':d.get('conversion_audit'),'arms':arms,
  'distance':(req.get('race') or {}).get('distance'), 'column_capture':{c:str(top[i]) in selected['columns'][c]['selected'] for i,c in enumerate(['W','P2','P3'])}, 'candidate_policy_sha256':selected['policy_sha256'], 'candidate_selection_sha256':selected['sha256'], 'static_freeze_preserved':q['static_prediction']==req['static_prediction'], 'signed_final_time_A_B':f['receipt']['timestamp'], 'signed_final_time_C_D':None, 'capital_virtual_timestamp_not_candidate_final':True, 'source_sha256':source['source_snapshot_sha256'],'original_final_ref':f['receipt_sha256'],'original_result_ref':result['receipt_sha256'],
  'original_actual_krs_runs':load(fp.parent/'krs_receipt_envelope.json')['artifact']['actual_run_count'],
  'scope':'A/B_FROZEN_HISTORICAL_OOS; C/D/PR262_POST_EVENT_REGRESSION_ONLY','actual_purchase_pfs':None,'candidate_forward_oos_count':0})
 if args.candidate_mode=='HEAD_LOCAL_VNEXT_R2':
  rows[-1]['reference_selection']=old262
  rows[-1]['original_aki_shadow']=load(fp.parent/'aki_adaptive_purchase_shadow_pre_result.json')
def cohort(rr):
 out={}
 for name in ['A_PRODUCTION','B_ORIGINAL_AKI','PR262_REFERENCE','C_SELECTION','D_CAPITAL_ONLY']:
  valid=[r for r in rr if r.get('arms',{}).get(name,{}).get('status')=='SETTLED']
  rec=[{'race_id':r['race_id'],'date':r['date'],**r['arms'][name]} for r in valid]
  out[name]={'aggregate':_aggregate(rec),'robustness':_robustness(rec),'eligible':len(rec),'holds':len(rr)-len(rec),
   'full_loss_count':sum(x['return']==0 and x['investment']>0 for x in rec),
   'capture':{k:sum(x[k] for x in rec) for k in ['winner','pair','exact']},'ticket_count':sum(x['ticket_count'] for x in rec)}
 return out
report={'candidate_mode':args.candidate_mode,'selector_file_sha256':hashlib.sha256((ROOT/'runtime/local_aki_columns.py').read_bytes()).hexdigest(),'status':'CANDIDATE / HISTORICAL_REGRESSION','rows':rows,'original17_and_replay':cohort(rows),
 'kaw13_eight':cohort([r for r in rows if r.get('date')=='2026-10-13' and r.get('venue')=='KAW']),
 'candidate_forward_oos':0,'venue_distance':{venue:{str(distance):cohort([r for r in rows if r.get('venue')==venue and r.get('distance')==distance]) for distance in sorted({r.get('distance') for r in rows if r.get('venue')==venue},key=str)} for venue in ['KAW','OHI']},'capital_D':'EXISTING_WIDE_INTEGER_EQUAL_SPEND_ABLATION / NO_EV / NOT_OPTIMALITY_CLAIM',
 'economic_price_gate':'HOLD / NO_PRESTART_TICKET_PRICE_PANEL','equal_ticket':'PENDING_LEGAL_PREDEFINED_MATCHED_ARM / NO_PROPORTIONAL_RESCALE',
 'production_effect':'NONE','no_bet_opportunity_cost':'RESULT_ONLY_COMPARISON / NOT_CAUSAL_OR_FORWARD'}
raw=json.dumps(report,ensure_ascii=False,indent=2).encode();(OUT/'full_report.json.gz').write_bytes(gzip.compress(raw,mtime=0))
summary={k:v for k,v in report.items() if k!='rows'};summary['rows']=[{k:r[k] for k in ['race_id','date','venue','distance','top3','conditional_capture','column_capture','candidate_policy_sha256','candidate_selection_sha256','static_freeze_preserved','signed_final_time_A_B','signed_final_time_C_D','capital_virtual_timestamp_not_candidate_final','source_sha256','original_final_ref','original_result_ref'] if k in r} | {'status':r.get('status','VERIFIED_REGRESSION'),'arms':{n:{k:v for k,v in a.items() if k not in ['tickets','measurement']} for n,a in r.get('arms',{}).items()}} for r in rows]
summary['full_json_sha256']=hashlib.sha256(raw).hexdigest();summary['full_gzip_sha256']=hashlib.sha256((OUT/'full_report.json.gz').read_bytes()).hexdigest();(OUT/'report.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print('VERIFIED_17_ORIGINAL_AND_RETROSPECTIVE_ARMS; FORWARD_C_D=0')

if args.candidate_mode=='HEAD_LOCAL_VNEXT_R2':
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
