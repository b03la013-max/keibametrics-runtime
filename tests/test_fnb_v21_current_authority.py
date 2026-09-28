import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from family_authority_guard import selftest

AUTH="profiles/KM_FAMILY_CURRENT_AUTHORITY_20260928_R32.json"
FNB="profiles/fnb_venue_canon_20260928_v2.1.json"
ROUTE="profiles/venue_chat_routes_20260928_R32.json"
SUITE="profiles/KM_LOCAL_SUITE_MANIFEST_20260928_R11.json"
RUNTIME="profiles/family_runtime_contracts_20260928_R24.json"
GATEWAY="profiles/current_execution_gateway.json"
SCOPE="profiles/family_scope_ownership_20260928_R1.json"


def load(path):
    return json.load(open(path,encoding="utf-8"))


def test_fnb_v21_is_current_and_r31_aligned():
    a=load(AUTH); f=load(FNB); r=load(ROUTE); s=load(SUITE); rt=load(RUNTIME); g=load(GATEWAY)
    assert a["manifest_id"]=="KM-FAMILY-CURRENT-AUTHORITY-20260928-R32"
    assert a["predecessor"]=="KM-FAMILY-CURRENT-AUTHORITY-20260928-R31"
    assert a["venue_canon_current_decisions"]["FNB"]["production"]=="船橋競馬攻略条項 v2.1-FNB"
    assert a["venue_canon_current_decisions"]["FNB"]["profile"]==f["profile_id"]
    assert r["profile_id"]=="KM-VENUE-CHAT-FORMAL-ROUTING-20260928-R32"
    fnb_route=next(x for x in r["venues"] if x["venue_id"]=="FNB")
    assert fnb_route["venue_canon_profile"]==f["profile_id"]
    assert fnb_route["first_day_temporal_bootstrap"]=="ACTIVE"
    assert s["manifest_id"]=="KM-LOCAL-SUITE-MANIFEST-20260928-R11"
    assert s["family_current_authority"]==a["manifest_id"]
    assert s["venue_routing"]==r["profile_id"]
    assert s["runtime"]["contract"]==rt["profile_id"]
    assert rt["profile_id"]=="KM-FAMILY-RUNTIME-CONTRACTS-20260928-R24"
    assert rt["families"]["LOCAL"]["suite_manifest"]==s["manifest_id"]
    assert rt["families"]["LOCAL"]["venue_routing"]==r["profile_id"]
    assert g["profile_id"]=="KM-LOCAL-EXECUTION-GATEWAY-v1.3-20260928"
    assert g["parent_current_authority"]==a["manifest_id"]
    assert g["venue_routing"]==r["profile_id"]
    assert g["family_runtime_contracts"]=="profiles/family_runtime_contracts_20260928_R24.json"


def test_fnb_v21_owns_venue_prediction_only():
    f=load(FNB); scope=load(SCOPE)
    allowed=set(scope["venue_allowed_scopes"])
    assert set(f["venue_owned_scopes"]) <= allowed
    assert "TICKET_CONSTRUCTION" in f["common_owned_scopes"]
    assert "CAPITAL" in f["common_owned_scopes"]
    assert "RECEIPT_VERIFICATION" in f["common_owned_scopes"]
    assert "PFS_MEASUREMENT" in f["common_owned_scopes"]
    assert "NO_VENUE_OWNED_TICKET_CONSTRUCTION" in f["hard_prohibitions"]
    assert "NO_VENUE_OWNED_CAPITAL_POLICY" in f["hard_prohibitions"]
    assert "NO_VENUE_OWNED_RUNTIME_OR_RECEIPT_AUTHORITY" in f["hard_prohibitions"]


def test_fnb_v21_preserves_v20_numerical_freeze():
    f=load(FNB); a=load(AUTH); s=load(SUITE); g=load(GATEWAY)
    assert f["predictive_behavior_change"] is False
    assert f["numerical_change"] is False
    freeze=f["production_freeze"]
    assert freeze["index_formulas"]=="UNCHANGED"
    assert freeze["index_weights"]=="UNCHANGED"
    assert freeze["krs_engine_physics"]=="UNCHANGED"
    assert freeze["parameter_map"]=="UNCHANGED"
    assert freeze["production_mec"]=="MEC-R3 UNCHANGED"
    assert freeze["capital_policy"]=="UNCHANGED"
    sup=a["supersession_declaration"]
    assert sup["predictive_model_formula_change"] is False
    assert sup["production_numerical_change"] is False
    assert sup["krs_engine_physics_change"] is False
    assert sup["mec_r3_policy_change"] is False
    assert sup["capital_policy_change"] is False
    assert s["production_numeric_suite"]["numerical_change"] is False
    assert g["policy"]["production_numerical_policy_changed"] is False
    assert g["policy"]["production_mec_policy_changed"] is False
    assert g["policy"]["capital_policy_changed"] is False


def test_first_day_temporal_bootstrap_and_oos_are_fail_closed():
    f=load(FNB)
    b=f["first_day_temporal_bootstrap"]
    assert b["pre_race_1_track_state"]=="UNVERIFIED_CURRENT / HISTORICAL_PRIOR_ONLY"
    assert b["future_result_leakage_forbidden"] is True
    assert f["current_week_oos"]["automatic_promotion"] is False
    assert "NO_HISTORICAL_GCI_AS_CURRENT_GCI" in f["hard_prohibitions"]
    assert "NO_RESULT_DERIVED_PRE_RACE_FEATURE" in f["hard_prohibitions"]


def test_legacy_execution_and_capital_are_reinterpreted_not_deleted():
    f=load(FNB)
    legacy=f["legacy_reinterpretation"]
    assert legacy["Execution Compiler LOCAL v1.0.0"]["current_status"].startswith("COMPATIBILITY_SOURCE")
    assert legacy["Three-Layer Capital Architecture-FNB"]["current_status"]=="VENUE DIAGNOSTIC INPUT ONLY"
    assert legacy["Adaptive Capital Width v3-FNB"]["current_owner"]=="COMMON_FAMILY MEC + CAPITAL"
    assert legacy["Priority Cross-Layer Consistency v2-FNB"]["current_status"].startswith("REGRESSION INVARIANT")


def test_family_authority_guard_resolves_r32():
    report=selftest(AUTH)
    assert report["status"]=="PASS"
    assert report["authority"]=="KM-FAMILY-CURRENT-AUTHORITY-20260928-R32"
    assert report["jra"]=="PASS"
    assert report["local"]=="PASS"
    assert report["ban"]=="EXPECTED_BLOCKED"
