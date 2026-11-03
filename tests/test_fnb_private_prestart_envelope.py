"""Execution-envelope regressions; fixtures are never claimed as LIVE runs."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from runtime import local_fnb_research_runtime as r


def stamp(value):
    return datetime.fromisoformat(value).astimezone(timezone.utc)


@pytest.fixture
def assets(tmp_path, monkeypatch):
    request = {'family_id': 'LOCAL', 'venue_id': 'FNB', 'race_date': '2026-11-04',
        'race_no': 2, 'race_id': 'KM-LOCAL-FNB-20261104-R02-TEST',
        'prediction_cutoff': '2026-11-04T14:10:00+09:00',
        'scheduled_post_at': '2026-11-04T14:15:00+09:00'}
    source = {'source_freeze_at': '2026-11-04T14:01:00+09:00',
        'source_snapshot_sha256': 'e' * 64,
        'sources': [{'official': True, 'fetched_at': '2026-11-04T14:00:00+09:00'}]}
    decision = {'profile': 'KM-FNB-FIXED-CONTEXT-PRIVATE-OWNER-EXECUTION-DECISION-20261103-R1',
        'decision': 'APPROVED_FIXED_MODEL_PRIVATE_NONPRODUCTION_RESEARCH_USE',
        'model_id': 'KM-FNB-CONTEXT-PARETO-STATIC-RESEARCH-v0.1-20261103',
        'model_version': '0.1', 'model_code_sha256': r.MODEL_SHA,
        'model_profile_sha256': r.MODEL_PROFILE_SHA,
        'authority_evidence': {'type': 'DIRECT_USER_INSTRUCTION_IN_CURRENT_CHAT',
            'owner_identity_confirmed_by_direct_instruction': True,
            'record_is_crypto_signature': False, 'request_id': 'TEST-OWNER-INSTRUCTION'},
        'authorization_observed_at': '2026-11-04T13:00:00+09:00',
        'permitted_scope': {'classification': r.PRESTART_CLASSIFICATION,
            'family_id': 'LOCAL', 'venue_id': 'FNB',
            'purpose': 'WHOLLY_PRIVATE_NONCOMMERCIAL_RESEARCH',
            'races_by_date': {'2026-11-04': [2]}},
        'selection_policy': 'EXISTING_ORIGINAL_STRICT_MEC_ONLY_NEW_PROTECTION_POLICY_NOT_ADOPTED'}
    for key in ('production_owner_adoption', 'production_scope_changed',
            'numerical_policy_changed', 'signing_key_created_or_changed',
            'independent_BC_authorized_by_this_record', 'actual_purchase_authorized'):
        decision[key] = False
    clock = {'value': stamp('2026-11-04T14:05:00+09:00')}
    monkeypatch.setattr(r, '_actual_clock', lambda: clock['value'])

    def original(doc, name='decision.json'):
        data = r.encoded(doc); path = tmp_path / name; path.write_bytes(data)
        return path, r.digest(data)

    return request, source, decision, clock, original


def test_exact_dated_private_approval_is_not_a_provider_or_production_grant(assets):
    request, source, decision, clock, original = assets
    path, pin = original(decision)
    proof, data = r.verify_private_owner_decision(path, pin, request=request, source=source)
    assert data == path.read_bytes()
    assert proof['classification'] == r.PRESTART_CLASSIFICATION
    assert proof['model_code_sha256'] == r.MODEL_SHA
    assert proof['provider_rights_granted'] is False
    assert proof['production_scope_changed'] is False
    assert proof['owner_signature_claimed'] is False


@pytest.mark.parametrize('change', [
    lambda d: d.update(model_code_sha256='0' * 64),
    lambda d: d.update(model_profile_sha256='0' * 64),
    lambda d: d['permitted_scope'].update(races_by_date={'2026-11-04': [3]}),
    lambda d: d['permitted_scope'].update(classification='PRODUCTION'),
    lambda d: d['authority_evidence'].update(owner_identity_confirmed_by_direct_instruction=False),
    lambda d: d.update(numerical_policy_changed=True),
    lambda d: d.update(selection_policy='NEW_UNKNOWN_PROTECTION_POLICY'),
])
def test_wrong_model_race_policy_or_scope_is_rejected(assets, change):
    request, source, decision, clock, original = assets
    change(decision); path, pin = original(decision)
    with pytest.raises(r.ResearchHold, match='DECISION_SCOPE_OR_MODEL_MISMATCH'):
        r.verify_private_owner_decision(path, pin, request=request, source=source)


def test_owner_record_byte_tampering_is_rejected(assets):
    request, source, decision, clock, original = assets
    path, pin = original(decision); path.write_bytes(path.read_bytes() + b' ')
    with pytest.raises(r.ResearchHold, match='PINNED_ORIGINAL_BYTES_MISMATCH'):
        r.verify_private_owner_decision(path, pin, request=request, source=source)


def test_earlier_eligible_source_is_allowed_but_future_approval_and_expired_cutoff_are_rejected(assets):
    request, source, decision, clock, original = assets
    decision['authorization_observed_at'] = '2026-11-04T14:02:00+09:00'
    path, pin = original(decision)
    proof, _ = r.verify_private_owner_decision(path, pin, request=request, source=source)
    assert stamp(proof['approved_at']) > stamp(source['source_freeze_at'])
    decision['authorization_observed_at'] = '2026-11-04T14:06:00+09:00'
    path, pin = original(decision)
    with pytest.raises(r.ResearchHold, match='DECISION_NOT_YET_EFFECTIVE'):
        r.verify_private_owner_decision(path, pin, request=request, source=source)
    decision['authorization_observed_at'] = '2026-11-04T13:00:00+09:00'
    path, pin = original(decision)
    clock['value'] = stamp(request['prediction_cutoff'])
    with pytest.raises(r.ResearchHold, match='CUTOFF_EXPIRED_NOT_NO_BET'):
        r.verify_private_owner_decision(path, pin, request=request, source=source)


@pytest.mark.parametrize('cutoff', ['2026-11-04T14:10:01+09:00', '2026-11-04T14:09:59+09:00'])
def test_approved_prestart_cutoff_cannot_be_shortened_or_extended(assets, cutoff):
    request, source, decision, clock, original = assets
    request['prediction_cutoff'] = cutoff
    path, pin = original(decision)
    with pytest.raises(r.ResearchHold, match='APPROVED_CUTOFF_300_SECONDS_REQUIRED'):
        r.verify_private_owner_decision(path, pin, request=request, source=source)


def prepare_orchestration(assets, monkeypatch, tmp_path):
    """Isolate external calculation; verify the runtime's real stage ordering."""
    from runtime import local_fnb_r13_private_single_numeric as numeric
    from runtime import local_fnb_observation_context as observations
    from runtime import local_fnb_context_static_candidate as model
    from runtime import local_fnb_semantic_closure as semantic
    request, source, decision, clock, original = assets
    paths = {}
    for key, doc in (('source', {}), ('request', request), ('trust', {}), ('owner_decision', decision)):
        paths[key] = original(doc, key + '.json')
    calls = []

    def verified(envelope, supplied_request, trust):
        calls.append('SOURCE_SIGNATURE_AND_ADMISSION'); return deepcopy(source)

    def calculate(**kwargs):
        calls.append(('NUMERICAL', kwargs['diagnostic_only']))
        folder = kwargs['private_root'] / request['race_id']; folder.mkdir()
        (folder / 'numerical_materialization.json').write_bytes(r.encoded({'runners': [{'runner_id': '1'}, {'runner_id': '2'}]}))
        (folder / 'all_horse_29_index_report.md').write_text('TEST FIXTURE, NOT LIVE')
        return {'private_root': str(folder)}

    def prediction(context, **kwargs):
        calls.append('STATIC')
        return {'active_runners': ['1', '2'], 'PRE_KRS_input': {}, 'classification': model.CLASSIFICATION,
            'model_id': model.MODEL_ID, 'model_version': '0.1', 'sha256': 'b' * 64}

    def krs(*args, **kwargs):
        calls.append('KRS'); return {'new_engine_execution': True}

    def strict(*args, **kwargs):
        calls.append('STRICT_MEC'); return {'status': 'HOLD_UNRESOLVED_SEMANTICS_NOT_NO_BET'}

    def render(*args, **kwargs):
        calls.append(('BODY', kwargs['private_owner_decision'] is not None))
        return b'TEST FIXTURE, NOT LIVE\n'

    monkeypatch.setattr(r, 'verify_source', verified)
    monkeypatch.setattr(numeric, 'execute', calculate)
    monkeypatch.setattr(observations, 'build_observation_packet', lambda *a, **k: {})
    monkeypatch.setattr(model, 'build_context', lambda *a, **k: {})
    monkeypatch.setattr(model, 'predict', prediction)
    monkeypatch.setattr(r, 'build_upstream', lambda *a, **k: ({}, []))
    monkeypatch.setattr(r, 'execute_krs', krs)
    monkeypatch.setattr(semantic, 'assess_semantics', lambda *a, **k: {})
    monkeypatch.setattr(semantic, 'execute_strict_mec', strict)
    monkeypatch.setattr(r, '_render_private_body', render)
    cache = tmp_path / 'cache'; cache.mkdir(); receipt = r.encoded({})
    (cache / 'context_receipt.json').write_bytes(receipt)
    options = {'private_root': tmp_path / 'private', 'krs_cache': cache,
        'krs_cache_receipt_sha256': r.digest(receipt)}
    for name in ('source', 'request', 'trust', 'owner_decision'):
        options[name + '_path'], options[name + '_sha256'] = paths[name]
    return options, calls, krs


