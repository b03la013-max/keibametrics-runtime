import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))

from local_candidate_dual_oos_tracker import build_measurement, evaluate_measurements


def post(race_id="URW-20260924-R09-FORMAL-R1",training=False,eligible=True):
    arm_common={
      "candidate_mapping_id":"v01",
      "winner_rank":2,"second_rank":1,"third_rank":3,"top3_mean_rank":2.0,
      "winner_capture":True,"p2_capture":True,"p3_capture":True,"top3_set_capture":True,
      "candidate_oos_event_eligible":eligible,
      "candidate_is_calibration_training_race":False,
    }
    v02=dict(arm_common)
    v02.update({"candidate_mapping_id":"v02","winner_rank":1,"top3_mean_rank":1.666667,
                "candidate_is_calibration_training_race":training,
                "candidate_oos_event_eligible":bool(eligible and not training)})
    return {
      "profile":"KM-LOCAL-NUMERICAL-CANDIDATE-POSTRESULT-v0.2-DUAL-20260923",
      "race_id":race_id,
      "result_available_at":"2026-09-24T20:00:00+09:00",
      "actual_top3":["2","1","3"],
      "dual_shadow_sha256":"DUAL",
      "sha256":"POST",
      "arms":{"v0.1":dict(arm_common),"v0.2":v02},
      "candidate_krs_postresult":{
        "v0.1":{"post_result_evaluation":{"classification":"SUPPORTIVE","rescues":[],"misses":[]}},
        "v0.2":{"post_result_evaluation":{"classification":"UNIQUE-RESCUE","rescues":["WINNER_ROLE_RESCUE"],"misses":[]}},
      },
      "comparison":{
        "same_source":True,
        "winner_rank_gain_v02_vs_v01":1.0,
        "winner_capture_delta_v02_vs_v01":0,
      }
    }


def request(race_id="URW-20260924-R09-FORMAL-R1",verified=False):
    return {
      "race_id":race_id,
      "source":"NAR_OFFICIAL_RESULT",
      "official_result_verified":verified,
      "official_result_verification_ref":"NAR:TEST" if verified else None,
    }


def test_unverified_result_is_persistable_but_not_r30_admissible():
    m=build_measurement(post(),request(verified=False))
    assert m["temporal_dual_oos_eligible"] is True
    assert m["promotion_measurement_admissible"] is False
    assert m["hold_reason"]=="RESULT_AUTHORITY_NOT_VERIFIED"
    s=evaluate_measurements([m])
    assert s["promotion_admissible_races"]==0
    assert s["held_races"]==1
    assert s["remaining_to_r30"]==30
    assert s["automatic_promotion"] is False


def test_calibration_training_race_never_enters_r30_even_if_result_verified():
    rid="URW-20260923-R12-FORMAL-R1"
    m=build_measurement(post(race_id=rid,training=True),request(race_id=rid,verified=True))
    assert m["temporal_dual_oos_eligible"] is False
    assert m["promotion_measurement_admissible"] is False
    assert m["hold_reason"]=="DUAL_OOS_TEMPORAL_OR_TRAINING_GATE_NOT_PASS"


def test_verified_future_oos_event_is_admitted_and_tracks_krs_rescue():
    m=build_measurement(post(),request(verified=True))
    assert m["promotion_measurement_admissible"] is True
    assert m["arms"]["v0.2"]["krs_classification"]=="UNIQUE-RESCUE"
    s=evaluate_measurements([m])
    assert s["promotion_admissible_races"]==1
    assert s["arms"]["v0.2"]["krs_unique_rescue_rate"]==1.0
    assert s["v0.2_minus_v0.1"]["mean_winner_rank_gain"]==1.0
    assert s["status"]=="WAITING_R30"


def test_r30_only_opens_human_review_and_never_promotes():
    rows=[]
    for i in range(30):
        rid=f"URW-202610{i+1:02d}-R09-FORMAL-R1"
        rows.append(build_measurement(post(race_id=rid),request(race_id=rid,verified=True)))
    s=evaluate_measurements(rows)
    assert s["promotion_admissible_races"]==30
    assert s["remaining_to_r30"]==0
    assert s["promotion_review_ready"] is True
    assert s["status"]=="HUMAN_REVIEW_REQUIRED"
    assert s["automatic_promotion"] is False
    assert s["production_effect"]=="NONE"


def test_candidate_pfs_and_harm_are_not_invented():
    m=build_measurement(post(),request(verified=True))
    assert m["candidate_ticket_pfs"]["status"]=="NOT_AVAILABLE"
    assert m["krs_harm_measurement"]["status"]=="UNASSESSABLE_WITHOUT_CANDIDATE_TICKET_ACTIVATION"
