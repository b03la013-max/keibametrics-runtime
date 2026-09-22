from __future__ import annotations

from typing import Any, Dict

import app as legacy
from fastapi import FastAPI, HTTPException

from source_acquisition import SOURCE_PROFILE, acquire_sources, verify_source_artifact, sha_obj
from nar_source_manifest import PROFILE as NAR_MANIFEST_PROFILE, build_local_nar_manifest
from nar_runner_universe import (
    PROFILE as NAR_RUNNER_UNIVERSE_PROFILE,
    enrich_source_artifact,
    validate_krs_horses,
)

APP_VERSION = "KM-LOCAL-PHYSICAL-RUNTIME-v1.5-REV.2-20260923-NAR-RUNNER-UNIVERSE-GATE"
SOURCE_REQUIRED = True
legacy.APP_VERSION = APP_VERSION

app = FastAPI(title="KeibaMetrics LOCAL Physical Runtime", version=APP_VERSION)


def _require_source_receipt(payload: Dict[str, Any], race_id: str) -> Dict[str, Any]:
    env = payload.get("source_receipt")
    if not isinstance(env, dict):
        raise HTTPException(422, "SOURCE_RECEIPT_REQUIRED")
    if not legacy.verify_envelope(env):
        raise HTTPException(422, "SOURCE_RECEIPT_SIGNATURE_INVALID")
    rec = env.get("receipt") or {}
    if rec.get("phase") != "SOURCE":
        raise HTTPException(422, "SOURCE_RECEIPT_PHASE_INVALID")
    if rec.get("status") != "SOURCE_FROZEN":
        raise HTTPException(422, "SOURCE_RECEIPT_NOT_FROZEN")
    if str(rec.get("race_id") or "") != str(race_id):
        raise HTTPException(422, "SOURCE_RECEIPT_RACE_ID_MISMATCH")
    valid, errors = verify_source_artifact(env.get("artifact") or {})
    if not valid:
        raise HTTPException(422, "SOURCE_ARTIFACT_INVALID:" + ",".join(errors))
    return env


@app.get("/health")
def health():
    h = dict(legacy.health())
    h["runtime_revision"] = APP_VERSION
    h["runtime_app_sha256"] = legacy.sha_file(__file__)
    h["source_acquisition_profile"] = SOURCE_PROFILE
    h["source_acquisition_required"] = SOURCE_REQUIRED
    caps = list(h.get("capabilities") or [])
    for c in ("SOURCE_ACQUIRE", "SOURCE_VERIFY", "SOURCE_FREEZE"):
        if c not in caps:
            caps.insert(0, c)
    h["capabilities"] = caps
    h["source_acquisition_sha256"] = legacy.sha_file("/opt/km/source_acquisition.py")
    h["nar_source_manifest_profile"] = NAR_MANIFEST_PROFILE
    h["nar_source_manifest_sha256"] = legacy.sha_file("/opt/km/nar_source_manifest.py")
    h["nar_runner_universe_profile"] = NAR_RUNNER_UNIVERSE_PROFILE
    h["nar_runner_universe_sha256"] = legacy.sha_file("/opt/km/nar_runner_universe.py")
    for c in ("SOURCE_RUNNER_UNIVERSE", "SOURCE_MANIFEST_LOCAL_NAR"):
        if c not in caps:
            caps.insert(0, c)
    h["capabilities"] = caps
    return h


@app.post("/verify")
def verify(payload: Dict[str, Any]):
    return legacy.verify(payload)


@app.post("/source/manifest/local")
def source_manifest_local(payload: Dict[str, Any]):
    legacy.validate_family(payload)
    try:
        return build_local_nar_manifest(payload)
    except ValueError as e:
        raise HTTPException(422, str(e))


@app.post("/source/acquire")
def source_acquire(payload: Dict[str, Any]):
    legacy.validate_family(payload)
    race_id = str(payload.get("race_id") or "")
    if not race_id:
        raise HTTPException(422, "RACE_ID_REQUIRED")
    artifact, errors = acquire_sources(payload)
    artifact["source_manifest_profile"] = payload.get("manifest_profile")
    if payload.get("manifest_profile") == NAR_MANIFEST_PROFILE:
        try:
            artifact = enrich_source_artifact(artifact)
        except Exception as e:
            errors = list(errors) + ["OFFICIAL_RUNNER_UNIVERSE_EXTRACTION_FAILED:" + str(e)]
            artifact["formal_ready"] = False
    artifact["errors"] = list(dict.fromkeys(errors))
    artifact["source_snapshot_sha256"] = sha_obj(
        {k: v for k, v in artifact.items() if k != "source_snapshot_sha256"}
    )
    status = "SOURCE_FROZEN" if not artifact["errors"] and artifact.get("formal_ready") is True else "FAIL"
    return legacy.signed_receipt("SOURCE", race_id, status, artifact, artifact["errors"])


@app.post("/source/verify")
def source_verify(payload: Dict[str, Any]):
    sig = legacy.verify_envelope(payload)
    rec = payload.get("receipt") or {}
    valid_artifact, errors = verify_source_artifact(payload.get("artifact") or {})
    valid = (
        sig
        and rec.get("phase") == "SOURCE"
        and rec.get("status") == "SOURCE_FROZEN"
        and valid_artifact
    )
    return {
        "valid": bool(valid),
        "verified": bool(valid),
        "signature_valid": bool(sig),
        "artifact_valid": bool(valid_artifact),
        "errors": errors,
        "signer_key_id": legacy.SIGNER,
        "family": legacy.FAMILY,
        "source_profile": SOURCE_PROFILE,
    }


