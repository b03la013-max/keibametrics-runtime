import json,os,shutil,subprocess,sys,urllib.request,urllib.parse
sys.path.insert(0,"runtime")
from local_candidate_postresult import evaluate_dual
from local_candidate_dual_oos_tracker import build_measurement, write_status
from local_candidate_v03_postresult import evaluate_v03
from local_candidate_v03_oos_tracker import (
    build_measurement as build_v03_measurement,
    write_status as write_v03_status,
)
from local_mec_r4_bridge import verify_signed_final_binding
from mec_r4_shadow import settle_mec_r4_shadow, settle_ticket_list
from mec_r4_oos_tracker import write_status as write_mec_r4_oos_status
from local_mec_r5_shadow import (
    verify_signed_final_binding as verify_local_mec_r5_signed_final_binding,
    settle_shadow as settle_local_mec_r5_shadow,
)
from local_mec_r5_oos_tracker import write_status as write_local_mec_r5_oos_status
from common_exact_continuity_shadow import (
    verify_signed_final_binding as verify_common_exact_continuity_binding,
    settle_shadow as settle_common_exact_continuity_shadow,
)
from common_exact_continuity_oos_tracker import write_status as write_common_exact_continuity_oos_status
from execution_gateway import load_gateway, normalize_request, family_config, artifact_name as gateway_artifact_name, request_json, result_route
from execution_store import materialize_phase, verify_result_reuse
from race_day_fast_reflection import build_fast_reflection

raw_req=json.load(open(sys.argv[1],encoding="utf-8"))
gateway=load_gateway()
req,execution_context=normalize_request(raw_req,gateway)
execution_id=str(execution_context["execution_id"])
acceptance_only=bool(req.get("acceptance_only"))
shutil.rmtree("runtime_result_in",ignore_errors=True)
os.makedirs("runtime_result_in",exist_ok=True)
os.makedirs("runtime_out",exist_ok=True)

# Explicit run/artifact references remain backward compatible. New
# executions first resolve the immutable FORMAL phase from the canonical
# execution store. Actions artifacts are only a compatibility fallback.
route=result_route(raw_req,gateway)
run_id=req.get("source_run_id")
artifact_name=req.get("artifact_name")
resolution_mode="EXPLICIT_BACKWARD_COMPAT"
chosen=None
canonical=None
if route=="CANONICAL":
    canonical=materialize_phase(execution_id,"FORMAL","runtime_result_in")
    if canonical is not None:
        run_id=(canonical.get("manifest") or {}).get("run_id")
        artifact_name=gateway_artifact_name(execution_id,"FORMAL",gateway,"LOCAL")
        resolution_mode="CANONICAL_EXECUTION_STORE"
    else:
        target_name=gateway_artifact_name(execution_id,"FORMAL",gateway,"LOCAL")
        repo=os.environ.get("GITHUB_REPOSITORY") or ""
        token=os.environ.get("GH_TOKEN") or ""
        if not repo or not token:
            raise SystemExit("FINAL_ARTIFACT_AUTO_RESOLUTION_CONTEXT_MISSING")
        url=(
            f"https://api.github.com/repos/{repo}/actions/artifacts"
            f"?name={urllib.parse.quote(target_name)}&per_page=100"
        )
        status,listing=request_json(
            url,
            method="GET",
            headers={
                "accept":"application/vnd.github+json",
                "authorization":f"Bearer {token}",
                "x-github-api-version":"2022-11-28",
                "user-agent":"keibametrics-execution-gateway",
            },
            timeout=60,
            attempts=4,
        )
        if status>=300:
            raise SystemExit("FORMAL_ARTIFACT_LIST_FAILED:"+str(status))
        candidates=[
            a for a in (listing.get("artifacts") or [])
            if not a.get("expired") and str(a.get("name") or "")==target_name
        ]
        if not candidates:
            raise SystemExit("FORMAL_ARTIFACT_NOT_FOUND_FOR_EXECUTION_ID:"+execution_id)
        candidates.sort(key=lambda a:str(a.get("created_at") or ""),reverse=True)
        chosen=candidates[0]
        artifact_name=target_name
        run_id=((chosen.get("workflow_run") or {}).get("id"))
        if not run_id:
            raise SystemExit("FORMAL_ARTIFACT_WORKFLOW_RUN_ID_MISSING")
        resolution_mode="EXECUTION_ID_AUTO_RESOLVE"

if run_id is not None and resolution_mode!="CANONICAL_EXECUTION_STORE":
    run_id=int(run_id)
json.dump({
    "mode":resolution_mode,
    "execution_id":execution_id,
    "formal_artifact_name":artifact_name,
    "workflow_run_id":run_id,
    "artifact_id":(chosen or {}).get("id"),
    "created_at":(chosen or {}).get("created_at"),
    "execution_store_manifest_sha256":((canonical or {}).get("latest") or {}).get("manifest_sha256"),
},open("runtime_out/artifact_resolution.json","w",encoding="utf-8"),
  ensure_ascii=False,sort_keys=True,indent=2)

if resolution_mode!="CANONICAL_EXECUTION_STORE":
    subprocess.run(["gh","run","download",str(run_id),"-n",artifact_name,"-D","runtime_result_in"],check=True)
