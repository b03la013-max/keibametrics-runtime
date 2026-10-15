import json
from types import SimpleNamespace
from pathlib import Path
import pytest
from runtime import formal_execution_orchestrator as o


def put_source(path, race='race', valid=True):
    path.mkdir(parents=True, exist_ok=True)
    (path/'source_receipt_envelope.json').write_text(json.dumps({
        'receipt': {'phase': 'SOURCE', 'status': 'SOURCE_FROZEN', 'family': 'LOCAL', 'race_id': race},
        'receipt_sha256': 'signed', 'signature': 'signed', 'artifact': {'formal_ready': True}}))
    (path/'source_verification.json').write_text(json.dumps({'valid': valid, 'verified': valid, 'signature_valid': valid, 'artifact_valid': valid}))


@pytest.mark.parametrize('kind', ['absent', 'wrong-race', 'unverified'])
def test_checkpoint_must_have_verified_receipt_bound_to_race(tmp_path, kind):
    if kind != 'absent':
        put_source(tmp_path, race='other' if kind == 'wrong-race' else 'race', valid=kind != 'unverified')
    with pytest.raises(o.FormalOrchestrationError, match='SOURCE_CHECKPOINT_RECEIPT_OR_VERIFICATION'):
        o.validate_source_checkpoint(tmp_path, {'race_id': 'race'})


def test_subprocess_writes_and_persists_requested_output(monkeypatch, tmp_path):
    out = tmp_path/'isolated'
    seen = []
    def runner(*args, **kwargs):
        assert kwargs['env']['KM_RUNTIME_OUT'] == str(out.resolve())
        put_source(Path(kwargs['env']['KM_RUNTIME_OUT']))
        return SimpleNamespace(returncode=0, stdout='', stderr='')
    monkeypatch.setattr(o.subprocess, 'run', runner)
    monkeypatch.setattr(o, 'persist_phase', lambda *a, **k: seen.append(a) or {})
    o.run_phase({'execution_id': 'race', 'race_id': 'race'}, 'SOURCE',
                run_id='test', github_sha='sha', runtime_out=out, tmp_root=tmp_path/'tmp')
    assert len(seen) == 1
    assert (seen[0][3]/'source_receipt_envelope.json').is_file()


def test_zero_exit_without_source_never_publishes_checkpoint(monkeypatch, tmp_path):
    monkeypatch.setattr(o.subprocess, 'run', lambda *a, **k: SimpleNamespace(returncode=0, stdout='', stderr=''))
    monkeypatch.setattr(o, 'persist_phase', lambda *a, **k: pytest.fail('empty SOURCE must not persist'))
    with pytest.raises(o.FormalOrchestrationError, match='MISSING'):
        o.run_phase({'execution_id': 'race', 'race_id': 'race'}, 'SOURCE',
                    run_id='test', github_sha='sha', runtime_out=tmp_path/'out', tmp_root=tmp_path/'tmp')


def test_source_only_resume_rejects_bare_basis_checkpoint(monkeypatch, tmp_path):
    monkeypatch.setattr(o, 'resolve_phase', lambda *a: {'run_dir': tmp_path})
    monkeypatch.setattr(o, 'source_checkpoint_compatibility', lambda *a: {'status': 'PASS'})
    with pytest.raises(o.FormalOrchestrationError, match='MISSING'):
        o.orchestrate({'family_id': 'LOCAL', 'execution_id': 'race', 'race_id': 'race',
                       'execution_phase': 'SOURCE', 'analysis_only': True}, run_id='test', github_sha='sha')


def test_race_entry_without_static_stops_after_source_and_numerical(monkeypatch, tmp_path):
    from runtime import local_race_entry as e
    monkeypatch.setattr(o, 'validate_request_context', lambda *a: None)
    monkeypatch.setattr(o, 'resolve_phase', lambda *a: {'run_dir': tmp_path})
    monkeypatch.setattr(o, 'validate_source_checkpoint', lambda *a: None)
    monkeypatch.setattr(o, '_load_checkpoint_json', lambda *a: {
        'receipt_sha256': 'signed', 'artifact': {'source_snapshot_sha256': 'snapshot', 'official_runner_universe': {'runners': [{'runner_id': '1'}]}}})
    phases = []
    def run_source(req, **kwargs):
        phases.append(req['execution_phase'])
        assert req['analysis_only'] is True
        return {'status': 'SOURCE_PASS', 'completion': False}
    monkeypatch.setattr(o, 'orchestrate', run_source)
    monkeypatch.setattr(e, 'assess', lambda: {'status': 'READY', 'required_indices': ['SSI']})
    monkeypatch.setattr(e, 'materialize_production', lambda *a: {'strict_full_numerical_ready': True})
    report = e.run({'family_id': 'LOCAL', 'execution_id': 'race', 'race_id': 'race',
                    'scheduled_post_at': '2099-01-01T12:10:00+09:00', 'prediction_cutoff': '2099-01-01T12:00:00+09:00'},
                   output=tmp_path/'out', run_id='test')
    assert phases == ['SOURCE']
    assert report['code'] == 'STATIC_PREDICTION_FREEZE_REQUIRED'
    assert report['no_bet_decision'] is False
    assert report['formal_final_proven'] is False


