import copy
import pytest

from runtime.jra_execution_maturity_bridge import (
    JRAMaturityBridgeError,
    build_source_request,
    build_formal_request,
    verify_formal_request_binding,
)
from runtime.entry_transport_fallback import (
    EntryTransportFallbackError,
    build_legacy_formal_request,
    validate_fallback_request,
)

def intent():
    return {
        "family_id":"JRA",
        "execution_id":"KM-JRA-HSN-20990101-R01-SINGLE-R1",
        "race_id":"KM-JRA-HSN-20990101-R01",
        "venue_id":"HSN",
        "race_date":"2099-01-01",
        "race_no":1,
        "temporal_mode":"FORMAL-PRE-RACE",
        "prediction_cutoff":"2099-01-01T10:00:00+09:00",
        "scheduled_post_at":"2099-01-01T10:15:00+09:00",
        "external_dispatch_deadline_at":"2099-01-01T10:08:00+09:00",
        "current_authority_manifest":"KM-FAMILY-CURRENT-AUTHORITY-TEST",
        "jra_source":{"jra_meeting_key":"TESTMEETING"},
        "run_count":5000,
        "seed":2099010101,
        "static_prediction_frozen":True,
        "static_prediction":{"status":"FROZEN","ranking":[1,2,3]},
        "role_registry":[{"runner_id":"1","column":"W","status":"CORE"}],
        "pair_dispositions":[{"head":"1","second":"2","status":"PURCHASE"}],
        "third_dispositions":[{"head":"1","second":"2","third":"3","status":"PURCHASE"}],
        "available_bet_types":["EXACTA","TRIFECTA"],
        "capital_policy":{"mode":"RECOMMENDATION_ONLY"},
        "runners":[
            {"runner_id":"1","name":"A"},
            {"runner_id":"2","name":"B"},
            {"runner_id":"3","name":"C"},
        ],
        "required_indices":["HPI","SSI"],
    }

def envelope():
    return {
        "receipt_sha256":"a"*64,
        "receipt":{"runtime_revision":"KM-JRA-SOURCE-RUNTIME-v1.7-20260926"},
        "artifact":{
            "family_id":"JRA",
            "race_id":"KM-JRA-HSN-20990101-R01",
            "prediction_cutoff":"2099-01-01T10:00:00+09:00",
            "source_freeze_at":"2099-01-01T00:55:00+00:00",
            "source_snapshot_sha256":"b"*64,
            "formal_ready":True,
        },
    }

def test_build_source_request_uses_jra_not_local_source_semantics():
    s=build_source_request(intent())
    assert s["family_id"]=="JRA"
    assert s["jra_meeting_key"]=="TESTMEETING"
    assert s["execution_id"]==intent()["execution_id"]
    assert s["require_jra_horse_history"] is True
    assert "LOCAL" not in str(s)

def test_build_formal_binds_static_to_signed_source_and_semantic_basis():
    q=build_formal_request(intent(),envelope())
    static=q["static_prediction"]
    assert static["source_basis_receipt_sha256"]=="a"*64
    assert static["source_basis_snapshot_sha256"]=="b"*64
    assert static["source_checkpoint_manifest_sha256"]==q["source_checkpoint_manifest"]["sha256"]
    assert q["source_execution_id"]==intent()["execution_id"]
    assert q["formal_semantic_basis_sha256"]
    assert q["jra_maturity_bridge"]["production_prediction_change"] is False
    assert q["jra_maturity_bridge"]["production_numerical_change"] is False
    assert "LOCAL_PARAMETER_MAP" in q["jra_maturity_bridge"]["excluded_cross_family_material"]
    assert verify_formal_request_binding(q,envelope())["status"]=="PASS"

def test_formal_binding_rejects_semantic_tamper():
    q=build_formal_request(intent(),envelope())
    q["pair_dispositions"]=[]
    with pytest.raises(JRAMaturityBridgeError,match="FORMAL_SEMANTIC_HASH_MISMATCH"):
        verify_formal_request_binding(q,envelope())

def test_formal_binding_rejects_source_cutoff_mismatch():
    e=envelope()
    e["artifact"]["prediction_cutoff"]="2099-01-01T09:59:00+09:00"
    with pytest.raises(JRAMaturityBridgeError,match="SOURCE_CUTOFF_MISMATCH"):
        build_formal_request(intent(),e)

def test_jra_entry_fallback_preserves_semantics_and_uses_jra_formal_runner():
    q=build_formal_request(intent(),envelope())
    f=build_legacy_formal_request(q,primary_failure_code="PRIMARY_CONNECTOR_REJECTED")
    assert f["execution_id"]==q["execution_id"]
    assert f["source_execution_id"]==q["source_execution_id"]
    meta=f["entry_transport_fallback"]
    assert meta["family"]=="JRA"
    assert meta["fallback_root"]=="runtime/requests"
    assert meta["fallback_workflow"]==".github/workflows/km-formal-request-runner.yml"
    assert meta["external_safety_bypass"] is False
    assert validate_fallback_request(f)["status"]=="PASS"

def test_jra_entry_fallback_requires_signed_source_reference():
    q=intent()
    q.pop("jra_source")
    q["execution_phase"]="FORMAL"
    q["phase"]="FORMAL"
    with pytest.raises(EntryTransportFallbackError,match="JRA_SOURCE_EXECUTION_ID_REQUIRED"):
        build_legacy_formal_request(q)
