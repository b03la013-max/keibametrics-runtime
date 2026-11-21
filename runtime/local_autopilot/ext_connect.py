"""External-information connection layer for the LOCAL formal ranking (Owner order 2026-11-21 13:09 JST
「水分ボンバーオンラインもNARの資料もGoogleドライブの精読も接続しなさい」).

Where it acts: formal_rakuten, between the Production Full29 numerical ranking (local_krs_bridge_candidate,
`overall` = mean of the W / P2 / P3 role scores) and the Static freeze. The Production 29-index registry, the
KRS Engine, parameter_map, MEC, the 60-ticket cap and the purchase policy are NOT changed. Only the order of the
runners handed to Static (roles 3/6/9, MEC input roles, cap order) changes:

    overall' = (1 - EXT_SHARE) * overall + EXT_SHARE * EXT,      EXT_SHARE = 0.30 (same share as VMI-L, 11/15)
    EXT      = 52 + sum_k  W[k] * (score_k - 52)                  (fixed weights, sum 1; a missing source = 52)

Components (0-100, 52 neutral; fixed priors, never fitted to the race being predicted):
  VMI   水分ボンバー: 0.40 近走 + 0.20 距離 + 0.15 馬場 + 0.25 平均 (available columns renormalised),
        in-race deviation 52 + 2 x (value - race mean)
  CCI / TRI / TMI / KBA / PACE   競馬ブック bands (same mapping as the PAPER engine)
  BVI   NAR sire (0.6) + damsire (0.4)    \
  JKY   NAR jockey x venue                 |  A/E of top-3 against the popularity x field-size expectation of the
  TRN   NAR trainer x venue                |  same venue, shrunk toward 1 with M pseudo-starts, from every NAR
  FRM   NAR venue x distance x frame band  |  official start (2023-01 ..) + the Rakuten result backfill strictly
  HRS   NAR the horse's own record         |  BEFORE the race day. score = 52 + 20 log2(A/E), clipped 30..75
  PAT   Drive-reading patterns (mean)     /   labels below; their strength is measured on NAR, not taken
        MOVE  出戻り/転入/同場 x 前走着順帯   (ゆっくり解説「見逃してるぜ？その穴馬」, T15)    from the documents
        DIRECT 同場同距離の勝ち歴 x 前走着順帯 (浦和 v1.7 / 佐賀 v1.2 W1R, T12)
        LEAD  前走逃げ・先行型               (川崎・高知 YouTube, T8)
        GOROT 馬場 x 距離ローテ x 前走位置     (地方競馬向け・複勝軸選定と穴馬激走パターン)
        LAYOFF 長期休養明け / AGED 高齢×中5日以内 (浦和 v1.6 第26条)
Every value used is recorded in the formal artifact (ext_connection) together with the base ranking, so the
connected ranking is compared with the unconnected one on the same races (prereg C26).
Raw 水分ボンバー numbers and NAR tables stay in the private cache on the runner (not in Git).
"""
from __future__ import annotations

import json
import math
import os
import re
import time
import unicodedata
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

PROFILE = 'KM-LOCAL-EXT-CONNECTION-v1.0-20261121'
EXT_FROM = '2026-11-22'          # first race day (morning edition) on which the connection is applied
EXT_SHARE = 0.30
NEUTRAL = 52.0
W = {'VMI': 0.25,
     'CCI': 0.06, 'TRI': 0.06, 'TMI': 0.06, 'KBA': 0.06, 'PACE': 0.02,
     'BVI': 0.10, 'JKY': 0.08, 'TRN': 0.07, 'FRM': 0.04, 'HRS': 0.08,
     'PAT': 0.12}
SBO_COLS = {'recent': 0.40, 'dist': 0.20, 'going': 0.15, 'avg': 0.25}
BAND_SCORE = {'VERY_STRONG': 66.0, 'STRONG': 59.0, 'NEUTRAL': 52.0, 'CAUTION': 45.0}
PACE_TARGET = {'逃げ': 82.0, '好位': 66.0, '中位': 52.0, '後方': 38.0}
MIN_N, M = 30, 30                 # group cells
H_MIN, H_M = 3, 8                 # the horse's own record
TABLE_VERSION = 1
CIRCUIT = {'OHI': 'NANKAN', 'FNB': 'NANKAN', 'KAW': 'NANKAN', 'URW': 'NANKAN', 'MIZ': 'IWATE', 'MOR': 'IWATE',
           'SON': 'HYOGO', 'HMJ': 'HYOGO'}
