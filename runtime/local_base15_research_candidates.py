"""Unadopted LOCAL base-component hypotheses; never a Production score provider.

The fifteen complete nonmissing mappings are absent from the inherited canon.
Every mapping and every numerical choice in this module is therefore a *new
research hypothesis*.  This module does not import, patch, or emit the formal
evidence Registry, Owner inputs, DCR, Static, KRS, tickets, or signed artifacts.
An UNKNOWN has score=None, never 52 or zero.  The formal missing terminal is
unchanged.  Fixture arithmetic does not qualify a measurement or a forecast.
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping


PROFILE = "KM-LOCAL-BASE15-RESEARCH-CANDIDATES-v0.1-20261103"
CLASSIFICATION = "PRIVATE_RESEARCH_UNADOPTED_NOT_OOS_NOT_PRODUCTION"
MIN_REFERENCE_ENTITIES = 3  # New research choice, not an inherited requirement.
JTI_HALF_LIFE_DAYS = 180.0  # Research choice; Article14 specifies decay, not this number.
MIN_JTI_EFFECTIVE_RACES = 5.0  # New research pilot floor, not Article14 text.
MIN_STABLE_RACE_COUNT = 10  # New research pilot floor; not claimed as canon.
TRI_GOOD_RUN_MAX_FINISH = 3  # New research label, not an inherited good-run definition.
CANON_BVI_CONDITION_RACES = 30  # Article67 condition set, NOT thirty per parent.
CODING_PROTOCOL = "KM-LOCAL-BASE15-OBSERVATIONAL-RUBRIC-v0.1-20261103"


def _spec(index: str, component: str, weight: int, articles: list[int],
          observation: str, columns: list[str], recipe: str,
          identity: list[str], overlap: list[str], use: str = "RESEARCH_ONLY") -> dict:
    return dict(
        rule_id=f"LOCAL-NUM-PROD-v1.0-{index}-{component}",
        research_rule_id=f"{PROFILE}:{index}:{component}", index=index,
        component=component, formal_weight_unchanged=weight,
        inherited_articles=articles, inherited_complete_score_formula=False,
        observation_target=observation, required_columns=columns,
        identity_fields=identity, raw_recipe=recipe,
        transform_candidate="100*(count(reference_raw<target_raw)+0.5*count(reference_raw==target_raw))/N",
        transform_origin="NEW_RESEARCH_MIDRANK_HYPOTHESIS_NOT_CANONICAL_FORMULA",
        neutral_semantics="50 is an empirical midrank, not the formal missing terminal52",
        missing_semantics="UNKNOWN score=null; no missing52 is reclassified as a measurement",
        intended_consumer=use, overlap_components=overlap,
        confidence_interval=dict(value=None,
            reason="reference groups may share races/horses; independence and sampling design are not established",
            required_before_statistical_CI="preregister a complete sampling frame and race-cluster resampling; validate coverage on held-out days"),
        measurement_interval="if a source measurement has a range, no scalar is formed here; retain UNKNOWN until an independently adopted interval mapping exists",
        reference_population="pre-Freeze complete enumeration, >=3 distinct prespecified comparison entities; exact selector and all sources hash-bound",
        temporal_rule="every source observation and event strictly precedes immutable prediction Freeze; historical auxiliary post-Freeze snapshots excluded",
        dcr_effect="none: formal DCR and coverage remain unchanged; research admissibility reported separately",
        downstream_effect="none: no automatic W/P2/P3, Owner, KRS or ticket consumption; later adoption requires full29 Before/After and frozen forward comparison",
        registry_compatibility="separate research_rule_id; formal rule_id is a reference only; formal weights/formula/terminal unchanged",
        uncertainty="observational association; no causal aptitude/skill claim; no probability or EV interpretation",
        falsification=["out-of-day direction reverses or confidence intervals fail coverage",
            "improvement disappears after class/horse-quality/popularity stratification",
            "same-information ablation shows no increment or redundant component inflation",
            "reliable coverage falls below the preregistered usable subset"],
        production_requirements=["explicit numerical Policy adoption and Scope",
            "Provider/source qualification and permanent Identity audit",
            "independent actual-Raw arithmetic and range/denominator tests",
            "prospective sampling, calibration and uncertainty validation",
            "frozen W/P2/P3, Pair/Third, six-method Capital evaluation without hindsight"],
        adopted=False, production_enabled=False,
    )


RULE_SPECS = [
    _spec("BVIg-L", "sire_fit", 30, [13, 67], "conditional sire offspring observed Top3 rate",
          ["sire_id", "finish", "race_id", "horse_id", "venue", "distance_m", "surface", "going", "class", "sand_era"],
          "race-cluster mean of I(finish<=3); using a Top3 event rather than extending Article67's undefined fourth-and-later points",
          ["sire_id"], ["damsire_fit", "venue_stat", "HPI-L"]),
    _spec("BVIg-L", "damsire_fit", 20, [13, 67], "conditional damsire offspring observed Top3 rate",
          ["damsire_id", "finish", "race_id", "horse_id", "venue", "distance_m", "surface", "going", "class", "sand_era"],
          "race-cluster mean of I(finish<=3); descriptive offspring association, not causal heredity",
          ["damsire_id"], ["sire_fit", "venue_stat", "HPI-L"]),
    _spec("BVIg-L", "distance_sustain", 15, [13, 67], "named last-corner to finish preservation/advance",
          ["parent_id", "finish", "last_corner_rank", "last_corner_name", "field_size", "race_id", "horse_id", "distance_m"],
          "race-cluster mean((last_corner_rank-finish)/(field_size-1)); Singleton only, no grouped-position midpoint",
          ["parent_id"], ["RFIg-L", "distance_trait"]),
    _spec("BVIg-L", "distance_trait", 10, [13, 67], "parent-group target-distance association relative to a prespecified other distance",
          ["parent_id", "finish", "field_size", "distance_m", "race_id", "horse_id"],
          "mean finish percentile at target distance minus mean at prespecified reference_distance_m; no post-result distance bin selection",
          ["parent_id"], ["distance_sustain", "CFIg-L"]),
    _spec("BVIg-L", "surface_sand_fit", 15, [13, 67], "parent-group target going/sand-era association",
          ["parent_id", "finish", "field_size", "going", "sand_era", "race_id", "horse_id"],
          "mean finish percentile in target going minus prespecified reference going, within the same surface and sand era",
          ["parent_id"], ["sire_fit", "CFIg-L"]),
    _spec("BVIg-L", "venue_stat", 5, [13, 67], "parent-group venue association relative to a prespecified comparison venue",
          ["parent_id", "finish", "field_size", "venue", "race_id", "horse_id"],
          "mean finish percentile at target venue minus prespecified comparison venue; surface/distance/class/era remain matched",
          ["parent_id"], ["sire_fit", "damsire_fit", "CFIg-L"]),
    _spec("BVIg-L", "physical_style_fit", 5, [13, 67], "target's pre-Freeze body/style resemblance to qualified parent-group Top3 observations",
          ["parent_id", "body_weight_kg", "style_fraction", "finish", "race_id", "horse_id"],
          "negative mean two-dimensional Gower distance from target to Top3 offspring; weight range uses complete group, style is pre-Freeze singleton-derived [0,1]",
          ["parent_id"], ["RFIg-L", "BWI-L", "HPI-L"]),
    _spec("JTI-L", "stable_combo", 15, [14], "jockey x stable observed Top3 performance",
          ["jockey_id", "stable_id", "finish", "race_id", "horse_id", "event_at", "jockey_active_verified", "jockey_active_source_sha256", "official_jockey_status"],
          "race-cluster mean I(finish<=3), exponentially weighted 2^(-age_days/180) in the declared complete twelve-month frame",
          ["jockey_id", "stable_id"], ["JTI-L.venue", "CSI-L.stable_venue_class_distance", "HPI-L"]),
    _spec("CSI-L", "stable_venue_class_distance", 25, [17], "stable's exactly matching venue/class/distance observed Top3 performance",
          ["stable_id", "finish", "race_id", "horse_id", "venue", "class", "distance_m"],
          "race-cluster mean I(finish<=3); exact condition matching; pilot minimum10 independent races is a new research floor",
          ["stable_id"], ["JTI-L.stable_combo", "HPI-L"]),
    _spec("CSI-L", "cci_specificity", 15, [15, 17], "comment evidence specificity, not positive ability",
          ["horse_id", "comment_text", "speaker_id", "explicit_time", "explicit_condition", "explicit_comparison", "explicit_uncertainty", "coding_protocol", "independent_coder_agreement"],
          "four prespecified evidence dimensions each present=1/absent=0, mean; two coders must agree; missing context is UNKNOWN, not absent",
          ["horse_id", "speaker_id"], ["CCI", "TRI"], "EVIDENCE_QUALITY_ONLY_NO_ABILITY_UPLIFT"),
    _spec("CSI-L", "tri_vertical_comparison", 15, [16, 17], "same horse's preparation resemblance to its own past good-run preparation",
          ["horse_id", "work_type", "effort", "distance_m", "work_time_seconds", "good_run_preparation", "good_run_result_source_sha256", "good_run_result_event_at", "good_run_result_race_id", "good_run_result_finish", "good_run_result_field_size", "race_id"],
          "negative absolute distance of current work seconds from same-horse matched preparation preceding a verified historical Top3 result, divided by matched-history range; Top3 label is a new research choice; zero range gives UNKNOWN, faster is not automatically better",
          ["horse_id"], ["TRI", "CCI", "BWI-L"]),
    _spec("BWI-L", "weight_change_reason_rate", 15, [18, 68], "independently evidenced weight-change reason compatibility",
          ["horse_id", "current_weight_kg", "previous_weight_kg", "official_delta_kg", "reason_evidence_id", "reason_expected_delta_low_kg", "reason_expected_delta_high_kg"],
          "audit Article68 delta%=100*delta/previous; raw=-distance(delta,[independently evidenced expected low,high])/previous; reason interval is not inferred from the observed delta itself",
          ["horse_id"], ["BWI-L.good_weight_range", "CSI-L"]),
    _spec("BWI-L", "age_growth", 10, [18, 68], "horse-specific directly corroborated muscular growth, not age alone",
          ["horse_id", "age_years", "sex", "prior_muscle_grade", "current_muscle_grade", "growth_cause_evidence_id", "fatigue_excluded", "excess_fat_excluded", "coding_protocol"],
          "current-minus-prior same-horse muscle grade/2 on a frozen0..2 anatomical rubric; cause attribution and fatigue/fat exclusion must be independently evidenced",
          ["horse_id"], ["paddock", "weight_change_reason_rate"]),
    _spec("BWI-L", "transport_season", 5, [18, 68], "matched observed state preservation over actual transport under season conditions",
          ["horse_id", "transport_id", "transport_departure_at", "transport_arrival_at", "season_match_id", "prior_state_grade", "current_state_grade", "coding_protocol"],
          "current-minus-prior matched state grade/2 with actual transport timing and prespecified season comparator; calendar month or stable address alone never creates a penalty",
          ["horse_id", "transport_id"], ["paddock", "CSI-L", "weight_change_reason_rate"]),
    _spec("BWI-L", "paddock", 10, [18, 68], "observed current condition with reproducible anatomy/gait rubric",
          ["horse_id", "observer_ids", "grades", "coding_protocol"],
          "mean of six0..2 condition grades (abdomen,hindquarters,coat,gait,arousal,sweat)/2; two independent observers must agree on every dimension; arousal/sweat graded as condition, never more-is-better",
          ["horse_id"], ["CSI-L", "TRI", "weight_change_reason_rate"]),
]
for _rule in RULE_SPECS:
    if _rule["component"] in ("sire_fit", "damsire_fit", "stable_combo", "stable_venue_class_distance", "physical_style_fit"):
        _rule["required_columns"] = sorted(set(_rule["required_columns"] + ["field_size"]))
SPEC_BY_ID = {s["rule_id"]: s for s in RULE_SPECS}
SPEC_BY_COMPONENT = {f"{s['index']}.{s['component']}": s for s in RULE_SPECS}


class Ineligible(ValueError):
    """A research data qualification failure, never a low measurement score."""


def canonical_sha256(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def _time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise Ineligible("TIMESTAMP_MISSING")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Ineligible("TIMESTAMP_INVALID") from exc
    if result.tzinfo is None:
        raise Ineligible("TIMESTAMP_TIMEZONE_REQUIRED")
    return result


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise Ineligible(f"FINITE_NUMBER_REQUIRED:{label}")
    return float(value)


def _required(obj: Mapping, key: str) -> Any:
    if key not in obj or obj[key] is None or obj[key] == "":
        raise Ineligible(f"OBSERVATION_MISSING:{key}")
    return obj[key]


def _rank(row: Mapping, key: str) -> int:
    v = _number(_required(row, key), key)
    n = _number(_required(row, "field_size"), "field_size")
    if int(v) != v or int(n) != n or not 1 <= v <= n or n < 2:
        raise Ineligible(f"POINT_RANK_OR_FIELD_INVALID:{key}")
    return int(v)


def _finish_percentile(row: Mapping) -> float:
    return 1.0 - (_rank(row, "finish") - 1) / (_number(row["field_size"], "field_size") - 1)


def _race_mean(rows: list[Mapping], value) -> float:
    by_race: dict[str, list[float]] = {}
    for row in rows:
        by_race.setdefault(str(_required(row, "race_id")), []).append(value(row))
    if not by_race:
        raise Ineligible("NO_QUALIFIED_RACES")
    return statistics.mean(statistics.mean(v) for v in by_race.values())


def _grade(obj: Mapping, key: str) -> float:
    value = _number(_required(obj, key), key)
    if value not in (0, 1, 2):
        raise Ineligible(f"ORDINAL_RUBRIC_GRADE_INVALID:{key}")
    return value


def _validate_source_fact(fact: Mapping, freeze: datetime, sources: Mapping) -> None:
    sha = _required(fact, "source_sha256")
    if not isinstance(sha, str) or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
        raise Ineligible("SOURCE_SHA_INVALID")
    if sha not in sources:
        raise Ineligible("SOURCE_NOT_BOUND_TO_MANIFEST")
    source = sources[sha]
    if _required(source, "raw_sha256") != sha:
        raise Ineligible("SOURCE_MANIFEST_HASH_MISMATCH")
    _required(source, "source_id")
    observed = _time(_required(source, "observed_at"))
    event = _time(_required(fact, "event_at"))
    if observed >= freeze or event >= freeze:
        raise Ineligible("POST_FREEZE_SOURCE_OR_EVENT")
    if event > observed:
        raise Ineligible("EVENT_AFTER_SOURCE_OBSERVATION")
    if source.get("qualification") != "ELIGIBLE_PRIVATE_RESEARCH":
        raise Ineligible("SOURCE_QUALIFICATION_UNVERIFIED")


def _validate_entity(spec: Mapping, entity: Mapping, freeze: datetime,
                     sources: Mapping, selector: Mapping) -> None:
    if not isinstance(entity, Mapping):
        raise Ineligible("ENTITY_OBJECT_REQUIRED")
    for key in spec["identity_fields"]:
        value = _required(entity, key)
        if not isinstance(value, str) or not value.startswith(str(selector["provider"]) + ":"):
            raise Ineligible(f"PERMANENT_PROVIDER_ID_REQUIRED:{key}")
    rows = _required(entity, "rows")
    if not isinstance(rows, list) or not rows:
        raise Ineligible("NO_QUALIFIED_OBSERVATIONS")
    seen: set[tuple] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            raise Ineligible("ROW_OBJECT_REQUIRED")
        _validate_source_fact(row, freeze, sources)
        horse = _required(row, "horse_id")
        if not isinstance(horse, str) or not horse.startswith(str(selector["provider"]) + ":"):
            raise Ineligible("PERMANENT_HORSE_ID_REQUIRED")
        key = (_required(row, "race_id"), horse)
        if key in seen:
            raise Ineligible("DUPLICATE_RACE_HORSE_ROW")
        seen.add(key)
        if "horse_id" in spec["identity_fields"] and horse != entity["horse_id"]:
            raise Ineligible("SAME_HORSE_ROW_IDENTITY_MISMATCH")
        if "distance_m" in row and _number(row["distance_m"], "distance_m") <= 0:
            raise Ineligible("POSITIVE_DISTANCE_REQUIRED")
        for name, expected in selector["exact_conditions"].items():
            if name in selector.get("contrast_fields", []):
                continue
            if _required(row, name) != expected:
                raise Ineligible(f"COMPARISON_CONDITION_MISMATCH:{name}")
        for name in spec["identity_fields"]:
            if name in ("parent_id", "sire_id", "damsire_id", "stable_id", "jockey_id"):
                if _required(row, name) != entity[name]:
                    raise Ineligible(f"ENTITY_IDENTITY_MISMATCH:{name}")
    if spec["component"] == "stable_combo":
        status_sha = _required(entity, "jockey_active_source_sha256")
        if status_sha not in sources:
            raise Ineligible("JOCKEY_ACTIVE_SOURCE_NOT_BOUND")
        status_source = sources[status_sha]
        if status_source.get("authority") != "NAR_OFFICIAL":
            raise Ineligible("JOCKEY_ACTIVE_OFFICIAL_SOURCE_REQUIRED")
        statuses = _required(status_source, "official_jockey_status")
        if not isinstance(statuses, Mapping):
            raise Ineligible("JOCKEY_ACTIVE_STATUS_MAPPING_REQUIRED")
        jockey_id = entity["jockey_id"]
        if jockey_id not in statuses:
            raise Ineligible("JOCKEY_ACTIVE_SAME_ID_STATUS_MISSING")
        status = statuses[jockey_id]
        if not isinstance(status, Mapping) or status.get("jockey_id") != jockey_id:
            raise Ineligible("JOCKEY_ACTIVE_SOURCE_IDENTITY_MISMATCH")
        _validate_source_fact({"source_sha256": status_sha,
                               "event_at": _required(status, "event_at")}, freeze, sources)
        jst = timezone(timedelta(hours=9))
        prediction_date = freeze.astimezone(jst).date()
        if (_time(status["event_at"]).astimezone(jst).date() != prediction_date or
                _time(status_source["observed_at"]).astimezone(jst).date() != prediction_date):
            raise Ineligible("JOCKEY_ACTIVE_NOT_VERIFIED_ON_PREDICTION_JST_DATE")
        if status.get("active") is not True:
            raise Ineligible("JOCKEY_NOT_OFFICIALLY_ACTIVE")
    if spec["component"] == "physical_style_fit" or spec["index"] in ("CSI-L", "BWI-L") and spec["component"] != "stable_venue_class_distance":
        current = _required(entity, "current")
        _validate_source_fact(current, freeze, sources)
        current_horse = _required(current, "horse_id")
        if not isinstance(current_horse, str) or not current_horse.startswith(str(selector["provider"])+":"):
            raise Ineligible("CURRENT_PERMANENT_HORSE_ID_REQUIRED")
        if _required(current, "horse_id") != entity.get("horse_id", current["horse_id"]):
            raise Ineligible("CURRENT_SAME_HORSE_IDENTITY_MISMATCH")
        if spec["component"] == "tri_vertical_comparison":
            for row in rows:
                if row.get("good_run_preparation") is True:
                    outcome = {"source_sha256": _required(row, "good_run_result_source_sha256"),
                               "event_at": _required(row, "good_run_result_event_at")}
                    _validate_source_fact(outcome, freeze, sources)
                    finish_fact = {"finish": _required(row, "good_run_result_finish"),
                                   "field_size": _required(row, "good_run_result_field_size")}
                    if _rank(finish_fact, "finish") > TRI_GOOD_RUN_MAX_FINISH:
                        raise Ineligible("TRI_GOOD_RUN_LABEL_NOT_TOP3")
                    if _required(row, "good_run_result_race_id") != row["race_id"]:
                        raise Ineligible("TRI_GOOD_RUN_RESULT_RACE_MISMATCH")
                    if _time(outcome["event_at"]) <= _time(row["event_at"]):
                        raise Ineligible("TRI_GOOD_RUN_RESULT_MUST_FOLLOW_PREPARATION")
        for name in ("speaker_id", "transport_id"):
            if name in spec["identity_fields"] and _required(current, name) != entity[name]:
                raise Ineligible(f"CURRENT_IDENTITY_MISMATCH:{name}")
        if spec["component"] in ("paddock", "age_growth", "transport_season"):
            if _required(current, "baseline_horse_id") != current_horse:
                raise Ineligible("BASELINE_SAME_HORSE_IDENTITY_MISMATCH")
            baseline = {"source_sha256": _required(current, "baseline_source_sha256"),
                        "event_at": _required(current, "baseline_event_at")}
            _validate_source_fact(baseline, freeze, sources)
            if _time(baseline["event_at"]) >= _time(current["event_at"]):
                raise Ineligible("BASELINE_NOT_PRIOR_TO_CURRENT_OBSERVATION")


def raw_metric(rule_id: str, entity: Mapping, freeze: datetime, selector: Mapping) -> tuple[float, dict]:
    """Calculate a hypothesis's observation statistic, not its Production score."""
    spec = SPEC_BY_ID.get(rule_id) or SPEC_BY_COMPONENT.get(rule_id)
    if spec is None:
        raise Ineligible("UNKNOWN_RESEARCH_RULE")
    c = spec["component"]
    rows = entity["rows"]
    detail: dict[str, Any] = {"rows": len(rows), "independent_race_ids": len({r["race_id"] for r in rows})}
    if c in ("sire_fit", "damsire_fit", "stable_venue_class_distance", "stable_combo"):
        if c == "stable_venue_class_distance" and detail["independent_race_ids"] < MIN_STABLE_RACE_COUNT:
            raise Ineligible("RESEARCH_STABLE_PILOT_FLOOR_10_RACES")
        event = lambda r: float(_rank(r, "finish") <= 3)
        if c != "stable_combo":
            return _race_mean(rows, event), detail
        if entity.get("jockey_active_verified") is not True or selector.get("complete_twelve_months") is not True:
            raise Ineligible("CURRENT_JOCKEY_OR_COMPLETE_TWELVE_MONTH_FRAME_UNVERIFIED")
        try:
            window_start = freeze.replace(year=freeze.year-1)
        except ValueError:  # Leap-day anniversary is the final February day.
            window_start = freeze.replace(year=freeze.year-1, day=28)
        if _time(_required(selector, "population_window_start")) != window_start:
            raise Ineligible("EXACT_TWELVE_MONTH_WINDOW_START_REQUIRED")
        numerator = denominator = squared_weights = 0.0
        race_rows: dict[str, list[Mapping]] = {}
        for row in rows:
            age = (freeze - _time(row["event_at"])).total_seconds() / 86400
            if not window_start <= _time(row["event_at"]) < freeze:
                raise Ineligible("JTI_OUTSIDE_DECLARED_TWELVE_MONTH_FRAME")
            race_rows.setdefault(row["race_id"], []).append(row)
        for rr in race_rows.values():
            age = (freeze - _time(rr[0]["event_at"])).total_seconds() / 86400
            w = 2 ** (-age / JTI_HALF_LIFE_DAYS)
            numerator += w * statistics.mean(event(r) for r in rr)
            denominator += w
            squared_weights += w*w
        detail["decay_weight_sum"] = denominator
        detail["effective_races_kish"] = denominator**2/squared_weights
        if detail["effective_races_kish"] < MIN_JTI_EFFECTIVE_RACES:
            raise Ineligible("RESEARCH_JTI_PILOT_FLOOR_5_EFFECTIVE_RACES")
        return numerator / denominator, detail
    if c == "distance_sustain":
        def gain(row):
            _required(row, "last_corner_name")
            return (_rank(row, "last_corner_rank") - _rank(row, "finish")) / (row["field_size"] - 1)
        return _race_mean(rows, gain), detail
    if c in ("distance_trait", "surface_sand_fit", "venue_stat"):
        field = {"distance_trait": "distance_m", "surface_sand_fit": "going", "venue_stat": "venue"}[c]
        contrast = _required(selector, "contrast")
        if field not in selector.get("contrast_fields", []) or contrast.get("field") != field:
            raise Ineligible("PRESPECIFIED_CONTRAST_FIELD_REQUIRED")
        target, reference = _required(contrast, "target"), _required(contrast, "reference")
        if target == reference:
            raise Ineligible("CONTRAST_MUST_DIFFER")
        a = [r for r in rows if _required(r, field) == target]
        b = [r for r in rows if r[field] == reference]
        if len(a) + len(b) != len(rows):
            raise Ineligible("OUTSIDE_PRESPECIFIED_CONTRAST")
        return _race_mean(a, _finish_percentile) - _race_mean(b, _finish_percentile), detail
    if c == "physical_style_fit":
        good = [r for r in rows if _rank(r, "finish") <= 3]
        if not good:
            raise Ineligible("NO_QUALIFIED_TOP3_OFFSPRING")
        weights = [_number(_required(r, "body_weight_kg"), "body_weight_kg") for r in rows]
        if any(w <= 0 for w in weights):
            raise Ineligible("POSITIVE_BODY_WEIGHT_REQUIRED")
        span = max(weights) - min(weights)
        if span <= 0:
            raise Ineligible("ZERO_BODY_WEIGHT_COMPARISON_RANGE")
        current = _required(entity, "current")
        tw = _number(_required(current, "target_body_weight_kg"), "target_body_weight_kg")
        ts = _number(_required(current, "target_style_fraction"), "target_style_fraction")
        if _required(current, "parent_id") != entity["parent_id"]:
            raise Ineligible("TARGET_PARENT_RELATION_IDENTITY_MISMATCH")
        if current.get("style_basis") != "PRE_FREEZE_SINGLETON_HISTORY":
            raise Ineligible("TARGET_QUALIFIED_STYLE_HISTORY_REQUIRED")
        if tw <= 0 or not 0 <= ts <= 1:
            raise Ineligible("TARGET_PHYSICAL_STYLE_INVALID")
        ds = []
        for r in good:
            style = _number(_required(r, "style_fraction"), "style_fraction")
            if not 0 <= style <= 1 or r.get("style_basis") != "PRE_FREEZE_SINGLETON_HISTORY":
                raise Ineligible("QUALIFIED_STYLE_HISTORY_REQUIRED")
            ds.append((abs(tw-r["body_weight_kg"])/span + abs(ts-style))/2)
        return -statistics.mean(ds), detail
    current = _required(entity, "current")
    if c in ("cci_specificity", "age_growth", "transport_season", "paddock"):
        if _required(current, "coding_protocol") != CODING_PROTOCOL:
            raise Ineligible("FIXED_CODING_PROTOCOL_REQUIRED")
    if c == "cci_specificity":
        _required(current, "comment_text")
        _required(current, "coding_protocol")
        if current.get("independent_coder_agreement") is not True:
            raise Ineligible("COMMENT_CODER_AGREEMENT_UNVERIFIED")
        flags = [_required(current, k) for k in ("explicit_time", "explicit_condition", "explicit_comparison", "explicit_uncertainty")]
        if any(type(v) is not bool for v in flags):
            raise Ineligible("COMMENT_FULL_CONTEXT_CODE_REQUIRED")
        return statistics.mean(float(v) for v in flags), detail
    if c == "tri_vertical_comparison":
        ct = _number(_required(current, "work_time_seconds"), "work_time_seconds")
        if ct <= 0:
            raise Ineligible("POSITIVE_WORK_TIME_REQUIRED")
        good = []
        for r in rows:
            if r["horse_id"] != entity["horse_id"]:
                raise Ineligible("TRI_SAME_HORSE_REQUIRED")
            for k in ("work_type", "effort", "distance_m"):
                if _required(r, k) != _required(current, k):
                    raise Ineligible(f"TRI_WORK_CONDITION_MISMATCH:{k}")
            if r.get("good_run_preparation") is True:
                value = _number(_required(r, "work_time_seconds"), "work_time_seconds")
                if value <= 0:
                    raise Ineligible("POSITIVE_WORK_TIME_REQUIRED")
                good.append(value)
        if len(good) < 2 or max(good) == min(good):
            raise Ineligible("INSUFFICIENT_SAME_HORSE_GOOD_PREPARATION_RANGE")
        return -abs(ct-statistics.median(good))/(max(good)-min(good)), detail
    if c == "weight_change_reason_rate":
        prev = _number(_required(current, "previous_weight_kg"), "previous_weight_kg")
        weight = _number(_required(current, "current_weight_kg"), "current_weight_kg")
        delta = _number(_required(current, "official_delta_kg"), "official_delta_kg")
        if min(prev, weight) <= 0 or weight-prev != delta:
            raise Ineligible("OFFICIAL_WEIGHT_DELTA_INCONSISTENT")
        _required(current, "reason_evidence_id")
        if current.get("reason_independent_of_delta") is not True:
            raise Ineligible("INDEPENDENT_REASON_EVIDENCE_REQUIRED")
        lo = _number(_required(current, "reason_expected_delta_low_kg"), "reason_expected_delta_low_kg")
        hi = _number(_required(current, "reason_expected_delta_high_kg"), "reason_expected_delta_high_kg")
        if lo > hi:
            raise Ineligible("REASON_INTERVAL_INVALID")
        detail["article68_raw_delta_pct"] = 100*delta/prev
        return -max(lo-delta, delta-hi, 0)/prev, detail
    if c == "age_growth":
        age = _number(_required(current, "age_years"), "age_years")
        if age < 0 or age != int(age) or _required(current, "sex") not in ("M", "F", "G"):
            raise Ineligible("AGE_OR_SEX_INVALID")
        _required(current, "coding_protocol")
        _required(current, "growth_cause_evidence_id")
        if current.get("fatigue_excluded") is not True or current.get("excess_fat_excluded") is not True:
            raise Ineligible("GROWTH_VS_FAT_FATIGUE_NOT_DISTINGUISHED")
        return (_grade(current, "current_muscle_grade")-_grade(current, "prior_muscle_grade"))/2, detail
    if c == "transport_season":
        _required(current, "season_match_id")
        _required(current, "coding_protocol")
        depart = _time(_required(current, "transport_departure_at"))
        arrive = _time(_required(current, "transport_arrival_at"))
        if _time(_required(current, "baseline_event_at")) > depart:
            raise Ineligible("TRANSPORT_BASELINE_NOT_BEFORE_DEPARTURE")
        if not depart < arrive <= _time(current["event_at"]) < freeze:
            raise Ineligible("ACTUAL_TRANSPORT_TIMING_INVALID")
        return (_grade(current, "current_state_grade")-_grade(current, "prior_state_grade"))/2, detail
    if c == "paddock":
        observers = _required(current, "observer_ids")
        _required(current, "coding_protocol")
        if not isinstance(observers, list) or len(set(observers)) < 2:
            raise Ineligible("TWO_INDEPENDENT_OBSERVERS_REQUIRED")
        grades = _required(current, "grades")
        values = []
        for dimension in ("abdomen", "hindquarters", "coat", "gait", "arousal", "sweat"):
            ratings = _required(grades, dimension)
            if not isinstance(ratings, list) or len(ratings) != len(observers):
                raise Ineligible("COMPLETE_OBSERVER_DIMENSION_REQUIRED")
            if len(set(ratings)) != 1:
                raise Ineligible("PADDOCK_OBSERVER_DISAGREEMENT")
            values.append(_grade({dimension: ratings[0]}, dimension)/2)
        return statistics.mean(values), detail
    raise Ineligible("RECIPE_NOT_IMPLEMENTED")


