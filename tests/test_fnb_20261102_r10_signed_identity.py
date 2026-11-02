"""FNB R10 exact logical race versus execution identity acceptance.

A valid signed receipt uses KM-LOCAL-FNB-YYYYMMDD-RXX-LIVE-Rn while
the store pointer has LOCAL-...-EXEC. Never weaken other venue checks.
"""
from __future__ import annotations

import inspect
from copy import deepcopy

import pytest

from runtime import formal_execution_orchestrator as o
from runtime.local_fnb_r10_signed_race_identity import (
    expected_race_id, local_receipt_race_id,
)
from runtime import local_race_key_gate


EID="LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"
RID="KM-LOCAL-FNB-20261002-R04-LIVE-R1"


def test_real_signed_fnb_r04_receipt_race_id_is_not_execution_store_id():
    source=o.resolve_phase(EID,"SOURCE")
    formal=o.resolve_phase(EID,"FORMAL")
    assert source is not None and formal is not None
    signed=o._load_checkpoint_json(source,"source_receipt_envelope.json")
    frozen=o._load_checkpoint_json(formal,"final_receipt_envelope.json")
    temporal=o._load_checkpoint_json(formal,"final_before_post_verification.json")
    assert signed["receipt"]["race_id"]==RID
    assert frozen["receipt"]["race_id"]==RID
    assert temporal["race_id"]==RID
    assert temporal["execution_id"]==EID
    assert expected_race_id(EID,signed["artifact"])==RID
    assert signed["receipt"]["race_id"]!=EID


@pytest.mark.parametrize("invalid",[
    "LOCAL-KM-LOCAL-FNB-20261002-R13-LIVE-R1-EXEC",
    "LOCAL-KM-LOCAL-FNB-20261302-R04-LIVE-R1-EXEC",
    "LOCAL-KM-LOCAL-KAW-20261002-R04-LIVE-R1-EXEC",
    "LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R0-EXEC",
    "LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC/../FAKE",
])
def test_exact_execution_id_rejects_cross_venue_or_bad_revision(invalid):
    with pytest.raises(ValueError):
        expected_race_id(invalid)


def test_signed_source_context_cross_race_mismatch_is_hard_hold():
    src={"race_id":RID,"source_race_context":{
        "venue_id":"FNB","race_date":"2026/10/02","race_no":4}}
    assert expected_race_id(EID,src)==RID
    for field,value in [("venue_id","KAW"),("race_date","2026/10/03"),("race_no",5)]:
        forged=deepcopy(src)
        forged["source_race_context"][field]=value
        with pytest.raises(ValueError,match="FNB_SIGNED_SOURCE_RACE_IDENTITY_MISMATCH"):
            expected_race_id(EID,forged)


def test_non_fnb_legacy_record_identity_unchanged():
    eid="LOCAL-KM-LOCAL-KAW-20261016-R01-LIVE-R1-EXEC"
    assert local_receipt_race_id(eid)==eid
    assert local_receipt_race_id(eid,{})==eid


def test_all_3_existing_signed_gate_readers_use_canonical_fnb_race():
    rb=inspect.getsource(local_race_key_gate.readback_final)
    cert=inspect.getsource(local_race_key_gate.certify)
    terminal=inspect.getsource(local_race_key_gate.terminal_state)
    assert "signed_race_id = local_receipt_race_id(" in rb
    assert "receipt.get('race_id')!=signed_race_id" in rb
    assert "temporal.get('race_id')!=signed_race_id" in rb
    assert "signed_race_id = local_receipt_race_id(eid, artifact)" in cert
    assert 'str(temporal.get("race_id")) != signed_race_id' in cert
    assert "expected_signed_race_id = local_receipt_race_id(execution_id)" in terminal
    assert "final.get('receipt', {}).get('race_id') != expected_signed_race_id" in terminal
