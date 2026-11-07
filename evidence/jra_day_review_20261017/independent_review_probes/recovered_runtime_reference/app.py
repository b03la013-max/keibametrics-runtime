from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

RUNTIME_REV = "KM-EXEC-RUNTIME-v1.3.1-BASE44-RECEIPT-LOG-20260917"
SIGNER_KEY_ID = os.getenv("KM_RECEIPT_SIGNER_KEY_ID", "KM-RUNTIME-ED25519-20260917")
ENGINE_VERSION = "KRS-Engine v1.1.0"
PARAM_VERSION = "0.1-provisional"
PARAM_STATUS = "PROVISIONAL_UNCALIBRATED"
ENGINE_PATH = Path("/opt/km/KRS-Engine_v1.1.0_PORTABLE.py")
PARAM_PATH = Path("/opt/km/parameter_map_v0.1-provisional.json")
EXPECTED_ENGINE_SHA = os.getenv("KM_ENGINE_SHA256", "")
EXPECTED_PARAM_SHA = os.getenv("KM_PARAM_SHA256", "")
PUBLIC_HOST = os.getenv("KM_PUBLIC_HOST", "quorumprobe-production.up.railway.app")

PLACEHOLDERS = {"TBD", "PENDING", "TODO", "TEMP", "NOT-YET-CALCULATED", "NOT-YET-GENERATED", "後で計算"}
ALLOWED_INDEX_STATUSES = {"CALCULATED", "MISSING-WITH-REASON", "NOT-APPLICABLE-WITH-REASON", "N/A-WITH-REASON"}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def sha256_obj(obj: Any) -> str:
    return sha256_bytes(canonical_json(obj).encode("utf-8"))


def file_sha(path: Path) -> Optional[str]:
    try:
        return sha256_bytes(path.read_bytes())
    except FileNotFoundError:
        return None


def get_private_key() -> Ed25519PrivateKey:
    raw_b64 = os.getenv("KM_RECEIPT_PRIVATE_KEY_B64", "")
    if not raw_b64:
        raise RuntimeError("KM_RECEIPT_PRIVATE_KEY_B64 missing")
    raw = base64.b64decode(raw_b64)
    if len(raw) == 32:
        return Ed25519PrivateKey.from_private_bytes(raw)
    try:
        return serialization.load_pem_private_key(raw, password=None)  # type: ignore[return-value]
    except Exception as exc:
        raise RuntimeError("invalid receipt private key") from exc


def public_key_b64() -> str:
    pub = get_private_key().public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    return base64.b64encode(pub).decode("ascii")


def sign_body(body: Dict[str, Any]) -> Dict[str, Any]:
    wire = canonical_json(body).encode("utf-8")
    sig = get_private_key().sign(wire)
    return {
        "receipt": body,
        "receipt_sha256": sha256_bytes(wire),
        "signature": base64.b64encode(sig).decode("ascii"),
        "signer_key_id": SIGNER_KEY_ID,
        "signature_alg": "Ed25519",
    }


def verify_envelope(envelope: Dict[str, Any]) -> Dict[str, Any]:
    try:
        body = envelope["receipt"]
        sig = base64.b64decode(envelope["signature"])
        pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64()))
        pub.verify(sig, canonical_json(body).encode("utf-8"))
        expected = sha256_obj(body)
        supplied = envelope.get("receipt_sha256")
        if supplied and supplied != expected:
            return {"valid": False, "reason": "RECEIPT_HASH_MISMATCH", "expected": expected, "supplied": supplied}
        return {"valid": True, "signer_key_id": envelope.get("signer_key_id", SIGNER_KEY_ID), "receipt_sha256": expected}
    except Exception as exc:
        return {"valid": False, "reason": f"SIGNATURE_INVALID:{type(exc).__name__}"}




