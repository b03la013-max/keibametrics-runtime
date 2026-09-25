from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import pathlib
import re
import urllib.request
from typing import Any, Dict, Tuple

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_POINTER = REPO_ROOT / "profiles" / "current_execution_gateway.json"


class ExecutionGatewayError(ValueError):
    pass


def load_gateway(path: str | pathlib.Path | None = None) -> Dict[str, Any]:
    p = pathlib.Path(path) if path else DEFAULT_POINTER
    if not p.is_absolute():
        p = REPO_ROOT / p
    with p.open(encoding="utf-8") as f:
        doc = json.load(f)
    if not str(doc.get("profile_id") or "").strip():
        raise ExecutionGatewayError("EXECUTION_GATEWAY_PROFILE_ID_MISSING")
    if not isinstance(doc.get("families"), dict):
        raise ExecutionGatewayError("EXECUTION_GATEWAY_FAMILIES_MISSING")
    return doc


def family_config(family: str, gateway: Dict[str, Any] | None = None) -> Dict[str, Any]:
    g = gateway or load_gateway()
    fam = str(family or "").upper()
    cfg = (g.get("families") or {}).get(fam)
    if not isinstance(cfg, dict):
        raise ExecutionGatewayError(f"EXECUTION_GATEWAY_FAMILY_NOT_CONFIGURED:{fam}")
    return cfg


def contract_path(gateway: Dict[str, Any] | None = None) -> pathlib.Path:
    g = gateway or load_gateway()
    rel = str(g.get("family_runtime_contracts") or "").strip()
    if not rel:
        raise ExecutionGatewayError("FAMILY_RUNTIME_CONTRACT_POINTER_MISSING")
    return REPO_ROOT / rel


def _safe_id(value: str) -> str:
    x = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "").strip())
    x = re.sub(r"-+", "-", x).strip("-")
    if not x:
        raise ExecutionGatewayError("EXECUTION_ID_EMPTY")
    return x[:180]


def execution_phase(request: Dict[str, Any]) -> str:
    phase = str(request.get("execution_phase") or request.get("phase") or "FORMAL").upper()
    aliases = {
        "SOURCE_ONLY": "SOURCE",
        "SOURCE-FREEZE": "SOURCE",
        "SOURCE_FREEZE": "SOURCE",
        "POST_RACE": "RESULT",
        "POST-RACE": "RESULT",
        "SETTLEMENT": "RESULT",
    }
    return aliases.get(phase, phase)


def derive_execution_id(request: Dict[str, Any]) -> str:
    explicit = str(request.get("execution_id") or "").strip()
    if explicit:
        return _safe_id(explicit)
    family = str(request.get("family_id") or "LOCAL").upper()
    race_id = str(request.get("race_id") or "").strip()
    if not race_id:
        raise ExecutionGatewayError("RACE_ID_REQUIRED_FOR_EXECUTION_ID")
    return _safe_id(f"{family}-{race_id}-EXEC")


def artifact_name(execution_id: str, phase: str, gateway: Dict[str, Any] | None = None, family: str = "LOCAL") -> str:
    g = gateway or load_gateway()
    cfg = family_config(family, g)
    prefix = str(cfg.get("artifact_prefix") or "km-execution")
    normalized_phase = execution_phase({"execution_phase": phase})
    return _safe_id(f"{prefix}-{execution_id}-{normalized_phase}")


