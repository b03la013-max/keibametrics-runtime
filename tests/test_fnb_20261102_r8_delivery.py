"""Legacy FNB Signed FINAL must not pass dual Owner delivery checks."""
from runtime import formal_execution_orchestrator as o
from runtime.local_fnb_r8_delivery_completeness import audit_presentation


def test_r8_single_owner_final_is_incomplete_for_dual_owner_delivery():
    eid="LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"
    phase=o.resolve_phase(eid,"FORMAL")
    assert phase is not None
    saved=o._load_checkpoint_json(phase,"final_receipt_envelope.json")
    artifact=saved["artifact"]
    grade=audit_presentation(artifact,[str(i) for i in range(1,13)])
    assert grade["status"]=="DELIVERY_PRESENTATION_INCOMPLETE"
    assert "DUAL_OWNER_SIX_METHODS_MISSING" in grade["missing"]
    assert "ALL_RUNNERS_29_INDICES_NOT_MATERIALIZED" in grade["missing"]
    assert grade["prestart_delivery_pass"] is False
    assert grade["recipient_ack"] is False