def log_execution_receipt(label: str, obj: Any) -> None:
    """Emit receipt/status metadata to Railway logs for operational verification.

    Never logs private keys or raw KRS output.
    """
    try:
        if isinstance(obj, dict) and isinstance(obj.get("run_receipt"), dict):
            payload = {"status": obj.get("status"), "run_receipt": obj.get("run_receipt")}
        else:
            payload = obj
        print(f"KM_EXEC_RECEIPT {label} {canonical_json(payload)}", flush=True)
    except Exception as exc:
        print(f"KM_EXEC_RECEIPT_LOG_ERROR {label} {type(exc).__name__}:{exc}", flush=True)

def runtime_health() -> Dict[str, Any]:
    engine_sha = file_sha(ENGINE_PATH)
    param_sha = file_sha(PARAM_PATH)
    engine_ok = bool(engine_sha and (not EXPECTED_ENGINE_SHA or engine_sha == EXPECTED_ENGINE_SHA))
    param_ok = bool(param_sha and (not EXPECTED_PARAM_SHA or param_sha == EXPECTED_PARAM_SHA))
    key_ok = False
    try:
        _ = public_key_b64()
        key_ok = True
    except Exception:
        pass
    return {
        "status": "READY" if engine_ok and param_ok and key_ok else "DEGRADED",
        "runtime_revision": RUNTIME_REV,
        "mcp_bridge": "ACTIVE",
        "mcp_endpoint": f"https://{PUBLIC_HOST}/mcp",
        "engine": {"version": ENGINE_VERSION, "sha256": engine_sha, "expected_sha256": EXPECTED_ENGINE_SHA, "ready": engine_ok},
        "parameter_map": {"version": PARAM_VERSION, "status": PARAM_STATUS, "sha256": param_sha, "expected_sha256": EXPECTED_PARAM_SHA, "ready": param_ok},
        "receipt_signer": {"key_id": SIGNER_KEY_ID, "algorithm": "Ed25519", "ready": key_ok, "public_key_b64": public_key_b64() if key_ok else None},
        "capabilities": ["PRE_KRS", "KRS_EXECUTE", "FINAL", "RESULT", "VERIFY_RECEIPT"],
        "timestamp": utcnow(),
    }


def _required_indices_errors(indices: Any) -> List[str]:
    errs: List[str] = []
    if not isinstance(indices, list) or len(indices) == 0:
        return ["REQUIRED_INDICES_EMPTY"]
    for i, item in enumerate(indices):
        if not isinstance(item, dict):
            errs.append(f"REQUIRED_INDEX_{i}_INVALID")
            continue
        st = str(item.get("status", "")).upper()
        if st not in ALLOWED_INDEX_STATUSES:
            errs.append(f"REQUIRED_INDEX_{i}_UNRESOLVED")
        if "REASON" in st:
            reason = str(item.get("reason", "")).strip()
            if not reason or reason.upper() in PLACEHOLDERS:
                errs.append(f"REQUIRED_INDEX_{i}_PLACEHOLDER_REASON")
    return errs


def _verify_krs_receipt_and_output(artifacts: Dict[str, Any]) -> List[str]:
    errs: List[str] = []
    env = artifacts.get("krs_run_receipt")
    if not isinstance(env, dict):
        return ["KRS_EXECUTABLE_BUT_RUN_RECEIPT_MISSING"]
    vr = verify_envelope(env)
    if not vr.get("valid"):
        errs.append("KRS_RUN_RECEIPT_INVALID")
        return errs
    rec = env.get("receipt", {})
    if rec.get("status") != "EXECUTED":
        errs.append("KRS_RUN_NOT_EXECUTED")
    if not rec.get("output_sha256"):
        errs.append("KRS_OUTPUT_HASH_MISSING")
    wire = artifacts.get("krs_output_canonical_json")
    if wire is not None:
        if sha256_bytes(str(wire).encode("utf-8")) != rec.get("output_sha256"):
            errs.append("KRS_OUTPUT_HASH_MISMATCH")
    return errs


