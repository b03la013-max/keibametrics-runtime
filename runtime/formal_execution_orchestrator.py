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


def checkpoint_status(execution_id: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "execution_id": execution_id,
        "source": {"status": "MISSING"},
        "formal": {"status": "MISSING"},
    }
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
        files = set((resolved.get("manifest") or {}).get("files") or {})
        required = "source_receipt_envelope.json" if phase == "SOURCE" else "final_receipt_envelope.json"
        out[phase.lower()] = {
            "status": "COMPLETE" if required in files else "INCOMPLETE",
            "run_id": (resolved.get("manifest") or {}).get("run_id"),
            "manifest_sha256": (resolved.get("latest") or {}).get("manifest_sha256"),
            "required_file": required,
            "required_file_present": required in files,
        }
    return out


def resume_plan(execution_id: str) -> Dict[str, Any]:
    cp = checkpoint_status(execution_id)
    if cp["formal"]["status"] == "COMPLETE":
        action = "RETURN_IMMUTABLE_FORMAL"
        resume_from = "COMPLETE"
    elif cp["source"]["status"] == "COMPLETE":
        action = "RESUME_FORMAL"
        resume_from = "FORMAL"
    elif cp["source"]["status"] == "CORRUPT":
        action = "FAIL_CLOSED"
        resume_from = "SOURCE_CHECKPOINT_REPAIR_REQUIRED"
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
    plan = resume_plan(execution_id)
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
        report["first_failed_phase"] = "SOURCE"
        report["first_failed_code"] = "SOURCE_CHECKPOINT_CORRUPT"
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

        formal_req = build_phase_request(intent, "FORMAL")
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