@pytest.mark.parametrize('intent', [{'family_id': 'JRA'}, {'execution_id': 'one', 'race_id': 'two'}])
def test_race_entry_rejects_cross_family_and_conflicting_identity(tmp_path, intent):
    from runtime.local_race_entry import run
    with pytest.raises(ValueError, match='RACE_ENTRY_'):
        run(intent, output=tmp_path, run_id='test')


def test_race_only_entry_derives_stable_identity(monkeypatch, tmp_path):
    from runtime import local_race_entry as e
    expected = 'KM-LOCAL-KAW-20990101-R08-LIVE-R1'
    monkeypatch.setattr(o, 'validate_request_context', lambda *a: {'current_authority_manifest': 'current'})
    monkeypatch.setattr(o, 'resolve_phase', lambda *a: {'run_dir': tmp_path})
    monkeypatch.setattr(o, 'validate_source_checkpoint', lambda *a: None)
    monkeypatch.setattr(o, '_load_checkpoint_json', lambda *a: {
        'receipt_sha256': 'signed', 'artifact': {'source_snapshot_sha256': 'snapshot',
        'official_runner_universe': {'runners': [{'runner_id': '1'}]}}})
    def source(req, **kwargs):
        assert req['execution_id'] == req['race_id'] == expected
        assert req['current_authority_manifest'] == 'current'
        return {'status': 'SOURCE_PASS', 'completion': False}
    monkeypatch.setattr(o, 'orchestrate', source)
    monkeypatch.setattr(e, 'assess', lambda: {'status': 'READY', 'required_indices': ['SSI']})
    monkeypatch.setattr(e, 'materialize_production', lambda *a: {'strict_full_numerical_ready': True})
    report = e.run({'venue_id': 'kaw', 'race_date': '2099-01-01', 'race_no': 8,
                    'prediction_cutoff': '2099-01-01T12:00:00+09:00',
                    'scheduled_post_at': '2099-01-01T12:10:00+09:00'}, output=tmp_path/'out', run_id='test')
    assert report['execution_id'] == expected
    assert report['owner_resolution']['c2_owner_required'] is False


@pytest.mark.parametrize("analysis_only", [False, True])
def test_entry_connects_discovered_canonical_static_to_existing_formal(monkeypatch, tmp_path, analysis_only):
    from runtime import local_race_entry as e
    from tests.test_local_static_input_resolver import request, source, frozen, put
    put(tmp_path, frozen())
    monkeypatch.setattr(o, 'ROOT', tmp_path)
    monkeypatch.setattr(o, 'validate_request_context', lambda *a: {'current_authority_manifest': 'current'})
    monkeypatch.setattr(o, 'resolve_phase', lambda *a: {'run_dir': tmp_path})
    monkeypatch.setattr(o, 'validate_source_checkpoint', lambda *a: None)
    monkeypatch.setattr(o, '_load_checkpoint_json', lambda *a: source())
    calls = []
    def orchestration(q, **kwargs):
        if q.get('analysis_only'):
            calls.append('SOURCE')
            return {'status': 'SOURCE_PASS', 'completion': False}
        calls.append('FORMAL')
        assert q['static_prediction_frozen'] is True
        assert q['static_prediction']['ranking'] == ['1', '2']
        assert q['race_id'] == 'race'
        return {'status': 'FULL_LIFECYCLE_EXECUTION_PASS', 'completion': {'complete': True}}
    monkeypatch.setattr(o, 'orchestrate', orchestration)
    monkeypatch.setattr(e, 'assess', lambda: {'status': 'READY', 'required_indices': ['SSI']})
    monkeypatch.setattr(e, 'materialize_production', lambda *a: {'strict_full_numerical_ready': True})
    report = e.run({**request(), 'analysis_only': analysis_only}, output=tmp_path/'out', run_id='test')
    if analysis_only:
        assert calls == ['SOURCE']
        assert report['code'] == 'ANALYSIS_ONLY_SOURCE_COMPLETE'
        assert json.loads((tmp_path/'out/static_owner_input.json').read_text())['static_generation_allowed'] is False
    else:
        assert calls == ['SOURCE', 'FORMAL']
        assert report['completion']['complete'] is True
    assert report['owner_resolution']['input_mode'] == 'CANONICAL_FORMAL_INTENT'