def test_approved_envelope_executes_all_stages_without_asserting_delivery_or_mec_pass(assets, monkeypatch, tmp_path):
    options, calls, _ = prepare_orchestration(assets, monkeypatch, tmp_path)
    result = r.run(**options)
    assert calls == ['SOURCE_SIGNATURE_AND_ADMISSION', ('NUMERICAL', False), 'STATIC', 'KRS',
                     'STRICT_MEC', ('BODY', True)]
    assert result['classification'] == r.PRESTART_CLASSIFICATION
    assert result['fixed_model_private_use_verified'] is True
    assert result['completion_before_cutoff'] is True
    assert result['recipient_delivery_proven'] is False
    assert result['formal_final'] is False
    assert result['independent_BC'] is False
    assert result['model_adopted'] is False
    assert result['original_strict_MEC']['status'].startswith('HOLD_')
    assert result['paper_hypothesis_executed_separately'] is False
    assert r.digest((r.REPO / 'runtime/local_fnb_context_static_candidate.py').read_bytes()) == r.MODEL_SHA
    manifest = Path(result['output_directory']) / 'research_execution_manifest.json'
    r._verify_saved_manifest(manifest, recipe=result['input_recipe'], race_id=result['race_id'])


def test_cutoff_expiring_during_krs_cannot_publish_prestart_completion(assets, monkeypatch, tmp_path):
    options, calls, previous = prepare_orchestration(assets, monkeypatch, tmp_path)
    request, source, decision, clock, original = assets

    def slow_krs(*args, **kwargs):
        result = previous(*args, **kwargs); clock['value'] = stamp(request['prediction_cutoff']); return result

    monkeypatch.setattr(r, 'execute_krs', slow_krs)
    with pytest.raises(r.ResearchHold, match='CUTOFF_EXPIRED_NOT_NO_BET'):
        r.run(**options)
    assert 'STRICT_MEC' not in calls
    assert not list(options['private_root'].rglob('research_execution_manifest.json'))


