from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from jra_local_week_transfer_shadow import build_jra_week_transfer_shadow, evaluate_jra_week_transfer_shadow_result

UTC = "2026-10-11T01:01:00+09:00"
POST = "2026-10-11T14:00:00+09:00"


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def request():
    semantic = {
        "profile": "KM-JRA-SOURCE-DERIVED-CANDIDATE-SEMANTICS-v0.3-20261004-STRUCTURE-DERIVED",
        "w_active": ["1"],
        "p2_active": ["2", "3"],
        "p3_active": ["3", "4"],
        "production_authority": False,
    }
    semantic["sha256"] = digest(semantic)
    return {
        "race_id": "KM-JRA-TKY-20261011-R01",
        "family_id": "JRA",
        "candidate_policy_cohort": "JRA-CANDIDATE-v0.3-STRUCTURE-DERIVED",
        "base_index_mapping_authority": {"production_authority": False},
        "temporal_mode": "FORMAL-PRE-RACE",
        "acceptance_only": False,
        "scheduled_post_at": POST,
        "source_snapshot_sha256": "a" * 64,
        "static_prediction": {"roles": {"1": ["W"], "2": ["P2"], "3": ["P2", "P3"], "4": ["P3"]}},
        "candidate_semantic_freeze": semantic,
        "purchased_heads": ["1"],
        "role_registry": [
            {"runner_id": "1", "column": "W", "status": "CORE", "reason": "SOURCE"},
            {"runner_id": "2", "column": "P2", "status": "CORE", "reason": "SOURCE"},
            {"runner_id": "3", "column": "P2", "status": "PROTECTED", "reason": "SOURCE"},
            {"runner_id": "3", "column": "P3", "status": "PROTECTED", "reason": "SOURCE"},
            {"runner_id": "4", "column": "P3", "status": "PROTECTED", "reason": "SOURCE"},
        ],
        "pair_dispositions": [
            {"head": "1", "second": "2", "status": "PURCHASE", "reason": "PRE_RESULT_STRUCTURAL"},
            {"head": "1", "second": "3", "status": "PROTECT", "reason": "PRE_RESULT_ALT"},
        ],
        "third_dispositions": [
            {"head": "1", "second": "2", "third": "3", "status": "PURCHASE", "reason": "PRE_RESULT_PROTECTED"},
            {"head": "1", "second": "2", "third": "4", "status": "PROTECT", "reason": "PRE_RESULT_PROTECTED"},
        ],
        "aki_capital_bridge": {"status": "FORMAL_AKI_INPUT_NOT_AVAILABLE_IN_CURRENT_JRA_CANDIDATE_20_INDEX"},
    }


def tickets():
    return [
        {"bet_type": "EXACTA", "selection": [1, 2], "stake": 100},
        {"bet_type": "TRIFECTA", "selection": [1, 2, 3], "stake": 100},
        {"bet_type": "TRIO", "selection": [1, 2, 4], "stake": 100},
    ]


def test_forward_read_only_success_and_full_pair_matrix():
    req = request()
    original = copy.deepcopy(req)
    purchased = tickets()
    out = build_jra_week_transfer_shadow(req, purchased, None, generated_at=UTC)
    assert req == original
    assert purchased == tickets()
    assert out["temporal_class"] == "FORWARD_PRE_RESULT"
    assert out["production_effect"] == "NONE"
    assert out["purchase_authority"] is False
    assert out["automatic_purchase"] is False
    assert out["local_aki_adaptive_paper_policy_imported"] is False
    assert out["head_local_p2_unterminalized"] == []
    assert len(out["head_local_p2_matrix"]) == 2
    assert out["purchased_pair_third_unterminalized"] == []
    assert any(row["pair_status"] == "PROTECT" and not row["terminalized"]
               for row in out["pair_conditioned_third_matrix"])
    assert out["cross_ticket_diagnostic"]["purchased_exact_without_same_set_trio"] == [[1, 2, 3]]
    assert out["capital_exposure_diagnostic"]["total_yen"] == 300
    assert out["capital_exposure_diagnostic"]["horse_exposure"][0]["runner_id"] == 1
    assert out["score_confidence"]["formal_jra_aki"].startswith("EXPLICIT GAP")
    assert digest({k: v for k, v in out.items() if k != "sha256"}) == out["sha256"]


