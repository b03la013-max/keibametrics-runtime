"""Real frozen equal-exposure comparisons, no purchase/OOS authority."""
import copy,json,sys,unittest
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tests'),str(ROOT/'research/jra_conditional_rank')]
from test_jra_role_learning_repair import fixture
from probability_shadow import distribution,scores
from head_p2_shadow import predict,matched_exposure

class HeadExposureTest(unittest.TestCase):
 def test_real_controls_preserve_budget_stakes_and_baseline_bytes(self):
  base=json.loads((ROOT/'research/jra_conditional_rank/probability_candidate.json').read_text())
  head=json.loads((ROOT/'research/jra_conditional_rank/head_p2_candidate.json').read_text())
  for v,n in [('TKY',11),('KYO',2),('KYO',4),('KYO',10),('TKY',8),('TKY',12)]:
   with self.subTest(v=v,n=n):
    q,f,_=fixture(v,n);old=copy.deepcopy(f)
    for d in (distribution(scores(q['runners'],base['rank_model']),dict(W=1.,P2=1.,P3=1.)),predict(q['runners'],base,head)):
     out=matched_exposure(d,f)
     self.assertEqual(out['required_capital'],f['final_ticket']['total_investment'])
     self.assertEqual(Counter((t['bet_type'],t['stake']) for t in out['tickets']),Counter((t['bet_type'],t['stake']) for t in f['final_ticket']['tickets']))
     self.assertFalse(out['oos_eligible']);self.assertFalse(out['purchase_authority']);self.assertEqual(f,old)
 def test_missing_third_joint_and_mass_corruption_fail_closed(self):
  q,f,_=fixture();m=json.loads((ROOT/'research/jra_conditional_rank/probability_candidate.json').read_text())
  d=distribution(scores(q['runners'],m['rank_model']),dict(W=1.,P2=1.,P3=1.))
  for kind in ('joint','mass','third','negative_conditionals','marginal'):
   bad=copy.deepcopy(d);key=next(iter(bad['ordered_joint']))
   if kind=='joint':bad['ordered_joint'].pop(key)
   elif kind=='mass':bad['ordered_joint'][key]*=2
   elif kind=='third':bad['pair_third'][next(iter(bad['pair_third']))].pop(next(iter(next(iter(bad['pair_third'].values())))))
   elif kind=='negative_conditionals':
    head=next(iter(bad['head_p2']))
    bad['head_p2'][head]={s:-p for s,p in bad['head_p2'][head].items()}
    for pair in bad['pair_third']:
     if pair.startswith(head+'>'):bad['pair_third'][pair]={t:-p for t,p in bad['pair_third'][pair].items()}
   else:
    ids=list(bad['marginals']['P2']);bad['marginals']['P2'][ids[0]]+=0.01;bad['marginals']['P2'][ids[1]]-=0.01
   with self.subTest(kind=kind),self.assertRaises(ValueError):matched_exposure(bad,f)
