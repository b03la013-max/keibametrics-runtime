from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

CONTRACT_PATH = Path("profiles/family_prediction_utility_contract_20260927_R1.json")
CURRENT_PATH = Path("runtime/family_prediction_utility/current.json")

class FamilyPredictionUtilityError(ValueError):
    pass

def _load(path: str | Path) -> Dict[str, Any]:
    p=Path(path)
    if not p.exists():
        raise FamilyPredictionUtilityError(f"MISSING_REQUIRED_ARTIFACT:{p}")
    with p.open(encoding="utf-8") as fh:
        obj=json.load(fh)
    if not isinstance(obj,dict):
        raise FamilyPredictionUtilityError(f"ARTIFACT_NOT_OBJECT:{p}")
    return obj

def _sha(obj: Dict[str, Any]) -> str:
    payload=json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def _candidate_pfs(pfs: Dict[str, Any]) -> Dict[str, Any]:
    c=pfs.get("candidate_forward_oos") or {}
    agg=c.get("aggregate") or {}
    rob=c.get("robustness") or {}
    density=c.get("mec_capital_density") or {}
    tier=(c.get("tier_pfs") or {}).get("tiers") or {}
    return {
        "status":c.get("status"),
        "eligible_race_count":c.get("eligible_race_count"),
        "settled_race_count":c.get("settled_race_count"),
        "settlement_coverage_pct":c.get("settlement_coverage_pct"),
        "investment":agg.get("investment"),
        "return":agg.get("return"),
        "headline_pfs":agg.get("investment_weighted_pfs"),
        "largest_return_excluded_pfs":(rob.get("excluding_largest_return") or {}).get("investment_weighted_pfs"),
        "top3_returns_excluded_pfs":(rob.get("excluding_top3_returns") or {}).get("investment_weighted_pfs"),
        "largest_return_share_pct":rob.get("largest_return_share_pct"),
        "max_drawdown":rob.get("max_drawdown"),
        "max_losing_streak":rob.get("max_losing_streak"),
        "capital_density":density.get("tiers") or {},
        "tier_pfs":tier,
        "production_effect":c.get("production_effect"),
    }

