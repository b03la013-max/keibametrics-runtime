import importlib.util
from pathlib import Path
from datetime import datetime, timezone
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('intake',ROOT/'scripts/jra_weekend_bvi_intake.py')
intake=importlib.util.module_from_spec(spec);spec.loader.exec_module(intake)

class IntakeTests(unittest.TestCase):
    def plan(self):
        return {'profile':intake.PROFILE,'input_policy':'JRA_OFFICIAL_REACQUISITION_ONLY',
                'historical_prediction_rewrite':False,'dates':[
                    {'date':'2026-10-10','expected_races':24},
                    {'date':'2026-10-11','expected_races':24}]}
    def test_complete_weekend_is_16_sequential_three_race_windows(self):
        w=intake.windows(self.plan(),datetime(2026,10,11,12,tzinfo=timezone.utc))
        self.assertEqual(len(w),16)
        self.assertEqual({x['start'] for x in w},set(range(0,24,3)))
    def test_same_day_before_evening_is_deferred(self):
        w=intake.windows(self.plan(),datetime(2026,10,11,9,tzinfo=timezone.utc))
        self.assertEqual(len(w),8);self.assertTrue(all(x['date']=='2026-10-10' for x in w))
    def test_future_date_is_not_collected(self):
        self.assertEqual(intake.windows(self.plan(),datetime(2026,10,9,12,tzinfo=timezone.utc)),[])
    def test_cannot_queue_bloodb_as_official(self):
        p=self.plan();p['input_policy']='BLOODB_AS_OFFICIAL'
        with self.assertRaises(ValueError):intake.windows(p)
    def test_historical_prediction_rewrite_rejected(self):
        p=self.plan();p['historical_prediction_rewrite']=True
        with self.assertRaises(ValueError):intake.windows(p)
    def test_duplicate_day_rejected(self):
        p=self.plan();p['dates'][1]=p['dates'][0]
        with self.assertRaises(ValueError):intake.windows(p)
    def test_unattested_file_cannot_be_admitted(self):
        import tempfile,json
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'fake.json';p.write_text(json.dumps({'official':True,'source':'www.jra.go.jp'}))
            with self.assertRaisesRegex(ValueError,'OIDC'):intake.verify_admission(p)

if __name__=='__main__':unittest.main()


def test_partial_admission_remains_pending_and_full_retry_preserves_original(tmp_path):
    import json
    plan={'profile':intake.PROFILE,'input_policy':'JRA_OFFICIAL_REACQUISITION_ONLY',
          'historical_prediction_rewrite':False,'dates':[{'date':'2026-10-10','expected_races':12}]}
    corpus=tmp_path/'runtime/pedigree_corpus';receipts=tmp_path/'runtime/pedigree_intake_receipts'
    corpus.mkdir(parents=True);receipts.mkdir(parents=True)
    old=corpus/'old.json';old.write_text(json.dumps({'sha256':'old','horse_count':47,'horse_token_count':48}))
    receipt={'status':'OFFICIAL_BVI_CORPUS_ADMITTED','file':'old.json','harvest_sha256':'old'}
    (receipts/'20261010-race0.json').write_text(json.dumps(receipt))
    before=old.read_bytes();now=datetime(2026,10,11,12,tzinfo=timezone.utc)
    assert {'date':'2026-10-10','start':0} in intake.pending_windows(plan,tmp_path,now)
    (corpus/'retry.json').write_text(json.dumps({'sha256':'new','horse_count':48,'horse_token_count':48}))
    receipt.update(file='retry.json',harvest_sha256='new')
    (receipts/'20261010-race0-retry-1.json').write_text(json.dumps(receipt))
    assert {'date':'2026-10-10','start':0} not in intake.pending_windows(plan,tmp_path,now)
    assert old.read_bytes()==before
