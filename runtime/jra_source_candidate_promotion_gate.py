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
    avg_rank=None
    ranks=[(r["result_evaluation"] or {}).get("winner_static_rank") for r in rows]
    ranks=[float(x) for x in ranks if isinstance(x,(int,float))]
    if ranks: avg_rank=round(sum(ranks)/len(ranks),6)
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
