import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))
sys.path.insert(0,str(ROOT/"runtime"/"jra_source_runtime"))
from jra_zero_touch_source_index_orchestrator import build_zero_touch_source_index_report,build_source_runner_stubs

def mapping():
    return json.load(open(ROOT/"mapping"/"jra_base_index_evidence_mapping_v1.0_20260921.json",encoding="utf-8"))

def source():
    return {
      "family_id":"JRA","race_id":"ZT","source_snapshot_sha256":"SRC",
      "jra_official_runner_universe":{"runners":[
        {"runner_id":"1","horse_no":1,"name":"A","canonical_name":"A","assigned_weight":56.0},
        {"runner_id":"2","horse_no":2,"name":"B","canonical_name":"B","assigned_weight":56.0}
      ]},
      "jra_official_runner_universe_sha256":"U",
      "jra_official_race_card_detail":{"runners":[
        {"runner_id":"1","horse_no":1,"horse_name":"A","career_record":{"wins":1,"seconds":0,"thirds":0,"others":4,"starts":5},"assigned_weight":56.0,"recent_runs":[]},
        {"runner_id":"2","horse_no":2,"horse_name":"B","career_record":{"wins":0,"seconds":1,"thirds":0,"others":5,"starts":6},"assigned_weight":56.0,"recent_runs":[]}
      ]},
      "jra_official_race_card_detail_sha256":"D"
    }

def test_runner_stubs_are_source_only():
    x=build_source_runner_stubs(source())
    assert len(x)==2
    assert x[0]["career_starts"]==5
    assert x[0]["evidence_features"]=={}

def test_zero_touch_report_is_truthful_and_fail_closed():
    r=build_zero_touch_source_index_report(source(),mapping())
    assert r["runner_count"]==2
    assert r["claims"]["source_to_71_feature_state"]=="COMPLETE"
    assert r["claims"]["source_to_20_index_shadow"]=="COMPLETE"
    assert r["production_source_only_formal_base_ready"] is False
    assert r["claims"]["source_to_20_index_production"]=="BLOCKED"
    assert r["claims"]["no_synthesis"] is True
    assert r["shadow_has_all_71_feature_states"] is True
    assert r["shadow_has_20_index_diagnostic"] is True
    assert r["source_feature_trace_schema"]=="KM-JRA-SOURCE-FEATURE-INDEX-TRACE-v1.0-20260927"
    t=r["per_runner_coverage"]["1"]["source_feature_trace"]
    assert t["summary"]["feature_count"]==71
    assert t["features"]["weight_load_fit"]["production_feature_state"]=="SOURCE_GENERATED_PRODUCTION_FEATURE"


def test_unverified_detail_runner_cannot_enlarge_official_universe():
    a=source()
    a["jra_official_race_card_detail"]["runners"].append(
      {"runner_id":"99","horse_no":99,"horse_name":"EXTRA",
       "career_record":{"starts":8}})
    rows=build_source_runner_stubs(a)
    assert [r["runner_id"] for r in rows]==["1","2"]
    assert "99" not in {r["runner_id"] for r in rows}


def test_missing_career_count_is_not_inferred_from_partial_history():
    a=source()
    a["jra_official_race_card_detail"]["runners"][0].pop("career_record")
    a["jra_official_horse_history"]={"runners":{
      "1":{"run_count":2,"runs":[{"date":"2026-09-01"},{"date":"2026-08-01"}]}}}
    rows=build_source_runner_stubs(a)
    assert rows[0]["career_starts"] is None
    assert rows[0]["newcomer"] is None
    a["jra_official_horse_history"]["runners"]["1"]["total_starts"]=11
    rows=build_source_runner_stubs(a)
    assert rows[0]["career_starts"]==11
    assert rows[0]["newcomer"] is False


def test_duplicate_official_id_rejected_before_shadow_index_generation():
    a=source()
    a["jra_official_runner_universe"]["runners"].append(
      {"runner_id":"1","horse_no":1,"name":"CLONE"})
    import pytest
    with pytest.raises(ValueError,match="JRA_OFFICIAL_RUNNER_UNIVERSE_INVALID"):
        build_zero_touch_source_index_report(a,mapping())
