from __future__ import annotations
import hashlib,json,os
from collections import defaultdict
from datetime import datetime

from mec_r4_shadow import settle_ticket_list
from local_mec_r5_shadow import PROFILE as CANDIDATE_PROFILE, CANDIDATE_ID, ARM_ORDER

PROFILE="KM-LOCAL-MEC-R5-FORWARD-OOS-TRACKER-v1.0-20260924"
ACTIVATION_AT="2026-09-24T00:00:00+09:00"
TARGET=30
ALL_ARMS=["PRODUCTION_BASELINE_R3"]+ARM_ORDER

def _sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def _dt(s):
    return datetime.fromisoformat(str(s).replace("Z","+00:00"))

def _load(p):
    with open(p,encoding="utf-8") as f:return json.load(f)

def _max_drawdown(rows):
    eq=peak=dd=0.0
    for x in rows:
        eq+=float(x.get("profit_loss") or 0)
        peak=max(peak,eq)
        dd=max(dd,peak-eq)
    return round(dd,2)

def _aggregate(rows):
    inv=sum(float(x.get("investment") or 0) for x in rows)
    ret=sum(float(x.get("return") or 0) for x in rows)
    hits=sum(float(x.get("return") or 0)>0 for x in rows)
    hbl=sum(0<float(x.get("return") or 0)<float(x.get("investment") or 0) for x in rows)
    return {
      "eligible_races":len(rows),
      "investment":round(inv,2),"return":round(ret,2),"profit_loss":round(ret-inv,2),
      "investment_weighted_pfs":round(ret/inv*100,9) if inv else None,
      "hit_races":hits,"hit_race_rate":round(hits/len(rows)*100,6) if rows else None,
      "hit_but_loss_count":hbl,"hit_but_loss_rate":round(hbl/len(rows)*100,6) if rows else None,
      "ticket_count_total":sum(int(x.get("ticket_count") or 0) for x in rows),
      "max_drawdown":_max_drawdown(rows)
    }

