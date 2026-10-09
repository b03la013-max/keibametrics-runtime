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


def test_post_cutoff_acquisition_preserves_fail_closed_and_reports_cause():
    observed = {}
    def call(path, payload, timeout):
        if path.endswith('/acquire'):
            return 200, {
                'receipt': {'status': 'FAIL'},
                'receipt_sha256': 'source-receipt-sha',
                'artifact': {
                    'formal_ready': False,
                    'source_freeze_at': '2026-10-09T07:11:20+00:00',
                    'errors': [
                        'SOURCE_POST_CUTOFF:NAR-OHI-20261009-R04-RACE-CARD',
                        'SOURCE_POST_CUTOFF:NAR-OHI-20261009-R04-ODDS-TANFUKU',
                    ],
                    'large_raw_payload': 'private original source stays in saved artifact',
                },
            }
        raise AssertionError('Unexpected endpoint: ' + path)
    def fail(code, details):
        observed.update(code=code, details=details)
        raise ValueError(code)
    saved = {}
    acquire = acquire_function(call, lambda k,v: saved.update({k:v}), fail)
    request = {
        'source_acquisition_request': {
            'prediction_cutoff': '2026-10-09T07:10:00+00:00',
            'sources': [{'source_id':'NAR-OHI-20261009-R04-RACE-CARD','required':True}],
        },
        'prediction_cutoff': '2026-10-09T07:10:00+00:00',
    }
    with pytest.raises(ValueError, match='SOURCE_ACQUISITION_NOT_FROZEN'):
        acquire(request, 'OHI-R04')
    assert observed['code'] == 'SOURCE_ACQUISITION_NOT_FROZEN'
    assert observed['details']['prediction_cutoff'] == request['prediction_cutoff']
    assert observed['details']['receipt_status'] == 'FAIL'
    assert observed['details']['source_errors'] == [
        'SOURCE_POST_CUTOFF:NAR-OHI-20261009-R04-RACE-CARD',
        'SOURCE_POST_CUTOFF:NAR-OHI-20261009-R04-ODDS-TANFUKU',
    ]
    assert len(observed['details']['required_post_cutoff_sources']) == 2
    assert 'source' not in observed['details']
    assert 'large_raw_payload' not in str(observed['details'])
    assert 'source_receipt_envelope.json' in saved


def test_post_cutoff_failure_hint_requires_new_id_when_cutoff_changes():
    import datetime
    import os
    node = next(
        n for n in ast.parse(Path('runtime/non_jra_formal_runner.py').read_text()).body
        if isinstance(n, ast.FunctionDef) and n.name == 'fail_closed'
    )
    saved = {}
    env = {
        'execution_id': 'KM-LOCAL-OHI-20261009-R04-LIVE-R1',
        'phase': 'SOURCE',
        'stage_manifest': [],
        'failure_class_for': lambda code: 'SOURCE_OR_RUNNER_UNIVERSE',
        'resume_hint_for': lambda code: 'RETRY_SAME_EXECUTION_ID_FROM_SOURCE',
        'persist': lambda name, value: saved.update({name: value}),
        'datetime': datetime,
        'os': os,
    }
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<fail_closed>', 'exec'), env)
    with pytest.raises(AssertionError):
        env['fail_closed']('SOURCE_ACQUISITION_NOT_FROZEN', {
            'source_errors':['SOURCE_POST_CUTOFF:NAR-OHI-20261009-R04-RACE-CARD'],
        })
    diagnostic = saved['failure_diagnostic.json']
    assert diagnostic['code'] == 'SOURCE_ACQUISITION_NOT_FROZEN'
    assert diagnostic['resume_hint'] == 'NEW_EXECUTION_ID_IF_CUTOFF_CHANGES_KEEP_PRIOR_SOURCE_BASIS'
    assert diagnostic['failure_class'] == 'SOURCE_OR_RUNNER_UNIVERSE'
