"""LOCAL statistical tables from historical results (Owner 2026-11-19「統計的アプローチも実装したい」). Evidence only.

Class: HISTORICAL_BACKFILL_LEARNING (not Forward OOS). Tables are audit priors and research leads: they never
change Production numbers, roles or tickets. A table cell only becomes a pre-registered Forward OOS candidate
by Owner decision, after a time-split check here.

Every cell carries what is needed to judge it (ChatGPT 11/19 proposal A, adopted):
  source, period, conditions, unit (one row = one start), races, starts, unique_horses,
  1st / 2nd / 3rd / out counts, win / 2nd / 3rd / top2 / top3 rates, Wilson 95 % for win and top3,
  100-yen flat ROI for 単勝 and 複勝 (from the official payouts, so the 7頭以下 = 2着まで rule is automatic),
  market-adjusted A/E (actual top3 / expected top3 from the popularity x field-band base of the same data),
  missing count, small-sample flag (starts < MIN_N), and a leakage note (historical popularity is FINAL).
Venues are never pooled: every key starts with the venue (Owner 2026-11-19).

Tables
  T1_BASE      venue x surface x distance x class      field size, winning-time median, favourite win / top3
  T2_POP       venue x distance band x popularity band  finish-position split (W / P2 / P3 differ)
  T3_GATE      venue x distance x going x field band x 枠  with A/E so strong horses drawn wide do not fool it
  T4_FRONT     three separate denominators (11/19 proposal 3): pre-race front candidate -> took the lead group;
               took the lead group -> still there at the last corner; last-corner position -> 1st / 2nd / 3rd
  T5_CHANGE    distance change / venue change / days since last start, each vs the horse's previous start
Pre-race inputs only for the "candidate" / "change" definitions: a horse's earlier starts (strictly earlier date).
Rates are never multiplied together; a horse's matching cells are listed side by side (no additive score).
"""
import csv
import io
import json
import math
import re
from collections import defaultdict
from datetime import date

PROFILE = 'KM-LOCAL-HIST-STATS-v1.0-20261119'
CLASS = 'HISTORICAL_BACKFILL_LEARNING (not Forward OOS)'
MIN_N = 30
LEAK_NOTE = 'popularity / odds are FINAL (post-race); at prediction time compare with the pre-race odds snapshot'
VENUE_CODE = {'盛岡': 'MOR', '水沢': 'MIZ', '浦和': 'URW', '船橋': 'FNB', '大井': 'OHI', '川崎': 'KAW', '金沢': 'KNZ',
              '笠松': 'KSM', '名古屋': 'NGY', '園田': 'SON', '姫路': 'HMJ', '高知': 'KOC', '佐賀': 'SAG', '門別': 'MON',
              '帯広': 'OBI', '帯広ば': 'OBI'}


def going_class(g):
    g = str(g or '')
    return 'WET' if ('不' in g or '重' in g) and '稍' not in g else 'DAMP' if '稍' in g else 'DRY' if '良' in g else 'UNKNOWN'


def dist_band(d):
    d = int(d or 0)
    return 'UNKNOWN' if not d else 'S' if d <= 1300 else 'M' if d <= 1700 else 'L'


def field_band(n):
    return 'F<=8' if n <= 8 else 'F9-11' if n <= 11 else 'F12+'


def pop_band(p):
    return None if not p else str(p) if p <= 5 else '6-9' if p <= 9 else '10+'


def class_code(cond):
    """Coarse class from the race condition text ('C2三' -> 'C2', 'B1' -> 'B1', '2歳' -> '2YO', 'A2' ...)."""
    s = str(cond or '')
    m = re.search(r'([ABC])\s*([1-4])', s)
    if m:
        return m[1] + m[2]
    if re.search(r'[23]歳', s):
        return re.search(r'([23])歳', s)[1] + 'YO'
    if any(k in s for k in ('重賞', 'Jpn', 'SI', 'SII', 'SIII', 'Ｇ', '特別')):
        return 'OPEN'
    return 'OTHER'


def _int(x):
    m = re.search(r'-?\d+', str(x or ''))
    return int(m[0]) if m else None


def _time(x):
    m = re.match(r'(?:(\d+):)?(\d+(?:\.\d+)?)', str(x or '').strip())
    return (int(m[1] or 0) * 60 + float(m[2])) if m else None