def build_status():
    activation=_dt(ACTIVATION_AT)
    entries=[]; errors=[]
    root="runtime/local_mec_r5_shadow_results"
    if os.path.isdir(root):
        for fn in sorted(os.listdir(root)):
            if not fn.endswith(".json"): continue
            rid=fn[:-5]
            try:
                result=_load(os.path.join(root,fn))
                sp=os.path.join("runtime","local_mec_r5_shadow_artifacts",rid+".json")
                lp=os.path.join("runtime","local_mec_r5_shadow_lineage",rid+".json")
                if not os.path.exists(sp) or not os.path.exists(lp):
                    errors.append({"race_id":rid,"reason":"R5_LINEAGE_MISSING"}); continue
                sh=_load(sp); line=_load(lp)
                if sh.get("profile")!=CANDIDATE_PROFILE or sh.get("candidate_id")!=CANDIDATE_ID:
                    continue
                if sh.get("production_effect")!="NONE":
                    errors.append({"race_id":rid,"reason":"R5_PRODUCTION_EFFECT_NOT_NONE"}); continue
                if line.get("lineage_type")!="LOCAL_MEC_R5_SIGNED_FINAL_BOUND" or line.get("binding_valid") is not True:
                    errors.append({"race_id":rid,"reason":"R5_SIGNED_FINAL_BINDING_INVALID"}); continue
                if line.get("shadow_sha256")!=sh.get("sha256") or line.get("basis_sha256")!=sh.get("source_basis_sha256"):
                    errors.append({"race_id":rid,"reason":"R5_SHADOW_LINEAGE_HASH_MISMATCH"}); continue
                gen=_dt(sh.get("generated_at"))
                if gen<activation: continue
                if str(sh.get("temporal_mode") or "").upper()!="FORMAL-PRE-RACE": continue
                if not sh.get("scheduled_post_at") or gen>=_dt(sh["scheduled_post_at"]): continue
                arms=result.get("arms") or {}
                if sorted(arms)!=sorted(ARM_ORDER):
                    errors.append({"race_id":rid,"reason":"R5_ARM_SET_MISMATCH","arms":sorted(arms)}); continue
                if any(str((arms[a] or {}).get("status"))!="SETTLED" for a in ARM_ORDER): continue

                prod_result=line.get("production_result") or {}
                prod_settle=line.get("production_settlement") or {}
                if str(prod_settle.get("status") or "").upper()!="SETTLED": continue
                p_tickets=line.get("production_tickets") or []
                replay=settle_ticket_list(p_tickets,prod_result)
                if replay.get("status")!="SETTLED":
                    errors.append({"race_id":rid,"reason":"R5_PRODUCTION_REPLAY_INCOMPLETE"}); continue
                p_inv=float(prod_settle.get("total_investment") or 0)
                p_ret=float(prod_settle.get("total_payout") or 0)
                if abs(float(replay.get("investment") or 0)-p_inv)>0.001 or abs(float(replay.get("return") or 0)-p_ret)>0.001:
                    errors.append({"race_id":rid,"reason":"R5_PRODUCTION_REPLAY_MISMATCH"}); continue

                rowarms={"PRODUCTION_BASELINE_R3":{
                  "investment":p_inv,"return":p_ret,"profit_loss":p_ret-p_inv,
                  "pfs":p_ret/p_inv*100 if p_inv else None,"ticket_count":len(p_tickets),"hit":p_ret>0
                }}
                for a in ARM_ORDER:
                    x=arms[a]
                    rowarms[a]={
                      "investment":x.get("investment"),"return":x.get("return"),
                      "profit_loss":x.get("profit_loss"),"pfs":x.get("pfs"),
                      "ticket_count":x.get("ticket_count"),"hit":float(x.get("return") or 0)>0
                    }
                entries.append({
                  "race_id":rid,"generated_at":sh.get("generated_at"),
                  "shadow_sha256":sh.get("sha256"),"final_receipt_sha256":line.get("final_receipt_sha256"),
                  "final_artifact_sha256":line.get("final_artifact_sha256"),"arms":rowarms
                })
            except Exception as e:
                errors.append({"race_id":rid,"reason":"R5_TRACKER_EXCEPTION","error":type(e).__name__+":"+str(e)})
    entries.sort(key=lambda x:(x["generated_at"],x["race_id"]))
    entries=entries[:TARGET]
    rows=defaultdict(list)
    for e in entries:
        for a,x in e["arms"].items(): rows[a].append(x)
    agg={a:_aggregate(rows[a]) for a in ALL_ARMS}
    b=agg["PRODUCTION_BASELINE_R3"]
    cmp={}
    for a in ARM_ORDER:
        x=agg[a]
        bp=b.get("investment_weighted_pfs"); xp=x.get("investment_weighted_pfs")
        binv=float(b.get("investment") or 0); xinv=float(x.get("investment") or 0)
        cmp[a]={
          "investment_delta":round(xinv-binv,2),
          "capital_reduction_pct":round((binv-xinv)/binv*100,6) if binv else None,
          "return_delta":round(float(x.get("return") or 0)-float(b.get("return") or 0),2),
          "profit_loss_delta":round(float(x.get("profit_loss") or 0)-float(b.get("profit_loss") or 0),2),
          "pfs_points":round(float(xp)-float(bp),9) if xp is not None and bp is not None else None,
          "hit_race_delta":int(x.get("hit_races") or 0)-int(b.get("hit_races") or 0),
          "max_drawdown_delta":round(float(x.get("max_drawdown") or 0)-float(b.get("max_drawdown") or 0),2)
        }
    out={
      "profile":PROFILE,"candidate_profile":CANDIDATE_PROFILE,"candidate_id":CANDIDATE_ID,
      "status":"COMPLETE_30_HUMAN_REVIEW_REQUIRED" if len(entries)>=TARGET else "WAITING_30",
      "activation_at":ACTIVATION_AT,"target_eligible_races":TARGET,"eligible_races":len(entries),
      "remaining_races":max(0,TARGET-len(entries)),
      "training_exclusion":["URW-20260923-R07-FORMAL-R1","URW-20260923-R10-FORMAL-R1","URW-20260923-R11-FORMAL-R1","URW-20260923-R12-FORMAL-R1"],
      "production_baseline":"KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R3",
      "production_effect":"NONE","automatic_promotion":False,"human_review_required":True,
      "rule_change_during_window":"FORBIDDEN except correctness repair",
      "entries":entries,"aggregates":agg,"comparison_vs_production":cmp,"errors":errors
    }
    out["sha256"]=_sha(out)
    return out

def write_status(path="runtime/local_mec_r5_oos_status.json"):
    out=build_status()
    with open(path,"w",encoding="utf-8") as f:json.dump(out,f,ensure_ascii=False,sort_keys=True,indent=2)
    return out

if __name__=="__main__":
    x=write_status()
    print(json.dumps({"status":x["status"],"eligible_races":x["eligible_races"],"remaining_races":x["remaining_races"],"sha256":x["sha256"]},ensure_ascii=False,separators=(",",":")))
