"""Read-only LOCAL Full29 index-to-outcome association audit.

A past result is NEVER a prediction input. This audit is descriptive only:
it cannot create a MODEL, authorize Consumer/KRS/Ticket, or register OOS.
The caller must supply an immutable previously frozen numerical artifact and
its own official full finish order. Signature verification remains external.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
import hashlib
import json
import math

PROFILE = "KM-LOCAL-FULL29-OUTCOME-DESCRIPTIVE-v1-20261111"
TERMINAL = {"CALCULATED", "RULED-NEUTRAL", "RULED-HOLD", "NOT-APPLICABLE"}


class IndexAuditError(ValueError):
    pass


def _digest(data):
    return hashlib.sha256(json.dumps(
        data, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()


def _time(value):
    if not isinstance(value, str):
        raise IndexAuditError("TIMESTAMP_REQUIRED")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise IndexAuditError("TIMESTAMP_INVALID") from exc
    if parsed.tzinfo is None:
        raise IndexAuditError("TIMESTAMP_WITH_TIMEZONE_REQUIRED")
    return parsed


def _rank(values):
    """Average ranks for ties, ascending, stdlib only."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [None] * len(values)
    k = 0
    while k < len(order):
        j = k + 1
        while j < len(order) and values[order[j]] == values[order[k]]:
            j += 1
        for pos in order[k:j]:
            ranks[pos] = (k + j + 1) / 2.0
        k = j
    return ranks


def _spearman(xs, ys):
    if len(xs) < 3:
        return None
    a, b = _rank(xs), _rank(ys)
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    da = sum((x-ma)**2 for x in a)
    db = sum((x-mb)**2 for x in b)
    if da == 0 or db == 0:
        return None
    return sum((x-ma)*(y-mb) for x,y in zip(a,b)) / math.sqrt(da*db)


def audit(numerical, outcome, *, frozen_at, scheduled_post_at,
          source_prestart_attested=False, result_official_attested=False):
    """Evaluate monotone association, not forecast calibration or causal value.

    Source/result signatures are NOT verified by this function. Caller boolean
    attestations are recorded but never upgraded to signed FORMAL receipts.
    """
    if not isinstance(numerical, dict) or not isinstance(outcome, dict):
        raise IndexAuditError("ARTIFACT_OBJECT_REQUIRED")
    rid = numerical.get("race_id")
    if not rid or rid != outcome.get("race_id"):
        raise IndexAuditError("RACE_IDENTITY_MISMATCH")
    indices = numerical.get("required_indices")
    if not isinstance(indices, list) or len(indices) != 29 or len(set(indices)) != 29:
        raise IndexAuditError("FULL29_MANIFEST_REQUIRED")
    if any(not isinstance(k, str) or not k for k in indices):
        raise IndexAuditError("INDEX_NAME_INVALID")
    rows = numerical.get("runners")
    finish = outcome.get("finish_order")
    if not isinstance(rows, list) or not rows:
        raise IndexAuditError("NUMERICAL_RUNNER_UNIVERSE_REQUIRED")
    if not isinstance(finish, list) or not finish:
        raise IndexAuditError("FULL_FINISH_ORDER_REQUIRED")
    ids = [str(row.get("runner_id") or "") for row in rows if isinstance(row, dict)]
    if len(ids) != len(rows) or not all(ids) or len(set(ids)) != len(ids):
        raise IndexAuditError("NUMERICAL_RUNNER_IDENTITY_INVALID")
    finish_ids = [str(x) for x in finish]
    if (len(finish_ids) != len(ids) or len(set(finish_ids)) != len(finish_ids)
            or set(finish_ids) != set(ids)):
        raise IndexAuditError("FINISH_UNIVERSE_MISMATCH")
    before = _time(frozen_at) < _time(scheduled_post_at)
    if not before:
        raise IndexAuditError("POSTSTART_NUMERICAL_CANNOT_BE_PRESTART_STUDY")

    finish_rank = {x:i+1 for i,x in enumerate(finish_ids)}
    all_stats = {}
    for name in indices:
        pairs = []
        statuses = Counter()
        for row in rows:
            spec = (row.get("canonical_components") or {}).get(name)
            if not isinstance(spec, dict):
                raise IndexAuditError(f"INDEX_TERMINAL_MISSING:{name}")
            status = spec.get("terminal_status")
            if status not in TERMINAL:
                raise IndexAuditError(f"INDEX_TERMINAL_INVALID:{name}")
            statuses[status] += 1
            if status != "CALCULATED":
                continue  # A ruled-neutral value is NOT a measured ability.
            v = spec.get("value")
            if (isinstance(v, bool) or not isinstance(v, (int, float))
                    or not math.isfinite(v) or not 0 <= v <= 100):
                raise IndexAuditError(f"INDEX_CALCULATED_VALUE_INVALID:{name}")
            pairs.append((v, -finish_rank[str(row["runner_id"])]))
        corr = _spearman([x for x,_ in pairs], [y for _,y in pairs])
        all_stats[name] = {
            "calculated_runner_count": statuses["CALCULATED"],
            "ruled_neutral_runner_count": statuses["RULED-NEUTRAL"],
            "ruled_hold_runner_count": statuses["RULED-HOLD"],
            "not_applicable_runner_count": statuses["NOT-APPLICABLE"],
            "total_runner_count": len(rows),
            "higher_score_better_finish_spearman": round(corr, 8) if corr is not None else None,
            "status": "DESCRIPTIVE_ASSOCIATION_ONLY" if corr is not None else "INSUFFICIENT_VARIATION_OR_COVERAGE",
        }
    result = {
        "profile": PROFILE,
        "race_id": rid,
        "classification": "NONPRODUCTION_RETROSPECTIVE_DIAGNOSTIC_NOT_OOS",
        "source_prestart_attested_unverified": source_prestart_attested is True,
        "result_official_attested_unverified": result_official_attested is True,
        "external_signature_verification": "NOT_PERFORMED",
        "prediction_consumption_authorized": False,
        "prediction_or_ticket_recalculated": False,
        "input_numerical_sha256": _digest(numerical),
        "input_outcome_sha256": _digest(outcome),
        "freeze_timestamp": frozen_at,
        "scheduled_post_timestamp": scheduled_post_at,
        "full_active_runner_count": len(ids),
        "indices": all_stats,
        "limitations": [
            "Index associations are not independent predictive value, causal ablations or calibrated probabilities.",
            "No race weights, odds, payouts, tickets or training parameters have been modified.",
            "Rows with RULED-NEUTRAL are excluded from numerical association; missingness is reported.",
            "Do not pool across races or claim Forward OOS without a separate preregistered design.",
            "Signed SOURCE and RESULT proof must be verified by the existing external authority.",
            "Full finish order is required; refunds, scratches and dead heats need separate official reconciliation.",
        ],
    }
    result["sha256"] = _digest(result)
    return result
