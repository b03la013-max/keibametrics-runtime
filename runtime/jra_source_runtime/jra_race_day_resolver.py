"""Resolve "venue + race number (+ date)" into an official JRA Formal intent.

Uses only the official JRA race-card navigation (calendar -> day -> race list)
to obtain the 10-digit meeting key, the official post time, class, course and
field size. The intent's cutoff and dispatch deadline are derived from the
official post time; nothing is guessed when the official page does not list
the race (fail closed).
"""
from __future__ import annotations

import datetime as _dt
import re
from typing import Any, Dict, List

PROFILE = "KM-JRA-OFFICIAL-RACE-DAY-RESOLVER-v1.0-20261010"
JST = _dt.timezone(_dt.timedelta(hours=9))
VENUES = {  # official JRA course code -> (canonical venue_id, name)
    "01": ("SPP", "札幌"), "02": ("HKD", "函館"), "03": ("FKS", "福島"), "04": ("NGT", "新潟"),
    "05": ("TKY", "東京"), "06": ("NKY", "中山"), "07": ("CHK", "中京"), "08": ("KYO", "京都"),
    "09": ("HSN", "阪神"), "10": ("KKR", "小倉"),
}
NAME_TO_CODE = {name: code for code, (_, name) in VENUES.items()}
ID_TO_CODE = {vid: code for code, (vid, _) in VENUES.items()}


def venue_code(venue: str) -> str:
    v = str(venue or "").strip().replace("競馬場", "")
    code = NAME_TO_CODE.get(v) or ID_TO_CODE.get(v.upper())
    if not code:
        raise ValueError("JRA_VENUE_UNKNOWN:" + v)
    return code


def parse_day_rows(day_html_text_rows: List[str]) -> List[Dict[str, Any]]:
    """Parse the official day race list rows (in race-number order)."""
    races = []
    for row in day_html_text_rows:
        t = re.sub(r"\s+", " ", str(row or "")).strip()
        m = re.search(r"(\d{1,2})時(\d{2})分", t)
        if not m or "頭" not in t:
            continue
        course = re.search(r"(芝→ダート|ダート→芝|芝|ダート|障害)\s*([\d,]+)m\s*(\d+)頭", t)
        races.append({
            "post_time": f"{int(m.group(1)):02d}:{m.group(2)}",
            "surface": None if not course else ("ダ" if course.group(1) == "ダート" else
                                                "芝" if course.group(1) == "芝" else course.group(1)),
            "distance_m": None if not course else int(course.group(2).replace(",", "")),
            "field_size": None if not course else int(course.group(3)),
            "title": t[m.end():(course.start() if course else len(t))].strip(),
            "raw": t,
        })
    for i, r in enumerate(races, 1):
        r["race_no"] = i
    return races