def normalize_request(request: Dict[str, Any], gateway: Dict[str, Any] | None = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    g = gateway or load_gateway()
    out = copy.deepcopy(request)
    family = str(out.get("family_id") or "LOCAL").upper()
    cfg = family_config(family, g)
    eid = derive_execution_id(out)
    diagnostics = {
        "request_runtime_expected_revision": out.get("runtime_expected_revision"),
        "request_external_endpoint": out.get("external_endpoint"),
        "request_source_receipt_artifact_id": out.get("source_receipt_artifact_id"),
        "request_source_run_id": out.get("source_run_id"),
        "request_artifact_name": out.get("artifact_name"),
    }
    legacy_override = bool(out.get("legacy_handoff_override"))
    if not legacy_override:
        out.pop("source_receipt_artifact_id", None)
        out.pop("source_run_id", None)
        out.pop("artifact_name", None)
    out["execution_id"] = eid
    out["execution_gateway_profile"] = g["profile_id"]
    out["resolved_runtime_profile"] = cfg.get("runtime_profile")
    out["resolved_external_endpoint"] = cfg.get("external_endpoint")
    out["runtime_expected_revision_diagnostic_only"] = out.get("runtime_expected_revision")
    out.pop("runtime_expected_revision", None)
    out.pop("external_endpoint", None)
    ctx = {
        "execution_id": eid,
        "family_id": family,
        "phase": execution_phase(out),
        "gateway_profile": g["profile_id"],
        "runtime_profile": cfg.get("runtime_profile"),
        "runtime_git_revision_pointer": cfg.get("runtime_git_revision"),
        "external_endpoint": cfg.get("external_endpoint"),
        "request_diagnostics": diagnostics,
        "legacy_handoff_override": legacy_override,
    }
    return out, ctx


def sha256_file(path: str | pathlib.Path, repo_root: pathlib.Path | None = None) -> str:
    root = repo_root or REPO_ROOT
    p = pathlib.Path(path)
    if not p.is_absolute():
        p = root / p
    return hashlib.sha256(p.read_bytes()).hexdigest()


def repository_bundle(cfg: Dict[str, Any], repo_root: pathlib.Path | None = None) -> Dict[str, str]:
    files = cfg.get("bundle_files") or {}
    if not isinstance(files, dict) or not files:
        raise ExecutionGatewayError("RUNTIME_BUNDLE_FILE_MAP_MISSING")
    return {health_field: sha256_file(path, repo_root) for health_field, path in files.items()}


def bundle_fingerprint(bundle: Dict[str, str]) -> str:
    raw = json.dumps(bundle, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def assess_runtime_health(
    health: Dict[str, Any],
    family: str = "LOCAL",
    gateway: Dict[str, Any] | None = None,
    repo_root: pathlib.Path | None = None,
) -> Dict[str, Any]:
    g = gateway or load_gateway()
    cfg = family_config(family, g)
    expected_bundle = repository_bundle(cfg, repo_root)
    errors = []
    warnings = []

    if health.get("status") != "READY":
        errors.append("RUNTIME_HEALTH_NOT_READY")

    expected_profile = str(cfg.get("runtime_profile") or "")
    actual_profile = str(health.get("runtime_revision") or "")
    if expected_profile and actual_profile != expected_profile:
        errors.append("RUNTIME_PROFILE_MISMATCH")

    expected_engine = str(cfg.get("engine_sha256") or "")
    actual_engine = str(health.get("engine_sha256") or "")
    if expected_engine and actual_engine != expected_engine:
        errors.append("ENGINE_SHA256_MISMATCH")

    expected_parameter = str(cfg.get("parameter_map_sha256") or "")
    actual_parameter = str(health.get("parameter_map_sha256") or "")
    if expected_parameter and actual_parameter != expected_parameter:
        errors.append("PARAMETER_MAP_SHA256_MISMATCH")

    expected_signer = str(cfg.get("receipt_signer_key_id") or "")
    actual_signer = str(health.get("receipt_signer_key_id") or health.get("signer_key_id") or "")
    if expected_signer and actual_signer != expected_signer:
        errors.append("RECEIPT_SIGNER_MISMATCH")

    bundle_mismatches = {}
    for field, expected in expected_bundle.items():
        actual = str(health.get(field) or "")
        if actual != expected:
            bundle_mismatches[field] = {"expected": expected, "actual": actual}
    if bundle_mismatches:
        errors.append("RUNTIME_BUNDLE_HASH_MISMATCH")

    required_caps = set(cfg.get("required_capabilities") or [])
    actual_caps = set(health.get("capabilities") or [])
    missing_caps = sorted(required_caps - actual_caps)
    if missing_caps:
        errors.append("RUNTIME_CAPABILITY_MISSING")

    pointer_revision = str(cfg.get("runtime_git_revision") or "")
    health_revision = str(health.get("github_revision") or "")
    git_revision_match = bool(pointer_revision and health_revision == pointer_revision)
    if pointer_revision and health_revision and not git_revision_match and not bundle_mismatches:
        warnings.append("GITHUB_REVISION_DIAGNOSTIC_MISMATCH_BUNDLE_COMPATIBLE")

    result = {
        "status": "PASS" if not errors else "FAIL",
        "gateway_profile": g.get("profile_id"),
        "family_id": str(family).upper(),
        "runtime_profile_expected": expected_profile,
        "runtime_profile_actual": actual_profile,
        "runtime_git_revision_pointer": pointer_revision,
        "runtime_git_revision_actual": health_revision,
        "git_revision_match": git_revision_match,
        "git_revision_is_compatibility_authority": False,
        "bundle_fingerprint_expected": bundle_fingerprint(expected_bundle),
        "bundle_fingerprint_actual": bundle_fingerprint({
            k: str(health.get(k) or "") for k in expected_bundle
        }),
        "bundle_mismatches": bundle_mismatches,
        "missing_capabilities": missing_caps,
        "errors": errors,
        "warnings": warnings,
        "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    return result


def validate_phase_transition(previous_phase: str | None, next_phase: str) -> None:
    nxt = execution_phase({"execution_phase": next_phase})
    prev = execution_phase({"execution_phase": previous_phase}) if previous_phase else None
    allowed = {
        None: {"SOURCE"},
        "SOURCE": {"SOURCE", "FORMAL"},
        "FORMAL": {"FORMAL", "RESULT"},
        "RESULT": {"RESULT"},
    }
    if nxt not in allowed.get(prev, set()):
        raise ExecutionGatewayError(f"INVALID_LIFECYCLE_TRANSITION:{prev}->{nxt}")


def new_lifecycle_state(request: Dict[str, Any], gateway: Dict[str, Any] | None = None) -> Dict[str, Any]:
    normalized, ctx = normalize_request(request, gateway)
    return {
        "schema": "KM-EXECUTION-LIFECYCLE-v1",
        "execution_id": ctx["execution_id"],
        "race_id": normalized.get("race_id"),
        "family_id": ctx["family_id"],
        "gateway_profile": ctx["gateway_profile"],
        "current_phase": None,
        "status": "CREATED",
        "phases": {},
    }


def record_phase(state: Dict[str, Any], phase: str, status: str, references: Dict[str, Any] | None = None) -> Dict[str, Any]:
    out = copy.deepcopy(state)
    nxt = execution_phase({"execution_phase": phase})
    validate_phase_transition(out.get("current_phase"), nxt)
    out["current_phase"] = nxt
    out["status"] = status
    out.setdefault("phases", {})[nxt] = {
        "status": status,
        "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "references": copy.deepcopy(references or {}),
    }
    return out


def fetch_health(endpoint: str, timeout: int = 30) -> Dict[str, Any]:
    rq = urllib.request.Request(str(endpoint).rstrip("/") + "/health", headers={"accept": "application/json"})
    with urllib.request.urlopen(rq, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _cli() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    hp = sub.add_parser("health-check")
    hp.add_argument("--family", default="LOCAL")
    hp.add_argument("--output")

    rp = sub.add_parser("resolve-request")
    rp.add_argument("--request", required=True)

    args = ap.parse_args()
    gateway = load_gateway()

    if args.cmd == "health-check":
        cfg = family_config(args.family, gateway)
        health = fetch_health(cfg["external_endpoint"])
        result = assess_runtime_health(health, args.family, gateway)
        payload = {"health": health, "assessment": result}
        if args.output:
            pathlib.Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            pathlib.Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 0 if result["status"] == "PASS" else 2

    request = json.loads(pathlib.Path(args.request).read_text(encoding="utf-8"))
    normalized, ctx = normalize_request(request, gateway)
    print(json.dumps({"request": normalized, "context": ctx}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
