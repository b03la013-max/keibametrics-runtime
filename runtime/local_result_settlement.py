"""LOCAL's existing flat-result accounting, independent of caller totals.

This is not a JRA normalizer or a new outcome contract. Ties, refunds and
unresolved outcomes must use a separately admitted contract; this path HOLDs.
No prediction, odds, model or Capital policy is used here.
"""
from __future__ import annotations


class LocalSettlementError(ValueError):
    pass


def money(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise LocalSettlementError(name + "_INVALID")
    text = str(value)
    if not text.isascii() or not text.isdigit():
        raise LocalSettlementError(name + "_INVALID")
    try:
        return int(text)
    except ValueError as exc:
        raise LocalSettlementError(name + "_INVALID") from exc


def settle_frozen_tickets(final_ticket, official):
    """Return exact flat accounting or refuse before a COMPLETE signature.

    A missing winning payout is UNKNOWN, not zero. A cancelled runner cannot
    be silently converted into a loss. Returned facts are newly allocated;
    the frozen FINAL and official observation are never changed.
    """
    if not isinstance(final_ticket, dict) or not isinstance(final_ticket.get("tickets"), list):
        raise LocalSettlementError("FINAL_TICKET_LIST_REQUIRED")
    if not isinstance(official, dict):
        raise LocalSettlementError("OFFICIAL_RESULT_REQUIRED")
    if any(official.get(k) for k in (
        "dead_heat", "finish_groups", "top3_orders", "refund_runner_ids",
        "refunds", "refunded_tickets", "cancelled", "void")):
        raise LocalSettlementError("LOCAL_NONFLAT_RESULT_NOT_SETTLED")
    order = official.get("finish_order")
    if not isinstance(order, list) or len(order) < 3:
        raise LocalSettlementError("OFFICIAL_FINISH_ORDER_REQUIRED")
    order = [money(x, "OFFICIAL_RUNNER") for x in order]
    if 0 in order or len(set(order)) != len(order):
        raise LocalSettlementError("LOCAL_NONFLAT_RESULT_NOT_SETTLED")
    payouts = official.get("payouts")
    if not isinstance(payouts, dict):
        raise LocalSettlementError("OFFICIAL_PAYOUTS_REQUIRED")
    payouts = {str(k).upper(): money(v, "OFFICIAL_PAYOUT") for k, v in payouts.items()}
    targets = {"EXACTA": order[:2], "TRIO": sorted(order[:3]), "TRIFECTA": order[:3]}
    total, returned, winning, by_type, seen = 0, 0, [], {}, set()
    for ticket in final_ticket["tickets"]:
        if not isinstance(ticket, dict):
            raise LocalSettlementError("FROZEN_TICKET_INVALID")
        kind = str(ticket.get("bet_type") or "").upper()
        selection = ticket.get("selection")
        if kind not in targets or not isinstance(selection, list):
            raise LocalSettlementError("LOCAL_UNSUPPORTED_SETTLEMENT_TICKET_HOLD")
        selection = [money(x, "TICKET_RUNNER") for x in selection]
        if (len(selection) != len(targets[kind]) or 0 in selection
                or len(set(selection)) != len(selection)):
            raise LocalSettlementError("FROZEN_TICKET_SELECTION_INVALID")
        canonical = sorted(selection) if kind == "TRIO" else selection
        identity = (kind, tuple(canonical))
        if identity in seen:
            raise LocalSettlementError("DUPLICATE_FROZEN_TICKET")
        seen.add(identity)
        stake = money(ticket.get("stake"), "TICKET_STAKE")
        if stake <= 0 or stake % 100:
            raise LocalSettlementError("TICKET_STAKE_UNIT_INVALID")
        row = by_type.setdefault(kind, {"investment": 0, "return": 0, "wins": []})
        total += stake
        row["investment"] += stake
        if canonical == targets[kind]:
            if payouts.get(kind, 0) <= 0:
                raise LocalSettlementError("RESULT_WINNING_PAYOUT_NOT_READY:" + kind)
            amount = stake * payouts[kind] // 100
            win = {"bet_type": kind, "selection": selection, "stake": stake,
                   "payout_per_100": payouts[kind], "return": amount}
            winning.append(win)
            row["wins"].append(win)
            row["return"] += amount
            returned += amount
    if final_ticket.get("total_investment") is not None:
        if money(final_ticket["total_investment"], "FINAL_TICKET_INVESTMENT") != total:
            raise LocalSettlementError("FINAL_TICKET_TOTAL_MISMATCH")
    return {"investment": total, "return": returned, "winning_tickets": winning,
            "by_type": by_type, "gross_stake": total, "effective_stake": total,
            "refund": 0}
