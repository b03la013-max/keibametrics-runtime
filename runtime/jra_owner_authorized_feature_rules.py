"""Owner-authorized observed-feature rules for JRA Production numerics.

New deterministic rules authorized by the KeibaMetrics owner on 2026-10-10 to
close Production Base13 coverage from JRA OFFICIAL facts already captured in
the signed SOURCE (race-card recent runs: corner calls, final 3F, margin,
class; full official horse history; official person stats; same-day official
results; registered workout assessment; point-in-time pedigree corpus).

Boundaries kept:
- Only pre-race facts: runs strictly before the race day, same-day results
  only from earlier races, SOURCE freeze <= prediction cutoff.
- Coverage thresholds, index weights and formulas are unchanged.
- A feature is emitted only when its minimum sample is met; otherwise it stays
  MISSING (no neutral fill for unknowns). An observed condition (e.g. a first
  jockey pairing) may map to a category only where the rule says so.
- Every feature is labelled OWNER-AUTHORIZED / UNVALIDATED so it can be
  measured and revised; none claims calibrated predictive validity.
"""
from __future__ import annotations

from datetime import date, datetime
import math
import re
from statistics import mean, pstdev
from typing import Any

from jra_evidence_feature_normalizer_production import comment_band, percentile_band, rate_band

PROFILE = "KM-JRA-OWNER-AUTHORIZED-OBSERVED-FEATURE-RULES-v1.1-20261010"
RULE_AUTHORITY = "OWNER-AUTHORIZED-NEW-RULE-20261010 / UNVALIDATED"

RULES = {
    "recent_speed": "KM-JRA-OA-RECENT-SPEED-MARGIN-v1",
    "finish_margin": "KM-JRA-OA-FINISH-MARGIN-BEST-v1",
    "speed_reliability": "KM-JRA-OA-SPEED-RELIABILITY-v1",
    "closing_quality": "KM-JRA-OA-CLOSING-GAIN-v1",
    "position_quality": "KM-JRA-OA-EARLY-POSITION-v1",
    "dash_quality": "KM-JRA-OA-DASH-FRONT-RATE-v1",
    "gate_quality": "KM-JRA-OA-START-NOT-BEHIND-RATE-v1",
    "position_reproducibility": "KM-JRA-OA-POSITION-REPRODUCIBILITY-v1",
    "pace_resilience": "KM-JRA-OA-PACE-RESILIENCE-v1",
    "pressure_resilience": "KM-JRA-OA-PRESSURE-RESILIENCE-v1",
    "progression_ability": "KM-JRA-OA-PROGRESSION-v1",
    "class_performance": "KM-JRA-OA-CLASS-PERFORMANCE-v1",
    "official_recent_quality": "KM-JRA-OA-OFFICIAL-RECENT-QUALITY-v1",
    "rotation_fit": "KM-JRA-OA-ROTATION-INTERVAL-v1",
    "layoff_readiness": "KM-JRA-OA-LAYOFF-READINESS-v1",
    "preparation_continuity": "KM-JRA-OA-PREPARATION-CONTINUITY-v1",
    "physical_readiness": "KM-JRA-OA-PHYSICAL-READINESS-BW-v1",
    "bodyweight_range_fit": "KM-JRA-OA-BODYWEIGHT-RANGE-v1",
    "bodyweight_history_quality": "KM-JRA-OA-BODYWEIGHT-HISTORY-STABILITY-v1",
    "weight_load_fit": "KM-JRA-OA-WEIGHT-LOAD-RELATIVE-v1",
    "turn_direction_fit": "KM-JRA-OA-TURN-DIRECTION-FIT-v1",
    "similar_geometry_fit": "KM-JRA-OA-SIMILAR-GEOMETRY-FIT-v1",
    "going_fit": "KM-JRA-OA-GOING-FIT-SAMEDAY-v1",
    "same_day_track_fit": "KM-JRA-OA-SAMEDAY-STYLE-FIT-v1",
    "track_bias_fit": "KM-JRA-OA-SAMEDAY-DRAW-BIAS-v1",
    "draw_course_fit": "KM-JRA-OA-SAMEDAY-DRAW-BIAS-v1",
    "jockey_horse_fit": "KM-JRA-OA-JOCKEY-HORSE-PAIRING-v1",
    "stable_trainer_class": "KM-JRA-OA-TRAINER-CAREER-CLASS-v1",
    "target_intent": "KM-JRA-OA-TARGET-INTENT-CONTINUITY-v1",
    "market_stability": "KM-JRA-OA-MARKET-STABILITY-CROSS-RACE-v1",
    "market_mismatch": "KM-JRA-OA-MARKET-FORM-MISMATCH-v1",
    "training_comments_quality": "KM-JRA-OA-TRAINING-COMMENT-v1",
    "workout_finish": "KM-JRA-OA-WORKOUT-FINAL-RATING-v1",
    "same_course_distance_quality": "KM-JRA-OA-COURSE-DISTANCE-EXPERIENCE-v1",
    "distance_fit": "KM-JRA-OA-DISTANCE-FIT-v1",
    "pedigree_surface": "KM-JRA-OA-PEDIGREE-SIRE-SURFACE-v1",
    "pedigree_distance": "KM-JRA-OA-PEDIGREE-SIRE-DISTANCE-v1",
    "pedigree_class": "KM-JRA-OA-PEDIGREE-SIRE-CLASS-v1",
    "maternal_class_signal": "KM-JRA-OA-PEDIGREE-DAMSIRE-SURFACE-v1",
    "sire_track_signal": "KM-JRA-OA-PEDIGREE-SIRE-TRACK-v1",
    "sprint_pedigree": "KM-JRA-OA-PEDIGREE-SIRE-SPRINT-v1",
    "sire_newcomer_signal": "KM-JRA-OA-PEDIGREE-SIRE-DEBUT-v1",
    # v1.1 additions (owner-authorized 2026-10-10 22:30 JST, UNVALIDATED)
    "opponent_strength": "KM-JRA-OA-OPPONENT-CLASS-FACED-v1",
    "hidden_class": "KM-JRA-OA-HIDDEN-CLASS-PEAK-v1",
    "course_geometry_fit": "KM-JRA-OA-COURSE-GEOMETRY-SURFACE-FIT-v1",
    "physical_pedigree_fit": "KM-JRA-OA-PEDIGREE-PHYSICAL-FIT-v1",
}