def corner_positions(s):
    """'(3,5)8,2-11' style passing order -> {horse_no: position (1 = leader)}. Grouped horses share a rank."""
    pos, k = {}, 0
    for tok in re.findall(r'\([^)]*\)|\d+', str(s or '')):
        nums = [int(x) for x in re.findall(r'\d+', tok)]
        k += 1
        for n in nums:
            pos.setdefault(n, k)
        k += len(nums) - 1
    return pos


# ------------------------------------------------------------------ adapters -> normalised races
def _rows(text):
    return list(csv.DictReader(io.StringIO(text)))


def _decode(b):
    for enc in ('utf-8-sig', 'cp932'):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            continue
    return b.decode('utf-8', 'replace')


def from_nar_csv(racelist, horselist, payback, source='NAR_OFFICIAL_CSV'):
    """keiba.go.jp data-download CSVs (bytes or str) -> {race_id: race}. Column names per the official manual."""
    t = lambda x: _decode(x) if isinstance(x, (bytes, bytearray)) else x
    races = {}
    for r in _rows(t(racelist)):
        v = VENUE_CODE.get(r.get('競馬場', '').strip(), r.get('競馬場', '').strip())
        d = r.get('競走年月日', '').replace('/', '-').strip()
        rid = f"{v}_{d.replace('-', '')}_R{int(_int(r.get('レース番号')) or 0):02d}"
        corners = [r.get(f'コーナー通過順{i}') for i in range(1, 9) if r.get(f'コーナー通過順{i}')]
        races[rid] = {'race_id': rid, 'date': d, 'venue': v, 'race_no': _int(r.get('レース番号')),
                      'surface': 'TURF' if '芝' in r.get('芝ダート区分', '') else 'DIRT', 'distance': _int(r.get('距離')),
                      'going': r.get('馬場', '').strip(), 'weather': r.get('天候', '').strip(), 'cond': r.get('条件', '').strip(),
                      'field': _int(r.get('頭数')), 'first_corner': corner_positions(corners[0]) if corners else {},
                      'last_corner': corner_positions(corners[-1]) if corners else {}, 'runners': [], 'payouts': {},
                      'source': source}
    for h in _rows(t(horselist)):
        v = VENUE_CODE.get(h.get('競馬場', '').strip(), h.get('競馬場', '').strip())
        d = h.get('競走年月日', '').replace('/', '-').strip()
        rid = f"{v}_{d.replace('-', '')}_R{int(_int(h.get('レース番号')) or 0):02d}"
        if rid not in races:
            continue
        fin_txt = h.get('着順', '').strip()
        fin = _int(fin_txt) if fin_txt.isdigit() else None
        races[rid]['runners'].append({
            'no': _int(h.get('馬番')), 'frame': _int(h.get('枠番')), 'name': h.get('馬名', '').strip(),
            'horse_key': f"{h.get('馬名', '').strip()}|{h.get('生年月日', '').strip()}",
            'sex': h.get('性', '').strip(), 'age': _int(h.get('齢')), 'sire': h.get('父馬名', '').strip() or None,
            'damsire': h.get('母父馬名', '').strip() or None, 'jockey': h.get('騎手名', '').strip(),
            'trainer': h.get('調教師', '').strip(), 'load': h.get('負担重量', '').strip(), 'bw': _int(h.get('馬体重')),
            'bw_chg': _int(h.get('馬体重増減')), 'finish': fin, 'finish_text': fin_txt,
            'status': 'RAN' if fin else ('SCRATCH' if any(k in fin_txt for k in ('取', '除')) or not fin_txt else 'DNF'),
            'pop': _int(h.get('人気')), 'time': _time(h.get('タイム')), 'last3f': h.get('上がり3F', '').strip()})
    for p in _rows(t(payback)):
        v = VENUE_CODE.get(p.get('競馬場', '').strip(), p.get('競馬場', '').strip())
        d = p.get('競走年月日', '').replace('/', '-').strip()
        rid = f"{v}_{d.replace('-', '')}_R{int(_int(p.get('レース番号')) or 0):02d}"
        if rid not in races:
            continue
        pay = races[rid]['payouts']
        if _int(p.get('単勝組番')):
            pay.setdefault('WIN', {})[str(_int(p['単勝組番']))] = _int(p.get('単勝払戻金（円）'))
        for i in (1, 2, 3):
            if _int(p.get(f'複勝組番{i}')):
                pay.setdefault('PLACE', {})[str(_int(p[f'複勝組番{i}']))] = _int(p.get(f'複勝払戻金{i}（円）'))
    return races


