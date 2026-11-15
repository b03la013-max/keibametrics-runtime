"""R8: historical real FNB SOURCE, full recorded-feature arithmetic test."""
import json
import sys
from pathlib import Path

from runtime import formal_execution_orchestrator as o
from runtime.local_fnb_r8_arithmetic_29 import verify_29


def test_r8_fnb_real_source_348_arithmetic_cells():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/"runtime"))
    from local_fullnumerical_production import materialize_production
    eid="LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"
    phase=o.resolve_phase(eid,"SOURCE")
    assert phase is not None
    env=o._load_checkpoint_json(phase,"source_receipt_envelope.json")
    intent=json.loads((root/"runtime/formal_intents/KM-LOCAL-FNB-20261002-R04-LIVE-R1.json").read_text())
    out=materialize_production(env["artifact"],intent,intent["required_indices"])
    registry=json.loads((root/"mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json").read_text())
    mapping=json.loads((root/"mapping/local_full_numerical_mapping_v1.0_production_20261008.json").read_text())
    audit=verify_29(out,registry,mapping)
    assert audit["status"]=="29_OF_29_RECORDED_FEATURE_ARITHMETIC_PASS",audit["issues"]
    assert audit["basic_12_index_cells"]==144
    assert audit["extra_17_index_cells"]==204
    assert audit["checked_cells"]==348
    assert audit["source_to_feature_independent_recalculation"]=="NOT_PERFORMED"
    assert audit["prediction_krs_ticket_capital_authorized"] is False
