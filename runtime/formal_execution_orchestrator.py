from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time
import re
import base64
import gzip
import unicodedata
import urllib.error
from typing import Any, Dict, Optional

sys.path.insert(0, "runtime")

from execution_gateway import derive_execution_id, load_gateway, result_route, ExecutionGatewayError
from execution_store import ExecutionStoreError, materialize_phase, persist_phase, resolve_phase
from formal_import_closure import FormalImportClosureError, build_closure
from family_authority_guard import load_authority, validate_request_context, verify_execution_completion
from entry_transport_fallback import build_legacy_formal_request, validate_fallback_request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_RUNTIME_OUT = ROOT / "runtime_out"
DEFAULT_TMP_ROOT = ROOT / "runtime" / "orchestrator_tmp"

SUPPORTED_FAMILIES = {"LOCAL"}


def current_single_entry_profile() -> str:
    gateway = load_gateway()
    block = gateway.get("formal_single_entry") if isinstance(gateway, dict) else None
    profile = block.get("profile") if isinstance(block, dict) else None
    if not profile:
        raise FormalOrchestrationError("FORMAL_SINGLE_ENTRY_PROFILE_MISSING_FROM_GATEWAY")
    return str(profile)


class FormalOrchestrationError(RuntimeError):
    pass


RETRYABLE_OFFICIAL_RESULT_CODES = frozenset({
    "OFFICIAL_RESULT_NOT_DUE",
    "OFFICIAL_RESULT_FINISH_TABLE_HOLD",
    "OFFICIAL_RESULT_PAYOUT_NOT_READY",
    "OFFICIAL_RESULT_HTTP_OR_AUTHORITY_HOLD",
    "OFFICIAL_RESULT_PAGE_RACE_IDENTITY_HOLD",
    "OFFICIAL_RESULT_NOT_FINAL",
    "OFFICIAL_RESULT_TRANSPORT_PENDING",
})


def _sha_obj(obj: Any) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _norm_date(value: Any) -> Optional[str]:
    if value is None or str(value).strip() == "":
        return None
    return str(value).strip().replace("/", "-")


def _norm_cutoff(value: Any) -> Optional[str]:
    if value is None or str(value).strip() == "":
        return None
    raw = str(value).strip()
    try:
        return dt.datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(dt.timezone.utc).isoformat()
    except Exception:
        return raw



def _parse_iso(value: Any) -> dt.datetime:
    return dt.datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))


def _static_status_is_explicitly_frozen(static_prediction: Dict[str, Any]) -> bool:
    status = str(static_prediction.get("status") or "").upper()
    tokens = status.replace("/", " ").replace("|", " ").split()
    return any(token == "FROZEN" or token.startswith("FROZEN-") for token in tokens)


FINAL_PREDICTION_STATIC_FIELDS = (
    "ranking",
    "roles",
    "alternative_winner",
    "alternative_winners",
    "partial_order",
    "ties",
    "unresolved",
    "ineligible",
    "uncertainty",
    "evidence_conflict",
    "market_conflict",
    "venue_state",
)


