from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Dict

PROFILE = "KM-JRA-LOCAL-MATURITY-IMPORT-20261003-R1"

NONSEMANTIC_KEYS = {
    "execution_attempt","retry_reason","retry_repair_sha","execution_mode",
    "single_entry","execution_phase","phase","jra_single_entry",
    "jra_maturity_bridge","entry_transport_fallback","transport_metadata",
    "formal_semantic_basis_sha256",
}

SOURCE_REQUIRED = (
    "family_id","race_id","venue_id","race_date","race_no",
    "prediction_cutoff","scheduled_post_at",
)

class JRAMaturityBridgeError(ValueError):
    pass

def _canon(obj: Any) -> bytes:
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")

def _sha(obj: Any) -> str:
    return hashlib.sha256(_canon(obj)).hexdigest()

def _load(path: str | Path) -> Dict[str,Any]:
    obj=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(obj,dict):
        raise JRAMaturityBridgeError("OBJECT_REQUIRED")
    return obj

def _family(req: Dict[str,Any]) -> str:
    return str(req.get("family_id") or "").upper()

def _execution_id(intent: Dict[str,Any]) -> str:
    explicit=str(intent.get("execution_id") or "").strip()
    if explicit:
        return explicit
    race_id=str(intent.get("race_id") or "").strip()
    if not race_id:
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_RACE_ID_REQUIRED")
    return race_id+"-SINGLE-R1"

def _require_jra(intent: Dict[str,Any]) -> None:
    if _family(intent)!="JRA":
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_JRA_ONLY")
    missing=[k for k in SOURCE_REQUIRED if intent.get(k) in (None,"")]
    if missing:
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_REQUIRED_MISSING:"+",".join(missing))

def semantic_payload(req: Dict[str,Any]) -> Dict[str,Any]:
    return {
        k:copy.deepcopy(v) for k,v in req.items()
        if k not in NONSEMANTIC_KEYS
    }

def semantic_sha256(req: Dict[str,Any]) -> str:
    return _sha(semantic_payload(req))

def build_source_request(intent: Dict[str,Any]) -> Dict[str,Any]:
    _require_jra(intent)
    cfg=intent.get("jra_source") if isinstance(intent.get("jra_source"),dict) else {}
    meeting_key=str(cfg.get("jra_meeting_key") or intent.get("jra_meeting_key") or "").strip()
    if not meeting_key:
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_MEETING_KEY_REQUIRED")
    out={
        "family_id":"JRA",
        "race_id":intent["race_id"],
        "execution_id":_execution_id(intent),
        "venue_id":intent["venue_id"],
        "race_date":intent["race_date"],
        "race_no":intent["race_no"],
        "jra_meeting_key":meeting_key,
        "temporal_mode":str(intent.get("temporal_mode") or "FORMAL-PRE-RACE"),
        "prediction_cutoff":intent["prediction_cutoff"],
        "scheduled_post_at":intent["scheduled_post_at"],
        "external_dispatch_deadline_at":(
            intent.get("external_dispatch_deadline_at")
            or intent.get("release_deadline_at")
        ),
        "require_jra_race_card_detail":bool(cfg.get("require_jra_race_card_detail",True)),
        "require_jra_horse_history":bool(cfg.get("require_jra_horse_history",True)),
        "require_jra_person_stats":bool(cfg.get("require_jra_person_stats",True)),
        "require_registered_common_workout":bool(cfg.get("require_registered_common_workout",True)),
        "require_jma_weather":bool(cfg.get("require_jma_weather",True)),
        "require_tsl_shadow":bool(cfg.get("require_tsl_shadow",False)),
        "jra_single_entry_profile":PROFILE,
    }
    if not out["external_dispatch_deadline_at"]:
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_DISPATCH_DEADLINE_REQUIRED")
    return out

