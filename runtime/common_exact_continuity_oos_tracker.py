from __future__ import annotations
import hashlib, json, os
from collections import defaultdict
from datetime import datetime

from common_exact_continuity_shadow import PROFILE as CANDIDATE_PROFILE, CANDIDATE_ID, ACTIVATION_AT, TARGET, ARM_ORDER

PROFILE="KM-COMMON-EXACT-CONTINUITY-OOS-TRACKER-v1.0-20260930"

def _sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _load(p):
    with open(p,encoding="utf-8") as f:return json.load(f)
def _dt(s):
    return datetime.fromisoformat(str(s).replace("Z","+00:00"))
def _official_result_authority(rid):
    root="runtime/family_result_requests"; refs=[]
    if os.path.isdir(root):
        for fn in sorted(os.listdir(root)):
            if not fn.endswith(".json"): continue
            try:r=_load(os.path.join(root,fn))
            except Exception:continue
            if str(r.get("race_id") or "")!=str(rid):continue
            if r.get("official_result_verified") is True:
                refs.append({"file":fn,"acceptance_only":bool(r.get("acceptance_only")),"source":r.get("source")})
    return {"verified":bool(refs),"oos_admissible":any(not x["acceptance_only"] for x in refs),"refs":refs}
def _agg(rows):
    inv=sum(float(x.get("investment") or 0) for x in rows)
    ret=sum(float(x.get("return") or 0) for x in rows)
    from pfs_grand_review import _robustness
    diagnostic_rows=[{"race_id":f"{i:08d}","investment":float(x.get("investment") or 0),
                      "return":float(x.get("return") or 0),
                      "profit_loss":float(x.get("profit_loss") or 0),
                      "hit_but_loss":0<float(x.get("return") or 0)<float(x.get("investment") or 0)} for i,x in enumerate(rows)]
    return {
      "added_ticket_count":sum(int(x.get("candidate_count",0)) for x in rows),
      "false_addition_count":sum(int(x.get("candidate_count",0))-int(bool(x.get("rescue_hit"))) for x in rows),
      "added_capital":round(inv,2),"robustness":_robustness(diagnostic_rows),
      "eligible_races":len(rows),"investment":round(inv,2),"return":round(ret,2),
      "profit_loss":round(ret-inv,2),"investment_weighted_pfs":round(ret/inv*100,9) if inv else None,
      "rescue_hits":sum(bool(x.get("rescue_hit")) for x in rows),
      "mean_pfs_delta_points":round(sum(float(x.get("pfs_delta_points") or 0) for x in rows)/len(rows),9) if rows else None,
    }
def build_status():
    entries=[];held=[];errors=[];root="runtime/common_exact_continuity_shadow_results"
    if os.path.isdir(root):
        for fn in sorted(os.listdir(root)):
            if not fn.endswith(".json"):continue
            rid=fn[:-5]
            try:
                res=_load(os.path.join(root,fn))
                auth=_official_result_authority(rid)
                if not auth["verified"] or not auth["oos_admissible"]:
                    held.append({"race_id":rid,"reason":"RESULT_AUTHORITY_NOT_OOS_ADMISSIBLE"});continue
                sp=os.path.join("runtime","common_exact_continuity_shadow_artifacts",rid+".json")
                lp=os.path.join("runtime","common_exact_continuity_shadow_lineage",rid+".json")
                if not os.path.exists(sp) or not os.path.exists(lp):
                    errors.append({"race_id":rid,"reason":"SHADOW_OR_LINEAGE_MISSING"});continue
                sh=_load(sp);line=_load(lp)
                if any(obj.get("sha256") != _sha({k:v for k,v in obj.items() if k!="sha256"})
                       for obj in (sh,line,res)):
                    errors.append({"race_id":rid,"reason":"CONTENT_HASH_MISMATCH"});continue
                if any(str(obj.get("race_id") or "")!=rid for obj in (sh,line,res)):
                    errors.append({"race_id":rid,"reason":"RACE_ID_MISMATCH"});continue
                if res.get("shadow_sha256")!=sh.get("sha256"):
                    errors.append({"race_id":rid,"reason":"SETTLEMENT_SHADOW_MISMATCH"});continue

                if sh.get("profile")!=CANDIDATE_PROFILE or sh.get("candidate_id")!=CANDIDATE_ID:continue
                if sh.get("production_effect")!="NONE" or line.get("production_effect")!="NONE":
                    errors.append({"race_id":rid,"reason":"PRODUCTION_EFFECT_NOT_NONE"});continue
                if line.get("lineage_type")!="COMMON_EXACT_CONTINUITY_SIGNED_FINAL_BOUND" or line.get("binding_valid") is not True:
                    errors.append({"race_id":rid,"reason":"SIGNED_FINAL_BINDING_INVALID"});continue
                if line.get("shadow_sha256")!=sh.get("sha256") or line.get("basis_sha256")!=sh.get("source_basis_sha256"):
                    errors.append({"race_id":rid,"reason":"HASH_LINEAGE_MISMATCH"});continue
                if _dt(sh["generated_at"])<_dt(ACTIVATION_AT):continue
                if str(sh.get("temporal_mode") or "").upper()!="FORMAL-PRE-RACE":continue
                if _dt(sh["generated_at"])>=_dt(sh["scheduled_post_at"]):continue
                if res.get("oos_eligible") is not True or res.get("status")!="FORWARD-OOS-SETTLEMENT / SIGNED-FINAL-BOUND":
                    held.append({"race_id":rid,"reason":"SETTLEMENT_NOT_FORWARD_OOS"});continue
                if sorted((res.get("arms") or {}).keys())!=sorted(ARM_ORDER):
                    errors.append({"race_id":rid,"reason":"ARM_SET_MISMATCH"});continue
                entries.append({"race_id":rid,"generated_at":sh.get("generated_at"),"shadow_sha256":sh.get("sha256"),
                                "final_receipt_sha256":line.get("final_receipt_sha256"),"arms":res["arms"],
                                "official_exact_in_candidate_set":res.get("official_exact_in_candidate_set")})
            except Exception as e:
                errors.append({"race_id":rid,"reason":"TRACKER_EXCEPTION","error":type(e).__name__+":"+str(e)})
    entries.sort(key=lambda x:(x["generated_at"],x["race_id"]));entries=entries[:TARGET]
    rows=defaultdict(list)
    for e in entries:
        for a,x in e["arms"].items():rows[a].append(x)
    out={
      "profile":PROFILE,"candidate_profile":CANDIDATE_PROFILE,"candidate_id":CANDIDATE_ID,
      "status":"COMPLETE_30_HUMAN_REVIEW_REQUIRED" if len(entries)>=TARGET else "WAITING_30",
      "activation_at":ACTIVATION_AT,"target_eligible_races":TARGET,"eligible_races":len(entries),
      "remaining_races":max(0,TARGET-len(entries)),"held":held,"errors":errors,
      "production_effect":"NONE","automatic_promotion":False,"human_review_required":True,
      "entries":entries,"aggregates":{a:_agg(rows[a]) for a in ARM_ORDER},
    }
    out["sha256"]=_sha(out);return out
def write_status(path="runtime/common_exact_continuity_oos_status.json"):
    out=build_status()
    with open(path,"w",encoding="utf-8") as f:json.dump(out,f,ensure_ascii=False,sort_keys=True,indent=2)
    return out
if __name__=="__main__":
    x=write_status();print(json.dumps({"status":x["status"],"eligible_races":x["eligible_races"],"remaining_races":x["remaining_races"],"sha256":x["sha256"]},ensure_ascii=False,separators=(",",":")))