def test_missing_global_p2_pair_is_detected_not_purchased():
    req = request()
    req["pair_dispositions"] = [req["pair_dispositions"][0]]
    out = build_jra_week_transfer_shadow(req, tickets(), {}, generated_at=UTC)
    assert out["head_local_p2_unterminalized"] == [
        {"head": 1, "second": 3, "status": "NOT_TERMINALIZED", "reason": None, "terminalized": False}
    ]
    assert out["automatic_purchase"] is False


def test_missing_third_on_purchased_pair_is_reported():
    req = request()
    req["third_dispositions"] = [req["third_dispositions"][0]]
    out = build_jra_week_transfer_shadow(req, tickets(), {}, generated_at=UTC)
    assert len(out["purchased_pair_third_unterminalized"]) == 1
    assert out["purchased_pair_third_unterminalized"][0]["third"] == 4


def test_wrong_family_or_production_authority_rejected():
    req = request()
    req["family_id"] = "LOCAL"
    with pytest.raises(ValueError, match="FAMILY_OR_AUTHORITY"):
        build_jra_week_transfer_shadow(req, tickets(), None, generated_at=UTC)
    req["family_id"] = "JRA"
    req["base_index_mapping_authority"]["production_authority"] = True
    with pytest.raises(ValueError, match="FAMILY_OR_AUTHORITY"):
        build_jra_week_transfer_shadow(req, tickets(), None, generated_at=UTC)


def test_prestart_boundary_and_replay_boundary():
    req = request()
    with pytest.raises(ValueError, match="AFTER_SCHEDULED_POST"):
        build_jra_week_transfer_shadow(req, tickets(), None, generated_at="2026-10-11T15:00:00+09:00")
    req["temporal_mode"] = "POST-START-REPLAY"
    out = build_jra_week_transfer_shadow(req, tickets(), None, generated_at="2026-10-11T15:00:00+09:00")
    assert out["temporal_class"] == "ACCEPTANCE_OR_REPLAY_NO_OOS_CREDIT"


def test_forged_semantic_hash_rejected():
    req = request()
    req["candidate_semantic_freeze"]["sha256"] = "b" * 64
    with pytest.raises(ValueError, match="SEMANTIC_FREEZE_INVALID"):
        build_jra_week_transfer_shadow(req, tickets(), None, generated_at=UTC)


def test_duplicate_purchased_tickets_rejected():
    req = request()
    tx = tickets()
    tx.append(copy.deepcopy(tx[0]))
    with pytest.raises(ValueError, match="DUPLICATE_PURCHASED_TICKET"):
        build_jra_week_transfer_shadow(req, tx, None, generated_at=UTC)


def test_duplicate_pair_and_third_rejected():
    req = request()
    req["pair_dispositions"].append(copy.deepcopy(req["pair_dispositions"][0]))
    with pytest.raises(ValueError, match="DUPLICATE_PAIR"):
        build_jra_week_transfer_shadow(req, tickets(), None, generated_at=UTC)
    req = request()
    req["third_dispositions"].append(copy.deepcopy(req["third_dispositions"][0]))
    with pytest.raises(ValueError, match="DUPLICATE_THIRD"):
        build_jra_week_transfer_shadow(req, tickets(), None, generated_at=UTC)


def test_cross_ticket_observability_is_not_automatic_purchase():
    req = request()
    tx = tickets()
    tx.append({"bet_type": "EXACTA", "selection": [1, 3], "stake": 100})
    out = build_jra_week_transfer_shadow(req, tx, None, generated_at=UTC)
    assert out["capital_exposure_diagnostic"]["total_yen"] == 400
    assert out["capital_exposure_diagnostic"]["fixed_exposure_cap_applied"] is False
    assert out["cross_ticket_diagnostic"]["purchased_trifecta_without_same_head_exacta"] == []
    assert out["purchase_authority"] is False


def test_live_workflow_freezes_before_signed_final():
    script = (Path(__file__).resolve().parents[1] / ".github/workflows/km-jra-source-candidate-forward-oos.yml").read_text()
    assert script.index("transfer_shadow=build_jra_week_transfer_shadow") < script.index('fcode,final=call("/final"')
    assert '"jra_local_week_transfer_shadow_binding"' in script
    assert 'jra_local_week_transfer_shadow_pre_result.json' in script
    assert '"jra_local_week_transfer_shadow_sha256"' in script


def pre_result_reference(req, frozen):
    return {
        "race_id": req["race_id"],
        "sha256": "f" * 64,
        "source_snapshot_sha256": req["source_snapshot_sha256"],
        "candidate_semantic_freeze_sha256": req["candidate_semantic_freeze"]["sha256"],
        "scheduled_post_at": req["scheduled_post_at"],
        "jra_local_week_transfer_shadow_sha256": frozen["sha256"],
        "candidate_final_verified": True,
        "oos_eligible": True,
        "roles": req["static_prediction"]["roles"],
    }


