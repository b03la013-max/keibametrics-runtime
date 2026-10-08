"""AKI-aware selective purchase RESEARCH SHADOW, never a Production selector.

Keep all frozen Semantic-MEC units for prediction diagnostics. Construct a
separate, finite, auditable, 100-yen PAPER portfolio from existing R3 tickets.
AKI numbers are UNCALIBRATED: they control pilot *width*, NOT probabilities,
expected value, live bets, KRS, or Production capital.
"""
from __future__ import annotations
import copy
import datetime as dt
import hashlib
import json
import math
from collections import Counter
from typing import Any, Mapping

from formal_oos_policy import request_oos_policy
from capital_policy import load_family_default_capital_policy
from mec_r4_shadow import settle_ticket_list

PROFILE = "KM-FAMILY-AKI-ADAPTIVE-PURCHASE-SHADOW-20261009-R1"
CANDIDATE = "AKI-ADAPTIVE-SELECTIVE-PAPER-v0.1"
ACTIVATION_AT = "2026-10-09T00:00:00+09:00"
# Experimental, not calibrated/Production thresholds. Freeze before OOS.
THRESHOLDS = {"w_stable_max": 40.0, "w_contested_min": 60.0,
              "axis_low_max": 45.0, "axis_high_min": 60.0,
              "asi_stable_min": 60.0, "asi_fragile_max": 40.0,
              "rsi_uncertain_min": 65.0}
# Existing local v4.12 core ticket-type width guidance; exacta is a
# conservative shadow cap, not an existing official numeric policy.
TYPE_CAPS = {"STABLE": {"TRIO": 5, "TRIFECTA": 6, "EXACTA": 3},
             "SELECTIVE": {"TRIO": 8, "TRIFECTA": 18, "EXACTA": 5},
             "VOLATILE": {"TRIO": 10, "TRIFECTA": 24, "EXACTA": 6}}
# Pilot exposure caps are uncalibrated shadow-only design hypotheses.
EXPOSURE_YEN = {"STABLE": 2000, "SELECTIVE": 1500, "VOLATILE": 1000}
INDEXES = ("W-AKI", "P2-AKI", "P3-AKI", "ASI", "RSI")
BET_TYPES = ("EXACTA", "TRIO", "TRIFECTA")


class AdaptivePurchaseError(ValueError):
    pass


def _sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _when(value: Any) -> dt.datetime:
    try:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("naive timestamp")
        return parsed.astimezone(dt.timezone.utc)
    except (ValueError, TypeError) as exc:
        raise AdaptivePurchaseError("INVALID_TIME") from exc


def _provenance(req: Mapping[str, Any], ids: set[int]) -> dict[int, dict[str, float]]:
    ledger = req.get("index_provenance_ledger") or {}
    if not isinstance(ledger, Mapping) or ledger.get("race_id") != req.get("race_id"):
        raise AdaptivePurchaseError("AKI_PROVENANCE_RACE_MISMATCH")
    digest = ledger.get("sha256")
    if not digest or digest != req.get("index_provenance_hash") or digest != _sha({k: v for k, v in ledger.items() if k != "sha256"}):
        raise AdaptivePurchaseError("AKI_PROVENANCE_DIGEST_INVALID")
    rows = ledger.get("rows") or []
    seen: dict[int, dict[str, float]] = {rid: {} for rid in ids}
    for row in rows:
        if not isinstance(row, Mapping) or row.get("index") not in INDEXES:
            continue
        try:
            rid = int(row["runner_id"])
        except (ValueError, TypeError, KeyError) as exc:
            raise AdaptivePurchaseError("AKI_RUNNER_INVALID") from exc
        if rid not in ids:
            continue
        name = row["index"]
        if name in seen[rid]:
            raise AdaptivePurchaseError("AKI_DUPLICATE_INDEX")
        if row.get("terminal_status") != "CALCULATED" or row.get("production_authority") is not True:
            raise AdaptivePurchaseError("AKI_NOT_CALCULATED_PROVENANCE")
        try:
            value = float(row["value"])
        except (ValueError, KeyError, TypeError) as exc:
            raise AdaptivePurchaseError("AKI_VALUE_MISSING") from exc
        if not math.isfinite(value) or not 0 <= value <= 100:
            raise AdaptivePurchaseError("AKI_OUT_OF_RANGE")
        seen[rid][name] = value
    for rid in ids:
        if len(seen[rid]) != len(INDEXES):
            raise AdaptivePurchaseError(f"AKI_MISSING_REQUIRED_INDEX:{rid}")
    return seen


