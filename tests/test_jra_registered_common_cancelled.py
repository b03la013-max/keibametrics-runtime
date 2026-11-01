"""Offline synthetic gates; no real source content included."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'runtime/jra_source_runtime'), str(ROOT / 'runtime')]
import jra_registered_common as candidate

def fixture():
    declared = [{'horse_no': 1, 'name': 'ALPHA', 'status': 'ACTIVE'}, {'horse_no': 2, 'name': 'BETA', 'status': 'ACTIVE'},
                {'horse_no': 3, 'name': 'GAMMA', 'status': 'CANCELLED', 'status_source_id': 'OFFICIAL-SYNTHETIC', 'status_source_snapshot_sha256': 'a' * 64}]
    artifact = {'source_race_context': {'race_date': '2026-10-31', 'race_no': 6}, 'jra_race_context': {'venue_name': '東京'},
                'jra_official_runner_universe': {'runners': deepcopy(declared[:2])},
                'jra_declared_runner_universe': {'universe_type': 'DECLARED', 'runner_universe_sha256': 'b' * 64, 'source_snapshot_sha256': 'c' * 64, 'runners': deepcopy(declared)}}
    parsed = {'runner_count': 3, 'schema': 'COMPACT_ASSESSMENT', 'runners': [{'horse_no': n, 'runner_id': str(n), 'horse_name': name, 'assessment': 'SYNTHETIC', 'rating': 'B', 'final1f': None} for n, name in [(1, 'ALPHA'), (2, 'BETA'), (3, 'GAMMA')]]}
    raw = '<title>調教 2026年10月31日 東京6R</title>'.encode()
    return parsed, artifact, raw

class TestCancelledWorkout(unittest.TestCase):
    def test_exact_declared_cancel_only_exclusion_and_input_immutability(self):
        parsed, artifact, raw = fixture()
        original = deepcopy((parsed, artifact))
        out = candidate._normalize_declared_cancelled_workout(parsed, artifact, raw, 'text/html; charset=UTF-8')
        self.assertEqual(candidate._reconcile(out, artifact)['verified'], True)
        self.assertEqual([r['horse_no'] for r in out['runners']], [1, 2])
        self.assertEqual(original, (parsed, artifact))
        self.assertEqual(out['cancelled_runner_exclusions']['excluded'][0]['horse_no'], 3)
        self.assertTrue(all(r['final1f'] is None for r in out['runners']))

    def test_normal_exact_active_feed_is_unchanged(self):
        parsed, artifact, raw = fixture()
        parsed['runners'].pop(); parsed['runner_count'] = 2
        self.assertIs(candidate._normalize_declared_cancelled_workout(parsed, artifact, b'unchanged normal path', ''), parsed)

    def test_negative_boundaries_remain_rejected(self):
        for change in ('extra_active', 'unknown_extra', 'missing_active', 'cancel_name', 'duplicate', 'no_status_source', 'wrong_race', 'wrong_date', 'wrong_venue', 'out_of_range', 'fractional', 'boolean', 'runner_id_conflict', 'active_status'):
            with self.subTest(change=change):
                parsed, artifact, raw = fixture()
                if change == 'extra_active': artifact['jra_declared_runner_universe']['runners'][2]['status'] = 'ACTIVE'
                elif change == 'unknown_extra': parsed['runners'].append({'horse_no': 4, 'horse_name': 'DELTA'})
                elif change == 'missing_active': parsed['runners'].pop(0)
                elif change == 'cancel_name': parsed['runners'][2]['horse_name'] = 'WRONG'
                elif change == 'duplicate': parsed['runners'].append(deepcopy(parsed['runners'][0]))
                elif change == 'no_status_source': artifact['jra_declared_runner_universe']['runners'][2].pop('status_source_snapshot_sha256')
                elif change == 'wrong_race': raw = raw.replace(b'6R', b'7R')
                elif change == 'wrong_date': raw = raw.replace(b'31', b'30')
                elif change == 'wrong_venue': raw = raw.replace('東京'.encode(), '京都'.encode())
                elif change == 'out_of_range':
                    parsed['runners'][2].update(horse_no=19, runner_id='19'); artifact['jra_declared_runner_universe']['runners'][2]['horse_no'] = 19
                elif change == 'fractional':
                    parsed['runners'][2]['horse_no'] = 3.5; artifact['jra_declared_runner_universe']['runners'][2]['horse_no'] = 3.5
                elif change == 'boolean': parsed['runners'][0]['horse_no'] = True
                elif change == 'runner_id_conflict': parsed['runners'][0]['runner_id'] = '2'
                else: artifact['jra_official_runner_universe']['runners'][0]['status'] = 'CANCELLED'
                out = candidate._normalize_declared_cancelled_workout(parsed, artifact, raw, 'text/html; charset=UTF-8')
                self.assertEqual(out, parsed)
                self.assertFalse(candidate._reconcile(out, artifact)['verified'])

if __name__ == '__main__':
    unittest.main()
