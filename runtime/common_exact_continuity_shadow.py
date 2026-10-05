from __future__ import annotations
import copy, hashlib, json
from datetime import datetime
from typing import Any, Dict

from formal_oos_policy import request_oos_policy

PROFILE="KM-COMMON-EXACT-CONTINUITY-FORWARD-SHADOW-20260930-R1"
CANDIDATE_ID="COMMON-EXACT-CONTINUITY-SHADOW-v0.1"
ACTIVATION_AT="2026-10-01T00:00:00+09:00"
TARGET=30
ARM_ORDER=["CONTINUITY_ALL","KRS_TOP1","KRS_TOP3","KRS_TOP5"]
HARD_MARKERS=("STRUCTURAL","NOT_APPLICABLE","IMPOSSIBLE","SCRATCH","WITHDRAWN",
              "ROLE_INELIGIBLE","UNIVERSE_MISMATCH","FORMAL_OUT_OF_SCOPE")

def _canon(x:Any)->str:
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def _sha(x:Any)->str:
    return hashlib.sha256(_canon(x).encode("utf-8")).hexdigest()

def _dt(x:Any)->datetime:
    return datetime.fromisoformat(str(x).replace("Z","+00:00"))

def _roles(req:Dict[str,Any], final_package:Dict[str,Any])->Dict[str,Any]:
    return (final_package or {}).get("roles") or (req.get("static_prediction") or {}).get("roles") or {}

def _active_p3(req:Dict[str,Any], final_package:Dict[str,Any])->set[int]:
    out=set()
    for k,vals in _roles(req,final_package).items():
        if any(str(v).upper().startswith("P3") for v in (vals or [])):
            out.add(int(k))
    return out


def _role_status_map(req:Dict[str,Any])->dict[int,dict[str,str]]:
    out={}
    for row in req.get("role_registry") or []:
        try:
            runner=int(row["runner_id"])
        except Exception:
            continue
        col=str(row.get("column") or "").upper()
        status=str(row.get("status") or "").upper()
        if col:
            out.setdefault(runner,{})[col]=status
    return out

def _hard_reason(reason:Any)->bool:
    text=str(reason or "").upper()
    return any(marker in text for marker in HARD_MARKERS)

def _hard_pair_exclusions(req:Dict[str,Any])->set[tuple[int,int]]:
    out=set()
    for row in req.get("pair_dispositions") or []:
        if str(row.get("status") or "").upper()!="EXCLUDE" or not _hard_reason(row.get("reason")):
            continue
        try:
            out.add((int(row["head"]),int(row["second"])))
        except Exception:
            continue
    return out

def _conversion_diagnostics(req:Dict[str,Any], final_package:Dict[str,Any],
                            candidates:list[Dict[str,Any]])->Dict[str,Any]:
    roles=_roles(req,final_package)
    status_map=_role_status_map(req)
    material={(h,s) for h,s,_ in _material_pairs(req)}
    hard_pairs=_hard_pair_exclusions(req)

    winner_migration=[]
    for runner,vals in roles.items():
        rid=int(runner)
        role_set={str(v).upper() for v in (vals or [])}
        if any(v.startswith("W") for v in role_set):
            continue
        lower={k:v for k,v in status_map.get(rid,{}).items()
               if k in {"P2","P3"} and v in {"CORE","PROTECTED"}}
        if lower:
            winner_migration.append({
                "runner_id":rid,
                "lower_role_status":lower,
                "diagnostic":"LOWER_ROLE_RETAINED_W_ABSENT",
                "automatic_w_promotion":False,
                "purchase_authority":False,
            })

    active_w=sorted(int(r) for r,vals in roles.items()
                    if any(str(v).upper().startswith("W") for v in (vals or [])))
    protected_p2=sorted(r for r,cols in status_map.items()
                        if cols.get("P2") in {"CORE","PROTECTED"})
    pair_residual=[]
    for h in active_w:
        for s in protected_p2:
            if h==s or (h,s) in material or (h,s) in hard_pairs:
                continue
            pair_residual.append({
                "head":h,"second":s,
                "p2_status":status_map.get(s,{}).get("P2"),
                "diagnostic":"ACTIVE_W_X_CORE_OR_PROTECTED_P2_NO_MATERIAL_PAIR",
                "terminal":"PAIR-RESIDUAL",
                "automatic_purchase":False,
                "purchase_authority":False,
            })

    selective=[]
    for row in candidates:
        if row.get("selective_exact_candidate"):
            selective.append({
                "exact":list(row["exact"]),
                "pair_status":row.get("pair_status"),
                "p3_role_status":row.get("p3_role_status"),
                "independent_protection_reasons":list(row.get("independent_protection_reasons") or []),
                "diagnostic":"MATERIAL_PAIR_X_INDEPENDENTLY_PROTECTED_P3",
                "automatic_purchase":False,
                "purchase_authority":False,
            })
    return {
        "status":"SHADOW-DIAGNOSTIC-ONLY / NOT-OOS-ARM / NO-AUTO-PROMOTION",
        "production_effect":"NONE",
        "arm_definition_changed":False,
        "winner_role_migration_candidates":winner_migration,
        "pair_residual_candidates":pair_residual,
        "selective_exact_candidates":selective,
    }

