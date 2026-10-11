from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from jra_aki_capital_preflight import AXES, AKICapitalError, sha, verify_official_v21, verify_aki_ticket_binding
from jra_static_owner_executable import compile_static_owner
from minimum_efficient_coverage import build_mec_plan
from capital_policy import resolve_capital_policy


def official():
    registry = {a: {'rule_id': 'FIXTURE-' + a, 'mapping_version': 'FIXTURE-NOT-PRODUCTION'} for a in AXES}
    values = dict(zip(AXES, [20, 30, 80, 85, 40, 10, 5]))
    p = {'version': 'AKI-JRA v2.1', 'race_id': 'TEST', 'source_snapshot_sha256': 's' * 64,
         'components': {a: dict(registry[a], value=values[a], status='CALCULATED',
                               evidence_refs=['fixture'], source_fact='synthetic only') for a in AXES}}
    p['sha256'] = sha(p)
    return p, registry


def test_official_formula_separate_axes_and_no_asi_in_total():
    p, registry = official()
    out = verify_official_v21(p, race_id='TEST', source_hash='s' * 64, rule_registry=registry)
    assert out['total'] == pytest.approx(32)
    assert out['P-AKI_compatibility_only'] == pytest.approx(57.5)
    assert out['axis_candidate_rule'] == 'SINGLE_AXIS_CANDIDATE'
    p['components']['ASI']['value'] = 10
    p['sha256'] = sha({k: v for k, v in p.items() if k != 'sha256'})
    changed = verify_official_v21(p, race_id='TEST', source_hash='s' * 64, rule_registry=registry)
    assert changed['total'] == out['total']
    assert changed['axis_candidate_rule'] == 'SINGLE_AXIS_FORBIDDEN'


@pytest.mark.parametrize('mutation', ['missing_p2', 'wrong_source', 'wrong_rule', 'nan', 'tamper'])
def test_official_missing_or_forged_components_block(mutation):
    p, registry = official()
    if mutation == 'missing_p2':
        del p['components']['P2-AKI']
    elif mutation == 'wrong_source':
        p['source_snapshot_sha256'] = 'other'
    elif mutation == 'wrong_rule':
        p['components']['P3-AKI']['rule_id'] = 'unregistered'
    elif mutation == 'nan':
        p['components']['P3-AKI']['value'] = float('nan')
    else:
        p['components']['P3-AKI']['value'] = 1
    if mutation not in ('tamper', 'nan'):
        p['sha256'] = sha({k: v for k, v in p.items() if k != 'sha256'})
    with pytest.raises(ValueError):
        verify_official_v21(p, race_id='TEST', source_hash='s' * 64, rule_registry=registry)


def replay_request():
    p = ROOT / 'runtime/requests/KM-JRA-TKY-20261011-R11-LIVE-R1-FORMAL.json'
    req = json.loads(p.read_text())
    owner = compile_static_owner(req, source_snapshot_sha256=req['source_snapshot_sha256'],
                                 source_receipt_sha256=req['source_snapshot_sha256'],
                                 frozen_at=req['prediction_cutoff'], prediction_cutoff=req['prediction_cutoff'])
    rebuilt = deepcopy(req)
    rebuilt.update({k: owner[k] for k in ('static_prediction', 'role_registry', 'pair_dispositions',
                                        'third_dispositions', 'purchased_heads')})
    return req, rebuilt


def test_real_1584_cartesian_regression_and_replayed_width_binding():
    old, repaired = replay_request()
    old_mec = build_mec_plan(old)
    assert old_mec['ticket_count'] == 1584
    with pytest.raises(AKICapitalError, match='AKI_WIDTH_DECISION_MISSING'):
        verify_aki_ticket_binding(old, old_mec)
    new = build_mec_plan(repaired)
    verified = verify_aki_ticket_binding(repaired, new)
    assert verified['ticket_count'] == 20
    assert verified['exacta_count'] == 4
    assert verified['trifecta_count'] == 16
    assert verified['official_v21_verified'] is False
    assert resolve_capital_policy({}, old_mec)['decision'] == 'PAPER'
    assert resolve_capital_policy({}, new)['required_capital'] == 2000
    assert resolve_capital_policy({}, new)['decision'] == 'EXECUTE_FULL_MEC'
    # No extra purchase to fill the 10,000-yen ceiling.
    assert resolve_capital_policy({}, new)['unused_budget'] == 8000
    changed = deepcopy(new)
    changed['tickets'].append({'bet_type': 'EXACTA', 'selection': [4, 16], 'stake': 100})
    with pytest.raises(AKICapitalError, match='AKI_ACTUAL_TICKET_SET_MISMATCH'):
        verify_aki_ticket_binding(repaired, changed)
    repaired['aki_calculation_requirement'] = 'OFFICIAL_V2_1'
    with pytest.raises(AKICapitalError, match='OFFICIAL_V2_1_NOT_SATISFIED'):
        verify_aki_ticket_binding(repaired, new)


def test_selected_width_is_not_reexpanded_downstream():
    _, repaired = replay_request()
    new = build_mec_plan(repaired)
    changed = deepcopy(repaired)
    changed['pair_dispositions'].append({'head': '4', 'second': '16', 'status': 'PURCHASE'})
    with pytest.raises(AKICapitalError, match='AKI_PAIR_PURCHASE_SET_MISMATCH'):
        verify_aki_ticket_binding(changed, new)


def test_stable_vs_contested_full20_proxy_widths_and_known_limit():
    from test_jra_production_auto_handoff import numerical_runner
    from jra_static_owner_executable import MAPPING
    def evaluate(scores):
        req = {'family_id': 'JRA', 'race_id': 'SYNTHETIC',
               'base_index_mapping_authority': {'mapping_id': MAPPING, 'production_authority': True},
               'runners': [numerical_runner(i + 1, score) for i, score in enumerate(scores)]}
        owner = compile_static_owner(req, source_snapshot_sha256='a' * 64,
                                     source_receipt_sha256='b' * 64, frozen_at='2026-10-11T10:00:00+09:00',
                                     prediction_cutoff='2026-10-11T10:00:00+09:00')
        req.update({k: owner[k] for k in ('static_prediction', 'role_registry', 'pair_dispositions',
                                        'third_dispositions', 'purchased_heads')})
        return verify_aki_ticket_binding(req, build_mec_plan(req))
    stable = evaluate([95, 70, 68, 66, 64, 62, 60, 58, 56])
    volatile = evaluate([75 - .1*i for i in range(16)])
    assert stable['column_widths']['W'] == 1
    assert volatile['column_widths']['W'] >= 2
    # Existing row semantics overlap the heads in rows 2/3. More heads alone
    # therefore do not imply more valid tickets. Preserve this counterexample
    # rather than claiming the old proxy satisfies formal v2.1 width semantics.
    assert stable['ticket_count'] == 10
    assert volatile['ticket_count'] == 8
