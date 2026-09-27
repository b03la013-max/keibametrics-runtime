from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List

PROFILE="KM-JRA-SOURCE-DERIVED-CANDIDATE-PROMOTION-GATE-v0.1-20260926"
TARGET=30

def _sha(x:Any)->str:
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()

def evaluate(records:List[Dict[str,Any]])->Dict[str,Any]:
    eligible=[x for x in records if x.get("oos_eligible") is True and x.get("result_evaluation")]
    unique={}
    for x in eligible:
        rid=str(x.get("race_id") or "")
        if rid and rid not in unique:
            unique[rid]=x
    rows=list(unique.values())
    n=len(rows)
    def rate(key):
        vals=[1.0 if (r["result_evaluation"] or {}).get(key) else 0.0 for r in rows]
        return round(sum(vals)/len(vals),6) if vals else None
    def mean_metric(path):
        vals=[]
        for r in rows:
            cur=r.get("result_evaluation") or {}
            for key in path:
                cur=cur.get(key) if isinstance(cur,dict) else None
            if isinstance(cur,(int,float)):
                vals.append(float(cur))
        return round(sum(vals)/len(vals),6) if vals else None

    avg_rank=mean_metric(["winner_static_rank"])
    krs_classes={}
    for r in rows:
        cls=((r.get("result_evaluation") or {}).get("krs_incremental_utility") or {}).get("classification")
        if cls:
            krs_classes[str(cls)]=krs_classes.get(str(cls),0)+1
    report={
      "profile":PROFILE,
      "status":"WAITING_R30" if n<TARGET else "R30_REVIEW_REQUIRED",
      "eligible_race_count":n,
      "target_eligible_races":TARGET,
      "winner_capture_rate":rate("winner_capture"),
      "p2_capture_rate":rate("p2_capture"),
      "p3_capture_rate":rate("p3_capture"),
      "ordered_pair_capture_rate":rate("ordered_pair_capture"),
      "exact_capture_rate":rate("exact_capture"),
      "top3_set_capture_rate":rate("top3_set_capture"),
      "mean_winner_static_rank":avg_rank,
      "mean_second_static_rank":mean_metric(["second_static_rank"]),
      "mean_third_static_rank":mean_metric(["third_static_rank"]),
      "mean_top3_static_rank":mean_metric(["top3_mean_static_rank"]),
      "mean_winner_capture_efficiency":mean_metric(["winner_capture_efficiency"]),
      "mean_p2_capture_efficiency":mean_metric(["p2_capture_efficiency"]),
      "mean_p3_capture_efficiency":mean_metric(["p3_capture_efficiency"]),
      "mean_market_winner_rank":mean_metric(["market_baseline","winner_rank"]),
      "mean_market_top3_rank":mean_metric(["market_baseline","top3_mean_rank"]),
      "mean_candidate_vs_market_winner_rank_gain":mean_metric(["candidate_vs_market","winner_rank_gain"]),
      "mean_candidate_vs_market_top3_rank_gain":mean_metric(["candidate_vs_market","top3_mean_rank_gain"]),
      "mean_krs_rescue_density":mean_metric(["krs_incremental_utility","rescue_density"]),
      "krs_result_class_counts":krs_classes,
      "automatic_promotion":False,
      "promotion_decision":"NOT_AUTHORIZED",
      "required_next_action":"Continue unknown pre-result frozen OOS collection." if n<TARGET else "Independent review against current Production and simple baselines; explicit Promotion Declaration required.",
      "production_effect":"NONE",
    }
    report["sha256"]=_sha(report)
    return report

def bind_result(pre_record:Dict[str,Any], evaluation:Dict[str,Any])->Dict[str,Any]:
    if str(evaluation.get("pre_result_record_sha256") or "")!=str(pre_record.get("sha256") or ""):
        raise ValueError("CANDIDATE_OOS_LINEAGE_MISMATCH")
    out=dict(pre_record)
    out["result_evaluation"]=evaluation
    out["production_effect"]="NONE"
    out["automatic_promotion"]=False
    out["sha256"]=_sha({k:v for k,v in out.items() if k!="sha256"})
    return out
