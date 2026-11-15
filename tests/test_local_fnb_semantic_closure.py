"""Synthetic contract/coverage counterexamples; no empirical or OOS credit."""
from copy import deepcopy
from itertools import permutations
import json
from pathlib import Path

import pytest

from runtime import local_fnb_semantic_closure as m

NOW = '2026-11-03T05:00:00+00:00'


def seal(p):
    p.pop('sha256', None)
    p['sha256'] = m._sha(p)
    return p


def fixture():
    active = ['1', '2', '3', '4']
    def ranks(front):
        return {'front': front, 'rows': [{'runner_id': r, 'unknown': r == '4',
            'rank': None if r == '4' else 1 if r in front else 2,
            'rank_interval': {'min': 1, 'max': 4}} for r in active]}
    return seal({'model_id': m.MODEL_ID, 'model_version': '0.1',
        'model_code_sha256': m.MODEL_CODE_SHA256,
        'classification': 'PRIVATE_RESEARCH_UNADOPTED_NOT_REGISTERED_OOS',
        'race_id': 'KM-LOCAL-FNB-SYNTHETIC-R1', 'active_runners': active,
        'source_snapshot_sha256': 'a' * 64,
        'source_freeze_at': '2026-10-01T00:00:00+00:00',
        'freeze_at': '2026-11-03T04:00:00+00:00',
        'column_rankings': {'W': ranks(['1']), 'P2': ranks(['2']), 'P3': ranks(['1'])},
        'roles': {'1': ['W', 'P3'], '2': ['P2'], '3': [],
            '4': ['W_UNKNOWN_POSSIBLE', 'P2_UNKNOWN_POSSIBLE', 'P3_UNKNOWN_PROTECTED']},
        'head_local_P2': [{'head': '1', 'ranking': ranks(['2'])}],
        'pair_conditioned_Third': [{'head': '1', 'second': '2', 'ranking': ranks(['3'])}],
        'pair_dispositions': [{'head': '1', 'second': '2', 'status': m.PROPOSAL_STATUS,
            'reason': 'HEAD_CONDITIONED_PARETO_FRONT_NOT_TICKET_SELECTION'}],
        'third_dispositions': [{'head': '1', 'second': '2', 'third': '3', 'status': m.PROPOSAL_STATUS,
            'reason': 'PAIR_CONDITIONED_PARETO_FRONT_NOT_TICKET_SELECTION'}],
        'unresolved_semantic_paths': [{'head': '4', 'second_candidates': ['1', '2', '3'],
            'third_candidates_rule': 'ALL_ACTIVE_EXCLUDING_THIS_HEAD_AND_CHOSEN_SECOND',
            'status': 'UNKNOWN_HEAD_PATH_NOT_EVALUATED_NOT_REJECTED_NOT_PURCHASED'}]})


def test_inventory_every_active_slot_and_structural_terminal_only():
    p = fixture()
    out = m.assess_semantics(p, evaluated_at=NOW)
    assert out['recorded_slots'] == {'role': 12, 'pair': 16, 'third': 64}
    assert out['regular_terminal_count'] == 4 + 64 - 24
    assert out['full_semantic_complete'] is False
    assert out['inventory_completion_is_not_selection_completion']
    unknown_head = [r for r in out['third_assessments'] if r['head'] == '4' and len({r['head'], r['second'], r['third']}) == 3]
    assert len(unknown_head) == 6
    assert all(r['status'] == 'UNRESOLVED_UNKNOWN_POSSIBLE' for r in unknown_head)


def test_off_global_trace_is_not_declared_structurally_ineligible():
    trace = m.trace_pair_local_thirds(fixture())[0]
    assert trace['pair_id'] == '1>2' and trace['third_id'] == '3'
    assert trace['third_roles'] == [] and not trace['third_in_global_p3']
    assert trace['head_local_pair_formed']
    assert trace['new_selection_policy_required']
    assert not trace['formal_structural_ineligibility_proven']


def test_original_strict_mec_runs_and_never_becomes_no_bet():
    p = fixture()
    before = deepcopy(p)
    out = m.execute_strict_mec(p, evaluated_at=NOW)
    assert out['status'] == 'HOLD_NOT_NO_BET'
    assert out['canonical_mec_error'].startswith('ACTIVE_W_WITHOUT_MATERIAL_PAIR_CLOSURE')
    assert out['tickets'] is None and out['no_bet'] is None
    assert len(out['all_hold_causes']) == 4
    assert p == before


def test_pair_local_third_consumed_without_global_p3_promotion():
    p = fixture()
    before = deepcopy(p)
    out = m.research_pair_local_protection(p, evaluated_at=NOW)
    assert out['conditional_third_proposals_consumed_in_candidate'] == 1
    assert out['all_original_conditional_third_proposals_consumed']
    assert out['methods']['EXACTA']['point_count'] == 1
    assert out['methods']['TRIO']['tickets'][0]['selection'] == [1, 2, 3]
    assert out['methods']['TRIFECTA']['status'] == 'COMPUTED_ZERO_ORIENTATION'
    assert out['original_strict_hold_lifted'] is False
    assert not out['global_static_p3_changed'] and p == before


