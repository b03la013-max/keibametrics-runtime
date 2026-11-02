"""Synthetic negative/positive receipts: never upload actual horse/source bytes."""
import hashlib
import json
from datetime import datetime, timezone

import pytest
from runtime.local_fnb_r19_chat_readback import parse_intent, readback

NOW=datetime(2026,11,2,7,20,tzinfo=timezone.utc)
RACE="KM-LOCAL-FNB-20261102-R04-PRIVATE-R1"

def fixture(tmp_path, **changes):
    folder=tmp_path/RACE
    folder.mkdir()
    content=("# SYNTHETIC-ONLY\n## BASELINE\n### EXACTA\n### TRIO\n"
             "### TRIFECTA\n## CANDIDATE\n### EXACTA\n### TRIO\n"
             "### TRIFECTA\n## 全馬29指数\n未使用 0円\n")
    (folder/"FULL_ALL_HORSES_BC_SIX_METHODS.md").write_text(content)
    receipt={"race_id":RACE,
        "status":"FULL_PRIVATE_PRESENTATION_READY_DELIVERY_ACK_UNVERIFIED",
        "classification":"POSTCUTOFF_DIAGNOSTIC_ONLY",
        "owner_six_methods_proven":True,
        "two_owners_5000_seed1_executed":True,
        "all29_source_feature_receipt_verified":True,
        "complete_private_full_horse_delivery_presentation":{
            "status":"FULL_PRESENTATION_READY_RECIPIENT_ACK_UNVERIFIED",
            "private_body_roundtrip_verified":True,
            "two_owners":["BASELINE","CANDIDATE"],
            "six_alternative_methods":True,
            "all_horses":9,
            "all_29_index_cells":261,
            "body_filename":"FULL_ALL_HORSES_BC_SIX_METHODS.md",
            "full_body_sha256":hashlib.sha256(content.encode()).hexdigest()}}
    receipt.update(changes)
    (folder/"private_pipeline_checkpoint.json").write_text(json.dumps(receipt))
    return folder

def test_single_race_and_explicit_date():
    assert parse_intent("船橋4Rのケイバメトリクス調査",NOW)=={
        "venue_id":"FNB","race_date":"2026-11-02","race_no":4}
    assert parse_intent("2026年11月2日 FNB第4レース",NOW)["race_no"]==4

@pytest.mark.parametrize("query",["浦和4R","船橋4Rと船橋5R",
    "船橋4R 川崎3R","2026-11-02 2026-11-03 船橋4R","明日 船橋4R"])
def test_ambiguous_race_fails(query):
    with pytest.raises(ValueError):
        parse_intent(query,NOW)

def test_missing_is_not_no_bet(tmp_path):
    r=readback("船橋4R",tmp_path,NOW)
    assert r["status"]=="FULL_DELIVERY_NOT_COMPLETED"
    assert r["computed_no_bet"] is False
    assert r["recipient_delivery_ack"] is False

def test_original_is_read_back_but_not_signed(tmp_path):
    fixture(tmp_path)
    r=readback("船橋4R",tmp_path,NOW)
    assert r["status"]=="VERIFIED_FROZEN_PRIVATE_BODY_READY_TO_RENDER"
    assert r["index_cell_count"]==261
    assert not r["formal_signed_final_proven"]
    assert not r["recipient_delivery_ack"]
    assert "## BASELINE" in r["body"]

def test_corruption_fails_closed(tmp_path):
    folder=fixture(tmp_path)
    (folder/"FULL_ALL_HORSES_BC_SIX_METHODS.md").write_text("tampered")
    assert readback("船橋4R",tmp_path,NOW)["reason"]=="FNB_FULL_BODY_SHA_MISMATCH"

def test_race_revision_collision_does_not_fall_back(tmp_path):
    fixture(tmp_path)
    (tmp_path/"KM-LOCAL-FNB-20261102-R04-PRIVATE-R2").mkdir()
    assert readback("船橋4R",tmp_path,NOW)["reason"]=="FNB_MULTIPLE_REVISIONS_RECONCILIATION_REQUIRED"

def test_numeric_only_is_not_complete(tmp_path):
    fixture(tmp_path,status="NUMERIC_ONLY_FROZEN_OWNER_PACKETS_MISSING")
    r=readback("船橋4R",tmp_path,NOW)
    assert r["status"]=="FULL_DELIVERY_NOT_COMPLETED"

def test_260_not_261_is_rejected(tmp_path):
    folder=fixture(tmp_path)
    p=folder/"private_pipeline_checkpoint.json"
    r=json.loads(p.read_text())
    r["complete_private_full_horse_delivery_presentation"]["all_29_index_cells"]=260
    p.write_text(json.dumps(r))
    assert readback("船橋4R",tmp_path,NOW)["reason"]=="FNB_ALL_HORSE_29_CELL_COUNT_INVALID"
