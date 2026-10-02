from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Dict

MULTI_PROFILE = "KM-FAMILY-ENTRY-TRANSPORT-FALLBACK-MULTI-20261003"

FAMILY_FALLBACK = {
    "LOCAL": {
        "profile": "KM-FAMILY-ENTRY-TRANSPORT-FALLBACK-20261001-R1",
        "root": "runtime/family_requests",
        "workflow": ".github/workflows/km-family-non-jra-formal-runner.yml",
        "primary_root": "runtime/formal_intents",
    },
    "JRA": {
        "profile": "KM-FAMILY-ENTRY-TRANSPORT-FALLBACK-20261003-R2",
        "root": "runtime/requests",
        "workflow": ".github/workflows/km-formal-request-runner.yml",
        "primary_root": "runtime/jra_formal_intents",
    },
}

SEMANTIC_FIELDS = (
    "race_id", "family_id", "venue_id", "race_date", "race_no",
    "prediction_cutoff", "scheduled_post_at", "release_deadline_at",
    "external_dispatch_deadline_at", "source_execution_id",
    "runners", "required_indices", "run_count", "seed",
    "static_prediction_frozen", "static_prediction", "final_prediction_package",
    "role_registry", "pair_dispositions", "third_dispositions",
    "available_bet_types", "capital_policy", "oos_policy",
)

class EntryTransportFallbackError(ValueError):
    pass