def source_checkpoint_manifest(source_env: Dict[str,Any], source_execution_id: str) -> Dict[str,Any]:
    artifact=source_env.get("artifact") if isinstance(source_env.get("artifact"),dict) else {}
    receipt=source_env.get("receipt") if isinstance(source_env.get("receipt"),dict) else {}
    manifest={
        "source_execution_id":str(source_execution_id),
        "receipt_sha256":str(source_env.get("receipt_sha256") or ""),
        "source_snapshot_sha256":str(artifact.get("source_snapshot_sha256") or ""),
        "race_id":str(artifact.get("race_id") or ""),
        "prediction_cutoff":str(artifact.get("prediction_cutoff") or ""),
        "source_freeze_at":str(artifact.get("source_freeze_at") or ""),
        "runtime_revision":str(receipt.get("runtime_revision") or ""),
    }
    missing=[k for k,v in manifest.items() if not str(v).strip()]
    if missing:
        raise JRAMaturityBridgeError("JRA_SOURCE_CHECKPOINT_INCOMPLETE:"+",".join(missing))
    manifest["sha256"]=_sha(manifest)
    return manifest

def build_formal_request(
    intent: Dict[str,Any],
    source_env: Dict[str,Any],
    *,
    source_execution_id: str|None=None,
) -> Dict[str,Any]:
    _require_jra(intent)
    source_execution_id=str(source_execution_id or _execution_id(intent)).strip()
    checkpoint=source_checkpoint_manifest(source_env,source_execution_id)
    artifact=source_env.get("artifact") or {}
    if str(artifact.get("race_id") or "")!=str(intent.get("race_id") or ""):
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_SOURCE_RACE_MISMATCH")
    if str(artifact.get("prediction_cutoff") or "")!=str(intent.get("prediction_cutoff") or ""):
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_SOURCE_CUTOFF_MISMATCH")

    out=copy.deepcopy(intent)
    out.pop("jra_source",None)
    out["family_id"]="JRA"
    out["execution_id"]=_execution_id(intent)
    out["source_execution_id"]=source_execution_id
    out["temporal_mode"]=str(out.get("temporal_mode") or "FORMAL-PRE-RACE")
    out["static_prediction_frozen"]=bool(out.get("static_prediction_frozen"))
    static=out.get("static_prediction")
    if not isinstance(static,dict):
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_STATIC_PREDICTION_REQUIRED")
    if out["static_prediction_frozen"] is not True:
        raise JRAMaturityBridgeError("JRA_SINGLE_ENTRY_STATIC_FREEZE_REQUIRED")
    static=copy.deepcopy(static)
    static["source_basis_receipt_sha256"]=checkpoint["receipt_sha256"]
    static["source_basis_snapshot_sha256"]=checkpoint["source_snapshot_sha256"]
    static["source_checkpoint_manifest_sha256"]=checkpoint["sha256"]
    out["static_prediction"]=static
    out["source_checkpoint_manifest"]=checkpoint
    out["jra_maturity_bridge"]={
        "profile":PROFILE,
        "origin_family":"LOCAL",
        "target_family":"JRA",
        "promotion_class":"C0_SCHEMA_INTERFACE + C1_EXECUTION_CORRECTNESS",
        "imported_mechanisms":[
            "SINGLE_ENTRY_CONTINUATION",
            "STABLE_EXECUTION_ID",
            "DURABLE_SOURCE_CHECKPOINT_REUSE",
            "STATIC_SIGNED_SOURCE_BINDING",
            "FORMAL_SEMANTIC_BASIS",
            "FAIL_CLOSED_RESUME_DIAGNOSTICS",
            "ENTRY_TRANSPORT_SEMANTIC_HASH",
            "FAST_POSTRESULT_REFLECTION",
        ],
        "excluded_cross_family_material":[
            "LOCAL_SOURCE_ADAPTER",
            "LOCAL_EVIDENCE_RULES",
            "LOCAL_NUMERICAL_MAPPING",
            "LOCAL_PARAMETER_MAP",
            "LOCAL_PREDICTION_COEFFICIENTS",
            "LOCAL_VENUE_MECHANISMS",
            "LOCAL_MEC_R5_PRODUCTION_AUTHORITY",
        ],
        "production_prediction_change":False,
        "production_numerical_change":False,
        "krs_physics_change":False,
        "mec_r3_change":False,
        "capital_policy_change":False,
        "automatic_promotion":False,
    }
    out["formal_semantic_basis_sha256"]=semantic_sha256(out)
    return out

