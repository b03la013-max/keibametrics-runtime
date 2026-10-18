import copy,json,sys,tempfile,unittest
from pathlib import Path
from datetime import datetime,timedelta,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'));sys.path.insert(0,str(ROOT/'scripts'))
from jra_conditional_rank_shadow import compare,sha,vectors
from jra_prediction_quality_audit import ranks,corr,equal_budget,records
from jra_role_learning_shadow import persist_shadow,digest

def future():
 q=json.loads((ROOT/'runtime/requests/KM-JRA-TKY-20261018-R10-LIVE-R1-FORMAL.json').read_text());f=json.loads((ROOT/'runtime/final_artifacts/KM-JRA-TKY-20261018-R10.json').read_text())
 model=json.loads((ROOT/'research/jra_conditional_rank/model.json').read_text());when=datetime.now(timezone.utc)+timedelta(days=10)
 rid='KM-JRA-TKY-20990101-R10';q['race_id']=f['race_id']=rid;q['prediction_cutoff']=f['prediction_cutoff']=(when+timedelta(minutes=10)).isoformat();q['source_snapshot']['source_freeze_at']=when.isoformat();q['static_computed_at']=(when+timedelta(minutes=1)).isoformat();f['final_freeze_timestamp']=(when+timedelta(minutes=2)).isoformat();f['krs_prediction_utility']['race_id']=rid;f['sha256']=digest({k:v for k,v in f.items() if k!='sha256'})
 return q,f,model,(when+timedelta(minutes=3)).isoformat()

class QualityTests(unittest.TestCase):
 def test_ties_and_constant_correlations(self):
  self.assertEqual(ranks({'a':3,'b':3,'c':1}),{'a':1.5,'b':1.5,'c':3})
  self.assertIsNone(corr([1,1,1],[1,2,3]));self.assertEqual(corr([1,2,3],[1,2,3]),1)
 def test_equal_budget_actual_100_yen_and_baseline_saturation(self):
  tickets=[{'bet_type':'EXACTA','selection':[1,i+2],'stake':100} for i in range(6)]
  out=equal_budget(tickets,400);self.assertEqual(sum(t['stake'] for t in out),400);self.assertEqual(out,tickets[:4])
  self.assertTrue(all(t['stake']%100==0 for t in equal_budget(tickets,1900)))
 def test_future_result_blind_full_conditional_rankings(self):
  q,f,m,obs=future();old=copy.deepcopy((q,m));out=compare(q,m)
  self.assertEqual((q,m),old);self.assertEqual(set(out['role_rankings']),{'W','P2','P3'});self.assertEqual(out['tickets_created'],0)
  for h,l in out['head_local_p2'].items():self.assertNotIn(h,l)
  for p,l in out['pair_conditioned_third'].items():self.assertFalse(set(p.split('>'))&set(l))
 def test_no_late_training_or_model_hash_override(self):
  q,f,m,obs=future()
  for kind in ('hash','late_model','target_overlap','late_result'):
   x=copy.deepcopy(m)
   if kind=='hash':x['coefficients']['W'][0]+=1
   if kind=='late_model':x['created_at']=q['prediction_cutoff']
   if kind=='target_overlap':x['training_manifest'][0]['race_id']=q['race_id']
   if kind=='late_result':x['training_manifest'][0]['result_captured_at']=q['prediction_cutoff']
   if kind!='hash':x['sha256']=sha({k:v for k,v in x.items() if k!='sha256'})
   with self.subTest(kind=kind),self.assertRaises(ValueError):compare(q,x)
 def test_full20_not_missing_imputed(self):
  q,f,m,obs=future();q['runners'][0]['canonical_components']['BVI']['value']=None
  with self.assertRaises(ValueError):vectors(q['runners'])
 def test_new_model_attaches_to_existing_freeze_without_changing_tickets(self):
  q,f,m,obs=future()
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);p=root/'research/jra_conditional_rank/model.json';p.parent.mkdir(parents=True);p.write_text(json.dumps(m));out=persist_shadow(root,q,f,observed_at=obs)
   self.assertEqual(out['conditional_rank_comparison']['model_sha256'],m['sha256'])
   self.assertEqual(out['arms']['PRODUCTION']['tickets'],f['final_ticket']['tickets'])
   self.assertIn('runtime/jra_conditional_rank_shadow.py',out['additional_code_sha256']);self.assertFalse(out['oos_eligible'])
 def test_same_day_past_cannot_be_refrozen_as_oos_with_new_model(self):
  q=json.loads((ROOT/'runtime/requests/KM-JRA-TKY-20261018-R10-LIVE-R1-FORMAL.json').read_text());m=json.loads((ROOT/'research/jra_conditional_rank/model.json').read_text())
  with self.assertRaisesRegex(ValueError,'BEFORE_SOURCE'):compare(q,m)
 def test_real_36_races_9000_cells_include_zero_bet(self):
  day=[r for r in records() if r['day']=='20261018'];self.assertEqual(len(day),36);self.assertEqual(sum(r['no_bet'] for r in day),2)
  self.assertEqual(sum(len(r['runners'])*20 for r in day),9000)

