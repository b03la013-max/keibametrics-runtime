import json
from pathlib import Path

import pytest

from jra_role_learning_shadow import digest
from jra_ticket_tree_renderer import render_ticket_tree
from selection import build_candidate

ROOT = Path(__file__).resolve().parents[2]


def _final(venue, race):
    return json.loads((ROOT / "runtime" / "final_artifacts"
                       / f"KM-JRA-{venue}-20261107-R{race:02}.json").read_text())


def _rebind(final):
    final.pop("sha256", None)
    final["sha256"] = digest(final)


def test_selection_restores_unordered_core_set_without_new_forecast():
    final = _final("TKY", 5)
    candidate = build_candidate(final, budget_yen=1300)
    assert not any(t["bet_type"] == "TRIO" for t in final["final_ticket"]["tickets"])
    assert {"bet_type": "TRIO", "selection": [1, 8, 9], "stake": 100} in candidate["tickets"]
    assert candidate["total_investment"] == 1300
    assert candidate["price_eligibility"] == "NOT_EVALUATED"
    assert not candidate["purchase_authority"]
    tree = render_ticket_tree({"final_ticket": candidate,
                               "capital_policy_decision": {"decision": "AKI_REFERENCE_ONLY"}})
    assert tree["canonical_roundtrip_verified"] and tree["total_investment"] == 1300


def test_unordered_joint_support_keeps_set_and_counts_when_direction_changes():
    final = _final("TKY", 5)
    utility = final["krs_prediction_utility"]
    utility["top_trifecta_occurrence"] = [
        {"W": 8, "P2": 9, "P3": 1, "count": 20},
        {"W": 9, "P2": 1, "P3": 8, "count": 10},
    ]
    _rebind(final)
    a = build_candidate(final, budget_yen=1300, include_krs_sets=True)
    utility["top_trifecta_occurrence"][0] = {"W": 1, "P2": 8, "P3": 9, "count": 20}
    _rebind(final)
    b = build_candidate(final, budget_yen=1300, include_krs_sets=True)
    for c in (a, b):
        row = next(x for x in c["trio_candidates"] if x["set"] == [1, 8, 9])
        assert row["visible_joint_occurrences"] == 30
        assert "KRS_JOINT_SET_PLACE_FRONTIER" in row["evidence"]
        assert row["has_visible_winner_outside_official_w"]
    assert [x for x in a["tickets"] if x["bet_type"] == "TRIO"] == [
        x for x in b["tickets"] if x["bet_type"] == "TRIO"]


def test_paper_preserves_unfunded_evidence():
    candidate = build_candidate(_final("KYO", 5), budget_yen=10000, include_krs_sets=True)
    assert candidate["paper"]
    assert candidate["tickets"] == []
    assert candidate["total_investment"] == 0
    assert candidate["trio_candidates"]


def test_tampered_and_invalid_occurrence_are_rejected():
    final = _final("TKY", 5)
    final["krs_prediction_utility"]["top_trifecta_occurrence"][0]["P2"] = 19
    with pytest.raises(ValueError, match="FINAL_HASH_MISMATCH"):
        build_candidate(final, budget_yen=1300, include_krs_sets=True)
    _rebind(final)
    with pytest.raises(ValueError, match="RUNNER_ID_INVALID"):
        build_candidate(final, budget_yen=1300, include_krs_sets=True)


def test_unordered_final_duplicate_permutations_fail_closed():
    final = _final("TKY", 4)
    ft = final["final_ticket"]
    trio = next(t for t in ft["tickets"] if t["bet_type"] == "TRIO")
    ft["tickets"].append({**trio, "selection": list(reversed(trio["selection"]))})
    ft["total_investment"] += trio["stake"]
    _rebind(final)
    with pytest.raises(ValueError, match="CANONICAL_STAKE_INVALID"):
        build_candidate(final, budget_yen=1300)

def test_ordered_exception_controls_keep_dedicated_pair_and_exact():
    final = _final("KYO", 10)
    reserved = build_candidate(final, budget_yen=1200, preserve_base_single_head=True)
    assert {"bet_type": "EXACTA", "selection": [5, 6], "stake": 100} in reserved["tickets"]
    assert {"bet_type": "TRIFECTA", "selection": [5, 6, 13], "stake": 100} in reserved["tickets"]
    pair_only = build_candidate(_final("TKY", 10), budget_yen=2400)
    assert {"bet_type": "EXACTA", "selection": [10, 2], "stake": 100} in pair_only["tickets"]
    assert not any(t["bet_type"] == "TRIFECTA" and t["selection"][:2] == [10, 2]
                   for t in pair_only["tickets"])

def test_only_observed_orientation_excluded_does_not_support_trio():
    final = _final("FKS", 1)
    utility = final["krs_prediction_utility"]
    utility["top_trifecta_occurrence"] = [
        row for row in utility["top_trifecta_occurrence"] if
        {row["W"], row["P2"], row["P3"]} == {3, 7, 8}
    ]
    _rebind(final)
    initial = build_candidate(final, budget_yen=800, include_krs_sets=True)
    assert any(x["set"] == [3, 7, 8] for x in initial["trio_candidates"])
    final["minimum_efficient_coverage"]["hard_third_exclusions_retained"] = [
        {"head": row["W"], "second": row["P2"], "third": row["P3"]}
        for row in utility["top_trifecta_occurrence"]
    ]
    _rebind(final)
    candidate = build_candidate(final, budget_yen=800, include_krs_sets=True)
    assert all(x["set"] != [3, 7, 8] for x in candidate["trio_candidates"])


def test_native_trio_keeps_explicit_already_combined_stake():
    final = _final("TKY", 4)
    ft = final["final_ticket"]
    trio = next(t for t in ft["tickets"] if t["bet_type"] == "TRIO")
    trio["stake"] += 100
    ft["total_investment"] += 100
    _rebind(final)
    candidate = build_candidate(final, budget_yen=1400)
    selected = [t for t in candidate["tickets"] if t["bet_type"] == "TRIO"
                and sorted(t["selection"]) == sorted(trio["selection"])]
    assert selected == [{"bet_type": "TRIO", "selection": sorted(trio["selection"]), "stake": 200}]