def from_rakuten_backfill(rec):
    """runtime/local_autopilot/backfill.py record -> race (order / payouts / header; per-row cells mapped
    where the class names are known: number, order, position=枠)."""
    v, h, res = rec['venue_id'], rec.get('header') or {}, rec.get('result') or {}
    rid = f"{v}_{rec['race_date'].replace('-', '')}_R{int(rec['race_no']):02d}"
    order = res.get('order') or []
    runners = []
    for c in rec.get('rows') or []:
        no = _int(c.get('number'))
        if not no:
            continue
        fin = order.index(no) + 1 if no in order else None
        st = re.match(r'([牡牝セ騸])\s*(\d+)', c.get('state') or '')
        w = re.findall(r'[+-]?\d+', (c.get('weight') or '').replace('±', '+'))
        runners.append({'no': no, 'frame': _int(c.get('position')), 'name': c.get('horse') or c.get('name'),
                        'horse_key': ('RKT:' + c['horse_id']) if c.get('horse_id') else (c.get('horse') or c.get('name')),
                        'finish': fin, 'sex': st[1] if st else None, 'age': int(st[2]) if st else None,
                        'load': c.get('weightTax'), 'bw': int(w[0]) if w else None, 'bw_chg': int(w[1]) if len(w) > 1 else None,
                        'jockey': re.sub(r'\s*\(.*', '', c.get('jockey') or '').lstrip('☆▲△◇★') or None,
                        'trainer': c.get('tamer'), 'time': _time(c.get('time')), 'last3f': c.get('spurt'),
                        'status': 'RAN' if fin else ('SCRATCH' if no in (res.get('non_starters') or []) else 'DNF'),
                        'pop': _int(c.get('rank')), 'sire': None, 'damsire': None})
    corners = [cv for name, cv in (h.get('corners') or []) if 'コーナー' in name]
    pays = {}
    for k in ('WIN', 'PLACE'):
        for combo, yen in ((res.get('payouts') or {}).get(k) or {}).items():
            pays.setdefault(k, {})[str(_int(combo))] = yen
    return {rid: {'race_id': rid, 'date': rec['race_date'], 'venue': v, 'race_no': rec['race_no'], 'surface': h.get('surface', 'DIRT'),
                  'distance': h.get('distance'), 'going': h.get('going') or '', 'weather': h.get('weather'), 'cond': h.get('race_name', ''),
                  'field': sum(1 for r in runners if r['status'] != 'SCRATCH') or len(order),
                  'first_corner': corner_positions(corners[0]) if corners else {},
                  'last_corner': corner_positions(corners[-1]) if corners else {},
                  'runners': runners, 'payouts': pays, 'source': 'RAKUTEN_RESULT_PAGE'}}


# ------------------------------------------------------------------ per-start rows with pre-race history features
def starts(races):
    """Flatten to one row per start of a horse that ran; attach pre-race features from the horse's earlier starts."""
    hist = defaultdict(list)
    out = []
    for race in sorted(races.values(), key=lambda r: (r['date'], r['venue'], r['race_no'] or 0)):
        field = race.get('field') or sum(1 for x in race['runners'] if x['status'] != 'SCRATCH')
        for x in race['runners']:
            if x['status'] == 'SCRATCH' or not x.get('no'):
                continue
            prev = [p for p in hist.get(x.get('horse_key'), []) if p['date'] < race['date']]
            last = prev[-1] if prev else None
            early = [p['fc_ratio'] for p in prev[-5:] if p['fc_ratio'] is not None]
            fc = race['first_corner'].get(x['no'])
            lc = race['last_corner'].get(x['no'])
            row = {'race_id': race['race_id'], 'date': race['date'], 'venue': race['venue'], 'surface': race['surface'],
                   'distance': race['distance'], 'band': dist_band(race['distance']), 'going': going_class(race['going']),
                   'cls': class_code(race['cond']), 'field': field, 'fband': field_band(field), 'frame': x.get('frame'),
                   'no': x['no'], 'horse': x.get('horse_key'), 'pop': x.get('pop'), 'finish': x.get('finish'),
                   'ran': x['status'] == 'RAN', 'time': x.get('time'), 'sire': x.get('sire'),
                   'win_pay': (race['payouts'].get('WIN') or {}).get(str(x['no'])),
                   'place_pay': (race['payouts'].get('PLACE') or {}).get(str(x['no'])),
                   'fc': fc, 'lc': lc, 'fc_ratio': (fc - 1) / max(1, field - 1) if fc else None,
                   'lc_ratio': (lc - 1) / max(1, field - 1) if lc else None,
                   'front_candidate': (sum(early) / len(early) <= 0.25) if len(early) >= 2 else None,
                   'prev_dist': last['distance'] if last else None, 'prev_venue': last['venue'] if last else None,
                   'days_since': (date.fromisoformat(race['date']) - date.fromisoformat(last['date'])).days if last else None}
            out.append(row)
            hist[x.get('horse_key')].append({'date': race['date'], 'distance': race['distance'], 'venue': race['venue'],
                                             'fc_ratio': row['fc_ratio']})
    return out


