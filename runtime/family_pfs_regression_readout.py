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

    learning_required = manifest.get("require_prequential_learning_binding") is True
    learning_ids = []
    reviews = []
    rows = []
    seen = set()
    for item in cohort:
        race_id = str(item.get("race_id") or "")
        if not race_id or race_id in seen:
            raise RegressionEvidenceError(f"DUPLICATE_OR_MISSING_RACE:{race_id}")
        seen.add(race_id)

        src_path = _get_existing_file(root, str(item.get("result_summary_path") or ""))
        try:
            raw = src_path.read_bytes()
        except OSError as exc:
            raise RegressionEvidenceError(f"EVIDENCE_NOT_READABLE:{src_path}") from exc
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
        for key, field in (
            ("expected_ordered_pair", "ordered_pair_ticket_coverage"),
            ("expected_ordered_exact", "ordered_exact_ticket_coverage"),
        ):
            if key in item and conversion.get(field) is not item[key]:
                raise RegressionEvidenceError(f"CONVERSION_COVERAGE_CONFLICT:{race_id}:{key}")

        if learning_required:
            event = summary.get("learning_event") or {}
            if (event.get("status") != "PREQUENTIAL-NEXT-RACE-ONLY"
                    or event.get("state_id") != race_id + "-LEARNING-NEXT"
                    or event.get("source_review_sha256") != review.get("sha256")
                    or event.get("production_change_authorized") is not False
                    or event.get("reference_metrics", {}).get("first_material_failure") != failure
                    or "RETROACTIVE_PREDICTION_REWRITE" not in (event.get("forbidden") or [])):
                raise RegressionEvidenceError(f"LEARNING_BINDING_INVALID:{race_id}")
            learning_ids.append(event["state_id"])

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

    # The paired AKI paper tracker is the *same seven-race* pre-result cohort.
    # It remains non-Production and never creates new OOS entries. MEC-R5's
    # 30-race cohort is deliberately not pooled with these seven AKI rows.
    paired_aki = None
    separate_r5 = None
    comparison = None
    bindings = manifest.get("candidate_measurement_bindings") or {}
    if "aki" in bindings:
        pinned = bindings["aki"]
        aki_path = pinned.get("status_path")
        if aki_path != "runtime/aki_adaptive_oos_status.json":
            raise RegressionEvidenceError("AKI_PATH_NOT_CANONICAL")
        source = (root / aki_path)
        try:
            aki_raw = source.read_bytes()
        except OSError as exc:
            raise RegressionEvidenceError("AKI_STATUS_UNAVAILABLE") from exc
        if _git_blob_sha(aki_raw) != pinned.get("status_git_blob_sha"):
            raise RegressionEvidenceError("AKI_STATUS_BLOB_CHANGED")
        aki = _load(source)
        if (aki.get("sha256") != pinned.get("reported_sha256")
                or aki.get("status") != "WAITING_FORWARD_OOS"
                or aki.get("errors") != []
                or aki.get("eligible_races") != len(rows)
                or aki.get("eligible_races") != pinned.get("race_count")
                or aki.get("days") != pinned.get("distinct_days")
                or aki.get("actual_purchase_pfs") is not None
                or aki.get("automatic_promotion") is not False
                or aki.get("production_change_authorized") is not False):
            raise RegressionEvidenceError("AKI_MEASUREMENT_STATUS_INVALID")
        settled = aki.get("settled_rows") or []
        indexed = {r["race_id"]: r for r in settled}
        if len(indexed) != len(settled) or set(indexed) != seen:
            raise RegressionEvidenceError("AKI_RACE_UNIVERSE_MISMATCH")
        for row, review in zip(rows, reviews):
            arow = indexed[row["race_id"]]
            if (arow.get("oos_eligible") is not True
                    or arow.get("paper_only") is not True
                    or arow.get("actual_purchase") is not False
                    or arow.get("production_effect") != "NONE"
                    or arow.get("candidate_action") != "PAPER"
                    or arow.get("regime") != "SELECTIVE"
                    or arow.get("production", {}).get("investment") != row["investment"]
                    or arow.get("production", {}).get("return") != row["return"]
                    or arow.get("final_receipt_sha256") != review["final_receipt_sha256"]):
                raise RegressionEvidenceError(f"AKI_FROZEN_ROW_CONFLICT:{row['race_id']}")
            source_summary = _load(_get_existing_file(root,
                next(x["result_summary_path"] for x in cohort if x["race_id"] == row["race_id"])))
            if arow.get("result_receipt_sha256") != source_summary.get("result_receipt"):
                raise RegressionEvidenceError(f"AKI_RESULT_RECEIPT_CONFLICT:{row['race_id']}")
        prod, cand = aki.get("production") or {}, aki.get("adaptive") or {}
        if (prod.get("investment") != sum(x["investment"] for x in rows)
                or prod.get("return") != sum(x["return"] for x in rows)
                or prod.get("investment") != pinned.get("production_investment_yen")
                or prod.get("return") != pinned.get("production_return_yen")
                or cand.get("investment") != pinned.get("adaptive_paper_investment_yen")
                or cand.get("return") != pinned.get("adaptive_paper_return_yen")):
            raise RegressionEvidenceError("AKI_AGGREGATE_CONFLICT")
        comparison = {"AKI_SELECTIVE_PAPER": {
            "investment": cand["investment"], "return": cand["return"],
            "pfs": cand["pfs"], "profit_loss": cand["profit_loss"],
            "max_drawdown": None,
            "equal_budget_pfs": None,
            "equal_ticket_profit": None,
            "hit_but_loss_rate": None,
            "set_coverage_rate": None,
            "largest_return_share": None,
        }}
        paired_aki = {
            "measurement_status": aki["status"],
            "measurement_report_sha256": aki["sha256"],
            "candidate": cand, "production_same_races": prod,
            "eligible_races_already_counted_by_original_tracker": len(rows),
            "distinct_days": aki["days"],
            "oos_increment_from_this_regression": 0,
            "actual_purchase_pfs": None,
            "economic_verdict": ("ADVERSE" if cand["pfs"] < prod["pfs"]
                                 else "NOT_YET_PROMOTION_EVIDENCE"),
            "equal_budget_comparison": None,
            "equal_ticket_comparison": None,
            "normalization_note": "DIFFERENT_PURCHASED_TICKETS_AND_BUDGETS; NO_LINEAR_REWEIGHTING_AS_EXECUTABLE_RESULT",
            "promotion_authorized": False,
        }
    if "mec_r5" in bindings:
        pinned = bindings["mec_r5"]
        if pinned.get("status_path") != "runtime/local_mec_r5_oos_status.json":
            raise RegressionEvidenceError("R5_PATH_NOT_CANONICAL")
        r5_source = root / pinned["status_path"]
        try:
            r5_raw = r5_source.read_bytes()
        except OSError as exc:
            raise RegressionEvidenceError("R5_STATUS_UNAVAILABLE") from exc
        if _git_blob_sha(r5_raw) != pinned.get("status_git_blob_sha"):
            raise RegressionEvidenceError("R5_STATUS_BLOB_CHANGED")
        r5 = _load(r5_source)
        prod30 = (r5.get("aggregates") or {}).get("PRODUCTION_BASELINE_R3") or {}
        cand30 = (r5.get("aggregates") or {}).get("SET_PAIR_EXACT_TOP4") or {}
        if (r5.get("status") != "COMPLETE_30_HUMAN_REVIEW_REQUIRED"
                or r5.get("eligible_races") != pinned.get("eligible_races")
                or prod30.get("investment_weighted_pfs") != pinned.get("production_30_pfs")
                or cand30.get("investment_weighted_pfs") != pinned.get("candidate_top4_pfs")
                or r5.get("automatic_promotion") is not False):
            raise RegressionEvidenceError("R5_COHORT_STATUS_INVALID")
        separate_r5 = {
            "status": r5["status"], "eligible_races": r5["eligible_races"],
            "production": prod30, "candidate_top4": cand30,
            "overlap_with_seven_race_aki_not_assumed": True,
            "pooled_pfs": None, "oos_increment_from_this_regression": 0,
            "promotion_authorized": False,
        }
    score = build_owner_scorecard(reviews, candidate_comparisons=comparison)
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
        "prequential_learning_binding": {
            "required": learning_required,
            "verified_existing_event_count": len(learning_ids),
            "existing_state_ids": learning_ids,
            "new_learning_events_created": 0,
            "source_review_artifacts_rewritten": False,
        },
        "paired_aki_paper": paired_aki,
        "distinct_mec_r5_cohort": separate_r5,
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
