"""Read-only next-race learning consumption audit. Never changes Production input."""
from __future__ import annotations
import hashlib
import json
import re
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
                               learning_states, prediction_input=None, family_id='JRA'):
    """Distinguish temporal eligibility, read evidence, and actual input binding.

    prediction_input must be an existing frozen input artifact; this function
    does not synthesize, edit, or inject it.
    """
    freeze, cutoff = _time(source_freeze), _time(prediction_cutoff)
    if freeze > cutoff:
        raise ValueError("SOURCE_AFTER_CUTOFF")
    if family_id not in {'JRA', 'LOCAL'} or not race_id.startswith(f"KM-{family_id}-"):
        raise ValueError(f"{family_id}_SCOPE_REQUIRED")
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
            elif not str(state.get("race_id", "")).startswith(f"KM-{family_id}-"):
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


def audit_official_observation_consumption(root, race_id, *, source_freeze, prediction_cutoff):
    """Read the separate, authorized prior-race observation route from signed FINAL.

    No Learning State is fed to scoring. The ablation operates only on the
    existing Base13 mapping and reports no implied Static or ticket effect.
    """
    if __package__:
        from .jra_production_postresult import verify_archived_final_signature
    else:
        from jra_production_postresult import verify_archived_final_signature

    from execution_store import resolve_phase
    from jra_evidence_to_base_production import _weighted_index, load_mapping
    from jra_source_runtime.source_acquisition import verify_source_artifact
    from jra_source_runtime.verify_source_envelope import verify

    match = re.fullmatch(r"KM-JRA-([A-Z]{3})-([0-9]{8})-R([0-9]{2})", race_id)
    if not match:
        raise ValueError("JRA_OBSERVATION_TARGET_REQUIRED")
    venue, day, target_number = match.groups()
    target_day = datetime.strptime(day, "%Y%m%d").date().isoformat()
    root = Path(root)
    final = json.loads((root / "runtime/final_artifacts" / (race_id + ".json")).read_bytes())
    verify_archived_final_signature(final, root=root, race_id=race_id)
    package = final["final_prediction_package"]
    binding = package["execution_stage_manifest"]["SIGNED_SOURCE_RECEIPT_VERIFIED"]
    execution_id = binding.get("execution_id", "")
    if not re.fullmatch(re.escape(race_id) + r"-LIVE-R[1-9][0-9]*", execution_id):
        raise ValueError("JRA_OBSERVATION_SOURCE_EXECUTION_MISMATCH")
    if _time(binding["source_freeze_at"]) != _time(source_freeze) or _time(final["prediction_cutoff"]) != _time(prediction_cutoff):
        raise ValueError("JRA_OBSERVATION_CALLER_CLOCK_MISMATCH")
    checkpoint = resolve_phase(execution_id, "SOURCE", root=root / "runtime/executions")
    name = "source_receipt_envelope.json"
    if checkpoint is None or name not in checkpoint["manifest"]["files"]:
        raise ValueError("JRA_OBSERVATION_SOURCE_CHECKPOINT_MISSING")
    envelope_path = checkpoint["run_dir"] / name
    checked = verify(envelope_path)
    envelope = json.loads(envelope_path.read_bytes())
    source = envelope["artifact"]
    verified, errors = verify_source_artifact(source)
    if not verified:
        raise ValueError("JRA_OBSERVATION_SOURCE_INVALID:" + "|".join(errors))
    source_context = source["source_race_context"]
    freeze, cutoff = _time(source_freeze), _time(prediction_cutoff)
    if (
        checked["race_id"] != race_id or checked["family"] != "JRA" or checked["status"] != "PASS"
        or envelope["receipt"]["phase"] != "SOURCE" or checked["receipt_sha256"] != binding["receipt_sha256"]
        or source["race_id"] != race_id or source_context["venue_id"] != venue
        or source_context["race_date"] != target_day or source_context["race_no"] != int(target_number)
        or _time(source["source_freeze_at"]) != freeze or _time(source["prediction_cutoff"]) != cutoff
        or not freeze <= _time(envelope["receipt"]["timestamp"]) <= cutoff
        or source["source_snapshot_sha256"] != binding["source_snapshot_sha256"]
        or source["source_snapshot_sha256"] != final["source_snapshot_sha256"]
    ):
        raise ValueError("JRA_OBSERVATION_SOURCE_FINAL_BINDING_MISMATCH")

    same_day = source["jra_official_same_day_results"]
    result_sha = _sha(same_day)
    if (result_sha != source["jra_official_same_day_results_sha256"]
            or result_sha != binding["official_same_day_result_detail_sha256"]
            or same_day.get("official") is not True or same_day.get("production_fact_authority") is not True):
        raise ValueError("JRA_OBSERVATION_RESULT_BUNDLE_MISMATCH")
    snapshots = {s.get("snapshot_sha256"): s for s in source["sources"]}
    prior_results = {}
    for number, row in same_day["races"].items():
        if not 0 < int(number) < int(target_number) or row.get("race_no") != int(number):
            raise ValueError("JRA_OBSERVATION_NON_PRIOR_RACE")
        snapshot_sha = row["source_snapshot_sha256"]
        snap = snapshots[snapshot_sha]
        if (snap.get("source_id") != f"JRA-OFFICIAL-SAME-DAY-R{int(number):02d}-DETAIL"
                or snap.get("official") is not True or snap.get("authority") != "JRA_OFFICIAL"
                or snap.get("cutoff_relation") != "PRE_CUTOFF"
                or row.get("official") is not True or row.get("production_fact_authority") is not True
                or not _time(f'{target_day}T{row["scheduled_post_hhmm"]}:00+09:00') <= _time(snap["fetched_at"]) < freeze):
            raise ValueError("JRA_OBSERVATION_PRIOR_RESULT_PROVENANCE_MISMATCH")
        prior_results[number] = {
            "race_id": f"KM-JRA-{venue}-{day}-R{int(number):02d}",
            "fetched_at": snap["fetched_at"], "raw_sha256": snap["raw_sha256"],
            "snapshot_sha256": snapshot_sha,
        }

    mapping_path = root / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json"
    mapping = load_mapping(mapping_path)
    cells = []
    for runner_id, runner in package["index_provenance_replay"]["runners"].items():
        for index, trace in runner["base_index_trace"].items():
            features, affected = {}, {}
            for component in trace["components"]:
                refs = component["evidence_refs"]
                result_refs = [r.rsplit("R", 1)[1] for r in refs if r.startswith("JRA_OFFICIAL_SAME_DAY:R")]
                name = component["feature"]
                features[name] = {"category": component["category"], "evidence_refs": refs,
                                  "source_fact": component["source_fact"], "rule_id": component["feature_rule_id"]}
                if result_refs:
                    affected[name] = [prior_results[str(int(n))]["race_id"] for n in result_refs]
            if not affected:
                continue
            on = _weighted_index(index, trace["profile"], features, mapping)
            if any(on.get(key) != trace.get(key) for key in (
                "value", "rule_id", "mapping_version", "coverage_weight", "components", "information_status"
            )) or on["value"] != runner["base_final_values"][index]:
                raise ValueError("JRA_OBSERVATION_SIGNED_CELL_REBUILD_MISMATCH")
            off = _weighted_index(index, trace["profile"], {k: v for k, v in features.items() if k not in affected}, mapping)
            cells.append({"runner_id": runner_id, "index": index, "signed_value": on["value"],
                          "same_day_component_ablation_value": off["value"],
                          "delta": round(on["value"] - off["value"], 6),
                          "same_day_features": affected})
    out = {
        "race_id": race_id, "final_sha256": final["sha256"], "final_signature_verified": True,
        "source_receipt_sha256": checked["receipt_sha256"], "source_ed25519_verified": True,
        "source_provenance": "BINDING_FROM_SIGNED_FINAL; INDEPENDENT_OIDC_NOT_REPERFORMED",
        "source_freeze": source_freeze, "prediction_cutoff": prediction_cutoff,
        "replay_mapping_file_sha256": hashlib.sha256(mapping_path.read_bytes()).hexdigest(),
        "prior_official_result_snapshots": prior_results, "base_index_cells": cells,
        "signed_consumed_cell_count": len(cells), "ablation_value_changed_count": sum(c["delta"] != 0 for c in cells),
        "scope": "SIGNED_OFFICIAL_PRE_RACE_OBSERVATIONS_AND_BASE_INDEX_COMPONENT_ABLATION_ONLY",
        "production_learning_state_use": "NOT_ESTABLISHED", "production_policy_changed": False,
    }
    out["sha256"] = _sha(out)
    return out


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--race-id", required=True)
    parser.add_argument("--family-id", choices=['JRA','LOCAL'], default='JRA')
    parser.add_argument("--source-freeze", required=True)
    parser.add_argument("--cutoff", required=True)
    parser.add_argument("--states", required=True)
    parser.add_argument("--prediction-input")
    parser.add_argument("--signed-official-observations-root")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    states = json.loads(Path(args.states).read_text(encoding="utf-8"))
    frozen = json.loads(Path(args.prediction_input).read_text(encoding="utf-8")) if args.prediction_input else None
    if not isinstance(states, list):
        raise ValueError("STATES_MUST_BE_LIST")
    report = audit_learning_consumption(
        race_id=args.race_id, source_freeze=args.source_freeze,
        prediction_cutoff=args.cutoff, learning_states=states,
        prediction_input=frozen, family_id=args.family_id)
    if args.signed_official_observations_root:
        report["official_observation_consumption"] = audit_official_observation_consumption(
            args.signed_official_observations_root, args.race_id,
            source_freeze=args.source_freeze, prediction_cutoff=args.cutoff)
        report["sha256"] = _sha({k: v for k, v in report.items() if k != "sha256"})
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
