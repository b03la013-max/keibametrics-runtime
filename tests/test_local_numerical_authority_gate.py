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


def test_synthetic_fully_bound_registry_can_be_ready(tmp_path):
    evidence={
      "registry_id":"TEST-EVIDENCE",
      "status":"ACTIVE / NUMERICAL",
      "common_component_sets":{"HPI-L":{"recent_finish":100}},
      "component_score_rules":{
        "HPI-L":{
          "recent_finish":{"rule_id":"TEST-R1","transform":"score = clamp(0,100,x)"}
        }
      }
    }
    mapping={"registry_id":"TEST-MAPPING","status":"ACTIVE / NUMERICAL"}
    ep=tmp_path/"e.json"; mp=tmp_path/"m.json"
    ep.write_text(json.dumps(evidence),encoding="utf-8")
    mp.write_text(json.dumps(mapping),encoding="utf-8")
    out=assess(ep,mp)
    assert out["status"]=="READY"
    assert out["full_numerical_authority"] is True
    assert out["missing_component_rules"]==[]
