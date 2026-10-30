"""Summarize frozen-policy replay without tuning rules against payouts."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/local_aki_columns_20261012"


def metrics(rows, arm):
    settlements = [r[arm + "_settlement"] for r in rows
                   if r[arm + "_settlement"]["status"] == "SETTLED"]
    investment = sum(s["investment"] for s in settlements)
    returned = sum(s["return"] for s in settlements)
    cumulative = peak = drawdown = streak = longest = 0
    for s in settlements:
        cumulative += s["profit_loss"]
        peak = max(peak, cumulative)
        drawdown = max(drawdown, peak - cumulative)
        streak = streak + 1 if s["profit_loss"] < 0 else 0
        longest = max(longest, streak)
    largest = max((s["return"] for s in settlements), default=0)
    return {"races": len(settlements), "investment": investment, "return": returned,
            "pfs": returned / investment * 100 if investment else None,
            "profit_loss": returned - investment,
            "hit_races": sum(bool(s["hit_types"]) for s in settlements),
            "hit_but_loss_races": sum(bool(s["hit_types"]) and s["profit_loss"] < 0 for s in settlements),
            "ticket_count": sum(s["ticket_count"] for s in settlements),
            "max_drawdown": drawdown, "max_losing_streak": longest, "largest_payout": largest,
            "pfs_excluding_largest_payout_from_return_only": (returned-largest)/investment*100 if investment else None}


def compare(corpus):
    unique = {}
    for r in corpus["races"]:
        if "candidate_settlement" not in r or r.get("acceptance_only"):
            continue
        key = tuple(r["identity"])
        if key not in unique or r["latest"]["signed_at"] > unique[key]["latest"]["signed_at"]:
            unique[key] = r
    rows = sorted(unique.values(), key=lambda r: (r["identity"][1], r["identity"][0], r["identity"][2]))
    def arms(rr): return {a: metrics(rr, a) for a in ("candidate", "production")}
    def strata(key):
        values = sorted({r[key] for r in rows}, key=str)
        return {str(v): arms([r for r in rows if r[key] == v]) for v in values}
    return {"status": "RETROSPECTIVE_REPLAY / NO PERFORMANCE_PROMOTION",
            "policy_outcomes_not_used_for_tuning": True, "unknown_future_oos_count": 0,
            "unique_settled_non_acceptance_races": len(rows),
            "chronological_order": "date then venue_id then race_no; simultaneous multi-venue order is a reporting convention",
            "all": arms(rows), "by_venue": strata("venue"), "by_field_size": strata("runner_count"),
            "by_class": strata("class"), "by_distance": strata("distance"),
            "role_capture": {c: sum(r["capture"][c] for r in rows) for c in ("W", "P2", "P3")},
            "missing_any_actual_role_count": sum(not all(r["capture"].values()) for r in rows),
            "equal_budget_and_count": {
                "method": "LINEAR_ANALYTIC_NORMALIZATION / NOT_RESELECTION / NOT_INTEGER_100_YEN_EXECUTABLE",
                "eligible_races": sum(r["production_settlement"]["investment"] > 0 and r["candidate_settlement"]["investment"] > 0 for r in rows),
                "candidate_return_scaled_to_production_investment": sum(
                    r["candidate_settlement"]["return"] * r["production_settlement"]["investment"] / r["candidate_settlement"]["investment"]
                    for r in rows if r["candidate_settlement"]["investment"] > 0),
                "same_ticket_count_executable_comparison": "NOT_COMPLETED; no outcome-optimized pruning"},
            "chronological_research_split": {
                "before_20261009": arms([r for r in rows if r["race_date"] < "2026-10-09"]),
                "from_20261009": arms([r for r in rows if r["race_date"] >= "2026-10-09"]),
                "status": "RETROSPECTIVE_ONLY / outcomes available before policy freeze"},
            "tickets_verified_efficient": "Only R3 material coverage and dedupe verified; economic optimality and over/under-width not proven."}


if __name__ == "__main__":
    report = compare(json.loads((OUT / "corpus_audit.json").read_text()))
    (OUT / "comparison.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"races": report["unique_settled_non_acceptance_races"],
                      "all": report["all"], "capture": report["role_capture"]}, ensure_ascii=False))