def _material_pairs(req:Dict[str,Any])->list[tuple[int,int,str]]:
    out=[]
    for x in req.get("pair_dispositions") or []:
        st=str(x.get("status") or "").upper()
        if st in {"PURCHASE","PROTECT","MATERIAL"}:
            out.append((int(x["head"]),int(x["second"]),st))
    return out

def _third_map(req:Dict[str,Any])->dict[tuple[int,int,int],Dict[str,Any]]:
    out={}
    for x in req.get("third_dispositions") or []:
        try:
            out[(int(x["head"]),int(x["second"]),int(x["third"]))]=copy.deepcopy(x)
        except Exception:
            continue
    return out

def _hard_excluded(row:Dict[str,Any]|None)->bool:
    if not row or str(row.get("status") or "").upper()!="EXCLUDE":
        return False
    reason=str(row.get("reason") or "").upper()
    return any(m in reason for m in HARD_MARKERS)

def _ticket_key(t:Dict[str,Any])->tuple[str,tuple[int,...]]:
    bt=str(t.get("bet_type") or "").upper()
    sel=tuple(int(x) for x in (t.get("selection") or []))
    if bt=="TRIO": sel=tuple(sorted(sel))
    return bt,sel

def _production_exact_set(final_ticket:Dict[str,Any])->set[tuple[int,int,int]]:
    out=set()
    for t in (final_ticket or {}).get("tickets") or []:
        if str(t.get("bet_type") or "").upper()=="TRIFECTA":
            sel=tuple(int(x) for x in (t.get("selection") or []))
            if len(sel)==3: out.add(sel)
    return out

def _krs_rank_map(krs_utility:Dict[str,Any]|None)->dict[tuple[int,int,int],Dict[str,Any]]:
    out={}
    ku=krs_utility or {}
    for i,row in enumerate(ku.get("top_trifecta_occurrence") or [],start=1):
        try:
            key=(int(row["W"]),int(row["P2"]),int(row["P3"]))
        except Exception:
            continue
        out[key]={
            "rank":i,
            "frequency":row.get("frequency"),
            "count":row.get("count"),
            "source":"top_trifecta_occurrence",
        }
    for row in ku.get("actionable_pair_third_proposals") or []:
        try:
            key=(int(row["head"]),int(row["second"]),int(row["third"]))
        except Exception:
            continue
        z=out.setdefault(key,{})
        z["actionable"]=bool(row.get("actionable"))
        z["overall_rank"]=row.get("overall_rank")
        z["best_frequency"]=row.get("best_frequency")
        z["pair_source"]=row.get("pair_source")
    return out

