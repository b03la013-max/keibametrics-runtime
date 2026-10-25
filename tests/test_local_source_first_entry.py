import json
from types import SimpleNamespace
from pathlib import Path
import pytest
from runtime import formal_execution_orchestrator as o
from urw_reference_fixture_support import fixture_root

SYNTHETIC_ROOT=fixture_root()


@pytest.fixture(autouse=True)
def synthetic_reference_store(monkeypatch,request):
    # Only reference readback tests use this store. Formal tests retain their
    # independent source/authority fixtures and explicit per-test roots.
    if request.node.originalname in {
        'test_actual_unsigned_reference_readback_never_refetches_or_recomputes',
        'test_normal_chat_returns_actual_cached_reference_and_message_without_formal_dispatch',
        'test_frozen_reference_answer_is_complete_without_refetch_or_prediction_change',
        'test_reference_completion_checks_displayed_facts_not_status_or_size',
        'test_reference_answer_rejects_different_race_source',
        'test_normal_chat_rejects_another_race_cached_in_requested_directory',
    }:
        monkeypatch.setattr(o,'ROOT',SYNTHETIC_ROOT)


def test_chat_reference_resolves_fullwidth_race_and_jst_date():
    from datetime import datetime, timezone
    from runtime.local_race_entry import resolve_chat_intent
    value = resolve_chat_intent('浦和５Ｒのケイバメトリクス調査願います',
        now=datetime(2026, 10, 18, 16, tzinfo=timezone.utc))
    assert value == {'family_id': 'LOCAL', 'venue_id': 'URW', 'race_date': '2026-10-19',
                     'race_no': 5, 'prediction_mode': 'AUTO', 'requested_formal': False}


@pytest.mark.parametrize('text', ['浦和13R', '浦和2Rと浦和3R', '浦和2Rと3R', '明日の浦和2R', '川崎2R', '浦和2Rと大井2R',
    '2026-10-19と2026-10-20の浦和2R'])
def test_chat_ambiguous_or_foreign_race_cannot_dispatch(text):
    from runtime.local_race_entry import resolve_chat_intent
    with pytest.raises(ValueError):
        resolve_chat_intent(text)


def test_reference_routes_before_formal_authority_and_never_publishes(monkeypatch, tmp_path):
    from runtime import local_race_entry as entry
    monkeypatch.setattr(o, 'validate_request_context', lambda *a: pytest.fail('REFERENCE MUST NOT ENTER FORMAL'))
    monkeypatch.setattr(entry, 'run_reference', lambda *a, **k: {'status': 'REFERENCE_AVAILABLE'})
    intent = {'prediction_mode': 'REFERENCE'}
    assert entry.run(intent, output=tmp_path, run_id='contract')['status'] == 'REFERENCE_AVAILABLE'
    with pytest.raises(ValueError, match='CANNOT_PUBLISH'):
        entry.run(intent, output=tmp_path, run_id='contract', checkpoint_publisher=lambda *a: None)
    with pytest.raises(ValueError, match='MODE_INVALID'):
        entry.run({'prediction_mode': 'FAKE_FORMAL'}, output=tmp_path, run_id='contract')


def test_actual_unsigned_reference_readback_never_refetches_or_recomputes(monkeypatch, tmp_path):
    import shutil
    from runtime import local_race_entry as entry
    from scripts import urw_candidate_krs_replay as capture
    original = SYNTHETIC_ROOT/'research/urw_owner/20261019_prediction_availability/chat_R05'
    for name in ('reference_prediction.json', 'reference_prediction.md', 'reference_source.json',
                 'reference_intent.json', 'entry_report.json'):
        shutil.copyfile(original/name, tmp_path/name)
    monkeypatch.setattr(capture, 'capture_public_urw_sources', lambda *a, **k: pytest.fail('CACHE MUST NOT FETCH'))
    intent = {**entry.resolve_chat_intent('2026-10-19 浦和5Rのケイバメトリクス調査願います'), 'prediction_mode':'REFERENCE'}
    before = (tmp_path/'reference_prediction.json').read_bytes()
    report = entry.run(intent, output=tmp_path, run_id='readback-contract')
    assert report['reference_readback_only'] and report['source_freshness_claim'] is False
    assert report['formal_final_proven'] is report['prediction_reexecution'] is False
    assert (tmp_path/'reference_prediction.json').read_bytes() == before
    (tmp_path/'reference_prediction.md').write_text('TAMPER')
    with pytest.raises(ValueError, match='NO_REEXECUTION'):
        entry.run(intent, output=tmp_path, run_id='tamper-contract')
    assert (tmp_path/'reference_prediction.json').read_bytes() == before


