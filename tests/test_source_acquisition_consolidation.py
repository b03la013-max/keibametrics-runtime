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


def _source_consumer_endpoints():
    """Exercise existing endpoints with crypto/signers stubbed, never a POST."""
    import types
    from runtime.local_physical.source_acquisition import SOURCE_PROFILE
    source = Path('runtime/local_physical/app_v15.py').read_text()
    nodes = {n.name:n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)}
    calls = []
    class EndpointHold(Exception):
        def __init__(self, status, detail):
            self.status, self.detail = status, detail
            super().__init__(detail)
    legacy = types.SimpleNamespace(validate_family=lambda p:None, verify_envelope=lambda p:True,
        pre_krs=lambda p:calls.append('pre_krs') or {'receipt':{'status':'NO_SIGNING_TEST'}},
        final=lambda p:calls.append('final') or {'receipt':{'status':'NO_SIGNING_TEST'}},
        SIGNER='SYNTHETIC_ONLY', FAMILY='LOCAL')
    scope = {'Dict':dict, 'Any':object, 'legacy':legacy, 'HTTPException':EndpointHold,
        'verify_source_artifact':lambda artifact:(True, []), 'SOURCE_PROFILE':SOURCE_PROFILE,
        'NAR_MANIFEST_PROFILE':'KM-LOCAL-NAR-SOURCE-MANIFEST-v1.0-20260923',
        'validate_krs_horses':lambda source,data:(data.get('valid', False), ['TEST_RUNNER_MISMATCH'])}
    for name in ('_require_source_receipt','source_verify','pre_krs','final'):
        node=nodes[name];node.decorator_list=[]
        exec(compile(ast.Module(body=[node],type_ignores=[]),'existing_source_consumer_endpoints','exec'), scope)
    return scope, calls, EndpointHold


def _source_consumer_payload(profile):
    return {'race_id':'SYNTHETIC-URW-CONSUMER',
        'source_receipt':{'receipt':{'phase':'SOURCE','status':'SOURCE_FROZEN','race_id':'SYNTHETIC-URW-CONSUMER'},
            'artifact':{'source_manifest_profile':profile,
                'official_runner_universe':{'runners':[{'runner_id':'1'}]}}},
        'krs_input_data':{'valid':True}, 'final_prediction_package':{'ranking':[1]},
        'final_ticket':{'tickets':[{'selection':[1],'stake':100}]}}


@pytest.mark.parametrize('profile', [None, '', 'UNKNOWN', 'NANKAN_OFFICIAL', 'KM-URW-NANKAN-PRIVATE-REFERENCE-v1'])
@pytest.mark.parametrize('endpoint', ['pre_krs','final'])
def test_unknown_source_consumer_never_reaches_formal_handler(profile, endpoint):
    scope, calls, Hold = _source_consumer_endpoints()
    with pytest.raises(Hold, match='SOURCE_CONSUMER_NOT_AUTHORIZED'):
        scope[endpoint](_source_consumer_payload(profile))
    assert calls == []


@pytest.mark.parametrize('endpoint', ['pre_krs','final'])
def test_current_nar_consumer_preserves_valid_universe_handler(endpoint):
    scope, calls, _ = _source_consumer_endpoints()
    scope[endpoint](_source_consumer_payload(scope['NAR_MANIFEST_PROFILE']))
    assert calls == [endpoint]


@pytest.mark.parametrize('endpoint', ['pre_krs','final'])
def test_current_nar_consumer_still_rejects_invalid_universe(endpoint):
    scope, calls, Hold = _source_consumer_endpoints()
    payload = _source_consumer_payload(scope['NAR_MANIFEST_PROFILE'])
    if endpoint == 'pre_krs':payload['krs_input_data']['valid'] = False
    else:payload['final_ticket']['tickets'][0]['selection'] = [999]
    with pytest.raises(Hold, match='SOURCE_(?:FINAL_)?RUNNER_UNIVERSE_MISMATCH'):
        scope[endpoint](payload)
    assert calls == []


def test_generic_source_signature_verification_does_not_grant_formal_consumer():
    scope, calls, Hold = _source_consumer_endpoints()
    payload = _source_consumer_payload('UNREGISTERED-NANKAN-SYNTHETIC')
    # The SOURCE-only verification endpoint remains distinct from consumption.
    result = scope['source_verify'](payload['source_receipt'])
    assert result['verified'] is True and result['signature_valid'] is True
    with pytest.raises(Hold, match='SOURCE_CONSUMER_NOT_AUTHORIZED'):
        scope['pre_krs'](payload)
    assert calls == []


def test_signature_failure_remains_first_source_failure():
    scope, calls, Hold = _source_consumer_endpoints()
    scope['legacy'].verify_envelope = lambda p:False
    with pytest.raises(Hold, match='SOURCE_RECEIPT_SIGNATURE_INVALID'):
        scope['pre_krs'](_source_consumer_payload('UNREGISTERED'))
    assert calls == []
