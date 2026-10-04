from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Dict, Iterable, List, Tuple

PROFILE="KM-JRA-SOURCE-DERIVED-CANDIDATE-SEMANTICS-v0.3-20261004-STRUCTURE-DERIVED"
ACTIVE={"CORE","PROTECTED","CONDITIONAL","RESIDUAL"}


def _sha(x:Any)->str:
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()


def _val(r:Dict[str,Any],name:str)->float:
    return float((r.get("canonical_components") or {})[name]["value"])


def _sort_ids(runners:List[Dict[str,Any]],metric:str)->List[str]:
    return [
        str(r["runner_id"])
        for r in sorted(runners,key=lambda r:(-_val(r,metric),int(r["runner_id"])))
    ]


def _upper_cluster(
    runners:List[Dict[str,Any]],
    metric:str,
    *,
    min_active:int,
    excluded:Iterable[str]=(),
)->Tuple[List[str],Dict[str,Any]]:
    """Return the naturally stronger 1-D score cluster.

    This deliberately uses no race budget and no fixed target width.  The only
    floor is the structural cardinality required to form the target column
    (1 head, 2 pair candidates, 3 triple candidates before exclusions).
    """
    excluded={str(x) for x in excluded}
    rows=[
        (str(r["runner_id"]),_val(r,metric))
        for r in runners if str(r["runner_id"]) not in excluded
    ]
    rows.sort(key=lambda z:(-z[1],int(z[0]) if z[0].isdigit() else z[0]))
    if not rows:
        return [],{
            "metric":metric,"method":"UPPER_CLUSTER_1D_KMEANS","status":"EMPTY",
            "range":None,"upper_centroid":None,"lower_centroid":None,
        }
    if len(rows)<=min_active:
        return [rid for rid,_ in rows],{
            "metric":metric,"method":"UPPER_CLUSTER_1D_KMEANS","status":"STRUCTURAL_FLOOR",
            "range":round(rows[0][1]-rows[-1][1],6),
            "upper_centroid":round(sum(v for _,v in rows)/len(rows),6),
            "lower_centroid":None,
        }

    vals=[v for _,v in rows]
    span=max(vals)-min(vals)
    if abs(span)<=1e-12:
        chosen=[rid for rid,_ in rows]
        return chosen,{
            "metric":metric,"method":"UPPER_CLUSTER_1D_KMEANS","status":"PARITY_ALL_ACTIVE",
            "range":0.0,"upper_centroid":vals[0],"lower_centroid":vals[0],
        }

    low=min(vals); high=max(vals)
    assignments=None
    for _ in range(64):
        now=[0 if abs(v-low)<=abs(v-high) else 1 for v in vals]
        if assignments==now:
            break
        assignments=now
        g0=[v for v,a in zip(vals,assignments) if a==0]
        g1=[v for v,a in zip(vals,assignments) if a==1]
        if not g0 or not g1:
            break
        low=sum(g0)/len(g0)
        high=sum(g1)/len(g1)
        if low>high:
            low,high=high,low
            assignments=[1-a for a in assignments]

    chosen=[rid for (rid,_),a in zip(rows,assignments or [1]*len(rows)) if a==1]
    # Combination-cardinality floor only; this is not a preferred width.
    if len(chosen)<min_active:
        chosen=[rid for rid,_ in rows[:min_active]]

    return chosen,{
        "metric":metric,
        "method":"UPPER_CLUSTER_1D_KMEANS",
        "status":"PASS",
        "range":round(span,6),
        "upper_centroid":round(high,6),
        "lower_centroid":round(low,6),
        "active_count":len(chosen),
        "field_count":len(rows),
        "structural_floor":min_active,
        "budget_input_used":False,
    }


def _future_multiplicity(w:int,p2:int,p3:int)->str:
    if w<=1 and p2<=2 and p3<=3:
        return "CONCENTRATED"
    if w<=1 and (p2>2 or p3>3):
        return "ASYMMETRIC"
    return "DIVERSE"


