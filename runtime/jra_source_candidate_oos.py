from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict

from krs_prediction_utility import evaluate_against_result as evaluate_krs_against_result

PROFILE="KM-JRA-SOURCE-DERIVED-CANDIDATE-OOS-TRACKER-v0.2-20260927"
TRACE_SCHEMA="KM-JRA-SOURCE-CANDIDATE-UTILITY-ATTRIBUTION-v1.0-20260927"

def _sha(x:Any)->str:
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()

def _dt(v):
    if not v:
        return None
    return datetime.fromisoformat(str(v).replace("Z","+00:00")).astimezone(timezone.utc)

def _compact_objective_trace(candidate:Dict[str,Any])->Dict[str,Any]:
    obj=candidate.get("candidate_source_objective_shadow") or {}
    out={}
    for rid,rr in (obj.get("runners") or {}).items():
        features={}
        for name,spec in (rr.get("features") or {}).items():
            features[str(name)]={
                "score":spec.get("score"),
                "category":spec.get("category"),
                "missing":bool(spec.get("missing")),
                "coverage":spec.get("coverage"),
                "candidate_rule_id":spec.get("candidate_rule_id"),
                "source_fact":spec.get("source_fact"),
                "raw_metric":spec.get("raw_metric"),
            }
        out[str(rid)]={
            "profile":rr.get("profile"),
            "observed_feature_count":rr.get("observed_feature_count"),
            "missing_feature_count":rr.get("missing_feature_count"),
            "features":features,
            "base_indices":rr.get("base_indices"),
            "derived_indices":rr.get("derived_indices"),
        }
    return {
        "schema":TRACE_SCHEMA,
        "profile":obj.get("profile"),
        "sha256":obj.get("sha256"),
        "runner_count":len(out),
        "runners":out,
    }

def _market_ranking(trace:Dict[str,Any])->list[str]:
    rows=[]
    for rid,rr in (trace.get("runners") or {}).items():
        f=(rr.get("features") or {}).get("market_rank") or {}
        raw=f.get("raw_metric")
        if isinstance(raw,(int,float)):
            rows.append((float(raw),str(rid)))
    return [rid for _,rid in sorted(rows,key=lambda z:(z[0],int(z[1]) if z[1].isdigit() else z[1]))]

def _rank(ranking:list[str],rid:str):
    return ranking.index(rid)+1 if rid in ranking else None

def _mean_rank(ranks):
    vals=[float(x) for x in ranks if isinstance(x,(int,float))]
    return round(sum(vals)/len(vals),6) if vals else None

def _role_width(roles:Dict[str,set],role:str)->int:
    return sum(1 for x in roles.values() if role in x)

def _index_rankings(trace:Dict[str,Any])->Dict[str,list[str]]:
    score_maps:Dict[str,list[tuple[float,str]]]={}
    for rid,rr in (trace.get("runners") or {}).items():
        for idx,spec in (rr.get("base_indices") or {}).items():
            value=(spec or {}).get("diagnostic_neutralized_score")
            if isinstance(value,(int,float)):
                score_maps.setdefault(str(idx),[]).append((float(value),str(rid)))
        for idx,value in (rr.get("derived_indices") or {}).items():
            if isinstance(value,(int,float)):
                score_maps.setdefault(str(idx),[]).append((float(value),str(rid)))
    return {
        idx:[rid for _,rid in sorted(rows,key=lambda z:(-z[0],int(z[1]) if z[1].isdigit() else z[1]))]
        for idx,rows in score_maps.items()
    }

def _runner_attribution(trace:Dict[str,Any],rid:str,index_rankings:Dict[str,list[str]])->Dict[str,Any]:
    rr=(trace.get("runners") or {}).get(rid) or {}
    features=rr.get("features") or {}
    missing=sorted(name for name,spec in features.items() if (spec or {}).get("missing") is True)
    observed=sorted(name for name,spec in features.items() if (spec or {}).get("missing") is False)
    return {
        "observed_feature_count":rr.get("observed_feature_count"),
        "missing_feature_count":rr.get("missing_feature_count"),
        "missing_features":missing,
        "observed_features":observed,
        "index_ranks":{idx:_rank(ranking,rid) for idx,ranking in index_rankings.items()},
        "derived_indices":rr.get("derived_indices") or {},
        "diagnostic_only":True,
        "causal_claim":False,
    }

