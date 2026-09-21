from __future__ import annotations
import hashlib, json
from typing import Any
from krs_prediction_utility import evaluate_against_result

LEARNING_PROFILE="KM-FAMILY-POSTRESULT-CLOSED-LOOP-v1.0-20260921"

class LearningError(ValueError):
    pass

def _sha(obj:Any)->str:
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def _roles(final_artifact):
    fp=final_artifact.get("final_prediction_package") or {}
    roles=fp.get("roles")
    if isinstance(roles,dict):
        return {str(k):set(map(str,v or [])) for k,v in roles.items()}
    out={}
    for r in final_artifact.get("role_registry") or []:
        if str(r.get("status")) in {"CORE","PROTECTED","CONDITIONAL","RESIDUAL"}:
            out.setdefault(str(r.get("runner_id")),set()).add(str(r.get("column")))
    return out

def _ticket_key(t):
    return str(t.get("bet_type","")).upper(), tuple(str(x) for x in (t.get("selection") or []))

def _coverage(final_artifact, top3):
    ft=final_artifact.get("final_ticket") or {}
    tickets=ft.get("tickets") or []
    a,b,c=map(str,top3)
    exacta=False
    top3set=False
    exact=False
    hit_types=[]
    for t in tickets:
        bt,sel=_ticket_key(t)
        if bt=="EXACTA" and sel==(a,b):
            exacta=True; hit_types.append("EXACTA")
        elif bt=="TRIO" and set(sel)=={a,b,c}:
            top3set=True; hit_types.append("TRIO")
        elif bt=="TRIFECTA":
            if len(sel)>=2 and sel[:2]==(a,b):
                exacta=True
            if set(sel)=={a,b,c}:
                top3set=True
            if sel==(a,b,c):
                exact=True; hit_types.append("TRIFECTA")
    return {
      "ordered_pair_ticket_coverage":exacta,
      "top3_set_ticket_coverage":top3set,
      "ordered_exact_ticket_coverage":exact,
      "matching_ticket_types":sorted(set(hit_types)),
      "ticket_count":len(tickets),
      "investment":int(ft.get("total_investment") or 0),
    }

def _mec_actual_coverage(final_artifact, top3):
    mec=final_artifact.get("minimum_efficient_coverage")
    if not isinstance(mec,dict):
        return {"available":False}
    a,b,c=map(str,top3)
    ids={str(x.get("id")) for x in (mec.get("coverage_units") or [])}
    pair=f"ORDERED_PAIR:{a}>{b}"
    tail="TAIL_SET:"+">".join(sorted((a,b,c),key=lambda z:int(z) if z.isdigit() else z))
    exact=f"EXACT_THIRD:{a}>{b}>{c}"
    return {
      "available":True,
      "profile":mec.get("profile"),
      "precompression_semantic_universe":bool(mec.get("precompression_semantic_universe")),
      "material_coverage_ratio":mec.get("material_coverage_ratio"),
      "ordered_pair_unit_present":pair in ids,
      "top3_tail_set_unit_present":tail in ids,
      "ordered_exact_unit_present":exact in ids,
      "minimum_required_capital":mec.get("minimum_required_capital"),
      "ticket_count":mec.get("ticket_count"),
      "semantic_tail_floor_count":mec.get("semantic_tail_floor_count"),
    }

