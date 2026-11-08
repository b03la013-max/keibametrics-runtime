import json
from hashlib import sha256
from pathlib import Path

import pytest
from cryptography.exceptions import InvalidSignature

from jra_role_learning_shadow import digest
from jra_ticket_tree_renderer import render_ticket_tree
from selection import _independent_sets, build_candidate, build_pair_gap_reference

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


def test_independent_place_support_requires_joint_set_three_evidence_ledgers_and_axis():
    facts = [{"feature": name, "category": "STRONG", "evidence_refs": ["bound-source-fact"]}
             for name in ("same_course_fit", "recent_form")]
    metrics = {str(n): {"sri": 80 - n, "zai_place": 90 - n} for n in range(1, 7)}
    evidence = {n: facts for n in range(1, 7)}
    evidence[4] = facts[:1]
    evidence[5] = [facts[0], {**facts[1], "result_derived": True}]
    seen = {(1, 2, 3): {(2, 3, 1): 20, (3, 1, 2): 10},
            (1, 3, 4): {(1, 3, 4): 60}, (1, 2, 5): {(1, 2, 5): 90},
            (2, 3, 6): {(3, 2, 6): 70}}
    sets = _independent_sets(seen, metrics, evidence, {(2, 3, 1)})
    assert list(sets) == [(1, 2, 3)]
    assert sets[(1, 2, 3)]["single_place_axis_options"] == [1]
    assert sets[(1, 2, 3)]["eligible_visible_joint_occurrences"] == 10
    assert not _independent_sets(seen, metrics, evidence, {(2, 3, 1), (3, 1, 2)})


def test_independent_arm_keeps_original_frozen_tickets_and_is_separate_from_other_arms():
    final = _final("TKY", 5)
    before = digest(final)
    candidate = build_candidate(final, budget_yen=1300, include_independent_sets=True)
    assert digest(final) == before
    assert candidate["arm"] == "INDEPENDENT_JOINT_PLACE"
    assert candidate["total_investment"] <= 1300
    assert candidate["purchase_authority"] is candidate["oos_eligible"] is False
    assert render_ticket_tree({"final_ticket": candidate})["canonical_roundtrip_verified"]
    with pytest.raises(ValueError, match="ARMS_MUST_REMAIN_SEPARATE"):
        build_candidate(final, budget_yen=1300, include_krs_sets=True, include_independent_sets=True)


def _gap_archives(venue, race):
    rid = f"KM-JRA-{venue}-20261107-R{race:02}"
    base = ROOT / "runtime"
    lane = base / "source_candidate_oos" / rid
    raw = (ROOT / "evidence/jra_bvi_phase3_20261017/runtime_health.json").read_bytes()
    assert sha256(raw).hexdigest() == "e39b362fdf7def09e3cfdfb2a1a00e36e1feea2c4c29af75756973b5d3c35628"
    return (
        json.loads((base / "exact_gaps" / f"{rid}-LIVE-R1.json").read_bytes()),
        json.loads((lane / "pre_result.json").read_bytes()),
        json.loads((lane / "candidate_final.json").read_bytes()),
        json.loads(raw)["krs"]["body"]["receipt_signer"],
    )


@pytest.mark.parametrize(("venue", "race", "reason"), [
    ("KYO", 1, "NO_QUALIFIED_JOINT_SET"), ("TKY", 7, "SOURCE_CANDIDATE_PAPER_GATE")
])
def test_pair_gap_preserves_technical_stop_and_zero_exposure(venue, race, reason):
    gap, pre, final, signer = _gap_archives(venue, race)
    result = build_pair_gap_reference(gap, pre, final, signer=signer, budget_yen=2000)
    assert result["production_terminal"] == "FAIL_CLOSED_NO_TERMINAL"
    assert result["research_terminal"] == reason and result["candidate_run_count"] == 5000
    assert result["total_investment"] == 0 and result["tickets"] == []
    assert result["purchase_authority"] is result["oos_eligible"] is False


def test_pair_gap_rejects_unrelated_checkpoint_and_rehashed_bad_signature():
    gap, pre, final, signer = _gap_archives("KYO", 1)
    broken = {**gap, "source_checkpoint_manifest": {**gap["source_checkpoint_manifest"],
                                                    "source_snapshot_sha256": "1" * 64}}
    _rebind(broken["source_checkpoint_manifest"])
    _rebind(broken)
    with pytest.raises(ValueError, match="CANDIDATE_ARCHIVE_BINDING"):
        build_pair_gap_reference(broken, pre, final, signer=signer, budget_yen=100)
    final["krs_run_receipt"]["signature"] = "A" * 86 + "=="
    _rebind(final)
    with pytest.raises(InvalidSignature):
        build_pair_gap_reference(gap, pre, final, signer=signer, budget_yen=100)
