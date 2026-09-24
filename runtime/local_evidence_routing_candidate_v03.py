from __future__ import annotations

import copy
import hashlib
import json
import math
import re
import statistics
import unicodedata
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from local_nar_evidence_candidate import (
    compile_candidate_evidence,
    _clamp,
    _going_group,
    _norm,
)

PROFILE = "KM-LOCAL-NUMERICAL-EVIDENCE-ROUTING-v0.3-CANDIDATE-20260925"
DEFAULT_REGISTRY = "mapping/local_evidence_feature_rule_registry_v0.3_candidate_20260925_evidence_routing.json"
BASELINE_REGISTRY = "mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json"
DESIGN_FREEZE_DATE = "2026-09-25"
NEUTRAL = 52.0


class LocalEvidenceRoutingV03Error(ValueError):
    pass


def _sha(x: Any) -> str:
    return hashlib.sha256(
        json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _load(path: str | Path) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _as_float(x: Any) -> float | None:
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)) and math.isfinite(float(x)):
        return float(x)
    m = re.search(r"-?\d+(?:\.\d+)?", unicodedata.normalize("NFKC", str(x or "")).replace(",", ""))
    return float(m.group()) if m else None


def _finish_score(finish: Any, field_size: Any) -> float | None:
    try:
        f = int(finish)
        n = int(field_size)
    except Exception:
        return None
    if f < 1 or n < 2:
        return None
    return _clamp(100.0 * (n - min(f, n)) / (n - 1))


def _mean(xs: Iterable[float | None]) -> float | None:
    v = [float(x) for x in xs if x is not None and math.isfinite(float(x))]
    return None if not v else sum(v) / len(v)


def _recency_weighted(xs: List[float | None], *, max_items: int = 8) -> float | None:
    vals = [(i, float(x)) for i, x in enumerate(xs[:max_items]) if x is not None and math.isfinite(float(x))]
    if not vals:
        return None
    weights = [1.00, 0.88, 0.77, 0.67, 0.58, 0.50, 0.43, 0.37]
    num = den = 0.0
    for i, x in vals:
        w = weights[min(i, len(weights) - 1)]
        num += x * w
        den += w
    return num / den if den else None


def _venue_eq(a: Any, b: Any) -> bool:
    aa = _norm(a).replace("ナ", "")
    bb = _norm(b).replace("ナ", "")
    return bool(aa and bb and (aa == bb or aa in bb or bb in aa))


def _history_perf(rows: List[Dict[str, Any]], pred) -> Tuple[float | None, float, int]:
    hit = [r for r in rows if pred(r)]
    vals = [_finish_score(r.get("finish"), r.get("field_size")) for r in hit]
    vals = [x for x in vals if x is not None]
    score = _recency_weighted(vals)
    coverage = min(1.0, len(vals) / 5.0)
    return score, coverage, len(vals)


def _feature_rule_id(index: str, component: str) -> str:
    return f"LOCAL-NUM-CAND-v0.3-{index}-{component}"


def _set_feature(
    runner: Dict[str, Any],
    component: str,
    *,
    index: str,
    score: float | None,
    fact: str,
    refs: Iterable[str],
    coverage: float,
    raw_metric: Any,
    missing: bool | None = None,
    source_window: str,
    source_timestamp: str | None = None,
) -> None:
    feats = runner["evidence_features"]
    old = copy.deepcopy(feats.get(component) or {})
    miss = bool(score is None) if missing is None else bool(missing)
    val = NEUTRAL if score is None else _clamp(float(score))
    feats[component] = {
        **old,
        "score": round(val, 6),
        "rule_id": _feature_rule_id(index, component),
        "evidence_refs": sorted(set(str(x) for x in refs if x)),
        "source_fact": fact,
        "source_timestamp": str(source_timestamp or old.get("source_timestamp") or ""),
        "missing": miss,
        "coverage": round(max(0.0, min(1.0, float(coverage))), 6),
        "candidate_only": True,
        "production_authority": False,
        "calibration_status": "UNVALIDATED_EVIDENCE_ROUTING_CANDIDATE",
        "raw_metric": raw_metric,
        "evidence_window": source_window,
        "routing_profile": PROFILE,
    }


