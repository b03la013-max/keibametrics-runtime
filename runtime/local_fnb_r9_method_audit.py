"""Validate six ALTERNATIVE owner-method ticket trees, not one pooled bet.

Read-only post-FINAL display audit. This is not predictive authorization,
a signed ticket, capital policy update, a delivered message or a purchase.
"""
from __future__ import annotations

from runtime.jra_ticket_tree_renderer import render_ticket_tree, TicketTreeError

OWNERS = ("BASELINE", "CANDIDATE")
METHODS = ("EXACTA", "TRIO", "TRIFECTA")


def audit_methods(portfolios):
    failures = []
    verified = []
    if not isinstance(portfolios, dict) or set(portfolios) != set(OWNERS):
        return {"complete": False, "failures": ["DUAL_OWNER_SIX_METHODS_MISSING"],
                "methods": verified}
    for owner in OWNERS:
        methods = portfolios[owner]
        if not isinstance(methods, dict) or set(methods) != set(METHODS):
            failures.append("DUAL_OWNER_METHODS_INCOMPLETE:" + owner)
            continue
        for method in METHODS:
            entry = methods[method]
            label = owner + "." + method
            if not isinstance(entry, dict):
                failures.append("METHOD_ENTRY_NOT_OBJECT:" + label)
                continue
            tickets = entry.get("tickets")
            points, total, budget, remaining = (
                entry.get("point_count"), entry.get("total_investment"),
                entry.get("capital_limit"), entry.get("unused_capital"))
            if (not isinstance(tickets, list) or type(points) is not int
                    or type(total) is not int or type(budget) is not int
                    or type(remaining) is not int or
                    min(points, total, budget, remaining) < 0):
                failures.append("METHOD_STAKES_OR_COUNTS_MISSING:" + label)
                continue
            if len(tickets) != points or total + remaining != budget:
                failures.append("METHOD_STAKES_OR_COUNTS_MISMATCH:" + label)
                continue
            no_bet = entry.get("no_bet")
            if type(no_bet) is not bool:
                failures.append("METHOD_NO_BET_NOT_EXPLICIT:" + label)
                continue
            if (no_bet and (tickets or total != 0 or
                            not isinstance(entry.get("reason"), str) or
                            not entry["reason"].strip())):
                failures.append("METHOD_FALSE_NO_BET:" + label)
                continue
            if not no_bet and (not tickets or total == 0):
                failures.append("METHOD_UNCALCULATED_ZERO_TICKETS:" + label)
                continue
            if (any(not isinstance(t, dict) or
                    t.get("bet_type") != method for t in tickets)):
                failures.append("METHOD_WRONG_TICKET_TYPE:" + label)
                continue
            # Rebuild the same per-method ticket tree with the existing
            # canonical renderer; its round-trip catches wrong permutations,
            # duplicates, stake units and missing ordered orientations.
            artifact = {"final_ticket": {"tickets": tickets, "no_bet": no_bet},
                        "capital_policy_decision": {
                            "decision": "RECOMMENDATION_ONLY"}}
            try:
                result = render_ticket_tree(artifact)
            except (ValueError, KeyError, TypeError, TicketTreeError) as exc:
                failures.append("METHOD_TREE_ROUNDTRIP_INVALID:" + label +
                                ":" + type(exc).__name__)
                continue
            if (result["ticket_count"] != points or
                    result["total_investment"] != total or
                    entry.get("canonical_tree") != result["text"]):
                failures.append("METHOD_RENDERED_TREE_OR_TOTAL_MISMATCH:" + label)
                continue
            verified.append({"owner": owner, "method": method,
                             "point_count": points, "stake_total": total,
                             "unused_capital": remaining,
                             "no_bet": no_bet})
    return {"complete": len(verified) == 6 and not failures,
            "failures": failures, "methods": verified,
            "six_alternative_portfolios_not_pooled": True,
            "actual_purchase_verified": False,
            "recipient_ack_verified": False}
