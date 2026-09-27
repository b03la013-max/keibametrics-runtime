import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))

from family_prediction_utility import build_snapshot,validate_snapshot,FamilyPredictionUtilityError

def _write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False),encoding="utf-8")
    return str(path)

def test_family_prediction_utility_snapshot_separates_dynamic_state_and_freezes_production(tmp_path):
    cand=tmp_path/"candidate.json"
    krs=tmp_path/"krs.json"
    mec=tmp_path/"mec.json"
    pfs=tmp_path/"pfs.json"
    hsn=tmp_path/"hsn.json"
    nky=tmp_path/"nky.json"

    _write(cand,{
      "status":"WAITING_R30","eligible_race_count":15,"target_eligible_races":30,
      "winner_capture_rate":0.46,"p2_capture_rate":0.6,"p3_capture_rate":0.66,
      "ordered_pair_capture_rate":0.33,"exact_capture_rate":0.26,"top3_set_capture_rate":0.46,
      "mean_winner_static_rank":3.9,"mean_candidate_vs_market_winner_rank_gain":None,
      "mean_candidate_vs_market_top3_rank_gain":None,"automatic_promotion":False
    })
    _write(krs,{
      "status":"WAITING_R30","eligible_races":4,"required_races":30,
      "metrics":{"pair_rescue_races":1},"automatic_production_promotion":False
    })
    _write(mec,{
      "status":"WAITING_30","eligible_races":3,"target_eligible_races":30,
      "automatic_promotion":False,"production_effect":"NONE"
    })
    _write(pfs,{
      "candidate_forward_oos":{
        "status":"MEASUREMENT-ONLY / NON-PRODUCTION / NO-AUTO-PROMOTION",
        "eligible_race_count":15,"settled_race_count":8,"settlement_coverage_pct":53.3,
        "aggregate":{"investment":18900,"return":51940,"investment_weighted_pfs":274.8},
        "robustness":{
          "excluding_largest_return":{"investment_weighted_pfs":65.1},
          "excluding_top3_returns":{"investment_weighted_pfs":0},
          "largest_return_share_pct":79.1,"max_drawdown":5000,"max_losing_streak":2
        },
        "mec_capital_density":{"tiers":{"CORE":{"capital":12000}}},
        "tier_pfs":{"tiers":{"CORE":{"pfs":0}}},
        "production_effect":"NONE"
      }
    })
    _write(hsn,{
      "decision":{"canon_revision_required":False},
      "venue_authority":{"current_venue_candidate":"HSN Rev.4"},
      "final_verdict":"KEEP"
    })
    _write(nky,{
      "decision":{"canon_revision_required":False},
      "venue_authority":{"current_venue_candidate":"NKY Rev.4"},
      "final_verdict":"KEEP"
    })

    contract=tmp_path/"contract.json"
    _write(contract,{
      "profile_id":"KM-FAMILY-PREDICTION-UTILITY-CONTRACT-20260927-R1",
      "production_effect":"NONE",
      "automatic_promotion":False,
      "system_objective_order":["PREDICTION_UTILITY","EXECUTION_CONFORMANCE"],
      "hard_distinctions":["FORMAL_PASS != PREDICTION_SUCCESS"],
      "first_material_failure_owner_order":["STATIC_PREDICTION","MEC"],
      "required_trace_contract":{"source_feature_trace_schema":"TRACE"},
      "production_freeze":{"numerical_change":"NONE","prediction_behavior_change":"NONE"},
      "dynamic_state_sources":{
        "source_candidate_oos":str(cand),"krs_oos":str(krs),"mec_r4_oos":str(mec),
        "pfs_grand_review":str(pfs),"hsn_venue_audit":str(hsn),"nky_venue_audit":str(nky)
      }
    })

    s=build_snapshot(contract)
    validate_snapshot(s)
    assert s["system_objective_order"][0]=="PREDICTION_UTILITY"
    assert s["dynamic_state"]["source_derived_candidate"]["eligible_races"]==15
    assert s["dynamic_state"]["krs"]["role"]=="SECOND_OPINION_ENGINE"
    assert s["dynamic_state"]["candidate_pfs"]["headline_pfs"]==274.8
    assert s["dynamic_state"]["candidate_pfs"]["largest_return_excluded_pfs"]==65.1
    assert s["venue_canon"]["HSN"]["canon_revision_required"] is False
    assert s["venue_canon"]["NKY"]["canon_revision_required"] is False
    assert s["production_freeze"]["numerical_change"]=="NONE"
    assert s["production_effect"]=="NONE"
    assert s["promotion"]["automatic"] is False
    assert s["sha256"]

def test_family_prediction_utility_rejects_production_leak(tmp_path):
    contract=tmp_path/"bad.json"
    contract.write_text(json.dumps({
      "profile_id":"KM-FAMILY-PREDICTION-UTILITY-CONTRACT-20260927-R1",
      "production_effect":"PRODUCTION_CHANGE",
      "automatic_promotion":False,
      "production_freeze":{"numerical_change":"NONE","prediction_behavior_change":"NONE"},
      "dynamic_state_sources":{}
    }),encoding="utf-8")
    try:
        build_snapshot(contract)
        assert False,"expected rejection"
    except FamilyPredictionUtilityError as exc:
        assert "PRODUCTION_EFFECT" in str(exc)
