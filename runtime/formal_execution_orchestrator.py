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
from typing import Any, Dict, Optional

sys.path.insert(0, "runtime")

from execution_gateway import derive_execution_id, load_gateway
from execution_store import ExecutionStoreError, materialize_phase, persist_phase, resolve_phase
from formal_import_closure import FormalImportClosureError, build_closure

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_RUNTIME_OUT = ROOT / "runtime_out"
DEFAULT_TMP_ROOT = ROOT / "runtime" / "orchestrator_tmp"

SUPPORTED_FAMILIES = {"LOCAL"}


class FormalOrchestrationError(RuntimeError):
    pass


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
    if cp["formal"]["status"] == "COMPLETE":
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
        "failure_class": diag.get("failure_class") or "UNCLASSIFIED",
        "last_successful_stage": diag.get("last_successful_stage"),
        "resume_hint": diag.get("resume_hint") or "RETRY_SAME_EXECUTION_ID",
        "stdout_tail": stdout[-4000:],
        "stderr_tail": stderr[-4000:],
    }


def run_phase(
    request: Dict[str, Any],
    phase: str,
    *,
    run_id: str,
    github_sha: Optional[str],
    runtime_out: pathlib.Path,
    tmp_root: pathlib.Path,
) -> Dict[str, Any]:
    execution_id = str(request["execution_id"])
    request_path = tmp_root / execution_id / f"{phase.lower()}_request.json"
    _write(request_path, request)
    _reset_runtime_out(runtime_out)

    env = os.environ.copy()
    env["REQUEST_FILE"] = str(request_path.relative_to(ROOT))
    proc = subprocess.run(
        [sys.executable, "-m", "runtime.non_jra_formal_runner"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise FormalOrchestrationError(json.dumps(
            _phase_failure(runtime_out, phase, proc.returncode, proc.stdout, proc.stderr),
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
            formal_checkpoint_basis(request, source_resolved),
        )
    persisted = persist_phase(
        execution_id,
        phase,
        f"{run_id}-{phase.lower()}",
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

    mode = str(intent.get("execution_mode") or "AUTO").upper()
    if mode not in {"AUTO", "FULL_LIFECYCLE", "FORMAL_SINGLE_ENTRY"}:
        raise FormalOrchestrationError(f"UNSUPPORTED_EXECUTION_MODE:{mode}")

    execution_id = derive_execution_id(intent)
    try:
        validate_temporal_truthfulness(intent)
    except FormalOrchestrationError as exc:
        return {
            "schema": "KM-FORMAL-SINGLE-ENTRY-ORCHESTRATION-v1",
            "profile": "KM-FAMILY-FORMAL-SINGLE-ENTRY-20260929-R1",
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
            "profile": "KM-FAMILY-FORMAL-SINGLE-ENTRY-20260929-R1",
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
    plan = resume_plan(execution_id, intent)
    report: Dict[str, Any] = {
        "schema": "KM-FORMAL-SINGLE-ENTRY-ORCHESTRATION-v1",
        "profile": "KM-FAMILY-FORMAL-SINGLE-ENTRY-20260929-R1",
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
        if plan["resume_from"] == "NEW_EXECUTION_ID_REQUIRED_FORMAL_LEGACY":
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
        report["status"] = "ALREADY_COMPLETE"
        report["resume_from"] = "COMPLETE"
        report["phases"].append({
            "phase": "FORMAL",
            "status": "REUSED_IMMUTABLE",
            "run_id": (resolved.get("manifest") or {}).get("run_id"),
            "manifest_sha256": (resolved.get("latest") or {}).get("manifest_sha256"),
            "compatibility": plan["checkpoints"]["formal"].get("compatibility"),
        })
        return report

    try:
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

        formal_req = bind_formal_request_to_source(
            build_phase_request(intent, "FORMAL")
        )
        report["phases"].append(run_phase(
            formal_req,
            "FORMAL",
            run_id=run_id,
            github_sha=github_sha,
            runtime_out=runtime_out,
            tmp_root=tmp_root,
        ))
        report["status"] = "FULL_LIFECYCLE_EXECUTION_PASS"
        report["resume_from"] = "COMPLETE"
        return report
    except FormalOrchestrationError as exc:
        try:
            failure = json.loads(str(exc))
        except Exception:
            failure = {
                "phase": "UNKNOWN",
                "code": "ORCHESTRATION_EXCEPTION",
                "failure_class": "ORCHESTRATION",
                "detail": str(exc),
                "resume_hint": "RETRY_SAME_EXECUTION_ID",
            }
        report["status"] = "FAIL_CLOSED"
        report["failure"] = failure
        report["first_failed_phase"] = failure.get("phase")
        report["first_failed_code"] = failure.get("code")
        report["first_failed_class"] = failure.get("failure_class")
        report["last_successful_stage"] = failure.get("last_successful_stage")
        # SOURCE success is already durable even if FORMAL fails.
        report["resume_from"] = "FORMAL" if failure.get("phase") == "FORMAL" else "SOURCE"
        return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--intent", required=True)
    ap.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID") or "manual")
    ap.add_argument("--github-sha", default=os.environ.get("GITHUB_SHA"))
    ap.add_argument("--plan-only", action="store_true")
    ap.add_argument("--output", default=str(DEFAULT_RUNTIME_OUT / "orchestration_report.json"))
    args = ap.parse_args()

    intent = _load(args.intent)
    runtime_out = DEFAULT_RUNTIME_OUT
    runtime_out.mkdir(parents=True, exist_ok=True)
    report = orchestrate(
        intent,
        run_id=str(args.run_id),
        github_sha=args.github_sha,
        runtime_out=runtime_out,
        plan_only=args.plan_only,
    )
    _write(pathlib.Path(args.output), report)
    print("KM_FORMAL_SINGLE_ENTRY_RESULT=" + json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0 if report.get("status") in {"PLANNED", "ALREADY_COMPLETE", "FULL_LIFECYCLE_EXECUTION_PASS"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
