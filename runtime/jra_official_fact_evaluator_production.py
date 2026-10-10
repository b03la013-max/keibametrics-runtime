"""JRA official-source observed-feature evaluators for Production numerical mapping.

Only already-registered rules and genuinely observed *pre-race* facts can
create index inputs. Absent races, population stats, pedigree outcomes or
unmatched identities are not treated as neutral observations.
"""
from __future__ import annotations

import json
import math
import re
from statistics import median
from datetime import date, datetime
from pathlib import Path
from typing import Any

from jra_evidence_feature_normalizer_production import percentile_band, rate_band, bodyweight_delta_band

PROFILE = "JRA-OFFICIAL-OBSERVED-FEATURE-PRODUCTION-IMPLEMENTATION-20261010"
RULES = {
    "recent_performance": "JRA-EVIDENCE-PERCENTILE-RECENT-PERFORMANCE-v1",
    "recent_speed": "JRA-EVIDENCE-PERCENTILE-RECENT-SPEED-v1",
    "recent_consistency": "JRA-RECENT-CONSISTENCY-RATE-v1",
    "same_course_fit": "KM-JRA-SAME-COURSE-FIT-v1",
    "same_distance_fit": "KM-JRA-SAME-DISTANCE-FIT-v1",
    "surface_fit": "KM-JRA-SURFACE-FIT-v1",
    "going_fit": "KM-JRA-GOING-FIT-v1",
    "same_course_distance_quality": "KM-JRA-SAME-COURSE-DISTANCE-QUALITY-v1",
    "jockey_quality": "KM-JRA-JOCKEY-QUALITY-v1",
    "trainer_quality": "KM-JRA-TRAINER-QUALITY-v1",
    "rotation_fit": "KM-JRA-ROTATION-FIT-v1",
    "bodyweight_range_fit": "KM-JRA-BODYWEIGHT-RANGE-FIT-v1",
    "class_performance": "KM-JRA-CLASS-PERFORMANCE-v1",
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


def _jra_official_class_strength(name: str) -> float | None:
    """Known printed JRA class labels only. Never infer from a horse name."""
    t = str(name or "").upper().replace(" ", "").replace("　", "")
    if not t:
        return None
    # Normalize full-width grade tokens and unicode Roman numerals before
    # checking a grade token. Japanese characters before G are NOT a
    # Unicode word boundary, so \\bG... would incorrectly miss all JRA
    # Japanese race names such as 神戸新聞杯GⅡ.
    t=(t.replace("Ｇ","G").replace("Ⅲ","III")
         .replace("Ⅱ","II").replace("Ⅰ","I")
         .replace("３","3").replace("２","2").replace("１","1"))
    for pattern,value in (
        (r"(?<![A-Z])(?:GIII|G3|JPNIII|JPN3)(?![A-Z0-9])",88.0),
        (r"(?<![A-Z])(?:GII|G2|JPNII|JPN2)(?![A-Z0-9])",92.0),
        (r"(?<![A-Z])(?:GI|G1|JPNI|JPN1)(?![A-Z0-9])",96.0),
    ):
        if re.search(pattern,t): return value
    if "リステッド" in t or re.search(r"\\(L\\)$", t):
        return 84.0
    if any(x in t for x in ("オープン", "OPEN")):
        return 82.0
    if "3勝クラス" in t or "３勝クラス" in t: return 78.0
    if "2勝クラス" in t or "２勝クラス" in t: return 74.0
    if "1勝クラス" in t or "１勝クラス" in t: return 70.0
    if "未勝利" in t: return 54.0
    if "新馬" in t: return 52.0
    return None


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
    # Real JRA horse-history Rt measures can support a peer-relative speed
    # category. Each runner needs 2 earlier ratings and the active race needs
    # at least 4 independently rated runners; no cross-date leakage or
    # fallback zero ratings. Keep this normalizer under the registered v1 rule.
    histories = {rid: _observed_runs(history.get(rid) or {}, detail.get(rid) or {}, race_day)
                 for rid in official}
    speed_means = {}
    for rid, rows in histories.items():
        scores = []
        for row in rows[:4]:
            rating = row.get("rating")
            if isinstance(rating, bool) or not isinstance(rating, (int, float)):
                continue
            rating = float(rating)
            if math.isfinite(rating) and 1 <= rating <= 150:
                scores.append(rating)
        if len(scores) >= 2:
            speed_means[rid] = sum(scores) / len(scores)
    out = {}
    for rid in official:
        d = detail.get(rid) or {}
        runs = histories[rid]
        features = {}
        if len(speed_means) >= 4 and rid in speed_means:
            value = speed_means[rid]
            less = sum(v < value for v in speed_means.values())
            tied = sum(v == value for v in speed_means.values())
            percentile = (less + (tied - 1) / 2) / (len(speed_means) - 1)
            references = [
                f"JRA_OFFICIAL_HISTORY_RT:{rid}:{r['date']}:{r.get('rating')}"
                for r in runs[:4] if isinstance(r.get("rating"), (float, int))
                and not isinstance(r.get("rating"), bool)
                and math.isfinite(float(r["rating"])) and 1 <= float(r["rating"]) <= 150
            ]
            features["recent_speed"] = {
                "category": percentile_band(percentile),
                "rule_id": RULES["recent_speed"],
                "evidence_refs": [sha] + references,
                "source_fact": (
                    f"Pre-race JRA history Rt mean={value:.6f};"
                    f" peer_percentile={percentile:.6f}; rated_peers={len(speed_means)};"
                    f" prior_race_rating_observations={len(references)}"
                ),
                "source_authority": "JRA_OFFICIAL",
                "result_derived": False,
                "production_authority": True,
                "observation_count": len(references),
            }

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

        # Consecutive-race timing is a directly observed pre-race fact.
        # Use the existing registered rotation rule and already existing
        # candidate timing bands; leave debutants and malformed dates missing.
        if runs:
            latest = _date(runs[0]["date"])
            days = (race_day - latest).days if latest else None
            if days is not None and days > 0:
                if 14 <= days <= 42:
                    cat = "STRONG"
                elif 8 <= days <= 70:
                    cat = "POSITIVE"
                elif 71 <= days <= 120:
                    cat = "NEUTRAL"
                elif days < 8:
                    cat = "CAUTION"
                else:
                    cat = "MIXED"
                features["rotation_fit"] = {
                    "category": cat,
                    "rule_id": RULES["rotation_fit"],
                    "evidence_refs": [sha, f"JRA_OFFICIAL_HISTORY:{rid}:{latest}"],
                    "source_fact": f"Last verified prior start {latest}; days_to_target_race={days}; course conditions not assumed",
                    "source_authority": "JRA_OFFICIAL",
                    "result_derived": False,
                    "production_authority": True,
                    "observation_count": 1,
                }

        # Existing, registered delta-band normalizer applied to the distance
        # from the horse's real prior bodyweight median. Distinct from the
        # official same-day bodyweight-change feature; never use imaginary
        # 'ideal weight', and require >=2 independent past observations.
        current = d.get("current_body_weight")
        if type(current) is int and 300 <= current <= 700:
            historical = [
                (int(x["body_weight"]), str(x["date"]))
                for x in runs[:6] if type(x.get("body_weight")) is int
                and 300 <= x["body_weight"] <= 700
            ]
            if len(historical) >= 2:
                baseline = float(median(v for v, _ in historical))
                features["bodyweight_range_fit"] = {
                    "category": bodyweight_delta_band(current-baseline),
                    "rule_id": RULES["bodyweight_range_fit"],
                    "evidence_refs": [sha] + [
                        f"JRA_OFFICIAL_BODYWEIGHT:{rid}:{day}:{weight}"
                        for weight, day in historical
                    ],
                    "source_fact": (
                        f"Official current bodyweight={current} kg; prior "
                        f"median={baseline:.1f} kg; signed_delta={current-baseline:+.1f} kg;"
                        f" prior_observations={len(historical)}"
                    ),
                    "source_authority": "JRA_OFFICIAL",
                    "result_derived": False,
                    "production_authority": True,
                    "observation_count": len(historical),
                }

        # Class-adjusted performance is derived only from the race class
        # printed in JRA's historical result and that race's verified field/
        # finish, never the future/current target's class. These levels are
        # inherited from the already existing candidate JRA class ladder.
        class_records=[]
        for x in runs[:4]:
            cls=_jra_official_class_strength(x.get("race_name") or x.get("race_class_text"))
            if cls is None:
                continue
            finishing=(x["field_size"]-x["finish"])/(x["field_size"]-1)
            class_records.append((x,cls,finishing))
        if len(class_records)>=2:
            # An explicit quality/class mixture: 55% level reached, 45%
            # normalized finish within the class. Observed-only, not P(win).
            values=[0.55*cls + 45.0*finish for _,cls,finish in class_records]
            value=sum(values)/len(values)
            features["class_performance"]={
                "category": percentile_band(value/100.0),
                "rule_id":RULES["class_performance"],
                "evidence_refs":[sha]+[
                    f"JRA_OFFICIAL_HISTORY_CLASS:{rid}:{row['date']}:{row.get('race_name')}:{row['finish']}/{row['field_size']}"
                    for row,_,_ in class_records
                ],
                "source_fact": (
                    f"Real prior JRA class-adjusted finish observations={len(values)};"
                    f" class_level_weight=0.55; field_finish_weight=0.45;"
                    f" score={value:.6f}; target result excluded"
                ),
                "source_authority":"JRA_OFFICIAL",
                "result_derived":False,
                "production_authority":True,
                "observation_count":len(values),
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
            if starts < 30 or not math.isfinite(raw) or not 0 <= raw <= 100:
                continue
            # Official JRA "勝率" uses a fractional 0..1 ratio (e.g. 0.044
            # for 4.4%), not 4.4 percent; published figures round to 3
            # decimal places. Other explicit percent-style imports may be
            # accepted ONLY when integer wins/starts independently agree.
            wins = stats.get("wins")
            if wins is None:
                if raw > 1.0:
                    continue
                rate = raw
            else:
                if type(wins) is not int or wins < 0 or wins > starts:
                    continue
                rate = wins / starts
                displayed = raw if raw <= 1.0 else raw / 100.0
                tolerance = 0.0015 if raw <= 1.0 else 0.0055
                if abs(rate - displayed) > tolerance:
                    continue
            if not 0 <= rate <= 1:
                continue
            features[feature] = {
                "category": rate_band(rate),
                "rule_id": RULES[feature],
                "evidence_refs": [sha, f"JRA_OFFICIAL_PERSON_STATS:{rid}:{who}"],
                "source_fact": f"Official {who} matched; starts={starts}; wins={wins}; displayed_win_rate={raw}; ratio={rate:.6f}",
                "source_authority": "JRA_OFFICIAL",
                "result_derived": False,
                "production_authority": True,
                "observation_count": starts,
            }
        out[rid] = features
    return out
