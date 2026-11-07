"""FNB frozen qualitative-context transport; no model, scoring, or Scope grant.

The v2.1 venue canon requires context before Static.  A list of mechanism
names is not their output.  This module binds an externally adopted Context
Producer's full records to the exact SOURCE/active universe and preserves the
records verbatim.  It cannot evaluate their predictive truth or authorize the
producer.  Existing trusted Owner policy must bind that producer explicitly.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
import math
import re

CANON = "KM-LOCAL-FNB-v2.1-20260928-R1"
SCHEMA = "KM-LOCAL-FNB-FROZEN-VENUE-CONTEXT-v1"
PRODUCER_KEYS = ("model_id", "version", "code_sha256", "adoption_receipt_sha256")
# Names are transport fields for the preserved v2.1 sequence, not new weights,
# thresholds, scores, class rules, or automatic tactical interpretations.
MODULE_FIELDS = {
    # track_state/same_day_state below mean interpreted same-day Bias/GCI,
    # not directly reported weather/going. Their first-race value stays null.
    "CURRENT_TRACK_STATE_CLASSIFY": ("track_state", "weather", "going", "same_day_state"),
    "FPR_FNB": ("acquisition", "maintenance"),
    "FSD_FNB": ("front_demand", "assertion", "restraint"),
    "LCC_FNB": ("position_acquisition", "leadership_acquisition", "competition_absorption",
                "leadership_maintenance", "finish_conversion"),
    "REACHABLE_POSITION_RANGE": ("early", "corner3", "corner4", "finish"),
    "STAGE_COST_TOPOLOGY": ("Leader", "Pressing", "Tracking", "Mid-race Progression",
                            "Absorption", "Final Conversion", "edges"),
    "P2_REACHABILITY_RESCUE": ("review",),
    "ROLE_DIVERGENCE_REVIEW": ("review",),
    "DISTANCE_CAPABILITY_RESCUE": ("review",),
    "COMMENT_OBJECTIVE_CONFLICT_REVIEW": ("review",),
    "COURSE_SPECIFIC_LEADERSHIP_REVIEW": ("review",),
}
RUNNER_MODULES = {
    "FPR_FNB", "FSD_FNB", "LCC_FNB", "REACHABLE_POSITION_RANGE", "STAGE_COST_TOPOLOGY",
    "P2_REACHABILITY_RESCUE", "ROLE_DIVERGENCE_REVIEW", "DISTANCE_CAPABILITY_RESCUE",
    "COMMENT_OBJECTIVE_CONFLICT_REVIEW", "COURSE_SPECIFIC_LEADERSHIP_REVIEW",
}
_SHA = re.compile(r"[0-9a-f]{64}")
_PLACEHOLDERS = {"PASS", "PRESENT", "COMPLETE", "COMPLETED", "READY", "OBSERVED",
                 "UNKNOWN", "N/A", "NONE", "TBD", "TODO", "FIXTURE", "UNVERIFIED"}


class FnbVenueContextError(ValueError):
    pass


def canonical_sha256(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _dt(value):
    try:
        out = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError) as exc:
        raise FnbVenueContextError("FNB_CONTEXT_INVALID_CLOCK") from exc
    if out.tzinfo is None:
        raise FnbVenueContextError("FNB_CONTEXT_NAIVE_CLOCK")
    return out.astimezone(timezone.utc)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _content(value):
    """Reject empty/status-only placeholders, booleans and nonfinite numbers."""
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().upper() not in _PLACEHOLDERS
    if isinstance(value, bool) or value is None:
        return False
    if isinstance(value, (float, int)):
        return math.isfinite(value)
    if isinstance(value, list):
        return bool(value) and all(_content(x) for x in value)
    if isinstance(value, dict):
        return bool(value) and all(_text(k) and _content(v) for k, v in value.items())
    return False


def _observation(record, *, source_ids, freeze, source_freeze, runner_count, range_required=False):
    if not isinstance(record, dict):
        raise FnbVenueContextError("FNB_CONTEXT_OBSERVATION_REQUIRED")
    status = record.get("status")
    if status in {"UNKNOWN", "NOT_APPLICABLE"}:
        if record.get("value") is not None or not _text(record.get("reason")):
            raise FnbVenueContextError("FNB_CONTEXT_UNKNOWN_MUST_REMAIN_EXPLICIT_NULL")
        return False
    if range_required and status in {"OBSERVED", "DERIVED"}:
        value = record.get("value")
        if (not isinstance(value, dict) or set(value) != {"min", "max"}
                or type(value["min"]) is not int or type(value["max"]) is not int
                or not 1 <= value["min"] <= value["max"] <= runner_count):
            raise FnbVenueContextError("FNB_CONTEXT_RANGE_MUST_REMAIN_RANGE")
    if status not in {"OBSERVED", "DERIVED"} or not _content(record.get("value")):
        raise FnbVenueContextError("FNB_CONTEXT_FULL_CONTENT_REQUIRED")
    refs = record.get("source_ids")
    if (not isinstance(refs, list) or not refs
            or not all(type(x) is str and x in source_ids for x in refs)
            or len(refs) != len(set(refs))):
        raise FnbVenueContextError("FNB_CONTEXT_SOURCE_REFERENCE_MISMATCH")
    fetched_times = []
    for source_id in refs:
        snapshot = source_ids[source_id]
        # Past event time and fetch time are distinct: an old observation may
        # be fetched later, but not after the context that claims to use it.
        fetched = _dt(snapshot.get("fetched_at"))
        if fetched > source_freeze:
            raise FnbVenueContextError("FNB_CONTEXT_REFERENCED_SOURCE_POST_SOURCE_FREEZE")
        fetched_times.append(fetched)
        if (fetched > freeze
                or snapshot.get("post_cutoff_or_ineligible") is True
                or snapshot.get("stale") is True or snapshot.get("current") is False
                or snapshot.get("status") in {"FETCH_FAILED", "FAILED", "BLOCKED", "INELIGIBLE"}
                or ("http_status" in snapshot and
                    (type(snapshot["http_status"]) is not int or not 200 <= snapshot["http_status"] < 300))):
            raise FnbVenueContextError("FNB_CONTEXT_REFERENCED_SOURCE_NOT_AVAILABLE_AT_FREEZE")
    observed = _dt(record.get("observed_at"))
    if observed > freeze:
        raise FnbVenueContextError("FNB_CONTEXT_POSTFREEZE_OBSERVATION")
    # observed_at is the underlying evidence observation/event time, never a
    # future scenario realization. Pure computation has a separate derived_at.
    if observed > max(fetched_times):
        raise FnbVenueContextError("FNB_CONTEXT_OBSERVATION_AFTER_REFERENCED_FETCH")
    if status == "DERIVED" and not _text(record.get("derivation")):
        raise FnbVenueContextError("FNB_CONTEXT_DERIVATION_REQUIRED")
    if status == "DERIVED" and not max(fetched_times) <= _dt(record.get("derived_at")) <= freeze:
        raise FnbVenueContextError("FNB_CONTEXT_DERIVATION_CLOCK_MISMATCH")
    return True


def fnb_context_temporal_receipt(request, envelope):
    """Reuse the existing FNB first-day/result-lineage guard for this schema.

    SOURCE signature and RESULT receipt verification stay with their existing
    caller.  A carrier cannot replace those with a qualitative claim.  Going
    and weather observations remain separate from inferred same-day bias.
    """
    from runtime.local_fnb_r11_venue_temporal import verify
    source = envelope.get("artifact") or {}
    try:
        receipt = verify(source_artifact=source, request=request)
    except (ValueError, TypeError) as exc:
        raise FnbVenueContextError(str(exc)) from exc
    context = request.get("venue_prediction_context") or {}
    modules = context.get("modules")
    if not isinstance(modules, dict):
        raise FnbVenueContextError("FNB_CONTEXT_REQUIRED_MODULES_MISMATCH")
    rows = modules.get("CURRENT_TRACK_STATE_CLASSIFY") or {}
    if not isinstance(rows, dict):
        raise FnbVenueContextError("FNB_CONTEXT_MODULE_CONTENT_REQUIRED:CURRENT_TRACK_STATE_CLASSIFY")
    if not receipt.get("prior_race_results_accepted"):
        for field in ("track_state", "same_day_state"):
            record = rows.get(field) or {}
            if record.get("status") != "UNKNOWN" or record.get("value") is not None:
                raise FnbVenueContextError("FNB_CONTEXT_SAME_DAY_BIAS_REQUIRES_VERIFIED_PRIOR_RESULT")
    out = copy.deepcopy(receipt)
    out["context_frozen_at"] = context.get("frozen_at")
    out["source_freeze_at"] = source.get("source_freeze_at")
    out["source_receipt_sha256"] = envelope.get("receipt_sha256")
    out["prior_result_observation_times"] = [
        {"race_no": row["race_no"], "first_observed_at": row["first_observed_at"]}
        for row in source.get("fnb_same_day_result_observations") or []]
    return out


def bind_fnb_frozen_venue_context(request, envelope, policy, active_ids, *, static_freeze_at):
    """Return a deep copy only after full transport checks.

    The producer binding is an *additional input contract*, never inferred from
    the caller's carrier.  This function does not grant FNB Owner Scope, sign a
    SOURCE, generate context, or create rankings.  Unknown observations stay
    null and are counted separately; structural validity is not LIVE acceptance.
    """
    expected = policy.get("fnb_venue_context_producer")
    if (not isinstance(expected, dict) or not all(_text(expected.get(k)) for k in PRODUCER_KEYS)
            or not _SHA.fullmatch(expected["code_sha256"])
            or not _SHA.fullmatch(expected["adoption_receipt_sha256"])):
        raise FnbVenueContextError("FNB_CONTEXT_PRODUCER_NOT_BOUND_BY_OWNER_POLICY")
    context = request.get("venue_prediction_context")
    if not isinstance(context, dict) or context.get("schema") != SCHEMA:
        raise FnbVenueContextError("FNB_CONTEXT_FULL_FROZEN_DOCUMENT_REQUIRED")
    if context.get("canon") != CANON:
        raise FnbVenueContextError("FNB_CONTEXT_CANON_MISMATCH")
    if context.get("producer") != expected:
        raise FnbVenueContextError("FNB_CONTEXT_PRODUCER_BINDING_MISMATCH")
    if (not _text(policy.get("family_authority_basis"))
            or context.get("authority_id") != policy.get("family_authority_basis")):
        raise FnbVenueContextError("FNB_CONTEXT_AUTHORITY_MISMATCH")
    if (context.get("venue_id") != "FNB" or context.get("race_id") != request.get("race_id")
            or context.get("race_date") != request.get("race_date")
            or type(context.get("race_no")) is not int
            or context.get("race_no") != request.get("race_no")):
        raise FnbVenueContextError("FNB_CONTEXT_RACE_IDENTITY_MISMATCH")
    source = envelope.get("artifact") or {}
    if (not _SHA.fullmatch(str(context.get("source_receipt_sha256") or ""))
            or context.get("source_receipt_sha256") != envelope.get("receipt_sha256")
            or not _SHA.fullmatch(str(context.get("source_snapshot_sha256") or ""))
            or context.get("source_snapshot_sha256") != source.get("source_snapshot_sha256")):
        raise FnbVenueContextError("FNB_CONTEXT_SOURCE_BINDING_MISMATCH")
    ids = [str(x) for x in active_ids]
    supplied = context.get("active_runner_ids")
    if (len(ids) != len(set(ids)) or not isinstance(supplied, list)
            or any(type(x) is not str for x in supplied)
            or len(supplied) != len(set(supplied)) or set(supplied) != set(ids)):
        raise FnbVenueContextError("FNB_CONTEXT_ACTIVE_UNIVERSE_MISMATCH")
    frozen, cutoff, post, static = (_dt(context.get("frozen_at")),
                                   _dt(request.get("prediction_cutoff")),
                                   _dt(request.get("scheduled_post_at")), _dt(static_freeze_at))
    source_freeze = _dt(source.get("source_freeze_at"))
    if not source_freeze <= frozen <= static < cutoff < post:
        raise FnbVenueContextError("FNB_CONTEXT_TEMPORAL_BINDING_MISMATCH")
    modules = context.get("modules")
    if not isinstance(modules, dict) or set(modules) != set(MODULE_FIELDS):
        raise FnbVenueContextError("FNB_CONTEXT_REQUIRED_MODULES_MISMATCH")
    fnb_context_temporal_receipt(request, envelope)
    source_rows = [x for x in source.get("sources") or []
                   if x.get("official") is True and x.get("cutoff_relation") == "PRE_CUTOFF"]
    if any(not _text(x.get("source_id")) for x in source_rows):
        raise FnbVenueContextError("FNB_CONTEXT_TYPED_SOURCE_ID_REQUIRED")
    refs = {x["source_id"]: x for x in source_rows}
    if len(refs) != len(source_rows):
        raise FnbVenueContextError("FNB_CONTEXT_DUPLICATE_SOURCE_ID")
    # Density is a separate race-level qualitative assessment.  Do not infer it
    # from runner count or collapse the per-runner demand/assertion/restraint.
    density_known = _observation(context.get("front_group_density"), source_ids=refs,
                                freeze=frozen, source_freeze=source_freeze, runner_count=len(ids))
    known, unknown = int(density_known), int(not density_known)
    for module_id, fields in MODULE_FIELDS.items():
        module = modules[module_id]
        if not isinstance(module, dict):
            raise FnbVenueContextError("FNB_CONTEXT_MODULE_CONTENT_REQUIRED:" + module_id)
        rows = module if module_id in RUNNER_MODULES else {"race": module}
        if module_id in RUNNER_MODULES and set(rows) != set(ids):
            raise FnbVenueContextError("FNB_CONTEXT_RUNNER_MODULE_UNIVERSE_MISMATCH:" + module_id)
        for row in rows.values():
            if not isinstance(row, dict) or set(row) != set(fields):
                raise FnbVenueContextError("FNB_CONTEXT_MODULE_FIELDS_MISMATCH:" + module_id)
            for field, obs in row.items():
                present = _observation(obs, source_ids=refs, freeze=frozen,
                                       source_freeze=source_freeze, runner_count=len(ids),
                                       range_required=module_id == "REACHABLE_POSITION_RANGE")
                known += int(present)
                unknown += int(not present)
    if not known:
        raise FnbVenueContextError("FNB_CONTEXT_EMPTY_EVIDENCE_CARRIER_FORBIDDEN")
    if context.get("temporal_status") != "PRESTART_FROZEN_NO_RESULT":
        raise FnbVenueContextError("FNB_CONTEXT_PRESTART_STATUS_REQUIRED")
    declared_hash = context.get("sha256")
    if not _SHA.fullmatch(str(declared_hash or "")) or declared_hash != canonical_sha256(
            {k: v for k, v in context.items() if k != "sha256"}):
        raise FnbVenueContextError("FNB_CONTEXT_DOCUMENT_SHA_MISMATCH")
    # No fields, UNKNOWNs, ranges, or qualitative assessments are rewritten.
    return copy.deepcopy(context)
