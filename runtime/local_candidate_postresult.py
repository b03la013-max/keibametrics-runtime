from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List

PROFILE="KM-LOCAL-NUMERICAL-CANDIDATE-POSTRESULT-v0.1-20260923"


def _sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def _rank(ranking,horse):
    vals=[str(x) for x in ranking]
    try:return vals.index(str(horse))+1
    except ValueError:return None


def evaluate(candidate_summary: Dict[str,Any], actual_finish_order: List[int],
             *, result_available_at: str, candidate_krs_summary: Dict[str,Any]|None=None) -> Dict[str,Any]:
    pred=(candidate_summary or {}).get("candidate_static_prediction") or {}
    actual=[str(x) for x in actual_finish_order[:3]]
    if len(actual)!=3:
        raise ValueError("ACTUAL_TOP3_REQUIRED")
    ranking=[str(x) for x in pred.get("ranking") or []]
    W=set(str(x) for x in pred.get("W") or [])
    P2=set(str(x) for x in pred.get("P2") or [])
    P3=set(str(x) for x in pred.get("P3") or [])
    ranks=[_rank(ranking,x) for x in actual]
    full=(candidate_summary or {}).get("candidate_full_numerical_summary") or {}
    krs=candidate_krs_summary or {}
    oos=bool(
        candidate_summary.get("status")=="FROZEN_PRE_RESULT_NUMERICAL_CANDIDATE_SHADOW"
        and krs.get("status")=="EXECUTED"
        and krs.get("pre_post_complete") is True
        and krs.get("oos_temporal_eligible") is True
        and full.get("production_authority") is False
    )
    out={
      "profile":PROFILE,
      "race_source_snapshot_sha256":candidate_summary.get("source_snapshot_sha256"),
      "candidate_shadow_sha256":candidate_summary.get("sha256"),
      "candidate_mapping_id":full.get("mapping_id"),
      "result_available_at":result_available_at,
      "actual_top3":actual,
      "winner_rank":ranks[0],
      "second_rank":ranks[1],
      "third_rank":ranks[2],
      "top3_mean_rank":None if any(x is None for x in ranks) else sum(ranks)/3,
      "winner_capture":actual[0] in W,
      "p2_capture":actual[1] in P2,
      "p3_capture":actual[2] in P3,
      "top3_set_capture":all(x in P3 for x in actual),
      "candidate_krs_status":krs.get("status") or "NOT_AVAILABLE",
      "candidate_krs_receipt_sha256":krs.get("receipt_sha256"),
      "candidate_krs_pre_post_complete":krs.get("pre_post_complete"),
      "candidate_oos_event_eligible":oos,
      "production_effect":"NONE",
      "automatic_promotion":False,
      "result_derived_feature_count":0,
      "note":"Measures a frozen numerical candidate only. Never rewrites Production prediction or same-race features."
    }
    out["sha256"]=_sha(out)
    return out
