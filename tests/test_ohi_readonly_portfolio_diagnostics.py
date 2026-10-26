import copy
import importlib.util
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/'scripts/ohi_readonly_portfolio_diagnostics.py'
spec=importlib.util.spec_from_file_location('ohi_diagnostic',PATH)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class ReadonlyPortfolioTests(unittest.TestCase):
    def tickets(self):
        return [{'bet_type':'EXACTA','selection':[1,2],'stake':100,'coverage_ids':['PAIR:1>2']},
                {'bet_type':'EXACTA','selection':[2,1],'stake':100,'coverage_ids':['PAIR:2>1']},
                {'bet_type':'TRIO','selection':[1,2,3],'stake':100,'coverage_ids':['TRIO:1>2>3','TAIL:1>2>3']}]

    def result(self):
        return {'payouts_complete':True,'verification_status':'LABELLED_TEST_ONLY',
            'winning_selections':{'EXACTA':[{'selection':[1,2],'payout_per_100':500}],
                'TRIO':[{'selection':[1,2,3],'payout_per_100':600}]}}

    def test_trio_sums_native_ordered_permutations_not_marginal_products(self):
        pred={'ordered_pairs':[{'head':'1','second':'2','model_mass':0.4}],
            'ordered_triples':[{'head':'1','second':'2','third':'3','model_mass':0.1},
                {'head':'2','second':'1','third':'3','model_mass':0.2}]}
        scores=m.conditional_scores(pred)
        self.assertAlmostEqual(0.3,scores['TRIO:1>2>3'])
        self.assertEqual(0.4,scores['EXACTA:1>2'])
        self.assertAlmostEqual(0.1,scores['TRIFECTA:1>2>3'])

    def test_missing_or_refund_result_is_unknown_not_zero(self):
        for result in (None,{}, {'payouts_complete':True,'winning_selections':{'TRIO':[]}},
                       {**self.result(),'refund_runner_ids':['1']}):
            with self.subTest(result=result):self.assertIsNone(m.outcome(self.tickets(),result)['return'])

    def test_zero_ticket_pfs_is_null_and_winning_payouts_not_duplicated(self):
        r=m.outcome([],self.result())
        self.assertEqual(0,r['investment']);self.assertEqual(0,r['return']);self.assertIsNone(r['pfs'])
        r=m.outcome(self.tickets(),self.result());self.assertEqual(1100,r['return'])
        bad=self.result();bad['winning_selections']['EXACTA']*=2
        with self.assertRaisesRegex(ValueError,'DUPLICATE'):m.outcome(self.tickets(),bad)

    def test_frontier_retains_all_units_and_outcomes_do_not_change_selection(self):
        tickets=self.tickets();before=copy.deepcopy(tickets);order=[m.key(t) for t in tickets]
        a=m.frontier(tickets,order,200,self.result(),frozen_winning_keys=['EXACTA:1>2','TRIO:1>2>3'])
        b=m.frontier(tickets,order,200,None)
        self.assertEqual(before,tickets);self.assertIsNone(a['chosen_prefix'])
        self.assertEqual([0,1,2,3],[p['prefix_length'] for p in a['frontier']])
        self.assertEqual([p['selected_keys_sha256'] for p in a['frontier']],
                         [p['selected_keys_sha256'] for p in b['frontier']])
        self.assertEqual(4,a['frontier'][0]['lost_material_unit_count'])
        self.assertFalse(a['frontier'][-1]['within_fixed_10000_yen_cap'])
        self.assertEqual(['TRIO:1>2>3'],a['frontier'][2]['lost_frozen_winning_keys'])

    def test_duplicate_self_unknown_and_invalid_stake_rejected(self):
        good=self.tickets();m.validate_tickets(good,{'1','2','3'})
        for rows in (good+good[:1],[{**good[0],'selection':[1,1]}],
                     [{**good[0],'selection':[1,4]}],[{**good[0],'stake':100.0}]):
            with self.subTest(rows=rows),self.assertRaises(ValueError):m.validate_tickets(rows,{'1','2','3'})

    def test_missing_model_or_no_bet_does_not_gain_new_authority(self):
        self.assertIsNone(m.conditional_scores({'ranking':['1','2','3']}))
        bad={'ordered_pairs':[{'head':'1','second':'2','model_mass':float('nan')}],'ordered_triples':[]}
        with self.assertRaises(ValueError):m.conditional_scores(bad)

    def test_summary_missing_results_does_not_publish_full_cohort_pfs(self):
        a=m.outcome(self.tickets(),self.result());b=m.outcome(self.tickets(),None)
        r=m.summarize_evaluations([a,b]);self.assertIsNone(r['return']);self.assertIsNone(r['pfs']);self.assertIsNone(r['max_drawdown'])


if __name__=='__main__':unittest.main()
