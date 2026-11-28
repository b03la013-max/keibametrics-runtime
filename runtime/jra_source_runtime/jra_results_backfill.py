"""JRA official historical results backfill (Owner decision 2026-11-20 02:03, confirmed 2026-11-21 13:11).

Class: HISTORICAL_BACKFILL_LEARNING (not Forward OOS). It feeds the central-version statistical tables
(jra_hist_stats.py). Nothing here changes Production numbers, roles, tickets or capital; adoption of any
finding goes through the existing pre-registration + forward OOS + Owner decision path.

Source and manners (checked 2026-11-25 and recorded in OUT/source_policy.json):
  * www.jra.go.jp only. robots.txt = "User-agent: * / Disallow:" (nothing disallowed). The site terms
    (/use/) restrict secondary use of copyrighted media; we keep FACTS only (positions, times, weights,
    names), never raw HTML, images or video.
  * honest User-Agent, no credentials, no proxy / IP rotation, one request at a time with DELAY seconds
    between requests (>= 3 s);
  * 403 / 429 / 503: stop immediately, hold HOLD_SECONDS (30 min) and do NOT retry; every refusal is
    appended to state.refusals (the same discipline as the LOCAL rakuten.py / backfill.py worker);
  * runs at night on the Owner's Mac runner (km-jra), stops at a deadline, resumes from the cursor.

Navigation reuses the official archive flow already used by the pedigree harvest
(calendar -> pw01skl archive month -> pw01srl day -> pw01sde result).

  python runtime/jra_source_runtime/jra_results_backfill.py run --until 2023-12-01 --minutes 300
  python runtime/jra_source_runtime/jra_results_backfill.py status
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
import http.client
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source_acquisition import _decode  # noqa: E402
from jra_pedigree_harvest import archive_month_token  # noqa: E402

PROFILE = "KM-JRA-OFFICIAL-RESULTS-BACKFILL-v1.0-20261125"
CLASS = "HISTORICAL_BACKFILL_LEARNING (not Forward OOS)"
BASE = "https://www.jra.go.jp"
UA = "KeibaMetrics-JRA-Results-Backfill/1.0 (personal non-commercial research; +https://github.com/b03la013-max)"
DELAY = 3.0
HOLD_SECONDS = 1800
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("KM_JRA_RESULTS_HISTORY_OUT") or ROOT / "runtime/jra_results_history")
PAGE = "/JRADB/accessS.html"
VENUES = {"01": "SPP", "02": "HKD", "03": "FKS", "04": "NGT", "05": "TKY",  # canonical (jra_race_day_resolver)
          "06": "NKY", "07": "CHK", "08": "KYO", "09": "HSN", "10": "KKR"}
ENTRY = re.compile(r"doAction\('/JRADB/accessS\.html'\s*,\s*'([^']+)'\)")


class Refused(Exception):
    """403 / 429 / 503: stop now, hold, never retry within the hold."""


class Client:
    def __init__(self, delay=DELAY, opener=None, clock=time.monotonic, sleep=time.sleep):
        if delay < 3.0:
            raise ValueError("JRA_BACKFILL_DELAY_TOO_SHORT")
        import http.cookiejar
        self.delay, self.clock, self.sleep = delay, clock, sleep
        self.opener = opener or urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.last = None
        self.requests = 0

    def _open(self, path, data=None):
        if self.last is not None:
            wait = self.delay - (self.clock() - self.last)
            if wait > 0:
                self.sleep(wait)
        req = urllib.request.Request(BASE + path, data=data, headers={"User-Agent": UA, "Accept-Language": "ja"})
        self.last = self.clock()
        self.requests += 1
        try:
            with self.opener.open(req, timeout=30) as r:
                if urllib.parse.urlsplit(r.geturl()).hostname != "www.jra.go.jp":
                    raise ValueError("JRA_BACKFILL_FOREIGN_HOST")
                raw = r.read(6_000_001)
                if len(raw) > 6_000_000:
                    raise ValueError("JRA_BACKFILL_PAGE_TOO_LARGE")
                return _decode(raw, r.headers.get("content-type", ""))
        except urllib.error.HTTPError as e:
            if e.code in (403, 429, 503):
                raise Refused(f"HTTP_{e.code}:{path}") from None
            raise

    def get(self, path):
        return self._open(path)

    def post(self, token):
        return self._open(PAGE, urllib.parse.urlencode({"cname": token}).encode())


def _calendar(d: dt.date) -> str:
    return f"/keiba/calendar{d.year}/{d.year}/{d.month}/{d.strftime('%m%d')}.html"


def _entry_day(today: dt.date | None = None) -> dt.date:
    """Most recent Sunday strictly before today: JRA has a calendar page only for race days, and a
    non-race day's page answers 403 (first nightly run 2026-11-26 asked for Thursday 11/26)."""
    t = today or dt.date.today()
    back = (t.weekday() + 1) % 7 or 7  # Mon=0 .. Sun=6 -> days back to the previous Sunday
    return t - dt.timedelta(days=back)