VENUE_NAME = {'盛岡': 'MOR', '水沢': 'MIZ', '浦和': 'URW', '船橋': 'FNB', '大井': 'OHI', '川崎': 'KAW', '金沢': 'KNZ',
              '笠松': 'KSM', '名古屋': 'NGY', '園田': 'SON', '姫路': 'HMJ', '高知': 'KOC', '佐賀': 'SAG', '門別': 'MON'}


def private_dir():
    return Path(os.environ.get('KM_PRIVATE_CACHE') or (Path.home() / '.km_private_cache'))


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


def score(ae):
    return max(30.0, min(75.0, NEUTRAL + 20.0 * math.log2(max(ae, 1e-6))))


# ---------------------------------------------------------------- pattern labels (Drive reading)
def labels(cur, hist):
    """cur: {'date','venue','distance','going','age'}; hist: the horse's earlier starts, oldest first,
    each {'date','venue','distance','finish','early'} (early = first-corner ratio 0 front .. 1 rear)."""
    if not hist:
        return [('DEBUT', 'Y')]
    last = hist[-1]
    out = []
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
    if cur.get('distance') and last.get('distance'):
        ch = 'SHORT' if cur['distance'] < last['distance'] else 'LONG' if cur['distance'] > last['distance'] else 'SAME'
        pos = 'NA' if last.get('early') is None else 'FRONT' if last['early'] <= 0.33 else 'BACK'
        out.append(('GOROT', f"{going_class(cur.get('going'))}|{ch}|{pos}"))
    try:
        days = (date.fromisoformat(cur['date']) - date.fromisoformat(last['date'])).days
    except (TypeError, ValueError):
        days = None
    if days is not None and days >= 180:
        out.append(('LAYOFF', 'LONG'))
    if days is not None and days <= 6 and (cur.get('age') or 0) >= 7:
        out.append(('AGED', 'SHORT'))
    return out


# ---------------------------------------------------------------- training rows from NAR + backfill
def _rows(races):
    """One row per start (horse ran), with the pre-race pattern labels from the horse's earlier starts."""
    from runtime.local_autopilot import hist_stats as hs
    hist = defaultdict(list)
    out = []
    for race in sorted(races.values(), key=lambda r: (r['date'], r['venue'], r['race_no'] or 0)):
        field = race.get('field') or sum(1 for x in race['runners'] if x['status'] != 'SCRATCH')
        cur = {'date': race['date'], 'venue': race['venue'], 'distance': race.get('distance'), 'going': race.get('going')}
        done = []
        for x in race['runners']:
            if x['status'] == 'SCRATCH' or not x.get('no'):
                continue
            hk = key(x.get('name')) or x.get('horse_key')
            prev = hist.get(hk, [])
            fc = race['first_corner'].get(x['no'])
            early = (fc - 1) / max(1, field - 1) if fc else None
            if x['status'] == 'RAN' and x.get('pop'):
                out.append({'date': race['date'], 'venue': race['venue'], 'distance': race.get('distance'),
                            'band': dist_band(race.get('distance')), 'going': going_class(race.get('going')),
                            'fband': field_band(field), 'pop': x['pop'], 'top3': bool(x.get('finish') and x['finish'] <= 3),
                            'sire': key(x.get('sire')), 'damsire': key(x.get('damsire')), 'jockey': key(x.get('jockey')),
                            'trainer': key(x.get('trainer')), 'frame': frame_band(x.get('frame')), 'horse': hk,
                            'labels': labels(dict(cur, age=x.get('age')), prev)})
            done.append((hk, {'date': race['date'], 'venue': race['venue'], 'distance': race.get('distance'),
                              'finish': x.get('finish'), 'early': early}))
        for hk, h in done:
            hist[hk].append(h)
    return out, hist


def cell_keys(r):
    v, b, g, d = r['venue'], r['band'], r['going'], r['distance']
    ks = []
    if r['sire']:
        ks += [('S', r['sire'], v, b, g), ('S', r['sire'], v), ('S', r['sire'], b), ('S', r['sire'])]
    if r['damsire']:
        ks += [('D', r['damsire'], v), ('D', r['damsire'], b), ('D', r['damsire'])]
    if r['jockey']:
        ks += [('J', r['jockey'], v), ('J', r['jockey'])]
    if r['trainer']:
        ks += [('T', r['trainer'], v), ('T', r['trainer'])]
    if r['frame']:
        ks += [('F', v, d, r['frame'], r['fband']), ('F', v, d, r['frame'])]
    if r['horse']:
        ks += [('H', r['horse'], v, d), ('H', r['horse'], v), ('H', r['horse'])]
    for name, val in r['labels']:
        ks += [('P', name, val, circ(v)), ('P', name, val)]
    return ks


