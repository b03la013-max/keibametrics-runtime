import json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))

from jra_source_to_evidence_features import compile_source_to_features,attach_source_features_to_request

def _mapping():
    return json.load(open(ROOT/"mapping"/"jra_base_index_evidence_mapping_v1.0_20260921.json",encoding="utf-8"))

def _artifact():
    return {
      "family_id":"JRA",
      "race_id":"T",
      "source_snapshot_sha256":"SRC",
      "jra_official_runner_universe_sha256":"U",
      "jra_official_runner_universe":{
        "runners":[
          {"runner_id":"1","horse_no":1,"name":"A","status":"ACTIVE","assigned_weight":56.0},
          {"runner_id":"2","horse_no":2,"name":"B","status":"ACTIVE","assigned_weight":56.0}
        ]
      },
      "tsl_public_shadow_evidence_sha256":"TSL",
      "tsl_public_shadow_evidence":{
        "production_authority":False,"prediction_authority":False,
        "runners":[
          {"horse_no":1,"horse_name":"A","mark":"◎","win_vote":{"value":9.0},"place_vote":{"value":8.0},"quinella_vote":{"value":7.0},"fracture":{"value":1},"competition":{"value":2},"anomaly":{"value":None}},
          {"horse_no":2,"horse_name":"B","mark":"△","win_vote":{"value":2.0},"place_vote":{"value":3.0},"quinella_vote":{"value":4.0},"fracture":{"value":5},"competition":{"value":6},"anomaly":{"value":1}}
        ]
      }
    }

def test_source_compiler_autofills_only_safe_production_fact_and_isolates_tsl():
    runners=[{"runner_id":"1","name":"A","career_starts":8,"evidence_features":{}},
             {"runner_id":"2","name":"B","career_starts":6,"evidence_features":{}}]
    r=compile_source_to_features(_artifact(),runners,_mapping())
    f=r["runners"]["1"]["generated_production_features"]
    assert f["weight_load_fit"]["category"]=="NEUTRAL"
    assert f["weight_load_fit"]["rule_id"]=="JRA-WEIGHT-EQUAL-CONDITION-v1"
    assert "market_rank" not in f
    assert r["runners"]["1"]["shadow_observation_count"]==1
    assert r["formal_base_ready_after_merge"] is False
    assert "JRA_HORSE_HISTORY" in r["missing_source_families"]

def test_source_compiler_never_silently_overwrites_existing_feature():
    runners=[
      {"runner_id":"1","name":"A","career_starts":8,"evidence_features":{
        "weight_load_fit":{"category":"POSITIVE","rule_id":"JRA-HANDICAP-RELIEF-BAND-v1","evidence_refs":["X"],"source_fact":"authorized existing classification"}
      }},
      {"runner_id":"2","name":"B","career_starts":8,"evidence_features":{}}
    ]
    req={"race_id":"T","runners":runners}
    out=attach_source_features_to_request(req,_artifact(),_mapping())
    assert out["runners"][0]["evidence_features"]["weight_load_fit"]["category"]=="POSITIVE"
    conflicts=out["source_to_evidence_feature_runner_coverage"]["1"]["merge_conflicts"]
    assert conflicts and conflicts[0]["resolution"].startswith("EXISTING_PRESERVED")
    assert out["runners"][0]["source_shadow_observations"][0]["production_authority"] is False
