"""Read signed FINAL's existing frozen numerical evidence without changing FINAL.

No signer, license, arithmetic, delivery or consumer permission is proven here.
Missing or malformed evidence is explicitly UNKNOWN; never implicitly zero.
"""
from __future__ import annotations
import json
from pathlib import Path
import re

from runtime import formal_execution_orchestrator as o


def frozen_numeric_readback(execution_id: str, formal: dict, root: Path) -> dict:
    from runtime.local_race_key_gate import attest_numeric_quality, attest_frozen_numeric_counts

    result = {
        "numeric_evidence_quality": attest_numeric_quality({}),
        "numeric_checkpoint_consistency": {
            "status": "NUMERICAL_REPORT_COUNTS_UNVERIFIED",
            "consistency_verified": False,
            "independent_index_evaluation": "NOT_PERFORMED"},
        "numeric_evidence_scope": "FROZEN_LEDGER_COUNTS_ONLY",
        "independent_formula_recalculation": "NOT_PERFORMED",
        "numerical_consumer_permissions": "NOT_GRANTED_BY_READBACK",
        "numeric_readback_error": None,
    }
    if not isinstance(formal, dict):
        return {**result, "numeric_readback_error": "FORMAL_CHECKPOINT_UNAVAILABLE"}
    rid = (formal.get("latest") or {}).get("run_id")
    if not isinstance(rid, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,180}", rid):
        return {**result, "numeric_readback_error": "FORMAL_RUN_ID_INVALID"}
    root = Path(root)
    path = root / "runtime/execution_reports" / execution_id / (rid + ".json")
    if not path.is_file():
        return {**result, "numeric_readback_error": "ORIGINAL_ENTRY_REPORT_NOT_FOUND"}
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(report, dict):
            raise ValueError("REPORT_NOT_OBJECT")
        listed = (formal.get("manifest") or {}).get("files") or {}
        mat = o._load_checkpoint_json(formal, "numerical_materialization_summary.json") if (
            "numerical_materialization_summary.json" in listed) else None
        stage = o._load_checkpoint_json(formal, "mandatory_stage_manifest.json") if (
            "mandatory_stage_manifest.json" in listed) else None
        # Never trust the report's counts until it has been bound to the
        # immutable FORMAL stage's actual execution/race identity.
        # A non-matching report must not claim 348 CALCULATED or source quality
        # merely because its own JSON counters are internally consistent.
        completion = report.get("completion")
        if not isinstance(completion, dict) or not isinstance(stage, dict):
            raise ValueError("R7_NUMERIC_STAGE_IDENTITY_UNAVAILABLE")
        expected_race = stage.get("race_id")
        if (report.get("family_id") != "LOCAL"
                or report.get("execution_id") != execution_id
                or completion.get("execution_id") != execution_id
                or stage.get("execution_id") != execution_id
                or not isinstance(expected_race, str)
                or not expected_race.startswith("KM-LOCAL-")
                or report.get("race_id") != expected_race
                or completion.get("race_id") != expected_race
                or completion.get("phase") != "FORMAL"):
            raise ValueError("R7_NUMERIC_REPORT_STAGE_RACE_IDENTITY_MISMATCH")
        quality = attest_numeric_quality(report)
        consistency = attest_frozen_numeric_counts(report, mat, stage)
        if not consistency["consistency_verified"]:
            return {**result,
                    "numeric_evidence_quality": {
                        "status": "NUMERICAL_UNVERIFIED_FROZEN_COUNTER_MISMATCH",
                        "all_cells_calculated": False,
                        "reported_numeric_value_closure": False,
                        "independent_evidence_verification": "NOT_PERFORMED"},
                    "numeric_checkpoint_consistency": consistency,
                    "numeric_readback_error": "NUMERIC_REPORT_MATERIALIZED_MANIFEST_MISMATCH"}
        severity = ("NUMERICALLY_DEGRADED" if quality["status"] in {
            "NUMERICAL_HELD_OR_UNRESOLVED", "NUMERICAL_NOT_APPLICABLE_PRESENT",
            "NUMERICAL_COUNTS_INVALID", "NUMERICAL_COUNTS_NOT_REPORTED"
        } else ("NUMERICALLY_NEUTRALIZED" if quality["status"] ==
                  "NUMERICAL_RULED_NEUTRAL_ONLY" else "NUMERICALLY_TERMINALIZED"))
        return {**result, "numeric_evidence_verdict": severity,
                "numeric_evidence_quality": quality,
                "numeric_checkpoint_consistency": consistency,
                "frozen_execution_class": (completion.get("execution_class", "UNKNOWN")
                                           if isinstance(completion, dict) else "UNKNOWN")}
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return {**result, "numeric_readback_error":
                "NUMERIC_LEDGER_READBACK_FAILED:" + type(exc).__name__}
