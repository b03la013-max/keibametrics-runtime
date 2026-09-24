from __future__ import annotations
import copy, hashlib, json
from datetime import datetime, timezone
from typing import Any, Dict, List
from mec_r4_shadow import settle_ticket_list

PROFILE="KM-LOCAL-MEC-R5-SET-PAIR-ORIENTATION-SHADOW-CANDIDATE-20260924-R1"
CANDIDATE_ID="LOCAL-MEC-R5-SPO-SHADOW-v0.1"
ARM_ORDER=["SET_ONLY","SET_PAIR"]+[f"SET_PAIR_EXACT_TOP{k}" for k in range(3,9)]
HARD_MARKERS=("STRUCTURAL","NOT_APPLICABLE","IMPOSSIBLE","SCRATCH","WITHDRAWN",
              "ROLE_INELIGIBLE","UNIVERSE_MISMATCH","FORMAL_OUT_OF_SCOPE")

def _canon(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def _sha(x): return hashlib.sha256(_canon(x).encode()).hexdigest()

def _norm(bt,sel):
    a=[int(x) for x in sel]
    return tuple(sorted(a)) if str(bt).upper()=="TRIO" else tuple(a)

def _key(bt,sel): return (str(bt).upper(),_norm(bt,sel))

def _add(store,bt,sel,stake=100,source="R5"):
    bt=str(bt).upper(); k=_key(bt,sel)
    if k not in store:
        store[k]={"bet_type":bt,"selection":[int(x) for x in sel],"stake":int(stake or 100),"shadow_source":source}

def _ranking(req,art):
    fp=art.get("final_prediction_package") or req.get("final_prediction_package") or {}
    return [int(x) for x in (fp.get("ranking") or (req.get("static_prediction") or {}).get("ranking") or [])]

def _roles(req,art):
    fp=art.get("final_prediction_package") or req.get("final_prediction_package") or {}
    return fp.get("roles") or (req.get("static_prediction") or {}).get("roles") or {}

def _hard_exclusions(req):
    out=set()
    for x in req.get("third_dispositions") or []:
        if str(x.get("status") or "").upper()!="EXCLUDE": continue
        reason=str(x.get("reason") or "").upper()
        if any(m in reason for m in HARD_MARKERS):
            out.add((int(x["head"]),int(x["second"]),int(x["third"])))
    return out

def _material_pairs(req):
    out=[]
    for x in req.get("pair_dispositions") or []:
        if str(x.get("status") or "").upper() in {"PURCHASE","PROTECT"}:
            out.append((int(x["head"]),int(x["second"]),str(x.get("status")).upper()))
    return out

def _production_tickets(art):
    return copy.deepcopy((art.get("final_ticket") or {}).get("tickets") or [])

def _exact_universe(req,art,top_k):
    rank={h:i+1 for i,h in enumerate(_ranking(req,art))}
    p3={int(k) for k,v in _roles(req,art).items() if "P3" in (v or [])}
    hard=_hard_exclusions(req)
    out=[]
    for h,s,pstat in _material_pairs(req):
        for t in sorted(p3):
            if t in {h,s}: continue
            if (h,s,t) in hard: continue
            if not all(rank.get(x,10**9)<=top_k for x in (h,s,t)): continue
            out.append((h,s,t,pstat))
    return out

def build_arm(req:Dict[str,Any], final_envelope:Dict[str,Any], name:str)->Dict[str,Any]:
    art=final_envelope.get("artifact") or final_envelope
    tickets=_production_tickets(art)
    store={}
    # LOCAL evidence from 2026-09-23 showed unordered set protection is the
    # low-capital carrier of many correct top3 structures. Preserve ALL TRIO.
    for t in tickets:
        if str(t.get("bet_type") or "").upper()=="TRIO":
            _add(store,"TRIO",t["selection"],t.get("stake") or 100,"R3_SET_COVERAGE")
    if name!="SET_ONLY":
        for t in tickets:
            if str(t.get("bet_type") or "").upper()=="EXACTA":
                _add(store,"EXACTA",t["selection"],t.get("stake") or 100,"R3_ORDERED_PAIR")
    top_k=None
    if name.startswith("SET_PAIR_EXACT_TOP"):
        top_k=int(name.replace("SET_PAIR_EXACT_TOP",""))
        for h,s,t,pstat in _exact_universe(req,art,top_k):
            _add(store,"TRIFECTA",[h,s,t],100,"ORIENTATION_"+pstat+"_TOP"+str(top_k))

    rows=sorted(store.values(),key=lambda x:(x["bet_type"],tuple(x["selection"])))
    prod_trio={_key(t["bet_type"],t["selection"]) for t in tickets if str(t.get("bet_type") or "").upper()=="TRIO"}
    prod_exacta={_key(t["bet_type"],t["selection"]) for t in tickets if str(t.get("bet_type") or "").upper()=="EXACTA"}
    retained={_key(t["bet_type"],t["selection"]) for t in rows}
    set_ret=len(prod_trio & retained)/len(prod_trio) if prod_trio else 1.0
    pair_ret=len(prod_exacta & retained)/len(prod_exacta) if prod_exacta else (1.0 if name!="SET_ONLY" else 0.0)
    return {
      "arm":name,"production_authority":False,
      "ticket_count":len(rows),"minimum_shadow_capital":sum(int(x["stake"]) for x in rows),
      "set_coverage_retention_ratio":round(set_ret,9),
      "ordered_pair_retention_ratio":round(pair_ret,9),
      "exact_top_k":top_k,
      "tickets":rows,"sha256":_sha(rows)
    }

def build_shadow(req,final_envelope,generated_at=None,basis_sha256=None):
    generated_at=generated_at or datetime.now(timezone.utc).isoformat()
    arms={a:build_arm(req,final_envelope,a) for a in ARM_ORDER}
    out={
      "profile":PROFILE,"candidate_id":CANDIDATE_ID,
      "status":"SHADOW / LOCAL-SPECIFIC / RESULT-INFORMED-DESIGN / NON-PRODUCTION / FORWARD-OOS-REQUIRED",
      "race_id":req.get("race_id"),"production_baseline":"KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R3",
      "generated_at":generated_at,"scheduled_post_at":req.get("scheduled_post_at"),
      "temporal_mode":req.get("temporal_mode"),"source_basis_sha256":basis_sha256,
      "design_boundary":"2026-09-23 LOCAL results may inform this candidate; those races are TRAINING/REPLAY ONLY and never OOS.",
      "production_effect":"NONE","arms":arms
    }
    out["sha256"]=_sha(out)
    return out

def settle_shadow(shadow,result_request):
    result={"official_result":{"top3":[int(x) for x in (result_request.get("finish_order") or [])[:3]],
                               "payouts_per_100_yen":{str(k).upper():int(v) for k,v in (result_request.get("payouts") or {}).items()}}}
    arms={}
    for a,x in shadow["arms"].items():
        arms[a]=settle_ticket_list(x["tickets"],result)
    out={"profile":PROFILE,"candidate_id":CANDIDATE_ID,"race_id":shadow.get("race_id"),
         "status":"RETROSPECTIVE-TRAINING-SETTLEMENT / NOT-OOS","production_effect":"NONE","arms":arms}
    out["sha256"]=_sha(out)
    return out


def bind_shadow_to_trace(trace,shadow,basis_sha256):
    out=copy.deepcopy(trace or {})
    out["local_mec_r5_shadow_binding"]={
      "profile":PROFILE,"candidate_id":CANDIDATE_ID,
      "shadow_sha256":shadow.get("sha256"),"basis_sha256":basis_sha256,
      "generated_at":shadow.get("generated_at"),"scheduled_post_at":shadow.get("scheduled_post_at"),
      "temporal_mode":shadow.get("temporal_mode"),"production_effect":"NONE"
    }
    return out

def verify_signed_final_binding(final_envelope,shadow):
    art=final_envelope.get("artifact") or {}
    rec=final_envelope.get("receipt") or {}
    if rec.get("phase")!="FINAL" or rec.get("status")!="PASS":
        raise AssertionError("LOCAL_MEC_R5_FINAL_NOT_PASS")
    b=(art.get("ticket_transport_trace") or {}).get("local_mec_r5_shadow_binding") or {}
    if b.get("shadow_sha256")!=shadow.get("sha256"):
        raise AssertionError("LOCAL_MEC_R5_SHADOW_SHA_NOT_BOUND")
    if b.get("basis_sha256")!=shadow.get("source_basis_sha256"):
        raise AssertionError("LOCAL_MEC_R5_BASIS_SHA_NOT_BOUND")
    if str(b.get("production_effect"))!="NONE":
        raise AssertionError("LOCAL_MEC_R5_PRODUCTION_EFFECT_FORBIDDEN")
    if str(shadow.get("temporal_mode") or "").upper()!="FORMAL-PRE-RACE":
        raise AssertionError("LOCAL_MEC_R5_NOT_FORMAL_PRE_RACE")
    gen=datetime.fromisoformat(str(shadow.get("generated_at")).replace("Z","+00:00"))
    post=datetime.fromisoformat(str(shadow.get("scheduled_post_at")).replace("Z","+00:00"))
    if not gen<post:
        raise AssertionError("LOCAL_MEC_R5_NOT_PRE_RESULT")
    return {
      "valid":True,"profile":PROFILE,"candidate_id":CANDIDATE_ID,
      "shadow_sha256":shadow.get("sha256"),"basis_sha256":shadow.get("source_basis_sha256"),
      "final_receipt_sha256":final_envelope.get("receipt_sha256"),
      "final_artifact_sha256":rec.get("artifact_sha256"),"production_effect":"NONE"
    }