def _capital_diagnostics(final_ticket:Dict[str,Any], final_package:Dict[str,Any])->Dict[str,Any]:
    rows=(final_ticket or {}).get("tickets") or []
    tiers={}
    for t in rows:
        tier=str(t.get("mec_tier") or t.get("tier") or "UNSPECIFIED").upper()
        z=tiers.setdefault(tier,{"ticket_count":0,"stake":0})
        z["ticket_count"]+=1
        z["stake"]+=int(t.get("stake") or 0)
    total=sum(int(t.get("stake") or 0) for t in rows)
    roles=(final_package or {}).get("roles") or {}
    return {
        "status":"DIAGNOSTIC-FREEZE-ONLY / NOT-OOS-ARM",
        "total_ticket_count":len(rows),
        "total_investment":total,
        "tier_breakdown":tiers,
        "active_w_count":sum(any(str(v).upper().startswith("W") for v in (vals or [])) for vals in roles.values()),
        "active_p2_count":sum(any(str(v).upper().startswith("P2") for v in (vals or [])) for vals in roles.values()),
        "active_p3_count":sum(any(str(v).upper().startswith("P3") for v in (vals or [])) for vals in roles.values()),
        "automatic_capital_change":False,
        "oos_arm":False,
        "production_effect":"NONE",
    }

def build_shadow(req:Dict[str,Any], final_ticket:Dict[str,Any], final_package:Dict[str,Any],
                 krs_utility:Dict[str,Any]|None, generated_at:str,
                 basis_sha256:str)->Dict[str,Any]:
    rid=str(req.get("race_id") or "")
    if not rid: raise AssertionError("COMMON_EXACT_RACE_ID_MISSING")
    scheduled=req.get("scheduled_post_at")
    temporal_mode=str(req.get("temporal_mode") or "").upper()
    p3=_active_p3(req,final_package)
    tm=_third_map(req)
    prod_exact=_production_exact_set(final_ticket)
    kr=_krs_rank_map(krs_utility)
    candidates=[]
    for h,s,pstat in _material_pairs(req):
        for t in sorted(p3):
            if t in {h,s}: continue
            key=(h,s,t)
            explicit=tm.get(key)
            if _hard_excluded(explicit): continue
            if key in prod_exact: continue
            k=kr.get(key) or {}
            p3_status=_role_status_map(req).get(t,{}).get("P3")
            protection=[]
            if p3_status in {"CORE","PROTECTED"}:
                protection.append("STATIC_P3_"+p3_status)
            explicit_status=str((explicit or {}).get("status") or "").upper()
            if explicit_status in {"PURCHASE","PROTECT","MATERIAL"}:
                protection.append("PAIR_LOCAL_THIRD_"+explicit_status)
            if bool(k.get("actionable")):
                protection.append("KRS_ACTIONABLE_REAUDIT")
            if isinstance(k.get("rank"),int) and k["rank"]<=3:
                protection.append("KRS_TOP3_REAUDIT")
            candidates.append({
                "exact":[h,s,t],
                "pair_status":pstat,
                "third_status":(explicit or {}).get("status") or "AUTO_SEMANTIC_ONLY",
                "third_reason":(explicit or {}).get("reason") or "MATERIAL_PAIR_X_ACTIVE_P3_NOT_EXPLICITLY_MATERIALIZED",
                "p3_role_status":p3_status,
                "independent_protection_reasons":protection,
                "selective_exact_candidate":bool(protection),
                "krs_rank":k.get("rank"),
                "krs_frequency":k.get("frequency"),
                "krs_count":k.get("count"),
                "krs_actionable":bool(k.get("actionable")),
                "krs_overall_rank":k.get("overall_rank"),
                "krs_best_frequency":k.get("best_frequency"),
                "krs_pair_source":k.get("pair_source"),
            })
    candidates.sort(key=lambda x:tuple(x["exact"]))
    def arm_ids(limit=None):
        if limit is None:
            rows=candidates
        else:
            rows=[x for x in candidates if isinstance(x.get("krs_rank"),int) and x["krs_rank"]<=limit]
        return [">".join(str(v) for v in x["exact"]) for x in rows]
    arms={
        "CONTINUITY_ALL":arm_ids(None),
        "KRS_TOP1":arm_ids(1),
        "KRS_TOP3":arm_ids(3),
        "KRS_TOP5":arm_ids(5),
    }
    policy=request_oos_policy(req)
    pre_result=bool(temporal_mode=="FORMAL-PRE-RACE" and scheduled and _dt(generated_at)<_dt(scheduled))
    after_activation=bool(_dt(generated_at)>=_dt(ACTIVATION_AT))
    forward=bool(pre_result and after_activation and policy["oos_allowed"])
    out={
        "profile":PROFILE,"candidate_id":CANDIDATE_ID,
        "status":"PREREGISTERED / SHADOW / NON-PRODUCTION / PRE-RESULT-FROZEN / NO-AUTO-PROMOTION",
        "race_id":rid,
        "generated_at":generated_at,
        "scheduled_post_at":scheduled,
        "temporal_mode":req.get("temporal_mode"),
        "activation_at":ACTIVATION_AT,
        "source_basis_sha256":basis_sha256,
        "production_effect":"NONE",
        "automatic_purchase":False,
        "shadow_measurement_unit_stake":100,
        "candidate_count":len(candidates),
        "candidates":candidates,
        "arms":arms,
        "krs_non_probability_notice":"KRS occurrence rank/frequency is uncalibrated support only; no probability, EV or Production authority.",
        "acceptance_only":bool(policy["acceptance_only"]),
        "request_oos_eligible":bool(policy["request_oos_eligible"]),
        "forward_oos_candidate":forward,
        "oos_exclusion_reason":(
            policy.get("oos_exclusion_reason") if not policy["oos_allowed"] else
            (None if after_activation else "BEFORE_CANDIDATE_ACTIVATION")
        ),
        "capital_width_diagnostics":_capital_diagnostics(final_ticket,final_package),
        "conversion_diagnostics":_conversion_diagnostics(req,final_package,candidates),
    }
    out["sha256"]=_sha({k:v for k,v in out.items() if k!="sha256"})
    return out

