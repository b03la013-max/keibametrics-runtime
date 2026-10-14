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
def market_probe(request_path, out_path):
    """Capture prices only; no candidate admission, prediction/KRS or bet."""
    from runtime.local_race_key_shadow_owner import market_source_manifest, bind_market_evidence
    q=load(Path(request_path));out=Path(out_path).resolve();out.mkdir(parents=True,exist_ok=True)
    if (out/'terminal.json').exists():
        # A cached terminal is not signature verification. Revalidate SOURCE
        # without reacquisition/KRS and preserve the original observation.
        from runtime.local_race_key_shadow_owner import _sha
        prior=load(out/'terminal.json');envelope=load(out/'source_receipt.json');binding=load(out/'market_binding.json')
        checked=verify((out/'source_receipt.json',envelope))
        if (checked.get('offline_signature') is not True or checked.get('external_verify',{}).get('valid') is not True
                or prior['source_ref']!=envelope['receipt_sha256']
                or binding['source_receipt_sha256']!=envelope['receipt_sha256']
                or binding['race_id']!=q['race_id'] or binding['ticket_sha256']!=_sha(q.get('paper_tickets',[]))
                or binding['selection_sha256']!=q.get('selection_sha256')
                or binding['prediction_cutoff']!=q['prediction_cutoff']
                or binding['runner_ids']!=sorted({str(x['runner_id']) for x in q['runners']},key=int)
                or _sha({k:v for k,v in binding.items() if k!='sha256'})!=prior['binding_sha256']):
            raise ValueError('MARKET_CACHED_SIGNATURE_OR_BINDING_INVALID')
        recompiled=bind_market_evidence(q,envelope,signatures_verified=True,tickets=q.get('paper_tickets',[]),
            frozen_at=binding['frozen_at'],selection_sha256=q.get('selection_sha256'))
        if recompiled['ticket_price_coverage']!=binding['ticket_price_coverage']:
            raise ValueError('MARKET_CACHED_PRICE_BINDING_MISMATCH')
        name=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        target=out/'revalidations';target.mkdir(exist_ok=True)
        (target/(name+'.json')).write_text(json.dumps({'status':'VERIFIED_CACHED_MARKET_SOURCE',
            'source_verification':checked,'binding_sha256':prior['binding_sha256'],
            'source_reacquisition':False,'new_krs_runs':0,'new_forward_count':0},indent=2)+'\n')
        print(json.dumps({'status':'VERIFIED_CACHED_MARKET_SOURCE','source_ref':prior['source_ref'],'new_forward_count':0}));return
    def save(name,obj):
        p=out/(name+'.json');encoded=json.dumps(obj,ensure_ascii=False,indent=2)+'\n'
        if p.exists() and p.read_text()!=encoded:raise ValueError('IMMUTABLE_MARKET_PROBE_CONFLICT:'+name)
        p.write_text(encoded);return obj
    manifest=save('manifest',market_source_manifest(q))
    endpoint=json.loads((ROOT/'profiles/current_execution_gateway.json').read_text())['families']['LOCAL']['external_endpoint']
    request=urllib.request.Request(endpoint+'/source/acquire',data=json.dumps(manifest).encode(),headers={'Content-Type':'application/json'})
    if (out/'source_receipt.json').exists():envelope=load(out/'source_receipt.json')
    else:
        with urllib.request.urlopen(request,timeout=180) as response:envelope=save('source_receipt',json.load(response))
    checked=save('source_verification',verify((out/'source_receipt.json',envelope)))
    if checked.get('offline_signature') is not True or checked.get('external_verify',{}).get('valid') is not True:
        raise ValueError('MARKET_SOURCE_VERIFY_FAILED')
    frozen=datetime.datetime.now(datetime.timezone.utc).isoformat()
    binding=bind_market_evidence(q,envelope,signatures_verified=True,tickets=q.get('paper_tickets',[]),
                                frozen_at=frozen,selection_sha256=q.get('selection_sha256'))
    save('market_binding',binding)
    save('terminal',{'status':'MARKET_OBSERVATION_ONLY','source_ref':envelope['receipt_sha256'],
        'binding_sha256':binding['sha256'],'market_payout_sufficiency':binding['market_payout_sufficiency'],
        'new_krs_runs':0,'new_candidate_count':0,'new_forward_count':0,'actual_purchase':False,
        'cutoff_authority':'EXPLICIT_OBSERVATION_CUTOFF_NOT_A_PREDICTION_OR_TICKET_FREEZE',
        'code_file_sha256':{p:__import__('hashlib').sha256((ROOT/p).read_bytes()).hexdigest() for p in
            ['runtime/local_race_key_shadow_owner.py','tools/local_kaw_candidate_comparison.py']}})
    print(json.dumps({'source_ref':envelope['receipt_sha256'],'panels':{k:v['status'] for k,v in binding['panels'].items()},'new_forward_count':0}))


if __name__=='__main__':
    if '--market-probe' in sys.argv:
        import argparse
        p=argparse.ArgumentParser();p.add_argument('--market-probe',required=True);p.add_argument('--market-out',required=True)
        a=p.parse_args();market_probe(a.market_probe,a.market_out)
    else:run('--external' in sys.argv)
