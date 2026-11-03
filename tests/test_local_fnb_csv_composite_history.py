"""Synthetic archive identities only; no public fixture contains real Raw."""
import base64
from copy import deepcopy
import gzip
import hashlib
import json

from runtime import local_fnb_csv_composite_history as history
from runtime import local_base63_source_witness as witness
from runtime.local_physical.source_acquisition import SOURCE_PROFILE, _html_tables
from tests.test_local_base63_source_witness import fixture


def original(*, changed_id=False, wrong_label=False, changed_finish=False):
    source, request = fixture()
    card = source["sources"][0]
    raw = gzip.decompress(base64.b64decode(card["raw_gzip_b64"])).decode()
    for no in (1,2):
        identity = 200+no if changed_id and no == 1 else 100+no
        label = f"テスト馬{no}"
        endpoint = "OtherProfile" if wrong_label and no == 2 else "HorseMarkInfo"
        raw = raw.replace(f"<td>テスト馬{no}</td>", f'<td><a href="/KeibaWeb/DataRoom/{endpoint}?k_lineageLoginCode={identity}">{label}</a></td>')
    if changed_finish:
        raw = raw.replace("1 26.09.25 良 5頭", "2 26.09.25 良 5頭")
    card.update(raw_gzip_b64=base64.b64encode(gzip.compress(raw.encode())).decode(),
        raw_sha256=hashlib.sha256(raw.encode()).hexdigest(), byte_count=len(raw.encode()),
        content_type="text/html; charset=utf-8", authority="NAR_OFFICIAL", http_status=200)
    card["snapshot_sha256"] = witness.canon_hash({k:v for k,v in card.items() if k!="snapshot_sha256"})
    source.update(profile=SOURCE_PROFILE, race_id=request["race_id"], formal_ready=True,
        active_runner_universe={"runners": request["runners"]})
    source["normalized_evidence"] = {"race_card_tables": {"value": _html_tables(raw),
        "source_id": card["source_id"], "snapshot_sha256": card["snapshot_sha256"],
        "fetched_at": card["fetched_at"]}}
    source["normalized_evidence_sha256"] = witness.canon_hash(source["normalized_evidence"])
    source["source_snapshot_sha256"] = witness.canon_hash({k:v for k,v in source.items() if k!="source_snapshot_sha256"})
    receipt = {"family":"LOCAL", "phase":"SOURCE", "status":"SOURCE_FROZEN",
        "errors":[], "race_id":source["race_id"], "artifact_sha256": witness.canon_hash(source)}
    return {"artifact":source,"receipt":receipt,"receipt_sha256":witness.canon_hash(receipt),
        "signature_alg":"Ed25519","signature":"SYNTHETIC_SIGNATURE_PRESENCE_NOT_VERIFIED",
        "signer_key_id":"SYNTHETIC_NOT_TRUSTED"}


def write(tmp_path, name, envelope):
    path = tmp_path/name
    path.write_text(json.dumps(envelope,ensure_ascii=False))
    return path


def test_actual_original_reparse_and_direct_anchor_only_makes_hypothesis(tmp_path):
    path=write(tmp_path,"one.json",original())
    result=history.build_archive_index(tmp_path,[path],"2026-11-03T12:00:00Z")
    assert len(result["entries"])==2 and not result["holds"]
    first=next(x for k,x in result["entries"].items() if k[0]=="テスト馬1")
    assert first["archived_observed_id"]=="NAR:101"
    assert first["current_horse_id"] is None
    assert first["birthdate_match_verified"] is False
    assert first["signature_cryptographically_verified_here"] is False
    assert first["status"]=="UNIQUE_ARCHIVED_COMPOSITE_HYPOTHESIS"
    assert len(first["starts"])==len(first["independent_history"])==5
    assert len(first["source_refs"])==3
    receipt = result["receipt"]
    assert receipt["input_manifest"][0]["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert receipt["sha256"] == history._hash({k:v for k,v in receipt.items() if k!="sha256"})


def test_conflicting_observed_ids_remove_composite_instead_of_aliasing(tmp_path):
    paths=[write(tmp_path,"one.json",original()),write(tmp_path,"two.json",original(changed_id=True))]
    result=history.build_archive_index(tmp_path,paths,"2026-11-03T12:00:00Z")
    assert len(result["entries"])==1
    assert result["holds"][0]["reason"]=="ARCHIVE_COMPOSITE_CONFLICTING_OBSERVED_IDS"
    assert len(result["ambiguous_keys"])==1
    assert result["receipt"]["holds_sha256"]==history._hash(result["holds"])


def test_conflicting_dated_start_is_not_latest_capture_overwrite(tmp_path):
    paths=[write(tmp_path,"one.json",original()),write(tmp_path,"two.json",original(changed_finish=True))]
    result=history.build_archive_index(tmp_path,paths,"2026-11-03T12:00:00Z")
    assert len(result["entries"])==1
    assert result["holds"][0]["reason"]=="ARCHIVE_COMPOSITE_CONFLICTING_DATED_START_FACTS"


def test_missing_same_name_anchor_drops_whole_archive_without_partial_rows(tmp_path):
    path=write(tmp_path,"wrong.json",original(wrong_label=True))
    result=history.build_archive_index(tmp_path,[path],"2026-11-03T12:00:00Z")
    assert result["entries"]=={}
    assert "ONE_DIRECT_HORSE_ANCHOR" in result["holds"][0]["reason"]


def test_receipt_tamper_and_future_capture_have_explicit_holds(tmp_path):
    envelope=original();envelope["artifact"]["sources"][0]["raw_sha256"]="0"*64
    path=write(tmp_path,"tampered.json",envelope)
    result=history.build_archive_index(tmp_path,[path],"2026-11-03T12:00:00Z")
    assert not result["entries"] and "ENVELOPE_HASH" in result["holds"][0]["reason"]
    assert result["receipt"]["input_manifest"][0]["sha256"]==hashlib.sha256(path.read_bytes()).hexdigest()
    path=write(tmp_path,"future.json",original())
    result=history.build_archive_index(tmp_path,[path],"2026-10-02T06:56:00Z")
    assert not result["entries"] and "CAPTURE_AT_OR_AFTER_ASOF" in result["holds"][0]["reason"]


def test_dedup_same_dated_run_and_same_archive_does_not_expand_history(tmp_path):
    path=write(tmp_path,"same.json",original())
    result=history.build_archive_index(tmp_path,[path,path],"2026-11-03T12:00:00Z")
    assert result["receipt"]["unique_archive_snapshots"]==1
    assert all(len(x["starts"])==5 and len(x["provenance"])==1 for x in result["entries"].values())