def _ticket_key(t: Mapping[str, Any]) -> tuple[str, tuple[int, ...]]:
    bt = str(t.get("bet_type") or "").upper()
    if bt not in BET_TYPES:
        raise AdaptivePurchaseError("UNSUPPORTED_BET_TYPE")
    try:
        sel = tuple(int(x) for x in t["selection"])
        amount = int(t.get("stake"))
    except (ValueError, TypeError, KeyError) as exc:
        raise AdaptivePurchaseError("INVALID_FROZEN_TICKET") from exc
    if len(sel) != (2 if bt == "EXACTA" else 3) or len(set(sel)) != len(sel):
        raise AdaptivePurchaseError("INVALID_FROZEN_SELECTION")
    if amount < 100 or amount % 100:
        raise AdaptivePurchaseError("INVALID_FROZEN_STAKE")
    return (bt, tuple(sorted(sel)) if bt == "TRIO" else sel)


def _selected_roles(req: Mapping[str, Any], art: Mapping[str, Any]):
    frozen = art.get("final_prediction_package") or {}
    static = req.get("static_prediction") or {}
    ranking = frozen.get("ranking") or static.get("ranking") or []
    roles = frozen.get("roles") or static.get("roles") or {}
    try:
        order = [int(x) for x in ranking]
        role_map = {int(k): set(str(x).upper() for x in v) for k, v in roles.items()}
    except (ValueError, TypeError) as exc:
        raise AdaptivePurchaseError("ROLES_RANKING_INVALID") from exc
    if not order or len(order) != len(set(order)) or set(role_map) - set(order):
        raise AdaptivePurchaseError("RANKING_DUPLICATE_OR_MISSING_ROLE")
    return order, role_map


def _axis(m: Mapping[int, dict[str, float]], ids: list[int], index: str) -> float:
    # Fixed rank-ordered first-two average. Thresholds are research hypotheses.
    head = ids[:2]
    if not head:
        raise AdaptivePurchaseError("AKI_NO_ROLE_UNIVERSE")
    return round(sum(m[i][index] for i in head) / len(head), 6)


def _budget(req: Mapping[str, Any], regime: str) -> tuple[int, str]:
    # RECOMMENDATION_ONLY may not disable a PAPER research safety ceiling.
    default = load_family_default_capital_policy()
    ceiling = int(default.get("max_race_capital") or 0)
    if ceiling < 0 or ceiling % 100:
        raise AdaptivePurchaseError("INVALID_DEFAULT_BUDGET")
    policy = req.get("capital_policy") or {}
    if policy.get("mode") == "HARD_RACE_BUDGET":
        cap = policy.get("max_race_capital")
        if not isinstance(cap, int) or cap < 0 or cap % 100:
            raise AdaptivePurchaseError("INVALID_REQUEST_BUDGET")
        ceiling = min(ceiling, cap)
        source = "MIN_USER_AND_FAMILY_SHADOW_CEILING"
    elif policy.get("mode") in ("RECOMMENDATION_ONLY", None):
        source = "FAMILY_CEILING_EVEN_IF_PRODUCTION_RECOMMENDATION_ONLY"
    else:
        raise AdaptivePurchaseError("UNKNOWN_CAPITAL_MODE")
    return min(ceiling, EXPOSURE_YEN[regime]), source