def build_tables(races, before_day, with_history=False):
    rows, hist = _rows({k: v for k, v in races.items() if v['date'] < before_day})
    base = defaultdict(lambda: [0, 0])
    for r in rows:
        k = (r['venue'], min(r['pop'], 10), r['fband'])
        base[k][0] += 1
        base[k][1] += r['top3']
    exp = {k: v[1] / v[0] for k, v in base.items() if v[0]}
    cells = defaultdict(lambda: [0, 0, 0.0])
    for r in rows:
        e = exp.get((r['venue'], min(r['pop'], 10), r['fband']))
        if e is None:
            continue
        for k in cell_keys(r):
            c = cells[k]
            c[0] += 1
            c[1] += r['top3']
            c[2] += e
    out = {'version': TABLE_VERSION, 'before_day': before_day, 'starts': len(rows),
            'period': [min((r['date'] for r in rows), default=None), max((r['date'] for r in rows), default=None)],
            'cells': {json.dumps(k, ensure_ascii=False): [n, a, round(e, 4)] for k, (n, a, e) in cells.items()}}
    if with_history:   # last 20 starts per horse are enough for every label
        return out, {h: v[-20:] for h, v in hist.items()}
    return out


def ensure(root, day, budget_s=None):
    """Build (once per race day) the NAR tables and horse histories from every source dated before `day`.
    Returns the tables or None. Kept in the private cache, never in the data branch."""
    p = private_dir() / 'ext' / f'tables_{day}.json'
    h = private_dir() / 'ext' / f'history_{day}.json'
    if p.exists() and h.exists():
        return p
    from runtime.local_autopilot import hist_stats as hs
    t0 = time.time()
    races, src = hs.load_sources(root, os.environ.get('KM_NAR_ROOT'))
    if not races:
        return None
    t, hist = build_tables(races, day, with_history=True)
    t['source'] = src
    t['build_seconds'] = round(time.time() - t0, 1)
    p.parent.mkdir(parents=True, exist_ok=True)
    h.write_text(json.dumps(hist, ensure_ascii=False, separators=(',', ':')))
    p.write_text(json.dumps(t, ensure_ascii=False, separators=(',', ':')))
    for old in sorted(p.parent.glob('*_20*.json')):   # keep the last 3 days
        if old.stem.split('_')[-1] < (date.fromisoformat(day) - timedelta(days=3)).isoformat():
            old.unlink()
    return p


_LOADED = {}


def load(day):
    if day in _LOADED:
        return _LOADED[day]
    p = private_dir() / 'ext' / f'tables_{day}.json'
    h = private_dir() / 'ext' / f'history_{day}.json'
    if not (p.exists() and h.exists()):
        return None
    t = json.loads(p.read_text())
    cells = {tuple(json.loads(k)): v for k, v in t.pop('cells').items()}
    _LOADED.clear()
    _LOADED[day] = (t, cells, json.loads(h.read_text()))
    return _LOADED[day]


def ae_of(cells, keys, min_n=MIN_N, m=M):
    """Most specific cell with >= min_n starts -> (score, key, n, A/E raw)."""
    for k in keys:
        c = cells.get(k)
        if c and c[0] >= min_n and c[2] > 0:
            pbar = c[2] / c[0]
            ae = (c[1] + m * pbar) / (c[2] + m * pbar)
            return score(ae), k, c[0], round(c[1] / c[2], 3)
    return None, None, 0, None


# ---------------------------------------------------------------- current race
def card_history(r, race_day):
    """The runner's Rakuten card starts (newest first on the card) -> oldest-first history entries."""
    out = []
    for s in r.get('starts') or []:
        try:
            y, m_, d = s['date'].split('.')
            dt = date(2000 + int(y), int(m_), int(d)).isoformat()
        except (KeyError, ValueError, AttributeError):
            continue
        v = next((c for n, c in VENUE_NAME.items() if n in str(s.get('venue') or '')), None)
        if not v or dt >= race_day:
            continue
        pos = s.get('content_positions') or []
        fs = s.get('field_size')
        out.append({'date': dt, 'venue': v, 'distance': s.get('distance'), 'finish': s.get('finish'),
                    'early': (pos[0] - 1) / (fs - 1) if pos and fs and fs > 1 else None})
    return sorted(out, key=lambda x: x['date'])


