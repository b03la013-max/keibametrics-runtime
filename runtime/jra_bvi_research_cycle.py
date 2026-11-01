"""Non-production BVI research audit and idempotent cohort continuation.

This consumes existing canonical ledgers. The separate successor adapter may
fit exploratory models from byte-bound inherited admissions. It never fetches
a result, refits fixed D, signs a prediction, changes OOS or authorizes Production.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

PROFILE = "KM-JRA-BVI-CONTINUOUS-RESEARCH-v1"
FIXED_MODEL = "runtime/jra_static_owner_forward_oos/models/bvi_env_20261024_5e7f3b31cebd.json"
FIXED_FILE_SHA = "a969cc518da73b4795932f02d8f3cbc6d0ac47a1a7904907055e46958d9f0fc1"
FIXED_MODEL_SHA = "5e7f3b31cebd2e3ab11e2cd436a7a38988d0bba83488f6f0ef784f980fafd126"
BOUND_FILES = {
    "runtime/jra_bvi_environment.py", "runtime/jra_bvi_env_shadow.py",
    "runtime/jra_bvi_shadow_comparison.py", "runtime/jra_bvi_oos_metrics.py",
    "scripts/jra_bvi_pipeline_forward_shadow.py",
}
LEDGERS = {
    "SOURCE_DERIVED": "runtime/source_candidate_oos_status.json",
    "STATIC_OWNER": "runtime/jra_static_owner_forward_oos/current.json",
    "BVI_ENV_FIXED_D": "runtime/jra_static_owner_forward_oos/pedigree_env_current.json",
}
HYPOTHESES = (
    ("A_DISTANCE", "distance_m × surface", "sire,damsire", "MATCHED_GENERAL_PARENT_EFFECT_AT_OTHER_DISTANCES"),
    ("B_VENUE", "venue × independently evidenced course geometry", "sire,damsire", "MATCHED_DISTANCE_SURFACE_GOING_AT_OTHER_VENUES"),
    ("C_GOING", "良/稍重/重/不良 within surface", "sire,damsire", "MATCHED_VENUE_DISTANCE_CLASS_ON_GOOD_GOING"),
    ("D_PARENT_CROSS", "sire × damsire × environment", "sire,damsire", "ADDITIVE_PARENT_GENERAL_AND_ENVIRONMENT_EFFECTS"),
    ("E_ENV_CHANGE", "distance/surface/turn-direction/gradient change", "sire,damsire", "SAME_HORSE_EARLIER_FORM_AND_NO_CHANGE_CONTROLS"),
    ("F_MATERNAL", "dam/maternal family × environment", "dam,maternal_family", "SIRE_DAMSIRE_GENERAL_EFFECT_AND_INDIVIDUAL_FORM"),
    ("G_LOW_CAREER", "newcomer/2-year-old/low-career × environment", "sire,damsire", "CAREER_MATCHED_GENERAL_PARENT_BASELINE"),
)
RACE_RE = re.compile(r"KM-JRA-(?:SPP|HKD|FKS|NGT|TKY|NKY|CHK|KYO|HSN|KKR)-20\d{6}-R(?:0[1-9]|1[0-2])$")


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def sealed(value):
    value = dict(value)
    value["sha256"] = sha(value)
    return value


def clock(value):
    result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("RESEARCH_AWARE_TIMESTAMP_REQUIRED")
    return result


def preserve_clock(expected, previous, name, latest):
    """Only the first observation clock may differ on an idempotent reread."""
    value = previous.get(name)
    if clock(value) > clock(latest):
        raise ValueError("RESEARCH_STORED_CLOCK_IN_FUTURE")
    return sealed({**{k: v for k, v in expected.items() if k != "sha256"}, name: value})


def count(value):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("RESEARCH_NONNEGATIVE_INTEGER_REQUIRED")
    return value


def immutable(path, value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if load(path) != value:
            raise ValueError("RESEARCH_IMMUTABLE_RECORD_CHANGED:" + str(path))
        return False
    path.write_text(raw)
    return True


def audit_fixed_model(root):
    path = root / FIXED_MODEL
    publication = load(path)
    if file_sha(path) != FIXED_FILE_SHA or publication["model"]["model_sha256"] != FIXED_MODEL_SHA:
        raise ValueError("RESEARCH_FIXED_D_MODEL_CHANGED")
    code = publication.get("code_file_sha256") or {}
    if set(code) != BOUND_FILES or any(file_sha(root / name) != digest for name, digest in code.items()):
        raise ValueError("RESEARCH_FIXED_D_BOUND_CODE_CHANGED")
    return {"model_sha256": FIXED_MODEL_SHA, "raw_sha256": FIXED_FILE_SHA,
            "bound_code_sha256": code, "model_publication_loaded": True,
            "race_freeze_or_oos_increment": 0, "retrained": False}, publication["model"]


def read_ledger(root, path):
    target = root / path
    if not target.exists():
        return {"status": "NOT_OBSERVED", "path": path, "eligible_settled_races": None}, None
    data = load(target)
    n = data.get("eligible_settled_races", data.get("eligible_race_count"))
    if n is not None:
        n = count(n)
    return {"status": "OBSERVED_CANONICAL_LEDGER_NOT_REVERIFIED_SIGNATURES_HERE", "path": path,
            "file_sha256": file_sha(target), "eligible_settled_races": n,
            "required_forward_races": data.get("required_forward_races"),
            "canonical_status": data.get("status"), "counts_are_not_pooled": True}, data


def fixed_d_cohorts(ledger):
    """Read one fixed-model/current-policy group at a time; never add groups."""
    if ledger is None:
        return []
    if ledger.get("required_forward_races") != 30 or ledger.get("automatic_promotion") is not False:
        raise ValueError("RESEARCH_FIXED_D_CONTRACT_CHANGED")
    selected = []
    for fingerprint, group in (ledger.get("cohorts") or {}).items():
        if group.get("model_sha256") != FIXED_MODEL_SHA or group.get("current_base_policy") is not True:
            continue
        n = count(group.get("eligible_settled_races"))
        ids = group.get("race_ids")
        if (not isinstance(ids, list) or len(ids) != n or len(set(ids)) != n
                or any(not isinstance(x, str) or not RACE_RE.fullmatch(x) for x in ids)
                or group.get("automatic_promotion") is not False):
            raise ValueError("RESEARCH_FIXED_D_COHORT_MEMBERSHIP_INVALID")
        selected.append({"cohort_fingerprint": fingerprint, "model_sha256": FIXED_MODEL_SHA,
                         "race_ids": sorted(ids), "reported_settled_count": n,
                         "basis": "EXISTING_CANONICAL_SETTLEMENT; NO_NEW_OOS_ADMISSION_HERE"})
    return sorted(selected, key=lambda x: x["cohort_fingerprint"])


def corpus_quality(summary_path, observed_at):
    if summary_path is None or not summary_path.exists():
        return {"status": "NOT_OBSERVED", "scientific_training_qualified": False,
                "permanent_official_horse_ids": None, "qualified_independent_labels": None,
                "reason": "NO_ADMITTED_CORPUS_QUALITY_SUMMARY_PROVIDED"}
    d = load(summary_path)
    expected = d.get("sha256")
    if not expected or sha({k: v for k, v in d.items() if k != "sha256"}) != expected:
        raise ValueError("RESEARCH_CORPUS_SUMMARY_HASH_INVALID")
    if clock(d.get("created_at")) > clock(observed_at):
        raise ValueError("RESEARCH_CORPUS_SUMMARY_FROM_FUTURE")
    reader = d.get("actual_reader_corpus") or {}
    permanent = d.get("permanent_registry_horse_ids")
    if permanent is not None:
        count(permanent)
    # No collection/support total establishes scientific training eligibility.
    return {"status": "INHERITED_ADMISSION_SUMMARY_HASH_RECHECKED; NO_FRESH_OIDC_HERE",
            "summary_file_sha256": file_sha(summary_path), "summary_sha256": expected,
            "reader_manifest_sha256": reader.get("manifest_sha256"),
            "composite_horses": reader.get("horse_count"), "history_rows": reader.get("run_count"),
            "dedicated_harvest_scope": {"verified_windows": d.get("verified_window_count"),
                "verified_artifact_files": len(d["verified_harvest_artifacts"]) if isinstance(d.get("verified_harvest_artifacts"), list) else None,
                "horse_observations": d.get("raw_horse_observations"),
                "composite_horses": d.get("unique_composite_horses"),
                "unique_history_rows": d.get("unique_dedicated_prior_runs")},
            "permanent_official_horse_ids": permanent, "qualified_independent_labels": None,
            "scientific_training_qualified": False,
            "reason": "PERMANENT_ID_LABEL_AVAILABILITY_OPPONENT_AND_SELECTION_BIAS_QUALIFICATION_NOT_ESTABLISHED"}


def discover_corpus_quality(root, observed_at):
    """Reuse already persisted Collector summaries; no duplicate HTTP/OIDC."""
    accepted = []; rejected = []
    for path in sorted((root / "runtime/pedigree_intake_receipts").glob("day-audit-*.json")):
        try:
            item = corpus_quality(path, observed_at)
            accepted.append((clock(load(path)["created_at"]), path.name, item))
        except (ValueError, KeyError, OSError, TypeError) as exc:
            rejected.append({"path": str(path.relative_to(root)), "reason": str(exc)})
    result = max(accepted, key=lambda x: (x[0], x[1]))[2] if accepted else corpus_quality(None, observed_at)
    result["quarantined_summaries"] = rejected
    result["selection"] = "LATEST_VALID_PERSISTED_COLLECTOR_SUMMARY_AT_OR_BEFORE_AUDIT"
    return result


def hypothesis_records(model, quality, registered_at):
    domain = {role: sorted({x["parent"] for x in model.get("parent_distributions", {}).get(role, [])})
              for role in ("sire", "damsire")}
    records = []
    for name, environment, roles, control in HYPOTHESES:
        protocol = {"family": name, "environment": environment, "pedigree_roles": roles.split(","),
            "effect_direction": "TWO_SIDED; POSITIVE_INCREMENT_NOT_ASSUMED", "control": control,
            "confounders": ["individual_prior_form", "class", "age", "sex", "field_size", "opponent_strength",
                            "venue_distance_surface_going", "acquisition_selection", "survivorship"],
            "metrics": ["normalized_finish_MSE", "MAE", "W_P2_P3_rank_capture", "Ordered_Pair", "Third",
                        "false_rescue", "same_budget_PFS", "Robust_PFS"],
            "label_definition": "1-(finish-1)/(field_size-1)",
            "sampling": "HORSE_AND_PARENT_AND_RACE_DAY_CLUSTER_AUDIT; RUNS_NOT_INDEPENDENT_OFFSPRING",
            "validation": "CHRONOLOGICAL_TRAIN_VALIDATION_TEST_AND_ROLLING_FUTURE_COHORTS",
            "multiple_testing": "REGISTER_ALL_TESTED_GROUPS; FAMILYWISE_HOLM_0.05_IF_VALID_CLUSTER_PVALUES_EXIST",
            "rejection": "WORSE_HELD_OUT_PRIMARY_MSE_OR_ROLE_ECONOMIC_HARM; UNKNOWN_OR_UNCALIBRATED_SUPPORT_HOLD",
            "validation_period": "SET_AND_FREEZE_WITH_SEPARATE_CANDIDATE_BEFORE_FIRST_FUTURE_EVALUATION",
            "retest": "NEW_ADMITTED_DATASET_SHA_PLUS_PREDECLARED_REPLICATION; NEVER_RENAME_OLD_FAILURE",
            "production_authority": False}
        identity = sha(protocol)
        records.append(sealed({"hypothesis_id": "BVI-HYP-" + name + "-" + identity[:12],
            "protocol": protocol, "protocol_sha256": identity,
            "lifecycle_state": "HYPOTHESIS_REGISTERED", "status": "HOLD_DATA_QUALITY",
            "generated_at": registered_at,
            "pedigree_domain": domain if name != "F_MATERNAL" else {"dam": None, "maternal_family": None},
            "domain_source": {"model_sha256": FIXED_MODEL_SHA, "meaning": "OBSERVED_COMPOSITE_NAMES; NOT_PERMANENT_IDS"},
            "independent_eligible_samples": None, "tested": False, "effect_estimate": None,
            "qualified_data_required": "INDEPENDENT_ID_LABEL_TIME_OPPONENT_SELECTION_AND_ENVIRONMENT_QUALIFICATION",
            "next_action": "QUALIFY_DATA_BEFORE_HISTORICAL_FIT"}))
    return records


def historical_basis(path):
    if path is None or not path.exists():
        return {"status": "NOT_OBSERVED", "decision": "HOLD", "forward_oos_increment": 0}
    d = load(path)
    if d.get("classification") != "HISTORICAL_PROXY_DIAGNOSTIC_NOT_FIXED_D_FORWARD_OOS":
        raise ValueError("RESEARCH_HISTORICAL_SERIES_LABEL_REQUIRED")
    general = d["test"]["GENERAL_ONLY"]
    env = d["test"]["HIERARCHICAL_ENV"]
    if count(general["n"]) == 0 or count(general["n"]) != count(env["n"]):
        return {"status": "INCOMPARABLE_POPULATIONS", "decision": "HOLD", "forward_oos_increment": 0}
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not 0 <= x <= 1
           for x in (general["mse"], env["mse"])):
        raise ValueError("RESEARCH_HISTORICAL_LOSS_INVALID")
    worse = env["mse"] > general["mse"]
    return {"status": "RESEARCH_BASIS_READ; NO_REFIT_OR_NEW_HYPOTHESIS_TEST", "input_file_sha256": file_sha(path),
            "source": d["source"], "test_n": general["n"], "general_mse": general["mse"],
            "environment_mse": env["mse"], "mse_delta": env["mse"] - general["mse"],
            "decision": "REJECT_HISTORICAL_INCREMENT" if worse else "HOLD_REQUIRES_QUALIFIED_FORWARD_TEST",
            "single_permutation_is_not_significance": True, "rolling_evaluation": "NOT_EXECUTED",
            "forward_oos_increment": 0}


def settlement_status(path):
    if path is None:
        return {"status": "NOT_OBSERVED", "counts": None}
    if not path.exists():
        return {"status": "BLOCKED", "counts": None,
                "reason": "REQUIRED_SETTLEMENT_MANIFEST_MISSING", "research_audit_still_runs": True}
    d = load(path)
    values = d.get("counts") or {}
    for value in values.values():
        if value is not None:
            count(value)
    return {"status": d.get("status", "UNKNOWN"), "counts": values,
            "file_sha256": file_sha(path), "required_stages": d.get("required_stages"),
            "research_audit_still_runs": True}


def review_membership(root, cohort):
    """Do not turn a forged aggregate counter into a cohort-review trigger."""
    refs = []
    for race_id in cohort["race_ids"]:
        path = root / "runtime/jra_static_owner_forward_oos" / race_id / "pedigree_env_result.json"
        d = load(path)
        if (d.get("sha256") != sha({k: v for k, v in d.items() if k != "sha256"})
                or d.get("race_id") != race_id or d.get("oos_eligible") is not True
                or d.get("signed_result_verified") is not True
                or d.get("policy_fingerprint") != cohort["cohort_fingerprint"]
                or d.get("environment_candidate", {}).get("model_sha256") != FIXED_MODEL_SHA):
            raise ValueError("RESEARCH_CANONICAL_SETTLEMENT_REFERENCE_INVALID:" + race_id)
        refs.append({"race_id": race_id, "file_sha256": file_sha(path), "canonical_record_sha256": d["sha256"]})
    return refs


def milestone_record(group, refs, event_key):
    return sealed({"event_id": event_key, "cohort_fingerprint": group["cohort_fingerprint"],
        "model_sha256": FIXED_MODEL_SHA, "milestone_races": 30,
        "observed_membership_count": len(refs), "canonical_membership": refs,
        "lifecycle_state": "OOS_SETTLED",
        "scope": "CANONICAL_SETTLEMENT_REVIEW_PACKET; NOT_NEW_OOS_ADMISSION",
        "signature_verification_repeated_here": False,
        "independent_review": "REQUIRED_NOT_AUTOMATICALLY_PERFORMED",
        "next_cohort": {"state": "WAITING_ELIGIBLE_CANDIDATE", "candidate_id": None,
            "requirements": ["independent_review_of_frozen_cohort", "qualified_new_dataset_sha",
                "separate_candidate_model_code_protocol_sha", "prospective_independent_publication_witness",
                "approved_research_execution_scope"]},
        "collection_continues": True, "quality_audit_continues": True,
        "hypothesis_exploration_continues": True, "automatic_promotion": False})


def run(root, *, output=None, corpus_summary=None, successor_summary=None, settlement_manifest=None, basis=None, observed_at=None):
    root = Path(root).resolve()
    registered_at = observed_at or datetime.now(timezone.utc).isoformat()
    clock(registered_at)
    output = Path(output) if output else root / "research/bvi_research_cycle"
    if not output.is_absolute():
        output = root / output
    output = output.resolve()
    # Never let an output flag write over Production or signed canonical inputs.
    try:
        if (root / "research").is_symlink():
            raise ValueError("RESEARCH_ROOT_SYMLINK_FORBIDDEN")
        output.relative_to((root / "research").resolve())
    except ValueError:
        raise ValueError("RESEARCH_OUTPUT_MUST_STAY_IN_RESEARCH")
    fixed, model = audit_fixed_model(root)
    quality = (corpus_quality(Path(corpus_summary), registered_at) if corpus_summary
               else discover_corpus_quality(root, registered_at))
    comparisons = historical_basis(Path(basis) if basis else root / "research/bvi_research_cycle/known_research_basis.json")
    settlement = settlement_status(Path(settlement_manifest) if settlement_manifest else None)
    ledgers = {}; env = None
    for series, path in LEDGERS.items():
        record, data = read_ledger(root, path)
        ledgers[series] = record
        if series == "BVI_ENV_FIXED_D":
            env = data
    cohorts = fixed_d_cohorts(env)
    hypotheses = []
    for record in hypothesis_records(model, quality, registered_at):
        target = output / "hypotheses" / (record["hypothesis_id"] + ".json")
        if target.exists():
            previous = load(target)
            expected = preserve_clock(record, previous, "generated_at", registered_at)
            if previous != expected:
                raise ValueError("RESEARCH_HYPOTHESIS_PROTOCOL_CHANGED")
            record = previous
        else:
            immutable(target, record)
        hypotheses.append(record)
    review_events = []
    failures = []
    # The existing daily audit is also the research trigger. No extra cron or
    # monitor actor; changed data get a distinct, never-Production diagnostic.
    try:
        from jra_bvi_successor_research import run as run_successor
        successor = run_successor(root, observed_at=registered_at, summary_path=successor_summary)
        if successor.get("status") == "BLOCKED":
            failures.append({"stage": "SUCCESSOR_DIAGNOSTIC", "reason": "FIT_OR_POPULATION_UNUSABLE"})
    except (ValueError, KeyError, OSError, TypeError) as exc:
        successor = {"status": "BLOCKED", "reason": str(exc), "forward_oos_increment": 0}
        failures.append({"stage": "SUCCESSOR_DIAGNOSTIC", "reason": str(exc)})
    for group in cohorts:
        if group["reported_settled_count"] < 30:
            continue
        try:
            refs = review_membership(root, group)
            # Preserve the first observed threshold-crossing snapshot. A
            # periodic audit can first see >30; never pretend it saw exactly30.
            event_key = sha({"profile": PROFILE, "cohort": group["cohort_fingerprint"], "milestone": 30})
            target = output / "milestones" / (event_key + ".json")
            if target.exists():
                event = load(target)
                original_refs = event.get("canonical_membership")
                available = {sha(ref) for ref in refs}
                if (not isinstance(original_refs, list) or len(original_refs) < 30
                        or len({sha(ref) for ref in original_refs}) != len(original_refs)
                        or any(sha(ref) not in available for ref in original_refs)
                        or event != milestone_record(group, original_refs, event_key)):
                    raise ValueError("RESEARCH_MILESTONE_CONTENT_CHANGED")
            else:
                event = milestone_record(group, refs, event_key)
                immutable(target, event)
            review_events.append({"event_id": event_key, "sha256": event["sha256"],
                                  "next_cohort_state": "WAITING_ELIGIBLE_CANDIDATE"})
        except (ValueError, KeyError, OSError) as exc:
            failures.append({"cohort_fingerprint": group["cohort_fingerprint"], "reason": str(exc)})
    fingerprint = {"research_code_sha256": file_sha(Path(__file__)),
                   "fixed_model": fixed, "quality": quality, "ledgers": ledgers,
                   "historical_basis": comparisons, "hypothesis_ids": [x["hypothesis_id"] for x in hypotheses],
                   "hypothesis_record_sha256": {x["hypothesis_id"]: x["sha256"] for x in hypotheses},
                   "review_events": review_events, "failures": failures, "settlement": settlement}
    # Liveness clocks are not new evidence or a reason to refit.
    fingerprint["successor_research"] = {k:v for k,v in successor.items()
                                         if k not in {"last_checked_at", "sha256"}}
    evidence_sha = sha(fingerprint)
    status = "BLOCKED" if failures else "PARTIAL"
    manifest = sealed({"profile": PROFILE, "status": status, "audit_execution_complete": not failures,
        "audit_execution_status": "BLOCKED" if failures else "VERIFIED_COMPLETE",
        "research_completion": "PARTIAL_DATA_QUALITY_AND_FUTURE_OOS_PENDING",
        "observed_at": registered_at, "evidence_sha256": evidence_sha,
        **fingerprint, "counts": {"registered_hypotheses": len(hypotheses), "tested_new_hypotheses": 0,
            "held_for_quality": len(hypotheses), "rejected_historical_candidates": int(comparisons["decision"] == "REJECT_HISTORICAL_INCREMENT"),
            "milestone_review_events": len(review_events), "failures": len(failures)},
        "persistent_research_enabled": True, "stop_at_30": False, "forward_oos_increment": 0,
        "new_candidate_fit": successor.get("new_candidate_fit", "NOT_EXECUTED"), "prediction_utility_success": False,
        "production_improvement_success": False, "production_effect": "NONE", "purchase_authority": False})
    # Repeated daily audit of identical evidence does not manufacture new events.
    event_path = output / "audits" / (evidence_sha + ".json")
    if event_path.exists():
        previous = load(event_path)
        if previous != preserve_clock(manifest, previous, "observed_at", registered_at):
            raise ValueError("RESEARCH_AUDIT_CONTENT_CHANGED")
        manifest = previous
    else:
        immutable(event_path, manifest)
    # The immutable event is deduplicated; liveness is a separate derived view.
    # A non-race day's identical inputs must still show that an audit ran.
    manifest = sealed({**{k: v for k, v in manifest.items() if k != "sha256"},
                       "audit_record_sha256": manifest["sha256"], "last_checked_at": registered_at})
    output.mkdir(parents=True, exist_ok=True)
    (output / "current.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--corpus-summary", type=Path)
    parser.add_argument("--successor-summary", type=Path)
    parser.add_argument("--settlement-manifest", type=Path)
    parser.add_argument("--basis", type=Path)
    args = parser.parse_args()
    try:
        record = run(args.root, output=args.output, corpus_summary=args.corpus_summary, successor_summary=args.successor_summary,
                     settlement_manifest=args.settlement_manifest, basis=args.basis)
    except (ValueError, KeyError, OSError) as exc:
        # A crash is visible to the mandatory workflow gate, never SUCCESS.
        incident_id = sha({"profile": PROFILE, "stage": "RESEARCH_AUDIT", "reason": str(exc)})
        failure = sealed({"profile": PROFILE, "status": "BLOCKED", "audit_execution_complete": False,
            "observed_at": datetime.now(timezone.utc).isoformat(), "reason": str(exc),
            "incident_id": incident_id,
            "forward_oos_increment": 0, "production_effect": "NONE"})
        output = args.output or args.root / "research/bvi_research_cycle"
        if not output.is_absolute():
            output = args.root / output
        output = output.resolve()
        research_root = args.root.resolve() / "research"
        if not research_root.is_symlink() and output.is_relative_to(research_root.resolve()):
            output.mkdir(parents=True, exist_ok=True)
            incident_path = output / "failures" / (incident_id + ".json")
            if incident_path.exists():
                first = load(incident_path)
                failure = sealed({**{k: v for k, v in failure.items() if k != "sha256"},
                    "first_failure_sha256": first["sha256"]})
            else:
                immutable(incident_path, failure)
            (output / "current.json").write_text(json.dumps(failure, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(failure))
        return 1
    print(json.dumps({"profile": PROFILE, "status": record["status"], "counts": record["counts"],
                      "stop_at_30": False, "forward_oos_increment": 0}, ensure_ascii=False))
    return 1 if record["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
