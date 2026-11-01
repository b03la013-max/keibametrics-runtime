"""Read-only, byte-bound audit of the retained 2026-11-01 natural harvest.

This script does not call a Producer, OIDC service, KRS, or dispatch.  It
revalidates bytes admitted by the original CI audit, then replays saved BVI
components.  Inherited admission and a new attestation are different claims.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, date, timezone
import hashlib
import json
from pathlib import Path
import re
import statistics
import sys
import unicodedata


def raw_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact_sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def counts(values):
    return dict(sorted(Counter(values).items(), key=lambda item: str(item[0])))


def distribution(values):
    values = sorted(values)
    return {"groups": len(values), "min": min(values) if values else None,
            "median": statistics.median(values) if values else None,
            "max": max(values) if values else None,
            "below_2": sum(v < 2 for v in values),
            "below_5": sum(v < 5 for v in values),
            "below_10": sum(v < 10 for v in values)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--audit", type=Path, required=True)
    p.add_argument("--summary", type=Path, required=True)
    p.add_argument("--health", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    root = a.root.resolve()
    sys.path.insert(0, str(root / "runtime"))
    from jra_pedigree_corpus import _horse_identity, _clean_runs, _verified_source
    from jra_bvi_consumption import build_bvi_consumption
    from jra_delivery import verify_signed_final
    from jra_owner_authorized_feature_rules import class_rank
    from family_authority_guard import resolve_current_authority

    audit, summary, health = read(a.audit), read(a.summary), read(a.health)
    if raw_sha(a.audit) != summary["audit_raw_sha256"]:
        raise ValueError("INHERITED_FULL_AUDIT_RAW_SHA_MISMATCH")
    target = date.fromisoformat(audit["target_race_date"])
    artifacts = audit["verified_harvest_artifacts"]
    identities, parent_observations = set(), Counter()
    parent_sets = {"sire": defaultdict(set), "damsire": defaultdict(set)}
    composite_parents, name_triples = defaultdict(set), defaultdict(set)
    valid_observations = raw_observations = 0
    runs, conflicts, verified, nov1 = {}, set(), [], []
    dedicated_identity_sets = {"before_nov1": set(), "nov1": set()}
    for item in artifacts:
        path = root / "runtime/pedigree_corpus" / item["file"]
        obj = read(path)
        if raw_sha(path) != item["file_sha256"]:
            raise ValueError("HARVEST_FILE_SHA_MISMATCH:" + path.name)
        content = hashlib.sha256(json.dumps(
            {k: v for k, v in obj.items() if k != "sha256"},
            ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        if content != item["sha256"] or content != obj["sha256"]:
            raise ValueError("HARVEST_CONTENT_SHA_MISMATCH:" + path.name)
        verified.append({"file": path.name, "file_sha256": raw_sha(path),
                         "content_sha256": content})
        current_day = item["date"] == "2026-11-01"
        if current_day:
            stem = path.stem
            acquisition = read(root / "runtime/pedigree_intake_receipts" /
                               (stem + "-41255432695-1-acquisition.json"))
            admission = read(root / "runtime/pedigree_intake_receipts" /
                             (stem + "-admitted-41255432695.json"))
            if (acquisition["harvest_sha256"] != content or
                    admission["harvest_sha256"] != content or
                    admission["status"] != "OFFICIAL_BVI_CORPUS_ADMITTED"):
                raise ValueError("NOV1_ACQUISITION_ADMISSION_BINDING_MISMATCH")
            nov1.append({"file": path.name, "content_sha256": content,
                         "race_ids": item["race_ids"], "profiles": obj["horse_count"],
                         "raw_prior_observations": sum(len(h.get("runs", [])) for h in obj["horses"]),
                         "acquisition_new": acquisition["new"],
                         "reused_profile_observations": obj.get("reused_profile_count", 0),
                         "captured_at": obj["harvested_at"],
                         "admitted_at": admission["verified_at"],
                         "admission_prior_run_count": admission["prior_run_count"]})
        for horse in obj["horses"]:
            identity = _horse_identity(horse)
            identities.add(identity)
            dedicated_identity_sets["nov1" if current_day else "before_nov1"].add(identity)
            for key in ("sire", "dam", "damsire"):
                parent_observations[key] += bool(horse.get(key))
            composite_parents[identity].add((horse.get("sire"), horse.get("dam"), horse.get("damsire")))
            name_triples[horse.get("horse_name")].add((horse.get("sire"), horse.get("dam")))
            for parent_type in parent_sets:
                if horse.get(parent_type):
                    parent_sets[parent_type][horse[parent_type]].add(identity)
            for raw in horse.get("runs", []):
                raw_observations += 1
                clean = _clean_runs([raw], target, include_environment=True)
                for run in clean:
                    valid_observations += 1
                    key = (identity, run["date"], run["venue"], run["surface"],
                           run["distance_m"], run["race_name"])
                    fact = (run["finish"], run["field_size"])
                    if key in runs and runs[key]["fact"] != fact:
                        conflicts.add(key)
                    record = runs.setdefault(key, {"fact": fact, "sire": horse.get("sire"),
                        "damsire": horse.get("damsire"), "going": set(), "raw_surface": set(),
                        "official_race_id": set(), "label_available_at": set()})
                    record["going"].add(run["going"] or "UNKNOWN")
                    record["raw_surface"].add(run["surface_raw"] or "UNKNOWN")
                    if raw.get("official_race_id") or raw.get("race_id"):
                        record["official_race_id"].add(raw.get("official_race_id") or raw["race_id"])
                    if raw.get("label_available_at"):
                        record["label_available_at"].add(raw["label_available_at"])
    for key in conflicts:
        runs.pop(key, None)
    if (len(identities) != audit["unique_composite_horses"] or
            len(runs) != audit["unique_dedicated_prior_runs"] or
            raw_observations != audit["raw_prior_run_observations"] or
            valid_observations != audit["valid_prior_run_observations_before_dedup"]):
        raise ValueError("DEDICATED_SCOPE_DENOMINATOR_REPRODUCTION_MISMATCH")

    going, surface, raw_surface, venue, distance, classes = Counter(), Counter(), Counter(), Counter(), Counter(), Counter()
    offspring_runs, env_groups = Counter(), defaultdict(set)
    obstacle_keys, jra_flat_keys, expanded_jump_keys = [], [], []
    unknown_going_raw_surface = Counter()
    jra_venues = {"札幌", "函館", "福島", "新潟", "東京", "中山", "中京", "京都", "阪神", "小倉"}
    for key, record in runs.items():
        identity, day, track, surf, length, name = key
        g = next(iter(record["going"])) if len(record["going"]) == 1 else "CONFLICT"
        going[g] += 1
        surface[surf] += 1
        raw_surface["|".join(sorted(record["raw_surface"]))] += 1
        venue[track] += 1
        distance[str(length)] += 1
        classes[str(class_rank(name))] += 1
        offspring_runs[identity] += 1
        jump = any("障" in s or "芝ダ" in s for s in record["raw_surface"]) or "障" in name
        expanded_jump = bool(any("障" in s or ("芝" in s and "ダ" in s) for s in record["raw_surface"]) or
            re.search(r"障害|ジャンプ|ハイJ|グランドJ|スプリングJ|東京HJ|京都HJ|中山GJ|新潟JS|阪神JS|牛若丸JS|ペガサスJS|J[・.]?G(?:I{1,3}|[123])",
                      unicodedata.normalize("NFKC", name).upper()))
        if jump:
            obstacle_keys.append(key)
        if expanded_jump:
            expanded_jump_keys.append(key)
        if track in jra_venues and not jump and surf in {"芝", "ダ"}:
            jra_flat_keys.append(key)
        if g == "UNKNOWN":
            unknown_going_raw_surface["|".join(sorted(record["raw_surface"]))] += 1
        for parent_type in parent_sets:
            parent = record[parent_type]
            if parent:
                env_groups[(parent_type, parent, track, surf, length, class_rank(name), g)].add(identity)
    quality = {"valid_deduplicated_runs": len(runs),
        "going": dict(going), "going_known_rate": 1 - going["UNKNOWN"] / len(runs),
        "normalized_surface": dict(surface), "raw_surface": dict(raw_surface),
        "venue": dict(venue), "distance_m": dict(distance), "class_rank": dict(classes),
        "composite_horses_with_valid_prior_runs": len(offspring_runs),
        "runs_per_composite_horse": distribution(list(offspring_runs.values())),
        "run_weight_is_not_independent_offspring_weight": True,
        "parent_nonempty_profile_observations": dict(parent_observations),
        "sire_independent_composite_offspring": distribution([len(v) for v in parent_sets["sire"].values()]),
        "damsire_independent_composite_offspring": distribution([len(v) for v in parent_sets["damsire"].values()]),
        "exact_parent_environment_independent_offspring": distribution([len(v) for v in env_groups.values()]),
        "environment_group_definition": "PARENT_TYPE,PARENT,VENUE,NORMALIZED_SURFACE,EXACT_DISTANCE,CLASS_RANK,NORMALIZED_GOING",
        "inherited_raw_going_quality_group_count": len(audit["quality_groups"]),
        "unknown_going_raw_surface": dict(unknown_going_raw_surface),
        "official_permanent_horse_ids": audit["permanent_registry_horse_ids"],
        "independently_joinable_official_prior_race_ids": sum(bool(v["official_race_id"]) for v in runs.values()),
        "independently_recorded_label_available_at": sum(bool(v["label_available_at"]) for v in runs.values()),
        "composite_parent_triple_conflicts": sum(len(v) > 1 for v in composite_parents.values()),
        "same_name_multiple_sire_dam_triples": sum(len(v) > 1 for v in name_triples.values()),
        "obstacle_or_mixed_surface_runs": len(obstacle_keys),
        "obstacle_composite_horses": len({k[0] for k in obstacle_keys}),
        "obstacle_marker_screen_definition": "RAW_SURFACE_HAS_障_OR_芝ダ_OR_RACE_NAME_HAS_障",
        "obstacle_marker_screen_is_exhaustive": False,
        "named_jump_stakes_not_exhaustively_excluded_by_initial_screen": True,
        "expanded_PR342_named_jump_screen_diagnostic": {
            "source_commit": "e5808fb82bdf99d51539ee3c7de28416d65623a9",
            "source_file": "research/jra_bvi_next/candidate.py::is_explicit_jump",
            "source_file_raw_sha256": "a454642661251c346e71b3c65bef938a0e72518cd9cd68a3bb9c86b22465f3c5",
            "current_dedicated_runs": len(expanded_jump_keys),
            "current_composite_horses": len({k[0] for k in expanded_jump_keys}),
            "additional_runs_vs_initial_screen": len(set(expanded_jump_keys) - set(obstacle_keys)),
            "scope": "ADDITIONAL_CURRENT_DIAGNOSTIC; NOT_ORIGINAL_FIXED_D_TRAINING; NO_MODEL_CHANGE"},
        "raw_surface_obstacle_normalized_as_turf": sum(k[3] == "芝" for k in obstacle_keys),
        "jra_ten_venue_runs": sum(n for v, n in venue.items() if v in jra_venues),
        "non_jra_or_overseas_history_runs": sum(n for v, n in venue.items() if v not in jra_venues),
        "separate_jra_flat_research_filter": {"runs": len(jra_flat_keys),
            "composite_horses": len({k[0] for k in jra_flat_keys}),
            "going_known": sum(runs[k]["going"] != {"UNKNOWN"} for k in jra_flat_keys),
            "definition": "EXACT_TEN_JRA_VENUES_AND_TURF_OR_DIRT_AND_NO_RAW_SURFACE_障_OR_芝ダ_AND_NO_RACE_NAME_障",
            "flat_proxy_only": True, "qualified_flat_dataset": False,
            "named_jump_stakes_not_exhaustively_excluded": True,
            "scientific_training_eligible": False, "fixed_D_modified": False},
        "fixed_D_historical_467_rows_126_horses": "PRESERVED_HISTORICAL_LIMIT; NOT_RELABELED_AS_CURRENT_CORPUS_COUNTS",
        "missing_going_root_cause": "UNRESOLVED_ORIGINAL_MISSING_VS_PARSER; RETAINED_NORMALIZED_ROWS_AND_RAW_HASHES_DO_NOT_INCLUDE_ORIGINAL_HTML",
        "uncertainty": "COMPOSITE_IDENTITY_ONLY; REPEATED_HORSE_AND_SIRE_DEPENDENCE; NO_CAUSAL_OR_BINOMIAL_INDEPENDENCE_CLAIM",
        "selection_bias": "OBSERVED_PROFILE_AND_SELECTED_RACE_SAMPLE; NOT_NATIONAL_JRA_POPULATION",
        "scientific_training_eligible": False,
        "training_blockers": ["NO_PERMANENT_HORSE_ID_JOIN", "NO_INDEPENDENT_OFFICIAL_PRIOR_RACE_LABEL_JOIN", "NO_INDEPENDENT_LABEL_PUBLICATION_TIME"]}

    authority_path, authority = resolve_current_authority(root)
    contract = read(root / authority["common_family_components"]["family_runtime_contracts_profile"])["families"]["JRA"]
    mapping = read(root / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")
    replays, proofs = [], {}
    for inherited in audit["production_predictions"]:
        rid = inherited["race_id"]
        request_path = root / "runtime/requests" / (rid + "-LIVE-R1-FORMAL.json")
        source_path = root / inherited["source_path"]
        req, envelope = read(request_path), read(source_path)
        if raw_sha(source_path) != inherited["source_file_sha256"] or not _verified_source(source_path):
            raise ValueError("SOURCE_RETAINED_BYTES_OR_LOCAL_SIGNATURE_MISMATCH:" + rid)
        source = envelope["artifact"]
        proof = build_bvi_consumption(req, mapping, source)
        proofs[rid] = proof
        final_path = root / "runtime/final_artifacts" / (rid + ".json")
        final = read(final_path)
        verify_signed_final(final, health, contract)
        if any(final.get(k) != req.get(k) for k in ("race_id", "prediction_cutoff", "source_snapshot_sha256")):
            raise ValueError("SIGNED_FINAL_REQUEST_BINDING_MISMATCH:" + rid)
        manifest = proof["pedigree_corpus_manifest"]
        used_batches = [v for v in nov1 if "ATTESTED_HARVEST:" + v["content_sha256"] in manifest["snapshots"]]
        replays.append({"race_id": rid, "runner_count": len(proof["runners"]),
            "request_file_sha256": raw_sha(request_path), "source_file_sha256": raw_sha(source_path),
            "source_snapshot_sha256": source["source_snapshot_sha256"],
            "source_local_crypto": "ED25519_AND_NESTED_SNAPSHOT_HASH_VERIFIED",
            "source_oidc": "INHERITED_ORIGINAL_CI_PROOF_NOT_FRESHLY_ATTESTED_HERE",
            "prediction_cutoff": req["prediction_cutoff"],
            "numerical_calculated_at": req["numerical_calculated_at"],
            "static_freeze_timestamp": req["static_freeze_timestamp"],
            "bvi_counts": proof["counts"], "corpus_manifest_sha256": manifest["manifest_sha256"],
            "corpus_snapshot_count": manifest["snapshot_count"],
            "new_nov1_batches_in_actual_frozen_manifest": [v["file"] for v in used_batches],
            "corpus_lineage": proof["corpus_artifact_lineage_status"],
            "component_bindings": proof["corpus_component_bindings"],
            "static_proof": proof["static_execution_proof_status"],
            "static_full_ranking": req["bvi_static_consumption_proof"]["full_ranking"],
            "static_roles": req["bvi_static_consumption_proof"]["roles"],
            "index_provenance_hash": proof["index_provenance_hash"],
            "final_file_sha256": raw_sha(final_path), "final_sha256": final["sha256"],
            "final_signature": "VERIFIED_USING_CURRENT_READ_ONLY_RUNTIME_PUBLIC_KEY_AND_R51_CONTRACT",
            "final_signed_at": final["final_receipt"]["receipt"]["timestamp"],
            "final_ticket_count": len(final["final_ticket"]["tickets"]),
            "capital": final["capital_policy_decision"]["required_capital"],
            "downstream_hashes": proof["downstream_artifact_hashes"],
            "claim_limit": "ACTUAL_NUMERICAL_CONSUMPTION_OF_BOUND_CORPUS; PER_BATCH_MARGINAL_CAUSAL_EFFECT_NOT_ESTABLISHED_BY_INCLUSION_ALONE"})

    diagnostics = []
    for diagnostic in audit["inflow_diagnostics"]:
        row = {k: v for k, v in diagnostic.items() if k != "comparison"}
        if diagnostic.get("comparison"):
            row["excluded_inflow_files"] = [v["file"] for v in nov1]
            row["excluded_inflow_content_sha256"] = [v["content_sha256"] for v in nov1]
            row["counterfactual_scope"] = "SAME_SIGNED_SOURCE_AND_RUNNERS; ALL_EIGHT_NOV1_HARVESTS_EXCLUDED_VS_INCLUDED_AT_RECORDED_DIAGNOSTIC_CUTOFF; NOT_ORIGINAL_FORMAL_CUTOFF_RECOMPUTE"
            row["arms"] = {}
            for arm, after in diagnostic["comparison"]["WITH_NEW_INFLOW"].items():
                before = diagnostic["comparison"]["WITHOUT_NEW_INFLOW"][arm]
                changes = [{"runner_id": rid, "before": old, "after": after["bvi"][rid],
                            "delta": round(after["bvi"][rid] - old, 10)}
                           for rid, old in before["bvi"].items() if abs(after["bvi"][rid] - old) > 1e-8]
                row["arms"][arm] = {"bvi_changes": changes,
                    "static_ranking_changed": before["ranking"] != after["ranking"],
                    "roles_changed": before["roles"] != after["roles"],
                    "krs_input_changed": before["krs_input_sha256"] != after["krs_input_sha256"],
                    "krs_input_before_sha256": before["krs_input_sha256"],
                    "krs_input_after_sha256": after["krs_input_sha256"],
                    "before_bvi_counts": before["bvi_counts"], "after_bvi_counts": after["bvi_counts"]}
                feature_changes = []
                before_rows = {r["runner_id"]: r for r in before["postcapture_bvi_contributions"]}
                for runner in after["postcapture_bvi_contributions"]:
                    old_parts = {c["feature"]: c for c in before_rows[runner["runner_id"]]["components"]}
                    for part in runner["components"]:
                        old = old_parts.get(part["feature"])
                        if old is None or old.get("source_fact") != part.get("source_fact"):
                            feature_changes.append({"runner_id": runner["runner_id"], "feature": part["feature"],
                                "before": old, "after": part,
                                "value_contribution_delta": round(part["value_contribution"] - (old or {}).get("value_contribution", 0), 10)})
                row["arms"][arm]["sample_and_feature_deltas"] = feature_changes
        diagnostics.append(row)
    detail_path = a.output.with_name(a.output.stem + "_consumption_details.json")
    detail_path.parent.mkdir(parents=True, exist_ok=True)
    detail_path.write_text(json.dumps(proofs, ensure_ascii=False, indent=2) + "\n")
    report = {"profile": "KM-JRA-BVI-READONLY-CORPUS-AUDIT-20261101",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "authority": authority["manifest_id"], "authority_path": str(authority_path.relative_to(root)),
        "inheritance": {"audit_raw_sha256": raw_sha(a.audit), "artifact_id": summary["artifact_id"],
            "original_run_id": 41255432695, "zip_sha256": summary["zip_sha256"],
            "qualification": summary["qualification"], "fresh_oidc_performed": False},
        "runtime_verification_material": {"health_file_sha256": raw_sha(a.health),
            "provider_timestamp": health.get("timestamp"),
            "status": health.get("status"), "engine_sha256": health.get("engine", {}).get("sha256"),
            "parameter_map_sha256": health.get("parameter_map", {}).get("sha256"),
            "public_receipt_signer_key_id": health.get("receipt_signer", {}).get("key_id"),
            "scope": "READ_ONLY_PUBLIC_VERIFICATION_MATERIAL_NO_KRS_EXECUTION"},
        "dedicated_scope": {"verified_raw_files": len(verified), "unique_windows": audit["verified_window_count"],
            "horse_profile_observations": audit["raw_horse_observations"],
            "composite_horses": len(identities), "raw_prior_observations": raw_observations,
            "clean_prior_observations": valid_observations, "deduplicated_runs": len(runs),
            "invalid_or_future_observations": raw_observations - valid_observations,
            "duplicate_prior_observations": valid_observations - len(runs), "conflicting_run_keys": len(conflicts)},
        "all_reader_scope_inherited_not_rebuilt_without_oidc": audit["actual_reader_corpus"],
        "verified_files": verified, "quality": quality, "nov1_batches": nov1,
        "nov1_unique_composite_horses": len(dedicated_identity_sets["nov1"]),
        "nov1_composites_not_in_previous_dedicated_harvest": len(dedicated_identity_sets["nov1"] - dedicated_identity_sets["before_nov1"]),
        "nov1_identity_difference_is_not_national_new_horses": True,
        "actual_early_formal_consumption": replays,
        "consumption_details_file": detail_path.name, "consumption_details_raw_sha256": raw_sha(detail_path),
        "inherited_postcapture_inflow_diagnostics": diagnostics,
        "fixed_D_forward_oos_increment": 0, "prediction_improvement_demonstrated": False,
        "capital_improvement_demonstrated": False, "production_mutation": False}
    report["sha256"] = compact_sha(report)
    a.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(a.output), "sha256": report["sha256"],
                      "scope": report["dedicated_scope"], "going": quality["going"],
                      "actual_early_formal_races": len(replays)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
