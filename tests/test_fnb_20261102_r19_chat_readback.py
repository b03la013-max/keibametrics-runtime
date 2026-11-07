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

def test_heading_only_stub_is_not_complete_even_with_true_flags(tmp_path):
    fixture(tmp_path)
    r=readback("船橋4R",tmp_path,NOW)
    assert r["status"]=="FULL_DELIVERY_NOT_COMPLETED"
    assert r["reason"]=="FNB_SAVED_PRESENTATION_INPUT_PROOF_MISSING"
    assert not r["computed_no_bet"]
    assert not r["recipient_delivery_ack"]
    assert "body" not in r

def complete_fixture(tmp_path):
    # Explicitly synthetic content; no real Engine run or SOURCE signature.
    from test_fnb_20261102_r18_full_private_delivery import prepare_ticket, RID
    from runtime.local_fnb_r18_full_private_delivery import verified_full_delivery
    root,sem,dual,port=prepare_ticket(tmp_path)
    folder=root/RID
    for owner in ("BASELINE","CANDIDATE"):
        raw=json.dumps({"prediction_id":RID+"-"+owner,"synthetic_test":True}).encode()
        (folder/(owner+"_krs_input.json")).write_bytes(raw)
        dual["owners"][owner]["candidate_or_baseline_input_sha256"]=hashlib.sha256(raw).hexdigest()
    for name,obj in (("private_dual_krs_receipt.json",dual),
                     ("frozen_owner_semantics.json",sem),
                     ("six_alternative_method_portfolios.json",port["owners"])):
        (folder/name).write_text(json.dumps(obj,ensure_ascii=False))
    grade=verified_full_delivery(race_id=RID,private_root=root,semantics=sem,
                                portfolios=port["owners"],diagnostic_only=True)
    names=["numerical_materialization.json","private_dual_krs_receipt.json",
           "frozen_owner_semantics.json","six_alternative_method_portfolios.json"]
    names += [o+s for o in ("BASELINE","CANDIDATE")
              for s in ("_krs_input.json","_krs_output.json")]
    receipt={"race_id":RID,"status":"FULL_PRIVATE_PRESENTATION_READY_DELIVERY_ACK_UNVERIFIED",
        "classification":"POSTCUTOFF_DIAGNOSTIC_ONLY","owner_six_methods_proven":True,
        "two_owners_5000_seed1_executed":True,"all29_source_feature_receipt_verified":True,
        "complete_private_full_horse_delivery_presentation":grade,
        "presentation_artifact_sha256":{n:hashlib.sha256((folder/n).read_bytes()).hexdigest()
                                        for n in names}}
    (folder/"private_pipeline_checkpoint.json").write_text(json.dumps(receipt))
    return root,folder

def test_real_content_readback_is_read_only_and_never_execution_attestation(tmp_path):
    root,folder=complete_fixture(tmp_path)
    before={p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in folder.iterdir()}
    r=readback("2026-11-02 船橋3R",root,NOW)
    assert r["status"]=="VERIFIED_FROZEN_PRIVATE_BODY_READY_TO_RENDER"
    assert r["index_cell_count"]==203
    assert r["presentation_content_recomputed_from_saved_inputs"] is True
    assert r["execution_signature_verified_by_readback"] is False
    assert r["formal_signed_final_proven"] is False
    assert r["recipient_delivery_ack"] is False
    assert r["body"].count("|HPI-L|")==7
    assert before=={p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in folder.iterdir()}

@pytest.mark.parametrize("name",["numerical_materialization.json","BASELINE_krs_input.json",
                                "CANDIDATE_krs_output.json","frozen_owner_semantics.json"])
def test_changed_input_bytes_fail_even_when_body_and_booleans_are_unchanged(tmp_path,name):
    root,folder=complete_fixture(tmp_path)
    (folder/name).write_bytes(b"{}")
    r=readback("2026-11-02 船橋3R",root,NOW)
    assert r["status"]=="FULL_DELIVERY_NOT_COMPLETED"
    assert r["reason"].startswith("FNB_SAVED_PRESENTATION_INPUT_SHA_MISMATCH:")

def test_rehashed_truncated_body_still_fails_full_content_reconstruction(tmp_path):
    root,folder=complete_fixture(tmp_path)
    body=folder/"FULL_ALL_HORSES_BC_SIX_METHODS.md"
    body.write_text("## BASELINE\n## CANDIDATE\n## 全馬29指数\n未使用\n")
    p=folder/"private_pipeline_checkpoint.json";receipt=json.loads(p.read_text())
    receipt["complete_private_full_horse_delivery_presentation"]["full_body_sha256"]=hashlib.sha256(body.read_bytes()).hexdigest()
    p.write_text(json.dumps(receipt))
    assert readback("2026-11-02 船橋3R",root,NOW)["reason"].startswith("FNB_SAVED_BODY_DIFFERS_FROM_FULL_INPUTS:")

def test_rehashed_different_ticket_portfolio_is_not_frozen_mec(tmp_path):
    root,folder=complete_fixture(tmp_path)
    p=folder/"six_alternative_method_portfolios.json";portfolio=json.loads(p.read_text())
    portfolio["BASELINE"]["EXACTA"]["tickets"][0]["stake"]=900
    p.write_text(json.dumps(portfolio))
    cp=folder/"private_pipeline_checkpoint.json";receipt=json.loads(cp.read_text())
    receipt["presentation_artifact_sha256"][p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    cp.write_text(json.dumps(receipt))
    assert readback("2026-11-02 船橋3R",root,NOW)["reason"]=="FNB_SAVED_TICKETS_NOT_FROZEN_COMMON_MEC_OUTPUT"

def test_r14_full_body_persists_exact_reconstructable_inputs(tmp_path,monkeypatch):
    # Test the real R14 -> R17 -> R18 -> R19 connection, with numerical/Engine
    # boundaries explicitly stubbed. No real Race execution is counted.
    import runtime.local_fnb_r14_private_work_entry as entry
    root,folder=complete_fixture(tmp_path)
    sem=json.loads((folder/"frozen_owner_semantics.json").read_text())
    digest=hashlib.sha256((folder/"numerical_materialization.json").read_bytes()).hexdigest()
    num={"private_materialization_sha256":digest,"full_private_readback_verified":True,
         "29_index_cells":203}
    monkeypatch.setattr(entry,"numeric_execute",lambda **kwargs:num)
    monkeypatch.setattr(entry,"dual_krs_execute",lambda **kwargs:{"status":"SYNTHETIC_BOUNDARY_ONLY"})
    owners={o:{"numerical_materialization_sha256":digest,
               "horses":[{"horse_no":n} for n in range(1,8)]}
            for o in ("BASELINE","CANDIDATE")}
    result=entry.run(source={"source_snapshot_sha256":sem["BASELINE"]["source_snapshot_sha256"]},
        request={"race_id":folder.name,"prediction_cutoff":"2026-11-02T06:30:00Z"},
        root=root,public_repo=tmp_path/"public",owners=owners,
        engine=tmp_path/"not_executed",params=tmp_path/"not_executed",
        frozen_semantics=sem,diagnostic_only=True,now=NOW)
    assert result["complete_presentation_content_verified"] is True
    receipt=json.loads((folder/"private_pipeline_checkpoint.json").read_text())
    assert len(receipt["presentation_artifact_sha256"])==8
    restored=readback("2026-11-02 船橋3R",root,NOW)
    assert restored["presentation_content_recomputed_from_saved_inputs"] is True
    assert restored["recipient_delivery_ack"] is False

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