def build_shadow(req: dict, final_artifact: dict, *, generated_at: str,
                 basis_sha256: str) -> dict[str, Any]:
    """Construct exactly one frozen, result-blind shadow portfolio."""
    art = final_artifact.get("artifact") or final_artifact
    final_ticket = art.get("final_ticket") or {}
    production_tickets = final_ticket.get("tickets") or []
    order, roles = _selected_roles(req, art)
    rank = {rid: i for i, rid in enumerate(order)}
    if not basis_sha256 or not req.get("race_id"):
        raise AdaptivePurchaseError("BASIS_OR_RACE_ID_MISSING")
    post = _when(req.get("scheduled_post_at"))
    generated = _when(generated_at)
    activation = _when(ACTIVATION_AT)
    if generated >= post or str(req.get("temporal_mode")).upper() != "FORMAL-PRE-RACE":
        raise AdaptivePurchaseError("NOT_FROZEN_BEFORE_START")
    if generated < activation:
        raise AdaptivePurchaseError("PRE_ACTIVATION_NOT_OOS")
    if req.get("post_result_after_final") is not None:
        raise AdaptivePurchaseError("RESULT_BEARING_INPUT_FORBIDDEN")

    model = _provenance(req, set(order))
    by_role = {role: [i for i in order if role in roles.get(i, ())] for role in ("W", "P2", "P3")}
    if any(not v for v in by_role.values()):
        raise AdaptivePurchaseError("MISSING_ROLE_COLUMN")
    axes = {
        "W-AKI": _axis(model, by_role["W"], "W-AKI"),
        "P2-AKI": _axis(model, by_role["P2"], "P2-AKI"),
        "P3-AKI": _axis(model, by_role["P3"], "P3-AKI"),
        "ASI": _axis(model, by_role["W"], "ASI"),
        "RSI": _axis(model, by_role["W"], "RSI"),
    }
    t = THRESHOLDS
    stable = axes["W-AKI"] < t["w_stable_max"] and axes["ASI"] >= t["asi_stable_min"]
    volatile = axes["W-AKI"] >= t["w_contested_min"] or axes["ASI"] <= t["asi_fragile_max"]
    regime = "STABLE" if stable else ("VOLATILE" if volatile else "SELECTIVE")
    fragile = regime == "VOLATILE" and axes["ASI"] <= t["asi_fragile_max"] and axes["RSI"] >= t["rsi_uncertain_min"]
    head_size = 1 if stable else (3 if volatile else 2)
    p2_size = 2 if axes["P2-AKI"] < t["axis_low_max"] else (4 if axes["P2-AKI"] >= t["axis_high_min"] else 3)
    p3_size = 2 if axes["P3-AKI"] < t["axis_low_max"] else (5 if axes["P3-AKI"] >= t["axis_high_min"] else 3)
    heads = by_role["W"][:head_size]
    seconds = by_role["P2"][:p2_size]
    thirds = by_role["P3"][:p3_size]
    caps = TYPE_CAPS[regime]
    budget, budget_source = _budget(req, regime)

    # Never silently invent a ticket: consider ONLY frozen Production tickets.
    distinct: dict[tuple[str, tuple[int, ...]], dict] = {}
    for old in production_tickets:
        key = _ticket_key(old)
        if any(x not in rank for x in key[1]):
            raise AdaptivePurchaseError("FROZEN_TICKET_UNKNOWN_RUNNER")
        if key in distinct:
            raise AdaptivePurchaseError("DUPLICATE_FROZEN_TICKET")
        distinct[key] = old

    eligible = []
    discard = Counter()
    for key, original in distinct.items():
        bt, sel = key
        if bt == "EXACTA":
            allowed = sel[0] in heads and sel[1] in seconds
        elif bt == "TRIFECTA":
            allowed = sel[0] in heads and sel[1] in seconds and sel[2] in thirds
        else:
            allowed = any(a in heads and b in seconds and c in thirds
                          and len({a, b, c}) == 3
                          for a in sel for b in sel for c in sel)
        if not allowed:
            discard["NON_MATERIAL_COLUMN_FOR_THIS_REGIME"] += 1
            continue
        tier = str(original.get("mec_tier") or "TAIL").upper()
        tier_score = {"CORE": 0, "PROTECTION": 7, "TAIL": 13}.get(tier, 20)
        # Prefer smaller ranks and core independent evidence. No post-result data.
        score = (tier_score, sum(rank[x] for x in sel), max(rank[x] for x in sel),
                 {"TRIO": 0, "EXACTA": 1, "TRIFECTA": 2}[bt], sel)
        eligible.append((score, key, original))
    eligible.sort(key=lambda x: x[0])

    chosen = []
    chosen_keys = set()
    type_counts = Counter()
    remaining = budget
    for score, key, original in eligible:
        bt, sel = key
        if fragile:
            discard["FRAGILE_VOLATILE_ABSTENTION"] += 1
            continue
        if type_counts[bt] >= caps[bt]:
            discard["BET_TYPE_WIDTH_CAP"] += 1
            continue
        if remaining < 100:
            discard["EXPOSURE_BUDGET_EXHAUSTED"] += 1
            continue
        if key in chosen_keys:
            raise AdaptivePurchaseError("INTERNAL_DUPLICATE")
        # 100-yen exposure per proposed ticket; no Kelly/EV, no stake expansion.
        chosen.append({"bet_type": bt, "selection": list(sel), "stake": 100,
                       "origin": "FROZEN_R3_TICKET_ONLY",
                       "mec_tier": original.get("mec_tier"),
                       "coverage_ids": copy.deepcopy(original.get("coverage_ids") or [])})
        chosen_keys.add(key)
        type_counts[bt] += 1
        remaining -= 100

    selected_units = set(x for tkt in chosen for x in tkt["coverage_ids"])
    semantic_units = {str(x["id"]) for x in (art.get("minimum_efficient_coverage") or {}).get("coverage_units") or []}
    if selected_units - semantic_units:
        raise AdaptivePurchaseError("ADAPTIVE_SELECTED_UNKNOWN_MATERIAL_UNIT")
    request_policy = request_oos_policy(req)
    acceptance_only = bool(request_policy["acceptance_only"])
    forward = bool(request_policy["oos_allowed"] and not acceptance_only)
    not_buy = "NO_BET" if not chosen else "PAPER"
    out = {
        "profile": PROFILE, "candidate_id": CANDIDATE,
        "status": "SHADOW / NON-PRODUCTION / NO-BET-AUTHORITY / UNCALIBRATED_AKI",
        "race_id": req["race_id"], "generated_at": generated_at,
        "scheduled_post_at": req["scheduled_post_at"], "source_basis_sha256": basis_sha256,
        "index_provenance_sha256": req["index_provenance_hash"],
        "design_activation_at": ACTIVATION_AT, "temporal_mode": req.get("temporal_mode"),
        "temporal_class": ("ACCEPTANCE-ONLY / NOT-OOS" if acceptance_only else
                           "FORWARD-CANDIDATE / PENDING-SIGNED-FINAL" if forward else "NOT-OOS"),
        "acceptance_only": acceptance_only, "forward_oos_candidate": forward,
        "oos_exclusion_reason": request_policy.get("oos_exclusion_reason"),
        "regime": regime, "experimental_thresholds": copy.deepcopy(THRESHOLDS),
        "aki_axes": axes, "width": {"head": len(heads), "p2": len(seconds), "p3": len(thirds)},
        "selected_role_columns": {"W": heads, "P2": seconds, "P3": thirds},
        "fragile_market": fragile, "type_caps": copy.deepcopy(caps),
        "capital_ceiling_yen": budget, "capital_basis": budget_source,
        "production_ticket_count": len(production_tickets),
        "candidate_action": not_buy, "candidate_tickets": chosen,
        "candidate_ticket_count": len(chosen), "candidate_capital_yen": 100 * len(chosen),
        "unspent_ceiling_yen": budget - 100 * len(chosen),
        "selected_ticket_count_by_type": dict(type_counts),
        "discard_reasons": dict(discard),
        "semantic_unit_count": len(semantic_units),
        "selected_material_unit_count": len(selected_units),
        "selected_material_coverage_ratio": (round(len(selected_units) / len(semantic_units), 6) if semantic_units else None),
        "unselected_semantic_unit_count": len(semantic_units - selected_units),
        "market_price_validation": "NOT_VALIDATED / NO_CALIBRATED_PROBABILITIES",
        "expected_value": None, "kelly": None,
        "actual_purchase": False, "automatic_promotion": False,
        "result_informed_selection": False, "production_effect": "NONE",
        "immutable_production_mec": (art.get("minimum_efficient_coverage") or {}).get("sha256"),
        "baseline_production_ticket_hash": _sha(production_tickets),
    }
    out["sha256"] = _sha(out)
    return out