# ------------------------------------------------------------------ cell statistics
def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 4), round(c + h, 4)]


def expected_top3(rows):
    base = defaultdict(lambda: [0, 0])
    for r in rows:
        if r['pop']:
            k = (r['venue'], min(r['pop'], 10), r['fband'])
            base[k][0] += 1
            base[k][1] += bool(r['finish'] and r['finish'] <= 3)
    return {k: v[1] / v[0] for k, v in base.items() if v[0]}


def cell(rows, table, conditions, exp=None, source='', period=None):
    n = len(rows)
    c = [sum(1 for r in rows if r['finish'] == i) for i in (1, 2, 3)]
    rate = lambda k: round(k / n, 4) if n else None
    win_stake = sum(1 for r in rows)
    out = {'table': table, 'conditions': conditions, 'unit': 'start', 'source': source, 'period': period,
           'races': len({r['race_id'] for r in rows}), 'starts': n, 'unique_horses': len({r['horse'] for r in rows}),
           'n1': c[0], 'n2': c[1], 'n3': c[2], 'nout': n - sum(c),
           'win': rate(c[0]), 'p2': rate(c[1]), 'p3': rate(c[2]), 'top2': rate(c[0] + c[1]), 'top3': rate(sum(c)),
           'win_ci95': wilson(c[0], n), 'top3_ci95': wilson(sum(c), n),
           'roi_win': round(sum(r['win_pay'] or 0 for r in rows if r['finish'] == 1) / (100 * win_stake), 3) if win_stake else None,
           'roi_place': round(sum(r['place_pay'] or 0 for r in rows) / (100 * win_stake), 3) if win_stake else None,
           'missing_pop': sum(1 for r in rows if not r['pop']), 'small_sample': n < MIN_N}
    if exp is not None:
        e = sum(exp.get((r['venue'], min(r['pop'], 10), r['fband']), 0) for r in rows if r['pop'])
        out['expected_top3'] = round(e, 2)
        out['ae_top3'] = round(sum(c) / e, 3) if e else None
    return out


def _period(rows):
    ds = sorted(r['date'] for r in rows)
    return [ds[0], ds[-1]] if ds else None


