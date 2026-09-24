from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

PROFILE="KM-LOCAL-NUMERICAL-V03-FORWARD-OOS-TRACKER-v1.0-20260925"
POST_PROFILE="KM-LOCAL-NUMERICAL-CANDIDATE-POSTRESULT-v0.3-EVIDENCE-ROUTING-20260925"
MINIMUM_FOR_HUMAN_REVIEW=30


def _sha(x: Any) -> str:
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def _avg(rows: List[Dict[str,Any]], key: str):
    vals=[]
    for row in rows:
        v=((row.get("arm") or {}).get(key))
        if isinstance(v,bool): vals.append(int(v))
        elif isinstance(v,(int,float)): vals.append(float(v))
    return None if not vals else sum(vals)/len(vals)


def build_measurement(post: Dict[str,Any], result_request: Dict[str,Any], *, baseline_measurement: Dict[str,Any]|None=None) -> Dict[str,Any]:
    d=post or {}
    if d.get("profile")!=POST_PROFILE:
        raise ValueError("V03_POSTRESULT_PROFILE_INVALID")
    rid=str(d.get("race_id") or result_request.get("race_id") or "")
    if not rid or str(result_request.get("race_id") or "")!=rid:
        raise ValueError("V03_RESULT_REQUEST_RACE_ID_MISMATCH")
    arm=d.get("arm") or {}
    official=bool(result_request.get("official_result_verified") is True)
    temporal=bool(arm.get("candidate_oos_event_eligible") is True and d.get("future_oos_candidate") is True)
    admissible=bool(official and temporal)
    base=baseline_measurement or {}
    v01=((base.get("arms") or {}).get("v0.1") or {})
    def gain(key):
        a=v01.get(key); b=arm.get(key)
        return None if not isinstance(a,(int,float)) or not isinstance(b,(int,float)) else round(float(a)-float(b),6)
    m={
      "profile":PROFILE,
      "race_id":rid,
      "race_date":d.get("race_date"),
      "result_available_at":d.get("result_available_at"),
      "actual_top3":d.get("actual_top3"),
      "v03_shadow_sha256":d.get("v03_shadow_sha256"),
      "v03_postresult_sha256":d.get("sha256"),
      "result_authority":{
        "status":"VERIFIED" if official else "HOLD_RESULT_AUTHORITY",
        "official_result_verified":official,
        "verification_ref":result_request.get("official_result_verification_ref"),
        "source":result_request.get("source"),
      },
      "temporal_v03_oos_eligible":temporal,
      "promotion_measurement_admissible":admissible,
      "hold_reason":None if admissible else ("RESULT_AUTHORITY_NOT_VERIFIED" if temporal else "V03_PRE_DESIGN_OR_TEMPORAL_GATE_NOT_PASS"),
      "arm":{
        "mapping_id":arm.get("candidate_mapping_id"),
        "winner_rank":arm.get("winner_rank"),
        "second_rank":arm.get("second_rank"),
        "third_rank":arm.get("third_rank"),
        "top3_mean_rank":arm.get("top3_mean_rank"),
        "winner_capture":arm.get("winner_capture"),
        "p2_capture":arm.get("p2_capture"),
        "p3_capture":arm.get("p3_capture"),
        "top3_set_capture":arm.get("top3_set_capture"),
        "krs_status":arm.get("candidate_krs_status"),
      },
      "vs_v01":{
        "baseline_available":bool(v01),
        "winner_rank_gain":gain("winner_rank"),
        "second_rank_gain":gain("second_rank"),
        "third_rank_gain":gain("third_rank"),
        "top3_mean_rank_gain":gain("top3_mean_rank"),
        "winner_capture_delta":None if "winner_capture" not in v01 else int(bool(arm.get("winner_capture")))-int(bool(v01.get("winner_capture"))),
        "p2_capture_delta":None if "p2_capture" not in v01 else int(bool(arm.get("p2_capture")))-int(bool(v01.get("p2_capture"))),
        "p3_capture_delta":None if "p3_capture" not in v01 else int(bool(arm.get("p3_capture")))-int(bool(v01.get("p3_capture"))),
      },
      "candidate_krs_postresult":d.get("candidate_krs_postresult"),
      "candidate_ticket_pfs":{"status":"NOT_AVAILABLE","reason":"v0.3 freezes numerical roles/KRS only; no candidate capital authority."},
      "production_effect":"NONE",
      "automatic_promotion":False,
    }
    m["sha256"]=_sha(m)
    return m


