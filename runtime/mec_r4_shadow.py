import copy, hashlib, json
from datetime import datetime, timezone

PROFILE="KM-FAMILY-MEC-R4-SHADOW-CANDIDATE-20260922-R1"
CANDIDATE_ID="MEC-R4-CPSS-SHADOW-v0.1"
ARM_ORDER=[
    "CORE_ONLY",
    "CORE_PROTECTION",
    "CPSS_ALL",
    "CPSS_TOP3",
    "CPSS_TOP4",
    "CPSS_TOP5",
    "CPSS_TOP6",
    "CPSS_TOP7",
    "CPSS_TOP8",
]
SOFT_MARKERS=("MATERIALITY","SOFT")
HARD_MARKERS=("STRUCTURAL","NOT_APPLICABLE","IMPOSSIBLE","SCRATCH","WITHDRAWN",
              "ROLE_INELIGIBLE","UNIVERSE_MISMATCH","FORMAL_OUT_OF_SCOPE")

def _canon(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def _sha(x):
    return hashlib.sha256(_canon(x).encode("utf-8")).hexdigest()

def _norm(bt,sel):
    a=[int(x) for x in sel]
    return tuple(sorted(a)) if bt=="TRIO" else tuple(a)

def _key(bt,sel):
    return (str(bt).upper(),_norm(str(bt).upper(),sel))

def _add(store,bt,sel,stake=100,source="SHADOW"):
    bt=str(bt).upper()
    k=_key(bt,sel)
    if k not in store:
        store[k]={
            "bet_type":bt,
            "selection":[int(x) for x in sel],
            "stake":int(stake or 100),
            "shadow_source":source,
        }

def _tickets(final_artifact):
    return copy.deepcopy((final_artifact.get("final_ticket") or {}).get("tickets") or [])

def _roles(final_artifact):
    return (final_artifact.get("final_prediction_package") or {}).get("roles") or (final_artifact.get("static_prediction") or {}).get("roles") or {}

def _ranking(final_artifact):
    return [int(x) for x in ((final_artifact.get("final_prediction_package") or {}).get("ranking") or (final_artifact.get("static_prediction") or {}).get("ranking") or [])]

def _thirds(final_artifact):
    return final_artifact.get("third_dispositions") or []

def _tier(t):
    return str(t.get("mec_tier") or t.get("tier") or "").upper()

def _base_store(final_artifact,tiers):
    tickets=_tickets(final_artifact)
    has_tier=any(_tier(t) for t in tickets)
    out={}
    for t in tickets:
        if has_tier and _tier(t) not in tiers:
            continue
        _add(out,t["bet_type"],t["selection"],t.get("stake") or 100,"FROZEN_"+(_tier(t) or "LEGACY"))
    return out,has_tier

def _soft_exclusions(final_artifact):
    active_p3={int(k) for k,v in _roles(final_artifact).items() if "P3" in (v or [])}
    out=[]
    for x in _thirds(final_artifact):
        if str(x.get("status","")).upper()!="EXCLUDE":
            continue
        third=int(x["third"])
        if third not in active_p3:
            continue
        reason=str(x.get("reason") or "").upper()
        if any(m in reason for m in HARD_MARKERS):
            continue
        if not any(m in reason for m in SOFT_MARKERS):
            continue
        out.append(copy.deepcopy(x))
    return out

def _apply_soft_restore(store,final_artifact):
    for x in _soft_exclusions(final_artifact):
        h,s,t=int(x["head"]),int(x["second"]),int(x["third"])
        _add(store,"TRIFECTA",[h,s,t],100,"SOFT_P3_RESTORE")
        _add(store,"TRIO",sorted([h,s,t]),100,"SOFT_P3_RESTORE")

def _apply_structural_closure(store,final_artifact,top_k=None):
    rank={h:i+1 for i,h in enumerate(_ranking(final_artifact))}
    retained=list(store.values())
    for x in retained:
        if x["bet_type"]!="TRIFECTA" or len(x["selection"])!=3:
            continue
        sel=[int(v) for v in x["selection"]]
        if top_k is not None and not all(rank.get(v,10**9)<=int(top_k) for v in sel):
            continue
        _add(store,"EXACTA",sel[:2],100,"STRUCTURAL_CLOSURE")
        _add(store,"TRIO",sorted(sel),100,"STRUCTURAL_CLOSURE")

def _arm(final_artifact,name):
    if name=="CORE_ONLY":
        store,has_tier=_base_store(final_artifact,{"CORE"})
    else:
        store,has_tier=_base_store(final_artifact,{"CORE","PROTECTION"})
    if name.startswith("CPSS"):
        _apply_soft_restore(store,final_artifact)
        top_k=None
        if name.startswith("CPSS_TOP"):
            top_k=int(name.replace("CPSS_TOP",""))
        _apply_structural_closure(store,final_artifact,top_k=top_k)
    tickets=sorted(store.values(),key=lambda x:(x["bet_type"],tuple(x["selection"]),x["stake"]))
    return {
        "arm":name,
        "tier_metadata_available":has_tier,
        "ticket_count":len(tickets),
        "minimum_shadow_capital":sum(int(x["stake"]) for x in tickets),
        "tickets":tickets,
        "sha256":_sha(tickets),
    }

def build_mec_r4_shadow(final_artifact,generated_at=None):
    generated_at=generated_at or datetime.now(timezone.utc).isoformat()
    arms={name:_arm(final_artifact,name) for name in ARM_ORDER}
    out={
        "artifact_type":"KM_MEC_SHADOW_PRE_RESULT",
        "profile":PROFILE,
        "candidate_id":CANDIDATE_ID,
        "status":"SHADOW / NON-PRODUCTION / PRE-RESULT-FROZEN / NO-AUTO-PROMOTION",
        "race_id":final_artifact["race_id"],
        "generated_at":generated_at,
        "source_immutable_final_sha256":final_artifact.get("sha256"),
        "source_final_receipt_sha256":final_artifact.get("final_receipt_sha256"),
        "scheduled_post_at":final_artifact.get("scheduled_post_at"),
        "temporal_mode":final_artifact.get("temporal_mode"),
        "production_mec_profile":((final_artifact.get("minimum_efficient_coverage") or {}).get("profile")),
        "production_effect":"NONE",
        "semantic_universe_policy":"UNCHANGED_INFORMATION_RETENTION",
        "generic_tail_purchase":"OFF_IN_SHADOW_ARMS",
        "hard_structural_exclusion":"PRESERVED",
        "result_derived_selection":"FORBIDDEN",
        "krs_authority_change":"FORBIDDEN",
        "soft_exclusion_restored_count":len(_soft_exclusions(final_artifact)),
        "arms":arms,
    }
    out["sha256"]=_sha(out)
    return out

def _payout(result,bet_type,top3):
    payouts=((result.get("official_result") or {}).get("payouts") or {})
    w,s,t=[int(x) for x in top3]
    bt=str(bet_type).upper()
    if bt=="EXACTA":
        obj=payouts.get("exacta")
        if isinstance(obj,(int,float)): return float(obj)
        if isinstance(obj,dict):
            for k in (f"{w}>{s}",f"{w}-{s}",f"{w},{s}"):
                if k in obj: return float(obj[k])
    elif bt=="TRIO":
        obj=payouts.get("trio")
        if isinstance(obj,(int,float)): return float(obj)
        if isinstance(obj,dict):
            k="-".join(str(x) for x in sorted([w,s,t]))
            if k in obj: return float(obj[k])
    elif bt=="TRIFECTA":
        obj=payouts.get("trifecta")
        if isinstance(obj,(int,float)): return float(obj)
        if isinstance(obj,dict):
            k=f"{w}>{s}>{t}"
            if k in obj: return float(obj[k])
    return None

def settle_mec_r4_shadow(shadow_artifact,result):
    top3=[int(x) for x in ((result.get("official_result") or {}).get("top3") or [])]
    if len(top3)!=3:
        raise AssertionError("SHADOW_RESULT_TOP3_MISSING")
    arms={}
    for name,arm in shadow_artifact["arms"].items():
        inv=sum(int(t["stake"]) for t in arm["tickets"])
        ret=0.0
        hit_types=[]
        unresolved=[]
        targets={
            "EXACTA":top3[:2],
            "TRIO":sorted(top3),
            "TRIFECTA":top3,
        }
        for t in arm["tickets"]:
            bt=t["bet_type"]
            if bt not in targets or _key(bt,t["selection"])!=_key(bt,targets[bt]):
                continue
            pay=_payout(result,bt,top3)
            if pay is None:
                unresolved.append(bt)
                continue
            ret += pay*(int(t["stake"])/100.0)
            hit_types.append(bt)
        status="SETTLED" if not unresolved else "PARTIAL_PAYOUT_MISSING"
        arms[name]={
            "status":status,
            "investment":inv,
            "return":ret if not unresolved else None,
            "profit_loss":(ret-inv) if not unresolved else None,
            "pfs":(ret/inv*100.0) if (inv and not unresolved) else None,
            "hit_types":sorted(set(hit_types)),
            "unresolved_payout_types":sorted(set(unresolved)),
            "ticket_count":arm["ticket_count"],
        }
    out={
        "artifact_type":"KM_MEC_SHADOW_POST_RESULT_SETTLEMENT",
        "profile":PROFILE,
        "candidate_id":CANDIDATE_ID,
        "race_id":shadow_artifact["race_id"],
        "source_shadow_sha256":shadow_artifact["sha256"],
        "source_immutable_final_sha256":shadow_artifact.get("source_immutable_final_sha256"),
        "result_status":(result.get("official_result") or {}).get("status"),
        "official_top3":top3,
        "authority":"SHADOW-PFS / NOT-ACTUAL-PURCHASE",
        "production_effect":"NONE",
        "arms":arms,
    }
    out["sha256"]=_sha(out)
    return out
