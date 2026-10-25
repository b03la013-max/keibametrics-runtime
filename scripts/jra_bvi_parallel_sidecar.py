"""Overlap read-only cache warming with the existing Production wait.

The frozen five-file ENV implementation is called unchanged. Warming may read
an immutable main request as a *hint*, but that hint can never authorize a
prediction: the successful parent run's unique artifact must later contain the
same exact request and SOURCE bytes. All signature, timestamp, model, priority,
and cutoff checks are repeated by the ordinary freeze entry point.
"""
from __future__ import annotations

import argparse
import cProfile
from datetime import datetime, timezone, timedelta
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import pstats
import re
import subprocess
import sys
import time as clock
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "runtime"), str(ROOT / "runtime/jra_source_runtime")]
import jra_bvi_pipeline_forward_shadow as frozen

REPO = "b03la013-max/keibametrics-runtime"
PROFILE = "KM-JRA-BVI-PARALLEL-READONLY-PREWARM-v1"
MODEL = "runtime/jra_static_owner_forward_oos/models/bvi_env_20261024_5e7f3b31cebd.json"
MODEL_FILE_SHA = "a969cc518da73b4795932f02d8f3cbc6d0ac47a1a7904907055e46958d9f0fc1"
MODEL_SHA = "5e7f3b31cebd2e3ab11e2cd436a7a38988d0bba83488f6f0ef784f980fafd126"


def utcnow():
    return datetime.now(timezone.utc)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def verify_fixed_model(report, *, root=ROOT):
    raw = (root / MODEL).read_bytes()
    publication = json.loads(raw)
    if (digest(raw) != MODEL_FILE_SHA or publication["model"].get("model_sha256") != MODEL_SHA
            or any(digest((root / name).read_bytes()) != value
                for name, value in publication["code_file_sha256"].items())
            or set(publication["code_file_sha256"]) != set(frozen.ENV_CODE_FILES)):
        raise ValueError("BVI_SIDECAR_FIXED_MODEL_OR_CODE_CHANGED")
    report.update(fixed_model_file_sha256=MODEL_FILE_SHA, fixed_model_sha256=MODEL_SHA,
        fixed_model_and_bound_implementation_changed=False)


def job_budget_gate(deadline, report):
    """An additional denial-only transport gate; never replaces frozen checks.

    Python emits urllib.Request before opening the socket. Do not start a
    request whose ORIGINAL timeout plus ORIGINAL reserve exceeds the existing
    fifteen-minute ACTIVE budget or absolute GitHub job budget. No timeout or
    canonical clock is changed. Waiting for Production is a separate phase.
    """
    def gate(event, args):
        if event != "urllib.Request":
            return
        required = {"https://quorumprobe-production.up.railway.app/krs/execute": 450,
                    "https://quorumprobe-production.up.railway.app/verify": 60}.get(args[0])
        if required is not None and (deadline - utcnow()).total_seconds() < required:
            report["job_budget_rejection"] = {"observed_at": utcnow().isoformat(),
                "required_seconds": required, "job_deadline": deadline.isoformat()}
            raise ValueError("BVI_SIDECAR_JOB_BUDGET_TOO_SHORT_FOR_ORIGINAL_RPC")
    return gate