class WitnessBindingTests(unittest.TestCase):
 def test_nested_hash_and_required_maps_must_bind(self):
  import io,zipfile,hashlib
  from test_jra_live_acceptance_continuation import proof_fixture
  from jra_role_learning_shadow import verify_actions_artifact
  original,run,artifact,archive,code,result=proof_fixture()
  n={'candidate_id':'JRA-CONDITIONAL-RANK-20261018-R1','role_rankings':{'W':['1']},'model_sha256':'m'*64,'code_sha256':'c'*64,
     'source_sha256':original['source_sha256'],'runner_universe_sha256':original['runner_universe_sha256'],'prediction_cutoff':original['prediction_cutoff']}
  n['sha256']=sha(n)
  original['conditional_rank_comparison']=n
  original['additional_code_sha256']={'runtime/jra_conditional_rank_shadow.py':n['code_sha256']}
  original['additional_input_sha256']={'research/jra_conditional_rank/model.json':n['model_sha256']}
  def bundle(s):
   s['sha256']=sha({k:v for k,v in s.items() if k!='sha256'});blob=io.BytesIO()
   with zipfile.ZipFile(blob,'w') as z:z.writestr(s['race_id']+'/role_learning_shadow.json',json.dumps(s))
   data=blob.getvalue();a=copy.deepcopy(artifact);a['digest']='sha256:'+hashlib.sha256(data).hexdigest()
   return a,data
  a,data=bundle(original);self.assertTrue(verify_actions_artifact(original,run,a,data,code)['verified'])
  for kind in ('nested_hash','code_map','model_map','missing_map'):
   s=copy.deepcopy(original)
   if kind=='nested_hash':s['conditional_rank_comparison']['sha256']='bad'
   if kind=='code_map':s['additional_code_sha256']['runtime/jra_conditional_rank_shadow.py']='wrong'
   if kind=='model_map':s['additional_input_sha256']['research/jra_conditional_rank/model.json']='wrong'
   if kind=='missing_map':s.pop('additional_input_sha256')
   a,data=bundle(s)
   with self.subTest(kind=kind),self.assertRaisesRegex(ValueError,'NESTED_RANK_BINDING'):verify_actions_artifact(s,run,a,data,code)
 def test_noninteger_or_partial_yen_budget_rejected(self):
  for v in (-100,True,150,1.2):
   with self.subTest(budget=v),self.assertRaises(ValueError):equal_budget([],v)

