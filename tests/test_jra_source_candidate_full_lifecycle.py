import copy,hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))

from jra_evidence_to_base_production import load_mapping
from jra_source_candidate_numerical import materialize_source_candidate
from jra_source_candidate_semantics import build_candidate_semantics
from jra_source_candidate_oos import pre_result_record,evaluate_result
from formal_request_validator import validate_pre_krs_request
from minimum_efficient_coverage import build_mec_plan,validate_mec_plan
from capital_policy import resolve_capital_policy

MAPPING=ROOT/"mapping"/"jra_base_index_evidence_mapping_v1.0_20260921.json"

def source():
    x={
      "family_id":"JRA","race_id":"TEST-CAND",
      "jra_race_context":{"venue_name":"阪神","distance_m":1200,"surface":"ダ","going":"良"},
      "source_race_context":{"race_date":"2026-09-26"},
      "jra_official_runner_universe_sha256":"b"*64,
      "jra_official_runner_universe":{"runners":[
        {"runner_id":"1","horse_no":1,"canonical_name":"A","name":"A","status":"ACTIVE","assigned_weight":56.0},
        {"runner_id":"2","horse_no":2,"canonical_name":"B","name":"B","status":"ACTIVE","assigned_weight":56.0},
        {"runner_id":"3","horse_no":3,"canonical_name":"C","name":"C","status":"ACTIVE","assigned_weight":56.0},
        {"runner_id":"4","horse_no":4,"canonical_name":"D","name":"D","status":"ACTIVE","assigned_weight":56.0},
      ]},
      "jra_official_race_card_detail_sha256":"c"*64,
      "jra_official_race_card_detail":{"runners":[
        {"runner_id":"1","horse_no":1,"horse_name":"A","career_record":{"starts":6},"assigned_weight":56.0,"current_body_weight":480,"current_body_weight_change":2,"win_odds":3.0,"popularity_rank":1,"jockey":"J1","trainer":"T1","recent_runs":[{"date":"2026-09-01","venue":"阪神","finish":1,"field_size":12,"distance_m":1200,"surface":"ダ","going":"良","body_weight":478,"final3f":36.1,"margin":0.0,"passing_positions_raw":"2 2"}]},
        {"runner_id":"2","horse_no":2,"horse_name":"B","career_record":{"starts":6},"assigned_weight":56.0,"current_body_weight":490,"current_body_weight_change":0,"win_odds":5.0,"popularity_rank":2,"jockey":"J2","trainer":"T2","recent_runs":[{"date":"2026-09-01","venue":"阪神","finish":2,"field_size":12,"distance_m":1200,"surface":"ダ","going":"良","body_weight":490,"final3f":36.4,"margin":0.2,"passing_positions_raw":"3 3"}]},
        {"runner_id":"3","horse_no":3,"horse_name":"C","career_record":{"starts":6},"assigned_weight":56.0,"current_body_weight":500,"current_body_weight_change":4,"win_odds":8.0,"popularity_rank":3,"jockey":"J3","trainer":"T3","recent_runs":[{"date":"2026-09-01","venue":"阪神","finish":5,"field_size":12,"distance_m":1200,"surface":"ダ","going":"良","body_weight":496,"final3f":37.0,"margin":0.8,"passing_positions_raw":"5 5"}]},
        {"runner_id":"4","horse_no":4,"horse_name":"D","career_record":{"starts":6},"assigned_weight":56.0,"current_body_weight":510,"current_body_weight_change":-2,"win_odds":12.0,"popularity_rank":4,"jockey":"J4","trainer":"T4","recent_runs":[{"date":"2026-09-01","venue":"阪神","finish":8,"field_size":12,"distance_m":1200,"surface":"ダ","going":"良","body_weight":512,"final3f":37.5,"margin":1.3,"passing_positions_raw":"8 8"}]},
      ]},
      "jra_official_horse_history":{"runners":{
        "1":{"runs":[{"date":"2026-09-01","venue":"阪神","finish":1,"field_size":12,"distance_m":1200,"surface":"ダ","going":"良","body_weight":478,"final3f":36.1,"margin":0.0,"passing_positions_raw":"2 2"}]},
        "2":{"runs":[{"date":"2026-09-01","venue":"阪神","finish":2,"field_size":12,"distance_m":1200,"surface":"ダ","going":"良","body_weight":490,"final3f":36.4,"margin":0.2,"passing_positions_raw":"3 3"}]},
        "3":{"runs":[{"date":"2026-09-01","venue":"阪神","finish":5,"field_size":12,"distance_m":1200,"surface":"ダ","going":"良","body_weight":496,"final3f":37.0,"margin":0.8,"passing_positions_raw":"5 5"}]},
        "4":{"runs":[{"date":"2026-09-01","venue":"阪神","finish":8,"field_size":12,"distance_m":1200,"surface":"ダ","going":"良","body_weight":512,"final3f":37.5,"margin":1.3,"passing_positions_raw":"8 8"}]},
      }}
    }
    projection={k:v for k,v in x.items() if k!="source_snapshot_sha256"}
    x["source_snapshot_sha256"]=hashlib.sha256(
        json.dumps(projection,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    ).hexdigest()
    return x

def test_candidate_full_numerical_transport_semantic_mec():
    mp=load_mapping(MAPPING)
    req={
      "race_id":"TEST-CAND","family_id":"JRA","venue_id":"HSN",
      "race":{"venue":"阪神","surface":"ダ","distance":1200,"course":"右","going":"良","class":"2勝"},
      "environment":{"track":"ダ","weather":"晴"},
      "run_count":5000,"seed":17,
      "prediction_cutoff":"2026-09-26T16:00:00+09:00",
      "temporal_mode":"POST-START-REPLAY",
      "orchestration_ref":{"authority":"BASE44","execution_session_id":"candidate-test","session_nonce":"n","created_at":"2026-09-26T16:00:00+09:00"},
    }
    req=materialize_source_candidate(req,source(),mp)
    req=build_candidate_semantics(req)
    req["source_snapshot"]={k:v for k,v in source().items() if k!="source_snapshot_sha256"}
    assert req["candidate_numerical_summary"]["required_count"]==80
    assert req["candidate_numerical_summary"]["calculated_count"]==80
    for r in req["runners"]:
        assert len(r["canonical_components"])==20
        assert len(req["krs_input_data"]["horses"][int(r["runner_id"])-1]["hsv"])==30
        assert len(req["krs_input_data"]["horses"][int(r["runner_id"])-1]["static"])==11
        assert all(x["production_authority"] is False for x in r["canonical_components"].values())
    pre=validate_pre_krs_request(req)
    assert pre["runner_count"]==4
    assert pre["canonical_component_count"]==80
    mec=build_mec_plan(req,None,strict_head_closure=True,min_stake=100)
    check=validate_mec_plan(mec)
    cap=resolve_capital_policy(req,mec)
    assert check["material_coverage_ratio"]==1.0
    assert cap["decision"]=="EXECUTE_RECOMMENDATION_PORTFOLIO"
    req["candidate_frozen_at"]="2026-09-26T15:59:00+09:00"
    rec=pre_result_record(req)
    assert rec["production_effect"]=="NONE"
    assert rec["oos_eligible"] is False
    ev=evaluate_result(rec,[1,2,3])
    assert ev["production_effect"]=="NONE"
    assert ev["automatic_promotion"] is False
