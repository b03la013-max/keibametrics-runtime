"""EXT model v2: everything collected -> measured scores (Owner 2026-11-21 13:32 JST
「１２３全て始めなさい／指数に接続できていないのは接続させなさい／自前で計算しているのに記録だけのものも
指数に接続させなさい／むしろ全てを指数に接続させ常に改善させなさい」).

Every score is 0-100 with 52 = neutral and comes from a MEASURED top-3 A/E: actual top-3 / the popularity x
field-size expectation of the venue, over every NAR official start (2023-01 ..) plus the Rakuten result backfill
dated strictly before the race day, shrunk toward 1 (M pseudo-starts), score = 52 + 20 log2(A/E), clipped 30..75.
The documents (Drive reading, YouTube, 亀谷, 危険な1番人気) only decide WHICH label a horse carries; how strong a
label is comes from the data.

Two outlets:
  * full29_evidence(): fills the Full29 components that were canonical-neutral for lack of a source
    (BVIg-L 7 parts, JTI-L stable_combo, CSI-L stable_venue_class_distance / cci_specificity /
    tri_vertical_comparison, BWI-L weight_change_reason_rate / age_growth / transport_season,
    DCR training_comment_trial, NCI class_relative_time) -> the 29 indices and the KRS input move.
  * race scores for the ranking layer (ext_connect): VMI (水分ボンバー), SPD (own NAR speed figure), TMI / KBA / PACE
    (競馬ブック), JKY, FRM, HRS, PAT (all pattern labels).
Weights of the NAR-measured components are re-estimated weekly (fit_weights) and adopted only when the later
hold-out weeks improve; every fit is logged.
"""
from __future__ import annotations

import json
import math
import os
import re
import statistics
import unicodedata
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

NEUTRAL = 52.0
MIN_N, M = 30, 30
H_MIN, H_M = 3, 8
TABLE_VERSION = 3
CIRCUIT = {'OHI': 'NANKAN', 'FNB': 'NANKAN', 'KAW': 'NANKAN', 'URW': 'NANKAN', 'MIZ': 'IWATE', 'MOR': 'IWATE',
           'SON': 'HYOGO', 'HMJ': 'HYOGO'}
VENUE_NAME = {'盛岡': 'MOR', '水沢': 'MIZ', '浦和': 'URW', '船橋': 'FNB', '大井': 'OHI', '川崎': 'KAW', '金沢': 'KNZ',
              '笠松': 'KSM', '名古屋': 'NGY', '園田': 'SON', '姫路': 'HMJ', '高知': 'KOC', '佐賀': 'SAG', '門別': 'MON'}
SMALL_TRACK = {'URW', 'KAW', 'SON', 'KSM', 'MIZ'}
LEFT_TURN = {'URW', 'FNB', 'KAW', 'MOR'}                 # same set as local_nar_evidence_candidate
GEOMETRY = {'OHI': 'LARGE', 'MON': 'LARGE', 'MOR': 'LARGE', 'FNB': 'MID', 'KNZ': 'MID', 'NGY': 'MID', 'SAG': 'MID',
            'KOC': 'MID', 'HMJ': 'MID', 'MIZ': 'SMALL', 'URW': 'SMALL', 'KAW': 'SMALL', 'SON': 'SMALL', 'KSM': 'SMALL'}
CLASS_ORDER = {'C3': 1, 'C2': 2, 'C1': 3, 'B3': 4, 'B2': 5, 'B1': 6, 'A2': 7, 'A1': 8, 'OPEN': 9}
BAND_SCORE = {'VERY_STRONG': 66.0, 'STRONG': 59.0, 'NEUTRAL': 52.0, 'CAUTION': 45.0}


def key(s):
    s = unicodedata.normalize('NFKC', str(s or '')).strip()
    return re.sub(r'[\s☆▲△◇★▽()（）]', '', s) or None


def circ(v):
    return CIRCUIT.get(v, v)


def going_class(g):
    g = str(g or '')
    return 'WET' if ('不' in g or '重' in g) and '稍' not in g else 'DAMP' if '稍' in g else 'DRY' if '良' in g else 'UNKNOWN'


def dist_band(d):
    d = int(d or 0)
    return 'UNKNOWN' if not d else 'S' if d <= 1300 else 'M' if d <= 1700 else 'L'


def field_band(n):
    n = n or 0
    return 'F<=8' if n <= 8 else 'F9-11' if n <= 11 else 'F12+'


def frame_band(f):
    return None if not f else 'IN' if f <= 2 else 'OUT' if f >= 7 else 'MID'


def fin_band(f):
    return None if not f else '1-3' if f <= 3 else '4-6' if f <= 6 else '7+'


