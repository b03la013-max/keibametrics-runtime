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
    assert exact["arm_definitions"]=="FROZEN / UNCHANGED"
    assert exact["production_effect"]=="NONE"
    assert exact["automatic_purchase"] is False
    r5=g["changes"]["local_mec_r5"]
    assert r5["arm_definitions"]=="FROZEN / UNCHANGED"
    assert r5["production_effect"]=="NONE"
    assert g["invariants"]["same_day_promotion"]=="FORBIDDEN"
    assert g["invariants"]["automatic_promotion"] is False
