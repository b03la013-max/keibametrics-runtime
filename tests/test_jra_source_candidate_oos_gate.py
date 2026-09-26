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
