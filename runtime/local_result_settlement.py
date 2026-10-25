"""LOCAL's existing flat-result accounting, independent of caller totals.

This is not a JRA normalizer or a new outcome contract. Ties, refunds and
unresolved outcomes must use a separately admitted contract; this path HOLDs.
No prediction, odds, model or Capital policy is used here.
"""
from __future__ import annotations

from itertools import permutations, product

STRUCTURED_RESEARCH_PROFILE = "KM-LOCAL-STRUCTURED-SETTLEMENT-RESEARCH-v1-20261026"


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
        "dead_heat", "finish_groups", "finish_rank_groups", "winning_selections", "top3_orders", "refund_runner_ids",
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


def settle_structured_research(final_ticket, official, *, profile, runner_ids):
    """Adapt PR136's multiple wins/refunds without changing flat admission.

    Explicit research caller only. The active signer, normalizer, RESULT API,
    Source Registry and historical ledgers do not invoke/admit this profile.
    All official top-three permutations must have positive integer payouts;
    each canonical frozen ticket is counted once, with refunds separate.
    """
    if profile != STRUCTURED_RESEARCH_PROFILE:
        raise LocalSettlementError("STRUCTURED_RESEARCH_PROFILE_REQUIRED")
    if not isinstance(official, dict) or official.get("cancelled") or official.get("void"):
        raise LocalSettlementError("STRUCTURED_OFFICIAL_OUTCOME_REQUIRED")
    if any(k in official for k in ("finish_order", "top3", "payouts", "finish_groups", "dead_heat",
                                   "top3_orders", "refunds", "refunded_tickets")):
        raise LocalSettlementError("STRUCTURED_OUTCOME_ALIAS_NOT_ADMITTED")
    groups = official.get("finish_rank_groups")
    if not isinstance(groups, list) or not groups:
        raise LocalSettlementError("OFFICIAL_FINISH_RANK_GROUPS_REQUIRED")
    count, all_ids, top_groups = 0, set(), []
    for group in groups:
        if not isinstance(group, dict) or money(group.get("rank"), "OFFICIAL_RANK") != count + 1:
            raise LocalSettlementError("OFFICIAL_FINISH_RANK_SEQUENCE_INVALID")
        runners = group.get("runners")
        if not isinstance(runners, list) or not runners:
            raise LocalSettlementError("OFFICIAL_FINISH_GROUP_INVALID")
        runners = [money(x, "OFFICIAL_RUNNER") for x in runners]
        if 0 in runners or len(set(runners)) != len(runners) or all_ids.intersection(runners):
            raise LocalSettlementError("OFFICIAL_FINISH_GROUP_DUPLICATE")
        if count < 3:
            top_groups.append(list(permutations(runners, min(len(runners), 3-count))))
        all_ids.update(runners)
        count += len(runners)
    if count < 3:
        raise LocalSettlementError("OFFICIAL_TOP3_INCOMPLETE")
    orders = {tuple(x for part in seq for x in part)[:3] for seq in product(*top_groups)}
    targets = {"EXACTA": {o[:2] for o in orders},
               "TRIO": {tuple(sorted(o)) for o in orders}, "TRIFECTA": orders}
    excluded = official.get("refund_runner_ids", [])
    if not isinstance(excluded, list):
        raise LocalSettlementError("REFUND_RUNNER_IDS_INVALID")
    excluded = [money(x, "REFUND_RUNNER") for x in excluded]
    if (0 in excluded or len(set(excluded)) != len(excluded) or all_ids.intersection(excluded)
            or (excluded and (not isinstance(official.get("refund_authority"), str)
                              or not official["refund_authority"].strip()))):
        raise LocalSettlementError("REFUND_OFFICIAL_AUTHORITY_OR_UNIVERSE_INVALID")
    excluded = set(excluded)
    universe = [money(x, "FROZEN_RUNNER") for x in runner_ids]
    nonfinishers = official.get("nonfinishers", [])
    if not isinstance(nonfinishers, list):
        raise LocalSettlementError("OFFICIAL_NONFINISHERS_INVALID")
    nonfinished = set()
    for row in nonfinishers:
        if not isinstance(row, dict) or row.get("status") not in ("DNF", "DQ"):
            raise LocalSettlementError("OFFICIAL_NONFINISHERS_INVALID")
        rid = money(row.get("runner_id"), "OFFICIAL_NONFINISHER")
        if rid == 0 or rid in nonfinished or rid in all_ids | excluded:
            raise LocalSettlementError("OFFICIAL_NONFINISHERS_INVALID")
        nonfinished.add(rid)
    if (not universe or 0 in universe or len(set(universe)) != len(universe)
            or set(universe) != all_ids | excluded | nonfinished):
        raise LocalSettlementError("OFFICIAL_ALL_RUNNER_STATES_REQUIRED")
    selections = official.get("winning_selections")
    if not isinstance(selections, dict) or set(selections) != set(targets):
        raise LocalSettlementError("OFFICIAL_WINNING_SELECTIONS_INCOMPLETE")
    prices = {}
    for kind in targets:
        rows = selections[kind]
        if not isinstance(rows, list):
            raise LocalSettlementError("OFFICIAL_WINNING_SELECTIONS_INVALID")
        prices[kind] = {}
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("selection"), list):
                raise LocalSettlementError("OFFICIAL_WINNING_SELECTION_INVALID")
            sel = tuple(money(x, "OFFICIAL_RUNNER") for x in row["selection"])
            if kind == "TRIO":
                sel = tuple(sorted(sel))
            pay = money(row.get("payout_per_100"), "OFFICIAL_PAYOUT")
            if sel not in targets[kind] or sel in prices[kind] or pay <= 0:
                raise LocalSettlementError("OFFICIAL_WINNING_SELECTION_INVALID")
            prices[kind][sel] = pay
        if set(prices[kind]) != targets[kind]:
            raise LocalSettlementError("OFFICIAL_WINNING_SELECTIONS_INCOMPLETE")
    # Reuse the strict flat path to validate every ticket, duplicate, unit and
    # stated total. Sentinel outcomes do not settle any real ticket.
    if not isinstance(final_ticket, dict) or not isinstance(final_ticket.get("tickets"), list):
        raise LocalSettlementError("FINAL_TICKET_LIST_REQUIRED")
    frozen_ids = {money(x, "TICKET_RUNNER") for t in final_ticket["tickets"]
                  if isinstance(t, dict) for x in (t.get("selection") or [])}
    if not frozen_ids.issubset(set(universe)):
        raise LocalSettlementError("TICKET_FROZEN_RUNNER_UNIVERSE_MISMATCH")
    sentinel = max(all_ids | excluded | frozen_ids | {0}) + 1
    validated = settle_frozen_tickets(final_ticket, {
        "finish_order": [sentinel, sentinel+1, sentinel+2], "payouts": {}})
    winning, refunded, by_type = [], [], {}
    for t in final_ticket["tickets"]:
        kind = str(t["bet_type"]).upper()
        sel = tuple(money(x, "TICKET_RUNNER") for x in t["selection"])
        key = tuple(sorted(sel)) if kind == "TRIO" else sel
        stake = money(t["stake"], "TICKET_STAKE")
        row = by_type.setdefault(kind, {"investment": 0, "winning_return": 0, "refund": 0})
        row["investment"] += stake
        if excluded.intersection(sel):
            row["refund"] += stake
            refunded.append({"bet_type": kind, "selection": list(sel), "stake": stake, "refund": stake})
        elif key in prices[kind]:
            amount = stake * prices[kind][key] // 100
            row["winning_return"] += amount
            winning.append({"bet_type": kind, "selection": list(sel), "stake": stake,
                            "payout_per_100": prices[kind][key], "return": amount})
    gross = validated["investment"]
    refund = sum(r["refund"] for r in by_type.values())
    win = sum(r["winning_return"] for r in by_type.values())
    for row in by_type.values():
        row.update(effective_stake=row["investment"]-row["refund"],
                   return_including_refund=row["winning_return"]+row["refund"])
    return {"profile": profile, "status": "RESEARCH_SETTLED_NOT_FORMAL",
            "investment": gross, "gross_stake": gross, "effective_stake": gross-refund,
            "winning_return": win, "refund": refund, "return": win+refund,
            "profit_loss": win+refund-gross, "pfs": (win+refund)*100/gross if gross else None,
            "refund_adjusted_pfs": win*100/(gross-refund) if gross>refund else None,
            "winning_tickets": winning, "refunded_tickets": refunded, "by_type": by_type,
            "official_top3_orders": [list(o) for o in sorted(orders)],
            "production_authority": False, "new_forward_oos_credit": 0}
