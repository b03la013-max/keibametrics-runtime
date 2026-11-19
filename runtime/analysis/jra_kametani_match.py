"""JRA 亀谷 bloodline match + known-result measurement (D6 port, NON-PRODUCTION).

Reads research/kametani/sire_rules_jra_v1.json and evaluates each runner from the signed request
(official race card, official horse history, official pre-cutoff market observation). The LOCAL v2
matcher handles the shared keys; the JRA keys (venue / straight / slope / root / cls / born_le) are
evaluated here. A scene is MATCH only when every condition is known and true.

Measurement: for settled races, compare top-3 rate of BUY / CAUTION / NONE runners against the
rate expected from their official popularity rank (market-neutral lift). Known-result replay only:
never forward OOS, production_effect NONE.

Usage: python runtime/analysis/jra_kametani_match.py --dates 20261114 20261115 [--out x.json]
"""
import argparse, collections, glob, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'runtime/local_autopilot')]
import bloodline_kametani as bk  # noqa: E402  (shared v2 semantics: check, sire_type)

RULES = ROOT / 'research/kametani/sire_rules_jra_v1.json'
JRA_KEYS = ('venue', 'straight', 'slope', 'flat_or_long', 'root', 'cls', 'born_le')
_C = {}


def rules():
    if 'r' not in _C:
        d = json.loads(RULES.read_text())
        _C.update(r={bk._n(e['name']): e for e in d['entries'] if e['kind'] in ('SIRE', 'DAMSIRE')},
                  course=d['course'], profile=d['profile'])
    return _C['r']


def race_class(name):
    n = name or ''
    if '新馬' in n:
        return 'newcomer'
    if '未勝利' in n:
        return 'maiden'
    if '1勝クラス' in n:
        return '1win'
    if any(k in n for k in ('2勝クラス', '3勝クラス', 'オープン', 'リステッド', 'G')):
        return '2win+'
    return None


def _jra(alt, ctx):
    v = {}
    sv = 'T' if ctx['surface'] == 'TURF' else 'D'
    straight, slope = (_C['course'].get(ctx['venue']) or {}).get(sv, (None, None))
    if 'venue' in alt:
        v['venue'] = ctx['venue'] in alt['venue']
    if 'straight' in alt:
        v['straight'] = None if straight is None else straight == alt['straight']
    if 'slope' in alt:
        v['slope'] = None if slope is None else slope == alt['slope']
    if 'flat_or_long' in alt:
        v['flat_or_long'] = True if (straight == 'long' or slope == 0) else (
            None if straight is None or slope is None else False)
    if 'root' in alt:
        v['root'] = (ctx['distance'] % 400 == 0) == bool(alt['root'])
    if 'cls' in alt:
        c = ctx['cls']
        v['cls'] = None if c is None else {'maiden': c == 'maiden', 'maiden_1win': c in ('maiden', '1win'),
                                            'low': c in ('newcomer', 'maiden', '1win'), '2win+': c == '2win+'}[alt['cls']]
    if 'born_le' in alt:
        v['born_le'] = None if ctx['age'] is None else (ctx['year'] - ctx['age']) <= alt['born_le']
    return v


def check(alt, ctx):
    v = _jra(alt, ctx)
    base = {k: x for k, x in alt.items() if k not in JRA_KEYS}
    _, bv = bk.check(base, ctx) if base else ('MATCH', {})
    v.update(bv)
    if any(x is False for x in v.values()):
        return 'NO', v
    return ('UNKNOWN' if any(x is None for x in v.values()) else 'MATCH'), v


