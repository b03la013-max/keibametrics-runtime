"""Readback census of governed rules and unadopted numerical hypotheses.

This module executes no score/Owner/KRS and grants no SOURCE or Consumer scope.
It keeps the old35-runner212-cell gap ledger separate from current race counts.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from decimal import Decimal

from runtime.local_base15_research_candidates import research_specification

PROFILE = "KM-FNB-BASE63-RULE-QUALIFICATION-CENSUS-20261104-R13"
CLASSIFICATION = "CURRENT_COVERAGE_READBACK_NOT_NEW_NUMERICAL_EXECUTION_NOT_FORMAL_ADOPTION"


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _file(path):
    path = Path(path)
    raw = path.read_bytes()
    return {"path": str(path), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def rule_decision_packet(repo_root):
    """Return the exact15 proposal contracts; no new mapping is synthesized."""
    root = Path(repo_root).resolve()
    formal_path = root/"mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json"
    candidate_path = root/"profiles/local_base15_research_candidates_v0.1_20261103.json"
    code_path = root/"runtime/local_base15_research_candidates.py"
    formal = json.loads(formal_path.read_bytes())
    candidate = research_specification()
    pinned = json.loads(candidate_path.read_bytes())
    if candidate != pinned or candidate.get("adopted") is not False:
        raise ValueError("BASE15_EXACT_UNADOPTED_PROFILE_CODE_AGREEMENT_REQUIRED")
    records = []
    for spec in candidate["rules"]:
        index, component = spec["index"], spec["component"]
        current = formal["component_score_rules"][index][component]
        if current["rule_id"] != spec["rule_id"]:
            raise ValueError("BASE15_FORMAL_RULE_ID_REFERENCE_MISMATCH")
        records.append({"index": index, "component": component,
            "formal_rule": deepcopy(current),
            "formal_weight": formal["common_component_sets"][index][component],
            "formal_nonmissing_numeric_mapping_complete": False,
            "formal_available_missing_terminal": {"score": formal["missing_policy"]["neutral_score"],
                "state": formal["missing_policy"]["state"],
                "require_missing_flag": True, "ability_interpretation": "UNKNOWN_NOT_WEAK",
                "source_fact_and_refs_required": True, "DCR_consequence_required": True},
            "research_rule_id": spec["research_rule_id"],
            "research_raw_evidence_columns": spec["required_columns"],
            "research_permanent_identity_fields": spec["identity_fields"],
            "research_raw_formula": spec["raw_recipe"],
            "research_raw_denominator": spec["reference_population"],
            "research_0_to_100_formula": spec["transform_candidate"],
            "research_0_to_100_denominator": "N = number of eligible distinct prespecified reference entities, excluding target; minimum3 is a new research choice",
            "research_neutral": spec["neutral_semantics"],
            "research_missing": spec["missing_semantics"],
            "research_observation_coding_protocol": candidate["coding_protocol"]["id"],
            "numeric_choices_origin": spec["transform_origin"],
            "inherited_articles": spec["inherited_articles"],
            "inherited_requirement": (candidate["inherited_requirements"] if index == "BVIg-L" else {}),
            "arithmetic_comparison": {"formal_missing_score": 52,
                "candidate_missing_score": None, "same_numeric_policy": False,
                "reason": "formal UNKNOWN transport neutral52 is not a measured midrank50; no substitution is authorized"},
            "independent_witness_contract": {"raw": "rederive raw_recipe from every eligible source row and fixed sampling frame",
                "score": "independent count of reference_raw less/equal than target_raw, N retained; no production scorer import",
                "source_hashes": "all original byte SHA and cell/row provenance required",
                "actual_current_qualified_witness": False},
            "prediction_freeze_eligibility": {"adopted": False,
                "formal_prediction_consumption": False, "formal_KRS_consumption": False,
                "reason": "unadopted numerical hypothesis plus current identity/complete denominator/qualified evidence not established",
                "temporal_rule": spec["temporal_rule"]},
            "required_adoption_evidence": spec["production_requirements"],
            "candidate_review_package_complete": True,
            "production_adoption_ready": False,
            "formal_registry_changed": False})
    return {"profile": PROFILE, "classification": CLASSIFICATION,
        "formal_registry": _file(formal_path), "candidate_profile": _file(candidate_path),
        "candidate_code": _file(code_path), "rule_count": len(records), "rules": records,
        "new_numeric_policy_adopted": False, "formal_consumer_grants_added": 0,
        "goal_A_does_not_require_all15_new_mappings_adopted": True,
        "goal_A_existing_path": "Eligible SOURCE may use existing executable rules and explicitly governed missing52 terminals with DCR/UNKNOWN; no blanket numerical stop is introduced here"}


def census(numerical_artifact_paths, *, repo_root, supplemental_artifact_paths=()):
    """Read each existing actual-raw witness once and partition current gaps."""
    packet = rule_decision_packet(repo_root)
    specs = {(r["index"], r["component"]): r for r in packet["rules"]}
    formal = json.loads(Path(packet["formal_registry"]["path"]).read_bytes())
    totals = Counter(); by_rule = {}; inputs = []; races = []; prior_witnesses = Counter()
    identities = set()
    for supplied in numerical_artifact_paths:
        path = Path(supplied); artifact = json.loads(path.read_bytes())
        receipt = artifact["receipt"]; request = artifact["request"]
        if receipt.get("sha256") != sha({k:v for k,v in receipt.items() if k != "sha256"}):
            raise ValueError("BASE63_CENSUS_PRIOR_RECEIPT_HASH_MISMATCH")
        race_key = (request["race_date"], request["race_no"])
        if race_key in identities:
            raise ValueError("BASE63_CENSUS_DUPLICATE_RACE")
        identities.add(race_key)
        if (receipt.get("active_universe_verified") is not False
                or receipt.get("formal_source_admitted") is not False
                or artifact["numerical"].get("classification") !=
                    "PRELIMINARY_LISTED_REFERENCE_NOT_ACTIVE_VERIFIED_NOT_FORMAL"):
            raise ValueError("BASE63_CENSUS_EXPLICIT_PRIOR_PRELIMINARY_CLASSIFICATION_REQUIRED")
        inputs.append(_file(path))
        races.append({"date": race_key[0], "race_no": race_key[1], "listed": receipt["listed_runners"],
            "original_zip_sha256": receipt["original_zip_sha256"], "observed_at": receipt["observed_at"],
            "source_qualified_for_current_formal_prediction": False,
            "prior_component_witness_sha256": sha(artifact["component_witness"]),
            "new_full29_execution": False})
        actual = {str(r["runner_id"]): r for r in artifact["numerical"]["runners"]}
        if (len(actual) != receipt["listed_runners"] or
                len(artifact["component_witness"]) != len(actual)*63 or
                len({(r["runner_id"],r["index"],r["component"]) for r in artifact["component_witness"]}) != len(actual)*63):
            raise ValueError("BASE63_CENSUS_PRIOR_GRID_INCOMPLETE_OR_DUPLICATE")
        for row in artifact["component_witness"]:
            key = (row["index"], row["component"])
            feature = actual[row["runner_id"]]["evidence_features"][row["component"]]
            same = (row["comparison"] == "MATCH" and feature["missing"] == row["missing"]
                and feature["rule_id"] == row["rule_id"]
                and abs(Decimal(str(feature["score"]))-Decimal(str(row["witness_score"]))) <= Decimal("0.000002"))
            if not same:
                raise ValueError("BASE63_CENSUS_PRIOR_WITNESS_RECORD_DRIFT")
            formal_rule = formal["component_score_rules"][row["index"]][row["component"]]
            record = by_rule.setdefault(key, {"index": key[0], "component": key[1],
                "formal_rule_id": formal_rule["rule_id"], "formal_transform": formal_rule["transform"],
                "formal_missing_rule": formal_rule["missing_rule"], "listed_component_records": 0,
                "unadopted_nonmissing_mapping": key in specs,
                "prior_witness_comparisons": Counter(), "numeric_missing": 0,
                "numeric_nonmissing": 0, "evidence_quality": Counter(),
                "primary_gap_partition": Counter(), "formal_qualified_consumable_records": 0})
            record["listed_component_records"] += 1
            record["prior_witness_comparisons"][row["comparison"]] += 1
            prior_witnesses[row["comparison"]] += 1
            missing = bool(feature["missing"])
            record["numeric_missing" if missing else "numeric_nonmissing"] += 1
            record["evidence_quality"][row["evidence_quality"]] += 1
            primary = ("UNADOPTED_NONMISSING_NUMERIC_MAPPING" if key in specs else
                "EVIDENCE_NOT_OBSERVED" if missing else "OBSERVED_PROXY_OR_MANAGEMENT_REQUIRES_SOURCE_QUALIFICATION")
            record["primary_gap_partition"][primary] += 1
            totals[primary] += 1
            totals["missing" if missing else "nonmissing"] += 1
            totals["records"] += 1
            if missing and feature["score"] != 52:
                raise ValueError("BASE63_CENSUS_EXISTING_MISSING_TERMINAL_DRIFT")
    supplemental = []
    for path in supplemental_artifact_paths:
        artifact = json.loads(Path(path).read_bytes()); summary = artifact["summary"]
        if (summary.get("source_identity_hypothesis_not_qualified_current_id") is not True
                or summary.get("formal_source_admitted") is not False):
            raise ValueError("BASE63_CENSUS_SUPPLEMENTAL_CLASSIFICATION_REQUIRED")
        supplemental.append({"input": _file(path), "race_id": summary["race_id"],
            "identity_hypotheses": summary["composite_hypotheses_consumed"],
            "starts": summary["history_starts_consumed"],
            "additional_nonmissing_hypothesis_records": summary["new_nonmissing_hypothesis_components"],
            "formal_coverage_increment": 0, "not_added_to_current_formal_counts": True})
    result = {"profile": PROFILE, "classification": CLASSIFICATION,
        "scope": {"races": len(races), "listed_runners": sum(r["listed"] for r in races),
            "active_runner_count": None, "active_universe_qualified": False},
        "current_listed_component_records": totals["records"],
        "current_numerical_missing": totals["missing"], "current_numerical_nonmissing": totals["nonmissing"],
        "primary_gap_partition": {k: v for k,v in totals.items() if k not in {"records","missing","nonmissing"}},
        "existing_witness_readback_comparisons": dict(prior_witnesses),
        "formal_qualified_consumable_records": 0, "new_live_races": 0,
        "historical_gap_ledger": {"scope": "PRIOR35_HISTORICAL_RUNNERS_ONLY_NOT_CURRENT24R",
            "old_missing": 212, "rule_or_implementation_side": 180, "qualified_observation_side": 32,
            "added_to_current_counts": False, "source": "R13 owner instruction section9.2; inherited ledger unchanged"},
        "current_rules": [dict(r, prior_witness_comparisons=dict(r["prior_witness_comparisons"]),
            evidence_quality=dict(r["evidence_quality"]), primary_gap_partition=dict(r["primary_gap_partition"]))
            for _,r in sorted(by_rule.items())], "races": races,
        "supplemental_identity_hypothesis_study": supplemental,
        "rules15_decision_packet": packet, "input_manifest": inputs,
        "new_numerical_policy": False, "new_score_computation": False,
        "new_adoption_of15_required_before_any_existing_formal_numerics": False,
        "old22575_observations_or15researchrule_counts_changed": False}
    result["sha256"] = sha(result)
    return result


def reconcile_current_csv(raw, *, capture, numerical_artifact_paths, now=None):
    """Compare a fresh offered snapshot with old numerics without rewriting them."""
    from runtime.local_nar_csv_reference import inspect_zip
    compared = []; conflicts = []; old_inputs = []
    for supplied in numerical_artifact_paths:
        path = Path(supplied); prior = json.loads(path.read_bytes())
        race = {"venue_id": "FNB", "race_date": prior["request"]["race_date"],
            "race_no": prior["request"]["race_no"]}
        current = inspect_zip(raw, capture=capture, race=race, encoding="utf-8-sig",
            header_mode="present", now=now)
        old = prior["parsed"]
        current_rows = {str(x["runner_number"]): x["prestart_reference_fields"] for x in current["runners"]}
        old_rows = {str(x["runner_number"]): x["prestart_reference_fields"] for x in old["runners"]}
        differences = []
        if current["race_identity"] != old["race_identity"]:
            differences.append({"field": "race_identity", "old": old["race_identity"], "new": current["race_identity"]})
        if set(current_rows) != set(old_rows):
            differences.append({"field": "listed_set", "old": sorted(old_rows), "new": sorted(current_rows)})
        for rid in set(current_rows) & set(old_rows):
            for field in current_rows[rid]:
                if current_rows[rid][field] != old_rows[rid].get(field):
                    differences.append({"runner_id": rid, "field": field,
                        "old": old_rows[rid].get(field), "new": current_rows[rid][field]})
        entry = {"race": race, "fresh_listed": len(current_rows),
            "fresh_zip_raw_sha256": capture["raw_sha256"], "fresh_capture_at": capture["captured_at"],
            "old_zip_raw_sha256": old["capture"]["raw_sha256"], "differences": differences,
            "old_numerical_inputs_unchanged": not differences,
            "recomputed_scores": False, "active_verified": False,
            "formal_source_admitted": False,
            "target_result_columns_present": current["target_outcome_fields_present"]}
        compared.append(entry); old_inputs.append(_file(path))
        if differences: conflicts.append(entry)
    result = {"profile": PROFILE, "classification": "FRESH_CSV_IDENTITY_AND_INPUT_RECONCILIATION_NOT_ACTIVE_OR_NUMERICAL_ADMISSION",
        "fresh_zip_raw_sha256": capture["raw_sha256"], "fresh_capture_at": capture["captured_at"],
        "races_compared": len(compared), "listed": sum(x["fresh_listed"] for x in compared),
        "races_with_changed_numerical_inputs": len(conflicts), "race_comparisons": compared,
        "old_numerical_artifacts_manifest": old_inputs,
        "new_live_races": 0, "new_score_computations": 0, "formal_coverage_increment": 0}
    result["sha256"] = sha(result)
    return result
