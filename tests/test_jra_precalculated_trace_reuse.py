"""Offline mechanical fixtures: preserve an already calculated feature snapshot."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
sys.path.insert(0, str(ROOT / 'tests'))
from jra_source_to_evidence_features import attach_source_features_to_request, SourceToFeatureError
from jra_evidence_to_base_production import build_production_ledger
from jra_production_auto_handoff import compile_production_auto_handoff
from test_jra_production_auto_handoff import fixture as handoff_fixture, FREEZE

def sha(x):
    return hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def fixture():
    mapping = json.loads((ROOT / 'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text())
    source = {'family_id': 'JRA', 'race_id': 'KM-JRA-SYNTHETIC-TRACE', 'source_snapshot_sha256': 'a' * 64}
    features = {'weight_load_fit': {'category': 'NEUTRAL', 'rule_id': 'JRA-WEIGHT-EQUAL-CONDITION-v1',
                'evidence_refs': ['SYNTHETIC-MECHANICAL-TEST'], 'source_fact': 'offline equal assigned weights'}}
    runners = [{'runner_id': str(n), 'career_starts': 1, 'evidence_features': deepcopy(features)} for n in (1, 2)]
    full = {'race_id': source['race_id'], 'source_snapshot_sha256': source['source_snapshot_sha256'],
            'pedigree_corpus_manifest': {'snapshots': [], 'snapshot_count': 0, 'manifest_sha256': sha([])},
            'runners': {r['runner_id']: {'merged_evidence_features': r['evidence_features']} for r in runners}}
    full['sha256'] = sha(full)
    req = {'race_id': source['race_id'], 'source_snapshot_sha256': source['source_snapshot_sha256'],
           'runners': runners, 'index_provenance_ledger': build_production_ledger(source['race_id'], runners, mapping),
           'source_to_evidence_feature_compiler': {k: v for k, v in full.items() if k != 'runners'},
           'source_to_evidence_feature_sha256': full['sha256']}
    return req, source, mapping

class TestPrecalculatedTraceReuse(unittest.TestCase):
    def test_original_snapshot_reused_without_later_corpus_read_or_value_change(self):
        req, source, mapping = fixture()
        original = deepcopy(req)
        with patch('jra_source_to_evidence_features.compile_source_to_features', side_effect=AssertionError('do not acquire later corpus')):
            out = attach_source_features_to_request(req, source, mapping)
        self.assertEqual(out, original)
        self.assertEqual(req, original)
        out['runners'][0]['evidence_features'].clear()
        self.assertEqual(req, original)

    def test_unbound_or_foreign_requests_cannot_silently_reuse(self):
        for mutation in ('feature', 'source', 'runner', 'mapping', 'compiler', 'missing_feature_hash', 'ledger_value', 'rehash_forged_ledger', 'career_profile'):
            with self.subTest(mutation=mutation):
                req, source, mapping = fixture()
                if mutation == 'feature': req['runners'][0]['evidence_features']['weight_load_fit']['category'] = 'STRONG'
                elif mutation == 'source': source['race_id'] = 'FOREIGN'
                elif mutation == 'runner': req['runners'].pop()
                elif mutation == 'mapping': req['index_provenance_ledger']['mapping_id'] = 'FOREIGN'
                elif mutation == 'compiler': req['source_to_evidence_feature_compiler']['sha256'] = '0' * 64
                elif mutation == 'missing_feature_hash': req['index_provenance_ledger']['runners']['1'].pop('feature_snapshot_sha256')
                elif mutation == 'career_profile': req['runners'][0]['career_starts'] = 7
                else:
                    ledger = req['index_provenance_ledger']
                    ledger['runners']['1']['base_indices']['HPI']['value'] += 1
                    if mutation == 'rehash_forged_ledger': ledger['sha256'] = sha({k: v for k, v in ledger.items() if k != 'sha256'})
                with self.assertRaises(ValueError):
                    attach_source_features_to_request(req, source, mapping)

    def test_valid_original_compiler_without_corpus_is_not_reclassified_as_missing(self):
        req, source, mapping = fixture()
        compiler = req['source_to_evidence_feature_compiler']
        compiler['pedigree_corpus_manifest'] = None
        original_report = {**{k: v for k, v in compiler.items() if k != 'sha256'},
                           'runners': {r['runner_id']: {'merged_evidence_features': r['evidence_features']} for r in req['runners']}}
        compiler['sha256'] = sha(original_report)
        req['source_to_evidence_feature_sha256'] = compiler['sha256']
        with patch('jra_source_to_evidence_features.compile_source_to_features', side_effect=AssertionError('no reread')):
            self.assertEqual(attach_source_features_to_request(req, source, mapping), req)

    def test_handoff_carries_exact_original_coverage_without_mutation_or_numerical_change(self):
        intent, source, report, authority = handoff_fixture()
        baseline = compile_production_auto_handoff(intent, source, report, current_authority=authority, frozen_at=FREEZE, root=ROOT)
        prepared = report['prepared_numerical_request']
        row = {'factual_runner_updates': {}, 'generated_production_feature_count': 0,
               'shadow_observation_count': 0, 'merge_conflicts': [], 'source_only_formal_base_ready': False,
               'source_only_coverage': {}, 'automation_gap': {}, 'coverage': {}, 'source_fact_availability': {},
               'source_feature_trace': {'original_at_numeric_time': True}, 'source_feature_trace_summary': {},
               'rule_evaluator_inputs': {'sha256': 'b' * 64}, 'merged_evidence_features': {}}
        full = {'race_id': intent['race_id'], 'source_snapshot_sha256': source['artifact']['source_snapshot_sha256'],
                'pedigree_corpus_manifest': {'snapshots': [], 'snapshot_count': 0, 'manifest_sha256': sha([])},
                'runners': {r['runner_id']: deepcopy(row) for r in prepared['runners']}}
        full['sha256'] = sha(full)
        report['source_feature_report'] = deepcopy(full)
        prepared['source_to_evidence_feature_compiler'] = {k: v for k, v in full.items() if k != 'runners'}
        prepared['source_to_evidence_feature_sha256'] = full['sha256']
        intent['source_to_evidence_feature_runner_coverage'] = {'forged_intent': True}
        original = deepcopy((intent, source, report, authority))
        out = compile_production_auto_handoff(intent, source, report, current_authority=authority, frozen_at=FREEZE, root=ROOT)
        self.assertEqual(original, (intent, source, report, authority))
        self.assertEqual(out['source_to_evidence_feature_runner_coverage']['1']['source_feature_trace'], row['source_feature_trace'])
        for field in ('runners', 'static_prediction', 'role_registry', 'pair_dispositions', 'third_dispositions', 'krs_input_data', 'capital_policy'):
            self.assertEqual(out[field], baseline[field], field)
        out['source_to_evidence_feature_runner_coverage']['1']['source_feature_trace'].clear()
        self.assertEqual(original, (intent, source, report, authority))

if __name__ == '__main__':
    unittest.main()