def build_snapshot(contract_path: str | Path=CONTRACT_PATH) -> Dict[str, Any]:
    contract=_load(contract_path)
    if contract.get("profile_id")!="KM-FAMILY-PREDICTION-UTILITY-CONTRACT-20260927-R1":
        raise FamilyPredictionUtilityError("CONTRACT_ID_MISMATCH")
    if contract.get("production_effect")!="NONE":
        raise FamilyPredictionUtilityError("CONTRACT_PRODUCTION_EFFECT_MUST_BE_NONE")
    if contract.get("automatic_promotion") is not False:
        raise FamilyPredictionUtilityError("CONTRACT_AUTO_PROMOTION_FORBIDDEN")
    freeze=contract.get("production_freeze") or {}
    if freeze.get("numerical_change")!="NONE" or freeze.get("prediction_behavior_change")!="NONE":
        raise FamilyPredictionUtilityError("PRODUCTION_FREEZE_VIOLATION")

    sources=contract.get("dynamic_state_sources") or {}
    candidate=_load(sources["source_candidate_oos"])
    krs=_load(sources["krs_oos"])
    mec=_load(sources["mec_r4_oos"])
    pfs=_load(sources["pfs_grand_review"])
    hsn=_load(sources["hsn_venue_audit"])
    nky=_load(sources["nky_venue_audit"])

    if candidate.get("automatic_promotion") is not False:
        raise FamilyPredictionUtilityError("CANDIDATE_AUTO_PROMOTION_FORBIDDEN")
    if krs.get("automatic_production_promotion") is not False:
        raise FamilyPredictionUtilityError("KRS_AUTO_PROMOTION_FORBIDDEN")
    if mec.get("automatic_promotion") is not False:
        raise FamilyPredictionUtilityError("MEC_AUTO_PROMOTION_FORBIDDEN")
    if (pfs.get("candidate_forward_oos") or {}).get("production_effect")!="NONE":
        raise FamilyPredictionUtilityError("CANDIDATE_PFS_PRODUCTION_LEAK")
    if (hsn.get("decision") or {}).get("canon_revision_required") is not False:
        raise FamilyPredictionUtilityError("HSN_UNEXPECTED_CANON_REVISION")
    if (nky.get("decision") or {}).get("canon_revision_required") is not False:
        raise FamilyPredictionUtilityError("NKY_UNEXPECTED_CANON_REVISION")

    dynamic={
        "source_derived_candidate":{
            "status":candidate.get("status"),
            "eligible_races":candidate.get("eligible_race_count"),
            "target_races":candidate.get("target_eligible_races"),
            "winner_capture_rate":candidate.get("winner_capture_rate"),
            "p2_capture_rate":candidate.get("p2_capture_rate"),
            "p3_capture_rate":candidate.get("p3_capture_rate"),
            "ordered_pair_capture_rate":candidate.get("ordered_pair_capture_rate"),
            "exact_capture_rate":candidate.get("exact_capture_rate"),
            "top3_set_capture_rate":candidate.get("top3_set_capture_rate"),
            "mean_winner_static_rank":candidate.get("mean_winner_static_rank"),
            "candidate_vs_market_winner_rank_gain":candidate.get("mean_candidate_vs_market_winner_rank_gain"),
            "candidate_vs_market_top3_rank_gain":candidate.get("mean_candidate_vs_market_top3_rank_gain"),
            "automatic_promotion":False,
        },
        "krs":{
            "status":krs.get("status"),
            "eligible_races":krs.get("eligible_races"),
            "target_races":krs.get("required_races"),
            "metrics":krs.get("metrics") or {},
            "automatic_production_promotion":False,
            "role":"SECOND_OPINION_ENGINE",
        },
        "mec_r4":{
            "status":mec.get("status"),
            "eligible_races":mec.get("eligible_races"),
            "target_races":mec.get("target_eligible_races"),
            "production_effect":mec.get("production_effect"),
            "automatic_promotion":False,
        },
        "candidate_pfs":_candidate_pfs(pfs),
    }

    snapshot={
        "profile":"KM-FAMILY-PREDICTION-UTILITY-CURRENT-v1.0-20260927",
        "contract_id":contract.get("profile_id"),
        "status":"ACTIVE / DYNAMIC-MEASUREMENT / PREDICTION-UTILITY-FIRST / NO-AUTO-PROMOTION",
        "system_objective_order":contract.get("system_objective_order"),
        "hard_distinctions":contract.get("hard_distinctions"),
        "first_material_failure_owner_order":contract.get("first_material_failure_owner_order"),
        "trace_contract":contract.get("required_trace_contract"),
        "production_freeze":freeze,
        "dynamic_state":dynamic,
        "venue_canon":{
            "HSN":{
                "candidate":(hsn.get("venue_authority") or {}).get("current_venue_candidate"),
                "canon_revision_required":False,
                "verdict":hsn.get("final_verdict"),
            },
            "NKY":{
                "candidate":(nky.get("venue_authority") or {}).get("current_venue_candidate"),
                "canon_revision_required":False,
                "verdict":nky.get("final_verdict"),
            }
        },
        "current_bottlenecks":[
            "PRODUCTION_SOURCE_TO_FEATURE_EVALUATOR_CLOSURE",
            "STATIC_WINNER_AND_ORDER_ROLE_DISCRIMINATION",
            "KRS_RESCUE_TO_DOWNSTREAM_CONVERSION",
            "MEC_CAPITAL_DENSITY_AND_TAIL_VALUE",
            "ROBUST_PFS_STABILITY"
        ],
        "promotion":{
            "automatic":False,
            "primary_evidence":"FROZEN_UNKNOWN_OOS",
            "explicit_declaration_required":True,
            "candidate_ready":False,
            "krs_ready":False,
            "mec_r4_ready":False,
        },
        "production_effect":"NONE",
    }
    snapshot["sha256"]=_sha(snapshot)
    return snapshot

def validate_snapshot(snapshot: Dict[str, Any]) -> None:
    if snapshot.get("contract_id")!="KM-FAMILY-PREDICTION-UTILITY-CONTRACT-20260927-R1":
        raise FamilyPredictionUtilityError("SNAPSHOT_CONTRACT_MISMATCH")
    if snapshot.get("production_effect")!="NONE":
        raise FamilyPredictionUtilityError("SNAPSHOT_PRODUCTION_EFFECT")
    ds=snapshot.get("dynamic_state") or {}
    if ((ds.get("source_derived_candidate") or {}).get("automatic_promotion")) is not False:
        raise FamilyPredictionUtilityError("SNAPSHOT_CANDIDATE_AUTO_PROMOTION")
    if ((ds.get("krs") or {}).get("automatic_production_promotion")) is not False:
        raise FamilyPredictionUtilityError("SNAPSHOT_KRS_AUTO_PROMOTION")
    if ((ds.get("mec_r4") or {}).get("automatic_promotion")) is not False:
        raise FamilyPredictionUtilityError("SNAPSHOT_MEC_AUTO_PROMOTION")
    freeze=snapshot.get("production_freeze") or {}
    if freeze.get("numerical_change")!="NONE":
        raise FamilyPredictionUtilityError("SNAPSHOT_NUMERICAL_FREEZE_BROKEN")

def write_snapshot(path: str | Path=CURRENT_PATH) -> Dict[str, Any]:
    snapshot=build_snapshot()
    validate_snapshot(snapshot)
    p=Path(path)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(snapshot,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return snapshot

if __name__=="__main__":
    print(json.dumps(write_snapshot(),ensure_ascii=False,sort_keys=True,indent=2))