def _canon(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def semantic_payload(req: Dict[str, Any]) -> Dict[str, Any]:
    return {k: copy.deepcopy(req.get(k)) for k in SEMANTIC_FIELDS if k in req}

def semantic_sha256(req: Dict[str, Any]) -> str:
    return hashlib.sha256(_canon(semantic_payload(req)).encode("utf-8")).hexdigest()

def _family_cfg(req: Dict[str,Any]) -> tuple[str,Dict[str,str]]:
    family=str(req.get("family_id") or "").upper()
    cfg=FAMILY_FALLBACK.get(family)
    if not cfg:
        raise EntryTransportFallbackError("ENTRY_FALLBACK_FAMILY_UNSUPPORTED")
    return family,cfg

def build_legacy_formal_request(
    intent: Dict[str, Any],
    *,
    primary_failure_code: str = "PRIMARY_ENTRY_TRANSPORT_FAILURE",
) -> Dict[str, Any]:
    family,cfg=_family_cfg(intent)
    execution_id = str(intent.get("execution_id") or "").strip()
    if not execution_id:
        raise EntryTransportFallbackError("ENTRY_FALLBACK_EXPLICIT_EXECUTION_ID_REQUIRED")
    if family=="JRA" and not str(intent.get("source_execution_id") or "").strip():
        raise EntryTransportFallbackError("ENTRY_FALLBACK_JRA_SOURCE_EXECUTION_ID_REQUIRED")
    if not isinstance(intent.get("static_prediction"), dict):
        raise EntryTransportFallbackError("ENTRY_FALLBACK_STATIC_PREDICTION_REQUIRED")
    if intent.get("static_prediction_frozen") is not True:
        raise EntryTransportFallbackError("ENTRY_FALLBACK_STATIC_FREEZE_REQUIRED")

    out = copy.deepcopy(intent)
    digest = semantic_sha256(intent)
    out["execution_phase"] = "FORMAL"
    out["phase"] = "FORMAL"
    out["execution_mode"] = "ENTRY_TRANSPORT_FALLBACK"
    out["entry_transport_fallback"] = {
        "profile": cfg["profile"],
        "family": family,
        "trigger": "PRIMARY_SINGLE_ENTRY_SUBMISSION_FAILED_BEFORE_COMMIT",
        "primary_failure_code": str(primary_failure_code),
        "primary_root": cfg["primary_root"],
        "fallback_root": cfg["root"],
        "fallback_workflow": cfg["workflow"],
        "same_execution_id_required": True,
        "durable_source_checkpoint_reuse_required": True,
        "semantic_sha256": digest,
        "no_silent_semantic_reduction": True,
        "external_safety_bypass": False,
        "production_prediction_change": False,
        "production_numerical_change": False,
        "krs_change": False,
        "mec_change": False,
        "capital_change": False,
    }
    return out

def validate_fallback_request(req: Dict[str, Any]) -> Dict[str, Any]:
    meta = req.get("entry_transport_fallback")
    if not isinstance(meta, dict):
        return {"profile": MULTI_PROFILE, "status": "NOT_APPLICABLE"}

    family,cfg=_family_cfg(req)
    if str(req.get("execution_phase") or req.get("phase") or "").upper() != "FORMAL":
        raise EntryTransportFallbackError("ENTRY_FALLBACK_FORMAL_PHASE_REQUIRED")
    if not str(req.get("execution_id") or "").strip():
        raise EntryTransportFallbackError("ENTRY_FALLBACK_EXPLICIT_EXECUTION_ID_REQUIRED")
    if family=="JRA" and not str(req.get("source_execution_id") or "").strip():
        raise EntryTransportFallbackError("ENTRY_FALLBACK_JRA_SOURCE_EXECUTION_ID_REQUIRED")
    if not isinstance(req.get("static_prediction"), dict):
        raise EntryTransportFallbackError("ENTRY_FALLBACK_STATIC_PREDICTION_REQUIRED")
    if req.get("static_prediction_frozen") is not True:
        raise EntryTransportFallbackError("ENTRY_FALLBACK_STATIC_FREEZE_REQUIRED")
    if meta.get("external_safety_bypass") is not False:
        raise EntryTransportFallbackError("ENTRY_FALLBACK_SAFETY_BYPASS_FORBIDDEN")
    if meta.get("same_execution_id_required") is not True:
        raise EntryTransportFallbackError("ENTRY_FALLBACK_STABLE_EXECUTION_ID_REQUIRED")
    if meta.get("durable_source_checkpoint_reuse_required") is not True:
        raise EntryTransportFallbackError("ENTRY_FALLBACK_SOURCE_REUSE_REQUIRED")
    if str(meta.get("profile") or "")!=cfg["profile"]:
        raise EntryTransportFallbackError("ENTRY_FALLBACK_PROFILE_MISMATCH")
    if str(meta.get("family") or "")!=family:
        raise EntryTransportFallbackError("ENTRY_FALLBACK_FAMILY_MISMATCH")
    if str(meta.get("fallback_root") or "")!=cfg["root"]:
        raise EntryTransportFallbackError("ENTRY_FALLBACK_ROOT_MISMATCH")
    if str(meta.get("fallback_workflow") or "")!=cfg["workflow"]:
        raise EntryTransportFallbackError("ENTRY_FALLBACK_WORKFLOW_MISMATCH")
    expected = str(meta.get("semantic_sha256") or "").strip()
    actual = semantic_sha256(req)
    if not expected or expected != actual:
        raise EntryTransportFallbackError(
            f"ENTRY_FALLBACK_SEMANTIC_HASH_MISMATCH:{expected}!={actual}"
        )
    return {
        "profile": cfg["profile"],
        "status": "PASS",
        "family": family,
        "execution_id": str(req["execution_id"]),
        "semantic_sha256": actual,
        "fallback_root": cfg["root"],
        "fallback_workflow": cfg["workflow"],
        "source_checkpoint_reuse_required": True,
        "safety_bypass": False,
    }

def main() -> int:
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)
    v = sp.add_parser("validate")
    v.add_argument("--request", required=True)
    v.add_argument("--output")
    args = p.parse_args()
    req = json.loads(Path(args.request).read_text(encoding="utf-8"))
    out = validate_fallback_request(req)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(
            json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2)+"\n",
            encoding="utf-8",
        )
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
