"""Exercise the shared function without running the script's live entrypoint."""
import ast
import copy
from pathlib import Path
import pytest


def acquire_function(call, persist, fail_closed):
    tree = ast.parse(Path('runtime/non_jra_formal_runner.py').read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'acquire_verified_source')
    env = dict(copy=copy, call=call, persist=persist, fail_closed=fail_closed)
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<acquire>', 'exec'), env)
    return env['acquire_verified_source']


@pytest.mark.parametrize('mode', ['discovered', 'manifest', 'request'])
@pytest.mark.parametrize('failure', [None, 'acquire', 'verify', 'readiness'])
def test_source_paths_preserve_calls_and_fail_closed(mode, failure):
    calls, saved = [], {}
    req = dict(venue_id='FNB', race_date='2026-09-29', race_no=1, prediction_cutoff='cutoff')
    if mode == 'manifest':
        req['required_source_manifest'] = [{'id': 'official'}]
    if mode == 'request':
        req['source_acquisition_request'] = {'sources': [{'id': 'official'}]}
    original = copy.deepcopy(req)
    def call(path, payload, timeout):
        calls.append((path, copy.deepcopy(payload), timeout))
        if path.endswith('/local'):
            return 200, {'sources': [{'id': 'official'}]}
        if path.endswith('/acquire'):
            return 200, {'receipt': {'status': 'FAILED' if failure == 'acquire' else 'SOURCE_FROZEN'},
                         'artifact': {'formal_ready': failure != 'readiness'}}
        return 200, {'valid': failure != 'verify'}
    def fail(code, details):
        raise ValueError(code)
    acquire = acquire_function(call, lambda k,v: saved.update({k:v}), fail)
    if failure:
        expected = {'acquire': 'SOURCE_ACQUISITION_NOT_FROZEN', 'verify': 'SOURCE_SIGNATURE_OR_ARTIFACT_VERIFY_FAILED', 'readiness': 'SOURCE_NOT_FORMAL_READY'}[failure]
        with pytest.raises(ValueError, match=expected):
            acquire(req, 'race')
    else:
        source, artifact = acquire(req, 'race')
        assert artifact['formal_ready']
        assert saved['source_verification.json']['valid']
    assert req == original
    acquisition = next(c for c in calls if c[0].endswith('/acquire'))
    assert acquisition[1]['race_id'] == 'race'
    assert acquisition[1]['family_id'] == 'LOCAL'
    assert acquisition[1]['prediction_cutoff'] == 'cutoff'
    assert sum(c[0].endswith('/acquire') for c in calls) == 1