def test_normal_chat_returns_actual_cached_reference_and_message_without_formal_dispatch(monkeypatch, tmp_path):
    from runtime import local_race_entry as entry
    from scripts import urw_candidate_krs_replay as capture
    monkeypatch.setattr(o, 'orchestrate', lambda *a, **k: pytest.fail('blocked chat must not POST'))
    monkeypatch.setattr(capture, 'capture_public_urw_sources', lambda *a, **k: pytest.fail('saved reference must not refetch'))
    intent = entry.resolve_chat_intent('2026-10-19 浦和6Rのケイバメトリクス調査願います')
    result = entry.run(intent, output=tmp_path, run_id='normal-chat-contract')
    assert result['status'] == 'FORMAL_BLOCKED_REFERENCE_AVAILABLE'
    assert result['formal_final_proven'] is False
    assert result['reference']['reference_readback_only'] is True
    assert 'NON-PRODUCTION / NON-FORMAL / REFERENCE ONLY' in result['message']
    assert all(r['name'] in result['message'] for r in json.loads(
        (o.ROOT/'research/urw_owner/20261019_prediction_availability/reference_repair/R06/reference_prediction.json').read_text())['runners'])
    assert 'UNKNOWN' in result['message']
    assert (tmp_path/'chat_response.md').read_text() == result['message']
    assert result['delivery']['formal_delivery_verified'] is False


def test_frozen_reference_answer_is_complete_without_refetch_or_prediction_change(monkeypatch, tmp_path):
    import hashlib
    from runtime import local_race_entry as entry
    from runtime import local_race_key_shadow_owner as owner
    from scripts import urw_candidate_krs_replay as capture
    saved = o.ROOT/'research/urw_owner/20261019_prediction_availability/reference_repair/R12'
    files = [saved/n for n in ('reference_prediction.json', 'reference_prediction.md',
                              'reference_source.json', 'reference_intent.json', 'entry_report.json')]
    before = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    monkeypatch.setattr(capture, 'capture_public_urw_sources', lambda *a, **k: pytest.fail('readback must not capture'))
    monkeypatch.setattr(owner, 'compile_reference_prediction', lambda *a, **k: pytest.fail('readback must not recompute'))
    result = entry.run(entry.resolve_chat_intent('2026-10-19 浦和12R'), output=tmp_path, run_id='frozen-answer')
    text = result['message']
    assert '秋の暮（あきのくれ）特別Ｃ３選抜馬イ' in text
    assert '13:24:40.837105+09:00' in text and '13:38:29.763527+09:00' in text
    assert 'k_raceNo=12' in text and 'Evidence SHA' in text and '最終結論' in text
    assert '- 4 キングスウェイ：参考順位UNKNOWN' in text
    assert '- 9 ルラクソント：参考順位UNKNOWN' in text
    assert '近走確認範囲' in text and '通算の「場」「距」成績ではありません' in text
    assert len([line for line in text.splitlines() if line.startswith('- ')]) == 12
    assert result['answer_content_check']['content_complete'] is True
    assert result['delivery']['chat_render_verified'] is False
    assert result['delivery']['user_acknowledgement_verified'] is False
    assert {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files} == before