def build_candidate_semantics(request:Dict[str,Any])->Dict[str,Any]:
    req=copy.deepcopy(request)
    runners=req.get("runners") or []
    if len(runners)<2:
        raise ValueError("CANDIDATE_RUNNERS_INSUFFICIENT")

    ids=_sort_ids(runners,"ZAI_WIN")
    w_ids,w_diag=_upper_cluster(runners,"ZAI_WIN",min_active=1)
    p2_ids,p2_diag=_upper_cluster(runners,"ZAI_PLACE",min_active=min(2,len(runners)))
    p3_ids,p3_diag=_upper_cluster(runners,"T3I",min_active=min(3,len(runners)))

    role_registry=[]
    roles={rid:[] for rid in ids}
    column_rank={
        "W":{rid:i+1 for i,rid in enumerate(_sort_ids(runners,"ZAI_WIN"))},
        "P2":{rid:i+1 for i,rid in enumerate(_sort_ids(runners,"ZAI_PLACE"))},
        "P3":{rid:i+1 for i,rid in enumerate(_sort_ids(runners,"T3I"))},
    }
    active_map={"W":set(w_ids),"P2":set(p2_ids),"P3":set(p3_ids)}
    for rid in ids:
        for col in ("W","P2","P3"):
            if rid in active_map[col]:
                rank=column_rank[col][rid]
                status="CORE" if rank==1 else "PROTECTED"
                role_registry.append({
                    "runner_id":rid,"column":col,"status":status,
                    "reason":f"STRUCTURE_DERIVED_{col}_UPPER_CLUSTER_RANK_{rank}",
                    "authority":PROFILE,"production_authority":False,
                })
                roles[rid].append(col)
            else:
                role_registry.append({
                    "runner_id":rid,"column":col,"status":"EXCLUDED",
                    "reason":f"STRUCTURE_DERIVED_{col}_LOWER_CLUSTER",
                    "authority":PROFILE,"production_authority":False,
                })

    by={str(r["runner_id"]):r for r in runners}
    pair=[]
    pair_diags={}
    for h in w_ids:
        second_ids,diag=_upper_cluster(
            runners,"ZAI_PLACE",min_active=1,excluded={h}
        )
        # Respect the global active P2 semantic universe; if its intersection is
        # empty, retain the strongest distinct second as a structural necessity.
        seconds=[s for s in second_ids if s in active_map["P2"]]
        if not seconds:
            seconds=[s for s in _sort_ids(runners,"ZAI_PLACE") if s!=h][:1]
        pair_diags[h]={**diag,"active_seconds":seconds}
        for s in [x for x in p2_ids if x!=h]:
            is_purchase=s in seconds
            pair.append({
                "head":h,"second":s,
                "status":"PURCHASE" if is_purchase else "PROTECT",
                "reason":(
                    "STRUCTURE_DERIVED_PAIR_UPPER_CLUSTER"
                    if is_purchase else "STRUCTURE_DERIVED_PAIR_ACTIVE_P2_PROTECTION"
                ),
                "authority":PROFILE,"production_authority":False,
            })

    third=[]
    third_diags={}
    for p in [x for x in pair if x["status"]=="PURCHASE"]:
        h,s=p["head"],p["second"]
        purchase_thirds,diag=_upper_cluster(
            runners,"T3I",min_active=1,excluded={h,s}
        )
        active_thirds=[t for t in p3_ids if t not in {h,s}]
        chosen=[t for t in purchase_thirds if t in set(active_thirds)]
        if not chosen and active_thirds:
            chosen=active_thirds[:1]
        third_diags[f"{h}>{s}"]={**diag,"active_thirds":active_thirds,"purchase_thirds":chosen}
        for t in active_thirds:
            third.append({
                "head":h,"second":s,"third":t,
                "status":"PURCHASE" if t in chosen else "PROTECT",
                "reason":(
                    "STRUCTURE_DERIVED_THIRD_UPPER_CLUSTER"
                    if t in chosen else "STRUCTURE_DERIVED_THIRD_ACTIVE_P3_PROTECTION"
                ),
                "authority":PROFILE,"production_authority":False,
            })

    # AKI is a review trigger, never a direct ticket-count knob. Current JRA
    # Candidate 20-index materialization does not contain formal W/P2/P3-AKI,
    # so we preserve that gap rather than synthesizing fake AKI numbers.
    supplied_aki=req.get("aki_capital_bridge") if isinstance(req.get("aki_capital_bridge"),dict) else None
    aki_bridge={
        "profile":"KM-JRA-AKI-CAPITAL-BRIDGE-CANDIDATE-v0.1-20261004",
        "status":"SUPPLIED" if supplied_aki else "FORMAL_AKI_INPUT_NOT_AVAILABLE_IN_CURRENT_JRA_CANDIDATE_20_INDEX",
        "direct_ticket_count_control":False,
        "budget_input_used":False,
        "w_aki":None if not supplied_aki else supplied_aki.get("w_aki"),
        "p2_aki":None if not supplied_aki else supplied_aki.get("p2_aki"),
        "p3_aki":None if not supplied_aki else supplied_aki.get("p3_aki"),
        "asi":None if not supplied_aki else supplied_aki.get("asi"),
        "rsi":None if not supplied_aki else supplied_aki.get("rsi"),
        "head_review":"STRUCTURE_DERIVED_FROM_ZAI_WIN_UNTIL_FORMAL_W_AKI_IS_AVAILABLE",
        "second_review":"STRUCTURE_DERIVED_FROM_ZAI_PLACE_UNTIL_FORMAL_P2_AKI_IS_AVAILABLE",
        "third_review":"STRUCTURE_DERIVED_FROM_T3I_UNTIL_FORMAL_P3_AKI_IS_AVAILABLE",
        "production_authority":False,
    }

    fms=_future_multiplicity(len(w_ids),len(p2_ids),len(p3_ids))
    future_multiplicity={
        "profile":"KM-JRA-FUTURE-MULTIPLICITY-CANDIDATE-v0.1-20261004",
        "state":fms,
        "head_count":len(w_ids),
        "second_count":len(p2_ids),
        "third_count":len(p3_ids),
        "basis":"PRE_RESULT_SCORE_STRUCTURE / ROLE_CLUSTERING; FORMAL AKI REVIEW PENDING WHEN UNSUPPLIED",
        "epistemic_state":"UNRESOLVED" if not supplied_aki else "REVIEWED_BY_SUPPLIED_AKI_CONTEXT",
        "aleatoric_state":(
            "LOW" if fms=="CONCENTRATED" else "COLUMN_ASYMMETRIC" if fms=="ASYMMETRIC" else "MULTI_WORLD"
        ),
        "budget_input_used":False,
        "production_authority":False,
    }

    req["static_prediction"]={
        "ranking":ids,
        "roles":{rid:roles[rid] for rid in ids},
        "authority":PROFILE,
        "production_authority":False,
        "ranking_metric":"ZAI_WIN_CANDIDATE_DIAGNOSTIC",
    }
    req["role_registry"]=role_registry
    req["purchased_heads"]=w_ids
    req["pair_dispositions"]=pair
    req["third_dispositions"]=third
    req["orientation_exclusions"]=[]
    req["head_nonselection_reasons"]={}
    req["available_bet_types"]=["EXACTA","TRIO","TRIFECTA"]
    req["aki_capital_bridge"]=aki_bridge
    req["future_multiplicity"]=future_multiplicity

    # Capital is deliberately downstream. Preserve an explicit race-level cap,
    # but it must not participate in role/pair/third generation.
    if "capital_policy" in req and req.get("capital_policy") is not None:
        req["capital_policy"]=copy.deepcopy(req["capital_policy"])
    else:
        req.pop("capital_policy",None)

    req["candidate_semantic_freeze"]={
        "profile":PROFILE,
        "ranking":ids,
        "w_active":w_ids,
        "p2_active":p2_ids,
        "p3_active":p3_ids,
        "role_registry_count":len(role_registry),
        "pair_count":len(pair),
        "third_count":len(third),
        "width_policy":{
            "policy_id":"KM-JRA-CANDIDATE-STRUCTURE-DERIVED-WIDTH-20261004-R1",
            "driver":"RACE_FORCE_RELATIONSHIP_NOT_BUDGET",
            "fixed_w_width":None,
            "fixed_p2_width":None,
            "fixed_p3_width":None,
            "target_capital_band_yen":None,
            "budget_fill_forbidden":True,
            "budget_input_used":False,
            "w_structure":w_diag,
            "p2_structure":p2_diag,
            "p3_structure":p3_diag,
            "pair_structure":pair_diags,
            "third_structure":third_diags,
            "future_multiplicity_state":fms,
            "aki_direct_ticket_count_prohibited":True,
            "note":"Ticket width emerges from pre-result score/role structure. AKI is a column review trigger, never a budget or fixed-count controller.",
        },
        "production_authority":False,
    }
    req["candidate_semantic_freeze"]["sha256"]=_sha(req["candidate_semantic_freeze"])
    req["candidate_policy_cohort"]="JRA-CANDIDATE-v0.3-STRUCTURE-DERIVED"

    req["final_prediction_package"]={
        "authority":PROFILE,
        "candidate_only":True,
        "production_authority":False,
        "static_prediction":copy.deepcopy(req["static_prediction"]),
        "role_registry":copy.deepcopy(role_registry),
        "pair_dispositions":copy.deepcopy(pair),
        "third_dispositions":copy.deepcopy(third),
        "aki_capital_bridge":copy.deepcopy(aki_bridge),
        "future_multiplicity":copy.deepcopy(future_multiplicity),
        "candidate_semantic_freeze_sha256":req["candidate_semantic_freeze"]["sha256"],
        "notice":"Engineering/OOS candidate only. Ticket width is structure-derived; race budget is downstream only. Formal JRA AKI numerics remain an explicit gap unless supplied.",
    }
    return req
