"""Offered NAR CSV -> existing 63/29 arithmetic for the LISTED field only.

This offline reference computation does not pass SOURCE admission, infer an
Active universe, verify changes/signatures, or activate Prediction Consumers.
No current-race outcome or aggregate record is invented as individual history.
The independent Decimal witness reparses the original CSV, not compiler output.
"""
from __future__ import annotations

import csv
from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import zipfile

from runtime.local_nar_csv_reference import inspect_zip, SCHEMAS
from runtime import local_base63_source_witness as witness

PROFILE = "KM-FNB-CSV-PRELIMINARY-LISTED-NUMERICAL-v1"
CLASSIFICATION = "PRELIMINARY_LISTED_REFERENCE_NOT_ACTIVE_VERIFIED_NOT_FORMAL"


def _sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _number(value, integer=False):
    if value in (None, ""):
        return None
    result = Decimal(str(value))
    if not result.is_finite() or integer and result != result.to_integral_value():
        raise ValueError("CSV_PRELIMINARY_NONFINITE_OR_NONINTEGRAL_NUMBER")
    return int(result) if integer else float(result)


def _load_number(value):
    if value in (None, ""):
        return None
    # Official CSV prints the apprentice allowance mark in this same cell.
    # The printed number already is the carried weight: do not subtract again.
    match = re.fullmatch(r"[▲△☆★◇]?(\d+(?:\.\d+)?)", str(value).strip())
    if match is None:
        raise ValueError("CSV_PRELIMINARY_CARRIED_WEIGHT_CELL_UNRECOGNIZED")
    return _number(match[1])


def _independent_csv_field(raw, capture, race, encoding):
    """Separate CSV traversal and facts for the existing Decimal witness."""
    key = ("船橋", race["race_date"].replace("-", ""), str(race["race_no"]))
    context = None
    horses = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        if archive.testzip() is not None:
            raise ValueError("CSV_PRELIMINARY_INDEPENDENT_CRC_FAILURE")
        for kind in ("racelist", "horselist"):
            names = [n for n in archive.namelist() if n.endswith("_"+kind+".csv")]
            if len(names) != 1:
                raise ValueError("CSV_PRELIMINARY_INDEPENDENT_TABLE_AMBIGUOUS")
            reader = csv.DictReader(io.StringIO(archive.read(names[0]).decode(encoding), newline=""))
            if tuple(reader.fieldnames or []) != SCHEMAS[kind]:
                raise ValueError("CSV_PRELIMINARY_INDEPENDENT_HEADER_MISMATCH")
            for line, row in enumerate(reader, 2):
                if (row["競馬場"], row["競走年月日"], row["レース番号"]) != key:
                    continue
                if kind == "racelist":
                    if context is not None:
                        raise ValueError("CSV_PRELIMINARY_INDEPENDENT_RACE_DUPLICATE")
                    context = {"venue": "FNB", "distance": int(row["距離"]),
                        "direction": {"左": "LEFT", "右": "RIGHT", "直": "STRAIGHT"}[row["回り"]],
                        "surface": {"芝": "TURF", "ダート": "DIRT"}[row["芝ダート区分"]],
                        "going": row["馬場"], "race_titles": [row["レース名"]],
                        "raw_table": names[0], "raw_csv_row": line}
                else:
                    rid = str(int(row["馬番"]))
                    if rid in horses:
                        raise ValueError("CSV_PRELIMINARY_INDEPENDENT_RUNNER_DUPLICATE")
                    horses[rid] = {"runner_id": rid, "horse_no": int(rid), "name": row["馬名"],
                        "jockey": witness.jockey(row["騎手名"]),
                        "load": witness.number(re.sub(r"^[▲△☆★◇]", "", row["負担重量"])) if row["負担重量"] else None,
                        "body_weight": _number(row["馬体重"], True),
                        "body_weight_change": _number(row["馬体重増減"], True),
                        "sire": row["父馬名"], "dam": row["母馬名"],
                        "damsire": row["母父馬名"], "trainer": row["調教師"], "history": [],
                        "raw_table": names[0], "raw_csv_row": line,
                        "zip_raw_sha256": capture["raw_sha256"]}
    if context is None or not horses:
        raise ValueError("CSV_PRELIMINARY_INDEPENDENT_IDENTITY_NOT_FOUND")
    return context, horses


