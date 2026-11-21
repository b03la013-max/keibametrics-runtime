"""岩手 free newspaper marks (勝ちそーチャンネル tesio.jp) -> TM-like consensus index for 水沢 / 盛岡.

Owner 2026-11-21 22:34 / 22:41 JST: find free sources for venues Keibabook does not cover; free only.
Access policy: tesio.jp robots.txt allows crawling (only /wp-admin/ disallowed); the site states no
reproduction ban beyond its copyright line. We fetch one page per race, honestly identified, with spacing,
and never retry around HTTP errors. The raw marks stay in the PRIVATE cache; only the derived in-race
index (52 + 8z, same scale and point table as the Keibabook TM index) enters the formal record.
"""
import html
import json
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from runtime.capture.keibabook_local_ingest import MARK_POINTS, _zidx

VENUES = {'MIZ', 'MOR'}
UA = 'KeibaMetrics-LOCAL/1.0 (personal research; polite single fetch per race)'
GAP_S = 2.0
_last = [0.0]


def url(race_date, race_no):
    return f"https://www.tesio.jp/{race_date.replace('-', '')}-{int(race_no):02d}/"


def parse(page):
    """-> {horse_no: [mark, mark, mark]} from table.yosou-data (rowspan-safe: the last 7 cells are
    馬番, 馬名, 重量, 騎手, three marks)."""
    m = re.search(r'<table[^>]*yosou-data[^>]*>(.*?)</table>', page, re.S)
    if not m:
        return {}
    out = {}
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', m.group(1), re.S):
        cells = [html.unescape(re.sub(r'<[^>]+>|\s+', '', c)) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.S)]
        if len(cells) >= 7 and cells[-7].isdigit():
            out[int(cells[-7])] = cells[-3:]
    return out


def tm_index(marks):
    score = {no: sum(MARK_POINTS.get(c[:1], 0) for c in ms) for no, ms in marks.items()}
    return _zidx(score) if any(score.values()) else {}


def fetch(race_date, race_no, timeout=15):
    wait = GAP_S - (time.monotonic() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.monotonic()
    req = urllib.request.Request(url(race_date, race_no), headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', 'replace')


def cache_path(private_dir, race_date, venue_id, race_no):
    return Path(private_dir) / 'tesio' / race_date / f'{venue_id}_{int(race_no):02d}.json'


def for_race(private_dir, race_date, venue_id, race_no, deadline, fetcher=fetch):
    """-> ({horse_no: {'tm': idx}} or None, meta). Uses a cached capture taken before the cutoff, else
    one fresh fetch (rejected when it lands after the cutoff)."""
    if venue_id not in VENUES:
        return None, {'status': 'NOT_APPLICABLE'}
    p = cache_path(private_dir, race_date, venue_id, race_no)
    try:
        c = json.loads(p.read_text())
        if datetime.fromisoformat(c['fetched_at']) < deadline:
            idx = tm_index({int(k): v for k, v in c['marks'].items()})
            return ({no: {'tm': v, 'src': 'tesio'} for no, v in idx.items()} or None,
                    {'status': 'USED_CACHE' if idx else 'NO_MARKS', 'fetched_at': c['fetched_at'], 'source': 'tesio.jp'})
    except (OSError, ValueError, KeyError):
        pass
    try:
        page = fetcher(race_date, race_no)
    except Exception as exc:          # HTTP errors are final: no retry, no workaround
        return None, {'status': 'UNAVAILABLE', 'error': f'{type(exc).__name__}:{str(exc)[:100]}'}
    at = datetime.now(timezone.utc).astimezone(deadline.tzinfo)
    if at >= deadline:
        return None, {'status': 'FETCHED_AFTER_CUTOFF'}
    marks = parse(page)
    if not marks:
        return None, {'status': 'NOT_PUBLISHED'}
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({'fetched_at': at.isoformat(), 'url': url(race_date, race_no),
                             'marks': {str(k): v for k, v in marks.items()}}, ensure_ascii=False))
    idx = tm_index(marks)
    return ({no: {'tm': v, 'src': 'tesio'} for no, v in idx.items()} or None,
            {'status': 'USED_FRESH' if idx else 'NO_MARKS', 'fetched_at': at.isoformat(), 'source': 'tesio.jp'})
