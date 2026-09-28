import copy
import json
from pathlib import Path

from runtime.race_day_fast_path import (
    materialization_equivalence,
    materialize_request_fast,
    discover_next_requests,
    prewarm_request,
    compare_production_outputs,
)
from runtime.race_day_fast_reflection import build_fast_reflection

FIXTURE=Path("runtime/family_requests/URW-20260923-R07-FORMAL-R1.json")
RESULT_FIXTURE=Path("runtime/executions/LOCAL-GATEWAY-DURABLE-SMOKE-20260925-R1/RESULT/runs/36131389099/result_receipt_envelope.json")


def load(p):
    return json.load(open(p,encoding="utf-8"))


def req_indices(q):
    x=q["required_indices"]
    if x and isinstance(x[0],dict):
        return [str(z.get("index") or z.get("index_name") or z.get("name") or "") for z in x]
    return [str(z) for z in x]


def test_fast_materialization_is_exact_on_cold_and_warm_cache(tmp_path):
    q=load(FIXTURE)
    idx=req_indices(q)
    first=materialization_equivalence(q,idx,tmp_path)
    assert first["status"]=="PASS"
    second=materialization_equivalence(q,idx,tmp_path)
    assert second["status"]=="PASS"
    assert second["cache_report"]["cache_hits"]==len(q["runners"])
    assert second["full_sha256"]==second["fast_sha256"]


def test_cache_never_restores_unrelated_stale_runner_fields(tmp_path):
    q=load(FIXTURE)
    idx=req_indices(q)
    fast1,rep1=materialize_request_fast(q,idx,cache_root=tmp_path)
    q2=copy.deepcopy(q)
    q2["runners"][0]["name"]="CURRENT-NAME-MUST-SURVIVE"
    fast2,rep2=materialize_request_fast(q2,idx,cache_root=tmp_path)
    assert fast2["runners"][0]["name"]=="CURRENT-NAME-MUST-SURVIVE"
    assert rep2["cache_hits"]==len(q["runners"])
    assert fast1["runners"][0]["canonical_components"]==fast2["runners"][0]["canonical_components"]


def test_required_index_change_invalidates_runner_cache(tmp_path):
    q=load(FIXTURE)
    idx=req_indices(q)
    materialize_request_fast(q,idx,cache_root=tmp_path)
    shortened=idx[:-1]
    fast,rep=materialize_request_fast(q,shortened,cache_root=tmp_path)
    assert rep["cache_hits"]==0
    assert fast["numeric_coverage"]["required_count"]==len(q["runners"])*len(shortened)


def test_fast_reflection_is_small_and_preserves_first_material_failure():
    env=load(RESULT_FIXTURE)
    r=build_fast_reflection(env["artifact"],race_id="TEST")
    assert r["status"]=="RACE-DAY-DIAGNOSTIC-COMPLETE"
    assert r["first_material_failure"]=="PREDICTION_ROLE_W"
    assert r["production_change_authorized"] is False
    assert r["deep_review_required"] is True
    assert "RETROACTIVE_PREDICTION_REWRITE" in r["forbidden"]


def test_production_equivalence_ignores_receipt_time_but_not_ticket_change():
    base={
      "artifact":{
        "final_prediction_package":{
          "static_prediction":{"ranking":[1,2,3]},
          "actual_numerical_calculation":{"calculated_count":3},
          "local_mapping_registry":"M",
          "index_provenance_hash":"P",
          "local_krs_bridge_id":"B",
          "local_krs_input_sha256":"K",
        },
        "minimum_efficient_coverage":{"profile":"MEC","tickets":[{"bet_type":"EXACTA","selection":[1,2],"stake":100}],"material_coverage_ratio":1},
        "capital_policy_decision":{"mode":"NORMAL","decision":"BET","required_capital":100},
        "final_ticket":{"no_bet":False,"total_investment":100,"tickets":[{"bet_type":"EXACTA","selection":[1,2],"stake":100}],"frozen_at":"A"},
        "ticket_transport_trace":{"candidate_source":"X","selection_source":"Y","bet_type_dispositions":[]},
      },
      "receipt":{"timestamp":"A"}
    }
    same=copy.deepcopy(base); same["receipt"]["timestamp"]="B"; same["artifact"]["final_ticket"]["frozen_at"]="B"
    assert compare_production_outputs(base,same)["status"]=="PASS"
    changed=copy.deepcopy(same); changed["artifact"]["final_ticket"]["tickets"][0]["selection"]=[2,1]
    assert compare_production_outputs(base,changed)["status"]=="FAIL"


def test_discover_next_three_requests(tmp_path):
    def write(no):
        p=tmp_path/f"R{no:02d}.json"
        json.dump({
          "family_id":"LOCAL","execution_phase":"FORMAL",
          "venue_id":"FNB","race_date":"2026-09-28","race_no":no,
          "runners":[{"runner_id":"1"}],"required_indices":["HPI-L"]
        },open(p,"w",encoding="utf-8"))
        return p
    current=write(4)
    for n in (1,2,3,5,6,7,8): write(n)
    got=discover_next_requests(current,tmp_path,3)
    assert [json.load(open(p))["race_no"] for p in got]==[5,6,7]


def test_prewarm_nonready_is_nonblocking(tmp_path):
    p=tmp_path/"x.json"
    json.dump({"family_id":"LOCAL","venue_id":"FNB","race_date":"2026-09-28","race_no":2},open(p,"w"))
    r=prewarm_request(p,tmp_path/"cache")
    assert r["status"]=="NOT_PREWARMABLE"
    assert r["reason"]=="RUNNERS_OR_REQUIRED_INDICES_NOT_READY"
