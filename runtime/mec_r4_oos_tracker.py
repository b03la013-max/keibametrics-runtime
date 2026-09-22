from __future__ import annotations
import json, os, hashlib
from collections import defaultdict
from datetime import datetime, timezone

PROFILE="KM-FAMILY-MEC-R4-FORWARD-OOS-TRACKER-v1.0-20260922"
CANDIDATE_PROFILE="KM-FAMILY-MEC-R4-SHADOW-CANDIDATE-20260922-R1"
CANDIDATE_ID="MEC-R4-CPSS-SHADOW-v0.1"
ACTIVATION_AT="2026-09-22T21:08:00+09:00"
TARGET=30
EXPECTED_ARMS=[
    "CORE_ONLY","CORE_PROTECTION","CPSS_ALL",
    "CPSS_TOP3","CPSS_TOP4","CPSS_TOP5","CPSS_TOP6","CPSS_TOP7","CPSS_TOP8"
]

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

def _aggregate_arm(rows):
    inv=sum(float(x.get("investment") or 0) for x in rows)
    ret=sum(float(x.get("return") or 0) for x in rows)
    hits=sum(float(x.get("return") or 0)>0 for x in rows)
    hbl=sum((float(x.get("return") or 0)>0 and float(x.get("return") or 0)<float(x.get("investment") or 0)) for x in rows)
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
                final_path=os.path.join("runtime","final_artifacts",rid+".json")
                if not (os.path.exists(shadow_path) and os.path.exists(final_path)):
                    errors.append({"race_id":rid,"reason":"LINEAGE_ARTIFACT_MISSING"})
                    continue
                shadow=_load(shadow_path); final=_load(final_path)
                if shadow.get("profile")!=CANDIDATE_PROFILE or shadow.get("candidate_id")!=CANDIDATE_ID:
                    continue
                if shadow.get("production_effect")!="NONE":
                    errors.append({"race_id":rid,"reason":"PRODUCTION_EFFECT_NOT_NONE"})
                    continue
                if shadow.get("source_immutable_final_sha256")!=final.get("sha256"):
                    errors.append({"race_id":rid,"reason":"FINAL_LINEAGE_MISMATCH"})
                    continue
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
                entries.append({
                    "race_id":rid,
                    "generated_at":shadow.get("generated_at"),
                    "source_shadow_sha256":shadow.get("sha256"),
                    "source_final_sha256":final.get("sha256"),
                    "settlement_sha256":result.get("sha256"),
                    "arms":{
                        a:{
                            "investment":arms[a].get("investment"),
                            "return":arms[a].get("return"),
                            "profit_loss":arms[a].get("profit_loss"),
                            "pfs":arms[a].get("pfs"),
                            "ticket_count":arms[a].get("ticket_count"),
                            "hit":float(arms[a].get("return") or 0)>0,
                        } for a in EXPECTED_ARMS
                    }
                })
    entries.sort(key=lambda x:(x["generated_at"],x["race_id"]))
    if len(entries)>TARGET:
        entries=entries[:TARGET]
    arm_rows=defaultdict(list)
    for e in entries:
        for a,x in e["arms"].items():
            arm_rows[a].append(x)
    aggregates={a:_aggregate_arm(arm_rows[a]) for a in EXPECTED_ARMS}
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
