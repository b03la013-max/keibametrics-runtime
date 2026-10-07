import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def test_r43_activates_owner_utility_without_predictive_policy_change():
    a = load("profiles/KM_FAMILY_CURRENT_AUTHORITY_20261007_R43.json")
    assert a["manifest_id"] == "KM-FAMILY-CURRENT-AUTHORITY-20261007-R43"
    assert "CURRENT-AUTHORITY" in a["status"]
    assert a["predecessor"] == "KM-FAMILY-CURRENT-AUTHORITY-20261005-R40"
    d = a["r43_change_declaration"]
    assert d["governance_change"] is True
    assert d["post_result_measurement_change"] is True
    assert d["learning_routing_change"] is True
    assert d["production_prediction_change"] is False
    assert d["production_numerical_change"] is False
    assert d["krs_physics_change"] is False
    assert d["parameter_map_change"] is False
    assert d["mec_r3_change"] is False
    assert d["capital_policy_change"] is False
    assert d["ticket_authority_change"] is False
    assert d["venue_canon_change"] is False
    assert d["automatic_promotion"] is False

def test_r43_does_not_silently_promote_open_candidates():
    a = load("profiles/KM_FAMILY_CURRENT_AUTHORITY_20261007_R43.json")
    for key in ("r41", "r42", "ohi_v24"):
        assert "NON-PRODUCTION" in a["noncurrent_candidate_lineages"][key]["status"]
        assert "NOT-INHERITED-AS-PRODUCTION" in a["noncurrent_candidate_lineages"][key]["status"]

def test_owner_utility_profile_requires_no_stagnation_and_semantic_purchase_separation():
    p = load("profiles/family_owner_utility_pfs_improvement_20261007_R1.json")
    assert "EVERY_RACE_LEARNS != EVERY_RACE_CHANGES_NOTHING" in p["principles"]
    assert "SEMANTIC_UNIVERSE != PURCHASED_UNIVERSE" in p["principles"]
    assert "UNKNOWN != MUST_PURCHASE" in p["principles"]
    assert "DOMINANT_PFS_LOSS_OWNER" in p["failure_localization"]["axes"]
    assert p["promotion"]["automatic_promotion"] is False

def test_runtime_is_connected_to_postresult_learning():
    post = (ROOT / "runtime/post_result_learning.py").read_text(encoding="utf-8")
    fast = (ROOT / "runtime/race_day_fast_reflection.py").read_text(encoding="utf-8")
    assert "build_pfs_improvement_assessment" in post
    assert 'review["pfs_improvement"]' in post
    assert '"dominant_pfs_loss_owner"' in post
    assert '"improvement_routes"' in post
    assert '"dominant_pfs_loss_owner"' in fast
    assert '"improvement_routes"' in fast
