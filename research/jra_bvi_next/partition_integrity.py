"""Audit stored BVI historical aggregate model comparisons without refitting.

This is a read-only arithmetic and qualification check on already-published
post-capture research. It does not inspect independent official race labels,
reverify OIDC, create new statistics from missing rows, or mint Forward OOS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

PROFILE = "KM-JRA-BVI-HELDOUT-AGGREGATE-INTEGRITY-v0.1-20261028"
ARMS = (
    "CONTROL_ONLY",
    "GENERAL_ONLY",
    "HIERARCHICAL_ENV",
    "HIERARCHICAL_ENV_SEASON",
    "PERMUTED_PEDIGREE_NEGATIVE_CONTROL",
)
PARTITIONS = ("VALIDATION", "TEST")


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def _canonical_sha(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _metric(row: dict, arm: str, metric: str) -> float:
    value = row[arm][metric]
    _require(type(value) in (int, float) and math.isfinite(value) and value >= 0,
             "NONFINITE_OR_NEGATIVE_METRIC:" + arm + ":" + metric)
    return float(value)


def _n(row: dict, arm: str) -> int:
    n = row[arm]["n"]
    _require(type(n) is int and n > 0, "INVALID_SAMPLE_COUNT:" + arm)
    horses = row[arm]["composite_horses"]
    _require(type(horses) is int and 1 <= horses <= n, "INVALID_COMPOSITE_HORSE_COUNT:" + arm)
    return n


def _compare(row: dict) -> dict:
    g, e = row["GENERAL_ONLY"], row["HIERARCHICAL_ENV"]
    return {
        "n": _n(row, "GENERAL_ONLY"),
        "composite_horses_proxy": g["composite_horses"],
        "general_mse": _metric(row, "GENERAL_ONLY", "mse"),
        "environment_mse": _metric(row, "HIERARCHICAL_ENV", "mse"),
        "delta_mse_env_minus_general": _metric(row, "HIERARCHICAL_ENV", "mse") - _metric(row, "GENERAL_ONLY", "mse"),
        "general_mae": _metric(row, "GENERAL_ONLY", "mae"),
        "environment_mae": _metric(row, "HIERARCHICAL_ENV", "mae"),
        "delta_mae_env_minus_general": _metric(row, "HIERARCHICAL_ENV", "mae") - _metric(row, "GENERAL_ONLY", "mae"),
        "delta_mse_control_minus_general": _metric(row, "CONTROL_ONLY", "mse") - _metric(row, "GENERAL_ONLY", "mse"),
        "delta_mse_permuted_minus_general": _metric(row, "PERMUTED_PEDIGREE_NEGATIVE_CONTROL", "mse") - _metric(row, "GENERAL_ONLY", "mse"),
        "delta_mse_season_minus_general": _metric(row, "HIERARCHICAL_ENV_SEASON", "mse") - _metric(row, "GENERAL_ONLY", "mse"),
    }


def _validate_arm_set(row: dict, expected_n: int, label: str) -> None:
    _require(set(ARMS) == set(row), "MODEL_ARMS_NOT_FIXED:" + label)
    for arm in ARMS:
        _require(_n(row, arm) == expected_n, "MODEL_SAMPLE_MISMATCH:" + label + ":" + arm)
        for metric in ("mse", "mae"):
            _metric(row, arm, metric)


def audit_report(report: dict) -> dict:
    _require(report.get("classification") == "POST_CAPTURE_CHRONOLOGICAL_DIAGNOSTIC; NOT_FORWARD_OOS",
             "HISTORICAL_CLASSIFICATION_REQUIRED")
    _require(report.get("production_training_eligibility") is False
             and report.get("production_effect") == "NONE"
             and report.get("purchase_authority") is False
             and report.get("forward_oos_increment") == 0
             and report.get("fixed_incumbent_modified") is False,
             "NONPRODUCTION_SAFETY_CONTRACT_FAILED")
    _require(report.get("eligible_permanent_horse_ids") == 0
             and report.get("independent_race_labels") == 0,
             "INDEPENDENT_ID_OR_LABEL_STATUS_CHANGED")
    protocol = report.get("protocol") or {}
    _require(_canonical_sha(protocol) == report.get("protocol_sha256"), "PROTOCOL_SHA_MISMATCH")
    _require(protocol.get("hyperparameter_search") is False
             and protocol.get("automatic_promotion") is False
             and protocol.get("label") == "1-(finish-1)/(field_size-1)",
             "FIXED_CONTINUOUS_TARGET_CONTRACT_FAILED")
    _require(report.get("decision") == "REJECT_HISTORICAL_INCREMENT"
             and report.get("predictive_improvement_demonstrated") is False,
             "INCUMBENT_REJECTION_NOT_PRESERVED")
    _require(set(report.get("partitions") or {}) == set(PARTITIONS),
             "CHRONOLOGICAL_PARTITIONS_MISMATCH")

    out = {"profile": PROFILE,
           "classification": "READ_ONLY_POST_CAPTURE_AGGREGATE_ARITHMETIC; UNQUALIFIED_PROXY; NOT_FORWARD_OOS",
           "source_dataset_sha256": report["dataset_sha256"],
           "source_protocol_sha256": report["protocol_sha256"],
           "partitions": {},
           "model_selection": "REJECT_HISTORICAL_INCREMENT",
           "promotion_authorized": False, "production_effect": "NONE",
           "forward_oos_increment": 0, "purchase_authority": False,
           "independent_race_label_verified": False,
           "permanent_horse_id_verified": False,
           "train_disjoint_status": "REPORTED_COMPOSITE_HORSE_NONOVERLAP_ONLY; NOT_INDEPENDENTLY_ROW_REVERIFIED",
           "validation_test_horse_disjoint": "NOT_ESTABLISHED",
           "significance_test": "NOT_RUN; NO_ROW_LEVEL_PAIRED_RESIDUALS",
           "brier": None, "logloss": None,
           "probability_metric_status": "NOT_COMPUTABLE_FOR_CONTINUOUS_FINISH_RANK_PROXY_WITHOUT_CALIBRATED_BINARY_PROBABILITIES",
           "negative_controls": {"control_only": "NO_PEDIGREE_ABLATION",
                                 "permuted_pedigree": "SINGLE_FIXED_SEED_PERMUTATION_NOT_SIGNIFICANCE_TEST",
                                 "independent_second_placebo": "NOT_EXECUTED"}}

    for name in PARTITIONS:
        p = report["partitions"][name]
        arms = p["arms"]
        total = _n(arms, "GENERAL_ONLY")
        _validate_arm_set(arms, total, name + ":all")
        seen = p["groups"]["horse_seen"]
        _require(set(seen) == {"True", "False"}, "HORSE_SEEN_PARTITION_INCOMPLETE:" + name)
        n_seen, n_unseen = (_n(seen["True"], "GENERAL_ONLY"),
                            _n(seen["False"], "GENERAL_ONLY"))
        _require(n_seen + n_unseen == total, "HORSE_SEEN_SAMPLE_NONPARTITION:" + name)
        _require(n_unseen == p["dependence"]["unseen_horse_rows"],
                 "UNSEEN_HORSE_ROW_COUNT_MISMATCH:" + name)
        _require(seen["True"]["GENERAL_ONLY"]["composite_horses"]
                 == p["dependence"]["horse_overlap_with_train"],
                 "TRAIN_HORSE_OVERLAP_COUNT_MISMATCH:" + name)
        _require(seen["True"]["GENERAL_ONLY"]["composite_horses"]
                 + seen["False"]["GENERAL_ONLY"]["composite_horses"]
                 == arms["GENERAL_ONLY"]["composite_horses"],
                 "COMPOSITE_HORSE_COUNT_NONPARTITION:" + name)

        for label, bucket in seen.items():
            _validate_arm_set(bucket, n_seen if label == "True" else n_unseen, name + ":horse_seen:" + label)
        for arm in ARMS:
            for metric in ("mse", "mae"):
                aggregate = _metric(arms, arm, metric)
                by_horse = (
                    n_seen * _metric(seen["True"], arm, metric)
                    + n_unseen * _metric(seen["False"], arm, metric)
                ) / total
                _require(abs(aggregate - by_horse) <= 1e-11,
                         "HORSE_SEEN_WEIGHTED_AGGREGATE_MISMATCH:" + name + ":" + arm + ":" + metric)

        # Venue and surface are disjoint reported slices. Going may be incomplete;
        # never force a missing going observation into a synthetic category.
        for dimension in ("venue", "surface"):
            segments = p["groups"][dimension]
            _require(sum(_n(v, "GENERAL_ONLY") for v in segments.values()) == total,
                     "GROUP_COVERAGE_INCOMPLETE:" + name + ":" + dimension)
            for segment, bucket in segments.items():
                _validate_arm_set(bucket, _n(bucket, "GENERAL_ONLY"),
                                  name + ":" + dimension + ":" + segment)
            for arm in ARMS:
                for metric in ("mse", "mae"):
                    weighted = sum(_n(x, arm) * _metric(x, arm, metric)
                                   for x in segments.values()) / total
                    _require(abs(_metric(arms, arm, metric) - weighted) <= 1e-11,
                             "GROUP_WEIGHTED_AGGREGATE_MISMATCH:" + name + ":" + dimension + ":" + arm + ":" + metric)

        out["partitions"][name] = {
            "all": _compare(arms),
            "reported_train_disjoint_composite_horses": _compare(seen["False"]),
            "reported_train_seen_composite_horses": _compare(seen["True"]),
            "train_disjoint_proxy_rows": n_unseen,
            "training_overlap_proxy_horses": p["dependence"]["horse_overlap_with_train"],
            "venue_delta_mse": {k: {"n": _n(v, "GENERAL_ONLY"),
                                    "delta_env_minus_general": _compare(v)["delta_mse_env_minus_general"]}
                                for k, v in sorted(p["groups"]["venue"].items())},
        }

    v = out["partitions"]["VALIDATION"]["reported_train_disjoint_composite_horses"]
    t = out["partitions"]["TEST"]["reported_train_disjoint_composite_horses"]
    out["unseen_horse_effect_direction_consistent"] = (
        (v["delta_mse_env_minus_general"] > 0) == (t["delta_mse_env_minus_general"] > 0)
    )
    out["future_incremental_value_proven"] = False
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path,
                        default=Path(__file__).resolve().parent / "evidence/current_corpus_evaluation.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    original = args.input.read_bytes()
    record = audit_report(json.loads(original))
    record["source_report_raw_sha256"] = hashlib.sha256(original).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({"profile": PROFILE, "source_report_raw_sha256": record["source_report_raw_sha256"],
                      "partitions": {k: {"n": v["all"]["n"],
                                        "delta_mse": v["all"]["delta_mse_env_minus_general"],
                                        "unseen_n": v["train_disjoint_proxy_rows"],
                                        "unseen_delta_mse": v["reported_train_disjoint_composite_horses"]["delta_mse_env_minus_general"]}
                                     for k, v in record["partitions"].items()},
                      "future_incremental_value_proven": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