# Alternative rule ids for a feature, used only when the primary rule's sample
# is unmet. Each is a distinct, registered rule with its own sample minimum.
FALLBACK_RULES = {
    "pedigree_distance": "KM-JRA-OA-PEDIGREE-DAMSIRE-DISTANCE-FALLBACK-v1",
    "pedigree_class": "KM-JRA-OA-PEDIGREE-DAMSIRE-CLASS-FALLBACK-v1",
    "physical_pedigree_fit": "KM-JRA-OA-PEDIGREE-PHYSICAL-FIT-DAMSIRE-FALLBACK-v1",
}

LEFT_TURN = {"東京", "中京", "新潟"}
GEOMETRY = {"東京": "LONG_LEFT", "新潟": "LONG_LEFT", "中京": "LEFT",
            "京都": "BIG_RIGHT", "阪神": "BIG_RIGHT",
            "中山": "SMALL_RIGHT", "福島": "SMALL_RIGHT", "小倉": "SMALL_RIGHT",
            "札幌": "SMALL_RIGHT", "函館": "SMALL_RIGHT"}
LADDER = ["VERY_WEAK", "WEAK", "CAUTION", "MIXED", "NEUTRAL", "POSITIVE", "STRONG", "VERY_STRONG", "EXCEPTIONAL"]


# ----------------------------------------------------------------- helpers
def _date(v):
    try:
        return date.fromisoformat(str(v))
    except (TypeError, ValueError):
        return None


def _dt(v):
    try:
        d = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        return d if d.tzinfo else None
    except (TypeError, ValueError):
        return None


def _surface(v):
    s = str(v or "")
    return "ダ" if s.startswith("ダ") else "芝" if s.startswith("芝") else "障" if s.startswith("障") else s


def _name(v):
    return re.sub(r"[\s▲△◇☆★]+", "", str(v or ""))


def class_rank(text: Any) -> int | None:
    t = str(text or "").replace("Ｇ", "G").replace("Ⅰ", "1").replace("Ⅱ", "2").replace("Ⅲ", "3")
    if re.search(r"G1|JpnI(?!I)", t):
        return 7
    if re.search(r"G2", t):
        return 6
    if re.search(r"G3", t):
        return 5
    if re.search(r"オープン|OP|\(L\)|（L）|リステッド", t):
        return 4
    if "3勝" in t or "1600万" in t:
        return 3
    if "2勝" in t or "1000万" in t:
        return 2
    if "1勝" in t or "500万" in t:
        return 1
    if "未勝利" in t or "新馬" in t:
        return 0
    return None


def decode_passing_positions(digits: str, field_size: Any) -> list[int] | None:
    s = str(digits or "")
    try:
        n = int(field_size)
    except (TypeError, ValueError):
        return None
    if not s.isdigit() or n < 1:
        return None
    found = []

    def walk(i, acc):
        if len(acc) > 4:
            return
        if i == len(s):
            if acc:
                found.append(list(acc))
            return
        for w in (1, 2):
            part = s[i:i + w]
            if len(part) < w or part.startswith("0"):
                continue
            v = int(part)
            if 1 <= v <= n:
                acc.append(v)
                walk(i + w, acc)
                acc.pop()
    walk(0, [])
    if not found:
        return None
    multi = [c for c in found if len(c) >= 2]
    found = multi or found
    low = min(sum(abs(a - b) for a, b in zip(c, c[1:])) for c in found)
    win = [c for c in found if sum(abs(a - b) for a, b in zip(c, c[1:])) == low]
    if len({(c[0], c[-1]) for c in win}) != 1:
        return None
    return min(win, key=len)


def _nf(r):
    return (r["field_size"] - r["finish"]) / (r["field_size"] - 1)


def _thr(x, table, default):
    for limit, cat in table:
        if x >= limit:
            return cat
    return default


def _margin_band(sec):
    for limit, cat in ((0.2, "VERY_STRONG"), (0.4, "STRONG"), (0.7, "POSITIVE"), (1.0, "NEUTRAL"),
                       (1.5, "MIXED"), (2.0, "CAUTION"), (3.0, "WEAK")):
        if sec <= limit:
            return cat
    return "VERY_WEAK"


def _share_band(x):
    return _thr(x, ((0.75, "VERY_STRONG"), (0.5, "STRONG"), (0.34, "POSITIVE"),
                    (0.25, "NEUTRAL"), (1e-9, "MIXED")), "CAUTION")


def _ped_band(m):
    return _thr(m, ((0.64, "VERY_STRONG"), (0.58, "STRONG"), (0.54, "POSITIVE"), (0.46, "NEUTRAL"),
                    (0.42, "MIXED"), (0.36, "CAUTION")), "WEAK")


