from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from typing import Any, Iterable, Mapping

PROFILE_ID = "KM-FAMILY-PFS-OWNER-SCORECARD-20261007-R1"


def _num(v: Any) -> float | None:
    try:
        return None if v is None else float(v)
    except (TypeError, ValueError):
        return None


def _max_drawdown(rows: list[dict[str, Any]]) -> tuple[float, int]:
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    current_losing = 0
    max_losing = 0
    for row in rows:
        pl = float(row.get("profit_loss") or 0.0)
        equity += pl
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
        if pl < 0:
            current_losing += 1
            max_losing = max(max_losing, current_losing)
        else:
            current_losing = 0
    return round(max_dd, 2), max_losing


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    inv = sum(float(x.get("investment") or 0.0) for x in rows)
    ret = sum(float(x.get("return") or 0.0) for x in rows)
    pfs_values = [
        float(x["pfs"]) for x in rows
        if x.get("pfs") is not None
    ]
    max_dd, max_losing = _max_drawdown(rows)
    return {
        "race_count": len(rows),
        "investment": round(inv, 2),
        "return": round(ret, 2),
        "profit_loss": round(ret - inv, 2),
        "pfs": round(ret / inv * 100.0, 9) if inv else None,
        "median_race_pfs": round(statistics.median(pfs_values), 9) if pfs_values else None,
        "hit_races": sum(bool(x.get("hit")) for x in rows),
        "hit_but_loss_count": sum(bool(x.get("hit_but_loss")) for x in rows),
        "hit_but_loss_rate": (
            round(sum(bool(x.get("hit_but_loss")) for x in rows) / len(rows) * 100.0, 6)
            if rows else None
        ),
        "max_drawdown": max_dd,
        "max_losing_streak": max_losing,
    }


def build_owner_scorecard(
    race_reviews: Iterable[Mapping[str, Any]],
    *,
    candidate_comparisons: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    owner_counts = Counter()
    failure_counts = Counter()
    by_bet_type: dict[str, list[dict[str, float]]] = defaultdict(list)

    for raw in race_reviews:
        review = dict(raw)
        capital = review.get("capital") or {}
        pfs_imp = review.get("pfs_improvement") or {}
        investment = _num(capital.get("investment"))
        ret = _num(capital.get("return"))
        pfs = _num(capital.get("pfs"))
        if investment is None or ret is None:
            continue

        row = {
            "race_id": review.get("race_id"),
            "investment": investment,
            "return": ret,
            "profit_loss": ret - investment,
            "pfs": pfs if pfs is not None else (ret / investment * 100.0 if investment else None),
            "hit": bool(capital.get("hit")),
            "hit_but_loss": bool(capital.get("hit_but_loss")),
        }
        rows.append(row)

        first = str((review.get("failure_localization") or {}).get("first_material_failure") or "UNRESOLVED")
        failure_counts[first] += 1
        owner = str((pfs_imp.get("dominant_pfs_loss_owner") or {}).get("owner") or "UNKNOWN")
        owner_counts[owner] += 1

        bt = review.get("by_bet_type") or capital.get("by_bet_type") or {}
        if isinstance(bt, Mapping):
            for bet_type, values in bt.items():
                if not isinstance(values, Mapping):
                    continue
                bi = _num(values.get("investment"))
                br = _num(values.get("return") if values.get("return") is not None else values.get("payout"))
                if bi is None or br is None:
                    continue
                by_bet_type[str(bet_type).upper()].append({
                    "investment": bi,
                    "return": br,
                    "profit_loss": br - bi,
                })

    aggregate = _aggregate(rows)
    total_return = sum(float(x.get("return") or 0.0) for x in rows)
    ranked_returns = sorted(rows, key=lambda x: float(x.get("return") or 0.0), reverse=True)
    largest_share = (
        float(ranked_returns[0]["return"]) / total_return
        if ranked_returns and total_return > 0 else None
    )
    top2_share = (
        sum(float(x["return"]) for x in ranked_returns[:2]) / total_return
        if ranked_returns and total_return > 0 else None
    )
    top3_share = (
        sum(float(x["return"]) for x in ranked_returns[:3]) / total_return
        if ranked_returns and total_return > 0 else None
    )

    bet_type_report = {}
    for bet_type, values in sorted(by_bet_type.items()):
        inv = sum(x["investment"] for x in values)
        ret = sum(x["return"] for x in values)
        bet_type_report[bet_type] = {
            "investment": round(inv, 2),
            "return": round(ret, 2),
            "profit_loss": round(ret - inv, 2),
            "pfs": round(ret / inv * 100.0, 9) if inv else None,
        }

    candidates = {}
    for name, raw in (candidate_comparisons or {}).items():
        c = dict(raw)
        candidates[str(name)] = {
            "investment": _num(c.get("investment")),
            "return": _num(c.get("return")),
            "pfs": _num(c.get("pfs")),
            "profit_loss": _num(c.get("profit_loss")),
            "equal_budget_pfs": _num(c.get("equal_budget_pfs")),
            "equal_ticket_profit": _num(c.get("equal_ticket_profit")),
            "max_drawdown": _num(c.get("max_drawdown")),
            "hit_but_loss_rate": _num(c.get("hit_but_loss_rate")),
            "set_coverage_rate": _num(c.get("set_coverage_rate")),
            "largest_return_share": _num(c.get("largest_return_share")),
        }

    return {
        "profile": PROFILE_ID,
        "aggregate": aggregate,
        "first_material_failure_frequency": dict(failure_counts),
        "dominant_pfs_loss_owner_frequency": dict(owner_counts),
        "by_bet_type": bet_type_report,
        "payout_concentration": {
            "largest_return_race": ranked_returns[0]["race_id"] if ranked_returns else None,
            "largest_return_share": round(largest_share, 9) if largest_share is not None else None,
            "top2_return_share": round(top2_share, 9) if top2_share is not None else None,
            "top3_return_share": round(top3_share, 9) if top3_share is not None else None,
        },
        "candidate_comparisons": candidates,
        "production_change_authorized": False,
        "actual_purchase_pfs_rule": "UNKNOWN unless verified purchase ledger exists.",
        "interpretation_rule": "PFS, prediction utility, conversion quality and capital efficiency must be read separately.",
    }
