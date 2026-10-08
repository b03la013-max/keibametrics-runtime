"""Read-only Family PFS scorecard from frozen RESULT regression manifests.

Does not execute prediction, reconstruct a ticket, add OOS credit, approve
purchases or alter policy. Unresolved evidence fails closed, never as a loss.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

if __package__:
    from .family_pfs_owner_scorecard import build_owner_scorecard
    from .family_pfs_improvement import build_pfs_improvement_assessment
else:
    from family_pfs_owner_scorecard import build_owner_scorecard
    from family_pfs_improvement import build_pfs_improvement_assessment

PROFILE = "KM-FAMILY-PFS-REGRESSION-READOUT-20261008-R1"


class RegressionEvidenceError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RegressionEvidenceError(f"EVIDENCE_NOT_READABLE:{path}") from exc
    if not isinstance(obj, dict):
        raise RegressionEvidenceError(f"EVIDENCE_NOT_OBJECT:{path}")
    return obj


def _git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw).hexdigest()


def _get_existing_file(root: Path, path: str) -> Path:
    try:
        relative = Path(path)
        absolute = (root / relative).resolve()
        absolute.relative_to(root.resolve())
        if absolute.suffix != ".json" or not relative.parts or relative.parts[0] != "runtime":
            raise ValueError("INVALID_EVIDENCE_PATH")
        if "RESULT" not in relative.parts or "result_summary.json" != relative.name:
            raise ValueError("NOT_FROZEN_RESULT_SUMMARY")
        return absolute
    except (ValueError, TypeError) as exc:
        raise RegressionEvidenceError(f"EVIDENCE_PATH_REJECTED:{path}") from exc


def build_regression_readout(root: Path, manifest_path: Path) -> dict[str, Any]:
    """Fail-closed *historical* evaluation of a pre-existing frozen result set."""
    root = root.resolve()
    manifest = _load(manifest_path)
    if "REGRESSION-EVIDENCE" not in str(manifest.get("status")):
        raise RegressionEvidenceError("NOT_REGRESSION_EVIDENCE")
    if "NOT-NEW-OOS-CREDIT" not in str(manifest.get("status")):
        raise RegressionEvidenceError("OOS_CREDIT_BOUNDARY_MISSING")
    cohort = manifest.get("verified_result_records")
    if not isinstance(cohort, list) or not cohort:
        raise RegressionEvidenceError("EMPTY_COHORT")

    reviews = []
    rows = []
    seen = set()
    for item in cohort:
        race_id = str(item.get("race_id") or "")
        if not race_id or race_id in seen:
            raise RegressionEvidenceError(f"DUPLICATE_OR_MISSING_RACE:{race_id}")
        seen.add(race_id)

        src_path = _get_existing_file(root, str(item.get("result_summary_path") or ""))
        raw = src_path.read_bytes()
        pinned = str(item.get("result_summary_git_blob_sha") or "")
        if len(pinned) != 40 or _git_blob_sha(raw) != pinned:
            raise RegressionEvidenceError(f"FROZEN_RESULT_BLOB_CHANGED:{race_id}")
        summary = _load(src_path)
        review = summary.get("automatic_post_result_review") or {}
        cap = review.get("capital") or {}
        conversion = review.get("conversion") or {}
        failure = (review.get("failure_localization") or {}).get("first_material_failure")

        if summary.get("verified") is not True or not summary.get("result_receipt"):
            raise RegressionEvidenceError(f"RESULT_VERIFIED_STATUS_MISSING:{race_id}")
        if review.get("race_id") != race_id or summary.get("race_id") != race_id:
            raise RegressionEvidenceError(f"RESULT_IDENTITY_MISMATCH:{race_id}")
        if not review.get("final_receipt_sha256") or not review.get("sha256"):
            raise RegressionEvidenceError(f"FINAL_REVIEW_BINDING_MISSING:{race_id}")
        if cap.get("settlement_status") != "COMPLETE":
            raise RegressionEvidenceError(f"INCOMPLETE_SETTLEMENT:{race_id}")
        if not all(isinstance(summary.get(k), int) for k in ("investment", "return")):
            raise RegressionEvidenceError(f"AMOUNT_NOT_INTEGER:{race_id}")
        investment, payout = summary["investment"], summary["return"]
        if investment < 0 or payout < 0:
            raise RegressionEvidenceError(f"NEGATIVE_AMOUNT:{race_id}")
        if investment != item.get("investment_yen") or payout != item.get("return_yen"):
            raise RegressionEvidenceError(f"MANIFEST_AMOUNT_CONFLICT:{race_id}")
        if cap.get("investment") != investment or cap.get("return") != payout:
            raise RegressionEvidenceError(f"SIGNED_REVIEW_AMOUNT_CONFLICT:{race_id}")
        if failure != item.get("first_material_failure"):
            raise RegressionEvidenceError(f"FIRST_FAILURE_MISMATCH:{race_id}")

        by_type = summary.get("by_type") or {}
        if not isinstance(by_type, dict):
            raise RegressionEvidenceError(f"BET_TYPES_INVALID:{race_id}")
        if sum(int(x["investment"]) for x in by_type.values()) != investment or sum(int(x["return"]) for x in by_type.values()) != payout:
            raise RegressionEvidenceError(f"BET_TYPE_TOTAL_MISMATCH:{race_id}")
        matching = conversion.get("matching_ticket_types")
        if not isinstance(matching, list):
            raise RegressionEvidenceError(f"MATCHING_TYPES_UNAVAILABLE:{race_id}")
        trio_purchased = "TRIO" in matching
        if trio_purchased != item.get("expected_purchased_trio"):
            raise RegressionEvidenceError(f"PURCHASED_TRIO_CONFLICT:{race_id}")

        row = {
            "race_id": race_id,
            "investment": investment,
            "return": payout,
            "pfs": (round(payout / investment * 100.0, 9) if investment else None),
            "first_failure": failure,
            "hit": bool(summary.get("winning_tickets")),
            "purchased_trio_hit": trio_purchased,
            "ordered_pair_hit": bool(conversion.get("ordered_pair_ticket_coverage")),
            "exact_oriented_hit": bool(conversion.get("ordered_exact_ticket_coverage")),
            "winner_w_capture": (review.get("prediction") or {}).get("role_capture", {}).get("winner_w"),
            "second_p2_capture": (review.get("prediction") or {}).get("role_capture", {}).get("second_p2"),
            "third_p3_capture": (review.get("prediction") or {}).get("role_capture", {}).get("third_p3"),
        }
        rows.append(row)
        reviews.append({
            **review,
            "by_bet_type": by_type,
            "pfs_improvement": build_pfs_improvement_assessment(review),
        })

    score = build_owner_scorecard(reviews)
    totals = manifest.get("day_totals") or {}
    aggregate = score["aggregate"]
    if (aggregate["investment"] != totals.get("investment_yen")
            or aggregate["return"] != totals.get("return_yen")
            or aggregate["race_count"] != totals.get("races")
            or aggregate["hit_races"] != totals.get("hit_races")
            or aggregate["hit_but_loss_count"] != totals.get("hit_but_loss_races")):
        raise RegressionEvidenceError("DAILY_TOTAL_CONFLICT")
    if score["first_material_failure_frequency"] != manifest.get("first_failure_counts"):
        raise RegressionEvidenceError("FIRST_FAILURE_DISTRIBUTION_CONFLICT")

    # A zero-investment abstention has no PFS. In hindsight it avoids this
    # portfolio's realized loss; it is NOT an ex-ante profitable selector.
    out = {
        "profile": PROFILE,
        "manifest_id": manifest.get("profile_id"),
        "source_authority": manifest.get("authority"),
        "status": "HISTORICAL_REGRESSION_ONLY / NON-PRODUCTION / NOT-NEW-OOS-CREDIT",
        "verification_class": "PINNED_GIT_BLOB_AND_REPOSITORY_RECORDED_RESULT_STATUS / NOT_INDEPENDENT_SIGNATURE_VERIFICATION",
        "source_races": rows,
        "frozen_recommendation_scorecard": score,
        "actual_purchase_pfs": None,
        "actual_purchase_status": "UNKNOWN / NO_INDEPENDENT_PURCHASE_LEDGER",
        "no_bet_reference": {
            "investment": 0,
            "return": 0,
            "profit_loss": 0,
            "pfs": None,
            "avoided_frozen_recommendation_loss_in_hindsight": -aggregate["profit_loss"],
            "interpretation": "HINDSIGHT_BENCHMARK_ONLY / NOT_A_FROZEN_SELECTIVE_NO_BET_STRATEGY",
        },
        "prediction_capture": {
            k: sum(row[k] is True for row in rows)
            for k in ("winner_w_capture", "second_p2_capture", "third_p3_capture")
        },
        "conversion_capture": {
            k: sum(row[k] is True for row in rows)
            for k in ("purchased_trio_hit", "ordered_pair_hit", "exact_oriented_hit")
        },
        "owner_attribution_caveat": "HEURISTIC_DIAGNOSTIC_NOT_CAUSAL_ESTIMATE",
        "existing_shadow": manifest.get("existing_forward_shadow_status_at_basis_main"),
        "excluded": manifest.get("excluded"),
        "production_change_authorized": False,
        "automatic_promotion": False,
        "future_action": "CONTINUE_PRE-RESULT_FROZEN_UNKNOWN_OOS_COMPARISONS_IN_EXISTING_COHORTS",
    }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Existing regression JSON path")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--output", help="Optional output JSON path (no mutation of source artifacts)")
    args = parser.parse_args()
    readout = build_regression_readout(Path(args.root), Path(args.manifest))
    data = json.dumps(readout, ensure_ascii=False, indent=2, sort_keys=True) + chr(10)
    if args.output:
        Path(args.output).write_text(data, encoding="utf-8")
    else:
        print(data, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
