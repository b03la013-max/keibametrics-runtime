"""Minimal authenticated LOCAL race-key intake; transport only, no prediction synthesis.

Used by workflow_dispatch/repository_dispatch. The official signed SOURCE supplies
the runner universe; a separate already-frozen canonical Static is required for
FORMAL. No result-informed historical intent is created.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import re
import subprocess
import os

from runtime.family_authority_guard import resolve_current_authority
from runtime.local_physical.nar_source_manifest import VENUE_NAMES

JST = timezone(timedelta(hours=9))
VENUE = re.compile(r"[A-Z]{3}")
DAY = re.compile(r"\d{4}-\d{2}-\d{2}")


class IntakeError(ValueError):
    pass


def aware(value: object, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise IntakeError(label + "_INVALID") from exc
    if parsed.tzinfo is None:
        raise IntakeError(label + "_TIMEZONE_REQUIRED")
    if parsed.utcoffset() != timedelta(hours=9):
        raise IntakeError(label + "_JST_REQUIRED")
    return parsed


def build(fields: dict, *, now: datetime | None = None, authority_resolver=None) -> dict:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise IntakeError("NOW_TIMEZONE_REQUIRED")
    venue = str(fields.get("venue_id") or "").strip()
    if not VENUE.fullmatch(venue) or venue not in VENUE_NAMES:
        raise IntakeError("LOCAL_VENUE_NOT_SUPPORTED")
    day_raw = str(fields.get("race_date") or "").strip()
    if not DAY.fullmatch(day_raw):
        raise IntakeError("RACE_DATE_INVALID")
    try:
        day = date.fromisoformat(day_raw)
    except ValueError as exc:
        raise IntakeError("RACE_DATE_INVALID") from exc
    race_raw = str(fields.get("race_no") or "").strip()
    if not re.fullmatch(r"(?:[1-9]|1[0-2])", race_raw):
        raise IntakeError("RACE_NO_INVALID")
    race_no = int(race_raw)
    post = aware(fields.get("scheduled_post_at"), "SCHEDULED_POST")
    cutoff = aware(fields.get("prediction_cutoff"), "PREDICTION_CUTOFF")
    if post.date() != day or cutoff.date() != day:
        raise IntakeError("RACE_DATE_AND_POST_MISMATCH")
    if cutoff >= post:
        raise IntakeError("CUTOFF_NOT_BEFORE_POST")
    if now.astimezone(timezone.utc) >= cutoff.astimezone(timezone.utc):
        raise IntakeError("SOURCE_CUTOFF_EXPIRED")
    deadline = post - timedelta(seconds=120)
    if now.astimezone(timezone.utc) >= deadline.astimezone(timezone.utc):
        raise IntakeError("RELEASE_DEADLINE_EXPIRED")
    get_authority = authority_resolver or resolve_current_authority
    _, canon = get_authority(now=now)
    manifest = str(canon.get("manifest_id") or "").strip()
    if not manifest or "CURRENT-AUTHORITY" not in str(canon.get("status") or ""):
        raise IntakeError("CURRENT_AUTHORITY_NOT_ACTIVE")
    eid = f"KM-LOCAL-{venue}-{day:%Y%m%d}-R{race_no:02d}-LIVE-R1"
    # Transport metadata, not a Static Prediction or bet placement.
    return {
        "family_id": "LOCAL",
        "race_id": eid,
        "execution_id": eid,
        "execution_phase": "SOURCE",
        "analysis_only": False,
        "temporal_mode": "FORMAL-PRE-RACE",
        "venue_id": venue,
        "race_date": day.isoformat(),
        "race_no": race_no,
        "prediction_cutoff": cutoff.isoformat(),
        "scheduled_post_at": post.isoformat(),
        "release_deadline_at": deadline.isoformat(),
        "release_buffer_seconds": 120,
        "current_authority_manifest": manifest,
        "resolved_current_authority_manifest": manifest,
        "source_policy": "CURRENT_LOCAL_OFFICIAL_NAR",
        "require_full_numerical_authority": True,
        "degraded_execution": False,
        "collect_official_odds": True,
    }


FIELDS = ("venue_id", "race_date", "race_no", "scheduled_post_at", "prediction_cutoff")

def resolve_event(event: dict, event_name: str, *, cwd: Path) -> dict:
    """Resolve immutable event range, never moving checkout HEAD. One cell per race."""
    requests, errors, seen = [], [], set()
    candidates = []
    def git_read(*args):
        return subprocess.check_output(["git", *args], cwd=cwd, text=True)
    if event_name == "push":
        before, after = event.get("before", ""), event.get("after", "")
        if not all(re.fullmatch(r"[0-9a-f]{40}", x) for x in (before, after)):
            raise IntakeError("PUSH_EVENT_SHA_REQUIRED")
        if event.get("deleted"):
            raise IntakeError("DELETED_PUSH_NOT_EXECUTABLE")
        paths = (git_read("ls-tree", "-r", "--name-only", after, "runtime/race_key_requests/")
                 if before == "0" * 40 else git_read("diff", "--name-only", "--diff-filter=AMR", before, after, "--", "runtime/race_key_requests/"))
        for path in paths.splitlines():
            if re.fullmatch(r"runtime/race_key_requests/[A-Za-z0-9_.-]+\.json", path):
                candidates.append((path, git_read("show", after + ":" + path)))
    elif event_name in {"workflow_dispatch", "repository_dispatch"}:
        candidates = [(event_name, json.dumps(event.get("inputs") if event_name == "workflow_dispatch" else event.get("client_payload")))]
    else:
        raise IntakeError("UNSUPPORTED_RACE_KEY_EVENT")
    for origin, raw in candidates:
        try:
            data = json.loads(raw)
            if not isinstance(data, dict) or set(data) != set(FIELDS):
                raise IntakeError("RACE_KEY_ONLY_FIVE_SCALAR_FIELDS")
            if any(isinstance(v, bool) or not isinstance(v, (str,int)) or "\n" in str(v) or "\r" in str(v) for v in data.values()):
                raise IntakeError("RACE_KEY_VALUE_TYPE_INVALID")
            # Shape validation uses the same intake gate; the real wall-clock
            # cutoff is rechecked immediately inside each entry job.
            post = aware(data['scheduled_post_at'], 'SCHEDULED_POST')
            cutoff = aware(data['prediction_cutoff'], 'PREDICTION_CUTOFF')
            probe = build(data, now=min(cutoff,post)-timedelta(days=1))
            eid = probe['execution_id']
            if eid in seen:
                raise IntakeError("DUPLICATE_RACE_KEY_IN_EVENT")
            seen.add(eid)
            requests.append({**data,'execution_id':eid,'ingress_origin':origin})
        except (ValueError, TypeError, KeyError) as exc:
            errors.append({'origin':origin,'status':'TERMINAL_ERROR','reason':str(exc)})
    if not candidates:
        errors.append({'status':'TERMINAL_ERROR','reason':'EVENT_HAS_NO_RACE_KEY'})
    return {'event_name':event_name,'before':event.get('before'),'after':event.get('after'),
            'requests':requests,'errors':errors,'status':'PARTIAL' if errors and requests else 'PASS' if requests else 'TERMINAL_ERROR',
            'received_at':datetime.now(timezone.utc).isoformat(),'prestart_delivery_proven':False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-file")
    parser.add_argument("--event-name")
    parser.add_argument("--github-output")
    parser.add_argument("--venue-id")
    parser.add_argument("--race-date")
    parser.add_argument("--race-no")
    parser.add_argument("--scheduled-post-at")
    parser.add_argument("--prediction-cutoff")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.event_file:
        try:
            report = resolve_event(json.loads(Path(args.event_file).read_text()), args.event_name, cwd=Path.cwd())
        except Exception as exc:
            report = {'requests':[],'errors':[{'status':'TERMINAL_ERROR','reason':str(exc)}],'status':'TERMINAL_ERROR'}
        target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        if args.github_output:
            with Path(args.github_output).open('a') as f:
                f.write('matrix='+json.dumps({'include':report['requests']},separators=(',',':'))+'\n')
                f.write('has_requests='+str(bool(report['requests'])).lower()+'\n')
        return 0
    fields = {
        "venue_id": args.venue_id,
        "race_date": args.race_date,
        "race_no": args.race_no,
        "scheduled_post_at": args.scheduled_post_at,
        "prediction_cutoff": args.prediction_cutoff,
    }
    data = build(fields)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "RACE_KEY_REQUEST_PREPARED",
        "execution_id": data["execution_id"],
        "current_authority_manifest": data["current_authority_manifest"],
        "static_generation_executed": False,
        "full_formal_completion_claim": False,
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
