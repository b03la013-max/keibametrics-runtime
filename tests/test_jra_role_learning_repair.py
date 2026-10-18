"""Real positive/negative controls plus temporal leakage and immutable sidecars."""
import copy,json,sys,tempfile,unittest
from datetime import datetime,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
from jra_role_learning_shadow import build_shadow,intake,digest,settle_shadow,persist_shadow,pre_result_witness
from post_result_learning import build_post_result_review,build_learning_state

def fixture(v='TKY',n=10):
 rid=f'KM-JRA-{v}-20261018-R{n:02d}'
 return (json.loads((ROOT/'runtime/requests'/f'{rid}-LIVE-R1-FORMAL.json').read_text()),
         json.loads((ROOT/'runtime/final_artifacts'/f'{rid}.json').read_text()),
         json.loads((ROOT/'runtime/results'/f'{rid}.json').read_text()))

class RepairTests(unittest.TestCase):
 def test_real_positive_controls_keep_signed_ticket_and_role_structure(self):
  for v,n in [('TKY',11),('KYO',2),('KYO',4),('KYO',10)]:
   with self.subTest(venue=v,race=n):
    q,f,r=fixture(v,n);before=copy.deepcopy((q,f,r));review=build_post_result_review(r,f)
    shadow=build_shadow(q,f,historical=True,observed_at=f['final_freeze_timestamp'])
    settled=settle_shadow(shadow,r)
    self.assertEqual(settled['arms']['PRODUCTION']['total_payout'],r['settlement']['total_payout'])
    self.assertEqual((q,f,r),before);self.assertFalse(shadow['oos_eligible'])
    for name,arm in shadow['arms'].items():
     if name!='CORE_PROTECTION':self.assertGreaterEqual(arm['required_capital'],f['final_ticket']['total_investment'])
    self.assertTrue(all(x['static_role_hit']==review['prediction']['role_capture'][{'W':'winner_w','P2':'second_p2','P3':'third_p3'}[x['role']]] for x in review['krs']['post_result_evaluation']['rank_comparison']))
 def test_tky8_negative_control_and_tky10_rescue_cost_are_honest(self):
  q,f,r=fixture(n=8);review=build_post_result_review(r,f)
  self.assertEqual(review['krs']['post_result_evaluation']['unique_rescue_role_count'],0)
  q,f,r=fixture();s=build_shadow(q,f,historical=True,observed_at=f['final_freeze_timestamp']);out=settle_shadow(s,r)
  self.assertEqual(out['arms']['PRODUCTION']['total_payout'],670)
  self.assertGreater(out['arms']['PAIR_THIRD']['total_investment'],out['arms']['PRODUCTION']['total_investment'])
  self.assertFalse(out['oos_eligible'])
 def test_source_final_hash_and_universe_must_match(self):
  q,f,r=fixture();g=copy.deepcopy(f);g['sha256']='tampered'
  with self.assertRaisesRegex(ValueError,'HASH'):build_shadow(q,g,historical=True)
  g=copy.deepcopy(f);g['source_snapshot_sha256']='0'*64;g['sha256']=digest({k:v for k,v in g.items() if k!='sha256'})
  with self.assertRaisesRegex(ValueError,'SOURCE'):build_shadow(q,g,historical=True)
  g=copy.deepcopy(q);g['runners']=g['runners'][:-1]
  with self.assertRaisesRegex(ValueError,'UNIVERSE'):build_shadow(g,f,historical=True)
 def test_live_late_freeze_never_becomes_forward_oos(self):
  q,f,r=fixture()
  with self.assertRaisesRegex(ValueError,'AFTER_CUTOFF'):build_shadow(q,f,observed_at='2026-10-18T17:00:00+09:00')
  s=build_shadow(q,f,observed_at=f['final_freeze_timestamp']);self.assertFalse(s['oos_eligible'])
  self.assertFalse(pre_result_witness(ROOT,s)['verified'])
 def test_new_learning_is_bound_and_old_learning_is_not_backdated(self):
  q,f,r=fixture();review=build_post_result_review(r,f);old=build_learning_state(review)
  self.assertNotIn('effective_time',old)
  stamp=(datetime.fromisoformat(q['source_snapshot']['source_freeze_at'])-timedelta(minutes=1)).isoformat()
  review=copy.deepcopy(review);review['race_id']='KM-JRA-TKY-20261018-R09';review['failure_localization']['first_material_failure']='PREDICTION_ROLE_W';review['sha256']=digest({k:v for k,v in review.items() if k!='sha256'})
  state=build_learning_state(review,effective_time=stamp)
  s=build_shadow(q,f,states=[state],observed_at=f['final_freeze_timestamp'])
  self.assertEqual(s['learning_state_bindings'][0]['state_sha256'],state['sha256'])
  self.assertEqual(s['learning_applied_to_arm'],'LEARNING_ON')
  self.assertEqual(s['learning_intake']['accepted'][0]['source_race_id'],review['race_id'])
 def test_same_race_duplicate_and_late_learning_rejected(self):
  q,f,r=fixture();rev=build_post_result_review(r,f)
  state=build_learning_state(rev,effective_time='2026-10-18T00:00:00+00:00')
  args=dict(race_id=q['race_id'],source_freeze=q['source_snapshot']['source_freeze_at'],cutoff=q['prediction_cutoff'],observed_at=f['final_freeze_timestamp'])
  self.assertEqual(intake([state],**args)['excluded'][0]['reason'],'SAME_RACE_LEAKAGE')
  self.assertEqual(len(intake([state,state],**args)['excluded']),2)
  state['race_id']='KM-JRA-TKY-20261018-R09';state['effective_time']=q['source_snapshot']['source_freeze_at'];state['sha256']=digest({k:v for k,v in state.items() if k!='sha256'})
  self.assertEqual(intake([state],**args)['excluded'][0]['reason'],'NOT_AVAILABLE_BEFORE_SOURCE')
 def test_real_shadow_result_bindings_and_tamper_rejected(self):
  q,f,r=fixture();s=build_shadow(q,f,historical=True,observed_at=f['final_freeze_timestamp'])
  bad=copy.deepcopy(s);bad['arms']['PRODUCTION']['required_capital']+=100
  with self.assertRaisesRegex(ValueError,'HASH'):settle_shadow(bad,r)
  bad=copy.deepcopy(r);bad['frozen_prediction_ref']['immutable_final_sha256']='wrong'
  with self.assertRaisesRegex(ValueError,'BINDING'):settle_shadow(s,bad)
 def test_untracked_freeze_cannot_be_counted_as_forward(self):
  q,f,r=fixture();s=build_shadow(q,f,historical=True)
  with tempfile.TemporaryDirectory() as tmp:self.assertFalse(pre_result_witness(tmp,s)['verified'])