def test_final_manifest_write_crossing_cutoff_is_rejected_and_cannot_be_reused(assets, monkeypatch, tmp_path):
    options, calls, _ = prepare_orchestration(assets, monkeypatch, tmp_path)
    request, source, decision, clock, original = assets
    original_write = r._immutable

    def boundary_write(path, data):
        result = original_write(path, data)
        if Path(path).name == 'research_execution_manifest.json':
            clock['value'] = stamp(request['prediction_cutoff'])
        return result

    monkeypatch.setattr(r, '_immutable', boundary_write)
    with pytest.raises(r.ResearchHold, match='CUTOFF_EXPIRED_NOT_NO_BET'):
        r.run(**options)
    manifest = next(options['private_root'].rglob('research_execution_manifest.json'))
    assert (manifest.parent / 'prestart_finalization_failure.json').is_file()
    with pytest.raises(r.ResearchHold, match='FINAL_SAVE_EXPIRED'):
        r._verify_saved_manifest(manifest)


def test_actual_static_save_is_later_than_model_input_asof(assets, monkeypatch, tmp_path):
    options, calls, _ = prepare_orchestration(assets, monkeypatch, tmp_path)
    from runtime import local_fnb_context_static_candidate as model
    previous = model.predict
    clock = assets[3]

    def slow_prediction(*args, **kwargs):
        result = previous(*args, **kwargs)
        clock['value'] = stamp('2026-11-04T14:06:00+09:00')
        return result

    monkeypatch.setattr(model, 'predict', slow_prediction)
    result = r.run(**options)
    assert stamp(result['model_input_asof']) < stamp(result['static_freeze_at'])
    assert result['static_freeze_at'] == clock['value'].isoformat()


