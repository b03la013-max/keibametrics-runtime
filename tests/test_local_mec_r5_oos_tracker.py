import json,sys
from pathlib import Path

def w(p,o):
    q=Path(p);q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(o),encoding="utf-8")

def official(rid):
    w(f"runtime/family_result_requests/{rid}-RESULT.json",{
      "race_id":rid,"official_result_verified":True,
      "source":"TEST_OFFICIAL_RESULT","official_result_verification_ref":"TEST:OFFICIAL"
    })

def test_r5_local_signed_forward_tracker(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path)
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import importlib, local_mec_r5_oos_tracker as m
    importlib.reload(m)
    rid="URW-20260924-R01-FORMAL-R1"
    official(rid)
    sh={"profile":m.CANDIDATE_PROFILE,"candidate_id":m.CANDIDATE_ID,"production_effect":"NONE",
        "source_basis_sha256":"B","generated_at":"2026-09-24T13:00:00+09:00",
        "scheduled_post_at":"2026-09-24T13:10:00+09:00","temporal_mode":"FORMAL-PRE-RACE","sha256":"S"}
    arms={a:{"status":"SETTLED","investment":100,"return":200,"profit_loss":100,"pfs":200,"ticket_count":1} for a in m.ARM_ORDER}
    w(f"runtime/local_mec_r5_shadow_artifacts/{rid}.json",sh)
    w(f"runtime/local_mec_r5_shadow_results/{rid}.json",{
      "race_id":rid,
      "status":"FORWARD-OOS-SETTLEMENT / SIGNED-FINAL-BOUND",
      "oos_eligible":True,
      "signed_final_binding_valid":True,
      "arms":arms
    })
    result={"official_result":{"top3":[1,2,3],"payouts":{"exacta":{"1>2":150}}}}
    w(f"runtime/local_mec_r5_shadow_lineage/{rid}.json",{
      "lineage_type":"LOCAL_MEC_R5_SIGNED_FINAL_BOUND","binding_valid":True,
      "shadow_sha256":"S","basis_sha256":"B","final_receipt_sha256":"FR","final_artifact_sha256":"FA",
      "production_tickets":[{"bet_type":"EXACTA","selection":[1,2],"stake":100}],
      "production_result":result,"production_settlement":{"status":"SETTLED","total_investment":100,"total_payout":150}
    })
    out=m.build_status()
    assert out["eligible_races"]==1
    assert out["aggregates"]["PRODUCTION_BASELINE_R3"]["investment_weighted_pfs"]==150
    assert out["aggregates"]["SET_ONLY"]["investment_weighted_pfs"]==200


def test_r5_tracker_rejects_mislabeled_or_unbound_settlement(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path)
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import importlib, local_mec_r5_oos_tracker as m
    importlib.reload(m)
    rid="URW-20260924-R02-FORMAL-R1"
    official(rid)
    sh={"profile":m.CANDIDATE_PROFILE,"candidate_id":m.CANDIDATE_ID,"production_effect":"NONE",
        "source_basis_sha256":"B2","generated_at":"2026-09-24T14:00:00+09:00",
        "scheduled_post_at":"2026-09-24T14:10:00+09:00","temporal_mode":"FORMAL-PRE-RACE","sha256":"S2"}
    arms={a:{"status":"SETTLED","investment":100,"return":200,"profit_loss":100,"pfs":200,"ticket_count":1} for a in m.ARM_ORDER}
    w(f"runtime/local_mec_r5_shadow_artifacts/{rid}.json",sh)
    w(f"runtime/local_mec_r5_shadow_results/{rid}.json",{
      "race_id":rid,"status":"FORWARD-CANDIDATE-UNBOUND / NOT-OOS","oos_eligible":False,"arms":arms
    })
    w(f"runtime/local_mec_r5_shadow_lineage/{rid}.json",{
      "lineage_type":"LOCAL_MEC_R5_SIGNED_FINAL_BOUND","binding_valid":True,
      "shadow_sha256":"S2","basis_sha256":"B2","final_receipt_sha256":"FR2","final_artifact_sha256":"FA2",
      "production_tickets":[],"production_result":{},"production_settlement":{"status":"SETTLED","total_investment":0,"total_payout":0}
    })
    out=m.build_status()
    assert out["eligible_races"]==0
    assert any(x["reason"]=="R5_SETTLEMENT_NOT_FORWARD_OOS" for x in out["errors"])

def test_r5_result_authority_hold(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path)
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import importlib, local_mec_r5_oos_tracker as m
    importlib.reload(m)
    rid="URW-20260924-R99-FORMAL-R1"
    sh={"profile":m.CANDIDATE_PROFILE,"candidate_id":m.CANDIDATE_ID,"production_effect":"NONE",
        "source_basis_sha256":"B99","generated_at":"2026-09-24T15:00:00+09:00",
        "scheduled_post_at":"2026-09-24T15:10:00+09:00","temporal_mode":"FORMAL-PRE-RACE","sha256":"S99"}
    arms={a:{"status":"SETTLED","investment":100,"return":0,"profit_loss":-100,"pfs":0,"ticket_count":1} for a in m.ARM_ORDER}
    w(f"runtime/local_mec_r5_shadow_artifacts/{rid}.json",sh)
    w(f"runtime/local_mec_r5_shadow_results/{rid}.json",{
      "race_id":rid,"status":"FORWARD-OOS-SETTLEMENT / SIGNED-FINAL-BOUND","oos_eligible":True,"arms":arms
    })
    w(f"runtime/local_mec_r5_shadow_lineage/{rid}.json",{
      "lineage_type":"LOCAL_MEC_R5_SIGNED_FINAL_BOUND","binding_valid":True,
      "shadow_sha256":"S99","basis_sha256":"B99","final_receipt_sha256":"FR99","final_artifact_sha256":"FA99",
      "production_tickets":[],"production_result":{},"production_settlement":{"status":"SETTLED","total_investment":0,"total_payout":0}
    })
    out=m.build_status()
    assert out["eligible_races"]==0
    assert out["held_races"]==1
    assert out["held"][0]["reason"]=="RESULT_AUTHORITY_NOT_VERIFIED"
