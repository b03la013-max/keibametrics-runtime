"""水分ボンバーオンライン (SBO, nar.k-ba.net) reader — external auxiliary indicator.

Owner decision 2026-11-15 20:5x JST: adopt SBO now as a one-step-lower external
auxiliary indicator (VMI-equivalent, like JRA's TSL). Investigated before use:
free, no login, robots.txt empty (200), no terms page (disclaimer + copyright
only), data in static HTML: per horse 近走/距離/馬場/平均 index.

Rules kept here:
  * honest User-Agent, robots.txt re-read every 6 h and obeyed, >= 10 s between
    requests (persisted), 403/429/503 -> 30 min hold, never retried in a loop;
  * the raw page and SBO's own numbers / recommended bets are NOT committed to
    the public repository (copyright): only the page SHA-256, fetch time, the
    coverage count and our derived VMI-L value per horse are kept;
  * a snapshot fetched after the prediction cutoff is never used for that race.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from runtime.local_autopilot.rakuten import UA, SourceStop, nfkc, robots_allows, robots_policy

ORIGIN = 'https://nar.k-ba.net'
DELAY = 10.0
VENUE_CODE = {'MOR': 10, 'MIZ': 11, 'URW': 18, 'FNB': 19, 'OHI': 20, 'KAW': 21, 'KNZ': 22, 'KSM': 23,
              'NGY': 24, 'SON': 27, 'HMJ': 28, 'KOC': 31, 'SAG': 32, 'MON': 36}


class Client:
    def __init__(self, state_path):
        self.state_path = Path(state_path)
        try:
            self.state = json.loads(self.state_path.read_text())
        except (OSError, ValueError):
            self.state = {}
        self.requests = 0

    def _save(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(self.state, ensure_ascii=False, indent=1) + '\n')

    def _raw(self, url):
        if self.state.get('hold_until_epoch', 0) > time.time():
            raise SourceStop('SBO_HOLD')
        wait = self.state.get('last_request_epoch', 0) + self.state.get('delay', DELAY) - time.time()
        if wait > 0:
            time.sleep(wait)
        self.state['last_request_epoch'] = time.time()
        self.requests += 1
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,text/plain'})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                body, status = r.read(2_000_000), r.status
        except urllib.error.HTTPError as e:
            if e.code in (403, 429, 503):
                self.state['hold_until_epoch'] = time.time() + 1800
            self._save()
            raise SourceStop(f'SBO_HTTP_{e.code}') from e
        except OSError as e:
            self._save()
            raise SourceStop(f'SBO_NETWORK:{type(e).__name__}') from e
        self._save()
        if status != 200:
            raise SourceStop(f'SBO_HTTP_{status}')
        return body.decode('utf-8', errors='replace')

    def get(self, path):
        rb = self.state.get('robots')
        if not rb or time.time() - rb.get('at', 0) > 6 * 3600:
            rb = {'at': time.time(), 'text': self._raw(ORIGIN + '/robots.txt')}
            self.state['robots'] = rb
            self._save()
        pol = robots_policy(rb['text'], UA)
        self.state['delay'] = max(DELAY, pol['crawl_delay'] + 1)
        if not robots_allows(pol, path):
            raise SourceStop('SBO_ROBOTS_DISALLOWED:' + path)
        return self._raw(ORIGIN + path)


def _num(cell):
    m = re.match(r'\s*(\d+(?:\.\d+)?)\s*(?:\((\d+)\))?', cell)
    if not m:
        return None, 0
    n = int(m[2]) if m[2] is not None else 1
    return (float(m[1]) if n > 0 else None), n


def parse_table(html):
    """{horse_no: {'recent','dist','going','avg','n'}} from a table.html page."""
    m = re.search(r'<table id="table">(.*?)</table>', html, re.S)
    if not m:
        return {}
    out = {}
    for tr in re.findall(r'<tr>(.*?)</tr>', m[1], re.S):
        tds = [nfkc(re.sub(r'<[^>]+>', ' ', td)) for td in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
        if len(tds) < 10 or not tds[0].isdigit():
            continue
        recent, n1 = _num(tds[6])
        dist, _ = _num(tds[7])
        going, _ = _num(tds[8])
        avg, _ = _num(tds[9])
        out[int(tds[0])] = {'recent': recent, 'dist': dist, 'going': going, 'avg': avg, 'n': n1}
    return out


def vmi(table, active_nos):
    """VMI-L 0-100 within the race: 52 + 2 x (SBO avg - race mean), unknown = 52.
    Fixed prior (not fitted to any result)."""
    vals = {no: table[no]['avg'] for no in active_nos if no in table and table[no]['avg'] is not None}
    if len(vals) < 2:
        return {no: None for no in active_nos}
    mu = sum(vals.values()) / len(vals)
    return {no: (max(0.0, min(100.0, 52 + 2.0 * (vals[no] - mu))) if no in vals else None) for no in active_nos}


def snapshot(client, race_date, venue_id, race_no):
    code = VENUE_CODE.get(venue_id)
    if code is None:
        return {'status': 'VENUE_NOT_COVERED'}
    path = f"/{race_date.replace('-', '')}/{code}/{race_no}/table.html"
    html = client.get(path)
    table = parse_table(html)
    return {'status': 'OK' if table else 'NO_TABLE', 'path': path,
            'sha256': hashlib.sha256(html.encode()).hexdigest(), 'table': table}
