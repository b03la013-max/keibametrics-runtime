"""R16 actual archived FNB official original bytes into private unsigned source."""
from __future__ import annotations
import base64,copy,gzip,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
import pytest

from runtime import formal_execution_orchestrator as o
from runtime.local_fnb_r16_private_browser_capture import ingest

ROOT=Path(__file__).resolve().parents[1]
RID="KM-LOCAL-FNB-20261002-R04-LIVE-R1"
EID="LOCAL-"+RID+"-EXEC"

@pytest.fixture(scope="module")
def original():
    saved=o.resolve_phase(EID,"SOURCE")
    assert saved is not None
    art=o._load_checkpoint_json(saved,"source_receipt_envelope.json")["artifact"]
    card=[s for s in art["sources"] if
          s.get("source_class")=="OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT"]
    assert len(card)==1
    req=json.loads((ROOT/"runtime/formal_intents"/(RID+".json")).read_text())
    return art,card[0],req

def _run(tmp_path,original,**replace):
    art,card,req=original
    raw=gzip.decompress(base64.b64decode(card["raw_gzip_b64"]))
    html=tmp_path/"original_browser_captured.html"
    html.write_bytes(raw)
    config={"html_path":html,"request":req,"observed_url":card["requested_url"],
            "capture_time":art["source_freeze_at"],
            "private_output":tmp_path/"user_private",
            "public_repo":ROOT,
            "now":datetime(2026,11,2,tzinfo=timezone.utc),
            "diagnostic_only":True}
    config.update(replace)
    return ingest(**config)

def test_r16_real_official_20261002_browser_bytes_private_import(original,tmp_path):
    report=_run(tmp_path,original)
    assert report["status"]=="FNB_BROWSER_SOURCE_IMPORTED_TO_PRIVATE_RESEARCH_UNSIGNED"
    assert report["declared_runner_count"]==12
    assert report["signed_source_verified"] is False
    assert report["registered_oos_increment"]==0
    folder=tmp_path/"user_private"/RID
    parsed=json.loads((folder/"unsigned_official_card_artifact.json").read_text())
    receipt=json.loads((folder/"source_browser_import_receipt.json").read_text())
    assert parsed["race_id"]==RID
    assert len(parsed["declared_runner_universe"]["runners"])==12
    assert parsed["source_became_signed"] is False
    assert receipt["card_raw_reparsed_and_identity_checked"] is True
    assert receipt["full_29_indices_calculated_here"] is False
    assert receipt["active_runner_count_verified"] is False
    assert hashlib.sha256((folder/"unsigned_official_card_artifact.json").read_bytes()).hexdigest()==receipt["stored_artifact_sha256"]
    assert report["source_artifact_sha256"]==receipt["stored_artifact_sha256"]

def test_r16_unofficial_different_card_url_fails_even_with_real_raw(original,tmp_path):
    with pytest.raises(ValueError,match="FNB_BROWSER_CANONICAL_OFFICIAL_URL_REQUIRED"):
        _run(tmp_path,original,observed_url="https://third-party.invalid/horse-card")

def test_r16_future_race_runner_set_conflict_fails(original,tmp_path):
    art,card,req=original
    bad=copy.deepcopy(req)
    bad["runners"].pop()
    with pytest.raises(ValueError,match="FNB_BROWSER_INTENT_VS_OFFICIAL_DECLARED_RUNNERS_CONFLICT"):
        _run(tmp_path,original,request=bad)

def test_r16_import_after_cutoff_is_explicitly_diagnostic_only(original,tmp_path):
    with pytest.raises(ValueError,match="FNB_BROWSER_PREDICTION_CUTOFF_ALREADY_EXPIRED"):
        _run(tmp_path,original,diagnostic_only=False)

def test_r16_public_repo_html_path_and_storage_forbidden(original,tmp_path):
    with pytest.raises(ValueError,match="FNB_OFFICIAL_PRIVATE_BROWSER_BYTES_PUBLIC_REPO_FORBIDDEN"):
        _run(tmp_path,original,private_output=ROOT/"secret-source")

def test_r16_mismatched_raw_bytes_fail_closed(original,tmp_path):
    art,card,req=original
    bad=tmp_path/"bad_original.html"
    bad.write_bytes(b"<html>not a NAR card</html>")
    with pytest.raises(ValueError):
        _run(tmp_path,original,html_path=bad)



def test_r16_actual_one_trigger_work_browser_to_full29(original,tmp_path,capsys):
    from runtime.local_fnb_r14_private_work_entry import main
    art,card,request=original
    html=tmp_path/"desktop_browser_original_bytes.html"
    html.write_bytes(gzip.decompress(base64.b64decode(card["raw_gzip_b64"])))
    request_file=tmp_path/"race_request.json"
    request_file.write_text(json.dumps(request,ensure_ascii=False),encoding="utf-8")
    private=tmp_path/"full_private_pipeline"
    rc=main(["--private-browser-html",str(html),
             "--browser-original-url",card["requested_url"],
             "--browser-captured-at",art["source_freeze_at"],
             "--request",str(request_file),
             "--private-root",str(private),
             "--diagnostic-only"])
    assert rc==0
    printed=json.loads(capsys.readouterr().out)
    assert printed["numeric_cells"]==348
    assert printed["krs_two_owners_done"] is False
    assert printed["formal_final_or_delivery_done"] is False
    assert printed["private_official_browser_source_signed"] is False
    assert (private/RID/"unsigned_official_card_artifact.json").is_file()
    assert (private/RID/"numerical_materialization.json").is_file()
    assert (private/RID/"all_horse_29_index_report.md").is_file()
    assert (private/RID/"private_pipeline_checkpoint.json").is_file()


def test_r16_browser_cli_requires_original_url_and_capture_time(original,tmp_path):
    from runtime.local_fnb_r14_private_work_entry import main
    html=tmp_path/"blank.html"
    html.write_text("placeholder")
    request=tmp_path/"request.json"
    request.write_text(json.dumps(original[2],ensure_ascii=False))
    with pytest.raises(ValueError,match="FNB_BROWSER_HTML_EXACT_URL_AND_CAPTURE_TIME_REQUIRED"):
        main(["--private-browser-html",str(html),
              "--request",str(request),
              "--private-root",str(tmp_path/"out")])