def gh_json(endpoint):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("BVI_SIDECAR_GITHUB_TOKEN_REQUIRED")
    request = urllib.request.Request("https://api.github.com/repos/" + REPO + endpoint,
        headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json"})
    # 403/429/auth failures propagate. No alternate identity or retry bypass.
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def resolve_intent(path, event_sha, *, root=ROOT):
    if not path:
        names = subprocess.check_output(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", event_sha],
            cwd=root, text=True).splitlines()
        names = [n for n in names if n.startswith("runtime/jra_formal_intents/") and n.endswith(".json")]
        if len(names) != 1:
            raise ValueError("BVI_SIDECAR_EXACT_INTENT_REQUIRED")
        path = names[0]
    relative = PurePosixPath(path)
    if (relative.is_absolute() or ".." in relative.parts or len(relative.parts) != 3
            or relative.parts[:2] != ("runtime", "jra_formal_intents") or relative.suffix != ".json"):
        raise ValueError("BVI_SIDECAR_INTENT_PATH_INVALID")
    intent = json.loads((root / relative).read_text())
    eid = str(intent.get("execution_id") or (str(intent.get("race_id") or "") + "-SINGLE-R1"))
    if (intent.get("family_id") != "JRA" or not re.fullmatch(r"KM-JRA-[A-Z]+-20\d{6}-R\d{2}", str(intent.get("race_id")))
            or not re.fullmatch(r"[A-Za-z0-9._-]+", eid) or ".." in eid):
        raise ValueError("BVI_SIDECAR_INTENT_IDENTITY_INVALID")
    return intent, eid


def require_identity(request, intent, eid):
    if (request.get("execution_id") != eid
            or any(request.get(k) != intent.get(k) for k in ("family_id", "race_id", "prediction_cutoff", "scheduled_post_at"))):
        raise ValueError("BVI_SIDECAR_PARENT_INTENT_BINDING_INVALID")
    frozen.require_open_window(request)  # Actual clock only; no caller clock override.


def profile_call(label, operation, report):
    started = utcnow(); monotonic = clock.monotonic(); profile = cProfile.Profile()
    profile.enable()
    try:
        return operation()
    finally:
        profile.disable()
        measured = []
        names = {"_verified_source", "_attested", "build_corpus", "compare", "environment_predictions_for_source",
                 "production_priority_window", "execute_diagnostic_downstream", "call", "priority_call",
                 "bind_production_reference", "arm_consumption", "load_environment_model_publication", "verify_signed_final",
                 "compile_static_owner", "compile_research_static", "_environment_arm"}
        for (filename, line, name), (primitive, calls, own, cumulative, _) in pstats.Stats(profile).stats.items():
            if name in names:
                measured.append({"file": Path(filename).name, "line": line, "function": name,
                    "calls": calls, "self_seconds": own, "cumulative_seconds": cumulative})
        report.setdefault("timings", {})[label] = {"started_at": started.isoformat(),
            "finished_at": utcnow().isoformat(), "wall_seconds": clock.monotonic() - monotonic,
            "profile": sorted(measured, key=lambda row: (row["file"], row["line"])),
            "scope": "CUMULATIVE_TIMES_OVERLAP; NO_PER_ARM_STATIC_CLOCK; call_IS_KRS_AND_VERIFY_HTTP_COMBINED"}


def prewarm(request_path, source_path, intent, eid, report, *, root=ROOT):
    request_raw = request_path.read_bytes(); source_raw = source_path.read_bytes()
    request = json.loads(request_raw); require_identity(request, intent, eid)
    checked = frozen._verified_source(source_path)
    if (checked is None or checked.get("source_snapshot_sha256") != request.get("source_snapshot_sha256")
            or checked.get("race_id") != request["race_id"]
            or not frozen._attested(source_path, not_after=frozen.time(request["prediction_cutoff"]))):
        raise ValueError("BVI_SIDECAR_PREWARM_SOURCE_UNVERIFIED")
    source = json.loads(source_raw)["artifact"]
    from jra_execution_maturity_bridge import verify_formal_request_binding
    if verify_formal_request_binding(request, json.loads(source_raw)).get("status") != "PASS":
        raise ValueError("BVI_SIDECAR_PREWARM_FORMAL_SOURCE_UNBOUND")
    card = source["jra_official_race_card_detail"]["runners"]
    now = frozen.require_open_window(request)
    corpus = frozen.build_corpus(root, prediction_cutoff=now.isoformat(), race_date=request["race_date"],
        exclude_race_id=request["race_id"], required_sires={r["sire"] for r in card if r.get("sire")},
        required_damsires={r["damsire"] for r in card if r.get("damsire")})
    # No features, Static, KRS, FINAL, model fit or prediction freeze is made.
    report["prewarm"] = {"request_file_sha256": digest(request_raw), "source_file_sha256": digest(source_raw),
        "source_snapshot_sha256": source["source_snapshot_sha256"], "available_at": now.isoformat(),
        "corpus_manifest_sha256": corpus["manifest_sha256"], "authority": "NON_AUTHORITATIVE_HINT_UNTIL_PARENT_ARTIFACT_MATCH",
        "predictions_created": 0, "external_krs_calls": 0}
    return report["prewarm"]


def refresh_main(root=ROOT):
    # Read-only remote fetch; local checkout only. Never pushes or dispatches.
    before = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    subprocess.run(["git", "pull", "--ff-only", "origin", "main"], cwd=root,
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=90)
    changed = subprocess.check_output(["git", "diff", "--name-only", before, "HEAD", "--",
        ":(glob)runtime/**/*.py", ":(glob)scripts/**/*.py", "mapping", "profiles", "governance", MODEL], cwd=root, text=True)
    if changed.strip():
        # Modules already imported before warming cannot be relabelled with a
        # newer on-disk algorithm SHA. A fresh independent run is required.
        raise ValueError("BVI_SIDECAR_LOADED_CODE_OR_AUTHORITY_CHANGED")


def warm_hint(intent, eid, report, *, root=ROOT):
    request_path = root / "runtime/requests" / (eid + "-FORMAL.json")
    if not request_path.is_file():
        return None
    request = json.loads(request_path.read_text()); require_identity(request, intent, eid)
    source_id = str(request.get("source_execution_id") or "")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", source_id) or ".." in source_id:
        raise ValueError("BVI_SIDECAR_PREWARM_SOURCE_EXECUTION_INVALID")
    candidates = []
    for path in (root / "runtime/executions" / source_id / "SOURCE/runs").glob("*/source_receipt_envelope.json"):
        artifact = json.loads(path.read_text()).get("artifact") or {}
        if artifact.get("source_snapshot_sha256") == request.get("source_snapshot_sha256"):
            candidates.append(path)
    if len(candidates) != 1:
        report["prewarm_hint_status"] = "ABSENT_OR_AMBIGUOUS; NO_HINT_ACCEPTED"
        return None
    return profile_call("read_only_prewarm", lambda: prewarm(request_path, candidates[0], intent, eid, report, root=root), report)


def download_parent_artifact(run_id, eid, cutoff, destination):
    result = gh_json(f"/actions/runs/{run_id}/artifacts?per_page=100")
    if result.get("total_count", 0) > 100:
        raise ValueError("BVI_SIDECAR_ARTIFACT_UNIVERSE_TOO_LARGE")
    name = f"km-jra-single-entry-{eid}-{run_id}"
    artifacts = [a for a in result.get("artifacts", []) if a.get("name") == name and not a.get("expired")]
    if len(artifacts) != 1:
        raise ValueError("BVI_SIDECAR_UNIQUE_PARENT_ARTIFACT_REQUIRED")
    artifact = artifacts[0]
    if (artifact.get("workflow_run", {}).get("id") != run_id
            or frozen.time(artifact["created_at"]) > cutoff or artifact.get("size_in_bytes", 0) > 64 * 1024 * 1024):
        raise ValueError("BVI_SIDECAR_PARENT_ARTIFACT_IDENTITY_OR_TIME_INVALID")
    raw = subprocess.check_output(["gh", "api", f"repos/{REPO}/actions/artifacts/{artifact['id']}/zip"], timeout=90)
    expected = str(artifact.get("digest") or "")
    if expected != "sha256:" + digest(raw):
        raise ValueError("BVI_SIDECAR_PARENT_ARTIFACT_PROVIDER_HASH_INVALID")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        members = archive.infolist()
        if len({m.filename for m in members}) != len(members):
            raise ValueError("BVI_SIDECAR_PARENT_ARTIFACT_DUPLICATE_PATH")
        if sum(m.file_size for m in members) > 512 * 1024 * 1024:
            raise ValueError("BVI_SIDECAR_PARENT_ARTIFACT_TOO_LARGE")
        if any(PurePosixPath(m.filename).is_absolute() or ".." in PurePosixPath(m.filename).parts for m in members):
            raise ValueError("BVI_SIDECAR_PARENT_ARTIFACT_UNSAFE_PATH")
        if archive.testzip() is not None:
            raise ValueError("BVI_SIDECAR_PARENT_ARTIFACT_CRC_INVALID")
        destination.mkdir(parents=True, exist_ok=False)
        archive.extractall(destination)
    return {"parent_run_id": run_id, "artifact_id": artifact["id"], "name": name,
        "provider_created_at": artifact["created_at"], "zip_sha256": digest(raw)}


def bind_parent_input(directory, intent, eid, hint, report, *, root=ROOT):
    request_path = directory / "jra_single_entry_formal_request.json"
    source_path = directory / "jra_single_entry_source_checkpoint/source_receipt_envelope.json"
    verification = json.loads((directory / "jra_formal_completion_verification.json").read_text())
    request_raw = request_path.read_bytes(); source_raw = source_path.read_bytes()
    request = json.loads(request_raw); require_identity(request, intent, eid)
    from jra_single_entry_outcome import verify_formal_completion_summary
    summaries = list((directory / "canonical_formal").glob("**/formal_execution_summary.json"))
    if len(summaries) != 1 or verify_formal_completion_summary(json.loads(summaries[0].read_text()), request) != verification:
        raise ValueError("BVI_SIDECAR_PARENT_COMPLETION_BINDING_INVALID")
    if hint and (hint["request_file_sha256"] != digest(request_raw) or hint["source_file_sha256"] != digest(source_raw)):
        raise ValueError("BVI_SIDECAR_PREWARM_PARENT_BYTES_DIFFER")
    final = json.loads((root / "runtime/final_artifacts" / (request["race_id"] + ".json")).read_text())
    if final.get("final_receipt_sha256") != verification["signed_final_receipt_sha256"]:
        raise ValueError("BVI_SIDECAR_PARENT_FINAL_RECEIPT_MISMATCH")
    # Signature, exact SOURCE/request/FINAL, all model/code hashes, fresh wall
    # clocks, priority and safe-window checks are owned by canonical freeze.
    report["parent_input"] = {"request_file_sha256": digest(request_raw), "source_file_sha256": digest(source_raw),
        "completion_file_sha256": digest((directory / "jra_formal_completion_verification.json").read_bytes()),
        "signed_final_receipt_sha256": verification["signed_final_receipt_sha256"],
        "warm_hint_matched": bool(hint), "acceptance": "SUCCESSFUL_ORIGINAL_RUN_ARTIFACT; HINT_ALONE_NEVER_SUFFICIENT"}
    return request_path, source_path, request


def verify_parent_final(request, report, *, root=ROOT):
    """Require the target's genuine signed FINAL before any research request.

    Receipt equality with a successful workflow artifact is content binding,
    not signature verification. Use the same CURRENT authority and live trust
    anchor as canonical freeze, before allowing that entry point to do work.
    """
    from jra_delivery import verify_signed_final
    observed = frozen.require_open_window(request)
    authority_path, authority = frozen.resolve_current_authority(root, now=observed)
    if frozen.time(authority["effective_at"]) > frozen.time(request["prediction_cutoff"]):
        raise ValueError("BVI_SIDECAR_PARENT_AUTHORITY_AFTER_CUTOFF")
    contracts = json.loads((root / authority["common_family_components"]["family_runtime_contracts_profile"]).read_text())
    contract = contracts["families"]["JRA"]
    final_raw = (root / "runtime/final_artifacts" / (request["race_id"] + ".json")).read_bytes()
    final = json.loads(final_raw)
    if (any(final.get(k) != request.get(k) for k in
            ("race_id", "source_snapshot_sha256", "prediction_cutoff", "scheduled_post_at"))
            or final.get("final_receipt_sha256") != report["parent_input"]["signed_final_receipt_sha256"]):
        raise ValueError("BVI_SIDECAR_PARENT_FINAL_REQUEST_BINDING_INVALID")
    with urllib.request.urlopen(contract["external_endpoint"].rstrip("/") + "/health", timeout=20) as response:
        health = json.load(response)
    verify_signed_final(final, health, contract)
    completed = frozen.require_open_window(request)
    signed_at = frozen.time(final["final_receipt"]["receipt"]["timestamp"])
    if signed_at > min(observed, frozen.time(request["prediction_cutoff"])):
        raise ValueError("BVI_SIDECAR_PARENT_FINAL_TIMESTAMP_INVALID")
    report["parent_final_verified"] = {"observed_at": observed.isoformat(),
        "completed_at": completed.isoformat(), "signature_verified": True,
        "final_file_sha256": digest(final_raw), "final_receipt_sha256": final["final_receipt_sha256"],
        "authority_file": str(authority_path.relative_to(root)),
        "health_sha256": frozen.sha(health), "external_krs_calls": 0}


def run(run_id, intent_path, event_sha, report, *, root=ROOT):
    intent, eid = resolve_intent(intent_path, event_sha, root=root)
    cutoff = frozen.time(intent["prediction_cutoff"])
    parent = gh_json(f"/actions/runs/{run_id}")
    if (parent.get("id") != run_id or parent.get("repository", {}).get("full_name") != REPO
            or parent.get("head_repository", {}).get("full_name") != REPO or parent.get("head_branch") != "main"
            or parent.get("head_sha") != event_sha
            or parent.get("path") != ".github/workflows/km-jra-formal-single-entry.yml"):
        raise ValueError("BVI_SIDECAR_PARENT_RUN_INVALID")
    verify_fixed_model(report, root=root)
    report["final_present_at_launcher"] = (root / "runtime/final_artifacts" / (intent["race_id"] + ".json")).exists()
    hint = None; started = clock.monotonic(); last_refresh = -120.0; job_deadline = wait_deadline = None
    report.update(parent_run_id=run_id, parent_event_sha=parent.get("head_sha"), race_id=intent["race_id"],
        prediction_cutoff=intent["prediction_cutoff"], wait_started_at=utcnow().isoformat())
    while True:
        if (utcnow() >= cutoff or clock.monotonic() - started >= 15 * 60
                or (wait_deadline and utcnow() >= wait_deadline)):
            report["status"] = "PENDING; PARENT_WAIT_BUDGET_OR_CUTOFF_EXPIRED"
            return None
        jobs = gh_json(f"/actions/runs/{run_id}/jobs?per_page=100")
        own = [j for j in jobs.get("jobs", []) if j.get("name") == "pedigree-forward-shadow"]
        if len(own) != 1 or not own[0].get("started_at"):
            raise ValueError("BVI_SIDECAR_ACTUAL_JOB_START_REQUIRED")
        actual_start = frozen.time(own[0]["started_at"])
        if actual_start > utcnow():
            raise ValueError("BVI_SIDECAR_FUTURE_JOB_CLOCK")
        actual_deadline = actual_start + timedelta(minutes=30)
        if job_deadline is not None and job_deadline != actual_deadline:
            raise ValueError("BVI_SIDECAR_JOB_CLOCK_CHANGED")
        job_deadline = actual_deadline
        wait_deadline = actual_start + timedelta(minutes=15)
        report.update(github_job_started_at=own[0]["started_at"], job_deadline=job_deadline.isoformat(),
            wait_deadline=wait_deadline.isoformat())
        if utcnow() >= wait_deadline:
            report["status"] = "PENDING; PARENT_WAIT_BUDGET_OR_CUTOFF_EXPIRED"
            return None
        producers = [j for j in jobs.get("jobs", []) if j.get("name") == "orchestrate"]
        if jobs.get("total_count", 0) > 100 or len(producers) > 1:
            raise ValueError("BVI_SIDECAR_UNIQUE_PARENT_JOB_REQUIRED")
        if not producers:
            clock.sleep(min(60, max(0, (cutoff - utcnow()).total_seconds())))
            continue
        producer = producers[0]
        if producer.get("status") == "completed":
            report["parent_completed_at"] = producer.get("completed_at")
            report["parent_conclusion"] = producer.get("conclusion")
            if producer.get("conclusion") != "success":
                report["status"] = "PENDING; PRODUCTION_PARENT_NOT_SUCCESSFUL"
                return None
            break
        if clock.monotonic() - last_refresh >= 120:
            refresh_main(root); last_refresh = clock.monotonic()
            if hint is None and not report["final_present_at_launcher"]:
                hint = warm_hint(intent, eid, report, root=root)
        clock.sleep(min(60, max(0, (cutoff - utcnow()).total_seconds())))
    report["wait_finished_at"] = utcnow().isoformat()
    report["artifact"] = download_parent_artifact(run_id, eid, cutoff, root / "runtime_out/pedigree_forward_input")
    refresh_main(root)
    verify_fixed_model(report, root=root)
    request_path, source_path, request = bind_parent_input(root / "runtime_out/pedigree_forward_input", intent, eid, hint, report, root=root)
    output = root / "runtime/jra_static_owner_forward_oos" / request["race_id"] / "pedigree_env_pre_result.json"
    if output.exists():
        report["status"] = "ALREADY_FROZEN; NO_DUPLICATE"
        return None
    profile_call("parent_final_signature_verification", lambda: verify_parent_final(request, report, root=root), report)
    active_started = utcnow()
    active_deadline = min(job_deadline, active_started + timedelta(minutes=15)) if job_deadline else active_started
    report.update(active_started_at=active_started.isoformat(), active_deadline=active_deadline.isoformat())
    if (active_deadline - active_started).total_seconds() < 450:
        report["status"] = "PENDING; JOB_BUDGET_TOO_SHORT_FOR_CANONICAL_REQUEST"
        return None
    # Existing canonical priority checks still run before every request. This
    # observer can only deny an additional unsafe launch; it cannot admit one.
    sys.addaudithook(job_budget_gate(active_deadline, report))
    report["canonical_freeze_started_at"] = utcnow().isoformat()
    result = profile_call("canonical_freeze", lambda: frozen.freeze(request_path, source_path, output,
        environment_model_path=root / MODEL), report)
    report.update(status="CANONICAL_PRE_RESULT_FROZEN; INDEPENDENT_WITNESS_STILL_REQUIRED",
        prediction_sha256=result["sha256"], canonical_freeze_finished_at=utcnow().isoformat())
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as out:
            out.write("output=" + output.relative_to(root).as_posix() + "\n")
    return result


def delivery_timing(run_id, attempt):
    """Observe already executed steps; this report admits no OOS sample."""
    jobs = gh_json(f"/actions/runs/{run_id}/attempts/{attempt}/jobs?per_page=100")
    own = [j for j in jobs.get("jobs", []) if j.get("name") == "pedigree-forward-shadow"]
    if jobs.get("total_count", 0) > 100 or len(own) != 1:
        raise ValueError("BVI_SIDECAR_UNIQUE_TIMING_JOB_REQUIRED")
    phases = []
    for step in own[0].get("steps", []):
        start, end = step.get("started_at"), step.get("completed_at")
        phases.append({"name": step["name"], "status": step.get("status"), "conclusion": step.get("conclusion"),
            "started_at": start, "completed_at": end,
            "wall_seconds": (frozen.time(end) - frozen.time(start)).total_seconds() if start and end else None})
    artifacts = gh_json(f"/actions/runs/{run_id}/artifacts?per_page=100")
    name = f"jra-pedigree-env-pre-cutoff-{run_id}-{attempt}"
    witnesses = [{k: a.get(k) for k in ("id", "name", "created_at", "digest", "expired")}
        for a in artifacts.get("artifacts", []) if a.get("name") == name]
    return {"profile": PROFILE, "scope": "OBSERVED_PROVIDER_METADATA_ONLY; NOT_A_NEW_WITNESS_OR_OOS_ADMISSION",
        "run_id": run_id, "run_attempt": attempt, "job_id": own[0]["id"],
        "observed_at": utcnow().isoformat(), "steps": phases, "existing_witness_metadata": witnesses}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--intent-path", default="")
    parser.add_argument("--event-sha", required=True)
    parser.add_argument("--delivery-timing-only", action="store_true")
    args = parser.parse_args()
    if args.delivery_timing_only:
        save(ROOT / "runtime_out/jra_bvi_forward_delivery_timing.json",
            delivery_timing(args.run_id, int(os.environ["GITHUB_RUN_ATTEMPT"])))
        sys.exit(0)
    report = {"profile": PROFILE, "launcher_started_at": utcnow().isoformat(), "status": "STARTED",
        "launcher_file_sha256": digest(Path(__file__).read_bytes()),
        "launcher_checkout_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "production_effect": "NONE", "forward_oos_increment": 0,
        "fixed_model_and_bound_implementation_changed": "NOT_YET_VERIFIED", "job_timeout_minutes": 30,
        "production_wait_budget_minutes": 15, "active_research_budget_minutes": 15,
        "safety_policy": "UNCHANGED_CANONICAL_600S_CAP_420S_RPC_30S_RESERVE_120S_MARGIN"}
    try:
        run(args.run_id, args.intent_path, args.event_sha, report)
    except Exception as exc:
        report.update(status="NOT_FROZEN", reason=type(exc).__name__ + ":" + str(exc))
        save(ROOT / "runtime_out/jra_bvi_forward_freeze_failure.json", {"profile": frozen.PROFILE,
            "status": "NOT_FROZEN", "first_failed_operation": "FORWARD_COMPARISON_FREEZE",
            "reason": report["reason"], "recorded_at": utcnow().isoformat(),
            "production_effect": "NONE", "forward_oos_increment": 0})
        raise
    finally:
        report["launcher_finished_at"] = utcnow().isoformat()
        save(ROOT / "runtime_out/jra_bvi_forward_timing.json", report)
