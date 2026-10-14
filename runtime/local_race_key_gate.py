"""Verify minimal race-key handoff without conflating SOURCE with signed FINAL."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from runtime import formal_execution_orchestrator as o


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
        allowed = {"STATIC_PREDICTION_FREEZE_REQUIRED", "ANALYSIS_ONLY_SOURCE_COMPLETE"}
        if entry_report.get("code") not in allowed:
            raise RaceKeyGateError("UNEXPECTED_FORMAL_HOLD:" + str(entry_report.get("code")))
        if entry_report.get("formal_final_proven") is True:
            raise RaceKeyGateError("SOURCE_ONLY_FALSE_FINAL_CLAIM")
        return {**report, "status": "SOURCE_VERIFIED_STATIC_PENDING", "reason": entry_report.get("code")}
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