def bind_shadow_to_trace(trace:Dict[str,Any], shadow:Dict[str,Any])->Dict[str,Any]:
    out=copy.deepcopy(trace or {})
    out["common_exact_continuity_shadow_binding"]={
        "profile":PROFILE,"candidate_id":CANDIDATE_ID,
        "shadow_sha256":shadow.get("sha256"),
        "basis_sha256":shadow.get("source_basis_sha256"),
        "generated_at":shadow.get("generated_at"),
        "scheduled_post_at":shadow.get("scheduled_post_at"),
        "temporal_mode":shadow.get("temporal_mode"),
        "forward_oos_candidate":bool(shadow.get("forward_oos_candidate")),
        "acceptance_only":bool(shadow.get("acceptance_only")),
        "production_effect":"NONE",
    }
    return out

def verify_signed_final_binding(final_envelope:Dict[str,Any], shadow:Dict[str,Any])->Dict[str,Any]:
    if shadow.get("sha256") != _sha({k:v for k,v in shadow.items() if k!="sha256"}):
        raise AssertionError("COMMON_EXACT_SHADOW_CONTENT_HASH_MISMATCH")
    rec=final_envelope.get("receipt") or {}
    art=final_envelope.get("artifact") or {}
    if rec.get("phase")!="FINAL" or rec.get("status")!="PASS":
        raise AssertionError("COMMON_EXACT_FINAL_NOT_PASS")
    b=(art.get("ticket_transport_trace") or {}).get("common_exact_continuity_shadow_binding") or {}
    if b.get("shadow_sha256")!=shadow.get("sha256"):
        raise AssertionError("COMMON_EXACT_SHADOW_SHA_NOT_BOUND")
    if b.get("basis_sha256")!=shadow.get("source_basis_sha256"):
        raise AssertionError("COMMON_EXACT_BASIS_SHA_NOT_BOUND")
    if str(b.get("production_effect"))!="NONE":
        raise AssertionError("COMMON_EXACT_PRODUCTION_EFFECT_FORBIDDEN")
    if str(shadow.get("temporal_mode") or "").upper()!="FORMAL-PRE-RACE":
        raise AssertionError("COMMON_EXACT_NOT_FORMAL_PRE_RACE")
    if not shadow.get("generated_at") or not shadow.get("scheduled_post_at") or _dt(shadow["generated_at"])>=_dt(shadow["scheduled_post_at"]):
        raise AssertionError("COMMON_EXACT_NOT_PRE_RESULT")
    return {
        "valid":True,"profile":PROFILE,"candidate_id":CANDIDATE_ID,
        "shadow_sha256":shadow.get("sha256"),
        "basis_sha256":shadow.get("source_basis_sha256"),
        "final_receipt_sha256":final_envelope.get("receipt_sha256"),
        "final_artifact_sha256":rec.get("artifact_sha256"),
        "forward_oos_candidate":bool(shadow.get("forward_oos_candidate")),
        "production_effect":"NONE",
    }