def _shift(cat, steps):
    i = LADDER.index(cat)
    return LADDER[max(0, min(len(LADDER) - 1, i + steps))]


def _rows(obj):
    if isinstance(obj, dict):
        obj = obj.get("runners", obj)
    if isinstance(obj, dict):
        return {str(k): v for k, v in obj.items() if isinstance(v, dict)}
    if isinstance(obj, list):
        return {str(r.get("runner_id") or r.get("horse_no")): r for r in obj
                if isinstance(r, dict) and (r.get("runner_id") or r.get("horse_no")) is not None}
    return {}


def _valid_run(x, day):
    d = _date(x.get("date"))
    try:
        fin, field = int(x["finish"]), int(x["field_size"])
    except (KeyError, TypeError, ValueError):
        return None
    if d is None or d >= day or field < 2 or not 1 <= fin <= field:
        return None
    return {**x, "finish": fin, "field_size": field, "date": str(d), "surface": _surface(x.get("surface"))}


# ------------------------------------------------------------ main entry
def owner_authorized_observations(source: dict, registry: dict, *, corpus: dict | None = None) -> dict[str, dict]:
    """Return runner -> owner-authorized features. Never fills an unmet sample."""
    if source.get("family_id") != "JRA":
        return {}
    sha = str(source.get("source_snapshot_sha256") or "")
    freeze, cutoff = _dt(source.get("source_freeze_at")), _dt(source.get("prediction_cutoff"))
    ctx = source.get("jra_race_context") or {}
    day = _date((source.get("source_race_context") or {}).get("race_date") or ctx.get("race_date"))
    if not (sha and freeze and cutoff and freeze <= cutoff and day):
        return {}
    registered = registry.get("feature_rules") or {}
    missing = [f for f, rule in list(RULES.items()) + list(FALLBACK_RULES.items())
               if rule not in registered.get(f, [])]
    if missing:
        raise ValueError("JRA_OWNER_AUTHORIZED_RULE_NOT_REGISTERED:" + ",".join(sorted(missing)))
    official = _rows(source.get("jra_official_runner_universe") or {})
    if len(official) < 2:
        return {}
    detail = _rows(source.get("jra_official_race_card_detail") or {})
    history = _rows(source.get("jra_official_horse_history") or {})
    persons = _rows(source.get("jra_official_person_stats") or {})
    workout = {str(x.get("runner_id") or x.get("horse_no")): x
               for x in ((source.get("jra_registered_common") or {}).get("workout") or {}).get("runners") or []
               if isinstance(x, dict)}
    venue = str(ctx.get("venue_name") or "")
    surface = _surface(ctx.get("surface"))
    distance = ctx.get("distance_m")
    cur_class = class_rank(ctx.get("race_class"))
    try:
        race_no = int(ctx.get("race_no") or (source.get("source_race_context") or {}).get("race_no"))
    except (TypeError, ValueError):
        race_no = None
    active = [rid for rid, r in official.items() if str(r.get("status") or "ACTIVE") == "ACTIVE"]

    # ---- same-day official results (strictly earlier races, same surface)
    same_day = []
    raw_races = (source.get("jra_official_same_day_results") or {}).get("races") or []
    if isinstance(raw_races, dict):
        raw_races = list(raw_races.values())
    for race in raw_races:
        if not isinstance(race, dict):
            continue
        try:
            no = int(race.get("race_no"))
        except (TypeError, ValueError):
            continue
        env = race.get("race_environment") or {}
        if race_no is None or no >= race_no or _surface(env.get("surface")) != surface:
            continue
        same_day.append(race)
    same_day.sort(key=lambda r: int(r["race_no"]))
    today_going = None
    for race in same_day:
        g = (race.get("race_environment") or {}).get("going")
        if g:
            today_going = str(g)
    env_now = (source.get("jra_official_race_card_detail") or {}).get("race_environment") or {}
    if env_now.get("going") and _surface(env_now.get("going_surface")) == surface:
        today_going = str(env_now["going"])
    top3_front, top3_inner, sd_refs = [], [], []
    for race in same_day:
        runners = [r for r in race.get("runners") or [] if isinstance(r, dict)]
        n = int(race.get("runner_count") or len(runners) or 0)
        if n < 4:
            continue
        sd_refs.append(f"JRA_OFFICIAL_SAME_DAY:R{race['race_no']}")
        for r in runners:
            try:
                fin = int(r.get("finish"))
            except (TypeError, ValueError):
                continue
            if not 1 <= fin <= 3:
                continue
            calls = r.get("passing_positions") or []
            if calls:
                top3_front.append((calls[0] - 1) / max(1, n - 1) <= 0.33)
            try:
                top3_inner.append(int(r.get("horse_no")) <= n / 2)
            except (TypeError, ValueError):
                pass

    # ---- field-level form ranks for market mismatch
    def form_score(rid):
        runs = [z for z in (_valid_run(x, day) for x in ((history.get(rid) or {}).get("runs")
                                                         or (detail.get(rid) or {}).get("recent_runs") or [])) if z]
        runs.sort(key=lambda r: r["date"], reverse=True)
        return mean(_nf(r) for r in runs[:4]) if runs else None
    form = {rid: form_score(rid) for rid in active}
    formed = sorted([rid for rid in active if form[rid] is not None], key=lambda r: -form[r])
    weights = []
    for rid in active:
        try:
            weights.append(float(official[rid].get("assigned_weight")))
        except (TypeError, ValueError):
            weights = []
            break

    out: dict[str, dict] = {}
    for rid in official:
        d = detail.get(rid) or {}
        feats: dict[str, dict] = {}

        def put(name, category, refs, fact, n, authority="JRA_OFFICIAL", rule=None):
            feats[name] = {
                "category": category, "rule_id": rule or RULES[name],
                "evidence_refs": [sha] + list(refs),
                "source_fact": f"{name}: {fact}; pre_race_only; {RULE_AUTHORITY}",
                "source_authority": authority, "result_derived": False,
                "production_authority": True, "observation_count": n,
                "rule_authority": RULE_AUTHORITY,
            }

        hist_runs = [z for z in (_valid_run(x, day) for x in ((history.get(rid) or {}).get("runs") or [])) if z]
        recent = []
        for x in d.get("recent_runs") or []:
            z = _valid_run(x, day)
            if not z:
                continue
            if z.get("passing_positions_parser") and z.get("passing_positions"):
                calls = [int(v) for v in z["passing_positions"]]
            else:
                # SOURCEs captured before the v2 parser split every digit;
                # re-decode the preserved digit string instead.
                calls = decode_passing_positions(z.get("passing_positions_raw"), z["field_size"]) \
                    if z.get("passing_positions_raw") else None
            z["calls"] = calls
            if not z.get("jockey"):
                m = re.search(r"番人気\s+(.+?)\s+\d{2}(?:\.\d+)?\s*kg", str(z.get("raw") or ""))
                z["jockey"] = m.group(1).strip() if m else None
            recent.append(z)
        recent.sort(key=lambda r: r["date"], reverse=True)
        recent = recent[:4]
        runs = hist_runs or list(recent)
        runs.sort(key=lambda r: r["date"], reverse=True)
        # Race-card recent runs carry the official class text that the horse
        # history table omits for named races; bind it by run date.
        class_by_date = {r["date"]: r.get("race_class_text") for r in recent if r.get("race_class_text")}
        for r in runs:
            if class_rank(r.get("race_name")) is None and class_by_date.get(r["date"]):
                r["race_name"] = str(r.get("race_name") or "") + " " + str(class_by_date[r["date"]])
        try:
            career = int(((d.get("career_record") or {}).get("starts")))
        except (TypeError, ValueError):
            career = len(runs)
        k = 1 if career <= 3 else 2
        rref = [f"JRA_OFFICIAL_RACE_CARD_RECENT:{rid}:{r['date']}" for r in recent]
        href = [f"JRA_OFFICIAL_HISTORY:{rid}:{r['date']}:{r['finish']}:{r['field_size']}" for r in runs[:8]]

        # -- margin / speed (race-card recent runs)
        behind = [0.0 if r["finish"] == 1 else max(0.0, float(r["margin"]))
                  for r in recent if isinstance(r.get("margin"), (int, float))]
        if len(behind) >= k:
            put("recent_speed", _margin_band(mean(behind)), rref,
                f"mean_seconds_behind_winner={mean(behind):.3f}; runs={len(behind)}", len(behind))
            put("finish_margin", _margin_band(min(behind)), rref,
                f"best_seconds_behind_winner={min(behind):.3f}; runs={len(behind)}", len(behind))
        if len(behind) >= 3:
            share = sum(1 for b in behind if b <= 0.5) / len(behind)
            put("speed_reliability", _share_band(share), rref,
                f"share_within_0.5s={share:.3f}; runs={len(behind)}", len(behind))

        # -- corner calls
        with_calls = [r for r in recent if r.get("calls")]
        early = [(r["calls"][0] - 1) / (r["field_size"] - 1) for r in with_calls]
        if len(with_calls) >= k:
            gain = [(r["calls"][-1] - r["finish"]) / r["field_size"] for r in with_calls]
            put("closing_quality", _thr(mean(gain), ((0.25, "VERY_STRONG"), (0.15, "STRONG"), (0.07, "POSITIVE"),
                                                     (-0.02, "NEUTRAL"), (-0.08, "MIXED"), (-0.15, "CAUTION")), "WEAK"),
                rref, f"mean_last_call_to_finish_gain_ratio={mean(gain):.3f}; runs={len(gain)}", len(gain))
            put("position_quality", percentile_band(1 - mean(early)), rref,
                f"mean_early_position_ratio={mean(early):.3f}; runs={len(early)}", len(early))
            front = sum(1 for r in with_calls if r["calls"][0] <= max(2, round(r["field_size"] * 0.25))) / len(with_calls)
            put("dash_quality", _share_band(front), rref, f"front_quarter_first_call_rate={front:.3f}", len(with_calls))
            not_back = sum(1 for e in early if e <= 0.5) / len(early)
            put("gate_quality", _share_band(not_back), rref, f"first_call_not_behind_midfield_rate={not_back:.3f}", len(early))
        if len(with_calls) >= 2:
            sd = pstdev(early)
            put("position_reproducibility", _thr(-sd, ((-0.08, "VERY_STRONG"), (-0.12, "STRONG"), (-0.17, "POSITIVE"),
                                                       (-0.23, "NEUTRAL"), (-0.30, "MIXED")), "CAUTION"),
                rref, f"early_position_ratio_std={sd:.3f}; runs={len(early)}", len(early))
        if len(with_calls) >= k:
            held = [r for r in with_calls if (r["calls"][-1] - 1) / (r["field_size"] - 1) <= 0.5]
            if held:
                put("pace_resilience", percentile_band(mean(_nf(r) for r in held)), rref,
                    f"normalized_finish_when_top_half_at_last_call={mean(_nf(r) for r in held):.3f}; runs={len(held)}", len(held))
        crowded = [r for r in runs if r["field_size"] >= 14]
        if len(crowded) >= k:
            put("pressure_resilience", percentile_band(mean(_nf(r) for r in crowded)), href,
                f"normalized_finish_in_14plus_fields={mean(_nf(r) for r in crowded):.3f}; runs={len(crowded)}", len(crowded))
        if len(runs) >= 3:
            delta = mean(_nf(r) for r in runs[:2]) - mean(_nf(r) for r in runs[2:5])
            put("progression_ability", _thr(delta, ((0.25, "VERY_STRONG"), (0.12, "STRONG"), (0.04, "POSITIVE"),
                                                    (-0.04, "NEUTRAL"), (-0.12, "MIXED")), "CAUTION"),
                href, f"recent2_minus_prior3_normalized_finish={delta:.3f}", len(runs))

        # -- class
        if cur_class is not None and runs:
            ranked = [(class_rank(r.get("race_name") or r.get("race_class_text")), r) for r in runs]
            at = [r for c, r in ranked if c is not None and c >= cur_class]
            below = [r for c, r in ranked if c is not None and c == cur_class - 1]
            if len(at) >= k:
                put("class_performance", percentile_band(mean(_nf(r) for r in at)), href,
                    f"normalized_finish_at_or_above_class={mean(_nf(r) for r in at):.3f}; runs={len(at)}", len(at))
            elif len(below) >= k:
                put("class_performance", _shift(percentile_band(mean(_nf(r) for r in below)), -1), href,
                    f"untested_at_class; one_class_below_normalized_finish={mean(_nf(r) for r in below):.3f}; one_band_discount", len(below))
            # Opposition faced: official class of the last <=6 runs relative to
            # today's class (strength of fields met, independent of finish).
            faced = [c for c, _ in ranked[:6] if c is not None]
            if len(faced) >= k:
                dlt = mean(c - cur_class for c in faced)
                put("opponent_strength", _thr(dlt, ((1.0, "STRONG"), (0.34, "POSITIVE"), (-0.34, "NEUTRAL"),
                                                    (-1.0, "MIXED")), "CAUTION"),
                    href, f"mean_official_class_faced_minus_today={dlt:+.2f}; runs={len(faced)}", len(faced))
            # Hidden class: highest official class at which the horse has
            # already finished top-3 or in the top 30% of the field.
            known = [(c, r) for c, r in ranked if c is not None]
            if len(known) >= k:
                peaks = [c for c, r in known if r["finish"] <= 3 or _nf(r) >= 0.7]
                if peaks:
                    gap_c = max(peaks) - cur_class
                    cat = ("STRONG" if gap_c >= 1 else "POSITIVE" if gap_c == 0
                           else "NEUTRAL" if gap_c == -1 else "MIXED")
                    fact = f"peak_class_with_top3_or_top30pct={max(peaks)}; today_class={cur_class}"
                else:
                    cat, fact = "CAUTION", f"no_top3_or_top30pct_at_any_known_class; today_class={cur_class}"
                put("hidden_class", cat, href, fact + f"; runs={len(known)}", len(known))
        if runs:
            q = mean(_nf(r) for r in runs[:4])
            put("official_recent_quality", percentile_band(q), href,
                f"normalized_finish_last{min(4, len(runs))}={q:.3f}", min(4, len(runs)))

        # -- rotation / layoff / continuity
        if runs:
            gap = (day - date.fromisoformat(runs[0]["date"])).days
            put("rotation_fit", "CAUTION" if gap < 7 else "NEUTRAL" if gap <= 13 else "POSITIVE" if gap <= 70
                else "MIXED" if gap <= 120 else "CAUTION" if gap <= 240 else "WEAK",
                href[:1], f"days_since_last_run={gap}", 1)
            if gap <= 70:
                put("layoff_readiness", "POSITIVE", href[:1], f"days_since_last_run={gap}; in_racing_rhythm", 1)
            else:
                returns = [runs[i] for i in range(len(runs) - 1)
                           if (date.fromisoformat(runs[i]["date"]) - date.fromisoformat(runs[i + 1]["date"])).days > 70]
                if returns:
                    put("layoff_readiness", percentile_band(mean(_nf(r) for r in returns)), href,
                        f"days_since_last_run={gap}; prior_layoff_return_normalized_finish={mean(_nf(r) for r in returns):.3f}", len(returns))
                else:
                    put("layoff_readiness", "CAUTION", href[:1], f"days_since_last_run={gap}; first_long_layoff_return_untested", 1)
            n180 = sum(1 for r in runs if (day - date.fromisoformat(r["date"])).days <= 180)
            put("preparation_continuity", {0: "CAUTION", 1: "MIXED", 2: "NEUTRAL", 3: "POSITIVE"}.get(n180, "STRONG"),
                href, f"official_runs_in_180_days={n180}", n180)
            last = runs[0]
            same_cond = last.get("surface") == surface and distance is not None and last.get("distance_m") is not None \
                and abs(int(last["distance_m"]) - int(distance)) <= 200
            big_change = last.get("surface") != surface or (distance is not None and last.get("distance_m") is not None
                                                            and abs(int(last["distance_m"]) - int(distance)) > 400)
            put("target_intent", "STRONG" if same_cond and _nf(last) >= 0.6 else "NEUTRAL" if same_cond
                else "MIXED" if big_change else "NEUTRAL", href[:1],
                f"last_run_surface={last.get('surface')} distance={last.get('distance_m')} nf={_nf(last):.3f}; "
                f"today_surface={surface} distance={distance}", 1)

        # -- bodyweight
        bws = [(int(r["body_weight"]), r) for r in runs if isinstance(r.get("body_weight"), int)]
        cur_bw = d.get("current_body_weight")
        if len(bws) >= 3:
            spread = max(b for b, _ in bws[:6]) - min(b for b, _ in bws[:6])
            put("bodyweight_history_quality", _thr(-spread, ((-10, "STRONG"), (-20, "POSITIVE"), (-30, "NEUTRAL")), "CAUTION"),
                href, f"bodyweight_spread_last6={spread}kg", len(bws[:6]))
        if isinstance(cur_bw, int) and len(bws) >= 2:
            good = [b for b, r in bws if _nf(r) >= 0.5]
            if good:
                lo, hi = min(good), max(good)
                cat = "STRONG" if lo - 4 <= cur_bw <= hi + 4 else "NEUTRAL" if lo - 10 <= cur_bw <= hi + 10 else "CAUTION"
                fact = f"current={cur_bw}kg; top_half_finish_weights={lo}-{hi}kg"
            else:
                med = sorted(b for b, _ in bws)[len(bws) // 2]
                cat = "NEUTRAL" if abs(cur_bw - med) <= 6 else "MIXED"
                fact = f"current={cur_bw}kg; median_past={med}kg; no_top_half_finish"
            put("physical_readiness", cat, href, fact, len(bws))
            lo, hi = min(b for b, _ in bws), max(b for b, _ in bws)
            put("bodyweight_range_fit", "POSITIVE" if lo <= cur_bw <= hi else "NEUTRAL" if lo - 6 <= cur_bw <= hi + 6 else "CAUTION",
                href, f"current={cur_bw}kg; career_range={lo}-{hi}kg", len(bws))
        if weights and len(set(weights)) > 1:
            try:
                dw = float(official[rid].get("assigned_weight")) - mean(weights)
                put("weight_load_fit", _thr(-dw, ((2, "STRONG"), (0.5, "POSITIVE"), (-0.5, "NEUTRAL"), (-2, "MIXED")), "CAUTION"),
                    [f"JRA_OFFICIAL_RUNNER_UNIVERSE:{rid}:ASSIGNED_WEIGHT"],
                    f"assigned_minus_field_mean={dw:+.2f}kg", len(weights))
            except (TypeError, ValueError):
                pass

        # -- course geometry
        if venue:
            direction = "LEFT" if venue in LEFT_TURN else "RIGHT"
            same_dir = [r for r in runs if r.get("venue") and (("LEFT" if r["venue"] in LEFT_TURN else "RIGHT") == direction)
                        and r["venue"] in GEOMETRY]
            if len(same_dir) >= k:
                put("turn_direction_fit", percentile_band(mean(_nf(r) for r in same_dir)), href,
                    f"{direction}_turn_normalized_finish={mean(_nf(r) for r in same_dir):.3f}; runs={len(same_dir)}", len(same_dir))
            geo = GEOMETRY.get(venue)
            same_geo = [r for r in runs if GEOMETRY.get(r.get("venue")) == geo]
            if geo and len(same_geo) >= k:
                put("similar_geometry_fit", percentile_band(mean(_nf(r) for r in same_geo)), href,
                    f"{geo}_normalized_finish={mean(_nf(r) for r in same_geo):.3f}; runs={len(same_geo)}", len(same_geo))
            geo_surf = [r for r in same_geo if r.get("surface") == surface]
            if geo and surface and len(geo_surf) >= k:
                put("course_geometry_fit", percentile_band(mean(_nf(r) for r in geo_surf)), href,
                    f"{geo}_{surface}_normalized_finish={mean(_nf(r) for r in geo_surf):.3f}; runs={len(geo_surf)}",
                    len(geo_surf))
        if distance is not None:
            near = [r for r in runs if r.get("surface") == surface and r.get("distance_m") is not None
                    and abs(int(r["distance_m"]) - int(distance)) <= 200]
            if len(near) >= k:
                put("distance_fit", percentile_band(mean(_nf(r) for r in near)), href,
                    f"same_surface_within_200m_normalized_finish={mean(_nf(r) for r in near):.3f}; runs={len(near)}", len(near))
            if venue:
                cd = [r for r in near if r.get("venue") == venue]
                if cd:
                    put("same_course_distance_quality", percentile_band(mean(_nf(r) for r in cd)), href,
                        f"same_venue_surface_within_200m_normalized_finish={mean(_nf(r) for r in cd):.3f}; runs={len(cd)}", len(cd))
                elif runs:
                    put("same_course_distance_quality", "CAUTION", href[:1],
                        "no_prior_run_at_this_venue_surface_distance_band; untested", 0)

        # -- going / same-day
        if today_going and surface:
            gr = [r for r in runs if r.get("surface") == surface and str(r.get("going") or "") == today_going]
            if len(gr) >= k:
                put("going_fit", percentile_band(mean(_nf(r) for r in gr)), href + sd_refs,
                    f"today_going_from_same_day_official={today_going}; normalized_finish={mean(_nf(r) for r in gr):.3f}; runs={len(gr)}", len(gr))
        if len(top3_front) >= 6 and len(early) >= k:
            bias = sum(top3_front) / len(top3_front)
            style = mean(early)
            if bias >= 0.5:
                cat = "STRONG" if style <= 0.33 else "NEUTRAL" if style <= 0.6 else "CAUTION"
            elif bias <= 0.2:
                cat = "STRONG" if style >= 0.6 else "NEUTRAL" if style >= 0.33 else "MIXED"
            else:
                cat = "NEUTRAL"
            put("same_day_track_fit", cat, rref + sd_refs,
                f"same_day_top3_front_share={bias:.3f} (n={len(top3_front)}); horse_early_ratio={style:.3f}", len(top3_front))
        if len(top3_inner) >= 6:
            try:
                no = int(official[rid].get("horse_no") or d.get("horse_no") or rid)
                inner = no <= len(active) / 2
                share = sum(top3_inner) / len(top3_inner)
                fit = share if inner else 1 - share
                cat = _thr(fit, ((0.67, "STRONG"), (0.56, "POSITIVE"), (0.44, "NEUTRAL"), (0.33, "MIXED")), "CAUTION")
                fact = f"same_day_top3_inner_half_share={share:.3f} (n={len(top3_inner)}); horse_no={no}/{len(active)}"
                put("track_bias_fit", cat, sd_refs, fact, len(top3_inner))
                put("draw_course_fit", cat, sd_refs, fact, len(top3_inner))
            except (TypeError, ValueError):
                pass

        # -- people
        p = persons.get(rid) or {}
        jockey = _name(p.get("current_jockey") or d.get("jockey"))
        if jockey and runs:
            paired = [r for r in runs if _name(r.get("jockey")) == jockey]
            if paired:
                put("jockey_horse_fit", percentile_band(mean(_nf(r) for r in paired)), href,
                    f"pairings={len(paired)}; normalized_finish={mean(_nf(r) for r in paired):.3f}", len(paired))
            else:
                put("jockey_horse_fit", "NEUTRAL", href[:1], "observed_first_pairing_with_current_jockey", 0)
        if p.get("trainer_matched") is True:
            career = (p.get("trainer") or {}).get("career_flat") or {}
            try:
                starts, wr = int(career["starts"]), float(career["win_rate"])
                if starts >= 100 and 0 <= wr < 1:
                    put("stable_trainer_class", rate_band(wr), [f"JRA_OFFICIAL_PERSON_STATS:{rid}:trainer:career"],
                        f"trainer_career_starts={starts}; win_rate={wr:.3f}", starts)
            except (KeyError, TypeError, ValueError):
                pass

        # -- market (single official observation + official histories)
        pop = d.get("popularity_rank")
        try:
            pop = int(pop)
        except (TypeError, ValueError):
            pop = None
        n_act = len(active)
        if pop and n_act >= 2:
            past = [(int(r["popularity_rank"]) - 1) / (r["field_size"] - 1) for r in runs[:4]
                    if isinstance(r.get("popularity_rank"), int) and 1 <= r["popularity_rank"] <= r["field_size"]]
            if len(past) >= 2:
                cur = (pop - 1) / (n_act - 1)
                diff = abs(cur - mean(past))
                put("market_stability", _thr(-diff, ((-0.1, "STRONG"), (-0.2, "POSITIVE"), (-0.35, "NEUTRAL")), "MIXED"),
                    href + [f"JRA_OFFICIAL_MARKET:{rid}"],
                    f"current_popularity_ratio={cur:.3f}; past_mean={mean(past):.3f}; cross_race_stability", len(past))
            if rid in formed and len(formed) >= 3:
                fr = formed.index(rid) / (len(formed) - 1)
                pr = (pop - 1) / (n_act - 1)
                mm = pr - fr
                put("market_mismatch", _thr(mm, ((0.3, "STRONG"), (0.12, "POSITIVE"), (-0.12, "NEUTRAL"), (-0.3, "MIXED")), "CAUTION"),
                    href[:4] + [f"JRA_OFFICIAL_MARKET:{rid}"],
                    f"popularity_ratio={pr:.3f}; form_rank_ratio={fr:.3f}; underrated_by={mm:+.3f}", len(formed))

        # -- registered workout
        w = workout.get(rid) or {}
        if len(workout) >= 2 and str(w.get("assessment") or ""):
            put("training_comments_quality", comment_band(w["assessment"]),
                [f"REGISTERED_JRA_COMMON:WORKOUT:{rid}"], f"assessment={w['assessment']}", 1,
                authority="REGISTERED_JRA_COMMON")
        rating = str(w.get("rating") or "").strip().upper()
        if len(workout) >= 2 and rating in {"A", "B", "C", "D", "E"}:
            put("workout_finish", {"A": "STRONG", "B": "POSITIVE", "C": "NEUTRAL", "D": "CAUTION", "E": "WEAK"}[rating],
                [f"REGISTERED_JRA_COMMON:WORKOUT:{rid}"], f"final_workout_rating={rating}", 1,
                authority="REGISTERED_JRA_COMMON")

        # -- pedigree (point-in-time corpus)
        if corpus and corpus.get("horses"):
            name = str(d.get("horse_name") or official[rid].get("name") or "")
            sire, damsire = str(d.get("sire") or "").strip(), str(d.get("damsire") or "").strip()
            cref = [f"JRA_PEDIGREE_CORPUS:{corpus.get('manifest_sha256')}"]

            def pool(key, value, pred):
                horses, rows = 0, []
                for hn, h in corpus["horses"].items():
                    if h.get("horse_name") == name or not value or h.get(key) != value:
                        continue
                    sel = [r for r in h["runs"].values() if pred(r)]
                    if sel:
                        horses += 1
                        rows.extend(sel)
                return horses, rows

            def ped(feature, key, value, pred, min_h, min_r, label, rule=None):
                h, rows = pool(key, value, pred)
                if h >= min_h and len(rows) >= min_r:
                    m = mean(_nf(r) for r in rows)
                    put(feature, _ped_band(m), cref,
                        f"{key}={value}; {label}; offspring={h}; runs={len(rows)}; normalized_finish={m:.3f}",
                        len(rows), authority="JRA_OFFICIAL_POINT_IN_TIME_CORPUS", rule=rule)

            def physical_fit(key, value, rule):
                # Body weights at which this sire's (or damsire's) offspring ran
                # well on today's surface vs. this horse's official body weight.
                if not value or not surface:
                    return
                bw_now = cur_bw if isinstance(cur_bw, int) else (bws[0][0] if bws else None)
                if not isinstance(bw_now, int):
                    return
                h, rows = pool(key, value, lambda r: r["surface"] == surface and isinstance(r.get("body_weight"), int)
                               and _nf(r) >= 0.6)
                if h < 3 or len(rows) < 8:
                    return
                w = sorted(int(r["body_weight"]) for r in rows)
                lo, hi = w[len(w) // 10], w[min(len(w) - 1, (9 * len(w)) // 10)]
                cat = "POSITIVE" if lo <= bw_now <= hi else "NEUTRAL" if lo - 10 <= bw_now <= hi + 10 else "CAUTION"
                put("physical_pedigree_fit", cat, cref + href[:1],
                    f"{key}={value}; surface={surface}; good_run_bodyweight_p10_p90={lo}-{hi}kg; "
                    f"horse_bodyweight={bw_now}kg; offspring={h}; runs={len(rows)}",
                    len(rows), authority="JRA_OFFICIAL_POINT_IN_TIME_CORPUS", rule=rule)
            if surface:
                ped("pedigree_surface", "sire", sire, lambda r: r["surface"] == surface, 4, 12, f"surface={surface}")
                ped("maternal_class_signal", "damsire", damsire, lambda r: r["surface"] == surface, 3, 8, f"damsire_surface={surface}")
                if distance is not None:
                    ped("pedigree_distance", "sire", sire, lambda r: r["surface"] == surface and r.get("distance_m") is not None
                        and abs(int(r["distance_m"]) - int(distance)) <= 200, 3, 8, f"surface={surface}; distance={distance}±200")
            if cur_class is not None:
                ped("pedigree_class", "sire", sire, lambda r: (class_rank(r.get("race_name")) or -1) >= cur_class, 3, 6,
                    f"class_rank>={cur_class}")
            # Damsire fallbacks: only when the sire sample is unmet, with a
            # stricter minimum, a distinct rule id and the damsire named.
            if surface and distance is not None and "pedigree_distance" not in feats:
                ped("pedigree_distance", "damsire", damsire, lambda r: r["surface"] == surface
                    and r.get("distance_m") is not None and abs(int(r["distance_m"]) - int(distance)) <= 200,
                    4, 12, f"DAMSIRE_FALLBACK; surface={surface}; distance={distance}±200",
                    rule=FALLBACK_RULES["pedigree_distance"])
            if cur_class is not None and "pedigree_class" not in feats:
                ped("pedigree_class", "damsire", damsire,
                    lambda r: (class_rank(r.get("race_name")) or -1) >= cur_class, 4, 10,
                    f"DAMSIRE_FALLBACK; class_rank>={cur_class}", rule=FALLBACK_RULES["pedigree_class"])
            physical_fit("sire", sire, RULES["physical_pedigree_fit"])
            if "physical_pedigree_fit" not in feats:
                physical_fit("damsire", damsire, FALLBACK_RULES["physical_pedigree_fit"])
            if venue:
                ped("sire_track_signal", "sire", sire, lambda r: r.get("venue") == venue, 3, 6, f"venue={venue}")
            ped("sprint_pedigree", "sire", sire, lambda r: r.get("distance_m") is not None and int(r["distance_m"]) <= 1400,
                3, 8, "distance<=1400")
            # The earliest available race is NOT necessarily a debut: a
            # historical SOURCE often has only the last few prior starts.
            # Only an explicitly labelled official 新馬/メイクデビュー
            # result establishes debut. Missing debut is UNKNOWN, not WEAK.
            debut = []
            debut_h = 0
            for hn, h in corpus["horses"].items():
                if h.get("horse_name") == name or h.get("sire") != sire or not h["runs"]:
                    continue
                explicit_debuts = [
                    r for r in h["runs"].values()
                    if "新馬" in str(r.get("race_name") or "")
                    or "メイクデビュー" in str(r.get("race_name") or "")
                ]
                if len(explicit_debuts) != 1:
                    continue
                debut.append(explicit_debuts[0])
                debut_h += 1
            if debut_h >= 4:
                m = mean(_nf(r) for r in debut)
                put("sire_newcomer_signal", _ped_band(m), cref,
                    f"sire={sire}; explicit_official_debut_race_count={debut_h}; normalized_finish={m:.3f}", debut_h,
                    authority="JRA_OFFICIAL_POINT_IN_TIME_CORPUS")
            if "distance_fit" not in feats and "pedigree_distance" in feats and not runs:
                x = dict(feats["pedigree_distance"])
                x["rule_id"] = RULES["distance_fit"]
                x["source_fact"] = "distance_fit (newcomer, sire distance record): " + x["source_fact"]
                feats["distance_fit"] = x
        out[rid] = feats
    return out
