"""Race-day autopilot: dispatch the official resolver at the right time.

A plan file (runtime/jra_race_day_plan/<YYYY-MM-DD>.json) lists venue + race
numbers. On each scheduled tick this resolves the OFFICIAL JRA post times and,
for every planned race whose post time is inside the dispatch window (default
65..35 minutes before post: after official body weights, before the cutoff),
dispatches km-jra-race-intent-resolver.yml exactly once. It never builds a
prediction itself and never dispatches after the window (no late freeze).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import subprocess
from pathlib import Path

from jra_race_day_resolver import JST, VENUES, resolve_day, venue_code

PROFILE = "KM-JRA-RACE-DAY-AUTOPILOT-v1.0-20261011"


def due(post: _dt.datetime, now: _dt.datetime, window=(65, 35)) -> str:
    lead = (post - now).total_seconds() / 60
    if lead > window[0]:
        return "WAIT"
    if lead < window[1]:
        return "MISSED_WINDOW"
    return "DISPATCH"


def plan_entries(plan: dict):
    for e in plan.get("entries") or []:
        races = e.get("races") or [e.get("race_no")]
        for r in races:
            yield str(e["venue"]), int(r), int(e.get("run_count") or plan.get("run_count") or 5000)


def race_id_for(race_date: str, venue: str, race_no: int) -> str:
    vid = VENUES[venue_code(venue)][0]
    return f"KM-JRA-{vid}-{_dt.date.fromisoformat(race_date).strftime('%Y%m%d')}-R{race_no:02d}"


def tick(root: Path, race_date: str, now: _dt.datetime, *, resolve=resolve_day, dispatch=None) -> list[dict]:
    plan_path = root / "runtime" / "jra_race_day_plan" / f"{race_date}.json"
    if not plan_path.exists():
        return []
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    window = tuple(plan.get("dispatch_window_minutes_before_post") or (65, 35))
    if not (window[0] > window[1] > 5):
        raise ValueError("AUTOPILOT_WINDOW_INVALID")
    state_path = plan_path.with_suffix(".state.json")
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    days = {}
    out = []
    for venue, race_no, run_count in plan_entries(plan):
        rid = race_id_for(race_date, venue, race_no)
        if rid in state or list((root / "runtime" / "jra_formal_intents").glob(rid + "-LIVE-*.json")):
            out.append({"race_id": rid, "status": "ALREADY_DISPATCHED"})
            continue
        if venue not in days:
            try:
                days[venue] = resolve(race_date, venue)
            except Exception as exc:  # official card not available: report, never guess
                days[venue] = exc
        if isinstance(days[venue], Exception):
            out.append({"race_id": rid, "status": "OFFICIAL_CARD_UNAVAILABLE:" + str(days[venue])[:120]})
            continue
        _, races = days[venue]
        race = next((r for r in races if r["race_no"] == race_no), None)
        if race is None:
            out.append({"race_id": rid, "status": "NOT_ON_OFFICIAL_CARD"})
            continue
        hh, mm = map(int, race["post_time"].split(":"))
        d = _dt.date.fromisoformat(race_date)
        post = _dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=JST)
        decision = due(post, now, window)
        row = {"race_id": rid, "post": post.isoformat(), "status": decision, "title": race.get("title")}
        if decision == "DISPATCH":
            (dispatch or _gh_dispatch)(venue, race_no, race_date, run_count)
            state[rid] = {"dispatched_at": now.isoformat(), "post": post.isoformat(), "profile": PROFILE}
        out.append(row)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return out


def _gh_dispatch(venue, race_no, race_date, run_count):
    subprocess.run(["gh", "workflow", "run", "km-jra-race-intent-resolver.yml", "--ref", "main",
                    "-f", f"venue={venue}", "-f", f"race_no={race_no}", "-f", f"race_date={race_date}",
                    "-f", f"run_count={run_count}"], check=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default="../..")
    ap.add_argument("--date", default=_dt.datetime.now(JST).date().isoformat())
    a = ap.parse_args()
    res = tick(Path(a.repo_root).resolve(), a.date, _dt.datetime.now(JST))
    print(json.dumps({"profile": PROFILE, "date": a.date, "races": res}, ensure_ascii=False))
