import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def test_fnb_v22_is_candidate_and_v21_remains_production():
    c=load("profiles/fnb_venue_canon_candidate_20260930_v2.2.json")
    ca=load("profiles/KM_FAMILY_CURRENT_AUTHORITY_20260929_R35.json")
    assert "CANDIDATE" in c["status"]
    assert "NON-PRODUCTION" in c["status"]
    assert c["production_pointer_change"] is False
    assert c["numerical_change"] is False
    assert ca["venue_canon_current_decisions"]["FNB"]["production"]=="船橋競馬攻略条項 v2.1-FNB"
    assert ca["venue_canon_current_decisions"]["FNB"]["profile"]=="KM-LOCAL-FNB-v2.1-20260928-R1"

def test_fnb_v22_keeps_common_failures_out_of_venue_ownership():
    c=load("profiles/fnb_venue_canon_candidate_20260930_v2.2.json")
    ids={x["id"] for x in c["venue_shadow_hypotheses"]}
    assert ids=={
        "FNB-2YO-LOWOBS-ALT-P2-REACHABILITY-R1",
        "FNB-DISTANCE-RETURN-CLASS-CONTEXT-W-REACHABILITY-R1",
        "FNB-LAYOFF-HISTORICAL-CEILING-DECAY-AUDIT-R1",
        "FNB-CLASS-EXPOSURE-RELIEF-TRANSLATION-AUDIT-R1",
    }
    assert c["common_handoff"]["venue_canon_ownership"] is False
    assert "MATERIAL_PAIR_X_ACTIVE_P3_EXACT_CONTINUITY" in c["common_handoff"]["topics"]
    assert "CONCENTRATION_AWARE_CAPITAL_WIDTH" in c["common_handoff"]["topics"]

def test_common_shadow_has_no_production_authority():
    s=load("research/fnb/KM-FAMILY-FNB-20260930-COMMON-SHADOW-PACK-R1.json")
    assert "NON-PRODUCTION" in s["status"]
    assert all(v is False for v in s["production_changes"].values())
    exact=next(x for x in s["hypotheses"] if x["id"]=="KM-COMMON-EXACT-CONTINUITY-AUDIT-R1")
    assert exact["automatic_purchase"] is False
    capital=next(x for x in s["hypotheses"] if x["id"]=="KM-COMMON-CONCENTRATION-AWARE-CAPITAL-WIDTH-HYPOTHESIS-R1")
    assert capital["oos_eligible"] is False
    assert capital["automatic_capital_change"] is False

def test_today_is_not_candidate_oos():
    c=load("profiles/fnb_venue_canon_candidate_20260930_v2.2.json")
    assert c["oos_validation"]["todays_races_eligible"] is False
    assert c["day_regression_basis"]["exact_semantic_only_repeat_races"]==["R04","R05","R07","R08","R09","R11","R12"]
