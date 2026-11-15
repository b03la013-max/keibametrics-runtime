"""Mechanical transport counterexamples only; no empirical/OOS credit."""
from copy import deepcopy

import pytest

from runtime import local_fnb_saved_paper_tickets as m
from runtime import local_fnb_semantic_closure as semantic
from test_local_fnb_semantic_closure import fixture, seal, NOW


def inputs():
    p = fixture()
    p['runner_world_stage_basis'] = {r:{'paths':[], 'unknown':[]} for r in p['active_runners']}
    seal(p)
    return {'prediction':p, 'request':{'scheduled_post_at':'2026-11-03T15:00:00+09:00',
            'prediction_cutoff':'2026-11-03T14:55:00+09:00'},
        'raw':{'original_provider_card.html':b'SYNTHETIC ONLY'},
        'documents':{'krs/research_krs_receipt.json':{'synthetic':True},
            'provider_reference_capture_and_scope.json':{'qualified_source':False}}}


def test_single_owner_protects_pair_local_third_without_asserting_orientation():
    x = inputs(); before = deepcopy(x)
    r = m.construct_single_owner(x, authorization_ref='SYNTHETIC', evaluated_at=NOW)
    s = r['studies']['S1']
    methods = s['paper_result']['methods']
    assert methods['EXACTA']['tickets'][0]['selection'] == [1,2]
    assert methods['TRIO']['tickets'][0]['selection'] == [1,2,3]
    assert methods['TRIFECTA']['point_count'] == 0
    assert methods['TRIFECTA']['zero_reason'] == 'NO_EXACT_PURCHASE_ORIENTATION_ASSERTED'
    assert s['strict_pair_scoped_mec_verified']
    assert r['owner_count'] == 1 and not r['independent_BC']
    assert not r['formal_selected_ticket'] and not r['computed_no_bet']
    assert r['new_krs_executions'] == 0 and x == before


def test_ledgers_keep_all_unknown_and_structural_decisions_separate():
    r = m.construct_single_owner(inputs(), authorization_ref='SYNTHETIC', evaluated_at=NOW)
    s1, s2 = (r['studies'][s]['ledger'] for s in ('S1','S2'))
    for s in (s1,s2):
        assert len(s['pairs']) == 16 and len(s['thirds']) == 64
        assert all(x['material_selection_status'] == 'STRUCTURAL_INELIGIBLE'
            for x in s['pairs'] if x['head'] == x['second'])
        assert all(x['material_selection_status'] != 'STRUCTURAL_INELIGIBLE'
            for x in s['thirds'] if len({x['head'],x['second'],x['third']}) == 3)
    assert next(x for x in s1['pairs'] if (x['head'],x['second']) == ('4','1'))['material_selection_status'] == 'UNRESOLVED_UNKNOWN'
    assert next(x for x in s2['pairs'] if (x['head'],x['second']) == ('4','1'))['material_selection_status'] == 'PROTECT'
    assert not s2['unknown_evidence_resolved']


def test_unchanged_profile_and_no_budget_compression(monkeypatch):
    x = inputs()
    monkeypatch.setattr('runtime.capital_policy.load_family_default_capital_policy',
        lambda:{'mode':'HARD_RACE_BUDGET','max_race_capital':100,'insufficient_action':'PAPER'})
    r = m.construct_single_owner(x, authorization_ref='SYNTHETIC', evaluated_at=NOW)
    s2 = r['studies']['S2']['paper_result']['methods']['EXACTA']
    assert s2['point_count'] == 5 and s2['paper_required_capital'] == 500
    assert s2['capital_shortfall'] == 400 and s2['capital_policy']['decision'] == 'PAPER'
    assert not s2['computed_whole_race_no_bet'] and not s2['formal_selected_ticket']
    assert s2['available_unspent_cash'] == 100


def test_missing_material_pair_cannot_remove_a_w_head():
    x = inputs(); p = x['prediction']
    p['pair_dispositions'] = []; p['third_dispositions'] = []; seal(p)
    with pytest.raises(ValueError, match='MATERIAL_W_WITHOUT_PAIR'):
        m.construct_single_owner(x, authorization_ref='SYNTHETIC', evaluated_at=NOW)


def test_formal_purchase_injected_into_unadopted_proposal_is_rejected():
    x = inputs(); p = x['prediction']
    p['third_dispositions'][0]['status'] = 'PURCHASE'; seal(p)
    with pytest.raises(ValueError, match='UNCHANGED_ORIGINAL_SEMANTIC_PROPOSALS'):
        m.construct_single_owner(x, authorization_ref='SYNTHETIC', evaluated_at=NOW)


def test_ledger_closure_counterexample_is_not_a_no_bet():
    p = inputs()['prediction']
    s = semantic.research_pair_local_protection(p,evaluated_at=NOW)
    s['known_pair_scoped_subplans'] = []
    with pytest.raises(ValueError, match='MATERIAL_W_WITHOUT_PAIR'):
        m.selection_ledger(p,s,selected_at=NOW)


def test_profile_drift_rejected(monkeypatch):
    monkeypatch.setitem(m.POLICY_PINS,'S1','0'*64)
    with pytest.raises(ValueError, match='SELECTION_PROFILE_DRIFT'):
        m.construct_single_owner(inputs(),authorization_ref='SYNTHETIC',evaluated_at=NOW)


def test_postcutoff_is_diagnostic_and_ack_never_inferred():
    r = m.construct_single_owner(inputs(),authorization_ref='SYNTHETIC',evaluated_at='2026-11-03T07:00:00+00:00')
    assert r['classification'] == 'POSTCUTOFF_DIAGNOSTIC_PAPER_NOT_OOS'
    assert not r['recipient_ack_verified'] and not r['natural_delivery_verified']
    assert not r['original_strict_mec_hold_lifted'] and r['PFS'] is None
