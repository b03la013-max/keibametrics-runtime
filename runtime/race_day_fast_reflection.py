from __future__ import annotations
import copy,hashlib,json
from typing import Any,Dict

PROFILE_ID="KM-FAMILY-RACE-DAY-FAST-REFLECTION-20260928-R1"

def _sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def build_fast_reflection(result_artifact:Dict[str,Any], *, race_id:str|None=None)->Dict[str,Any]:
    art=copy.deepcopy(result_artifact or {})
    review=art.get("automatic_post_result_review") or {}
    failure=art.get("failure_localization") or {}
    review_failure=(review.get("failure_localization") or {})
    settlement=art.get("settlement") or (review.get("capital") or {})
    pred=review.get("prediction") or {}
    conversion=review.get("conversion") or {}
    krs=review.get("krs") or {}
    learning=art.get("learning_event") or art.get("automatic_next_race_learning_state") or {}
    first=(
        failure.get("primary_failure")
        or review_failure.get("first_material_failure")
        or "UNRESOLVED"
    )
    role_capture=pred.get("role_capture") or {}
    out={
        "profile":PROFILE_ID,
        "race_id":race_id or art.get("race_id") or review.get("race_id"),
        "status":"RACE-DAY-DIAGNOSTIC-COMPLETE",
        "purpose":"Immediate between-race diagnosis only; deep causal research is deferred to daily review.",
        "settlement":{
            "investment":settlement.get("investment") or settlement.get("settled_investment"),
            "return":settlement.get("return"),
            "profit_loss":settlement.get("profit_loss"),
            "pfs":settlement.get("pfs"),
            "status":settlement.get("status") or settlement.get("settlement_status"),
        },
        "prediction":{
            "status":pred.get("status"),
            "winner_w":role_capture.get("winner_w"),
            "second_p2":role_capture.get("second_p2"),
            "third_p3":role_capture.get("third_p3"),
        },
        "conversion":{
            "status":conversion.get("status"),
            "ordered_pair_ticket_coverage":conversion.get("ordered_pair_ticket_coverage"),
            "top3_set_ticket_coverage":conversion.get("top3_set_ticket_coverage"),
            "ordered_exact_ticket_coverage":conversion.get("ordered_exact_ticket_coverage"),
        },
        "krs":{
            "pre_result_utility_class":krs.get("pre_result_utility_class"),
            "post_result_classification":((krs.get("post_result_evaluation") or {}).get("classification")),
        },
        "first_material_failure":first,
        "materiality":failure.get("materiality"),
        "next_race_learning_state_id":learning.get("state_id"),
        "production_change_authorized":False,
        "deep_review_required":first not in {"NONE","UNRESOLVED"},
        "deep_review_timing":"AFTER_MEETING_OR_EXPLICIT_EXCEPTION",
        "forbidden":[
            "RETROACTIVE_PREDICTION_REWRITE",
            "SAME-RACE_RESULT_TO_PRE-RACE_FEATURE",
            "AUTOMATIC_NUMERICAL_WEIGHT_CHANGE",
            "AUTO_VENUE_CANON_CHANGE_BETWEEN_RACES"
        ],
    }
    out["sha256"]=_sha(out)
    return out