def test_signed_result_attribution_to_frozen_pair_third_and_exposure():
    req = request()
    frozen = build_jra_week_transfer_shadow(req, tickets(), None, generated_at=UTC)
    pre = pre_result_reference(req, frozen)
    original = copy.deepcopy(frozen)
    observed = evaluate_jra_week_transfer_shadow_result(frozen, pre, [1, 2, 3])
    assert frozen == original
    assert observed["conversion_first_lost_link_observation"] == "NO_DECLARED_ROLE_PAIR_THIRD_LOSS"
    assert observed["actual_head_local_p2"]["purchased_declared"] is True
    assert observed["actual_pair_conditioned_third"]["purchased_declared"] is True
    assert observed["cross_ticket_observation"]["actual_exact_has_missing_same_set_trio"] is True
    assert observed["observed_capital_exposure"]["total_frozen_yen"] == 300
    assert observed["counterfactual_pfs"] is None
    assert observed["production_effect"] == "NONE"
    assert observed["automatic_purchase"] is False
    assert digest({k: v for k, v in observed.items() if k != "sha256"}) == observed["sha256"]


def test_result_distinguishes_winner_miss_from_pair_loss():
    req = request()
    frozen = build_jra_week_transfer_shadow(req, tickets(), None, generated_at=UTC)
    pre = pre_result_reference(req, frozen)
    observed = evaluate_jra_week_transfer_shadow_result(frozen, pre, [4, 2, 3])
    assert observed["conversion_first_lost_link_observation"] == "WINNER_HEAD_NOT_IN_FROZEN_MATRIX"
    assert observed["actual_second_in_global_p2_matrix"] is True


def test_result_detects_global_p2_present_but_head_local_unterminalized():
    req = request()
    req["pair_dispositions"] = [req["pair_dispositions"][0]]
    frozen = build_jra_week_transfer_shadow(req, tickets(), None, generated_at=UTC)
    observed = evaluate_jra_week_transfer_shadow_result(frozen, pre_result_reference(req, frozen), [1, 3, 4])
    assert observed["actual_second_in_global_p2_matrix"] is True
    assert observed["conversion_first_lost_link_observation"] == "HEAD_LOCAL_P2_UNTERMINALIZED"
    assert observed["population_terminalization"]["head_local_p2_unterminalized"] == 1


def test_result_detects_third_missing_from_purchased_pair():
    req = request()
    req["third_dispositions"] = [req["third_dispositions"][1]]
    frozen = build_jra_week_transfer_shadow(req, tickets(), None, generated_at=UTC)
    observed = evaluate_jra_week_transfer_shadow_result(frozen, pre_result_reference(req, frozen), [1, 2, 3])
    assert observed["actual_third_in_global_p3_matrix"] is True
    assert observed["conversion_first_lost_link_observation"] == "PURCHASED_PAIR_THIRD_UNTERMINALIZED"


def test_result_fails_closed_on_tampered_sha_semantic_and_oos():
    req = request()
    frozen = build_jra_week_transfer_shadow(req, tickets(), None, generated_at=UTC)
    pre = pre_result_reference(req, frozen)
    broken = copy.deepcopy(frozen)
    broken["profile"] = "FAKE"
    with pytest.raises(ValueError, match="HASH_INVALID"):
        evaluate_jra_week_transfer_shadow_result(broken, pre, [1, 2, 3])
    bad_pre = copy.deepcopy(pre)
    bad_pre["candidate_semantic_freeze_sha256"] = "e" * 64
    with pytest.raises(ValueError, match="SEMANTIC_BASIS_MISMATCH"):
        evaluate_jra_week_transfer_shadow_result(frozen, bad_pre, [1, 2, 3])
    bad_pre = copy.deepcopy(pre)
    bad_pre["oos_eligible"] = False
    with pytest.raises(ValueError, match="NOT_FROZEN_FORWARD_OOS"):
        evaluate_jra_week_transfer_shadow_result(frozen, bad_pre, [1, 2, 3])


