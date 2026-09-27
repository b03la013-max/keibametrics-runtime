import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from family_authority_guard import (
    FamilyAuthorityError,
    selftest,
    validate_request_context,
)

AUTH="profiles/KM_FAMILY_CURRENT_AUTHORITY_20260928_R31.json"


def authority_id():
    return json.load(open(AUTH, encoding="utf-8"))["manifest_id"]


def base(family):
    return {
        "family_id": family,
        "temporal_mode": "FORMAL-PRE-RACE",
        "current_authority_manifest": authority_id(),
    }


def test_selftest_r31():
    report=selftest(AUTH)
    assert report["status"]=="PASS"
    assert report["jra"]=="PASS"
    assert report["local"]=="PASS"
    assert report["ban"]=="EXPECTED_BLOCKED"


def test_cross_family_parameter_map_is_rejected():
    req=base("JRA")
    req["parameter_map_authority"]="parameter_map-BAN Rev.13"
    with pytest.raises(FamilyAuthorityError, match="CROSS_FAMILY_AUTHORITY_REUSE"):
        validate_request_context(req, authority_path=AUTH)


def test_common_scope_cannot_be_reclaimed_by_venue():
    req=base("LOCAL")
    req["authority_scope_bindings"]={"MEC":"VENUE_SPECIFIC"}
    with pytest.raises(FamilyAuthorityError, match="AUTHORITY_SCOPE_OWNER_MISMATCH"):
        validate_request_context(req, authority_path=AUTH)


def test_candidate_parameter_cannot_enter_production_formal():
    req=base("JRA")
    req["parameter_map_authority"]="JRA-PARAMETER-CANDIDATE"
    with pytest.raises(FamilyAuthorityError, match="NON_PRODUCTION_AUTHORITY_IN_PRODUCTION_SCOPE"):
        validate_request_context(req, authority_path=AUTH)


def test_candidate_parameter_allowed_for_acceptance_only_same_family():
    req=base("JRA")
    req["acceptance_only"]=True
    req["parameter_map_authority"]="JRA-PARAMETER-CANDIDATE"
    report=validate_request_context(req, authority_path=AUTH)
    assert report["production_formal"] is False
    assert report["status"]=="PASS"


def test_ban_production_formal_stays_blocked_until_runtime_verified():
    with pytest.raises(FamilyAuthorityError, match="FAMILY_RUNTIME_BLOCKED"):
        validate_request_context(base("BAN"), authority_path=AUTH)


def test_r31_keeps_production_numerics_frozen():
    ca=json.load(open(AUTH, encoding="utf-8"))
    s=ca["supersession_declaration"]
    assert s["predictive_model_formula_change"] is False
    assert s["base_index_weight_change"] is False
    assert s["derived_index_formula_change"] is False
    assert s["krs_engine_physics_change"] is False
    assert s["mec_r3_policy_change"] is False
    assert s["capital_policy_change"] is False
    assert s["venue_production_canon_change"] is False
    assert s["candidate_to_production_promotion"] is False
    assert s["production_numerical_change"] is False
    assert s["automatic_promotion"] is False