fin_path=os.path.join("runtime_result_in","final_receipt_envelope.json")
fin=json.load(open(fin_path,encoding="utf-8"))
rid=req["race_id"]
if (fin.get("receipt") or {}).get("race_id")!=rid:
    raise SystemExit("RESULT_FINAL_RACE_ID_MISMATCH")
endpoint=str(family_config("LOCAL",gateway).get("external_endpoint") or "").rstrip("/")
if not endpoint.startswith("https://"):
    raise SystemExit("CANONICAL_LOCAL_EXTERNAL_ENDPOINT_INVALID")

tickets=((fin.get("artifact") or {}).get("final_ticket") or {}).get("tickets") or []
top3=[int(x) for x in req["finish_order"][:3]]
payouts={str(k).upper():int(v) for k,v in (req.get("payouts") or {}).items()}
total_investment=sum(int(t.get("stake") or 0) for t in tickets)
total_return=0
winning=[]
by_type={}
for t in tickets:
    bt=str(t.get("bet_type") or "").upper()
    sel=[int(x) for x in (t.get("selection") or [])]
    st=int(t.get("stake") or 0)
    b=by_type.setdefault(bt,{"investment":0,"return":0,"wins":[]})
    b["investment"]+=st
    hit=(bt=="EXACTA" and sel==top3[:2]) or (bt=="TRIO" and set(sel)==set(top3)) or (bt=="TRIFECTA" and sel==top3)
    if hit and bt in payouts:
        r=st*payouts[bt]//100
        total_return+=r; b["return"]+=r
        win={"bet_type":bt,"selection":sel,"stake":st,"payout_per_100":payouts[bt],"return":r}
        winning.append(win); b["wins"].append(win)

result_payload={
  "family_id":"LOCAL","race_id":rid,
  "final_receipt":fin,
  "official_result":{
    "finish_order":[int(x) for x in req["finish_order"]],
    "result_available_at":req["result_available_at"],
    "source":req.get("source") or "USER_SUPPLIED_RESULT",
    "payouts":payouts
  },
  "result_available_at":req["result_available_at"],
  "settlement":{
    "status":"COMPLETE",
    "investment":total_investment,
    "settled_investment":total_investment,
    "return":total_return,
    "winning_tickets":winning
  },
  "pfs_authority":req.get("pfs_authority") or "FROZEN-RECOMMENDATION"
}
def post(path,payload):
    status,body=request_json(
        endpoint+path,
        method="POST",
        payload=payload,
        timeout=180,
        attempts=4,
    )
    if status>=300:
        raise SystemExit(f"RUNTIME_POST_FAILED:{path}:{status}:{json.dumps(body,ensure_ascii=False)}")
    return body
final_ver=post("/verify",fin)
if not final_ver.get("verified") and not final_ver.get("valid"):
    raise SystemExit("FINAL_SIGNATURE_VERIFY_FAILED_BEFORE_MEC_SHADOW")

reuse_path=os.environ.get("KM_RESULT_REUSE_PATH")
if reuse_path:
    # The orchestrator transports an immutable stored receipt, not a new
    # RESULT request. Verify it externally and bind every financial input.
    res=json.load(open(reuse_path,encoding="utf-8"))
    ver=post("/verify",res)
    recovery=verify_result_reuse(res,fin,result_payload,ver)
    json.dump(recovery,open("runtime_out/result_recovery.json","w",encoding="utf-8"),
              ensure_ascii=False,sort_keys=True)
else:
    res=post("/result",result_payload)
    # Preserve the response before /verify transport can fail. An unverified
    # receipt is not completion, but must never trigger another /result call.
    json.dump(res,open("runtime_out/result_receipt_envelope.json","w",encoding="utf-8"),
              ensure_ascii=False,sort_keys=True,separators=(",",":"))
    json.dump({"FINAL":True,"RESULT":False},
              open("runtime_out/receipt_verifications.json","w",encoding="utf-8"),
              ensure_ascii=False,sort_keys=True)
    ver=post("/verify",res)
if (res.get("receipt") or {}).get("status")!="PASS":
    raise SystemExit("RESULT_NOT_PASS:"+json.dumps(res,ensure_ascii=False))
if not ver.get("verified"):
    raise SystemExit("RESULT_SIGNATURE_VERIFY_FAILED")