def _source_fetched_at(source: Dict[str, Any], source_id: Any, fallback: Any = None) -> str:
    """Resolve the timestamp of the concrete source snapshot used by a routed feature.

    Feature provenance must point to the source that actually supplied the fact.
    Falling back to SOURCE freeze is allowed for deterministic derived ledgers, but
    a horse/rider profile must not inherit the race-card fetch time by accident.
    """
    sid = str(source_id or "")
    if sid:
        for row in source.get("sources") or []:
            if str((row or {}).get("source_id") or "") == sid:
                ts = (row or {}).get("fetched_at")
                if ts:
                    return str(ts)
    if fallback:
        return str(fallback)
    return str(source.get("source_freeze_at") or "")


def _profile_maps(source: Dict[str, Any]):
    aux = source.get("auxiliary_evidence") or {}
    profiles = aux.get("profiles") or {}
    registry = profiles.get("runner_entity_registry") or []
    by_runner = {str(x.get("runner_id")): x for x in registry if x.get("runner_id") is not None}
    return (
        profiles.get("horses") or {},
        profiles.get("riders") or {},
        profiles.get("trainers") or {},
        by_runner,
        aux.get("same_day_position_bias") or {},
    )


def _person_top3_rate(stat: Dict[str, Any] | None) -> float | None:
    if not isinstance(stat, dict):
        return None
    total = int(stat.get("total") or 0)
    if total <= 0:
        return None
    return _clamp(100.0 * (
        int(stat.get("first") or 0) + int(stat.get("second") or 0) + int(stat.get("third") or 0)
    ) / total)


def _popularity_band_score(profile: Dict[str, Any], *, favorite: bool) -> Tuple[float | None, int]:
    bands = []
    for _, rows in (profile.get("yearly_popularity_bands") or {}).items():
        for r in rows or []:
            m = re.search(r"(\d+)", str(r.get("label") or ""))
            if not m:
                continue
            pop = int(m.group(1))
            if (favorite and pop <= 3) or ((not favorite) and pop >= 6):
                bands.append(r)
    total = sum(int(x.get("total") or 0) for x in bands)
    if total <= 0:
        return None, 0
    top3 = sum(
        int(x.get("first") or 0) + int(x.get("second") or 0) + int(x.get("third") or 0)
        for x in bands
    )
    return _clamp(100.0 * top3 / total), total