def merged_history(nar_hist, card_hist):
    seen = {(h['date'], h['venue']) for h in card_hist}
    return sorted([h for h in nar_hist if (h['date'], h['venue']) not in seen] + card_hist, key=lambda x: x['date'])


def sbo_vmi(table, active):
    comp = {}
    for no in active:
        row = (table or {}).get(no) or (table or {}).get(str(no))
        if not row:
            continue
        parts = [(row.get(c), w) for c, w in SBO_COLS.items() if isinstance(row.get(c), (int, float))]
        if parts:
            comp[no] = sum(v * w for v, w in parts) / sum(w for _, w in parts)
    if len(comp) < 2:
        return {}, {}
    mu = sum(comp.values()) / len(comp)
    return {no: max(0.0, min(100.0, NEUTRAL + 2.0 * (v - mu))) for no, v in comp.items()}, comp


def race_ext(race, runners, day, sbo_table=None, kb=None):
    """Per-runner EXT components and EXT. `race`: venue_id, distance, going, race_date; `runners`: parsed card
    rows (horse_no, name, sire, damsire, current_jockey, trainer, frame_no, age, starts)."""
    loaded = load(day)
    t, cells, hist = loaded if loaded else (None, {}, {})
    active = [x['horse_no'] for x in runners]
    vmi, _ = sbo_vmi(sbo_table, active)
    kb = kb or {}
    v, d = race['venue_id'], race.get('distance')
    b, g = dist_band(d), going_class(race.get('going'))
    field = len(runners)
    out = {}
    for x in runners:
        no = x['horse_no']
        comp, src = {}, {}
        if no in vmi:
            comp['VMI'] = vmi[no]
        kbx = kb.get(no) or kb.get(str(no)) or {}
        if kbx:
            comp['CCI'] = BAND_SCORE.get(kbx.get('cci'), NEUTRAL)
            comp['TRI'] = BAND_SCORE.get(kbx.get('tri'), NEUTRAL)
            if kbx.get('tm') is not None:
                comp['TMI'] = float(kbx['tm'])
            ab = [y for y in (kbx.get('rt'), kbx.get('cpu')) if y is not None]
            if ab:
                comp['KBA'] = sum(ab) / len(ab)
            if kbx.get('pace') in PACE_TARGET:
                comp['PACE'] = PACE_TARGET[kbx['pace']]
        if cells:
            s_, d_ = key(x.get('sire')), key(x.get('damsire'))
            ss = ae_of(cells, [('S', s_, v, b, g), ('S', s_, v), ('S', s_, b), ('S', s_)]) if s_ else (None,) * 4
            ds = ae_of(cells, [('D', d_, v), ('D', d_, b), ('D', d_)]) if d_ else (None,) * 4
            if ss[0] is not None or ds[0] is not None:
                comp['BVI'] = (0.6 * (ss[0] if ss[0] is not None else NEUTRAL) + 0.4 * (ds[0] if ds[0] is not None else NEUTRAL))
                src['BVI'] = {'sire': ss[1:], 'damsire': ds[1:]}
            j = key(x.get('current_jockey'))
            js = ae_of(cells, [('J', j, v), ('J', j)]) if j else (None,) * 4
            if js[0] is not None:
                comp['JKY'], src['JKY'] = js[0], js[1:]
            tr = key(x.get('trainer'))
            ts = ae_of(cells, [('T', tr, v), ('T', tr)]) if tr else (None,) * 4
            if ts[0] is not None:
                comp['TRN'], src['TRN'] = ts[0], ts[1:]
            fb = frame_band(x.get('frame_no'))
            fs = ae_of(cells, [('F', v, d, fb, field_band(field)), ('F', v, d, fb)]) if fb else (None,) * 4
            if fs[0] is not None:
                comp['FRM'], src['FRM'] = fs[0], fs[1:]
            hk = key(x.get('name'))
            hs_ = ae_of(cells, [('H', hk, v, d), ('H', hk, v), ('H', hk)], H_MIN, H_M) if hk else (None,) * 4
            if hs_[0] is not None:
                comp['HRS'], src['HRS'] = hs_[0], hs_[1:]
            hh = merged_history(hist.get(hk) or [], card_history(x, day))
            labs = labels({'date': day, 'venue': v, 'distance': d, 'going': race.get('going'), 'age': x.get('age')}, hh)
            ps = [(lab, ae_of(cells, [('P', lab[0], lab[1], circ(v)), ('P', lab[0], lab[1])])) for lab in labs]
            ps = [(lab, a) for lab, a in ps if a[0] is not None]
            if ps:
                comp['PAT'] = sum(a[0] for _, a in ps) / len(ps)
                src['PAT'] = [{'label': f'{lab[0]}={lab[1]}', 'score': round(a[0], 1), 'n': a[2], 'ae': a[3]} for lab, a in ps]
        ext = NEUTRAL + sum(W[k] * (comp[k] - NEUTRAL) for k in comp)
        out[no] = {'EXT': round(ext, 2), 'components': {k: round(val, 1) for k, val in comp.items()}, 'cells': src}
    status = {'tables': bool(cells), 'tables_period': (t or {}).get('period'), 'tables_starts': (t or {}).get('starts'),
              'sbo_horses': len(vmi), 'kb_horses': sum(1 for x in runners if kb.get(x['horse_no']) or kb.get(str(x['horse_no'])))}
    return out, status


