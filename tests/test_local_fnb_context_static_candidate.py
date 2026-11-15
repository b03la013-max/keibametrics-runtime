"""Synthetic correctness, never real source/model adoption or OOS evidence."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from runtime import local_fnb_context_static_candidate as m

NOW="2026-11-03T03:30:00+00:00"


def seal(doc):
    doc.pop("sha256",None);doc["sha256"]=m.sha(doc);return doc


def fixture():
    # Names and numeric facts deliberately synthetic, not an official card.
    def row(seq,finish):
        return {"event_date":"2026-10-01","field_size":10,"finish":finish,
                "printed_position_sequence":seq,"distance_m":1200,"same_distance":True,
                "source_raw_sha256":"a"*64,"source_fetched_at":"2026-11-03T02:00:00+00:00"}
    histories=[[row([2,2,2],2)],[row([4,4,4],2)],[row([8,7,6],3)],[],[row([2,2,2],1)]]
    p={"profile":m.OBSERVATION_PROFILE,"venue_canon":m.CANON,"classification":m.CLASSIFICATION,
       "race_id":"KM-LOCAL-FNB-20261103-R02-PRIVATE-R1","raw_to_normalized_tables_equal":True,
       "source_freeze_at":"2026-11-03T02:01:00+00:00","generated_at":"2026-11-03T03:00:00+00:00",
       "source_snapshot_sha256":"b"*64,"source_receipt_sha256":"c"*64,"raw_card_sha256":"a"*64,
       "header":{"distance":1200,"surface":"dirt","class":"SYNTHETIC"},
       "runners":[{"runner_id":str(i),"name":"SYNTHETIC-"+str(i),"historical_fnb_observations":v}
                  for i,v in enumerate(histories,1)]}
    return seal(p)


def test_profile_exact():
    path=Path(__file__).resolve().parents[1]/"profiles/local_fnb_context_static_candidate_v0.1_20261103.json"
    assert json.loads(path.read_text())==m.specification()


def test_real_context_is_consumed_and_ablation_is_not_second_owner():
    context=m.build_context(fixture(),generated_at=NOW)
    out=m.compare_context_ablation(context,frozen_at=NOW)
    full=out["context_prediction"]
    assert full["independent_BC_pair"] is False
    assert out["rank_changed_columns"]
    assert out["head_local_P2_changed"]
    assert out["pair_conditioned_Third_changed"]
    assert all(len(full["column_rankings"][c]["rows"])==5 for c in ("W","P2","P3"))
    unknown=next(x for x in full["column_rankings"]["W"]["rows"] if x["runner_id"]=="4")
    assert unknown["rank"] is None and unknown["rank_interval"]=={"min":1,"max":5}
    assert full["roles"]["4"]==["W_UNKNOWN_POSSIBLE","P2_UNKNOWN_POSSIBLE","P3_UNKNOWN_PROTECTED"]
    assert any(p.get("head")=="4" for p in full["unresolved_semantic_paths"])
    assert any(p.get("second")=="4" for p in full["unresolved_semantic_paths"])
    assert any(p.get("third")=="4" for p in full["unresolved_semantic_paths"])
    assert full["KRS_executed"] is False
    assert full["ticket_generation_executed"] is False
    assert not full["production_adopted"]
    assert not context["formal_context_ready"]
    assert all(r.get("reachable_position_range",{}).get("corner3") is None
               for r in context["runners"] if r["status"]!="UNKNOWN")


def test_pre_krs_draft_keeps_numeric_arrays_and_has_no_authority():
    packet=fixture();context=m.build_context(packet,generated_at=NOW)
    original={"race":{"race_id":packet["race_id"],"venue":"FNB","distance_m":1200,"surface":"DIRT"},
              "horses":[{"horse_no":i,"hsv":{"base_competitive_ability":52},
                         "static":{"tpi":52},"static_roles":[]} for i in range(1,6)]}
    before=deepcopy(original)
    result=m.compare_context_ablation(context,frozen_at=NOW,upstream_krs_input=original)
    q=result["context_prediction"]["PRE_KRS_input"]
    assert original==before
    for a,b in zip(q["horses"],original["horses"]):
        assert a["hsv"]==b["hsv"] and a["static"]==b["static"]
    assert not q["keibametrics_input_authority"]["model_adoption_verified"]
    assert result["PRE_KRS_role_semantics_changed"]
    assert result["PRE_KRS_physical_numeric_arrays_changed"] is False
    wrong=deepcopy(original);wrong["race"]["distance_m"]=1600
    with pytest.raises(ValueError,match="RACE_IDENTITY"):m.predict(context,frozen_at=NOW,upstream_krs_input=wrong)


def test_all_unknown_does_not_invent_rank_or_worlds():
    packet=fixture()
    for r in packet["runners"]:r["historical_fnb_observations"]=[]
    context=m.build_context(seal(packet),generated_at=NOW)
    out=m.compare_context_ablation(context,frozen_at=NOW)
    p=out["context_prediction"]
    assert all(p["column_rankings"][c]["front"]==[] for c in ("W","P2","P3"))
    assert p["pair_dispositions"]==[]
    assert len(p["unresolved_semantic_paths"])==5
    assert out["rank_changed_columns"]==[]
    assert out["head_local_P2_changed"] is False
    assert out["pair_conditioned_Third_changed"] is False


@pytest.mark.parametrize("mutation,code",[
    (lambda p:p["runners"][0]["historical_fnb_observations"][0].update(event_date="2026-11-03"),"HISTORICAL_LINEAGE"),
    (lambda p:p["runners"][0]["historical_fnb_observations"][0].update(source_fetched_at="2026-11-03T04:00:00+00:00"),"HISTORICAL_LINEAGE"),
    (lambda p:p["runners"][0]["historical_fnb_observations"][0].update(printed_position_sequence=[0,1]),"POSITIONS_INVALID"),
    (lambda p:p["runners"][0]["historical_fnb_observations"][0].update(same_distance=False),"DISTANCE_FLAG"),
    (lambda p:p["runners"][1].update(runner_id="1"),"UNIVERSE_INVALID"),
])
def test_invalid_inputs_cannot_be_silently_consumed(mutation,code):
    p=fixture();mutation(p)
    with pytest.raises(ValueError,match=code):m.build_context(seal(p),generated_at=NOW)


def test_original_bytes_and_clock_are_bound():
    p=fixture();p["header"]["distance"]=1500
    with pytest.raises(ValueError,match="ORIGINAL_SHA"):m.build_context(p,generated_at=NOW)
    with pytest.raises(ValueError,match="BEFORE_INPUT"):m.build_context(fixture(),generated_at="2026-11-03T02:00:00+00:00")
    ctx=m.build_context(fixture(),generated_at=NOW)
    with pytest.raises(ValueError,match="BEFORE_CONTEXT"):m.predict(ctx,frozen_at="2026-11-03T02:00:00+00:00")


def test_context_unknown_cannot_be_numeric_or_nan():
    c=m.build_context(fixture(),generated_at=NOW)
    c["runners"][3]["metrics"]={"finish":0}
    with pytest.raises(ValueError,match="UNKNOWN_WITH_SYNTHETIC"):m.predict(seal(c),frozen_at=NOW)


def test_pareto_matches_independent_dominance_count_and_interval():
    vectors={"1":(1,0),"2":(0,1),"3":(2,2),"4":None}
    r=m._rank(vectors,list(vectors))
    assert set(r["front"])=={"1","2"}
    assert next(x for x in r["rows"] if x["runner_id"]=="3")["pareto_layer"]==2
    assert next(x for x in r["rows"] if x["runner_id"]=="4")["rank_interval"]=={"min":1,"max":4}


@pytest.mark.parametrize("axis,column,change",[
    ("FPR","W",lambda r:r["FPR"].update(maintenance_loss=1)),
    ("FSD","W",lambda r:r["FSD"].update(overlapping_historical_acquisition_intervals=["1","2","3"])),
    ("LCC","W",lambda r:r["LCC"].update(leadership_maintenance_observations=1)),
    ("RANGE","P2",lambda r:r["reachable_position_range"]["last_reported_hypothesis"].update(max=1)),
    ("STAGE","P2",lambda r:r["stage_cost_topology"].update(Leader=1)),
])
def test_each_mechanism_changes_its_declared_role_comparison(axis,column,change):
    context=m.build_context(fixture(),generated_at=NOW)
    before=m.predict(context,frozen_at=NOW)
    change(context["runners"][4]);after=m.predict(seal(context),frozen_at=NOW)
    def vector(p):return next(x["comparison_vector"] for x in p["column_rankings"][column]["rows"] if x["runner_id"]=="5")
    assert vector(before)!=vector(after),axis
    assert before["production_adopted"] is after["production_adopted"] is False
