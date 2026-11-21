"""BAN sources: 楽天競馬 帯広 (baba 03) card/result via the LOCAL throttled client, own speed index,
NAR official ledger history (Owner-downloaded ZIP extract on the Mac), optional キンタロー/水分ボンバー/競馬ブック
feeds (files dropped by the browser-side collectors; absent -> neutral + DCR-B down)."""
import csv
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parent / 'local_autopilot'))
import rakuten as RK  # noqa: E402

BABA = '03'
MODEL = json.loads((HERE / 'speed_model.json').read_text())
Z2H = str.maketrans('０１２３４５６７８９ＡＢＣＯＰ', '0123456789ABCOP')


def race_class(name):
    s = RK.nfkc(name).translate(Z2H)
    m = re.search(r'(A1|A2|B1|B2|B3|B4|C1|C2|C3|OP|オープン)', s)
    return (m.group(1) if m else 'OTHER').replace('オープン', 'OP')


def speed_index(sec, load, moisture, month, cls, young):
    """Own index (NAR-fit OLS, research/banei_nar/build.py). Unknown moisture -> training mean."""
    if sec is None or load is None:
        return None
    m = MODEL['moisture_mean'] if moisture is None else moisture
    f = {'load': load, 'm': m, 'm2': m * m, 'y': 1.0 if young else 0.0, f'mon_{month}': 1.0, f'cls_{cls}': 1.0, 'c': 1.0}
    pred = sum(c * f.get(col, 0.0) for col, c in zip(MODEL['columns'], MODEL['coef']))
    return round(80 - 10 * (sec - pred) / MODEL['sd'], 2)


def _sec(t):
    m = re.fullmatch(r'(?:(\d+):)?(\d{1,2}\.\d)', t or '')
    return None if not m else int(m[1] or 0) * 60 + float(m[2])


# ------------------------------------------------------------------ 楽天 (ばんえい card template)
def day_meeting(top_html, day):
    d = day.replace('-', '')
    for rid in re.findall(r'race_card/list/RACEID/(\d{18})', top_html):
        if rid.startswith(d) and rid[8:10] == BABA:
            return rid[:16]
    return None


def parse_menu_ban(card_html, day):
    """(race_no, rid, 'HH:MM') for the whole 帯広 day. 楽天 menu links use a meeting-coded prefix
    (e.g. 2026112103041701RR); the canonical day+'03030000'+RR id serves the same card (verified 2026-11-21)."""
    i = card_html.find('<ul class="raceNumber')
    seg = card_html[i:card_html.find('</ul>', i)]
    d = day.replace('-', '')
    out = {}
    for num, hhmm in re.findall(r'<span class="num">(\d{1,2})R</span>\s*<span class="time">(\d{1,2}:\d{2})</span>', seg):
        out[int(num)] = (int(num), f'{d}{BABA}0300{int(num):04d}'[:18], hhmm)
    return sorted(out.values())


def parse_start_ban(td):
    """One past start cell (ばんえい: 200ダ, load 3 digits, time m:ss.s (margin), body 4 digits k)."""
    if 'class="place"' not in td:
        return None
    place = re.search(r'<span class="place">(.*?)</span>', td, re.S)
    body = td[td.find('</div>') + 6:]
    L = RK.lines(body)
    ft = RK.text(place[1]) if place else ''
    out = {'finish': int(ft) if ft.isdigit() else None, 'date': None, 'race_name': '', 'pop': None,
           'jockey': None, 'load': None, 'sec': None, 'margin': None, 'body_weight': None}
    for k, ln in enumerate(L):
        m = re.fullmatch(r'(\S+)\s+(\d{2}\.\d{2}\.\d{2})', ln)
        if m and not out['date']:
            out['date'] = m[2]
            out['race_name'] = L[k + 1] if k + 1 < len(L) else ''
            continue
        m = re.search(r'200(?:ダ|ば)?\s*(\d+)人', ln)
        if m and out['pop'] is None:
            out['pop'] = int(m[1])
            continue
        m = re.fullmatch(r'[☆▲△◇★]?(\S+?)\s+(\d{3,4})', ln)
        if m and out['load'] is None and out['pop'] is not None:
            out['jockey'], out['load'] = m[1], int(m[2])
            continue
        m = re.search(r'((?:\d+:)?\d{1,2}\.\d)\s*\((-?\d+\.\d)\)', ln)
        if m:
            out['sec'], out['margin'] = _sec(m[1]), float(m[2])
            continue
        m = re.search(r'(\d{3,4})k', ln)
        if m and out['body_weight'] is None:
            out['body_weight'] = int(m[1])
    return out


