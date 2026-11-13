"""Rakuten keiba public race-card reader (all NAR venues) for the LOCAL autopilot.

keiba.rakuten.co.jp/robots.txt allows /race_card/ for all agents with
Crawl-Delay: 60, so this client:
  * sends an honest User-Agent, no credentials, no proxy/IP rotation;
  * reads robots.txt and refuses any disallowed path;
  * keeps >= 61 s between ANY two requests, persisted across workflow runs;
  * never retries on 403/429 (stops the tick), never stores raw HTML in Git.
One card page carries runners, odds/popularity, 連対時馬体重, current body
weight and the last five starts, so one request per race is enough.
"""
from __future__ import annotations

import json
import re
import time
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from html import unescape
from pathlib import Path

JST = timezone(timedelta(hours=9))
ORIGIN = 'https://keiba.rakuten.co.jp'
UA = 'KeibaMetrics-LOCAL-PrivateResearch/1.0 (+https://github.com/b03la013-max/keibametrics-runtime)'
DELAY = 61.0
# NAR baba codes -> (venue_id, name). 03 (ばんえい) is a separate system.
VENUES = {'10': ('MOR', '盛岡'), '11': ('MIZ', '水沢'), '18': ('URW', '浦和'), '19': ('FNB', '船橋'),
          '20': ('OHI', '大井'), '21': ('KAW', '川崎'), '22': ('KNZ', '金沢'), '23': ('KSM', '笠松'),
          '24': ('NGY', '名古屋'), '27': ('SON', '園田'), '28': ('HMJ', '姫路'), '31': ('KOC', '高知'),
          '32': ('SAG', '佐賀'), '36': ('MON', '門別')}


class SourceStop(RuntimeError):
    """Access refused / policy stop: end this tick, never retry immediately."""