if __name__=='__main__':unittest.main()

class PersistenceWitnessTests(unittest.TestCase):
 def test_backdated_git_commit_never_proves_independent_pre_result_receipt(self):
  import os,subprocess
  q,f,r=fixture();s=build_shadow(q,f,historical=True,observed_at=f['final_freeze_timestamp'])
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)
   def git(*a,env=None):return subprocess.check_output(['git',*a],cwd=root,env=env,stderr=subprocess.DEVNULL)
   git('init');git('config','user.name','test');git('config','user.email','test@example.invalid')
   (root/'initial').write_text('base');git('add','initial');git('commit','-m','base')
   p=root/'runtime/role_rescue_shadow'/f"{s['race_id']}.json";p.parent.mkdir(parents=True);p.write_text(json.dumps(s))
   git('add',str(p.relative_to(root)))
   env=dict(os.environ,GIT_AUTHOR_DATE='2026-10-18T05:10:00+00:00',GIT_COMMITTER_DATE='2026-10-18T05:10:00+00:00')
   git('commit','-m','deliberately backdated',env=env)
   proof=pre_result_witness(root,s)
   self.assertTrue(proof.get('git_history_correlated'))
   self.assertFalse(proof['verified'])

class FamilyIsolationTests(unittest.TestCase):
 def test_local_preregistered_definition_bytes_unchanged(self):
  import hashlib
  protocol=json.loads((ROOT/'research/utility/forward_protocol.json').read_text())
  path='runtime/krs_prediction_utility.py'
  self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),protocol['definition_sha256'][path])
 def test_jra_producer_records_actual_frozen_roles(self):
  from jra_krs_measurement import build_krs_prediction_utility
  q,f,_=fixture();u=copy.deepcopy(f['krs_prediction_utility']);zones=u['snapshot']['role_zones']
  u['snapshot']['role_zones']={k:v for k,v in zip(('w_max_rank','p2_max_rank','p3_max_rank'),(zones['W'],zones['P2'],zones['P3']))}
  out=build_krs_prediction_utility(q,{'status':'EXECUTED','output':u})
  for row in out['summary']:
   self.assertEqual(row['static_roles'],sorted(q['static_prediction']['roles'][str(row['horse_no'])]))