def month_days(client, month: dt.date) -> dict:
    """{YYYYMMDD: [pw01srl day tokens]} for one archive month (observed tokens only)."""
    cal = client.get(_calendar(_entry_day()))
    archive = next((t for t in ENTRY.findall(cal) if t.startswith("pw01skl")), None)
    if archive is None:
        raise ValueError("JRA_BACKFILL_ARCHIVE_ENTRY_NOT_OBSERVED")
    selector = client.post(archive)
    page = client.post(archive_month_token(selector, month.replace(day=1).isoformat()))
    days = {}
    for tok in sorted(set(re.findall(r"pw01srl\d{2}\d{10}\d{8}/[0-9A-Fa-f]{2}", page))):
        days.setdefault(tok[-11:-3], []).append(tok)
    return days


def _txt(cell):
    return re.sub(r"\s+", " ", cell.get_text(" ", strip=True)).strip()


def _int(s):
    m = re.search(r"-?\d+", s or "")
    return int(m.group(0)) if m else None


def parse_result_page(html: str) -> dict:
    """Facts only from one official result page."""
    soup = BeautifulSoup(html, "html.parser")
    head = re.sub(r"\s+", " ", (soup.select_one(".race_header") or soup).get_text(" ", strip=True))
    race = {}
    m = re.search(r"(\d+)回(\S+?)(\d+)日", head)
    if m:
        race.update(kai=int(m[1]), venue_name=m[2], nichi=int(m[3]))
    m = re.search(r"天候\s*(\S+?)\s*(芝|ダート|障害)\s*(良|稍重|重|不良)", head)
    if m:
        race.update(weather=m[1], going_surface=m[2], going=m[3])
    m = re.search(r"コース[:：]\s*([\d,]+)\s*メートル\s*[（(]([^）)]+)[）)]", head)
    if m:
        race.update(distance_m=int(m[1].replace(",", "")), course=m[2])
    m = re.search(r"発走時刻[:：]\s*(\d{1,2})時(\d{2})分", head)
    if m:
        race["post_hhmm"] = f"{int(m[1]):02d}:{int(m[2]):02d}"
    def sel(q):
        e = soup.select_one(".race_header " + q)
        return _txt(e) if e else None
    race.update(race_name=sel(".race_title .race_name"), age_condition=sel(".race_title .type .category"),
                class_text=sel(".race_title .type .class"), rule=sel(".race_title .type .rule"),
                weight_rule=sel(".race_title .type .weight"))
    race["obstacle"] = "障害" in (race.get("going_surface") or "") or "障害" in (race.get("course") or "")
    table = None
    for t in soup.find_all("table"):
        h = [re.sub(r"\s+", "", _txt(c)) for c in (t.find("tr") or []).find_all(["th", "td"])] if t.find("tr") else []
        if "着順" in h and "馬番" in h and "馬名" in h:
            table, header = t, h
            break
    if table is None:
        raise ValueError("JRA_BACKFILL_RESULT_TABLE_NOT_FOUND")
    col = {k: next((i for i, x in enumerate(header) if k in x), None) for k in
           ("着順", "枠", "馬番", "馬名", "性齢", "負担重量", "騎手", "タイム", "着差", "コーナー", "上り", "馬体重", "調教師", "人気")}
    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all(["td", "th"])
        def c(k):
            i = col[k]
            return cells[i] if i is not None and i < len(cells) else None
        if not c("馬番") or _int(_txt(c("馬番"))) is None:
            continue
        fin = _txt(c("着順")) if c("着順") else ""
        frame = None
        if c("枠"):
            img = c("枠").find("img")
            frame = _int((img.get("alt") if img else "") or _txt(c("枠")))
        sexage = _txt(c("性齢")) if c("性齢") else ""
        weight = _txt(c("馬体重")) if c("馬体重") else ""
        wm = re.match(r"(\d+)\(([+-]?\d+|前計不|計不)\)", weight.replace(" ", ""))
        rows.append({
            "finish": int(fin) if fin.isdigit() else None, "finish_label": fin,
            "frame": frame, "horse_no": _int(_txt(c("馬番"))), "horse_name": _txt(c("馬名")),
            "sex": sexage[:1] or None, "age": _int(sexage[1:]),
            "carried_kg": float(_txt(c("負担重量"))) if c("負担重量") and re.fullmatch(r"\d+(\.\d)?", _txt(c("負担重量"))) else None,
            "jockey": _txt(c("騎手")) if c("騎手") else None,
            "time": _txt(c("タイム")) or None if c("タイム") else None,
            "margin": _txt(c("着差")) or None if c("着差") else None,
            "passing": [int(x) for x in re.findall(r"\d{1,2}", _txt(c("コーナー")))] if c("コーナー") else [],
            "last3f": float(_txt(c("上り"))) if c("上り") and re.fullmatch(r"\d+\.\d", _txt(c("上り"))) else None,
            "body_weight": int(wm[1]) if wm else None,
            "body_weight_change": int(wm[2]) if wm and re.fullmatch(r"[+-]?\d+", wm[2]) else None,
            "trainer": _txt(c("調教師")) if c("調教師") else None,
            "popularity": _int(_txt(c("人気"))) if c("人気") else None,
        })
    if not rows:
        raise ValueError("JRA_BACKFILL_RESULT_ROWS_EMPTY")
    race["field_size"] = len(rows)
    return {"race": race, "runners": rows}


