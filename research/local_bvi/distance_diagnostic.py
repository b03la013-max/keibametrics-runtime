"""Estimate a sire's distance effect within comparable LOCAL flat races.

This diagnostic never alters the AEI baseline, ranking, canonical BVIg-L,
or ticket inputs. Both arms use the same venue, surface, going, race kind
and published conditions. Published conditions are not a full class canon.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import timedelta, timezone
from math import sqrt
from statistics import fmean

from runtime.local_bvi_bloodline_research import _name, _timestamp


JST = timezone(timedelta(hours=9))
MIN_RACES_PER_ARM = 30
MIN_DATES_PER_ARM = 8


def _context(race):
    return tuple(_name(race.get(field)) for field in
                 ("venue", "surface", "going", "race_kind", "conditions"))


def _past_observation(race, cutoff):
    observed = _timestamp(race.get("observed_at"))
    return (observed is not None and observed <= cutoff
            and race["race_date"] < cutoff.astimezone(JST).date().isoformat())


def _race_residuals(races, cutoff):
    """Return one observation per sire per race with a verified result marker."""
    strata = defaultdict(list)
    seen = set()
    for race in races:
        context = _context(race)
        if (not all(context) or race["venue"].startswith("帯広")
                or race.get("surface") not in {"DIRT", "TURF"}
                or not race.get("distance") or not race.get("has_payback")
                or not _past_observation(race, cutoff)):
            continue
        key = (race["venue"], race["race_date"], race["race_no"])
        if key in seen:
            raise ValueError("DUPLICATE_DISTANCE_RESEARCH_RACE")
        seen.add(key)
        # The endpoint is place among numeric finishers. Cancellations, DNF,
        # disqualifications and ambiguous blank placings are outside it.
        ranked = [r for r in race["runners"] if type(r.get("finish")) is int and r["finish"] > 0]
        if len(ranked) < 4 or not any(r["finish"] == 1 for r in ranked):
            continue
        base = fmean(r["finish"] <= 3 for r in ranked)
        values = defaultdict(list)
        for runner in ranked:
            sire = _name(runner.get("sire"))
            if sire:
                values[sire].append((runner["finish"] <= 3) - base)
        for sire, residuals in values.items():
            strata[context, sire].append((race["distance"], race["race_date"], fmean(residuals)))
    return strata


def _difference(same, other):
    return fmean(value for _, value in same) - fmean(value for _, value in other)


def _estimate(observations, distance):
    same = [(day, score) for d, day, score in observations if d == distance]
    other = [(day, score) for d, day, score in observations if d != distance]
    same_days = {day for day, _ in same}
    other_days = {day for day, _ in other}
    result = {"same_distance_races": len(same), "other_distance_races": len(other),
              "same_distance_days": len(same_days), "other_distance_days": len(other_days),
              "effect_pp": None, "approximate_95_interval_pp": None,
              "status": "INSUFFICIENT_COMPARABLE_RACES"}
    if min(len(same), len(other)) < MIN_RACES_PER_ARM or min(len(same_days), len(other_days)) < MIN_DATES_PER_ARM:
        return result
    estimate = _difference(same, other)
    # Leaving out one meeting date at a time captures common race-day variation.
    # This is a descriptive interval; it does not adjust for repeated horses,
    # unrecorded class or persistent differences in the choice of distance.
    dates = same_days | other_days
    estimates = [_difference([(day, v) for day, v in same if day != removed],
                             [(day, v) for day, v in other if day != removed])
                 for removed in sorted(dates)]
    center = fmean(estimates)
    se = sqrt((len(dates) - 1) / len(dates) * sum((value - center) ** 2 for value in estimates))
    result.update(status="UNCALIBRATED_DISTANCE_EFFECT", effect_pp=round(100 * estimate, 4),
                  approximate_95_interval_pp=[round(100 * (estimate + sign * 1.96 * se), 4) for sign in (-1, 1)])
    return result


def evaluate_distance(races, target_races, *, as_of):
    """Return optional research estimates for the declared sires of each target.

    Callers supply a point-in-time cohort from a comparable period in the private corpus. Historical
    results observed after ``as_of`` contribute no records. Targets must be
    observed by that instant, with a scheduled start still in the future.
    """
    cutoff = _timestamp(as_of)
    if cutoff is None:
        raise ValueError("DISTANCE_RESEARCH_AS_OF_REQUIRED")
    strata = _race_residuals(races, cutoff)
    for target in target_races:
        observed = _timestamp(target.get("observed_at"))
        start = _timestamp(target.get("scheduled_at"))
        if (observed is None or start is None or not observed <= cutoff < start
                or target["race_date"] != start.astimezone(JST).date().isoformat()
                or target.get("has_payback") or any(r.get("finish") is not None for r in target["runners"])):
            raise ValueError("DISTANCE_RESEARCH_PRESTART_TARGET_REQUIRED")
        context = _context(target)
        estimates = {}
        for runner in target["runners"]:
            sire = _name(runner.get("sire"))
            if not sire or sire in estimates or runner.get("finish_status") in {"CANCELLED", "EXCLUDED"}:
                continue
            estimates[sire] = _estimate(strata.get((context, sire), ()), target.get("distance"))
        yield {"venue": target["venue"], "race_date": target["race_date"], "race_no": target["race_no"],
               "record_scope": "LOCAL_DISTANCE_DIAGNOSTIC", "as_of": as_of,
               "prediction_authority": False, "formal_bvi": 52, "sires": estimates}
