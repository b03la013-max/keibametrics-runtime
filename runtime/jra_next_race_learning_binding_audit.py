"""Read-only next-race learning consumption audit. Never changes Production input."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime
from pathlib import Path


def _time(value):
    if not isinstance(value, str):
        raise ValueError("TIMESTAMP_REQUIRED")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("TIMEZONE_REQUIRED")
    return parsed


def _sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def audit_learning_consumption(*, race_id, source_freeze, prediction_cutoff,
                               learning_states, prediction_input=None):
    """Distinguish temporal eligibility, read evidence, and actual input binding.

    prediction_input must be an existing frozen input artifact; this function
    does not synthesize, edit, or inject it.
    """
    freeze, cutoff = _time(source_freeze), _time(prediction_cutoff)
    if freeze > cutoff:
        raise ValueError("SOURCE_AFTER_CUTOFF")
    if not race_id.startswith("KM-JRA-"):
        raise ValueError("JRA_SCOPE_REQUIRED")
    if prediction_input is not None and not isinstance(prediction_input, dict):
        raise ValueError("PREDICTION_INPUT_MUST_BE_OBJECT")
    bindings = (prediction_input or {}).get("learning_state_bindings", [])
    if not isinstance(bindings, list):
        raise ValueError("INVALID_LEARNING_BINDINGS")
    if not isinstance(learning_states, list):
        raise ValueError("STATES_MUST_BE_LIST")
    eligible, rejected, consumed = [], [], []
    seen = set()
    for state in learning_states:
        if not isinstance(state, dict):
            rejected.append({"state_id": None, "reason": "INVALID_STATE"})
            continue
        sid = state.get("state_id")
        reason = None
        if not isinstance(sid, str) or not sid or sid in seen:
            reason = "MISSING_OR_DUPLICATE_ID"
        else:
            seen.add(sid)
            if state.get("race_id") == race_id:
                reason = "SAME_RACE_LEAKAGE"
            elif not str(state.get("race_id", "")).startswith("KM-JRA-"):
                reason = "FAMILY_MISMATCH"
            elif not state.get("sha256") or not isinstance(state.get("sha256"), str):
                reason = "STATE_DIGEST_MISSING"
            elif not state.get("effective_time"):
                reason = "EFFECTIVE_TIME_MISSING"
            else:
                try:
                    if _time(state["effective_time"]) >= freeze:
                        reason = "NOT_AVAILABLE_AT_SOURCE_FREEZE"
                except (TypeError, ValueError):
                    reason = "INVALID_EFFECTIVE_TIME"
        if reason:
            rejected.append({"state_id": sid, "reason": reason})
            continue
        eligible.append(sid)
        # Explicit reference only: digest provenance and actual numerical use remain unverified.
        for binding in bindings:
            if not isinstance(binding, dict):
                continue
            if binding.get("state_id") == sid and isinstance(binding.get("state_sha256"), str) and binding["state_sha256"] == state.get("sha256"):
                consumed.append(sid)
                break
    result = {
        "race_id": race_id, "source_freeze": source_freeze,
        "prediction_cutoff": prediction_cutoff,
        "eligible_state_ids": eligible, "rejected": rejected,
        "input_bound_state_ids": consumed,
        "status": "INPUT_BINDING_REFERENCE_OBSERVED_UNVERIFIED" if consumed else "NEXT_RACE_CONSUMPTION_UNVERIFIED",
        "prediction_effect": "NOT_ASSESSED",
        "digest_integrity": "UNVERIFIED_EXTERNAL_STATE_PROVENANCE",
        "input_freeze_integrity": "UNVERIFIED",
        "production_policy_changed": False,
    }
    result["sha256"] = _sha(result)
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--race-id", required=True)
    parser.add_argument("--source-freeze", required=True)
    parser.add_argument("--cutoff", required=True)
    parser.add_argument("--states", required=True)
    parser.add_argument("--prediction-input")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    states = json.loads(Path(args.states).read_text(encoding="utf-8"))
    frozen = json.loads(Path(args.prediction_input).read_text(encoding="utf-8")) if args.prediction_input else None
    if not isinstance(states, list):
        raise ValueError("STATES_MUST_BE_LIST")
    report = audit_learning_consumption(
        race_id=args.race_id, source_freeze=args.source_freeze,
        prediction_cutoff=args.cutoff, learning_states=states,
        prediction_input=frozen)
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
