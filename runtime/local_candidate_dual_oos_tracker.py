from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

PROFILE="KM-LOCAL-NUMERICAL-CANDIDATE-DUAL-OOS-TRACKER-v0.1-20260923"
MINIMUM_FOR_HUMAN_REVIEW=30


def _sha(x: Any) -> str:
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def _avg(rows: List[Dict[str,Any]], path: List[str]):
    vals=[]
    for row in rows:
        cur=row
        for key in path:
            if not isinstance(cur,dict):
                cur=None; break
            cur=cur.get(key)
        if isinstance(cur,bool): vals.append(int(cur))
        elif isinstance(cur,(int,float)): vals.append(float(cur))
    return None if not vals else sum(vals)/len(vals)


def build_measurement(dual_postresult: Dict[str,Any], result_request: Dict[str,Any]) -> Dict[str,Any]:
    d=dual_postresult or {}
    if d.get("profile")!="KM-LOCAL-NUMERICAL-CANDIDATE-POSTRESULT-v0.2-DUAL-20260923":
        raise ValueError("DUAL_POSTRESULT_PROFILE_INVALID")
    rid=str(d.get("race_id") or result_request.get("race_id") or "")
    if not rid:
        raise ValueError("RACE_ID_REQUIRED")
    if str(result_request.get("race_id") or "")!=rid:
        raise ValueError("RESULT_REQUEST_RACE_ID_MISMATCH")
    arms=d.get("arms") or {}
    v01=arms.get("v0.1") or {}
    v02=arms.get("v0.2") or {}
    comp=d.get("comparison") or {}
    krs_post=d.get("candidate_krs_postresult") or {}

    explicit_official=bool(result_request.get("official_result_verified") is True)
    authority_ref=result_request.get("official_result_verification_ref")
    result_authority_status="VERIFIED" if explicit_official else "HOLD_RESULT_AUTHORITY"

    temporal_pair=bool(
        v01.get("candidate_oos_event_eligible") is True
        and v02.get("candidate_oos_event_eligible") is True
        and comp.get("same_source") is True
        and v02.get("candidate_is_calibration_training_race") is False
    )
    promotion_admissible=bool(temporal_pair and explicit_official)

    def krs_eval(label):
        x=krs_post.get(label) or {}
        return (x.get("post_result_evaluation") or {}) if isinstance(x,dict) else {}

    k1=krs_eval("v0.1"); k2=krs_eval("v0.2")
    measurement={
      "profile":PROFILE,
      "race_id":rid,
      "result_available_at":d.get("result_available_at"),
      "actual_top3":d.get("actual_top3"),
      "dual_shadow_sha256":d.get("dual_shadow_sha256"),
      "dual_postresult_sha256":d.get("sha256"),
      "same_source":comp.get("same_source"),
      "result_authority":{
        "status":result_authority_status,
        "official_result_verified":explicit_official,
        "verification_ref":authority_ref,
        "source":result_request.get("source"),
      },
      "temporal_dual_oos_eligible":temporal_pair,
      "promotion_measurement_admissible":promotion_admissible,
      "hold_reason":None if promotion_admissible else (
        "RESULT_AUTHORITY_NOT_VERIFIED" if temporal_pair and not explicit_official else "DUAL_OOS_TEMPORAL_OR_TRAINING_GATE_NOT_PASS"
      ),
      "arms":{
        "v0.1":{
          "mapping_id":v01.get("candidate_mapping_id"),
          "winner_rank":v01.get("winner_rank"),
          "second_rank":v01.get("second_rank"),
          "third_rank":v01.get("third_rank"),
          "top3_mean_rank":v01.get("top3_mean_rank"),
          "winner_capture":v01.get("winner_capture"),
          "p2_capture":v01.get("p2_capture"),
          "p3_capture":v01.get("p3_capture"),
          "top3_set_capture":v01.get("top3_set_capture"),
          "krs_classification":k1.get("classification"),
          "krs_rescues":k1.get("rescues") or [],
          "krs_misses":k1.get("misses") or [],
        },
        "v0.2":{
          "mapping_id":v02.get("candidate_mapping_id"),
          "winner_rank":v02.get("winner_rank"),
          "second_rank":v02.get("second_rank"),
          "third_rank":v02.get("third_rank"),
          "top3_mean_rank":v02.get("top3_mean_rank"),
          "winner_capture":v02.get("winner_capture"),
          "p2_capture":v02.get("p2_capture"),
          "p3_capture":v02.get("p3_capture"),
          "top3_set_capture":v02.get("top3_set_capture"),
          "krs_classification":k2.get("classification"),
          "krs_rescues":k2.get("rescues") or [],
          "krs_misses":k2.get("misses") or [],
        }
      },
      "comparison":comp,
      "candidate_ticket_pfs":{
        "status":"NOT_AVAILABLE",
        "reason":"Candidate dual shadow currently freezes numerical roles and KRS only; candidate ticket activation/capital is intentionally not implemented.",
      },
      "krs_harm_measurement":{
        "status":"UNASSESSABLE_WITHOUT_CANDIDATE_TICKET_ACTIVATION",
        "note":"Do not infer harm from a proposal that was never activated into a ticket/capital decision."
      },
      "production_effect":"NONE",
      "automatic_promotion":False,
    }
    measurement["sha256"]=_sha(measurement)
    return measurement


