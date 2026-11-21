"""Read-only 2026-10-31 research handoff preflight; never a registration.

No external SOURCE, no scheduler/sidecar dispatch, no model refit, no signing.
The independent archive and a genuinely pre-cutoff fixed research model remain
separate requirements. A rejected historical candidate cannot be made an OOS
candidate just by running this check before race day.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from partition_integrity import audit_report

PROFILE = "KM-JRA-BVI-RESEARCH-FORWARD-PREFLIGHT-20261030"
AUTHORITY = "KM-FAMILY-CURRENT-AUTHORITY-20261012-R51"
FIXED_D = "runtime/jra_static_owner_forward_oos/models/bvi_env_20261024_5e7f3b31cebd.json"
FIXED_D_SHA256 = "a969cc518da73b4795932f02d8f3cbc6d0ac47a1a7904907055e46958d9f0fc1"
TARGET_DATE = "2026-10-31"
TARGET_VENUES = ("TKY", "KYO")


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def assess(authority: dict, static_oos: dict, pedigree_oos: dict,
           historical: dict, fixed_model_sha: str,
           *, plan: dict | None = None) -> dict:
    """Pure safety check. Inputs remain immutable and historical metrics stay historical."""
    require(authority.get("manifest_id") == AUTHORITY, "UNEXPECTED_CURRENT_AUTHORITY")
    require("JRA" in (authority.get("family_scoped_authority") or {}),
            "JRA_SCOPE_NOT_RESOLVED")
    require(fixed_model_sha == FIXED_D_SHA256, "FIXED_D_BYTES_CHANGED")
    require(static_oos.get("eligible_settled_races") == 0
            and static_oos.get("automatic_promotion") is False,
            "STATIC_OOS_OR_PROMOTION_NOT_AT_ZERO_BASELINE")
    require(pedigree_oos.get("eligible_settled_races") == 0
            and pedigree_oos.get("unpooled_race_count") == 0
            and not pedigree_oos.get("cohorts"), "PEDIGREE_OOS_COHORT_NOT_AT_ZERO_BASELINE")
    require(set((pedigree_oos.get("arms") or {}).keys()) == {
                "A_CURRENT", "B_PEDIGREE_ENHANCED_SHADOW",
                "C_BLOODLINE_ABLATION", "D_BVI_ENV_SHADOW",
            }, "FOUR_ARM_COHORT_SHAPE_CHANGED")
    require(pedigree_oos.get("automatic_promotion") is False
            and pedigree_oos.get("production_effect") == "NONE"
            and pedigree_oos.get("required_forward_races") == 30,
            "PEDIGREE_OOS_SAFETY_POLICY_CHANGED")
    comparison = audit_report(historical)
    full_test = comparison["partitions"]["TEST"]["all"]
    full_validation = comparison["partitions"]["VALIDATION"]["all"]
    require(full_test["delta_mse_env_minus_general"] > 0
            and full_validation["delta_mse_env_minus_general"] > 0,
            "HISTORICAL_REJECT_DIRECTION_NOT_RECONCILED")
    require(comparison["model_selection"] == "REJECT_HISTORICAL_INCREMENT"
            and comparison["future_incremental_value_proven"] is False,
            "REJECTED_RESEARCH_MODEL_MISREPRESENTED")
    if plan is not None:
        require(plan.get("family_id") == "JRA" and
                plan.get("race_date") == TARGET_DATE, "FUTURE_PLAN_DATE_OR_FAMILY_MISMATCH")
    # No mutation, independent provider archive or pre-cutoff registration here.
    return {
        "profile": PROFILE,
        "classification": "READ_ONLY_RESEARCH_PREPARATION; NOT_REGISTRATION_OR_FORWARD_OOS",
        "target_date": TARGET_DATE,
        "target_venues": list(TARGET_VENUES),
        "authority": AUTHORITY,
        "fixed_d_raw_sha256": fixed_model_sha,
        "official_plan_in_repository": plan is not None,
        "official_plan_is_fresh_signed_source": False,
        "planned_race_count": None,
        "new_formal_requests": None,
        "new_signed_finals": None,
        "new_independent_pre_cutoff_freezes": 0,
        "independent_registration_receipt": None,
        "candidate_fixed_and_accepted_for_future": False,
        "historical_candidate_decision": "REJECT_HISTORICAL_INCREMENT",
        "historical_test": full_test,
        "historical_validation": full_validation,
        "historical_train_unseen_is_official_ID_verified": False,
        "independent_race_labels": 0,
        "new_forward_oos_credit": 0,
        "eligible_settled_forward_oos": 0,
        "ticket_effect": None,
        "pfs_increment": None,
        "production_effect": "NONE",
        "dispatch_performed": False,
        "unresolved": [
            "APPROVED_DISTINCT_PROSPECTIVE_RESEARCH_MODEL_AND_EXACT_CODE_HASH",
            "INDEPENDENT_TIME_STAMPED_REGISTRATION_BEFORE_FUTURE_SOURCE_CUTOFF",
            "FRESH_OFFICIAL_LISTED_RUNNERS_AND_FORMAL_REQUEST",
            "ELIGIBLE_PRESTART_PRODUCTION_AND_RESEARCH_FREEZE",
            "PERMANENT_HORSE_IDS_AND_INDEPENDENT_RESULT_LABEL_CLOCKS",
            "INDEPENDENT_REVIEW_AND_LIVE_RESULT_AFTER_RACE",
        ],
    }


def run(root: Path) -> dict:
    root = root.resolve()
    authority = json.loads((root / "profiles/KM_FAMILY_CURRENT_AUTHORITY_20261012_R51.json").read_text())
    static = json.loads((root / "runtime/jra_static_owner_forward_oos/current.json").read_text())
    pedigree = json.loads((root / "runtime/jra_static_owner_forward_oos/pedigree_env_current.json").read_text())
    history = json.loads((root / "research/jra_bvi_next/evidence/current_corpus_evaluation.json").read_text())
    model_sha = hashlib.sha256((root / FIXED_D).read_bytes()).hexdigest()
    plan_path = root / "runtime/jra_race_day_plan" / (TARGET_DATE + ".json")
    plan = json.loads(plan_path.read_text()) if plan_path.exists() else None
    return assess(authority, static, pedigree, history, model_sha, plan=plan)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.repository)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    require(not args.output.exists(), "IMMUTABLE_RESEARCH_PREFLIGHT_OUTPUT_EXISTS")
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: result[key] for key in
          ("profile", "target_date", "official_plan_in_repository",
           "historical_candidate_decision", "eligible_settled_forward_oos",
           "new_forward_oos_credit", "dispatch_performed")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
