"""Real historical Raw consumption and adversarial boundary checks; zero LIVE credit."""
from copy import deepcopy
from pathlib import Path
import json

import pytest

from runtime.local_fnb_observation_context import build_observation_packet
from runtime.local_fnb_venue_context_binding import canonical_sha256

ROOT = Path(__file__).resolve().parents[1]
RID = "KM-LOCAL-FNB-20261002-R04-LIVE-R1"


def archived():
    path = next((ROOT / "runtime/executions").glob("*FNB*20261002*R04*/SOURCE/runs/*/source_receipt_envelope.json"))
    envelope = json.loads(path.read_text())
    request = json.loads((ROOT / "runtime/formal_intents" / (RID + ".json")).read_text())
    return request, envelope


def rehash(envelope):
    source = envelope["artifact"]
    source["normalized_evidence_sha256"] = canonical_sha256(source["normalized_evidence"])
    source["source_snapshot_sha256"] = canonical_sha256({k: v for k, v in source.items() if k != "source_snapshot_sha256"})
    envelope["receipt"]["artifact_sha256"] = canonical_sha256(source)
    envelope["receipt_sha256"] = canonical_sha256(envelope["receipt"])


def compile(request, envelope):
    return build_observation_packet(request, envelope, generated_at="2026-11-03T11:30:00+09:00")


def test_real_fnb_raw_is_consumed_without_role_scope_or_oos_promotion():
    req, envelope = archived()
    before = deepcopy(envelope)
    got = compile(req, envelope)
    assert got["counts"] == {"active_runners": 12, "historical_fnb_starts": 35, "printed_position_sequences": 35}
    assert got["runners"][0]["historical_fnb_observations"][0]["printed_position_sequence"] == [8, 8, 7, 5]
    assert got["raw_to_normalized_tables_equal"] is True
    assert all(v["status"] == "UNKNOWN" for v in got["predictive_modules"].values())
    assert got["formal_context_ready"] is False and got["prestart_generation"] is False
    assert got["role_or_rank_changed"] is False and got["forward_oos_credit"] == 0
    assert envelope == before


def test_changed_normalized_table_even_with_fresh_artifact_hash_is_not_raw():
    req, envelope = archived()
    envelope["artifact"]["normalized_evidence"]["race_card_tables"]["value"][0].append(["false data"])
    rehash(envelope)
    with pytest.raises(ValueError, match="RAW_NORMALIZED_TABLE_MISMATCH"):
        compile(req, envelope)


def test_normalized_table_cannot_claim_another_source_id():
    req, envelope = archived()
    envelope["artifact"]["normalized_evidence"]["race_card_tables"]["source_id"] = "another-source"
    rehash(envelope)
    with pytest.raises(ValueError, match="RAW_NORMALIZED_TABLE_MISMATCH"):
        compile(req, envelope)


def test_actual_generation_clock_cannot_be_backdated_before_source():
    req, envelope = archived()
    with pytest.raises(ValueError, match="GENERATION_BEFORE_SOURCE_FREEZE"):
        build_observation_packet(req, envelope, generated_at="2026-09-01T10:00:00+09:00")


def test_wrong_venue_request_never_relabels_history():
    req, envelope = archived()
    req["venue_id"] = "KAW"
    with pytest.raises(ValueError, match="RACE_IDENTITY_MISMATCH"):
        compile(req, envelope)


def test_active_subset_cannot_discard_an_official_active_runner():
    req, envelope = archived()
    source = envelope["artifact"]
    key = "active_runner_universe" if source.get("active_runner_universe") else "official_runner_universe"
    source[key]["runners"] = source[key]["runners"][1:]
    rehash(envelope)
    with pytest.raises(ValueError, match="ACTIVE_STATUS_UNIVERSE_MISMATCH"):
        compile(req, envelope)


def test_raw_integrity_failure_stops_before_compilation():
    req, envelope = archived()
    envelope["artifact"]["sources"][0]["raw_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="SOURCE_INVALID"):
        compile(req, envelope)


def test_receipt_cannot_be_relabelled_as_different_phase_or_race():
    req, envelope = archived()
    for key, value in [("phase", "FINAL"), ("status", "FAIL"), ("race_id", "WRONG-RACE")]:
        changed = deepcopy(envelope)
        changed["receipt"][key] = value
        changed["receipt_sha256"] = canonical_sha256(changed["receipt"])
        with pytest.raises(ValueError, match="ENVELOPE_HASH_MISMATCH"):
            compile(req, changed)