def bind_to_trace(trace: dict, shadow: dict) -> dict:
    out = copy.deepcopy(trace or {})
    out["aki_adaptive_purchase_shadow_binding"] = {
        "profile": PROFILE, "candidate_id": CANDIDATE,
        "shadow_sha256": shadow["sha256"],
        "source_basis_sha256": shadow["source_basis_sha256"],
        "index_provenance_sha256": shadow["index_provenance_sha256"],
        "generated_at": shadow["generated_at"],
        "scheduled_post_at": shadow["scheduled_post_at"],
        "forward_oos_candidate": shadow["forward_oos_candidate"],
        "acceptance_only": shadow["acceptance_only"],
        "production_effect": "NONE",
    }
    return out


def verify_signed_final_binding(final_envelope: dict, shadow: dict) -> dict:
    if _sha({k: v for k, v in shadow.items() if k != "sha256"}) != shadow.get("sha256"):
        raise AdaptivePurchaseError("SHADOW_CONTENT_HASH_MISMATCH")
    receipt = final_envelope.get("receipt") or {}
    art = final_envelope.get("artifact") or {}
    if receipt.get("phase") != "FINAL" or receipt.get("status") != "PASS":
        raise AdaptivePurchaseError("SIGNED_FINAL_MISSING")
    if receipt.get("race_id") != shadow.get("race_id"):
        raise AdaptivePurchaseError("SIGNED_FINAL_RACE_MISMATCH")
    binding = (art.get("ticket_transport_trace") or {}).get("aki_adaptive_purchase_shadow_binding") or {}
    expected = bind_to_trace({}, shadow)["aki_adaptive_purchase_shadow_binding"]
    if binding != expected or binding.get("production_effect") != "NONE":
        raise AdaptivePurchaseError("SHADOW_FINAL_BINDING_MISMATCH")
    if not _when(shadow["generated_at"]) < _when(receipt.get("timestamp")) < _when(shadow["scheduled_post_at"]):
        raise AdaptivePurchaseError("SHADOW_FINAL_TEMPORAL_INVALID")
    return {
        "valid": True, "profile": PROFILE, "candidate_id": CANDIDATE,
        "shadow_sha256": shadow["sha256"], "basis_sha256": shadow["source_basis_sha256"],
        "final_receipt_sha256": final_envelope.get("receipt_sha256"),
        "final_artifact_sha256": receipt.get("artifact_sha256"),
        "forward_oos_candidate": shadow["forward_oos_candidate"],
        "acceptance_only": shadow["acceptance_only"], "production_effect": "NONE",
    }