def pre_result_record(candidate:Dict[str,Any])->Dict[str,Any]:
    mode=str(candidate.get("temporal_mode") or "")
    frozen=_dt(candidate.get("candidate_frozen_at"))
    post=_dt(candidate.get("scheduled_post_at"))
    final_ts=_dt(candidate.get("candidate_final_receipt_timestamp"))
    final_verified=candidate.get("candidate_final_verified") is True
    acceptance=bool(candidate.get("acceptance_only"))
    temporal_ok=bool(
        mode=="FORMAL-PRE-RACE"
        and not acceptance
        and frozen is not None and post is not None and frozen < post
        and final_ts is not None and final_ts < post
        and final_verified
    )
    objective_trace=_compact_objective_trace(candidate)
    market_ranking=_market_ranking(objective_trace)
    x={
      "profile":PROFILE,
      "trace_schema":TRACE_SCHEMA,
      "race_id":candidate.get("race_id"),
      "prediction_id":candidate.get("prediction_id"),
      "source_snapshot_sha256":candidate.get("source_snapshot_sha256"),
      "candidate_numerical_profile":(candidate.get("candidate_numerical_summary") or {}).get("profile"),
      "candidate_semantic_profile":(candidate.get("candidate_semantic_freeze") or {}).get("profile"),
      "candidate_semantic_freeze_sha256":(candidate.get("candidate_semantic_freeze") or {}).get("sha256"),
      "ranking":(candidate.get("static_prediction") or {}).get("ranking"),
      "roles":(candidate.get("static_prediction") or {}).get("roles"),
      "candidate_objective_trace":objective_trace,
      "market_ranking":market_ranking,
      "candidate_krs_utility_shadow":candidate.get("candidate_krs_utility_shadow"),
      "pair_dispositions":candidate.get("pair_dispositions"),
      "third_dispositions":candidate.get("third_dispositions"),
      "temporal_mode":mode,
      "scheduled_post_at":candidate.get("scheduled_post_at"),
      "frozen_at":candidate.get("candidate_frozen_at"),
      "candidate_final_receipt_sha256":candidate.get("candidate_final_receipt_sha256"),
      "candidate_final_receipt_timestamp":candidate.get("candidate_final_receipt_timestamp"),
      "candidate_final_verified":final_verified,
      "acceptance_only":acceptance,
      "production_effect":"NONE",
      "automatic_promotion":False,
      "oos_eligible":temporal_ok,
      "oos_temporal_rule":"candidate_freeze < signed_candidate_final < scheduled_post; FORMAL-PRE-RACE; not acceptance-only",
    }
    x["sha256"]=_sha(x)
    return x

