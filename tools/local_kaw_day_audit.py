"""Audit every scheduled race; saved signatures are not evidence of delivery."""
import argparse,base64,json,hashlib,sys,gzip,urllib.request,datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from mec_r4_shadow import settle_ticket_list
from jra_ticket_tree_renderer import render_ticket_tree
from local_fullnumerical_production import materialize_production

KEY=Ed25519PublicKey.from_public_bytes(base64.b64decode('jqWqOYlmhXXmpv/nR7lx3c2n/S5shDYava/WJVxn4kE='))
def load(p):return json.loads(p.read_text())
def sha(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def verify(item):
 path,e=item
 try:
  KEY.verify(base64.b64decode(e['signature']),json.dumps(e['receipt'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
  assert sha(e['artifact'])==e['receipt']['artifact_sha256']
  req=urllib.request.Request('https://witnessstrictimage-production.up.railway.app/verify',data=json.dumps(e).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=60) as response:r=json.load(response)
  assert r['valid'] is True
  return {'path':str(path.relative_to(ROOT)),'receipt_sha256':e['receipt_sha256'],'kind':e['receipt'].get('kind'),'timestamp':e['receipt'].get('timestamp'),'offline_signature':True,'external_verify':r,'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 except Exception as exc:return {'path':str(path.relative_to(ROOT)),'status':'HOLD','reason':str(exc)}

def audit():
 rows=[];receipts=[];performance=[]
 for number in range(1,13):
  dirs=sorted((ROOT/'runtime/executions').glob(f'*KAW-20261014-R{number:02d}*'))
  row={'race_no':number,'date':'2026-10-14','request_received_at':None,'request_time_authority':'CHAT_RECEIPT_NOT_AVAILABLE','user_received_at':None,'prestart_delivery_pass':False,'delivery_status':'UNPROVEN','actual_purchase_pfs':None}
  if not dirs:
   rows.append({**row,'status':'NO_SIGNED_EXECUTION_EVIDENCE','cause':'UNKNOWN; R06_CONNECTOR_REFUSAL_REPORTED_ISSUE268' if number==6 else 'UNKNOWN_REQUEST_OR_START; NOT_EXCLUDED_FROM_DENOMINATOR'});continue
  d=dirs[-1];row['execution_id']=d.name;phase_paths={}
  for phase in ['SOURCE','FORMAL','RESULT']:
   ptr=d/phase/'LATEST.json'
   if ptr.exists():
    pointer=load(ptr);folder=ROOT/'runtime/executions'/pointer['run_path'];phase_paths[phase]=folder
    row[phase]={'run_id':pointer['run_id'],'persisted_at':pointer['updated_at']}
    for label in ['source','pre_krs','krs','final','result']:
     p=folder/f'{label}_receipt_envelope.json'
     if p.exists():
      e=load(p);receipts.append((p,e));row[phase][label+'_ref']=e.get('receipt_sha256');row[phase][label+'_signed_at']=e.get('receipt',{}).get('timestamp')
  source=load(phase_paths['SOURCE']/'source_receipt_envelope.json');row['official_context']=source['artifact'].get('source_race_context');row['source_freeze']=source['artifact'].get('source_freeze_at')
  req_path=ROOT/'runtime/formal_intents'/f'{d.name}.json';req=load(req_path) if req_path.exists() else None
  row.update(status='SOURCE_ONLY',first_failed_stage='STATIC_OR_FORMAL_UNCONFIRMED',error_cause='INSUFFICIENT_LOGS',prestart_final_pass=False)
  reports=[load(p) for p in (ROOT/'runtime/execution_reports'/d.name).glob('*.json')]
  row['execution_reports']=reports
  if req:
   row.update(scheduled_post_at=req.get('scheduled_post_at'),prediction_cutoff=req.get('prediction_cutoff'),static_freeze=req.get('static_prediction_freeze_timestamp') or req.get('static_prediction',{}).get('frozen_at'))
   calc=materialize_production(source['artifact'],req,req['required_indices'])
   row['numerical']={'required_indices':len(calc['required_indices']),'runner_count':len(calc['runners']),'terminal_closure':sum(x.get('terminal_status') in ['CALCULATED','RULED-NEUTRAL'] for r in calc['runners'] for x in r['canonical_components'].values()),'calculated':sum(x.get('terminal_status')=='CALCULATED' for r in calc['runners'] for x in r['canonical_components'].values()),'strict_ready':calc.get('strict_full_numerical_ready'),'authority_distinction':'TERMINAL_CLOSURE_AND_NUMERICAL_CONFORMANCE != PREDICTION_CONSUMPTION_OR_OOS_VALUE'}
  if 'FORMAL' in phase_paths:
   fpath=phase_paths['FORMAL'];final=load(fpath/'final_receipt_envelope.json');krs=load(fpath/'krs_receipt_envelope.json');pre=load(fpath/'pre_krs_receipt_envelope.json');inp=load(fpath/'krs_input.json') if (fpath/'krs_input.json').exists() else None
   row['actual_krs_runs']=krs['artifact'].get('actual_run_count');row['krs_input_sha256']=krs['artifact'].get('input_sha256');row['krs_lineage_match']=pre['artifact'].get('input_sha256')==krs['artifact'].get('input_sha256') and (inp is None or sha(inp)==krs['artifact'].get('input_sha256'))
   temporal=load(fpath/'final_before_post_verification.json');row.update(status='SIGNED_FINAL',first_failed_stage=None,error_cause=None,prestart_final_pass=temporal.get('verified') is True,final_freeze=final['artifact']['final_freeze_timestamp'])
   tree=render_ticket_tree(final['artifact']);row['tree']={'roundtrip_verified':tree['canonical_roundtrip_verified'],'ticket_count':tree['ticket_count'],'investment':tree['total_investment'],'historical_delivery_proven':False}
   out=ROOT/'research/kaw_day_20261014/trees';out.mkdir(parents=True,exist_ok=True);(out/f'R{number:02d}.txt').write_text(tree['text']+'\n')
   if 'RESULT' in phase_paths:
    result=load(phase_paths['RESULT']/'result_receipt_envelope.json');rev=result['artifact']['automatic_post_result_review'];facts={'official_result':{**result['artifact']['official_result'],'top3':rev['official_top3']}};tickets=final['artifact']['final_ticket']['tickets'];settlement=settle_ticket_list(tickets,facts)
    assert settlement['investment']==rev['capital']['investment'] and settlement['return']==rev['capital']['return']
    row.update(status='RESULT_SETTLED',first_material_failure=rev['failure_localization']['first_material_failure'],recommendation_settlement=settlement,learning_present=bool(result['artifact'].get('automatic_next_race_learning_state')),result_final_lineage= result['artifact']['frozen_refs'].get('final_receipt_sha256')==final['receipt_sha256'])
    if number in [4,5,11,12]:
     arms={'PRODUCTION':{'tickets':tickets,'settlement':settlement,'authority':'FROZEN-RECOMMENDATION'}}
     ap=fpath/'aki_adaptive_purchase_shadow_pre_result.json'
     if ap.exists():
      a=load(ap);arms['ORIGINAL_AKI']={'tickets':a['candidate_tickets'],'settlement':settle_ticket_list(a['candidate_tickets'],facts),'frozen_sha256':a['sha256'],'temporal_class':a.get('temporal_class')}
     mp=fpath/'local_mec_r5_shadow_pre_result.json'
     if mp.exists():
      m=load(mp)
      for name,a in m['arms'].items():arms['MEC_R5_'+name]={'tickets':a['tickets'],'settlement':settle_ticket_list(a['tickets'],facts),'frozen_sha256':a['sha256']}
     top=rev['official_top3']
     for name,a in arms.items():
      ts=a['tickets'];a['capture']={'winner':any(t['bet_type']!='TRIO' and t['selection'][0]==top[0] for t in ts),'pair':any(t['bet_type'] in ['EXACTA','TRIFECTA'] and t['selection'][:2]==top[:2] for t in ts),'exact':any(t['bet_type']=='TRIFECTA' and t['selection']==top for t in ts),'trio':any(t['bet_type']=='TRIO' and sorted(t['selection'])==sorted(top) for t in ts)}
     performance.append({'race_no':number,'race_id':d.name,'official_top3':top,'final_ref':final['receipt_sha256'],'result_ref':result['receipt_sha256'],'first_material_failure':rev['failure_localization']['first_material_failure'],'krs_review':rev['krs'],'roles':final['artifact']['final_prediction_package']['roles'],'arms':arms,'actual_purchase':'UNKNOWN','new_candidate_forward_count':0})
  rows.append(row)
 with ThreadPoolExecutor(max_workers=4) as pool:checks=list(pool.map(verify,receipts))
 out={'all_scheduled_races':12,'rows':rows,'receipts':checks,'summary':{'signed_final_count':sum(r.get('prestart_final_pass',False) for r in rows),'result_count':sum(r['status']=='RESULT_SETTLED' for r in rows),'delivery_proven_count':0,'missing_execution_count':sum(r['status']=='NO_SIGNED_EXECUTION_EVIDENCE' for r in rows)},'production_effect':'NONE','new_genuine_forward_count':0}
 root=ROOT/'research/kaw_day_20261014';root.mkdir(exist_ok=True)
 (root/'execution_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');(root/'performance.json.gz').write_bytes(gzip.compress(json.dumps(performance,ensure_ascii=False,indent=2).encode(),mtime=0))
 print(json.dumps(out['summary']));print('External receipt verification',len(checks),sum(x.get('offline_signature') is True for x in checks))
def audit_family():
 """Inventory all saved executions, retaining research and missing intents separately.
 Rates describe persisted execution IDs, not unobservable chat requests or races.
 """
 from execution_store import resolve_phase
 from collections import Counter
 root=ROOT/'runtime'; intents={p.stem:p for directory in ['formal_intents','jra_formal_intents'] for p in (root/directory).glob('*.json')}
 ids=sorted(set(intents)|{p.name for p in (root/'executions').iterdir() if p.is_dir()})
 rows=[]
 for eid in ids:
  request=load(intents[eid]) if eid in intents else {}
  row={'execution_id':eid,'family':request.get('family_id') or next((token for token in eid.split('-') if token in {'LOCAL','JRA','BAN'}), 'UNKNOWN'),
       'intent_ref':str(intents[eid].relative_to(ROOT)) if eid in intents else None,
       'request_received_at':None,'delivery_received_at':None,'verified_delivery':False,
       'population':'LIVE_LABELED_SAVED_EXECUTION' if '-LIVE-' in eid else 'RESEARCH_OR_OTHER_NOT_LIVE_DENOMINATOR',
       'scheduled_post_at':request.get('scheduled_post_at'),'prediction_cutoff':request.get('prediction_cutoff'),
       'phases':{},'attempts':[],'errors':[]}
  for phase in ['SOURCE','FORMAL','RESULT']:
   runs=root/'executions'/eid/phase/'runs'
   for attempt in sorted(runs.glob('*')):
    if not attempt.is_dir():continue
    row['attempts'].append({'phase':phase,'run_id':attempt.name})
   try:r=resolve_phase(eid,phase,root=root/'executions')
   except Exception as exc:
    row['errors'].append({'phase':phase,'code':str(exc)});continue
   if not r:continue
   folder=Path(r['run_dir']);names={'SOURCE':'source','FORMAL':'final','RESULT':'result'}
   envpath=folder/(names[phase]+'_receipt_envelope.json');env=load(envpath) if envpath.exists() else {}
   rec=env.get('receipt') or {};art=env.get('artifact') or {}
   row['phases'][phase]={'run_id':r['manifest'].get('run_id'),'code_sha':r['manifest'].get('github_sha'),
    'manifest_integrity':'PASS','receipt_ref':env.get('receipt_sha256'),'signed_at':rec.get('timestamp'),
    'receipt_status':rec.get('status'),'signature_reverified':False,'receipt_path':str(envpath.relative_to(ROOT)) if envpath.exists() else None}
   if phase=='FORMAL':
    temporal=load(folder/'final_before_post_verification.json') if (folder/'final_before_post_verification.json').exists() else {}
    row['prestart_final_recorded']=temporal.get('verified') is True
    row['prestart_proof_authority']='SAVED_TEMPORAL_CHECK; NOT_FRESH_SIGNATURE_ACCEPTANCE'
    row['static_frozen_at']=art.get('final_prediction_package',{}).get('frozen_at')
    row['krs_ref']=art.get('krs_receipt_sha256')
   if phase=='RESULT':
    row['settlement_present']=bool(art.get('settlement') or art.get('automatic_post_result_review'))
    row['learning_present']=bool(art.get('automatic_next_race_learning_state'))
  for reportpath in sorted((root/'execution_reports'/eid).glob('*.json')):
   try:report=load(reportpath)
   except (ValueError,OSError):continue
   code=report.get('first_failed_code') or report.get('code')
   if code:row['errors'].append({'code':code,'phase':report.get('first_failed_phase'),
       'ref':str(reportpath.relative_to(ROOT)),'resume_hint':report.get('resume_hint')})
  row['first_unproven_stage']=next((p for p in ['SOURCE','FORMAL','RESULT'] if p not in row['phases']),None)
  row['root_cause']='RECORDED_ERROR' if row['errors'] else ('INSUFFICIENT_EVIDENCE' if row['first_unproven_stage'] else 'NO_MISSING_SAVED_PHASE')
  row['alias_warning']='Transport EXEC aliases and versioned retries are retained; not distinct races.'
  rows.append(row)
 live=[r for r in rows if r['population']=='LIVE_LABELED_SAVED_EXECUTION']
 score={}
 for family in sorted({r['family'] for r in live}):
  subset=[r for r in live if r['family']==family];n=len(subset)
  score[family]={'saved_live_execution_ids':n,'saved_intents':sum(bool(r['intent_ref']) for r in subset),
    **{p.lower()+'_saved':sum(p in r['phases'] for r in subset) for p in ['SOURCE','FORMAL','RESULT']},
    'prestart_final_recorded':sum(r.get('prestart_final_recorded',False) for r in subset),
    'verified_delivery':0,'request_acceptance_rate':None,'automatic_recovery_success_rate':None,
    'denominator_warning':'Execution IDs include retries; chat requests and absent intents are not fully observable; no Race/Family reliability claim.'}
 auxiliary=[]
 for directory in ['jra_no_bet_terminals','jra_no_bet_learning','jra_race_day_status','learning_states','race_key_requests']:
  for p in sorted((root/directory).glob('*.json')):
   obj=load(p)
   auxiliary.append({'ref':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'status':obj.get('status'),'execution_id':obj.get('execution_id') or obj.get('race_id'),'authority':'SEPARATE_LEDGER_NOT_INFERRED_AS_SIGNED_FORMAL'})
 out={'auxiliary_ledgers':auxiliary,'status':'COMPLETED_INVENTORY_NOT_LIVE_ACCEPTANCE','observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'rows':rows,'scorecard':score,'all_saved_execution_ids':len(ids),'research_or_other_count':len(rows)-len(live),
      'unobserved_requests':'UNKNOWN_NOT_ZERO','new_forward_acceptance_count':0,
      'first_unproven_stage_counts':dict(Counter(r['first_unproven_stage'] or 'NONE' for r in live))}
 target=ROOT/'research/family_reliability_20261015';target.mkdir(parents=True,exist_ok=True)
 (target/'execution_inventory.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k!='rows'},ensure_ascii=False,indent=2))

if __name__=='__main__':
 if '--family' in sys.argv:audit_family()
 else:audit()