@app.post("/pre-krs")
def pre_krs(payload: Dict[str, Any]):
    legacy.validate_family(payload)
    race_id = str(payload.get("race_id") or "")
    source = _require_source_receipt(payload, race_id)
    source_artifact = source.get("artifact") or {}
    if source_artifact.get("source_manifest_profile") == NAR_MANIFEST_PROFILE:
        valid_universe, universe_errors = validate_krs_horses(
            source_artifact, payload.get("krs_input_data")
        )
        if not valid_universe:
            raise HTTPException(
                422,
                "SOURCE_RUNNER_UNIVERSE_MISMATCH:" + ",".join(universe_errors),
            )
    out = legacy.pre_krs(payload)
    if (out.get("receipt") or {}).get("status") == "PASS":
        art = dict(out.get("artifact") or {})
        art["source_receipt_sha256"] = source.get("receipt_sha256")
        art["source_snapshot_sha256"] = (source.get("artifact") or {}).get("source_snapshot_sha256")
        out = legacy.signed_receipt("PRE_KRS", race_id, "PASS", art, [])
    return out


@app.post("/krs/execute")
def krs_execute(payload: Dict[str, Any]):
    return legacy.krs_execute(payload)


@app.post("/final")
def final(payload: Dict[str, Any]):
    legacy.validate_family(payload)
    race_id = str(payload.get("race_id") or "")
    source = _require_source_receipt(payload, race_id)
    out = legacy.final(payload)
    if (out.get("receipt") or {}).get("status") == "PASS":
        art = dict(out.get("artifact") or {})
        art["source_receipt_sha256"] = source.get("receipt_sha256")
        art["source_snapshot_sha256"] = (source.get("artifact") or {}).get("source_snapshot_sha256")
        out = legacy.signed_receipt("FINAL", race_id, "PASS", art, [])
    return out


@app.post("/formal")
def formal(payload: Dict[str, Any]):
    legacy.validate_family(payload)
    race_id = str(payload.get("race_id") or "")
    if not race_id:
        raise HTTPException(422, "RACE_ID_REQUIRED")

    work = dict(payload)
    source = work.get("source_receipt")
    if not isinstance(source, dict) and isinstance(work.get("source_acquisition_request"), dict):
        req = dict(work["source_acquisition_request"])
        req["family_id"] = legacy.FAMILY
        req["race_id"] = race_id
        source = source_acquire(req)
        work["source_receipt"] = source

    try:
        source = _require_source_receipt(work, race_id)
    except HTTPException as e:
        return legacy.signed_receipt(
            "FORMAL",
            race_id,
            "FAIL",
            {"source_receipt": source},
            [str(e.detail)],
        )

    pre = pre_krs(work)
    if (pre.get("receipt") or {}).get("status") != "PASS":
        return legacy.signed_receipt(
            "FORMAL",
            race_id,
            "FAIL",
            {"source_receipt": source, "pre_krs_receipt": pre},
            ["PRE_KRS_FAIL"],
        )

    run = legacy.krs_execute(
        {
            "family_id": legacy.FAMILY,
            "race_id": race_id,
            "krs_input_data": work.get("krs_input_data"),
            "run_count": work.get("run_count", 5000),
            "seed": work.get("seed", 1),
        }
    )
    if (run.get("receipt") or {}).get("status") != "EXECUTED":
        return legacy.signed_receipt(
            "FORMAL",
            race_id,
            "FAIL",
            {"source_receipt": source, "pre_krs_receipt": pre, "krs_run_receipt": run},
            ["KRS_FAIL"],
        )

    fin_payload = {
        "family_id": legacy.FAMILY,
        "race_id": race_id,
        "source_receipt": source,
        "krs_run_receipt": run,
        "final_prediction_package": work.get("final_prediction_package"),
        "final_ticket": work.get("final_ticket"),
        "minimum_efficient_coverage": work.get("minimum_efficient_coverage"),
        "capital_policy_decision": work.get("capital_policy_decision"),
        "ticket_transport_trace": work.get("ticket_transport_trace"),
        "execution_stage_manifest": work.get("execution_stage_manifest"),
        "final_freeze_timestamp": work.get("final_freeze_timestamp"),
    }
    fin = final(fin_payload)
    if (fin.get("receipt") or {}).get("status") != "PASS":
        return legacy.signed_receipt(
            "FORMAL",
            race_id,
            "FAIL",
            {
                "source_receipt": source,
                "pre_krs_receipt": pre,
                "krs_run_receipt": run,
                "final_receipt": fin,
            },
            ["FINAL_FAIL"],
        )

    artifact = {
        "source_receipt": source,
        "pre_krs_receipt": pre,
        "krs_run_receipt": run,
        "final_receipt": fin,
        "source_receipt_sha256": source.get("receipt_sha256"),
        "source_snapshot_sha256": (source.get("artifact") or {}).get("source_snapshot_sha256"),
        "requested_run_count": run["artifact"]["requested_run_count"],
        "actual_run_count": run["artifact"]["actual_run_count"],
        "input_sha256": run["artifact"]["input_sha256"],
        "output_sha256": run["artifact"]["output_sha256"],
        "final_ticket_sha256": fin["artifact"]["ticket_sha256"],
    }
    return legacy.signed_receipt("FORMAL", race_id, "FULL_FORMAL_E2E_PASS", artifact, [])


@app.post("/result")
def result(payload: Dict[str, Any]):
    return legacy.result(payload)