def test_saved_owner_proof_is_bound_to_immutable_decision_record(assets, monkeypatch, tmp_path):
    options, calls, _ = prepare_orchestration(assets, monkeypatch, tmp_path)
    result = r.run(**options)
    manifest = Path(result['output_directory']) / 'research_execution_manifest.json'
    changed = json.loads(manifest.read_bytes())
    changed['private_owner_decision']['owner_request_id'] = 'OTHER-INSTRUCTION'
    manifest.write_bytes(r.encoded(changed))
    # Even recomputing the unsigned save receipt cannot change the pinned
    # Owner instruction or bind a different request to that original.
    receipt_path = manifest.parent / 'prestart_finalization_receipt.json'
    receipt = json.loads(receipt_path.read_bytes())
    receipt['manifest_sha256'] = r.digest(manifest.read_bytes())
    receipt_path.write_bytes(r.encoded(receipt))
    with pytest.raises(r.ResearchHold, match='COMPLETED_PRIVATE_PRESTART_PROOF_CHANGED'):
        r._verify_saved_manifest(manifest, recipe=result['input_recipe'], race_id=result['race_id'])


def test_default_diagnostic_and_real_source_gate_remain_unchanged(assets, monkeypatch, tmp_path):
    options, calls, _ = prepare_orchestration(assets, monkeypatch, tmp_path)
    options.pop('owner_decision_path'); options.pop('owner_decision_sha256')
    options['now'] = assets[3]['value']
    result = r.run(**options)
    assert result['classification'] == r.CLASSIFICATION
    assert ('NUMERICAL', True) in calls
    assert ('BODY', False) in calls
    assert 'fixed_model_private_use_verified' not in result
    assert result['recipient_delivery_proven'] is False


def test_prestart_cannot_use_asof_override_or_new_paper_policy(assets, monkeypatch, tmp_path):
    options, calls, _ = prepare_orchestration(assets, monkeypatch, tmp_path)
    with pytest.raises(r.ResearchHold, match='ASOF_OVERRIDE_FORBIDDEN'):
        r.run(**options, now=assets[3]['value'])
    with pytest.raises(r.ResearchHold, match='ONLY_EXISTING_STRICT_MEC_AUTHORIZED'):
        r.run(**options, paper_policy='unknown-path-protection')
    assert not any(isinstance(c, tuple) and c[0] == 'NUMERICAL' for c in calls)


def test_approval_cannot_bypass_actual_source_verification(assets, tmp_path):
    request, source, decision, clock, original = assets
    path, pin = original(decision)
    source_path, source_pin = original({}, 'source.json')
    request_path, request_pin = original(request, 'request.json')
    trust_path, trust_pin = original({}, 'trust.json')
    with pytest.raises(r.ResearchHold, match='SOURCE_INTENT_OR_PINNED_TRUST_MISMATCH'):
        r.run(source_path=source_path, source_sha256=source_pin,
            request_path=request_path, request_sha256=request_pin,
            trust_path=trust_path, trust_sha256=trust_pin, private_root=tmp_path / 'private',
            owner_decision_path=path, owner_decision_sha256=pin)
    assert not (tmp_path / 'private').exists()


def test_valid_completed_prestart_original_is_readable_after_cutoff_without_new_calculation(assets, monkeypatch, tmp_path):
    options, calls, _ = prepare_orchestration(assets, monkeypatch, tmp_path)
    first = r.run(**options)
    folder = Path(first['output_directory'])
    before = {str(p.relative_to(folder)): p.read_bytes() for p in folder.rglob('*') if p.is_file()}
    calls.clear()
    assets[3]['value'] = stamp(assets[0]['scheduled_post_at'])
    reused = r.run(**options)
    assert calls == ['SOURCE_SIGNATURE_AND_ADMISSION']
    assert reused['completion_reused'] is True
    assert reused['new_engine_executions_this_call'] == 0
    assert reused['prestart_computation_completed_at'] == first['prestart_computation_completed_at']
    assert reused['recipient_delivery_proven'] is False
    after = {str(p.relative_to(folder)): p.read_bytes() for p in folder.rglob('*') if p.is_file()}
    assert after == before


def test_new_prestart_execution_stays_blocked_after_cutoff(assets, monkeypatch, tmp_path):
    options, calls, _ = prepare_orchestration(assets, monkeypatch, tmp_path)
    assets[3]['value'] = stamp(assets[0]['prediction_cutoff'])
    with pytest.raises(r.ResearchHold, match='CUTOFF_EXPIRED_NOT_NO_BET'):
        r.run(**options)
    assert calls == ['SOURCE_SIGNATURE_AND_ADMISSION']
    assert not list(options['private_root'].rglob('run_started.json'))