def evaluate_measurements(measurements: List[Dict[str,Any]], *, minimum_for_review: int=MINIMUM_FOR_HUMAN_REVIEW) -> Dict[str,Any]:
    uniq={}
    for m in measurements:
        rid=str(m.get("race_id") or "")
        if not rid:
            raise ValueError("MEASUREMENT_RACE_ID_REQUIRED")
        if rid in uniq:
            raise ValueError("DUPLICATE_MEASUREMENT_RACE_ID:"+rid)
        uniq[rid]=m
    all_rows=[uniq[k] for k in sorted(uniq)]
    admitted=[x for x in all_rows if x.get("promotion_measurement_admissible") is True]
    held=[x for x in all_rows if x.get("promotion_measurement_admissible") is not True]

    def arm_summary(label):
        return {
          "winner_capture_rate":_avg(admitted,["arms",label,"winner_capture"]),
          "p2_capture_rate":_avg(admitted,["arms",label,"p2_capture"]),
          "p3_capture_rate":_avg(admitted,["arms",label,"p3_capture"]),
          "top3_set_capture_rate":_avg(admitted,["arms",label,"top3_set_capture"]),
          "mean_winner_rank":_avg(admitted,["arms",label,"winner_rank"]),
          "mean_top3_mean_rank":_avg(admitted,["arms",label,"top3_mean_rank"]),
          "krs_unique_rescue_rate":None if not admitted else sum(
              1 for x in admitted if (x.get("arms",{}).get(label,{}).get("krs_classification")=="UNIQUE-RESCUE")
          )/len(admitted),
        }

    v01=arm_summary("v0.1"); v02=arm_summary("v0.2")
    delta={
      "winner_capture_rate":None if v01["winner_capture_rate"] is None or v02["winner_capture_rate"] is None else v02["winner_capture_rate"]-v01["winner_capture_rate"],
      "p2_capture_rate":None if v01["p2_capture_rate"] is None or v02["p2_capture_rate"] is None else v02["p2_capture_rate"]-v01["p2_capture_rate"],
      "p3_capture_rate":None if v01["p3_capture_rate"] is None or v02["p3_capture_rate"] is None else v02["p3_capture_rate"]-v01["p3_capture_rate"],
      "top3_set_capture_rate":None if v01["top3_set_capture_rate"] is None or v02["top3_set_capture_rate"] is None else v02["top3_set_capture_rate"]-v01["top3_set_capture_rate"],
      "mean_winner_rank_gain":None if v01["mean_winner_rank"] is None or v02["mean_winner_rank"] is None else v01["mean_winner_rank"]-v02["mean_winner_rank"],
      "mean_top3_mean_rank_gain":None if v01["mean_top3_mean_rank"] is None or v02["mean_top3_mean_rank"] is None else v01["mean_top3_mean_rank"]-v02["mean_top3_mean_rank"],
      "krs_unique_rescue_rate":None if v01["krs_unique_rescue_rate"] is None or v02["krs_unique_rescue_rate"] is None else v02["krs_unique_rescue_rate"]-v01["krs_unique_rescue_rate"],
    }
    n=len(admitted)
    status={
      "profile":PROFILE,
      "total_measurements":len(all_rows),
      "promotion_admissible_races":n,
      "held_races":len(held),
      "remaining_to_r30":max(0,minimum_for_review-n),
      "minimum_for_human_promotion_review":minimum_for_review,
      "promotion_review_ready":n>=minimum_for_review,
      "status":"HUMAN_REVIEW_REQUIRED" if n>=minimum_for_review else "WAITING_R30",
      "arms":{"v0.1":v01,"v0.2":v02},
      "v0.2_minus_v0.1":delta,
      "held":[{"race_id":x.get("race_id"),"hold_reason":x.get("hold_reason")} for x in held],
      "candidate_ticket_pfs_status":"NOT_AVAILABLE_UNTIL_CANDIDATE_TICKET_ACTIVATION_EXISTS",
      "automatic_promotion":False,
      "production_effect":"NONE",
      "decision_policy":"R30 only opens human review. This tracker never promotes, changes weights, or rewrites Production.",
    }
    status["sha256"]=_sha(status)
    return status


def read_measurements(directory: str|Path) -> List[Dict[str,Any]]:
    p=Path(directory)
    if not p.exists():
        return []
    rows=[]
    for fn in sorted(p.glob("*.json")):
        rows.append(json.loads(fn.read_text(encoding="utf-8")))
    return rows


def write_status(directory: str|Path, out_path: str|Path) -> Dict[str,Any]:
    status=evaluate_measurements(read_measurements(directory))
    Path(out_path).parent.mkdir(parents=True,exist_ok=True)
    Path(out_path).write_text(json.dumps(status,ensure_ascii=False,indent=2,sort_keys=True),encoding="utf-8")
    return status


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("measurement_dir")
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(write_status(a.measurement_dir,a.out),ensure_ascii=False,indent=2,sort_keys=True))
