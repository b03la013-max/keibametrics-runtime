import json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))

from jra_source_to_evidence_features import compile_source_to_features,attach_source_features_to_request,validate_feature_contract

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


def test_all_71_mapping_features_have_source_family_and_registry_binding():
    m=_mapping()
    rr=json.load(open(ROOT/"mapping"/"jra_evidence_feature_rule_registry_v1.1_20260922.json",encoding="utf-8"))
    c=validate_feature_contract(m,rr)
    assert c["mapping_feature_count"]==71
    assert c["source_family_mapped_count"]==71
    assert c["rule_registry_bound_count"]==71
    assert c["missing_source_map"]==[]

def test_source_only_readiness_and_gap_are_explicit():
    runners=[{"runner_id":"1","name":"A","career_starts":8,"evidence_features":{}},
             {"runner_id":"2","name":"B","career_starts":8,"evidence_features":{}}]
    r=compile_source_to_features(_artifact(),runners,_mapping())
    assert r["source_only_formal_base_ready"] is False
    assert r["runners"]["1"]["source_only_formal_base_ready"] is False
    assert r["runners"]["1"]["automation_gap"]["missing_source_family_count"]>0

def test_tsl_stays_shadow_and_never_autofills_external_index_support():
    runners=[{"runner_id":"1","name":"A","career_starts":8,"evidence_features":{}},
             {"runner_id":"2","name":"B","career_starts":8,"evidence_features":{}}]
    r=compile_source_to_features(_artifact(),runners,_mapping())
    for rr in r["runners"].values():
        assert "external_index_support" not in rr["generated_production_features"]
        assert rr["shadow_observation_count"]==1
        assert rr["shadow_observations"][0]["authority"]=="TSL_PUBLIC_NON_OFFICIAL"


def test_official_detail_autofills_career_starts_and_rule_inputs():
    a=_artifact()
    a["jra_race_context"]={"venue_name":"中山","distance_m":1200,"surface":"ダ"}
    a["source_race_context"]={"race_date":"2026-09-26"}
    a["jra_official_race_card_detail_sha256"]="DETAIL"
    a["jra_official_race_card_detail"]={"runners":[
      {"runner_id":"1","horse_no":1,"horse_name":"A","career_record":{"wins":1,"seconds":1,"thirds":1,"others":3,"starts":6},
       "win_odds":5.7,"popularity_rank":2,"assigned_weight":56.0,"jockey":"J1","trainer":"T1","trainer_base":"美浦",
       "sire":"S1","dam":"D1","damsire":"DS1","current_body_weight":470,"current_body_weight_change":2,
       "recent_runs":[
         {"date":"2026-09-05","venue":"中山","finish":3,"field_size":16,"popularity_rank":8,"assigned_weight":54.0,"distance_m":1200,"surface":"ダ","going":"重","body_weight":438,"final3f":36.4,"margin":0.5,"passing_positions_raw":"22"},
         {"date":"2026-07-26","venue":"新潟","finish":9,"field_size":15,"popularity_rank":9,"assigned_weight":53.0,"distance_m":1000,"surface":"芝","going":"不良","body_weight":440,"final3f":35.6,"margin":1.0,"passing_positions_raw":None}
       ]},
      {"runner_id":"2","horse_no":2,"horse_name":"B","career_record":{"wins":0,"seconds":0,"thirds":0,"others":0,"starts":0},
       "win_odds":11.4,"popularity_rank":5,"assigned_weight":56.0,"jockey":"J2","trainer":"T2","trainer_base":"美浦",
       "sire":"S2","dam":"D2","damsire":"DS2","current_body_weight":480,"current_body_weight_change":0,"recent_runs":[]}
    ]}
    req={"race_id":"T","runners":[{"runner_id":"1","name":"A","evidence_features":{}},{"runner_id":"2","name":"B","evidence_features":{}}]}
    out=attach_source_features_to_request(req,a,_mapping())
    assert out["runners"][0]["career_starts"]==6
    assert out["runners"][0]["newcomer"] is False
    assert out["runners"][1]["career_starts"]==0
    assert out["runners"][1]["newcomer"] is True
    ri=out["runners"][0]["source_rule_evaluator_inputs"]
    assert ri["feature_inputs"]["recent_consistency"]["top3_rate"]==0.5
    assert ri["feature_inputs"]["same_course_fit"]["sample_count"]==1
    assert ri["feature_inputs"]["same_distance_fit"]["sample_count"]==1
    assert ri["feature_inputs"]["market_rank"]["popularity_rank"]==2
    assert ri["source_family_inputs"]["JRA_HORSE_HISTORY"]["available"] is True
    # Two deterministic Production evaluators are now bound to exact official facts.
    ef=out["runners"][0]["evidence_features"]
    assert ef["bodyweight_delta_fit"]["category"]=="STRONG"
    assert ef["bodyweight_delta_fit"]["rule_id"]=="JRA-BODYWEIGHT-DELTA-BAND-v1"
    assert ef["market_rank"]["category"]=="WEAK"
    assert ef["market_rank"]["rule_id"]=="JRA-MARKET-RANK-BAND-v1"
    # Other raw official inputs are not silently turned into Production categories.
    assert "recent_performance" not in ef
    assert "jockey_quality" not in ef
    assert "trainer_quality" not in ef