def apply(ranking_scores, ext):
    """ranking_scores: candidate runner_scores (runner_id, overall). Returns (new ranking, rows)."""
    rows = []
    for r in ranking_scores:
        no = int(r['runner_id'])
        e = (ext.get(no) or {}).get('EXT', NEUTRAL)
        rows.append({'runner_id': str(no), 'overall_base': round(r['overall'], 3), 'EXT': e,
                     'overall_connected': round((1 - EXT_SHARE) * r['overall'] + EXT_SHARE * e, 3)})
    ranking = [x['runner_id'] for x in sorted(rows, key=lambda x: (-x['overall_connected'], int(x['runner_id'])))]
    return ranking, rows


# ---------------------------------------------------------------- formal hook
def enabled(race_date):
    return str(race_date) >= EXT_FROM and os.environ.get('KM_EXT_CONNECTION', '1') != '0'


def sbo_cache_path(race_date, venue_id, race_no):
    return private_dir() / 'sbo' / race_date / f'{venue_id}_{int(race_no):02d}.json'


def save_sbo(race_date, venue_id, race_no, snap, fetched_at):
    """PAPER-side fetch -> private cache (the raw 水分ボンバー numbers never enter Git)."""
    if not snap or snap.get('status') != 'OK':
        return
    p = sbo_cache_path(race_date, venue_id, race_no)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({'fetched_at': fetched_at, 'sha256': snap.get('sha256'),
                             'table': {str(k): v for k, v in snap['table'].items()}}, ensure_ascii=False))


def sbo_for(r, deadline, fetch=None):
    """Cached snapshot fetched before the cutoff, else one fresh fetch (same access policy as the PAPER side)."""
    from datetime import datetime
    p = sbo_cache_path(r['race_date'], r['venue_id'], r['race_no'])
    try:
        c = json.loads(p.read_text())
        if datetime.fromisoformat(c['fetched_at']) < deadline:
            return {int(k): v for k, v in c['table'].items()}, {'status': 'USED_CACHE', 'fetched_at': c['fetched_at'], 'sha256': c['sha256']}
    except (OSError, ValueError, KeyError):
        pass
    if fetch is None:
        return None, {'status': 'NOT_FETCHED'}
    try:
        snap, at = fetch()
        if snap.get('status') != 'OK':
            return None, {'status': snap.get('status')}
        if datetime.fromisoformat(at) >= deadline:
            return None, {'status': 'FETCHED_AFTER_CUTOFF'}
        save_sbo(r['race_date'], r['venue_id'], r['race_no'], snap, at)
        return snap['table'], {'status': 'USED_FRESH', 'fetched_at': at, 'sha256': snap.get('sha256')}
    except Exception as exc:
        return None, {'status': 'UNAVAILABLE', 'error': f'{type(exc).__name__}:{str(exc)[:120]}'}


def kb_for(day_dir, r, deadline):
    from datetime import datetime
    p = Path(day_dir) / 'external' / 'keibabook_bands.json'
    try:
        doc = json.loads(p.read_text())
    except (OSError, ValueError):
        return None, {'status': 'NOT_CAPTURED'}
    cap = datetime.fromisoformat(str(doc.get('captured_at')).replace('Z', '+00:00'))
    if cap >= deadline:
        return None, {'status': 'CAPTURED_AFTER_CUTOFF', 'captured_at': doc.get('captured_at')}
    race = next((x for x in doc.get('races', []) if x.get('venue') == r['venue_name'] and x.get('race_no') == r['race_no']), None)
    if not race:
        return None, {'status': 'NOT_PROVIDED', 'captured_at': doc.get('captured_at')}
    kb = {int(k): v for k, v in (race.get('horses') or {}).items() if v}
    return kb, {'status': 'USED' if kb else 'NOT_PROVIDED', 'captured_at': doc.get('captured_at'), 'horses': len(kb)}


