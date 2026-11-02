"""R13 official historical SOURCE→private all-horse 29-index complete replay.

The real historical NAR SOURCE fixture is used only as an input. Any success
is retrospective and cannot be counted toward 2026-11-02 formal prestart OOS.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json
import pytest

from runtime import formal_execution_orchestrator as o
from runtime.local_fnb_r13_private_single_numeric import execute
from runtime.local_fnb_r13_private_source_admission import (
    SCOPE,PURPOSE,admit)

ROOT=Path(__file__).resolve().parents[1]
RACE="KM-LOCAL-FNB-20261002-R04-LIVE-R1"
EID="LOCAL-"+RACE+"-EXEC"

@pytest.fixture(scope="module")
def saved():
    src=o.resolve_phase(EID,"SOURCE")
    assert src is not None
    art=o._load_checkpoint_json(src,"source_receipt_envelope.json")["artifact"]
    req=json.loads((ROOT/"runtime/formal_intents"/(RACE+".json")).read_text())
    return art,req

def test_r13_real_private_noncommercial_12_horses_348_cells_756_features_29_formula(saved,tmp_path):
    source,req=saved
    grade=execute(source_artifact=source,request=req,
                  private_root=tmp_path,repo_root=ROOT,
                  now=datetime(2026,11,2,tzinfo=timezone.utc),
                  diagnostic_only=True)
    assert grade["status"]=="PRIVATE_NUMERIC_DIAGNOSTIC_COMPLETE_NOT_FORMAL"
    assert grade["runner_count"]==12
    assert grade["29_index_cells"]==348
    assert grade["calculated"]==312
    assert grade["neutral"]==36
    assert grade["unknown_components"]==274
    assert grade["full_private_readback_verified"] is True
    assert grade["signed_final_or_delivery_claim"] is False
    assert grade["registered_oos_increment"]==0
    assert "HISTORICAL_DIAGNOSTIC" in grade["classification"]
    folder=Path(grade["private_root"])
    original=(folder/"numerical_materialization.json").read_bytes()
    assertion=json.loads((folder/"private_numerical_receipt.json").read_text())
    assert hashlib.sha256(original).hexdigest()==assertion["numerical_materialization_sha256"]
    assert assertion["private_use_scope"]==PURPOSE
    assert assertion["source_admission"]["full_v2_dated_oos_plan_required_for_this_lane"] is False
    assert assertion["fixed_two_owners_krs_5000_seed1_verified"] is False
    assert assertion["recipient_delivery_ack_verified"] is False
    assert assertion["pfs"] is None
    assert folder.parent==tmp_path
    pretty=(folder/"all_horse_29_index_report.md").read_text(encoding="utf-8")
    assert "全馬29指数" in pretty
    assert pretty.count("| HPI-L |")==12
    assert pretty.count("| RSI |")==12
    assert "CALCULATED" in pretty and "RULED-NEUTRAL" in pretty
    assert "未計算" in pretty and "NO-BETではない" in pretty
    assert hashlib.sha256((folder/"all_horse_29_index_report.md").read_bytes()).hexdigest()==assertion["private_readable_document_sha256"]
    assert assertion["private_readable_index_cells"]==348
    assert assertion["recipient_delivery_ack_verified"] is False

def test_r13_missing_v2_plan_cannot_disqualify_private_independent_numeric(saved,tmp_path):
    source,req=saved
    permission=admit(source=source,request=req,purpose=PURPOSE,
                     classification=SCOPE,destination=tmp_path,
                     public_repo_root=ROOT)
    assert permission["status"]=="PRIVATE_NUMERICAL_LANE_SOURCE_METADATA_ADMITTED"
    assert permission["full_v2_dated_oos_plan_required_for_this_lane"] is False
    assert permission["formal_owner_or_numeric_consumers_authorized"] is False
    assert permission["issuer_signature_verified_here"] is False

def test_r13_after_race_does_not_retroactively_create_prestart_forecast(saved,tmp_path):
    source,req=saved
    with pytest.raises(ValueError,match="FNB_PRESTART_CUTOFF_EXPIRED"):
        execute(source_artifact=source,request=req,private_root=tmp_path,
                repo_root=ROOT,now=datetime(2026,11,2,tzinfo=timezone.utc))

def test_r13_public_repository_raw_and_horse_numerics_are_forbidden(saved):
    source,req=saved
    with pytest.raises(ValueError,match="PUBLIC_GIT_REPO_FORBIDDEN"):
        admit(source=source,request=req,purpose=PURPOSE,
              classification=SCOPE,destination=ROOT/"runtime"/"private_fnb",
              public_repo_root=ROOT)

def test_r13_cross_race_ledger_source_identity_fails(saved,tmp_path):
    source,req=saved
    bad=deepcopy(req)
    bad["race_id"]="KM-LOCAL-FNB-20261002-R05-LIVE-R1"
    with pytest.raises(ValueError,match="PRIVATE_SOURCE_RACE_IDENTITY_MISMATCH"):
        admit(source=source,request=bad,purpose=PURPOSE,
              classification=SCOPE,destination=tmp_path,public_repo_root=ROOT)



def test_r13_cli_reads_private_source_and_writes_only_private_document(saved,tmp_path,capsys):
    from runtime.local_fnb_r13_private_single_numeric import main
    source,req=saved
    source_path=tmp_path/"official_source.json"
    intent_path=tmp_path/"race_intent.json"
    source_path.write_text(json.dumps(source,ensure_ascii=False),encoding="utf-8")
    intent_path.write_text(json.dumps(req,ensure_ascii=False),encoding="utf-8")
    private=tmp_path/"private_store"
    assert main(["--source-artifact",str(source_path),
                 "--request",str(intent_path),
                 "--private-output",str(private),
                 "--diagnostic-only"])==0
    output=capsys.readouterr().out
    summary=json.loads(output)
    assert summary["runner_count"]==12
    assert summary["29_index_cells"]==348
    assert "private_root" not in output
    assert (private/RACE/"all_horse_29_index_report.md").is_file()
    assert (private/RACE/"private_numerical_receipt.json").is_file()