def _distance_bucket(value: Any) -> str:
    try:
        return str((int(value) // 100) * 100)
    except Exception:
        return "UNKNOWN"


def _pedigree_cohort(
    ledger: Dict[str, Any],
    *,
    key: str,
    name: str,
    venue: str,
    distance: int,
    going: str,
) -> Dict[str, Any] | None:
    if not name:
        return None
    groups = ledger.get("sire_cohorts" if key == "sire" else "damsire_cohorts") or []
    db = _distance_bucket(distance)
    gg = _going_group(going)
    candidates = [
        x for x in groups
        if str(x.get(key) or "") == str(name)
        and _venue_eq(x.get("venue"), venue)
        and str(x.get("distance_bucket")) == db
        and str(x.get("going_group")) == gg
    ]
    if not candidates:
        return None
    best = max(candidates, key=lambda x: int(x.get("starts") or 0))
    observations = [
        x for x in (ledger.get("observations") or [])
        if str(x.get(key) or "") == str(name)
        and _venue_eq(x.get("venue"), venue)
        and str(x.get("distance_bucket")) == db
        and str(x.get("going_group")) == gg
    ]
    distinct = len({str(x.get("runner_id")) for x in observations if x.get("runner_id") is not None})
    if int(best.get("starts") or 0) < 20 or distinct < 3:
        return None
    return {**best, "distinct_horses": distinct}


def _context_shadow(source: Dict[str, Any], rid: str) -> Dict[str, Any]:
    aux = source.get("auxiliary_evidence") or {}
    jma = source.get("jma_weather_evidence") or {}
    sbo = source.get("sbo_public_shadow_evidence") or {}
    sbo_runner = next(
        (x for x in (sbo.get("runners") or []) if str(x.get("horse_no")) == str(rid)),
        None,
    )
    return {
        "same_day_position_bias": copy.deepcopy(aux.get("same_day_position_bias") or {}),
        "jma_weather": {
            "profile": jma.get("profile"),
            "status": jma.get("status"),
            "station": jma.get("station"),
            "observation": jma.get("observation"),
            "production_authority": False,
        },
        "sbo_public_shadow": {
            "profile": sbo.get("profile"),
            "status": sbo.get("status"),
            "oos_eligible": sbo.get("oos_eligible"),
            "runner": copy.deepcopy(sbo_runner),
            "production_authority": False,
            "ability_index_weight": 0,
        },
    }


def compile_candidate_evidence_v03(
    source_artifact: Dict[str, Any],
    request: Dict[str, Any],
    registry_path: str | Path = DEFAULT_REGISTRY,
) -> Dict[str, Any]:
    """Compile v0.3 evidence-routing shadow.

    This starts from the deterministic v0.1 parser so runner identity and the 63
    component schema stay identical, then reroutes already-captured pre-cutoff
    evidence. It never mutates Production prediction or uses post-result data.
    """
    reg = _load(registry_path)
    if "v0.3" not in str(reg.get("registry_id")):
        raise LocalEvidenceRoutingV03Error("V03_REGISTRY_REQUIRED")

    out = compile_candidate_evidence(source_artifact, request, BASELINE_REGISTRY)
    horses, riders, trainers, entities, same_day = _profile_maps(source_artifact)
    ledger = source_artifact.get("point_in_time_population_ledger") or {}
    race = request.get("race") or {}
    venue = str(race.get("venue") or race.get("venue_id") or request.get("venue_id") or "")
    distance = int(race.get("distance") or 0)
    going = str(
        ((source_artifact.get("normalized_evidence") or {}).get("track_condition") or {}).get("value")
        or race.get("going") or ""
    )
    surface = str(race.get("surface") or "dirt").upper()
    aux_sha = source_artifact.get("auxiliary_evidence_sha256")
    pop_sha = source_artifact.get("point_in_time_population_ledger_sha256")
    jma_sha = source_artifact.get("jma_weather_evidence_sha256")
    sbo_sha = source_artifact.get("sbo_public_shadow_evidence_sha256")
    source_freeze_ts = str(source_artifact.get("source_freeze_at") or "")

    for runner in out.get("runners") or []:
        rid = str(runner.get("runner_id"))
        raw = runner.get("raw_candidate_evidence") or {}
        hp = horses.get(rid) or {}
        hist = list(hp.get("history") or [])
        h_refs = [hp.get("source_id"), hp.get("source_snapshot_sha256"), aux_sha]
        horse_source_ts = _source_fetched_at(source_artifact, hp.get("source_id"), source_freeze_ts)
        entity = entities.get(rid) or {}
        rider_profile = riders.get(str(entity.get("rider_license_no") or "")) or {}
        trainer_profile = trainers.get(str(entity.get("trainer_license_no") or "")) or {}
        rider_source_ts = _source_fetched_at(source_artifact, rider_profile.get("source_id"), source_freeze_ts)
        trainer_source_ts = _source_fetched_at(source_artifact, trainer_profile.get("source_id"), source_freeze_ts)

        # CFI: full pre-target horse history, not the race-card last-five window.
        same_venue, cov, n = _history_perf(hist, lambda r: _venue_eq(r.get("venue"), venue))
        _set_feature(runner, "same_venue", index="CFIg-L", score=same_venue,
                     fact=f"full pre-target NAR horse history same venue={venue}; matched={n}/{len(hist)}",
                     refs=h_refs, coverage=cov, raw_metric={"matched": n, "history": len(hist)},
                     source_window="FULL_PRE_TARGET_NAR_HORSE_HISTORY",
                     source_timestamp=horse_source_ts)

        same_dist, cov, n = _history_perf(hist, lambda r: int(r.get("distance") or -1) == distance)
        _set_feature(runner, "same_distance", index="CFIg-L", score=same_dist,
                     fact=f"full pre-target NAR horse history same distance={distance}; matched={n}/{len(hist)}",
                     refs=h_refs, coverage=cov, raw_metric={"matched": n, "history": len(hist)},
                     source_window="FULL_PRE_TARGET_NAR_HORSE_HISTORY",
                     source_timestamp=horse_source_ts)

        similar, cov, n = _history_perf(
            hist,
            lambda r: r.get("distance") is not None and abs(int(r.get("distance")) - distance) <= max(200, int(distance * 0.20)),
        )
        _set_feature(runner, "similar_distance", index="CFIg-L", score=similar,
                     fact=f"full pre-target similar-distance window around {distance}m; matched={n}/{len(hist)}",
                     refs=h_refs, coverage=cov, raw_metric={"matched": n, "history": len(hist)},
                     source_window="FULL_PRE_TARGET_NAR_HORSE_HISTORY",
                     source_timestamp=horse_source_ts)

        wet, cov, n = _history_perf(hist, lambda r: _going_group(r.get("going")) == _going_group(going))
        _set_feature(runner, "going_fit", index="CFIg-L", score=wet,
                     fact=f"full pre-target going-group match={_going_group(going)}; matched={n}/{len(hist)}",
                     refs=h_refs, coverage=cov, raw_metric={"matched": n, "history": len(hist)},
                     source_window="FULL_PRE_TARGET_NAR_HORSE_HISTORY_PLUS_CURRENT_NAR_OFFICIAL_GOING",
                     source_timestamp=horse_source_ts)

        # RFI: only the going-adaptation component can be extended safely from
        # profile history because NAR horse profile history does not expose all
        # corner positions. Position components retain their observed last-five inputs.
        _set_feature(runner, "going_adaptation", index="RFIg-L", score=wet,
                     fact=f"full pre-target performance under current going-group={_going_group(going)}; no invented corner positions",
                     refs=h_refs, coverage=cov, raw_metric={"matched": n, "history": len(hist)},
                     source_window="FULL_PRE_TARGET_NAR_HORSE_HISTORY",
                     source_timestamp=horse_source_ts)

        # BVI: point-in-time population ledger is selection-biased shadow. Use only
        # cohorts with >=20 starts and >=3 distinct horses; otherwise remain UNKNOWN.
        sire = str(raw.get("sire") or "")
        damsire = str(raw.get("damsire") or "")
        sire_row = _pedigree_cohort(ledger, key="sire", name=sire, venue=venue, distance=distance, going=going)
        damsire_row = _pedigree_cohort(ledger, key="damsire", name=damsire, venue=venue, distance=distance, going=going)
        _set_feature(runner, "sire_fit", index="BVIg-L",
                     score=(100.0 * float(sire_row["top3_rate"]) if sire_row and sire_row.get("top3_rate") is not None else None),
                     fact=("point-in-time sire cohort descriptive top3 rate; minimum sample passed"
                           if sire_row else "point-in-time sire cohort insufficient/selection-biased; remain UNKNOWN"),
                     refs=[pop_sha], coverage=(min(1.0, int(sire_row.get("starts") or 0) / 60.0) if sire_row else 0),
                     raw_metric=sire_row, source_window="POINT_IN_TIME_PRE_TARGET_POPULATION_LEDGER",
                     source_timestamp=source_freeze_ts)
        _set_feature(runner, "damsire_fit", index="BVIg-L",
                     score=(100.0 * float(damsire_row["top3_rate"]) if damsire_row and damsire_row.get("top3_rate") is not None else None),
                     fact=("point-in-time damsire cohort descriptive top3 rate; minimum sample passed"
                           if damsire_row else "point-in-time damsire cohort insufficient/selection-biased; remain UNKNOWN"),
                     refs=[pop_sha], coverage=(min(1.0, int(damsire_row.get("starts") or 0) / 60.0) if damsire_row else 0),
                     raw_metric=damsire_row, source_window="POINT_IN_TIME_PRE_TARGET_POPULATION_LEDGER",
                     source_timestamp=source_freeze_ts)

        # JTI: retain horse/rider pair-specific evidence where appropriate, but use
        # official rider popularity bands for favorite/longshot reliability.
        fav_score, fav_n = _popularity_band_score(rider_profile, favorite=True)
        lng_score, lng_n = _popularity_band_score(rider_profile, favorite=False)
        rider_refs = [rider_profile.get("source_id"), rider_profile.get("source_snapshot_sha256"), aux_sha]
        _set_feature(runner, "favorite_reliability", index="JTI-L", score=fav_score,
                     fact=f"NAR rider profile popularity-band top3 rate for popularity<=3; starts={fav_n}",
                     refs=rider_refs, coverage=min(1.0, fav_n / 50.0), raw_metric={"starts": fav_n},
                     source_window="NAR_RIDER_PROFILE_PRE_CUTOFF",
                     source_timestamp=rider_source_ts)
        _set_feature(runner, "longshot_record", index="JTI-L", score=lng_score,
                     fact=f"NAR rider profile popularity-band top3 rate for popularity>=6; starts={lng_n}",
                     refs=rider_refs, coverage=min(1.0, lng_n / 50.0), raw_metric={"starts": lng_n},
                     source_window="NAR_RIDER_PROFILE_PRE_CUTOFF",
                     source_timestamp=rider_source_ts)

        # CSI: trainer profile is preserved as context and never mislabeled as
        # venue/class/distance specificity. Layoff/transfer remain horse-history based.
        runner["candidate_trainer_profile_context_v03"] = {
            "source_id": trainer_profile.get("source_id"),
            "source_snapshot_sha256": trainer_profile.get("source_snapshot_sha256"),
            "source_timestamp": trainer_source_ts,
            "latest_year": copy.deepcopy(trainer_profile.get("latest_year")),
            "lifetime_local": copy.deepcopy(trainer_profile.get("lifetime_local")),
            "production_authority": False,
            "direct_score_binding": False,
        }

        # BWI: use all pre-target bodyweight observations rather than only last five.
        bw_rows = [
            (int(r["body_weight"]), _finish_score(r.get("finish"), r.get("field_size")))
            for r in hist if isinstance(r.get("body_weight"), int)
        ]
        good = [bw for bw, perf in bw_rows if perf is not None and perf >= 60]
        current_bw = raw.get("current_body_weight")
        gwr = None
        if isinstance(current_bw, int) and good:
            lo, hi = min(good) - 5, max(good) + 5
            gwr = 85.0 if lo <= current_bw <= hi else _clamp(85.0 - 2.0 * min(abs(current_bw - lo), abs(current_bw - hi)))
        _set_feature(runner, "good_weight_range", index="BWI-L", score=gwr,
                     fact=f"full pre-target bodyweight history; current={current_bw}; good-range samples={len(good)}",
                     refs=h_refs, coverage=min(1.0, len(good) / 6.0), raw_metric={"good_weights": good},
                     source_window="FULL_PRE_TARGET_NAR_HORSE_HISTORY",
                     source_timestamp=horse_source_ts)

        bw_cov = min(1.0, (int(isinstance(current_bw, int)) + len(bw_rows)) / 10.0)
        _set_feature(runner, "bodyweight_range_coverage", index="DCR", score=100.0 * bw_cov,
                     fact=f"full pre-target bodyweight observations={int(isinstance(current_bw,int))+len(bw_rows)}/10 target",
                     refs=h_refs, coverage=1.0, raw_metric=bw_cov,
                     source_window="FULL_PRE_TARGET_NAR_HORSE_HISTORY",
                     source_timestamp=horse_source_ts)

        comparable = sum(
            1 for r in hist if _venue_eq(r.get("venue"), venue) and int(r.get("distance") or -1) == distance
        )
        comp_cov = min(1.0, comparable / 5.0)
        _set_feature(runner, "same_venue_distance_comparability", index="DCR", score=100.0 * comp_cov,
                     fact=f"full pre-target same venue+distance comparable runs={comparable}",
                     refs=h_refs, coverage=1.0, raw_metric=comparable,
                     source_window="FULL_PRE_TARGET_NAR_HORSE_HISTORY",
                     source_timestamp=horse_source_ts)

        races_observed = int(same_day.get("races_observed") or 0)
        race_no = int(request.get("race_no") or race.get("race_no") or 1)
        same_day_cov = min(1.0, races_observed / max(1, race_no - 1))
        _set_feature(runner, "same_day_gci_coverage", index="DCR", score=100.0 * same_day_cov,
                     fact=f"same-day official result coverage races={races_observed}/{max(0,race_no-1)}",
                     refs=[aux_sha, same_day.get("sha256")], coverage=1.0, raw_metric=same_day_cov,
                     source_window="SAME_DAY_PRE_TARGET_OFFICIAL_RESULTS",
                     source_timestamp=source_freeze_ts)

        runner["candidate_context_features_v03"] = _context_shadow(source_artifact, rid)
        runner["candidate_context_features_v03"]["rider_profile_latest_year"] = copy.deepcopy(rider_profile.get("latest_year"))
        runner["candidate_context_features_v03"]["trainer_profile_latest_year"] = copy.deepcopy(trainer_profile.get("latest_year"))
        runner["candidate_context_features_v03"]["source_authority_boundary"] = {
            "NAR_AUXILIARY": "CANDIDATE_FEATURE_INPUT_ALLOWED_PRE_CUTOFF",
            "JMA": "CONTEXT_ONLY_UNLESS_RULE_BOUND",
            "SBO": "DIAGNOSTIC_ONLY_NO_ABILITY_INDEX_WEIGHT",
            "POINT_IN_TIME_POPULATION": "SHADOW_MIN_SAMPLE_ONLY",
        }

        missing = []
        for idx, comps in reg.get("common_component_sets", {}).items():
            for comp in comps:
                f = (runner.get("evidence_features") or {}).get(comp) or {}
                if bool(f.get("missing")):
                    missing.append(f"{idx}.{comp}")
        runner["candidate_missing_components"] = sorted(set(missing))
        runner["candidate_missing_count"] = len(runner["candidate_missing_components"])
        runner["candidate_component_count"] = sum(len(v) for v in reg.get("common_component_sets", {}).values())
        runner["candidate_feature_coverage_ratio"] = round(
            1.0 - runner["candidate_missing_count"] / max(1, runner["candidate_component_count"]), 6
        )
        runner["candidate_evidence_sha256"] = _sha({
            "features": runner.get("evidence_features"),
            "context": runner.get("candidate_context_features_v03"),
            "trainer_context": runner.get("candidate_trainer_profile_context_v03"),
        })

    out["candidate_evidence_compiler"] = {
        "profile": PROFILE,
        "registry_id": reg["registry_id"],
        "production_authority": False,
        "source_snapshot_sha256": source_artifact.get("source_snapshot_sha256"),
        "official_runner_universe_sha256": source_artifact.get("official_runner_universe_sha256"),
        "auxiliary_evidence_sha256": aux_sha,
        "population_ledger_sha256": pop_sha,
        "jma_weather_evidence_sha256": jma_sha,
        "sbo_public_shadow_evidence_sha256": sbo_sha,
        "runner_count": len(out.get("runners") or []),
        "result_derived_features": 0,
        "design_freeze_date": DESIGN_FREEZE_DATE,
        "missing_policy": "OBSERVED_ONLY_RENORMALIZE",
        "sbo_ability_index_weight": 0,
        "provenance_policy": "FEATURE_TIMESTAMP_MUST_MATCH_CONCRETE_SOURCE_SNAPSHOT; JMA/SBO CONTEXT SHA MUST NOT APPEAR IN ABILITY FEATURE REFS UNLESS RULE-BOUND",
    }
    out["candidate_evidence_compiler"]["sha256"] = _sha(out["candidate_evidence_compiler"])
    out["candidate_v03_policy"] = {
        "profile": PROFILE,
        "production_effect": "NONE",
        "weight_change_from_v01": False,
        "evidence_routing_change": True,
        "unknown_is_average": False,
        "future_oos_required": True,
        "historical_20260924_replays_are_oos": False,
    }
    return out
