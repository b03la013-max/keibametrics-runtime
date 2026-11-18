"""LOCAL sire / damsire performance from our own daily collection (research BVI-L-R2, evidence only).

Why: the formal BVIg-L stays RULED-NEUTRAL (the NAR top-50 leading tables lack starts / 3rd places / going /
venue). Every Rakuten card we fetch already carries each runner's sire, damsire and last five starts (venue,
distance, surface, going, finish, field size, popularity). Pooling those past starts over all collected days gives
sire x venue x distance x going records with 1st-3rd counts.

Strength is measured against the market, not raw rates: a sire whose runners are usually favourites would
otherwise look strong. For every past start the expected top-3 probability is the pooled top-3 rate of its
popularity (and field-size band); A/E = actual top-3 / expected top-3, shrunk toward 1 with M pseudo-starts.
Score = 52 + 20*log2(A/E) clipped to [30, 75]. The most specific cell with >= MIN_N starts is used
(sire x venue x distance band x going -> sire x venue -> sire x surface x distance band -> sire x going -> sire),
damsire likewise; BVI-L-R2 = (40*sire + 25*damsire + 35*52)/100 (formal BVIg-L sire/damsire weights, rest neutral).
Only days strictly before the race date feed a prediction (no same-day information). No formal consumer.
"""
import json
import math
from collections import defaultdict
from pathlib import Path

PROFILE = 'KM-LOCAL-SIRE-STATS-BVI-L-R2-v1.0-20261119'
MIN_N, M = 30, 20.0


def dist_band(d):
    d = int(d or 0)
    return 'S' if d <= 1300 else 'M' if d <= 1700 else 'L'


def going_class(g):
    g = str(g or '')
    return 'WET' if ('不' in g or '重' in g) else 'DAMP' if '稍' in g else 'DRY' if '良' in g else 'UNKNOWN'


def _bvi_rows(o):
    if isinstance(o, dict):
        if 'bloodline_bvi_research' in o:
            return o['bloodline_bvi_research']
        for v in o.values():
            r = _bvi_rows(v)
            if r:
                return r
    return None


def collect(root, before_day):
    """Unique past starts (horse, date, venue, distance) of runners on cards of days < before_day."""
    recs = {}
    for qp in sorted(Path(root).glob('20*/queue.json')):
        d = qp.parent
        if d.name >= before_day:
            continue
        try:
            races = json.loads(qp.read_text())['races']
        except (OSError, ValueError, KeyError):
            continue
        for key, r in races.items():
            sires = {}
            for p in (d / 'formal' / 'rev2' / f'{key}.full29.json', d / 'formal' / f'{key}.full29.json'):
                try:
                    for x in _bvi_rows(json.loads(p.read_text())) or []:
                        sires[int(x['runner_id'])] = (x.get('sire'), x.get('damsire'))
                    break
                except (OSError, ValueError, KeyError, TypeError):
                    continue
            ed = [e for e in r.get('editions') or [] if e.get('rev')]
            if not ed:
                continue
            try:
                pred = json.loads((d / 'rev' / f"{ed[-1]['rev']}.json").read_text())
            except (OSError, ValueError):
                continue
            names = {x['no']: x['name'] for x in pred.get('runners') or []}
            for no, starts in ((pred.get('prediction') or {}).get('prior_runs') or {}).items():
                s = sires.get(int(no))
                if not s or not s[0]:
                    continue
                for st in starts or []:
                    if not st.get('finish') or not st.get('field_size') or not st.get('ride_popularity'):
                        continue
                    if str(st.get('venue', '')).startswith('J'):      # JRA starts are a different population
                        continue
                    recs[(names.get(int(no)), st.get('date'), st.get('venue'), st.get('distance'))] = {
                        'sire': s[0], 'damsire': s[1], 'venue': st.get('venue'), 'surface': st.get('surface'),
                        'band': dist_band(st.get('distance')), 'going': going_class(st.get('going')),
                        'top3': st['finish'] <= 3, 'pop': int(st['ride_popularity']), 'field': int(st['field_size'])}
    return list(recs.values())