@pytest.mark.parametrize('damage', ['truncate', 'omit-horse', 'change-evidence', 'search-only'])
def test_reference_completion_checks_displayed_facts_not_status_or_size(damage, tmp_path):
    from runtime import local_race_entry as entry
    result = entry.run(entry.resolve_chat_intent('2026-10-19 浦和12R'), output=tmp_path, run_id='body-negative')
    parts = result['reference']['answer_required_parts']
    body = result['message']
    if damage == 'truncate':
        body = body.split('最終結論')[0]
    elif damage == 'omit-horse':
        body = '\n'.join(line for line in body.splitlines() if not line.startswith('- 4 ')) + '補足'*2000
    elif damage == 'change-evidence':
        body = body.replace('3戦・0勝・3着内1回', '3戦・3勝・3着内3回')
    else:
        body = '回答が完了しました。7件のウェブサイトを検索しました。参考評価を示します。'
    assert entry.reference_answer_content_check(parts, body)['content_complete'] is False
    assert entry.reference_answer_content_check([], '完了')['content_complete'] is False


def test_reference_answer_rejects_different_race_source():
    from runtime import local_race_entry as entry
    base = o.ROOT/'research/urw_owner/20261019_prediction_availability/reference_repair'
    prediction = json.loads((base/'R12/reference_prediction.json').read_text())
    source = json.loads((base/'R11/reference_source.json').read_text())
    with pytest.raises(ValueError, match='SOURCE_BINDING_HOLD'):
        entry.reference_answer(prediction, source)


def test_chat_final_has_priority_over_owner_and_reference(monkeypatch, tmp_path):
    from runtime import local_race_entry as entry
    final = {'execution_id':'verified-contract-only', 'final_receipt_sha256':'verified-sha',
             'freeze_time':'original-before-cutoff', 'signature':'verified-signature', 'rendered_investment':100,
             'canonical_prediction':{'prediction_package':{'ranking':['1','2']}}, 'canonical_tree':'original vertical tree'}
    monkeypatch.setattr(entry, '_chat_final', lambda *a: (final, [final]))
    monkeypatch.setattr(entry, 'chat_formal_status', lambda *a: pytest.fail('readback cannot require current Owner'))
    monkeypatch.setattr(entry, '_chat_reference', lambda *a, **k: pytest.fail('formal content must win'))
    result = entry.run(entry.resolve_chat_intent('浦和6R'), output=tmp_path, run_id='verified-contract')
    assert result['status'] == 'FORMAL_VERIFIED'
    assert 'original vertical tree' in result['message']
    assert result['delivery']['user_acknowledgement_verified'] is False


def test_bad_final_stops_generation_but_not_independent_reference(monkeypatch, tmp_path):
    from runtime import local_race_entry as entry
    monkeypatch.setattr(entry, '_chat_final', lambda *a: (None, [{'status':'HOLD_READBACK','reason':'hash mismatch'}]))
    monkeypatch.setattr(entry, 'chat_formal_status', lambda *a: {'status':'AUTHORIZED_EXISTING_DISPATCH'})
    monkeypatch.setattr(entry, '_chat_reference', lambda *a, **k: ({'execution_id':'ref'}, 'REFERENCE ONLY'))
    from runtime import local_race_day_dispatcher as dispatcher
    monkeypatch.setattr(dispatcher, 'prepare_worker', lambda *a, **k: pytest.fail('must not overwrite damaged FINAL'))
    result = entry.run(entry.resolve_chat_intent('浦和6R'), output=tmp_path, run_id='damaged-final')
    assert result['formal']['code'] == 'EXISTING_FINAL_RECONCILIATION_REQUIRED'
    assert result['status'] == 'FORMAL_BLOCKED_REFERENCE_AVAILABLE'


