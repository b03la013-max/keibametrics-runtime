from __future__ import annotations
from datetime import datetime
import hashlib, json

PROFILE="KM-JRA-KRS-OOS-PROMOTION-GATE-v1.0-20260921"
R30_MINIMUM=30

def _dt(s):
    if not s: return None
    return datetime.fromisoformat(str(s).replace("Z","+00:00"))

def _sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def build_oos_measurement(review, final_artifact):
    ku=final_artifact.get("krs_prediction_utility") or {}
    final_receipt=final_artifact.get("final_receipt") or {}
    receipt_ts=((final_receipt.get("receipt") or {}).get("timestamp")
                if isinstance(final_receipt,dict) else None)
    post=final_artifact.get("scheduled_post_at")
    temporal=str(final_artifact.get("temporal_mode") or "")
    eligible=bool(
        temporal=="FORMAL-PRE-RACE"
        and _dt(receipt_ts) is not None and _dt(post) is not None
        and _dt(receipt_ts) < _dt(post)
        and ku.get("utility_revision")
    )
    actual=review.get("official_top3") or []
    role_props=ku.get("actionable_role_proposals") or []
    pair_props=ku.get("actionable_ordered_pair_proposals") or []
    third_props=ku.get("actionable_pair_third_proposals") or []
    role_hits=0
    if len(actual)==3:
        targets={(int(actual[0]),"ADD_W_SHADOW"),(int(actual[1]),"ADD_P2_SHADOW"),(int(actual[2]),"ADD_P3_SHADOW")}
        role_hits=sum(1 for x in role_props if (int(x["horse_no"]),str(x["proposal"])) in targets)
        pair_hit=any((int(x["head"]),int(x["second"]))==(int(actual[0]),int(actual[1])) for x in pair_props)
        third_hit=any((int(x["head"]),int(x["second"]),int(x["third"]))==tuple(map(int,actual)) for x in third_props)
    else:
        pair_hit=third_hit=False
    m={
      "profile":PROFILE,
      "race_id":review.get("race_id"),
      "eligible":eligible,
      "eligibility_reason":"PRE_RACE_FROZEN_SIGNED_KRS_UTILITY" if eligible else "NOT_OOS_ELIGIBLE",
      "utility_revision":ku.get("utility_revision"),
      "utility_class":ku.get("utility_class"),
      "actionable_role_proposals":len(role_props),
      "actionable_role_hits":role_hits,
      "actionable_pair_proposals":len(pair_props),
      "ordered_pair_rescue_hit":bool(pair_hit),
      "actionable_third_proposals":len(third_props),
      "ordered_exact_rescue_hit":bool(third_hit),
      "post_result_classification":(review.get("krs") or {}).get("post_result_evaluation",{}).get("classification"),
      "production_effect":"NONE",
    }
    m["sha256"]=_sha(m)
    return m

def evaluate_r30(measurements):
    eligible=[x for x in measurements if x.get("eligible") is True]
    n=len(eligible)
    role_props=sum(int(x.get("actionable_role_proposals",0)) for x in eligible)
    role_hits=sum(int(x.get("actionable_role_hits",0)) for x in eligible)
    pair_props=sum(int(x.get("actionable_pair_proposals",0)) for x in eligible)
    pair_hits=sum(1 for x in eligible if x.get("ordered_pair_rescue_hit"))
    third_props=sum(int(x.get("actionable_third_proposals",0)) for x in eligible)
    third_hits=sum(1 for x in eligible if x.get("ordered_exact_rescue_hit"))
    out={
      "profile":PROFILE,
      "eligible_races":n,
      "required_races":R30_MINIMUM,
      "status":"WAITING_R30" if n<R30_MINIMUM else "R30_EVIDENCE_COMPLETE_HUMAN_PROMOTION_REVIEW_REQUIRED",
      "automatic_production_promotion":False,
      "metrics":{
        "role_proposals":role_props,
        "role_hits":role_hits,
        "role_hit_rate":(role_hits/role_props if role_props else None),
        "pair_proposals":pair_props,
        "pair_rescue_races":pair_hits,
        "third_proposals":third_props,
        "exact_third_rescue_races":third_hits,
      },
      "requirements_after_r30":[
        "Compare Static-only vs Static+KRS decision coverage under identical frozen policy.",
        "Measure false-positive candidate-width and capital cost.",
        "Require no retroactive result-derived thresholds.",
        "Require explicit Family promotion decision; this module never self-promotes."
      ],
    }
    out["sha256"]=_sha(out)
    return out
