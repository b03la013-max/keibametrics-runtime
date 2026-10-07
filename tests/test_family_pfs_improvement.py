from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

from family_pfs_improvement import (
    PROFILE_ID,
    build_pfs_improvement_assessment,
    classify_dominant_pfs_loss_owner,
)


def review(first="NONE", pfs=120.0, hit=True, hit_but_loss=False):
    return {
        "race_id": "TEST-RACE",
        "failure_localization": {"first_material_failure": first},
        "capital": {
            "pfs": pfs,
            "hit": hit,
            "hit_but_loss": hit_but_loss,
        },
    }


def test_hit_but_loss_routes_to_capital_without_changing_production():
    x = build_pfs_improvement_assessment(
        review("CAPITAL_EFFICIENCY", 61.71, True, True)
    )
    assert x["profile"] == PROFILE_ID
    assert x["dominant_pfs_loss_owner"]["owner"] == "CAPITAL"
    assert "RACE_CONDITIONAL_CAPITAL_LAYER_SELECTION" in x["test_next_tracks"]
    assert "TEST_NEXT" in x["learning_routes"]
    assert "DO_NOT_CHANGE" in x["learning_routes"]
    assert x["production_change_authorized"] is False
    assert x["automatic_promotion"] is False
    assert x["no_stagnation_satisfied"] is True


def test_prediction_role_failure_remains_prediction_owner_when_no_deeper_evidence():
    x = build_pfs_improvement_assessment(
        review("PREDICTION_ROLE_W", 0.0, False, False)
    )
    assert x["dominant_pfs_loss_owner"]["owner"] == "PREDICTION_ROLE"
    assert "WINNER_ROLE_MIGRATION" in x["test_next_tracks"]
    assert "TEST_NEXT" in x["learning_routes"]


def test_explicit_layer_loss_evidence_can_separate_first_failure_from_deep_pfs_loss():
    r = review("PREDICTION_ROLE_W", 12.87, True, True)
    loc = classify_dominant_pfs_loss_owner(
        r,
        layer_loss_evidence={
            "PREDICTION_ROLE": 3500,
            "CAPITAL": 10020,
        },
    )
    assert loc["owner"] == "CAPITAL"
    assert loc["basis"] == "EXPLICIT_LAYER_LOSS_EVIDENCE"
    x = build_pfs_improvement_assessment(
        r,
        layer_loss_evidence={
            "PREDICTION_ROLE": 3500,
            "CAPITAL": 10020,
        },
    )
    assert x["first_material_failure"] == "PREDICTION_ROLE_W"
    assert x["dominant_pfs_loss_owner"]["owner"] == "CAPITAL"
    assert "WINNER_ROLE_MIGRATION" in x["test_next_tracks"]
    assert "RACE_CONDITIONAL_CAPITAL_LAYER_SELECTION" in x["test_next_tracks"]


def test_profitable_race_can_keep_behavior_while_still_testing_connection_failure():
    x = build_pfs_improvement_assessment(
        review("ORDERED_PAIR_CONVERSION", 211.91, True, False)
    )
    assert x["dominant_pfs_loss_owner"]["owner"] == "NONE_REALIZED_PFS_POSITIVE"
    assert "PAIR_RESIDUAL" in x["test_next_tracks"]
    assert "TEST_NEXT" in x["learning_routes"]
    assert x["production_change_authorized"] is False


def test_correctness_bug_routes_to_repair_now():
    x = build_pfs_improvement_assessment(
        review("EXECUTION", 0.0, False, False),
        correctness_bug=True,
    )
    assert "REPAIR_NOW" in x["learning_routes"]
    assert x["production_change_authorized"] is False


def test_promotion_review_never_auto_promotes():
    x = build_pfs_improvement_assessment(
        review("NONE", 130.0, True, False),
        candidate_forward_evidence={
            "genuine_unknown_oos_ready": True,
            "human_review_ready": True,
            "robustness_ready": True,
        },
    )
    assert "PROMOTION_REVIEW" in x["learning_routes"]
    assert x["automatic_promotion"] is False
    assert x["production_change_authorized"] is False


def test_unknown_pfs_does_not_invent_capital_success_or_failure():
    x = build_pfs_improvement_assessment(
        review("UNRESOLVED", None, False, False)
    )
    assert x["pfs_status"] == "UNKNOWN"
    assert x["dominant_pfs_loss_owner"]["owner"] == "UNKNOWN"
    assert x["production_change_authorized"] is False


def test_semantic_purchase_and_unknown_purchase_principles_are_explicit():
    x = build_pfs_improvement_assessment(review())
    assert "SEMANTIC_UNIVERSE != PURCHASED_UNIVERSE" in x["principles"]
    assert "UNKNOWN != MUST_PURCHASE" in x["principles"]
