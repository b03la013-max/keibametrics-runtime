"""Read-only, per-cell integrity audit of LOCAL 29-index numerical artifacts.

This is a research acceptance witness. A PASS means that a materializer output
is internally consistent with an independently supplied runner/index manifest;
not that SOURCE is licensed/signed, formula arithmetic independently correct,
Production prediction consumers authorized, or a FINAL delivered.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any


PROFILE = "KM-LOCAL-NUMERIC-CELL-GRID-INTEGRITY-CANDIDATE-v1"
STATUSES = ("CALCULATED", "RULED-NEUTRAL", "RULED-HOLD", "NOT-APPLICABLE")
COUNTER = {
    "CALCULATED": "calculated_count",
    "RULED-NEUTRAL": "ruled_neutral_count",
    "RULED-HOLD": "ruled_hold_count",
    "NOT-APPLICABLE": "not_applicable_count",
}


def _sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                      separators=(",", ":")).encode("utf-8")).hexdigest()


def _value_ok(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 100


def attest_cell_grid(materialized: dict, *, expected_indices: list[str],
                     expected_runner_ids: list[str]) -> dict:
    """Check all required runner/index cells against a caller-supplied frozen universe.

    This never mutates the input. The two expected manifests MUST come from the
    separately validated pre-cutoff race request, not materialized's own fields.
    In particular, the output does not assert an independent arithmetic replay.
    """
    issues: list[str] = []
    if (not isinstance(expected_indices, list) or len(expected_indices) != 29
            or any(not isinstance(x, str) or not x for x in expected_indices)
            or len(set(expected_indices)) != 29):
        issues.append("FROZEN_29_INDEX_MANIFEST_INVALID")
    if (not isinstance(expected_runner_ids, list) or not expected_runner_ids
            or any(not isinstance(x, str) or not x for x in expected_runner_ids)
            or len(set(expected_runner_ids)) != len(expected_runner_ids)):
        issues.append("FROZEN_RUNNER_MANIFEST_INVALID")
    if not isinstance(materialized, dict):
        materialized = {}
        issues.append("MATERIALIZED_ARTIFACT_MISSING")
    if materialized.get("required_indices") != expected_indices:
        issues.append("INDEX_MANIFEST_MISMATCH")
    runners = materialized.get("runners")
    if not isinstance(runners, list):
        issues.append("RUNNER_GRID_MISSING")
        runners = []
    observed_ids = [r.get("runner_id") if isinstance(r, dict) else None for r in runners]
    if (len(observed_ids) != len(expected_runner_ids)
            or len(set(str(i) for i in observed_ids)) != len(observed_ids)
            or set(observed_ids) != set(expected_runner_ids)):
        issues.append("RUNNER_UNIVERSE_MISMATCH")

    totals = {name: 0 for name in STATUSES}
    rows: list[dict] = []
    canonicals: list[dict] = []
    for runner in runners:
        if not isinstance(runner, dict):
            issues.append("RUNNER_RECORD_INVALID")
            continue
        rid = runner.get("runner_id")
        canonical = runner.get("canonical_components")
        if not isinstance(canonical, dict):
            issues.append(f"CANONICAL_COMPONENTS_MISSING:{rid}")
            continue
        canonicals.append(canonical)
        if set(canonical) != set(expected_indices):
            issues.append(f"CANONICAL_INDEX_SET_MISMATCH:{rid}")
        if runner.get("numerical_index_sha256") != _sha(canonical):
            issues.append(f"RUNNER_CELL_HASH_MISMATCH:{rid}")
        for idx in expected_indices:
            spec = canonical.get(idx)
            if not isinstance(spec, dict):
                issues.append(f"CELL_MISSING:{rid}:{idx}")
                continue
            status = spec.get("terminal_status")
            if status not in STATUSES:
                issues.append(f"CELL_TERMINAL_INVALID:{rid}:{idx}")
                continue
            if status in ("CALCULATED", "RULED-NEUTRAL") and not _value_ok(spec.get("value")):
                issues.append(f"CELL_NUMERIC_VALUE_INVALID:{rid}:{idx}")
            if not spec.get("rule_id") or not spec.get("evidence_refs") or not spec.get("source_fact"):
                issues.append(f"CELL_PROVENANCE_MISSING:{rid}:{idx}")
            totals[status] += 1
            rows.append({"runner_id": str(rid), "index": idx,
                         "terminal_status": status, "value": spec.get("value"),
                         "rule_id": spec.get("rule_id")})

    coverage = materialized.get("numeric_coverage")
    if not isinstance(coverage, dict):
        coverage = {}
        issues.append("NUMERIC_COVERAGE_MISSING")
    calculated, neutral = totals["CALCULATED"], totals["RULED-NEUTRAL"]
    expected_total = len(expected_indices) * len(expected_runner_ids)
    expected_counts = {
        "required_count": expected_total,
        "terminalized_count": len(rows),
        "numeric_value_count": calculated + neutral,
        "unresolved_count": expected_total - len(rows),
        **{field: totals[status] for status, field in COUNTER.items()},
    }
    for key, expected in expected_counts.items():
        if type(coverage.get(key)) is not int or coverage[key] != expected:
            issues.append("COVERAGE_COUNTER_MISMATCH:" + key)
    if not isinstance(coverage.get("unresolved"), list):
        issues.append("COVERAGE_UNRESOLVED_DETAIL_MISSING")
    elif len(coverage["unresolved"]) != expected_counts["unresolved_count"]:
        issues.append("COVERAGE_UNRESOLVED_DETAIL_MISMATCH")
    if materialized.get("index_terminalization_hash") != _sha(rows):
        issues.append("TERMINALIZATION_HASH_MISMATCH")
    if materialized.get("index_provenance_hash") != _sha(canonicals):
        issues.append("PROVENANCE_HASH_MISMATCH")

    full_terminal = len(rows) == expected_total
    full_numeric = (full_terminal and totals["RULED-HOLD"] == 0
                    and totals["NOT-APPLICABLE"] == 0)
    all_calculated = full_terminal and calculated == expected_total
    for key, expected in (("full_terminalization", full_terminal),
                          ("full_numerical_calculation", all_calculated),
                          ("full_numerical_closure", full_numeric),
                          ("strict_full_numerical_ready", full_numeric)):
        if materialized.get(key) is not expected:
            issues.append("NUMERICAL_CLOSURE_FLAG_MISMATCH:" + key)
    valid = not issues
    return {
        "profile": PROFILE,
        "status": "CELL_GRID_CONSISTENT" if valid else "CELL_GRID_INTEGRITY_FAILED",
        "structural_consistency_verified": valid,
        "required_cells": expected_total,
        "observed_terminal_cells": len(rows),
        "calculated_cells": calculated,
        "ruled_neutral_cells": neutral,
        "numeric_value_closure_structurally_verified": valid and full_numeric,
        "all_cells_calculated_structurally_verified": valid and all_calculated,
        "independent_arithmetic_recalculation": "NOT_PERFORMED",
        "source_signature_and_license_verification": "NOT_PERFORMED",
        "prediction_krs_ticket_capital_authorization": "NOT_EVALUATED_OR_GRANTED",
        "formal_final_delivery_proof": "NOT_PERFORMED",
        "issues": issues[:80],
        "additional_issue_count": max(0, len(issues) - 80),
    }