def class_code(text):
    from runtime.local_autopilot.hist_stats import class_code as cc
    return cc(text)


def weather_class(w):
    w = str(w or '')
    return None if not w else 'RAIN' if ('雨' in w or '雪' in w) else 'DRY'


def season(d):
    m = int(d[5:7])
    return 'WINTER' if m in (12, 1, 2) else 'SPRING' if m in (3, 4, 5) else 'SUMMER' if m in (6, 7, 8) else 'AUTUMN'


def chg_band(c):
    if c is None:
        return None
    return '<=-10' if c <= -10 else '-9..-4' if c <= -4 else '-3..3' if c <= 3 else '4..9' if c <= 9 else '>=10'


def spd_band(dev):
    if dev is None:
        return 'NA'
    for lo, name in ((8, '>8'), (4, '4..8'), (1, '1..4'), (-1, '-1..1'), (-4, '-4..-1'), (-8, '-8..-4')):
        if dev > lo:
            return name
    return '<=-8'


def score(ae):
    return max(30.0, min(75.0, NEUTRAL + 20.0 * math.log2(max(ae, 1e-6))))


def style(hist):
    e = [p['early'] for p in hist[-3:] if p.get('early') is not None]
    if not e:
        return None
    m = sum(e) / len(e)
    return 'FRONT' if m <= 0.3 else 'BACK' if m >= 0.6 else 'MID'


def spd_of(hist):
    figs = [p['fig'] for p in hist[-4:] if p.get('fig') is not None]
    if not figs:
        return None
    best = sorted(figs, reverse=True)[:2]
    return sum(best) / len(best)


# ---------------------------------------------------------------- pattern labels
def _kame(cur, hist):
    """亀谷 sire scenes + 南関 YouTube sire rules -> labels (the scene list decides the label, NAR the strength)."""
    from runtime.local_autopilot import bloodline_kametani as bk
    if not cur.get('sire'):
        return []
    starts = [{'content_positions': [p['pos']] if p.get('pos') else [], 'field_size': p.get('field'),
               'finish': p.get('finish'), 'distance': p.get('distance'), 'surface': 'DIRT',
               'ride_body_weight': p.get('bw')} for p in reversed(hist[-5:])]
    runner = {'sire': cur['sire'], 'damsire': cur.get('damsire'), 'sex_age': cur.get('sex') or '', 'age': cur.get('age'),
              'starts': starts, 'popularity': cur.get('pop'), 'frame_no': cur.get('frame_no')}
    race = {'surface': 'DIRT', 'distance': cur.get('distance'), 'going': cur.get('going'), 'venue_id': cur.get('venue')}
    out = []
    try:
        ev = bk.evaluate(runner, race)
        if ev:
            out.append(('KAME', 'BOTH' if ev['buy_match'] and ev['caution_match'] else 'BUY' if ev['buy_match']
                        else 'CAUTION' if ev['caution_match'] else 'NONE'))
        sides = sorted({h['side'] for h in bk.nankan(runner, race)})
        if sides:
            out.append(('NKSIRE', '+'.join(sides)))
    except Exception:
        pass
    return out


def _yymmdd(d):
    s = str(d or '')
    return f'{s[2:4]}.{s[5:7]}.{s[8:10]}' if len(s) >= 10 and s[4] == '-' else None


def cand_labels(cur, hist):
    """Candidate labels measured as their OWN components (not in PAT, weight 0 until the hold-out refit adopts one).
    KAME3: 亀谷 sire rules v3 (kametani_v3, B4 2026-11-24)."""
    from runtime.local_autopilot import kametani_v3 as k3
    if not (cur.get('sire') or cur.get('damsire')):
        return []
    starts = [{'content_positions': [p['pos']] if p.get('pos') else [], 'field_size': p.get('field'),
               'finish': p.get('finish'), 'distance': p.get('distance'), 'surface': 'DIRT',
               'ride_body_weight': p.get('bw'), 'date': _yymmdd(p.get('date'))} for p in reversed(hist[-5:])]
    runner = {'sire': cur.get('sire'), 'damsire': cur.get('damsire'), 'sex_age': cur.get('sex') or '',
              'age': cur.get('age'), 'starts': starts, 'popularity': cur.get('pop'), 'frame_no': cur.get('frame_no')}
    race = {'surface': 'DIRT', 'distance': cur.get('distance'), 'going': cur.get('going'), 'venue_id': cur.get('venue'),
            'race_date': cur.get('date')}
    try:
        v = k3.label(runner, race)
    except Exception:
        return []
    return [('KAME3', v)] if v else []


