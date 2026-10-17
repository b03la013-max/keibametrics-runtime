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
import time
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
                 revision: int = 1, orchestration_session_id: str | None = None) -> Dict[str, Any]:
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
    intent = {
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
    if orchestration_session_id:
        # Same orchestration-reference contract the Candidate lane uses; the
        # session id names the real GitHub Actions run that resolved the race.
        intent["orchestration_ref"] = {
            "authority": "BASE44",
            "execution_session_id": str(orchestration_session_id),
            "session_nonce": f"{intent['execution_id']}:{orchestration_session_id}",
            "created_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "issuer": "km-jra-race-intent-resolver / GitHub Actions",
        }
    return intent


def resolve_meetings(race_date: str) -> List[str]:
    """Official JRA venues (canonical names) holding races on race_date."""
    from jra_pedigree_harvest import _Client, _calendar
    d8 = _dt.date.fromisoformat(race_date).strftime("%Y%m%d")
    c = _Client(delay=1.0)
    c.deadline_monotonic = time.monotonic() + 180
    cal = c.get(_calendar(race_date))
    m = re.search(r"doAction\('/JRADB/accessD\.html'\s*,\s*'([^']+)'\)", cal)
    if not m:
        raise ValueError("JRA_RESOLVER_ENTRY_TOKEN_NOT_FOUND")
    s1 = c.post("/JRADB/accessD.html", m.group(1))
    codes = sorted(set(re.findall(r"pw01drl00(\d{2})\d{8}" + d8 + r"/[0-9A-Fa-f]{2}", s1)))
    return [VENUES[c_][1] for c_ in codes if c_ in VENUES]


def resolve_day(race_date: str, venue: str, *, deadline_monotonic=None):
    """Official JRA day race list for one venue: (meeting_key, races)."""
    from jra_pedigree_harvest import _Client, _calendar
    from source_acquisition import _html_tables
    code = venue_code(venue)
    d8 = _dt.date.fromisoformat(race_date).strftime("%Y%m%d")
    c = _Client(delay=1.0)
    c.deadline_monotonic = deadline_monotonic or time.monotonic() + 180
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
    return key, races


def resolve_and_build(race_date: str, venue: str, race_no: int, **kw) -> Dict[str, Any]:
    """Network path (official JRA only); used by the resolver workflow."""
    deadline = kw.pop("deadline_monotonic", None)
    key, races = resolve_day(race_date, venue, **({"deadline_monotonic": deadline} if deadline is not None else {}))
    race = next((r for r in races if r["race_no"] == int(race_no)), None)
    if race is None:
        raise ValueError("JRA_RESOLVER_RACE_NOT_FOUND")
    return build_intent(race_date=race_date, venue=venue, race_no=race_no, meeting_key=key, race=race, **kw)


def execute(a, deadline_monotonic):
    import json
    from pathlib import Path
    intent = resolve_and_build(a.date, a.venue, a.race, run_count=a.run_count, revision=a.revision,
                               orchestration_session_id=a.orchestration_session_id, deadline_monotonic=deadline_monotonic)
    # A Formal pre-race prediction needs SOURCE + Full20 + KRS + MEC + signed
    # FINAL before the cutoff. Too close to post: no intent, no error, and no
    # late or backdated FINAL; the day's status index holds the real state.
    post_at = _dt.datetime.fromisoformat(intent["scheduled_post_at"])
    lead = (post_at - _dt.datetime.now(JST)).total_seconds() / 60
    if lead < a.min_lead_minutes:
        print(json.dumps({"status": "TOO_LATE_FOR_PRE_RACE_FINAL", "race_id": intent["race_id"],
                          "scheduled_post_at": intent["scheduled_post_at"],
                          "minutes_to_post": round(lead, 1), "required_minutes": a.min_lead_minutes,
                          "status_index": f"runtime/jra_race_day_status/{a.date}.json"}, ensure_ascii=False))
        raise SystemExit(0)
    # Bind the intent to the Current Authority in force at resolution time:
    # every downstream lane (Production Formal, Candidate Parallel) refuses a
    # request that does not declare the current manifest.
    import sys as _sys
    _root = Path(__file__).resolve().parents[2]
    _sys.path.insert(0, str(_root / "runtime"))
    from family_authority_guard import resolve_current_authority
    _, _current = resolve_current_authority(root=_root, now=_dt.datetime.now(_dt.timezone.utc))
    intent["current_authority_manifest"] = _current["manifest_id"]
    p = Path(a.out_dir) / (intent["execution_id"] + ".json")
    if p.exists():
        raise SystemExit("INTENT_ALREADY_EXISTS:" + str(p))
    p.write_text(json.dumps(intent, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(intent, ensure_ascii=False))


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
    ap.add_argument("--orchestration-session-id")
    ap.add_argument("--min-lead-minutes", type=float, default=15.0)
    a = ap.parse_args()
    import os
    import sys
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / "runtime"))
    rid = f"KM-JRA-{VENUES[venue_code(a.venue)][0]}-{_dt.date.fromisoformat(a.date).strftime('%Y%m%d')}-R{a.race:02d}"
    if not 1 <= a.race <= 12:
        raise ValueError("JRA_RACE_NO_INVALID")
    # A previously observed official schedule can only shorten the 180s
    # resolver budget; it cannot authorize an intent or replace fresh resolve.
    retry_deadline = None
    schedule_path = root / "runtime/jra_race_day_plan" / (a.date + ".schedule.json")
    if schedule_path.exists():
        schedule = json.loads(schedule_path.read_text()).get(rid) or {}
        if schedule.get("post"):
            post = _dt.datetime.fromisoformat(schedule["post"])
            if post.tzinfo is None or post.astimezone(JST).date().isoformat() != a.date:
                raise ValueError("JRA_RESOLVER_SCHEDULE_TIME_INVALID")
            retry_deadline = post - _dt.timedelta(minutes=a.min_lead_minutes)
    budget = min(180, (retry_deadline - _dt.datetime.now(JST)).total_seconds()) if retry_deadline else 180
    try:
        if budget <= 0:
            from jra_pedigree_harvest import OfficialDeadlineExceeded
            raise OfficialDeadlineExceeded("JRA_RESOLVER_INTAKE_DEADLINE")
        # Linux Actions wall-clock guard also interrupts DNS/TLS/body calls;
        # socket timeouts alone do not bound DNS or a slowly streaming body.
        import signal
        from jra_pedigree_harvest import OfficialDeadlineExceeded
        def expired(*_):
            raise OfficialDeadlineExceeded("JRA_RESOLVER_OVERALL_DEADLINE")
        previous = signal.signal(signal.SIGALRM, expired)
        signal.setitimer(signal.ITIMER_REAL, budget)
        try:
            execute(a, time.monotonic() + budget)
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous)
    except Exception as exc:
        from jra_pedigree_harvest import retryable_official_error
        from jra_single_entry_outcome import record_formal_failure
        import traceback
        observed = _dt.datetime.now(JST)
        eligible = retry_deadline is not None and observed < retry_deadline
        failure = {
            "run_id": os.environ.get("GITHUB_RUN_ID", "0"),
            "workflow_run_id": os.environ.get("GITHUB_RUN_ID", "0"),
            "run_attempt": int(os.environ.get("GITHUB_RUN_ATTEMPT", "1")),
            "first_failed_stage": "RESOLVE_OFFICIAL_RACE_AND_BUILD_INTENT",
            "failure_owner": "JRA_OFFICIAL_RACE_RESOLVER",
            "exception_class": type(exc).__name__, "error": str(exc)[:2000],
            "official_request": getattr(exc, "official_request", None),
            "traceback": traceback.format_exc()[-12000:],
            "retryable": retryable_official_error(exc),
            "retry_deadline": retry_deadline.isoformat() if retry_deadline else None,
            "temporal_eligibility": eligible,
            "last_attempt_at": observed.isoformat(), "status_updated_at": observed.isoformat(),
            "terminal_state": ("RESOLVER_FAILED" if eligible or retry_deadline is None
                               else "RESOLVER_DEADLINE_EXCEEDED"),
            "conclusion": "failure", "exit_code": 1,
            "run_url": "https://github.com/" + os.environ.get("GITHUB_REPOSITORY", "b03la013-max/keibametrics-runtime") + "/actions/runs/" + os.environ.get("GITHUB_RUN_ID", "0"),
        }
        record_formal_failure(root, {"family_id": "JRA", "race_id": rid,
                              "execution_id": f"{rid}-LIVE-R{a.revision}"}, failure)
        raise
