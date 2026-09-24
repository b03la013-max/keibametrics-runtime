from __future__ import annotations
import json, os, hashlib
from collections import defaultdict
from datetime import datetime, timezone
from mec_r4_shadow import settle_ticket_list

PROFILE="KM-FAMILY-MEC-R4-FORWARD-OOS-TRACKER-v1.0-20260922"
CANDIDATE_PROFILE="KM-FAMILY-MEC-R4-SHADOW-CANDIDATE-20260922-R1"
CANDIDATE_ID="MEC-R4-CPSS-SHADOW-v0.1"
ACTIVATION_AT="2026-09-22T21:08:00+09:00"
TARGET=30
EXPECTED_ARMS=[
    "CORE_ONLY","CORE_PROTECTION","CPSS_ALL",
    "CPSS_TOP3","CPSS_TOP4","CPSS_TOP5","CPSS_TOP6","CPSS_TOP7","CPSS_TOP8"
]
ALL_ARMS=["PRODUCTION_BASELINE_R3"]+EXPECTED_ARMS

def _sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def _dt(s):
    return datetime.fromisoformat(str(s).replace("Z","+00:00"))

def _load(path):
    with open(path,encoding="utf-8") as f: return json.load(f)

def _max_drawdown(rows):
    equity=0.0
    peak=0.0
    max_dd=0.0
    for r in rows:
        equity += float(r.get("profit_loss") or 0)
        peak=max(peak,equity)
        max_dd=max(max_dd,peak-equity)
    return round(max_dd,2)

def _aggregate_bet_type(rows):
    out={}
    for bt in ("EXACTA","TRIO","TRIFECTA"):
        inv=ret=0.0
        n=0
        hits=0
        for x in rows:
            b=(x.get("by_bet_type") or {}).get(bt) or {}
            if b.get("investment") is None or b.get("return") is None:
                continue
            n+=1
            inv+=float(b.get("investment") or 0)
            ret+=float(b.get("return") or 0)
            hits+=bool(b.get("hit"))
        out[bt]={
            "race_observation_count":n,
            "investment":round(inv,2),
            "return":round(ret,2),
            "profit_loss":round(ret-inv,2),
            "pfs":round(ret/inv*100.0,9) if inv else None,
            "hit_races":hits,
        }
    return out

def _aggregate_arm(rows):
    inv=sum(float(x.get("investment") or 0) for x in rows)
    ret=sum(float(x.get("return") or 0) for x in rows)
    hits=sum(float(x.get("return") or 0)>0 for x in rows)
    hbl=sum((float(x.get("return") or 0)>0 and float(x.get("return") or 0)<float(x.get("investment") or 0)) for x in rows)
    ordered=sorted(rows,key=lambda x:float(x.get("return") or 0),reverse=True)
    largest=float(ordered[0].get("return") or 0) if ordered else 0.0
    total_return=ret
    ex=ordered[1:] if len(ordered)>1 else []
    ex_inv=sum(float(x.get("investment") or 0) for x in ex)
    ex_ret=sum(float(x.get("return") or 0) for x in ex)
    return {
        "eligible_races":len(rows),
        "investment":round(inv,2),
        "return":round(ret,2),
        "profit_loss":round(ret-inv,2),
        "investment_weighted_pfs":round(ret/inv*100.0,9) if inv else None,
        "hit_races":hits,
        "hit_race_rate":round(hits/len(rows)*100.0,6) if rows else None,
        "hit_but_loss_count":hbl,
        "hit_but_loss_rate":round(hbl/len(rows)*100.0,6) if rows else None,
        "ticket_count_total":sum(int(x.get("ticket_count") or 0) for x in rows),
        "max_drawdown":_max_drawdown(rows),
        "core_structure_retention_min":min((float(v) for v in (x.get("core_structure_retention_ratio") for x in rows) if v is not None),default=None),
        "semantic_information_retention_min":min((float(v) for v in (x.get("semantic_information_retention_ratio") for x in rows) if v is not None),default=None),
        "generic_tail_capital_avoided_total":round(sum(float(x.get("generic_tail_capital_avoided") or 0) for x in rows),2),
        "largest_return":round(largest,2) if ordered else None,
        "largest_return_share_pct":round(largest/total_return*100.0,6) if total_return else None,
        "excluding_largest_return_pfs":round(ex_ret/ex_inv*100.0,9) if ex_inv else None,
        "bet_type":_aggregate_bet_type(rows),
    }