def race_tokens(client, day_tokens: list, d8: str) -> list:
    out = set()
    for tok in day_tokens:
        page = client.post(tok)
        out |= set(re.findall(r"pw01sde\d{2}\d{12}" + d8 + r"/[0-9A-Fa-f]{2}", page))
    return sorted(out)


def race_key(token: str) -> dict:
    m = re.fullmatch(r"pw01sde\d{2}(\d{2})(\d{4})(\d{2})(\d{2})(\d{2})(\d{8})/[0-9A-Fa-f]{2}", token)
    if not m or m[1] not in VENUES:
        raise ValueError("JRA_BACKFILL_RACE_TOKEN_INVALID")
    return {"race_id": f"KM-JRA-{VENUES[m[1]]}-{m[6]}-R{int(m[5]):02d}", "venue_id": VENUES[m[1]],
            "race_no": int(m[5]), "date": m[6]}


def _state_path():
    return OUT / "state.json"


def load_state():
    p = _state_path()
    if p.exists():
        return json.loads(p.read_text())
    return {"profile": PROFILE, "done_days": [], "refusals": [], "hold_until": None, "months_seen": {}}


def save_state(s):
    OUT.mkdir(parents=True, exist_ok=True)
    _state_path().write_text(json.dumps(s, ensure_ascii=False, indent=1, sort_keys=True) + "\n")


def write_policy():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "source_policy.json").write_text(json.dumps({
        "profile": PROFILE, "class": CLASS, "checked_at": "2026-11-25T20:10:00+09:00",
        "robots_txt": {"url": BASE + "/robots.txt", "content": "User-agent: *\nDisallow: \n",
                       "meaning": "no path disallowed"},
        "site_terms": {"url": BASE + "/use/",
                       "summary": "Copyrighted media (video, audio, images, articles) may not be reused beyond private use / quotation without JRA permission. No clause on automated access. We store derived race facts only; no raw HTML, images or video.",
                       "action": "facts only; honest UA; >=3 s between requests; stop + 30 min hold on 403/429/503; night runs only"},
        "user_agent": UA, "delay_seconds": DELAY, "hold_seconds_on_refusal": HOLD_SECONDS,
        "owner_decision": "2026-11-20 02:03 JST (confirmed 2026-11-21 13:11)"}, ensure_ascii=False, indent=1) + "\n")