def settle_shadow(shadow: dict, official_result: dict, *, signed_final_verified: bool,
                  signed_result_verified: bool, official_result_verified: bool) -> dict:
    if _sha({k: v for k, v in shadow.items() if k != "sha256"}) != shadow.get("sha256"):
        raise AdaptivePurchaseError("SHADOW_CONTENT_HASH_MISMATCH")
    if not all((signed_final_verified, signed_result_verified, official_result_verified)):
        raise AdaptivePurchaseError("RESULT_AUTHORITY_NOT_VERIFIED")
    if (official_result.get("refund_runner_ids") or [] or
            len(official_result.get("winning_selections") or []) > 1):
        raise AdaptivePurchaseError("SPECIAL_SETTLEMENT_REQUIRES_AUTHORIZED_REPLAY")
    if shadow.get("candidate_action") == "NO_BET":
        settlement = {"status": "SETTLED_ABSTENTION", "investment": 0, "return": 0,
                      "profit_loss": 0, "pfs": None, "ticket_count": 0,
                      "hit_types": [], "unresolved_payout_types": []}
    else:
        settlement = settle_ticket_list(
            shadow["candidate_tickets"], {"official_result": {
                "top3": official_result.get("finish_order"),
                "payouts": official_result.get("payouts") or {},
            }}
        )
        if settlement["status"] != "SETTLED":
            raise AdaptivePurchaseError("SHADOW_PAYOUT_UNRESOLVED")
    out = {
        "profile": PROFILE, "candidate_id": CANDIDATE, "race_id": shadow["race_id"],
        "source_shadow_sha256": shadow["sha256"],
        "status": ("FORWARD-OOS-SETTLEMENT / SIGNED-FINAL-RESULT-BOUND"
                   if shadow["forward_oos_candidate"] and not shadow["acceptance_only"]
                   else "ACCEPTANCE-OR-REPLAY / NOT-OOS"),
        "oos_eligible": bool(shadow["forward_oos_candidate"] and not shadow["acceptance_only"]),
        "candidate_action": shadow["candidate_action"], "settlement": settlement,
        "actual_purchase": False, "production_effect": "NONE",
    }
    out["sha256"] = _sha(out)
    return out
