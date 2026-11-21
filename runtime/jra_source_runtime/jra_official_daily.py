"""JRA official race-day notices: 馬場情報 and 開催お知らせ (変更情報). RECORD ONLY.

Owner approval 2026-11-21 10:59. Collected from www.jra.go.jp inside the race-day autopilot loop
(at most every FETCH_EVERY seconds, pages fetched SLEEP seconds apart, honest User-Agent). Nothing
here changes a prediction, a ticket, or a number:
  * 馬場情報: per venue page (/keiba/baba/index.html, index2.html, index3.html) for going, weather,
    使用コース, 芝丈, 芝の状態; the page's own data files _data_cushion.html (芝クッション値) and
    _data_moist.html (含水率 芝/ダート × ゴール前/4コーナー) for every venue with measurement times.
    Recorded for the BVI environment fields (cushion_value / moisture_pct) as evidence only.
  * 開催お知らせ (/JRADB/accessI.html): per race 出走取消・競走除外・騎手変更・発走時刻変更 etc. This is
    the input the Rev2 pre-post re-check (Owner 2026-11-21 10:19, implementation from 11/26) will read.
Output: runtime/jra_official_daily/<date>.json — a list of observations, a new one appended only
when the parsed content changed (identical re-reads keep the last observed_at fresh).
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

PROFILE = "KM-JRA-OFFICIAL-DAILY-v1"
BASE = "https://www.jra.go.jp"
UA = "KeibaMetrics-runtime/1.0 (+https://github.com/b03la013-max/keibametrics-runtime; race-day notices, low rate)"
BABA_PAGES = ("/keiba/baba/index.html", "/keiba/baba/index2.html", "/keiba/baba/index3.html")
CUSHION_DATA = "/keiba/baba/_data_cushion.html"   # every venue, recent measurement history
MOIST_DATA = "/keiba/baba/_data_moist.html"
NOTICE_CNAME = "pw01ide01/4F"
FETCH_EVERY = 1200
SLEEP = 3.0
JST = _dt.timezone(_dt.timedelta(hours=9))
_LAST = {"at": 0.0}


def _fetch(path, data=None):
    req = urllib.request.Request(BASE + path, data=data, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        cs = r.headers.get_content_charset()
    for enc in ([cs] if cs else []) + ["utf-8", "shift_jis", "cp932"]:
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("cp932", errors="replace")


class _Text(HTMLParser):
    """Visible text with one line per block element; script/style dropped."""
    BLOCK = {"p", "div", "li", "tr", "td", "th", "h1", "h2", "h3", "h4", "dt", "dd", "caption", "option", "br", "table"}

    def __init__(self):
        super().__init__(); self.out = []; self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        elif tag in self.BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1
        elif tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, d):
        if not self.skip:
            self.out.append(d)


def text_lines(html):
    p = _Text(); p.feed(html)
    return [s for s in (re.sub(r"[ \t　]+", " ", x).strip() for x in "".join(p.out).split("\n")) if s]


def _after(lines, label, pred, start=0, span=40):
    try:
        i = lines.index(label, start)
    except ValueError:
        return None, -1
    for j in range(i + 1, min(len(lines), i + span)):
        if pred(lines[j]):
            return lines[j], j
    return None, -1


def parse_baba(html):
    L = text_lines(html)
    meet = next((x for x in L if re.match(r"第\d+回\S+競馬第\d+日", x)), None)
    cond_at = next((m.group(1) for x in L for m in [re.match(r"馬場状態（(.+?)現在）", x)] if m), None)
    weather = next((x.split("：", 1)[1] for x in L if x.startswith("天候：")), None)
    going = {}
    c0 = next((i for i, x in enumerate(L) if x.startswith("馬場状態（")), 0)
    for lab, key in (("芝", "turf"), ("ダート", "dirt")):
        v, _ = _after(L, lab, lambda s: s in ("良", "稍重", "重", "不良"), start=c0, span=4)
        going[key] = v
    out = {"meeting": meet, "condition_at": cond_at, "weather": weather, "going": going}
    for lab, key in (("使用コース", "course_in_use"), ("芝の状態", "turf_condition"), ("注記：", "note")):
        if lab.endswith("："):
            out[key] = next((x[len(lab):] for x in L if x.startswith(lab)), None)
        else:
            v, _ = _after(L, lab, lambda s: len(s) > 1, span=3)
            out[key] = v
    t = next((i for i, x in enumerate(L) if x.startswith("芝コース") and "芝丈" in x), -1)
    if t >= 0:
        k = L.index("芝", t) if "芝" in L[t:] else -1
        out["turf_length_cm"] = {"noshiba": L[k + 1], "yoshiba": L[k + 2]} if k > 0 and k + 2 < len(L) else None
    return out


_UNIT = re.compile(r'<div class="unit">(.*?)(?=<div class="unit">|</div><!-- /\[#rc|$)', re.S)
_VENUE = re.compile(r'<div id="rc([A-Z])" title="([^"]+)">(.*?)</div><!-- /\[#rc\1\] -->', re.S)


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def parse_cushion(html):
    """_data_cushion.html -> {venue: [{measured_at, value}, ...]} newest first."""
    out = {}
    for _, venue, body in _VENUE.findall(html):
        rows = []
        for u in _UNIT.findall(body):
            t = re.search(r'class="time">([^<]+)<', u); v = re.search(r'class="cushion">([^<]*)<', u)
            if t:
                rows.append({"measured_at": t.group(1).strip(), "value": _num(v.group(1).strip()) if v else None})
        out[venue] = rows
    return out


def parse_moist(html):
    """_data_moist.html -> {venue: [{measured_at, turf:{goal_pct,corner4_pct,band}, dirt:{...}, note}]}."""
    out = {}
    for _, venue, body in _VENUE.findall(html):
        rows = []
        for u in _UNIT.findall(body):
            t = re.search(r'class="time">([^<]+)<', u)
            if not t:
                continue
            row = {"measured_at": t.group(1).strip()}
            for surf in ("turf", "dirt"):
                m = re.search(r'<div class="%s">(.*?)</div>' % surf, u, re.S)
                if not m:
                    row[surf] = None; continue
                g = re.search(r'class="mg"(?: data-condition="(\w*)")?>([^<]*)<', m.group(1))
                c = re.search(r'class="m4c"(?: data-condition="(\w*)")?>([^<]*)<', m.group(1))
                row[surf] = {"goal_pct": _num(g.group(2)) if g else None, "corner4_pct": _num(c.group(2)) if c else None,
                             "band": (g.group(1) if g else None) or None}
            n = re.search(r'<li>注記：([^<]*)</li>', u)
            row["note"] = n.group(1).strip() if n else None
            rows.append(row)
        out[venue] = rows
    return out


class _Notice(HTMLParser):
    """Tables 'basic' with a caption like 5回京都5日; rows: th race number, td dl(dt type, dd detail)."""

    def __init__(self):
        super().__init__(); self.meetings = []; self.cur = None; self.cell = None; self.buf = []; self.row = None
        self.h2 = None; self.in_h2 = False; self.dates = []

    def handle_starttag(self, tag, attrs):
        if tag == "h2":
            self.in_h2 = True; self.buf = []
        elif tag == "caption":
            self.cell = "caption"; self.buf = []
        elif tag == "tr" and self.cur is not None:
            self.row = {"no": None, "items": []}
        elif tag == "th" and self.row is not None:
            self.cell = "th"; self.buf = []
        elif tag in ("dt", "dd") and self.row is not None:
            self.cell = tag; self.buf = []

    def handle_endtag(self, tag):
        txt = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        if tag == "h2" and self.in_h2:
            self.in_h2 = False
            if "開催情報" in txt:
                self.h2 = txt.split()[0]
        elif tag == "caption" and self.cell == "caption":
            self.cell = None
            if re.fullmatch(r"\d+回\S+\d+日", txt):
                self.cur = {"date_label": self.h2, "meeting": txt, "races": {}}; self.meetings.append(self.cur)
            else:
                self.cur = None
        elif tag == "th" and self.cell == "th":
            self.cell = None
            if txt.isdigit():
                self.row["no"] = int(txt)
        elif tag == "dt" and self.cell == "dt":
            self.cell = None; self.row["items"].append({"type": txt, "detail": None})
        elif tag == "dd" and self.cell == "dd":
            self.cell = None
            if self.row["items"]:
                it = self.row["items"][-1]; it["detail"] = txt
                m = re.match(r"(\d+)番\s*(\S+)", txt)
                if m:
                    it.update(horse_no=int(m.group(1)), horse_name=m.group(2))
        elif tag == "tr" and self.row is not None:
            if self.cur is not None and self.row["no"]:
                self.cur["races"][str(self.row["no"])] = self.row["items"]
            self.row = None
        elif tag == "table":
            self.cur = None

    def handle_data(self, d):
        if self.in_h2 or self.cell:
            self.buf.append(d)


def parse_notices(html):
    p = _Notice(); p.feed(html)
    return {"meetings": p.meetings}


def collect(fetch=_fetch, sleep=time.sleep):
    obs = {"baba": [], "cushion": None, "moisture": None, "notices": None, "errors": []}
    for key, path, parse in (("cushion", CUSHION_DATA, parse_cushion), ("moisture", MOIST_DATA, parse_moist)):
        try:
            obs[key] = parse(fetch(path))
        except Exception as e:  # noqa: BLE001
            obs["errors"].append({"url": BASE + path, "error": type(e).__name__ + ":" + str(e)[:200]})
        sleep(SLEEP)
    for path in BABA_PAGES:
        try:
            obs["baba"].append({"url": BASE + path, **parse_baba(fetch(path))})
        except Exception as e:  # noqa: BLE001 — record and continue; nothing downstream depends on it
            obs["errors"].append({"url": BASE + path, "error": type(e).__name__ + ":" + str(e)[:200]})
        sleep(SLEEP)
    try:
        html = fetch("/JRADB/accessI.html", urllib.parse.urlencode({"cname": NOTICE_CNAME}).encode())
        obs["notices"] = {"url": BASE + "/JRADB/accessI.html", **parse_notices(html)}
    except Exception as e:  # noqa: BLE001
        obs["errors"].append({"url": BASE + "/JRADB/accessI.html", "error": type(e).__name__ + ":" + str(e)[:200]})
    return obs


def record(root: Path, race_date: str, now=None, fetch=_fetch, sleep=time.sleep, force=False):
    """Collect at most every FETCH_EVERY seconds; append when content changed. Returns the path or None."""
    if not force and time.monotonic() - _LAST["at"] < FETCH_EVERY and _LAST["at"]:
        return None
    _LAST["at"] = time.monotonic()
    now = now or _dt.datetime.now(JST)
    obs = collect(fetch, sleep)
    body = {k: obs[k] for k in ("baba", "cushion", "moisture", "notices")}
    digest = hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    path = root / "runtime" / "jra_official_daily" / f"{race_date}.json"
    doc = json.loads(path.read_text()) if path.exists() else {
        "profile": PROFILE, "race_date": race_date, "record_only": True, "production_effect": "NONE",
        "source": "www.jra.go.jp 馬場情報 / 開催お知らせ", "observations": []}
    last = doc["observations"][-1] if doc["observations"] else None
    if last and last.get("sha256") == digest:
        last["last_seen_at"] = now.isoformat(timespec="seconds")
        if obs["errors"]:
            last["errors"] = obs["errors"]
    else:
        doc["observations"].append({"observed_at": now.isoformat(timespec="seconds"),
                                    "last_seen_at": now.isoformat(timespec="seconds"),
                                    "sha256": digest, **obs})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    return path


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--date", required=True); ap.add_argument("--repo-root", default=".")
    a = ap.parse_args()
    print(record(Path(a.repo_root).resolve(), a.date, force=True))
