"""R9 63 component evidence quality checks on the archived FNB signed store.

This suite never upgrades SOURCE to licensed current input or numerical
predictions to approved downstream consumers.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

from runtime import formal_execution_orchestrator as o
from runtime.local_fnb_r9_evidence_63 import audit_63

ROOT=Path(__file__).resolve().parents[1]
EID="LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"


@pytest.fixture(scope="module")
def real():
    sys.path.insert(0,str(ROOT/"runtime"))
    from local_fullnumerical_production import materialize_production
    saved=o.resolve_phase(EID,"SOURCE")
    assert saved is not None
    envelope=o._load_checkpoint_json(saved,"source_receipt_envelope.json")
    intent=json.loads((ROOT/"runtime/formal_intents/KM-LOCAL-FNB-20261002-R04-LIVE-R1.json").read_text())
    registry=json.loads((ROOT/"mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json").read_text())
    mat=materialize_production(envelope["artifact"],intent,intent["required_indices"])
    return mat,registry,intent,envelope["artifact"]


def test_r9_real_fnb_756_component_records_have_source_lineage(real):
    m,reg,intent,src=real
    result=audit_63(m,reg,intent,src)
    assert result["status"]=="ALL_63_COMPONENT_RECORDS_LINEAGE_VERIFIED",result["issues"]
    assert result["runner_count"]==12
    assert result["expected_component_records"]==756
    assert result["recorded_components_verified"]==756
    assert result["missing_component_records"]==274
    assert result["observed_component_records"]==482
    assert sum(v["missing_component_records"] for v in
               result["per_index_evidence_quality"].values())==274
    assert result["calculated_index_does_not_mean_all_components_observed"] is True
    assert result["missing_not_weak"] is True
    assert result["source_to_feature_transform_arithmetic_independently_verified"] is False


@pytest.mark.parametrize("variant",[
    "component_missing", "rule_forged", "timestamp_post_cutoff",
    "missing_score_forged", "source_ref_forged", "runner_universe_removed"])
def test_r9_evidence_component_tamper_fails_closed(real,variant):
    mat,registry,intent,source=real
    mat=deepcopy(mat)
    row=mat["runners"][0]
    comp="recent_finish"
    if variant=="component_missing":
        row["evidence_features"].pop(comp)
    elif variant=="rule_forged":
        row["evidence_features"][comp]["rule_id"]="FAKE_RULE"
    elif variant=="timestamp_post_cutoff":
        row["evidence_features"][comp]["source_timestamp"]="2026-10-02T17:30:00+09:00"
    elif variant=="missing_score_forged":
        row["evidence_features"][comp]["missing"]=True
        row["evidence_features"][comp]["score"]=81.0
    elif variant=="source_ref_forged":
        row["evidence_features"][comp]["evidence_refs"]=[]
    elif variant=="runner_universe_removed":
        mat["runners"].pop()
    result=audit_63(mat,registry,intent,source)
    assert result["status"]=="FEATURE_LINEAGE_HOLD",result
    assert result["issues"],variant


def test_r9_cross_race_signed_source_is_not_usable_for_feature_proof(real):
    m,reg,intent,src=real
    altered=deepcopy(intent)
    altered["race_id"]="KM-LOCAL-FNB-20261002-R05-LIVE-R1"
    result=audit_63(m,reg,altered,src)
    assert result["status"]=="FEATURE_LINEAGE_HOLD"
    assert "FNB_SOURCE_OR_INTENT_RACE_IDENTITY_INVALID" in result["issues"]