CAND_COMPONENTS = {'KAME3': 'KM3'}


def labels(cur, hist):
    """cur: date, venue, distance, going, age, sex, pop, frame_no, jockey, cls, weather, special, daybias, sire,
    damsire. hist: the horse's earlier starts, oldest first (date, venue, distance, finish, early, late, cls,
    jockey, fig, f3best, field, pos, bw)."""
    out = _kame(cur, hist)
    pop = cur.get('pop')
    if not hist:
        out.append(('DEBUT', 'Y'))
        if pop == 1:
            out.append(('FAV_DANGER', 'DEBUT'))
        return out
    last = hist[-1]
    lf = fin_band(last.get('finish')) or 'NA'
    if circ(last['venue']) == circ(cur['venue']):
        mv = 'SAME'
    elif any(circ(p['venue']) == circ(cur['venue']) for p in hist[:-1]):
        mv = 'RETURN'
    else:
        mv = 'NEW_MOVE'
    out.append(('MOVE', f"{mv}|{'7+' if lf == '7+' else 'ELSE'}"))
    dw = any(p['venue'] == cur['venue'] and p.get('distance') == cur.get('distance') and p.get('finish') == 1 for p in hist)
    out.append(('DIRECT', f"{'Y' if dw else 'N'}|{lf}"))
    ear = [p['early'] for p in hist[-5:] if p.get('early') is not None]
    if last.get('early') is not None and last['early'] <= 0.0 and len(ear) >= 2 and sum(ear) / len(ear) <= 0.25:
        out.append(('LEAD', 'REPEAT'))
    pos = 'NA' if last.get('early') is None else 'FRONT' if last['early'] <= 0.33 else 'BACK'
    if cur.get('distance') and last.get('distance'):
        ch = 'SHORT' if cur['distance'] < last['distance'] else 'LONG' if cur['distance'] > last['distance'] else 'SAME'
        out.append(('GOROT', f"{going_class(cur.get('going'))}|{ch}|{pos}"))
    try:
        days = (date.fromisoformat(cur['date']) - date.fromisoformat(last['date'])).days
    except (TypeError, ValueError):
        days = None
    if days is not None and days >= 180:
        out.append(('LAYOFF', 'LONG'))
    if days is not None and days <= 6 and (cur.get('age') or 0) >= 7:
        out.append(('AGED', 'SHORT'))
    # class move (class_move.py / 南関クラス分け YouTube)
    c0, c1 = CLASS_ORDER.get(last.get('cls')), CLASS_ORDER.get(cur.get('cls'))
    if c0 and c1:
        out.append(('CLASS', f"{'UP' if c1 > c0 else 'DOWN' if c1 < c0 else 'SAME'}|{lf}"))
    # CRZ / MAI: last start 4-corner band x finish band, max gain over 5 starts
    if last.get('late') is not None:
        lb = 'FRONT' if last['late'] <= 0.25 else 'BACK' if last['late'] >= 0.6 else 'MID'
        out.append(('PREVLC', f"{lb}|{lf}"))
    gains = [p['early'] - p['late'] for p in hist[-5:] if p.get('early') is not None and p.get('late') is not None]
    if gains:
        g = max(gains)
        out.append(('MPA', 'BIG' if g >= 0.3 else 'SOME' if g >= 0.1 else 'NONE'))
    if last.get('f3best') is not None:
        out.append(('PREV3F', f"{'Y' if last['f3best'] else 'N'}|{lf}"))
    if last.get('jockey') and cur.get('jockey'):
        out.append(('JCHG', 'Y' if key(last['jockey']) != key(cur['jockey']) else 'N'))
    st = style(hist)
    if pop and pop <= 2:
        out.append(('FAVFRAME', f"{frame_band(cur.get('frame_no')) or 'NA'}"))
        out.append(('FAVGOING', f"{pop}|{going_class(cur.get('going'))}"))    # T13 人気馬×馬場 (名古屋・高知 YouTube)
        if (cur.get('age') or 0) >= 7 and last.get('early') is not None and last['early'] <= 0.25 and lf != '1-3':
            out.append(('FAVAGE', 'FADED_FRONT'))
    if cur.get('special') == 'KOC_FINAL':
        out.append(('SPECIAL', f"KOC_FINAL|{'1-3' if (pop or 99) <= 3 else '4+'}"))
    if last['venue'] != cur['venue']:
        out.append(('ROUTE', f"{last['venue']}>{cur['venue']}|{pos}"))
    wc = weather_class(cur.get('weather'))
    if wc and st:
        out.append(('WEATHER', f'{wc}|{st}'))
    if cur.get('daybias') and st:
        out.append(('DAYBIAS', f"{cur['daybias']}|{st}"))
    good = [p['bw'] for p in hist if p.get('bw') and p.get('finish') and p['finish'] <= 3]
    if good and cur.get('bw'):       # 馬体重は前走比でなく好走レンジで見る（馬体重の見方 / 中央版 §62）
        lo, hi = min(good), max(good)
        out.append(('GOODBW', 'IN' if lo - 4 <= cur['bw'] <= hi + 4 else 'LIGHT' if cur['bw'] < lo - 4 else 'HEAVY'))
    if pop == 1:   # 危険な1番人気 checklist (第10章), read mechanically
        n = sum([not any(p['venue'] == cur['venue'] for p in hist),
                 not any(p.get('distance') == cur.get('distance') for p in hist),
                 st == 'BACK', days is not None and days >= 90, (last.get('finish') or 1) > 1,
                 bool(last.get('jockey') and cur.get('jockey') and key(last['jockey']) != key(cur['jockey'])),
                 cur['venue'] in SMALL_TRACK and (cur.get('frame_no') or 0) >= 7])
        out.append(('FAV_DANGER', '3+' if n >= 3 else str(n)))
    return out