def materialize_preliminary(raw, *, capture, race, repo_root=None,
                            encoding="utf-8-sig", header_mode="present", now=None):
    """Compute the unchanged candidate transforms without asserting admission.

    Every output is tied to original bytes. Only a future, outcome-free race
    can use this preliminary path; expired/result data needs a different audit.
    """
    root = Path(repo_root or Path(__file__).resolve().parents[1]).resolve()
    parsed = inspect_zip(raw, capture=capture, race=race, encoding=encoding,
                         header_mode=header_mode, now=now)
    identity = parsed["race_identity"]
    post = datetime.fromisoformat(identity["scheduled_post_at"])
    observed = datetime.fromisoformat(capture["captured_at"].replace("Z", "+00:00"))
    checked = now or datetime.now(timezone.utc)
    if checked.tzinfo is None:
        raise ValueError("CSV_PRELIMINARY_AWARE_NOW_REQUIRED")
    if observed >= post or checked >= post or parsed["target_outcome_fields_present"]:
        raise ValueError("CSV_PRELIMINARY_FUTURE_OUTCOME_FREE_RACE_REQUIRED")
    source_id = "NAR-CSV-LISTED-"+capture["raw_sha256"]
    snapshot = parsed["sha256"]
    request = {"family_id": "LOCAL", "venue_id": "FNB", "race_date": race["race_date"],
        "race_no": race["race_no"], "race_id": "KM-LOCAL-FNB-"+race["race_date"].replace("-", "")
            +"-R"+str(race["race_no"]).zfill(2)+"-CSV-LISTED-REFERENCE",
        "classification": CLASSIFICATION, "scheduled_post_at": identity["scheduled_post_at"],
        "prediction_cutoff": (post-timedelta(seconds=300)).isoformat(),
        "cutoff_basis": "PRIVATE_RESEARCH_300S_REFERENCE_NOT_OFFICIAL_CUTOFF_RESOLUTION",
        "race": {"venue": "船橋", "distance_m": identity["distance_m"],
            "direction": identity["turn"], "surface": identity["surface"],
            "class": parsed["race_reference_fields"]["レース名"],
            "name": parsed["race_reference_fields"]["レース名"]},
        "runners": [{"runner_id": str(x["runner_number"]), "name": x["horse_name"]}
                    for x in parsed["runners"]]}
    source = {"schema": PROFILE, "classification": CLASSIFICATION,
        "source_freeze_at": capture["captured_at"], "source_snapshot_sha256": snapshot,
        "sources": [{"source_id": source_id, "snapshot_sha256": snapshot,
                     "raw_sha256": capture["raw_sha256"], "format": "application/zip",
                     "requested_url": capture["source_url"], "fetched_at": capture["captured_at"]}],
        "normalized_evidence": {"track_condition": {"value": parsed["race_reference_fields"]["馬場"] or None},
            "weather": {"value": parsed["race_reference_fields"]["天候"] or None}},
        "active_runner_universe_verified": False, "formal_source_admitted": False,
        "production_numeric_consumers_authorized": False}
    raw_field = {}
    from runtime.local_fnb_csv_source_admission import printed_csv_market
    for runner in parsed["runners"]:
        fields = runner["prestart_reference_fields"]
        rid = str(runner["runner_number"])
        raw_field[rid] = {"runner_id": rid, "horse_no": int(rid), "name": runner["horse_name"],
            "frame_no": _number(fields["枠番"], True), "current_jockey": fields["騎手名"],
            "current_load": _load_number(fields["負担重量"]), "age": _number(fields["齢"], True),
            "current_body_weight": _number(fields["馬体重"], True),
            "current_body_weight_change": _number(fields["馬体重増減"], True),
            "sire": fields["父馬名"], "dam": fields["母馬名"], "damsire": fields["母父馬名"],
            "trainer": fields["調教師"], "starts": [],
            **printed_csv_market(runner,listed_count=len(parsed['runners']),capture=capture),
            "horse_id": None, "sire_id": None, "damsire_id": None,
            "jockey_id": None, "stable_id": None,
            "race_card_source_id": source_id, "race_card_snapshot_sha256": snapshot,
            "race_card_fetched_at": capture["captured_at"], "field_provenance": runner["field_provenance"]}
    if str(root/"runtime") not in sys.path:
        sys.path.insert(0, str(root/"runtime"))
    from runtime.local_nar_evidence_candidate import compile_parsed_candidate_evidence
    from runtime.local_fullnumerical_candidate import materialize_candidate
    from runtime.local_fnb_r8_arithmetic_29 import verify_29
    registry_path = root/"mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json"
    mapping_path = root/"mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json"
    registry = json.loads(registry_path.read_bytes())
    mapping = json.loads(mapping_path.read_bytes())
    compiled = compile_parsed_candidate_evidence(source, request, raw_field, registry_path)
    numerical = materialize_candidate(compiled, registry_path, mapping_path)
    context, independent = _independent_csv_field(raw, capture, race, encoding)
    if {k: witness.compact(v["name"]) for k,v in independent.items()} != {
            k: witness.compact(v["name"]) for k,v in raw_field.items()}:
        raise ValueError("CSV_PRELIMINARY_INDEPENDENT_LISTED_SET_MISMATCH")
    with localcontext() as ctx:
        ctx.prec = 40
        rows, indices = witness.independently_score(independent, source, request, registry,
            context=context, management={"prior_result_count": 0, "prior_race_numbers": [],
                                         "odds_source_present": False})
    actual = {str(x["runner_id"]): x for x in numerical["runners"]}
    for row in rows:
        old = actual[row["runner_id"]]["evidence_features"][row["component"]]
        row["comparison"] = "MATCH" if (abs(Decimal(str(old["score"]))-Decimal(str(row["witness_score"]))) <= witness.EPSILON
            and old["missing"] == row["missing"]
            and abs(Decimal(str(old["coverage"]))-Decimal(str(row["coverage"]))) <= witness.EPSILON
            and old["rule_id"] == row["rule_id"]) else "MISMATCH"
        row["original_csv_row"] = independent[row["runner_id"]]["raw_csv_row"]
        row["original_csv_table"] = independent[row["runner_id"]]["raw_table"]
        row["original_zip_sha256"] = capture["raw_sha256"]
    for row in indices:
        value = actual[row["runner_id"]]["canonical_components"][row["index"]]["value"]
        row["comparison"] = "MATCH" if abs(Decimal(str(value))-Decimal(str(row["witness_value"]))) <= witness.EPSILON else "MISMATCH"
    arithmetic29 = verify_29(numerical, registry, mapping)
    receipt = {"profile": PROFILE, "classification": CLASSIFICATION,
        "race_id": request["race_id"], "listed_runners": len(raw_field),
        "original_zip_sha256": capture["raw_sha256"], "observed_at": capture["captured_at"],
        "source_snapshot_sha256": snapshot, "registry_sha256": hashlib.sha256(registry_path.read_bytes()).hexdigest(),
        "mapping_sha256": hashlib.sha256(mapping_path.read_bytes()).hexdigest(),
        "component_records": len(rows), "component_matches": sum(x["comparison"] == "MATCH" for x in rows),
        "missing_components": sum(x["missing"] for x in rows),
        "management_records": sum(x["evidence_quality"] == "MANAGEMENT" for x in rows),
        "nonmanagement_nonmissing_records": sum(not x["missing"] and x["index"] != "DCR" for x in rows),
        "base_index_records": len(indices), "base_index_matches": sum(x["comparison"] == "MATCH" for x in indices),
        "arithmetic29": arithmetic29,
        "active_universe_verified": False, "current_changes_verified": False,
        "formal_source_admitted": False, "production_consumers_authorized": False,
        "registered_oos_increment": 0, "live_accepted_races": 0,
        "aggregate_records_used_as_individual_history": False,
        "independent_csv_reparse": True, "independent_decimal_rule_execution": True,
        "empirical_measurement_complete_63": False,
        "listed_field_relative_scores_require_active_recomputation": True}
    receipt["sha256"] = _sha(receipt)
    numerical["csv_preliminary_reference"] = receipt
    return {"parsed": parsed, "source": source, "request": request,
        "raw_field": raw_field, "numerical": numerical, "receipt": receipt,
        "component_witness": rows, "base_index_witness": indices}
