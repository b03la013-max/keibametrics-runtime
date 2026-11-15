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
        owners:dict|None=None,portfolios:dict|None=None,
        frozen_semantics:dict|None=None,
        now=None,diagnostic_only=False):
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
        frozen_path=folder/"numerical_materialization.json"
        frozen_bytes=frozen_path.read_bytes()
        if hashlib.sha256(frozen_bytes).hexdigest()!=num["private_materialization_sha256"]:
            raise ValueError("FNB_PRIVATE_FROZEN_29_INDEX_BYTES_CHANGED")
        frozen=json.loads(frozen_bytes)
        runner_ids={int(row["runner_id"]) for row in frozen.get("runners",[])}
        if not runner_ids or len(runner_ids)!=len(frozen.get("runners",[])):
            raise ValueError("FNB_PRIVATE_NUMERICAL_ACTIVE_UNIVERSE_INVALID")
        for owner in ("BASELINE","CANDIDATE"):
            if owners[owner].get("numerical_materialization_sha256")!=num["private_materialization_sha256"]:
                raise ValueError("FNB_PRIVATE_OWNER_NOT_BOUND_TO_SAME_29_INDEX_FREEZE:"+owner)
            own_horses=owners[owner].get("horses")
            if not isinstance(own_horses,list) or {
                    int(h.get("horse_no")) for h in own_horses if isinstance(h,dict)}!=runner_ids:
                raise ValueError("FNB_PRIVATE_OWNER_ACTIVE_RUNNER_UNIVERSE_MISMATCH:"+owner)
        if engine is None or params is None:
            raise ValueError("FNB_PRIVATE_DUAL_KRS_ENGINE_AND_MAP_REQUIRED")
        downstream=dual_krs_execute(inputs=owners,engine=Path(engine),
                 params=Path(params),private_output=root,public_repo=public_repo,
                 race_id=race_id,cutoff_at=request["prediction_cutoff"],
                 diagnostic_only=diagnostic_only,now=now)
        status="NUMERIC_AND_TWO_OWNER_KRS_COMPLETE_ROLES_TICKETS_NOT_FORMED"
        first_failure="W_P2_P3_MEC_SIX_TICKET_METHODS_NOT_EXECUTED"
    ticket_grade=None
    ticket_tree_sha=None
    constructed=None
    if frozen_semantics is not None:
        if downstream is None or portfolios is not None:
            raise ValueError("FNB_R17_FROZEN_SEMANTICS_REQUIRES_KRS_AND_NO_OTHER_PORTFOLIO")
        from runtime.local_fnb_r17_method_constructor import construct
        frozen_krs_path=folder/"private_dual_krs_receipt.json"
        if not frozen_krs_path.is_file():
            raise ValueError("FNB_R17_ACTUAL_BOTH_OWNER_KRS_RECEIPT_MISSING")
        krs_proof=json.loads(frozen_krs_path.read_text(encoding="utf-8"))
        constructed=construct(
            race_id=race_id,owner_semantics=frozen_semantics,private_root=root,
            dual_krs_manifest=krs_proof,
            source_snapshot_sha256=source.get("source_snapshot_sha256"),
            numerical_materialization_sha256=num["private_materialization_sha256"])
        portfolios=constructed["owners"]
    if portfolios is not None:
        if downstream is None:
            raise ValueError("FNB_TICKETS_WITHOUT_TWO_OWNER_KRS_FORBIDDEN")
        from runtime.local_fnb_r9_method_audit import audit_methods
        ticket_grade=audit_methods(portfolios)
        if not ticket_grade["complete"]:
            raise ValueError("FNB_SIX_ALTERNATIVE_METHOD_TREES_FAILED:"+",".join(
                ticket_grade["failures"][:6]))
        text_lines=["# 船橋 B／C各3方式｜私有独立券面・購入は未実施",
                    "この検収は既に作られた券面の正規表示であり、予測生成・本人ACKではありません。",""]
        for name in ("BASELINE","CANDIDATE"):
            text_lines.append("## "+name+"（他Ownerとは別の代替券面）")
            for method in ("EXACTA","TRIO","TRIFECTA"):
                v=portfolios[name][method]
                text_lines.append("### "+method+"／"+str(v["point_count"])+
                    "点／"+str(v["total_investment"])+"円／未使用"+
                    str(v["unused_capital"])+"円")
                if v["no_bet"]:
                    text_lines.append("計算済みNO-BET："+v["reason"])
                else:
                    text_lines.append(v["canonical_tree"])
                text_lines.append("")
        text_bytes=("\n".join(text_lines)+"\n").encode("utf-8")
        ticket_tree_sha=_atomic_private_write(
            folder/"baseline_candidate_6methods_alternative_trees.md",text_bytes)
        status="NUMERIC_KRS_SIX_ALTERNATIVE_TREES_STRUCTURED_DELIVERY_UNPROVEN"
        first_failure="SIGNED_FORMAL_ROLE_SEMANTIC_AND_RECIPIENT_ACK_NOT_PROVEN"
    full_delivery=None
    full_delivery_hold=None
    if constructed is not None:
        from runtime.local_fnb_r18_full_private_delivery import verified_full_delivery
        try:
            full_delivery=verified_full_delivery(
                race_id=race_id,private_root=root,
                semantics=frozen_semantics,portfolios=portfolios,
                diagnostic_only=diagnostic_only)
            status="FULL_PRIVATE_PRESENTATION_READY_DELIVERY_ACK_UNVERIFIED"
            first_failure="ACTUAL_RECIPIENT_ACK_OR_FORMAL_SIGNATURE_NOT_PROVEN"
        except ValueError as exc:
            full_delivery_hold=str(exc).split(":")[0]
            status="SIX_TREES_EXIST_FULL_DELIVERY_CONTENT_HOLD"
            first_failure=full_delivery_hold
    # Persist the exact inputs needed to reproduce the full presentation.
    # Boolean checkpoint fields alone cannot attest that horse cells or
    # selected tickets were actually present in the saved body.
    presentation_artifacts=None
    if full_delivery is not None:
        _atomic_private_write(folder/"frozen_owner_semantics.json",_encoded(frozen_semantics))
        _atomic_private_write(folder/"six_alternative_method_portfolios.json",_encoded(portfolios))
        names=["numerical_materialization.json","private_dual_krs_receipt.json",
               "frozen_owner_semantics.json","six_alternative_method_portfolios.json"]
        names += [owner+suffix for owner in ("BASELINE","CANDIDATE")
                  for suffix in ("_krs_input.json","_krs_output.json")]
        presentation_artifacts={name:hashlib.sha256((folder/name).read_bytes()).hexdigest()
                                for name in names}
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
      "existing_six_method_ticket_tree_audit":ticket_grade,
      "frozen_mec_six_method_generator_proven":constructed is not None,
      "frozen_mec_source_and_owner_receipts":(
          constructed["plan_evidence"] if constructed is not None else None),
      "six_method_rendered_private_tree_sha256":ticket_tree_sha,
      "complete_private_full_horse_delivery_presentation":full_delivery,
      "presentation_artifact_sha256":presentation_artifacts,
      "full_presentation_first_missing_field":full_delivery_hold,
      "model_w_p2_p3_decision_proven":False,
      "owner_six_methods_proven":ticket_grade is not None and ticket_grade["complete"],
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
        "six_alternative_method_trees_rendered":ticket_tree_sha is not None,
        "complete_all_horse_29_index_dual_owner_six_method_body_sha256":(
            full_delivery["full_body_sha256"] if full_delivery else None),
        "complete_presentation_content_verified":full_delivery is not None,
        "formal_final_or_delivery_done":False,
        "private_checkpoint_readback_verified":
            hashlib.sha256((folder/"private_pipeline_checkpoint.json").read_bytes()).hexdigest()==sha,
        "registered_oos_increment":0}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    source_group=p.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--source-artifact")
    source_group.add_argument("--private-browser-html")
    for flag in ("request","private-root"):
        p.add_argument("--"+flag,required=True)
    p.add_argument("--browser-original-url")
    p.add_argument("--browser-captured-at")
    for flag in ("baseline-owner","candidate-owner","engine","params"):
        p.add_argument("--"+flag)
    p.add_argument("--baseline-frozen-semantics")
    p.add_argument("--candidate-frozen-semantics")
    p.add_argument("--owner-method-portfolios")
    p.add_argument("--diagnostic-only",action="store_true")
    p.add_argument("--emit-full-private-body",action="store_true",
        help="Explicitly print verified complete B/C full body only in private non-CI Work actor")
    args=p.parse_args(argv)
    owner_files=[args.baseline_owner,args.candidate_owner]
    if any(owner_files) and not all(owner_files):
        raise ValueError("BOTH_OWNER_PACKETS_REQUIRED_NOT_ONE")
    if bool(args.baseline_frozen_semantics)!=bool(args.candidate_frozen_semantics):
        raise ValueError("BOTH_FROZEN_OWNER_SEMANTIC_SNAPSHOTS_REQUIRED")
    owner_data={"BASELINE":json.loads(Path(owner_files[0]).read_text()),
                "CANDIDATE":json.loads(Path(owner_files[1]).read_text())} if all(owner_files) else None
    request=json.loads(Path(args.request).read_text())
    browser_capture=None
    if args.private_browser_html:
        if not args.browser_original_url or not args.browser_captured_at:
            raise ValueError("FNB_BROWSER_HTML_EXACT_URL_AND_CAPTURE_TIME_REQUIRED")
        from runtime.local_fnb_r16_private_browser_capture import ingest
        browser_capture=ingest(
            html_path=Path(args.private_browser_html),request=request,
            observed_url=args.browser_original_url,
            capture_time=args.browser_captured_at,
            private_output=Path(args.private_root),
            public_repo=Path(__file__).resolve().parents[1],
            diagnostic_only=args.diagnostic_only)
        private_source=Path(args.private_root)/request["race_id"]/"unsigned_official_card_artifact.json"
        source=json.loads(private_source.read_text(encoding="utf-8"))
    else:
        source=json.loads(Path(args.source_artifact).read_text(encoding="utf-8"))
        if isinstance(source,dict) and "artifact" in source and "receipt" in source:
            source=source["artifact"]
    receipt=run(source=source,request=request,root=Path(args.private_root),
        public_repo=Path(__file__).resolve().parents[1],
        owners=owner_data,
        portfolios=(json.loads(Path(args.owner_method_portfolios).read_text())
            if args.owner_method_portfolios else None),
        frozen_semantics=({
            "BASELINE":json.loads(Path(args.baseline_frozen_semantics).read_text()),
            "CANDIDATE":json.loads(Path(args.candidate_frozen_semantics).read_text())}
            if args.baseline_frozen_semantics and args.candidate_frozen_semantics
            else None),
        engine=Path(args.engine) if args.engine else None,
        params=Path(args.params) if args.params else None,
        diagnostic_only=args.diagnostic_only)
    if browser_capture is not None:
        receipt["private_official_browser_import_sha256"]=browser_capture["source_artifact_sha256"]
        receipt["private_official_browser_source_signed"]=False
    if args.emit_full_private_body:
        import os
        if os.environ.get("GITHUB_ACTIONS")=="true" or os.environ.get("CI")=="true":
            raise ValueError("FNB_PRIVATE_HORSE_OR_TICKET_BODY_PUBLIC_CI_LOG_FORBIDDEN")
        name=receipt.get("complete_all_horse_29_index_dual_owner_six_method_body_sha256")
        if not receipt.get("complete_presentation_content_verified") or not name:
            raise ValueError("FNB_COMPLETE_SIX_METHOD_PRIVATE_DELIVERY_BODY_NOT_READY")
        body_file=Path(args.private_root).resolve()/request["race_id"]/"FULL_ALL_HORSES_BC_SIX_METHODS.md"
        data=body_file.read_bytes()
        if hashlib.sha256(data).hexdigest()!=name:
            raise ValueError("FNB_PRIVATE_COMPLETE_DELIVERY_BODY_BYTES_CHANGED")
        # This is an intentional private user-visible renderer, never a
        # public Actions artifact, external delivery or recipient ACK.
        print(data.decode("utf-8"))
    else:
        print(json.dumps(receipt,ensure_ascii=False,sort_keys=True))
    return 0


if __name__=="__main__":raise SystemExit(main())