def build_post_result_review(result:dict, final_artifact:dict)->dict:
    if not isinstance(result,dict) or not isinstance(final_artifact,dict):
        raise LearningError("INPUT_NOT_OBJECT")
    race_id=str(result.get("race_id") or "")
    if not race_id or race_id!=str(final_artifact.get("race_id") or ""):
        raise LearningError("RACE_ID_MISMATCH")
    top3=(result.get("official_result") or {}).get("top3")
    if not isinstance(top3,list) or len(top3)!=3:
        raise LearningError("OFFICIAL_TOP3_REQUIRED")
    top3=[int(x) for x in top3]
    ref=result.get("frozen_prediction_ref") or {}
    declared=str(ref.get("final_receipt_sha256") or "")
    actual=str(final_artifact.get("final_receipt_sha256") or "")
    if declared and actual and declared!=actual:
        raise LearningError(f"FINAL_RECEIPT_MISMATCH:{declared}!={actual}")

    roles=_roles(final_artifact)
    winner,p2,p3=map(str,top3)
    role_eval={
      "winner_w": "W" in roles.get(winner,set()),
      "second_p2": "P2" in roles.get(p2,set()),
      "third_p3": "P3" in roles.get(p3,set()),
    }
    coverage=_coverage(final_artifact,top3)
    mec_eval=_mec_actual_coverage(final_artifact,top3)

    ku=final_artifact.get("krs_prediction_utility") or {}
    if isinstance(ku,dict) and ku.get("utility_revision"):
        krs_eval=evaluate_against_result(ku,top3)
    else:
        krs_eval={"classification":"NOT_AVAILABLE","rescues":[],"supports":[],"misses":[]}

    settlement=result.get("settlement") or {}
    inv=int(settlement.get("total_investment") or coverage["investment"] or 0)
    ret=int(settlement.get("total_payout") or 0)
    pfs=(ret/inv*100.0) if inv>0 else None
    hit=bool(settlement.get("winning_tickets")) or bool(coverage["matching_ticket_types"])
    hit_but_loss=bool(hit and inv>0 and ret<inv)

    if not role_eval["winner_w"]:
        first_failure="PREDICTION_ROLE_W"
    elif not role_eval["second_p2"]:
        first_failure="PREDICTION_ROLE_P2"
    elif not role_eval["third_p3"]:
        first_failure="PREDICTION_ROLE_P3"
    elif not coverage["ordered_pair_ticket_coverage"]:
        first_failure="ORDERED_PAIR_CONVERSION"
    elif not coverage["top3_set_ticket_coverage"]:
        first_failure="THIRD_SET_COVERAGE"
    elif not coverage["ordered_exact_ticket_coverage"]:
        first_failure="EXACT_ORIENTATION"
    elif hit_but_loss:
        first_failure="CAPITAL_EFFICIENCY"
    else:
        first_failure="NONE"

    prediction_status=("PASS" if all(role_eval.values()) else "PARTIAL")
    conversion_status=("PASS" if coverage["ordered_pair_ticket_coverage"] and coverage["top3_set_ticket_coverage"] else "PARTIAL")
    capital_status=("PASS" if pfs is not None and pfs>=100.0 else "PARTIAL")

    review={
      "profile":LEARNING_PROFILE,
      "race_id":race_id,
      "formal_grade":ref.get("final_status") or "UNKNOWN",
      "immutable_final_artifact_sha256":final_artifact.get("sha256"),
      "final_receipt_sha256":actual or declared,
      "official_top3":top3,
      "prediction":{
        "status":prediction_status,
        "role_capture":role_eval,
        "ranking":(final_artifact.get("final_prediction_package") or {}).get("ranking"),
      },
      "krs":{
        "pre_result_utility_class":ku.get("utility_class"),
        "post_result_evaluation":krs_eval,
      },
      "conversion":{
        "status":conversion_status,
        **coverage,
      },
      "mec":mec_eval,
      "capital":{
        "status":capital_status,
        "authority":settlement.get("pfs_authority"),
        "investment":inv,
        "return":ret,
        "profit_loss":ret-inv,
        "pfs":round(pfs,9) if pfs is not None else None,
        "hit":hit,
        "hit_but_loss":hit_but_loss,
      },
      "failure_localization":{
        "first_material_failure":first_failure,
        "automatic":True,
      },
      "production_change_authorized":False,
      "prequential_only":True,
    }
    review["sha256"]=_sha(review)
    return review

def build_learning_state(review:dict)->dict:
    ff=(review.get("failure_localization") or {}).get("first_material_failure")
    shadow=[]
    immediate=[]
    if ff=="THIRD_SET_COVERAGE":
        shadow.append("PAIR_THIRD_TAIL_COVERAGE")
    elif ff=="EXACT_ORIENTATION":
        shadow.append("EXACT_ORIENTATION_DISCRIMINATION")
    elif ff=="ORDERED_PAIR_CONVERSION":
        shadow.append("ORDERED_PAIR_CONVERSION")
    elif ff and ff.startswith("PREDICTION_ROLE_"):
        shadow.append(ff)
    elif ff=="CAPITAL_EFFICIENCY":
        shadow.append("CAPITAL_ALLOCATION_EFFICIENCY")

    krs=(review.get("krs") or {}).get("post_result_evaluation") or {}
    if krs.get("classification")=="UNIQUE-RESCUE":
        shadow.append("KRS_RESCUE_PROMOTION_EVIDENCE")
    if review.get("mec",{}).get("available") and review["mec"].get("precompression_semantic_universe") is not True:
        immediate.append("MEC_PRECOMPRESSION_SEMANTIC_UNIVERSE_REQUIRED")

    state={
      "profile":LEARNING_PROFILE,
      "race_id":review["race_id"],
      "state_id":review["race_id"]+"-LEARNING-NEXT",
      "source_review_sha256":review["sha256"],
      "status":"PREQUENTIAL-NEXT-RACE-ONLY",
      "immediate_correctness":sorted(set(immediate)),
      "shadow_candidates":sorted(set(shadow)),
      "reference_metrics":{
        "pfs":review.get("capital",{}).get("pfs"),
        "first_material_failure":ff,
        "krs_classification":krs.get("classification"),
        "mec_profile":review.get("mec",{}).get("profile"),
      },
      "forbidden":["RETROACTIVE_PREDICTION_REWRITE","AUTOMATIC_NUMERIC_WEIGHT_CHANGE","RESULT_DERIVED_FEATURE_REWRITE"],
      "production_change_authorized":False,
    }
    state["sha256"]=_sha(state)
    return state
