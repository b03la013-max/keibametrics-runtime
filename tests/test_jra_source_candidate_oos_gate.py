import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))

from jra_source_candidate_oos import pre_result_record,evaluate_result
from jra_source_candidate_promotion_gate import bind_result,evaluate

def candidate(mode="FORMAL-PRE-RACE",acceptance=False,final_verified=True):
    return {
      "race_id":"R1","prediction_id":"P1","source_snapshot_sha256":"a"*64,
      "candidate_numerical_summary":{"profile":"NUM"},
      "candidate_semantic_freeze":{"profile":"SEM","sha256":"b"*64},
      "static_prediction":{"ranking":["1","2","3"],"roles":{"1":["W"],"2":["P2"],"3":["P3"]}},
      "pair_dispositions":[{"head":"1","second":"2","status":"PURCHASE"}],
      "third_dispositions":[{"head":"1","second":"2","third":"3","status":"PURCHASE"}],
      "temporal_mode":mode,"acceptance_only":acceptance,
      "scheduled_post_at":"2026-09-27T16:00:00+09:00",
      "candidate_frozen_at":"2026-09-27T15:50:00+09:00",
      "candidate_final_receipt_sha256":"c"*64,
      "candidate_final_receipt_timestamp":"2026-09-27T15:57:00+09:00",
      "candidate_final_verified":final_verified,
    }

def test_oos_eligibility_requires_pre_result_signed_final():
    r=pre_result_record(candidate())
    assert r["oos_eligible"] is True
    for bad in [
      candidate(mode="POST-START-REPLAY"),
      candidate(acceptance=True),
      candidate(final_verified=False),
    ]:
      assert pre_result_record(bad)["oos_eligible"] is False
    late=candidate();late["candidate_final_receipt_timestamp"]="2026-09-27T16:00:01+09:00"
    assert pre_result_record(late)["oos_eligible"] is False

def test_result_binding_and_r30_gate():
    records=[]
    for i in range(30):
      c=candidate();c["race_id"]=f"R{i+1}";c["prediction_id"]=f"P{i+1}"
      pre=pre_result_record(c)
      ev=evaluate_result(pre,[1,2,3])
      bound=bind_result(pre,ev)
      records.append(bound)
    g29=evaluate(records[:29])
    assert g29["status"]=="WAITING_R30"
    assert g29["eligible_race_count"]==29
    assert g29["automatic_promotion"] is False
    g30=evaluate(records)
    assert g30["status"]=="R30_REVIEW_REQUIRED"
    assert g30["eligible_race_count"]==30
    assert g30["promotion_decision"]=="NOT_AUTHORIZED"
    assert g30["automatic_promotion"] is False

def test_ineligible_replay_never_counts():
    pre=pre_result_record(candidate(mode="POST-START-REPLAY"))
    ev=evaluate_result(pre,[1,2,3])
    bound=bind_result(pre,ev)
    g=evaluate([bound])
    assert g["eligible_race_count"]==0


def test_result_evaluation_measures_market_baseline_width_efficiency_and_attribution():
    c=candidate()
    c["candidate_source_objective_shadow"]={
      "profile":"OBJ",
      "sha256":"d"*64,
      "runners":{
        "1":{
          "profile":"ESTABLISHED","observed_feature_count":2,"missing_feature_count":1,
          "features":{
            "market_rank":{"score":70.0,"category":"POSITIVE","missing":False,"coverage":1.0,"candidate_rule_id":"M","source_fact":"pop=2","raw_metric":2},
            "recent_performance":{"score":88.0,"category":"STRONG","missing":False,"coverage":1.0,"candidate_rule_id":"R","source_fact":"recent","raw_metric":[90,86]},
            "workout_speed":{"score":64.0,"category":"NEUTRAL","missing":True,"coverage":0.0,"candidate_rule_id":"W","source_fact":"missing","raw_metric":None}
          },
          "base_indices":{"HPI":{"diagnostic_neutralized_score":90.0}},
          "derived_indices":{"ZAI_WIN":92.0}
        },
        "2":{
          "profile":"ESTABLISHED","observed_feature_count":2,"missing_feature_count":0,
          "features":{"market_rank":{"score":90.0,"category":"STRONG","missing":False,"coverage":1.0,"candidate_rule_id":"M","source_fact":"pop=1","raw_metric":1}},
          "base_indices":{"HPI":{"diagnostic_neutralized_score":80.0}},
          "derived_indices":{"ZAI_WIN":82.0}
        },
        "3":{
          "profile":"ESTABLISHED","observed_feature_count":2,"missing_feature_count":0,
          "features":{"market_rank":{"score":60.0,"category":"MIXED","missing":False,"coverage":1.0,"candidate_rule_id":"M","source_fact":"pop=3","raw_metric":3}},
          "base_indices":{"HPI":{"diagnostic_neutralized_score":70.0}},
          "derived_indices":{"ZAI_WIN":72.0}
        }
      }
    }
    pre=pre_result_record(c)
    assert pre["market_ranking"]==["2","1","3"]
    ev=evaluate_result(pre,[1,2,3])
    assert ev["winner_static_rank"]==1
    assert ev["second_static_rank"]==2
    assert ev["third_static_rank"]==3
    assert ev["top3_mean_static_rank"]==2.0
    assert ev["w_width"]==1 and ev["p2_width"]==1 and ev["p3_width"]==1
    assert ev["winner_capture_efficiency"]==1.0
    assert ev["market_baseline"]["winner_rank"]==2
    assert ev["candidate_vs_market"]["winner_rank_gain"]==1.0
    assert ev["actual_top3_attribution"]["1"]["index_ranks"]["HPI"]==1
    assert ev["actual_top3_attribution"]["1"]["index_ranks"]["ZAI_WIN"]==1
    assert "workout_speed" in ev["actual_top3_attribution"]["1"]["missing_features"]
    assert ev["actual_top3_attribution"]["1"]["causal_claim"] is False


def test_promotion_gate_aggregates_rank_and_market_utility_without_auto_promotion():
    c=candidate()
    c["candidate_source_objective_shadow"]={
      "profile":"OBJ","sha256":"e"*64,
      "runners":{
        "1":{"features":{"market_rank":{"raw_metric":2,"missing":False}},"base_indices":{"HPI":{"diagnostic_neutralized_score":90.0}},"derived_indices":{"ZAI_WIN":92.0}},
        "2":{"features":{"market_rank":{"raw_metric":1,"missing":False}},"base_indices":{"HPI":{"diagnostic_neutralized_score":80.0}},"derived_indices":{"ZAI_WIN":82.0}},
        "3":{"features":{"market_rank":{"raw_metric":3,"missing":False}},"base_indices":{"HPI":{"diagnostic_neutralized_score":70.0}},"derived_indices":{"ZAI_WIN":72.0}}
      }
    }
    pre=pre_result_record(c)
    bound=bind_result(pre,evaluate_result(pre,[1,2,3]))
    g=evaluate([bound])
    assert g["mean_winner_static_rank"]==1.0
    assert g["mean_second_static_rank"]==2.0
    assert g["mean_third_static_rank"]==3.0
    assert g["mean_top3_static_rank"]==2.0
    assert g["mean_market_winner_rank"]==2.0
    assert g["mean_candidate_vs_market_winner_rank_gain"]==1.0
    assert g["automatic_promotion"] is False
    assert g["promotion_decision"]=="NOT_AUTHORIZED"
