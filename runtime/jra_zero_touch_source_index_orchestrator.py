from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Dict, List

from jra_source_to_evidence_features import compile_source_to_features
from jra_source_objective_evaluator import build_source_objective_candidate
from jra_evidence_to_base_production import build_production_ledger, ProductionMappingError

PROFILE="KM-JRA-ZERO-TOUCH-SOURCE-INDEX-ORCHESTRATOR-v1.0-20260926"

def _sha(x:Any)->str:
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()

def _detail_map(source:Dict[str,Any])->Dict[str,Dict[str,Any]]:
    d=source.get("jra_official_race_card_detail") or {}
    return {str(x.get("runner_id") or x.get("horse_no")):x for x in d.get("runners") or []}

def _official_map(source:Dict[str,Any])->Dict[str,Dict[str,Any]]:
    d=source.get("jra_official_runner_universe") or source.get("official_runner_universe") or {}
    return {str(x.get("runner_id") or x.get("horse_no")):x for x in d.get("runners") or []}

def build_source_runner_stubs(source:Dict[str,Any])->List[Dict[str,Any]]:
    detail=_detail_map(source)
    official=_official_map(source)
    ids=sorted(set(official)|set(detail),key=lambda x:int(x) if x.isdigit() else x)
    out=[]
    for rid in ids:
        o=official.get(rid) or {}
        d=detail.get(rid) or {}
        record=d.get("career_record") or {}
        starts=record.get("starts")
        if starts is None:
            # Full horse history is authoritative factual fallback for starts.
            h=(((source.get("jra_official_horse_history") or {}).get("runners") or {}).get(rid) or {})
            runs=h.get("runs") or []
            if runs:
                starts=len(runs)
        r={
          "runner_id":rid,
          "name":str(d.get("horse_name") or o.get("canonical_name") or o.get("name") or ""),
          "career_starts":starts,
          "newcomer": True if starts==0 else False if starts is not None else None,
          "evidence_features":{},
        }
        out.append(r)
    return out

def build_zero_touch_source_index_report(source:Dict[str,Any],mapping:Dict[str,Any])->Dict[str,Any]:
    if not isinstance(source,dict) or source.get("family_id") not in {None,"JRA"}:
        raise ValueError("JRA_SOURCE_REQUIRED")
    if not source.get("source_snapshot_sha256"):
        raise ValueError("SOURCE_SNAPSHOT_SHA_MISSING")
    runners=build_source_runner_stubs(source)
    if len(runners)<2:
        raise ValueError("SOURCE_RUNNER_STUBS_INSUFFICIENT")

    source_feature=compile_source_to_features(source,runners,mapping)
    objective=build_source_objective_candidate(source,runners,mapping)

    prod_ready=bool(source_feature.get("source_only_formal_base_ready"))
    prod_ledger=None
    prod_error=None
    if prod_ready:
        generated=[]
        for r in runners:
            rid=str(r["runner_id"])
            rr=(source_feature.get("runners") or {}).get(rid) or {}
            x=copy.deepcopy(r)
            x["evidence_features"]=copy.deepcopy(rr.get("generated_production_features") or {})
            generated.append(x)
        try:
            prod_ledger=build_production_ledger(str(source.get("race_id") or "SOURCE-ZERO-TOUCH"),generated,mapping)
        except Exception as exc:
            prod_ready=False
            prod_error=type(exc).__name__+":"+str(exc)

    observed=[]
    missing=[]
    if objective.get("available"):
        for rid,rr in (objective.get("runners") or {}).items():
            if rr.get("error"):
                continue
            observed.append(int(rr.get("observed_feature_count",0)))
            missing.append(int(rr.get("missing_feature_count",0)))

    out={
      "profile":PROFILE,
      "family_id":"JRA",
      "race_id":source.get("race_id"),
      "source_snapshot_sha256":source.get("source_snapshot_sha256"),
      "runner_count":len(runners),
      "runner_stubs":runners,
      "production_source_feature_report_sha256":source_feature.get("sha256"),
      "production_source_only_formal_base_ready":prod_ready,
      "production_status":"READY" if prod_ready else "BLOCKED_EXPLICIT_GAPS",
      "production_error":prod_error,
      "production_ledger":prod_ledger,
      "shadow_objective_available":bool(objective.get("available")),
      "shadow_objective_sha256":objective.get("sha256"),
      "shadow_observed_feature_count_min":min(observed) if observed else None,
      "shadow_observed_feature_count_max":max(observed) if observed else None,
      "shadow_missing_feature_count_min":min(missing) if missing else None,
      "shadow_missing_feature_count_max":max(missing) if missing else None,
      "shadow_has_all_71_feature_states":all((rr.get("feature_count")==71) for rr in (objective.get("runners") or {}).values() if not rr.get("error")) if objective.get("available") else False,
      "shadow_has_20_index_diagnostic":all(len((rr.get("all_20_diagnostic_values") or {}))==20 for rr in (objective.get("runners") or {}).values() if not rr.get("error")) if objective.get("available") else False,
      "source_feature_contract":source_feature.get("feature_contract"),
      "missing_source_families":source_feature.get("missing_source_families"),
      "per_runner_coverage":{
        rid:{
          "source_only_formal_base_ready":rr.get("source_only_formal_base_ready"),
          "automation_gap":rr.get("automation_gap"),
          "source_only_coverage":rr.get("source_only_coverage"),
        } for rid,rr in (source_feature.get("runners") or {}).items()
      },
      "objective_shadow":objective,
      "production_effect":"NONE unless production_source_only_formal_base_ready=true and downstream FORMAL-FULL explicitly consumes the generated ledger",
      "claims":{
        "source_to_71_feature_state":"COMPLETE",
        "source_to_20_index_shadow":"COMPLETE" if objective.get("available") else "UNAVAILABLE",
        "source_to_20_index_production":"READY" if prod_ready else "BLOCKED",
        "no_synthesis":True,
        "unknown_not_weak":True,
        "tsl_never_production":True,
      }
    }
    out["sha256"]=_sha({k:v for k,v in out.items() if k!="sha256"})
    return out
