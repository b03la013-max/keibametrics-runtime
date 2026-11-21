from __future__ import annotations
import hashlib, json
from typing import Any
from jra_krs_measurement import evaluate_against_result
from family_pfs_improvement import build_pfs_improvement_assessment

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
    purchased_exacta=False
    purchased_trio=False
    exact_oriented_set=False
    top3set=False
    exact=False
    hit_types=[]
    for t in tickets:
        bt,sel=_ticket_key(t)
        if bt=="EXACTA" and sel==(a,b):
            exacta=True; purchased_exacta=True; hit_types.append("EXACTA")
        elif bt=="TRIO" and set(sel)=={a,b,c}:
            top3set=True; purchased_trio=True; hit_types.append("TRIO")
        elif bt=="TRIFECTA":
            if len(sel)>=2 and sel[:2]==(a,b):
                exacta=True
            if len(sel)==3 and set(sel)=={a,b,c}:
                top3set=True
                exact_oriented_set=True
            if sel==(a,b,c):
                exact=True; hit_types.append("TRIFECTA")
    return {
      "ordered_pair_ticket_coverage":exacta,
      "top3_set_ticket_coverage":top3set,
      "purchased_trio_ticket_coverage":purchased_trio,
      "exact_oriented_top3_set_coverage":exact_oriented_set,
      "purchased_exacta_ticket_coverage":purchased_exacta,
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

_JRA_TRIO_REVIEW = "DECISION_AWARE_V4"
_INDEPENDENT_REVIEW_MODES = {"DECISION_AWARE_V3", _JRA_TRIO_REVIEW}


def _trio_key(selection):
    if not isinstance(selection, (list, tuple)):
        return None
    ids = frozenset(map(str, selection))
    return ids if len(selection) == len(ids) == 3 and all(
        rid.isascii() and rid.isdecimal() and 1 <= int(rid) <= 18 and str(int(rid)) == rid
        for rid in ids) else None


def _jra_trio_reachability(final, orders, roles, settlement, paper):
    """KMS unordered funnel from existing frozen evidence and actual settlement."""
    fp = final.get("final_prediction_package") or {}
    rank = {str(rid): i for i, rid in enumerate(fp.get("ranking") or [], 1)}
    mec = final.get("minimum_efficient_coverage") or {}
    final_ticket = final.get("final_ticket") or {}
    capital = final.get("capital_policy_decision") or {}
    units = mec.get("coverage_units")
    candidates = mec.get("tickets")
    role_basis_observed = isinstance(fp.get("roles"), dict) or isinstance(final.get("role_registry"), list)
    final_trios = [t for t in final_ticket.get("tickets") or []
                   if t.get("bet_type") == "TRIO"]
    trio_keys = [_trio_key(t.get("selection")) for t in final_trios]
    common_members = (frozenset.intersection(*trio_keys)
                      if trio_keys and all(trio_keys) else None)
    wins = settlement.get("winning_tickets")
    refunds = settlement.get("refunded_tickets")
    status = str(settlement.get("status") or "").upper()
    zero_exposure = (not final_trios and (paper or final_ticket.get("no_bet") is True
                    or capital.get("decision") == "NO_BET"))
    invested = sum(t["stake"] for t in final_trios)
    refunded = returned = effective = pfs = None
    if not invested:
        refunded = returned = effective = 0
    elif status in {"SETTLED", "COMPLETE"}:
        if isinstance(refunds, list):
            refunded = sum(t["refund"] for t in refunds if t.get("bet_type") == "TRIO")
        elif settlement.get("refund") == 0:
            refunded = 0
        if isinstance(wins, list):
            returned = sum(t["return"] for t in wins if t.get("bet_type") == "TRIO")
        if refunded is not None and 0 <= refunded <= invested:
            effective = invested - refunded
        if returned is not None and effective:
            pfs = round(100.0 * returned / effective, 9)

    outcomes = []
    for top3 in sorted({tuple(sorted(order)) for order in orders}):
        key = _trio_key(top3)
        members = [
            {"runner_id": rid, "static_rank": rank.get(str(rid)),
             "active_roles": sorted(roles.get(str(rid), set()) & {"W", "P2", "P3"})}
            for rid in top3
        ]
        missing = ([row["runner_id"] for row in members if not row["active_roles"]]
                   if role_basis_observed else None)
        sources = None if units is None else sorted({u["kind"] for u in units
            if u.get("kind") in {"TAIL_SET", "EXACT_THIRD"} and _trio_key(u.get("parts")) == key})
        generated = None if candidates is None else any(t.get("bet_type") == "TRIO"
            and _trio_key(t.get("selection")) == key for t in candidates)
        stake = sum(t["stake"] for t in final_trios if _trio_key(t.get("selection")) == key)
        outcome_return = None if returned is None else sum(
            t["return"] for t in wins or [] if t.get("bet_type") == "TRIO"
            and _trio_key(t.get("selection")) == key)
        if stake:
            failure = ("TRIO_SETTLEMENT_UNAVAILABLE" if outcome_return is None else
                       "TRIO_SETTLEMENT_NO_RECORDED_RETURN" if not outcome_return else
                       "TRIO_CAPITAL_EFFICIENCY" if pfs is not None and pfs < 100 else "NONE")
        elif zero_exposure:
            failure = "NOT_APPLICABLE_ZERO_EXPOSURE"
        elif generated is True:
            failure = "TRIO_FINAL_SELECTION_MISSING"
        elif generated is False and sources:
            failure = "MEC_TRIO_NOT_GENERATED"
        elif missing:
            failure = "PLACE_ROLE_MEMBER_MISSING"
        elif generated is False and sources == []:
            failure = "JOINT_SET_NOT_REACHABLE"
        else:
            failure = "TRIO_REACHABILITY_UNAVAILABLE"
        outcomes.append({
            "official_unordered_top3": list(top3),
            "members": members,
            "missing_place_role_members": missing,
            "mec_joint_set_evidence": sources,
            "mec_trio_candidate_reachable": generated,
            "final_trio_ticket_coverage": stake > 0,
            "all_shared_ticket_members_survive": (
                common_members <= key if common_members else None),
            "frozen_trio_stake": stake,
            "settled_trio_return": outcome_return,
            "first_trio_failure": failure,
        })

    return {
        "place_member_basis": "FROZEN_W_P2_P3_UNION_PROXY",
        "capital_decision": capital.get("decision"),
        # This measures joint exposure. A common selection does not prove
        # that a designated axis or two-axis policy caused the dependence.
        "shared_final_trio_ticket_members": (
            sorted(map(int, common_members)) if common_members is not None else None),
        "final_trio_disposition": next((row for row in final_ticket.get("bet_type_dispositions") or []
                                        if row.get("bet_type") == "TRIO"), None),
        "trio_ticket_count": len(final_trios),
        "frozen_trio_investment": invested,
        "trio_refund": refunded,
        "effective_trio_investment": effective,
        "settled_trio_return": returned,
        "trio_profit_loss": returned - effective if returned is not None and effective is not None else None,
        "trio_pfs": pfs,
        "actual_purchase_inferred": False,
        "by_valid_unordered_set": outcomes,
    }


def build_post_result_review(result:dict, final_artifact:dict, *, review_semantics="LEGACY")->dict:
    if review_semantics not in {"LEGACY", "DECISION_AWARE_V2"} | _INDEPENDENT_REVIEW_MODES:
        raise LearningError("REVIEW_SEMANTICS_UNSUPPORTED")
    if not isinstance(result,dict) or not isinstance(final_artifact,dict):
        raise LearningError("INPUT_NOT_OBJECT")
    race_id=str(result.get("race_id") or "")
    if not race_id or race_id!=str(final_artifact.get("race_id") or ""):
        raise LearningError("RACE_ID_MISMATCH")
    if review_semantics in _INDEPENDENT_REVIEW_MODES and (
            final_artifact.get("family_id")!="JRA" or not race_id.startswith("KM-JRA-")):
        raise LearningError(review_semantics+"_JRA_ONLY")
    top3=(result.get("official_result") or {}).get("top3")
    if not isinstance(top3,list) or len(top3)!=3:
        raise LearningError("OFFICIAL_TOP3_REQUIRED")
    top3=[int(x) for x in top3]
    official=result.get("official_result") or {}
    orders=[top3]
    # Follow the canonical race identity, as the shared KRS adapter does.
    # LOCAL/BAN keep their existing review schema and do not import a JRA
    # collector or inherit JRA-specific finish-group requirements.
    if race_id.startswith("KM-JRA-"):
        from jra_candidate_postresult_closedloop import official_top3_orders
        try:
            orders=official_top3_orders({**official,"top3":top3})
        except (ValueError,KeyError,TypeError) as exc:
            raise LearningError("OFFICIAL_FINISH_GROUPS_INVALID:"+str(exc)) from exc
    ref=result.get("frozen_prediction_ref") or {}
    declared=str(ref.get("final_receipt_sha256") or "")
    actual=str(final_artifact.get("final_receipt_sha256") or "")
    if declared and actual and declared!=actual:
        raise LearningError(f"FINAL_RECEIPT_MISMATCH:{declared}!={actual}")

    roles=_roles(final_artifact)
    role_orders=[{"winner_w":"W" in roles.get(str(order[0]),set()),
                  "second_p2":"P2" in roles.get(str(order[1]),set()),
                  "third_p3":"P3" in roles.get(str(order[2]),set())} for order in orders]
    role_eval={key:any(row[key] for row in role_orders) for key in role_orders[0]}
    coverages=[_coverage(final_artifact,order) for order in orders]
    coverage={**coverages[0]}
    for key,value in coverage.items():
        if type(value) is bool:coverage[key]=any(row[key] for row in coverages)
    coverage["matching_ticket_types"]=sorted({kind for row in coverages for kind in row["matching_ticket_types"]})
    mec_orders=[_mec_actual_coverage(final_artifact,order) for order in orders]
    mec_eval={**mec_orders[0]}
    for key,value in mec_eval.items():
        if type(value) is bool:mec_eval[key]=any(row[key] for row in mec_orders)

    ku=final_artifact.get("krs_prediction_utility") or {}
    if isinstance(ku,dict) and ku.get("utility_revision"):
        def krs_for(order):return evaluate_against_result(ku,order,
            static_ranking=(final_artifact.get("static_prediction") or {}).get("ranking")
                or (final_artifact.get("final_prediction_package") or {}).get("ranking"),
            static_roles=roles)
        if len(orders)==1:krs_eval=krs_for(top3)
        else:krs_eval={"classification":"DEAD_HEAT_MULTIPLE_VALID_ORDERS",
                       "aggregation":"PER_VALID_ORDER_NO_SINGLE_RESCUE_CLASS_CLAIM",
                       "by_valid_order":[{"top3":order,"evaluation":krs_for(order)} for order in orders]}
    else:
        krs_eval={"classification":"NOT_AVAILABLE","rescues":[],"supports":[],"misses":[]}

    settlement=result.get("settlement") or {}
    settlement_status=str(settlement.get("status") or "COMPLETE").upper()
    inv_raw=settlement.get("total_investment",settlement.get("investment",coverage["investment"]))
    inv=int(inv_raw) if inv_raw is not None else int(coverage["investment"] or 0)
    ret_raw=settlement.get("total_payout",settlement.get("return"))
    settled_inv_raw=settlement.get("settled_investment")
    refund=int(settlement.get("refund") or 0)
    effective_inv=int(settlement.get("effective_investment",inv-refund))
    if not (0<=refund<=inv and effective_inv==inv-refund):
        raise LearningError("SETTLEMENT_REFUND_INCONSISTENT")
    if settlement_status in {"PENDING","UNKNOWN"}:
        ret=None
        settled_inv=None
        pfs=None
        profit_loss=None
        settlement_completeness=None
    elif settlement_status=="PARTIAL":
        ret=int(ret_raw) if ret_raw is not None else None
        settled_inv=int(settled_inv_raw) if settled_inv_raw is not None else None
        pfs=(ret/settled_inv*100.0) if ret is not None and settled_inv not in (None,0) else None
        profit_loss=(ret-settled_inv) if ret is not None and settled_inv is not None else None
        settlement_completeness=(settled_inv/inv*100.0) if settled_inv is not None and inv>0 else None
    else:
        ret=int(ret_raw) if ret_raw is not None else None
        settled_inv=effective_inv
        pfs=(ret/effective_inv*100.0) if ret is not None and effective_inv>0 else None
        profit_loss=(ret+refund-inv) if ret is not None else None
        settlement_completeness=100.0 if ret is not None else None
    hit=bool(settlement.get("winning_tickets")) or bool(coverage["matching_ticket_types"])
    hit_but_loss=bool(hit and pfs is not None and pfs<100.0)

    decision_aware=review_semantics != "LEGACY"
    capital_decision=final_artifact.get("capital_policy_decision") or {}
    ft=final_artifact.get("final_ticket") or {}
    paper=bool(capital_decision.get("decision")=="PAPER" and ft.get("no_bet") is True
               and not ft.get("tickets") and inv==0 and coverage["investment"]==0)

    if not role_eval["winner_w"]:
        first_failure="PREDICTION_ROLE_W"
    elif not role_eval["second_p2"]:
        first_failure="PREDICTION_ROLE_P2"
    elif not role_eval["third_p3"]:
        first_failure="PREDICTION_ROLE_P3"
    elif decision_aware and paper:
        first_failure="NONE"
    elif not coverage["ordered_pair_ticket_coverage"]:
        first_failure="ORDERED_PAIR_CONVERSION"
    elif not coverage["top3_set_ticket_coverage"]:
        first_failure="THIRD_SET_COVERAGE"
    elif not coverage["ordered_exact_ticket_coverage"] and not (
            decision_aware and mec_eval.get("available") and
            mec_eval.get("ordered_exact_unit_present") is False):
        first_failure="EXACT_ORIENTATION"
    elif hit_but_loss:
        first_failure="CAPITAL_EFFICIENCY"
    else:
        first_failure="NONE"

    prediction_status=("PASS" if all(role_eval.values()) else "PARTIAL")
    conversion_status=("PASS" if coverage["ordered_pair_ticket_coverage"] and coverage["top3_set_ticket_coverage"] else "PARTIAL")
    capital_status=("HOLD" if settlement_status in {"PENDING","UNKNOWN"} else ("PASS" if pfs is not None and pfs>=100.0 else "PARTIAL"))
    if decision_aware and paper:
        conversion_status=capital_status="NOT_APPLICABLE_PAPER"

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
        "settlement_status":settlement_status,
        "investment":inv,
        "settled_investment":settled_inv,
        "return":ret,
        "profit_loss":profit_loss,
        "pfs":round(pfs,9) if pfs is not None else None,
        "settlement_completeness_pct":round(settlement_completeness,9) if settlement_completeness is not None else None,
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
    if decision_aware:
        review["review_semantics"]=review_semantics
        review["policy_compliance"]={
            "capital_decision":capital_decision.get("decision"),
            "paper_zero_exposure_compliant":paper if capital_decision.get("decision")=="PAPER" else None,
            "zero_exposure_reason":"PAPER_POLICY" if paper else None,
            "prediction_quality_is_separate":True,
        }
        review["failure_localization"]["residual_diagnostics"]=(
            ["EXACT_ORIENTATION_NOT_CAPTURED"] if not paper and not
            coverage["ordered_exact_ticket_coverage"] else [])
        if paper:
            review["capital"]["pfs_status"]="NOT_APPLICABLE_ZERO_EXPOSURE"
    if len(orders)>1:
        review.update(official_top3_orders=orders,official_finish_groups=official["finish_groups"],
                      official_top3_is_legacy_representative=True)
        review["prediction"]["dead_heat_order_evaluations"]=[
            {"top3":order,"role_capture":role_order,"ticket_coverage":order_coverage,
             "mec_coverage":order_mec}
            for order,role_order,order_coverage,order_mec in zip(orders,role_orders,coverages,mec_orders)]
        review["prediction"]["dead_heat_capture_aggregation"]="ANY_VALID_ORDER_PER_ROLE; JOINT_ORDERS_RETAINED"
    if review_semantics in _INDEPENDENT_REVIEW_MODES:
        # All three role captures are independent observations. A missed winner
        # does not make the actual second/third horse's Role capture unobservable.
        independent=["PREDICTION_ROLE_"+role for role,key in
                     (("W","winner_w"),("P2","second_p2"),("P3","third_p3"))
                     if not role_eval[key]]
        dependent=[]
        conversion_independent=[]
        # ANY-per-Role aggregation across dead-heat orders is not a joint
        # capture. Downstream eligibility must hold within one valid order.
        joint_cases=review["prediction"].get("dead_heat_order_evaluations") or [
            {"role_capture":role_eval,"ticket_coverage":coverage,"mec_coverage":mec_eval}]
        pair_prerequisites=any(row["role_capture"]["winner_w"] and
                               row["role_capture"]["second_p2"] for row in joint_cases)
        all_roles=any(all(row["role_capture"].values()) for row in joint_cases)
        exact_prerequisites=any(all(row["role_capture"].values()) and
            row["ticket_coverage"]["ordered_pair_ticket_coverage"] and
            row["ticket_coverage"]["top3_set_ticket_coverage"] and not (
                row["mec_coverage"].get("available") and
                row["mec_coverage"].get("ordered_exact_unit_present") is False)
            for row in joint_cases)
        if not paper:
            for name,covered,eligible in (
                    ("ORDERED_PAIR_CONVERSION",coverage["ordered_pair_ticket_coverage"],pair_prerequisites),
                    ("THIRD_SET_COVERAGE",coverage["top3_set_ticket_coverage"],all_roles),
                    ("EXACT_ORIENTATION",coverage["ordered_exact_ticket_coverage"],
                     exact_prerequisites)):
                if not covered:
                    (conversion_independent if eligible else dependent).append(name)
        review["failure_localization"].update(
            independent_role_failures=independent,
            secondary_independent_role_failures=[x for x in independent if x!=first_failure],
            independent_conversion_failures=conversion_independent,
            dependent_conversion_failures=dependent,
            capital_failure="HIT_BUT_LOSS" if hit_but_loss else None,
            joint_pair_role_capture_any_valid_order=pair_prerequisites,
            joint_all_role_capture_any_valid_order=all_roles,
            downstream_dependencies_are_diagnostics=True,
        )
    # Preserve historical review hashes when the original settlement did not
    # carry refund accounting. New settlements expose the separate denominator.
    if refund or "effective_investment" in settlement:
        review["capital"].update(refund=refund,effective_investment=effective_inv)
    review["pfs_improvement"]=build_pfs_improvement_assessment(review)
    if review_semantics == _JRA_TRIO_REVIEW:
        review["trio_reachability"] = _jra_trio_reachability(
            final_artifact, orders, roles, settlement, paper)
    review["sha256"]=_sha(review)
    return review

def build_learning_state(review:dict, *, effective_time=None)->dict:
    ff=(review.get("failure_localization") or {}).get("first_material_failure")
    pfs_improvement=review.get("pfs_improvement") or build_pfs_improvement_assessment(review)
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

    semantics=review.get("review_semantics")
    v3=semantics in _INDEPENDENT_REVIEW_MODES
    if v3:
        if not str(review.get("race_id") or "").startswith("KM-JRA-"):
            raise LearningError(semantics+"_JRA_ONLY")
        failures=review.get("failure_localization") or {}
        if ff in (failures.get("dependent_conversion_failures") or []):
            shadow=[]
        shadow.extend(failures.get("independent_role_failures") or [])

    krs=(review.get("krs") or {}).get("post_result_evaluation") or {}
    if krs.get("classification")=="UNIQUE-RESCUE":
        shadow.append("KRS_RESCUE_PROMOTION_EVIDENCE")
    if review.get("mec",{}).get("available") and review["mec"].get("precompression_semantic_universe") is not True:
        immediate.append("MEC_PRECOMPRESSION_SEMANTIC_UNIVERSE_REQUIRED")
    shadow.extend(pfs_improvement.get("test_next_tracks") or [])

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
        "dominant_pfs_loss_owner":(pfs_improvement.get("dominant_pfs_loss_owner") or {}).get("owner"),
        "hit_but_loss":pfs_improvement.get("hit_but_loss"),
        "krs_classification":krs.get("classification"),
        "mec_profile":review.get("mec",{}).get("profile"),
      },
      "pfs_improvement_profile":pfs_improvement.get("profile"),
      "improvement_routes":pfs_improvement.get("learning_routes") or [],
      "no_stagnation_satisfied":bool(pfs_improvement.get("no_stagnation_satisfied")),
      "forbidden":["RETROACTIVE_PREDICTION_REWRITE","AUTOMATIC_NUMERIC_WEIGHT_CHANGE","RESULT_DERIVED_FEATURE_REWRITE"],
      "production_change_authorized":False,
    }
    if v3:
        state["review_semantics"]=semantics
        state["reference_metrics"].update({
            key:(review.get("failure_localization") or {}).get(key,[])
            for key in ("independent_role_failures","secondary_independent_role_failures",
                        "independent_conversion_failures","dependent_conversion_failures")})
    if semantics == _JRA_TRIO_REVIEW:
        trio = review["trio_reachability"]
        state["reference_metrics"]["trio_reachability"] = {
            "trio_pfs": trio["trio_pfs"],
            "by_valid_unordered_set": [
                {k: row[k] for k in ("official_unordered_top3", "first_trio_failure")}
                for row in trio["by_valid_unordered_set"]],
        }
    if effective_time is not None:
        from datetime import datetime
        when=datetime.fromisoformat(effective_time.replace('Z','+00:00'))
        if when.tzinfo is None:
            raise LearningError("LEARNING_TIMEZONE_REQUIRED")
        state["effective_time"]=when.isoformat()
        state["learning_validity"]="FAMILY-CANDIDATE"
        state["prediction_use"]="SHADOW_REVIEW_CONTEXT_ONLY"
    state["sha256"]=_sha(state)
    return state
