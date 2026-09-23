import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))

from local_candidate_postresult import evaluate_dual, evaluate_candidate_krs_envelope


def arm(mapping,ranking,W,P2,P3):
    return {
      "source_snapshot_sha256":"SRC",
      "candidate_full_numerical_summary":{
        "mapping_id":mapping,
        "production_authority":False,
      },
      "candidate_static_prediction":{
        "ranking":[str(x) for x in ranking],
        "W":[str(x) for x in W],
        "P2":[str(x) for x in P2],
        "P3":[str(x) for x in P3],
        "roles":{str(x):(["W"] if x in W else [])+(["P2"] if x in P2 else [])+(["P3"] if x in P3 else []) for x in ranking},
        "runner_scores":[{"runner_id":str(x),"name":"H"+str(x)} for x in ranking],
        "sha256":"PRED-"+mapping,
      },
    }


def dual():
    return {
      "status":"FROZEN_PRE_RESULT_NUMERICAL_CANDIDATE_DUAL_SHADOW",
      "sha256":"DUAL",
      "arms":{
        "v0.1":arm("v01",[1,2,3,4],[1,2],[1,2,3],[1,2,3,4]),
        "v0.2":arm("v02",[2,1,3,4],[2,1],[2,1,3],[2,1,3,4]),
      }
    }


def krs():
    base={"status":"EXECUTED","receipt_sha256":"R","pre_post_complete":True,"oos_temporal_eligible":True}
    return {"v0.1":dict(base),"v0.2":dict(base)}


def test_training_race_is_not_v02_oos():
    out=evaluate_dual(
      dual(),[2,1,3],result_available_at="2026-09-23T20:00:00+09:00",
      race_id="URW-20260923-R12-FORMAL-R1",dual_krs_summary=krs(),
      calibration_training_race_ids=["URW-20260923-R12-FORMAL-R1"]
    )
    assert out["arms"]["v0.2"]["candidate_is_calibration_training_race"] is True
    assert out["arms"]["v0.2"]["candidate_oos_event_eligible"] is False
    assert out["comparison"]["winner_rank_gain_v02_vs_v01"]==1.0
    assert out["oos_policy"]["automatic_promotion"] is False


def test_future_unknown_race_can_be_dual_oos_but_never_auto_promotes():
    out=evaluate_dual(
      dual(),[2,1,3],result_available_at="2026-09-24T20:00:00+09:00",
      race_id="URW-20260924-R09-FORMAL-R1",dual_krs_summary=krs(),
      calibration_training_race_ids=["URW-20260923-R12-FORMAL-R1"]
    )
    assert out["arms"]["v0.1"]["candidate_oos_event_eligible"] is True
    assert out["arms"]["v0.2"]["candidate_oos_event_eligible"] is True
    assert out["comparison"]["winner_capture_delta_v02_vs_v01"]==0
    assert out["comparison"]["promotion_decision"]=="NO_AUTOMATIC_PROMOTION"
    assert out["oos_policy"]["minimum_future_oos_events_before_human_review"]==30


def synthetic_krs_envelope():
    summary=[]
    for no in [1,2,3,4]:
        summary.append({
          "horse_no":no,"name":"H"+str(no),
          "SSR-W":1.0/no,"SSR-P2":1.0/no,"SSR-P3":1.0/no,"SSR-T3":1.0/no,
          "Z4R-W":1.0/no,"Z4R-P2":1.0/no,"Z4R-P3":1.0/no,"LSR":1.0/no,
          "Robustness":"A","positions":{},"static_roles":[]
        })
    raw={
      "summary":summary,
      "snapshot":{"role_zones":{"w_max_rank":2,"p2_max_rank":3,"p3_max_rank":4},"run_count":5000,"master_seed":1},
      "top_exacta_occurrence":[{"W":2,"P2":1,"count":100,"frequency":0.02}],
      "top_trifecta_occurrence":[{"W":2,"P2":1,"P3":3,"count":50,"frequency":0.01}],
      "scenario_analysis":{},
      "engine":{"name":"TEST"},
    }
    return {
      "receipt_sha256":"KRS-REC",
      "artifact":{"raw_output":raw,"output_sha256":"OUT","actual_run_count":5000}
    }


def test_candidate_krs_postresult_is_measured_against_candidate_static_only():
    a=arm("v02",[2,1,3,4],[2,1],[2,1,3],[2,1,3,4])
    out=evaluate_candidate_krs_envelope(
      a,synthetic_krs_envelope(),[2,1,3],
      race_id="URW-20260924-R09-FORMAL-R1",arm_label="V02"
    )
    assert out["candidate_krs_actual_run_count"]==5000
    assert out["production_effect"]=="NONE"
    assert out["candidate_ticket_activation"]=="NOT_IMPLEMENTED"
    ev=out["post_result_evaluation"]
    assert ev["classification"] in {"SUPPORTIVE","UNIQUE-RESCUE","MIXED","NO-OBSERVED-RESCUE"}
    assert "candidate ticket PFS" in out["note"]


def test_evaluate_dual_can_attach_krs_postresult_without_changing_oos_policy():
    env={"v0.1":synthetic_krs_envelope(),"v0.2":synthetic_krs_envelope()}
    out=evaluate_dual(
      dual(),[2,1,3],result_available_at="2026-09-24T20:00:00+09:00",
      race_id="URW-20260924-R09-FORMAL-R1",dual_krs_summary=krs(),
      calibration_training_race_ids=[],dual_krs_envelopes=env
    )
    assert out["candidate_krs_postresult"]["v0.1"]["candidate_krs_receipt_sha256"]=="KRS-REC"
    assert out["candidate_krs_postresult"]["v0.2"]["candidate_krs_receipt_sha256"]=="KRS-REC"
    assert out["oos_policy"]["automatic_promotion"] is False