def build_status():
    activation=_dt(ACTIVATION_AT)
    entries=[]
    errors=[]
    root="runtime/mec_shadow_results"
    if os.path.isdir(root):
        for fn in sorted(os.listdir(root)):
            if not fn.endswith(".json"): continue
            path=os.path.join(root,fn)
            try:
                result=_load(path)
                rid=str(result.get("race_id") or "")
                shadow_path=os.path.join("runtime","mec_shadow_artifacts",rid+".json")
                if not os.path.exists(shadow_path):
                    errors.append({"race_id":rid,"reason":"SHADOW_ARTIFACT_MISSING"})
                    continue
                shadow=_load(shadow_path)
                if shadow.get("profile")!=CANDIDATE_PROFILE or shadow.get("candidate_id")!=CANDIDATE_ID:
                    continue
                if shadow.get("production_effect")!="NONE":
                    errors.append({"race_id":rid,"reason":"PRODUCTION_EFFECT_NOT_NONE"})
                    continue

                # JRA lineage uses a Git-versioned immutable FINAL artifact.
                # LOCAL lineage uses a pre-result Shadow digest cryptographically
                # bound into the signed external FINAL and imported after result.
                lineage_path=os.path.join("runtime","mec_shadow_lineage",rid+".json")
                final_path=os.path.join("runtime","final_artifacts",rid+".json")
                local_lineage=os.path.exists(lineage_path)
                if local_lineage:
                    lineage=_load(lineage_path)
                    if lineage.get("lineage_type")!="LOCAL_SIGNED_FINAL_BOUND":
                        errors.append({"race_id":rid,"reason":"LOCAL_LINEAGE_TYPE_INVALID"})
                        continue
                    if lineage.get("binding_valid") is not True:
                        errors.append({"race_id":rid,"reason":"LOCAL_SIGNED_FINAL_BINDING_INVALID"})
                        continue
                    if lineage.get("shadow_sha256")!=shadow.get("sha256"):
                        errors.append({"race_id":rid,"reason":"LOCAL_SHADOW_SHA_MISMATCH"})
                        continue
                    if lineage.get("basis_sha256")!=shadow.get("source_immutable_final_sha256"):
                        errors.append({"race_id":rid,"reason":"LOCAL_BASIS_SHA_MISMATCH"})
                        continue
                    if not lineage.get("final_receipt_sha256") or not lineage.get("final_artifact_sha256"):
                        errors.append({"race_id":rid,"reason":"LOCAL_SIGNED_FINAL_REFERENCE_MISSING"})
                        continue
                    source_final_sha=lineage.get("final_artifact_sha256")
                    p_tickets=lineage.get("production_tickets") or []
                    production_result=lineage.get("production_result") or {}
                    production_settlement=lineage.get("production_settlement") or {}
                    result_path=lineage_path
                else:
                    if not os.path.exists(final_path):
                        errors.append({"race_id":rid,"reason":"LINEAGE_ARTIFACT_MISSING"})
                        continue
                    final=_load(final_path)
                    if shadow.get("source_immutable_final_sha256")!=final.get("sha256"):
                        errors.append({"race_id":rid,"reason":"FINAL_LINEAGE_MISMATCH"})
                        continue
                    source_final_sha=final.get("sha256")
                    result_path=os.path.join("runtime","results",rid+".json")
                    if not os.path.exists(result_path):
                        errors.append({"race_id":rid,"reason":"PRODUCTION_RESULT_MISSING"})
                        continue
                    production_result=_load(result_path)
                    production_settlement=production_result.get("settlement") or {}
                    p_tickets=(final.get("final_ticket") or {}).get("tickets") or []
                gen=_dt(shadow.get("generated_at"))
                if gen < activation:
                    continue
                if str(shadow.get("temporal_mode") or "").upper()!="FORMAL-PRE-RACE":
                    continue
                post=shadow.get("scheduled_post_at")
                if not post or gen>=_dt(post):
                    continue
                arms=result.get("arms") or {}
                if sorted(arms)!=sorted(EXPECTED_ARMS):
                    errors.append({"race_id":rid,"reason":"ARM_SET_MISMATCH","arms":sorted(arms)})
                    continue
                if any(str((arms[a] or {}).get("status"))!="SETTLED" for a in EXPECTED_ARMS):
                    continue

                if str(production_settlement.get("status") or "").upper()!="SETTLED":
                    continue
                p_inv=float(production_settlement.get("total_investment") or production_settlement.get("investment") or 0)
                p_ret=float(production_settlement.get("total_payout") or production_settlement.get("return") or 0)
                p_detail=settle_ticket_list(p_tickets,production_result)
                if p_detail.get("status")!="SETTLED":
                    errors.append({"race_id":rid,"reason":"PRODUCTION_TICKET_SETTLEMENT_INCOMPLETE","detail":p_detail.get("unresolved_payout_types")})
                    continue
                if abs(float(p_detail.get("investment") or 0)-p_inv)>0.001 or abs(float(p_detail.get("return") or 0)-p_ret)>0.001:
                    errors.append({
                        "race_id":rid,
                        "reason":"PRODUCTION_SETTLEMENT_REPLAY_MISMATCH",
                        "official":{"investment":p_inv,"return":p_ret},
                        "replayed":{"investment":p_detail.get("investment"),"return":p_detail.get("return")}
                    })
                    continue
                production_arm={
                    "investment":p_inv,
                    "return":p_ret,
                    "profit_loss":p_ret-p_inv,
                    "pfs":(p_ret/p_inv*100.0) if p_inv else None,
                    "ticket_count":len(p_tickets),
                    "hit":p_ret>0,
                    "by_bet_type":p_detail.get("by_bet_type") or {},
                    "core_structure_retention_ratio":1.0,
                    "semantic_information_retention_ratio":1.0,
                    "generic_tail_capital_avoided":0,
                }

                entry_arms={"PRODUCTION_BASELINE_R3":production_arm}
                for a in EXPECTED_ARMS:
                    frozen_arm=(shadow.get("arms") or {}).get(a) or {}
                    entry_arms[a]={
                        "investment":arms[a].get("investment"),
                        "return":arms[a].get("return"),
                        "profit_loss":arms[a].get("profit_loss"),
                        "pfs":arms[a].get("pfs"),
                        "ticket_count":arms[a].get("ticket_count"),
                        "hit":float(arms[a].get("return") or 0)>0,
                        "by_bet_type":arms[a].get("by_bet_type") or {},
                        "core_structure_retention_ratio":frozen_arm.get("core_structure_retention_ratio"),
                        "semantic_information_retention_ratio":frozen_arm.get("semantic_information_retention_ratio"),
                        "generic_tail_capital_avoided":frozen_arm.get("generic_tail_capital_avoided"),
                    }
                entries.append({
                    "race_id":rid,
                    "generated_at":shadow.get("generated_at"),
                    "source_shadow_sha256":shadow.get("sha256"),
                    "source_final_sha256":source_final_sha,
                    "settlement_sha256":result.get("sha256"),
                    "production_result_path":result_path,
                    "lineage_type":("LOCAL_SIGNED_FINAL_BOUND" if local_lineage else "GIT_IMMUTABLE_FINAL"),
                    "arms":entry_arms,
                })
            except Exception as exc:
                errors.append({"race_id":locals().get("rid"),"reason":"TRACKER_EXCEPTION","error":type(exc).__name__+":"+str(exc)})
                continue
    entries.sort(key=lambda x:(x["generated_at"],x["race_id"]))
    if len(entries)>TARGET:
        entries=entries[:TARGET]
    arm_rows=defaultdict(list)
    for e in entries:
        for a,x in e["arms"].items():
            arm_rows[a].append(x)
    aggregates={a:_aggregate_arm(arm_rows[a]) for a in ALL_ARMS}
    baseline=aggregates["PRODUCTION_BASELINE_R3"]
    comparison={}
    for a in EXPECTED_ARMS:
        x=aggregates[a]
        b_inv=float(baseline.get("investment") or 0)
        x_inv=float(x.get("investment") or 0)
        b_pfs=baseline.get("investment_weighted_pfs")
        x_pfs=x.get("investment_weighted_pfs")
        comparison[a]={
            "investment_delta":round(x_inv-b_inv,2),
            "investment_reduction_pct":round((b_inv-x_inv)/b_inv*100.0,6) if b_inv else None,
            "return_delta":round(float(x.get("return") or 0)-float(baseline.get("return") or 0),2),
            "profit_loss_delta":round(float(x.get("profit_loss") or 0)-float(baseline.get("profit_loss") or 0),2),
            "pfs_points":round(float(x_pfs)-float(b_pfs),9) if x_pfs is not None and b_pfs is not None else None,
            "hit_race_delta":int(x.get("hit_races") or 0)-int(baseline.get("hit_races") or 0),
            "max_drawdown_delta":round(float(x.get("max_drawdown") or 0)-float(baseline.get("max_drawdown") or 0),2),
        }
    status="COMPLETE_30_HUMAN_REVIEW_REQUIRED" if len(entries)>=TARGET else "WAITING_30"
    out={
        "profile":PROFILE,
        "candidate_profile":CANDIDATE_PROFILE,
        "candidate_id":CANDIDATE_ID,
        "status":status,
        "activation_at":ACTIVATION_AT,
        "target_eligible_races":TARGET,
        "eligible_races":len(entries),
        "remaining_races":max(0,TARGET-len(entries)),
        "production_baseline":"KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R3",
        "production_effect":"NONE",
        "automatic_promotion":False,
        "human_review_required":True,
        "rule_change_during_window":"FORBIDDEN except correctness repair",
        "entries":entries,
        "aggregates":aggregates,
        "comparison_vs_production":comparison,
        "errors":errors,
    }
    out["sha256"]=_sha(out)
    return out

def write_status(path="runtime/mec_r4_oos_status.json"):
    out=build_status()
    with open(path,"w",encoding="utf-8") as f:
        json.dump(out,f,ensure_ascii=False,sort_keys=True,indent=2)
    return out

if __name__=="__main__":
    out=write_status()
    print(json.dumps({"status":out["status"],"eligible_races":out["eligible_races"],"remaining_races":out["remaining_races"],"sha256":out["sha256"]},ensure_ascii=False,separators=(",",":")))
