import copy
import pytest
from runtime.entry_transport_fallback import (
    EntryTransportFallbackError,
    build_legacy_formal_request,
    semantic_sha256,
    validate_fallback_request,
)

def intent():
    return {
        "family_id": "LOCAL",
        "execution_id": "LOCAL-FNB-TEST-EXEC",
        "execution_phase": "AUTO",
        "phase": "AUTO",
        "race_id": "KM-LOCAL-FNB-TEST-R1",
        "venue_id": "FNB",
        "race_date": "2099-01-01",
        "race_no": 1,
        "prediction_cutoff": "2099-01-01T12:00:00+09:00",
        "scheduled_post_at": "2099-01-01T12:10:00+09:00",
        "runners": [{"runner_id":"1","name":"A"},{"runner_id":"2","name":"B"}],
        "required_indices": ["HPI-L"],
        "run_count": 5000,
        "seed": 1,
        "static_prediction_frozen": True,
        "static_prediction": {"ranking":["1","2"],"status":"FROZEN"},
        "role_registry": [
            {"runner_id":"1","column":"W","status":"CORE"},
            {"runner_id":"2","column":"P2","status":"CORE"},
        ],
        "pair_dispositions": [
            {"head":"1","second":"2","status":"PURCHASE","reason":"TEST"}
        ],
        "third_dispositions": [],
        "available_bet_types": ["EXACTA"],
        "capital_policy": {"mode":"RECOMMENDATION_ONLY"},
    }

def test_build_fallback_preserves_semantics_and_execution_id():
    src=intent()
    out=build_legacy_formal_request(src, primary_failure_code="CONNECTOR_REJECTED")
    assert out["execution_id"]==src["execution_id"]
    assert out["execution_phase"]=="FORMAL"
    assert out["phase"]=="FORMAL"
    assert out["static_prediction"]==src["static_prediction"]
    assert out["role_registry"]==src["role_registry"]
    assert out["pair_dispositions"]==src["pair_dispositions"]
    assert out["entry_transport_fallback"]["semantic_sha256"]==semantic_sha256(src)
    assert validate_fallback_request(out)["status"]=="PASS"

def test_fallback_detects_semantic_loss():
    out=build_legacy_formal_request(intent())
    out["pair_dispositions"]=[]
    with pytest.raises(EntryTransportFallbackError, match="SEMANTIC_HASH_MISMATCH"):
        validate_fallback_request(out)

def test_fallback_forbids_safety_bypass():
    out=build_legacy_formal_request(intent())
    out["entry_transport_fallback"]["external_safety_bypass"]=True
    with pytest.raises(EntryTransportFallbackError, match="SAFETY_BYPASS_FORBIDDEN"):
        validate_fallback_request(out)

def test_fallback_requires_frozen_static():
    src=intent()
    src["static_prediction_frozen"]=False
    with pytest.raises(EntryTransportFallbackError, match="STATIC_FREEZE_REQUIRED"):
        build_legacy_formal_request(src)
