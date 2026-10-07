from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

from family_pfs_promotion_gate import evaluate_promotion_gate
from family_pfs_owner_scorecard import build_owner_scorecard


def complete_summary(**overrides):
    x = {
        "eligible_races": 30,
        "distinct_days": 3,
        "integrity_holds": 0,
        "candidate_pfs": 112.0,
        "production_pfs": 94.0,
        "candidate_max_drawdown": 8000,
        "production_max_drawdown": 12000,
        "candidate_equal_budget_drawdown": 7000,
        "production_equal_budget_drawdown": 10000,
        "candidate_equal_ticket_profit": 4500,
        "production_equal_ticket_profit": -1000,
        "candidate_set_coverage_rate": 0.95,
        "production_set_coverage_rate": 0.95,
        "candidate_hit_but_loss_rate": 0.20,
        "production_hit_but_loss_rate": 0.35,
        "candidate_largest_return_share": 0.32,
        "candidate_profit_without_best_race": 1200,
    }
    x.update(overrides)
    return x


def test_promotion_gate_requires_30_races_and_3_days():
    x = evaluate_promotion_gate(complete_summary(eligible_races=29))
    assert x["verdict"] == "CONTINUE_FORWARD_OOS"
    assert x["automatic_promotion"] is False
    assert x["production_change_authorized"] is False

    y = evaluate_promotion_gate(complete_summary(distinct_days=2))
    assert y["verdict"] == "CONTINUE_FORWARD_OOS"


def test_promotion_gate_only_allows_human_review_when_all_guards_pass():
    x = evaluate_promotion_gate(complete_summary())
    assert x["verdict"] == "REVIEW_ELIGIBLE"
    assert x["required_next_action"] == "EXPLICIT_HUMAN_PROMOTION_REVIEW"
    assert x["automatic_promotion"] is False
    assert x["production_change_authorized"] is False
    assert all(x["checks"].values())


def test_promotion_gate_rejects_or_simplifies_fragile_candidate():
    x = evaluate_promotion_gate(
        complete_summary(
            candidate_largest_return_share=0.72,
            candidate_profit_without_best_race=-2000,
        )
    )
    assert x["verdict"] == "REJECT_OR_SIMPLIFY_REVIEW"
    assert x["checks"]["single_race_dependency_bounded"] is False
    assert x["checks"]["profit_without_best_race_positive"] is False


def test_promotion_gate_holds_missing_metrics():
    x = complete_summary()
    x.pop("candidate_equal_ticket_profit")
    y = evaluate_promotion_gate(x)
    assert y["verdict"] == "HOLD_INCOMPLETE_OR_INTEGRITY"


def test_owner_scorecard_separates_pfs_loss_owner_from_first_failure():
    reviews = [
        {
            "race_id": "R1",
            "capital": {"investment": 1000, "return": 600, "pfs": 60, "hit": True, "hit_but_loss": True},
            "failure_localization": {"first_material_failure": "PREDICTION_ROLE_W"},
            "pfs_improvement": {"dominant_pfs_loss_owner": {"owner": "CAPITAL"}},
            "by_bet_type": {"TRIO": {"investment": 700, "return": 100}, "EXACTA": {"investment": 300, "return": 500}},
        },
        {
            "race_id": "R2",
            "capital": {"investment": 1000, "return": 1800, "pfs": 180, "hit": True, "hit_but_loss": False},
            "failure_localization": {"first_material_failure": "ORDERED_PAIR_CONVERSION"},
            "pfs_improvement": {"dominant_pfs_loss_owner": {"owner": "NONE_REALIZED_PFS_POSITIVE"}},
            "by_bet_type": {"TRIO": {"investment": 500, "return": 1800}, "EXACTA": {"investment": 500, "return": 0}},
        },
    ]
    x = build_owner_scorecard(reviews)
    assert x["aggregate"]["investment"] == 2000
    assert x["aggregate"]["return"] == 2400
    assert x["aggregate"]["pfs"] == 120.0
    assert x["aggregate"]["hit_but_loss_count"] == 1
    assert x["first_material_failure_frequency"]["PREDICTION_ROLE_W"] == 1
    assert x["first_material_failure_frequency"]["ORDERED_PAIR_CONVERSION"] == 1
    assert x["dominant_pfs_loss_owner_frequency"]["CAPITAL"] == 1
    assert x["by_bet_type"]["TRIO"]["investment"] == 1200
    assert x["by_bet_type"]["EXACTA"]["investment"] == 800
    assert x["production_change_authorized"] is False


def test_owner_scorecard_reports_concentration_and_candidate_metrics():
    reviews = [
        {
            "race_id": "A",
            "capital": {"investment": 1000, "return": 5000, "pfs": 500, "hit": True, "hit_but_loss": False},
            "failure_localization": {"first_material_failure": "NONE"},
            "pfs_improvement": {"dominant_pfs_loss_owner": {"owner": "NONE_REALIZED_PFS_POSITIVE"}},
        },
        {
            "race_id": "B",
            "capital": {"investment": 1000, "return": 0, "pfs": 0, "hit": False, "hit_but_loss": False},
            "failure_localization": {"first_material_failure": "PREDICTION_ROLE_W"},
            "pfs_improvement": {"dominant_pfs_loss_owner": {"owner": "PREDICTION_ROLE"}},
        },
    ]
    x = build_owner_scorecard(
        reviews,
        candidate_comparisons={
            "SELECTIVE_EXACT": {
                "investment": 2000,
                "return": 3000,
                "pfs": 150,
                "equal_budget_pfs": 145,
                "max_drawdown": 800,
            }
        },
    )
    assert x["payout_concentration"]["largest_return_race"] == "A"
    assert x["payout_concentration"]["largest_return_share"] == 1.0
    assert x["candidate_comparisons"]["SELECTIVE_EXACT"]["pfs"] == 150.0
