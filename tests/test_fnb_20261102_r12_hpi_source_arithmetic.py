"""R12 independent HPI six-component 12-horse real-source arithmetic."""
from copy import deepcopy
import json
import sys
from pathlib import Path

from runtime import formal_execution_orchestrator as o
from runtime.local_fnb_r12_hpi_source_arithmetic import verify_hpi_six

ROOT=Path(__file__).resolve().parents[1]


def historical():
    sys.path.insert(0,str(ROOT/"runtime"))
    from local_fullnumerical_production import materialize_production
    eid="LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"
    phase=o.resolve_phase(eid,"SOURCE")
    assert phase is not None
    art=o._load_checkpoint_json(phase,"source_receipt_envelope.json")["artifact"]
    intent=json.loads((ROOT/"runtime/formal_intents/KM-LOCAL-FNB-20261002-R04-LIVE-R1.json").read_text())
    return materialize_production(art,intent,intent["required_indices"])


def test_r12_historical_real_fnb_12_horses_six_hpi_components():
    numerical=historical()
    grade=verify_hpi_six(numerical)
    assert grade["status"]=="HPI_SIX_PARSED_START_ARITHMETIC_VERIFIED",grade["errors"]
    assert grade["runners"]==12
    assert grade["expected_cells"]==72
    assert grade["checked_cells"]==72
    assert grade["six_of_63_not_all_63_independent"] is True
    assert grade["source_html_to_start_parser_independent"] is False


def test_r12_tampered_hpi_value_is_detected_independently():
    materialized=historical()
    tampered=deepcopy(materialized)
    key="recent_finish"
    record=tampered["runners"][0]["evidence_features"][key]
    old=record["score"]
    record["score"]=float(old)-1 if float(old)>2 else float(old)+1
    grade=verify_hpi_six(tampered)
    assert grade["status"]=="HPI_COMPONENT_ARITHMETIC_HOLD"
    assert any("FEATURE_SCORE_OR_MISSING_DIFFERS:" in e for e in grade["errors"])


def test_r12_tampered_neutral_missing_flag_is_detected():
    numerical=historical()
    tampered=deepcopy(numerical)
    record=tampered["runners"][0]["evidence_features"]["repeatability"]
    record["missing"]=not record["missing"]
    grade=verify_hpi_six(tampered)
    assert grade["status"]=="HPI_COMPONENT_ARITHMETIC_HOLD"
