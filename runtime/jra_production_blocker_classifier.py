"""Separate the FIRST actual JRA Production blocked stage from independent blockers.

Diagnostic and routing only. This module never computes an index, never
materializes a Static prediction, never grants authority and never changes a
coverage threshold or weight. It answers three questions for one prepared
Production numerical report:

1. Where does the canonical pipeline actually stop first?
2. Which later stages would independently stop it even if the first were fixed?
3. Which zero-exposure terminal (if any) is the correct one for that stop?

Structural feasibility uses the *coarse* per-feature ``fact_available`` flag of
the source feature trace as an OPTIMISTIC upper bound. If an index cannot reach
its existing minimum coverage weight even when every fact-available feature is
assumed evaluable, the index is proven unclosable by evaluator work alone and
the owner is SOURCE ACQUISITION. The converse is never claimed: an index that
is closable under the upper bound is NOT proven closable.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

PROFILE = "KM-JRA-PRODUCTION-BLOCKER-CLASSIFIER-v1-20261010"
BASE = ("HPI", "SSI", "CFI", "RFI", "BVI", "JTI", "CSI",
        "TRI", "BWI", "GCI", "PRI", "KGI", "VMI")

STAGE_SOURCE = "SIGNED_SOURCE_OR_PREPARATION"
STAGE_NUMERICAL = "PRODUCTION_FEATURE_INDEX_CLOSURE"
STAGE_OWNER_AUTH = "PRODUCTION_STATIC_OWNER_AUTHORIZATION"
STAGE_OWNER_EXEC = "PRODUCTION_STATIC_OWNER_EXECUTION"
STAGE_TEMPORAL = "PREDICTION_CUTOFF_OR_DISPATCH_DEADLINE"

ROUTE_FORMAL = "FORMAL_PRE_KRS_HANDOFF"
ROUTE_EVIDENCE_NO_BET = "EVIDENCE_INSUFFICIENT_NO_BET"
ROUTE_STATIC_NO_BET = "STATIC_OWNER_UNAUTHORIZED_NO_BET"
ROUTE_FAIL_CLOSED = "FAIL_CLOSED_NO_TERMINAL"


def _time(value: Any):
    try:
        d = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return d.astimezone(timezone.utc) if d.tzinfo else None
    except (TypeError, ValueError):
        return None


def owner_activation_status(current_authority: dict | None, *, root: str = ".") -> dict:
    """Read-only view of the independent Static Owner activation gate."""
    try:
        from jra_production_auto_handoff import require_independent_owner_activation
    except ImportError:  # pragma: no cover - package import path
        from .jra_production_auto_handoff import require_independent_owner_activation
    if not isinstance(current_authority, dict):
        return {"authorized": False, "reason": "CURRENT_AUTHORITY_UNAVAILABLE"}
    try:
        require_independent_owner_activation(current_authority, root=root)
    except ValueError as exc:
        return {"authorized": False, "reason": str(exc),
                "manifest_id": current_authority.get("manifest_id")}
    return {"authorized": True, "reason": None,
            "manifest_id": current_authority.get("manifest_id")}


def structural_closure_feasibility(report: dict, mapping: dict) -> dict:
    """Upper-bound proof of which Base13 cells evaluator work can never close."""
    coverage = report.get("base_index_coverage_diagnostic") or {}
    traces = ((report.get("source_feature_report") or {}).get("runners") or {})
    cells = []
    by_index: dict[str, dict[str, int]] = {}
    missing_family: dict[str, int] = {}
    for row in coverage.get("rows") or []:
        profile = row.get("profile")
        index = row.get("index_id")
        rid = str(row.get("runner_id") or "")
        stat = by_index.setdefault(str(index), {"cells": 0, "met_now": 0,
                                                "upper_bound_closable": 0,
                                                "structurally_unclosable": 0})
        stat["cells"] += 1
        if row.get("status") != "BLOCKED":
            stat["met_now"] += 1
            stat["upper_bound_closable"] += 1
            continue
        if profile not in (mapping.get("index_profiles") or {}):
            stat["structurally_unclosable"] += 1
            cells.append({"runner_id": rid, "index_id": index, "profile": profile,
                          "class": "PROFILE_UNRESOLVED", "upper_bound_weight": 0.0,
                          "required_weight": None, "unavailable_fact_features": []})
            continue
        weights = mapping["index_profiles"][profile][index]
        required = float(mapping["profiles"][profile]["minimum_index_coverage_weight"])
        trace = ((traces.get(rid) or {}).get("source_feature_trace") or {}).get("features") or {}
        available_now = set(row.get("available_features") or [])
        bound = 0.0
        unavailable = []
        for feature, weight in weights.items():
            t = trace.get(feature) or {}
            if feature in available_now or t.get("fact_available") is True:
                bound += float(weight)
            else:
                family = str(t.get("source_family") or "UNKNOWN")
                unavailable.append({"feature": feature, "weight": float(weight),
                                    "source_family": family})
        if bound + 1e-12 >= required:
            stat["upper_bound_closable"] += 1
            continue
        stat["structurally_unclosable"] += 1
        for item in unavailable:
            missing_family[item["source_family"]] = missing_family.get(item["source_family"], 0) + 1
        cells.append({"runner_id": rid, "index_id": index, "profile": profile,
                      "class": "SOURCE_FACT_ACQUISITION_REQUIRED",
                      "upper_bound_weight": round(bound, 6),
                      "required_weight": required,
                      "unavailable_fact_features": unavailable})
    unclosable_indices = sorted(i for i, s in by_index.items() if s["structurally_unclosable"])
    return {
        "schema": "KM-JRA-BASE13-STRUCTURAL-CLOSURE-FEASIBILITY-v1",
        "method": "UPPER_BOUND_ASSUMES_EVERY_FACT_AVAILABLE_FEATURE_EVALUABLE",
        "proves_unclosable_only": True,
        "proves_closable": False,
        "mapping_id": mapping.get("mapping_id"),
        "index_summary": by_index,
        "structurally_unclosable_cell_count": len(cells),
        "structurally_unclosable_indices": unclosable_indices,
        "evaluator_work_alone_can_close_full20": not cells,
        "missing_source_family_counts": dict(sorted(missing_family.items(), key=lambda kv: (-kv[1], kv[0]))),
        "cells": cells,
        "threshold_or_weight_change": False,
    }


def classify_production_blockers(report: dict, *, owner_status: dict,
                                 intent: dict | None = None,
                                 now: str | None = None,
                                 feasibility: dict | None = None) -> dict:
    """Order blockers by the canonical pipeline and choose the terminal route."""
    blockers = []
    numerical_ready = (
        report.get("production_full_numerical_ready") is True
        and report.get("verified_full_index_count") == report.get("required_index_count")
        and int(report.get("required_index_count") or 0) > 0
    )
    if not numerical_ready:
        detail = {
            "stage": STAGE_NUMERICAL,
            "code": "JRA_AUTHORIZED_FULL20_INCOMPLETE",
            "required_index_count": report.get("required_index_count"),
            "verified_full_index_count": report.get("verified_full_index_count"),
            "partial_base_calculated_count": report.get("partial_base_calculated_count"),
            "partial_base_blocked_count": report.get("partial_base_blocked_count"),
            "first_error": report.get("production_numerical_error"),
        }
        if feasibility is not None:
            detail["subclass"] = (
                "STRUCTURAL_SOURCE_FACT_GAP"
                if feasibility.get("structurally_unclosable_cell_count") else
                "EVALUATOR_OR_AUTHORITY_GAP"
            )
            detail["structurally_unclosable_indices"] = feasibility.get("structurally_unclosable_indices")
            detail["next_owner"] = (
                "JRA_SOURCE_ADAPTER_OR_FACT_ACQUISITION"
                if feasibility.get("structurally_unclosable_cell_count") else
                "JRA_PRODUCTION_FEATURE_EVALUATOR_OR_AUTHORITY"
            )
        blockers.append(detail)
    if owner_status.get("authorized") is not True:
        blockers.append({
            "stage": STAGE_OWNER_AUTH,
            "code": owner_status.get("reason") or "JRA_PRODUCTION_STATIC_OWNER_NOT_AUTHORIZED",
            "next_owner": "INDEPENDENT_PRODUCTION_REVIEW_WITH_FORWARD_OOS",
            "self_approval_forbidden": True,
        })
    if numerical_ready and not (report.get("static_owner_executable_diagnostic") or {}).get("static_prediction"):
        blockers.append({
            "stage": STAGE_OWNER_EXEC,
            "code": "JRA_STATIC_OWNER_EXECUTION_NOT_AVAILABLE",
            "error": report.get("static_owner_executable_error"),
        })
    if intent is not None:
        current = _time(now or datetime.now(timezone.utc).isoformat())
        cutoff = _time(intent.get("prediction_cutoff"))
        if current is None or cutoff is None or current > cutoff:
            blockers.append({"stage": STAGE_TEMPORAL,
                             "code": "PREDICTION_CUTOFF_EXPIRED" if cutoff else "CUTOFF_INVALID",
                             "evaluated_at": current.isoformat() if current else None})
    order = (STAGE_SOURCE, STAGE_NUMERICAL, STAGE_OWNER_AUTH, STAGE_OWNER_EXEC, STAGE_TEMPORAL)
    blockers.sort(key=lambda b: order.index(b["stage"]))
    stages = [b["stage"] for b in blockers]
    if not blockers:
        route = ROUTE_FORMAL
    elif stages[0] == STAGE_NUMERICAL:
        route = ROUTE_EVIDENCE_NO_BET
    elif stages[0] == STAGE_OWNER_AUTH:
        route = ROUTE_STATIC_NO_BET
    else:
        route = ROUTE_FAIL_CLOSED
    return {
        "profile": PROFILE,
        "race_id": report.get("race_id"),
        "first_actual_blocked_stage": stages[0] if stages else None,
        "independent_blockers": blockers,
        "independent_blocker_stages": stages,
        "terminal_route": route,
        "numerical_full20_ready": numerical_ready,
        "static_owner_authorized": owner_status.get("authorized") is True,
        "authority_granted": False,
        "zero_exposure_is_not_formal_completion": True,
    }