def validate_phase(phase: Literal["PRE_KRS", "FINAL", "RESULT"], artifacts: Dict[str, Any]) -> List[str]:
    errs: List[str] = []
    race_id = artifacts.get("race_id")
    if not race_id:
        errs.append("RACE_ID_MISSING")
    if phase == "PRE_KRS":
        ru = artifacts.get("runner_universe")
        if not isinstance(ru, list) or len(ru) < 2:
            errs.append("RUNNER_UNIVERSE_INVALID")
        errs.extend(_required_indices_errors(artifacts.get("required_indices")))
        static = artifacts.get("static_prediction")
        if not isinstance(static, dict) or not static:
            errs.append("STATIC_PREDICTION_MISSING")
        if not artifacts.get("prediction_cutoff"):
            errs.append("PREDICTION_CUTOFF_MISSING")
        if artifacts.get("krs_required") is None:
            errs.append("KRS_REQUIRED_STATUS_MISSING")
    elif phase == "FINAL":
        fpp = artifacts.get("final_prediction_package")
        if not isinstance(fpp, dict) or not fpp:
            errs.append("FINAL_PREDICTION_PACKAGE_MISSING")
        ticket = artifacts.get("final_ticket")
        no_bet = bool(artifacts.get("no_bet"))
        if not no_bet and (not isinstance(ticket, dict) or not ticket):
            errs.append("FINAL_TICKET_MISSING")
        if not no_bet:
            traces = artifacts.get("ticket_transport")
            if not isinstance(traces, list) or not traces:
                errs.append("FPP_TICKET_TRACE_MISSING")
        if artifacts.get("krs_required") and artifacts.get("krs_executable", True):
            errs.extend(_verify_krs_receipt_and_output(artifacts))
        if not artifacts.get("final_freeze_timestamp"):
            errs.append("FINAL_FREEZE_TIMESTAMP_MISSING")
    elif phase == "RESULT":
        res = artifacts.get("official_result")
        if not isinstance(res, dict) or not res:
            errs.append("OFFICIAL_RESULT_MISSING")
        settlement = artifacts.get("settlement")
        if not isinstance(settlement, dict):
            errs.append("SETTLEMENT_MISSING")
        else:
            st = str(settlement.get("status", "")).upper()
            if st not in {"SETTLED", "PENDING", "UNKNOWN"}:
                errs.append("SETTLEMENT_STATUS_INVALID")
            if st in {"PENDING", "UNKNOWN"} and settlement.get("return") == 0:
                errs.append("PENDING_RETURN_MUST_NOT_BE_ZERO")
        if not artifacts.get("frozen_prediction_ref"):
            errs.append("FROZEN_PREDICTION_REF_MISSING")
        if not artifacts.get("learning_event"):
            errs.append("LEARNING_EVENT_MISSING")
    return errs


def issue_phase_receipt(phase: Literal["PRE_KRS", "FINAL", "RESULT"], artifacts: Dict[str, Any]) -> Dict[str, Any]:
    errors = validate_phase(phase, artifacts)
    body = {
        "schema": "KM-SIGNED-RECEIPT-v1",
        "runtime_revision": RUNTIME_REV,
        "phase": phase,
        "race_id": artifacts.get("race_id"),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "artifact_sha256": sha256_obj(artifacts),
        "timestamp": utcnow(),
    }
    return sign_body(body)


