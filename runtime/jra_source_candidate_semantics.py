from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Dict

PROFILE="KM-JRA-SOURCE-DERIVED-CANDIDATE-SEMANTICS-v0.1-20260926"
ACTIVE={"CORE","PROTECTED","CONDITIONAL","RESIDUAL"}

def _sha(x:Any)->str:
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()

def _val(r:Dict[str,Any],name:str)->float:
    return float((r.get("canonical_components") or {})[name]["value"])

def build_candidate_semantics(request:Dict[str,Any])->Dict[str,Any]:
    req=copy.deepcopy(request)
    runners=req.get("runners") or []
    if len(runners)<2:
        raise ValueError("CANDIDATE_RUNNERS_INSUFFICIENT")
    ordered=sorted(runners,key=lambda r:(-_val(r,"ZAI_WIN"),int(r["runner_id"])))
    ids=[str(r["runner_id"]) for r in ordered]
    w_ids=ids[:min(2,len(ids))]
    p2_order=[str(r["runner_id"]) for r in sorted(runners,key=lambda r:(-_val(r,"ZAI_PLACE"),int(r["runner_id"])))]
    p2_ids=p2_order[:min(4,len(p2_order))]
    p3_order=[str(r["runner_id"]) for r in sorted(runners,key=lambda r:(-_val(r,"T3I"),int(r["runner_id"])))]
    p3_ids=p3_order[:min(6,len(p3_order))]

    role_registry=[]
    roles={rid:[] for rid in ids}
    for rid in ids:
        for col,active_ids in (("W",w_ids),("P2",p2_ids),("P3",p3_ids)):
            if rid in active_ids:
                pos=active_ids.index(rid)
                status="CORE" if pos < (1 if col=="W" else 2 if col=="P2" else 3) else "PROTECTED"
                role_registry.append({
                    "runner_id":rid,"column":col,"status":status,
                    "reason":f"CANDIDATE_{col}_RANK_{pos+1}",
                    "authority":PROFILE,"production_authority":False,
                })
                roles[rid].append(col)
            else:
                role_registry.append({
                    "runner_id":rid,"column":col,"status":"EXCLUDED",
                    "reason":f"CANDIDATE_OUTSIDE_{col}_ACTIVE_ZONE",
                    "authority":PROFILE,"production_authority":False,
                })

    by={str(r["runner_id"]):r for r in runners}
    pair=[]
    for h in w_ids:
        seconds=[s for s in p2_ids if s!=h]
        seconds=sorted(seconds,key=lambda s:(-(_val(by[h],"ZAI_WIN")+_val(by[s],"ZAI_PLACE")),int(s)))
        for i,s in enumerate(seconds):
            pair.append({
                "head":h,"second":s,
                "status":"PURCHASE" if i<2 else "PROTECT",
                "reason":f"CANDIDATE_PAIR_SCORE_RANK_{i+1}",
                "authority":PROFILE,"production_authority":False,
            })

    third=[]
    for p in [x for x in pair if x["status"]=="PURCHASE"]:
        h,s=p["head"],p["second"]
        thirds=[t for t in p3_ids if t not in {h,s}]
        thirds=sorted(thirds,key=lambda t:(-_val(by[t],"T3I"),int(t)))
        for i,t in enumerate(thirds):
            third.append({
                "head":h,"second":s,"third":t,
                "status":"PURCHASE" if i==0 else "PROTECT",
                "reason":f"CANDIDATE_THIRD_T3I_RANK_{i+1}",
                "authority":PROFILE,"production_authority":False,
            })

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
    req["capital_policy"]=copy.deepcopy(req.get("capital_policy") or {"mode":"RECOMMENDATION_ONLY"})
    req["candidate_semantic_freeze"]={
        "profile":PROFILE,
        "ranking":ids,
        "w_active":w_ids,
        "p2_active":p2_ids,
        "p3_active":p3_ids,
        "role_registry_count":len(role_registry),
        "pair_count":len(pair),
        "third_count":len(third),
        "production_authority":False,
    }
    req["candidate_semantic_freeze"]["sha256"]=_sha(req["candidate_semantic_freeze"])
    req["final_prediction_package"]={
        "authority":PROFILE,
        "candidate_only":True,
        "production_authority":False,
        "static_prediction":copy.deepcopy(req["static_prediction"]),
        "role_registry":copy.deepcopy(role_registry),
        "pair_dispositions":copy.deepcopy(pair),
        "third_dispositions":copy.deepcopy(third),
        "candidate_semantic_freeze_sha256":req["candidate_semantic_freeze"]["sha256"],
        "notice":"Engineering/OOS candidate only. Must never overwrite Production Static/Role/Pair/Third.",
    }
    return req
