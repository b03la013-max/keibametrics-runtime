from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import re
import statistics
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Tuple

PROFILE = "KM-LOCAL-NAR-EVIDENCE-CANDIDATE-v0.1-20260923"
DEFAULT_REGISTRY = "mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json"
RECENCY = [0.30, 0.25, 0.20, 0.15, 0.10]
NEUTRAL = 52.0


class LocalCandidateEvidenceError(ValueError):
    pass


def _sha(x: Any) -> str:
    return hashlib.sha256(
        json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, float(x)))


def _norm(s: Any) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", str(s or ""))).strip()


def _load(path: str | Path) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _parse_date(s: str) -> dt.date | None:
    s = _norm(s)
    m = re.fullmatch(r"(\d{2})\.(\d{2})\.(\d{2})", s)
    if not m:
        return None
    yy, mm, dd = map(int, m.groups())
    return dt.date(2000 + yy, mm, dd)


def _time_seconds(s: str) -> float | None:
    s = str(s or "").strip()
    m = re.search(r"(\d+):(\d{2})\.(\d)", s)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2)) + int(m.group(3)) / 10.0
    m = re.search(r"(?<!\d)(\d{2,3})\.(\d)(?!\d)", s)
    if m:
        return int(m.group(1)) + int(m.group(2)) / 10.0
    return None


def _class_score(text: str) -> Tuple[float, str]:
    """Transparent ordinal only. Candidate / uncalibrated, never a probability."""
    t = _norm(text).upper()
    table = [
        (r"(JPN|JPN)?[ⅠI]$|JPN1|JPNI|G1|GI|Ｓ１|S1", 100),
        (r"JPN2|JPNII|G2|GII|Ｓ２|S2", 96),
        (r"JPN3|JPNIII|G3|GIII|Ｓ３|S3", 92),
        (r"オープン|OPEN|Ａ１|A1", 88),
        (r"Ａ２|A2", 84),
        (r"Ａ３|A3", 80),
        (r"３勝クラス|3勝クラス|Ｂ１|B1", 78),
        (r"２勝クラス|2勝クラス|Ｂ２|B2", 74),
        (r"１勝クラス|1勝クラス|Ｂ３|B3", 70),
        (r"Ｃ１|C1", 64),
        (r"Ｃ２|C2", 58),
        (r"Ｃ３|C3", 52),
        (r"未勝利|新馬", 54),
    ]
    hits = [score for pat, score in table if re.search(pat, t)]
    if hits:
        return float(max(hits)), "PARSED_CLASS_ORDINAL"
    # Composite request codes such as B3_C1_SELECTED.
    tokens = re.findall(r"[ABC]\d", t)
    if tokens:
        vals = []
        for token in tokens:
            vals.append({"A1": 88, "A2": 84, "A3": 80, "B1": 78, "B2": 74, "B3": 70,
                         "C1": 64, "C2": 58, "C3": 52}.get(token, NEUTRAL))
        return sum(vals) / len(vals), "PARSED_COMPOSITE_CLASS_ORDINAL"
    return NEUTRAL, "CLASS_UNRESOLVED_CANONICAL_NEUTRAL"


def _finish_score(finish: int | None, field: int | None) -> float | None:
    if finish is None or field is None or field <= 1:
        return None
    return _clamp(100.0 * (field - finish) / (field - 1))


def _weighted(values: List[float | None]) -> float | None:
    total = 0.0
    weight = 0.0
    for i, value in enumerate(values[:5]):
        if value is None:
            continue
        w = RECENCY[i]
        total += float(value) * w
        weight += w
    return None if weight <= 0 else total / weight


def _mean(values: List[float | None]) -> float | None:
    xs = [float(x) for x in values if x is not None]
    return None if not xs else sum(xs) / len(xs)


def _std(values: List[float | None]) -> float | None:
    xs = [float(x) for x in values if x is not None]
    if len(xs) < 2:
        return None
    return statistics.pstdev(xs)


def _going_group(x: str) -> str:
    x = _norm(x)
    if x in {"不良", "重"}:
        return "WET"
    if x == "稍重":
        return "INTERMEDIATE"
    if x == "良":
        return "DRY"
    return "UNKNOWN"


def _same_going(a: str, b: str) -> bool:
    ga, gb = _going_group(a), _going_group(b)
    if "UNKNOWN" in {ga, gb}:
        return False
    return ga == gb or ({ga, gb} <= {"WET", "INTERMEDIATE"})