def build(races, source):
    rows = starts(races)
    exp = expected_top3(rows)
    per = _period(rows)
    tables = defaultdict(list)

    def group(table, keyf, names, sub=None, with_exp=True):
        g = defaultdict(list)
        for r in (sub if sub is not None else rows):
            k = keyf(r)
            if k is not None and None not in k:
                g[k].append(r)
        for k, rs in sorted(g.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
            tables[table].append(cell(rs, table, dict(zip(names, k)), exp if with_exp else None, source, per))

    # T1 base
    by_race = defaultdict(list)
    for r in rows:
        by_race[r['race_id']].append(r)
    base = defaultdict(list)
    for rid, rs in by_race.items():
        r0 = rs[0]
        base[(r0['venue'], r0['surface'], r0['distance'], r0['cls'])].append(rs)
    for k, rlist in sorted(base.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
        wt = sorted(x['time'] for rs in rlist for x in rs if x['finish'] == 1 and x['time'])
        fav = [x for rs in rlist for x in rs if x['pop'] == 1]
        tables['T1_BASE'].append({'table': 'T1_BASE', 'conditions': dict(zip(('venue', 'surface', 'distance', 'class'), k)),
                                  'source': source, 'period': per, 'races': len(rlist),
                                  'avg_field': round(sum(len(rs) for rs in rlist) / len(rlist), 2),
                                  'win_time_median': wt[len(wt) // 2] if wt else None,
                                  'fav_win': round(sum(1 for x in fav if x['finish'] == 1) / len(fav), 4) if fav else None,
                                  'fav_top3': round(sum(1 for x in fav if x['finish'] and x['finish'] <= 3) / len(fav), 4) if fav else None,
                                  'small_sample': len(rlist) < 12})
    group('T2_POP', lambda r: (r['venue'], r['band'], pop_band(r['pop'])), ('venue', 'band', 'pop'), with_exp=False)
    group('T3_GATE', lambda r: (r['venue'], r['distance'], r['going'], r['fband'], r['frame']),
          ('venue', 'distance', 'going', 'field_band', 'frame'))
    # T4 front: three denominators
    cand = [r for r in rows if r['front_candidate'] is not None and r['fc_ratio'] is not None]
    g = defaultdict(lambda: [0, 0])
    for r in cand:
        k = (r['venue'], r['band'], r['front_candidate'])
        g[k][0] += 1
        g[k][1] += r['fc_ratio'] <= 0.25
    for k, (n, hit) in sorted(g.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
        tables['T4_FRONT'].append({'table': 'T4_FRONT', 'stage': 'TAKE_POSITION', 'source': source, 'period': per,
                                   'conditions': dict(zip(('venue', 'band', 'pre_race_front_candidate'), k)),
                                   'starts': n, 'took_lead_group': hit, 'rate': round(hit / n, 4), 'ci95': wilson(hit, n),
                                   'small_sample': n < MIN_N})
    took = [r for r in rows if r['fc_ratio'] is not None and r['fc_ratio'] <= 0.25 and r['lc_ratio'] is not None]
    g = defaultdict(lambda: [0, 0])
    for r in took:
        g[(r['venue'], r['band'])][0] += 1
        g[(r['venue'], r['band'])][1] += r['lc_ratio'] <= 0.25
    for k, (n, hit) in sorted(g.items()):
        tables['T4_FRONT'].append({'table': 'T4_FRONT', 'stage': 'KEEP_POSITION', 'source': source, 'period': per,
                                   'conditions': dict(zip(('venue', 'band'), k)), 'starts': n, 'kept_to_last_corner': hit,
                                   'rate': round(hit / n, 4), 'ci95': wilson(hit, n), 'small_sample': n < MIN_N})
    group('T4_FRONT_FINISH', lambda r: (r['venue'], r['band'], None if r['lc'] is None else min(r['lc'], 6)),
          ('venue', 'band', 'last_corner_pos(6=6+)'))
    # T5 changes vs the previous start
    def dchg(r):
        if not r['prev_dist'] or not r['distance']:
            return None
        d = r['distance'] - r['prev_dist']
        return 'SHORTER' if d <= -100 else 'LONGER' if d >= 100 else 'SAME'
    def gap(r):
        s = r['days_since']
        return None if s is None else '<=14d' if s <= 14 else '15-35d' if s <= 35 else '36-90d' if s <= 90 else '>90d'
    group('T5_DIST_CHANGE', lambda r: (r['venue'], r['band'], dchg(r)), ('venue', 'band', 'distance_change'))
    group('T5_VENUE_CHANGE', lambda r: (r['venue'], None if not r['prev_venue'] else ('SAME' if r['prev_venue'] == r['venue'] else 'FROM_' + r['prev_venue'])),
          ('venue', 'previous_venue'))
    group('T5_INTERVAL', lambda r: (r['venue'], gap(r)), ('venue', 'days_since_last'))
    return {'profile': PROFILE, 'class': CLASS, 'source': source, 'period': per, 'races': len(by_race), 'starts': len(rows),
            'min_n': MIN_N, 'leakage_note': LEAK_NOTE, 'tables': dict(tables)}


# ------------------------------------------------------------------ research helpers
def bh_qvalues(cells, key='ae_top3'):
    """Benjamini-Hochberg q-values for 'A/E != 1' over cells (normal approx on top3 counts). Discovery only."""
    ps = []
    for i, c in enumerate(cells):
        e, a = c.get('expected_top3'), (c.get('n1', 0) + c.get('n2', 0) + c.get('n3', 0))
        if not e or not c.get('starts'):
            continue
        var = e * (1 - e / c['starts'])
        if var <= 0:
            continue
        z = (a - e) / math.sqrt(var)
        ps.append((math.erfc(abs(z) / math.sqrt(2)), i))
    ps.sort()
    m, q, prev = len(ps), {}, 1.0
    for rank in range(m, 0, -1):
        p, i = ps[rank - 1]
        prev = min(prev, p * m / rank)
        q[i] = round(prev, 4)
    return q


def time_split(races, cut):
    """(discovery, validation) by date: a lead found before `cut` must hold after it, never re-chosen on both."""
    a = {k: v for k, v in races.items() if v['date'] < cut}
    b = {k: v for k, v in races.items() if v['date'] >= cut}
    return a, b


def runner_cells(stats, venue, distance, going, field, frame, pop=None):
    """Cells that match one runner today (listed side by side, never multiplied). UNKNOWN stays UNKNOWN."""
    out = []
    want = {'T3_GATE': {'venue': venue, 'distance': distance, 'going': going_class(going), 'field_band': field_band(field), 'frame': frame},
            'T2_POP': {'venue': venue, 'band': dist_band(distance), 'pop': pop_band(pop)}}
    for t, cond in want.items():
        hit = [c for c in stats['tables'].get(t, []) if c['conditions'] == cond]
        out.append(hit[0] if hit else {'table': t, 'conditions': cond, 'status': 'UNKNOWN_NO_CELL'})
    return out


def md(stats, top=20):
    L = [f"# 地方 統計表（{stats['class']}）", '',
         f"出典 {stats['source']} ／ 期間 {stats['period']} ／ {stats['races']}R・{stats['starts']}出走。"
         f"{MIN_N}出走未満は参考値。{stats['leakage_note']}", '']
    t2 = stats['tables'].get('T2_POP', [])
    if t2:
        L += ['## 人気別 着順の内訳（場×距離帯）', '', '| 場 | 距離帯 | 人気 | 出走 | 1着 | 2着 | 3着 | 3着内率(95%) | 単回収 | 複回収 |',
              '|---|---|---|---|---|---|---|---|---|---|']
        for c in t2:
            k = c['conditions']
            ci = c['top3_ci95'] or ['-', '-']
            L.append(f"| {k['venue']} | {k['band']} | {k['pop']} | {c['starts']}{'※' if c['small_sample'] else ''} | {c['n1']} | {c['n2']} | {c['n3']} | "
                     f"{c['top3']:.1%} ({ci[0]:.0%}–{ci[1]:.0%}) | {c['roi_win']:.0%} | {c['roi_place']:.0%} |")
    for name, title in (('T3_GATE', '枠（A/E＝人気から見た期待3着内に対する実績）'), ('T5_DIST_CHANGE', '距離変更'),
                        ('T5_INTERVAL', '出走間隔'), ('T4_FRONT_FINISH', '4角位置→着順')):
        cs = [c for c in stats['tables'].get(name, []) if not c['small_sample'] and c.get('ae_top3')]
        if not cs:
            continue
        cs.sort(key=lambda c: -abs(math.log(c['ae_top3'])))
        L += ['', f'## {title}：A/E の偏りが大きい区分（{MIN_N}出走以上、上位{top}）', '',
              '| 条件 | 出走 | 3着内率 | A/E | 単回収 |', '|---|---|---|---|---|']
        for c in cs[:top]:
            L.append(f"| {' / '.join(f'{k}={v}' for k, v in c['conditions'].items())} | {c['starts']} | {c['top3']:.1%} | "
                     f"{c['ae_top3']:.2f} | {c['roi_win']:.0%} |")
    return '\n'.join(L) + '\n'


def dump(stats, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False)


def load_sources(root):
    """All historical races available under the autopilot output root: NAR CSV months (hist/nar/<YYYYMM>/*.csv,
    preferred when present) and the Rakuten backfill results (backfill/results/<date>/*.json)."""
    from pathlib import Path
    root = Path(root)
    races = {}
    for rec in sorted((root / 'backfill' / 'results').glob('*/*.json')):
        try:
            races.update(from_rakuten_backfill(json.loads(rec.read_text())))
        except (ValueError, KeyError, TypeError):
            continue
    src = ['RAKUTEN_RESULT_PAGE'] if races else []
    for m in sorted((root / 'hist' / 'nar').glob('*')):
        rl, hl, pb = (sorted(m.glob(f'*_{k}.csv')) for k in ('racelist', 'horselist', 'payback'))
        if rl and hl and pb:
            races.update(from_nar_csv(rl[0].read_bytes(), hl[0].read_bytes(), pb[0].read_bytes()))
            src.append('NAR_OFFICIAL_CSV:' + m.name)
    return races, '+'.join(src) or 'NONE'


def write(root):
    from pathlib import Path
    races, src = load_sources(root)
    if not races:
        return None
    st = build(races, src)
    dump(st, Path(root) / 'hist_stats.json')
    Path(root, 'hist_stats.md').write_text(md(st))
    return st
