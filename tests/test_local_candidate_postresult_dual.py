import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))

from local_candidate_postresult import evaluate_dual


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