def _descriptor(text: str) -> Dict[str, Any]:
    t = unicodedata.normalize("NFKC", str(text or "")).strip()
    m = re.match(
        r"(?P<finish>\d+)\s+(?P<date>\d{2}\.\d{2}\.\d{2})\s+(?P<going>\S+)\s+"
        r"(?P<field>\d+)頭\s+(?P<venue>\S+)\s+(?P<course>.+?)\s+(?P<horse_no>\d+)番$",
        t,
    )
    if not m:
        return {"raw": t, "parsed": False}
    g = m.groupdict()
    dist = None
    dm = re.search(r"(\d{3,4})$", g["course"])
    if dm:
        dist = int(dm.group(1))
    surface = "TURF" if "芝" in g["course"] else "DIRT"
    direction = "LEFT" if "左" in g["course"] else ("RIGHT" if "右" in g["course"] else "UNKNOWN")
    venue = re.sub(r"^J", "Ｊ", g["venue"])
    return {
        "raw": t, "parsed": True, "finish": int(g["finish"]), "date": g["date"],
        "going": g["going"], "field_size": int(g["field"]), "venue": venue,
        "distance": dist, "surface": surface, "direction": direction,
        "horse_no": int(g["horse_no"]),
    }


def _ride(text: str) -> Dict[str, Any]:
    t = unicodedata.normalize("NFKC", str(text or "")).strip()
    m = re.match(r"(?P<pop>\d+)人\s+(?P<bw>\d{3,4})\s+(?P<jockey>.+?)\s+(?P<load>\d+(?:\.\d+)?)$", t)
    if not m:
        return {"raw": t, "parsed": False}
    g = m.groupdict()
    return {"raw": t, "parsed": True, "popularity": int(g["pop"]), "body_weight": int(g["bw"]),
            "jockey": _norm(g["jockey"]).replace("☆", "").replace("▲", "").replace("△", ""),
            "carried_weight": float(g["load"])}


def _run_content(text: str) -> Dict[str, Any]:
    t = unicodedata.normalize("NFKC", str(text or "")).strip()
    sec = _time_seconds(t)
    pm = re.search(r"(?<!\d)(\d+(?:-\d+){1,5})(?!\d)", t)
    positions = [int(x) for x in pm.group(1).split("-")] if pm else []
    fm = re.search(r"(\d{2}\.\d)\s*$", t)
    final3f = float(fm.group(1)) if fm else None
    return {"raw": t, "time_seconds": sec, "positions": positions, "final3f": final3f}


def _margin(text: str) -> Dict[str, Any]:
    t = unicodedata.normalize("NFKC", str(text or "")).strip()
    m = re.match(r"(?P<margin>\d+(?:\.\d+)?)\s+(?P<winner>.+)$", t)
    if not m:
        return {"raw": t, "margin": None, "winner": None}
    return {"raw": t, "margin": float(m.group("margin")), "winner": m.group("winner")}


def _is_primary(row: List[str]) -> bool:
    if len(row) < 2 or not re.fullmatch(r"\d{1,2}", str(row[0]).strip()):
        return False
    if len(row) >= 3 and re.fullmatch(r"\d{1,2}", str(row[1]).strip()):
        return _norm(row[2]) not in {"", "競走馬", "馬名"}
    return _norm(row[1]) not in {"", "競走馬", "馬名", "前走回"}


def _primary_identity(row: List[str]) -> Tuple[int | None, int, str, int]:
    if len(row) >= 3 and re.fullmatch(r"\d{1,2}", str(row[1]).strip()):
        return int(row[0]), int(row[1]), str(row[2]).strip(), 3
    return None, int(row[0]), str(row[1]).strip(), 2


def _record_after_label(row: List[str], label: str) -> Dict[str, int] | None:
    try:
        i = row.index(label)
    except ValueError:
        return None
    if i + 4 >= len(row):
        return None
    vals = []
    for x in row[i + 1:i + 5]:
        m = re.search(r"\d+", str(x))
        vals.append(int(m.group()) if m else 0)
    return {"win": vals[0], "second": vals[1], "third": vals[2], "other": vals[3],
            "starts": sum(vals)}