def evaluate_candidate(rule_id: str, packet: Mapping) -> dict:
    """Return a research score only after explicit data gates, never admission.

    packet = {classification, freeze_at, selector, selector_sha256, sources,
              target, references}.  The selector must be immutable before Freeze,
    explicitly mark population_complete, and enumerate the selected race IDs.
    Source qualification assertions here remain caller evidence; this evaluator
    does not turn them into provider permission or formal SOURCE verification.
    """
    spec = SPEC_BY_ID.get(rule_id) or SPEC_BY_COMPONENT.get(rule_id)
    result = dict(profile=PROFILE, classification=CLASSIFICATION,
                  production_adopted=False, formal_consumer_enabled=False,
                  rule_id=spec["rule_id"] if spec else str(rule_id),
                  research_rule_id=spec["research_rule_id"] if spec else None,
                  status="UNKNOWN", score=None, raw_metric=None, missing_reasons=[],
                  statistical_confidence_interval=None,
                  confidence_interval_reason="NOT_IDENTIFIED_SHARED_RACE_REFERENCE_DESIGN",
                  formal_missing_score_52_consumed=False, predictive_validity_proven=False,
                  provider_permission_verified_here=False, source_bytes_verified_here=False)
    try:
        if spec is None:
            raise Ineligible("UNKNOWN_RESEARCH_RULE")
        if packet.get("classification") != CLASSIFICATION:
            raise Ineligible("EXPLICIT_UNADOPTED_RESEARCH_CLASSIFICATION_REQUIRED")
        freeze = _time(_required(packet, "freeze_at"))
        selector = _required(packet, "selector")
        if packet.get("selector_sha256") != canonical_sha256(selector):
            raise Ineligible("SELECTOR_SHA_MISMATCH")
        if _time(_required(selector, "fixed_at")) >= freeze:
            raise Ineligible("SELECTOR_NOT_FIXED_BEFORE_FREEZE")
        _required(selector, "provider")
        if selector.get("population_complete") is not True:
            raise Ineligible("COMPLETE_COMPARISON_POPULATION_UNVERIFIED")
        if not isinstance(selector.get("exact_conditions"), Mapping) or not selector["exact_conditions"]:
            raise Ineligible("EXACT_COMPARISON_CONDITIONS_REQUIRED")
        if spec["index"] == "BVIg-L":
            for name in ("venue", "distance_m", "surface", "going", "class", "sand_era"):
                _required(selector["exact_conditions"], name)
        if spec["component"] == "stable_venue_class_distance":
            for name in ("venue", "class", "distance_m"):
                _required(selector["exact_conditions"], name)
            if selector.get("contrast_fields"):
                raise Ineligible("CSI_STABLE_EXACT_CONDITIONS_CANNOT_BE_CONTRASTED")
        race_ids = _required(selector, "condition_race_ids")
        if not isinstance(race_ids, list) or len(race_ids) != len(set(race_ids)):
            raise Ineligible("CONDITION_RACE_IDS_NOT_UNIQUE")
        if spec["index"] == "BVIg-L" and len(set(race_ids)) < CANON_BVI_CONDITION_RACES:
            raise Ineligible("ARTICLE67_CONDITION_SET_BELOW_30_RACES")
        sources = _required(packet, "sources")
        target = _required(packet, "target")
        references = _required(packet, "references")
        if not isinstance(references, list) or len(references) < MIN_REFERENCE_ENTITIES:
            raise Ineligible("RESEARCH_REFERENCE_ENTITY_FLOOR_3")
        entity_ids = [str(_required(e, "entity_id")) for e in references]
        if len(set(entity_ids)) != len(entity_ids) or target.get("entity_id") in entity_ids:
            raise Ineligible("REFERENCE_ENTITIES_NOT_DISTINCT_OR_SELF_INCLUDED")
        identities = [tuple(_required(e, k) for k in spec["identity_fields"]) for e in [target]+references]
        if len(set(identities)) != len(identities):
            raise Ineligible("PERMANENT_REFERENCE_IDENTITIES_NOT_DISTINCT")
        raw_values = []
        for entity in [target] + references:
            _validate_entity(spec, entity, freeze, sources, selector)
            if any(r["race_id"] not in race_ids for r in entity["rows"]):
                raise Ineligible("OBSERVATION_OUTSIDE_FIXED_RACE_FRAME")
            metric, detail = raw_metric(spec["rule_id"], entity, freeze, selector)
            raw_values.append(_number(metric, "derived_raw_metric"))
            if entity is target:
                result["observation_detail"] = detail
            if spec["component"] in ("weight_change_reason_rate", "age_growth"):
                current = entity["current"]
                prefix = "reason" if spec["component"] == "weight_change_reason_rate" else "growth_cause"
                fact = {"source_sha256": _required(current, prefix+"_source_sha256"),
                        "event_at": _required(current, prefix+"_event_at")}
                _validate_source_fact(fact, freeze, sources)
                if _time(fact["event_at"]) > _time(current["event_at"]):
                    raise Ineligible("CAUSE_EVIDENCE_AFTER_CURRENT_OBSERVATION")
                if _required(current, prefix+"_evidence_id") != sources[fact["source_sha256"]]["source_id"]:
                    raise Ineligible("INDEPENDENT_CAUSE_SOURCE_ID_MISMATCH")
        observed_race_ids = {r["race_id"] for e in [target]+references for r in e["rows"]}
        if observed_race_ids != set(race_ids):
            raise Ineligible("FIXED_RACE_FRAME_NOT_FULLY_REPRESENTED")
        if spec["index"] == "BVIg-L":
            conditions = selector["exact_conditions"]
            target_races = {r["race_id"] for e in [target]+references for r in e["rows"]
                            if all(r.get(k) == v for k, v in conditions.items())}
            if len(target_races) < CANON_BVI_CONDITION_RACES:
                raise Ineligible("ARTICLE67_TARGET_CONDITION_SET_BELOW_30_RACES")
            result["target_condition_independent_races"] = len(target_races)
        target_raw, refs = raw_values[0], raw_values[1:]
        score = 100*(sum(v < target_raw for v in refs)+0.5*sum(v == target_raw for v in refs))/len(refs)
        result.update(status="CALCULATED_RESEARCH_UNADOPTED", score=score,
                      raw_metric=target_raw, reference_raw_metrics=refs,
                      reference_entities=len(refs), selector_sha256=packet["selector_sha256"],
                      source_sha256s=sorted(sources), intended_consumer=spec["intended_consumer"])
    except Ineligible as exc:
        result["missing_reasons"] = [str(exc)]
    except (TypeError, KeyError, ValueError, OverflowError) as exc:
        result["status"] = "HOLD"
        result["missing_reasons"] = [f"MALFORMED_RESEARCH_INPUT:{type(exc).__name__}"]
    return result


