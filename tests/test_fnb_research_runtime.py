"""Durable private orchestration: lineage/caching, not physics reimplementation."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import sys

from runtime import local_fnb_research_runtime as r


class ResearchRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def cache(self):
        # Any single Race is accepted; neither the 3 archived dates nor their
        # number of runners are encoded in the replay contract.
        value = {'race': {'prediction_id': 'KM-LOCAL-FNB-20261105-R09-RESEARCH',
                         'race_no': 9, 'date': '2026-11-05', 'racecourse': '船橋'},
            'environment': {}, 'simulation': {'master_seed': 1, 'run_count': 5000},
            'horses': [{'horse_no': 2, 'name': 'SyntheticTwo', 'hsv': {}, 'static_roles': []},
                       {'horse_no': 5, 'name': 'SyntheticFive', 'hsv': {}, 'static_roles': ['P3']}],
            'fnb_context_candidate_semantics': {'old_trace': True}}
        output = {'snapshot': {'prediction_id': value['race']['prediction_id'],
            'run_count': 5000, 'master_seed': 1, 'field_size': 2},
            'engine': {'engine_version': '1.1.0', 'parameter_map_version': '0.1-provisional',
                       'parameter_status': 'PROVISIONAL_UNCALIBRATED'},
            'summary': [{'horse_no': 2}, {'horse_no': 5}]}
        cache = self.root / 'cache'; cache.mkdir()
        i = r.encoded(value); o = r.encoded(output)
        (cache / 'context_input.json').write_bytes(i)
        (cache / 'context_output.json').write_bytes(o)
        receipt = {'input_sha256': r.digest(i), 'output_sha256': r.digest(o),
            'status': 'EXECUTED', 'process_returncode': 0, 'engine_sha256': r.ENGINE_SHA,
            'parameter_map_sha256': r.MAP_SHA, 'actual_base_run_count': 5000,
            'actual_seed': 1, 'model_code_sha256': r.MODEL_SHA}
        data = r.encoded(receipt); (cache / 'context_receipt.json').write_bytes(data)
        return cache, value, r.digest(data)

    def test_metadata_only_cache_reuse_keeps_original_execution_sha(self):
        cache, value, pin = self.cache()
        original_sha = r.digest((cache / 'context_input.json').read_bytes())
        value['fnb_context_candidate_semantics'] = {'new_trace': 'unchanged engine input'}
        proof = r.reuse_krs(cache, value, self.root / 'result', receipt_sha256=pin)
        self.assertFalse(proof['new_engine_execution'])
        self.assertFalse(proof['full_input_bytes_equal'])
        self.assertEqual(proof['execution_input_sha256'], original_sha)
        self.assertTrue(proof['exact_engine_input_equal'])

    def test_rng_identity_roles_and_arrays_cannot_be_normalized_for_cache_hit(self):
        cache, value, pin = self.cache()
        for mutate in (lambda q: q['race'].update(prediction_id='other'),
                       lambda q: q['horses'][0].update(static_roles=['W']),
                       lambda q: q['horses'][0].update(hsv={'initial_acceleration': 80}),
                       lambda q: q['environment'].update(front_density_ratio=.5)):
            changed = deepcopy(value); mutate(changed)
            with self.assertRaisesRegex(r.ResearchHold, 'NOT_IDENTICAL_ENGINE_INPUT'):
                r.reuse_krs(cache, changed, self.root / 'hold', receipt_sha256=pin)

    def test_modified_cache_bytes_and_receipt_pin_rejected(self):
        cache, value, pin = self.cache()
        (cache / 'context_output.json').write_text('{}')
        with self.assertRaisesRegex(r.ResearchHold, 'BYTES_MISMATCH'):
            r.reuse_krs(cache, value, self.root / 'bad', receipt_sha256=pin)
        with self.assertRaisesRegex(r.ResearchHold, 'SHA_REQUIRED'):
            r.reuse_krs(cache, value, self.root / 'bad', receipt_sha256=None)

    def test_immutable_originals_and_symlink_parents_fail_closed(self):
        p = self.root / 'original.json'; r._immutable(p, b'first')
        with self.assertRaisesRegex(r.ResearchHold, 'REVISION_CONFLICT'):
            r._immutable(p, b'changed')
        (self.root / 'alias').symlink_to(self.root / 'other')
        with self.assertRaisesRegex(r.ResearchHold, 'SYMLINK_FORBIDDEN'):
            r._immutable(self.root / 'alias/raw.json', b'private')
        with self.assertRaisesRegex(r.ResearchHold, 'GIT_WORKTREE_FORBIDDEN'):
            r._private_root(r.REPO / 'public-source')

    def test_completed_manifest_requires_all_original_bytes(self):
        p = self.root / 'one'; p.write_bytes(b'actual')
        manifest = self.root / 'research_execution_manifest.json'
        manifest.write_bytes(r.encoded({'private_artifacts': [{'path': 'one', 'sha256': r.digest(b'actual')}]}))
        r._verify_saved_manifest(manifest)
        p.write_bytes(b'tampered')
        with self.assertRaisesRegex(r.ResearchHold, 'ORIGINAL_BYTES_CHANGED'):
            r._verify_saved_manifest(manifest)


if __name__ == '__main__':
    unittest.main()


def test_explicit_research_entry_never_enters_formal_or_writes_public_output(monkeypatch, tmp_path, capsys):
    from runtime import local_race_entry as entry
    descriptor = tmp_path / 'intent.json'; descriptor.write_text('{}')
    expected = {'profile': r.PROFILE, 'race_id': 'KM-LOCAL-FNB-20261105-R09-RESEARCH',
        'index_cells': 58, 'completion_reused': True, 'new_engine_executions_this_call': 0,
        'output_directory': str(tmp_path / 'private'), 'formal_final': False,
        'recipient_delivery_proven': False, 'registered_OOS_increment': 0}
    monkeypatch.setattr(r, 'run_intent', lambda path: expected)
    monkeypatch.setattr(entry, 'run', lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('FORMAL_CALLED')))
    monkeypatch.setattr(sys, 'argv', ['entry', '--research-intent', str(descriptor)])
    assert entry.main() == 0
    result = json.loads(capsys.readouterr().out)
    assert result == expected
    assert not (tmp_path / 'entry_report.json').exists()


def test_completed_manifest_reuse_rejects_foreign_identity_or_forged_formal_scope(tmp_path):
    recipe = {'source_sha256': 'a' * 64, 'code_pins': {'module': 'b' * 64}, 'paper_policy': None}
    original = {'profile': r.PROFILE, 'classification': r.CLASSIFICATION,
        'race_id': 'KM-LOCAL-FNB-20261105-R09-RESEARCH', 'input_recipe': recipe,
        'source_sha256': recipe['source_sha256'], 'code_pins': recipe['code_pins'],
        'unadopted_paper_policy_choice': None, 'output_directory': str(tmp_path),
        'registered_OOS_increment': 0, 'private_artifacts': []}
    for key in ('provider_usage_authority_granted', 'model_adopted', 'formal_OWNER_scope_changed',
                'numerical_consumers_changed', 'independent_BC', 'actual_purchase',
                'formal_final', 'recipient_delivery_proven'):
        original[key] = False
    path = tmp_path / 'research_execution_manifest.json'; path.write_bytes(r.encoded(original))
    r._verify_saved_manifest(path, recipe=recipe, race_id=original['race_id'])
    for mutate in (lambda q: q.update(race_id='OTHER_RACE'), lambda q: q.update(formal_final=True),
                   lambda q: q.update(source_sha256='c' * 64), lambda q: q.update(code_pins={}),
                   lambda q: q.update(unadopted_paper_policy_choice='unknown-path-protection')):
        changed = deepcopy(original); mutate(changed); path.write_bytes(r.encoded(changed))
        with unittest.TestCase().assertRaisesRegex(r.ResearchHold, 'IDENTITY_OR_SCOPE_CHANGED'):
            r._verify_saved_manifest(path, recipe=recipe, race_id=original['race_id'])


def test_source_preflight_legacy_imports_are_portable_from_unrelated_cwd(tmp_path):
    import os
    import subprocess
    env = dict(os.environ); env['PYTHONPATH'] = str(r.REPO)
    code = ('from runtime.local_fnb_research_runtime import verify_source, ResearchHold\n'
            'try: verify_source({}, {}, {})\n'
            'except ResearchHold as e: print(str(e))\n')
    result = subprocess.run([sys.executable, '-c', code], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == 'SOURCE_INTENT_OR_PINNED_TRUST_MISMATCH'


def test_only_literal_empty_nonrepository_bootstrap_is_allowed(tmp_path):
    import subprocess
    empty = tmp_path / 'empty'; empty.mkdir(); (empty / '.git').mkdir()
    assert r._private_root(empty / 'private') == empty / 'private'
    repository = tmp_path / 'initialized'; repository.mkdir()
    subprocess.run(['git', 'init', '-q', str(repository)], check=True)
    with unittest.TestCase().assertRaisesRegex(r.ResearchHold, 'GIT_WORKTREE_FORBIDDEN'):
        r._private_root(repository / 'raw')
