"""Selection failure is a verified zero-exposure decision, not a fake FINAL."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(ROOT / "runtime/jra_source_runtime"))
from test_jra_aki_v21_enacted import fixture
from jra_aki_capital_preflight import sha, AKICapitalError
from jra_aki_no_bet_terminal import (record_selection_failure, terminal_eligible,
    build_aki_no_bet_terminal, diagnose, STAGE, ROUTE)
from jra_production_no_bet_terminal import verify_no_bet_terminal
from jra_production_blocker_classifier import classify_production_blockers, ROUTE_FAIL_CLOSED


def inputs(single=False):
    q, s, a = fixture()
    if single:
        for r in q['runners'][1:]:
            r['canonical_components']['ZAI_WIN']['value'] = 0
        for k in ('DCR', 'BWI', 'PRI'):
            q['runners'][0]['canonical_components'][k]['value'] = 10 if k == 'DCR' else 50
    else:
        for r in q['runners']:
            for k in ('RFI', 'PRI', 'TPI', 'F3S'):
                r['canonical_components'][k]['value'] = 50
    report = {'family_id': 'JRA', 'race_id': q['race_id'],
              'current_authority_manifest': a['manifest_id'],
              'production_full_numerical_ready': True,
              'required_index_count': len(q['runners'])*20,
              'verified_full_index_count': len(q['runners'])*20,
              'runner_universe': [r['runner_id'] for r in q['runners']],
              'prepared_numerical_request': {'runners': deepcopy(q['runners'])},
              'static_owner_activation_status': {'authorized': True},
              'static_owner_executable_diagnostic': {'static_prediction': q['static_prediction']},
              'source_checkpoint_manifest': {**{k: s[k] for k in
                  ('race_id', 'prediction_cutoff', 'source_freeze_at', 'source_snapshot_sha256')},
                  'receipt_sha256': 'c'*64}}
    record_selection_failure(report, q, s, a, root=ROOT)
    report['auto_handoff_error'] = report['aki_selection_failure']['diagnostic']['code']
    report['sha256'] = sha(report)
    intent = {'family_id': 'JRA', 'race_id': q['race_id'],
              'prediction_cutoff': s['prediction_cutoff'], 'scheduled_post_at': '2026-10-11T10:10:00+09:00'}
    return intent, report


def build(intent, report, **kwargs):
    return build_aki_no_bet_terminal(intent, report, source_receipt_verified=True,
                                    created_at='2026-10-11T10:02:00+09:00', root=ROOT, **kwargs)


def test_empty_columns_route_to_no_bet_with_actual_full20():
    intent, report = inputs()
    before = deepcopy(report)
    d = report['aki_selection_failure']['diagnostic']
    assert d['empty_columns'] == ['W', 'P2', 'P3']
    assert all('SUPPORT_GROUP_COUNT_BELOW_TWO' in r['reasons'] for r in d['selection_ledger'])
    c = classify_production_blockers(report, owner_status={'authorized': True})
    assert c['first_actual_blocked_stage'] == STAGE and c['terminal_route'] == ROUTE
    t = build(intent, report)
    v = verify_no_bet_terminal(t, require_live=True)
    assert v['actual_full20'] and v['terminal_index_count'] == 160
    assert not t['krs_executed'] and not t['signed_final_verified'] and t['tickets'] == []
    assert report == before


def test_forbidden_single_head_is_distinct_from_empty_column():
    intent, report = inputs(single=True)
    assert report['auto_handoff_error'] == 'AKI_SINGLE_HEAD_FORBIDDEN'
    assert report['aki_selection_failure']['diagnostic']['empty_columns'] == []
    assert verify_no_bet_terminal(build(intent, report))['total_investment'] == 0


@pytest.mark.parametrize('fault', ['proof', 'source', 'ledger', 'unknown', 'authorization'])
def test_invalid_failures_cannot_be_relabelled_as_evidence_no_bet(fault):
    intent, report = inputs()
    if fault == 'proof': report.pop('aki_selection_failure')
    if fault == 'source': report['source_checkpoint_manifest']['source_snapshot_sha256'] = 'b'*64
    if fault == 'ledger': report['prepared_numerical_request']['runners'][0]['canonical_components']['RFI']['value'] = 90
    if fault == 'unknown': report['auto_handoff_error'] = 'AKI_REGISTRY_FINGERPRINT_MISMATCH'
    if fault == 'authorization': report['static_owner_activation_status']['authorized'] = False
    assert not terminal_eligible(report, root=ROOT)
    with pytest.raises(ValueError): build(intent, report)
    assert classify_production_blockers(report, owner_status={'authorized': True})['terminal_route'] == ROUTE_FAIL_CLOSED


def test_successful_selection_cannot_become_no_bet():
    with pytest.raises(ValueError, match='SELECTION_SUCCEEDED'):
        diagnose(*fixture()[:2], authority=fixture()[2], root=ROOT)


def test_temporal_labels_and_nonzero_exposure_rejected_even_after_rehash():
    intent, report = inputs()
    t = build(intent, report)
    t['total_investment'] = 100
    t['sha256'] = sha({k:v for k,v in t.items() if k != 'sha256'})
    with pytest.raises(ValueError, match='NONZERO'): verify_no_bet_terminal(t)
    with pytest.raises(ValueError, match='TEMPORAL'):
        build_aki_no_bet_terminal(intent, report, source_receipt_verified=True,
            created_at='2026-10-11T10:11:00+09:00', lineage='LIVE', root=ROOT)
    h = build_aki_no_bet_terminal(intent, report, source_receipt_verified=True,
        created_at='2026-10-11T10:11:00+09:00', lineage='HISTORICAL_DIAGNOSTIC', root=ROOT)
    with pytest.raises(ValueError, match='FORWARD_LIVE'): verify_no_bet_terminal(h, require_live=True)


def test_real_kyoto5_source_reproduces_stop_without_result_inputs():
    eid = 'KM-JRA-KYO-20261012-R05-LIVE-R1'
    report = json.loads((ROOT/'runtime/exact_gaps'/f'{eid}.json').read_text())
    path = ROOT/'runtime/executions'/eid/'SOURCE/runs/38196179597/source_receipt_envelope.json'
    env = json.loads(path.read_text())
    a = json.loads((ROOT/'profiles/KM_FAMILY_CURRENT_AUTHORITY_20261011_R50.json').read_text())
    i = json.loads((ROOT/'runtime/jra_formal_intents'/f'{eid}.json').read_text())
    from jra_production_auto_handoff import compile_production_auto_handoff
    from verify_source_envelope import verify
    assert verify(str(path))['valid']
    with pytest.raises(AKICapitalError, match='COLUMN_EMPTY'):
        compile_production_auto_handoff(i, env, report, current_authority=a,
            frozen_at='2026-10-12T02:39:00+00:00', root=ROOT)
    report['sha256'] = sha({k:v for k,v in report.items() if k != 'sha256'})
    assert report['aki_selection_failure']['diagnostic']['empty_columns'] == ['W', 'P2', 'P3']
    t = build_aki_no_bet_terminal(i, report, source_receipt_verified=True,
        created_at='2026-10-12T04:00:00+00:00', lineage='HISTORICAL_DIAGNOSTIC', root=ROOT)
    assert verify_no_bet_terminal(t)['terminal_index_count'] == 180
    # A test never creates a production LIVE artifact with an invented clock.
    from jra_race_day_autopilot import race_status
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for folder in ('jra_formal_intents', 'jra_no_bet_terminals'):
            (root/'runtime'/folder).mkdir(parents=True)
        (root/'runtime/jra_formal_intents'/f'{eid}.json').write_text(json.dumps(i))
        (root/'runtime/jra_no_bet_terminals'/f'{eid}.json').write_text(json.dumps(t))
        row = race_status(root, i['race_id'], {}, {}, None)
        assert row['state'] == 'AKI_NO_BET_HISTORICAL'
        assert row['ticket_count'] == row['total_investment'] == 0


def test_internal_handoff_failure_never_reports_formal_route():
    _, report = inputs()
    report['auto_handoff_error'] = 'JRA_INTERNAL_TRANSPORT_ERROR'
    c = classify_production_blockers(report, owner_status={'authorized': True})
    assert c['first_actual_blocked_stage'] == 'PRODUCTION_FORMAL_HANDOFF'
    assert c['terminal_route'] == ROUTE_FAIL_CLOSED


def test_aki_no_bet_closes_result_learning_without_pfs_credit():
    intent, report = inputs()
    terminal = build(intent, report)
    from jra_no_bet_postresult_learning import build_no_bet_learning, _hash
    result = {'official': True, 'result_derived': True,
              'runners': [{'runner_id': '2', 'finish': 1},
                          {'runner_id': '3', 'finish': 2},
                          {'runner_id': '1', 'finish': 3}]}
    result['sha256'] = _hash(result)
    result.update(race_no=5, source_snapshot_sha256='d'*64)
    learning = build_no_bet_learning(terminal, result, race_no=5,
        acquired_at='2026-10-11T10:15:00+09:00', result_source_snapshot_sha256='d'*64,
        official_capture_verified=True)
    assert learning['official_top3'] == ['2', '3', '1']
    assert learning['investment'] == learning['payout'] == 0 and learning['pfs'] is None
    assert learning['learning_class'] == 'AKI_POSITIVE_EVIDENCE_AND_OPPORTUNITY_COST_ONLY'
    assert not learning['eligible_for_production_prediction_kpi']