class EqualExposureTests(unittest.TestCase):
 def test_same_budget_per_kind_stake_multiset_and_no_production_mutation(self):
  from collections import Counter
  from jra_conditional_rank_shadow import exposure_portfolio,policy_sha
  q,f,m,_=future();before=copy.deepcopy(f);r=compare(q,m);p=exposure_portfolio(r,f)
  self.assertEqual(f,before);self.assertEqual(p['required_capital'],f['final_ticket']['total_investment'])
  self.assertEqual(p['ticket_count'],len(f['final_ticket']['tickets']))
  self.assertEqual(Counter((t['bet_type'],t['stake']) for t in p['tickets']),Counter((t['bet_type'],t['stake']) for t in f['final_ticket']['tickets']))
  self.assertEqual(len({(t['bet_type'],tuple(t['selection'])) for t in p['tickets']}),len(p['tickets']))
  for t in p['tickets']:
   self.assertEqual(len(t['selection']),len(set(t['selection'])))
   if t['bet_type']=='TRIO':self.assertEqual(t['selection'],sorted(t['selection']))
  changed=copy.deepcopy(m);changed['l2']+=1;self.assertNotEqual(policy_sha(m),policy_sha(changed))
 def test_oracle_conditioning_is_not_predicted_pair_and_all_migrations_tracked(self):
  from jra_conditional_rank_shadow import evaluate_comparison
  r={'candidate_id':'fixture','model_sha256':'a','model_policy_sha256':'b','role_rankings':{'W':['1','2','3'],'P2':['1','2','3'],'P3':['1','2','3']},
   'head_local_p2':{'1':['2','3'],'2':['1','3'],'3':['1','2']},
   'pair_conditioned_third':{'1>2':['3'],'2>1':['3']},'reference_role_widths':{'W':2,'P2':2,'P3':1},'baseline_roles':{'2':['P3'],'1':['W']}}
  out=evaluate_comparison(r,['2','1','3']);self.assertFalse(out['top1_ordered_pair_capture']);self.assertFalse(out['top1_exact_capture'])
  self.assertTrue(out['matched_width_conditional_exact_capture']);self.assertEqual(out['oracle_head_local_p2_rank'],1)
  self.assertEqual(out['p3_migrations_all_qualifying_horses']['W'],['2']);self.assertTrue(out['actual_winner_migration_rescue'])
 def test_real_positive_and_negative_controls_production_unchanged(self):
  from jra_conditional_rank_shadow import exposure_portfolio
  from jra_conditional_failure_audit import retrospective_rank
  m=json.loads((ROOT/'research/jra_conditional_rank/model.json').read_text())
  ids={'KM-JRA-TKY-20261018-R11','KM-JRA-KYO-20261018-R02','KM-JRA-KYO-20261018-R04','KM-JRA-KYO-20261018-R10','KM-JRA-TKY-20261018-R08','KM-JRA-TKY-20261018-R12','KM-JRA-NGT-20261018-R10'}
  seen=0
  for row in records():
   if row['race_id'] not in ids:continue
   frozen=copy.deepcopy(row['f']);r=retrospective_rank(row,m);p=exposure_portfolio(r,row['f'])
   self.assertFalse(r['oos_eligible']);self.assertEqual(row['f'],frozen);self.assertEqual(p['added_capital'],0);seen+=1
  self.assertEqual(seen,7)
 def test_settlement_reallocation_cost_includes_shared_ticket_stake_changes(self):
  from jra_role_learning_shadow import build_shadow,settle_shadow
  from jra_conditional_rank_shadow import exposure_portfolio,EXPOSURE_POLICY
  q,f,m,obs=future();shadow=build_shadow(q,f,observed_at=obs);rank=compare(q,m);p=exposure_portfolio(rank,f)
  baseline=copy.deepcopy(shadow['arms']['PRODUCTION']['tickets'])
  # Same selections and total exposure, but stakes move between a winning and losing selection.
  kind=baseline[0]['bet_type'];same=[t for t in baseline if t['bet_type']==kind][:2];self.assertEqual(len(same),2)
  for t in baseline:t['stake']=100
  samekeys=[(t['bet_type'],t['selection']) for t in same]
  winner=next(t for t in baseline if (t['bet_type'],t['selection'])==samekeys[0]);loser=next(t for t in baseline if (t['bet_type'],t['selection'])==samekeys[1]);winner['stake']=200
  base=shadow['arms']['PRODUCTION'];base['tickets']=baseline;base['required_capital']=sum(t['stake'] for t in baseline)
  for name,arm in shadow['arms'].items():
   if name!='PRODUCTION':arm['tickets']=copy.deepcopy(baseline);arm['required_capital']=base['required_capital'];arm['ticket_count']=len(baseline)
  candidate=copy.deepcopy(baseline)
  for t in candidate:
   if (t['bet_type'],t['selection'])==samekeys[0]:t['stake']=100
   if (t['bet_type'],t['selection'])==samekeys[1]:t['stake']=200
  p.update(tickets=candidate,required_capital=base['required_capital'],ticket_count=len(baseline));p['sha256']=sha({k:v for k,v in p.items() if k!='sha256'})
  shadow.update(conditional_rank_comparison=rank,conditional_rank_portfolio=p);shadow['sha256']=digest({k:v for k,v in shadow.items() if k!='sha256'})
  result=json.loads((ROOT/'runtime/results/KM-JRA-TKY-20261018-R10.json').read_text());result['race_id']=q['race_id'];result['frozen_prediction_ref']['immutable_final_sha256']=f['sha256'];result['official_result']['captured_at']=(datetime.fromisoformat(obs)+timedelta(days=1)).isoformat()
  # The real payout table can have either moved selection winning. The allocation identity holds regardless.
  out=settle_shadow(shadow,result)['conditional_rank_portfolio_result']
  self.assertEqual(out['redeployed_capital'],100);self.assertEqual(out['added_ticket_count'],0);self.assertEqual(out['removed_ticket_count'],0)
  self.assertEqual(out['net_payout_increment'],out['increased_allocation_return']-out['decreased_allocation_return'])
  self.assertIn(out['false_positive_cost'],(0,100));self.assertFalse(out['oos_eligible'])

