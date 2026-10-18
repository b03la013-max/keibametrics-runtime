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