def test_full_unknown_protection_and_exact_material_coverage():
    p = fixture()
    out = m.research_unknown_path_protection(p, evaluated_at=NOW)
    pairs = {(r['request']['pair_dispositions'][0]['head'], r['request']['pair_dispositions'][0]['second'])
        for r in out['known_pair_scoped_subplans']}
    assert pairs == {('1', '2'), ('1', '4'), ('4', '1'), ('4', '2'), ('4', '3')}
    triples = {tuple([r['request']['pair_dispositions'][0]['head'],
        r['request']['pair_dispositions'][0]['second'], t])
        for r in out['known_pair_scoped_subplans'] for t in r['effective_pair_scoped_p3']}
    expected_unknown = {(h, s, t) for h, s, t in permutations(p['active_runners'], 3)
        if h == '4' or (h == '1' and s == '4') or ((h, s) in pairs and t == '4')}
    assert expected_unknown <= triples
    assert out['all_declared_unknown_possible_paths_protected']
    assert out['candidate_all_selection_slots_terminal']
    assert out['candidate_decision_inventory']['candidate_regular_terminal_count'] == 92
    assert not out['full_semantic_complete'] and not out['unknown_evidence_uncertainty_resolved']
    assert out['original_unknown_semantic_paths'] == p['unresolved_semantic_paths']
    assert out['new_krs_runs'] == 0 and not out['production_adopted']


def test_no_conditional_third_leaks_into_another_pair():
    p = fixture()
    p['active_runners'].append('5'); p['roles']['5'] = []
    for col in ('W', 'P2', 'P3'):
        p['column_rankings'][col]['rows'].append({'runner_id': '5', 'unknown': False, 'rank': 2, 'rank_interval': {'min': 1, 'max': 5}})
        for row in p['column_rankings'][col]['rows']:
            row['rank_interval']['max'] = 5
    p['pair_dispositions'].append({'head': '1', 'second': '5', 'status': m.PROPOSAL_STATUS, 'reason': 'SYNTHETIC_SECOND_PAIR'})
    p['head_local_P2'][0]['ranking']['front'].append('5')
    seal(p)
    # Horse3 is structurally eligible under1>5 but was conditional only to1>2.
    out = m.research_pair_local_protection(p, evaluated_at=NOW)
    scope = next(r for r in out['known_pair_scoped_subplans'] if r['pair_id'] == '1>5')
    assert scope['effective_pair_scoped_p3'] == []
    assert p['column_rankings']['P3']['front'] == ['1']


def test_capital_paper_preserves_all_semantics_and_unique_stakes():
    p = fixture()
    out = m.research_unknown_path_protection(p, evaluated_at=NOW,
        capital_policy={'mode': 'HARD_RACE_BUDGET', 'max_race_capital': 100, 'insufficient_action': 'PAPER'})
    for method in ('EXACTA', 'TRIO'):
        v = out['methods'][method]
        assert v['capital_policy']['decision'] == 'PAPER'
        assert v['paper_required_capital'] > v['capital_limit']
        assert v['point_count'] == len(v['tickets'])
        assert v['paper_required_capital'] == 100 * v['point_count']
        assert len({tuple(t['selection']) for t in v['tickets']}) == v['point_count']
        assert all(t['stake'] == 100 for t in v['tickets'])
        assert v['canonical_roundtrip_verified'] and v['whole_race_no_bet'] is None
        assert v['recommended_cash_investment'] == v['actual_cash_investment'] == 0


def test_all_unknown_original_holds_but_new_policy_preserves_all_possible_paths():
    p = fixture()
    for col in ('W', 'P2', 'P3'):
        p['column_rankings'][col]['front'] = []
        for r in p['column_rankings'][col]['rows']:
            r.update(unknown=True, rank=None)
    p['roles'] = {r: ['W_UNKNOWN_POSSIBLE', 'P2_UNKNOWN_POSSIBLE', 'P3_UNKNOWN_PROTECTED'] for r in p['active_runners']}
    p['pair_dispositions'] = []; p['third_dispositions'] = []
    p['head_local_P2'] = []; p['pair_conditioned_Third'] = []
    seal(p)
    strict = m.execute_strict_mec(p, evaluated_at=NOW)
    assert strict['status'] == 'HOLD_NOT_NO_BET' and strict['tickets'] is None
    assert strict['canonical_mec_plan']['tickets'] == []
    out = m.research_unknown_path_protection(p, evaluated_at=NOW)
    assert out['candidate_material_pair_count'] == 12
    assert out['candidate_material_conditional_third_count'] == 24
    assert out['methods']['EXACTA']['point_count'] == 12
    assert out['methods']['TRIO']['point_count'] == 4
    assert out['all_declared_unknown_possible_paths_protected']


