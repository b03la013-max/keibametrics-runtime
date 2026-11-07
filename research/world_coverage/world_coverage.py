"""Offline, non-production coverage of frozen role worlds.

ANY_WIN is a payable-event diagnostic, never Exact Triple protection.
No result, probability, odds, KRS frequency or production writer is accepted.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import math

KINDS = {"EXACTA": 2, "TRIO": 3, "TRIFECTA": 3}
MODES = {"ANY_WIN", "ORDERED_PAIR", "TOP3_SET", "EXACT_TRIPLE"}
PROFILE = "JRA-FROZEN-WORLD-COVERAGE-RESEARCH-v1"
MAX_SAFE_TOTAL = 2**31 - 1


def number(value):
    if isinstance(value, bool):
        raise ValueError("HORSE_NUMBER_INVALID")
    out = int(value)
    if str(out) != str(value) or not 1 <= out <= 18:
        raise ValueError("HORSE_NUMBER_INVALID")
    return out


def world(value):
    out = tuple(number(v) for v in value)
    if len(out) != 3 or len(set(out)) != 3:
        raise ValueError("WORLD_REPEATED_OR_MISSING_HORSE")
    return out


@dataclass(frozen=True, order=True)
class Ticket:
    kind: str
    selection: tuple[int, ...]
    cost: int = 100

    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError("UNAUTHORIZED_BET_KIND")
        sel = tuple(number(v) for v in self.selection)
        if len(sel) != KINDS[self.kind] or len(set(sel)) != len(sel):
            raise ValueError("TICKET_SELECTION_INVALID")
        if type(self.cost) is not int or self.cost <= 0 or self.cost % 100:
            raise ValueError("STAKE_INVALID")
        object.__setattr__(self, "selection", tuple(sorted(sel)) if self.kind == "TRIO" else sel)


def worlds_from_frozen(final, *, include_protected=False):
    """Frozen PURCHASE rows; optional PROTECT rows are a separate research scope.

    Including PROTECT explores orientation without adding a horse after results;
    it does not grant that row Production Exact-Third purchase authority.
    """
    if type(include_protected) is not bool:
        raise ValueError("PROTECTED_SCOPE_MUST_BE_EXPLICIT_BOOLEAN")
    roles = final["final_prediction_package"]["roles"]
    valid = {number(h) for h in roles}
    heads = {number(h) for h, columns in roles.items() if "W" in columns}
    pairs = {(number(p["head"]), number(p["second"]))
             for p in final.get("pair_dispositions", [])
             if p.get("status") == "PURCHASE"}
    out = set()
    for t in final.get("third_dispositions", []):
        if t.get("status") not in ({"PURCHASE", "PROTECT"} if include_protected else {"PURCHASE"}):
            continue
        w = world((t["head"], t["second"], t["third"]))
        if not set(w) <= valid or w[0] not in heads or w[:2] not in pairs:
            raise ValueError("FROZEN_ROLE_PAIR_THIRD_MISMATCH")
        if "P2" not in roles[str(w[1])] or "P3" not in roles[str(w[2])]:
            raise ValueError("FROZEN_ROLE_PAIR_THIRD_MISMATCH")
        out.add(w)
    return tuple(sorted(out))


def candidate_tickets(worlds, kinds=("EXACTA", "TRIO", "TRIFECTA")):
    kinds = tuple(kinds)
    if not set(kinds) <= KINDS.keys():
        raise ValueError("UNAUTHORIZED_BET_KIND")
    out = set()
    for w in map(world, worlds):
        for k in kinds:
            out.add(Ticket(k, w[:2] if k == "EXACTA" else w))
    return tuple(sorted(out))


def covers(ticket, value, mode="ANY_WIN"):
    w = world(value)
    if mode not in MODES:
        raise ValueError("COVERAGE_MODE_INVALID")
    wanted = {"ORDERED_PAIR": "EXACTA", "TOP3_SET": "TRIO",
              "EXACT_TRIPLE": "TRIFECTA"}.get(mode)
    if wanted and ticket.kind != wanted:
        return False
    target = w[:2] if ticket.kind == "EXACTA" else tuple(sorted(w)) if ticket.kind == "TRIO" else w
    return ticket.selection == target


def coverage(tickets, worlds):
    ws = tuple(sorted(set(map(world, worlds))))
    ts = tuple(tickets)
    return {mode: sum(any(covers(t, w, mode) for t in ts) for w in ws)
            for mode in sorted(MODES)} | {"world_count": len(ws)}


def _validated(worlds, tickets, weights):
    ws = tuple(sorted(set(map(world, worlds))))
    ts = tuple(sorted(tickets))
    if len(set((t.kind, t.selection) for t in ts)) != len(ts):
        raise ValueError("DUPLICATE_TICKET")
    supplied = weights if weights is not None else {w: 1 for w in ws}
    if set(supplied) != set(ws) or any(type(v) is not int or v <= 0 for v in supplied.values()):
        raise ValueError("IMPORTANCE_MUST_BE_POSITIVE_INTEGER_NOT_PROBABILITY")
    if sum(supplied.values()) > MAX_SAFE_TOTAL or sum(t.cost for t in ts) > MAX_SAFE_TOTAL:
        raise ValueError("RESEARCH_INTEGER_RANGE_EXCEEDED")
    if len(ws) > 5000 or len(ts) > 10000:
        raise ValueError("RESEARCH_MODEL_SIZE_LIMIT")
    return ws, ts, [supplied[w] for w in ws]


def optimize(worlds, tickets, *, mode, budget=None, weights=None, time_limit=15):
    """Minimum full cover if budget=None; otherwise maximum importance at cap.

    A second solve minimizes spend at the best achieved coverage. OPTIMAL is
    returned only for solver status 0 in both solves and independently checked
    integer feasibility. A time-limited solution is never called a minimum.
    """
    import numpy as np
    from scipy.optimize import milp, Bounds, LinearConstraint

    if mode not in MODES:
        raise ValueError("COVERAGE_MODE_INVALID")
    if budget is not None and (type(budget) is not int or budget < 0 or budget > MAX_SAFE_TOTAL or budget % 100):
        raise ValueError("BUDGET_INVALID")
    if not math.isfinite(time_limit) or time_limit <= 0:
        raise ValueError("TIME_LIMIT_INVALID")
    ws, ts, importance = _validated(worlds, tickets, weights)
    common = {"profile": PROFILE, "production_effect": "NONE", "purchase_authority": False,
              "mode": mode, "result_used_in_selection": False, "world_count": len(ws),
              "budget": budget, "importance_semantics": "NON_PROBABILISTIC_PROTECTION_ONLY"}
    if not ws or not ts:
        return common | {"status": "EMPTY" if not ws else "NO_CANDIDATES", "optimal": not ws,
                         "tickets": (), "cost": 0, "importance_covered": 0,
                         "coverage": coverage((), ws)}
    A = np.array([[int(covers(t, w, mode)) for t in ts] for w in ws], dtype=float)
    costs = np.array([t.cost for t in ts], dtype=float)
    options = {"time_limit": time_limit, "mip_rel_gap": 0.0}
    n, m = len(ts), len(ws)
    second_solver_status = None
    tie_solved = False
    if budget is None:
        result = milp(costs, integrality=np.ones(n), bounds=Bounds(0, 1),
                      constraints=LinearConstraint(A, 1, np.inf), options=options)
        final = result
    else:
        matrix = np.concatenate([A, -np.eye(m)], axis=1)
        constraints = [LinearConstraint(matrix, 0, np.inf),
                       LinearConstraint(np.r_[costs, np.zeros(m)], 0, budget)]
        objective = np.r_[np.zeros(n), -np.array(importance)]
        result = milp(objective, integrality=np.ones(n+m), bounds=Bounds(0, 1),
                      constraints=constraints, options=options)
        final = result
        if result.x is not None:
            achieved = sum(v for v, y in zip(importance, result.x[n:]) if y > .5)
            constraints.append(LinearConstraint(np.r_[np.zeros(n), importance], achieved, np.inf))
            second = milp(np.r_[costs, np.zeros(m)], integrality=np.ones(n+m),
                          bounds=Bounds(0, 1), constraints=constraints, options=options)
            second_solver_status = int(second.status)
            if second.x is not None:
                final = second
                tie_solved = second.status == 0
    if final.x is None:
        return common | {"status": "INFEASIBLE" if final.status == 2 else "SOLVER_UNRESOLVED",
                         "optimal": False, "tickets": (), "cost": 0, "importance_covered": 0,
                         "coverage": coverage((), ws), "solver_status": int(final.status)}
    if any(abs(float(x)-round(float(x))) > 1e-6 for x in final.x):
        raise ValueError("SOLVER_NONINTEGRAL_SOLUTION")
    selected = tuple(t for t, x in zip(ts, final.x[:n]) if x > .5)
    spent = sum(t.cost for t in selected)
    flags = [any(covers(t, w, mode) for t in selected) for w in ws]
    if budget is None and not all(flags):
        raise ValueError("SOLVER_INCOMPLETE_FULL_COVER")
    if budget is not None and spent > budget:
        raise ValueError("SOLVER_BUDGET_VIOLATION")
    optimal = result.status == 0 and final.status == 0 and (budget is None or tie_solved)
    return common | {"status": "OPTIMAL" if optimal else "FEASIBLE_LIMIT_NOT_OPTIMAL",
                     "optimal": optimal, "tickets": selected, "cost": spent,
                     "importance_covered": sum(v for v, flag in zip(importance, flags) if flag),
                     "coverage": coverage(selected, ws), "solver_status": int(final.status),
                     "first_solver_status": int(result.status),
                     "second_solver_status": second_solver_status,
                     "minimum_spend_tie_break_proven": tie_solved if budget is not None else None}


def brute_force(worlds, tickets, *, mode, budget=None):
    """Independent tiny-case oracle for research tests; no race results."""
    if len(tickets) > 16:
        raise ValueError("BRUTE_FORCE_TEST_LIMIT")
    best = None
    for n in range(len(tickets)+1):
        for selected in combinations(tickets, n):
            spent = sum(t.cost for t in selected)
            if budget is not None and spent > budget:
                continue
            count = sum(any(covers(t, w, mode) for t in selected) for w in worlds)
            if budget is None and count != len(worlds):
                continue
            key = (spent,) if budget is None else (-count, spent)
            if best is None or key < best[0]:
                best = key, selected
    return best

