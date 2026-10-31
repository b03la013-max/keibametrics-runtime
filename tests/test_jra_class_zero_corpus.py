"""Regression for actual registered pedigree-class sample selection, offline."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from jra_owner_authorized_feature_rules import owner_authorized_observations, _class_at_least

REGISTRY = json.loads((ROOT / 'mapping/jra_evidence_feature_rule_registry_v1.3_20261010.json').read_text())

def source(race_class='2歳未勝利'):
    return {'family_id': 'JRA', 'source_snapshot_sha256': 'fixture-not-live',
            'source_freeze_at': '2026-10-31T04:00:00+00:00',
            'prediction_cutoff': '2026-10-31T14:30:00+09:00',
            'jra_race_context': {'race_date': '2026-10-31', 'race_class': race_class,
                                 'venue_name': '東京', 'surface': '芝', 'distance_m': 1600},
            'jra_official_runner_universe': {'runners': [{'runner_id': '1', 'status': 'ACTIVE'}, {'runner_id': '2', 'status': 'ACTIVE'}]},
            'jra_official_race_card_detail': {'runners': [{'runner_id': '1', 'horse_name': 'TARGET', 'sire': 'SIRE', 'damsire': 'DAMSIRE'}]}}

def corpus(count=3, n_runs=2, title='2歳未勝利', sire='SIRE'):
    return {'manifest_sha256': 'offline-corpus', 'horses': {
        f'H{i}': {'horse_name': f'H{i}', 'sire': sire, 'damsire': 'DAMSIRE',
                 'runs': {str(j): {'finish': 1, 'field_size': 10, 'race_name': title, 'surface': '芝', 'distance_m': 1600} for j in range(n_runs)}}
        for i in range(count)}}

class TestClassZeroSample(unittest.TestCase):
    def test_sire_zero_class_sample_reaches_existing_three_horse_six_run_minimum(self):
        f = owner_authorized_observations(source(), REGISTRY, corpus=corpus())['1']['pedigree_class']
        self.assertEqual(f['observation_count'], 6)
        self.assertEqual(f['rule_id'], 'KM-JRA-OA-PEDIGREE-SIRE-CLASS-v1')
        self.assertIn('offspring=3; runs=6', f['source_fact'])

    def test_damsire_zero_class_fallback_retains_existing_stricter_minimum(self):
        f = owner_authorized_observations(source(), REGISTRY, corpus=corpus(4, 3, sire='OTHER'))['1']['pedigree_class']
        self.assertEqual(f['observation_count'], 12)
        self.assertEqual(f['rule_id'], 'KM-JRA-OA-PEDIGREE-DAMSIRE-CLASS-FALLBACK-v1')

    def test_missing_sample_remains_missing(self):
        self.assertNotIn('pedigree_class', owner_authorized_observations(source(), REGISTRY, corpus=corpus(2))['1'])

    def test_maiden_does_not_qualify_for_one_win_class(self):
        self.assertNotIn('pedigree_class', owner_authorized_observations(source('3歳以上1勝クラス'), REGISTRY, corpus=corpus())['1'])

    def test_unknown_is_not_zero_and_positive_class_comparison_unchanged(self):
        self.assertFalse(_class_at_least('不明', 0))
        self.assertTrue(_class_at_least('2歳新馬', 0))
        self.assertTrue(_class_at_least('2勝クラス', 1))
        self.assertFalse(_class_at_least('1勝クラス', 2))

if __name__ == '__main__':
    unittest.main()