def nfkc(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', unescape(s or ''))).strip()


def text(fragment):
    return nfkc(re.sub(r'<[^>]+>', ' ', re.sub(r'<br\s*/?>', '\n', fragment or '')))


def lines(fragment):
    raw = re.sub(r'\s+', ' ', fragment or '')
    raw = re.sub(r'<br\s*/?>', '\x00', raw)
    raw = re.sub(r'<[^>]+>', ' ', raw)
    return [nfkc(x) for x in unescape(raw).split('\x00') if nfkc(x)]


def robots_policy(text, ua):
    """RFC 9309: groups naming our product token apply; otherwise every '*'
    group (Rakuten splits '*' into two groups, which are merged)."""
    groups, cur, in_rules = [], None, False
    for raw in text.splitlines():
        line = raw.split('#', 1)[0].strip()
        if ':' not in line:
            continue
        k, v = [x.strip() for x in line.split(':', 1)]
        k = k.lower()
        if k == 'user-agent':
            if cur is None or in_rules:
                cur = {'agents': [], 'rules': [], 'delay': 0.0}
                groups.append(cur)
                in_rules = False
            cur['agents'].append(v.lower())
        elif cur is not None and k in ('allow', 'disallow', 'crawl-delay'):
            in_rules = True
            if k == 'crawl-delay':
                try:
                    cur['delay'] = max(cur['delay'], float(v))
                except ValueError:
                    pass
            elif v:
                cur['rules'].append((k == 'allow', v))
    token = ua.split('/')[0].lower()
    mine = [g for g in groups if any(a != '*' and a in token for a in g['agents'])]
    chosen = mine or [g for g in groups if '*' in g['agents']]
    return {'rules': [r for g in chosen for r in g['rules']],
            'crawl_delay': max([g['delay'] for g in chosen] + [0.0]),
            'groups': 'product' if mine else 'star'}


def robots_allows(policy, path):
    best = None
    for allow, pat in policy['rules']:
        anchored = pat.endswith('$')
        body = pat[:-1] if anchored else pat
        rx = '^' + re.escape(body).replace(r'\*', '.*') + ('$' if anchored else '')
        if re.match(rx, path):
            key = (len(body.replace('*', '')), allow)  # longest wins; Allow wins ties
            if best is None or key > best:
                best = key
    return True if best is None else best[1]


class Client:
    def __init__(self, state_path):
        self.state_path = Path(state_path)
        try:
            self.state = json.loads(self.state_path.read_text())
        except (OSError, ValueError):
            self.state = {}
        self.requests = 0
        self.wait_seconds = 0.0
        self.delay = DELAY

    def _save(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(self.state, ensure_ascii=False, indent=1) + '\n')

    def _raw(self, url):
        hold = self.state.get('hold_until_epoch', 0)
        if hold > time.time():
            raise SourceStop(f'SOURCE_HOLD_UNTIL:{hold:.0f}')
        wait = self.state.get('last_request_epoch', 0) + self.delay - time.time()
        if wait > 0:
            self.wait_seconds += wait
            time.sleep(wait)
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,text/plain'})
        self.state['last_request_epoch'] = time.time()
        self.requests += 1
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                body = r.read(3_000_000)
                status = r.status
        except urllib.error.HTTPError as e:
            if e.code in (403, 429, 503):  # access refused / throttled: back off 30 min, no retry
                self.state['hold_until_epoch'] = time.time() + 1800
            self._save()
            raise SourceStop(f'HTTP_{e.code}:{url}') from e
        except OSError as e:
            self._save()
            raise SourceStop(f'NETWORK:{type(e).__name__}:{url}') from e
        self._save()
        if status != 200:
            raise SourceStop(f'HTTP_{status}:{url}')
        return body.decode('utf-8', errors='replace')

    def _robots(self):
        rb = self.state.get('robots')
        if not rb or time.time() - rb.get('at', 0) > 6 * 3600:
            txt = self._raw(ORIGIN + '/robots.txt')
            rb = {'at': time.time(), 'text': txt}
            self.state['robots'] = rb
            self._save()
        return robots_policy(rb['text'], UA)

    def _allowed(self, path):
        policy = self._robots()
        self.delay = max(DELAY, policy['crawl_delay'] + 1)
        return robots_allows(policy, path)

    def get(self, path):
        if not self._allowed(path.split('?')[0]):
            raise SourceStop('ROBOTS_DISALLOWED:' + path)
        return self._raw(ORIGIN + path)


def day_venues(top_html, day):
    """Venue race-list ids for `day` from the public top page."""
    d = day.replace('-', '')
    out = {}
    for rid in re.findall(r'race_card/list/RACEID/(\d{18})', top_html):
        if rid.startswith(d) and rid[8:10] in VENUES and rid[-2:] == '00' and rid[8:] != '0000000000':
            out[rid[8:10]] = rid[:-2]
    return out


def parse_menu(card_html, prefix):
    races = []
    i = card_html.find('<ul class="raceNumber')
    seg = card_html[i:card_html.find('</ul>', i)]
    for rid, num, hhmm in re.findall(r'RACEID/(\d{18})">\s*<span class="num">(\d{1,2})R</span>\s*'
                                    r'<span class="time">(\d{1,2}:\d{2})</span>', seg):
        if rid.startswith(prefix):
            races.append((int(num), rid, hhmm))
    cur = re.search(r'<span class="selected">\s*<span class="num">(\d{1,2})R</span>\s*<span class="time">(\d{1,2}:\d{2})</span>', seg)
    if cur:
        races.append((int(cur[1]), prefix + f'{int(cur[1]):02d}', cur[2]))
    return sorted(set(races))


def parse_header(card_html):
    i = card_html.find('<div id="raceInfomation"')
    seg = card_html[i:i + 4000]
    venue = text(re.search(r'<span class="racePlace">(.*?)</span>', seg, re.S)[1]) if 'racePlace' in seg else ''
    num = re.search(r'<span class="num">(\d+)</span>R', seg)
    dist = re.search(r'class="distance">\s*([^<]*?)([\d,]{3,5})m', seg)
    going = re.search(r'<dt>(?:ダ|芝)：</dt><dd>(.*?)</dd>', seg)
    post = re.search(r'<dt>発走時刻</dt><dd>(\d{1,2}:\d{2})</dd>', seg)
    h2 = re.search(r'<h2>(.*?)</h2>', seg, re.S)
    return {'venue_name_page': venue, 'race_no': int(num[1]) if num else None,
            'surface': 'TURF' if dist and '芝' in dist[1] else 'DIRT',
            'distance': int(dist[2].replace(',', '')) if dist else None,
            'going': text(going[1]) if going else None, 'post': post[1] if post else None,
            'race_name': text(h2[1]) if h2 else ''}


def _int(s):
    m = re.search(r'-?\d+', s or '')
    return int(m[0]) if m else None


def parse_start(td):
    if 'class="place"' not in td:
        return None
    place = re.search(r'<span class="place">(.*?)</span>', td, re.S)
    going = re.search(r'<span class="stateInfo">(.*?)</span>', td, re.S)
    field = re.search(r'<span class="numberInfo">(\d+)頭</span>', td)
    body = td[td.find('</div>') + 6:]
    L = lines(body)
    out = {'finish': _int(text(place[1])) if place and text(place[1]).isdigit() else None,
           'finish_text': text(place[1]) if place else None,
           'going': text(going[1]) if going else None, 'field_size': int(field[1]) if field else None,
           'surface': 'DIRT', 'distance': None, 'content_positions': [], 'margin': None,
           'ride_body_weight': None, 'content_final3f': None, 'ride_jockey': None,
           'ride_popularity': None, 'race_name': '', 'venue': '', 'date': None}
    for k, ln in enumerate(L):
        m = re.fullmatch(r'(\S+)\s+(\d{2}\.\d{2}\.\d{2})', ln)
        if m and not out['date']:
            out['venue'], out['date'] = m[1], m[2]
            if k + 1 < len(L):
                out['race_name'] = L[k + 1]
            if k + 2 < len(L):
                out['race_name'] += ' ' + L[k + 2]
            continue
        m = re.search(r'(?:内|外)?(\d{3,4})(?:左|右|直)?(ダ|芝)\s*(\d+)人', ln)
        if m:
            out['distance'], out['surface'] = int(m[1]), 'TURF' if m[2] == '芝' else 'DIRT'
            out['ride_popularity'] = int(m[3])
            continue
        m = re.fullmatch(r'[☆▲△◇★]?(\S+?)\s+(\d{2}\.\d)', ln)
        if m and out['ride_jockey'] is None and out['distance']:
            out['ride_jockey'] = m[1]
            continue
        m = re.search(r'((?:\d+:)?\d{2}\.\d)\s*\((-?\d+\.\d)\)', ln)
        if m:
            out['content_time_text'] = m[1]
            out['margin'] = 0.0 if out['finish'] == 1 else abs(float(m[2]))
            continue
        m = re.search(r'(\d{2}\.\d)\s+(\d{3})k', ln)
        if m:
            out['content_final3f'], out['ride_body_weight'] = float(m[1]), int(m[2])
            continue
        if re.fullmatch(r'\d{1,2}(?:-\d{1,2}){0,3}', ln) and out['content_final3f'] is not None:
            out['content_positions'] = [int(x) for x in ln.split('-')]
    if out['field_size'] and out['content_positions']:
        out['content_positions'] = [p for p in out['content_positions'] if 1 <= p <= out['field_size']]
    return out


def parse_card(card_html):
    i = card_html.find('<tbody class="raceCard">')
    body = card_html[i:card_html.find('</tbody>', i)]
    blocks = re.split(r'<tr class="box\d+(?=[ "])', body)[1:]
    runners, excluded = [], []
    frame = None
    last_no = 0
    for blk in blocks:
        tds = re.findall(r'<t[dh][^>]*class="([^"]*)"[^>]*>(.*?)</t[dh]>', blk, re.S)
        cell = {}
        starts = []
        for cls, inner in tds:
            if cls.startswith('race'):
                starts.append(inner)
            else:
                cell.setdefault(cls.split()[0], inner)
        row_class = blk[:blk.find('>')]
        number = text(cell.get('number'))
        name_html = cell.get('name', '')
        nm = re.search(r'<span class="mainHorse">.*?>([^<]+)</a>', name_html, re.S)
        name = nfkc(nm[1]) if nm else text(name_html)[:20]
        nl = lines(name_html.split('<div class="append">')[0])
        sire = nl[0] if nl else None
        app = name_html.split('<div class="append">')[1] if '<div class="append">' in name_html else ''
        damsire = re.search(r'\(([^)]+)\)', text(app))
        rate = re.search(r'<span class="rate">(.*?人気.*?)</span>', app, re.S) or re.search(r'<span class="rate">(.*?)</span>\s*\d{4}/', app, re.S)
        rt = text(rate[1]) if rate else ''
        win = re.search(r'(\d+(?:\.\d+)?)', rt)
        pop = re.search(r'(\d+)人気', rt)
        prof = lines(cell.get('profile', ''))
        sexage = prof[0] if prof else ''
        age = re.match(r'[牡牝セ騸]\s*(\d+)', sexage)
        load = next((float(x) for x in prof if re.fullmatch(r'\d{2}\.\d', x)), None)
        jm = re.search(r'jockey/detail/JOCKEYID/\d+">([^<]+)</a>', cell.get('profile', ''))
        trainer = prof[-1] if prof and not prof[-1].startswith('【') else None
        wr = re.findall(r'\d{3}', text(cell.get('weight')))
        wd = lines(cell.get('weightDistance'))
        cur_bw = _int(wd[0]) if wd and re.fullmatch(r'\d{3}', wd[0]) else None
        chg = _int(wd[1]) if len(wd) > 1 and re.fullmatch(r'[+-]?\d+|±0', wd[1].replace('±0', '0')) else None
        cancelled = ('cancel' in row_class or not number.isdigit()
                     or any(k in number + rt for k in ('取消', '除外', '中止')))
        horse_no = int(number) if number.isdigit() else (last_no + 1)  # 取消 rows hide the number
        last_no = horse_no
        frame = _int(text(cell.get('position'))) or frame
        row = {'horse_no': horse_no, 'frame_no': frame, 'scratch_marker': number if cancelled else None,
               'name': name, 'sire': sire, 'damsire': damsire[1] if damsire else None,
               'win_odds': float(win[1]) if win and not cancelled and '.' in win[1] else None,
               'popularity': int(pop[1]) if pop else None,
               'sex_age': sexage, 'age': int(age[1]) if age else None, 'current_load': load,
               'current_jockey': nfkc(jm[1]) if jm else None, 'trainer': trainer,
               'good_bw_range': [int(wr[0]), int(wr[-1])] if wr else None,
               'current_body_weight': cur_bw, 'current_body_weight_change': chg,
               'starts': [s for s in (parse_start(td) for td in starts) if s],
               'status': 'CANCELLED' if cancelled else 'ACTIVE_DECLARED'}
        (excluded if cancelled else runners).append(row)
    return runners, excluded


class Reader:
    def __init__(self, state_path):
        self.client = Client(state_path)

    def meetings(self, day):
        top = self.client.get('/')
        return day_venues(top, day)

    def card_page(self, rid):
        return self.client.get('/race_card/list/RACEID/' + rid)

    def result_page(self, rid):
        return self.client.get('/race_performance/list/RACEID/' + rid)
