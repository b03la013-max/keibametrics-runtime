from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

from local_numerical_authority_gate import assess
from local_fullnumerical_production import (
    materialize_production,
    PROD_MAPPING_ID,
    PROD_REGISTRY_ID,
)


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_production_numerical_authority_is_ready_63_of_63_and_29_indices():
    a = assess()
    assert a["status"] == "READY"
    assert a["full_numerical_authority"] is True
    assert a["required_component_rule_count"] == 63
    assert a["bound_component_rule_count"] == 63
    assert a["required_index_count"] == 29
    assert len(a["required_indices"]) == 29
    assert a["strict_numeric_terminal_policy"] == "CALCULATED_OR_RULED_NEUTRAL"
    assert a["prediction_consumption_authorized"] is False
    assert a["krs_consumption_authorized"] is False
    assert a["ticket_consumption_authorized"] is False
    assert a["capital_consumption_authorized"] is False


def test_r1_mechanical_replay_closes_all_29_indices_without_hold():
    req = load("runtime/formal_intents/KM-LOCAL-OHI-20261007-R01-LIVE-R1.json")
    src = load(
        "runtime/executions/KM-LOCAL-OHI-20261007-R01-LIVE-R1/"
        "FORMAL/runs/37571596254-formal/source_receipt_envelope.json"
    )
    original_static = json.loads(json.dumps(req["static_prediction"], ensure_ascii=False))
    out = materialize_production(src["artifact"], req, req["required_indices"])

    cov = out["numeric_coverage"]
    assert cov["required_count"] == 12 * 29 == 348
    assert cov["terminalized_count"] == 348
    assert cov["numeric_value_count"] == 348
    assert cov["ruled_hold_count"] == 0
    assert cov["not_applicable_count"] == 0
    assert cov["unresolved_count"] == 0
    assert cov["calculated_count"] + cov["ruled_neutral_count"] == 348
    assert out["full_terminalization"] is True
    assert out["full_numerical_closure"] is True
    assert out["strict_full_numerical_ready"] is True
    assert out["local_mapping_registry"] == PROD_MAPPING_ID
    assert out["numerical_evidence_registry"] == PROD_REGISTRY_ID
    assert out["static_prediction"] == original_static

    for runner in out["runners"]:
        cc = runner["canonical_components"]
        assert len(cc) == 29
        for _, spec in cc.items():
            assert spec["terminal_status"] in {"CALCULATED", "RULED-NEUTRAL"}
            assert isinstance(spec["value"], (int, float))
            assert not isinstance(spec["value"], bool)
            assert math.isfinite(float(spec["value"]))
            assert 0 <= float(spec["value"]) <= 100
            assert spec["rule_id"]
            assert spec["evidence_refs"]
            assert spec["source_fact"]
            assert spec.get("production_authority") is True
            assert spec.get("candidate_only") is False
            assert spec.get("mapping_version") == PROD_MAPPING_ID


def test_rule_bound_neutral_is_numeric_but_never_mislabeled_calculated():
    req = load("runtime/formal_intents/KM-LOCAL-OHI-20261007-R01-LIVE-R1.json")
    src = load(
        "runtime/executions/KM-LOCAL-OHI-20261007-R01-LIVE-R1/"
        "FORMAL/runs/37571596254-formal/source_receipt_envelope.json"
    )
    out = materialize_production(src["artifact"], req, req["required_indices"])
    neutral = []
    for runner in out["runners"]:
        for name, spec in runner["canonical_components"].items():
            if spec["terminal_status"] == "RULED-NEUTRAL":
                neutral.append((runner["runner_id"], name, spec))
    assert neutral
    for _, _, spec in neutral:
        assert isinstance(spec["value"], (int, float))
        assert spec["observation_basis"] == "ALL-MISSING"
        assert spec["missingness_fraction"] >= 1.0


def test_production_materialization_does_not_authorize_downstream_policy():
    req = load("runtime/formal_intents/KM-LOCAL-OHI-20261007-R01-LIVE-R1.json")
    src = load(
        "runtime/executions/KM-LOCAL-OHI-20261007-R01-LIVE-R1/"
        "FORMAL/runs/37571596254-formal/source_receipt_envelope.json"
    )
    out = materialize_production(src["artifact"], req, req["required_indices"])
    auth = out["production_numerical_authority"]
    assert auth["prediction_consumption_authorized"] is False
    assert auth["krs_consumption_authorized"] is False
    assert auth["ticket_consumption_authorized"] is False
    assert auth["capital_consumption_authorized"] is False


def test_production_registry_contains_no_candidate_authority_in_rule_ids():
    reg = load("mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json")
    for per_index in reg["component_score_rules"].values():
        for rule in per_index.values():
            assert "CAND" not in rule["rule_id"].upper()
            assert rule["production_numerical_authority"] is True
            assert rule["prediction_authority"] is False
            assert rule["result_derived_allowed"] is False


def test_r44_declares_numerical_ready_without_prediction_or_krs_promotion():
    a = load("profiles/KM_FAMILY_CURRENT_AUTHORITY_20261008_R44.json")
    assert a["manifest_id"] == "KM-FAMILY-CURRENT-AUTHORITY-20261008-R44"
    assert "LOCAL-PRODUCTION-NUMERICAL-v1.0-READY" in a["status"]
    L = a["family_scoped_authority"]["LOCAL"]
    assert "NUMERICAL-AUTHORITY-READY" in L["status"]
    assert "63 REQUIRED COMPONENT RULES BOUND" in L["numerical_authority_status"]
    b = L["numerical_consumption_boundary"]
    assert b["prediction_authority"] is False
    assert b["krs_input_authority"] is False
    assert b["ticket_authority"] is False
    assert b["capital_authority"] is False
    d = a["r44_change_declaration"]
    assert d["production_numerical_execution_change"] is True
    assert d["production_prediction_change"] is False
    assert d["predictive_weight_change"] is False
    assert d["krs_input_policy_change"] is False
    assert d["mec_r3_change"] is False
    assert d["capital_policy_change"] is False
