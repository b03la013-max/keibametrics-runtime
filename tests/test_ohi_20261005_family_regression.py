from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))


def test_ohi_day_regression_is_nonproduction_and_not_oos_credit():
    r=load(Path("research/common/KM-FAMILY-OHI-20261005-DAY-REGRESSION-R1.json"))
    assert r["parent_current_authority"]=="KM-FAMILY-CURRENT-AUTHORITY-20261004-R39"
    assert "NON-PRODUCTION" in r["status"]
    assert r["formal_grade"]["oos_credit"] is False
    assert r["frozen_recommendation_ledger"]["races"]==7
    assert r["failure_frequency"]=={
        "exact_purchase_continuity":3,
        "winner_role_head":2,
        "pair_materiality":1,
        "mec_cross_bet_capital":1,
    }
    assert r["bet_type_ledger"]["TRIFECTA"]["pfs_percent"]==4.89
    assert r["bet_type_ledger"]["TRIO"]["pfs_percent"]==106.38
    assert all(v=="UNCHANGED" for k,v in r["production_freeze"].items()
               if k not in {"automatic_promotion"})
    assert r["production_freeze"]["automatic_promotion"] is False


def test_family_revision_is_correctness_and_measurement_only():
    g=load(Path("governance/KM-FAMILY-LOCAL-CORRECTNESS-MEASUREMENT-20261005-R1.json"))
    assert g["parent_current_authority"]=="KM-FAMILY-CURRENT-AUTHORITY-20261004-R39"
    assert g["changes"]["result_acquisition_correctness"]["code"]=="OFFICIAL_RESULT_PAGE_RACE_IDENTITY_HOLD"
    exact=g["changes"]["common_exact_continuity"]
    assert exact["definition_and_oos_arms"]=="BYTE-SEMANTIC FROZEN / UNCHANGED"
    assert exact["change"]=="NONE"
    assert exact["production_effect"]=="NONE"
    diag=g["changes"]["family_conversion_diagnostics"]
    assert diag["profile"]=="KM-FAMILY-CONVERSION-DIAGNOSTICS-SHADOW-20261005-R1"
    assert diag["oos_arm"] is False
    assert diag["automatic_purchase"] is False
    assert diag["production_effect"]=="NONE"
    r5=g["changes"]["local_mec_r5"]
    assert r5["arm_definitions"]=="FROZEN / UNCHANGED"
    assert r5["production_effect"]=="NONE"
    assert g["invariants"]["same_day_promotion"]=="FORBIDDEN"
    assert g["invariants"]["automatic_promotion"] is False


def test_r40_is_correctness_only_successor():
    r39=load(Path("profiles/KM_FAMILY_CURRENT_AUTHORITY_20261004_R39.json"))
    r40=load(Path("profiles/KM_FAMILY_CURRENT_AUTHORITY_20261005_R40.json"))
    assert r40["manifest_id"]=="KM-FAMILY-CURRENT-AUTHORITY-20261005-R40"
    assert r40["predecessor"]==r39["manifest_id"]
    assert r40["common_family_components"]["mec"]==r39["common_family_components"]["mec"]
    assert r40["common_family_components"]["capital_policy"]==r39["common_family_components"]["capital_policy"]
    assert r40["family_scoped_authority"]["LOCAL"]["mec"]==r39["family_scoped_authority"]["LOCAL"]["mec"]
    diag=r40["family_scoped_authority"]["LOCAL"]["conversion_diagnostics"]
    assert diag["profile"]=="KM-FAMILY-CONVERSION-DIAGNOSTICS-SHADOW-20261005-R1"
    assert diag["existing_common_exact_definition"]=="UNCHANGED / PREREGISTERED OOS CONTRACT PRESERVED"
    assert diag["production_effect"]=="NONE"
    s=r40["supersession_declaration"]
    assert s["execution_correctness_change"] is True
    assert s["measurement_diagnostic_change"] is True
    assert s["predictive_model_formula_change"] is False
    assert s["production_semantic_policy_change"] is False
    assert s["production_numerical_change"] is False
    assert s["krs_engine_physics_change"] is False
    assert s["mec_r3_policy_change"] is False
    assert s["capital_policy_change"] is False
    assert s["venue_canon_change"] is False
    assert s["automatic_promotion"] is False