def research_specification() -> dict:
    return dict(profile=PROFILE, classification=CLASSIFICATION, adopted=False,
                production_consumers_enabled=False, default_research_execution_only=True,
                research_parameter_choices={"min_reference_entities": MIN_REFERENCE_ENTITIES,
                    "jti_half_life_days": JTI_HALF_LIFE_DAYS,
                    "jti_pilot_minimum_effective_races": MIN_JTI_EFFECTIVE_RACES,
                    "stable_pilot_minimum_independent_races": MIN_STABLE_RACE_COUNT,
                    "tri_good_run_maximum_finish": TRI_GOOD_RUN_MAX_FINISH,
                    "all_origin": "NEW_UNADOPTED_RESEARCH_CHOICES_NOT_FORMAL_CANON"},
                inherited_requirements={"article67_minimum_comparable_condition_races": CANON_BVI_CONDITION_RACES,
                    "not_added": "no parent-specific thirty-race requirement"},
                coding_protocol=dict(id=CODING_PROTOCOL, origin="NEW_UNADOPTED_RESEARCH_RUBRIC",
                    cci_presence_codes={"explicit_time": "full quoted text identifies current/date-specific state",
                        "explicit_condition": "full quote states the distance/going/class/tactical condition",
                        "explicit_comparison": "full quote explicitly compares this horse with its identified prior state",
                        "explicit_uncertainty": "full quote states a concrete conditional limitation or uncertainty",
                        "false": "the complete quoted context was inspected and the specific dimension is absent",
                        "unknown": "text/context/coder agreement absent -> whole component UNKNOWN"},
                    muscle_grades={"0": "same-horse same-site measured muscle thickness decreased beyond instrument uncertainty",
                        "1": "same protocol paired thickness uncertainty intervals overlap",
                        "2": "same-horse same-site measured muscle thickness increased beyond uncertainty; independent growth cause evidence required",
                        "unknown": "visual impression, age alone, noncomparable site or unmeasured uncertainty -> UNKNOWN"},
                    state_grades={"0": "paired same-horse rubric corroborates poorer condition",
                        "1": "paired same-horse rubric corroborates unchanged condition",
                        "2": "paired same-horse rubric corroborates improved condition",
                        "unknown": "no matched before/after state observations or no prespecified seasonal comparator -> UNKNOWN"},
                    paddock_dimensions=["abdomen", "hindquarters", "coat", "gait", "arousal", "sweat"],
                    paddock_grades={"0": "both observers identify a concrete adverse change against dated same-horse baseline",
                        "1": "both observers corroborate unchanged within baseline variation",
                        "2": "both observers identify a concrete improvement against the same dated baseline",
                        "unknown": "unseen dimension, absent baseline or inter-observer disagreement -> UNKNOWN"},
                    observer_policy="two distinct actors; exact agreement on complete six dimensions; identities/dated baseline/raw evidence retained",
                    interpretation="condition/evidence descriptives; never a claim of new racing ability"),
                rule_count=len(RULE_SPECS), rules=RULE_SPECS)