def evaluate_result(record:Dict[str,Any],actual_top3:list[int])->Dict[str,Any]:
    a=[str(int(x)) for x in actual_top3]
    if len(a)<3:
        raise ValueError("ACTUAL_TOP3_REQUIRED")
    ranking=[str(x) for x in record.get("ranking") or []]
    market_ranking=[str(x) for x in record.get("market_ranking") or []]
    roles={str(k):set(v or []) for k,v in (record.get("roles") or {}).items()}
    pairs={(str(x["head"]),str(x["second"])):x.get("status") for x in record.get("pair_dispositions") or []}
    thirds={(str(x["head"]),str(x["second"]),str(x["third"])):x.get("status") for x in record.get("third_dispositions") or []}
    candidate_ranks=[_rank(ranking,x) for x in a]
    market_ranks=[_rank(market_ranking,x) for x in a]
    candidate_top3_mean=_mean_rank(candidate_ranks)
    market_top3_mean=_mean_rank(market_ranks)
    objective_trace=record.get("candidate_objective_trace") or {}
    index_rankings=_index_rankings(objective_trace)
    actual_attribution={x:_runner_attribution(objective_trace,x,index_rankings) for x in a}
    krs_utility=record.get("candidate_krs_utility_shadow")
    krs_eval=None
    if isinstance(krs_utility,dict):
        try:
            krs_eval=evaluate_krs_against_result(krs_utility,[int(x) for x in a])
            actionable_width=sum(len(krs_utility.get(k) or []) for k in (
                "actionable_role_proposals","actionable_ordered_pair_proposals","actionable_pair_third_proposals"
            ))
            krs_eval["actionable_proposal_width"]=actionable_width
            krs_eval["rescue_density"]=(
                round(float(krs_eval.get("rescue_count") or 0)/actionable_width,6)
                if actionable_width else None
            )
        except Exception as exc:
            krs_eval={"classification":"UNASSESSABLE","error":type(exc).__name__+":"+str(exc)}
    winner_rank=candidate_ranks[0]
    market_winner_rank=market_ranks[0]
    out={
      "profile":PROFILE,
      "trace_schema":TRACE_SCHEMA,
      "race_id":record.get("race_id"),
      "pre_result_record_sha256":record.get("sha256"),
      "actual_top3":[int(x) for x in a],
      "winner_capture":"W" in roles.get(a[0],set()),
      "p2_capture":"P2" in roles.get(a[1],set()),
      "p3_capture":"P3" in roles.get(a[2],set()),
      "ordered_pair_capture":pairs.get((a[0],a[1])) in {"PURCHASE","PROTECT"},
      "exact_capture":thirds.get((a[0],a[1],a[2])) in {"PURCHASE","PROTECT"},
      "winner_static_rank":winner_rank,
      "second_static_rank":candidate_ranks[1],
      "third_static_rank":candidate_ranks[2],
      "top3_mean_static_rank":candidate_top3_mean,
      "top3_set_capture":all(x in set(ranking[:6]) for x in a),
      "w_width":_role_width(roles,"W"),
      "p2_width":_role_width(roles,"P2"),
      "p3_width":_role_width(roles,"P3"),
      "ordered_pair_width":sum(1 for status in pairs.values() if status in {"PURCHASE","PROTECT"}),
      "exact_third_width":sum(1 for status in thirds.values() if status in {"PURCHASE","PROTECT"}),
      "winner_capture_efficiency":round(1.0/_role_width(roles,"W"),6) if "W" in roles.get(a[0],set()) and _role_width(roles,"W") else 0.0,
      "p2_capture_efficiency":round(1.0/_role_width(roles,"P2"),6) if "P2" in roles.get(a[1],set()) and _role_width(roles,"P2") else 0.0,
      "p3_capture_efficiency":round(1.0/_role_width(roles,"P3"),6) if "P3" in roles.get(a[2],set()) and _role_width(roles,"P3") else 0.0,
      "market_baseline":{
          "ranking":market_ranking,
          "winner_rank":market_winner_rank,
          "second_rank":market_ranks[1],
          "third_rank":market_ranks[2],
          "top3_mean_rank":market_top3_mean,
      },
      "candidate_vs_market":{
          "winner_rank_gain":(
              round(float(market_winner_rank)-float(winner_rank),6)
              if isinstance(market_winner_rank,(int,float)) and isinstance(winner_rank,(int,float)) else None
          ),
          "top3_mean_rank_gain":(
              round(float(market_top3_mean)-float(candidate_top3_mean),6)
              if isinstance(market_top3_mean,(int,float)) and isinstance(candidate_top3_mean,(int,float)) else None
          ),
          "positive_means_candidate_better":True,
      },
      "actual_top3_attribution":actual_attribution,
      "krs_incremental_utility":krs_eval,
      "oos_eligible":bool(record.get("oos_eligible")),
      "production_effect":"NONE",
      "automatic_promotion":False,
      "attribution_notice":"Feature/index attribution is diagnostic and pre-result-frozen; it does not prove causal importance.",
    }
    out["sha256"]=_sha(out)
    return out
