"""Night-before SOURCE dry run for one JRA race day (diagnostic only).

Runs the existing ``app.source_acquire`` for every flat race of one venue on
the official card, with an ephemeral in-memory key.  Nothing is signed for
Production, persisted to the execution store, committed, or dispatched.  The
output only answers: would today's SOURCE code accept tomorrow's official
cards (runner universe, PDF/detail agreement, identity), and which errors are
expected to clear on race morning (body weight, odds, same-day fields).
"""
import argparse
import base64
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))


def _ephemeral_key():
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    raw = Ed25519PrivateKey.generate().private_bytes(
        serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
    os.environ["KM_JRA_SOURCE_PRIVATE_KEY_B64"] = base64.b64encode(raw).decode()
    os.environ["KM_JRA_SOURCE_SIGNER_KEY_ID"] = "KM-JRA-SOURCE-PREFLIGHT-DRYRUN-NOT-PRODUCTION"


def run(race_date, venue, pause=2.0):
    _ephemeral_key()
    from jra_race_day_resolver import JST, VENUES, official_jump_race, resolve_day, venue_code
    import app as japp
    vid = VENUES[venue_code(venue)][0]
    meeting_key, rows = resolve_day(race_date, venue)
    d = dt.date.fromisoformat(race_date)
    out = {"race_date": race_date, "venue": venue, "venue_id": vid, "meeting_key": meeting_key,
           "official_rows": len(rows), "classification": "PREFLIGHT_DRYRUN_NOT_PRODUCTION", "races": []}
    for race in rows:
        no = int(race["race_no"])
        rid = f"KM-JRA-{vid}-{d.strftime('%Y%m%d')}-R{no:02d}"
        hh, mm = map(int, race["post_time"].split(":"))
        post = dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=JST)
        row = {"race_id": rid, "race_no": no, "post": post.isoformat(), "title": race.get("title")}
        if official_jump_race(race):
            row["scope"] = "SCOPE_HOLD_JUMP"
            out["races"].append(row)
            continue
        req = {"execution_id": rid + "-PREFLIGHT", "family_id": "JRA", "jra_meeting_key": meeting_key,
               "prediction_cutoff": (post - dt.timedelta(minutes=5)).isoformat(),
               "external_dispatch_deadline_at": (post - dt.timedelta(minutes=2)).isoformat(),
               "scheduled_post_at": post.isoformat(), "race_date": race_date, "race_id": rid,
               "race_no": no, "temporal_mode": "FORMAL-PRE-RACE", "venue_id": vid,
               "require_jma_weather": False, "require_jra_horse_history": False,
               "require_jra_person_stats": False, "require_jra_race_card_detail": False,
               "require_registered_common_workout": False, "require_tsl_shadow": False}
        started = time.monotonic()
        try:
            env = japp.source_acquire(req)
            art = env.get("artifact") or {}
            receipt = env.get("receipt") or {}
            universe = art.get("jra_official_runner_universe") or {}
            row.update(scope="FLAT", receipt_status=receipt.get("status"),
                       receipt_errors=[str(e)[:400] for e in (receipt.get("errors") or [])],
                       artifact_errors=[str(e)[:400] for e in (art.get("errors") or [])],
                       warnings=[str(w)[:300] for w in (art.get("warnings") or [])][:12],
                       formal_ready=art.get("formal_ready"),
                       runner_count=universe.get("runner_count"),
                       universe_source=universe.get("source") or universe.get("authority"))
        except Exception as exc:  # report, never hide
            row.update(scope="FLAT", receipt_status="EXCEPTION",
                       exception=type(exc).__name__ + ":" + str(exc)[:600])
        row["seconds"] = round(time.monotonic() - started, 1)
        out["races"].append(row)
        print("PREFLIGHT_RACE " + json.dumps(row, ensure_ascii=False), flush=True)
        time.sleep(pause)
    return out


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--date", required=True)
    p.add_argument("--venue", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args(argv)
    out = run(a.date, a.venue)
    Path(a.output).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    flat = [r for r in out["races"] if r.get("scope") == "FLAT"]
    print("PREFLIGHT_SUMMARY " + json.dumps({
        "venue": a.venue, "official_rows": out["official_rows"], "flat": len(flat),
        "jump": len(out["races"]) - len(flat),
        "pass": sum(r.get("receipt_status") == "PASS" for r in flat),
        "formal_ready": sum(r.get("formal_ready") is True for r in flat)}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
