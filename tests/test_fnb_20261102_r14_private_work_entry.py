"""R14 one-trigger actual numeric first; no owners cannot become formal NO-BET."""
from datetime import datetime,timezone
from pathlib import Path
from copy import deepcopy
import hashlib,json
import pytest

from runtime import formal_execution_orchestrator as o
from runtime.local_fnb_r14_private_work_entry import run

ROOT=Path(__file__).resolve().parents[1]
RID="KM-LOCAL-FNB-20261002-R04-LIVE-R1"
EID="LOCAL-"+RID+"-EXEC"

@pytest.fixture(scope="module")
def archived():
    checkpoint=o.resolve_phase(EID,"SOURCE")
    assert checkpoint
    source=o._load_checkpoint_json(checkpoint,"source_receipt_envelope.json")["artifact"]
    request=json.loads((ROOT/"runtime/formal_intents"/(RID+".json")).read_text())
    return source,request

def _run(source,request,tmp_path,**kw):
    return run(source=source,request=request,root=tmp_path/"private",
        public_repo=ROOT,diagnostic_only=True,
        now=datetime(2026,11,2,5,0,tzinfo=timezone.utc),**kw)

def test_r14_real_archived_one_trigger_outputs_full29_and_reports_no_krs(tmp_path,archived):
    source,request=archived
    response=_run(source,request,tmp_path)
    assert response["status"]=="NUMERIC_ONLY_FROZEN_OWNER_PACKETS_MISSING"
    assert response["numeric_cells"]==348
    assert response["krs_two_owners_done"] is False
    assert response["formal_final_or_delivery_done"] is False
    assert response["private_checkpoint_readback_verified"] is True
    assert response["registered_oos_increment"]==0
    path=tmp_path/"private"/RID
    saved=json.loads((path/"private_pipeline_checkpoint.json").read_text())
    assert saved["source_readonly_private_numerical"]["calculated"]==312
    assert saved["source_readonly_private_numerical"]["neutral"]==36
    assert saved["source_readonly_private_numerical"]["unknown_components"]==274
    assert saved["first_uncompleted_stage"]=="FIXED_OWNER_INPUT_NOT_PROVIDED"
    assert saved["owner_six_methods_proven"] is False
    assert saved["pfs"] is None
    assert saved["is_formal_final"] is False
    assert (path/"all_horse_29_index_report.md").is_file()
    assert (path/"numerical_materialization.json").is_file()

def test_r14_owner_input_must_be_bound_to_this_numerical_freeze(tmp_path,archived):
    source,request=archived
    fake={"owner":"BASELINE","numerical_materialization_sha256":"0"*64}
    with pytest.raises(ValueError,match="FNB_PRIVATE_OWNER_NOT_BOUND_TO_SAME_29_INDEX_FREEZE"):
        _run(source,request,tmp_path,owners={"BASELINE":fake,"CANDIDATE":fake})
    assert (tmp_path/"private"/RID/"numerical_materialization.json").is_file()
    assert not (tmp_path/"private"/RID/"private_dual_krs_receipt.json").exists()

def test_r14_one_owner_is_not_silently_run_as_both(tmp_path,archived):
    source,request=archived
    with pytest.raises(ValueError,match="FNB_PRIVATE_BOTH_FROZEN_OWNER_PACKETS_REQUIRED"):
        _run(source,request,tmp_path,owners={"BASELINE":{}})
