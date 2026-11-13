"""R13: real historical NAR race card gives rider even when active row has none."""
from __future__ import annotations

from copy import deepcopy
import pytest
from runtime import formal_execution_orchestrator as o
from runtime.local_fnb_r13_rider_lineage import resolve_current_jockey

EID="LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"

@pytest.fixture(scope="module")
def archived_source():
    checkpoint=o.resolve_phase(EID,"SOURCE")
    assert checkpoint is not None
    return o._load_checkpoint_json(checkpoint,"source_receipt_envelope.json")["artifact"]

def test_r13_real_archived_nar_card_jockey_resolves_by_horse_number_and_sha(archived_source):
    horse=archived_source["official_runner_universe"]["runners"][0]
    rid=int(horse["horse_no"])
    observed=resolve_current_jockey(archived_source,rid)
    assert observed["horse_no"]==rid
    assert observed["current_jockey"].strip()
    assert observed["race_card_source_id"]
    assert len(observed["race_card_snapshot_sha256"])==64
    assert observed["result_source"]=="RECORDED_NAR_OFFICIAL_RACE_CARD"
    assert observed["issuer_signature_verified_here"] is False
    assert observed["independent_raw_bytes_reparsed_here"] is False

def test_r13_rejects_wrong_race_card_runner_name(archived_source):
    tampered=deepcopy(archived_source)
    horse=tampered["official_runner_universe"]["runners"][0]
    horse["name"]="他レースの別馬"
    with pytest.raises(ValueError,match="FNB_RECORDED_OFFICIAL_RIDER_HORSE_ID_MISMATCH"):
        resolve_current_jockey(tampered,int(horse["horse_no"]))

def test_r13_rejects_forged_embedded_active_rider(archived_source):
    tampered=deepcopy(archived_source)
    horse=tampered["official_runner_universe"]["runners"][0]
    horse["jockey"]="別騎手"
    with pytest.raises(ValueError,match="FNB_ACTIVE_ROW_VS_OFFICIAL_CARD_RIDER_CONFLICT"):
        resolve_current_jockey(tampered,int(horse["horse_no"]))

def test_r13_rejects_mismatched_companion_source_sha(archived_source):
    tampered=deepcopy(archived_source)
    card=tampered["normalized_evidence"]["race_card_tables"]
    card["snapshot_sha256"]="0"*64
    with pytest.raises(ValueError,match="FNB_RECORDED_RIDER_FROZEN_CARD_PROVENANCE_MISMATCH"):
        resolve_current_jockey(tampered,1)

@pytest.mark.parametrize("rid",[0,21,True,"1"])
def test_r13_invalid_horse_number_is_not_silently_coerced(archived_source,rid):
    with pytest.raises(ValueError,match="FNB_OFFICIAL_RIDER_HORSE_NUMBER_INVALID"):
        resolve_current_jockey(archived_source,rid)
