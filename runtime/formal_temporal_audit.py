"""Explain actual computation clocks separately from the legacy cutoff field.

This is clock consistency evidence. It is not an independent storage witness,
does not alter signed history, and cannot grant Forward OOS eligibility.
"""
from datetime import datetime


def _time(value):
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("TEMPORAL_AUDIT_TIMEZONE_REQUIRED")
    return parsed


def build_temporal_audit(request, source, final_freeze_at):
    source = source or request.get("source_snapshot") or {}
    proof = request.get("bvi_static_consumption_proof") or {}
    computed = request.get("static_computed_at")
    proof_computed = proof.get("computed_at")
    if computed and proof_computed and _time(computed) != _time(proof_computed):
        raise ValueError("STATIC_COMPUTED_AT_PROOF_MISMATCH")
    computed = computed or proof_computed
    values = {
        "source_freeze_at": source.get("source_freeze_at"),
        "static_computed_at": computed,
        "final_freeze_at": final_freeze_at,
        "prediction_cutoff": request.get("prediction_cutoff"),
        "scheduled_post_at": request.get("scheduled_post_at"),
        "legacy_static_freeze_timestamp": request.get("static_freeze_timestamp"),
    }
    s, c, f, cutoff, post, legacy = map(_time, values.values())
    checks = {
        "source_before_static": s <= c if s and c else None,
        "static_before_final": c <= f if c and f else None,
        "static_at_or_before_cutoff": c <= cutoff if c and cutoff else None,
        "final_at_or_before_cutoff": f <= cutoff if f and cutoff else None,
        "final_before_post": f < post if f and post else None,
    }
    legacy_is_cutoff = bool(computed and legacy and cutoff and legacy == cutoff)
    return {
        "profile": "KM-FORMAL-ACTUAL-CLOCK-AUDIT-v1",
        **values,
        "legacy_static_freeze_timestamp_semantics": (
            "DECLARED_CUTOFF_BOUNDARY_NOT_COMPUTATION_TIME" if legacy_is_cutoff
            else "UNRESOLVED_LEGACY_FIELD"
        ),
        "clock_checks": checks,
        "clock_consistency": "FAIL" if False in checks.values() else "PASS" if all(
            value is True for value in checks.values()) else "PENDING_MISSING_CLOCK",
        "independent_persistence_verified": False,
        "forward_oos_eligibility_granted": False,
    }