class ExposureWitnessTests(unittest.TestCase):
 def test_provider_archive_binds_separate_portfolio_model_and_policy(self):
  import io,zipfile,hashlib
  from test_jra_live_acceptance_continuation import proof_fixture
  from jra_role_learning_shadow import verify_actions_artifact
  from jra_conditional_rank_shadow import EXPOSURE_POLICY
  original,run,artifact,archive,code,result=proof_fixture()
  n={'candidate_id':'JRA-CONDITIONAL-RANK-20261018-R1','race_id':original['race_id'],'role_rankings':{'W':['1']},'model_sha256':'m'*64,'code_sha256':'c'*64,'model_policy_sha256':'p'*64,
     'source_sha256':original['source_sha256'],'runner_universe_sha256':original['runner_universe_sha256'],'prediction_cutoff':original['prediction_cutoff']}
  n['sha256']=sha(n);original['conditional_rank_comparison']=n
  original['additional_code_sha256']={'runtime/jra_conditional_rank_shadow.py':n['code_sha256']};original['additional_input_sha256']={'research/jra_conditional_rank/model.json':n['model_sha256']}
  p={k:original[k] for k in ('race_id','source_sha256','runner_universe_sha256','prediction_cutoff','baseline_final_sha256')}
  p.update(policy=EXPOSURE_POLICY,policy_sha256=sha(EXPOSURE_POLICY),rank_comparison_sha256=n['sha256'],model_policy_sha256=n['model_policy_sha256'],model_sha256=n['model_sha256'])
  p['sha256']=sha(p);original['conditional_rank_portfolio']=p
  def bundle(s):
   s['sha256']=sha({k:v for k,v in s.items() if k!='sha256'});blob=io.BytesIO()
   with zipfile.ZipFile(blob,'w') as z:z.writestr(s['race_id']+'/role_learning_shadow.json',json.dumps(s))
   data=blob.getvalue();a=copy.deepcopy(artifact);a['digest']='sha256:'+hashlib.sha256(data).hexdigest();return a,data
  a,data=bundle(original);self.assertTrue(verify_actions_artifact(original,run,a,data,code)['verified'])
  for key in ('policy_sha256','model_sha256','model_policy_sha256','source_sha256','rank_comparison_sha256','baseline_final_sha256'):
   s=copy.deepcopy(original);s['conditional_rank_portfolio'][key]='tampered';s['conditional_rank_portfolio']['sha256']=sha({k:v for k,v in s['conditional_rank_portfolio'].items() if k!='sha256'})
   a,data=bundle(s)
   with self.subTest(field=key),self.assertRaisesRegex(ValueError,'WITNESS_EXPOSURE_BINDING'):verify_actions_artifact(s,run,a,data,code)

class ExposureUniverseRegressionTests(unittest.TestCase):
 def test_rehashed_outsider_duplicate_missing_and_bad_exclusions_fail_closed(self):
  from jra_conditional_rank_shadow import exposure_portfolio
  q,f,m,_=future();rank=compare(q,m)
  for kind in ('outsider','duplicate','missing_head','head_in_p2','pair_in_third','universe_hash'):
   r=copy.deepcopy(rank);h=r['role_rankings']['W'][0];s=r['head_local_p2'][h][0]
   if kind=='outsider':r['head_local_p2'][h][0]='99'
   if kind=='duplicate':r['role_rankings']['P3'][0]=r['role_rankings']['P3'][1]
   if kind=='missing_head':r['head_local_p2'].pop(h)
   if kind=='head_in_p2':r['head_local_p2'][h][0]=h
   if kind=='pair_in_third':r['pair_conditioned_third'][h+'>'+s][0]=s
   if kind=='universe_hash':r['runner_universe_sha256']='bad'
   r['sha256']=sha({k:v for k,v in r.items() if k!='sha256'})
   with self.subTest(kind=kind),self.assertRaises(ValueError):exposure_portfolio(r,f)
