"""Subscriber-permitted Mac queue: authentic Blood-B link discovery -> local diagnostic.

Never manufacture rcode IDs, bypass DataBuyer login, or publish paid HTML.
Requires provider permission, official pre-start runner list, and a local Mac
session. No Production feature/BVI population/ticket/OOS activation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, date
import fcntl
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import sys
from urllib.parse import urljoin, urlparse, parse_qs

from bs4 import BeautifulSoup

from jra_bloodb_mac_collector import (
    BloodBError, HOME, PROFILE, PRIVATE, ROOT, allowed_page, official_universe,
    private_dir, utc_time, capture_context, playwright_sync,
)

QUEUE = HOME / "bloodb_queue.json"
AGENT = "jp.keibametrics.bloodb-collector"
VENUES = ("札幌", "函館", "福島", "新潟", "東京", "中山", "中京", "京都", "阪神", "小倉")

def _rcode(url: str) -> str | None:
    try:
        allowed_page(url)
    except BloodBError:
        return None
    parts = urlparse(url)
    if parts.path != "/main.php":
        return None
    return parse_qs(parts.query).get("rcode", [None])[0]

def _auth_ok(html: str):
    soup = BeautifulSoup(html, "html.parser")
    content = soup.get_text(" ", strip=True)
    if (soup.select_one('input[type="password"]') is not None or
            ("DataBuyer ID" in content and "ログイン" in content)):
        raise BloodBError("BLOODB_SUBSCRIBER_SESSION_EXPIRED")
    return soup

def discover_links(html: str, *, date_text: str, race_no: int,
                   venue: str | None = None) -> list[dict]:
    """Read ONLY real links present in the authenticated /allsel page.

    The first eight digits and final two digits of public rcode examples look
    like YYYYMMDD and race number. Use this only as an eligibility FILTER,
    never derive URL from it. Do not infer venue from numeric code.
    """
    race_day = date.fromisoformat(date_text).strftime("%Y%m%d")
    if not 1 <= int(race_no) <= 12:
        raise BloodBError("JRA_RACE_NUMBER_OUT_OF_RANGE")
    if venue is not None and venue not in VENUES:
        raise BloodBError("JRA_VENUE_UNKNOWN")
    soup = _auth_ok(html)
    rows = []
    for a in soup.find_all("a", href=True):
        resolved = urljoin(ROOT + "/allsel", a.get("href", ""))
        rcode = _rcode(resolved)
        if not rcode or not (rcode.startswith(race_day) and int(rcode[-2:]) == int(race_no)):
            continue
        label = a.get_text(" ", strip=True)
        # Broadest nearby venue context is a bounded parent, never scrape
        # other URLs or assume a numeric JRA course code.
        contexts = [label]
        parent = a.parent
        for _ in range(3):
            if parent is None:
                break
            val = parent.get_text(" ", strip=True)
            if len(val) <= 220:
                contexts.append(val)
            parent = parent.parent
        # The page may have a venue heading preceding a table. Do not trust
        # that context without a clear exact venue match.
        found = [name for name in VENUES if any(name in x for x in contexts)]
        unique_found = found[0] if len(found) == 1 else None
        if venue and unique_found and unique_found != venue:
            continue
        rows.append({"url": resolved, "rcode": rcode, "label": label[:100],
                     "observed_venue": unique_found})
    unique = {r["url"]: r for r in rows}
    return list(unique.values())

def discover_race_url(context, *, date_text: str, race_no: int,
                      venue: str | None = None) -> str:
    page = context.new_page()
    try:
        response = page.goto(ROOT + "/allsel", wait_until="domcontentloaded",
                             timeout=30000)
        if response is None or response.status != 200 or page.url.rstrip("/") != ROOT + "/allsel":
            raise BloodBError("BLOODB_INDEX_LOGIN_OR_ACCESS_FAILURE")
        raw = page.content()
        options = discover_links(raw, date_text=date_text,
                                 race_no=race_no, venue=venue)
    finally:
        page.close()
    if len(options) != 1:
        # Ambiguity is a hard block; this avoids selecting Kyoto's 9R for
        # Tokyo's 9R when multiple venues race on the same day.
        raise BloodBError("BLOODB_RACE_LINK_MISSING_OR_AMBIGUOUS:" + str(len(options)))
    if venue and options[0]["observed_venue"] not in (venue,):
        # Numeric rcode itself is not independent proof of venue identity.
        raise BloodBError("BLOODB_VENUE_CONTEXT_UNVERIFIED")
    return options[0]["url"]

def load_official(spec: dict) -> tuple[list[dict], dict]:
    if spec.get("signed_source_envelope_path"):
        src = Path(spec["signed_source_envelope_path"]).expanduser().resolve()
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from jra_source_runtime.verify_source_envelope import verify
        chk = verify(src)
        if chk["valid"] is not True or chk.get("family") != "JRA":
            raise BloodBError("JRA_SIGNED_ENVELOPE_INVALID")
        env = json.loads(src.read_text(encoding="utf-8"))
        art = env["artifact"]
        if art.get("race_id") != spec["race_id"]:
            raise BloodBError("JRA_SIGNED_RACE_ID_MISMATCH")
        identity = art.get("source_race_context") or art.get("jra_race_context") or {}
        if identity.get("race_date") != spec["race_date"]:
            raise BloodBError("JRA_SIGNED_RACE_DATE_MISMATCH")
        cutoff = utc_time(spec["prediction_cutoff"])
        frozen = utc_time(art.get("source_freeze_at"))
        if frozen >= cutoff:
            raise BloodBError("JRA_SOURCE_FREEZE_AFTER_PREDICTION_CUTOFF")
        detail = (art.get("jra_official_race_card_detail") or {}).get("runners") or []
        rows = [{"horse_no":x.get("horse_no") or x.get("runner_id"),
                 "name":x.get("horse_name") or x.get("name")}
                for x in detail if x.get("status") not in ("SCRATCHED","取消","除外")]
        official_universe(rows)
        return rows, {"level":"SOURCE_ED25519_ONLY_NOT_INDEPENDENT_OIDC_ATTESTED_HERE",
                      "source_artifact_sha256":chk["artifact_sha256"],
                      "source_receipt_sha256":chk["receipt_sha256"]}
    # Explicitly allow pre-verified external runner lists only as diagnostic;
    # don't pretend the JSON list is signed or externally attested.
    file = Path(spec["official_runners_path"]).expanduser().resolve()
    rows = json.loads(file.read_text(encoding="utf-8"))
    official_universe(rows)
    return rows, {"level":"USER_SUPPLIED_UNATTESTED_DIAGNOSTIC_ONLY",
                  "source_artifact_sha256":None}

def run_one(context, spec: dict, *, private_root: Path = PRIVATE,
            discover=discover_race_url, clock=None) -> dict:
    clock = clock or (lambda: datetime.now(timezone.utc))
    race_id = str(spec["race_id"])
    today = date.fromisoformat(spec["race_date"])
    if today.isoformat() != spec["race_date"]:
        raise BloodBError("RACE_DATE_INVALID")
    cutoff = utc_time(spec["prediction_cutoff"])
    if clock() >= cutoff:
        raise BloodBError("BLOODB_PREDICTION_CUTOFF_EXPIRED")
    official, source = load_official(spec)
    direct = spec.get("bloodb_race_url")
    if direct:
        url = allowed_page(direct)
    else:
        url = discover(context, date_text=spec["race_date"],
                       race_no=int(spec["race_no"]), venue=spec.get("venue"))
    if _rcode(url) is None:
        raise BloodBError("BLOODB_RACE_LINK_REQUIRED_NOT_INDEX")
    # Verify first 8 digits and last 2 of observed link against intent, not
    # enough to establish venue, which must be independently determined.
    rcode = _rcode(url)
    if rcode[:8] != today.strftime("%Y%m%d") or int(rcode[-2:]) != int(spec["race_no"]):
        raise BloodBError("BLOODB_RACE_LINK_DATE_OR_NUMBER_MISMATCH")
    data = capture_context(
        context, race_url=url, race_date=spec["race_date"],
        cutoff=spec["prediction_cutoff"], official=official,
        race_id=race_id, output_root=private_root, now=clock,
    )
    dest = private_root / race_id
    # Private sidecar is not Production authority; verified identity is
    # provenance context, never imply BloodB supplied independently signed.
    sidecar = dest / "jra_source_binding.json"
    from jra_bloodb_mac_collector import private_write, json_bytes
    private_write(sidecar, json_bytes({
        "race_id":race_id, "jra_official_source":source,
        "bloodb_page_sha256":data["raw_sha256"],
        "production_authority":False, "bvi_population_authority":False,
        "signed_final":False, "oos_increment":0,
    }))
    return {"race_id":race_id,"status":"PRIVATE_DIAGNOSTIC_CAPTURED",
            "runner_count":data["runner_count"],"raw_sha256":data["raw_sha256"],
            "source_binding":source["level"],
            "production_authority":False,"oos_increment":0}

def process_queue(context, queue_path: Path, *,
                  private_root: Path = PRIVATE,
                  clock=None, lookahead_minutes: int = 65,
                  discover=discover_race_url) -> dict:
    clock = clock or (lambda: datetime.now(timezone.utc))
    queue_path = queue_path.expanduser().resolve()
    if not queue_path.exists():
        raise BloodBError("BLOODB_QUEUE_MISSING")
    specs = json.loads(queue_path.read_text(encoding="utf-8"))
    if not isinstance(specs, list) or len(specs) > 80:
        raise BloodBError("BLOODB_QUEUE_INVALID_OR_OVERSIZED")
    private_root = private_dir(private_root)
    fd = os.open(private_root / ".queue.lock", os.O_CREAT | os.O_RDWR, 0o600)
    result = {"completed":[],"not_due":[],"past_cutoff":[],"already_collected":[],"failed":[]}
    with os.fdopen(fd, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for spec in specs:
            try:
                race_id = str(spec["race_id"])
                if not re.fullmatch(r"[A-Za-z0-9_.-]{4,120}", race_id):
                    raise BloodBError("RACE_ID_UNSAFE")
                remaining = (utc_time(spec["prediction_cutoff"])-clock()).total_seconds()
                if (private_root / race_id).exists():
                    result["already_collected"].append(race_id)
                elif remaining <= 0:
                    result["past_cutoff"].append(race_id)
                elif remaining > lookahead_minutes * 60:
                    result["not_due"].append(race_id)
                else:
                    try:
                        done = run_one(context, spec, private_root=private_root,
                                       clock=clock, discover=discover)
                        result["completed"].append(done)
                    except Exception as exc:
                        result["failed"].append({"race_id":race_id, "reason":str(exc)[:240]})
            except (KeyError, ValueError, TypeError) as exc:
                result["failed"].append({"race_id":str(spec.get("race_id") if isinstance(spec,dict) else "?"),
                                         "reason":str(exc)[:240]})
        fcntl.flock(lock, fcntl.LOCK_UN)
    return result

def launchd_plist(*, repo: Path, queue: Path = QUEUE,
                  profile: Path = PROFILE, private_root: Path = PRIVATE,
                  interval: int = 300) -> dict:
    if sys.platform != "darwin":
        raise BloodBError("MACOS_LAUNCHD_REQUIRED")
    if not 180 <= interval <= 3600:
        raise BloodBError("LAUNCHD_INTERVAL_OUT_OF_BOUNDS")
    path = repo.expanduser().resolve() / "runtime/jra_bloodb_mac_automation.py"
    if not path.is_file():
        raise BloodBError("MAC_AUTOMATION_SCRIPT_NOT_FOUND")
    directory = private_dir(private_root)
    return {"Label":AGENT,"RunAtLoad":True,"StartInterval":interval,
        "WorkingDirectory":str(repo.expanduser().resolve()),
        "ProgramArguments":[sys.executable,str(path),"queue",
             "--queue",str(queue.expanduser().resolve()),
             "--profile",str(profile.expanduser().resolve()),
             "--private-dir",str(directory),
             "--provider-permission-confirmed"],
        "StandardOutPath":str(directory/"queue.stdout.log"),
        "StandardErrorPath":str(directory/"queue.stderr.log")}

def cli(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode",choices=("discover","queue","install-launchd"))
    ap.add_argument("--queue",type=Path,default=QUEUE)
    ap.add_argument("--profile",type=Path,default=PROFILE)
    ap.add_argument("--private-dir",type=Path,default=PRIVATE)
    ap.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument("--interval",type=int,default=300)
    ap.add_argument("--provider-permission-confirmed",action="store_true")
    args=ap.parse_args(argv)
    if not args.provider_permission_confirmed:
        raise BloodBError("PROVIDER_AUTOMATED_ACCESS_PERMISSION_MUST_BE_CONFIRMED")
    if args.mode=="install-launchd":
        d = launchd_plist(repo=args.repo,queue=args.queue,
                profile=args.profile,private_root=args.private_dir,interval=args.interval)
        target=Path.home()/"Library/LaunchAgents"/(AGENT+".plist")
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open("wb") as stream:
            plistlib.dump(d,stream)
        os.chmod(target,0o600)
        # Explicit install means enable the local scheduled job.
        run=subprocess.run(["launchctl","bootstrap","gui/"+str(os.getuid()),
                            str(target)],capture_output=True,text=True,check=False)
        if run.returncode:
            raise BloodBError("MAC_LAUNCH_AGENT_SETUP_FAILED:"+run.stderr[:160])
        result={"installed":True,"plist":str(target),
                "runs_locally":True,"subscriber_session_stays_on_mac":True}
    else:
        specs=json.loads(args.queue.expanduser().read_text(encoding="utf-8"))
        profile=private_dir(args.profile)
        with playwright_sync()() as pl:
            context=pl.chromium.launch_persistent_context(str(profile),
                                      headless=True,accept_downloads=False)
            try:
                if args.mode=="queue":
                    result=process_queue(context,args.queue,private_root=args.private_dir)
                else:
                    first=next((x for x in specs if x.get("race_no") and x.get("race_date")),None)
                    if not first:
                        raise BloodBError("DISCOVER_REQUIRES_RACE_SPEC")
                    discovered=discover_race_url(context,date_text=first["race_date"],
                              race_no=int(first["race_no"]),venue=first.get("venue"))
                    result={"status":"OBSERVED_LINK_DISCOVERY",
                            "race_id":first["race_id"],"race_link":discovered}
            finally:
                context.close()
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    return int(bool(result.get("failed")))

if __name__=="__main__":
    raise SystemExit(cli())
