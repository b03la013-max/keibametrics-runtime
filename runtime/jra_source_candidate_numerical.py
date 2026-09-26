from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Dict, List

from jra_source_objective_evaluator import build_source_objective_candidate
from jra_zero_touch_source_index_orchestrator import build_source_runner_stubs
from jra_krs_input_builder_production import build_krs_input

PROFILE="KM-JRA-SOURCE-DERIVED-CANDIDATE-NUMERICAL-v0.1-20260926"
REQUIRED=["HPI","SSI","CFI","RFI","BVI","JTI","CSI","TRI","BWI","GCI","PRI","KGI","VMI",
          "DCR","TPI","ZAI_WIN","ZAI_PLACE","SRI","F3S","T3I"]

def _sha(x:Any)->str:
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()

def _finite(v:Any)->float:
    if not isinstance(v,(int,float)):
        raise ValueError("CANDIDATE_NUMERIC_NOT_NUMBER:"+repr(v))
    x=float(v)
    if not 0.0<=x<=100.0:
        raise ValueError("CANDIDATE_NUMERIC_OUT_OF_RANGE:"+repr(v))
    return round(x,6)

def materialize_source_candidate(request:Dict[str,Any], source_artifact:Dict[str,Any], mapping:Dict[str,Any])->Dict[str,Any]:
    req=copy.deepcopy(request)
    if str(source_artifact.get("family_id") or "JRA")!="JRA":
        raise ValueError("JRA_SOURCE_REQUIRED")
    source_sha=str(source_artifact.get("source_snapshot_sha256") or "")
    if not source_sha:
        raise ValueError("SOURCE_SNAPSHOT_SHA_MISSING")
    runners=build_source_runner_stubs(source_artifact)
    if len(runners)<2:
        raise ValueError("SOURCE_RUNNER_UNIVERSE_INSUFFICIENT")
    objective=build_source_objective_candidate(source_artifact,runners,mapping)
    if not objective.get("available"):
        raise ValueError("SOURCE_OBJECTIVE_CANDIDATE_UNAVAILABLE:"+str(objective.get("reason")))
    by_obj=objective.get("runners") or {}
    out_runners=[]
    total=0
    for r in runners:
        rid=str(r["runner_id"])
        rr=by_obj.get(rid) or {}
        vals=rr.get("all_20_diagnostic_values") or {}
        if set(vals)!=set(REQUIRED):
            missing=sorted(set(REQUIRED)-set(vals))
            extra=sorted(set(vals)-set(REQUIRED))
            raise ValueError(f"CANDIDATE_20_INDEX_SCHEMA:{rid}:missing={missing}:extra={extra}")
        observed=int(rr.get("observed_feature_count") or 0)
        missing_count=int(rr.get("missing_feature_count") or 0)
        candidate_components={}
        for idx in REQUIRED:
            v=_finite(vals[idx])
            candidate_components[idx]={
                "value":v,
                "terminal_status":"CALCULATED",
                "rule_id":f"KM-JRA-SOURCE-DERIVED-CANDIDATE-{idx}-v0.1",
                "mapping_version":PROFILE,
                "evidence_refs":[source_sha,objective.get("sha256"),f"CANDIDATE:RUNNER:{rid}:{idx}"],
                "source_fact":(
                    f"Source-derived candidate diagnostic {idx}={v:.6f}; "
                    f"observed_features={observed}; missing_features={missing_count}; "
                    "missing feature contributions may be neutralized only inside this non-Production candidate lane."
                ),
                "candidate_only":True,
                "production_authority":False,
                "neutralized_missing_feature_count":missing_count,
                "objective_profile":objective.get("profile"),
            }
            total+=1
        x=copy.deepcopy(r)
        x["canonical_components"]=candidate_components
        x["candidate_source_objective_runner"]= {
            "profile":rr.get("profile"),
            "observed_feature_count":observed,
            "missing_feature_count":missing_count,
            "base_indices":rr.get("base_indices"),
            "derived_indices":rr.get("derived_indices"),
        }
        out_runners.append(x)

    req["runners"]=out_runners
    req["source_snapshot_sha256"]=source_sha
    req["numeric_calculation_requirement"]="FULL_REQUIRED"
    req["base_index_mapping_authority"]={
        "mapping_id":PROFILE,
        "status":"CANDIDATE / NON-PRODUCTION / SOURCE-DERIVED-DIAGNOSTIC",
        "production_authority":False,
        "parent_production_mapping":mapping.get("mapping_id"),
        "source_objective_profile":objective.get("profile"),
    }
    req["candidate_numerical_summary"]={
        "profile":PROFILE,
        "required_count":len(out_runners)*20,
        "calculated_count":total,
        "ruled_hold_count":0,
        "not_applicable_count":0,
        "unresolved_count":0,
        "full_numerical_complete":total==len(out_runners)*20,
        "production_authority":False,
        "prediction_accuracy_claim":False,
        "source_snapshot_sha256":source_sha,
        "source_objective_sha256":objective.get("sha256"),
    }
    req["candidate_source_objective_shadow"]=objective
    req["index_provenance_hash"]=_sha({
        "profile":PROFILE,
        "source_snapshot_sha256":source_sha,
        "runners":{r["runner_id"]:r["canonical_components"] for r in out_runners},
    })
    req=build_krs_input(req,bridge_profile="JRA-KRS-HSV-BRIDGE-v1.0-CANDIDATE-SOURCE-DERIVED-20260926")
    req["explicit_engine_hsv_provenance"]["candidate_only"]=True
    req["explicit_engine_hsv_provenance"]["production_authority"]=False
    req["explicit_engine_hsv_provenance"]["source_objective_sha256"]=objective.get("sha256")
    return req
