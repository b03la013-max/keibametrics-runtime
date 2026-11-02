"""One invocation for FNB private official SOURCE→all29→dual fixed-owner KRS.

The PUBLIC repository stores only code and synthetic tests. Actual signed
official Raw and per-horse forecasts must be supplied to an existing PRIVATE
actor; real outputs stay private. The v2 OOS day-plan and new Production
numeric consumer flags are not prerequisites for this independent research.
The lifecycle has separate evidence grades: NUMERIC_ONLY, KRS_TWO_OWNER_DONE,
and COMPLETE_FORMAL_DELIVERY (never inferred here).
"""
from __future__ import annotations

import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path

from runtime.local_fnb_r13_private_single_numeric import (
    execute as numeric_execute, _atomic_private_write, _encoded)
from runtime.local_fnb_r14_private_dual_krs import execute as dual_krs_execute

PROFILE="KM-FNB-R14-PRIVATE-ONE-TRIGGER-NUMERIC-AND-KRS-v1"


def run(*,source:dict,request:dict,root:Path,public_repo:Path,
        engine:Path|None=None,params:Path|None=None,
        owners:dict|None=None,now=None,diagnostic_only=False):
    now=now or datetime.now(timezone.utc)
    num=numeric_execute(source_artifact=source,request=request,
        private_root=root,repo_root=public_repo,now=now,
        diagnostic_only=diagnostic_only)
    race_id=request["race_id"]
    root=Path(root).resolve()
    folder=root/race_id
    status="NUMERIC_ONLY_FROZEN_OWNER_PACKETS_MISSING"
    downstream=None
    first_failure="FIXED_OWNER_INPUT_NOT_PROVIDED"
    if owners is not None:
        if (not isinstance(owners,dict) or set(owners)!=
                {"BASELINE","CANDIDATE"}):
            raise ValueError("FNB_PRIVATE_BOTH_FROZEN_OWNER_PACKETS_REQUIRED")
        for owner in ("BASELINE","CANDIDATE"):
            if owners[owner].get("numerical_materialization_sha256")!=num["private_materialization_sha256"]:
                raise ValueError("FNB_PRIVATE_OWNER_NOT_BOUND_TO_SAME_29_INDEX_FREEZE:"+owner)
        if engine is None or params is None:
            raise ValueError("FNB_PRIVATE_DUAL_KRS_ENGINE_AND_MAP_REQUIRED")
        downstream=dual_krs_execute(inputs=owners,engine=Path(engine),
                 params=Path(params),private_output=root,public_repo=public_repo,
                 race_id=race_id,cutoff_at=request["prediction_cutoff"],
                 diagnostic_only=diagnostic_only,now=now)
        status="NUMERIC_AND_TWO_OWNER_KRS_COMPLETE_ROLES_TICKETS_NOT_FORMED"
        first_failure="W_P2_P3_MEC_SIX_TICKET_METHODS_NOT_EXECUTED"
    receipt={
      "profile":PROFILE,
      "classification":("POSTCUTOFF_DIAGNOSTIC_ONLY" if diagnostic_only else
        "SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS"),
      "status":status,"first_uncompleted_stage":first_failure,
      "race_id":race_id,"source_readonly_private_numerical":{
        k:v for k,v in num.items() if k not in ("private_root",)},
      "dual_real_krs_execution":downstream,
      "all29_source_feature_receipt_verified":num["full_private_readback_verified"],
      "two_owners_5000_seed1_executed":downstream is not None,
      "model_w_p2_p3_decision_proven":False,
      "owner_six_methods_proven":False,
      "user_ticket_rendered_and_acknowledged":False,
      "actual_purchase":False,
      "pfs":None,
      "is_formal_final":False,
      "registered_oos_increment":0,
      "production_numeric_consumers_changed":False,
      "public_repo_private_raw_written":False
    }
    payload=_encoded(receipt)
    sha=_atomic_private_write(folder/"private_pipeline_checkpoint.json",payload)
    return {"status":status,"race_id":race_id,
        "private_pipeline_receipt_sha256":sha,
        "numeric_cells":num["29_index_cells"],
        "krs_two_owners_done":downstream is not None,
        "formal_final_or_delivery_done":False,
        "private_checkpoint_readback_verified":
            hashlib.sha256((folder/"private_pipeline_checkpoint.json").read_bytes()).hexdigest()==sha,
        "registered_oos_increment":0}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ("source-artifact","request","private-root"):
        p.add_argument("--"+flag,required=True)
    for flag in ("baseline-owner","candidate-owner","engine","params"):
        p.add_argument("--"+flag)
    p.add_argument("--diagnostic-only",action="store_true")
    args=p.parse_args(argv)
    owner_files=[args.baseline_owner,args.candidate_owner]
    if any(owner_files) and not all(owner_files):
        raise ValueError("BOTH_OWNER_PACKETS_REQUIRED_NOT_ONE")
    owner_data={"BASELINE":json.loads(Path(owner_files[0]).read_text()),
                "CANDIDATE":json.loads(Path(owner_files[1]).read_text())} if all(owner_files) else None
    source=json.loads(Path(args.source_artifact).read_text())
    request=json.loads(Path(args.request).read_text())
    if isinstance(source,dict) and "artifact" in source and "receipt" in source:
        source=source["artifact"]
    receipt=run(source=source,request=request,root=Path(args.private_root),
        public_repo=Path(__file__).resolve().parents[1],
        owners=owner_data,engine=Path(args.engine) if args.engine else None,
        params=Path(args.params) if args.params else None,
        diagnostic_only=args.diagnostic_only)
    print(json.dumps(receipt,ensure_ascii=False,sort_keys=True))
    return 0


if __name__=="__main__":raise SystemExit(main())