def execute_krs(race_id: str, input_data: Dict[str, Any], mode: str, seed: int, input_class: str) -> Dict[str, Any]:
    mode_u = mode.upper()
    if mode_u == "SIM-STD":
        runs = 5000
    elif mode_u == "SIM-HIGH":
        runs = 20000
    elif mode_u == "SMOKE":
        runs = 100
    else:
        raise ValueError("mode must be SIM-STD, SIM-HIGH, or SMOKE")
    health = runtime_health()
    if health["status"] != "READY":
        body = {
            "schema": "KM-KRS-RUN-RECEIPT-v1",
            "runtime_revision": RUNTIME_REV,
            "race_id": race_id,
            "status": "EXECUTION-FAILED",
            "cause": "RUNTIME-DEGRADED",
            "mode": mode_u,
            "requested_run_count": runs,
            "actual_run_count": 0,
            "timestamp": utcnow(),
        }
        return {"status": "EXECUTION-FAILED", "output": None, "output_canonical_json": None, "run_receipt": sign_body(body)}

    payload = json.loads(json.dumps(input_data, ensure_ascii=False))
    payload.setdefault("race", {})
    payload["race"].setdefault("prediction_id", race_id)
    payload.setdefault("simulation", {})
    payload["simulation"]["run_count"] = runs
    payload["simulation"]["master_seed"] = int(seed)
    input_wire = canonical_json(payload)
    input_sha = sha256_bytes(input_wire.encode("utf-8"))

    started = time.time()
    with tempfile.TemporaryDirectory(prefix="kmkrs-") as td:
        inp = Path(td) / "input.json"
        out = Path(td) / "output.json"
        csvp = Path(td) / "summary.csv"
        inp.write_text(input_wire, encoding="utf-8")
        cmd = [sys.executable, str(ENGINE_PATH), str(inp), "--params", str(PARAM_PATH), "--output", str(out), "--csv", str(csvp), "--runs", str(runs), "--seed", str(seed), "--short"]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        elapsed_ms = int((time.time() - started) * 1000)
        if p.returncode != 0 or not out.exists():
            body = {
                "schema": "KM-KRS-RUN-RECEIPT-v1",
                "runtime_revision": RUNTIME_REV,
                "race_id": race_id,
                "status": "EXECUTION-FAILED",
                "cause": "ENGINE-EXECUTION-FAILED",
                "returncode": p.returncode,
                "stderr_tail": p.stderr[-2000:],
                "mode": mode_u,
                "input_class": input_class,
                "requested_run_count": runs,
                "actual_run_count": 0,
                "seed": seed,
                "input_sha256": input_sha,
                "engine_sha256": file_sha(ENGINE_PATH),
                "parameter_map_sha256": file_sha(PARAM_PATH),
                "elapsed_ms": elapsed_ms,
                "timestamp": utcnow(),
            }
            return {"status": "EXECUTION-FAILED", "output": None, "output_canonical_json": None, "run_receipt": sign_body(body)}
        output = json.loads(out.read_text(encoding="utf-8"))
        output_wire = canonical_json(output)
        output_sha = sha256_bytes(output_wire.encode("utf-8"))
        actual_runs = int(output.get("snapshot", {}).get("run_count", runs))
        body = {
            "schema": "KM-KRS-RUN-RECEIPT-v1",
            "runtime_revision": RUNTIME_REV,
            "race_id": race_id,
            "status": "EXECUTED",
            "mode": mode_u,
            "input_class": input_class,
            "requested_run_count": runs,
            "actual_run_count": actual_runs,
            "seed": seed,
            "input_sha256": input_sha,
            "output_sha256": output_sha,
            "engine_version": ENGINE_VERSION,
            "engine_sha256": file_sha(ENGINE_PATH),
            "parameter_map_version": PARAM_VERSION,
            "parameter_map_status": PARAM_STATUS,
            "parameter_map_sha256": file_sha(PARAM_PATH),
            "elapsed_ms": elapsed_ms,
            "timestamp": utcnow(),
        }
        return {
            "status": "EXECUTED",
            "output": output,
            "output_canonical_json": output_wire,
            "run_receipt": sign_body(body),
        }


mcp = MCPServer(
    name="KeibaMetrics Runtime",
    instructions=(
        "Execution-only bridge for KeibaMetrics. Use km_pre_krs before KRS, "
        "km_krs_execute when KRS is required, km_final before claiming Formal-Full completion, "
        "and km_result after official results. Do not invent PASS statuses without signed receipts."
    ),
 )


@mcp.tool()
def km_health() -> Dict[str, Any]:
    """Check KeibaMetrics external runtime, Engine, parameter_map, signer, and MCP bridge readiness."""
    return runtime_health()


@mcp.tool()
def km_pre_krs(artifacts: Dict[str, Any]) -> Dict[str, Any]:
    """Validate PRE_KRS artifacts and return a signed PRE_KRS receipt. Required before KRS in Formal-Full execution."""
    return issue_phase_receipt("PRE_KRS", artifacts)


