import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))

from local_numerical_authority_gate import assess


def test_current_local_numerical_authority_is_not_ready_and_cannot_be_silently_upgraded():
    out=assess(
        ROOT/"mapping"/"local_evidence_feature_rule_registry_v1.0_20260922.json",
        ROOT/"mapping"/"local_base_index_mapping_registry_v1.0_20260922.json",
    )
    assert out["profile"]=="KM-LOCAL-NUMERICAL-AUTHORITY-GATE-v1.0-20260923"
    assert out["status"]=="NOT_READY"
    assert out["full_numerical_authority"] is False
    assert "EVIDENCE_RULE_REGISTRY_EXPLICITLY_NON_NUMERICAL" in out["reasons"]
    assert out["required_component_rule_count"]>0
    assert out["bound_component_rule_count"]==0
    assert len(out["missing_component_rules"])==out["required_component_rule_count"]


def test_synthetic_ready_requires_full_production_numerical_contract(tmp_path):
    # The positive case must exercise the ACTUAL cardinality contract,
    # not a one-component registry that merely binds its one declared rule.
    base = ["HPI-L", "CFIg-L", "RFIg-L", "BVIg-L",
            "JTI-L", "CSI-L", "BWI-L", "DCR", "NCI"]
    evidence = {
        "registry_id": "TEST-EVIDENCE",
        "status": "ACTIVE / PRODUCTION-NUMERICAL-AUTHORITY",
        "common_component_sets": {
            index: {f"feature{i}": 100 for i in range(7)} for index in base
        },
        "component_score_rules": {
            index: {
                f"feature{i}": {"rule_id": f"TEST-{index}-{i}", "transform": "x"}
                for i in range(7)
            } for index in base
        },
    }
    required = base + [f"Derived{i:02d}" for i in range(20)]
    mapping = {
        "mapping_id": "TEST-MAPPING",
        "status": "ACTIVE / PRODUCTION-NUMERICAL-AUTHORITY",
        "required_indices": required,
        "strict_numerical_terminal_policy": "CALCULATED_OR_RULED_NEUTRAL",
        "calibration_status": "UNCALIBRATED_RULE_BASED_PRODUCTION_NUMERICAL",
    }
    ep = tmp_path / "e.json"
    mp = tmp_path / "m.json"
    ep.write_text(json.dumps(evidence), encoding="utf-8")
    mp.write_text(json.dumps(mapping), encoding="utf-8")
    out = assess(ep, mp)
    assert out["status"] == "READY"
    assert out["full_numerical_authority"] is True
    assert out["component_index_count"] == 9
    assert out["required_component_rule_count"] == 63
    assert out["bound_component_rule_count"] == 63
    assert out["required_index_count"] == 29
    assert out["missing_component_rules"] == []
    assert not out["prediction_consumption_authorized"]
    assert not out["krs_consumption_authorized"]


def test_synthetic_partial_bound_registry_cannot_claim_full_ready(tmp_path):
    evidence={
      "registry_id":"TEST-EVIDENCE",
      "status":"ACTIVE / NUMERICAL",
      "common_component_sets":{"HPI-L":{"recent_finish":100}},
      "component_score_rules":{"HPI-L":{"recent_finish":{"rule_id":"TEST-R1","transform":"x"}}},
    }
    mapping={"registry_id":"TEST-MAPPING","status":"ACTIVE / NUMERICAL"}
    ep=tmp_path/"e.json"; mp=tmp_path/"m.json"
    ep.write_text(json.dumps(evidence),encoding="utf-8")
    mp.write_text(json.dumps(mapping),encoding="utf-8")
    out=assess(ep,mp)
    assert out["status"]=="NOT_READY"
    assert out["full_numerical_authority"] is False


def test_partial_component_registry_cannot_claim_full_63_rule_authority(tmp_path):
    """A 1/63 bound registry must never be certified as full Production numeric READY."""
    evidence = {
        "registry_id": "TEST-PARTIAL",
        "status": "ACTIVE / PRODUCTION-NUMERICAL-AUTHORITY",
        "common_component_sets": {
            "HPI-L": {"recent_finish": 100}
        },
        "component_score_rules": {
            "HPI-L": {
                "recent_finish": {"rule_id": "TEST-R1", "transform": "x"}
            }
        },
    }
    mapping = {
        "mapping_id": "TEST-MAPPING",
        "status": "ACTIVE / PRODUCTION-NUMERICAL-AUTHORITY",
        "required_indices": [f"I{i:02d}" for i in range(29)],
        "strict_numerical_terminal_policy": "CALCULATED_OR_RULED_NEUTRAL",
    }
    ep = tmp_path / "partial_e.json"
    mp = tmp_path / "partial_m.json"
    ep.write_text(json.dumps(evidence), encoding="utf-8")
    mp.write_text(json.dumps(mapping), encoding="utf-8")
    out = assess(ep, mp)
    assert out["required_component_rule_count"] == 1
    assert out["status"] == "NOT_READY"
    assert out["full_numerical_authority"] is False
    assert "FULL_63_COMPONENT_SET_INVALID" in out["reasons"]
