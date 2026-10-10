"""JRA prospective Candidate dispatch guard for a verified-source NO_BET decision.

A late Candidate rerun is neither a timely forecast nor proof of FORMAL
completion. Never dispatch an event after its frozen prediction cutoff or
the registered external dispatch deadline.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping


class JRACandidateDispatchGuardError(ValueError):
    pass


def _time(raw: Any) -> datetime:
    try:
        out = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise JRACandidateDispatchGuardError("CANDIDATE_TIME_INVALID") from exc
    if out.tzinfo is None:
        raise JRACandidateDispatchGuardError("CANDIDATE_TIME_MISSING_TIMEZONE")
    return out.astimezone(timezone.utc)


def candidate_dispatch_decision(
    intent: Mapping[str, Any],
    source_checkpoint: Mapping[str, Any],
    *,
    now: str | None = None,
) -> dict[str, Any]:
    if intent.get("family_id") != "JRA":
        raise JRACandidateDispatchGuardError("JRA_ONLY")
    race = str(intent.get("race_id") or "")
    if not race or source_checkpoint.get("race_id") != race:
        raise JRACandidateDispatchGuardError("JRA_SIGNED_SOURCE_RACE_MISMATCH")
    if source_checkpoint.get("prediction_cutoff") != intent.get("prediction_cutoff"):
        raise JRACandidateDispatchGuardError("JRA_SIGNED_SOURCE_CUTOFF_MISMATCH")
    if not source_checkpoint.get("receipt_sha256") or not source_checkpoint.get("source_snapshot_sha256"):
        raise JRACandidateDispatchGuardError("JRA_SIGNED_SOURCE_CHECKPOINT_REQUIRED")
    freeze = _time(source_checkpoint.get("source_freeze_at"))
    cutoff = _time(intent.get("prediction_cutoff"))
    deadline = _time(intent.get("external_dispatch_deadline_at"))
    post = _time(intent.get("scheduled_post_at"))
    current = _time(now or datetime.now(timezone.utc).isoformat())
    if not freeze <= cutoff <= deadline < post:
        raise JRACandidateDispatchGuardError("JRA_TEMPORAL_CONTRACT_INVALID")
    if intent.get("acceptance_only") is True or intent.get("temporal_mode", "FORMAL-PRE-RACE") != "FORMAL-PRE-RACE":
        return {"dispatch": False, "reason": "NO_FORWARD_OOS_ACCEPTANCE_OR_REPLAY",
                "race_id": race, "classification": "NO_FORWARD_DISPATCH"}
    if current >= cutoff:
        return {"dispatch": False, "reason": "PREDICTION_CUTOFF_EXPIRED",
                "race_id": race, "classification": "NO_FORWARD_DISPATCH"}
    if current >= deadline:
        return {"dispatch": False, "reason": "EXTERNAL_DISPATCH_DEADLINE_EXPIRED",
                "race_id": race, "classification": "NO_FORWARD_DISPATCH"}
    return {"dispatch": True, "reason": "PRE_CUTOFF_DISPATCH_ELIGIBLE",
            "race_id": race, "classification": "PROSPECTIVE_CANDIDATE_ONLY"}
