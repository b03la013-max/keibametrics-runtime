"""Single-call FNB chat → private verified 29-index/KRS/six-method ticket completion.

This is an executable bridge, not an independent data provider or a model.
It accepts ONE pre-existing private Work bundle with official captured Raw,
the *separately frozen* fixed B/C owner KRS and semantic model packets, and
the exact existing KRS engine/map. It invokes R14→R17→R18, then R19 readback.

No placeholder tickets, no synthetic owner policy, no NAR access bypass, no
Production scope permission, no signing, no OOS registration or real purchase.
A private Work actor must acquire and persist lawful original source/model
packets before the cutoff. No full packet: explicit HOLD, not NO-BET.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import re
from pathlib import Path

from runtime.local_fnb_r19_chat_readback import parse_intent, readback
from runtime.local_fnb_r14_private_dual_krs import ENGINE_SHA, MAP_SHA

PROFILE="KM-FNB-R20-CHAT-PRIVATE-ONE-TRIGGER-SIX-METHODS-v1"
CLASSIFICATION="SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS"

def _hold(intent, stage, code):
    return {"profile":PROFILE,"status":"EXECUTION_HOLD_NOT_NO_BET",
            "intent":intent,"first_failed_stage":stage,"reason":code,
            "six_method_ticket_delivery_proven":False,
            "recipient_delivery_ack":False,"actual_purchase":False,
            "registered_oos_increment":0}

def _read_file(root, spec, label):
    if not isinstance(spec,dict) or set(spec)!={"path","sha256"}:
        raise ValueError("FNB_R20_"+label+"_PATH_AND_SHA_REQUIRED")
    name=spec["path"]
    expected=spec["sha256"]
    if not isinstance(name,str) or not name or not isinstance(expected,str) or len(expected)!=64:
        raise ValueError("FNB_R20_"+label+"_REF_INVALID")
    p=(root/name).resolve() if not Path(name).is_absolute() else Path(name).resolve()
    if p!=root and root not in p.parents:
        raise ValueError("FNB_R20_"+label+"_NOT_IN_PRIVATE_ROOT")
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
        raise ValueError("FNB_R20_"+label+"_BYTES_MISSING_OR_SHA_MISMATCH")
    return p

def _load_json(root, spec, label):
    p=_read_file(root,spec,label)
    try:return json.loads(p.read_bytes())
    except (ValueError,UnicodeError) as exc:
        raise ValueError("FNB_R20_"+label+"_INVALID_JSON") from exc

def _asset_path(spec, expected_sha, label):
    if not isinstance(spec,dict) or not isinstance(spec.get("path"),str):
        raise ValueError("FNB_R20_"+label+"_PATH_MISSING")
    p=Path(spec["path"]).resolve()
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected_sha:
        raise ValueError("FNB_R20_"+label+"_CURRENT_FROZEN_SHA_MISMATCH")
    return p

def complete(query, private_root, *, now=None, diagnostic_only=False, emit_private_body=False):
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("FNB_R20_AWARE_NOW_REQUIRED")
    intent=parse_intent(query,now)
    root=Path(private_root).resolve()
    public_repo=Path(__file__).resolve().parents[1]
    if root==public_repo or public_repo in root.parents:
        return _hold(intent,"PRIVATE_STORE","PUBLIC_REPOSITORY_FORBIDDEN_FOR_HORSE_DATA")
    if emit_private_body and (os.environ.get("CI")=="true" or os.environ.get("GITHUB_ACTIONS")=="true"):
        return _hold(intent,"PRIVATE_DELIVERY","PRIVATE_HORSE_OR_TICKET_BODY_PUBLIC_CI_FORBIDDEN")
    existing=readback(query,root,now)
    # Never re-run or silently replace a complete immutable original.
    if existing["status"]=="VERIFIED_FROZEN_PRIVATE_BODY_READY_TO_RENDER":
        return {"profile":PROFILE,**existing,"source":"EXISTING_COMPLETE_ORIGINAL_READBACK",
                "new_prediction_executed":False}
    if existing.get("first_failed_stage") in ("REVISION","BODY_BYTES","CONTENT"):
        return _hold(intent,existing["first_failed_stage"],existing["reason"])
    name=f"FNB_{intent['race_date']}_R{intent['race_no']:02d}_private_bundle.json"
    manifest_path=root/"inbox"/name
    if not manifest_path.is_file():
        return _hold(intent,"WORK_INPUT","PRIVATE_WORK_BUNDLE_NOT_PREPARED")
    try:
        bundle=json.loads(manifest_path.read_bytes())
        if (bundle.get("venue_id")!="FNB" or bundle.get("race_date")!=intent["race_date"]
                or bundle.get("race_no")!=intent["race_no"]
                or bundle.get("classification")!=CLASSIFICATION):
            raise ValueError("FNB_R20_PRIVATE_BUNDLE_SCOPE_OR_RACE_MISMATCH")
        request=_load_json(root,bundle.get("request"),"REQUEST")
        race_id=request.get("race_id")
        prefix=f"KM-LOCAL-FNB-{intent['race_date'].replace('-','')}-R{intent['race_no']:02d}"
        if (not isinstance(race_id,str) or not re.fullmatch(re.escape(prefix)+r"(?:-[A-Za-z0-9_]+)*",race_id)
                or request.get("venue_id")!="FNB"
                or request.get("race_date")!=intent["race_date"]
                or request.get("race_no")!=intent["race_no"]):
            raise ValueError("FNB_R20_REQUEST_RACE_IDENTITY_MISMATCH")
        cutoff=datetime.fromisoformat(request["prediction_cutoff"].replace("Z","+00:00"))
        if cutoff.tzinfo is None:
            raise ValueError("FNB_R20_UNVERIFIED_CUTOFF_TIMEZONE")
        if now>=cutoff and not diagnostic_only:
            return _hold(intent,"TIME","PRESTART_CUTOFF_EXPIRED_DIAGNOSTIC_REQUIRED")
        if request.get("family_id")!="LOCAL":
            raise ValueError("FNB_R20_LOCAL_ONLY")
        sources=[k for k in ("source","private_browser_html") if k in bundle]
        if len(sources)!=1:
            raise ValueError("FNB_R20_ONE_OFFICIAL_SOURCE_INPUT_REQUIRED")
        owners=bundle.get("owners")
        if not isinstance(owners,dict) or set(owners)!={"BASELINE","CANDIDATE"}:
            raise ValueError("FNB_R20_BOTH_FIXED_OWNER_PACKETS_NOT_FROZEN")
        owner_inputs={x:_load_json(root,owners[x].get("krs"),x+"_FROZEN_KRS")
                      for x in ("BASELINE","CANDIDATE")}
        semantics={x:_load_json(root,owners[x].get("semantics"),x+"_FROZEN_SEMANTIC")
                   for x in ("BASELINE","CANDIDATE")}
        if owner_inputs["BASELINE"].get("original_prediction_sha256")==owner_inputs["CANDIDATE"].get("original_prediction_sha256"):
            raise ValueError("FNB_R20_IDENTICAL_BASELINE_CANDIDATE_MODEL_FORBIDDEN")
        if any(semantics[x].get("original_prediction_sha256")!=owner_inputs[x].get("original_prediction_sha256")
               for x in ("BASELINE","CANDIDATE")):
            raise ValueError("FNB_R20_OWNER_SEMANTIC_KRS_MODEL_FREEZE_MISMATCH")
        if sources[0]=="source":
            source=_load_json(root,bundle["source"],"SOURCE")
            if isinstance(source,dict) and "artifact" in source and "receipt" in source:
                source=source["artifact"]
        else:
            from runtime.local_fnb_r16_private_browser_capture import ingest
            captured=_read_file(root,bundle["private_browser_html"],"ORIGINAL_HTML")
            url=bundle.get("browser_original_url")
            captured_at=bundle.get("browser_captured_at")
            if not isinstance(url,str) or not isinstance(captured_at,str):
                raise ValueError("FNB_R20_ORIGINAL_BROWSER_URL_AND_TIME_REQUIRED")
            ingest(html_path=captured,request=request,observed_url=url,
                   capture_time=captured_at,private_output=root,
                   public_repo=public_repo,diagnostic_only=diagnostic_only)
            source=json.loads((root/race_id/"unsigned_official_card_artifact.json").read_bytes())
        # Verify source identity/immutable bytes before even resolving executable assets.
        engine=_asset_path(bundle.get("engine"),ENGINE_SHA,"ENGINE")
        params=_asset_path(bundle.get("params"),MAP_SHA,"MAP")
        from runtime.local_fnb_r14_private_work_entry import run
        run(source=source,request=request,root=root,public_repo=public_repo,
            owners=owner_inputs,frozen_semantics=semantics,
            engine=engine,params=params,now=now,diagnostic_only=diagnostic_only)
        complete_original=readback(query,root,now)
        if complete_original["status"]!="VERIFIED_FROZEN_PRIVATE_BODY_READY_TO_RENDER":
            return _hold(intent,"DELIVERY_BODY",complete_original.get("reason","VERIFIED_FULL_BODY_MISSING"))
        return {"profile":PROFILE,**complete_original,"source":"NEW_PRIVATE_COMPLETE_EXECUTION",
                "new_prediction_executed":True}
    except (ValueError, OSError, KeyError, TypeError) as exc:
        # Never turn computation failure into a computed 0-ticket NO-BET.
        return _hold(intent,"SOURCE_TO_SIX_METHOD",str(exc).split(":")[0])

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--query",required=True)
    p.add_argument("--private-root",required=True)
    p.add_argument("--diagnostic-only",action="store_true")
    p.add_argument("--emit-private-full-body",action="store_true")
    args=p.parse_args(argv)
    result=complete(args.query,Path(args.private_root),
                    diagnostic_only=args.diagnostic_only,
                    emit_private_body=args.emit_private_full_body)
    if args.emit_private_full_body and result["status"]=="VERIFIED_FROZEN_PRIVATE_BODY_READY_TO_RENDER":
        print(result["body"],end="")
    else:
        print(json.dumps({k:v for k,v in result.items() if k!="body"},
                         ensure_ascii=False,sort_keys=True))
    return 0 if result["status"]=="VERIFIED_FROZEN_PRIVATE_BODY_READY_TO_RENDER" else 2

if __name__=="__main__":
    raise SystemExit(main())