def _derive_final_prediction_package_from_static(static_prediction: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key in FINAL_PREDICTION_STATIC_FIELDS:
        if key in static_prediction:
            out[key] = copy.deepcopy(static_prediction[key])
    if not out.get("ranking"):
        raise FormalOrchestrationError("FINAL_PREDICTION_PACKAGE_DERIVATION_REQUIRES_STATIC_RANKING")
    out["source"] = "CANONICALIZED_FROM_FROZEN_STATIC_SINGLE_ENTRY"
    out["production_prediction_change"] = False
    return out


def normalize_single_entry_intent(intent: Dict[str, Any]) -> tuple[Dict[str, Any], list[Dict[str, Any]]]:
    """Canonicalize redundant execution declarations without changing prediction semantics."""
    out = copy.deepcopy(intent)
    normalizations: list[Dict[str, Any]] = []
    static_prediction = out.get("static_prediction")
    if not isinstance(static_prediction, dict) or not static_prediction:
        raise FormalOrchestrationError("SINGLE_ENTRY_STATIC_PREDICTION_REQUIRED")

    freeze_flag = out.get("static_prediction_frozen")
    explicit_frozen = _static_status_is_explicitly_frozen(static_prediction)
    if freeze_flag is False and explicit_frozen:
        raise FormalOrchestrationError("STATIC_PREDICTION_FREEZE_DECLARATION_CONFLICT")
    if freeze_flag is not True:
        if not explicit_frozen:
            raise FormalOrchestrationError("SINGLE_ENTRY_STATIC_PREDICTION_FREEZE_REQUIRED")
        out["static_prediction_frozen"] = True
        normalizations.append({
            "code": "STATIC_FREEZE_CANONICALIZED_FROM_STATIC_STATUS",
            "source": "static_prediction.status",
            "status": static_prediction.get("status"),
        })

    final_package = out.get("final_prediction_package")
    if final_package is None or final_package == {}:
        out["final_prediction_package"] = _derive_final_prediction_package_from_static(
            static_prediction
        )
        normalizations.append({
            "code": "FINAL_PREDICTION_PACKAGE_CANONICALIZED_FROM_FROZEN_STATIC",
            "source": "static_prediction",
            "ranking_sha256": _sha_obj(static_prediction.get("ranking")),
            "roles_sha256": _sha_obj(static_prediction.get("roles") or {}),
            "production_prediction_change": False,
        })
    elif not isinstance(final_package, dict):
        raise FormalOrchestrationError("FINAL_PREDICTION_PACKAGE_MUST_BE_OBJECT")

    return out, normalizations


def _official_post_from_source(
    request: Dict[str, Any],
    source_resolved: Optional[Dict[str, Any]],
) -> Optional[dt.datetime]:
    if not source_resolved:
        return None
    env = _load_checkpoint_json(source_resolved, "source_receipt_envelope.json")
    if not env:
        return None
    artifact = env.get("artifact") if isinstance(env.get("artifact"), dict) else {}
    evidence = artifact.get("normalized_evidence") if isinstance(artifact.get("normalized_evidence"), dict) else {}
    start = evidence.get("start_time") if isinstance(evidence.get("start_time"), dict) else {}
    start_value = start.get("value")
    if not start_value:
        return None

    race = request.get("race") if isinstance(request.get("race"), dict) else {}
    source_context = artifact.get("source_race_context") if isinstance(artifact.get("source_race_context"), dict) else {}
    race_date = (
        request.get("race_date")
        or race.get("race_date")
        or race.get("date")
        or source_context.get("race_date")
    )
    if not race_date:
        return None
    hh, mm = [int(x) for x in str(start_value).split(":")[:2]]
    local_date = dt.date.fromisoformat(str(race_date).replace("/", "-"))
    jst = dt.timezone(dt.timedelta(hours=9))
    return dt.datetime.combine(local_date, dt.time(hh, mm), tzinfo=jst)


def reconcile_formal_request_with_signed_source(
    request: Dict[str, Any],
    source_resolved: Optional[Dict[str, Any]],
    *,
    max_auto_rebase_seconds: int = 300,
) -> tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """Make signed official SOURCE authoritative for small, temporally safe post-time corrections."""
    out = copy.deepcopy(request)
    if str(out.get("temporal_mode") or "FORMAL-PRE-RACE").upper() != "FORMAL-PRE-RACE":
        return out, None

    official_post = _official_post_from_source(out, source_resolved)
    scheduled = out.get("scheduled_post_at")
    if official_post is None or not scheduled:
        return out, None

    request_post = _parse_iso(scheduled).astimezone(official_post.tzinfo)
    delta_signed = (official_post - request_post).total_seconds()
    delta = abs(delta_signed)
    if delta <= 30:
        return out, None
    if delta > max_auto_rebase_seconds:
        raise FormalOrchestrationError(
            "OFFICIAL_POST_TIME_MISMATCH:"
            + json.dumps({
                "official_post_at": official_post.isoformat(),
                "request_scheduled_post_at": request_post.isoformat(),
                "delta_seconds": delta,
                "max_auto_rebase_seconds": max_auto_rebase_seconds,
            }, ensure_ascii=False, sort_keys=True)
        )

    cutoff = out.get("prediction_cutoff")
    if cutoff and _parse_iso(cutoff).astimezone(official_post.tzinfo) >= official_post:
        raise FormalOrchestrationError("OFFICIAL_POST_TIME_REBASE_VIOLATES_PREDICTION_CUTOFF")

    explicit_deadline = out.get("release_deadline_at")
    if explicit_deadline:
        old_deadline = _parse_iso(explicit_deadline).astimezone(official_post.tzinfo)
        buffer_seconds = max(0, int((request_post - old_deadline).total_seconds()))
    else:
        buffer_seconds = int(out.get("release_buffer_seconds") or 120)
    official_deadline = official_post - dt.timedelta(seconds=buffer_seconds)
    now = dt.datetime.now(dt.timezone.utc)
    if now >= official_deadline.astimezone(dt.timezone.utc):
        raise FormalOrchestrationError("DEADLINE_INSUFFICIENT_AFTER_OFFICIAL_POST_REBASE")

    out["scheduled_post_at"] = official_post.isoformat()
    out["release_deadline_at"] = official_deadline.isoformat()
    reconciliation = {
        "code": "OFFICIAL_POST_TIME_REBASED_FROM_SIGNED_SOURCE",
        "old_scheduled_post_at": request_post.isoformat(),
        "official_scheduled_post_at": official_post.isoformat(),
        "delta_seconds": delta_signed,
        "release_deadline_at": official_deadline.isoformat(),
        "prediction_change": False,
        "numerical_change": False,
    }
    return out, reconciliation


def source_checkpoint_basis(intent: Dict[str, Any]) -> Dict[str, Any]:
    race = intent.get("race") if isinstance(intent.get("race"), dict) else {}
    explicit_manifest = intent.get("required_source_manifest")
    source_request = intent.get("source_acquisition_request")
    explicit_sources = None
    if isinstance(explicit_manifest, list):
        explicit_sources = explicit_manifest
    elif isinstance(source_request, dict) and isinstance(source_request.get("sources"), list):
        explicit_sources = source_request.get("sources")
    return {
        "schema": "KM-SOURCE-CHECKPOINT-BASIS-v1",
        "family_id": str(intent.get("family_id") or "").upper(),
        "race_id": str(intent.get("race_id") or race.get("race_id") or ""),
        "venue_id": str(intent.get("venue_id") or race.get("venue_id") or "") or None,
        "race_date": _norm_date(intent.get("race_date") or race.get("race_date") or race.get("date")),
        "race_no": int(intent.get("race_no") or race.get("race_no") or 0) or None,
        "prediction_cutoff": _norm_cutoff(intent.get("prediction_cutoff") or race.get("prediction_cutoff")),
        "explicit_source_manifest_sha256": _sha_obj(explicit_sources) if explicit_sources is not None else None,
    }


def _load_checkpoint_json(resolved: Dict[str, Any], name: str) -> Optional[Dict[str, Any]]:
    run_dir = resolved.get("run_dir")
    if not isinstance(run_dir, pathlib.Path):
        return None
    path = run_dir / name
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else None


def _legacy_source_basis(resolved: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    env = _load_checkpoint_json(resolved, "source_receipt_envelope.json")
    if not env:
        return None
    receipt = env.get("receipt") if isinstance(env.get("receipt"), dict) else {}
    artifact = env.get("artifact") if isinstance(env.get("artifact"), dict) else {}
    context = artifact.get("source_race_context") if isinstance(artifact.get("source_race_context"), dict) else {}
    return {
        "schema": "KM-SOURCE-CHECKPOINT-BASIS-v1-LEGACY-DERIVED",
        "family_id": str(receipt.get("family") or "").upper(),
        "race_id": str(receipt.get("race_id") or artifact.get("race_id") or ""),
        "venue_id": str(context.get("venue_id") or "") or None,
        "race_date": _norm_date(context.get("race_date")),
        "race_no": int(context.get("race_no") or 0) or None,
        "prediction_cutoff": _norm_cutoff(artifact.get("prediction_cutoff")),
        "explicit_source_manifest_sha256": (
            str(artifact.get("required_source_manifest_sha256") or "") or None
        ),
    }


def source_checkpoint_compatibility(intent: Dict[str, Any], resolved: Dict[str, Any]) -> Dict[str, Any]:
    expected = source_checkpoint_basis(intent)
    actual = _load_checkpoint_json(resolved, "source_checkpoint_basis.json")
    source = "PERSISTED_BASIS"
    if actual is None:
        actual = _legacy_source_basis(resolved)
        source = "LEGACY_SIGNED_SOURCE_DERIVATION"
    if actual is None:
        return {
            "status": "UNVERIFIABLE",
            "basis_source": "NONE",
            "mismatches": {"checkpoint_basis": ["PRESENT", None]},
        }

    mismatches: Dict[str, Any] = {}
    for key in ("family_id", "race_id", "venue_id", "race_date", "race_no", "prediction_cutoff"):
        ev = expected.get(key)
        av = actual.get(key)
        if ev is not None and ev != av:
            mismatches[key] = [ev, av]

    # Compare an explicit request manifest only when the request itself pins one.
    # Auto-discovered manifests are validated by race identity + cutoff and the
    # signed SOURCE receipt instead of guessing their future hash.
    if expected.get("explicit_source_manifest_sha256") is not None:
        if expected["explicit_source_manifest_sha256"] != actual.get("explicit_source_manifest_sha256"):
            mismatches["explicit_source_manifest_sha256"] = [
                expected["explicit_source_manifest_sha256"],
                actual.get("explicit_source_manifest_sha256"),
            ]

    return {
        "status": "PASS" if not mismatches else "INCOMPATIBLE",
        "basis_source": source,
        "expected": expected,
        "actual": actual,
        "mismatches": mismatches,
    }


def validate_temporal_truthfulness(intent: Dict[str, Any]) -> None:
    mode = str(intent.get("temporal_mode") or "FORMAL-PRE-RACE").upper()
    acceptance_mode = str(intent.get("source_adapter_acceptance_mode") or "").upper()
    if bool(intent.get("acceptance_only")) and "ARCHIVED" in acceptance_mode and mode == "FORMAL-PRE-RACE":
        raise FormalOrchestrationError("ARCHIVED_ACCEPTANCE_MUST_USE_POST_START_REPLAY")


FORMAL_RETRY_METADATA_FIELDS = {
    "execution_attempt",
    "retry_reason",
    "retry_repair_sha",
    "execution_mode",
    "single_entry",
    "execution_phase",
    "phase",
}

FORMAL_TRANSPORT_ONLY_FIELDS = {
    "source_receipt_artifact_id",
    "source_run_id",
    "artifact_name",
    "external_endpoint",
    "runtime_expected_revision",
    "source_snapshot_sha256",
    "single_entry_source_binding_required",
    "single_entry_source_checkpoint_manifest_sha256",
    "mandatory_lifecycle_completion_required",
    "source_authoritative_reconciliation",
}


def _formal_semantic_payload(intent: Dict[str, Any]) -> Dict[str, Any]:
    payload = copy.deepcopy(intent)
    for key in FORMAL_RETRY_METADATA_FIELDS | FORMAL_TRANSPORT_ONLY_FIELDS:
        payload.pop(key, None)

    # The exact signed SOURCE is bound separately below. Legacy transport fields
    # may therefore change without redefining the prediction/decision identity.
    payload.pop("source_receipt_sha256", None)

    static = payload.get("static_prediction")
    if isinstance(static, dict):
        static = copy.deepcopy(static)
        static.pop("source_basis_receipt_sha256", None)
        static.pop("source_basis_snapshot_sha256", None)
        static.pop("source_checkpoint_manifest_sha256", None)
        payload["static_prediction"] = static

    # Normalize explicit execution_id rather than letting formatting aliases
    # create a false semantic difference.
    payload["execution_id"] = derive_execution_id(intent)
    return payload


def _source_binding_from_resolved(resolved: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not resolved:
        return None
    env = _load_checkpoint_json(resolved, "source_receipt_envelope.json")
    if not env:
        return None
    artifact = env.get("artifact") if isinstance(env.get("artifact"), dict) else {}
    return {
        "source_checkpoint_manifest_sha256": str((resolved.get("latest") or {}).get("manifest_sha256") or ""),
        "source_run_id": str((resolved.get("manifest") or {}).get("run_id") or ""),
        "source_receipt_sha256": str(env.get("receipt_sha256") or ""),
        "source_snapshot_sha256": str(artifact.get("source_snapshot_sha256") or ""),
    }


def bind_formal_request_to_source(request: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(request)
    execution_id = derive_execution_id(out)
    source_resolved = resolve_phase(execution_id, "SOURCE")
    binding = _source_binding_from_resolved(source_resolved)
    if not binding:
        raise FormalOrchestrationError("SINGLE_ENTRY_SOURCE_BINDING_MISSING")

    out, source_reconciliation = reconcile_formal_request_with_signed_source(
        out, source_resolved
    )
    if source_reconciliation is not None:
        out["source_authoritative_reconciliation"] = source_reconciliation

    receipt_sha = str(binding.get("source_receipt_sha256") or "")
    snapshot_sha = str(binding.get("source_snapshot_sha256") or "")
    manifest_sha = str(binding.get("source_checkpoint_manifest_sha256") or "")
    if not receipt_sha or not snapshot_sha or not manifest_sha:
        raise FormalOrchestrationError("SINGLE_ENTRY_SOURCE_BINDING_INCOMPLETE")

    static = out.get("static_prediction")
    if not isinstance(static, dict):
        raise FormalOrchestrationError("STATIC_PREDICTION_REQUIRED_FOR_SOURCE_BINDING")
    static = copy.deepcopy(static)

    existing_receipt = str(static.get("source_basis_receipt_sha256") or "")
    existing_snapshot = str(static.get("source_basis_snapshot_sha256") or "")
    if existing_receipt and existing_receipt != receipt_sha:
        raise FormalOrchestrationError("STATIC_SOURCE_BASIS_RECEIPT_MISMATCH_BEFORE_FORMAL")
    if existing_snapshot and existing_snapshot != snapshot_sha:
        raise FormalOrchestrationError("STATIC_SOURCE_BASIS_SNAPSHOT_MISMATCH_BEFORE_FORMAL")

    static["source_basis_receipt_sha256"] = receipt_sha
    static["source_basis_snapshot_sha256"] = snapshot_sha
    static["source_checkpoint_manifest_sha256"] = manifest_sha
    out["static_prediction"] = static
    out["source_receipt_sha256"] = receipt_sha
    out["source_snapshot_sha256"] = snapshot_sha
    out["single_entry_source_binding_required"] = True
    out["single_entry_source_checkpoint_manifest_sha256"] = manifest_sha
    return out


def formal_checkpoint_basis(
    intent: Dict[str, Any],
    source_resolved: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    semantic = _formal_semantic_payload(intent)
    source_binding = _source_binding_from_resolved(source_resolved)
    if not source_binding or not source_binding.get("source_receipt_sha256"):
        raise FormalOrchestrationError("FORMAL_BASIS_SOURCE_BINDING_MISSING")
    return {
        "schema": "KM-FORMAL-CHECKPOINT-BASIS-v1",
        "execution_id": derive_execution_id(intent),
        "family_id": str(intent.get("family_id") or "").upper(),
        "race_id": str(intent.get("race_id") or ""),
        "semantic_basis_sha256": _sha_obj(semantic),
        "semantic_components": {
            "static_prediction_sha256": (
                _sha_obj((_formal_semantic_payload(intent).get("static_prediction")))
                if isinstance(intent.get("static_prediction"), dict)
                else None
            ),
            "final_prediction_package_sha256": _sha_obj(intent.get("final_prediction_package")) if isinstance(intent.get("final_prediction_package"), dict) else None,
            "capital_policy_sha256": _sha_obj(intent.get("capital_policy")) if isinstance(intent.get("capital_policy"), dict) else None,
            "local_krs_bridge_sha256": _sha_obj(intent.get("local_krs_bridge")) if isinstance(intent.get("local_krs_bridge"), dict) else None,
            "role_registry_sha256": _sha_obj(intent.get("role_registry")) if isinstance(intent.get("role_registry"), list) else None,
            "pair_dispositions_sha256": _sha_obj(intent.get("pair_dispositions")) if isinstance(intent.get("pair_dispositions"), list) else None,
            "third_dispositions_sha256": _sha_obj(intent.get("third_dispositions")) if isinstance(intent.get("third_dispositions"), list) else None,
            "required_indices_sha256": _sha_obj(intent.get("required_indices") or intent.get("required_index_names") or []),
            "run_count": int(intent.get("run_count") or 0) or None,
            "seed": int(intent.get("seed") or 0) or None,
            "temporal_mode": str(intent.get("temporal_mode") or "FORMAL-PRE-RACE").upper(),
        },
        "source_binding": source_binding,
        "ignored_retry_metadata_fields": sorted(FORMAL_RETRY_METADATA_FIELDS),
        "ignored_transport_only_fields": sorted(FORMAL_TRANSPORT_ONLY_FIELDS | {"source_receipt_sha256"}),
    }


def formal_checkpoint_compatibility(
    intent: Dict[str, Any],
    formal_resolved: Dict[str, Any],
    source_resolved: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    actual = _load_checkpoint_json(formal_resolved, "formal_checkpoint_basis.json")
    if actual is None:
        return {
            "status": "UNBOUND_LEGACY",
            "basis_source": "NONE",
            "mismatches": {"formal_checkpoint_basis": ["PRESENT", None]},
        }
    try:
        expected = formal_checkpoint_basis(intent, source_resolved)
    except FormalOrchestrationError as exc:
        return {
            "status": "UNVERIFIABLE",
            "basis_source": "CURRENT_SOURCE_RESOLUTION_FAILED",
            "mismatches": {"source_binding": ["VERIFIABLE", str(exc)]},
        }

    mismatches: Dict[str, Any] = {}
    if expected.get("semantic_basis_sha256") != actual.get("semantic_basis_sha256"):
        mismatches["semantic_basis_sha256"] = [
            expected.get("semantic_basis_sha256"),
            actual.get("semantic_basis_sha256"),
        ]

    expected_source = expected.get("source_binding") or {}
    actual_source = actual.get("source_binding") or {}
    for key in (
        "source_checkpoint_manifest_sha256",
        "source_receipt_sha256",
        "source_snapshot_sha256",
    ):
        if expected_source.get(key) != actual_source.get(key):
            mismatches["source_binding." + key] = [
                expected_source.get(key),
                actual_source.get(key),
            ]

    return {
        "status": "PASS" if not mismatches else "INCOMPATIBLE",
        "basis_source": "PERSISTED_FORMAL_BASIS",
        "expected": expected,
        "actual": actual,
        "mismatches": mismatches,
    }


def _load(path: str | pathlib.Path) -> Dict[str, Any]:
    with pathlib.Path(path).open(encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise FormalOrchestrationError("FORMAL_INTENT_MUST_BE_OBJECT")
    return value


def _write(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")


def _copy_json_dir(src: pathlib.Path, dst: pathlib.Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)
    if not src.exists():
        return
    for p in src.iterdir():
        if p.is_file() and p.suffix == ".json":
            shutil.copy2(p, dst / p.name)


def _reset_runtime_out(runtime_out: pathlib.Path) -> None:
    if runtime_out.exists():
        shutil.rmtree(runtime_out)
    runtime_out.mkdir(parents=True, exist_ok=True)


def build_phase_request(intent: Dict[str, Any], phase: str) -> Dict[str, Any]:
    family = str(intent.get("family_id") or "").upper()
    if family not in SUPPORTED_FAMILIES:
        raise FormalOrchestrationError(f"SINGLE_ENTRY_FAMILY_NOT_SUPPORTED:{family}")
    out = copy.deepcopy(intent)
    out.pop("execution_mode", None)
    out.pop("single_entry", None)
    out["execution_id"] = derive_execution_id(intent)
    out["execution_phase"] = str(phase).upper()
    out["phase"] = str(phase).upper()
    # "完全フル規格" means full lifecycle, not permission to fabricate
    # unavailable Production numerical authority.
    out.setdefault("require_full_numerical_authority", False)
    if str(phase).upper() == "FORMAL":
        out["mandatory_lifecycle_completion_required"] = True
    return out


def checkpoint_status(execution_id: str, intent: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "execution_id": execution_id,
        "source": {"status": "MISSING"},
        "formal": {"status": "MISSING"},
    }
    source_resolved: Optional[Dict[str, Any]] = None
    for phase in ("SOURCE", "FORMAL"):
        try:
            resolved = resolve_phase(execution_id, phase)
        except ExecutionStoreError as exc:
            out[phase.lower()] = {
                "status": "CORRUPT",
                "error": str(exc),
            }
            continue
        if resolved is None:
            continue
        if phase == "SOURCE":
            source_resolved = resolved
        files = set((resolved.get("manifest") or {}).get("files") or {})
        required = "source_receipt_envelope.json" if phase == "SOURCE" else "final_receipt_envelope.json"
        status = "COMPLETE" if required in files else "INCOMPLETE"
        row = {
            "status": status,
            "run_id": (resolved.get("manifest") or {}).get("run_id"),
            "manifest_sha256": (resolved.get("latest") or {}).get("manifest_sha256"),
            "required_file": required,
            "required_file_present": required in files,
        }
        if phase == "SOURCE" and status == "COMPLETE" and intent is not None:
            compatibility = source_checkpoint_compatibility(intent, resolved)
            row["compatibility"] = compatibility
            if compatibility["status"] != "PASS":
                row["status"] = "INCOMPATIBLE"
        if phase == "FORMAL" and status == "COMPLETE" and intent is not None:
            compatibility = formal_checkpoint_compatibility(intent, resolved, source_resolved)
            row["compatibility"] = compatibility
            if compatibility["status"] == "UNBOUND_LEGACY":
                row["status"] = "UNBOUND_LEGACY"
            elif compatibility["status"] != "PASS":
                row["status"] = "INCOMPATIBLE"
        out[phase.lower()] = row
    return out


def resume_plan(execution_id: str, intent: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    cp = checkpoint_status(execution_id, intent)
    if cp["formal"]["status"] == "CORRUPT":
        action = "FAIL_CLOSED"
        resume_from = "FORMAL_CHECKPOINT_REPAIR_REQUIRED"
    elif cp["formal"]["status"] == "COMPLETE":
        action = "RETURN_IMMUTABLE_FORMAL"
        resume_from = "COMPLETE"
    elif cp["formal"]["status"] == "UNBOUND_LEGACY":
        action = "FAIL_CLOSED"
        resume_from = "NEW_EXECUTION_ID_REQUIRED_FORMAL_LEGACY"
    elif cp["formal"]["status"] == "INCOMPATIBLE":
        action = "FAIL_CLOSED"
        resume_from = "NEW_EXECUTION_ID_REQUIRED_FORMAL_BASIS"
    elif cp["source"]["status"] == "COMPLETE":
        action = "RESUME_FORMAL"
        resume_from = "FORMAL"
    elif cp["source"]["status"] == "CORRUPT":
        action = "FAIL_CLOSED"
        resume_from = "SOURCE_CHECKPOINT_REPAIR_REQUIRED"
    elif cp["source"]["status"] == "INCOMPATIBLE":
        action = "FAIL_CLOSED"
        resume_from = "NEW_EXECUTION_ID_REQUIRED"
    else:
        action = "RUN_SOURCE_THEN_FORMAL"
        resume_from = "SOURCE"
    return {"action": action, "resume_from": resume_from, "checkpoints": cp}


def _phase_failure(runtime_out: pathlib.Path, phase: str, returncode: int, stdout: str, stderr: str) -> Dict[str, Any]:
    diag_path = runtime_out / "failure_diagnostic.json"
    diag: Dict[str, Any] = {}
    if diag_path.exists():
        try:
            diag = json.loads(diag_path.read_text(encoding="utf-8"))
        except Exception:
            diag = {}
    return {
        "phase": phase,
        "returncode": returncode,
        "code": diag.get("code") or "SUBPROCESS_FAILED",
        "failure_class": diag.get("failure_class") or (
            "RUNTIME_TRANSPORT" if any(x in stderr for x in ("urllib.error.URLError:", "TimeoutError:", "ConnectionResetError:")) else "UNCLASSIFIED"),
        "last_successful_stage": diag.get("last_successful_stage"),
        "resume_hint": diag.get("resume_hint") or "RETRY_SAME_EXECUTION_ID",
        "stdout_tail": stdout[-4000:],
        "stderr_tail": stderr[-4000:],
    }


def _validate_explicit_result_revision(
    request: Dict[str, Any],
    previous: Dict[str, Any],
    formal: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Allow a RESULT correctness re-evaluation without deleting or rewriting the
    prior immutable RESULT run. The previous signed outcome/payout/source and
    the current immutable FINAL receipt must be identical. Only non-outcome
    correctness logic may change between revisions.
    """
    if str(request.get("result_revision") or "") != "CORRECTNESS_REEVALUATION":
        raise FormalOrchestrationError("RESULT_CHECKPOINT_REQUEST_MISMATCH_REQUIRES_EXPLICIT_REVISION")
    prev_env = _load_checkpoint_json(previous, "result_receipt_envelope.json")
    final_env = _load_checkpoint_json(formal, "final_receipt_envelope.json")
    if not isinstance(prev_env, dict) or not isinstance(final_env, dict):
        raise FormalOrchestrationError("RESULT_REVISION_LINEAGE_ARTIFACT_MISSING")
    prev_art = prev_env.get("artifact") if isinstance(prev_env.get("artifact"), dict) else {}
    prev_official = prev_art.get("official_result") if isinstance(prev_art.get("official_result"), dict) else {}
    req_order = [int(x) for x in (request.get("finish_order") or [])]
    prev_order = [int(x) for x in (prev_official.get("finish_order") or [])]
    if not req_order or req_order != prev_order:
        raise FormalOrchestrationError("RESULT_REVISION_OUTCOME_MISMATCH")
    req_payouts = {str(k).upper(): int(v) for k,v in (request.get("payouts") or {}).items()}
    prev_payouts = {str(k).upper(): int(v) for k,v in (prev_official.get("payouts") or {}).items()}
    if req_payouts != prev_payouts:
        raise FormalOrchestrationError("RESULT_REVISION_PAYOUT_MISMATCH")
    if str(request.get("source") or "") != str(prev_official.get("source") or ""):
        raise FormalOrchestrationError("RESULT_REVISION_SOURCE_MISMATCH")
    if str(request.get("result_available_at") or "") != str(prev_art.get("result_available_at") or prev_official.get("result_available_at") or ""):
        raise FormalOrchestrationError("RESULT_REVISION_RESULT_TIME_MISMATCH")
    frozen = prev_art.get("frozen_refs") or prev_art.get("frozen_references") or {}
    previous_final_sha = str(frozen.get("final_receipt_sha256") or "")
    current_final_sha = str(final_env.get("receipt_sha256") or "")
    if not previous_final_sha or previous_final_sha != current_final_sha:
        raise FormalOrchestrationError("RESULT_REVISION_FINAL_LINEAGE_MISMATCH")
    return {
        "status":"PASS",
        "revision":"CORRECTNESS_REEVALUATION",
        "previous_result_manifest_sha256":str((previous.get("latest") or {}).get("manifest_sha256") or ""),
        "previous_result_receipt_sha256":str(prev_env.get("receipt_sha256") or ""),
        "final_receipt_sha256":current_final_sha,
        "outcome_unchanged":True,
        "payouts_unchanged":True,
        "production_effect":"NONE",
    }


def run_phase(
    request: Dict[str, Any],
    phase: str,
    *,
    run_id: str,
    github_sha: Optional[str],
    runtime_out: pathlib.Path,
    tmp_root: pathlib.Path,
    checkpoint_intent: Optional[Dict[str, Any]] = None,
    resume_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    execution_id = str(request["execution_id"])
    request_path = tmp_root / execution_id / f"{phase.lower()}_request.json"
    _write(request_path, request)
    _reset_runtime_out(runtime_out)

    env = os.environ.copy()
    env.pop("KM_RESULT_REUSE_PATH", None)
    store_run_id = f"{run_id}-{phase.lower()}"
    if resume_result is not None:
        if str(phase).upper() != "RESULT":
            raise FormalOrchestrationError("RESULT_RECOVERY_PHASE_INVALID")
        envelope = _load_checkpoint_json(resume_result, "result_receipt_envelope.json")
        flags = _load_checkpoint_json(resume_result, "receipt_verifications.json") or {}
        if (not envelope or flags.get("RESULT") not in (True, False) or "RESULT" not in flags
                or _load_checkpoint_json(resume_result, "result_checkpoint_basis.json") != {"request_sha256": _sha_obj(request)}):
            raise FormalOrchestrationError("RESULT_RECOVERY_CHECKPOINT_OR_BASIS_INVALID")
        recovery_path = request_path.parent / "resume_signed_result.json"
        _write(recovery_path, envelope)
        env["KM_RESULT_REUSE_PATH"] = str(recovery_path.resolve())
        manifest_sha = (resume_result.get("latest") or {}).get("manifest_sha256")
        if not manifest_sha:
            raise FormalOrchestrationError("RESULT_RECOVERY_MANIFEST_REQUIRED")
        store_run_id += "-recovery-" + manifest_sha[:12]
    env["REQUEST_FILE"] = str(request_path.resolve())
    proc = subprocess.run(
        ([sys.executable, "-m", "runtime.local_result_from_signed_final", str(request_path)]
         if str(phase).upper() == "RESULT" else
         [sys.executable, "-m", "runtime.non_jra_formal_runner"]),
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        failure = _phase_failure(runtime_out, phase, proc.returncode, proc.stdout, proc.stderr)
        if resume_result is not None:
            # The earlier immutable receipt survives even when fresh /verify
            # transport fails before this attempt produces another artifact.
            failure["signed_result_preserved"] = True
            failure["resume_hint"] = "VERIFY_STORED_RESULT_THEN_RESUME_DOWNSTREAM"
        if str(phase).upper() == "RESULT" and (runtime_out / "result_receipt_envelope.json").is_file():
            verifications_path = runtime_out / "receipt_verifications.json"
            verifications = _load(verifications_path) if verifications_path.is_file() else {}
            response = _load(runtime_out / "result_receipt_envelope.json")
            if ("RESULT" in verifications and verifications.get("RESULT") in (True, False)
                    and (response.get("receipt") or {}).get("phase") == "RESULT"
                    and (response.get("receipt") or {}).get("race_id") == request.get("race_id")):
                partial_copy = tmp_root / execution_id / "result_out"
                _copy_json_dir(runtime_out, partial_copy)
                _write(partial_copy / "result_checkpoint_basis.json", {"request_sha256": _sha_obj(request)})
                _write(partial_copy / "post_signed_result_failure.json", {
                    "code": failure["code"], "status": "PARTIAL-LIFECYCLE", "duplicate_settlement_forbidden": True})
                persist_phase(execution_id, "RESULT", store_run_id, partial_copy, github_sha=github_sha)
                failure["signed_result_preserved"] = True
                failure["signed_result_verified"] = verifications.get("RESULT") is True
                failure["resume_hint"] = "RESUME_MISSING_LEARNING_WITHOUT_RESULT_REGENERATION"
        raise FormalOrchestrationError(json.dumps(
            failure,
            ensure_ascii=False,
            sort_keys=True,
        ))

    phase_copy = tmp_root / execution_id / f"{phase.lower()}_out"
    _copy_json_dir(runtime_out, phase_copy)
    if str(phase).upper() == "SOURCE":
        _write(phase_copy / "source_checkpoint_basis.json", source_checkpoint_basis(request))
    elif str(phase).upper() == "FORMAL":
        source_resolved = resolve_phase(execution_id, "SOURCE")
        _write(
            phase_copy / "formal_checkpoint_basis.json",
            formal_checkpoint_basis(checkpoint_intent if checkpoint_intent is not None else request, source_resolved),
        )
    if str(phase).upper() == "RESULT":
        _write(phase_copy / "result_checkpoint_basis.json", {"request_sha256": _sha_obj(request)})
    persisted = persist_phase(
        execution_id,
        phase,
        store_run_id,
        phase_copy,
        github_sha=github_sha,
    )
    return {
        "phase": phase,
        "status": "PASS",
        "manifest_sha256": (persisted.get("latest") or {}).get("manifest_sha256"),
        "run_id": (persisted.get("manifest") or {}).get("run_id"),
        "stdout_tail": proc.stdout[-4000:],
    }


def orchestrate(
    intent: Dict[str, Any],
    *,
    run_id: str,
    github_sha: Optional[str],
    runtime_out: pathlib.Path = DEFAULT_RUNTIME_OUT,
    tmp_root: pathlib.Path = DEFAULT_TMP_ROOT,
    plan_only: bool = False,
) -> Dict[str, Any]:
    family = str(intent.get("family_id") or "").upper()
    if family not in SUPPORTED_FAMILIES:
        raise FormalOrchestrationError(f"SINGLE_ENTRY_FAMILY_NOT_SUPPORTED:{family}")

    # RESULT is a later invocation of the same entry, never an attempt to
    # reacquire SOURCE or recompute a historical prediction.
    phase = str(intent.get("execution_phase") or intent.get("phase") or "").upper()
    # SOURCE-only is explicit analysis/prewarm work, never full completion.
    if phase in {"SOURCE", "SOURCE_ACQUIRE"} and intent.get("analysis_only") is True:
        execution_id = derive_execution_id(intent)
        saved = resolve_phase(execution_id, "SOURCE")
        if saved is not None:
            if source_checkpoint_compatibility(intent, saved).get("status") != "PASS":
                raise FormalOrchestrationError("SOURCE_CHECKPOINT_INCOMPATIBLE")
            return {"status": "SOURCE_PASS", "execution_id": execution_id, "completion": False}
        if plan_only:
            return {"status": "PLANNED", "execution_id": execution_id, "phases": ["SOURCE"]}
        acquired = run_phase(build_phase_request(intent, "SOURCE"), "SOURCE", run_id=run_id,
                             github_sha=github_sha, runtime_out=runtime_out, tmp_root=tmp_root)
        return {"status": "SOURCE_PASS", "execution_id": execution_id,
                "phases": [acquired], "completion": False}
    if phase in {"SOURCE", "SOURCE_ACQUIRE"}:
        intent = copy.deepcopy(intent)
        intent.pop("execution_phase", None)
        intent.pop("phase", None)

    if phase in {"RESULT", "POST_RACE", "POST-RACE", "SETTLEMENT"}:
        execution_id = derive_execution_id(intent)
        request = copy.deepcopy(intent)
        request["execution_id"] = execution_id
        route = result_route(request)
        formal = resolve_phase(execution_id, "FORMAL")
        if route == "CANONICAL" and formal is None:
            raise FormalOrchestrationError("RESULT_REQUIRES_EXISTING_FORMAL_CHECKPOINT")
        previous = resolve_phase(execution_id, "RESULT")
        recovery = None
        if previous is not None:
            basis = _load_checkpoint_json(previous, "result_checkpoint_basis.json")
            if basis != {"request_sha256": _sha_obj(request)}:
                _validate_explicit_result_revision(request, previous, formal)
            else:
                _reset_runtime_out(runtime_out)
                materialize_phase(execution_id, "RESULT", runtime_out)
                completion = verify_execution_completion(runtime_out, request, phase="RESULT")
                flags = _load_checkpoint_json(previous, "receipt_verifications.json") or {}
                if (completion["complete"] or plan_only or "RESULT" not in flags
                        or flags.get("RESULT") not in (True, False)
                        or not _load_checkpoint_json(previous, "result_receipt_envelope.json")):
                    return {"status": "ALREADY_COMPLETE" if completion["complete"] else "FORMAL_INCOMPLETE",
                            "execution_id": execution_id, "phase": "RESULT", "completion": completion}
                recovery = previous
        if plan_only:
            return {"status": "PLANNED", "execution_id": execution_id,
                    "phases": ["RESULT"], "prediction_reexecution": False}
        result = run_phase(request, "RESULT", run_id=run_id, github_sha=github_sha,
                           runtime_out=runtime_out, tmp_root=tmp_root, resume_result=recovery)
        completion = verify_execution_completion(runtime_out, request, phase="RESULT")
        _write(runtime_out / "lifecycle_completion.json", completion)
        return {"status": "FULL_LIFECYCLE_EXECUTION_PASS" if completion["complete"] else "FORMAL_INCOMPLETE",
                "execution_id": execution_id, "completion": completion,
                "execution_class": completion["execution_class"],
                "phases": [result], "prediction_reexecution": False}

    mode = str(intent.get("execution_mode") or "AUTO").upper()
    if mode == "ENTRY_TRANSPORT_FALLBACK":
        validate_fallback_request(intent)
        mode = "AUTO"
    if mode not in {"AUTO", "FULL_LIFECYCLE", "FORMAL_SINGLE_ENTRY"}:
        raise FormalOrchestrationError(f"UNSUPPORTED_EXECUTION_MODE:{mode}")

    execution_id = derive_execution_id(intent)

    try:
        validate_temporal_truthfulness(intent)
    except FormalOrchestrationError as exc:
        return {
            "schema": "KM-FORMAL-SINGLE-ENTRY-ORCHESTRATION-v1",
            "profile": current_single_entry_profile(),
            "status": "FAIL_CLOSED",
            "family_id": family,
            "race_id": intent.get("race_id"),
            "execution_id": execution_id,
            "gateway_profile": load_gateway().get("profile_id"),
            "first_failed_phase": "BOOTSTRAP",
            "first_failed_code": str(exc),
            "first_failed_class": "TEMPORAL_TRUTHFULNESS",
            "last_successful_stage": None,
            "resume_from": "INTENT_RECLASSIFICATION",
            "resume_hint": "CLASSIFY_ARCHIVED_ACCEPTANCE_AS_POST_START_REPLAY_NO_OOS",
            "production_prediction_change": False,
            "production_numerical_change": False,
            "krs_physics_change": False,
            "mec_change": False,
            "capital_change": False,
        }
    try:
        import_closure = build_closure("runtime/non_jra_formal_runner.py")
    except FormalImportClosureError as exc:
        return {
            "schema": "KM-FORMAL-SINGLE-ENTRY-ORCHESTRATION-v1",
            "profile": current_single_entry_profile(),
            "status": "FAIL_CLOSED",
            "family_id": family,
            "race_id": intent.get("race_id"),
            "execution_id": execution_id,
            "gateway_profile": load_gateway().get("profile_id"),
            "first_failed_phase": "BOOTSTRAP",
            "first_failed_code": "FORMAL_IMPORT_CLOSURE_FAILED",
            "first_failed_class": "INFRASTRUCTURE_COMPATIBILITY",
            "last_successful_stage": None,
            "resume_from": "BOOTSTRAP",
            "resume_hint": "REPAIR_CODE_THEN_RETRY_SAME_EXECUTION_ID",
            "detail": str(exc),
            "production_prediction_change": False,
            "production_numerical_change": False,
            "krs_physics_change": False,
            "mec_change": False,
            "capital_change": False,
        }
    intent_normalizations: list[Dict[str, Any]] = []
    if not plan_only:
        # C1 Production path requires an explicit result-blind Frozen Static
        # payload. Prediction-owner experimentation remains outside this repair.
        validate_request_context(intent)
        intent, intent_normalizations = normalize_single_entry_intent(intent)

    plan = resume_plan(execution_id, intent)
    report: Dict[str, Any] = {
        "schema": "KM-FORMAL-SINGLE-ENTRY-ORCHESTRATION-v1",
        "profile": current_single_entry_profile(),
        "status": "PLANNED" if plan_only else "RUNNING",
        "family_id": family,
        "race_id": intent.get("race_id"),
        "execution_id": execution_id,
        "intent_basis_sha256": _sha_obj(intent),
        "gateway_profile": load_gateway().get("profile_id"),
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "plan": plan,
        "import_closure": {
            "status": import_closure.get("status"),
            "file_count": import_closure.get("file_count"),
        },
        "phases": [],
        "intent_normalizations": intent_normalizations,
        "production_prediction_change": False,
        "production_numerical_change": False,
        "krs_physics_change": False,
        "mec_change": False,
        "capital_change": False,
    }
    if plan_only:
        return report

    if plan["action"] == "FAIL_CLOSED":
        report["status"] = "FAIL_CLOSED"
        if plan["resume_from"] == "FORMAL_CHECKPOINT_REPAIR_REQUIRED":
            report["first_failed_phase"] = "FORMAL"
            report["first_failed_code"] = "FORMAL_CHECKPOINT_CORRUPT"
            report["first_failed_class"] = "FORMAL_CHECKPOINT_INTEGRITY"
            report["resume_hint"] = "RESTORE_VERIFIED_IMMUTABLE_FORMAL_CHECKPOINT"
        elif plan["resume_from"] == "NEW_EXECUTION_ID_REQUIRED_FORMAL_LEGACY":
            report["first_failed_phase"] = "FORMAL"
            report["first_failed_code"] = "FORMAL_CHECKPOINT_LEGACY_UNBOUND"
            report["first_failed_class"] = "FORMAL_CHECKPOINT_INTEGRITY"
            report["resume_hint"] = "CREATE_NEW_EXECUTION_ID_TO_ESTABLISH_FORMAL_SEMANTIC_BASIS"
        elif plan["resume_from"] == "NEW_EXECUTION_ID_REQUIRED_FORMAL_BASIS":
            report["first_failed_phase"] = "FORMAL"
            report["first_failed_code"] = "FORMAL_CHECKPOINT_BASIS_MISMATCH"
            report["first_failed_class"] = "FORMAL_CHECKPOINT_INTEGRITY"
            report["resume_hint"] = "CREATE_NEW_EXECUTION_ID_FOR_CHANGED_FORMAL_BASIS"
        elif plan["resume_from"] == "NEW_EXECUTION_ID_REQUIRED":
            report["first_failed_phase"] = "SOURCE"
            report["first_failed_code"] = "SOURCE_CHECKPOINT_BASIS_MISMATCH"
            report["first_failed_class"] = "SOURCE_CHECKPOINT_INTEGRITY"
            report["resume_hint"] = "CREATE_NEW_EXECUTION_ID_FOR_CHANGED_SOURCE_BASIS"
        else:
            report["first_failed_phase"] = "SOURCE"
            report["first_failed_code"] = "SOURCE_CHECKPOINT_CORRUPT"
            report["first_failed_class"] = "SOURCE_CHECKPOINT_INTEGRITY"
            report["resume_hint"] = "REPAIR_OR_RECREATE_SOURCE_CHECKPOINT"
        report["resume_from"] = plan["resume_from"]
        return report

    if plan["action"] == "RETURN_IMMUTABLE_FORMAL":
        _reset_runtime_out(runtime_out)
        resolved = materialize_phase(execution_id, "FORMAL", runtime_out)
        if resolved is None:
            raise FormalOrchestrationError("FORMAL_CHECKPOINT_DISAPPEARED")
        completion = verify_execution_completion(runtime_out, {**intent,"execution_id":execution_id}, phase="FORMAL")
        report["completion"] = completion
        report["execution_class"] = completion["execution_class"]
        report["status"] = "ALREADY_COMPLETE" if completion["complete"] else "FORMAL_INCOMPLETE"
        report["resume_from"] = "RESULT_PENDING" if completion["complete"] else "MISSING_STAGES"
        report["phases"].append({
            "phase": "FORMAL",
            "status": "REUSED_IMMUTABLE",
            "run_id": (resolved.get("manifest") or {}).get("run_id"),
            "manifest_sha256": (resolved.get("latest") or {}).get("manifest_sha256"),
            "compatibility": plan["checkpoints"]["formal"].get("compatibility"),
        })
        return report

    try:
        check_deadline(intent)
        if plan["action"] == "RUN_SOURCE_THEN_FORMAL":
            source_req = build_phase_request(intent, "SOURCE")
            report["phases"].append(run_phase(
                source_req,
                "SOURCE",
                run_id=run_id,
                github_sha=github_sha,
                runtime_out=runtime_out,
                tmp_root=tmp_root,
            ))
        else:
            report["phases"].append({
                "phase": "SOURCE",
                "status": "REUSED_DURABLE_CHECKPOINT",
                "checkpoint": plan["checkpoints"]["source"],
            })

        check_deadline(intent)
        current_phase = "FORMAL"
        formal_req = bind_formal_request_to_source(build_phase_request(intent, "FORMAL"))
        if formal_req.get("source_authoritative_reconciliation"):
            report["source_authoritative_reconciliation"] = formal_req[
                "source_authoritative_reconciliation"
            ]
        report["phases"].append(run_formal_with_fallback(
            formal_req,
            "FORMAL",
            run_id=run_id,
            github_sha=github_sha,
            runtime_out=runtime_out,
            tmp_root=tmp_root,
            checkpoint_intent=intent,
        ))
        completion = verify_execution_completion(runtime_out, {**intent,"execution_id":execution_id}, phase="FORMAL")
        _write(runtime_out / "lifecycle_completion.json", completion)
        report["completion"] = completion
        report["execution_class"] = completion["execution_class"]
        report["status"] = "FULL_LIFECYCLE_EXECUTION_PASS" if completion["complete"] else "FORMAL_INCOMPLETE"
        report["resume_from"] = "RESULT_PENDING" if completion["complete"] else "MISSING_STAGES"
        return report
    except FormalOrchestrationError as exc:
        try:
            failure = json.loads(str(exc))
        except Exception:
            failure = {
                "phase": locals().get("current_phase", "SOURCE"),
                "code": str(exc),
                "failure_class": "ORCHESTRATION",
                "detail": str(exc),
                "resume_hint": "RETRY_SAME_EXECUTION_ID",
            }
        code = str(failure.get("code") or failure.get("detail") or "")
        if "OWNER" in code:
            report["dependency_failure"] = failure.get("detail") or code
        report["status"] = "DEADLINE_HOLD" if "DEADLINE" in code else "BLOCKED"
        report["execution_class"] = "BLOCKED"
        report["failure"] = failure
        report["first_failed_phase"] = failure.get("phase")
        report["first_failed_code"] = failure.get("code")
        report["first_failed_class"] = failure.get("failure_class")
        report["last_successful_stage"] = failure.get("last_successful_stage")
        # SOURCE success is already durable even if FORMAL fails.
        report["resume_from"] = failure.get("phase") or "SOURCE"
        return report


def completion_exit_code(report: Dict[str, Any]) -> int:
    # PLANNED is a successful read-only command, not an execution completion.
    if report.get("status") == "PLANNED":
        return 0
    if report.get("status") in {"FULL_LIFECYCLE_EXECUTION_PASS", "ALREADY_COMPLETE"}:
        completion = report.get("completion")
        return 0 if isinstance(completion, dict) and completion.get("complete") is True else 2
    return 2


def check_deadline(intent: Dict[str, Any]) -> None:
    if str(intent.get("temporal_mode") or "FORMAL-PRE-RACE").upper() != "FORMAL-PRE-RACE":
        return
    post = intent.get("scheduled_post_at")
    if not post:
        raise FormalOrchestrationError("SCHEDULED_POST_AT_REQUIRED")
    deadline = intent.get("release_deadline_at")
    end = _parse_iso(deadline) if deadline else _parse_iso(post) - dt.timedelta(
        seconds=int(intent.get("release_buffer_seconds") or 120))
    if dt.datetime.now(dt.timezone.utc) >= end.astimezone(dt.timezone.utc):
        raise FormalOrchestrationError("DEADLINE_HOLD:FORMAL_INCOMPLETE")


def run_formal_with_fallback(request, phase, **kwargs):
    try:
        check_deadline(request)
        return run_phase(request, phase, **kwargs)
    except FormalOrchestrationError as exc:
        try:
            failure = json.loads(str(exc))
        except ValueError:
            raise
        # R36 only handles transport failures. Safety, Authority, Prediction,
        # temporal and numerical failures never become a legacy retry.
        if failure.get("failure_class") not in {"TRANSPORT", "NETWORK", "RUNTIME_TRANSPORT"}:
            raise
        check_deadline(request)
        fallback = build_legacy_formal_request(request, primary_failure_code=failure.get("code"))
        validate_fallback_request(fallback)
        fallback = bind_formal_request_to_source(fallback)
        return run_phase(fallback, phase, **kwargs)


def _official_result_identity_matches(page_text: str, race_context: Dict[str, Any]) -> bool:
    """Match the official NAR result header in normalized visible page text.

    NAR may change which heading element wraps the result identity.  The
    identity itself remains fail-closed: date -> venue -> race -> 競走成績 must
    appear as one ordered result header, not as unrelated navigation tokens.
    """
    from local_physical.nar_source_manifest import VENUE_NAMES
    date = dt.date.fromisoformat(str(race_context["race_date"]).replace("/", "-"))
    venue = re.sub(r"\s+", "", unicodedata.normalize("NFKC", VENUE_NAMES[race_context["venue_id"]]))
    race_no = int(race_context["race_no"])
    normalized = re.sub(r"\s+", "", unicodedata.normalize("NFKC", str(page_text or "")))
    pattern = (
        re.escape(f"{date.year}年{date.month}月{date.day}日")
        + r"(?:\([^)]{1,4}\))?"
        + re.escape(venue)
        + re.escape(f"第{race_no}競走")
        + re.escape("競走成績")
    )
    return re.search(pattern, normalized) is not None


def parse_official_result_snapshot(snapshot, race_context, runner_ids):
    """NAR official finish/payout verification; unsupported outcomes HOLD.

    Uses the existing factual SOURCE decoder/table parser, never Prediction.
    The current settlement runtime supports EXACTA/TRIO/TRIFECTA only.
    """
    physical_path = str(ROOT / "runtime" / "local_physical")
    if physical_path not in sys.path:
        sys.path.insert(0, physical_path)
    from local_physical.source_acquisition import _decode, _html_tables, _html_text
    from local_physical.nar_auxiliary_evidence import _result_rows_from_table
    from local_physical.nar_source_manifest import VENUE_NAMES
    if snapshot.get("http_status") != 200 or snapshot.get("official") is not True:
        raise FormalOrchestrationError("OFFICIAL_RESULT_HTTP_OR_AUTHORITY_HOLD")
    raw = gzip.decompress(base64.b64decode(snapshot["raw_gzip_b64"]))
    if hashlib.sha256(raw).hexdigest() != snapshot.get("raw_sha256"):
        raise FormalOrchestrationError("OFFICIAL_RESULT_RAW_DIGEST_MISMATCH")
    html = _decode(raw, snapshot.get("content_type") or "")
    # Inspect race-page content, excluding site navigation and script literals.
    # An apparently populated finish/payout table is not sufficient while the
    # official page expressly reports a provisional or suspended result.
    body = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", html, flags=re.S | re.I)
    page_text = re.sub(r"\s+", "", unicodedata.normalize("NFKC", _html_text(body)))
    if any(marker in page_text for marker in (
            "審議中", "審議しています", "成績未確定", "着順未確定", "払戻未確定", "結果未確定")):
        raise FormalOrchestrationError("OFFICIAL_RESULT_NOT_FINAL")
    if any(marker in page_text for marker in ("競走取り止め", "競走取止", "競走中止", "開催中止")):
        # Cancellations require the existing authorized refund path; the flat
        # payout representation used here cannot safely settle them.
        raise FormalOrchestrationError("OFFICIAL_RESULT_CANCELLATION_HOLD")
    if not _official_result_identity_matches(page_text, race_context):
        raise FormalOrchestrationError("OFFICIAL_RESULT_PAGE_RACE_IDENTITY_HOLD")
    tables = _html_tables(html)
    finish_tables = [rows for table in tables if (rows := _result_rows_from_table(table))]
    if len(finish_tables) != 1:
        raise FormalOrchestrationError("OFFICIAL_RESULT_FINISH_TABLE_HOLD")
    rows = sorted(finish_tables[0], key=lambda row: row["finish"])
    positions = [row["finish"] for row in rows]
    order = [row["horse_no"] for row in rows]
    if (len(rows) < 3 or positions != list(range(1, len(rows) + 1))
            or len(set(order)) != len(order) or not set(map(str, order)).issubset(set(map(str, runner_ids)))):
        raise FormalOrchestrationError("OFFICIAL_RESULT_DEAD_HEAT_OR_UNIVERSE_HOLD")
    # Validate published winning selection as well as amount. Flat per-bet-type
    # payouts cannot represent dead heats, refunds or multiple winning sets.
    expected = {"馬連単": ("EXACTA", order[:2]), "三連複": ("TRIO", sorted(order[:3])),
                "三連単": ("TRIFECTA", order[:3])}
    payouts = {}
    for table in tables:
        for row in table:
            if not row or row[0] not in expected:
                continue
            name, selection = expected[row[0]]
            if len(row) != 4 or name in payouts:
                raise FormalOrchestrationError("OFFICIAL_RESULT_PAYOUT_AMBIGUOUS_HOLD")
            parsed = [int(x) for x in re.findall(r"\d+", row[1])]
            if parsed != selection or not re.fullmatch(r"[\d,]+円", row[2]):
                raise FormalOrchestrationError("OFFICIAL_RESULT_PAYOUT_SELECTION_HOLD")
            amount = int(row[2].replace(",", "").replace("円", ""))
            if amount <= 0:
                raise FormalOrchestrationError("OFFICIAL_RESULT_PAYOUT_AMOUNT_HOLD")
            payouts[name] = amount
    if set(payouts) != {"EXACTA", "TRIO", "TRIFECTA"}:
        raise FormalOrchestrationError("OFFICIAL_RESULT_PAYOUT_NOT_READY")
    return order, payouts


def acquire_official_result_request(intent, *, run_id, github_sha, tmp_root, fetch=None):
    """Acquire one immutable official RESULT checkpoint from frozen SOURCE identity."""
    from local_physical.source_acquisition import fetch_source
    from local_physical.nar_source_manifest import _result_source, LOCAL_BABA_CODES
    execution_id = derive_execution_id(intent)
    formal = resolve_phase(execution_id, "FORMAL")
    source = resolve_phase(execution_id, "SOURCE")
    if not formal or not source:
        raise FormalOrchestrationError("OFFICIAL_RESULT_REQUIRES_SOURCE_AND_FROZEN_FINAL")
    final = _load_checkpoint_json(formal, "final_receipt_envelope.json")
    signed_source = _load_checkpoint_json(source, "source_receipt_envelope.json")
    if not final or not signed_source:
        raise FormalOrchestrationError("OFFICIAL_RESULT_LINEAGE_MISSING")
    if final.get("receipt", {}).get("race_id") != intent["race_id"]:
        raise FormalOrchestrationError("OFFICIAL_RESULT_FINAL_RACE_MISMATCH")
    source_binding = _source_binding_from_resolved(source)
    formal_basis = _load_checkpoint_json(formal, "formal_checkpoint_basis.json") or {}
    if formal_basis.get("source_binding") != source_binding:
        raise FormalOrchestrationError("OFFICIAL_RESULT_FINAL_SOURCE_LINEAGE_MISMATCH")
    verification = _load_checkpoint_json(source, "source_verification.json") or {}
    if verification.get("verified") is not True or signed_source["artifact"].get("formal_ready") is not True:
        raise FormalOrchestrationError("OFFICIAL_RESULT_SOURCE_AUTHORITY_HOLD")
    cached = resolve_phase(execution_id, "OFFICIAL_RESULT")
    if cached:
        request = _load_checkpoint_json(cached, "official_result_request.json")
        if (request.get("frozen_final_sha256") != _sha_obj(final)
                or request.get("source_binding") != source_binding):
            raise FormalOrchestrationError("OFFICIAL_RESULT_FROZEN_FINAL_CHANGED")
        return request
    artifact = signed_source["artifact"]
    identity = artifact["source_race_context"]
    context_keys = {"venue_id": intent.get("venue_id"), "race_date": intent.get("race_date"),
                    "race_no": intent.get("race_no")}
    for key, value in context_keys.items():
        if str(value).replace("/", "-") != str(identity[key]).replace("/", "-"):
            raise FormalOrchestrationError("OFFICIAL_RESULT_SOURCE_IDENTITY_MISMATCH")
    if dt.datetime.now(dt.timezone.utc) < _parse_iso(intent["scheduled_post_at"]):
        raise FormalOrchestrationError("OFFICIAL_RESULT_NOT_DUE")
    tickets = ((final.get("artifact") or {}).get("final_ticket") or {}).get("tickets") or []
    if any(str(t.get("bet_type", "")).upper() not in {"EXACTA", "TRIO", "TRIFECTA"} for t in tickets):
        raise FormalOrchestrationError("OFFICIAL_RESULT_UNSUPPORTED_SETTLEMENT_TICKET_HOLD")
    spec = _result_source(identity["venue_id"], LOCAL_BABA_CODES[identity["venue_id"]],
                          str(identity["race_date"]).replace("-", "/"), int(identity["race_no"]))
    # RESULT collection has its own time axis; never reuse prediction cutoff.
    try:
        snapshot, errors = (fetch or fetch_source)(spec, "")
    except ValueError as exc:
        # DNS validation is part of the existing Source safety boundary. Retry
        # resolution failures without bypassing it or retaining raw diagnostics.
        if str(exc).startswith("SOURCE_DNS_RESOLUTION_FAILED:"):
            raise FormalOrchestrationError("OFFICIAL_RESULT_TRANSPORT_PENDING") from None
        raise
    if errors or snapshot.get("final_url") != spec["url"]:
        raise FormalOrchestrationError("OFFICIAL_RESULT_FETCH_OR_REDIRECT_HOLD")
    runners = artifact["active_runner_universe"]["runners"]
    order, payouts = parse_official_result_snapshot(snapshot, identity, [r["runner_id"] for r in runners])
    request = {"family_id": "LOCAL", "execution_id": execution_id, "race_id": intent["race_id"],
               "phase": "RESULT", "execution_phase": "RESULT", "temporal_mode": "RESULT",
               "finish_order": order, "payouts": payouts, "result_available_at": snapshot["fetched_at"],
               "result_timestamp_authority": "OBSERVED_AT_OFFICIAL_RETRIEVAL_PUBLICATION_TIME_UNKNOWN",
               "source": spec["url"], "official_result_verified": True,
               "official_result_verification_ref": spec["url"] + "#sha256=" + snapshot["raw_sha256"],
               "frozen_final_sha256": _sha_obj(final), "official_snapshot_sha256": snapshot["snapshot_sha256"],
               "source_binding": source_binding,
               "pfs_authority": "FROZEN-RECOMMENDATION"}
    dest = tmp_root / execution_id / "official_result_out"
    _write(dest / "official_result_snapshot.json", snapshot)
    _write(dest / "official_result_request.json", request)
    persist_phase(execution_id, "OFFICIAL_RESULT", f"{run_id}-official-result", dest, github_sha=github_sha)
    return request


def resume_official_result(intent, *, run_id, github_sha, runtime_out, tmp_root, wait_seconds=0):
    """Same workflow continues RESULT without generating another Prediction."""
    until = time.monotonic() + min(max(int(wait_seconds), 0), 10800)
    recovery_attempt = 0
    transport_policy = load_gateway().get("transport_reliability") or {}
    while True:
        try:
            request = acquire_official_result_request(intent, run_id=run_id, github_sha=github_sha, tmp_root=tmp_root)
            return orchestrate(request, run_id=run_id, github_sha=github_sha,
                               runtime_out=runtime_out, tmp_root=tmp_root)
        except FormalOrchestrationError as exc:
            code = str(exc)
            try:
                failure = json.loads(code)
            except ValueError:
                failure = {}
            if (isinstance(failure, dict) and failure.get("signed_result_preserved") is True
                    and failure.get("failure_class") == "RUNTIME_TRANSPORT"
                    and recovery_attempt < int(transport_policy.get("max_attempts", 1)) - 1
                    and time.monotonic() < until):
                delays = transport_policy.get("backoff_seconds") or [0]
                delay = float(delays[min(recovery_attempt, len(delays) - 1)])
                recovery_attempt += 1
                time.sleep(min(delay, max(0, until - time.monotonic())))
                continue
            retryable = code in RETRYABLE_OFFICIAL_RESULT_CODES
            if not retryable or time.monotonic() >= until:
                return {"status": "WAITING_OFFICIAL_RESULT" if retryable else "BLOCKED",
                        "execution_id": derive_execution_id(intent), "first_failed_code": code,
                        "prediction_reexecution": False, "completion": {"complete": False}}
            time.sleep(min(30, max(0, until - time.monotonic())))
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if time.monotonic() >= until:
                return {"status": "WAITING_OFFICIAL_RESULT", "execution_id": derive_execution_id(intent),
                        "first_failed_code": "OFFICIAL_RESULT_TRANSPORT_PENDING",
                        "prediction_reexecution": False, "completion": {"complete": False}}
            time.sleep(min(30, max(0, until - time.monotonic())))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--intent", required=True)
    ap.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID") or "manual")
    ap.add_argument("--github-sha", default=os.environ.get("GITHUB_SHA"))
    ap.add_argument("--plan-only", action="store_true")
    ap.add_argument("--phase", choices=["SOURCE", "RESULT"])
    ap.add_argument("--resume-official-result", action="store_true")
    ap.add_argument("--result-wait-seconds", type=int, default=0)
    ap.add_argument("--output", default=str(DEFAULT_RUNTIME_OUT / "orchestration_report.json"))
    args = ap.parse_args()

    intent = _load(args.intent)
    if args.phase:
        intent["execution_phase"] = args.phase
    runtime_out = DEFAULT_RUNTIME_OUT
    runtime_out.mkdir(parents=True, exist_ok=True)
    try:
        report = resume_official_result(
            intent, run_id=str(args.run_id), github_sha=args.github_sha, runtime_out=runtime_out,
            tmp_root=DEFAULT_TMP_ROOT, wait_seconds=args.result_wait_seconds,
        ) if args.resume_official_result else orchestrate(
            intent,
            run_id=str(args.run_id),
            github_sha=args.github_sha,
            runtime_out=runtime_out,
            plan_only=args.plan_only,
        )
    except (FormalOrchestrationError, ExecutionStoreError, ValueError, subprocess.TimeoutExpired) as exc:
        report = {"status": "BLOCKED", "execution_class": "BLOCKED", "completion": False,
                  "execution_id": derive_execution_id(intent), "first_failed_code": str(exc)}
    _write(pathlib.Path(args.output), report)
    print("KM_FORMAL_SINGLE_ENTRY_RESULT=" + json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return completion_exit_code(report)


if __name__ == "__main__":
    raise SystemExit(main())
