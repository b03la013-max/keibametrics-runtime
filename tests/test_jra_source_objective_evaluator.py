import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))
from jra_source_objective_evaluator import build_source_objective_candidate

def mapping():
    return json.load(open(ROOT/"mapping"/"jra_base_index_evidence_mapping_v1.0_20260921.json",encoding="utf-8"))

def source():
    return {
      "family_id":"JRA","race_id":"T","source_snapshot_sha256":"SRC","jra_official_race_card_detail_sha256":"DET",
      "source_race_context":{"race_date":"2026-09-26"},
      "jra_race_context":{"venue_name":"中山","distance_m":1800,"surface":"ダ"},
      "jra_official_race_card_detail":{
        "runners":[
          {"runner_id":"1","horse_no":1,"horse_name":"A","assigned_weight":55.0,"jockey":"甲","popularity_rank":1,
           "current_body_weight":480,"current_body_weight_change":2,
           "career_record":{"wins":2,"seconds":1,"thirds":1,"others":6,"starts":10},
           "sire":"S1","dam":"D1","damsire":"DS1",
           "recent_runs":[
             {"date":"2026-09-01","venue":"中山","finish":1,"field_size":12,"distance_m":1800,"surface":"ダ","going":"良","body_weight":478,"final3f":37.0,"margin":-0.2,"passing_positions":[2,2,1,1],"race_class_text":"2勝クラス","jockey":"甲"},
             {"date":"2026-08-01","venue":"東京","finish":4,"field_size":14,"distance_m":1600,"surface":"ダ","going":"良","body_weight":476,"final3f":37.4,"margin":0.6,"passing_positions":[4,4,4,4],"race_class_text":"2勝クラス","jockey":"乙"},
           ]},
          {"runner_id":"2","horse_no":2,"horse_name":"B","assigned_weight":57.0,"jockey":"丙","popularity_rank":2,
           "current_body_weight":500,"current_body_weight_change":10,
           "career_record":{"wins":1,"seconds":0,"thirds":1,"others":8,"starts":10},
           "sire":"S2","dam":"D2","damsire":"DS2",
           "recent_runs":[
             {"date":"2026-09-01","venue":"東京","finish":8,"field_size":12,"distance_m":1600,"surface":"ダ","going":"良","body_weight":490,"final3f":39.0,"margin":2.0,"passing_positions":[8,8,8,8],"race_class_text":"2勝クラス","jockey":"丙"},
             {"date":"2026-08-01","venue":"中山","finish":5,"field_size":10,"distance_m":1800,"surface":"ダ","going":"稍重","body_weight":492,"final3f":38.5,"margin":1.0,"passing_positions":[6,6,5,5],"race_class_text":"2勝クラス","jockey":"丙"},
           ]}
        ]
      }
    }

def test_objective_candidate_generates_complete_71_feature_diagnostic_and_20_indices():
    r=build_source_objective_candidate(source(),[{"runner_id":"1","career_starts":10},{"runner_id":"2","career_starts":10}],mapping())
    assert r["available"] is True
    assert r["runner_count"]==2
    for rr in r["runners"].values():
        assert rr["feature_count"]==71
        assert len(rr["base_indices"])==13
        assert len(rr["derived_indices"])==7
        assert len(rr["all_20_diagnostic_values"])==20
        assert rr["missing_feature_count"]>0
    assert r["candidate_ranking"][0]["runner_id"]=="1"

def test_missing_features_are_not_promoted_to_production():
    r=build_source_objective_candidate(source(),[{"runner_id":"1","career_starts":10},{"runner_id":"2","career_starts":10}],mapping())
    f=r["runners"]["1"]["features"]["workout_speed"]
    assert f["missing"] is True
    assert f["production_authority"] is False
    assert r["production_effect"]=="NONE"

def test_tsl_is_not_used_by_objective_candidate():
    s=source()
    s["tsl_public_shadow_evidence"]={"runners":[{"horse_no":2,"mark":"◎","win_vote":{"value":99}}]}
    r=build_source_objective_candidate(s,[{"runner_id":"1","career_starts":10},{"runner_id":"2","career_starts":10}],mapping())
    assert r["runners"]["2"]["features"]["external_index_support"]["missing"] is True
