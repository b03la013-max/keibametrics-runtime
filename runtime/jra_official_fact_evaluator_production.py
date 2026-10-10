"""JRA official-source observed-feature evaluators for Production numerical mapping.

Only already-registered rules and genuinely observed *pre-race* facts can
create index inputs. Absent races, population stats, pedigree outcomes or
unmatched identities are not treated as neutral observations.
"""
from __future__ import annotations

import json
import math
from datetime import date, datetime
from pathlib import Path
from typing import Any

from jra_evidence_feature_normalizer_production import percentile_band, rate_band

PROFILE = "JRA-OFFICIAL-OBSERVED-FEATURE-PRODUCTION-IMPLEMENTATION-20261010"
RULES = {
    "recent_performance": "JRA-EVIDENCE-PERCENTILE-RECENT-PERFORMANCE-v1",
    "recent_consistency": "JRA-RECENT-CONSISTENCY-RATE-v1",
    "same_course_fit": "KM-JRA-SAME-COURSE-FIT-v1",
    "same_distance_fit": "KM-JRA-SAME-DISTANCE-FIT-v1",
    "surface_fit": "KM-JRA-SURFACE-FIT-v1",
    "going_fit": "KM-JRA-GOING-FIT-v1",
    "same_course_distance_quality": "KM-JRA-SAME-COURSE-DISTANCE-QUALITY-v1",
    "jockey_quality": "KM-JRA-JOCKEY-QUALITY-v1",
    "trainer_quality": "KM-JRA-TRAINER-QUALITY-v1",
}


def _date(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def _datetime(value: Any) -> datetime | None:
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt if dt.tzinfo else None
    except (ValueError, TypeError):
        return None


def _rows(obj: Any) -> dict[str, dict]:
    if isinstance(obj, dict):
        obj = obj.get("runners", obj)
    if isinstance(obj, dict):
        return {str(k): v for k, v in obj.items() if isinstance(v, dict)}
    if isinstance(obj, list):
        return {str(r.get("runner_id") or r.get("horse_no")): r
                for r in obj if isinstance(r, dict)
                and (r.get("runner_id") or r.get("horse_no")) is not None}
    return {}


def _observed_runs(history: dict, detail: dict, race_day: date) -> list[dict]:
    records = history.get("runs") or detail.get("recent_runs") or []
    out = []
    for x in records:
        if not isinstance(x, dict):
            continue
        day = _date(x.get("date"))
        if day is None or day >= race_day:
            continue
        try:
            finish, field = int(x["finish"]), int(x["field_size"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (field >= 2 and 1 <= finish <= field):
            continue
        out.append({**x, "finish": finish, "field_size": field, "date": str(day)})
    out.sort(key=lambda x: x["date"], reverse=True)
    return out


def official_production_observations(source: dict, registry: dict) -> dict[str, dict[str, dict]]:
    """Return runner -> registered Production features, never fill missing facts.

    Trust in the signed SOURCE envelope is established by the external caller,
    not this function. Here we independently enforce race/date/cutoff and
    source-rule identity to prevent post-result or unregistered-score injection.
    """
    if source.get("family_id") != "JRA":
        return {}
    sha = str(source.get("source_snapshot_sha256") or "")
    freeze = _datetime(source.get("source_freeze_at"))
    cutoff = _datetime(source.get("prediction_cutoff"))
    race_day = _date((source.get("source_race_context") or {}).get("race_date"))
    if not (sha and freeze and cutoff and freeze <= cutoff and race_day):
        return {}
    registered = registry.get("feature_rules") or {}
    if any(rule not in registered.get(name, []) for name, rule in RULES.items()):
        raise ValueError("JRA_OFFICIAL_PRODUCTION_EVALUATOR_RULE_NOT_REGISTERED")
    official = _rows(source.get("jra_official_runner_universe") or {})
    if len(official) < 2:
        return {}
    detail = _rows(source.get("jra_official_race_card_detail") or {})
    history = _rows(source.get("jra_official_horse_history") or {})
    persons = _rows(source.get("jra_official_person_stats") or {})
    ctx = source.get("jra_race_context") or {}
    environment = ((source.get("jra_official_race_card_detail") or {}).get("race_environment") or {})
    venue = str(ctx.get("venue_name") or "")
    surface = str(ctx.get("surface") or "")
    distance = ctx.get("distance_m")
    going = str(ctx.get("going") or ctx.get("track_condition") or "")
    if not going and environment.get("going_surface") in (None, "", surface):
        going = str(environment.get("going") or "")
    out = {}
    for rid in official:
        d = detail.get(rid) or {}
        runs = _observed_runs(history.get(rid) or {}, d, race_day)
        features = {}

        def observed(name: str, selected: list[dict], *, normalized: bool = False):
            if len(selected) < 2:
                return
            values = [(x["field_size"]-x["finish"])/(x["field_size"]-1)
                      for x in selected] if normalized else [float(x["finish"] <= 3) for x in selected]
            rate = sum(values)/len(values)
            if not math.isfinite(rate) or not 0 <= rate <= 1:
                return
            features[name] = {
                "category": percentile_band(rate) if normalized else rate_band(rate),
                "rule_id": RULES[name],
                "evidence_refs": [sha] + [
                    f"JRA_OFFICIAL_HISTORY:{rid}:{x['date']}:{x['finish']}:{x['field_size']}"
                    for x in selected
                ],
                "source_fact": f"{name}: observed_count={len(selected)}; ratio={rate:.6f}; pre_race_only",
                "source_authority": "JRA_OFFICIAL",
                "result_derived": False,
                "production_authority": True,
                "observation_count": len(selected),
            }

        observed("recent_performance", runs[:4], normalized=True)
        observed("recent_consistency", runs[:4])
        if venue:
            observed("same_course_fit", [x for x in runs if str(x.get("venue") or "") == venue])
        if distance is not None:
            observed("same_distance_fit", [x for x in runs if str(x.get("distance_m")) == str(distance)])
        if surface:
            observed("surface_fit", [x for x in runs if str(x.get("surface") or "") == surface])
        if going and surface:
            observed("going_fit", [x for x in runs if str(x.get("going") or "") == going and str(x.get("surface") or "") == surface])
        if venue and distance is not None and surface:
            observed("same_course_distance_quality", [
                x for x in runs if str(x.get("venue") or "") == venue and
                str(x.get("distance_m")) == str(distance) and
                str(x.get("surface") or "") == surface
            ])
        p = persons.get(rid) or {}
        for who, feature in (("jockey", "jockey_quality"), ("trainer", "trainer_quality")):
            if p.get(who + "_matched") is not True:
                continue
            stats = (p.get(who) or {}).get("current_year_flat") or {}
            try:
                starts, raw = int(stats["starts"]), float(stats["win_rate"])
            except (KeyError, TypeError, ValueError):
                continue
            if starts < 30 or not math.isfinite(raw) or raw < 0 or raw == 1.0:
                continue
            rate = raw/100.0 if raw > 1.0 else raw
            if not 0 <= rate <= 1:
                continue
            features[feature] = {
                "category": rate_band(rate),
                "rule_id": RULES[feature],
                "evidence_refs": [sha, f"JRA_OFFICIAL_PERSON_STATS:{rid}:{who}"],
                "source_fact": f"Official {who} matched; starts={starts}; raw_win_rate={raw}; ratio={rate:.6f}",
                "source_authority": "JRA_OFFICIAL",
                "result_derived": False,
                "production_authority": True,
                "observation_count": starts,
            }
        out[rid] = features
    return out
