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


def test_r14_fixed_owner_must_match_all_real_12_horse_ids(tmp_path,archived):
    source,request=archived
    first=_run(source,request,tmp_path)
    numeric=json.loads((tmp_path/"private"/RID/"private_numerical_receipt.json").read_text())
    sha=numeric["numerical_materialization_sha256"]
    wrong={"numerical_materialization_sha256":sha,
           "horses":[{"horse_no":99,"hsv":{},"static":{}}]}
    with pytest.raises(ValueError,match="FNB_PRIVATE_OWNER_ACTIVE_RUNNER_UNIVERSE_MISMATCH"):
        _run(source,request,tmp_path,
             owners={"BASELINE":wrong,"CANDIDATE":wrong})
    assert not (tmp_path/"private"/RID/"private_dual_krs_receipt.json").exists()



def test_r14_six_independent_common_method_trees_private_render_only(tmp_path,archived,monkeypatch):
    from runtime.jra_ticket_tree_renderer import render_ticket_tree
    import runtime.local_fnb_r14_private_work_entry as entry
    source,request=archived
    first=_run(source,request,tmp_path)
    num=json.loads((tmp_path/"private"/RID/"private_numerical_receipt.json").read_text())
    sha=num["numerical_materialization_sha256"]
    owners={k:{"numerical_materialization_sha256":sha,
                "horses":[{"horse_no":n} for n in range(1,13)]}
            for k in ("BASELINE","CANDIDATE")}
    def method_entry(bet_type):
        ticket={"bet_type":bet_type,
                "selection":[1,2] if bet_type=="EXACTA" else [1,2,3],
                "stake":100}
        tree=render_ticket_tree({
            "final_ticket":{"tickets":[ticket],"no_bet":False},
            "capital_policy_decision":{"decision":"RECOMMENDATION_ONLY"}})
        return {"tickets":[ticket],"point_count":1,"total_investment":100,
                "capital_limit":500,"unused_capital":400,
                "no_bet":False,"canonical_tree":tree["text"]}
    methods={bet:method_entry(bet)
             for bet in ("EXACTA","TRIO","TRIFECTA")}
    portfolio={owner:deepcopy(methods) for owner in ("BASELINE","CANDIDATE")}
    # Explicitly synthetic transport test: NO real KRS execution is claimed.
    monkeypatch.setattr(entry,"dual_krs_execute",
        lambda **kwargs:{"status":"TEST_ONLY_STUB_NO_REAL_KRS"})
    response=_run(source,request,tmp_path,owners=owners,
                  engine=Path("fake"),params=Path("fake"),portfolios=portfolio)
    assert response["six_alternative_method_trees_rendered"] is True
    assert response["status"]=="NUMERIC_KRS_SIX_ALTERNATIVE_TREES_STRUCTURED_DELIVERY_UNPROVEN"
    doc=(tmp_path/"private"/RID/"baseline_candidate_6methods_alternative_trees.md").read_text()
    assert doc.count("### EXACTA") == 2
    assert doc.count("### TRIO") == 2
    assert doc.count("### TRIFECTA") == 2
    assert "BASELINE" in doc and "CANDIDATE" in doc
    assert "未使用400円" in doc
    receipt=json.loads((tmp_path/"private"/RID/"private_pipeline_checkpoint.json").read_text())
    assert receipt["owner_six_methods_proven"] is True
    assert receipt["user_ticket_rendered_and_acknowledged"] is False
    assert receipt["is_formal_final"] is False
    assert receipt["pfs"] is None


def test_r14_unformed_six_methods_are_not_fake_no_bet(tmp_path,archived):
    source,request=archived
    with pytest.raises(ValueError,match="FNB_TICKETS_WITHOUT_TWO_OWNER_KRS_FORBIDDEN"):
        _run(source,request,tmp_path,portfolios={"BASELINE":{},"CANDIDATE":{}})
