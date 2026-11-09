import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def test_ohi_v24_is_candidate_and_v23_remains_production():
    c = load("profiles/ohi_venue_canon_candidate_20261007_v2.4.json")
    assert "CANDIDATE" in c["status"]
    assert "NON-PRODUCTION" in c["status"]
    assert c["predecessor"]["canonical_name"] == "大井競馬攻略条項 v2.3-OHI"
    assert c["production_pointer_change"] is False
    assert c["production_effect"] == "NONE"
    assert c["numerical_change"] is False
    assert c["krs_physics_change"] is False
    assert c["parameter_map_change"] is False
    assert c["mec_r3_change"] is False
    assert c["capital_policy_change"] is False
    assert c["ticket_authority_change"] is False

def test_ohi_v24_has_only_four_venue_prediction_hypotheses():
    c = load("profiles/ohi_venue_canon_candidate_20261007_v2.4.json")
    ids = {x["id"] for x in c["venue_shadow_hypotheses"]}
    assert ids == {
        "OHI-ABILITY-READINESS-SEPARATION-R1",
        "OHI-ACQUISITION-LEADERSHIP-COST-STALKABILITY-R1",
        "OHI-VENUE-CONDITIONED-WINNER-ROLE-MIGRATION-R1",
        "OHI-TRANSFER-FIRST-OHI-ADAPTATION-UNCERTAINTY-R1",
    }
    assert all(x["owner"] == "VENUE_PREDICTION" for x in c["venue_shadow_hypotheses"])
    assert all(x["numerical_rule"] is False for x in c["venue_shadow_hypotheses"])

def test_common_capital_and_ticket_topics_stay_out_of_venue_authority():
    c = load("profiles/ohi_venue_canon_candidate_20261007_v2.4.json")
    assert c["common_handoff"]["venue_canon_ownership"] is False
    topics = set(c["common_handoff"]["topics"])
    assert "PROTECTION_BURDEN_RATIO" in topics
    assert "MARKET_PAYOUT_SUFFICIENCY" in topics
    assert "PAIR_LOCAL_SELECTIVE_EXACT_PURCHASE_AUTHORITY" in topics
    assert "PRODUCTION_MEC_R3" in topics
    assert "PRODUCTION_CAPITAL_POLICY" in topics
    assert "KRS_PHYSICS_PARAMETER_MAP" in topics

def test_20261007_is_regression_only_not_candidate_oos():
    c = load("profiles/ohi_venue_canon_candidate_20261007_v2.4.json")
    r = load("research/ohi/KM-LOCAL-OHI-20261007-VENUE-REGRESSION-R1.json")
    assert c["oos_validation"]["todays_races_eligible"] is False
    assert r["status"].find("NON-OOS") >= 0
    assert r["production_basis"]["venue_canon"] == "大井競馬攻略条項 v2.3-OHI"
    assert r["day_summary"]["race_count"] == 12
    assert r["day_summary"]["frozen_recommendation_investment_yen"] == 183200
    assert r["day_summary"]["frozen_recommendation_return_yen"] == 111440
    assert r["day_summary"]["pfs_pct"] == 60.83

def test_regression_fixtures_cover_positive_and_negative_controls():
    r = load("research/ohi/KM-LOCAL-OHI-20261007-VENUE-REGRESSION-R1.json")
    labels = {x["label"] for x in r["venue_owned_fixtures"]}
    assert labels == {
        "ABILITY_CEILING_VS_WINNER_CONVERSION",
        "INDEPENDENT_RESCUE_POSITIVE_CONTROL",
        "ROLE_CAPTURE_PAIR_CONNECTION_SEPARATION",
        "STATIC_KRS_COMMON_BLIND_SPOT",
    }
    assert "KNOWN_20261007_RESULTS_COUNT_AS_V24_OOS" in r["prohibited_inferences"]

def test_krs_firewall_and_human_promotion_gate_remain():
    c = load("profiles/ohi_venue_canon_candidate_20261007_v2.4.json")
    assert c["krs_boundary"]["firewall"] == "KEEP"
    assert c["krs_boundary"]["automatic_w_pair_exact_promotion"] is False
    assert c["promotion_gate"]["automatic_promotion"] is False
    assert c["promotion_gate"]["explicit_human_review"] is True
