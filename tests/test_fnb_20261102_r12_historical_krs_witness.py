"""R12 KRS capability independent historical receipt verification, no FNB LIVE claim."""
from copy import deepcopy
import base64
import json
from pathlib import Path

import pytest

from runtime import formal_execution_orchestrator as o
from runtime.local_fnb_r12_historical_krs_witness import (
    EID,RID,KEY_PATH,attest_archived_krs,verify_envelope)


ROOT=Path(__file__).resolve().parents[1]


def test_r12_actual_krs_signed_chain_four_phases_5000_not_seed_one():
    receipt=attest_archived_krs()
    assert receipt["status"]=="ARCHIVED_FNB_R04_KRS_SIGNED_LINEAGE_VERIFIED"
    assert receipt["signed_phase_envelopes_verified"]==[
        "SOURCE","PRE_KRS","KRS_RUN","FINAL"]
    assert receipt["actual_run_count"]==5000
    assert receipt["requested_run_count"]==5000
    assert receipt["actual_seed"]==2026100204
    assert receipt["seed_is_one"] is False
    assert receipt["independent_baseline_and_candidate_fixed_owner_receipts_proven"] is False
    assert receipt["new_20261102_krs_executed"] is False


@pytest.fixture(scope="module")
def archived_krs():
    phase=o.resolve_phase(EID,"FORMAL")
    signed=o._load_checkpoint_json(phase,"krs_receipt_envelope.json")
    gateway=json.loads((ROOT/"profiles/current_execution_gateway.json").read_text())["families"]["LOCAL"]
    health=json.loads((ROOT/KEY_PATH).read_text())
    public=base64.b64decode(health["receipt_public_key_b64"],validate=True)
    return signed,gateway,public


def test_r12_current_historical_krs_envelope_cryptographically_verifiable(archived_krs):
    signed,gateway,public=archived_krs
    a=verify_envelope(signed,race_id=RID,phase="KRS_RUN",
                      status="EXECUTED",public=public,cfg=gateway)
    assert a["actual_run_count"]==5000


@pytest.mark.parametrize("tamper",["seed","count","wrong_race","no_signature"])
def test_r12_forged_krs_seed_or_count_or_race_does_not_pass(archived_krs,tamper):
    signed,gateway,public=archived_krs
    signed=deepcopy(signed)
    if tamper=="seed":
        signed["artifact"]["seed"]=1
    elif tamper=="count":
        signed["artifact"]["actual_run_count"]=4999
    elif tamper=="wrong_race":
        signed["receipt"]["race_id"]="KM-LOCAL-FNB-20261002-R05-LIVE-R1"
    elif tamper=="no_signature":
        signed["signature"]="AAAA"
    with pytest.raises((ValueError,Exception)):
        verify_envelope(signed,race_id=RID,phase="KRS_RUN",
                        status="EXECUTED",public=public,cfg=gateway)