def connect(r, head, active, num_pred, day_dir, deadline, sbo_fetch=None):
    """-> connection record with the connected ranking. Never changes num_pred."""
    day = r['race_date']
    sbo_t, sbo_m = sbo_for(r, deadline, sbo_fetch)
    kb, kb_m = kb_for(day_dir, r, deadline)
    race = {'venue_id': r['venue_id'], 'distance': head.get('distance'), 'going': head.get('going'), 'race_date': day}
    ext, st = race_ext(race, active, day, sbo_t, kb)
    ranking, rows = apply(num_pred['runner_scores'], ext)
    rec = {'profile': PROFILE, 'owner_order': '2026-11-21 13:09 JST 接続しなさい', 'ext_share': EXT_SHARE, 'weights': W,
           'sbo_columns': SBO_COLS, 'status': st, 'sbo': sbo_m, 'keibabook': kb_m,
           'ranking_base': list(num_pred['ranking']), 'ranking': ranking, 'rows': rows,
           'runners': {str(k): v for k, v in ext.items()},
           'changed_top3': list(num_pred['ranking'][:3]) != ranking[:3],
           'changed_top6': sorted(num_pred['ranking'][:6]) != sorted(ranking[:6])}
    return rec


# ---------------------------------------------------------------- C26 comparison (connected vs base, same races)
def audit(root, days):
    """Effective formal revision per race: connected ranking vs the base ranking it replaced."""
    rows = []
    for day in sorted(days):
        dd = Path(root) / day
        for s1 in sorted((dd / 'formal').glob('*.summary.json')):
            k = s1.name.split('.')[0]
            s2 = dd / 'formal' / 'rev2' / s1.name
            try:
                sm = json.loads((s2 if s2.exists() else s1).read_text())
                res = json.loads(((dd / 'formal' / 'rev2' / f'{k}.result.json') if (dd / 'formal' / 'rev2' / f'{k}.result.json').exists()
                                  else (dd / 'formal' / f'{k}.result.json')).read_text())
            except (OSError, ValueError):
                continue
            if sm.get('status') != 'SIGNED_FINAL' or not sm.get('ranking_base') or not (sm.get('ext_connection') or {}).get('profile'):
                continue
            order = [str(x) for x in (res.get('order') or [])[:3]]
            if len(order) < 3:
                continue
            rows.append({'day': day, 'race': k, 'venue': k.split('_')[0], 'order': order,
                         'base': [str(x) for x in sm['ranking_base']], 'conn': [str(x) for x in sm['ranking']]})

    def m(rs, col):
        n = len(rs)
        if not n:
            return {'races': 0}
        win3 = sum(r['order'][0] in r[col][:3] for r in rs)
        sec6 = sum(r['order'][1] in r[col][:6] for r in rs)
        all9 = sum(all(x in r[col][:9] for x in r['order']) for r in rs)
        rk = [r[col].index(r['order'][0]) + 1 for r in rs if r['order'][0] in r[col]]
        return {'races': n, 'winner_in_W3': win3, 'winner_in_W3_rate': round(100 * win3 / n, 1),
                'second_in_P2_6': sec6, 'top3_in_P3_9': all9, 'winner_mean_rank': round(sum(rk) / len(rk), 2) if rk else None}
    by = {}
    for v in sorted({r['venue'] for r in rows}):
        rs = [r for r in rows if r['venue'] == v]
        by[v] = {'base': m(rs, 'base'), 'connected': m(rs, 'conn')}
    return {'races': len(rows), 'base': m(rows, 'base'), 'connected': m(rows, 'conn'), 'by_venue': by,
            'changed_W3': sum(sorted(r['base'][:3]) != sorted(r['conn'][:3]) for r in rows),
            'gained': [r['race'] for r in rows if r['order'][0] in r['conn'][:3] and r['order'][0] not in r['base'][:3]],
            'lost': [r['race'] for r in rows if r['order'][0] in r['base'][:3] and r['order'][0] not in r['conn'][:3]]}
