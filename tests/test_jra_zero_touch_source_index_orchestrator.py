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
