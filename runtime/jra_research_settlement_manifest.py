"""Mandatory operational manifest for existing, strictly separate research lanes.

Workflow colour and model utility are deliberately different measurements.
This module never calculates a prediction, changes a cohort, signs a RESULT,
buys tickets or promotes a model. It runs the existing settlement entry points.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

PROFILE = "KM-JRA-RESEARCH-SETTLEMENT-MANIFEST-v1"
STAGES = ("source_candidate", "static_owner", "bvi_env")
STAGE_PROFILES = {
    "source_candidate": "KM-JRA-CANDIDATE-AUTOMATIC-POSTRESULT-CLOSEDLOOP-20261010-R1",
    "static_owner": "JRA-STATIC-OWNER-INDEPENDENT-FORWARD-OOS",
    "bvi_env": "KM-JRA-BVI-CURRENT-POLICY-THREE-ARM-FORWARD-SHADOW-v1",
}


def summarize_races(rows):
    counts = {key: 0 for key in ("success_count", "failure_count", "retry_count",
        "unresolved_count", "not_due_count", "already_complete_count", "outside_cohort_count",
        "diagnostic_settled_count")}
    for row in rows:
        status = str(row.get("status") or "")
        if status in {"ALREADY_SETTLED", "ALREADY_SETTLED_DIAGNOSTIC_NOT_OOS"}:
            counts["already_complete_count"] += 1
            if status == "ALREADY_SETTLED_DIAGNOSTIC_NOT_OOS":
                counts["diagnostic_settled_count"] += 1
        elif status in {"SETTLED", "SETTLED_RECOMMENDATION", "DIAGNOSTIC_SETTLED_NOT_OOS"}:
            counts["success_count"] += 1
            if status == "DIAGNOSTIC_SETTLED_NOT_OOS":
                counts["diagnostic_settled_count"] += 1
        elif status in {"RESULT_NOT_YET_DUE", "PRE_RESULT_NOT_FROZEN", "NOT_APPLICABLE"}:
            counts["not_due_count"] += 1
        elif status == "OUTSIDE_CURRENT_COHORT":
            counts["outside_cohort_count"] += 1
        else:
            counts["unresolved_count"] += 1
            pending = status.startswith("PENDING") or row.get("retryable") is True
            counts["retry_count" if pending else "failure_count"] += 1
    done = counts["success_count"] + counts["already_complete_count"]
    status = ("PARTIAL" if done else "BLOCKED" if counts["failure_count"] else "PENDING") if counts["unresolved_count"] else (
        "VERIFIED_COMPLETE" if done else "NOT_APPLICABLE")
    return {"profile": PROFILE, "status": status, **counts, "processed": rows,
            "predictive_improvement_demonstrated": False, "production_effect": "NONE"}


def _json_output(text):
    for line in reversed(text.splitlines()):
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise ValueError("RESEARCH_STAGE_STRUCTURED_OUTPUT_MISSING")


def run_stage(stage, command, *, directory, root, runner=subprocess.run):
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    output = {"profile": PROFILE, "stage": stage, "started_at": started}
    try:
        result = runner(command, cwd=root, capture_output=True, text=True, timeout=600)
        (directory / (stage + ".stdout.log")).write_text(result.stdout)
        (directory / (stage + ".stderr.log")).write_text(result.stderr)
        payload = _json_output(result.stdout)
        if payload.get("profile") != STAGE_PROFILES[stage]:
            raise ValueError("RESEARCH_STAGE_OUTPUT_PROFILE_INVALID")
        if stage == "bvi_env":
            # Keep fixed ENV and Source-derived/ABC counts in different fields.
            env = payload.get("environment_candidate")
            if not isinstance(env, dict) or env.get("profile") != "KM-JRA-BVI-ENV-FOUR-ARM-FORWARD-SHADOW-v1":
                raise ValueError("RESEARCH_FIXED_ENV_SCORECARD_MISSING")
            rows = [{"race_id": r.get("race_id"), "status": "BLOCKED",
                     "reason": r.get("reason"), "retryable": False} for r in payload.get("race_failures") or []]
            settled = {rid for cohort in (env.get("cohorts") or {}).values() for rid in cohort.get("race_ids", [])}
            failed = {r["race_id"] for r in rows}
            for path in sorted((Path(root) / "runtime/jra_static_owner_forward_oos").glob("*/pedigree_env_pre_result.json")):
                pre = json.loads(path.read_text())
                rid = pre["race_id"]
                if rid in failed:
                    continue
                post = datetime.fromisoformat(pre["scheduled_post_at"].replace("Z", "+00:00"))
                if post.tzinfo is None:
                    raise ValueError("RESEARCH_ENV_POST_TIMEZONE_REQUIRED")
                status = ("ALREADY_SETTLED" if rid in settled else "RESULT_NOT_YET_DUE"
                          if post >= datetime.now(timezone.utc) else "PENDING_RESULT_OR_ADMISSION")
                rows.append({"race_id": rid, "status": status, "retryable": status.startswith("PENDING")})
            manifest = summarize_races(rows)
            output["fixed_environment_scorecard"] = env
            output["other_pipeline_scorecard_count_not_pooled"] = payload.get("eligible_settled_races")
        else:
            rows = payload.get("processed")
            if rows is None:
                rows = (payload.get("processing_manifest") or {}).get("processed")
            if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
                raise ValueError("RESEARCH_STAGE_RACE_MANIFEST_MISSING")
            manifest = summarize_races(rows)
        output.update(manifest=manifest, status=manifest["status"], returncode=result.returncode)
        if result.returncode and not manifest["unresolved_count"]:
            manifest["failure_count"] += 1; manifest["unresolved_count"] += 1
            manifest["status"] = output["status"] = "PARTIAL" if manifest["success_count"] else "BLOCKED"
    except Exception as exc:
        output.update(status="BLOCKED", error=type(exc).__name__ + ":" + str(exc),
                      returncode=2, manifest=summarize_races([
                          {"status": "BLOCKED", "reason": type(exc).__name__ + ":" + str(exc)}]))
    output["completed_at"] = datetime.now(timezone.utc).isoformat()
    path = directory / (stage + ".json")
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    return output


def collect(directory, *, required_outcomes=None):
    directory = Path(directory); stages = {}
    for name in STAGES:
        path = directory / (name + ".json")
        if path.exists():
            try:
                report = json.loads(path.read_text())
                if report.get("profile") != PROFILE or report.get("stage") != name:
                    raise ValueError("REQUIRED_STAGE_MANIFEST_IDENTITY_INVALID")
                expected = summarize_races(report["manifest"]["processed"])
                # A nonzero process may add one explicit process failure; the
                # structured row counts otherwise must agree with actual rows.
                if report.get("returncode"):
                    if not expected["unresolved_count"]:
                        expected["failure_count"] += 1
                        expected["unresolved_count"] += 1
                if any(report["manifest"].get(k) != expected[k] for k in (
                        "success_count", "failure_count", "retry_count", "unresolved_count",
                        "not_due_count", "already_complete_count", "outside_cohort_count", "diagnostic_settled_count")):
                    raise ValueError("REQUIRED_STAGE_MANIFEST_COUNTS_INVALID")
                stages[name] = report
            except (OSError, ValueError, KeyError, TypeError) as exc:
                stages[name] = {"status": "BLOCKED", "manifest": summarize_races([
                    {"status": "BLOCKED", "reason": str(exc)}])}
        else:
            stages[name] = {"status": "NOT_EXECUTED", "manifest": summarize_races([
                {"status": "BLOCKED", "reason": "REQUIRED_STAGE_MANIFEST_MISSING"}])}
    counts = {key: sum((row.get("manifest") or {}).get(key, 0) for row in stages.values())
              for key in ("success_count", "failure_count", "retry_count", "unresolved_count",
                          "not_due_count", "already_complete_count", "outside_cohort_count", "diagnostic_settled_count")}
    failures = {name: status for name, status in (required_outcomes or {}).items() if status != "success"}
    counts["failure_count"] += len(failures); counts["unresolved_count"] += len(failures)
    done = counts["success_count"] + counts["already_complete_count"]
    status = ("PARTIAL" if done else "BLOCKED" if counts["failure_count"] else "PENDING") if counts["unresolved_count"] else "VERIFIED_COMPLETE"
    return {"profile": PROFILE, "status": status, **counts, "required_stages": stages,
            "required_auxiliary_failures": failures, "cohort_counts_pooled": False,
            "counts_are_operational_records_not_independent_races": True,
            "model_performance_improvement_claimed": False, "production_effect": "NONE"}


def main():
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="action", required=True)
    run = sub.add_parser("run"); run.add_argument("--stage", choices=STAGES, required=True)
    run.add_argument("--directory", default="runtime_out/research_settlement")
    run.add_argument("command", nargs=argparse.REMAINDER)
    summary = sub.add_parser("collect"); summary.add_argument("--directory", default="runtime_out/research_settlement")
    summary.add_argument("--output", default="runtime_out/jra_research_settlement_manifest.json")
    summary.add_argument("--outcomes", default="{}")
    check = sub.add_parser("gate"); check.add_argument("--manifest", default="runtime_out/jra_research_settlement_manifest.json")
    args = parser.parse_args()
    if args.action == "run":
        command = args.command[1:] if args.command[:1] == ["--"] else args.command
        if not command:
            parser.error("stage command required")
        out = run_stage(args.stage, command, directory=args.directory, root=Path.cwd())
        print(json.dumps(out, ensure_ascii=False)); return 0 if out["returncode"] == 0 else 2
    if args.action == "collect":
        out = collect(args.directory, required_outcomes=json.loads(args.outcomes))
        path = Path(args.output); path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(out, ensure_ascii=False)); return 0
    out = json.loads(Path(args.manifest).read_text())
    print(json.dumps({"status": out["status"], "failure_count": out["failure_count"],
                      "retry_count": out["retry_count"], "unresolved_count": out["unresolved_count"]}))
    return 0 if out["status"] == "VERIFIED_COMPLETE" and out["unresolved_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
