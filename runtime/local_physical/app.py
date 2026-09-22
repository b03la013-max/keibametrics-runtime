from __future__ import annotations
import base64, hashlib, json, os, pathlib, subprocess, tempfile, datetime
from typing import Any, Dict
from fastapi import FastAPI, HTTPException
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

APP_VERSION="KM-LOCAL-PHYSICAL-RUNTIME-v1.1-20260922"
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
    r={"schema":RECEIPT_SCHEMA,"runtime_revision":APP_VERSION,"family":FAMILY,
       "phase":phase,"race_id":race_id,"status":status,"errors":errors or [],
       "artifact_sha256":sha_obj(artifact),"timestamp":utcnow(),
       "engine_version":"1.1.0","engine_sha256":ENGINE_SHA,
       "parameter_map_version":"0.1-provisional","parameter_map_sha256":PARAM_SHA,
       "calibration_status":"PROVISIONAL_UNCALIBRATED","github_revision":GIT_REV}
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
    if p.get("full_numerical_calculation") is not True: errs.append("FULL_NUMERICAL_CALCULATION_REQUIRED")
    if not p.get("static_prediction_frozen"): errs.append("STATIC_PREDICTION_FREEZE_REQUIRED")
    art={"input_sha256":sha_obj(krs or {}),"runner_count":len((krs or {}).get("horses") or []),
         "full_numerical_calculation":p.get("full_numerical_calculation"),
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
    if not isinstance(p.get("final_prediction_package"),dict): errs.append("FINAL_PREDICTION_PACKAGE_MISSING")
    ft=p.get("final_ticket")
    if not isinstance(ft,dict): errs.append("FINAL_TICKET_MISSING")
    if not p.get("final_freeze_timestamp"): errs.append("FINAL_FREEZE_TIMESTAMP_MISSING")
    artifact={"final_prediction_package":p.get("final_prediction_package"),"final_ticket":ft,
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
               "final_freeze_timestamp":p.get("final_freeze_timestamp")})
    if fin["receipt"]["status"]!="PASS":
        return signed_receipt("FORMAL",rid,"FAIL",
          {"pre_krs_receipt":pre,"krs_run_receipt":run,"final_receipt":fin},["FINAL_FAIL"])
    artifact={"pre_krs_receipt":pre,"krs_run_receipt":run,"final_receipt":fin,
      "requested_run_count":run["artifact"]["requested_run_count"],
      "actual_run_count":run["artifact"]["actual_run_count"],
      "input_sha256":run["artifact"]["input_sha256"],"output_sha256":run["artifact"]["output_sha256"],
      "final_ticket_sha256":fin["artifact"]["ticket_sha256"]}
    return signed_receipt("FORMAL",rid,"FULL_FORMAL_E2E_PASS",artifact,[])


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

    learning=p.get("learning_event")
    if not isinstance(learning,dict):
        errs.append("LEARNING_EVENT_MISSING")
        learning={}
    required_learning=["prediction_error_class","conversion_error_class","capital_efficiency_update","krs_trust_update"]
    missing_learning=[k for k in required_learning if k not in learning]
    if missing_learning:
        errs.append("LEARNING_EVENT_INCOMPLETE:"+",".join(missing_learning))

    failure=p.get("failure_localization")
    if not isinstance(failure,dict):
        errs.append("FAILURE_LOCALIZATION_MISSING")
        failure={}
    if "primary_failure" not in failure:
        errs.append("PRIMARY_FAILURE_MISSING")
    if "materiality" not in failure:
        errs.append("FAILURE_MATERIALITY_MISSING")

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
            "settled_investment":settled_investment if settled_investment is not None else investment,
            "return":ret,
            "profit_loss":profit_loss,
            "pfs":pfs,
            "pfs_authority":p.get("pfs_authority"),
            "settlement_completeness_pct":settlement_completeness
        },
        "failure_localization":failure,
        "learning_event":learning,
        "frozen_refs":frozen_refs,
        "result_available_at":p.get("result_available_at") or official.get("result_available_at"),
        "review_completed_at":utcnow()
    }
    return signed_receipt("RESULT",rid,"PASS" if not errs else "FAIL",artifact,errs)
