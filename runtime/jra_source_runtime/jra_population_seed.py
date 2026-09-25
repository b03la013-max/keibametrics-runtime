from __future__ import annotations
from collections import Counter
from typing import Any, Dict, List
from source_acquisition import sha_obj

PROFILE="KM-JRA-POINT-IN-TIME-POPULATION-SEED-v1.0-20260926"

def _clean(v:Any)->str:
    return str(v or "").strip()

def build_population_seed(artifact:Dict[str,Any])->Dict[str,Any]:
    aux=artifact.get("jra_auxiliary_evidence") or {}
    seed=(aux.get("race_card_population_seed") or {})
    rows:List[Dict[str,Any]]=[]
    for x in seed.get("seeds") or []:
        rows.append({
            "runner_id":str(x.get("runner_id") or x.get("horse_no") or ""),
            "horse_no":x.get("horse_no"),
            "horse_name":_clean(x.get("horse_name")),
            "sire":_clean(x.get("sire")),
            "dam":_clean(x.get("dam")),
            "damsire":_clean(x.get("damsire")),
            "body_weight":x.get("body_weight"),
            "body_weight_change":x.get("body_weight_change"),
        })
    sire=Counter(x["sire"] for x in rows if x.get("sire"))
    damsire=Counter(x["damsire"] for x in rows if x.get("damsire"))
    out={
        "profile":PROFILE,
        "status":"FIELD-CONDITIONED-SEED / POINT-IN-TIME / SELECTION-BIASED / SHADOW / NO-HISTORICAL-RATES",
        "production_authority":False,
        "prediction_authority":False,
        "population_fit_ready":False,
        "runner_count":len(rows),
        "field_seed":rows,
        "sire_field_counts":[{"sire":k,"field_count":v} for k,v in sorted(sire.items())],
        "damsire_field_counts":[{"damsire":k,"field_count":v} for k,v in sorted(damsire.items())],
        "source_auxiliary_sha256":artifact.get("jra_auxiliary_evidence_sha256"),
        "limitations":[
            "Current target-field identity seed only; this is not an unbiased JRA historical population.",
            "No win rate, top3 rate, BVI rate or predictive weight may be inferred from this seed alone.",
            "A future JRA historical-profile adapter must be separately source-verified before population rates are computed.",
            "TSL public shadow data is not used as population authority."
        ]
    }
    out["sha256"]=sha_obj({k:v for k,v in out.items() if k!="sha256"})
    return out

def enrich_with_population_seed(artifact:Dict[str,Any])->Dict[str,Any]:
    out=build_population_seed(artifact)
    artifact["jra_point_in_time_population_seed"]=out
    artifact["jra_point_in_time_population_seed_sha256"]=sha_obj(out)
    artifact["jra_point_in_time_population_profile"]=PROFILE
    return artifact
