import copy,itertools,json,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'scripts'),str(ROOT/'research/jra_conditional_rank')]
from probability_shadow import ID,POLICY,FEATURES,softmax,distribution,measures,ece,forecast,fit_temperatures,fit_ood,ood_score,sha

def fixture():
 runners=[{'runner_id':str(h),'canonical_components':{f:{'value':float(40+h)} for f in FEATURES}} for h in (1,2,3)]
 rank={'features':list(FEATURES),'coefficients':{r:[0.]*20 for r in ('W','P2','P3')},'training_manifest':[{'race_id':'KM-JRA-TKY-20000101-R01','result_captured_at':'2000-01-01T12:00:00+00:00'}]};rank['sha256']=sha(rank)
 model={'candidate_id':ID,'rank_model':rank,'policy':POLICY,'policy_sha256':sha(POLICY),'temperatures':{r:1. for r in ('W','P2','P3')},'created_at':'2000-01-03T00:00:00+00:00','calibration_manifest':[{'race_id':'KM-JRA-TKY-20000102-R01','source_freeze_at':'2000-01-02T01:00:00+00:00','result_captured_at':'2000-01-02T12:00:00+00:00'}]};model['sha256']=sha(model)
 for m in rank['training_manifest']:
  m.update(source_sha256='a'*64,final_sha256='b'*64,result_sha256='c'*64,source_freeze_at='2000-01-01T01:00:00+00:00',prediction_cutoff='2000-01-01T01:55:00+00:00',scheduled_post_at='2000-01-01T02:00:00+00:00')
 for m in model['calibration_manifest']:m.update(source_sha256='d'*64,final_sha256='e'*64,result_sha256='f'*64,prediction_cutoff='2000-01-02T01:55:00+00:00',scheduled_post_at='2000-01-02T02:00:00+00:00')
 rank['sha256']=sha({k:v for k,v in rank.items() if k!='sha256'});model['sha256']=sha({k:v for k,v in model.items() if k!='sha256'})
 q={'race_id':'KM-JRA-TKY-20000104-R01','runners':runners,'source_snapshot':{'source_freeze_at':'2000-01-04T01:00:00+00:00'},'source_snapshot_sha256':'unit-source','prediction_cutoff':'2000-01-04T02:00:00+00:00'}
 return q,model

