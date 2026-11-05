"""Reconstruct a saved frozen corpus; remove one new batch for diagnosis only.

No collection, admission, external execution, freeze or OOS registration occurs.
The original CI-admitted bytes and original FORMAL snapshot list are the input
allowlists.  This is deliberately separate from the authenticated live Reader.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import sys


def read(path):
    return json.loads(path.read_text())


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assemble(records, day, profile):
    from jra_pedigree_corpus import _horse_identity, _clean_runs
    horses, names, conflicts, maternal_conflicts = {}, {}, set(), set()
    snapshots = set()
    for snapshot, incoming_horses in records:
        snapshots.add(snapshot)
        for h in incoming_horses:
            identity = _horse_identity(h)
            if not identity:
                continue
            name = str(h["horse_name"]).strip()
            names.setdefault(name, set()).add(identity)
            row = horses.setdefault(identity, {"horse_id": identity, "horse_name": name,
                "sire": h["sire"], "dam": h["dam"], "damsire": h.get("damsire") or "", "runs": {}})
            row.setdefault("identity_kind", "NAME_SIRE_DAM_COMPOSITE_NOT_OFFICIAL_HORSE_ID")
            row.setdefault("source_references", [])
            if snapshot not in row["source_references"]:
                row["source_references"].append(snapshot)
            parent = str(h.get("damsire") or "").strip()
            if identity not in maternal_conflicts:
                if parent and row["damsire"] and parent != row["damsire"]:
                    maternal_conflicts.add(identity)
                    row["damsire"] = ""
                    row["maternal_identity_status"] = "CONFLICT_QUARANTINED"
                elif parent:
                    row["damsire"] = parent
                    row["maternal_identity_status"] = "OBSERVED"
            for run in _clean_runs(h.get("runs") or [], day):
                key = (run["date"], run["venue"], run["surface"], run["distance_m"], run["race_name"])
                if (identity, key) in conflicts:
                    continue
                previous = row["runs"].get(key)
                if previous is not None and previous != run:
                    conflicts.add((identity, key))
                    row["runs"].pop(key, None)
                else:
                    row["runs"][key] = run
    return {"profile": profile, "horses": horses, "snapshots": sorted(snapshots),
        "snapshot_count": len(snapshots), "manifest_sha256": sha(sorted(snapshots)),
        "horse_count": len(horses), "run_count": sum(len(h["runs"]) for h in horses.values()),
        "identity_collision_count": sum(len(ids) - 1 for ids in names.values() if len(ids) > 1),
        "run_conflict_count": len(conflicts), "maternal_identity_conflict_count": len(maternal_conflicts)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--audit", type=Path, required=True)
    p.add_argument("--summary", type=Path, required=True)
    p.add_argument("--source-paths", type=Path, required=True)
    p.add_argument("--extra-inherited-admission", type=Path, required=True,
                   help="Original CI log proof for a frozen harvest omitted by the later day audit.")
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    root = a.root.resolve()
    sys.path.insert(0, str(root / "runtime"))
    from jra_pedigree_corpus import _verified_source, PROFILE
    from jra_owner_authorized_feature_rules import owner_authorized_observations
    from jra_evidence_to_base_production import _weighted_index, _profile_for_runner
    from jra_bvi_consumption import build_bvi_consumption

    audit, admitted_summary, paths = read(a.audit), read(a.summary), read(a.source_paths)
    if digest(a.audit) != admitted_summary["audit_raw_sha256"]:
        raise ValueError("ORIGINAL_ADMISSION_AUDIT_HASH_MISMATCH")
    rid = "KM-JRA-TKY-20261101-R01"
    request_path = root / "runtime/requests" / (rid + "-LIVE-R1-FORMAL.json")
    request = read(request_path)
    original_measurement = next(r for r in audit["production_predictions"] if r["race_id"] == rid)
    if (request["source_snapshot_sha256"] != original_measurement["source_snapshot_sha256"] or
            request["prediction_cutoff"] != original_measurement["cutoff"] or
            request["index_provenance_hash"] != original_measurement["index_provenance_hash"] or
            sha({str(r["runner_id"]): r["evidence_features"] for r in request["runners"]}) !=
            original_measurement["evidence_feature_snapshot_sha256"]):
        raise ValueError("ACTUAL_REQUEST_DOES_NOT_MATCH_ORIGINAL_CI_MEASUREMENT")
    manifest = request["source_to_evidence_feature_compiler"]["pedigree_corpus_manifest"]
    snapshots = set(manifest["snapshots"])
    if sha(sorted(snapshots)) != manifest["manifest_sha256"]:
        raise ValueError("ORIGINAL_FROZEN_MANIFEST_INVALID")
    numeric_time = datetime.fromisoformat(request["numerical_calculated_at"])
    source_path = root / "runtime/executions/KM-JRA-TKY-20261101-R01-LIVE-R1/SOURCE/runs/41255545303/source_receipt_envelope.json"
    if not _verified_source(source_path):
        raise ValueError("TARGET_SOURCE_LOCAL_SIGNATURE_MISMATCH")
    source = read(source_path)["artifact"]
    if (source["source_snapshot_sha256"] != request["source_snapshot_sha256"] or
            digest(source_path) != original_measurement["source_file_sha256"]):
        raise ValueError("TARGET_REQUEST_SOURCE_BINDING_MISMATCH")
    cards = source["jra_official_race_card_detail"]["runners"]
    history = source["jra_official_horse_history"]["runners"]
    history_parents = [history.get(str(r.get("runner_id") or r.get("horse_no")), {}).get("pedigree") or {} for r in cards]
    relevant_sires = {str(r["sire"]).strip() for r in cards + history_parents if r.get("sire")}
    relevant_damsires = {str(r["damsire"]).strip() for r in cards + history_parents if r.get("damsire")}
    records, provenance = [], []
    for row in sorted(paths["receipts"], key=lambda r: r["path"]):
        path = root / row["path"]
        verified = _verified_source(path)
        if not verified or verified["source_snapshot_sha256"] != row["source_snapshot_sha256"]:
            raise ValueError("FROZEN_SOURCE_CONTENT_OR_SIGNATURE_MISMATCH:" + row["path"])
        snapshot = verified["source_snapshot_sha256"]
        if snapshot not in snapshots or verified["race_id"] == rid:
            raise ValueError("UNEXPECTED_OR_TARGET_SOURCE_IN_FROZEN_POOL")
        if datetime.fromisoformat(verified["source_freeze_at"].replace("Z", "+00:00")) > numeric_time:
            raise ValueError("SOURCE_FROZEN_AFTER_ORIGINAL_NUMERICAL_EXECUTION")
        records.append((snapshot, verified["horses"]))
        provenance.append({"path": row["path"], "file_sha256": digest(path), "snapshot": snapshot})
    target_batch = "ATTESTED_HARVEST:b81d5e5b4b22612d030ab8c6dd25e5ce0ea297d1b19b86b439eb2f02a94af14c"
    extra = read(a.extra_inherited_admission)
    extra_log = a.extra_inherited_admission.parent / extra["raw_original_job_log"]
    extra_metadata = a.extra_inherited_admission.parent / extra["run_and_step_metadata"]
    if (digest(extra_log) != extra["raw_original_job_log_sha256"] or
            digest(extra_metadata) != extra["run_and_step_metadata_sha256"] or extra.get("fresh_oidc") is not False):
        raise ValueError("INHERITED_ORIGINAL_BACKFILL_EVIDENCE_HASH_MISMATCH")
    log, metadata = extra_log.read_text(), read(extra_metadata)
    if ("Attestation created for " + Path(extra["file"]).name + "@sha256:" + extra["file_sha256"] not in log or
            extra["original_oidc_verified_at"] + " JRA_PEDIGREE_SIGSTORE_ATTESTATION_VERIFIED" not in log or
            metadata["run"]["id"] != extra["original_run_id"] or metadata["run"]["conclusion"] != "success" or
            not any(j["id"] == extra["original_job_id"] and
                    any(s["name"] == "Verify external OIDC signer before corpus publication" and
                        s["conclusion"] == "success" for s in j["steps"])
                    for j in metadata["jobs"]["jobs"]) or
            datetime.fromisoformat(extra["original_oidc_verified_at"].replace("Z", "+00:00")) > numeric_time):
        raise ValueError("ORIGINAL_BACKFILL_VERIFICATION_RECEIPT_INVALID")
    harvest_items = [{**r, "admission_basis": "INHERITED_DAY_AUDIT_ORIGINAL_RAW_SHA_ALLOWLIST"}
                     for r in audit["verified_harvest_artifacts"]]
    harvest_items.append({"file": Path(extra["file"]).name, "sha256": extra["content_sha256"],
                          "file_sha256": extra["file_sha256"],
                          "admission_basis": "ORIGINAL_BACKFILL_OIDC_VERIFICATION_JOB_LOG_NOT_LATER_DAY_AUDIT"})
    for item in sorted(harvest_items, key=lambda r: r["file"]):
        snapshot = "ATTESTED_HARVEST:" + item["sha256"]
        if snapshot not in snapshots:
            continue
        path = root / "runtime/pedigree_corpus" / item["file"]
        if digest(path) != item["file_sha256"]:
            raise ValueError("FROZEN_HARVEST_ORIGINAL_FILE_HASH_MISMATCH")
        harvest = read(path)
        content = hashlib.sha256(json.dumps({k: v for k, v in harvest.items() if k != "sha256"},
                                  ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        if content != item["sha256"] or content != harvest["sha256"]:
            raise ValueError("FROZEN_HARVEST_CONTENT_HASH_MISMATCH")
        if datetime.fromisoformat(harvest["harvested_at"]) > numeric_time:
            raise ValueError("HARVEST_CAPTURED_AFTER_ORIGINAL_NUMERICAL_EXECUTION")
        selected_horses = [h for h in harvest["horses"]
                           if h.get("sire") in relevant_sires or h.get("damsire") in relevant_damsires]
        records.append((snapshot, selected_horses))
        provenance.append({"path": str(path.relative_to(root)), "file_sha256": digest(path), "snapshot": snapshot,
                           "target_parent_relevant_profiles": len(selected_horses),
                           "admission_basis": item["admission_basis"]})
    if {r[0] for r in records} != snapshots or target_batch not in snapshots:
        raise ValueError("FROZEN_SNAPSHOT_INPUT_SET_NOT_EXACT")
    day = date.fromisoformat(request["race_date"])
    full = assemble(records, day, PROFILE)
    for key in ("manifest_sha256", "snapshot_count", "horse_count", "run_count", "identity_collision_count", "run_conflict_count"):
        if full[key] != manifest[key]:
            raise ValueError("FROZEN_POOL_RECONSTRUCTION_MISMATCH:" + key + ":" + str(full[key]) + ":" + str(manifest[key]))
    old = assemble([(s, h) for s, h in records if s != target_batch], day, PROFILE)
    registry = read(root / "mapping/jra_evidence_feature_rule_registry_v1.3_20261010.json")
    mapping = read(root / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")
    actual_consumption_proof = build_bvi_consumption(request, mapping, source)
    if actual_consumption_proof["static_execution_proof_status"] != "BOUND_ACTUAL_EXECUTION":
        raise ValueError("ACTUAL_STATIC_EXECUTION_BINDING_MISSING")
    pedigree = {feature for indices in mapping["index_profiles"].values() for feature in indices["BVI"]}
    reconstructed = owner_authorized_observations(source, registry, corpus=full)
    excluded = owner_authorized_observations(source, registry, corpus=old)
    rows, evidence_changes = [], []
    for runner in request["runners"]:
        runner_id = str(runner["runner_id"])
        actual = runner["evidence_features"]
        feature_changes = []
        for feature in sorted(pedigree):
            original = actual.get(feature)
            rebuilt = reconstructed[runner_id].get(feature)
            keys = ("category", "source_fact", "observation_count")
            if any((original or {}).get(k) != (rebuilt or {}).get(k) for k in keys):
                raise ValueError("ACTUAL_PEDIGREE_FEATURE_NOT_REPRODUCED:" + runner_id + ":" + feature)
            before = excluded[runner_id].get(feature)
            if any((before or {}).get(k) != (rebuilt or {}).get(k) for k in keys):
                weight = mapping["index_profiles"][_profile_for_runner(runner)]["BVI"].get(feature)
                feature_changes.append({"feature": feature, "without_batch": before, "actual_with_batch": rebuilt,
                    "used_in_actual_bvi": weight is not None, "actual_bvi_weight": weight})
        feature_sets = {}
        for label, observations in (("without_batch", excluded), ("actual_with_batch", reconstructed)):
            features = deepcopy(actual)
            for feature in pedigree:
                features.pop(feature, None)
                if feature in observations[runner_id]:
                    features[feature] = observations[runner_id][feature]
            feature_sets[label] = features
        results = {label: _weighted_index("BVI", _profile_for_runner(runner), features, mapping,
                                         acquisition_failure=runner.get("bvi_acquisition_failure"))
                   for label, features in feature_sets.items()}
        actual_value = runner["canonical_components"]["BVI"]["value"]
        if abs(results["actual_with_batch"]["value"] - actual_value) > 1e-6:
            raise ValueError("ACTUAL_BVI_NOT_REPRODUCED:" + runner_id)
        row = {"runner_id": runner_id, "runner_name": runner["name"], "actual_bvi": actual_value,
            "without_only_new_tokyo44_batch_bvi": results["without_batch"]["value"],
            "bvi_delta_due_to_batch_exclusion": round(actual_value - results["without_batch"]["value"], 10),
            "actual_numeric_replay": "PASS", "changed_sample_features": feature_changes}
        rows.append(row)
        evidence_changes.extend((runner_id, f["feature"]) for f in feature_changes)
    def bvi_order(key):
        return [r["runner_id"] for r in sorted(rows, key=lambda r: (-r[key], int(r["runner_id"])))]
    report = {"profile": "KM-JRA-BVI-EXACT-FROZEN-CORPUS-EXCLUSION-DIAGNOSTIC-20261101",
        "status": "POST_RESULT_DIAGNOSTIC_NOT_NEW_FREEZE_OR_OOS", "race_id": rid,
        "request_file_sha256": digest(request_path), "source_file_sha256": digest(source_path),
        "source_snapshot_sha256": request["source_snapshot_sha256"],
        "prediction_cutoff": request["prediction_cutoff"], "original_numerical_calculated_at": request["numerical_calculated_at"],
        "actual_request_original_ci_measurement_binding": "SOURCE_SHA_CUTOFF_FEATURE_SNAPSHOT_SHA_AND_INDEX_PROVENANCE_HASH_MATCHED",
        "actual_bvi_static_bound_proof_sha256": actual_consumption_proof["sha256"],
        "qualification": "INHERITED_FORMAL_FROZEN_SNAPSHOT_SET_AND_ORIGINAL_CI_HARVEST_ADMISSION; SOURCE_SIGNATURES_AND_ALL_INPUT_HASHES_RECHECKED; NO_NEW_OIDC_OR_ADMISSION",
        "one_frozen_harvest_absent_from_later_day_audit": extra,
        "one_frozen_harvest_admission_evidence_file_sha256": digest(a.extra_inherited_admission),
        "original_frozen_manifest_sha256": full["manifest_sha256"],
        "without_only_new_tokyo44_batch_manifest_sha256": old["manifest_sha256"],
        "excluded_snapshot": target_batch,
        "original_compiler_parent_filter": {"sires": sorted(relevant_sires), "damsires": sorted(relevant_damsires),
            "source_records": "ALL_HORSES_FROM_EACH_INCLUDED_SIGNED_SOURCE",
            "harvest_records": "ONLY_HORSES_MATCHING_TARGET_SIRE_OR_DAMSIRE"},
        "full": {k: v for k, v in full.items() if k != "horses"},
        "without_batch": {k: v for k, v in old.items() if k != "horses"},
        "actual_features_reproduced": True, "actual_bvi_reproduced_runners": len(rows),
        "runners_with_sample_evidence_changes": len({r for r, f in evidence_changes}),
        "sample_feature_changes": len(evidence_changes),
        "actual_weighted_bvi_component_sample_changes": sum(f["used_in_actual_bvi"] for r in rows for f in r["changed_sample_features"]),
        "actual_bvi_runners_with_new_batch_sample_consumption": sum(any(f["used_in_actual_bvi"] for f in r["changed_sample_features"]) for r in rows),
        "runners_with_bvi_numeric_changes": sum(bool(r["bvi_delta_due_to_batch_exclusion"]) for r in rows),
        "bvi_ordinal_ranking_with_batch": bvi_order("actual_bvi"),
        "bvi_ordinal_ranking_without_batch": bvi_order("without_only_new_tokyo44_batch_bvi"),
        "bvi_ordinal_is_not_static_ranking": True, "runners": rows, "verified_input_files": provenance,
        "static_roles_ticket_capital_counterfactual": "NOT_EXECUTED; ACTUAL_STATIC_BOUND_PROOF_IS_SAVED_SEPARATELY",
        "forward_oos_increment": 0, "production_mutation": False, "fixed_D_retrained": False}
    report["sha256"] = sha(report)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("race_id", "sha256", "actual_bvi_reproduced_runners", "runners_with_sample_evidence_changes", "sample_feature_changes", "runners_with_bvi_numeric_changes")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
