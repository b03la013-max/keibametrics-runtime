import copy, json, pathlib, sys, unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from selector import calibrate, select, risk_coupled_select, hit
from build_ledger import ROOT, build, identity, tickets
from run_shadow import run

class WidthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger=build()
        cls.production=[r for r in cls.ledger['rows'] if r['analysis_eligible'] and r['lane']=='JRA_PRODUCTION' and r['frozen_scores']]
        cls.candidate=[r for r in cls.ledger['rows'] if r['analysis_eligible'] and r['lane']=='JRA_CANDIDATE' and r['frozen_scores']]

    def test_budget_does_not_erase_prediction(self):
        row=self.production[0]
        a=risk_coupled_select(row['frozen_scores'],budget=100)
        b=risk_coupled_select(row['frozen_scores'],budget=100000)
        self.assertEqual(a['columns'],b['columns']);self.assertEqual(a['tickets'],b['tickets'])
        self.assertFalse(a['budget_compatible']);self.assertTrue(b['budget_compatible'])
        self.assertEqual(a['decision'],'PAPER')

    def test_set_identity_double_digit_horses(self):
        from selector import features
        keys=next(iter(self.production[0]['frozen_scores'].values())).keys()
        tied={h:{k:75.0 for k in keys} for h in ['2','10','15']}
        self.assertEqual(features(tied)['ranks']['W'],['10','15','2'])
        t=[{'bet_type':'TRIO','selection':[2,10,15],'stake':100}]
        self.assertTrue(hit(t,[15,2,10])['TRIO'])
        for row in self.production:
            ts=risk_coupled_select(row['frozen_scores'])['tickets']
            for t in ts:
                self.assertEqual(len(t['selection']),len(set(t['selection'])))
                if t['bet_type']=='TRIO':self.assertEqual(t['selection'],sorted(t['selection']))
            self.assertEqual(len(ts),len({(t['bet_type'],tuple(t['selection'])) for t in ts}))

    def test_date_block_and_mixed_authority_rejected(self):
        model=calibrate(self.candidate,.9);row=self.candidate[-1]
        with self.assertRaisesRegex(ValueError,'DATE_BOUNDARY'):
            select(row['frozen_scores'],model,lane=row['lane'],numerical_profile=row['numerical_profile'],race_date=model['calibration_last_date'])
        with self.assertRaisesRegex(ValueError,'AUTHORITY_MISMATCH'):
            select(row['frozen_scores'],model,lane='JRA_PRODUCTION',numerical_profile=row['numerical_profile'],race_date='20261012')
        with self.assertRaisesRegex(ValueError,'MIXED_LANE'):
            calibrate(self.candidate+[self.production[0]])

    def test_outcome_and_payout_not_inputs_to_selector(self):
        row=copy.deepcopy(self.production[0]);a=risk_coupled_select(row['frozen_scores'])
        row['outcome']={'top3':[1,2,3],'payouts':{'TRIFECTA':9999999}}
        self.assertEqual(a,risk_coupled_select(row['frozen_scores']))

    def test_small_sample_is_not_fake_quantile(self):
        model=calibrate(self.candidate[:6],.9)
        self.assertIsNone(model['q'])
        with self.assertRaisesRegex(ValueError,'DUPLICATE_RACE'):calibrate(self.candidate+self.candidate[:1])

    def test_width_is_variable_and_model_does_not_claim_oos(self):
        plans=[risk_coupled_select(row['frozen_scores']) for row in self.production]
        self.assertGreater(len({p['ticket_count'] for p in plans}),1)
        self.assertTrue(all(p['decision']=='PAPER' and p['fixed_ticket_cap'] is None for p in plans))

    def test_bad_indices_and_budget_rejected(self):
        s=copy.deepcopy(self.production[0]['frozen_scores']);h=next(iter(s));s[h]['RFI']=float('nan')
        with self.assertRaisesRegex(ValueError,'INVALID_INDEX'):risk_coupled_select(s)
        with self.assertRaisesRegex(ValueError,'INVALID_BUDGET'):risk_coupled_select(self.production[0]['frozen_scores'],budget=True)

    def test_runtime_rejects_candidate_lane(self):
        with self.assertRaisesRegex(ValueError,'NON_PRODUCTION'):run({'family_id':'JRA','static_prediction':{'production_authority':False}})

    def test_runtime_checks_component_evidence(self):
        q=json.loads((ROOT/'runtime/requests/KM-JRA-TKY-20261011-R11-LIVE-R1-FORMAL.json').read_text())
        q['runners'][0]['canonical_components']['RFI']['evidence_refs']=[]
        with self.assertRaisesRegex(Exception,'INDEX_INVALID'):run(q)

    def test_synthetic_identity_and_duplicate_ticket_rejected(self):
        self.assertIsNone(identity('KM-ACCEPT-JRA-TKY-20261011-R11'))
        with self.assertRaisesRegex(ValueError,'duplicate canonical'):tickets([{'bet_type':'TRIO','selection':[2,10,15]},{'bet_type':'TRIO','selection':[15,2,10]}])

    def test_research_axes_match_enacted_mapping_on_frozen_full20(self):
        sys.path.insert(0,str(ROOT/'runtime'))
        from jra_aki_v21 import apply_authorized_v21
        from selector import features
        authority=json.loads((ROOT/'profiles/KM_FAMILY_CURRENT_AUTHORITY_20261011_R50.json').read_text())
        for row in self.production:
            q=json.loads((ROOT/row['feature_path']).read_text())
            source={**q['source_snapshot'],'source_snapshot_sha256':q['source_snapshot_sha256']}
            official=apply_authorized_v21(q,source,authority,root=ROOT)['static_prediction']['aki_jra_v21']
            f=features(row['frozen_scores'])
            for c in ['W','P2','P3']:self.assertEqual(f['aki'][c],official['axes'][c+'-AKI'])
            self.assertEqual(f['rsi'],official['axes']['RSI'])
            self.assertEqual(f['axis_failure_risk'],official['axis_failure_risk'])

if __name__=='__main__':unittest.main()
