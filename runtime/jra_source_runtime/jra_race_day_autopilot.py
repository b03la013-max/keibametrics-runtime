"""Race-day autopilot: run EVERY JRA race of the day through the canonical
Formal pipeline at the right time, and publish a per-race status index.

Plan: runtime/jra_race_day_plan/<YYYY-MM-DD>.json. With ``"all_races": true``
(or when no plan file exists and --all-races-default is set) every race of every
venue on the OFFICIAL JRA calendar is planned. For each race whose official
post time is inside the dispatch window (default 55..30 minutes before post:
after official body weights, before the 5-minute cutoff) the canonical
km-jra-race-intent-resolver.yml is dispatched exactly once. Nothing is
predicted here and nothing is ever dispatched late.

Status index: runtime/jra_race_day_status/<date>.json (+ .md) lists, for every
race, its official post time and its real state: WAITING / DISPATCHED /
FINAL (with the 買い目 tree) / EVIDENCE_NO_BET (with the exact unclosed runner x
index cells) / MISSED_WINDOW / SETTLED. A chat or a person asking about
"競馬場 + R番号" reads this index instead of computing anything after cutoff.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import subprocess
import sys
import time
from pathlib import Path

from jra_race_day_resolver import JST, VENUES, resolve_day, resolve_meetings, venue_code

PROFILE = "KM-JRA-RACE-DAY-AUTOPILOT-v1.2-20261011"
DEFAULT_WINDOW = (55, 30)


def due(post: _dt.datetime, now: _dt.datetime, window=DEFAULT_WINDOW) -> str:
    lead = (post - now).total_seconds() / 60
    if lead > window[0]:
        return "WAIT"
    if lead < window[1]:
        return "MISSED_WINDOW"
    return "DISPATCH"


def plan_entries(plan: dict, race_date: str, *, meetings=resolve_meetings, resolve=resolve_day, days=None):
    days = {} if days is None else days
    if plan.get("all_races"):
        try:
            venues = meetings(race_date)
        except Exception as exc:  # report, never guess
            yield None, None, None, "OFFICIAL_CALENDAR_UNAVAILABLE:" + type(exc).__name__ + ":" + str(exc)[:160]
            return
        for v in venues:
            if v not in days:
                try:
                    days[v] = resolve(race_date, v)
                except Exception as exc:
                    days[v] = ValueError(type(exc).__name__ + ":" + str(exc))
            if isinstance(days[v], Exception):
                yield v, None, None, "OFFICIAL_CARD_UNAVAILABLE:" + str(days[v])[:200]
                continue
            for r in days[v][1]:
                yield v, int(r["race_no"]), int(plan.get("run_count") or 5000), None
        return
    for e in plan.get("entries") or []:
        races = e.get("races") or [e.get("race_no")]
        for r in races:
            yield str(e["venue"]), int(r), int(e.get("run_count") or plan.get("run_count") or 5000), None


def race_id_for(race_date: str, venue: str, race_no: int) -> str:
    vid = VENUES[venue_code(venue)][0]
    return f"KM-JRA-{vid}-{_dt.date.fromisoformat(race_date).strftime('%Y%m%d')}-R{race_no:02d}"


def tick(root: Path, race_date: str, now: _dt.datetime, *, resolve=resolve_day,
         meetings=resolve_meetings, dispatch=None, default_all=False, cache=None) -> list[dict]:
    plan_dir = root / "runtime" / "jra_race_day_plan"
    plan_path = plan_dir / f"{race_date}.json"
    if plan_path.exists():
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    elif default_all:
        plan = {"race_date": race_date, "all_races": True, "auto_generated": True}
    else:
        return []
    window = tuple(plan.get("dispatch_window_minutes_before_post") or DEFAULT_WINDOW)
    if not (window[0] > window[1] > 5):
        raise ValueError("AUTOPILOT_WINDOW_INVALID")
    plan_dir.mkdir(parents=True, exist_ok=True)
    state_path = plan_dir / f"{race_date}.state.json"
    schedule_path = plan_dir / f"{race_date}.schedule.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    schedule = json.loads(schedule_path.read_text(encoding="utf-8")) if schedule_path.exists() else {}
    # Official cards are cached across loop ticks (refreshed by the caller) so
    # the official site is not polled every tick.
    days: dict = cache.setdefault("days", {}) if cache is not None else {}
    if plan.get("all_races"):
        memo = cache if cache is not None else {}
        if "meetings" not in memo:
            try:
                memo["meetings"] = meetings(race_date)
            except Exception as exc:
                memo["meetings"] = exc
        cached = memo["meetings"]
        if isinstance(cached, (list, tuple)) and not cached:
            # Official calendar answered: no JRA meeting on this date. Nothing
            # to plan, dispatch or publish (no empty state/status files).
            return [{"race_id": race_date, "status": "NO_OFFICIAL_MEETINGS"}]
        def meetings(_d, _c=cached):
            if isinstance(_c, Exception):
                raise _c
            return _c
    out = []
    for venue, race_no, run_count, err in plan_entries(plan, race_date, meetings=meetings,
                                                       resolve=resolve, days=days):
        if err:
            key = f"{race_date}:{venue or 'ALL'}"
            schedule[key] = {"status": err}
            out.append({"race_id": key, "status": err})
            continue
        rid = race_id_for(race_date, venue, race_no)
        if venue not in days:
            try:
                days[venue] = resolve(race_date, venue)
            except Exception as exc:  # official card not available: report, never guess
                days[venue] = ValueError(type(exc).__name__ + ":" + str(exc))
        if isinstance(days[venue], Exception):
            out.append({"race_id": rid, "status": "OFFICIAL_CARD_UNAVAILABLE:" + str(days[venue])[:200]})
            schedule[rid] = {"status": out[-1]["status"]}
            continue
        race = next((r for r in days[venue][1] if r["race_no"] == race_no), None)
        if race is None:
            out.append({"race_id": rid, "status": "NOT_ON_OFFICIAL_CARD"})
            schedule[rid] = {"status": "NOT_ON_OFFICIAL_CARD"}
            continue
        hh, mm = map(int, race["post_time"].split(":"))
        d = _dt.date.fromisoformat(race_date)
        post = _dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=JST)
        schedule[rid] = {"post": post.isoformat(), "title": race.get("title"), "venue": venue,
                         "race_no": race_no, "official_day_row": race.get("raw"),
                         "dispatch_window_open": (post - _dt.timedelta(minutes=window[0])).isoformat(),
                         "dispatch_window_close": (post - _dt.timedelta(minutes=window[1])).isoformat()}
        if rid in state or list((root / "runtime" / "jra_formal_intents").glob(rid + "-LIVE-*.json")):
            out.append({"race_id": rid, "status": "ALREADY_DISPATCHED"})
            continue
        decision = due(post, now, window)
        if decision == "DISPATCH":
            (dispatch or _gh_dispatch)(venue, race_no, race_date, run_count)
            state[rid] = {"dispatched_at": now.isoformat(), "post": post.isoformat(), "profile": PROFILE}
        out.append({"race_id": rid, "post": post.isoformat(), "status": decision, "title": race.get("title")})
    schedule_path.write_text(json.dumps(schedule, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    write_status(root, race_date, now, schedule, state)
    return out


# --------------------------------------------------------------- status index
def _blocked_cells(gap: dict) -> list[str]:
    rows = ((gap.get("base_index_coverage_diagnostic") or {}).get("rows") or [])
    per: dict[str, list[str]] = {}
    for x in rows:
        if x.get("status") == "BLOCKED":
            per.setdefault(str(x.get("runner_id")), []).append(f"{x.get('index_id')}({x.get('profile')})")
    return [f"{rid}番:{'/'.join(v)}" for rid, v in sorted(per.items(), key=lambda z: int(z[0]) if z[0].isdigit() else 99)]


def race_status(root: Path, rid: str, sched: dict, state: dict, now: _dt.datetime) -> dict:
    row = {"race_id": rid, "post": sched.get("post"), "title": sched.get("title"),
           "venue": sched.get("venue"), "race_no": sched.get("race_no")}
    if sched.get("status"):
        row["state"] = sched["status"]
        return row
    intents = sorted(glob.glob(str(root / "runtime" / "jra_formal_intents" / (rid + "-LIVE-*.json"))))
    final_p = root / "runtime" / "final_artifacts" / (rid + ".json")
    result_p = root / "runtime" / "results" / (rid + ".json")
    eids = [Path(p).stem for p in intents]
    no_bet = [p for e in eids for p in glob.glob(str(root / "runtime" / "jra_no_bet_terminals" / (e + ".json")))]
    gaps = [p for e in eids for p in glob.glob(str(root / "runtime" / "exact_gaps" / (e + ".json")))]
    if final_p.exists():
        final = json.loads(final_p.read_text(encoding="utf-8"))
        row["state"] = "FINAL"
        row["final_receipt_sha256"] = final.get("final_receipt_sha256")
        row["immutable_final_sha256"] = final.get("sha256")
        try:
            from jra_ticket_tree_renderer import render_ticket_tree
            tree = render_ticket_tree(final)
            row["ticket_tree"] = tree["text"]
            row["ticket_count"] = tree["ticket_count"]
            row["total_investment"] = tree["total_investment"]
        except Exception as exc:
            row["ticket_tree_error"] = type(exc).__name__ + ":" + str(exc)
        try:
            sys.path.insert(0, str(root / "runtime"))
            from jra_aki_reference import aki_reference
            ref = aki_reference(root, rid)
            if ref:
                row["aki_reference"] = ref
        except Exception as exc:
            row["aki_reference_error"] = type(exc).__name__ + ":" + str(exc)
        if result_p.exists():
            res = json.loads(result_p.read_text(encoding="utf-8"))
            st = res.get("settlement") or {}
            row["state"] = ("SETTLED_SIGNED_RESULT_LEARNED"
                            if (root / "runtime" / "learning_states" / (rid + ".json")).exists() else "SETTLED")
            row["official_top3"] = (res.get("official_result") or {}).get("top3")
            row["settlement"] = {k: st.get(k) for k in ("total_investment", "total_payout", "profit_loss", "actual_purchase_status")}
    elif no_bet:
        row["state"] = "EVIDENCE_NO_BET"
        row["no_bet_terminal"] = Path(no_bet[-1]).relative_to(root).as_posix()
        if gaps:
            gap = json.loads(Path(gaps[-1]).read_text(encoding="utf-8"))
            row["full20"] = f"{gap.get('verified_full_index_count')}/{gap.get('required_index_count')}"
            row["unclosed_cells"] = _blocked_cells(gap)
    elif gaps:
        gap = json.loads(Path(gaps[-1]).read_text(encoding="utf-8"))
        row["state"] = "PRODUCTION_BLOCKED"
        row["first_blocked_stage"] = gap.get("first_blocked_stage")
        row["full20"] = f"{gap.get('verified_full_index_count')}/{gap.get('required_index_count')}"
        row["unclosed_cells"] = _blocked_cells(gap)
    elif eids or rid in state:
        row["state"] = "DISPATCHED_RUNNING"
        row["dispatched_at"] = (state.get(rid) or {}).get("dispatched_at")
    else:
        post = _dt.datetime.fromisoformat(sched["post"]) if sched.get("post") else None
        close = _dt.datetime.fromisoformat(sched["dispatch_window_close"]) if sched.get("dispatch_window_close") else None
        row["state"] = ("MISSED_WINDOW" if close and now > close else "WAITING")
        row["dispatch_window_open"] = sched.get("dispatch_window_open")
    return row


def write_status(root: Path, race_date: str, now: _dt.datetime, schedule: dict, state: dict) -> dict:
    rows = [race_status(root, rid, s, state, now) for rid, s in schedule.items()]
    rows.sort(key=lambda r: (r.get("post") or "", r["race_id"]))
    idx = {"profile": PROFILE, "race_date": race_date, "races": rows,
           "how_to_read": "Each race is run automatically 55-30 min before its official post. FINAL = signed pre-race "
                          "Production FINAL with the 買い目 tree; EVIDENCE_NO_BET = verified zero-exposure terminal "
                          "because some runner x index cells could not be closed from official evidence; "
                          "MISSED_WINDOW = never predicted (no late or backdated FINAL)."}
    d = root / "runtime" / "jra_race_day_status"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{race_date}.json").write_text(json.dumps(idx, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    md = [f"# JRA {race_date} 全レース状況", ""]
    for r in rows:
        head = f"## {r.get('venue') or ''}{r.get('race_no') or ''}R {r.get('title') or ''} ({(r.get('post') or '')[11:16]}) — {r.get('state')}"
        md.append(head)
        if r.get("ticket_tree"):
            md += ["```", r["ticket_tree"], "```"]
        if (r.get("aki_reference") or {}).get("tree"):
            md += ["```", r["aki_reference"]["tree"], "```"]
        if r.get("unclosed_cells"):
            md.append(f"Full20 {r.get('full20')} 未成立: " + "、".join(r["unclosed_cells"]))
        if r.get("settlement"):
            md.append(f"結果 {r.get('official_top3')} 精算 {r['settlement']}")
        md.append("")
    (d / f"{race_date}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return idx


def _gh_dispatch(venue, race_no, race_date, run_count):
    subprocess.run(["gh", "workflow", "run", "km-jra-race-intent-resolver.yml", "--ref", "main",
                    "-f", f"venue={venue}", "-f", f"race_no={race_no}", "-f", f"race_date={race_date}",
                    "-f", f"run_count={run_count}"], check=True)


def _post_result_closed_loop(root: Path, race_date: str) -> None:
    """Settle due Production FINALs (official result) and hand each RESULT
    request to the canonical Result Runner exactly once, only after the request
    is published on main. Scheduled cron alone proved unreliable, so the day
    loop drives it; idempotent per race (state: <date>.state.json)."""
    run = lambda *a: subprocess.run(list(a), cwd=root, text=True, capture_output=True)
    r = run(sys.executable, "runtime/jra_production_postresult.py", "--days", "1")
    print(r.stdout.strip()[-2000:], flush=True)
    d8 = _dt.date.fromisoformat(race_date).strftime("%Y%m%d")
    new = [x for x in run("git", "ls-files", "--others", "--exclude-standard",
                          "runtime/results").stdout.split() if x.startswith("runtime/results/KM-JRA-")]
    if new:
        run("git", "add", *new)
        run("git", "commit", "-m", "result: JRA Production official result request [skip ci]")
    pushed = False
    for i in range(5):
        if run("git", "pull", "--rebase", "--autostash", "origin", "main").returncode == 0 and \
                run("git", "push", "origin", "HEAD:main").returncode == 0:
            pushed = True
            break
        run("git", "rebase", "--abort")
        time.sleep(3 * (i + 1))
    if not pushed:
        return  # retried next tick; never dispatch an unpublished request
    state_path = root / "runtime" / "jra_race_day_plan" / f"{race_date}.state.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    done = set(state.get("_result_runner_dispatched") or [])
    published = sorted(Path(p).relative_to(root).as_posix() for p in
                       glob.glob(str(root / "runtime" / "results" / f"KM-JRA-*-{d8}-R*.json")))
    for path in published:
        rid = Path(path).stem
        if path in done or (root / "runtime" / "learning_states" / f"{rid}.json").exists():
            done.add(path)  # Result Runner already completed (learning state persisted)
            continue
        if run("gh", "workflow", "run", "km-formal-result-runner.yml", "--ref", "main",
               "-f", f"request_path={path}").returncode == 0:
            done.add(path)
    state["_result_runner_dispatched"] = sorted(done)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def _commit(root: Path, race_date: str) -> None:
    paths = [f"runtime/jra_race_day_plan/{race_date}.state.json", f"runtime/jra_race_day_plan/{race_date}.schedule.json",
             f"runtime/jra_race_day_status/{race_date}.json", f"runtime/jra_race_day_status/{race_date}.md"]
    run = lambda *a: subprocess.run(list(a), cwd=root, text=True, capture_output=True)
    run("git", "add", *paths)
    if run("git", "diff", "--cached", "--quiet").returncode == 0:
        return
    run("git", "commit", "-m", f"autopilot: race-day state and status {race_date} [skip ci]")
    for i in range(5):
        if run("git", "pull", "--rebase", "--autostash", "origin", "main").returncode == 0 and \
                run("git", "push", "origin", "HEAD:main").returncode == 0:
            return
        run("git", "rebase", "--abort")
        time.sleep(3 * (i + 1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default="../..")
    ap.add_argument("--date", default=_dt.datetime.now(JST).date().isoformat())
    ap.add_argument("--all-races-default", action="store_true",
                    help="plan every official race when no plan file exists for the date")
    ap.add_argument("--loop-until", help="HH:MM JST; tick every --interval seconds until then, committing state")
    ap.add_argument("--interval", type=int, default=120)
    a = ap.parse_args()
    root = Path(a.repo_root).resolve()
    cache: dict = {}
    cache_at = None
    while True:
        now = _dt.datetime.now(JST)
        if a.loop_until:
            subprocess.run(["git", "pull", "--rebase", "--autostash", "-q", "origin", "main"], cwd=root, capture_output=True)
        if cache_at is None or (now - cache_at).total_seconds() > 1800 or any(
                isinstance(v, Exception) for v in list(cache.get("days", {}).values()) + [cache.get("meetings")]):
            cache, cache_at = {}, now
        try:
            res = tick(root, a.date, now, default_all=a.all_races_default, cache=cache)
            print(json.dumps({"profile": PROFILE, "date": a.date, "at": now.isoformat(), "races": res}, ensure_ascii=False), flush=True)
            if [r.get("status") for r in res] == ["NO_OFFICIAL_MEETINGS"]:
                break  # non-race day: stop at once instead of idling until the loop end
        except Exception as exc:  # keep the day running; the index shows the last good state
            print(json.dumps({"profile": PROFILE, "error": type(exc).__name__ + ":" + str(exc)}, ensure_ascii=False), flush=True)
        if a.loop_until:
            _post_result_closed_loop(root, a.date)
        if not a.loop_until:
            break
        _commit(root, a.date)
        hh, mm = map(int, a.loop_until.split(":"))
        if now >= now.replace(hour=hh, minute=mm, second=0, microsecond=0):
            break
        time.sleep(max(30, a.interval))