def test_both_unavailable_preserves_first_failure_and_does_not_hide_reference_error(monkeypatch, tmp_path):
    from runtime import local_race_entry as entry
    monkeypatch.setattr(entry, '_chat_final', lambda *a: (None, []))
    monkeypatch.setattr(entry, 'chat_formal_status', lambda *a: {'status':'BLOCKED','first_failed_stage':'ACTIVATION','code':'DATED_OWNER_APPROVAL_REQUIRED'})
    def missing(*a, **k):
        raise ValueError('REFERENCE_DECLARED_UNIVERSE_MISMATCH')
    monkeypatch.setattr(entry, '_chat_reference', missing)
    result = entry.run(entry.resolve_chat_intent('浦和6R'), output=tmp_path, run_id='missing-reference')
    assert result['status'] == 'BOTH_UNAVAILABLE'
    assert 'DATED_OWNER_APPROVAL_REQUIRED' in result['message']
    assert 'REFERENCE_DECLARED_UNIVERSE_MISMATCH' in result['message']


@pytest.mark.parametrize('worker_status,expected', [
    ('DISPATCH_ACKNOWLEDGED_MONITOR_CHECKPOINTS','FORMAL_PENDING_REFERENCE_AVAILABLE'),
    ('DEADLINE_HOLD_NO_RETROACTIVE_START','FORMAL_BLOCKED_REFERENCE_AVAILABLE')])
def test_chat_authorized_route_reuses_scoped_existing_worker(monkeypatch, tmp_path, worker_status, expected):
    from runtime import local_race_entry as entry
    from runtime import local_race_day_dispatcher as dispatcher
    path = tmp_path/'plan.json'
    path.write_text('{}')
    eid = 'KM-LOCAL-URW-20990101-R06-LIVE-R1'
    monkeypatch.setattr(entry, '_chat_final', lambda *a: (None, []))
    monkeypatch.setattr(entry, 'chat_formal_status', lambda *a: {'status':'AUTHORIZED_EXISTING_DISPATCH',
        'plan_path':str(path),'approval_path':str(tmp_path/'approval.json'),'execution_id':eid})
    monkeypatch.setattr(entry, '_chat_reference', lambda *a, **k: ({'execution_id':'reference'}, 'REFERENCE ONLY'))
    seen = []
    def worker(*a, **k):
        seen.append(k['only_execution_id'])
        return {}, lambda: {'races':{eid:{'status':worker_status}}}
    monkeypatch.setattr(dispatcher, 'prepare_worker', worker)
    result = entry.run(entry.resolve_chat_intent('2099-01-01 浦和6R'), output=tmp_path/'out', run_id='scoped-contract')
    assert seen == [eid]
    assert result['formal_final_proven'] is False
    assert result['status'] == expected
    assert result['formal_dispatch']['status'] == worker_status


def test_normal_chat_rejects_another_race_cached_in_requested_directory(monkeypatch, tmp_path):
    import shutil
    from runtime import local_race_entry as entry
    from scripts import urw_candidate_krs_replay as capture
    original = o.ROOT/'research/urw_owner/20261019_prediction_availability/reference_repair/R05'
    for name in ('reference_prediction.json', 'reference_prediction.md', 'reference_source.json',
                 'reference_intent.json', 'entry_report.json'):
        shutil.copyfile(original/name, tmp_path/name)
    before = (tmp_path/'reference_prediction.json').read_bytes()
    monkeypatch.setattr(capture, 'capture_public_urw_sources', lambda *a, **k: pytest.fail('mismatch cannot regenerate'))
    result = entry.run(entry.resolve_chat_intent('2026-10-19 浦和6R'), output=tmp_path, run_id='wrong-cache')
    assert result['status'] == 'BOTH_UNAVAILABLE'
    assert result['reference']['code'] == 'REFERENCE_OUTPUT_ALREADY_EXISTS_NO_REEXECUTION'
    assert (tmp_path/'reference_prediction.json').read_bytes() == before