def verify_formal_request_binding(req: Dict[str,Any], source_env: Dict[str,Any]) -> Dict[str,Any]:
    _require_jra(req)
    meta=req.get("jra_maturity_bridge")
    if not isinstance(meta,dict):
        return {"profile":PROFILE,"status":"NOT_APPLICABLE"}
    if meta.get("profile")!=PROFILE:
        raise JRAMaturityBridgeError("JRA_MATURITY_PROFILE_MISMATCH")
    source_execution_id=str(req.get("source_execution_id") or "").strip()
    if not source_execution_id:
        raise JRAMaturityBridgeError("JRA_MATURITY_SOURCE_EXECUTION_ID_REQUIRED")
    checkpoint=source_checkpoint_manifest(source_env,source_execution_id)
    static=req.get("static_prediction")
    if not isinstance(static,dict):
        raise JRAMaturityBridgeError("JRA_MATURITY_STATIC_REQUIRED")
    expected={
        "source_basis_receipt_sha256":checkpoint["receipt_sha256"],
        "source_basis_snapshot_sha256":checkpoint["source_snapshot_sha256"],
        "source_checkpoint_manifest_sha256":checkpoint["sha256"],
    }
    for k,v in expected.items():
        if str(static.get(k) or "")!=str(v):
            raise JRAMaturityBridgeError(f"JRA_MATURITY_STATIC_SOURCE_BINDING_MISMATCH:{k}")
    declared=str(req.get("formal_semantic_basis_sha256") or "")
    actual=semantic_sha256(req)
    if not declared or declared!=actual:
        raise JRAMaturityBridgeError(
            f"JRA_MATURITY_FORMAL_SEMANTIC_HASH_MISMATCH:{declared}!={actual}"
        )
    if meta.get("production_prediction_change") is not False:
        raise JRAMaturityBridgeError("JRA_MATURITY_PREDICTION_CHANGE_FORBIDDEN")
    if meta.get("production_numerical_change") is not False:
        raise JRAMaturityBridgeError("JRA_MATURITY_NUMERICAL_CHANGE_FORBIDDEN")
    return {
        "profile":PROFILE,
        "status":"PASS",
        "source_execution_id":source_execution_id,
        "source_checkpoint_manifest_sha256":checkpoint["sha256"],
        "formal_semantic_basis_sha256":actual,
        "production_effect":"NONE",
    }

def main() -> int:
    p=argparse.ArgumentParser()
    sp=p.add_subparsers(dest="cmd",required=True)

    s=sp.add_parser("build-source")
    s.add_argument("--intent",required=True)
    s.add_argument("--output",required=True)

    f=sp.add_parser("build-formal")
    f.add_argument("--intent",required=True)
    f.add_argument("--source-envelope",required=True)
    f.add_argument("--source-execution-id")
    f.add_argument("--output",required=True)

    v=sp.add_parser("verify-formal")
    v.add_argument("--request",required=True)
    v.add_argument("--source-envelope",required=True)
    v.add_argument("--output")

    args=p.parse_args()
    if args.cmd=="build-source":
        out=build_source_request(_load(args.intent))
    elif args.cmd=="build-formal":
        out=build_formal_request(
            _load(args.intent),_load(args.source_envelope),
            source_execution_id=args.source_execution_id
        )
    else:
        out=verify_formal_request_binding(_load(args.request),_load(args.source_envelope))
    if getattr(args,"output",None):
        q=Path(args.output); q.parent.mkdir(parents=True,exist_ok=True)
        q.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
