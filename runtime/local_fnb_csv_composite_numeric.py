"""Optional private composite-identity hypothesis study using archived Raw.

Current permanent IDs remain unknown. This is a separate supplemental research
comparison, never a current-identity assertion or qualified SOURCE admission.
All score transforms and weights are the existing candidate v0.1 definitions.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path

from runtime import local_base63_source_witness as witness
from runtime.local_fnb_csv_preliminary_numeric import materialize_preliminary, _independent_csv_field
from runtime.local_fnb_r8_arithmetic_29 import verify_29

CLASSIFICATION = "PRELIMINARY_COMPOSITE_IDENTITY_HYPOTHESIS_RESEARCH_NOT_ACTIVE_VERIFIED_NOT_FORMAL"
_CURRENT_ONLY = {"carried_weight", "current_class", "race_set_level", "sire_fit", "damsire_fit",
    "distance_sustain", "distance_trait", "surface_sand_fit", "venue_stat", "physical_style_fit",
    "stable_combo", "stable_venue_class_distance", "cci_specificity", "tri_vertical_comparison",
    "weight_change_reason_rate", "age_growth", "transport_season", "paddock",
    "training_comment_trial", "same_day_gci_coverage", "late_odds_changes_coverage"}


def _key(fields):
    return tuple(witness.compact(fields[k]) for k in ("馬名", "父馬名", "母馬名", "母父馬名")) + (
        witness.compact(fields["性"]+fields["齢"]),)


def materialize_composite_reference(raw, *, capture, race, archive_index, repo_root=None, now=None):
    """Recompute with explicit archived label-match hypotheses; no promotion."""
    root = Path(repo_root or Path(__file__).resolve().parents[1]).resolve()
    baseline = materialize_preliminary(raw, capture=capture, race=race, repo_root=root, now=now)
    request = deepcopy(baseline["request"])
    request["classification"] = CLASSIFICATION
    request["race_id"] = request["race_id"].replace("-CSV-LISTED-REFERENCE", "-CSV-COMPOSITE-HYPOTHESIS")
    source = deepcopy(baseline["source"])
    source["classification"] = CLASSIFICATION
    current = deepcopy(baseline["raw_field"])
    context, independent = _independent_csv_field(raw, capture, race, "utf-8-sig")
    joins = {}
    target_day = date.fromisoformat(race["race_date"])
    index_receipt = archive_index.get("receipt") or {}
    try:
        index_as_of = datetime.fromisoformat(index_receipt["as_of"].replace("Z", "+00:00"))
        captured_at = datetime.fromisoformat(capture["captured_at"].replace("Z", "+00:00"))
        qualified_index = (index_as_of.tzinfo is not None and index_as_of == captured_at
            and index_receipt.get("target_year") == target_day.year
            and index_receipt.get("current_permanent_ids_inferred") is False
            and index_receipt.get("source_or_consumer_authority_granted") is False)
    except (KeyError, ValueError, TypeError):
        qualified_index = False
    if not qualified_index:
        raise ValueError("CSV_COMPOSITE_EXACT_CAPTURE_ASOF_HYPOTHESIS_INDEX_REQUIRED")
    records = archive_index.get("entries", archive_index.get("records", archive_index))
    for runner in baseline["parsed"]["runners"]:
        rid = str(runner["runner_number"])
        key = _key(runner["prestart_reference_fields"])
        entry = records.get(key)
        if not entry or entry.get("status") != "UNIQUE_ARCHIVED_COMPOSITE_HYPOTHESIS":
            continue
        if len(entry["starts"]) != len(entry["independent_history"]):
            raise ValueError("CSV_COMPOSITE_HISTORY_PAIR_COUNT_MISMATCH")
        paired = []
        for old, own in zip(entry["starts"], entry["independent_history"]):
            stamp = date(2000+int(old["date"][:2]), int(old["date"][3:5]), int(old["date"][6:8]))
            if stamp != own["date"]:
                raise ValueError("CSV_COMPOSITE_HISTORY_PAIR_DATE_MISMATCH")
            if stamp >= target_day:
                continue
            paired.append((stamp, old, own))
        paired.sort(key=lambda p: p[0], reverse=True)
        paired = paired[:5]
        if not paired:
            continue
        current[rid]["starts"] = deepcopy([p[1] for p in paired])
        independent[rid]["history"] = deepcopy([p[2] for p in paired])
        current[rid]["horse_id"] = None
        current[rid]["history_identity_status"] = "RESEARCH_COMPOSITE_LABEL_MATCH_WITH_ARCHIVED_OBSERVED_ID"
        current[rid]["history_composite_provenance"] = deepcopy(entry["provenance"])
        joins[rid] = {"match_key": list(key), "current_permanent_horse_id": None,
            "archived_observed_horse_id": entry["archived_observed_id"],
            "birthdate_reconciled": False, "current_identity_verified": False,
            "identity_classification": current[rid]["history_identity_status"],
            "dated_starts_used": len(paired), "source_refs": entry["source_refs"],
            "provenance": entry["provenance"]}
    from runtime.local_nar_evidence_candidate import compile_parsed_candidate_evidence
    from runtime.local_fullnumerical_candidate import materialize_candidate
    registry_path = root/"mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json"
    mapping_path = root/"mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json"
    registry = json.loads(registry_path.read_bytes())
    mapping = json.loads(mapping_path.read_bytes())
    compiled = compile_parsed_candidate_evidence(source, request, current, registry_path)
    for runner in compiled["runners"]:
        join = joins.get(str(runner["runner_id"]))
        if not join:
            continue
        for name, feature in runner["evidence_features"].items():
            if name in _CURRENT_ONLY:
                continue
            feature["evidence_refs"] = sorted(set(feature["evidence_refs"]+join["source_refs"]))
            feature["history_identity_qualification"] = join["identity_classification"]
            feature["current_identity_verified"] = False
        runner["candidate_evidence_sha256"] = hashlib.sha256(json.dumps(runner["evidence_features"],
            ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    numerical = materialize_candidate(compiled, registry_path, mapping_path)
    with localcontext() as ctx:
        ctx.prec = 40
        rows, indices = witness.independently_score(independent, source, request, registry,
            context=context, management={"prior_result_count": 0, "prior_race_numbers": [], "odds_source_present": False})
    actual = {str(r["runner_id"]): r for r in numerical["runners"]}
    old_rows = {(r["runner_id"], r["component"]): r for r in baseline["component_witness"]}
    for row in rows:
        feature = actual[row["runner_id"]]["evidence_features"][row["component"]]
        row["comparison"] = "MATCH" if (abs(Decimal(str(feature["score"]))-Decimal(str(row["witness_score"]))) <= witness.EPSILON
            and feature["missing"] == row["missing"] and abs(Decimal(str(feature["coverage"]))-Decimal(str(row["coverage"]))) <= witness.EPSILON
            and feature["rule_id"] == row["rule_id"]) else "MISMATCH"
        row["baseline_missing"] = old_rows[(row["runner_id"], row["component"])]["missing"]
        row["history_identity_qualification"] = joins.get(row["runner_id"], {}).get("identity_classification")
    for row in indices:
        value = actual[row["runner_id"]]["canonical_components"][row["index"]]["value"]
        row["comparison"] = "MATCH" if abs(Decimal(str(value))-Decimal(str(row["witness_value"]))) <= witness.EPSILON else "MISMATCH"
    arithmetic29 = verify_29(numerical, registry, mapping)
    summary = {"classification": CLASSIFICATION, "race_id": request["race_id"],
        "listed_runners": len(current), "composite_hypotheses_consumed": len(joins),
        "history_starts_consumed": sum(j["dated_starts_used"] for j in joins.values()),
        "component_records": len(rows), "component_matches": sum(x["comparison"] == "MATCH" for x in rows),
        "base_index_records": len(indices), "base_index_matches": sum(x["comparison"] == "MATCH" for x in indices),
        "missing_components": sum(x["missing"] for x in rows),
        "baseline_missing_components": baseline["receipt"]["missing_components"],
        "new_nonmissing_hypothesis_components": sum(x["baseline_missing"] and not x["missing"] for x in rows),
        "evidence_quality_counts": dict(Counter(x["evidence_quality"] for x in rows)),
        "arithmetic29": arithmetic29, "original_zip_sha256": capture["raw_sha256"],
        "source_identity_hypothesis_not_qualified_current_id": True,
        "formal_source_admitted": False, "active_universe_verified": False,
        "registered_oos_increment": 0, "live_accepted_races": 0,
        "production_consumers_authorized": False, "new_numeric_policy": False,
        "archive_index_receipt": deepcopy(index_receipt)}
    numerical["csv_composite_reference"] = summary
    return {"request": request, "source": source, "parsed": baseline["parsed"], "raw_field": current,
        "numerical": numerical, "summary": summary, "identity_hypotheses": joins,
        "component_witness": rows, "base_index_witness": indices}
