from __future__ import annotations
import base64, hashlib, json, os, pathlib, subprocess, tempfile, datetime
from typing import Any, Dict
from fastapi import FastAPI, HTTPException
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from post_result_learning import build_post_result_review, build_learning_state
from minimum_efficient_coverage import validate_mec_plan, MEC_PROFILE
from capital_policy import PROFILE as CAPITAL_PROFILE

APP_VERSION="KM-LOCAL-PHYSICAL-RUNTIME-v1.5-REV.4-20260923-RUNTIME-SYNC-ACTIVE-UNIVERSE"
RECEIPT_SCHEMA="KM-LOCAL-SIGNED-RECEIPT-v1"
ENGINE_PATH=os.environ.get("KM_LOCAL_ENGINE_PATH","/opt/km/KRS-Engine_v1.1.0_PORTABLE.py")
PARAM_PATH=os.environ.get("KM_LOCAL_PARAM_PATH","/opt/km/parameter_map_v0.1-provisional.json")
ENGINE_SHA=os.environ["KM_LOCAL_ENGINE_SHA256"]
PARAM_SHA=os.environ["KM_LOCAL_PARAMETER_MAP_SHA256"]
SIGNER=os.environ["KM_LOCAL_RECEIPT_SIGNER_KEY_ID"]
PRIVATE_B64=os.environ["KM_LOCAL_RECEIPT_PRIVATE_KEY_B64"]
GIT_REV=os.environ.get("KM_LOCAL_GITHUB_REV","UNKNOWN")
FAMILY="LOCAL"
HSV_KEYS=["base_competitive_ability","class_strength","condition_fit","distance_fit","surface_fit","gate_reliability","initial_acceleration","position_intent","inside_cut_ability","outside_press_ability","leader_need","stalk_acceptance","crowd_tolerance","early_position_hold","midrace_hold","progression_ceiling","progression_timing","corner_acceleration","traffic_escape","sustained_speed","pressure_tolerance","front_friction_tolerance","long_move_tolerance","final_reserve","deceleration_risk","training_state","bodyweight_state","layoff_uncertainty","comment_state","data_confidence"]
STATIC_KEYS=["tpi","zai_win","zai_place","sri","t3i","f3s","w_aki","p2_aki","p3_aki","asi","rsi"]
app=FastAPI(title="KeibaMetrics LOCAL Physical Runtime",version=APP_VERSION)