def test_normal_chat_cannot_override_race_identity_with_execution_id(tmp_path):
    from runtime import local_race_entry as entry
    intent = {**entry.resolve_chat_intent('浦和6R'), 'execution_id':'another-race'}
    with pytest.raises(ValueError, match='CHAT_IDENTITY_MUST_BE_RESOLVED'):
        entry.run(intent, output=tmp_path, run_id='identity-contract')


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
        assert calls[-2] == ('PUBLISHED', ['runtime/formal_intents/race.json'])
        assert q['static_prediction_frozen'] is True
        assert q['static_prediction']['ranking'] == ['1', '2']
        assert q['race_id'] == 'race'
        return {'status': 'FULL_LIFECYCLE_EXECUTION_PASS', 'completion': {'complete': True}}
    monkeypatch.setattr(o, 'orchestrate', orchestration)
    monkeypatch.setattr(e, 'assess', lambda: {'status': 'READY', 'required_indices': ['SSI']})
    monkeypatch.setattr(e, 'materialize_production', lambda *a: {'strict_full_numerical_ready': True})
    report = e.run({**request(), 'analysis_only': analysis_only}, output=tmp_path/'out', run_id='test',
                   checkpoint_publisher=lambda paths: calls.append(('PUBLISHED', paths)))
    if analysis_only:
        assert calls == ['SOURCE', ('PUBLISHED', ['runtime/executions/race/SOURCE'])]
        assert report['code'] == 'ANALYSIS_ONLY_SOURCE_COMPLETE'
        assert json.loads((tmp_path/'out/static_owner_input.json').read_text())['static_generation_allowed'] is False
    else:
        assert calls == ['SOURCE', ('PUBLISHED', ['runtime/executions/race/SOURCE']),
                         ('PUBLISHED', ['runtime/formal_intents/race.json']), 'FORMAL']
        assert report['completion']['complete'] is True
    assert report['owner_resolution']['input_mode'] == 'CANONICAL_FORMAL_INTENT'

@pytest.mark.parametrize('complete', [True, False])
def test_existing_final_readback_never_reacquires_or_regenerates(monkeypatch, tmp_path, complete):
    from runtime import local_race_entry as e
    monkeypatch.setattr(o, 'ROOT', tmp_path)
    monkeypatch.setattr(o, 'validate_request_context', lambda *a: None)
    monkeypatch.setattr(o, 'resolve_phase', lambda eid, phase: {
        'manifest': {'files': {'final_receipt_envelope.json': 'hash'}}} if phase == 'FORMAL' else None)
    monkeypatch.setattr(o, 'check_deadline', lambda *a, **k: pytest.fail('readback is not generation'))
    monkeypatch.setattr(e, 'build_formal_static', lambda *a, **k: pytest.fail('no new Static'))
    monkeypatch.setattr(e, 'materialize_production', lambda *a, **k: pytest.fail('no new numerical'))
    path = tmp_path/'runtime/formal_intents/race.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'execution_id': 'race', 'race_id': 'race',
        'static_prediction': {'ranking': ['1']}, 'prediction_cutoff': '2000-01-01T00:00:00Z'}))
    def readback(q, **kwargs):
        assert q['execution_phase'] == 'FORMAL'
        assert q['static_prediction']['ranking'] == ['1']
        assert 'analysis_only' not in q
        return {'status': 'ALREADY_COMPLETE' if complete else 'HOLD',
                'completion': {'complete': complete}}
    monkeypatch.setattr(o, 'orchestrate', readback)
    result = e.run({'execution_id': 'race'}, output=tmp_path/'out', run_id='retry')
    assert result['readback_only'] is True
    assert result['prediction_reexecution'] is False
    assert result['completion']['complete'] is complete


