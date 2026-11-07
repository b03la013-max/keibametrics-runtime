"""R7 independent limited arithmetic check on real archived FNB 4R data.

Not an unknown-future trial. Independent Decimal implementation audits only
12/29 indices; official feature extraction and other 17 indices are NOT audited.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

from runtime import formal_execution_orchestrator as o
from runtime.local_fnb_r7_arithmetic_witness import verify_arithmetic

ROOT=Path(__file__).resolve().parents[1]
EID="LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"


def _real_materialized():
    sys.path.insert(0,str(ROOT/"runtime"))
    from local_fullnumerical_production import materialize_production
    source=o.resolve_phase(EID,"SOURCE")
    assert source is not None
    env=o._load_checkpoint_json(source,"source_receipt_envelope.json")
    assert env["receipt"]["status"] == "SOURCE_FROZEN"
    intent=json.loads((ROOT/"runtime/formal_intents"/
                       "KM-LOCAL-FNB-20261002-R04-LIVE-R1.json").read_text())
    return materialize_production(env["artifact"],intent,intent["required_indices"])


def _registries():
    a=json.loads((ROOT/"mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json").read_text())
    b=json.loads((ROOT/"mapping/local_full_numerical_mapping_v1.0_production_20261008.json").read_text())
    return a,b


def test_real_fnb_r04_144_independently_recalculated_from_stored_features():
    mat=_real_materialized()
    reg,mp=_registries()
    proof=verify_arithmetic(mat,reg,mp)
    assert proof["status"] == "12_OF_29_INDEPENDENT_ARITHMETIC_VERIFIED", proof["issues"]
    assert proof["runners"] == 12
    assert proof["checked_cells"] == 12*12
    assert proof["expected_checked_cells"] == 12*12
    assert proof["full_29_arithmetic_verified"] is False
    assert proof["source_to_feature_transform_independently_verified"] is False
    assert proof["consumer_authorized"] is False
    assert proof["unknown_future_oos_registered"] is False


def test_independent_decimal_witness_detects_silent_base_score_tamper():
    mat=_real_materialized()
    reg,mp=_registries()
    bad=copy.deepcopy(mat)
    idx="HPI-L"
    value=bad["runners"][0]["canonical_components"][idx]["value"]
    bad["runners"][0]["canonical_components"][idx]["value"]=min(100.0,float(value)+1.0)
    proof=verify_arithmetic(bad,reg,mp)
    assert proof["status"] == "PARTIAL_ARITHMETIC_HOLD"
    assert any("BASE_ARITHMETIC_MISMATCH" in x for x in proof["issues"])


def test_independent_decimal_witness_detects_derived_tpi_sri_f3s_tamper():
    mat=_real_materialized()
    reg,mp=_registries()
    for idx in ("TPI-L","SRI-L","F3S-L"):
        bad=copy.deepcopy(mat)
        v=float(bad["runners"][0]["canonical_components"][idx]["value"])
        bad["runners"][0]["canonical_components"][idx]["value"]=v-0.9 if v>0.9 else v+0.9
        proof=verify_arithmetic(bad,reg,mp)
        assert proof["status"]=="PARTIAL_ARITHMETIC_HOLD"
        assert any(idx.split("-")[0] in x for x in proof["issues"]),proof["issues"]


def test_arithmetic_witness_cannot_grant_29_index_validation():
    reg,mp=_registries()
    proof=verify_arithmetic({"runners":[]},reg,mp)
    assert proof["checked_cells"]==0
    assert proof["full_29_arithmetic_verified"] is False
    assert proof["consumer_authorized"] is False
    assert proof["status"] == "PARTIAL_ARITHMETIC_HOLD"