@pytest.mark.parametrize('mutation,code', [
    (lambda p: p['active_runners'].append('4'), 'ACTIVE_INVALID'),
    (lambda p: p['roles'].pop('4'), 'FULL_ACTIVE_ROLES_MISSING'),
    (lambda p: p['pair_dispositions'][0].update(second='999'), 'PROPOSAL_IDENTITY_INVALID'),
    (lambda p: p['third_dispositions'].append(deepcopy(p['third_dispositions'][0])), 'DUPLICATE_PROPOSAL'),
    (lambda p: p['column_rankings']['W']['front'].append('4'), 'UNKNOWN_FRONT_PROMOTION'),
    (lambda p: p.update(model_code_sha256='0' * 64), 'FIXED_MODEL_CODE'),
])
def test_invalid_identity_or_model_fails_closed(mutation, code):
    p = fixture(); mutation(p)
    with pytest.raises(ValueError, match=code):
        m.assess_semantics(p, evaluated_at=NOW)


def test_time_and_unexpected_material_status_fail_closed():
    with pytest.raises(ValueError, match='BEFORE_MODEL_FREEZE'):
        m.assess_semantics(fixture(), evaluated_at='2026-10-02T00:00:00+00:00')
    p = fixture(); p['pair_dispositions'][0]['status'] = 'PURCHASE'
    seal(p)
    with pytest.raises(ValueError, match='UNCHANGED_ORIGINAL_SEMANTIC_PROPOSALS'):
        m.research_unknown_path_protection(p, evaluated_at=NOW)


def test_mutated_original_digest_and_unknown_rank_rejected():
    p = fixture(); p['third_dispositions'][0]['reason'] = 'MUTATED'
    with pytest.raises(ValueError, match='ORIGINAL_PREDICTION_SHA_MISMATCH'):
        m.assess_semantics(p, evaluated_at=NOW)
    p = fixture(); p['column_rankings']['W']['rows'][-1]['rank'] = 4
    seal(p)
    with pytest.raises(ValueError, match='UNKNOWN_RANK_MUST_REMAIN_NULL'):
        m.research_unknown_path_protection(p, evaluated_at=NOW)


def test_conditional_proposal_needs_actual_pair_local_front():
    p = fixture(); p['pair_conditioned_Third'][0]['ranking']['front'] = []
    seal(p)
    trace = m.trace_pair_local_thirds(p)
    assert not trace[0]['pair_conditioned_third_front_qualified']
    with pytest.raises(ValueError, match='LOCAL_PROPOSAL_SCHEMA_OR_FRONT_ELIGIBILITY_CONFLICT'):
        m.research_unknown_path_protection(p, evaluated_at=NOW)


def test_profiles_disclose_new_policy_and_no_formal_adoption():
    root = Path(__file__).resolve().parents[1] / 'profiles'
    pair = json.loads((root / 'local_fnb_pair_local_semantic_protection_research_v0.1_20261103.json').read_text())
    unknown = json.loads((root / 'local_fnb_unknown_paths_protection_research_v0.1_20261103.json').read_text())
    assert pair['profile'] == m.RESEARCH_POLICY
    assert unknown['profile'] == m.UNKNOWN_RESEARCH_POLICY
    assert not pair['selection_policy_adopted'] and not unknown['original_strict_MEC_HOLD_lifted']


def test_all_known_nonfront_is_unformed_original_not_computed_no_bet():
    p = fixture()
    p['roles'] = {r: [] for r in p['active_runners']}
    for col in ('W', 'P2', 'P3'):
        p['column_rankings'][col]['front'] = []
        for row in p['column_rankings'][col]['rows']:
            row.update(unknown=False, rank=2)
    p['pair_dispositions'] = []; p['third_dispositions'] = []
    p['unresolved_semantic_paths'] = []; p['head_local_P2'] = []; p['pair_conditioned_Third'] = []
    seal(p)
    out = m.execute_strict_mec(p, evaluated_at=NOW)
    assert out['status'] == 'HOLD_NOT_NO_BET' and out['no_bet'] is None
    assert out['first_failed_stage'] == 'KNOWN_W_HEAD_ASSESSMENT_UNFORMED'


def test_two_runners_no_triple_is_structural_not_missing_computation():
    p = fixture(); p['active_runners'] = ['1', '2']
    p['roles'] = {'1': ['W', 'P3'], '2': ['P2']}
    for col in ('W', 'P2', 'P3'):
        p['column_rankings'][col]['rows'] = [r for r in p['column_rankings'][col]['rows'] if r['runner_id'] in {'1', '2'}]
    p['third_dispositions'] = []; p['pair_conditioned_Third'] = []; p['unresolved_semantic_paths'] = []
    seal(p)
    out = m.research_unknown_path_protection(p, evaluated_at=NOW)
    assert out['methods']['EXACTA']['point_count'] == 1
    assert out['candidate_decision_inventory']['candidate_regular_terminal_count'] == 18
    for method in ('TRIO', 'TRIFECTA'):
        assert out['methods'][method]['tickets'] == []
        assert out['methods'][method]['zero_reason'] == 'STRUCTURAL_NO_THREE_DISTINCT_ACTIVE_RUNNERS'
        assert out['methods'][method]['whole_race_no_bet'] is None