art=res.get("artifact") or {}
os.makedirs("runtime_out",exist_ok=True)
json.dump(res,open("runtime_out/result_receipt_envelope.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True,separators=(",",":"))
# Persist verified terminal evidence before optional reflection/research work.
# A later failure must not cause the same signed outcome to be settled twice.
json.dump({"FINAL":bool(final_ver.get("verified") or final_ver.get("valid")),"RESULT":True},
          open("runtime_out/receipt_verifications.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True)

# Measurement authority is stronger than the operator confirmation flag alone.
def _runtime_result_authority_compat(obj,result,request,envelope,verification):
    """
    Correctness adapter only. Phase B.2's frozen validator was preregistered
    against the legacy key `frozen_references`, while Runtime RESULT v1 signs
    the identical immutable FINAL reference under `frozen_refs`.
    We never mutate the signed artifact. We accept the alias only when the
    frozen validator's sole failure is the FINAL-binding key mismatch and the
    signed runtime artifact carries the exact expected FINAL receipt SHA.
    """
    from local_candidate_postresult import result_authority
    authority=result_authority(obj,result,request,envelope,verification)
    if authority.get("status")=="PASS":
        return authority
    if authority.get("failures")!=["SIGNED_FINAL_EXECUTION_BINDING_MISMATCH"]:
        return authority
    artifact=(envelope or {}).get("artifact") or {}
    expected=str(obj.get("final_receipt_sha256") or "")
    actual=str(((artifact.get("frozen_refs") or {}).get("final_receipt_sha256")) or "")
    if not expected or actual!=expected:
        return authority
    return {
        **authority,
        "status":"PASS",
        "failures":[],
        "compatibility_resolution":"RUNTIME_V1_FROZEN_REFS_ALIAS_EXACT_SHA",
        "compatibility_production_effect":"NONE",
    }

try:
    normalized_signed_result={**art,"race_id":rid,"official_result":{**(art.get("official_result") or {}),"top3":top3}}
    shared_result_authority=_runtime_result_authority_compat(
        {"race_id":rid,"execution_id":execution_id,"final_receipt_sha256":fin.get("receipt_sha256")},
        normalized_signed_result,req,res,ver
    )
except Exception as authority_error:
    shared_result_authority={"status":"HOLD_RESULT_AUTHORITY","verified_signed_result":False,
                             "failures":[type(authority_error).__name__+":"+str(authority_error)],"production_effect":"NONE"}

# Critical-path reflection is available immediately after the verified RESULT.
# Deep candidate/MEC research continues below but is not required to understand
# the first material failure before preparing the next race.
fast_reflection=build_fast_reflection(art,race_id=rid)
json.dump(fast_reflection,open("runtime_out/race_day_fast_reflection.json","w",encoding="utf-8"),
          ensure_ascii=False,sort_keys=True,separators=(",",":"))
print("KM_RACE_DAY_FAST_REFLECTION="+json.dumps(fast_reflection,ensure_ascii=False,separators=(",",":")))

# Optional confirmed Actual Purchase measurement; never infer a purchase from FINAL.
try:
    from pfs_grand_review import actual_purchase_records
    actual_result={**art,"race_id":rid,"official_result":{**(art.get("official_result") or result_payload["official_result"]),"top3":top3}}
    actual_rows,actual_held=actual_purchase_records(result_overrides={rid:actual_result})
    json.dump({"status":"VERIFIED_DATA" if actual_rows else "UNKNOWN / NO VERIFIED PURCHASE",
        "records":actual_rows,"held":actual_held,"production_effect":"NONE"},
        open("runtime_out/actual_purchase_pfs.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True)
except Exception as actual_error:
    json.dump({"status":"UNKNOWN / MEASUREMENT_ERROR","error":str(actual_error),"production_effect":"NONE"},
        open("runtime_out/actual_purchase_pfs.json","w",encoding="utf-8"),ensure_ascii=False)

# LOCAL MEC-R4 forward OOS: only a Shadow whose digest was bound into
# the signed pre-result FINAL may enter the preregistered tracker.
mec_r4_shadow_settlement=None
# Phase B.1 reuses the existing LOCAL measurement owner and persistence step.
# RESULT signature has already been verified. A missing payout holds research only.
try:
    from local_candidate_postresult import persist_forward_capture,settle_forward_capture,persist_forward_settlement,forward_status
    forward_path=os.path.join("runtime_result_in","local_forward_measurement_pre_result.json")
    if os.path.exists(forward_path):
        forward=json.load(open(forward_path,encoding="utf-8"))
        persist_forward_capture(forward)
        forward_result=dict(art)
        forward_result["race_id"]=rid
        # Signed API result may expose finish_order rather than top3; shared settlement needs top3.
        forward_result["official_result"]=dict(art.get("official_result") or result_payload["official_result"])
        forward_result["official_result"]["top3"]=list(req["finish_order"][:3])
        forward_measurement=settle_forward_capture(forward,fin,forward_result,result_request=req,diagnosis=fast_reflection,result_envelope=res,result_verification=ver)
        # Preserve the preregistered settlement logic while correcting only the
        # Runtime-v1 RESULT key alias at the authority boundary.
        if (
            shared_result_authority.get("status")=="PASS"
            and (forward_measurement.get("result_authority") or {}).get("failures")==["SIGNED_FINAL_EXECUTION_BINDING_MISMATCH"]
        ):
            complete=bool(forward_measurement.get("arms")) and all(
                a.get("status")=="SETTLED" for a in (forward_measurement.get("arms") or {}).values()
            )
            krs_eligible=bool(
                forward.get("classification")=="FORWARD"
                and not req.get("acceptance_only")
            )
            eligible=bool(
                krs_eligible
                and complete
                and (forward.get("capital") or {}).get("production_comparable_equal_spend")
            )
            forward_measurement["result_authority"]=shared_result_authority
            forward_measurement["krs_eligible"]=krs_eligible
            forward_measurement["eligible"]=eligible
            forward_measurement["status"]="SETTLED" if complete else "HOLD_MISSING_PAYOUT_OR_ARM"
            import hashlib
            forward_measurement["sha256"]=hashlib.sha256(
                json.dumps(
                    {k:v for k,v in forward_measurement.items() if k!="sha256"},
                    ensure_ascii=False,sort_keys=True,separators=(",",":")
                ).encode()
            ).hexdigest()
        counts_before=forward_status()
        persist_forward_settlement(forward,forward_measurement)
        json.dump(forward_measurement,open("runtime_out/local_forward_measurement_settlement.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True)
        status=forward_status()
        json.dump(status,open("runtime/local_candidate_forward_status.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True)
        json.dump(status,open("runtime_out/local_candidate_forward_status.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True)
except (Exception,SystemExit) as forward_error:
    json.dump({"status":"SHADOW_HOLD_OR_REJECTED","production_effect":"NONE","error":str(forward_error)},
        open("runtime_out/local_forward_measurement_failure.json","w",encoding="utf-8"),ensure_ascii=False)

mec_r4_binding=None
mec_r4_oos_status=None
mec_r4_shadow_path=os.path.join("runtime_result_in","mec_r4_shadow_pre_result.json")
try:
    if (not acceptance_only) and os.path.exists(mec_r4_shadow_path):
        shadow=json.load(open(mec_r4_shadow_path,encoding="utf-8"))
        mec_r4_binding=verify_signed_final_binding(fin,shadow)
        shadow_result={
            "official_result":{
                "status":"OFFICIAL_OR_USER_SUPPLIED_OFFICIAL",
                "top3":top3,
                "payouts_per_100_yen":payouts,
            }
        }
        mec_r4_shadow_settlement=settle_mec_r4_shadow(shadow,shadow_result)
        prod_replay=settle_ticket_list(tickets,shadow_result)
        if prod_replay.get("status")!="SETTLED":
            raise SystemExit("MEC_R4_PRODUCTION_REPLAY_NOT_SETTLED")
        if int(prod_replay.get("investment") or 0)!=int(total_investment) or int(prod_replay.get("return") or 0)!=int(total_return):
            raise SystemExit("MEC_R4_PRODUCTION_REPLAY_MISMATCH")

        for d in ("runtime/mec_shadow_artifacts","runtime/mec_shadow_results","runtime/mec_shadow_lineage"):
            os.makedirs(d,exist_ok=True)
        json.dump(shadow,open(os.path.join("runtime","mec_shadow_artifacts",rid+".json"),"w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,indent=2)
        json.dump(mec_r4_shadow_settlement,open(os.path.join("runtime","mec_shadow_results",rid+".json"),"w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,indent=2)
        lineage={
            "lineage_type":"LOCAL_SIGNED_FINAL_BOUND",
            "race_id":rid,
            "binding_valid":True,
            "shadow_sha256":shadow.get("sha256"),
            "basis_sha256":shadow.get("source_immutable_final_sha256"),
            "final_receipt_sha256":fin.get("receipt_sha256"),
            "final_artifact_sha256":(fin.get("receipt") or {}).get("artifact_sha256"),
            "source_run_id":run_id,
            "source_artifact_name":artifact_name,
            "generated_at":shadow.get("generated_at"),
            "scheduled_post_at":shadow.get("scheduled_post_at"),
            "temporal_mode":shadow.get("temporal_mode"),
            "production_tickets":tickets,
            "production_result":shadow_result,
            "production_settlement":{
                "status":"SETTLED",
                "total_investment":total_investment,
                "total_payout":total_return,
            },
            "production_effect":"NONE","result_authority":shared_result_authority,
        }
        lineage["sha256"]=__import__("hashlib").sha256(
            json.dumps(lineage,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
        ).hexdigest()
        json.dump(lineage,open(os.path.join("runtime","mec_shadow_lineage",rid+".json"),"w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,indent=2)
        mec_r4_oos_status=write_mec_r4_oos_status()
        json.dump(mec_r4_shadow_settlement,open("runtime_out/mec_r4_shadow_settlement.json","w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,separators=(",",":"))
        json.dump(mec_r4_binding,open("runtime_out/mec_r4_shadow_binding.json","w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,separators=(",",":"))
        json.dump(mec_r4_oos_status,open("runtime_out/mec_r4_oos_status.json","w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,separators=(",",":"))

except (Exception, SystemExit) as shadow_error:
    shadow_diagnostic={"status":"SHADOW_HOLD_OR_REJECTED","production_effect":"NONE",
                       "error":type(shadow_error).__name__+":"+str(shadow_error),"stage":'if (not acceptance_only) and os.path.exists(mec_r4_shadow_path)'}
    try:
        json.dump(shadow_diagnostic,open("runtime_out/shadow_failure_192.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True)
    except Exception:
        print("KM_SHADOW_DIAGNOSTIC="+json.dumps(shadow_diagnostic,ensure_ascii=False))

# LOCAL-specific MEC-R5 candidate was designed from 2026-09-23
# training races and is eligible only for future signed-bound shadows.
local_mec_r5_shadow_settlement=None
local_mec_r5_binding=None
local_mec_r5_oos_status=None
local_mec_r5_shadow_path=os.path.join("runtime_result_in","local_mec_r5_shadow_pre_result.json")
try:
    if (not acceptance_only) and os.path.exists(local_mec_r5_shadow_path):
        r5_shadow=json.load(open(local_mec_r5_shadow_path,encoding="utf-8"))
        local_mec_r5_binding=verify_local_mec_r5_signed_final_binding(fin,r5_shadow)
        local_mec_r5_shadow_settlement=settle_local_mec_r5_shadow(
            r5_shadow,req,signed_final_binding_valid=True
        )

        shadow_result={
            "official_result":{
                "status":"OFFICIAL_OR_USER_SUPPLIED_OFFICIAL",
                "top3":top3,
                "payouts_per_100_yen":payouts,
            }
        }
        prod_replay_r5=settle_ticket_list(tickets,shadow_result)
        if prod_replay_r5.get("status")!="SETTLED":
            raise SystemExit("LOCAL_MEC_R5_PRODUCTION_REPLAY_NOT_SETTLED")
        if int(prod_replay_r5.get("investment") or 0)!=int(total_investment) or int(prod_replay_r5.get("return") or 0)!=int(total_return):
            raise SystemExit("LOCAL_MEC_R5_PRODUCTION_REPLAY_MISMATCH")

        for d in ("runtime/local_mec_r5_shadow_artifacts","runtime/local_mec_r5_shadow_results","runtime/local_mec_r5_shadow_lineage"):
            os.makedirs(d,exist_ok=True)
        json.dump(r5_shadow,open(os.path.join("runtime","local_mec_r5_shadow_artifacts",rid+".json"),"w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,indent=2)
        json.dump(local_mec_r5_shadow_settlement,open(os.path.join("runtime","local_mec_r5_shadow_results",rid+".json"),"w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,indent=2)
        r5_lineage={
            "lineage_type":"LOCAL_MEC_R5_SIGNED_FINAL_BOUND",
            "race_id":rid,
            "binding_valid":True,
            "shadow_sha256":r5_shadow.get("sha256"),
            "basis_sha256":r5_shadow.get("source_basis_sha256"),
            "final_receipt_sha256":fin.get("receipt_sha256"),
            "final_artifact_sha256":(fin.get("receipt") or {}).get("artifact_sha256"),
            "source_run_id":run_id,
            "source_artifact_name":artifact_name,
            "generated_at":r5_shadow.get("generated_at"),
            "scheduled_post_at":r5_shadow.get("scheduled_post_at"),
            "temporal_mode":r5_shadow.get("temporal_mode"),
            "production_tickets":tickets,
            "production_result":shadow_result,
            "production_settlement":{
                "status":"SETTLED",
                "total_investment":total_investment,
                "total_payout":total_return,
            },
            "production_effect":"NONE","result_authority":shared_result_authority,
        }
        r5_lineage["sha256"]=__import__("hashlib").sha256(
            json.dumps(r5_lineage,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
        ).hexdigest()
        json.dump(r5_lineage,open(os.path.join("runtime","local_mec_r5_shadow_lineage",rid+".json"),"w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,indent=2)
        local_mec_r5_oos_status=write_local_mec_r5_oos_status()
        json.dump(local_mec_r5_shadow_settlement,open("runtime_out/local_mec_r5_shadow_settlement.json","w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,separators=(",",":"))
        json.dump(local_mec_r5_binding,open("runtime_out/local_mec_r5_shadow_binding.json","w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,separators=(",",":"))
        json.dump(local_mec_r5_oos_status,open("runtime_out/local_mec_r5_oos_status.json","w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,separators=(",",":"))

except (Exception, SystemExit) as shadow_error:
    shadow_diagnostic={"status":"SHADOW_HOLD_OR_REJECTED","production_effect":"NONE",
                       "error":type(shadow_error).__name__+":"+str(shadow_error),"stage":'if (not acceptance_only) and os.path.exists(local_mec_r5_shadow_path)'}
    try:
        json.dump(shadow_diagnostic,open("runtime_out/shadow_failure_256.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True)
    except Exception:
        print("KM_SHADOW_DIAGNOSTIC="+json.dumps(shadow_diagnostic,ensure_ascii=False))

# Common Exact Continuity C2 shadow: only a pre-result artifact whose
# digest is bound into the signed FINAL can enter the forward OOS tracker.
common_exact_continuity_settlement=None
common_exact_continuity_binding=None
common_exact_continuity_oos_status=None
common_exact_path=os.path.join("runtime_result_in","common_exact_continuity_shadow_pre_result.json")
try:
    if (not acceptance_only) and os.path.exists(common_exact_path):
        common_exact=json.load(open(common_exact_path,encoding="utf-8"))
        common_exact_continuity_binding=verify_common_exact_continuity_binding(fin,common_exact)
        common_exact_continuity_settlement=settle_common_exact_continuity_shadow(
            common_exact,[int(x) for x in req["finish_order"]],payouts,
            int(total_investment),int(total_return),signed_final_binding_valid=True
        )
        for d in (
            "runtime/common_exact_continuity_shadow_artifacts",
            "runtime/common_exact_continuity_shadow_results",
            "runtime/common_exact_continuity_shadow_lineage",
        ):
            os.makedirs(d,exist_ok=True)
        json.dump(common_exact,open(os.path.join("runtime","common_exact_continuity_shadow_artifacts",rid+".json"),"w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,indent=2)
        json.dump(common_exact_continuity_settlement,open(os.path.join("runtime","common_exact_continuity_shadow_results",rid+".json"),"w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,indent=2)
        common_lineage={
            "lineage_type":"COMMON_EXACT_CONTINUITY_SIGNED_FINAL_BOUND",
            "race_id":rid,"binding_valid":True,
            "shadow_sha256":common_exact.get("sha256"),
            "basis_sha256":common_exact.get("source_basis_sha256"),
            "final_receipt_sha256":fin.get("receipt_sha256"),
            "final_artifact_sha256":(fin.get("receipt") or {}).get("artifact_sha256"),
            "source_run_id":run_id,"source_artifact_name":artifact_name,
            "generated_at":common_exact.get("generated_at"),
            "scheduled_post_at":common_exact.get("scheduled_post_at"),
            "temporal_mode":common_exact.get("temporal_mode"),
            "production_effect":"NONE","result_authority":shared_result_authority,
        }
        common_lineage["sha256"]=__import__("hashlib").sha256(
            json.dumps(common_lineage,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
        ).hexdigest()
        json.dump(common_lineage,open(os.path.join("runtime","common_exact_continuity_shadow_lineage",rid+".json"),"w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,indent=2)
        common_exact_continuity_oos_status=write_common_exact_continuity_oos_status()
        json.dump(common_exact_continuity_settlement,open("runtime_out/common_exact_continuity_shadow_settlement.json","w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,separators=(",",":"))
        json.dump(common_exact_continuity_binding,open("runtime_out/common_exact_continuity_shadow_binding.json","w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,separators=(",",":"))
        json.dump(common_exact_continuity_oos_status,open("runtime_out/common_exact_continuity_oos_status.json","w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,separators=(",",":"))

except (Exception, SystemExit) as shadow_error:
    shadow_diagnostic={"status":("SHADOW_HOLD" if "PAYOUT_REQUIRED" in str(shadow_error) else "SHADOW_REJECTED"),"production_effect":"NONE",
                       "error":type(shadow_error).__name__+":"+str(shadow_error),"stage":'if (not acceptance_only) and os.path.exists(common_exact_path)'}
    try:
        json.dump(shadow_diagnostic,open("runtime_out/common_exact_continuity_shadow_failure.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True)
    except Exception:
        print("KM_SHADOW_DIAGNOSTIC="+json.dumps(shadow_diagnostic,ensure_ascii=False))

candidate_dual_postresult=None
dual_path=os.path.join("runtime_result_in","candidate_numerical_dual_shadow_summary.json")
dual_krs_path=os.path.join("runtime_result_in","candidate_krs_dual_shadow_summary.json")
calibration_path="runtime/calibration/local_weight_calibration_v0.2_20260923_urw_day_summary.json"
try:
    if (not acceptance_only) and os.path.exists(dual_path):
        dual=json.load(open(dual_path,encoding="utf-8"))
        dual_krs=json.load(open(dual_krs_path,encoding="utf-8")) if os.path.exists(dual_krs_path) else {}
        cal=json.load(open(calibration_path,encoding="utf-8")) if os.path.exists(calibration_path) else {}
        envs={}
        for arm,fn in (("v0.1","candidate_krs_v01_receipt_envelope.json"),("v0.2","candidate_krs_v02_receipt_envelope.json")):
            pth=os.path.join("runtime_result_in",fn)
            if os.path.exists(pth):
                envs[arm]=json.load(open(pth,encoding="utf-8"))
        candidate_dual_postresult=evaluate_dual(
            dual,[int(x) for x in req["finish_order"]],
            result_available_at=req["result_available_at"],race_id=rid,
            dual_krs_summary=dual_krs,
            calibration_training_race_ids=cal.get("training_race_ids") or [],
            dual_krs_envelopes=envs
        )
        json.dump(candidate_dual_postresult,open("runtime_out/candidate_dual_shadow_postresult.json","w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,separators=(",",":"))

except (Exception, SystemExit) as shadow_error:
    shadow_diagnostic={"status":"SHADOW_HOLD_OR_REJECTED","production_effect":"NONE",
                       "error":type(shadow_error).__name__+":"+str(shadow_error),"stage":'if (not acceptance_only) and os.path.exists(dual_path)'}
    try:
        json.dump(shadow_diagnostic,open("runtime_out/shadow_failure_370.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True)
    except Exception:
        print("KM_SHADOW_DIAGNOSTIC="+json.dumps(shadow_diagnostic,ensure_ascii=False))

candidate_v03_postresult=None
candidate_v03_summary=None
candidate_krs_v03_summary=None
candidate_v03_binding_valid=False
v03_path=os.path.join("runtime_result_in","candidate_numerical_v03_shadow_summary.json")
v03_krs_summary_path=os.path.join("runtime_result_in","candidate_krs_v03_shadow_summary.json")
v03_krs_envelope_path=os.path.join("runtime_result_in","candidate_krs_v03_receipt_envelope.json")
try:
    if (not acceptance_only) and os.path.exists(v03_path):
        candidate_v03_summary=json.load(open(v03_path,encoding="utf-8"))
        candidate_krs_v03_summary=(
            json.load(open(v03_krs_summary_path,encoding="utf-8"))
            if os.path.exists(v03_krs_summary_path) else {}
        )
        v03_env=(
            json.load(open(v03_krs_envelope_path,encoding="utf-8"))
            if os.path.exists(v03_krs_envelope_path) else None
        )
        trace=((fin.get("artifact") or {}).get("ticket_transport_trace") or {})
        bound=(trace.get("numerical_candidate_v03_shadow") or {})
        candidate_v03_binding_valid=bool(
            bound.get("frozen_pre_result") is True
            and str(bound.get("shadow_sha256") or "")==str(candidate_v03_summary.get("sha256") or "")
            and str(bound.get("source_snapshot_sha256") or "")==str(candidate_v03_summary.get("source_snapshot_sha256") or "")
        )
        candidate_v03_postresult=evaluate_v03(
            candidate_v03_summary,[int(x) for x in req["finish_order"]],
            result_available_at=req["result_available_at"],race_id=rid,
            krs_summary=candidate_krs_v03_summary,
            krs_envelope=v03_env,
            signed_final_binding_valid=candidate_v03_binding_valid,
        )
        json.dump(candidate_v03_postresult,open("runtime_out/candidate_v03_shadow_postresult.json","w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,separators=(",",":"))
        json.dump({
            "race_id":rid,
            "binding_valid":candidate_v03_binding_valid,
            "signed_final_bound":bound,
            "shadow_sha256":candidate_v03_summary.get("sha256"),
            "production_effect":"NONE","result_authority":shared_result_authority,
        },open("runtime_out/candidate_v03_signed_final_binding.json","w",encoding="utf-8"),
          ensure_ascii=False,sort_keys=True,separators=(",",":"))

except (Exception, SystemExit) as shadow_error:
    shadow_diagnostic={"status":"SHADOW_HOLD_OR_REJECTED","production_effect":"NONE",
                       "error":type(shadow_error).__name__+":"+str(shadow_error),"stage":'if (not acceptance_only) and os.path.exists(v03_path)'}
    try:
        json.dump(shadow_diagnostic,open("runtime_out/shadow_failure_396.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True)
    except Exception:
        print("KM_SHADOW_DIAGNOSTIC="+json.dumps(shadow_diagnostic,ensure_ascii=False))

candidate_oos_measurement=None
candidate_oos_status=None
try:
    if candidate_dual_postresult is not None:
        candidate_oos_measurement=build_measurement(candidate_dual_postresult,req)
        mdir=os.path.join("runtime","local_candidate_dual_oos_measurements")
        os.makedirs(mdir,exist_ok=True)
        mpath=os.path.join(mdir,rid+".json")
        json.dump(candidate_oos_measurement,open(mpath,"w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,indent=2)
        candidate_oos_status=write_status(
            mdir,os.path.join("runtime","local_candidate_dual_oos_status.json")
        )
        json.dump(candidate_oos_measurement,open("runtime_out/candidate_dual_oos_measurement.json","w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,separators=(",",":"))
        json.dump(candidate_oos_status,open("runtime_out/candidate_dual_oos_status.json","w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,separators=(",",":"))

except (Exception, SystemExit) as shadow_error:
    shadow_diagnostic={"status":"SHADOW_HOLD_OR_REJECTED","production_effect":"NONE",
                       "error":type(shadow_error).__name__+":"+str(shadow_error),"stage":'if candidate_dual_postresult is not None'}
    try:
        json.dump(shadow_diagnostic,open("runtime_out/shadow_failure_433.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True)
    except Exception:
        print("KM_SHADOW_DIAGNOSTIC="+json.dumps(shadow_diagnostic,ensure_ascii=False))

candidate_v03_oos_measurement=None
candidate_v03_oos_status=None
try:
    if candidate_v03_postresult is not None:
        candidate_v03_oos_measurement=build_v03_measurement(
            candidate_v03_postresult,req,baseline_measurement=candidate_oos_measurement
        )
        v03dir=os.path.join("runtime","local_candidate_v03_oos_measurements")
        os.makedirs(v03dir,exist_ok=True)
        json.dump(candidate_v03_oos_measurement,open(os.path.join(v03dir,rid+".json"),"w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,indent=2)
        candidate_v03_oos_status=write_v03_status(
            v03dir,os.path.join("runtime","local_candidate_v03_oos_status.json")
        )
        json.dump(candidate_v03_oos_measurement,open("runtime_out/candidate_v03_oos_measurement.json","w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,separators=(",",":"))
        json.dump(candidate_v03_oos_status,open("runtime_out/candidate_v03_oos_status.json","w",encoding="utf-8"),
                  ensure_ascii=False,sort_keys=True,separators=(",",":"))

except (Exception, SystemExit) as shadow_error:
    shadow_diagnostic={"status":"SHADOW_HOLD_OR_REJECTED","production_effect":"NONE",
                       "error":type(shadow_error).__name__+":"+str(shadow_error),"stage":'if candidate_v03_postresult is not None'}
    try:
        json.dump(shadow_diagnostic,open("runtime_out/shadow_failure_450.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True)
    except Exception:
        print("KM_SHADOW_DIAGNOSTIC="+json.dumps(shadow_diagnostic,ensure_ascii=False))

try:
    if acceptance_only:
        open("runtime_out/acceptance_only.flag","w",encoding="utf-8").write("true\n")

except (Exception, SystemExit) as shadow_error:
    shadow_diagnostic={"status":"SHADOW_HOLD_OR_REJECTED","production_effect":"NONE",
                       "error":type(shadow_error).__name__+":"+str(shadow_error),"stage":'if acceptance_only'}
    try:
        json.dump(shadow_diagnostic,open("runtime_out/shadow_failure_466.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True)
    except Exception:
        print("KM_SHADOW_DIAGNOSTIC="+json.dumps(shadow_diagnostic,ensure_ascii=False))

summary={
  "race_id":rid,
  "execution_id":execution_id,
  "acceptance_only":acceptance_only,
  "result_receipt":res.get("receipt_sha256"),
  "verified":True,
  "investment":total_investment,
  "return":total_return,
  "profit_loss":total_return-total_investment,
  "pfs":(None if total_investment==0 else round(total_return/total_investment*100,6)),
  "winning_tickets":winning,
  "by_type":by_type,
  "failure_localization":art.get("failure_localization"),
  "automatic_post_result_review":art.get("automatic_post_result_review"),
  "learning_event":art.get("learning_event"),
  "race_day_fast_reflection":fast_reflection,
  "candidate_dual_shadow_postresult":candidate_dual_postresult,
  "candidate_dual_oos_measurement":candidate_oos_measurement,
  "candidate_dual_oos_status":candidate_oos_status,
  "candidate_v03_shadow_postresult":candidate_v03_postresult,
  "candidate_v03_signed_final_binding_valid":candidate_v03_binding_valid,
  "candidate_v03_oos_measurement":candidate_v03_oos_measurement,
  "candidate_v03_oos_status":candidate_v03_oos_status,
  "mec_r4_shadow_settlement_sha256":(mec_r4_shadow_settlement or {}).get("sha256"),
  "mec_r4_signed_final_binding":mec_r4_binding,
  "mec_r4_oos_status":mec_r4_oos_status,
  "local_mec_r5_shadow_settlement_sha256":(local_mec_r5_shadow_settlement or {}).get("sha256"),
  "local_mec_r5_signed_final_binding":local_mec_r5_binding,
  "local_mec_r5_oos_status":local_mec_r5_oos_status
}
json.dump(summary,open("runtime_out/result_summary.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True,separators=(",",":"))
print("KM_LOCAL_RESULT="+json.dumps(summary,ensure_ascii=False,separators=(",",":")))

# Initial live acceptance summarizes existing artifacts only; it does not generate predictions.
try:
    if 'forward_measurement' in globals():
        from local_candidate_postresult import initial_forward_acceptance
        acceptance=initial_forward_acceptance(forward,forward_measurement,counts_before,forward_status())
        extra={}
        for name in ['mec_r4_shadow_settlement.json','local_mec_r5_shadow_settlement.json','common_exact_continuity_shadow_settlement.json']:
            path=os.path.join('runtime_out',name)
            if os.path.exists(path):extra[name]=json.load(open(path,encoding='utf-8'))
            else:extra[name]={'status':'MISSING_NOT_ZERO'}
        acceptance['existing_shadow_settlements']=extra
        if any(x.get('status')=='MISSING_NOT_ZERO' or not x.get('arms') or any(a.get('status') not in {None,'SETTLED'} for a in x.get('arms',{}).values()) for x in extra.values()) or any(x.get('oos_eligible') is False for x in extra.values()):
            acceptance['status']='PENDING_OR_HELD';acceptance['post_result_settlement']='HOLD_MISSING_EXISTING_SHADOW_SETTLEMENT'
        json.dump(acceptance,open('runtime_out/local_initial_forward_acceptance.json','w',encoding='utf-8'),ensure_ascii=False,sort_keys=True)
        json.dump(acceptance,open('runtime/local_initial_forward_acceptance.json','w',encoding='utf-8'),ensure_ascii=False,sort_keys=True)
except Exception as error:
    json.dump({'status':'PENDING_OR_HELD','error':str(error),'production_effect':'NONE'},open('runtime_out/local_initial_forward_acceptance_failure.json','w',encoding='utf-8'),ensure_ascii=False)

# Durable learning closure has a direct immutable FINAL/RESULT lineage.
# Research HOLD is retained as a terminal, never counted or used to stop Production.
learning_state={"race_id":rid,"execution_id":execution_id,
    "final_receipt_sha256":fin.get("receipt_sha256"),"result_receipt_sha256":res.get("receipt_sha256"),
    "learning_event":art.get("learning_event"),"failure_localization":art.get("failure_localization"),
    "automatic_post_result_review":art.get("automatic_post_result_review"),
    "production_policy_change":False,"actual_purchase_pfs":"UNKNOWN_UNLESS_VERIFIED"}
json.dump(learning_state,open("runtime_out/learning_state.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True)
receipt_verifications={"FINAL":bool(final_ver.get("verified") or final_ver.get("valid")),"RESULT":bool(ver.get("verified"))}
json.dump(receipt_verifications,open("runtime_out/receipt_verifications.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True)
tracker_terminal={"race_id":rid,"execution_id":execution_id,
    "status":"PASS" if 'forward_measurement' in globals() and forward_measurement.get("eligible") is True else "HOLD",
    "research_failure_nonblocking":True,"production_effect":"NONE",
    "reason":None if 'forward_measurement' in globals() else "FORWARD_CAPTURE_OR_SETTLEMENT_MISSING"}
json.dump(tracker_terminal,open("runtime_out/forward_tracker_terminal.json","w",encoding="utf-8"),ensure_ascii=False,sort_keys=True)