def build_intent(*, race_date: str, venue: str, race_no: int, meeting_key: str, race: Dict[str, Any],
                 cutoff_minutes: int = 5, dispatch_minutes: int = 2, run_count: int = 5000,
                 revision: int = 1) -> Dict[str, Any]:
    code = venue_code(venue)
    vid, vname = VENUES[code]
    if not re.fullmatch(code + r"\d{8}", str(meeting_key)):
        raise ValueError("JRA_MEETING_KEY_VENUE_MISMATCH")
    if int(race.get("race_no") or 0) != int(race_no):
        raise ValueError("JRA_RACE_NO_MISMATCH")
    hh, mm = map(int, str(race["post_time"]).split(":"))
    day = _dt.date.fromisoformat(race_date)
    post = _dt.datetime(day.year, day.month, day.day, hh, mm, tzinfo=JST)
    cutoff = post - _dt.timedelta(minutes=cutoff_minutes)
    dispatch = post - _dt.timedelta(minutes=dispatch_minutes)
    if not cutoff < dispatch < post:
        raise ValueError("JRA_INTENT_TIME_ORDER_INVALID")
    d8 = day.strftime("%Y%m%d")
    race_id = f"KM-JRA-{vid}-{d8}-R{int(race_no):02d}"
    return {
        "family_id": "JRA",
        "execution_id": f"{race_id}-LIVE-R{int(revision)}",
        "race_id": race_id,
        "venue_id": vid,
        "race_date": race_date,
        "race_no": int(race_no),
        "temporal_mode": "FORMAL-PRE-RACE",
        "prediction_cutoff": cutoff.isoformat(),
        "scheduled_post_at": post.isoformat(),
        "external_dispatch_deadline_at": dispatch.isoformat(),
        "jra_source": {"jra_meeting_key": str(meeting_key)},
        "race": {"race_id": race_id, "venue": vname, "race_name": race.get("title"),
                 "surface": race.get("surface"), "distance": race.get("distance_m"),
                 "field_size_declared": race.get("field_size")},
        "run_count": int(run_count),
        "seed": int(d8) * 100 + int(race_no),
        "acceptance_only": False,
        "intent_resolver": {"profile": PROFILE, "official_day_row": race.get("raw"),
                            "cutoff_minutes_before_post": cutoff_minutes,
                            "dispatch_minutes_before_post": dispatch_minutes},
    }


def resolve_and_build(race_date: str, venue: str, race_no: int, **kw) -> Dict[str, Any]:
    """Network path (official JRA only); used by the resolver workflow."""
    from jra_pedigree_harvest import _Client, _calendar
    from source_acquisition import _html_tables
    code = venue_code(venue)
    d8 = _dt.date.fromisoformat(race_date).strftime("%Y%m%d")
    c = _Client(delay=0.3)
    cal = c.get(_calendar(race_date))
    m = re.search(r"doAction\('/JRADB/accessD\.html'\s*,\s*'([^']+)'\)", cal)
    if not m:
        raise ValueError("JRA_RESOLVER_ENTRY_TOKEN_NOT_FOUND")
    s1 = c.post("/JRADB/accessD.html", m.group(1))
    days = re.findall(r"pw01drl00(" + code + r"\d{8})" + d8 + r"/[0-9A-Fa-f]{2}", s1)
    if len(set(days)) != 1:
        raise ValueError("JRA_RESOLVER_MEETING_NOT_UNIQUE:" + ",".join(sorted(set(days))))
    key = days[0]
    tok = re.search(r"pw01drl00" + key + d8 + r"/[0-9A-Fa-f]{2}", s1).group(0)
    s2 = c.post("/JRADB/accessD.html", tok)
    rows = [" ".join(str(x) for x in row) for t in _html_tables(s2) for row in t]
    races = parse_day_rows(rows)
    toks = set(re.findall(r"pw01dde01" + key + r"(\d{2})" + d8, s2))
    if len(races) != len(toks):
        raise ValueError(f"JRA_RESOLVER_RACE_LIST_MISMATCH:{len(races)}!={len(toks)}")
    race = next((r for r in races if r["race_no"] == int(race_no)), None)
    if race is None:
        raise ValueError("JRA_RESOLVER_RACE_NOT_FOUND")
    return build_intent(race_date=race_date, venue=venue, race_no=race_no, meeting_key=key, race=race, **kw)


if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--venue", required=True)
    ap.add_argument("--race", type=int, required=True)
    ap.add_argument("--run-count", type=int, default=5000)
    ap.add_argument("--revision", type=int, default=1)
    ap.add_argument("--out-dir", default="runtime/jra_formal_intents")
    a = ap.parse_args()
    intent = resolve_and_build(a.date, a.venue, a.race, run_count=a.run_count, revision=a.revision)
    p = Path(a.out_dir) / (intent["execution_id"] + ".json")
    if p.exists():
        raise SystemExit("INTENT_ALREADY_EXISTS:" + str(p))
    p.write_text(json.dumps(intent, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(intent, ensure_ascii=False))