def test_result_runner_wires_frozen_transfer_before_candidate_result_binding():
    workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/km-formal-result-runner.yml").read_text()
    assert "evaluate_jra_week_transfer_shadow_result" in workflow
    assert workflow.index("transfer_eval=evaluate_jra_week_transfer_shadow_result(") < workflow.index(
        "source_candidate_result=bind_source_candidate_result(candidate_pre,candidate_eval)")
    assert "JRA_TRANSFER_FROZEN_PRE_RESULT_SHADOW_MISSING" in workflow
    assert "jra_local_week_transfer_result_sha256" in workflow



def test_frozen_recommendation_ticket_reachability_is_order_specific():
    req = request()
    frozen = build_jra_week_transfer_shadow(req, tickets(), None, generated_at=UTC)
    assert frozen["frozen_purchased_ticket_registry"] == {
        "EXACTA": [[1, 2]],
        "TRIFECTA": [[1, 2, 3]],
        "TRIO": [[1, 2, 4]],
    }
    pre = pre_result_reference(req, frozen)
    exact = evaluate_jra_week_transfer_shadow_result(frozen, pre, [1, 2, 3])
    assert exact["conversion_first_lost_link_observation"] == "NO_DECLARED_ROLE_PAIR_THIRD_LOSS"
    assert exact["frozen_purchased_ticket_reachability"] == {
        "status": "FROZEN_CANONICAL_RECOMMENDATION",
        "EXACTA": True, "TRIO": False, "TRIFECTA": True,
        "frozen_recommendation_only": True, "actual_purchase_verified": False,
    }
    trio = evaluate_jra_week_transfer_shadow_result(frozen, pre, [1, 2, 4])
    assert trio["frozen_purchased_ticket_reachability"]["EXACTA"] is True
    assert trio["frozen_purchased_ticket_reachability"]["TRIO"] is True
    assert trio["frozen_purchased_ticket_reachability"]["TRIFECTA"] is False
    reversal = evaluate_jra_week_transfer_shadow_result(frozen, pre, [2, 1, 4])
    assert reversal["frozen_purchased_ticket_reachability"]["EXACTA"] is False
    assert reversal["frozen_purchased_ticket_reachability"]["TRIO"] is True
    assert reversal["frozen_purchased_ticket_reachability"]["TRIFECTA"] is False


def test_declared_pair_third_does_not_imply_purchased_exact():
    req = request()
    only_pair = [tickets()[0]]
    frozen = build_jra_week_transfer_shadow(req, only_pair, None, generated_at=UTC)
    observed = evaluate_jra_week_transfer_shadow_result(
        frozen, pre_result_reference(req, frozen), [1, 2, 3]
    )
    assert observed["conversion_first_lost_link_observation"] == "NO_DECLARED_ROLE_PAIR_THIRD_LOSS"
    assert observed["actual_pair_conditioned_third"]["purchased_declared"] is True
    assert observed["frozen_purchased_ticket_reachability"]["EXACTA"] is True
    assert observed["frozen_purchased_ticket_reachability"]["TRIFECTA"] is False
    assert observed["frozen_purchased_ticket_reachability"]["actual_purchase_verified"] is False


def test_legacy_transfer_has_unknown_not_false_and_registry_integrity_guard():
    req = request()
    frozen = build_jra_week_transfer_shadow(req, tickets(), None, generated_at=UTC)
    legacy = copy.deepcopy(frozen)
    del legacy["frozen_purchased_ticket_registry"]
    legacy["sha256"] = digest({k: v for k, v in legacy.items() if k != "sha256"})
    observed = evaluate_jra_week_transfer_shadow_result(
        legacy, pre_result_reference(req, legacy), [1, 2, 3]
    )
    reach = observed["frozen_purchased_ticket_reachability"]
    assert reach["status"] == "LEGACY_NOT_FROZEN"
    assert reach["TRIFECTA"] is None
    tampered = copy.deepcopy(frozen)
    tampered["frozen_purchased_ticket_registry"]["TRIFECTA"] = []
    with pytest.raises(ValueError, match="FROZEN_SHADOW_HASH_INVALID"):
        evaluate_jra_week_transfer_shadow_result(
            tampered, pre_result_reference(req, frozen), [1, 2, 3]
        )
    duplicate = copy.deepcopy(frozen)
    duplicate["frozen_purchased_ticket_registry"]["EXACTA"].append([1, 2])
    duplicate["sha256"] = digest({k: v for k, v in duplicate.items() if k != "sha256"})
    with pytest.raises(ValueError, match="FROZEN_PURCHASE_REGISTRY_DUPLICATE"):
        evaluate_jra_week_transfer_shadow_result(
            duplicate, pre_result_reference(req, duplicate), [1, 2, 3]
        )