def parse_card_ban(html):
    i = html.find('<tbody class="raceCard">')
    body = html[i:html.find('</tbody>', i)]
    runners = []
    last = 0
    for blk in re.split(r'<tr class="box\d+(?=[ "])', body)[1:]:
        tds = re.findall(r'<t[dh][^>]*class="([^"]*)"[^>]*>(.*?)</t[dh]>', blk, re.S)
        cell, starts = {}, []
        for cls, inner in tds:
            (starts.append(inner) if cls.startswith('race') else cell.setdefault(cls.split()[0], inner))
        number = RK.text(cell.get('number'))
        nm = re.search(r'<span class="mainHorse">.*?>([^<]+)</a>', cell.get('name', ''), re.S)
        app = cell.get('name', '').split('<div class="append">')[1] if '<div class="append">' in cell.get('name', '') else ''
        rate = re.search(r'<span class="rate">(.*?)</span>', app, re.S)
        rt = RK.text(rate[1]) if rate else ''
        win = re.search(r'(\d+\.\d+)', rt)
        pop = re.search(r'(\d+)人気', rt)
        prof = RK.lines(cell.get('profile', ''))
        age = re.match(r'[牡牝セ騸]\s*(\d+)', prof[0]) if prof else None
        load = next((int(x) for x in prof if re.fullmatch(r'\d{3,4}', x)), None)
        jm = re.search(r'jockey/detail/JOCKEYID/\d+">([^<]+)</a>', cell.get('profile', ''))
        wr = [int(v) for v in re.findall(r'\d{3,4}', RK.text(cell.get('weight')))]
        wd = RK.lines(cell.get('weightDistance'))
        cur = int(wd[0]) if wd and re.fullmatch(r'\d{3,4}', wd[0]) else None
        chg = RK._int(wd[1].replace('±', '')) if len(wd) > 1 else None
        cancelled = not number.isdigit() or any(k in number + rt for k in ('取消', '除外', '中止'))
        no = int(number) if number.isdigit() else last + 1
        last = no
        runners.append({'no': no, 'name': RK.nfkc(nm[1]) if nm else RK.text(cell.get('name'))[:20],
                        'age': int(age[1]) if age else None, 'load': load,
                        'jockey': RK.nfkc(jm[1]) if jm else None,
                        'odds': float(win[1]) if win and not cancelled and float(win[1]) > 0 else None,
                        'pop': int(pop[1]) if pop else None,
                        'good_bw_range': (min(wr), max(wr)) if wr else None,
                        'body_weight': cur, 'body_delta': chg, 'scratched': cancelled,
                        'starts': [s for s in (parse_start_ban(t) for t in starts) if s]})
    return runners


def moisture_from_header(html):
    m = re.search(r'(?:馬場水分|水分)[^0-9]{0,20}(\d\.\d)', RK.nfkc(re.sub(r'<[^>]+>', ' ', html[:20000])))
    return float(m[1]) if m else None


# ------------------------------------------------------------------ NAR ledger + feeds
def nar_history(nar_dir):
    """{horse_name: [ {date, idx, moisture}, ... newest first]} from the Owner's NAR extract (optional)."""
    p = Path(nar_dir or '') / 'ban_horselist.csv'
    q = Path(nar_dir or '') / 'ban_racelist.csv'
    if not p.exists() or not q.exists():
        return {}
    races = {}
    with q.open(encoding='utf-8') as f:
        for row in csv.DictReader(f):
            races[(row['競走年月日'], row['レース番号'])] = row
    hist = {}
    with p.open(encoding='utf-8') as f:
        for row in csv.DictReader(f):
            rc = races.get((row['競走年月日'], row['レース番号']))
            if not rc:
                continue
            t = (row.get('タイム') or '').zfill(4)
            try:
                sec = int(t[:-3]) * 60 + int(t[-3:]) / 10
                load = int(re.sub(r'[^\d]', '', row['負担重量']))
                moist = float(rc['馬場'])
            except (ValueError, TypeError):
                continue
            d = row['競走年月日']
            idx = speed_index(sec, load, moist, int(d[4:6]), race_class(rc['レース名']),
                              '2歳' in rc['条件'] or '２歳' in rc['条件'])
            hist.setdefault(row['馬名'], []).append({'date': d, 'idx': idx, 'moisture': moist})
    for v in hist.values():
        v.sort(key=lambda z: z['date'], reverse=True)
    return hist


def load_feed(feed_dir, day, kind):
    """Browser-side collector outputs: <feed_dir>/<day>/<kind>.json (kind = kintaro / sbo / keibabook)."""
    p = Path(feed_dir or '') / day / f'{kind}.json'
    return json.loads(p.read_text()) if p.exists() else {}


def build_horses(card, moisture, race_date, hist, feeds, race_no):
    """Card + history + feeds -> engine horse dicts (provenance kept by the engine)."""
    kin = (feeds.get('kintaro') or {}).get(str(race_no), {})
    sbo = (feeds.get('sbo') or {}).get(str(race_no), {})
    kb = (feeds.get('keibabook') or {}).get(str(race_no), {})
    dt = datetime.strptime(race_date, '%Y-%m-%d')
    out = []
    for r in card:
        own = []
        for s in r['starts']:
            if s.get('sec') and s.get('load') and s.get('date'):
                d = datetime.strptime('20' + s['date'], '%Y.%m.%d')
                own.append({'idx': speed_index(s['sec'], s['load'], None, d.month, race_class(s['race_name']), False),
                            'moisture': None, 'date': d.strftime('%Y%m%d')})
        nar = [z for z in hist.get(r['name'], []) if z['date'] < dt.strftime('%Y%m%d')]
        seen = {z['date'] for z in nar}
        own = sorted(nar + [z for z in own if z['date'] not in seen], key=lambda z: z['date'], reverse=True)
        k = kin.get(str(r['no']), {})
        out.append({**r, 'own_past': own, 'sbo_past': sbo.get(str(r['no']), []),
                    'kintaro_past': k.get('past', []), 'front_ok': k.get('front_ok'),
                    'barrier_stable': k.get('barrier_stable'), 'cci': kb.get(str(r['no']), {}).get('cci'),
                    'body_stable': r['body_delta'] is not None and abs(r['body_delta']) < 16})
    return out
