"""Verify minimal race-key handoff without conflating SOURCE with signed FINAL."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from runtime import formal_execution_orchestrator as o
from runtime.local_race_key_intake import aware


class RaceKeyGateError(ValueError):
    pass


def certify(request: dict, entry_report: dict) -> dict:
    eid = request["execution_id"]
    source = o.resolve_phase(eid, "SOURCE")
    if source is None:
        raise RaceKeyGateError("SIGNED_SOURCE_CHECKPOINT_MISSING")
    o.validate_source_checkpoint(Path(source["run_dir"]), request)
    signed_source = o._load_checkpoint_json(source, "source_receipt_envelope.json")
    if not signed_source or not signed_source.get("receipt_sha256"):
        raise RaceKeyGateError("SIGNED_SOURCE_RECEIPT_MISSING")

    # A signed, coherent race universe can still be the WRONG start time if
    # the manual five-field trigger was supplied incorrectly. Never turn such
    # a SOURCE into a formal pre-race basis.
    artifact = signed_source.get("artifact") or {}
    official = artifact.get("source_race_context") or {}
    official_day = str(official.get("race_date") or "").replace("/", "-")
    if (official.get("venue_id") != request.get("venue_id")
            or official_day != request.get("race_date")
            or str(official.get("race_no")) != str(request.get("race_no"))):
        raise RaceKeyGateError("SIGNED_SOURCE_OFFICIAL_RACE_IDENTITY_MISMATCH")
    start = (artifact.get("normalized_evidence") or {}).get("start_time") or {}
    expected = aware(request.get("scheduled_post_at"), "SCHEDULED_POST")
    cutoff = aware(request.get("prediction_cutoff"), "PREDICTION_CUTOFF")
    if (start.get("authority") != "NAR_OFFICIAL" or start.get("cutoff_relation") != "PRE_CUTOFF"
            or str(start.get("value") or "") != expected.strftime("%H:%M")):
        raise RaceKeyGateError("SIGNED_SOURCE_OFFICIAL_POST_TIME_MISMATCH")
    try:
        frozen = datetime.fromisoformat(str(artifact["source_freeze_at"]).replace("Z", "+00:00"))
    except (KeyError, TypeError, ValueError) as exc:
        raise RaceKeyGateError("SOURCE_FREEZE_TIMESTAMP_INVALID") from exc
    if frozen.tzinfo is None or frozen.astimezone(timezone.utc) >= cutoff.astimezone(timezone.utc):
        raise RaceKeyGateError("SIGNED_SOURCE_FROZEN_AFTER_CUTOFF")

    status = str(entry_report.get("status") or "")
    report = {
        "execution_id": eid,
        "source_verified": True,
        "source_receipt_sha256": signed_source["receipt_sha256"],
        "formal_final_proven": False,
        "completion": False,
        "production_prediction_changed": False,
    }
    if status == "HOLD":
        code = str(entry_report.get("code") or "")
        normal_source_holds = {"STATIC_PREDICTION_FREEZE_REQUIRED", "ANALYSIS_ONLY_SOURCE_COMPLETE"}
        deadline_hold = (code == "DEADLINE_HOLD:FORMAL_INCOMPLETE"
                         and entry_report.get("prestart_deadline_expired") is True)
        if code not in normal_source_holds and not deadline_hold:
            raise RaceKeyGateError("UNEXPECTED_FORMAL_HOLD:" + code)
        if entry_report.get("formal_final_proven") is True:
            raise RaceKeyGateError("SOURCE_ONLY_FALSE_FINAL_CLAIM")
        # The SOURCE signature, official race clock, and pre-cutoff freeze
        # were verified above. Missing FORMAL must not falsify signed SOURCE.
        state = ("SOURCE_VERIFIED_FORMAL_DEADLINE_HOLD" if deadline_hold
                 else "SOURCE_VERIFIED_STATIC_PENDING")
        return {**report, "status": state, "reason": code}
    if o.completion_exit_code(entry_report) != 0:
        raise RaceKeyGateError("FORMAL_EXECUTION_NOT_COMPLETE:" + status)
    formal = o.resolve_phase(eid, "FORMAL")
    if formal is None:
        raise RaceKeyGateError("SIGNED_FINAL_CHECKPOINT_MISSING")
    flags = o._load_checkpoint_json(formal, "receipt_verifications.json") or {}
    temporal = o._load_checkpoint_json(formal, "final_before_post_verification.json") or {}
    final = o._load_checkpoint_json(formal, "final_receipt_envelope.json") or {}
    if (flags.get("SOURCE") is not True or flags.get("PRE_KRS") is not True
            or flags.get("KRS_RUN") is not True or flags.get("FINAL") is not True
            or temporal.get("verified") is not True or final.get("receipt_sha256") is None
            or (final.get("receipt") or {}).get("status") != "PASS"):
        raise RaceKeyGateError("SIGNED_FINAL_VERIFICATION_REQUIRED")
    if str(temporal.get("execution_id")) != eid or str(temporal.get("race_id")) != eid:
        raise RaceKeyGateError("FINAL_TEMPORAL_RACE_MISMATCH")
    return {**report, "status": "FULL_LIFECYCLE_EXECUTION_PASS",
            "formal_final_proven": True, "completion": True,
            "final_receipt_sha256": final["receipt_sha256"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--github-output")
    args = parser.parse_args()
    req = json.loads(Path(args.request).read_text(encoding="utf-8"))
    entry = json.loads(Path(args.report).read_text(encoding="utf-8"))
    result = certify(req, entry)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8") as output:
            output.write("execution_id=" + req["execution_id"] + "\n")
            output.write("formal_ready=" + str(result["formal_final_proven"]).lower() + "\n")
            output.write("source_verified=true\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
