"""Mac-local Blood Bias (blood-b.com) subscriber capture and diagnostic bridge.

Subscriber logs in *personally* using a persistent Chromium profile. Do not
send login information to ChatGPT/GitHub. Only run automated acquisition after
the provider has authorized that specific use. This is NOT a JRA signed SOURCE,
a BVI population database, a Production feature or a betting recommendation.

Actual authenticated HTML is not available in CI; parser is conservative,
versioned and must fail closed on a changed/unrecognized member-page structure.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, date
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import urlparse, parse_qsl
from bs4 import BeautifulSoup

HOME = Path.home() / ".keibametrics"
PROFILE = HOME / "browser_bloodb"
PRIVATE = HOME / "private_bloodb"
ROOT = "https://www.blood-b.com"
FIELDS = ("血統", "血統評価", "血統タイプ", "相対指数", "ローテ評価", "人気ランク")
SOURCE_PROFILE = "BLOODB-SUBSCRIBER-LOCAL-DIAGNOSTIC-v0.1"

class BloodBError(ValueError):
    pass

def private_dir(path: Path) -> Path:
    path = path.expanduser().resolve()
    root = HOME.expanduser().resolve()
    if path != root and root in path.parents:
        private_dir(root)
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.stat().st_mode & 0o077:
        raise BloodBError("PRIVATE_DIRECTORY_MODE_NOT_0700")
    return path

def private_write(file: Path, data: bytes):
    fd = os.open(file, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())

def json_bytes(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()

def utc_time(value: str) -> datetime:
    try:
        t = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise BloodBError("CUTOFF_INVALID") from exc
    if t.tzinfo is None:
        raise BloodBError("CUTOFF_TIMEZONE_REQUIRED")
    return t.astimezone(timezone.utc)

def allowed_page(url: str) -> str:
    """Exact site/path allow-list; refuse external SSO redirect and other URLs."""
    p = urlparse(url)
    if p.scheme != "https" or p.hostname != "www.blood-b.com" or p.port is not None or p.fragment:
        raise BloodBError("BLOODB_HOST_OR_SCHEME_NOT_ALLOWED")
    if p.path.rstrip("/") == "/allsel" and not p.query:
        return url
    if p.path == "/main.php":
        args = parse_qsl(p.query, keep_blank_values=True)
        if len(args) == 1 and args[0][0] == "rcode" and re.fullmatch(r"\d{14,20}", args[0][1]):
            return url
    raise BloodBError("BLOODB_UNVERIFIED_RACE_URL")

def namekey(x: str) -> str:
    return re.sub(r"[\s\u3000]+", "", str(x or ""))

def official_universe(rows: list[dict]):
    if not isinstance(rows, list) or not 2 <= len(rows) <= 18:
        raise BloodBError("SIGNED_JRA_RUNNER_UNIVERSE_REQUIRED")
    result = {}
    nums = set()
    for r in rows:
        if not isinstance(r, dict):
            raise BloodBError("JRA_RUNNER_ROW_INVALID")
        no = str(r.get("horse_no") or r.get("runner_id") or "")
        name = namekey(r.get("name") or r.get("horse_name"))
        if not no or not re.fullmatch(r"\d{1,2}", no) or not name or name in result or no in nums:
            raise BloodBError("JRA_RUNNER_UNIVERSE_DUPLICATE_OR_UNRESOLVED")
        result[name] = no
        nums.add(no)
    return result

def parse_rendered(html: str, official: list[dict]) -> dict:
    """Only explicitly labelled cells, exact independent horse-name matches.

    No assumptions about blood-b subscriber DOM beyond ordinary HTML tables.
    A real paid-page fixture/approval is needed to confirm actual coverage.
    """
    official_names = official_universe(official)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    if soup.select("input[type=password]") or ("DataBuyer ID" in text and "ログイン" in text):
        raise BloodBError("BLOODB_LOGIN_REQUIRED")
    selected = {}
    for table in soup.select("table"):
        trs = table.select("tr")
        header = next(([namekey(cell.get_text(" ", strip=True)) for cell in tr.select("th")]
                       for tr in trs if len(tr.select("th")) >= 2), None)
        if not header:
            continue
        recognizable = [x for x in header if any(namekey(k) == x for k in FIELDS)]
        if not recognizable:
            continue
        for tr in trs:
            cells = tr.find_all(["td"], recursive=False)
            if not cells or len(cells) != len(header):
                continue
            identities = set()
            for cell in cells:
                candidates = [cell.get_text(" ", strip=True)]
                candidates.extend(a.get_text(" ",strip=True) for a in cell.find_all("a"))
                identities.update(namekey(v) for v in candidates if namekey(v) in official_names)
            if len(identities) != 1:
                continue
            horse = identities.pop()
            if horse in selected:
                raise BloodBError("BLOODB_DUPLICATE_HORSE_ROWS")
            values = {}
            for title, cell in zip(header, cells):
                if title in {namekey(k) for k in FIELDS}:
                    value = cell.get_text(" ", strip=True)
                    if value:
                        values[next(k for k in FIELDS if namekey(k) == title)] = value[:160]
            if values:
                selected[horse] = {"horse_no": official_names[horse], "horse_name": horse,
                                   "observed_labels": values}
    missing = sorted(set(official_names) - set(selected))
    if missing:
        raise BloodBError("BLOODB_RUNNER_COVERAGE_UNVERIFIED:" + str(len(missing)) + "/" + str(len(official_names)))
    return {"horse_count":len(selected), "observations":list(selected.values()),
            "parser":"EXACT-NAME-HEADER-TABLE-v0.1", "observed_labels":sorted(set(
                label for row in selected.values() for label in row["observed_labels"]))}

def check_page_actual(actual_url: str, expected_url: str):
    if actual_url != expected_url:
        raise BloodBError("BLOODB_UNEXPECTED_REDIRECT_OR_LOGIN")

def capture_context(context, *, race_url: str, race_date: str, cutoff: str,
                    official: list[dict], output_root: Path = PRIVATE,
                    race_id: str, now=None, source_binding: dict | None = None) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_.-]{4,120}", race_id):
        raise BloodBError("RACE_ID_UNSAFE")
    expected = allowed_page(race_url)
    date.fromisoformat(race_date)
    limit = utc_time(cutoff)
    now = now or (lambda: datetime.now(timezone.utc))
    if now() >= limit:
        raise BloodBError("BLOODB_PREDICTION_CUTOFF_EXPIRED")
    private_dir(output_root)
    dest = output_root / race_id
    if dest.exists():
        raise BloodBError("BLOODB_IMMUTABLE_CAPTURE_EXISTS")
    page = context.new_page()
    try:
        response = page.goto(expected, wait_until="domcontentloaded", timeout=30000)
        if response is None or response.status != 200:
            raise BloodBError("BLOODB_PAGE_ACCESS_NOT_200")
        check_page_actual(page.url, expected)
        at = now()
        if at >= limit:
            raise BloodBError("BLOODB_PREDICTION_CUTOFF_EXPIRED")
        raw = page.content().encode("utf-8")
        if not (100 <= len(raw) <= 2_500_000):
            raise BloodBError("BLOODB_PAGE_SIZE_NOT_ACCEPTED")
        parsed = parse_rendered(raw.decode("utf-8"), official)
        if now() >= limit:
            raise BloodBError("BLOODB_PREDICTION_CUTOFF_EXPIRED")
    finally:
        page.close()
    staging = Path(tempfile.mkdtemp(dir=output_root, prefix=".pending-bloodb-"))
    try:
        os.chmod(staging, 0o700)
        digest = hashlib.sha256(raw).hexdigest()
        record = {
            "profile": SOURCE_PROFILE, "origin_url":expected,
            "race_id":race_id, "race_date":race_date,
            "captured_at":at.isoformat(), "prediction_cutoff":cutoff,
            "raw_sha256":digest,"capture_method":"MEMBER_AUTHENTICATED_RENDERED_DOM",
            "source_authentication":"LOCAL_SUBSCRIBER_SESSION_NOT_PROVIDER_SIGNED",
            "official_universe_authentication":"UPSTREAM_SOURCE_VERIFICATION_REQUIRED",
            **parsed, "production_authority":False, "bvi_population_authority":False,
            "signed_source":False,"signed_final":False,"oos_increment":0,
            "publisher_rights":"NOT_ESTABLISHED",
        }
        private_write(staging/"subscriber_page.html",raw)
        private_write(staging/"diagnostic.json",json_bytes(record))
        if source_binding is not None:
            private_write(staging/"jra_source_binding.json",json_bytes({
                "race_id":race_id,
                "jra_official_source":source_binding,
                "bloodb_page_sha256":digest,
                "production_authority":False,
                "bvi_population_authority":False,
                "signed_final":False,"oos_increment":0,
            }))
        summary = {
            "profile":SOURCE_PROFILE,"race_id":race_id,"runner_count":parsed["horse_count"],
            "captured_at":at.isoformat(),"raw_sha256":digest,
            "labels":parsed["observed_labels"], "production_authority":False,
            "upload_to_github":False,
        }
        private_write(staging/"summary.json",json_bytes(summary))
        staging.rename(dest)
        return summary
    finally:
        if staging.exists():
            shutil.rmtree(staging)

def playwright_sync():
    try:
        from playwright.sync_api import sync_playwright
        return sync_playwright
    except ImportError as exc:
        raise BloodBError("INSTALL_PLAYWRIGHT_AND_CHROMIUM_ON_MAC") from exc

def browser_login(profile: Path):
    profile = private_dir(profile)
    with playwright_sync()() as pl:
        context = pl.chromium.launch_persistent_context(str(profile), headless=False,
                                                        accept_downloads=False)
        try:
            page = context.new_page()
            page.goto(ROOT+"/allsel", wait_until="domcontentloaded")
            print("Log in with your own DataBuyer ID in the visible Chromium window.")
            print("Never send passwords, cookies, OTPs or session files to ChatGPT/GitHub.")
            input("Once you can view the subscriber page, press Enter to save local session: ")
        finally:
            context.close()

def inspect(profile: Path, url: str):
    """Check member-page structure; return labels only, never paid body or secrets."""
    url = allowed_page(url)
    with playwright_sync()() as pl:
        context = pl.chromium.launch_persistent_context(str(private_dir(profile)),
                                                         headless=True,accept_downloads=False)
        try:
            page = context.new_page()
            response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
            if response is None or response.status != 200:
                raise BloodBError("BLOODB_ACCESS_NOT_GRANTED")
            check_page_actual(page.url,url)
            soup=BeautifulSoup(page.content(),"html.parser")
            if soup.select("input[type=password]"):
                raise BloodBError("BLOODB_LOGIN_REQUIRED")
            structures=[len(t.select("tr")) for t in soup.select("table")]
            headings=sorted({namekey(x.get_text(" ",strip=True))[:30]
                             for x in soup.select("th") if x.get_text(strip=True)})
            return {"status":"INSPECTION_ONLY", "url_path":urlparse(url).path,
                    "table_row_counts":structures, "table_headers":headings[:65],
                    "no_paid_rows_exported":True}
        finally:
            context.close()

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=["login","inspect","capture"])
    parser.add_argument("--profile",type=Path,default=PROFILE)
    parser.add_argument("--race-url")
    parser.add_argument("--spec",type=Path)
    parser.add_argument("--private-dir",type=Path,default=PRIVATE)
    parser.add_argument("--provider-permission-confirmed",action="store_true")
    args=parser.parse_args(argv)
    if args.action=="login":
        browser_login(args.profile)
        return 0
    if not args.provider_permission_confirmed:
        raise BloodBError("PROVIDER_AUTOMATED_ACCESS_PERMISSION_MUST_BE_CONFIRMED")
    if args.action=="inspect":
        result=inspect(args.profile,args.race_url or ROOT+"/allsel")
    else:
        if not args.spec:
            raise BloodBError("SIGNED_JRA_RACE_SPEC_REQUIRED")
        spec=json.loads(args.spec.expanduser().read_text(encoding="utf-8"))
        official=json.loads(Path(spec["official_runners_path"]).expanduser().read_text(encoding="utf-8"))
        with playwright_sync()() as pl:
            context=pl.chromium.launch_persistent_context(str(private_dir(args.profile)),
                                                            headless=True,accept_downloads=False)
            try:
                result=capture_context(context, race_url=spec["bloodb_race_url"],
                            race_date=spec["race_date"],cutoff=spec["prediction_cutoff"],
                            official=official,race_id=spec["race_id"],output_root=args.private_dir)
            finally:
                context.close()
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