def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def jdump(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()

def sha_obj(x):
    return hashlib.sha256(jdump(x)).hexdigest()

def sha_file(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def private_key():
    return Ed25519PrivateKey.from_private_bytes(base64.b64decode(PRIVATE_B64))

def public_b64():
    b=private_key().public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
    return base64.b64encode(b).decode()

def signed_receipt(phase:str,race_id:str,status:str,artifact:Dict[str,Any],errors=None):
    runtime_hashes={
       "legacy_runtime_app_sha256":sha_file(__file__),
       "runtime_wrapper_sha256":sha_file("/opt/km/app_v15.py") if pathlib.Path("/opt/km/app_v15.py").exists() else None,
       "source_acquisition_sha256":sha_file("/opt/km/source_acquisition.py") if pathlib.Path("/opt/km/source_acquisition.py").exists() else None,
       "nar_source_manifest_sha256":sha_file("/opt/km/nar_source_manifest.py") if pathlib.Path("/opt/km/nar_source_manifest.py").exists() else None,
       "nar_runner_universe_sha256":sha_file("/opt/km/nar_runner_universe.py") if pathlib.Path("/opt/km/nar_runner_universe.py").exists() else None,
    }
    r={"schema":RECEIPT_SCHEMA,"runtime_revision":APP_VERSION,"family":FAMILY,
       "phase":phase,"race_id":race_id,"status":status,"errors":errors or [],
       "artifact_sha256":sha_obj(artifact),"timestamp":utcnow(),
       "engine_version":"1.1.0","engine_sha256":ENGINE_SHA,
       "parameter_map_version":"0.1-provisional","parameter_map_sha256":PARAM_SHA,
       "calibration_status":"PROVISIONAL_UNCALIBRATED","github_revision":GIT_REV,
       "runtime_hashes":runtime_hashes}
    rb=jdump(r)
    return {"receipt":r,"receipt_sha256":hashlib.sha256(rb).hexdigest(),
            "signature":base64.b64encode(private_key().sign(rb)).decode(),
            "signer_key_id":SIGNER,"signature_alg":"Ed25519","artifact":artifact}

def verify_envelope(env):
    try:
        rec=env["receipt"]
        private_key().public_key().verify(base64.b64decode(env["signature"]),jdump(rec))
        return hashlib.sha256(jdump(rec)).hexdigest()==env.get("receipt_sha256")
    except Exception:
        return False

def validate_family(p):
    if str(p.get("family_id") or "").upper()!=FAMILY:
        raise HTTPException(422,"LOCAL_FAMILY_REQUIRED")

def validate_krs_input(d):
    hs=d.get("horses")
    if not isinstance(hs,list) or len(hs)<2:
        raise HTTPException(422,"LOCAL_KRS_HORSES_INVALID")
    for h in hs:
        if set((h.get("hsv") or {}).keys())!=set(HSV_KEYS):
            raise HTTPException(422,f"LOCAL_HSV_SCHEMA_MISMATCH:{h.get('horse_no')}")
        if set((h.get("static") or {}).keys())!=set(STATIC_KEYS):
            raise HTTPException(422,f"LOCAL_STATIC_SCHEMA_MISMATCH:{h.get('horse_no')}")
    return True

@app.get("/health")
def health():
    es=sha_file(ENGINE_PATH); ps=sha_file(PARAM_PATH)
    ok=(es==ENGINE_SHA and ps==PARAM_SHA)
    return {"status":"READY" if ok else "HASH_MISMATCH","family":FAMILY,"runtime_revision":APP_VERSION,
      "engine_version":"1.1.0","engine_sha256":es,"expected_engine_sha256":ENGINE_SHA,
      "parameter_map_version":"0.1-provisional","parameter_map_sha256":ps,
      "expected_parameter_map_sha256":PARAM_SHA,"calibration_status":"PROVISIONAL_UNCALIBRATED",
      "receipt_signer_key_id":SIGNER,"receipt_public_key_b64":public_b64(),
      "github_revision":GIT_REV,"runtime_app_sha256":sha_file(__file__),"capabilities":["PRE_KRS","KRS_EXECUTE","FINAL","FORMAL","RESULT","VERIFY"]}

@app.post("/verify")
def verify(payload:Dict[str,Any]):
    valid=verify_envelope(payload)
    return {"valid":valid,"verified":valid,"signer_key_id":SIGNER,"family":FAMILY}

@app.post("/pre-krs")
def pre_krs(p:Dict[str,Any]):
    validate_family(p)
    rid=str(p.get("race_id") or "")
    if not rid: raise HTTPException(422,"RACE_ID_REQUIRED")
    krs=p.get("krs_input_data")
    errs=[]
    try: validate_krs_input(krs or {})
    except HTTPException as e: errs.append(str(e.detail))
    if p.get("required_index_unresolved",0): errs.append("REQUIRED_INDEX_UNRESOLVED")
    if p.get("full_terminalization") is not True: errs.append("FULL_INDEX_TERMINALIZATION_REQUIRED")
    full_numeric=(p.get("full_numerical_calculation") is True)
    input_mode=str(p.get("krs_input_mode") or ((krs or {}).get("keibametrics_input_authority") or {}).get("input_mode") or "")
    if not full_numeric and input_mode!="TECHNICAL_PROXY_DIAGNOSTIC":
        errs.append("NON_NUMERICAL_KRS_MUST_BE_TECHNICAL_PROXY_DIAGNOSTIC")
    if not p.get("static_prediction_frozen"): errs.append("STATIC_PREDICTION_FREEZE_REQUIRED")
    art={"input_sha256":sha_obj(krs or {}),"runner_count":len((krs or {}).get("horses") or []),
         "full_terminalization":bool(p.get("full_terminalization")),
         "full_numerical_calculation":full_numeric,
         "krs_input_mode":input_mode,
         "numerical_authority":"FULL_NUMERICAL" if full_numeric else "TERMINAL_COMPLETE_PROXY_KRS",
         "static_prediction_frozen":bool(p.get("static_prediction_frozen"))}
    return signed_receipt("PRE_KRS",rid,"PASS" if not errs else "FAIL",art,errs)

@app.post("/krs/execute")
def krs_execute(p:Dict[str,Any]):
    validate_family(p)
    rid=str(p.get("race_id") or "")
    inp=p.get("krs_input_data") or {}
    validate_krs_input(inp)
    run_count=int(p.get("run_count") or (inp.get("simulation") or {}).get("run_count") or 5000)
    seed=int(p.get("seed") or (inp.get("simulation") or {}).get("master_seed") or 1)
    if run_count<5000: raise HTTPException(422,"LOCAL_SIM_STD_MIN_5000")
    inp=json.loads(json.dumps(inp))
    inp.setdefault("simulation",{})["run_count"]=run_count
    inp["simulation"]["master_seed"]=seed
    started=utcnow()
    with tempfile.TemporaryDirectory() as td:
        ip=pathlib.Path(td)/"input.json"; op=pathlib.Path(td)/"output.json"; cp=pathlib.Path(td)/"summary.csv"
        ip.write_text(json.dumps(inp,ensure_ascii=False),encoding="utf-8")
        cmd=["python",ENGINE_PATH,str(ip),"--output",str(op),"--csv",str(cp),
             "--runs",str(run_count),"--seed",str(seed),"--params",PARAM_PATH]
        proc=subprocess.run(cmd,capture_output=True,text=True,timeout=max(120,run_count//20))
        if proc.returncode!=0 or not op.exists():
            art={"requested_run_count":run_count,"returncode":proc.returncode,"stderr_tail":proc.stderr[-2000:]}
            return signed_receipt("KRS_RUN",rid,"FAIL",art,["ENGINE_EXECUTION_FAILED"])
        out=json.loads(op.read_text(encoding="utf-8"))
    artifact={"requested_run_count":run_count,"actual_run_count":run_count,"seed":seed,
      "input_sha256":sha_obj(inp),"output_sha256":sha_obj(out),
      "engine_version":"1.1.0","engine_sha256":ENGINE_SHA,
      "parameter_map_version":"0.1-provisional","parameter_map_sha256":PARAM_SHA,
      "calibration_status":"PROVISIONAL_UNCALIBRATED","started_at":started,"completed_at":utcnow(),
      "raw_output":out}
    return signed_receipt("KRS_RUN",rid,"EXECUTED",artifact,[])

@app.post("/final")
def final(p:Dict[str,Any]):
    validate_family(p)
    rid=str(p.get("race_id") or "")
    errs=[]
    run=p.get("krs_run_receipt")
    if not isinstance(run,dict) or not verify_envelope(run): errs.append("KRS_RUN_RECEIPT_INVALID")
    elif (run.get("receipt") or {}).get("status")!="EXECUTED": errs.append("KRS_NOT_EXECUTED")
    fpp=p.get("final_prediction_package")
    if not isinstance(fpp,dict): errs.append("FINAL_PREDICTION_PACKAGE_MISSING")
    ft=p.get("final_ticket")
    if not isinstance(ft,dict): errs.append("FINAL_TICKET_MISSING")
    if not p.get("final_freeze_timestamp"): errs.append("FINAL_FREEZE_TIMESTAMP_MISSING")

    mec=p.get("minimum_efficient_coverage")
    if not isinstance(mec,dict):
        errs.append("MEC_MISSING")
        mec_check=None
    else:
        try:
            mec_check=validate_mec_plan(mec)
            if mec.get("profile")!=MEC_PROFILE: errs.append("MEC_PROFILE_MISMATCH")
            if mec.get("precompression_semantic_universe") is not True: errs.append("MEC_PRECOMPRESSION_UNIVERSE_REQUIRED")
        except Exception as e:
            mec_check=None
            errs.append("MEC_INVALID:"+str(e))

    capital=p.get("capital_policy_decision")
    if not isinstance(capital,dict):
        errs.append("CAPITAL_DECISION_MISSING")
    else:
        if str(capital.get("profile") or "")!=CAPITAL_PROFILE: errs.append("CAPITAL_PROFILE_MISMATCH")
        if isinstance(mec,dict) and str(capital.get("mec_sha256") or "")!=str(mec.get("sha256") or ""):
            errs.append("CAPITAL_MEC_HASH_MISMATCH")
        if float(capital.get("material_coverage_ratio",0) or 0)!=1.0:
            errs.append("CAPITAL_MATERIAL_COVERAGE_INCOMPLETE")

    trace=p.get("ticket_transport_trace")
    if not isinstance(trace,dict):
        errs.append("TICKET_TRANSPORT_TRACE_MISSING")
    else:
        for k in ("fpp_sha256","mec_sha256","candidate_count","selected_count","capital_decision_sha256"):
            if k not in trace: errs.append("TICKET_TRANSPORT_TRACE_FIELD_MISSING:"+k)
        if isinstance(mec,dict) and str(trace.get("mec_sha256") or "")!=str(mec.get("sha256") or ""):
            errs.append("TRACE_MEC_HASH_MISMATCH")
        if isinstance(capital,dict) and str(trace.get("capital_decision_sha256") or "")!=str(capital.get("sha256") or ""):
            errs.append("TRACE_CAPITAL_HASH_MISMATCH")

    stage_manifest=p.get("execution_stage_manifest")
    required_stages=["SOURCE_FREEZE","RUNNER_UNIVERSE","NUMERICAL_MATERIALIZATION","INDEX_PROVENANCE","STATIC_FREEZE","PRE_KRS","KRS","KRS_UTILITY","MEC","CAPITAL","FINAL_TICKET_FREEZE"]
    if not isinstance(stage_manifest,list):
        errs.append("EXECUTION_STAGE_MANIFEST_MISSING")
    else:
        names={str(x.get("stage")) for x in stage_manifest if isinstance(x,dict)}
        missing=[x for x in required_stages if x not in names]
        if missing: errs.append("EXECUTION_STAGE_MISSING:"+",".join(missing))

    if isinstance(ft,dict):
        ts=ft.get("tickets")
        if not isinstance(ts,list): errs.append("FINAL_TICKET_LIST_MISSING")
        total=ft.get("total_investment")
        if isinstance(ts,list):
            stake_sum=sum(int(x.get("stake",0)) for x in ts if isinstance(x,dict))
            if total is None or int(total)!=stake_sum: errs.append("FINAL_TICKET_STAKE_MISMATCH")
        if isinstance(capital,dict) and isinstance(mec,dict):
            no_bet=bool(capital.get("no_bet"))
            if no_bet and ts: errs.append("NO_BET_WITH_TICKETS")
            if not no_bet:
                if int(ft.get("total_investment") or -1)!=int(mec.get("minimum_required_capital") or -2):
                    errs.append("FINAL_CAPITAL_MEC_MISMATCH")
                if int(trace.get("selected_count",-1) if isinstance(trace,dict) else -1)!=len(ts or []):
                    errs.append("TRACE_SELECTED_COUNT_MISMATCH")

    if isinstance(run,dict) and str((run.get("receipt") or {}).get("race_id") or "")!=rid:
        errs.append("KRS_RUN_RACE_ID_MISMATCH")

    artifact={"final_prediction_package":fpp,"final_ticket":ft,
      "minimum_efficient_coverage":mec,"mec_verification":mec_check,
      "capital_policy_decision":capital,"ticket_transport_trace":trace,
      "execution_stage_manifest":stage_manifest,
      "final_freeze_timestamp":p.get("final_freeze_timestamp"),"ticket_sha256":sha_obj(ft or {}),
      "krs_receipt_sha256":(run or {}).get("receipt_sha256")}
    return signed_receipt("FINAL",rid,"PASS" if not errs else "FAIL",artifact,errs)

@app.post("/formal")
def formal(p:Dict[str,Any]):
    validate_family(p)
    rid=str(p.get("race_id") or "")
    pre=pre_krs(p)
    if pre["receipt"]["status"]!="PASS":
        return signed_receipt("FORMAL",rid,"FAIL",{"pre_krs_receipt":pre},["PRE_KRS_FAIL"])
    run=krs_execute({"family_id":FAMILY,"race_id":rid,"krs_input_data":p.get("krs_input_data"),
                     "run_count":p.get("run_count",5000),"seed":p.get("seed",1)})
    if run["receipt"]["status"]!="EXECUTED":
        return signed_receipt("FORMAL",rid,"FAIL",
          {"pre_krs_receipt":pre,"krs_run_receipt":run},["KRS_FAIL"])
    fin=final({"family_id":FAMILY,"race_id":rid,"krs_run_receipt":run,
               "final_prediction_package":p.get("final_prediction_package"),
               "final_ticket":p.get("final_ticket"),
               "minimum_efficient_coverage":p.get("minimum_efficient_coverage"),
               "capital_policy_decision":p.get("capital_policy_decision"),
               "ticket_transport_trace":p.get("ticket_transport_trace"),
               "execution_stage_manifest":p.get("execution_stage_manifest"),
               "final_freeze_timestamp":p.get("final_freeze_timestamp")})
    if fin["receipt"]["status"]!="PASS":
        return signed_receipt("FORMAL",rid,"FAIL",
          {"pre_krs_receipt":pre,"krs_run_receipt":run,"final_receipt":fin},["FINAL_FAIL"])
    artifact={"pre_krs_receipt":pre,"krs_run_receipt":run,"final_receipt":fin,
      "requested_run_count":run["artifact"]["requested_run_count"],
      "actual_run_count":run["artifact"]["actual_run_count"],
      "input_sha256":run["artifact"]["input_sha256"],"output_sha256":run["artifact"]["output_sha256"],
      "final_ticket_sha256":fin["artifact"]["ticket_sha256"]}
    formal_status="FULL_FORMAL_E2E_PASS" if (pre.get("artifact") or {}).get("full_numerical_calculation") is True else "FORMAL_E2E_TERMINALIZED_PROXY_KRS_PASS"
    return signed_receipt("FORMAL",rid,formal_status,artifact,[])


def _money_int(v,name):
    if isinstance(v,bool):
        raise HTTPException(422,f"{name}_INVALID")
    try:
        x=int(v)
    except Exception:
        raise HTTPException(422,f"{name}_INVALID")
    if x<0:
        raise HTTPException(422,f"{name}_NEGATIVE")
    return x

def _ticket_investment(final_ticket):
    if not isinstance(final_ticket,dict):
        return None
    if final_ticket.get("total_investment") is not None:
        return _money_int(final_ticket.get("total_investment"),"FINAL_TICKET_INVESTMENT")
    ts=final_ticket.get("tickets")
    if not isinstance(ts,list):
        return None
    return sum(_money_int(x.get("stake",0),"TICKET_STAKE") for x in ts if isinstance(x,dict))

@app.post("/result")
def result(p:Dict[str,Any]):
    validate_family(p)
    rid=str(p.get("race_id") or "")
    if not rid:
        raise HTTPException(422,"RACE_ID_REQUIRED")
    errs=[]

    fin=p.get("final_receipt")
    if not isinstance(fin,dict) or not verify_envelope(fin):
        errs.append("FINAL_RECEIPT_INVALID")
    elif (fin.get("receipt") or {}).get("status")!="PASS":
        errs.append("FINAL_RECEIPT_NOT_PASS")
    elif str((fin.get("receipt") or {}).get("race_id") or "")!=rid:
        errs.append("FINAL_RECEIPT_RACE_ID_MISMATCH")

    official=p.get("official_result")
    if not isinstance(official,dict):
        errs.append("OFFICIAL_RESULT_MISSING")
        official={}
    else:
        order=official.get("finish_order")
        if not isinstance(order,list) or not order:
            errs.append("OFFICIAL_FINISH_ORDER_MISSING")
        if not p.get("result_available_at") and not official.get("result_available_at"):
            errs.append("RESULT_AVAILABLE_AT_MISSING")

    settlement=p.get("settlement")
    if not isinstance(settlement,dict):
        errs.append("SETTLEMENT_MISSING")
        settlement={}
    settlement_status=str(settlement.get("status") or "").upper()
    allowed={"COMPLETE","PARTIAL","PENDING","UNKNOWN","VOID","REFUND"}
    if settlement_status not in allowed:
        errs.append("SETTLEMENT_STATUS_INVALID")

    final_ticket=((fin or {}).get("artifact") or {}).get("final_ticket")
    frozen_investment=_ticket_investment(final_ticket) if isinstance(final_ticket,dict) else None
    supplied_investment=settlement.get("investment")
    investment=None
    if supplied_investment is not None:
        try: investment=_money_int(supplied_investment,"SETTLEMENT_INVESTMENT")
        except HTTPException as e:
            errs.append(str(e.detail))
    if frozen_investment is not None and investment is not None and frozen_investment!=investment:
        errs.append("SETTLEMENT_INVESTMENT_MISMATCH_FROZEN_TICKET")
    if investment is None:
        investment=frozen_investment

    ret=None
    if settlement.get("return") is not None:
        try: ret=_money_int(settlement.get("return"),"SETTLEMENT_RETURN")
        except HTTPException as e:
            errs.append(str(e.detail))

    settled_investment=None
    if settlement.get("settled_investment") is not None:
        try: settled_investment=_money_int(settlement.get("settled_investment"),"SETTLED_INVESTMENT")
        except HTTPException as e:
            errs.append(str(e.detail))

    if settlement_status=="COMPLETE":
        if investment is None: errs.append("INVESTMENT_REQUIRED_FOR_COMPLETE_SETTLEMENT")
        if ret is None: errs.append("RETURN_REQUIRED_FOR_COMPLETE_SETTLEMENT")
        if settled_investment is not None and investment is not None and settled_investment!=investment:
            errs.append("COMPLETE_SETTLEMENT_AMOUNT_MISMATCH")
    elif settlement_status=="PARTIAL":
        if settled_investment is None or ret is None:
            errs.append("PARTIAL_SETTLEMENT_REQUIRES_SETTLED_INVESTMENT_AND_RETURN")
        elif investment is not None and settled_investment>investment:
            errs.append("SETTLED_INVESTMENT_EXCEEDS_TOTAL")
    elif settlement_status in {"PENDING","UNKNOWN"}:
        if ret==0:
            errs.append("PENDING_UNKNOWN_RETURN_ZERO_FORBIDDEN")
    elif settlement_status in {"VOID","REFUND"}:
        if ret is None:
            errs.append("VOID_REFUND_RETURN_REQUIRED")

    pfs=None
    profit_loss=None
    settlement_completeness=None
    if settlement_status=="COMPLETE" and investment is not None and ret is not None:
        pfs=None if investment==0 else round(ret/investment*100.0,6)
        profit_loss=ret-investment
        settlement_completeness=100.0
    elif settlement_status=="PARTIAL" and settled_investment is not None and ret is not None:
        pfs=None if settled_investment==0 else round(ret/settled_investment*100.0,6)
        profit_loss=ret-settled_investment
        settlement_completeness=(None if investment in (None,0) else round(settled_investment/investment*100.0,6))
    elif settlement_status in {"VOID","REFUND"} and investment is not None and ret is not None:
        pfs=None if investment==0 else round(ret/investment*100.0,6)
        profit_loss=ret-investment
        settlement_completeness=100.0

    auto_review=None
    auto_learning=None
    try:
        finish_order=official.get("finish_order") or []
        if len(finish_order)>=3 and isinstance(fin,dict):
            frozen_final_artifact=(fin.get("artifact") or {})
            frozen_fpp=(frozen_final_artifact.get("final_prediction_package") or {})
            final_artifact={
                "race_id":rid,
                "sha256":(fin.get("receipt") or {}).get("artifact_sha256"),
                "final_receipt_sha256":fin.get("receipt_sha256"),
                "final_prediction_package":frozen_fpp,
                "final_ticket":(frozen_final_artifact.get("final_ticket") or {}),
                "krs_prediction_utility":(
                    frozen_fpp.get("krs_prediction_utility_shadow")
                    or frozen_final_artifact.get("krs_prediction_utility")
                    or p.get("krs_prediction_utility")
                    or {}
                ),
                "minimum_efficient_coverage":(
                    frozen_final_artifact.get("minimum_efficient_coverage")
                    or frozen_fpp.get("minimum_efficient_coverage")
                    or p.get("minimum_efficient_coverage")
                    or {}
                ),
            }
            learning_result={
                "race_id":rid,
                "official_result":{"top3":[int(x) for x in finish_order[:3]]},
                "frozen_prediction_ref":{
                    "final_receipt_sha256":fin.get("receipt_sha256"),
                    "final_status":(fin.get("receipt") or {}).get("status")
                },
                "settlement":{
                    "status":settlement_status,
                    "investment":investment,
                    "total_investment":investment,
                    "settled_investment":settled_investment,
                    "return":ret,
                    "total_payout":ret,
                    "pfs_authority":p.get("pfs_authority"),
                    "winning_tickets":settlement.get("winning_tickets") or []
                }
            }
            auto_review=build_post_result_review(learning_result,final_artifact)
            auto_learning=build_learning_state(auto_review)
    except Exception as e:
        errs.append("AUTO_POSTRESULT_LEARNING_FAILED:"+str(e))

    caller_learning=p.get("learning_event") if isinstance(p.get("learning_event"),dict) else None
    caller_failure=p.get("failure_localization") if isinstance(p.get("failure_localization"),dict) else None

    if auto_review is not None:
        failure={
            "primary_failure":(auto_review.get("failure_localization") or {}).get("first_material_failure"),
            "secondary_failure":"NONE",
            "materiality":"MATERIAL" if (auto_review.get("failure_localization") or {}).get("first_material_failure")!="NONE" else "NON-MATERIAL",
            "automatic":True,
            "review_sha256":auto_review.get("sha256")
        }
    elif caller_failure is not None:
        failure=caller_failure
    else:
        failure={}
        errs.append("FAILURE_LOCALIZATION_MISSING")

    if auto_learning is not None:
        learning={
            "automatic":True,
            "profile":auto_learning.get("profile"),
            "state_id":auto_learning.get("state_id"),
            "status":auto_learning.get("status"),
            "source_review_sha256":auto_learning.get("source_review_sha256"),
            "immediate_correctness":auto_learning.get("immediate_correctness"),
            "shadow_candidates":auto_learning.get("shadow_candidates"),
            "reference_metrics":auto_learning.get("reference_metrics"),
            "forbidden":auto_learning.get("forbidden"),
            "production_change_authorized":auto_learning.get("production_change_authorized")
        }
    elif caller_learning is not None:
        learning=caller_learning
    else:
        learning={}
        errs.append("LEARNING_EVENT_MISSING")

    frozen_refs={
        "final_receipt_sha256":(fin or {}).get("receipt_sha256"),
        "final_ticket_sha256":sha_obj(final_ticket or {}),
        "final_freeze_timestamp":((fin or {}).get("artifact") or {}).get("final_freeze_timestamp")
    }
    artifact={
        "official_result":official,
        "settlement":{
            "status":settlement_status,
            "investment":investment,
            "settled_investment":(
                settled_investment
                if settled_investment is not None
                else (investment if settlement_status in {"COMPLETE","VOID","REFUND"} else None)
            ),
            "return":ret,
            "profit_loss":profit_loss,
            "pfs":pfs,
            "pfs_authority":p.get("pfs_authority"),
            "settlement_completeness_pct":settlement_completeness
        },
        "failure_localization":failure,
        "learning_event":learning,
        "automatic_post_result_review":auto_review,
        "automatic_next_race_learning_state":auto_learning,
        "caller_supplied_failure_localization":caller_failure,
        "caller_supplied_learning_event":caller_learning,
        "frozen_refs":frozen_refs,
        "result_available_at":p.get("result_available_at") or official.get("result_available_at"),
        "review_completed_at":utcnow()
    }
    return signed_receipt("RESULT",rid,"PASS" if not errs else "FAIL",artifact,errs)