def run(until: dt.date, minutes: float, client=None, now=None, start: dt.date | None = None):
    state = load_state()
    now = now or dt.datetime.now(dt.timezone.utc)
    if state.get("hold_until") and now < dt.datetime.fromisoformat(state["hold_until"]):
        return {"status": "HOLD", "hold_until": state["hold_until"]}
    client = client or Client()
    deadline = time.monotonic() + minutes * 60
    month = (start or dt.date.today()).replace(day=1)
    done = set(state["done_days"])
    saved = 0
    try:
        while month >= until.replace(day=1) and time.monotonic() < deadline:
            key = month.strftime("%Y%m")
            days = month_days(client, month)
            state["months_seen"][key] = sorted(days)
            for d8 in sorted(days, reverse=True):
                if d8 in done or dt.date(int(d8[:4]), int(d8[4:6]), int(d8[6:])) < until:
                    continue
                if dt.date(int(d8[:4]), int(d8[4:6]), int(d8[6:])) >= dt.date.today():
                    continue
                if time.monotonic() >= deadline:
                    break
                races = []
                for tok in race_tokens(client, days[d8], d8):
                    k = race_key(tok)
                    html = client.post(tok)
                    try:
                        body = parse_result_page(html)
                    except ValueError as e:
                        body = {"parse_error": str(e)}
                    races.append({**k, **body, "page_sha256": hashlib.sha256(html.encode()).hexdigest()})
                p = OUT / d8[:4] / f"{d8[:4]}-{d8[4:6]}-{d8[6:]}.json"
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps({"profile": PROFILE, "class": CLASS, "date": d8, "source": BASE,
                                         "collected_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                                         "races": races}, ensure_ascii=False, indent=0) + "\n")
                done.add(d8); state["done_days"] = sorted(done); saved += 1
                save_state(state)
            month = (month - dt.timedelta(days=1)).replace(day=1)
    except (urllib.error.URLError, http.client.HTTPException, ConnectionError, TimeoutError) as e:
        # 2026-11-28: one RemoteDisconnected after ~3 h ended the night run as a failure. A transient
        # network stop is not a refusal: keep every finished day, record it, resume from the cursor next run.
        ev = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "reason": f"NETWORK:{type(e).__name__}:{str(e)[:120]}"}
        state["network_stops"] = (state.get("network_stops") or [])[-29:] + [ev]
        save_state(state)
        return {"status": "NETWORK_STOP_RESUME_NEXT_RUN", "saved_days": saved, "stop": ev, "requests": client.requests}
    except Refused as e:
        ev = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "reason": str(e)}
        state["refusals"] = (state.get("refusals") or [])[-29:] + [ev]
        state["hold_until"] = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=HOLD_SECONDS)).isoformat()
        save_state(state)
        return {"status": "REFUSED_HOLD", "saved_days": saved, "refusal": ev, "requests": client.requests}
    save_state(state)
    return {"status": "OK", "saved_days": saved, "done_days_total": len(done), "requests": client.requests,
            "reached": month.isoformat()}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("--until", default="2023-12-01"); r.add_argument("--minutes", type=float, default=300)
    sub.add_parser("status")
    a = ap.parse_args()
    write_policy()
    if a.cmd == "run":
        print(json.dumps(run(dt.date.fromisoformat(a.until), a.minutes), ensure_ascii=False))
    else:
        s = load_state()
        print(json.dumps({"done_days": len(s["done_days"]), "first": (s["done_days"] or [None])[0],
                          "last": (s["done_days"] or [None])[-1], "refusals": len(s["refusals"]),
                          "hold_until": s.get("hold_until")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
