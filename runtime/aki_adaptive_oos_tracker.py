"""Read-only canonical OOS settlement for pre-FINAL AKI purchase paper shadow.

Requires verified FINAL, RESULT and official-result checkpoint. This records no
actual purchase, does not grant Production authority, and never alters R5 cohorts.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

from aki_adaptive_purchase_shadow import (
    AdaptivePurchaseError, PROFILE as AKI_PROFILE, _sha, _when,
    settle_shadow, verify_signed_final_binding, ACTIVATION_AT,
)
from mec_r4_shadow import settle_ticket_list

PROFILE = "KM-FAMILY-AKI-ADAPTIVE-OOS-MEASUREMENT-20261009-R1"


def _read(path: Path) -> dict:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise AdaptivePurchaseError(f"CHECKPOINT_UNREADABLE:{path}") from exc
    if not isinstance(obj, dict):
        raise AdaptivePurchaseError("CHECKPOINT_NOT_OBJECT")
    return obj


def _envelope(envelope: dict, phase: str, race: str):
    rec = envelope.get("receipt") or {}
    if rec.get("phase") != phase or rec.get("status") != "PASS" or rec.get("race_id") != race:
        raise AdaptivePurchaseError(f"{phase}_RECEIPT_INVALID")
    if _sha(envelope.get("artifact")) != rec.get("artifact_sha256"):
        raise AdaptivePurchaseError(f"{phase}_ARTIFACT_HASH_INVALID")
    if _sha(rec) != envelope.get("receipt_sha256"):
        raise AdaptivePurchaseError(f"{phase}_RECEIPT_HASH_INVALID")


def _verify_production_signed_settlement(signed: dict, recalculated: dict) -> None:
    """Match the actual Signed RESULT settlement schema; never silently default to -1.

    Production RESULT uses 'investment' and 'return', not the OOS-trackers'
    historical 'total_investment' / 'total_payout' aliases.
    """
    if (signed.get("status") != "COMPLETE"
            or signed.get("pfs_authority") != "FROZEN-RECOMMENDATION"
            or not all(k in signed for k in ("investment", "return"))):
        raise AdaptivePurchaseError("PRODUCTION_SIGNED_SETTLEMENT_SCHEMA_INVALID")
    try:
        investment = float(signed["investment"])
        payout = float(signed["return"])
    except (TypeError, ValueError) as exc:
        raise AdaptivePurchaseError("PRODUCTION_SIGNED_SETTLEMENT_SCHEMA_INVALID") from exc
    if (abs(investment - recalculated["investment"]) > 0.001
            or abs(payout - recalculated["return"]) > 0.001):
        raise AdaptivePurchaseError("PRODUCTION_SIGNED_SETTLEMENT_CONFLICT")


def evaluate_canonical(
    shadow: dict, attestation: dict, final: dict, result: dict,
    official_request: dict, formal_verifications: dict, result_verifications: dict,
) -> dict[str, Any]:
    race = str(shadow.get("race_id") or "")
    if not race or shadow.get("profile") != AKI_PROFILE:
        raise AdaptivePurchaseError("ADAPTIVE_PROFILE_OR_RACE_MISMATCH")
    if not (formal_verifications.get("FINAL") is True
            and result_verifications.get("FINAL") is True
            and result_verifications.get("RESULT") is True):
        raise AdaptivePurchaseError("EXTERNAL_RECEIPT_VERIFICATION_MISSING")
    _envelope(final, "FINAL", race)
    _envelope(result, "RESULT", race)
    bound = verify_signed_final_binding(final, shadow)
    if not all(attestation.get(k) == v for k, v in bound.items()):
        raise AdaptivePurchaseError("ADAPTIVE_FINAL_ATTESTATION_MISMATCH")
    ra = result["artifact"]
    if (ra.get("frozen_refs") or {}).get("final_receipt_sha256") != final.get("receipt_sha256"):
        raise AdaptivePurchaseError("RESULT_NOT_BOUND_TO_SAME_FINAL")
    if (official_request.get("official_result_verified") is not True
            or official_request.get("acceptance_only") is True
            or not official_request.get("official_result_verification_ref")
            or official_request.get("race_id") != race):
        raise AdaptivePurchaseError("OFFICIAL_RESULT_AUTHORITY_MISSING")
    official = ra.get("official_result") or {}
    if any(official_request.get(k) != official.get(k) for k in ("finish_order", "payouts")):
        raise AdaptivePurchaseError("OFFICIAL_RESULT_MISMATCH")
    if (official_request.get("refund_runner_ids") or official.get("refund_runner_ids")
            or len(official_request.get("winning_selections") or []) > 1):
        raise AdaptivePurchaseError("SPECIAL_OFFICIAL_OUTCOME_NEEDS_SETTLEMENT_SUPPORT")
    observed_at = _when(ra.get("result_available_at"))
    if not (_when(shadow["generated_at"]) <= _when(final["receipt"]["timestamp"])
            < _when(shadow["scheduled_post_at"]) <= observed_at):
        raise AdaptivePurchaseError("OOS_TEMPORAL_ORDER_INVALID")
    if _when(shadow["generated_at"]) < _when(ACTIVATION_AT):
        raise AdaptivePurchaseError("RESULT_BEFORE_DESIGN_ACTIVATION")

    production_tickets = (final["artifact"].get("final_ticket") or {}).get("tickets") or []
    if _sha(production_tickets) != shadow.get("baseline_production_ticket_hash"):
        raise AdaptivePurchaseError("PRODUCTION_TICKETS_CHANGED_AFTER_FREEZE")
    settled_production = settle_ticket_list(
        production_tickets, {"official_result": {
            "top3": official["finish_order"][:3], "payouts": official["payouts"],
        }}
    )
    if settled_production.get("status") != "SETTLED":
        raise AdaptivePurchaseError("PRODUCTION_PAYOUT_UNRESOLVED")
    _verify_production_signed_settlement(ra.get("settlement") or {}, settled_production)

    measured = settle_shadow(
        shadow, official,
        signed_final_verified=True, signed_result_verified=True,
        official_result_verified=True,
    )
    if shadow["forward_oos_candidate"] and not measured["oos_eligible"]:
        raise AdaptivePurchaseError("FORWARD_CLASSIFICATION_CONFLICT")
    p = settled_production
    c = measured["settlement"]
    return {
        "race_id": race, "race_day": str(_when(shadow["scheduled_post_at"]).astimezone(dt.timezone(dt.timedelta(hours=9))).date()),
        "profile": PROFILE, "shadow_sha256": shadow["sha256"],
        "final_receipt_sha256": final["receipt_sha256"],
        "result_receipt_sha256": result["receipt_sha256"],
        "official_result_verification_ref": official_request["official_result_verification_ref"],
        "oos_eligible": measured["oos_eligible"],
        "candidate_action": shadow["candidate_action"],
        "regime": shadow["regime"], "aki_axes": shadow["aki_axes"],
        "production": {"investment": p["investment"], "return": p["return"],
                       "profit_loss": p["profit_loss"], "pfs": p["pfs"],
                       "ticket_count": p["ticket_count"]},
        "adaptive": {"investment": c["investment"], "return": c["return"],
                     "profit_loss": c["profit_loss"], "pfs": c["pfs"],
                     "ticket_count": c["ticket_count"]},
        "paper_only": True, "actual_purchase": False, "production_effect": "NONE",
    }


def scan_execution_store(root: Path) -> dict:
    from execution_store import resolve_phase
    if not root.exists():
        return _summary([], [], [])
    rows, held, errors = [], [], []
    for execution in sorted(root.iterdir()):
        if not execution.is_dir():
            continue
        try:
            formal = resolve_phase(execution.name, "FORMAL", root=root)
            if not formal:
                continue
            d = formal["run_dir"]
            shadow_file = d / "aki_adaptive_purchase_shadow_pre_result.json"
            error_file = d / "aki_adaptive_purchase_shadow_error.json"
            if not shadow_file.exists():
                if error_file.exists():
                    held.append({"execution_id": execution.name, "reason": "SHADOW_HOLD",
                                 "details": _read(error_file).get("error")})
                continue  # Earlier executions are not rewritten or credited.
            shadow = _read(shadow_file)
            if shadow.get("forward_oos_candidate") is not True:
                held.append({"race_id": shadow.get("race_id"), "reason": "NOT_FORWARD_OOS"})
                continue
            phase_result = resolve_phase(execution.name, "RESULT", root=root)
            if not phase_result:
                held.append({"race_id": shadow.get("race_id"), "reason": "WAITING_SIGNED_RESULT"})
                continue
            official_phase = resolve_phase(execution.name, "OFFICIAL_RESULT", root=root)
            if not official_phase:
                held.append({"race_id": shadow.get("race_id"), "reason": "WAITING_OFFICIAL_RESULT"})
                continue
            row = evaluate_canonical(
                shadow,
                _read(d / "aki_adaptive_purchase_binding_attestation.json"),
                _read(d / "final_receipt_envelope.json"),
                _read(phase_result["run_dir"] / "result_receipt_envelope.json"),
                _read(official_phase["run_dir"] / "official_result_request.json"),
                _read(d / "receipt_verifications.json"),
                _read(phase_result["run_dir"] / "receipt_verifications.json"),
            )
            rows.append(row)
        except (AdaptivePurchaseError, AssertionError, KeyError, ValueError) as exc:
            errors.append({"execution_id": execution.name, "reason": type(exc).__name__ + ":" + str(exc)})
    race_ids = [x["race_id"] for x in rows]
    if len(race_ids) != len(set(race_ids)):
        errors.append({"reason": "DUPLICATE_OOS_RACE_ID"})
    return _summary(rows, held, errors)


def _summary(rows: list[dict], held: list[dict], errors: list[dict]) -> dict:
    valid = rows if not errors else []
    distinct_days = len(set(x["race_day"] for x in valid))
    def total(which: str):
        inv = sum(float(x[which]["investment"]) for x in valid)
        ret = sum(float(x[which]["return"]) for x in valid)
        return {
            "investment": round(inv, 2), "return": round(ret, 2),
            "profit_loss": round(ret - inv, 2),
            "pfs": round(ret / inv * 100, 9) if inv else None,
            "ticket_count": sum(int(x[which]["ticket_count"]) for x in valid),
            "hit_but_loss": sum(0 < x[which]["return"] < x[which]["investment"] for x in valid),
        }
    no_bet = [x for x in valid if x["candidate_action"] == "NO_BET"]
    report = {
        "profile": PROFILE,
        "status": ("INTEGRITY_HOLD" if errors else
                   "WAITING_FORWARD_OOS" if (len(valid) < 30 or distinct_days < 3) else "HUMAN_REVIEW_REQUIRED"),
        "eligible_races": len(valid), "days": distinct_days,
        "minimum_review_races": 30, "minimum_review_days": 3,
        "production": total("production"), "adaptive": total("adaptive"),
        "abstention_races": len(no_bet),
        "avoided_production_losses_on_abstentions_hindsight": round(
            sum(max(0, -x["production"]["profit_loss"]) for x in no_bet), 2),
        "missed_production_gains_on_abstentions_hindsight": round(
            sum(max(0, x["production"]["profit_loss"]) for x in no_bet), 2),
        "equal_budget_comparison": "NOT_PERFORMED / ABSTENTION_AND_RESELECTION_ARE_NOT_LINEAR_EXPOSURE",
        "settled_rows": valid, "held": held, "errors": errors,
        "actual_purchase_pfs": None,
        "automatic_promotion": False, "production_change_authorized": False,
        "new_index_or_numeric_policy_change": False,
        "candidate_design_status": "NON-PRODUCTION / FIXED-FORWARD / NO_RESULT_FITTING",
        "existing_r5_cohort_modified": False,
    }
    report["sha256"] = _sha(report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="runtime/executions")
    parser.add_argument("--output", default="runtime/aki_adaptive_oos_status.json")
    args = parser.parse_args()
    report = scan_execution_store(Path(args.root))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "eligible_races", "days", "held", "errors")}, ensure_ascii=False))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
