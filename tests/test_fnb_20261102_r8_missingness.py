"""R8: independent missingness accounting on archived FNB full29 data."""
import json
import sys
from pathlib import Path
from runtime import formal_execution_orchestrator as o
from runtime.local_fnb_r8_missingness_census import census


def test_fnb_r8_36_neutral_cells_are_explained_not_treated_as_weakness():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/"runtime"))
    from local_fullnumerical_production import materialize_production
    eid="LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"
    phase=o.resolve_phase(eid,"SOURCE")
    assert phase is not None
    artifact=o._load_checkpoint_json(phase,"source_receipt_envelope.json")["artifact"]
    intent=json.loads((root/"runtime/formal_intents/KM-LOCAL-FNB-20261002-R04-LIVE-R1.json").read_text())
    numerical=materialize_production(artifact,intent,intent["required_indices"])
    grade=census(numerical)
    assert grade["runner_count"]==12
    assert grade["cells"]==348
    assert grade["calculated"]==312
    assert grade["ruled_neutral"]==36
    assert sum(x.get("RULED-NEUTRAL",0) for x in grade["index_counts"].values())==36
    assert grade["neutral_is_not_low_ability"] is True
    assert grade["source_to_feature_independently_verified"] is False