def contexts(req):
    ss = req['source_snapshot']
    race = req['race']
    card = {str(r['runner_id']): r for r in ss['jra_official_race_card_detail']['runners']}
    hist = ss['jra_official_horse_history']['runners']
    hist = hist if isinstance(hist, dict) else {str(h['runner_id']): h for h in hist}
    going = next((o.get('going') for o in ss.get('aki_external_observations') or [] if o.get('going')), None)
    out = {}
    for rid, c in card.items():
        if c.get('status', 'ACTIVE') != 'ACTIVE':
            continue
        runs = (hist.get(rid) or {}).get('runs') or []
        starts = [{'finish': r.get('finish'), 'ride_body_weight': r.get('body_weight'), 'distance': r.get('distance_m'),
                   'surface': {'芝': 'TURF', 'ダ': 'DIRT'}.get(r.get('surface'))} for r in runs]
        out[rid] = {'surface': {'芝': 'TURF', 'ダ': 'DIRT'}.get(race['surface'], ''), 'distance': int(race['distance']),
                    'venue': race['venue'], 'going': going, 'sex': (c.get('sex') or '')[:1] or None, 'age': c.get('age'),
                    'year': int(req['race_date'][:4]), 'cls': race_class(race.get('race_name')),
                    'damsire_type': bk.sire_type(c.get('damsire')), 'starts': starts, 'newcomer': not runs,
                    'front': None, 'pop': c.get('popularity_rank'), 'frame': c.get('frame_no'),
                    'sire': c.get('sire'), 'current_bw': c.get('current_body_weight')}
    return out


def evaluate(ctx):
    e = rules().get(bk._n(ctx['sire']))
    if not e:
        return None
    res = {}
    for side in ('buy', 'caution'):
        res[side] = [check(a, ctx)[0] for a in e.get(side) or []]
    return {'entry_no': e['no'], 'buy_match': 'MATCH' in res['buy'], 'caution_match': 'MATCH' in res['caution'],
            'buy_unknown_only': 'MATCH' not in res['buy'] and 'UNKNOWN' in res['buy']}


def state(ev):
    if ev is None:
        return 'UNCOVERED'
    if ev['buy_match'] and ev['caution_match']:
        return 'BOTH'
    return 'BUY' if ev['buy_match'] else 'CAUTION' if ev['caution_match'] else 'NONE'


def measure(dates, root=ROOT):
    rows = []
    for d in dates:
        for p in sorted(glob.glob(str(root / f'runtime/requests/KM-JRA-*-{d}-R*-LIVE-R1-FORMAL.json'))):
            req = json.loads(Path(p).read_text())
            rp = root / 'runtime/results' / f"{req['race_id']}.json"
            if not rp.exists():
                continue
            fo = [str(x) for x in json.loads(rp.read_text())['official_result']['finish_order']]
            for rid, ctx in contexts(req).items():
                if not isinstance(ctx['pop'], int):
                    continue
                rows.append({'race_id': req['race_id'], 'runner_id': rid, 'surface': ctx['surface'],
                             'pop': ctx['pop'], 'state': state(evaluate(ctx)),
                             'win': fo[:1] == [rid], 'top3': rid in fo[:3]})
    base = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        b = base[min(r['pop'], 10)]
        b[0] += 1; b[1] += r['top3']
    exp = {k: v[1] / v[0] for k, v in base.items()}
    summ = {}
    for key in ('BUY', 'CAUTION', 'BOTH', 'NONE', 'UNCOVERED'):
        for surf in ('ALL', 'TURF', 'DIRT'):
            rs = [r for r in rows if r['state'] == key and (surf == 'ALL' or r['surface'] == surf)]
            if not rs:
                continue
            e = sum(exp[min(r['pop'], 10)] for r in rs)
            t3 = sum(r['top3'] for r in rs)
            summ[f'{key}/{surf}'] = {'runners': len(rs), 'wins': sum(r['win'] for r in rs), 'top3': t3,
                                     'expected_top3_by_popularity': round(e, 1),
                                     'lift': round(t3 / e, 3) if e else None,
                                     'mean_popularity': round(sum(r['pop'] for r in rs) / len(rs), 2)}
    return {'profile': 'KM-JRA-KAMETANI-MEASURE-v1', 'rules_profile': _C.get('profile'),
            'classification': 'KNOWN_RESULT_REPLAY / NOT_FORWARD_OOS / NON_PRODUCTION', 'production_effect': 'NONE',
            'races': len({r['race_id'] for r in rows}), 'summary': summ}, rows


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--dates', nargs='+', required=True); ap.add_argument('--out')
    a = ap.parse_args()
    rep, rows = measure([d.replace('-', '') for d in a.dates])
    if a.out:
        Path(a.out).write_text(json.dumps({**rep, 'runners': rows}, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps(rep, ensure_ascii=False, indent=1))
