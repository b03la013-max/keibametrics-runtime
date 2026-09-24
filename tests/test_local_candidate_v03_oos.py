import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))

from local_candidate_v03_postresult import evaluate_v03
from local_candidate_v03_oos_tracker import build_measurement, evaluate_measurements


def frozen_v03(race_date="2026-09-25"):
    arm={
      "status":"FROZEN_PRE_RESULT_NUMERICAL_CANDIDATE_SHADOW",
      "source_snapshot_sha256":"SRC",
      "sha256":"ARM-SHA",
      "candidate_full_numerical_summary":{
        "mapping_id":"LOCAL-FULL-NUMERICAL-MAPPING-v0.3-CANDIDATE-20260925-EVIDENCE-ROUTING",
        "production_authority":False,
      },
      "candidate_static_prediction":{
        "sha256":"PRED-SHA",
        "ranking":["1","2","3","4"],
        "W":["1","2"],"P2":["1","2","3"],"P3":["1","2","3","4"],
      },
      "runner_component_coverage":{
        "1":{"real_component_coverage_ratio":0.80,"missing_component_count":12},
        "2":{"real_component_coverage_ratio":0.70,"missing_component_count":18},
        "3":{"real_component_coverage_ratio":0.90,"missing_component_count":6},
        "4":{"real_component_coverage_ratio":0.60,"missing_component_count":24},
      },
    }
    return {
      "status":"FROZEN_PRE_RESULT_NUMERICAL_CANDIDATE_V03_SHADOW",
      "profile":"KM-LOCAL-NUMERICAL-EVIDENCE-ROUTING-v0.3-CANDIDATE-20260925",
      "design_freeze_date":"2026-09-25",
      "race_id":"URW-20260925-R01-FORMAL-R1",
      "race_date":race_date,
      "retrospective_replay":race_date<"2026-09-25",
      "source_snapshot_sha256":"SRC",
      "sha256":"V03-SHA",
      "arm":arm,
    }


def krs():
    return {
      "status":"EXECUTED",
      "receipt_sha256":"KRS-SHA",
      "pre_post_complete":True,
      "oos_temporal_eligible":True,
    }


def result_request(official=True):
    return {
      "race_id":"URW-20260925-R01-FORMAL-R1",
      "source":"NAR_OFFICIAL_RESULT_VERIFIED",
      "official_result_verified":official,
      "official_result_verification_ref":"NAR-REF" if official else None,
    }


def test_v03_future_signed_bound_official_result_is_oos_admissible():
    post=evaluate_v03(
      frozen_v03(),[1,2,3],
      result_available_at="2026-09-25T13:00:00+09:00",
      race_id="URW-20260925-R01-FORMAL-R1",
      krs_summary=krs(),
      signed_final_binding_valid=True,
    )
    assert post["arm"]["candidate_oos_event_eligible"] is True
    baseline={"arms":{
      "v0.1":{"winner_rank":2,"second_rank":3,"third_rank":4,
              "winner_capture":False,"p2_capture":True,"p3_capture":True},
      "v0.2":{"winner_rank":3,"second_rank":2,"third_rank":4,
              "winner_capture":False,"p2_capture":True,"p3_capture":True},
    }}
    m=build_measurement(post,result_request(True),baseline_measurement=baseline)
    assert m["promotion_measurement_admissible"] is True
    assert m["vs_v01"]["winner_rank_gain"]==1
    assert m["vs_v02"]["baseline_available"] is True
    assert m["vs_v02"]["winner_rank_gain"]==2
    assert m["arm"]["mean_component_coverage_ratio"]==0.75
    assert m["arm"]["mean_missing_component_count"]==15.0
    status=evaluate_measurements([m])
    assert status["promotion_admissible_races"]==1
    assert status["remaining_to_r30"]==29
    assert status["metrics"]["mean_component_coverage_ratio"]==0.75
    assert status["metrics"]["mean_missing_component_count"]==15.0
    assert status["vs_v02"]["available_races"]==1
    assert status["vs_v02"]["mean_winner_rank_gain"]==2
    assert status["automatic_promotion"] is False


def test_v03_20260924_replay_can_never_enter_forward_oos():
    s=frozen_v03("2026-09-24")
    s["race_id"]="URW-20260924-R10-FORMAL-R1"
    s["arm"]["candidate_static_prediction"]["ranking"]=["3","7","10","1"]
    post=evaluate_v03(
      s,[3,7,10],
      result_available_at="2026-09-24T18:45:00+09:00",
      race_id="URW-20260924-R10-FORMAL-R1",
      krs_summary=krs(),
      signed_final_binding_valid=True,
    )
    assert post["future_oos_candidate"] is False
    assert post["arm"]["candidate_oos_event_eligible"] is False


def test_v03_missing_signed_final_binding_blocks_oos():
    post=evaluate_v03(
      frozen_v03(),[1,2,3],
      result_available_at="2026-09-25T13:00:00+09:00",
      race_id="URW-20260925-R01-FORMAL-R1",
      krs_summary=krs(),
      signed_final_binding_valid=False,
    )
    assert post["arm"]["candidate_oos_event_eligible"] is False


def test_v03_unverified_result_authority_is_hold():
    post=evaluate_v03(
      frozen_v03(),[1,2,3],
      result_available_at="2026-09-25T13:00:00+09:00",
      race_id="URW-20260925-R01-FORMAL-R1",
      krs_summary=krs(),
      signed_final_binding_valid=True,
    )
    m=build_measurement(post,result_request(False))
    assert m["promotion_measurement_admissible"] is False
    assert m["hold_reason"]=="RESULT_AUTHORITY_NOT_VERIFIED"
