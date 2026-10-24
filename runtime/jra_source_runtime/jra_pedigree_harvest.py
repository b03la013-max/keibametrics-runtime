"""Harvest JRA OFFICIAL pedigree identity + race histories for the corpus.

Source: www.jra.go.jp only (robots.txt allows all paths). For a race day it
walks the official results (past days) or race cards (upcoming days), opens
every runner's official horse page and records:
  horse name, 父 (sire), 母の父 (damsire), full official race history.
The output feeds ``runtime/jra_pedigree_corpus.py``. No third-party source,
no login, polite sequential requests.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import html
import http.cookiejar
import json
import re
import random
import socket
import ssl
import errno
import sys
import http.client
from email.utils import parsedate_to_datetime
import time
import urllib.parse
import urllib.request
import urllib.error
from typing import Any, Dict, List
from bs4 import BeautifulSoup

from source_acquisition import _decode
from jra_horse_history import parse_horse_history

PROFILE = "KM-JRA-OFFICIAL-PEDIGREE-HARVEST-v1.0-20261010"
BASE = "https://www.jra.go.jp"
UA = "KeibaMetrics-JRA-Official-Pedigree-Harvest/1.0"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class OfficialDeadlineExceeded(TimeoutError):
    """No further official request may consume the reserved downstream budget."""


def retryable_official_error(exc):
    if isinstance(exc, OfficialDeadlineExceeded):
        return False
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code == 429 or 500 <= exc.code <= 599
    if isinstance(exc, urllib.error.URLError):
        return retryable_official_error(exc.reason)
    if isinstance(exc, ssl.SSLCertVerificationError):
        return False
    if isinstance(exc, (TimeoutError, ConnectionError, http.client.IncompleteRead,
                        http.client.RemoteDisconnected)):
        return True
    return isinstance(exc, OSError) and exc.errno in {
        errno.ECONNRESET, errno.ECONNABORTED, errno.ETIMEDOUT,
        errno.EPIPE, errno.EHOSTUNREACH, errno.ENETUNREACH, socket.EAI_AGAIN}


class _Client:
    def __init__(self, delay: float = 1.0, *, deadline_monotonic=None, stop_on_access_denied=False):
        if not 0.7 <= delay <= 15.0:
            raise ValueError("JRA_HARVEST_RATE_TOO_FAST_OR_INVALID")
        class _NoExternalRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                parsed = urllib.parse.urlsplit(newurl)
                if parsed.scheme != "https" or parsed.hostname != "www.jra.go.jp":
                    raise ValueError("JRA_HARVEST_REDIRECT_HOST_FORBIDDEN")
                return super().redirect_request(req, fp, code, msg, headers, newurl)
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
            _NoExternalRedirect())
        self.delay = delay
        self.deadline_monotonic = deadline_monotonic
        self.stop_on_access_denied = stop_on_access_denied
        self.last_response = {}

    def _open(self, url: str, data: bytes | None = None) -> str:
        if not url.startswith(BASE + "/"):
            raise ValueError("JRA_OFFICIAL_ONLY")
        req = urllib.request.Request(url, data=data, headers={
            "User-Agent": UA, "Accept": "text/html,*/*;q=0.1", "Accept-Language": "ja"})
        # Three attempts retain the old bound. Reset/timeout/body-read failures
        # now share it with 429/5xx. Keep the same opener, cookies, URL and POST
        # token: navigation reads are safe to retry; no new source is invented.
        deadline = min(time.monotonic() + 105, self.deadline_monotonic or float("inf"))
        def remaining():
            left = deadline - time.monotonic()
            if left <= 0:
                raise OfficialDeadlineExceeded("JRA_OFFICIAL_RETRY_DEADLINE")
            return left
        def pause(seconds):
            if seconds >= remaining():
                raise OfficialDeadlineExceeded("JRA_OFFICIAL_RETRY_DEADLINE")
            time.sleep(seconds)
        pause(self.delay)
        for attempt in range(3):
            phase = "CONNECT_TLS_OR_RESPONSE_HEADERS"
            try:
                with self.opener.open(req, timeout=min(30, remaining())) as r:
                    phase = "READ_BODY"
                    if urllib.parse.urlsplit(r.geturl()).hostname != "www.jra.go.jp":
                        raise ValueError("JRA_HARVEST_FINAL_HOST_INVALID")
                    # read1 returns after a single underlying read, so a slow
                    # stream cannot reset a 30s timeout forever. Bound every read.
                    chunks, size = [], 0
                    while True:
                        left = remaining()
                        sock = getattr(getattr(getattr(r, "fp", None), "raw", None), "_sock", None)
                        if sock is not None:
                            sock.settimeout(min(30, left))
                        chunk = r.read1(min(65536, 6_000_001 - size))
                        remaining()
                        if not chunk:
                            if getattr(r, "length", 0):
                                raise http.client.IncompleteRead(b"".join(chunks), r.length)
                            break
                        chunks.append(chunk); size += len(chunk)
                        if size > 6_000_000:
                            raise ValueError("JRA_HARVEST_PAGE_TOO_LARGE")
                    raw = b"".join(chunks)
                    self.last_response = {'url':url, 'raw_sha256':_sha(raw),
                                          'fetched_at':_dt.datetime.now(_dt.timezone.utc).isoformat()}
                    return _decode(raw, r.headers.get("content-type", ""))
            except (OSError, http.client.HTTPException) as exc:
                exc.official_request = {"url": url, "method": req.get_method(),
                                        "phase": phase, "attempt": attempt + 1}
                if (self.stop_on_access_denied and isinstance(exc, urllib.error.HTTPError)
                        and exc.code in (403,429)):
                    raise  # dedicated Collector stops; Formal client defaults are unchanged
                if not retryable_official_error(exc) or attempt == 2:
                    raise
                wait = 3 * (2 ** attempt) + random.uniform(0, 0.75)
                if isinstance(exc, urllib.error.HTTPError):
                    retry_after = exc.headers.get("Retry-After") if exc.headers else None
                    exc.close()
                    if retry_after:
                        try:
                            wait = max(wait, float(retry_after))
                        except ValueError:
                            try:
                                when = parsedate_to_datetime(retry_after)
                                wait = max(wait, (when - _dt.datetime.now(_dt.timezone.utc)).total_seconds())
                            except (ValueError, TypeError, OverflowError):
                                pass
                print(json.dumps({"stage":"JRA_OFFICIAL_HTTP_RETRY", **exc.official_request,
                                  "exception_class":type(exc).__name__, "backoff_seconds":wait}),
                      file=sys.stderr, flush=True)
                pause(wait)

    def get(self, path: str) -> str:
        return self._open(BASE + path)

    def post(self, path: str, token: str) -> str:
        return self._open(BASE + path, urllib.parse.urlencode({"cname": token}).encode())

    def raw_get(self, path: str) -> tuple[bytes, str]:
        if not path.startswith("/JRADB/accessU.html?CNAME="):
            raise ValueError("JRA_HARVEST_HORSE_ENDPOINT_REQUIRED")
        req = urllib.request.Request(BASE + path, headers={"User-Agent": UA, "Accept-Language": "ja"})
        time.sleep(self.delay)
        with self.opener.open(req, timeout=30) as r:
            if urllib.parse.urlsplit(r.geturl()).hostname != "www.jra.go.jp":
                raise ValueError("JRA_HARVEST_FINAL_HOST_INVALID")
            raw = r.read(6_000_001)
            if len(raw) > 6_000_000:
                raise ValueError("JRA_HARVEST_PAGE_TOO_LARGE")
            return raw, r.headers.get("content-type", "")


def _calendar(race_date: str) -> str:
    d = _dt.date.fromisoformat(race_date)
    return f"/keiba/calendar{d.year}/{d.year}/{d.month}/{d.strftime('%m%d')}.html"


def parse_horse_pedigree(decoded: str) -> Dict[str, str | None]:
    """Parse actual JRA horse-profile headers and parent cells (variable markup).

    Keep identity UNKNOWN when a genuinely incomplete profile has no parent.
    Never guess a sire or borrow a neighboring horse's profile.
    """
    soup = BeautifulSoup(decoded, "html.parser")
    def parent(label: str) -> str | None:
        for dt in soup.select("dt"):
            if re.sub(r"\s+", "", dt.get_text(" ",strip=True)).strip("：:") != label:
                continue
            dd = dt.find_next_sibling("dd")
            if dd is not None:
                copy = BeautifulSoup(str(dd), "html.parser")
                for el in copy.select(".sanku"):
                    el.decompose()
                value = copy.get_text(" ", strip=True)
                return re.sub(r"\s+", " ", value).strip() or None
        # Some official profile revisions use table headers for pedigree.
        for th in soup.select("th"):
            if re.sub(r"\s+", "", th.get_text(" ",strip=True)).strip("：:") == label:
                td = th.find_next_sibling("td")
                if td:
                    return td.get_text(" ", strip=True) or None
        return None
    name = None
    m = re.search(r'<span class="opt">\s*競走馬情報\s*</span>\s*([^<]+?)\s*<span class="name_en">', decoded)
    if m:
        name = html.unescape(m.group(1)).strip()
    if not name:
        for opt in soup.select("span.opt"):
            if "競走馬情報" not in opt.get_text(strip=True):
                continue
            for sibling in opt.next_siblings:
                if isinstance(sibling, str) and sibling.strip():
                    name = re.sub(r"\s+", " ", sibling).strip()
                    break
                if getattr(sibling, "name", "") == "span" and "name_en" in sibling.get("class",[]):
                    break
    if not name:
        for css in (".name_ja", ".name_jp", ".horse_name", ".horseName"):
            tag=soup.select_one(css)
            if tag:
                name=tag.get_text(" ",strip=True)
                if name: break
    return {"horse_name": name, "sire": parent("父"), "dam": parent("母"),
            "damsire": parent("母の父")}


def archive_month_token(decoded: str, race_date: str) -> str:
    """Follow the official archive form's published month/checksum mapping.

    Race/day/horse tokens still come only from observed official responses.
    Refuse changed markup or an unavailable year rather than guessing a URL.
    """
    day = _dt.date.fromisoformat(race_date)
    soup = BeautifulSoup(decoded, "html.parser")
    years = {x.get("value") for x in soup.select('select[name="kaisaiY_list"] option')}
    months = {x.get("value") for x in soup.select('select[name="kaisaiM_list"] option')}
    current = re.search(r'var\s+yearMonth\s*=\s*"(\d{6})"', decoded)
    checksums = dict(re.findall(r'objParam\["(\d{4})"\]="([0-9A-Fa-f]{2})"', decoded))
    target = day.strftime("%Y%m")
    required = ("pw01skl00", "pw01skl10", "Number(arg) >= yearMonth",
                "objParam[String(arg).substring(2,6)]")
    if (str(day.year) not in years or day.strftime("%m") not in months
            or current is None or target[2:] not in checksums
            or any(value not in decoded for value in required)):
        raise ValueError("JRA_HARVEST_ARCHIVE_FORM_NOT_OBSERVED")
    prefix = "pw01skl00" if target >= current.group(1) else "pw01skl10"
    return prefix + target + "/" + checksums[target[2:]]


def _day_navigation(client, race_date, mode):
    d8 = _dt.date.fromisoformat(race_date).strftime("%Y%m%d")
    page, entry_pat, day_pat, race_pat = {
        "results": ("/JRADB/accessS.html", r"doAction\('/JRADB/accessS\.html'\s*,\s*'([^']+)'\)",
                    r"pw01srl\d{2}\d{10}" + d8 + r"/[0-9A-Fa-f]{2}", r"pw01sde\d{2}\d{12}" + d8 + r"/[0-9A-Fa-f]{2}"),
        "cards": ("/JRADB/accessD.html", r"doAction\('/JRADB/accessD\.html'\s*,\s*'([^']+)'\)",
                  r"pw01drl\d{2}\d{10}" + d8 + r"/[0-9A-Fa-f]{2}", r"pw01dde\d{2}\d{12}" + d8 + r"/[0-9A-Fa-f]{2}"),
    }[mode]
    cal = client.get(_calendar(race_date))
    m = re.search(entry_pat, cal)
    if not m:
        raise ValueError("JRA_HARVEST_ENTRY_TOKEN_NOT_FOUND")
    entry_token = m.group(1)
    s1 = client.post(page, entry_token)
    days = sorted(set(re.findall(day_pat, s1)))
    if not days and mode == "results":
        entries = re.findall(entry_pat, cal)
        archive = next((token for token in entries if token.startswith("pw01skl")), None)
        if archive is None:
            raise ValueError("JRA_HARVEST_ARCHIVE_ENTRY_NOT_OBSERVED")
        selector = client.post(page, archive)
        entry_token = archive_month_token(selector, race_date)
        s1 = client.post(page, entry_token)
        days = sorted(set(re.findall(day_pat, s1)))
    return page, entry_token, days, race_pat


def race_reference(token, race_date):
    """Canonical execution reference, NOT an assertion of a permanent race ID."""
    from jra_race_day_resolver import VENUES
    m = re.fullmatch(r'pw01(?:sde|dde)\d{2}(\d{10})(\d{2})(\d{8})/[0-9A-Fa-f]{2}', token)
    if not m or m[3] != race_date.replace('-','') or m[1][:2] not in VENUES:
        raise ValueError('JRA_OBSERVED_RACE_REFERENCE_INVALID')
    venue_id, venue_name = VENUES[m[1][:2]]
    return {'race_id':f'KM-JRA-{venue_id}-{m[3]}-R{int(m[2]):02d}',
            'venue_id':venue_id,'venue':venue_name,'race_no':int(m[2]),
            'navigation_token_sha256':_sha(token.encode()),
            'identity_kind':'CANONICAL_EXECUTION_REFERENCE_NOT_PERMANENT_REGISTRY_ID'}


def discover_day(client, race_date, *, mode):
    page, entry, days, pattern = _day_navigation(client,race_date,mode)
    races=[]
    for day in days:
        client.post(page,entry)
        decoded=client.post(page,day)
        source=dict(getattr(client,'last_response',{}))
        for token in sorted(set(re.findall(pattern,decoded))):
            races.append({**race_reference(token,race_date),'official_listing':source})
    if not races or len(races)>36 or len({r['race_id'] for r in races})!=len(races):
        raise ValueError('JRA_OFFICIAL_DAY_UNIVERSE_INVALID')
    return races


def horse_tokens_for_day(client: _Client, race_date: str, *, mode: str,
                         stop_after: int | None = None,
                         start_race: int = 0, max_races: int | None = None) -> List[str]:
    """Return official horse-page CNAME tokens for a bounded day window."""
    page, entry_token, days, race_pat = _day_navigation(client,race_date,mode)
    out: List[str] = []
    race_index = 0
    client.scanned_race_count = 0
    client.race_observations = []
    completed = False
    for day in days:
        client.post(page, entry_token)
        s2 = client.post(page, day)
        day_races = sorted(set(re.findall(race_pat, s2)))
        client.scanned_race_count += len(day_races)
        for race in day_races:
            # Always select explicit race windows; a small three-horse test
            # must never visit all 36 race result pages. This also limits
            # requests during temporary 503/service-unavailable windows.
            if race_index < start_race:
                race_index += 1
                continue
            if max_races is not None and race_index >= start_race + max_races:
                completed = True
                break
            race_index += 1
            client.post(page, entry_token)
            client.post(page, day)
            s3 = client.post(page, race)
            record={**race_reference(race,race_date), 'source':dict(getattr(client,'last_response',{})),
                    'runners':[], 'universe_status':'UNRESOLVED'}
            try:
                if mode=='cards':
                    from jra_race_card_detail import parse_race_card_detail
                    detail=parse_race_card_detail(s3.encode('utf-8'),'text/html; charset=utf-8')
                else:
                    from jra_same_day_results import parse_result_detail
                    detail=parse_result_detail(s3.encode('utf-8'),'text/html; charset=utf-8')
                record['runners']=[{k:r.get(k) for k in ('runner_id','horse_no','horse_name','status','horse_profile_token','sire','dam','damsire')}
                                   for r in detail['runners']]
                # Bind result anchors to the official row, not to an opaque-ID guess.
                links={}
                for link in BeautifulSoup(s3,'html.parser').select('a[href]'):
                    match=re.search(r'accessU\.html\?CNAME=(pw01dud[^"\'&<>\s]+)',link['href'])
                    if match:
                        links.setdefault(link.get_text(' ',strip=True),set()).add(urllib.parse.unquote(match[1]))
                for row in record['runners']:
                    values=links.get(row.get('horse_name'),set())
                    if not row.get('horse_profile_token') and len(values)==1:
                        row['horse_profile_token']=next(iter(values))
                record['universe_status']='OBSERVED_OFFICIAL'
            except ValueError as exc:
                record['universe_error']=str(exc)[:160]
            client.race_observations.append(record)
            for tok in re.findall(r"accessU\.html\?CNAME=(pw01dud[^\"'&<>\s]+)", s3):
                tok = urllib.parse.unquote(tok)
                if tok not in out:
                    out.append(tok)
                if stop_after is not None and len(out) >= stop_after:
                    completed = True
                    break
            if completed:
                break
        if completed:
            break
    return out


def harvest_day(race_date: str, *, mode: str = "results", max_horses: int | None = None,
                delay: float = 1.0, start_index: int = 0,
                start_race: int = 0, max_races: int | None = None,
                existing_horses: dict | None = None) -> Dict[str, Any]:
    started = _dt.datetime.now(_dt.timezone.utc).isoformat()
    client = _Client(delay=delay,stop_on_access_denied=True)
    if start_race < 0 or (max_races is not None and not 1 <= max_races <= 36):
        raise ValueError("JRA_HARVEST_RACE_WINDOW_INVALID")
    if start_index < 0 or (max_horses is not None and not 1 <= max_horses <= 1000):
        raise ValueError("JRA_HARVEST_RANGE_INVALID")
    tokens = horse_tokens_for_day(
        client, race_date, mode=mode,
        stop_after=start_index + max_horses if max_horses is not None else None,
        start_race=start_race, max_races=max_races)
    total_tokens = len(tokens)
    if total_tokens == 0:
        if start_race > 0 and start_race >= client.scanned_race_count > 0:
            return {"profile": PROFILE, "race_date": race_date, "mode": mode,
                    "exhausted_window": True,
                    "observed_races": client.scanned_race_count,
                    "start_race": start_race, "horse_count": 0}
        raise ValueError("JRA_HARVEST_EMPTY_RACE_UNIVERSE")
    tokens = tokens[start_index:start_index + max_horses if max_horses is not None else None]
    if not tokens:
        raise ValueError("JRA_HARVEST_EMPTY_RANGE")
    horses, errors = [], []
    access_refused = False
    reused = 0
    for tok in tokens:
        try:
            cached=(existing_horses or {}).get(_sha(tok.encode()))
            if cached:
                references=[r for race in getattr(client,'race_observations',[]) for r in race['runners']
                            if r.get('horse_profile_token')==tok]
                if any(r.get(k) and cached.get(k) and r[k]!=cached[k]
                       for r in references for k in ('horse_name','sire','dam','damsire')):
                    raise ValueError('OFFICIAL_CACHED_PROFILE_CARD_IDENTITY_CONFLICT')
                horses.append(dict(cached));reused+=1
                continue
            raw, ct = client.raw_get("/JRADB/accessU.html?" + urllib.parse.urlencode({"CNAME": tok}))
            dec = _decode(raw, ct)
            ped = parse_horse_pedigree(dec)
            hist = parse_horse_history(raw, ct)
            if not ped.get("horse_name") or not ped.get("sire") or not ped.get("dam"):
                raise ValueError("PEDIGREE_IDENTITY_MISSING:"+
                                 "|".join(f"{k}={bool(ped.get(k))}" for k in ("horse_name","sire","dam","damsire"))+
                                 ":horse_profile_hash="+hashlib.sha256(tok.encode()).hexdigest()[:10])
            references=[r for race in getattr(client,'race_observations',[]) for r in race['runners']
                        if r.get('horse_profile_token')==tok]
            if any(r.get(k) and ped.get(k) and r[k]!=ped[k]
                   for r in references for k in ('horse_name','sire','dam','damsire')):
                raise ValueError('OFFICIAL_PROFILE_CARD_IDENTITY_CONFLICT')
            horses.append({**ped, "runs": hist.get("runs") or [], "raw_sha256": _sha(raw),
                           "profile_token_sha256": hashlib.sha256(tok.encode()).hexdigest(),
                           "official_profile_navigation_token":tok,
                           "profile_identity_kind":"OBSERVED_NAVIGATION_NOT_PERMANENT_REGISTRY_ID",
                           "official_permanent_horse_id":None,
                           "observed_at":_dt.datetime.now(_dt.timezone.utc).isoformat()})
        except Exception as exc:  # recorded, never fabricated
            errors.append(f"{type(exc).__name__}:{exc}"[:200])
            if isinstance(exc,urllib.error.HTTPError) and exc.code in (403,429):
                access_refused=True
                break
    out = {"profile": PROFILE, "official": True, "source": "www.jra.go.jp", "race_date": race_date,
           "mode": mode, "collection_started_at":started,
           "harvested_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
           "access_refused":access_refused,
           "reused_profile_count":reused,
           "race_observations":getattr(client,'race_observations',[]),
           "start_index": start_index, "start_race": start_race,
           "max_races": max_races,
           "discovery_complete": max_horses is None and max_races is None,
           "total_discovered_tokens": total_tokens if max_horses is None and max_races is None else None,
           "selected_token_count": len(tokens),
           "horse_token_count": len(tokens), "horse_count": len(horses), "horses": horses,
           "errors": errors,
           "coverage_class": "FULL" if not errors and len(horses)==len(tokens) else "PARTIAL_WITH_EXPLICIT_MISSINGNESS"}
    out["sha256"] = hashlib.sha256(json.dumps(out, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return out


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, action="append")
    ap.add_argument("--mode", choices=["results", "cards"], default="results")
    ap.add_argument("--out-dir", default="runtime/pedigree_corpus")
    ap.add_argument("--max-horses", type=int)
    ap.add_argument("--start-index", type=int, default=0)
    ap.add_argument("--start-race", type=int, default=0)
    ap.add_argument("--max-races", type=int)
    ap.add_argument("--delay", type=float, default=1.0)
    a = ap.parse_args()
    for day in a.date:
        res = harvest_day(day, mode=a.mode, max_horses=a.max_horses,
                          delay=a.delay, start_index=a.start_index,
                          start_race=a.start_race, max_races=a.max_races)
        if res.get("exhausted_window"):
            print(json.dumps(res, ensure_ascii=False))
            continue
        suffix = (f"-race{a.start_race}-r{a.max_races}" if a.max_races is not None else "")
        if a.start_index or a.max_horses:
            suffix += f"-offset{a.start_index}-n{a.max_horses}"
        p = Path(a.out_dir) / f"{day.replace('-', '')}-{a.mode}{suffix}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        if res["errors"] or res["horse_count"] != res["horse_token_count"]:
            print("JRA_HARVEST_DIAGNOSTIC_ERRORS="+json.dumps(res["errors"][:6],ensure_ascii=False))
            # A small number of honestly missing profiles can be included in a
            # bounded cohort with explicit coverage, never represented as full.
            # Substantial collection loss remains fatal and produces no corpus.
            if res["horse_token_count"] < 5 or res["horse_count"] / res["horse_token_count"] < 0.90:
                raise SystemExit(f"JRA_HARVEST_INCOMPLETE:{day}:{len(res['errors'])} errors; {res['horse_count']}/{res['horse_token_count']} parsed")
        if p.exists():
            raise SystemExit("JRA_HARVEST_IMMUTABLE_ALREADY_EXISTS:" + str(p))
        p.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps({k: res[k] for k in ("race_date", "mode", "horse_token_count", "horse_count")}
                         | {"errors": len(res["errors"])}, ensure_ascii=False))