def build(root, before_day):
    rows = collect(root, before_day)
    base = defaultdict(lambda: [0, 0])
    for r in rows:
        k = (min(r['pop'], 10), 'small' if r['field'] <= 9 else 'big')
        base[k][0] += 1
        base[k][1] += r['top3']
    exp = {k: v[1] / v[0] for k, v in base.items() if v[0]}
    cells = defaultdict(lambda: [0, 0.0, 0])        # n, expected, actual
    for r in rows:
        e = exp.get((min(r['pop'], 10), 'small' if r['field'] <= 9 else 'big'), 0.3)
        for who in ('sire', 'damsire'):
            name = r[who]
            if not name:
                continue
            for lvl, key in (('V_B_G', (r['venue'], r['band'], r['going'])), ('V', (r['venue'],)),
                             ('S_B', (r['surface'], r['band'])), ('G', (r['going'],)), ('ALL', ())):
                c = cells['|'.join((who, name, lvl) + key)]
                c[0] += 1
                c[1] += e
                c[2] += r['top3']
    return {'profile': PROFILE, 'before_day': before_day, 'records': len(rows),
            'sires': len({r['sire'] for r in rows}), 'min_n': MIN_N, 'shrink_m': M,
            'cells': {k: v for k, v in cells.items() if v[0] >= 5}}


def _score(c):
    n, e, a = c
    ae = (a + M * (e / n if n else 0.3)) / (e + M * (e / n if n else 0.3)) if e else 1.0
    return max(30.0, min(75.0, 52 + 20 * math.log2(max(ae, 1e-6))))


def lookup(stats, who, name, venue, surface, distance, going):
    if not name:
        return None
    b, g = dist_band(distance), going_class(going)
    for lvl, key in (('V_B_G', (venue, b, g)), ('V', (venue,)), ('S_B', (surface, b)), ('G', (g,)), ('ALL', ())):
        c = stats['cells'].get('|'.join((who, name, lvl) + key))
        if c and c[0] >= MIN_N:
            return {'level': lvl, 'n': c[0], 'actual_top3': c[2], 'expected_top3': round(c[1], 2),
                    'score': round(_score(c), 2)}
    return None


def race_evidence(race, runners, stats):
    if not stats:
        return {'profile': PROFILE, 'status': 'NO_STATS'}
    out = {}
    for x in runners:
        s = lookup(stats, 'sire', x.get('sire'), race.get('venue_name'), race.get('surface'), race.get('distance'), race.get('going'))
        d = lookup(stats, 'damsire', x.get('damsire'), race.get('venue_name'), race.get('surface'), race.get('distance'), race.get('going'))
        val = (40 * (s['score'] if s else 52) + 25 * (d['score'] if d else 52) + 35 * 52) / 100
        out[str(x['horse_no'])] = {'sire': s, 'damsire': d, 'bvi_l_r2': round(val, 2),
                                   'observed_weight': (40 if s else 0) + (25 if d else 0)}
    return {'profile': PROFILE, 'status': 'OK', 'stats_before_day': stats['before_day'], 'records': stats['records'],
            'covered': sum(1 for v in out.values() if v['observed_weight']), 'runners': len(out),
            'production_effect': 'NONE (formal BVIg-L stays RULED-NEUTRAL; Owner approval needed to connect)',
            'by_horse': out}


def write(root, before_day):
    st = build(root, before_day)
    Path(root, 'sire_stats.json').write_text(json.dumps(st, ensure_ascii=False) + '\n')
    return st


def load(root, race_day):
    try:
        st = json.loads(Path(root, 'sire_stats.json').read_text())
    except (OSError, ValueError):
        return None
    return st if st.get('before_day', '9999') <= race_day else None