def evaluate_measurements(rows: List[Dict[str,Any]]) -> Dict[str,Any]:
    by={}
    for x in rows:
        rid=str(x.get("race_id") or "")
        if not rid: raise ValueError("V03_MEASUREMENT_RACE_ID_REQUIRED")
        if rid in by: raise ValueError("V03_DUPLICATE_RACE_ID:"+rid)
        by[rid]=x
    all_rows=[by[k] for k in sorted(by)]
    admitted=[x for x in all_rows if x.get("promotion_measurement_admissible") is True]
    held=[x for x in all_rows if x.get("promotion_measurement_admissible") is not True]
    n=len(admitted)
    status={
      "profile":PROFILE,
      "status":"HUMAN_REVIEW_REQUIRED" if n>=MINIMUM_FOR_HUMAN_REVIEW else "WAITING_R30",
      "total_measurements":len(all_rows),
      "promotion_admissible_races":n,
      "held_races":len(held),
      "minimum_for_human_promotion_review":MINIMUM_FOR_HUMAN_REVIEW,
      "remaining_to_r30":max(0,MINIMUM_FOR_HUMAN_REVIEW-n),
      "promotion_review_ready":n>=MINIMUM_FOR_HUMAN_REVIEW,
      "metrics":{
        "winner_capture_rate":_avg(admitted,"winner_capture"),
        "p2_capture_rate":_avg(admitted,"p2_capture"),
        "p3_capture_rate":_avg(admitted,"p3_capture"),
        "top3_set_capture_rate":_avg(admitted,"top3_set_capture"),
        "mean_winner_rank":_avg(admitted,"winner_rank"),
        "mean_top3_mean_rank":_avg(admitted,"top3_mean_rank"),
      },
      "vs_v01":{
        "mean_winner_rank_gain":None if not admitted else sum(
            float((x.get("vs_v01") or {}).get("winner_rank_gain"))
            for x in admitted if isinstance((x.get("vs_v01") or {}).get("winner_rank_gain"),(int,float))
        ) / max(1,sum(isinstance((x.get("vs_v01") or {}).get("winner_rank_gain"),(int,float)) for x in admitted)),
        "mean_top3_rank_gain":None if not admitted else sum(
            float((x.get("vs_v01") or {}).get("top3_mean_rank_gain"))
            for x in admitted if isinstance((x.get("vs_v01") or {}).get("top3_mean_rank_gain"),(int,float))
        ) / max(1,sum(isinstance((x.get("vs_v01") or {}).get("top3_mean_rank_gain"),(int,float)) for x in admitted)),
      },
      "held":[{"race_id":x.get("race_id"),"hold_reason":x.get("hold_reason")} for x in held],
      "automatic_promotion":False,
      "production_effect":"NONE",
      "decision_policy":"R30 opens human review only. No automatic Production numerical promotion, weight change, or ticket activation."
    }
    status["sha256"]=_sha(status)
    return status


def read_measurements(directory: str|Path) -> List[Dict[str,Any]]:
    p=Path(directory)
    return [] if not p.exists() else [json.loads(x.read_text(encoding="utf-8")) for x in sorted(p.glob("*.json"))]


def write_status(directory: str|Path, out_path: str|Path) -> Dict[str,Any]:
    status=evaluate_measurements(read_measurements(directory))
    q=Path(out_path); q.parent.mkdir(parents=True,exist_ok=True)
    q.write_text(json.dumps(status,ensure_ascii=False,indent=2,sort_keys=True),encoding="utf-8")
    return status
