"""Post-event conversion replay of unchanged frozen numerical candidates."""
import sys,json,gzip,copy,datetime,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'runtime'))
from runtime.local_nar_evidence_candidate import compile_candidate_evidence
from runtime.local_evidence_routing_candidate_v03 import compile_candidate_evidence_v03
from runtime.local_fullnumerical_candidate import materialize_candidate
from runtime.local_krs_bridge_candidate import build_candidate_prediction
from runtime.local_race_key_shadow_owner import compile_candidate_portfolio
from runtime.mec_r4_shadow import settle_ticket_list
from runtime.jra_ticket_tree_renderer import render_ticket_tree
from tools.local_kaw_day_audit import load,sha,verify

def run(external=False):
 rows=[]
 for race_no in [4,5,11,12]:
  eid=f'KM-LOCAL-KAW-20261014-R{race_no:02d}-LIVE-R1';d=ROOT/'runtime/executions'/eid;fpath=next((d/'FORMAL').rglob('final_receipt_envelope.json'));src=load(fpath.with_name('source_receipt_envelope.json'));req=load(ROOT/'runtime/formal_intents'/f'{eid}.json');result=load(next((d/'RESULT').rglob('result_receipt_envelope.json')));top=result['artifact']['automatic_post_result_review']['official_top3'];facts={'official_result':{**result['artifact']['official_result'],'top3':top}}
  dual=load(fpath.with_name('candidate_numerical_dual_shadow_summary.json'));v3=load(fpath.with_name('candidate_numerical_v03_shadow_summary.json'))
  arms={}
  for version in ['v0.1','v0.2','v0.3']:
   if version=='v0.3':
    reg='mapping/local_evidence_feature_rule_registry_v0.3_candidate_20260925_evidence_routing.json';mapping='mapping/local_full_numerical_mapping_v0.3_candidate_20260925_evidence_routing.json';ce=compile_candidate_evidence_v03(src['artifact'],req,reg);q=materialize_candidate(ce,reg,mapping);frozen=v3['arm']
   else:
    ce=compile_candidate_evidence(src['artifact'],req)
    q=materialize_candidate(ce) if version=='v0.1' else materialize_candidate(ce,'mapping/local_evidence_feature_rule_registry_v0.2_candidate_20260923_urw_day_calibrated.json','mapping/local_full_numerical_mapping_v0.2_candidate_20260923_urw_day_calibrated.json');frozen=dual['arms'][version]
   q=build_candidate_prediction(q);pred=q['candidate_static_prediction']
   assert pred==frozen['candidate_static_prediction'],(eid,version,'FROZEN_PREDICTION_RECOMPUTATION_MISMATCH')
   portfolio=compile_candidate_portfolio(q,src['artifact'])
   stats={}
   for name,tickets in portfolio['variants'].items():
    s=settle_ticket_list(tickets,facts);s['ticket_count']=len(tickets)
    s['capture']={'winner':any(t['bet_type']!='TRIO' and t['selection'][0]==top[0] for t in tickets),'pair':any(t['bet_type'] in ['EXACTA','TRIFECTA'] and t['selection'][:2]==top[:2] for t in tickets),'exact':any(t['bet_type']=='TRIFECTA' and t['selection']==top for t in tickets),'trio':any(t['bet_type']=='TRIO' and sorted(t['selection'])==sorted(top) for t in tickets)}
    stats[name]=s
   budgets={}
   for budget in [2000,5000,10000]:
    cap=compile_candidate_portfolio(q,src['artifact'],budget=budget)
    budgets[str(budget)]={n:{'capital':c['capital'],'settlement':settle_ticket_list(c['tickets'],facts),'opportunity_cost_vs_unlimited_replay':stats[n]['profit_loss']} for n,c in cap['capital_variants'].items()}
   arms[version]={'portfolio':portfolio,'settlements':stats,'budget_scenarios':budgets,'frozen_prediction_reproduced':True,'prior_role_freeze_not_new_ticket_freeze':True}
  row={'race_id':eid,'top3_result_only':top,'source_ref':src['receipt_sha256'],'source_sha256':src['artifact']['source_snapshot_sha256'],'arms':arms,'temporal_class':'POST_EVENT_CONVERSION_REPLAY','genuine_forward_count':0,'actual_purchase_pfs':None,'production_changed':False}
  if external:
   # Bind the PAPER comparison to a new external signed artifact. Original
   # Production tickets and signatures remain in their original paths.
   original=load(fpath);payload={k:copy.deepcopy(v) for k,v in original['artifact'].items() if k in ['final_prediction_package','final_ticket','final_freeze_timestamp','minimum_efficient_coverage','capital_policy_decision','ticket_transport_trace','execution_stage_manifest']}
   payload.update(family_id='LOCAL',race_id=eid,source_receipt=src,krs_run_receipt=load(fpath.with_name('krs_receipt_envelope.json')),final_freeze_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat())
   payload['final_prediction_package']['temporal_mode']='REPLAY'
   payload['final_prediction_package']['post_event_candidate_portfolios']={'temporal_class':'POST_EVENT_CONVERSION_REPLAY','generated_at':payload['final_freeze_timestamp'],'code_binding_sha256':sha({'owner':(ROOT/'runtime/local_race_key_shadow_owner.py').read_text(),'graph':(ROOT/'runtime/local_production_static_owner.py').read_text(),'selector':(ROOT/'runtime/local_aki_columns.py').read_text()}),'portfolios':{k:v['portfolio'] for k,v in arms.items()},'production_authority':False,'new_forward_count':0,'actual_purchase':False}
   ext=ROOT/'evidence/kaw_day_20261014/external'/eid/payload['final_prediction_package']['post_event_candidate_portfolios']['code_binding_sha256'][:12];ext.mkdir(parents=True,exist_ok=True)
   reqx=urllib.request.Request('https://witnessstrictimage-production.up.railway.app/final',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
   with urllib.request.urlopen(reqx,timeout=120) as response:signed=json.load(response)
   (ext/'recon_final_receipt.json').write_text(json.dumps(signed,ensure_ascii=False,indent=2)+'\n')
   (ext/'recon_final_payload.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
   row['external_shadow_freeze']=verify((ext/'recon_final_receipt.json',signed));row['external_shadow_status']=signed.get('receipt',{}).get('status')
   if row['external_shadow_status']=='PASS':
    a=result['artifact'];rp={'family_id':'LOCAL','race_id':eid,'final_receipt':signed,'official_result':a['official_result'],'settlement':a['settlement'],'result_available_at':a['result_available_at'],'failure_localization':a.get('failure_localization',{}),'learning_event':{'temporal_class':'POST_EVENT_CONVERSION_REPLAY','candidate_settlements':{v:arm['settlements'] for v,arm in arms.items()},'production_change_authorized':False,'actual_purchase':False}}
    reqx=urllib.request.Request('https://witnessstrictimage-production.up.railway.app/result',data=json.dumps(rp).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(reqx,timeout=120) as response:rs=json.load(response)
    (ext/'recon_result_receipt.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2)+'\n')
    row['external_result_verify']=verify((ext/'recon_result_receipt.json',rs));row['external_result_status']=rs['receipt']['status']
   row['new_actual_krs_runs']=0;row['reused_krs_ref']=payload['krs_run_receipt']['receipt_sha256']
  rows.append(row)
 out=ROOT/'research/kaw_day_20261014';out.mkdir(exist_ok=True)
 (out/'candidate_comparison.json.gz').write_bytes(gzip.compress(json.dumps(rows,ensure_ascii=False,indent=2).encode(),mtime=0))
 summary=[{k:v for k,v in r.items() if k!='arms'}|{'arms':{v:{'settlements':a['settlements'],'width':a['portfolio']['variable_r5_width'],'portfolio_sha256':a['portfolio']['sha256']} for v,a in r['arms'].items()}} for r in rows]
 (out/'candidate_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':run('--external' in sys.argv)
