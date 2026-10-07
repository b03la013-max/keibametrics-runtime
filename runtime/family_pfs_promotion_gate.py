from __future__ import annotations

from typing import Any, Mapping

PROFILE_ID = "KM-FAMILY-PFS-PROMOTION-GATE-20261007-R1"

DEFAULT_REQUIREMENTS = {
    "minimum_races": 30,
    "minimum_days": 3,
    "candidate_pfs_min": 100.0,
    "maximum_single_race_return_share": 0.50,
}


def _num(v: Any) -> float | None:
    try:
        return None if v is None else float(v)
    except (TypeError, ValueError):
        return None


def evaluate_promotion_gate(summary: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate whether a forward candidate may enter human promotion review.

    Passing this gate NEVER promotes Production. It only changes the review
    status to REVIEW_ELIGIBLE.
    """
    races = int(summary.get("eligible_races") or 0)
    days = int(summary.get("distinct_days") or 0)
    holds = int(summary.get("integrity_holds") or 0)

    candidate_pfs = _num(summary.get("candidate_pfs"))
    production_pfs = _num(summary.get("production_pfs"))
    candidate_dd = _num(summary.get("candidate_max_drawdown"))
    production_dd = _num(summary.get("production_max_drawdown"))
    eq_budget_dd = _num(summary.get("candidate_equal_budget_drawdown"))
    prod_eq_budget_dd = _num(summary.get("production_equal_budget_drawdown"))
    eq_ticket_profit = _num(summary.get("candidate_equal_ticket_profit"))
    prod_eq_ticket_profit = _num(summary.get("production_equal_ticket_profit"))
    set_cov = _num(summary.get("candidate_set_coverage_rate"))
    prod_set_cov = _num(summary.get("production_set_coverage_rate"))
    hbl = _num(summary.get("candidate_hit_but_loss_rate"))
    prod_hbl = _num(summary.get("production_hit_but_loss_rate"))
    largest_share = _num(summary.get("candidate_largest_return_share"))
    without_best_profit = _num(summary.get("candidate_profit_without_best_race"))

    checks = {
        "minimum_races": races >= DEFAULT_REQUIREMENTS["minimum_races"],
        "minimum_days": days >= DEFAULT_REQUIREMENTS["minimum_days"],
        "no_integrity_holds": holds == 0,
        "candidate_pfs_above_break_even": candidate_pfs is not None and candidate_pfs > DEFAULT_REQUIREMENTS["candidate_pfs_min"],
        "candidate_pfs_above_production": (
            candidate_pfs is not None and production_pfs is not None and candidate_pfs > production_pfs
        ),
        "raw_drawdown_no_worse": (
            candidate_dd is not None and production_dd is not None and candidate_dd <= production_dd
        ),
        "equal_budget_drawdown_no_worse": (
            eq_budget_dd is not None and prod_eq_budget_dd is not None and eq_budget_dd <= prod_eq_budget_dd
        ),
        "equal_ticket_profit_no_worse": (
            eq_ticket_profit is not None and prod_eq_ticket_profit is not None and eq_ticket_profit >= prod_eq_ticket_profit
        ),
        "set_coverage_preserved": (
            set_cov is not None and prod_set_cov is not None and set_cov >= prod_set_cov
        ),
        "hit_but_loss_no_worse": (
            hbl is not None and prod_hbl is not None and hbl <= prod_hbl
        ),
        "single_race_dependency_bounded": (
            largest_share is not None and largest_share <= DEFAULT_REQUIREMENTS["maximum_single_race_return_share"]
        ),
        "profit_without_best_race_positive": (
            without_best_profit is not None and without_best_profit > 0
        ),
    }

    complete = all(
        value is not None
        for value in [
            candidate_pfs, production_pfs,
            candidate_dd, production_dd,
            eq_budget_dd, prod_eq_budget_dd,
            eq_ticket_profit, prod_eq_ticket_profit,
            set_cov, prod_set_cov,
            hbl, prod_hbl,
            largest_share, without_best_profit,
        ]
    )

    if races < DEFAULT_REQUIREMENTS["minimum_races"] or days < DEFAULT_REQUIREMENTS["minimum_days"]:
        verdict = "CONTINUE_FORWARD_OOS"
    elif holds > 0 or not complete:
        verdict = "HOLD_INCOMPLETE_OR_INTEGRITY"
    elif all(checks.values()):
        verdict = "REVIEW_ELIGIBLE"
    else:
        verdict = "REJECT_OR_SIMPLIFY_REVIEW"

    return {
        "profile": PROFILE_ID,
        "verdict": verdict,
        "checks": checks,
        "eligible_races": races,
        "distinct_days": days,
        "integrity_holds": holds,
        "automatic_promotion": False,
        "production_change_authorized": False,
        "required_next_action": (
            "EXPLICIT_HUMAN_PROMOTION_REVIEW"
            if verdict == "REVIEW_ELIGIBLE"
            else "CONTINUE_OR_REVISE_NONPRODUCTION_RESEARCH"
        ),
        "principle": "Passing gates is necessary for promotion review and never sufficient for automatic Production change.",
    }
