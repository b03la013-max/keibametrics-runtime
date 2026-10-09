"""JRA read-only transfer of LOCAL's 2026-10-03..09 conversion evidence.

Reuse the existing Family conversion diagnostic; add JRA-only matrix,
cross-ticket and exposure observations to the frozen Candidate FINAL.
No role, pair, third, ticket, stake, AKI or Production policy is changed.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import datetime
from typing import Any, Mapping

from family_conversion_diagnostics import build_diagnostics

PROFILE = "KM-JRA-LOCAL-WEEK-CONVERSION-OBSERVATION-SHADOW-20261010-R1"
VALID_PAIR = {"PURCHASE", "PROTECT", "EXCLUDE"}
MATERIAL = {"PURCHASE", "PROTECT", "MATERIAL"}
VALID_THIRD = {"PURCHASE", "PROTECT", "EXCLUDE", "MATERIAL"}
BET_TYPES = {"EXACTA": 2, "TRIO": 3, "TRIFECTA": 3}


def _sha(x: Any) -> str:
    return hashlib.sha256(
        json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _when(s: Any) -> datetime:
    value = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("JRA_TRANSFER_TIMEZONE_REQUIRED")
    return value


def _sel(t: Mapping[str, Any]) -> tuple[str, tuple[int, ...], int]:
    bet = str(t.get("bet_type") or "").upper()
    if bet not in BET_TYPES:
        raise ValueError("JRA_TRANSFER_UNSUPPORTED_BET_TYPE")
    selection = tuple(int(x) for x in t["selection"])
    if len(selection) != BET_TYPES[bet] or len(set(selection)) != len(selection):
        raise ValueError("JRA_TRANSFER_INVALID_TICKET_SELECTION")
    stake = int(t["stake"])
    if stake <= 0 or stake % 100:
        raise ValueError("JRA_TRANSFER_INVALID_STAKE")
    return bet, tuple(sorted(selection)) if bet == "TRIO" else selection, stake


def build_jra_week_transfer_shadow(
    req: Mapping[str, Any],
    tickets: list[Mapping[str, Any]],
    krs_utility: Mapping[str, Any] | None,
    *,
    generated_at: str,
) -> dict[str, Any]:
    if req.get("family_id") != "JRA" or (req.get("base_index_mapping_authority") or {}).get("production_authority") is not False:
        raise ValueError("JRA_TRANSFER_FAMILY_OR_AUTHORITY_MISMATCH")
    semantic = req.get("candidate_semantic_freeze") or {}
    if not semantic.get("sha256") or semantic["sha256"] != _sha({k: v for k, v in semantic.items() if k != "sha256"}):
        raise ValueError("JRA_TRANSFER_SEMANTIC_FREEZE_INVALID")
    basis = req.get("source_snapshot_sha256")
    if not isinstance(basis, str) or len(basis) != 64:
        raise ValueError("JRA_TRANSFER_SOURCE_BASIS_MISSING")

    generated = _when(generated_at)
    post = _when(req.get("scheduled_post_at"))
    preregistered = (
        req.get("temporal_mode") == "FORMAL-PRE-RACE"
        and not bool(req.get("acceptance_only"))
        and generated < post
    )
    if req.get("temporal_mode") == "FORMAL-PRE-RACE" and not req.get("acceptance_only") and not preregistered:
        raise ValueError("JRA_TRANSFER_AFTER_SCHEDULED_POST")

    pairs: dict[tuple[int, int], dict[str, Any]] = {}
    for row in req.get("pair_dispositions") or []:
        key = (int(row["head"]), int(row["second"]))
        if key in pairs:
            raise ValueError("JRA_TRANSFER_DUPLICATE_PAIR")
        pairs[key] = dict(row)
    thirds: dict[tuple[int, int, int], dict[str, Any]] = {}
    for row in req.get("third_dispositions") or []:
        key = (int(row["head"]), int(row["second"]), int(row["third"]))
        if key in thirds:
            raise ValueError("JRA_TRANSFER_DUPLICATE_THIRD")
        thirds[key] = dict(row)

    roles = req.get("static_prediction", {}).get("roles") or {}
    heads = {int(x) for x in (req.get("purchased_heads") or [])}
    heads |= {int(h) for h, vals in roles.items() if any(
        str(v).upper().startswith("W") or "ALTERNATIVE-W" in str(v).upper()
        for v in vals or []
    )}
    global_p2 = {int(h) for h, vals in roles.items() if "P2" in {str(v).upper() for v in vals or []}}
    global_p3 = {int(h) for h, vals in roles.items() if "P3" in {str(v).upper() for v in vals or []}}

    head_local_matrix = []
    open_pair_cells = []
    for h in sorted(heads):
        for s in sorted(global_p2 - {h}):
            p = pairs.get((h, s))
            status = str((p or {}).get("status") or "NOT_TERMINALIZED").upper()
            reason = (p or {}).get("reason")
            valid = status in VALID_PAIR and bool(str(reason or "").strip())
            row = {"head": h, "second": s, "status": status,
                   "reason": reason, "terminalized": valid}
            head_local_matrix.append(row)
            if not valid:
                open_pair_cells.append(row)

    pair_third_cells = []
    open_purchased_thirds = []
    for (h, s), p in sorted(pairs.items()):
        pair_status = str(p.get("status") or "").upper()
        if pair_status not in MATERIAL:
            continue
        for t in sorted(global_p3 - {h, s}):
            x = thirds.get((h, s, t))
            status = str((x or {}).get("status") or "NOT_TERMINALIZED").upper()
            reason = (x or {}).get("reason")
            terminal = status in VALID_THIRD and bool(str(reason or "").strip())
            row = {"head": h, "second": s, "third": t,
                   "pair_status": pair_status, "third_status": status,
                   "reason": reason, "terminalized": terminal,
                   "purchased_pair": pair_status == "PURCHASE"}
            pair_third_cells.append(row)
            # PROTECT-only pairs are deferred research routes, not required purchases.
            if pair_status == "PURCHASE" and not terminal:
                open_purchased_thirds.append(row)

    purchased: dict[str, set[tuple[int, ...]]] = {name: set() for name in BET_TYPES}
    stakes = defaultdict(int)
    head_exposure = defaultdict(int)
    horse_exposure = defaultdict(int)
    set_bet_types = defaultdict(set)
    sum_stakes = 0
    for ticket in tickets:
        bet, sel, stake = _sel(ticket)
        if sel in purchased[bet]:
            raise ValueError("JRA_TRANSFER_DUPLICATE_PURCHASED_TICKET")
        purchased[bet].add(sel)
        stakes[bet] += stake
        sum_stakes += stake
        for h in sel:
            horse_exposure[h] += stake
        if bet != "TRIO":
            head_exposure[sel[0]] += stake
        if len(sel) == 3:
            set_bet_types[tuple(sorted(sel))].add(bet)

    missing_trio_for_exact = [
        list(e) for e in sorted(purchased["TRIFECTA"])
        if tuple(sorted(e)) not in purchased["TRIO"]
    ]
    missing_exact_for_pair = [
        list(p) for p in sorted(purchased["TRIFECTA"])
        if p[:2] not in purchased["EXACTA"]
    ]
    shared_horse_exposure = [
        {"runner_id": h, "stake_yen": yen,
         "share_of_portfolio_pct": round(100 * yen / sum_stakes, 4) if sum_stakes else None}
        for h, yen in sorted(horse_exposure.items(), key=lambda item: (-item[1], item[0]))
    ]
    scenario_overlap = [
        {"three_horse_set": list(s), "purchased_bet_types": sorted(types)}
        for s, types in sorted(set_bet_types.items()) if len(types) > 1
    ]

    # Import existing family-neutral hypotheses without rewriting LOCAL or JRA policies.
    prior = build_diagnostics(
        dict(req), {"tickets": list(tickets)},
        req.get("final_prediction_package") or {}, dict(krs_utility or {}),
        generated_at, basis
    )

    aki = req.get("aki_capital_bridge") or {}
    trace = {
        "profile": PROFILE,
        "status": "JRA-CANDIDATE-SHADOW / READ-ONLY / NO-AUTO-PROMOTION",
        "race_id": req.get("race_id"),
        "generated_at": generated_at,
        "scheduled_post_at": req.get("scheduled_post_at"),
        "temporal_class": "FORWARD_PRE_RESULT" if preregistered else "ACCEPTANCE_OR_REPLAY_NO_OOS_CREDIT",
        "source_basis_sha256": basis,
        "semantic_freeze_sha256": semantic["sha256"],
        "candidate_policy_cohort": req.get("candidate_policy_cohort"),
        "head_local_p2_matrix": head_local_matrix,
        "head_local_p2_unterminalized": open_pair_cells,
        "pair_conditioned_third_matrix": pair_third_cells,
        "purchased_pair_third_unterminalized": open_purchased_thirds,
        "cross_ticket_diagnostic": {
            "purchased_exact_without_same_set_trio": missing_trio_for_exact,
            "purchased_trifecta_without_same_head_exacta": missing_exact_for_pair,
            "overlapping_trio_trifecta_sets": scenario_overlap,
            "note": "Observation only; missing other bet-type ticket is not intrinsically an error."
        },
        "capital_exposure_diagnostic": {
            "total_yen": sum_stakes,
            "by_bet_type_yen": dict(sorted(stakes.items())),
            "head_exposure_yen": dict(sorted(head_exposure.items())),
            "horse_exposure": shared_horse_exposure,
            "unpriced_world_concentration": "NOT CALCULATED / NO AUTHORIZED SCENARIO WEIGHTS",
            "fixed_exposure_cap_applied": False,
            "budget_influenced_semantics": False
        },
        "score_confidence": {
            "score_not_evidence_confidence": True,
            "aki_bridge_status": aki.get("status") or "FORMAL_AKI_NOT_AVAILABLE",
            "formal_jra_aki": "EXPLICIT GAP / NO LOCAL AKI COEFFICIENT TRANSFER",
        },
        "inherited_family_diagnostics": {
            "profile": prior.get("profile"),
            "sha256": prior.get("sha256"),
            "winner_role_migration_candidates": prior.get("winner_role_migration_candidates"),
            "pair_residual_candidates": prior.get("pair_residual_candidates"),
            "selective_exact_candidates": prior.get("selective_exact_candidates")
        },
        "evidence_class": "PRE_RESULT_OBSERVABILITY_ONLY / NOT_PROVEN_PREDICTION_GAIN",
        "production_effect": "NONE",
        "numeric_effect": "NONE",
        "semantic_effect": "NONE",
        "purchase_authority": False,
        "automatic_purchase": False,
        "automatic_promotion": False,
        "local_aki_adaptive_paper_policy_imported": False,
        "mec_r5_arm_definitions_changed": False,
        "mec_r3_changed": False
    }
    trace["sha256"] = _sha(trace)
    return trace


def evaluate_jra_week_transfer_shadow_result(
    frozen: Mapping[str, Any],
    pre_result: Mapping[str, Any],
    actual_top3: list[int],
) -> dict[str, Any]:
    """Attribute *already frozen* conversion decisions to a later RESULT.

    This does not reconstruct or alter prediction, tickets, capital or OOS
    eligibility.  It labels first lost conversion links and capital exposures
    without imputing unpurchased winning tickets or counterfactual payout.
    """
    if frozen.get("sha256") != _sha({k: v for k, v in frozen.items() if k != "sha256"}):
        raise ValueError("JRA_TRANSFER_FROZEN_SHADOW_HASH_INVALID")
    if str(frozen.get("sha256")) != str(pre_result.get("jra_local_week_transfer_shadow_sha256")):
        raise ValueError("JRA_TRANSFER_PRE_RESULT_SHADOW_BINDING_MISMATCH")
    if str(frozen.get("race_id")) != str(pre_result.get("race_id")):
        raise ValueError("JRA_TRANSFER_RACE_ID_MISMATCH")
    if str(frozen.get("source_basis_sha256")) != str(pre_result.get("source_snapshot_sha256")):
        raise ValueError("JRA_TRANSFER_SOURCE_BASIS_MISMATCH")
    if str(frozen.get("semantic_freeze_sha256")) != str(pre_result.get("candidate_semantic_freeze_sha256")):
        raise ValueError("JRA_TRANSFER_SEMANTIC_BASIS_MISMATCH")
    if str(frozen.get("scheduled_post_at")) != str(pre_result.get("scheduled_post_at")):
        raise ValueError("JRA_TRANSFER_SCHEDULE_MISMATCH")
    if frozen.get("production_effect") != "NONE" or frozen.get("purchase_authority") is not False:
        raise ValueError("JRA_TRANSFER_PRODUCTION_FIREWALL")
    if (frozen.get("temporal_class") != "FORWARD_PRE_RESULT"
            or pre_result.get("oos_eligible") is not True
            or pre_result.get("candidate_final_verified") is not True
            or _when(frozen.get("generated_at")) >= _when(frozen.get("scheduled_post_at"))):
        raise ValueError("JRA_TRANSFER_NOT_FROZEN_FORWARD_OOS")
    if not isinstance(actual_top3, list) or len(actual_top3) < 3:
        raise ValueError("JRA_TRANSFER_ACTUAL_TOP3_REQUIRED")
    actual = [int(x) for x in actual_top3[:3]]
    if any(x <= 0 for x in actual) or len(set(actual)) != 3:
        raise ValueError("JRA_TRANSFER_ACTUAL_TOP3_INVALID")
    w, p2, p3 = actual

    pair_matrix = frozen.get("head_local_p2_matrix") or []
    third_matrix = frozen.get("pair_conditioned_third_matrix") or []
    all_heads = {int(x["head"]) for x in pair_matrix}
    all_heads |= {int(x) for x in (frozen.get("capital_exposure_diagnostic") or {}).get("head_exposure_yen", {})}
    global_p2 = {int(x["second"]) for x in pair_matrix}
    global_p3 = {int(x["third"]) for x in third_matrix}
    actual_pair = next((x for x in pair_matrix
                        if int(x["head"]) == w and int(x["second"]) == p2), None)
    actual_third = next((x for x in third_matrix
                         if int(x["head"]) == w and int(x["second"]) == p2
                         and int(x["third"]) == p3), None)
    head_present = w in all_heads
    p2_present = p2 in global_p2
    p3_present = p3 in global_p3
    pair_status = str((actual_pair or {}).get("status") or "NOT_IN_FROZEN_MATRIX")
    third_status = str((actual_third or {}).get("third_status") or "NOT_IN_FROZEN_MATRIX")
    pair_terminal = bool((actual_pair or {}).get("terminalized"))
    third_terminal = bool((actual_third or {}).get("terminalized"))
    if not head_present:
        first_loss = "WINNER_HEAD_NOT_IN_FROZEN_MATRIX"
    elif not p2_present:
        first_loss = "ACTUAL_SECOND_NOT_IN_GLOBAL_P2"
    elif not pair_terminal:
        first_loss = "HEAD_LOCAL_P2_UNTERMINALIZED"
    elif pair_status == "EXCLUDE":
        first_loss = "HEAD_LOCAL_P2_EXCLUDED_WITH_REASON"
    elif pair_status == "PROTECT":
        first_loss = "HEAD_LOCAL_P2_PROTECTED_NOT_PURCHASE_DECLARED"
    elif not p3_present:
        first_loss = "ACTUAL_THIRD_NOT_IN_GLOBAL_P3"
    elif not third_terminal:
        first_loss = "PURCHASED_PAIR_THIRD_UNTERMINALIZED"
    elif third_status == "EXCLUDE":
        first_loss = "PAIR_LOCAL_THIRD_EXCLUDED_WITH_REASON"
    elif third_status == "PROTECT":
        first_loss = "PAIR_LOCAL_THIRD_PROTECTED_NOT_PURCHASE_DECLARED"
    else:
        first_loss = "NO_DECLARED_ROLE_PAIR_THIRD_LOSS"

    exposure = frozen.get("capital_exposure_diagnostic") or {}
    head_exposure = exposure.get("head_exposure_yen") or {}
    horse_exposure = {
        int(x["runner_id"]): x for x in exposure.get("horse_exposure") or []
    }
    absent_trios = {
        tuple(int(x) for x in row)
        for row in (frozen.get("cross_ticket_diagnostic") or {}).get(
            "purchased_exact_without_same_set_trio") or []
    }
    absent_exactas = {
        tuple(int(x) for x in row)
        for row in (frozen.get("cross_ticket_diagnostic") or {}).get(
            "purchased_trifecta_without_same_head_exacta") or []
    }
    all_pair_cells = len(pair_matrix)
    all_third_cells = len(third_matrix)
    out = {
        "profile": "KM-JRA-LOCAL-WEEK-TRANSFER-RESULT-ATTRIBUTION-20261010-R1",
        "race_id": pre_result.get("race_id"),
        "pre_result_record_sha256": pre_result.get("sha256"),
        "frozen_shadow_sha256": frozen.get("sha256"),
        "candidate_policy_cohort": frozen.get("candidate_policy_cohort"),
        "actual_top3": actual,
        "winner_head_in_frozen_matrix": head_present,
        "actual_second_in_global_p2_matrix": p2_present,
        "actual_third_in_global_p3_matrix": p3_present,
        "actual_head_local_p2": {
            "status": pair_status,
            "reason": (actual_pair or {}).get("reason"),
            "terminalized": pair_terminal,
            "purchased_declared": pair_status == "PURCHASE",
        },
        "actual_pair_conditioned_third": {
            "status": third_status,
            "reason": (actual_third or {}).get("reason"),
            "terminalized": third_terminal,
            "purchased_declared": third_status == "PURCHASE",
        },
        "conversion_first_lost_link_observation": first_loss,
        "population_terminalization": {
            "head_local_p2_cells": all_pair_cells,
            "head_local_p2_unterminalized": len(frozen.get("head_local_p2_unterminalized") or []),
            "pair_conditioned_third_cells": all_third_cells,
            "purchased_pair_third_unterminalized": len(
                frozen.get("purchased_pair_third_unterminalized") or []),
        },
        "cross_ticket_observation": {
            "actual_exact_has_missing_same_set_trio": actual in [
                list(x) for x in absent_trios
            ],
            "actual_exact_has_missing_same_head_exacta": actual in [
                list(x) for x in absent_exactas
            ],
            "note": "Cross-bet type absence alone is not a ticket construction failure.",
        },
        "observed_capital_exposure": {
            "total_frozen_yen": exposure.get("total_yen"),
            "winner_head_yen": head_exposure.get(str(w), head_exposure.get(w, 0)),
            "actual_top3_horse_exposure": [
                {
                    "runner_id": rid,
                    "stake_yen": (horse_exposure.get(rid) or {}).get("stake_yen", 0),
                    "portfolio_share_pct": (horse_exposure.get(rid) or {}).get(
                        "share_of_portfolio_pct"),
                }
                for rid in actual
            ],
            "unpriced_world_concentration": "NOT CALCULATED",
            "exposure_is_not_probability": True,
        },
        "oos_eligibility_change": False,
        "counterfactual_pfs": None,
        "automatic_purchase": False,
        "purchase_authority": False,
        "production_effect": "NONE",
        "automatic_promotion": False,
        "note": (
            "Outcome attribution to immutable pre-result decisions, not causal "
            "proof of predictive improvement or permission to purchase missing links."
        ),
    }
    out["sha256"] = _sha(out)
    return out