# ---------------------------------------------------------------- training rows
def _standards(races):
    t = defaultdict(list)
    for r in races.values():
        g = going_class(r.get('going'))
        for x in r['runners']:
            if x['status'] == 'RAN' and x.get('time'):
                t[(r['venue'], r.get('distance'), g)].append(x['time'])
    out = {}
    for k, v in t.items():
        if len(v) >= 30:
            v = sorted(v)
            q1, q3 = v[len(v) // 4], v[3 * len(v) // 4]
            out[k] = (statistics.median(v), max(0.3, (q3 - q1) / 1.35))
    return out


def _rows(races, std=None):
    """One row per start (horse ran, popularity known) with pre-race labels / speed; and the horse histories."""
    from runtime.local_autopilot import hist_stats as hs
    std = std if std is not None else _standards(races)
    hist = defaultdict(list)
    winners_style = defaultdict(list)
    out = []
    for race in sorted(races.values(), key=lambda r: (r['date'], r['venue'], r['race_no'] or 0)):
        field = race.get('field') or sum(1 for x in race['runners'] if x['status'] != 'SCRATCH')
        g = going_class(race.get('going'))
        s0 = std.get((race['venue'], race.get('distance'), g))
        f3 = [hs._f3(x.get('last3f')) for x in race['runners'] if x['status'] == 'RAN']
        best3 = min([v for v in f3 if v], default=None)
        ws = winners_style[(race['date'], race['venue'])]
        bias = None
        if len(ws) >= 3:
            fr = sum(1 for s in ws if s == 'FRONT') / len(ws)
            bias = 'FRONT' if fr >= 0.6 else 'BACK' if fr <= 0.15 else 'NEUTRAL'
        cur0 = {'date': race['date'], 'venue': race['venue'], 'distance': race.get('distance'), 'going': race.get('going'),
                'cls': hs.class_code(race.get('cond')), 'weather': race.get('weather'),
                'special': hs.special_flag(race['venue'], race.get('cond')), 'daybias': bias}
        done, rr = [], []
        for x in race['runners']:
            if x['status'] == 'SCRATCH' or not x.get('no'):
                continue
            hk = key(x.get('name')) or x.get('horse_key')
            prev = hist.get(hk, [])
            fc = race['first_corner'].get(x['no'])
            lc = race['last_corner'].get(x['no'])
            early = (fc - 1) / max(1, field - 1) if fc else None
            late = (lc - 1) / max(1, field - 1) if lc else None
            fig = (max(0.0, min(100.0, 50 + 10 * (s0[0] - x['time']) / s0[1]))
                   if s0 and x['status'] == 'RAN' and x.get('time') else None)
            if x['status'] == 'RAN' and x.get('pop'):
                cur = dict(cur0, age=x.get('age'), sex=x.get('sex'), pop=x['pop'], frame_no=x.get('frame'), bw=x.get('bw'),
                           jockey=x.get('jockey'), sire=x.get('sire'), damsire=x.get('damsire'))
                rr.append({'race_id': race['race_id'], 'date': race['date'], 'venue': race['venue'],
                           'distance': race.get('distance'), 'band': dist_band(race.get('distance')), 'going': g,
                           'fband': field_band(field), 'pop': x['pop'], 'top3': bool(x.get('finish') and x['finish'] <= 3),
                           'sire': key(x.get('sire')), 'damsire': key(x.get('damsire')), 'jockey': key(x.get('jockey')),
                           'trainer': key(x.get('trainer')), 'frame': frame_band(x.get('frame')), 'horse': hk,
                           'sex': x.get('sex'), 'age': x.get('age'), 'bwchg': chg_band(x.get('bw_chg')),
                           'season': season(race['date']), 'spd': spd_of(prev), 'labels': labels(cur, prev),
                           'cand_labels': cand_labels(cur, prev), 'style': style(prev), 'early_now': early})
            done.append((hk, {'date': race['date'], 'venue': race['venue'], 'distance': race.get('distance'),
                              'finish': x.get('finish'), 'early': early, 'late': late, 'cls': cur0['cls'],
                              'jockey': x.get('jockey'), 'fig': None if fig is None else round(fig, 1),
                              'f3best': (None if best3 is None or hs._f3(x.get('last3f')) is None else hs._f3(x.get('last3f')) == best3),
                              'field': field, 'pos': fc, 'bw': x.get('bw')}))
        sp = [r['spd'] for r in rr if r['spd'] is not None]
        mu = sum(sp) / len(sp) if len(sp) >= 2 else None
        for r in rr:
            r['spd_band'] = spd_band(None if mu is None or r['spd'] is None else r['spd'] - mu)
        out += rr
        w = next((x for x in race['runners'] if x.get('finish') == 1), None)
        if w:
            ws.append(style(hist.get(key(w.get('name')) or w.get('horse_key'), [])))
        for hk, h in done:
            hist[hk].append(h)
    return out, hist


def cell_keys(r):
    v, b, g, d, s = r['venue'], r['band'], r['going'], r['distance'], r['sire']
    ks = []
    if s:
        ks += [('S', s, v, b, g), ('S', s, v, b), ('S', s, v), ('S', s, b), ('S', s, g), ('S', s)]
    if r['damsire']:
        ks += [('D', r['damsire'], v), ('D', r['damsire'], b), ('D', r['damsire'], g), ('D', r['damsire'])]
    if r['jockey']:
        ks += [('J', r['jockey'], v), ('J', r['jockey'], b), ('J', r['jockey'])]
        if r['trainer']:
            ks += [('JT', r['jockey'], r['trainer'])]
    if r['trainer']:
        ks += [('T', r['trainer'], v, b), ('T', r['trainer'], v), ('T', r['trainer'])]
    if r['frame']:
        ks += [('F', v, d, r['frame'], r['fband']), ('F', v, d, r['frame'])]
    if r['horse']:
        ks += [('H', r['horse'], v, d), ('H', r['horse'], v), ('H', r['horse'])]
    if r['bwchg']:
        ks += [('BW', r['bwchg'], r['sex'])]
    h, j = r['horse'], r['jockey']
    if h:   # the horse's own record by course facts (CFIg-L / RFIg-L slots)
        ks += [('HD', h, 'LEFT' if v in LEFT_TURN else 'RIGHT'), ('HGe', h, GEOMETRY.get(v, 'MID')), ('HDi', h, d),
               ('HB', h, b), ('HGo', h, g)]
        if r.get('early_now') is not None and r['early_now'] <= 0.3:
            ks += [('HS', h, 'FRONT')]
        if j:
            ks += [('JH', j, h)]
    if j:   # jockey record by situation (JTI-L slots)
        pb = 'FAV' if r['pop'] <= 2 else 'LONG' if r['pop'] >= 6 else 'MID'
        ks += [('JF', j, pb)]
        if r.get('recent'):
            ks += [('JR', j, v)]
        if r.get('style'):
            ks += [('JS', j, r['style'])]
    if r['age']:
        ks += [('AG', min(r['age'], 9), r['sex'], circ(v)), ('AG', min(r['age'], 9), r['sex'])]
    ks += [('SE', r['season'], r['sex'], circ(v)), ('SPD', r['spd_band'], circ(v)), ('SPD', r['spd_band'])]
    for name, val in list(r['labels']) + list(r.get('cand_labels') or []):
        ks += [('P', name, val, circ(v)), ('P', name, val)]
    return ks


def expectation(rows):
    base = defaultdict(lambda: [0, 0])
    for r in rows:
        k = (r['venue'], min(r['pop'], 10), r['fband'])
        base[k][0] += 1
        base[k][1] += r['top3']
    return {k: v[1] / v[0] for k, v in base.items() if v[0]}


def accumulate(rows, exp, recent_from=None):
    cells = defaultdict(lambda: [0, 0, 0.0])
    for r in rows:
        r['recent'] = bool(recent_from and r['date'] >= recent_from)
        e = exp.get((r['venue'], min(r['pop'], 10), r['fband']))
        if e is None:
            continue
        for k in cell_keys(r):
            c = cells[k]
            c[0] += 1
            c[1] += r['top3']
            c[2] += e
    return cells


def build(races, before_day):
    """-> (tables, histories). Only races dated before `before_day`."""
    rs = {k: v for k, v in races.items() if v['date'] < before_day}
    std = _standards(rs)
    rows, hist = _rows(rs, std)
    exp = expectation(rows)
    cells = accumulate(rows, exp, (date.fromisoformat(before_day) - timedelta(days=365)).isoformat())
    t = {'version': TABLE_VERSION, 'before_day': before_day, 'starts': len(rows),
         'period': [min((r['date'] for r in rows), default=None), max((r['date'] for r in rows), default=None)],
         'standards': {json.dumps(k, ensure_ascii=False): v for k, v in std.items()},
         'cells': {json.dumps(k, ensure_ascii=False): [n, a, round(e, 4)] for k, (n, a, e) in cells.items()}}
    return t, {h: v[-20:] for h, v in hist.items()}


def ae_of(cells, keys, min_n=MIN_N, m=M):
    """Most specific cell with >= min_n starts -> (score, key, n, raw A/E)."""
    for k in keys:
        c = cells.get(k)
        if c and c[0] >= min_n and c[2] > 0:
            pbar = c[2] / c[0]
            ae = (c[1] + m * pbar) / (c[2] + m * pbar)
            return score(ae), k, c[0], round(c[1] / c[2], 3)
    return None, None, 0, None


# ---------------------------------------------------------------- per-runner measured components
def components(cells, r):
    """r: a row-like dict (same keys as a training row). -> {name: (score, detail)} for the NAR-measured parts."""
    v, b, g, d, s, ds = r['venue'], r['band'], r['going'], r['distance'], r['sire'], r['damsire']
    out = {}

    def put(name, keys, mn=MIN_N, m=M):
        a = ae_of(cells, keys, mn, m)
        if a[0] is not None:
            out[name] = (a[0], {'cell': list(a[1]), 'n': a[2], 'ae': a[3]})
    if s:
        put('sire_fit', [('S', s, v, b, g), ('S', s, v, b), ('S', s, v), ('S', s)])
        put('sire_band', [('S', s, b)])
        put('sire_going', [('S', s, g)])
        put('sire_venue', [('S', s, v)])
        put('sire_cell', [('S', s, v, b, g)])
    if ds:
        put('damsire_fit', [('D', ds, v), ('D', ds, b), ('D', ds)])
        put('damsire_band', [('D', ds, b)])
    if r['jockey']:
        put('JKY', [('J', r['jockey'], v), ('J', r['jockey'], b), ('J', r['jockey'])])
        if r['trainer']:
            put('jt_combo', [('JT', r['jockey'], r['trainer'])], 20, M)
    if r['trainer']:
        put('trainer', [('T', r['trainer'], v, b), ('T', r['trainer'], v), ('T', r['trainer'])])
    if r['frame']:
        put('FRM', [('F', v, d, r['frame'], r['fband']), ('F', v, d, r['frame'])])
    if r['horse']:
        put('HRS', [('H', r['horse'], v, d), ('H', r['horse'], v), ('H', r['horse'])], H_MIN, H_M)
    if r['bwchg']:
        put('bwchg', [('BW', r['bwchg'], r['sex'])])
    if r['age']:
        put('age_growth', [('AG', min(r['age'], 9), r['sex'], circ(v)), ('AG', min(r['age'], 9), r['sex'])])
    put('season', [('SE', r['season'], r['sex'], circ(v))])
    h, j = r['horse'], r['jockey']
    if h:
        put('turn_direction', [('HD', h, 'LEFT' if v in LEFT_TURN else 'RIGHT')], H_MIN, H_M)
        put('course_geometry', [('HGe', h, GEOMETRY.get(v, 'MID'))], H_MIN, H_M)
        put('same_distance', [('HDi', h, d)], H_MIN, H_M)
        put('same_venue', [('H', h, v)], H_MIN, H_M)
        put('similar_distance', [('HB', h, b)], H_MIN, H_M)
        put('going_fit', [('HGo', h, g)], H_MIN, H_M)
        put('lead_acceptance', [('HS', h, 'FRONT')], 2, H_M)
        if j:
            put('jockey_horse', [('JH', j, h)], 2, H_M)
    if j:
        put('jockey_fav', [('JF', j, 'FAV')])
        put('jockey_long', [('JF', j, 'LONG')])
        put('jockey_distance', [('J', j, b)])
        put('jockey_venue_recent', [('JR', j, v)])
        put('jockey_front', [('JS', j, 'FRONT')])
        put('jockey_back', [('JS', j, 'BACK')])
    gb = next((val for name, val in r['labels'] if name == 'GOODBW'), None)
    if gb:
        put('good_weight', [('P', 'GOODBW', gb, circ(v)), ('P', 'GOODBW', gb)])
    put('SPD', [('SPD', r['spd_band'], circ(v)), ('SPD', r['spd_band'])])
    ps = []
    for name, val in r['labels']:
        a = ae_of(cells, [('P', name, val, circ(v)), ('P', name, val)])
        if a[0] is not None:
            ps.append({'label': f'{name}={val}', 'score': round(a[0], 1), 'n': a[2], 'ae': a[3]})
    for name, val in r.get('cand_labels') or []:
        if name in CAND_COMPONENTS:
            put(CAND_COMPONENTS[name], [('P', name, val, circ(v)), ('P', name, val)])
    if ps:
        # deviations add up (each label measured on its own), mean keeps one label from dominating
        out['PAT'] = (NEUTRAL + sum(p['score'] - NEUTRAL for p in ps) / math.sqrt(len(ps)), ps)
    return out


def full29_evidence(comp, kb=None, spd_field_score=None):
    """NAR / 競馬ブック components -> Full29 component slots that are canonical-neutral without a source."""
    ev = {}

    def put(slot, name, fact):
        if name in comp:
            sc, det = comp[name]
            ev[slot] = {'score': round(max(0.0, min(100.0, sc)), 3), 'coverage': 1.0,
                        'fact': f'{fact}: {json.dumps(det, ensure_ascii=False)[:160]}', 'ref': 'KM-LOCAL-EXT-NAR-TABLES'}
    put('BVIg-L.sire_fit', 'sire_fit', 'NAR sire top-3 A/E (most specific cell)')
    put('BVIg-L.damsire_fit', 'damsire_fit', 'NAR damsire top-3 A/E')
    put('BVIg-L.distance_sustain', 'sire_band', 'NAR sire x distance band')
    put('BVIg-L.distance_trait', 'damsire_band', 'NAR damsire x distance band')
    put('BVIg-L.surface_sand_fit', 'sire_going', 'NAR sire x going')
    put('BVIg-L.venue_stat', 'sire_venue', 'NAR sire x venue')
    put('BVIg-L.physical_style_fit', 'sire_cell', 'NAR sire x venue x band x going')
    put('JTI-L.stable_combo', 'jt_combo', 'NAR jockey x trainer')
    put('CSI-L.stable_venue_class_distance', 'trainer', 'NAR trainer x venue x band')
    put('BWI-L.weight_change_reason_rate', 'bwchg', 'NAR body-weight change band x sex')
    put('BWI-L.age_growth', 'age_growth', 'NAR age x sex x circuit')
    put('BWI-L.transport_season', 'season', 'NAR season x sex x circuit')
    put('BWI-L.good_weight_range', 'good_weight', 'NAR A/E of 好走時馬体重レンジ内/外')
    put('CFIg-L.turn_direction', 'turn_direction', "NAR the horse's A/E by turn direction")
    put('CFIg-L.course_geometry', 'course_geometry', "NAR the horse's A/E by track size class")
    put('CFIg-L.same_distance', 'same_distance', "NAR the horse's A/E at this distance")
    put('CFIg-L.same_venue', 'same_venue', "NAR the horse's A/E at this venue")
    put('CFIg-L.similar_distance', 'similar_distance', "NAR the horse's A/E in this distance band")
    put('CFIg-L.going_fit', 'going_fit', "NAR the horse's A/E on this going")
    put('RFIg-L.going_adaptation', 'going_fit', "NAR the horse's A/E on this going")
    put('RFIg-L.leadership_stalk_acceptance', 'lead_acceptance', "NAR the horse's A/E when it ran in front")
    put('RFIg-L.jockey_reproducibility', 'jockey_horse', 'NAR A/E of this jockey on this horse')
    put('JTI-L.favorite_reliability', 'jockey_fav', 'NAR jockey A/E on 1-2 favourites')
    put('JTI-L.longshot_record', 'jockey_long', 'NAR jockey A/E on 6th+ favourites')
    put('JTI-L.distance_record', 'jockey_distance', 'NAR jockey A/E in this distance band')
    put('JTI-L.venue_recent', 'jockey_venue_recent', 'NAR jockey A/E at this venue, last 365 days')
    put('JTI-L.position_acquisition_skill', 'jockey_front', 'NAR jockey A/E on front-running types')
    put('JTI-L.progression_timing_skill', 'jockey_back', 'NAR jockey A/E on closers')
    if spd_field_score is not None:
        ev['NCI.class_relative_time'] = {'score': round(spd_field_score, 3), 'coverage': 1.0,
                                         'fact': 'own NAR speed figure, field-relative (measured A/E band)',
                                         'ref': 'KM-LOCAL-EXT-NAR-SPEED'}
    kb = kb or {}
    if kb.get('cci') in BAND_SCORE:
        ev['CSI-L.cci_specificity'] = {'score': BAND_SCORE[kb['cci']], 'coverage': 1.0,
                                       'fact': f"競馬ブック 厩舎の話 band={kb['cci']}", 'ref': 'KEIBABOOK-BANDS'}
    if kb.get('tri') in BAND_SCORE:
        ev['CSI-L.tri_vertical_comparison'] = {'score': BAND_SCORE[kb['tri']], 'coverage': 1.0,
                                               'fact': f"競馬ブック 調教 band={kb['tri']}", 'ref': 'KEIBABOOK-BANDS'}
    if kb.get('cci') in BAND_SCORE or kb.get('tri') in BAND_SCORE:
        ev['DCR.training_comment_trial'] = {'score': 100.0, 'coverage': 1.0, 'fact': '競馬ブック 調教/厩舎の話 present',
                                            'ref': 'KEIBABOOK-BANDS'}
    return ev


# ---------------------------------------------------------------- weekly weight refit (always improving)
def _p(e, comp, w):
    z = sum(w.get(k, 0.0) * (sc - NEUTRAL) for k, sc in comp.items()) / 20.0
    return min(0.97, max(1e-4, e * 2 ** z))


def _ll(data, w):
    s = 0.0
    for e, comp, y in data:
        p = _p(e, comp, w)
        s -= math.log(p if y else 1 - p)
    return s / max(1, len(data))


def fit(data, names, start, steps=(0.4, 0.2, 0.1, 0.05), rounds=3):
    """Coordinate search on top-3 log-loss of p = e * 2^(sum w_k (s_k-52)/20), w_k in [0, 1.5]."""
    w = dict(start)
    best = _ll(data, w)
    for _ in range(rounds):
        for st in steps:
            for k in names:
                for dlt in (st, -st):
                    c = dict(w)
                    c[k] = min(1.5, max(0.0, c.get(k, 0.0) + dlt))
                    v = _ll(data, c)
                    if v < best - 1e-7:
                        w, best = c, v
    return w, best


def fit_weights(races, day, names, current, weeks_fit=8, weeks_hold=4):
    """Tables from data before (day - fit - hold weeks); fit on the fit weeks; adopt only if the hold-out weeks
    (never used for the tables or the fit) improve over the current weights."""
    d = date.fromisoformat(day)
    t_end = (d - timedelta(weeks=weeks_fit + weeks_hold)).isoformat()
    f_end = (d - timedelta(weeks=weeks_hold)).isoformat()
    rs = {k: v for k, v in races.items() if v['date'] < day}
    std = _standards({k: v for k, v in rs.items() if v['date'] < t_end})
    rows, _ = _rows(rs, std)
    train = [r for r in rows if r['date'] < t_end]
    exp = expectation(train)
    cells = accumulate(train, exp)

    def data(lo, hi):
        out = []
        for r in rows:
            if lo <= r['date'] < hi:
                e = exp.get((r['venue'], min(r['pop'], 10), r['fband']))
                if e:
                    c = components(cells, r)
                    out.append((e, {k: c[k][0] for k in names if k in c}, r['top3']))
        return out
    fd, hd = data(t_end, f_end), data(f_end, day)
    if len(fd) < 2000 or len(hd) < 1000:
        return {'status': 'TOO_FEW', 'fit_rows': len(fd), 'hold_rows': len(hd), 'weights': current}
    w, _ = fit(fd, names, current)
    base = {k: 0.0 for k in names}
    ll_cur, ll_new, ll_mkt = _ll(hd, current), _ll(hd, w), _ll(hd, base)
    adopt = ll_new < ll_cur - 1e-5
    return {'status': 'ADOPTED' if adopt else 'KEPT_CURRENT', 'day': day, 'tables_before': t_end, 'fit': [t_end, f_end],
            'hold': [f_end, day], 'fit_rows': len(fd), 'hold_rows': len(hd),
            'holdout_logloss': {'market_only': round(ll_mkt, 6), 'current': round(ll_cur, 6), 'candidate': round(ll_new, 6)},
            'candidate': {k: round(v, 3) for k, v in w.items()}, 'weights': w if adopt else current}