def settle_shadow(shadow:Dict[str,Any], finish_order:list[int], payouts:Dict[str,Any],
                  production_investment:int, production_return:int,
                  signed_final_binding_valid:bool)->Dict[str,Any]:
    if shadow.get("sha256") != _sha({k:v for k,v in shadow.items() if k!="sha256"}):
        raise AssertionError("COMMON_EXACT_SHADOW_CONTENT_HASH_MISMATCH")
    if len(finish_order)<3 or len(set(finish_order[:3]))!=3:
        raise AssertionError("COMMON_EXACT_RESULT_TOP3_INVALID")
    if "TRIFECTA" not in (payouts or {}) or int(payouts["TRIFECTA"])<=0:
        raise AssertionError("COMMON_EXACT_OFFICIAL_PAYOUT_REQUIRED")
    top3=[int(x) for x in finish_order[:3]]
    exact=">".join(str(x) for x in top3)
    payout100=int((payouts or {}).get("TRIFECTA") or 0)
    arms={}
    for name,ids in (shadow.get("arms") or {}).items():
        ids=list(ids or [])
        hit=exact in ids
        inv=len(ids)*int(shadow.get("shadow_measurement_unit_stake") or 100)
        ret=payout100 if hit else 0
        pfs=(ret/inv*100) if inv else None
        plus_inv=int(production_investment)+inv
        plus_ret=int(production_return)+ret
        plus_pfs=(plus_ret/plus_inv*100) if plus_inv else None
        prod_pfs=(int(production_return)/int(production_investment)*100) if int(production_investment) else None
        arms[name]={
            "candidate_count":len(ids),"investment":inv,"return":ret,
            "profit_loss":ret-inv,"pfs":pfs,"rescue_hit":hit,
            "production_plus_arm_investment":plus_inv,
            "production_plus_arm_return":plus_ret,
            "production_plus_arm_pfs":plus_pfs,
            "pfs_delta_points":(plus_pfs-prod_pfs) if plus_pfs is not None and prod_pfs is not None else None,
        }
    eligible=bool(shadow.get("forward_oos_candidate") and signed_final_binding_valid)
    out={
        "profile":PROFILE,"candidate_id":CANDIDATE_ID,"race_id":shadow.get("race_id"),
        "status":("FORWARD-OOS-SETTLEMENT / SIGNED-FINAL-BOUND" if eligible else "NOT-OOS-SETTLEMENT"),
        "oos_eligible":eligible,
        "signed_final_binding_valid":bool(signed_final_binding_valid),
        "shadow_sha256":shadow.get("sha256"),
        "official_exact":top3,
        "official_exact_in_candidate_set":exact in set(shadow.get("arms",{}).get("CONTINUITY_ALL") or []),
        "production_investment":int(production_investment),
        "production_return":int(production_return),
        "production_pfs":(int(production_return)/int(production_investment)*100) if int(production_investment) else None,
        "trifecta_payout_per_100":payout100,
        "arms":arms,
        "production_effect":"NONE",
    }
    out["sha256"]=_sha({k:v for k,v in out.items() if k!="sha256"})
    return out
