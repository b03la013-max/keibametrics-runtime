"""Adversarial, offline checks for 10/31 research handoff non-promotion."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import forward_preflight as p


@pytest.fixture(scope="module")
def snapshots():
    files = (
        "profiles/KM_FAMILY_CURRENT_AUTHORITY_20261012_R51.json",
        "runtime/jra_static_owner_forward_oos/current.json",
        "runtime/jra_static_owner_forward_oos/pedigree_env_current.json",
        "research/jra_bvi_next/evidence/current_corpus_evaluation.json",
    )
    return tuple(json.loads((ROOT / f).read_text()) for f in files)


def call(snapshots, model_sha=p.FIXED_D_SHA256, plan=None):
    return p.assess(*snapshots, model_sha, plan=plan)


def test_repository_readonly_preflight_has_no_registration_or_result_credit():
    out = p.run(ROOT)
    assert out["target_date"] == "2026-10-31"
    assert out["target_venues"] == ["TKY", "KYO"]
    assert out["fixed_d_raw_sha256"] == p.FIXED_D_SHA256
    assert out["independent_registration_receipt"] is None
    assert out["new_forward_oos_credit"] == 0
    assert out["eligible_settled_forward_oos"] == 0
    assert out["candidate_fixed_and_accepted_for_future"] is False
    assert out["new_formal_requests"] is None
    assert out["new_signed_finals"] is None
    assert out["ticket_effect"] is None and out["pfs_increment"] is None
    assert out["dispatch_performed"] is False


def test_fixed_d_mutation_rejected_before_future_claim(snapshots):
    with pytest.raises(ValueError, match="FIXED_D_BYTES_CHANGED"):
        call(snapshots, model_sha="0" * 64)


def test_non_jra_authority_fails_closed(snapshots):
    x = copy.deepcopy(snapshots)
    x[0]["manifest_id"] = "R52"
    with pytest.raises(ValueError, match="UNEXPECTED_CURRENT_AUTHORITY"):
        call(x)
    x = copy.deepcopy(snapshots)
    x[0]["family_scoped_authority"].pop("JRA")
    with pytest.raises(ValueError, match="JRA_SCOPE_NOT_RESOLVED"):
        call(x)


def test_silent_oos_credit_and_promotion_are_rejected(snapshots):
    x = copy.deepcopy(snapshots)
    x[1]["eligible_settled_races"] = 1
    with pytest.raises(ValueError, match="STATIC_OOS_OR_PROMOTION"):
        call(x)
    x = copy.deepcopy(snapshots)
    x[2]["eligible_settled_races"] = 1
    with pytest.raises(ValueError, match="PEDIGREE_OOS_COHORT"):
        call(x)


def test_invalid_model_quality_claim_and_qualifications_rejected(snapshots):
    x = copy.deepcopy(snapshots)
    x[3]["decision"] = "PROMOTE"
    with pytest.raises(ValueError, match="INCUMBENT_REJECTION_NOT_PRESERVED"):
        call(x)
    x = copy.deepcopy(snapshots)
    x[3]["eligible_permanent_horse_ids"] = 1
    with pytest.raises(ValueError, match="INDEPENDENT_ID_OR_LABEL_STATUS_CHANGED"):
        call(x)


def test_wrong_future_plan_cannot_be_used_as_pre_registration(snapshots):
    with pytest.raises(ValueError, match="FUTURE_PLAN_DATE_OR_FAMILY_MISMATCH"):
        call(snapshots, plan={"family_id": "JRA", "race_date": "2026-10-25"})
    with pytest.raises(ValueError, match="FUTURE_PLAN_DATE_OR_FAMILY_MISMATCH"):
        call(snapshots, plan={"family_id": "LOCAL", "race_date": "2026-10-31"})


def test_stored_comparison_remains_rejected_even_if_subset_seems_better(snapshots):
    out = call(snapshots)
    assert out["historical_test"]["n"] == 2771
    assert out["historical_test"]["delta_mse_env_minus_general"] > 0
    assert out["historical_validation"]["n"] == 1546
    assert out["historical_validation"]["delta_mse_env_minus_general"] > 0
    assert out["historical_candidate_decision"] == "REJECT_HISTORICAL_INCREMENT"


def test_replaced_arm_cannot_pass_a_four_arm_count_check(snapshots):
    x = copy.deepcopy(snapshots)
    x[2]["arms"]["UNREGISTERED_INJECTED_ARM"] = x[2]["arms"].pop("D_BVI_ENV_SHADOW")
    with pytest.raises(ValueError, match="FOUR_ARM_COHORT_SHAPE_CHANGED"):
        call(x)


def test_pedigree_oos_autopromotion_and_policy_drift_rejected(snapshots):
    x = copy.deepcopy(snapshots)
    x[2]["automatic_promotion"] = True
    with pytest.raises(ValueError, match="PEDIGREE_OOS_SAFETY_POLICY_CHANGED"):
        call(x)
    x = copy.deepcopy(snapshots)
    x[2]["production_effect"] = "AUTO_PROMOTE"
    with pytest.raises(ValueError, match="PEDIGREE_OOS_SAFETY_POLICY_CHANGED"):
        call(x)