@pytest.mark.parametrize('source_status,checkpoint,expected', [
    ('BLOCKED', False, 'SOURCE_TRANSPORT_HOLD'),
    ('BLOCKED', True, 'SOURCE_TRANSPORT_HOLD'),
    ('SOURCE_PASS', False, 'SOURCE_CHECKPOINT_MISSING_AFTER_RUN'),
])
def test_source_hold_preserves_failure_and_never_enters_prediction(monkeypatch, tmp_path, source_status, checkpoint, expected):
    from runtime import local_race_entry as e
    monkeypatch.setattr(o, 'validate_request_context', lambda *a: None)
    monkeypatch.setattr(o, 'resolve_phase', lambda eid, phase: {'run_dir': tmp_path} if checkpoint and phase == 'SOURCE' else None)
    monkeypatch.setattr(o, 'check_deadline', lambda *a, **k: None)
    monkeypatch.setattr(o, 'orchestrate', lambda *a, **k: {
        'status': source_status, 'first_failed_phase': 'SOURCE',
        'first_failed_code': 'SOURCE_TRANSPORT_HOLD' if source_status == 'BLOCKED' else None})
    monkeypatch.setattr(o, 'validate_source_checkpoint', lambda *a: pytest.fail('failed SOURCE must stop before loading checkpoint'))
    monkeypatch.setattr(e, 'materialize_production', lambda *a: pytest.fail('no numerical after SOURCE HOLD'))
    monkeypatch.setattr(e, 'build_formal_static', lambda *a, **k: pytest.fail('no Static after SOURCE HOLD'))
    report = e.run({'family_id': 'LOCAL', 'execution_id': 'race', 'race_id': 'race'},
                   output=tmp_path/'out', run_id='source-hold')
    assert report['code'] == report['first_failed_code'] == expected
    assert report['first_failed_phase'] == 'SOURCE'
    assert report['completion'] is False and report['formal_final_proven'] is False
    assert report['prediction_reexecution'] is False
    assert json.loads((tmp_path/'out/entry_report.json').read_text()) == report


def test_source_is_durable_before_worker_crash_in_numerical(monkeypatch,tmp_path):
    from runtime import local_race_entry as e
    events=[]
    monkeypatch.setattr(o,'ROOT',tmp_path)
    monkeypatch.setattr(o,'validate_request_context',lambda *a:None)
    monkeypatch.setattr(o,'resolve_phase',lambda eid,phase:{'run_dir':tmp_path} if phase=='SOURCE' else None)
    monkeypatch.setattr(o,'orchestrate',lambda *a,**k:{'status':'SOURCE_PASS'})
    monkeypatch.setattr(o,'validate_source_checkpoint',lambda *a:events.append('verified-source'))
    monkeypatch.setattr(o,'_load_checkpoint_json',lambda *a:{'artifact':{'official_runner_universe':{'runners':[]}}})
    monkeypatch.setattr(e,'assess',lambda:{'status':'READY','required_indices':[]})
    def crash(*a):
        events.append('worker-crash');raise RuntimeError('WORKER_CRASH')
    monkeypatch.setattr(e,'materialize_production',crash)
    with pytest.raises(RuntimeError,match='WORKER_CRASH'):
        e.run({'execution_id':'race','race_id':'race'},output=tmp_path/'out',run_id='test',
              checkpoint_publisher=lambda paths:events.append(('durable',paths)))
    assert events==['verified-source',('durable',['runtime/executions/race/SOURCE']),'worker-crash']


def test_source_publish_conflict_stops_before_prediction(monkeypatch,tmp_path):
    from runtime import local_race_entry as e
    monkeypatch.setattr(o,'validate_request_context',lambda *a:None)
    monkeypatch.setattr(o,'resolve_phase',lambda eid,phase:{'run_dir':tmp_path} if phase=='SOURCE' else None)
    monkeypatch.setattr(o,'orchestrate',lambda *a,**k:{'status':'SOURCE_PASS'})
    monkeypatch.setattr(o,'validate_source_checkpoint',lambda *a:None)
    monkeypatch.setattr(e,'materialize_production',lambda *a:pytest.fail('no prediction before durable SOURCE'))
    def conflict(paths):raise RuntimeError('PERSIST_IMMUTABLE_OR_UNKNOWN_CONFLICT')
    with pytest.raises(RuntimeError,match='PERSIST_IMMUTABLE'):
        e.run({'execution_id':'race','race_id':'race'},output=tmp_path/'out',run_id='test',checkpoint_publisher=conflict)