def parse_race_card(source_artifact: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    ev = source_artifact.get("normalized_evidence") or {}
    rc = ev.get("race_card_tables") or {}
    tables = rc.get("value") if isinstance(rc, dict) else None
    if not isinstance(tables, list) or not tables:
        raise LocalCandidateEvidenceError("RACE_CARD_TABLES_MISSING")
    rows = None
    for table in tables:
        if isinstance(table, list) and any(isinstance(r, list) and "競走馬" in r for r in table):
            if rows is None or len(table) > len(rows):
                rows = table
    if not rows:
        raise LocalCandidateEvidenceError("RACE_CARD_MAIN_TABLE_MISSING")

    primary_indices = [i for i, row in enumerate(rows) if isinstance(row, list) and _is_primary(row)]
    out: Dict[str, Dict[str, Any]] = {}
    for n, i in enumerate(primary_indices):
        stop = primary_indices[n + 1] if n + 1 < len(primary_indices) else len(rows)
        group = rows[i:stop]
        if len(group) < 5:
            continue
        p, meta, blood, content, marginrow = group[:5]
        frame, horse_no, name, off = _primary_identity(p)
        recent_desc = [_descriptor(x) for x in p[-5:]]
        race_names = [str(x).strip() for x in meta[-5:]]
        ride_rows = [_ride(x) for x in blood[-5:]]
        contents = [_run_content(x) for x in content[-5:]]
        margins = [_margin(x) for x in marginrow[-5:]]

        current_jockey = _norm(p[off]).replace("☆", "").replace("▲", "").replace("△", "")
        odds_m = re.search(r"(\d+(?:\.\d+)?)\s*\((\d+)人気\)", str(p[off + 1]))
        odds = float(odds_m.group(1)) if odds_m else None
        pop = int(odds_m.group(2)) if odds_m else None
        sex_age = _norm(meta[0])
        age_m = re.search(r"(\d+)", sex_age)
        age = int(age_m.group(1)) if age_m else None
        load_m = re.search(r"(\d+(?:\.\d+)?)", unicodedata.normalize("NFKC", str(meta[3])))
        current_load = float(load_m.group(1)) if load_m else None
        bw_m = re.search(r"(\d{3,4})\s*\(([+-]?\d+)\)", unicodedata.normalize("NFKC", str(blood[2])))
        current_bw = int(bw_m.group(1)) if bw_m else None
        current_bw_change = int(bw_m.group(2)) if bw_m else None
        sire = str(blood[0]).strip()
        trainer = _norm(blood[1])
        dam = str(content[0]).strip()
        damsire = re.sub(r"^[（(]|[）)]$", "", str(marginrow[0]).strip())

        starts = []
        for j in range(5):
            d = recent_desc[j]
            if not d.get("parsed"):
                continue
            r = dict(d)
            r["race_name"] = race_names[j]
            r.update({f"ride_{k}": v for k, v in ride_rows[j].items() if k != "raw"})
            r.update({f"content_{k}": v for k, v in contents[j].items() if k != "raw"})
            r["margin"] = margins[j].get("margin")
            r["winner"] = margins[j].get("winner")
            r["class_score"], r["class_parse_state"] = _class_score(r["race_name"])
            r["finish_score"] = _finish_score(r.get("finish"), r.get("field_size"))
            starts.append(r)

        out[str(horse_no)] = {
            "runner_id": str(horse_no), "horse_no": horse_no, "frame_no": frame, "name": name,
            "current_jockey": current_jockey, "odds": odds, "popularity": pop,
            "sex_age": sex_age, "age": age, "current_load": current_load,
            "current_body_weight": current_bw, "current_body_weight_change": current_bw_change,
            "sire": sire, "dam": dam, "damsire": damsire, "trainer": trainer,
            "all_record": _record_after_label(p, "全"),
            "left_record": _record_after_label(p, "左"),
            "right_record": _record_after_label(p, "右"),
            "venue_record": _record_after_label(p, "場"),
            "distance_record": _record_after_label(p, "距"),
            "starts": starts,
            "race_card_source_id": rc.get("source_id"),
            "race_card_snapshot_sha256": rc.get("snapshot_sha256"),
            "race_card_fetched_at": rc.get("fetched_at"),
        }
    if not out:
        raise LocalCandidateEvidenceError("RACE_CARD_RUNNERS_EMPTY")
    return out


def _feature(score: float | None, rule: Dict[str, Any], refs: List[str], fact: str, ts: str,
             *, missing: bool = False, coverage: float = 1.0, raw: Any = None) -> Dict[str, Any]:
    if score is None:
        score = NEUTRAL
        missing = True
    return {
        "score": round(_clamp(score), 6),
        "rule_id": rule["rule_id"],
        "evidence_refs": sorted(set(str(x) for x in refs if x)),
        "source_fact": fact,
        "source_timestamp": ts,
        "missing": bool(missing),
        "coverage": round(_clamp(coverage * 100.0) / 100.0, 6),
        "candidate_only": True,
        "calibration_status": "UNVALIDATED_CANDIDATE",
        "raw_metric": raw,
    }


def _candidate_rule(reg: Dict[str, Any], index: str, component: str) -> Dict[str, Any]:
    try:
        return reg["component_score_rules"][index][component]
    except Exception as e:
        raise LocalCandidateEvidenceError(f"CANDIDATE_RULE_MISSING:{index}:{component}") from e


def _performance_on(starts: List[Dict[str, Any]], predicate) -> Tuple[float | None, float]:
    rows = [r for r in starts if predicate(r)]
    vals = [r.get("finish_score") for r in rows]
    return _mean(vals), min(1.0, len(rows) / 3.0)


def _interval_days(starts: List[Dict[str, Any]], race_date: dt.date | None) -> List[int]:
    dates = [_parse_date(r.get("date", "")) for r in starts]
    dates = [x for x in dates if x]
    if not dates:
        return []
    ans = []
    if race_date:
        ans.append((race_date - dates[0]).days)
    for a, b in zip(dates, dates[1:]):
        ans.append((a - b).days)
    return [x for x in ans if x >= 0]


def _interval_score(days: int | None) -> float | None:
    if days is None:
        return None
    if 14 <= days <= 42:
        return 85.0
    if 8 <= days <= 70:
        return 72.0
    if 71 <= days <= 120:
        return 60.0
    if days < 8:
        return 58.0
    return 52.0


def _same_venue_name(historical: str, current: str) -> bool:
    h, c = _norm(historical).replace("ナ", ""), _norm(current)
    return c and c in h


def _build_preliminary(raw: Dict[str, Any], request: Dict[str, Any], source: Dict[str, Any],
                       reg: Dict[str, Any], field_size: int) -> Dict[str, Any]:
    race = request.get("race") or {}
    venue = str(race.get("venue") or race.get("venue_id") or request.get("venue_id") or "")
    venue_name = {"URW": "浦和", "FNB": "船橋", "OHI": "大井", "KAW": "川崎",
                  "MOR": "盛岡", "MIZ": "水沢", "KSM": "笠松", "NGY": "名古屋",
                  "SON": "園田", "HIM": "姫路", "KCH": "高知", "SAG": "佐賀",
                  "MON": "門別", "KNZ": "金沢"}.get(venue.upper(), venue)
    distance = int(race.get("distance") or 0)
    going = str(((source.get("normalized_evidence") or {}).get("track_condition") or {}).get("value")
                or race.get("going") or "")
    direction = "LEFT" if venue.upper() in {"URW", "FNB", "KAW", "MOR"} else "RIGHT"
    surface = str(race.get("surface") or "dirt").upper()
    race_date_s = str(race.get("race_date") or race.get("date") or request.get("race_date") or "")
    try:
        race_date = dt.date.fromisoformat(race_date_s.replace("/", "-"))
    except Exception:
        race_date = None
    starts = raw["starts"]
    refs = [raw.get("race_card_source_id"), raw.get("race_card_snapshot_sha256")]
    ts = str(raw.get("race_card_fetched_at") or source.get("source_freeze_at") or "")
    features: Dict[str, Any] = {}
    missing_components: List[str] = []

    def put(index: str, comp: str, score: float | None, fact: str, *, coverage=1.0, raw_metric=None,
            extra_refs: List[str] | None = None, force_missing=False):
        rule = _candidate_rule(reg, index, comp)
        miss = force_missing or score is None
        if miss:
            missing_components.append(f"{index}.{comp}")
        features[comp] = _feature(score, rule, refs + (extra_refs or []), fact, ts,
                                  missing=miss, coverage=coverage, raw=raw_metric)

    finish_vals = [r.get("finish_score") for r in starts]
    recent_finish = _weighted(finish_vals)
    put("HPI-L", "recent_finish", recent_finish,
        f"last5 normalized finish scores={finish_vals}; recency weights={RECENCY}",
        coverage=min(1, len(starts) / 5), raw_metric=finish_vals)

    margin_scores = [None if r.get("margin") is None else 100.0 * math.exp(-float(r["margin"]) / 2.0) for r in starts]
    put("HPI-L", "finish_margin", _weighted(margin_scores),
        f"last5 winner-margin exponential scores={margin_scores}", coverage=sum(x is not None for x in margin_scores) / 5,
        raw_metric=[r.get("margin") for r in starts])

    last_corner_scores = []
    progress_scores = []
    first_call_scores = []
    maintenance_scores = []
    for r in starts:
        pos = r.get("content_positions") or []
        fs = r.get("field_size")
        if pos and fs and fs > 1:
            first = _finish_score(pos[0], fs)
            last = _finish_score(pos[-1], fs)
            first_call_scores.append(first)
            last_corner_scores.append(last)
            progress_scores.append(_clamp(50 + (last - first) / 2))
            maintenance_scores.append(_clamp(50 + (last - first) / 2))
        else:
            first_call_scores.append(None); last_corner_scores.append(None)
            progress_scores.append(None); maintenance_scores.append(None)
    put("HPI-L", "passing_position_content", _weighted(last_corner_scores),
        f"last-corner normalized reach={last_corner_scores}", coverage=sum(x is not None for x in last_corner_scores) / 5,
        raw_metric=last_corner_scores)

    class_vals = [r.get("class_score") for r in starts]
    put("HPI-L", "class_level", _weighted(class_vals),
        f"candidate class ordinals={class_vals}", coverage=len(class_vals) / 5, raw_metric=class_vals)
    opponent = [_clamp(0.75 * float(r.get("class_score", NEUTRAL)) +
                       0.25 * _clamp(50 + (float(r.get("field_size", field_size)) - 8) * 4))
                for r in starts]
    put("HPI-L", "opponent_strength", _weighted(opponent),
        f"class+field candidate opponent scores={opponent}", coverage=len(opponent) / 5, raw_metric=opponent)
    st = _std([x for x in finish_vals if x is not None])
    repeatability = None if st is None else _clamp(100 - 1.6 * st)
    put("HPI-L", "repeatability", repeatability,
        f"population std of normalized recent finish={st}", coverage=min(1, len(starts) / 3), raw_metric=st)

    venue_perf, venue_cov = _performance_on(starts, lambda r: _same_venue_name(r.get("venue", ""), venue_name))
    put("CFIg-L", "same_venue", venue_perf, f"same-venue {venue_name} performance", coverage=venue_cov,
        raw_metric={"venue": venue_name, "score": venue_perf})
    dist_perf, dist_cov = _performance_on(starts, lambda r: r.get("distance") == distance)
    put("CFIg-L", "same_distance", dist_perf, f"same-distance {distance}m performance", coverage=dist_cov,
        raw_metric={"distance": distance, "score": dist_perf})
    sim_perf, sim_cov = _performance_on(starts, lambda r: r.get("distance") and abs(r["distance"] - distance) <= max(200, int(distance * .20)))
    put("CFIg-L", "similar_distance", sim_perf, f"similar-distance window around {distance}m", coverage=sim_cov,
        raw_metric=sim_perf)
    geom_perf, geom_cov = _performance_on(starts, lambda r: r.get("direction") == direction and r.get("surface") == surface)
    put("CFIg-L", "course_geometry", geom_perf, f"same direction/surface={direction}/{surface}", coverage=geom_cov,
        raw_metric=geom_perf)
    dir_perf, dir_cov = _performance_on(starts, lambda r: r.get("direction") == direction)
    put("CFIg-L", "turn_direction", dir_perf, f"same direction={direction}", coverage=dir_cov, raw_metric=dir_perf)
    early_mean = _mean(first_call_scores)
    inner = None
    if field_size > 1 and raw.get("horse_no"):
        inner = 100 * (field_size - int(raw["horse_no"])) / (field_size - 1)
    draw_fit = None if early_mean is None or inner is None else _clamp(52 + ((early_mean - 50) / 50) * ((inner - 50) / 2))
    put("CFIg-L", "draw_style_fit", draw_fit, f"candidate draw/style interaction early={early_mean},inner={inner}",
        coverage=0.5 if draw_fit is not None else 0, raw_metric={"early": early_mean, "inner": inner})
    go_perf, go_cov = _performance_on(starts, lambda r: _same_going(r.get("going", ""), going))
    put("CFIg-L", "going_fit", go_perf, f"going-group match current={going}", coverage=go_cov, raw_metric=go_perf)

    early_valid = [x for x in first_call_scores if x is not None]
    style_std = _std(early_valid)
    style_repro = None if style_std is None else _clamp(100 - 1.5 * style_std)
    put("RFIg-L", "running_style_repro", style_repro, f"early-position stability std={style_std}",
        coverage=min(1, len(early_valid) / 3), raw_metric=style_std)
    put("RFIg-L", "position_acquisition", _weighted(first_call_scores),
        f"first-call normalized position={first_call_scores}", coverage=len(early_valid) / 5, raw_metric=first_call_scores)
    put("RFIg-L", "position_maintenance", _weighted(maintenance_scores),
        f"first-to-last-call retention={maintenance_scores}", coverage=sum(x is not None for x in maintenance_scores) / 5,
        raw_metric=maintenance_scores)
    put("RFIg-L", "third_corner_progression", _weighted(progress_scores),
        f"early-to-late progress proxy={progress_scores}", coverage=sum(x is not None for x in progress_scores) / 5,
        raw_metric=progress_scores)
    lead_scores = []
    nonfront_scores = []
    for r in starts:
        pos = r.get("content_positions") or []
        if pos and r.get("field_size"):
            if pos[0] <= 3:
                lead_scores.append(r.get("finish_score"))
            else:
                nonfront_scores.append(r.get("finish_score"))
    put("RFIg-L", "leadership_stalk_acceptance", _mean(lead_scores),
        f"performance when first call <=3={lead_scores}", coverage=min(1, len(lead_scores) / 3), raw_metric=lead_scores)
    put("RFIg-L", "kickback_traffic_tolerance", _mean(nonfront_scores),
        f"performance from first call >3={nonfront_scores}", coverage=min(1, len(nonfront_scores) / 3), raw_metric=nonfront_scores)
    wet_rows = [r.get("finish_score") for r in starts if _same_going(r.get("going", ""), going)]
    put("RFIg-L", "going_adaptation", _mean(wet_rows), f"position/performance current-going group={wet_rows}",
        coverage=min(1, len(wet_rows) / 3), raw_metric=wet_rows)
    curj = _norm(raw.get("current_jockey"))
    jockey_runs = [r for r in starts if _norm(r.get("ride_jockey")) == curj]
    put("RFIg-L", "jockey_reproducibility", _mean([r.get("finish_score") for r in jockey_runs]),
        f"current jockey={curj} same-horse recent runs={len(jockey_runs)}",
        coverage=min(1, len(jockey_runs) / 3), raw_metric=[r.get("finish_score") for r in jockey_runs])

    # Pedigree population statistics are not present in the current official race-card source.
    for comp in ["sire_fit","damsire_fit","distance_sustain","distance_trait","surface_sand_fit","venue_stat","physical_style_fit"]:
        put("BVIg-L", comp, None,
            f"{comp}: pedigree names are present ({raw.get('sire')}/{raw.get('damsire')}), but official population fit statistic is absent; canonical neutral, not weakness.",
            coverage=0, raw_metric={"sire": raw.get("sire"), "damsire": raw.get("damsire")}, force_missing=True)

    jockey_venue = [r for r in jockey_runs if _same_venue_name(r.get("venue", ""), venue_name)]
    put("JTI-L", "venue_recent", _mean([r.get("finish_score") for r in jockey_venue]),
        f"current jockey recent same-horse same-venue runs={len(jockey_venue)}", coverage=min(1, len(jockey_venue) / 3))
    jockey_dist = [r for r in jockey_runs if r.get("distance") == distance]
    put("JTI-L", "distance_record", _mean([r.get("finish_score") for r in jockey_dist]),
        f"current jockey recent same-horse same-distance runs={len(jockey_dist)}", coverage=min(1, len(jockey_dist) / 3))
    put("JTI-L", "stable_combo", None,
        "official stable-wide jockey/trainer combination statistic not included in current source bundle; canonical neutral.", coverage=0, force_missing=True)
    j_early = []
    j_prog = []
    for r in jockey_runs:
        pos = r.get("content_positions") or []
        fs = r.get("field_size")
        if pos and fs and fs > 1:
            a = _finish_score(pos[0], fs); z = _finish_score(pos[-1], fs)
            j_early.append(a); j_prog.append(_clamp(50 + (z-a)/2))
    put("JTI-L", "position_acquisition_skill", _mean(j_early),
        f"current jockey first-call quality on horse={j_early}", coverage=min(1, len(j_early) / 3))
    put("JTI-L", "progression_timing_skill", _mean(j_prog),
        f"current jockey progression quality on horse={j_prog}", coverage=min(1, len(j_prog) / 3))
    fav = [r.get("finish_score") for r in jockey_runs if r.get("ride_popularity") and r["ride_popularity"] <= 3]
    lng = [r.get("finish_score") for r in jockey_runs if r.get("ride_popularity") and r["ride_popularity"] >= max(6, field_size // 2)]
    put("JTI-L", "favorite_reliability", _mean(fav), f"current jockey popular same-horse runs={fav}", coverage=min(1, len(fav) / 3))
    put("JTI-L", "longshot_record", _mean(lng), f"current jockey longshot same-horse runs={lng}", coverage=min(1, len(lng) / 3))

    put("CSI-L", "stable_venue_class_distance", None,
        "official stable-wide venue/class/distance statistic not included in current source bundle; canonical neutral.", coverage=0, force_missing=True)
    venue_changes = len({re.sub("ナ$", "", _norm(r.get("venue"))) for r in starts if r.get("venue")})
    transfer_score = 70.0 if venue_changes <= 2 and starts else (60.0 if starts else None)
    put("CSI-L", "transfer_preparation", transfer_score,
        f"recent venue diversity={venue_changes}; candidate preparation proxy only.", coverage=min(1, len(starts)/5), raw_metric=venue_changes)
    intervals = _interval_days(starts, race_date)
    first_interval = intervals[0] if intervals else None
    put("CSI-L", "layoff_preparation", _interval_score(first_interval),
        f"days since latest start={first_interval}", coverage=1 if first_interval is not None else 0, raw_metric=first_interval)
    continuity = 100.0 * len(jockey_runs) / max(1, min(5, len(starts))) if starts else None
    put("CSI-L", "jockey_use_continuity", continuity,
        f"current jockey rode {len(jockey_runs)}/{min(5,len(starts))} recent runs", coverage=min(1, len(starts)/5), raw_metric=continuity)
    put("CSI-L", "cci_specificity", None, "official pre-race stable comment source absent from current bundle; canonical neutral.", coverage=0, force_missing=True)
    put("CSI-L", "tri_vertical_comparison", None, "official training/trial source absent from current bundle; canonical neutral.", coverage=0, force_missing=True)
    interval_std = _std([float(x) for x in intervals])
    rot = None if interval_std is None else _clamp(100 - interval_std)
    put("CSI-L", "rotation_management", rot, f"recent interval std days={interval_std}", coverage=min(1, len(intervals)/3), raw_metric=intervals)

    historical_bw = [(r.get("ride_body_weight"), r.get("finish_score")) for r in starts if r.get("ride_body_weight")]
    good_weights = [bw for bw, perf in historical_bw if perf is not None and perf >= 60]
    current_bw = raw.get("current_body_weight")
    gwr = None
    if current_bw is not None and good_weights:
        lo, hi = min(good_weights)-5, max(good_weights)+5
        gwr = 85.0 if lo <= current_bw <= hi else _clamp(85 - min(abs(current_bw-lo), abs(current_bw-hi))*2)
    put("BWI-L", "good_weight_range", gwr,
        f"current bodyweight={current_bw}; good recent range source={good_weights}", coverage=min(1, len(good_weights)/3), raw_metric=good_weights)
    put("BWI-L", "weight_change_reason_rate", None,
        f"bodyweight change={raw.get('current_body_weight_change')}kg but causal reason source absent; canonical neutral.", coverage=0, force_missing=True)
    current_load = raw.get("current_load")
    field_loads = [x.get("current_load") for x in (request.get("_candidate_raw_field") or {}).values() if x.get("current_load") is not None]
    load_score = None
    if current_load is not None and field_loads:
        lo, hi = min(field_loads), max(field_loads)
        load_score = 52.0 if hi == lo else 40 + 45 * (hi-current_load)/(hi-lo)
    put("BWI-L", "carried_weight", load_score, f"field-relative carried weight={current_load}; field={field_loads}",
        coverage=1 if load_score is not None else 0, raw_metric=current_load)
    put("BWI-L", "age_growth", None, f"age={raw.get('age')} but no horse-specific growth evidence; canonical neutral.", coverage=0, force_missing=True)
    put("BWI-L", "interval", _interval_score(first_interval), f"days since latest start={first_interval}",
        coverage=1 if first_interval is not None else 0, raw_metric=first_interval)
    bwchg = raw.get("current_body_weight_change")
    fatigue = None
    if first_interval is not None and bwchg is not None:
        fatigue = _clamp(70 + min(15, max(-15, bwchg))/3 - max(0, 14-first_interval))
    put("BWI-L", "fatigue_rebound", fatigue,
        f"candidate interval/bodyweight rebound proxy interval={first_interval},change={bwchg}",
        coverage=0.5 if fatigue is not None else 0, raw_metric={"interval":first_interval,"change":bwchg})
    put("BWI-L", "transport_season", None, "transport/season-specific causal source absent; canonical neutral.", coverage=0, force_missing=True)
    put("BWI-L", "paddock", None, "official paddock source absent from current automatic bundle; canonical neutral.", coverage=0, force_missing=True)

    recent_coverage = min(1.0, len(starts) / 5.0)
    put("DCR", "official_recent_coverage", 100*recent_coverage,
        f"official recent runs parsed={len(starts)}/5", coverage=1, raw_metric=len(starts))
    comparable = sum(1 for r in starts if _same_venue_name(r.get("venue",""), venue_name) and r.get("distance")==distance)
    comp_cov = min(1.0, comparable/3.0)
    put("DCR", "same_venue_distance_comparability", 100*comp_cov,
        f"same venue+distance recent comparable runs={comparable}", coverage=1, raw_metric=comparable)
    put("DCR", "training_comment_trial", 0.0,
        "training/comment/trial source not present in current automatic source manifest.", coverage=1, raw_metric=0)
    bw_cov = min(1.0, (int(current_bw is not None) + len(historical_bw))/6.0)
    put("DCR", "bodyweight_range_coverage", 100*bw_cov,
        f"bodyweight observations={int(current_bw is not None)+len(historical_bw)}/6", coverage=1, raw_metric=bw_cov)
    prev_result_keys = [k for k in (source.get("normalized_evidence") or {}) if re.fullmatch(r"same_day_r\d+_result_tables", k)]
    race_no = int(request.get("race_no") or race.get("race_no") or 1)
    same_day_cov = min(1.0, len(prev_result_keys)/max(1,race_no-1))
    put("DCR", "same_day_gci_coverage", 100*same_day_cov,
        f"same-day prior official result sources={len(prev_result_keys)}/{max(0,race_no-1)}", coverage=1, raw_metric=same_day_cov)
    odds_present = isinstance((source.get("normalized_evidence") or {}).get("odds_tables"), dict)
    put("DCR", "late_odds_changes_coverage", 100.0 if odds_present else 0.0,
        f"official odds source present={odds_present}", coverage=1, raw_metric=odds_present)

    current_class, cls_state = _class_score(str(race.get("class") or ""))
    prev_class = starts[0].get("class_score") if starts else None
    put("NCI", "current_class", current_class, f"current race class={race.get('class')}; state={cls_state}",
        coverage=1, raw_metric=current_class)
    put("NCI", "previous_class", prev_class, f"latest race class ordinal={prev_class}",
        coverage=1 if prev_class is not None else 0, raw_metric=prev_class)
    put("NCI", "recent_opponent_class", _weighted(class_vals), f"recent class ordinals={class_vals}",
        coverage=len(class_vals)/5, raw_metric=class_vals)
    put("NCI", "race_set_level", current_class, f"current race-set class ordinal={current_class}", coverage=1, raw_metric=current_class)
    pressure = None if prev_class is None else _clamp(50 + (prev_class-current_class)*1.5)
    put("NCI", "class_change_pressure", pressure,
        f"previous-current class delta={None if prev_class is None else prev_class-current_class}",
        coverage=1 if pressure is not None else 0, raw_metric=pressure)
    is_jra_transfer = bool(starts and _norm(starts[0].get("venue","")).startswith("J"))
    transfer_class = None
    if starts:
        transfer_class = _clamp(50 + ((prev_class or NEUTRAL)-current_class) * (1.2 if is_jra_transfer else 0.8))
    put("NCI", "transfer_class", transfer_class,
        f"latest venue={starts[0].get('venue') if starts else None}; JRA transfer={is_jra_transfer}",
        coverage=1 if transfer_class is not None else 0, raw_metric=transfer_class)
    # class_relative_time is populated in a second cross-runner pass.
    put("NCI", "class_relative_time", None,
        "awaiting field-relative comparable-time second pass.", coverage=0, force_missing=True)

    return {
        "runner_id": raw["runner_id"], "name": raw["name"],
        "evidence_features": features,
        "candidate_missing_components": missing_components,
        "candidate_missing_count": len(missing_components),
        "candidate_component_count": sum(len(v) for v in reg["common_component_sets"].values()),
        "raw_candidate_evidence": raw,
    }


def compile_candidate_evidence(source_artifact: Dict[str, Any], request: Dict[str, Any],
                               registry_path: str | Path = DEFAULT_REGISTRY) -> Dict[str, Any]:
    reg = _load(registry_path)
    raw_field = parse_race_card(source_artifact)
    request = json.loads(json.dumps(request, ensure_ascii=False))
    request["_candidate_raw_field"] = raw_field
    req_runners = request.get("runners") or []
    if not req_runners:
        raise LocalCandidateEvidenceError("REQUEST_RUNNERS_REQUIRED")
    expected = {str(x.get("runner_id")): _norm(x.get("name")) for x in req_runners}
    actual = {rid: _norm(x.get("name")) for rid, x in raw_field.items()}
    if set(expected) != set(actual):
        raise LocalCandidateEvidenceError(f"RUNNER_UNIVERSE_MISMATCH:{sorted(expected)}!={sorted(actual)}")
    for rid in expected:
        if expected[rid] != actual[rid]:
            raise LocalCandidateEvidenceError(f"RUNNER_NAME_MISMATCH:{rid}:{expected[rid]}!={actual[rid]}")

    compiled = []
    field_size = len(raw_field)
    for r in req_runners:
        rid = str(r.get("runner_id"))
        c = _build_preliminary(raw_field[rid], request, source_artifact, reg, field_size)
        c["static_roles"] = list(r.get("static_roles") or [])
        compiled.append(c)

    # Cross-runner comparable-time percentile for NCI.class_relative_time.
    race = request.get("race") or {}
    current_distance = int(race.get("distance") or 0)
    best_times: Dict[str, float] = {}
    for c in compiled:
        times = []
        for run in c["raw_candidate_evidence"]["starts"]:
            if run.get("distance") == current_distance and run.get("content_time_seconds"):
                times.append(float(run["content_time_seconds"]))
        if times:
            best_times[c["runner_id"]] = min(times)
    if best_times:
        lo, hi = min(best_times.values()), max(best_times.values())
        for c in compiled:
            feat = c["evidence_features"]["class_relative_time"]
            if c["runner_id"] in best_times:
                v = best_times[c["runner_id"]]
                score = 70.0 if hi == lo else 40 + 50*(hi-v)/(hi-lo)
                feat["score"] = round(_clamp(score),6)
                feat["missing"] = False
                feat["coverage"] = 1.0
                feat["source_fact"] = f"field-relative best comparable {current_distance}m time={v}; range={lo}..{hi}"
                feat["raw_metric"] = v
                key = "NCI.class_relative_time"
                if key in c["candidate_missing_components"]:
                    c["candidate_missing_components"].remove(key)
                    c["candidate_missing_count"] -= 1

    for c in compiled:
        c["candidate_feature_coverage_ratio"] = round(
            1.0 - c["candidate_missing_count"]/max(1,c["candidate_component_count"]), 6
        )
        c["candidate_evidence_sha256"] = _sha(c["evidence_features"])

    request.pop("_candidate_raw_field", None)
    request["runners"] = compiled
    request["candidate_current_state"] = {
        "official_going": str(((source_artifact.get("normalized_evidence") or {}).get("track_condition") or {}).get("value") or ""),
        "official_weather": str(((source_artifact.get("normalized_evidence") or {}).get("weather") or {}).get("value") or ""),
        "source_freeze_at": source_artifact.get("source_freeze_at"),
        "source_snapshot_sha256": source_artifact.get("source_snapshot_sha256"),
    }
    request["candidate_evidence_compiler"] = {
        "profile": PROFILE,
        "registry_id": reg["registry_id"],
        "production_authority": False,
        "source_snapshot_sha256": source_artifact.get("source_snapshot_sha256"),
        "official_runner_universe_sha256": source_artifact.get("official_runner_universe_sha256"),
        "runner_count": len(compiled),
        "result_derived_features": 0,
    }
    request["candidate_evidence_compiler"]["sha256"] = _sha(request["candidate_evidence_compiler"])
    return request