@mcp.tool()
def km_krs_execute(
    race_id: str,
    input_data: Dict[str, Any],
    mode: Literal["SIM-STD", "SIM-HIGH", "SMOKE"] = "SIM-STD",
    seed: int = 20260811,
    input_class: Literal["FORMAL", "DEGRADED", "MINIMUM-EXECUTABLE"] = "FORMAL",
) -> Dict[str, Any]:
    """Execute the real KRS Engine. SIM-STD=5000, SIM-HIGH=20000. Returns raw output plus signed Run Receipt."""
    return execute_krs(race_id, input_data, mode, seed, input_class)


@mcp.tool()
def km_final(artifacts: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Final Prediction/Ticket execution artifacts and return a signed FINAL receipt."""
    return issue_phase_receipt("FINAL", artifacts)


@mcp.tool()
def km_result(artifacts: Dict[str, Any]) -> Dict[str, Any]:
    """Validate official result, settlement, immutable frozen references, and learning event; returns signed RESULT receipt."""
    return issue_phase_receipt("RESULT", artifacts)


@mcp.tool()
def km_verify_receipt(envelope: Dict[str, Any]) -> Dict[str, Any]:
    """Verify an Ed25519-signed KeibaMetrics receipt envelope."""
    return verify_envelope(envelope)


@mcp.custom_route("/health", methods=["GET"])
async def health_route(request: Request):
    return JSONResponse(runtime_health())


@mcp.custom_route("/public-key", methods=["GET"])
async def public_key_route(request: Request):
    return JSONResponse({"signer_key_id": SIGNER_KEY_ID, "algorithm": "Ed25519", "public_key_b64": public_key_b64(), "runtime_revision": RUNTIME_REV})


@mcp.custom_route("/verify", methods=["POST"])
async def verify_route(request: Request):
    result = verify_envelope(await request.json())
    print(f"KM_EXEC_VERIFY {canonical_json(result)}", flush=True)
    return JSONResponse(result)


@mcp.custom_route("/pre-krs", methods=["POST"])
async def pre_krs_route(request: Request):
    result = issue_phase_receipt("PRE_KRS", await request.json())
    log_execution_receipt("PRE_KRS", result)
    return JSONResponse(result)


@mcp.custom_route("/krs/execute", methods=["POST"])
async def krs_execute_route(request: Request):
    data = await request.json()
    try:
        result = execute_krs(
            race_id=str(data.get("race_id") or data.get("input_data", {}).get("race", {}).get("prediction_id") or "UNKNOWN-RACE"),
            input_data=data.get("input_data") or data.get("input") or {},
            mode=str(data.get("mode", "SIM-STD")),
            seed=int(data.get("seed", 20260811)),
            input_class=str(data.get("input_class", "FORMAL")),
        )
        log_execution_receipt("KRS", result)
        return JSONResponse(result)
    except Exception as exc:
        return JSONResponse({"status": "EXECUTION-FAILED", "error": f"{type(exc).__name__}: {exc}"}, status_code=400)


@mcp.custom_route("/final", methods=["POST"])
async def final_route(request: Request):
    result = issue_phase_receipt("FINAL", await request.json())
    log_execution_receipt("FINAL", result)
    return JSONResponse(result)


@mcp.custom_route("/result", methods=["POST"])
async def result_route(request: Request):
    result = issue_phase_receipt("RESULT", await request.json())
    log_execution_receipt("RESULT", result)
    return JSONResponse(result)


@mcp.custom_route("/", methods=["GET"])
async def root_route(request: Request):
    return JSONResponse({"name": "KeibaMetrics Runtime", "runtime_revision": RUNTIME_REV, "mcp": "/mcp", "health": "/health"})


security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=[PUBLIC_HOST, f"{PUBLIC_HOST}:*"],
    allowed_origins=["https://chatgpt.com", "https://chat.openai.com", "https://app.base44.com"],
)

_mcp_app = mcp.streamable_http_app(transport_security=security, stateless_http=True, json_response=True)
app = CORSMiddleware(
    _mcp_app,
    allow_origins=["https://chatgpt.com", "https://chat.openai.com", "https://app.base44.com"],
    allow_origin_regex=r"https://[a-z0-9-]+\.base44\.app",
    allow_methods=["GET", "POST", "OPTIONS", "DELETE"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)