class ProbabilityTests(unittest.TestCase):
 def test_uniform_joint_marginals_and_no_repeat_orientation(self):
  sc={r:{str(h):0. for h in (1,2,3,4)} for r in ('W','P2','P3')};out=distribution(sc,{r:1 for r in sc})
  self.assertEqual(len(out['ordered_joint']),24);self.assertAlmostEqual(sum(out['ordered_joint'].values()),1)
  for role,p in out['marginals'].items():
   self.assertAlmostEqual(sum(p.values()),1)
   for value in p.values():self.assertAlmostEqual(value,.25)
  for key in out['ordered_joint']:self.assertEqual(len(set(key.split('>'))),3)
  for h,p in out['head_p2'].items():self.assertNotIn(h,p);self.assertAlmostEqual(sum(p.values()),1)
  for pair,p in out['pair_third'].items():self.assertFalse(set(pair.split('>'))&set(p));self.assertAlmostEqual(sum(p.values()),1)
 def test_temperature_changes_confidence_not_within_context_order(self):
  scores={'1':3.,'2':2.,'3':1.};cold=softmax(scores,.5);hot=softmax(scores,2)
  self.assertGreater(cold['1'],hot['1']);self.assertEqual(sorted(cold,key=cold.get),sorted(hot,key=hot.get))
  for h in scores:
   p=softmax(scores,1,(h,));self.assertEqual(list(sorted(p,key=p.get)),[x for x in sorted(scores,key=scores.get) if x!=h])
 def test_known_log_loss_brier_and_ece(self):
  m=measures({'1':.5,'2':.25,'3':.25},'2');self.assertAlmostEqual(m['log_loss'],math.log(4));self.assertAlmostEqual(m['brier_sum'],.875)
  self.assertAlmostEqual(m['rank_mid'],2.5);self.assertEqual(m['top1_correct'],0)
  self.assertAlmostEqual(ece([{'top1_confidence':.6,'top1_correct':1},{'top1_confidence':.6,'top1_correct':0}]),.1)
 def test_probabilities_stable_and_invalid_values_rejected(self):
  self.assertAlmostEqual(sum(softmax({'1':10000.,'2':-10000.},.125).values()),1)
  for temp in (0,-1,float('inf'),True):
   with self.subTest(temp=temp),self.assertRaises(ValueError):softmax({'1':0},temp)
  with self.assertRaises(ValueError):softmax({'1':float('nan')},1)
 def test_forecast_binds_inputs_and_has_no_purchase_or_oos_authority(self):
  q,m=fixture();old=copy.deepcopy((q,m));out=forecast(q,m,observed_at='2000-01-04T01:01:00+00:00')
  self.assertEqual((q,m),old);self.assertEqual(out['source_sha256'],q['source_snapshot_sha256']);self.assertEqual(out['model_sha256'],m['sha256'])
  self.assertFalse(out['ev_kelly_authority']);self.assertFalse(out['oos_eligible']);self.assertEqual(out['tickets_created'],0);self.assertEqual(out['sha256'],sha({k:v for k,v in out.items() if k!='sha256'}))
 def test_model_policy_weight_split_time_and_target_tamper_fail_closed(self):
  q,m=fixture()
  for kind in ('hash','policy','weights','target','late_created','duplicate_manifest','train_after_cal','label_after_model','nested_hash'):
   a=copy.deepcopy(m)
   if kind=='hash':a['sha256']='bad'
   elif kind=='policy':a['policy_sha256']='bad'
   elif kind=='weights':a['rank_model']['coefficients']['P2']=[0.]
   elif kind=='target':a['calibration_manifest'][0]['race_id']=q['race_id']
   elif kind=='late_created':a['created_at']=q['prediction_cutoff']
   elif kind=='duplicate_manifest':a['calibration_manifest'][0]['race_id']=a['rank_model']['training_manifest'][0]['race_id']
   elif kind=='train_after_cal':a['rank_model']['training_manifest'][0]['result_captured_at']='2000-01-02T02:00:00+00:00'
   elif kind=='label_after_model':a['calibration_manifest'][0]['result_captured_at']='2000-01-04T00:00:00+00:00'
   elif kind=='nested_hash':a['rank_model']['sha256']='bad'
   if kind!='nested_hash':a['rank_model']['sha256']=sha({k:v for k,v in a['rank_model'].items() if k!='sha256'})
   if kind!='hash':a['sha256']=sha({k:v for k,v in a.items() if k!='sha256'})
   with self.subTest(kind=kind),self.assertRaises(ValueError):forecast(q,a,observed_at='2000-01-04T01:01:00+00:00')
  for when in ('2000-01-04T00:59:00+00:00','2000-01-04T02:00:01+00:00'):
   with self.subTest(when=when),self.assertRaises(ValueError):forecast(q,m,observed_at=when)
 def test_calibration_refuses_duplicate_and_training_overlap(self):
  q,m=fixture();row={'race_id':q['race_id'],'q':q,'runners':q['runners'],'top3':['1','2','3']}
  with self.assertRaises(ValueError):fit_temperatures([row,row],m['rank_model'])
  row['race_id']=m['rank_model']['training_manifest'][0]['race_id']
  with self.assertRaises(ValueError):fit_temperatures([row],m['rank_model'])
 def test_ood_schema_and_split_integrity(self):
  q,m=fixture();rows=[{'race_id':str(i),'runners':q['runners']} for i in range(6)]
  spec=fit_ood(rows[:2],rows[2:]);self.assertIsNone(spec['threshold']) # finite sample 90% quantile unavailable with 4 calibration races
  self.assertEqual(ood_score(rows[0],spec),0)
  with self.assertRaises(ValueError):fit_ood(rows[:2],rows[1:])
  spec['scales']=[]
  with self.assertRaises(ValueError):ood_score(rows[0],spec)
 def test_detection_counts_have_error_positive_semantics(self):
  from jra_probability_readiness_audit import detection
  rows=[{'risk_diagnostics':{'winner_outside_W':error,'flags':{k:flag for k in ('evidence','market','ood')}}} for flag,error in ((True,True),(True,False),(False,True),(False,False))]
  for r in detection(rows).values():
   self.assertEqual([r[k] for k in ('tp','fp','fn','tn')],[1,1,1,1]);self.assertEqual(r['sensitivity'],.5)
 def test_saved_temporal_report_and_existing_72_pins(self):
  report=json.loads((ROOT/'evidence/jra_p0_20261018/PREDICTIVE_STRUCTURE_AUDIT.json').read_text());self.assertEqual(report['sha256'],sha({k:v for k,v in report.items() if k!='sha256'}));self.assertEqual(report['data_split']['rank_train'],19);self.assertEqual(report['data_split']['temperature_calibration'],22);self.assertEqual(report['data_split']['heldout_formal_final'],34)
  model=json.loads((ROOT/'research/jra_conditional_rank/model.json').read_text())
  for date in ('2026-10-24','2026-10-25'):
   plan=json.loads((ROOT/'runtime/jra_race_day_plan'/f'{date}.json').read_text());self.assertEqual(plan['forward_oos_preregistration']['model_sha256'],model['sha256']);self.assertFalse(report['next_72']['plan_change']);self.assertFalse(report['capital']['ev_kelly_eligible'])

class ProbabilitySchemaRegressionTests(unittest.TestCase):
 def test_rehashed_off_grid_missing_role_and_invalid_manifest_are_refused(self):
  q,m=fixture()
  for kind in ('off_grid','missing_role','empty_train','empty_cal','bad_sha','non_jra','source_after_result'):
   a=copy.deepcopy(m)
   if kind=='off_grid':a['temperatures']['W']=3.14159
   if kind=='missing_role':a['temperatures'].pop('P3')
   if kind=='empty_train':a['rank_model']['training_manifest']=[]
   if kind=='empty_cal':a['calibration_manifest']=[]
   if kind=='bad_sha':a['calibration_manifest'][0]['result_sha256']='wrong'
   if kind=='non_jra':a['calibration_manifest'][0]['race_id']='LOCAL-1'
   if kind=='source_after_result':a['calibration_manifest'][0]['source_freeze_at']='2000-01-03T00:00:00+00:00'
   a['rank_model']['sha256']=sha({k:v for k,v in a['rank_model'].items() if k!='sha256'});a['sha256']=sha({k:v for k,v in a.items() if k!='sha256'})
   with self.subTest(kind=kind),self.assertRaises(ValueError):forecast(q,a,observed_at='2000-01-04T01:01:00+00:00')
