"""Private FNB dual-owner KRS EXECUTION, not a simulated SUCCESS receipt.

Run the existing immutable KRS-Engine v1.1.0 and canonical provisional LOCAL
parameter_map, each owner exactly 5,000 times using master seed 1. No new KRS
physics, numeric consumer activation, role promotion, model probabilities,
ticket policy, wager, signing, GitHub push, or v2 OOS registration.

The caller must provide both previously frozen BASELINE and CANDIDATE inputs
and a private directory outside the publicly visible repository.
This actor does not obtain sources or fabricate missing owner predictions.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile
from datetime import datetime,timezone
from pathlib import Path

from runtime.local_fnb_r13_private_single_numeric import _atomic_private_write,_encoded,_sha

ENGINE_SHA="9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421"
MAP_SHA="d8c027ee5bcc8fd3d2c248e8059b341776be38910e833d7589f09ab817c161f5"
PROFILE="KM-FNB-R14-PRIVATE-DUAL-OWNER-REAL-KRS-5000-SEED1-v1"
OWNERS=("BASELINE","CANDIDATE")


def _digest_file(path:Path)->str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _aware(value):
    try:stamp=datetime.fromisoformat(str(value).replace("Z","+00:00"))
    except (ValueError,TypeError) as exc:raise ValueError("FNB_KRS_TIME_INVALID") from exc
    if stamp.tzinfo is None:raise ValueError("FNB_KRS_TIMEZONE_REQUIRED")
    return stamp


def _check_input(q, owner, race_id):
    if not isinstance(q,dict) or not isinstance(q.get("horses"),list):
        raise ValueError("FNB_KRS_FROZEN_OWNER_INPUT_REQUIRED:"+owner)
    if (q.get("owner")!=owner or q.get("race_id")!=race_id or
            q.get("classification")!="PRIVATE_NONPRODUCTION_FIXED_OWNER"):
        raise ValueError("FNB_KRS_WRONG_OWNER_OR_RACE:"+owner)
    if not isinstance(q.get("original_prediction_sha256"),str) or len(q["original_prediction_sha256"])!=64:
        raise ValueError("FNB_KRS_OWNER_FROZEN_PREDICTION_SHA_REQUIRED:"+owner)
    race=q.get("race")
    if not isinstance(race,dict) or race.get("prediction_id")!=race_id+"-"+owner:
        raise ValueError("FNB_KRS_PREDICTION_ID_NOT_OWNER_SCOPED:"+owner)
    if not isinstance(race.get("date"),str) or not isinstance(race.get("racecourse"),str):
        raise ValueError("FNB_KRS_DATE_AND_RACECOURSE_REQUIRED:"+owner)
    if not isinstance(race.get("race_no"),int) or not 1<=race["race_no"]<=12:
        raise ValueError("FNB_KRS_RACE_NUMBER_INVALID")
    ids=[]
    for h in q["horses"]:
        if not isinstance(h,dict) or not isinstance(h.get("horse_no"),int):
            raise ValueError("FNB_KRS_ACTIVE_HORSE_NO_INVALID")
        if not isinstance(h.get("hsv"),dict) or not isinstance(h.get("static"),dict):
            raise ValueError("FNB_KRS_HSV_AND_STATIC_EVIDENCE_REQUIRED")
        ids.append(h["horse_no"])
    if len(ids)<2 or len(ids)!=len(set(ids)):
        raise ValueError("FNB_KRS_ACTIVE_HORSE_SET_DUPLICATE_OR_EMPTY")
    return tuple(sorted(ids))


def execute(*,inputs:dict,engine:Path,params:Path,private_output:Path,
            public_repo:Path,race_id:str,cutoff_at:str,diagnostic_only:bool=False,
            now=None,python_exec=None):
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:raise ValueError("FNB_KRS_EXECUTION_TIMEZONE_REQUIRED")
    cutoff=_aware(cutoff_at)
    if now>=cutoff and not diagnostic_only:
        raise ValueError("FNB_KRS_PRESTART_CUTOFF_MISSED_NO_RETROACTIVE_FINAL")
    root=Path(private_output).resolve(); repo=Path(public_repo).resolve()
    if root==repo or repo in root.parents:
        raise ValueError("FNB_KRS_PRIVATE_OUTPUT_INSIDE_PUBLIC_GIT_REPO")
    if not isinstance(inputs,dict) or set(inputs)!=set(OWNERS):
        raise ValueError("FNB_KRS_BOTH_FIXED_OWNERS_REQUIRED")
    engine=Path(engine).resolve();params=Path(params).resolve()
    if _digest_file(engine)!=ENGINE_SHA or _digest_file(params)!=MAP_SHA:
        raise ValueError("FNB_KRS_IMMUTABLE_ENGINE_OR_PARAMETER_MAP_SHA_MISMATCH")
    cohort={name:_check_input(inputs[name],name,race_id) for name in OWNERS}
    if cohort["BASELINE"]!=cohort["CANDIDATE"]:
        raise ValueError("FNB_KRS_OWNERS_DIFFERENT_ACTIVE_UNIVERSES")
    conditions=[inputs[o]["race"] for o in OWNERS]
    if any(conditions[0].get(k)!=conditions[1].get(k) for k in
           ("date","race_no","racecourse","distance_m","surface","direction")):
        raise ValueError("FNB_KRS_DIFFERENT_RACE_CONDITIONS")
    folder=root/race_id
    folder.mkdir(parents=True,exist_ok=True)
    os.chmod(folder,0o700)
    if (not diagnostic_only and inputs["BASELINE"]["original_prediction_sha256"]==
                            inputs["CANDIDATE"]["original_prediction_sha256"]):
        raise ValueError("FNB_KRS_TWO_DISTINCT_FROZEN_OWNER_PREDICTIONS_REQUIRED")
    results={}
    for owner in OWNERS:
        original=inputs[owner]
        # Never alter the upstream STATIC or source-derived HSV arrays.
        payload=json.loads(json.dumps(original,ensure_ascii=False))
        if not isinstance(payload.get("simulation"),dict):
            payload["simulation"]={}
        payload["simulation"].update(run_count=5000,master_seed=1)
        input_bytes=_encoded(payload)
        input_sha=_atomic_private_write(folder/(owner+"_krs_input.json"),input_bytes)
        target=folder/(owner+"_krs_output.json")
        with tempfile.TemporaryDirectory(dir=root) as work:
            tmp=Path(work)/"out.json"
            command=[str(python_exec or sys.executable),str(engine),
                     str(folder/(owner+"_krs_input.json")),
                     "--params",str(params),"--runs","5000","--seed","1",
                     "--output",str(tmp)]
            completed=subprocess.run(command,capture_output=True,text=True,
                                     timeout=120,check=False)
            if completed.returncode!=0 or not tmp.is_file():
                raise ValueError("FNB_KRS_REAL_ENGINE_EXECUTION_FAILED:"+owner+
                                 ":"+str(completed.returncode))
            output_data=tmp.read_bytes()
        rendered=json.loads(output_data)
        snapshot=rendered.get("snapshot") or {}
        eng=rendered.get("engine") or {}
        if (snapshot.get("master_seed")!=1 or snapshot.get("run_count")!=5000
                or snapshot.get("prediction_id")!=race_id+"-"+owner
                or snapshot.get("race_no")!=conditions[0]["race_no"]
                or snapshot.get("field_size")!=len(cohort[owner])
                or eng.get("engine_version")!="1.1.0"
                or eng.get("parameter_map_version")!="0.1-provisional"
                or eng.get("parameter_status")!="PROVISIONAL_UNCALIBRATED"
                or not isinstance(rendered.get("summary"),list)
                or len(rendered["summary"])!=len(cohort[owner])):
            raise ValueError("FNB_KRS_EXECUTED_ENGINE_OUTPUT_NOT_BOUND_TO_OWNER:"+owner)
        output_sha=_atomic_private_write(target,output_data)
        results[owner]={
            "owner":owner,"source_original_prediction_sha256":original["original_prediction_sha256"],
            "actual_krs_runs":5000,"actual_master_seed":1,
            "candidate_or_baseline_input_sha256":input_sha,
            "actual_output_sha256":output_sha,
            "snapshot_id":snapshot.get("simulation_snapshot_id"),
            "convergence_status":(rendered.get("convergence_audit") or {}).get("status"),
            "seed_stability_status":(rendered.get("seed_stability_audit") or {}).get("status"),
            "uncalibrated_occurrences_not_win_probability":True,
            "external_ed25519_signed_receipt":False,
            "frozen_owner_sha_claim_independently_signed_verified":False,
            "ticket_purchase_proven":False}
    manifest={
        "profile":PROFILE,
        "classification":("POSTCUTOFF_DIAGNOSTIC_ONLY_NOT_REGISTERED_OOS"
           if diagnostic_only else "SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS"),
        "race_id":race_id,"owners":results,"active_runners":list(cohort["BASELINE"]),
        "engine_sha256":ENGINE_SHA,"parameter_map_sha256":MAP_SHA,
        "private_model_output_persisted_and_bytes_readback":True,
        "owner_source_sha_independently_frozen_here":False,
        "official_source_signature_issued_here":False,
        "formal_scope_or_numerical_consumer_changed":False,
        "w_p2_p3_common_decision_formed_here":False,
        "six_ticket_methods_formed_here":False,
        "user_delivery_ack_proven":False,
        "actual_purchase_proven":False,
        "registered_oos_increment":0}
    receipt=_encoded(manifest)
    receipt_sha=_atomic_private_write(folder/"private_dual_krs_receipt.json",receipt)
    if _sha((folder/"private_dual_krs_receipt.json").read_bytes())!=receipt_sha:
        raise ValueError("FNB_KRS_PRIVATE_RECEIPT_READBACK_FAILED")
    return {"status":"DUAL_OWNER_REAL_LOCAL_ENGINE_EXECUTED_PRIVATE" ,
            "race_id":race_id,"owner_count":len(results),
            "private_receipt_sha256":receipt_sha,
            "engine_sha256":ENGINE_SHA,"parameter_map_sha256":MAP_SHA,
            "registered_oos_increment":0,"formal_final_or_delivery_verified":False}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ("baseline-input","candidate-input","engine","params",
                "private-output","public-repo","race-id","cutoff-at"):
        parser.add_argument("--"+key,required=True)
    parser.add_argument("--diagnostic-only",action="store_true")
    args=parser.parse_args(argv)
    files={"BASELINE":args.baseline_input,"CANDIDATE":args.candidate_input}
    data={k:json.loads(Path(v).read_text(encoding="utf-8")) for k,v in files.items()}
    result=execute(inputs=data,engine=Path(args.engine),params=Path(args.params),
                   private_output=Path(args.private_output),
                   public_repo=Path(args.public_repo),race_id=args.race_id,
                   cutoff_at=args.cutoff_at,diagnostic_only=args.diagnostic_only)
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
