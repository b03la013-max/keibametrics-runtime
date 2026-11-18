"""Shadow tests of the formal role conversion (P1, 2026-11-19; prereg R6 C16/C17). Evidence only.

C16 W-CONSENSUS: add to the signed W set every horse ranked #1 by at least CONSENSUS of the win-oriented
    Full29 indices (F3S-L, SRI-L, T3I-L, TPI-L, ZAI-WIN). Measures winner capture W vs W+ and the extra heads.
C17 P2-BY-PLACE-INDEX: second-place candidates = the PLACE_K best by ZAI-PLACE instead of the signed P2 set
    (overall ranking top 6). Measured where the winner was in W: does the 2nd finisher sit in P2 vs P2'.
    (In-sample 11/16-18, 75-77R: C16 consensus rescued 2/35 W misses, C17 no gain -> kept as controls.)
C18 W+FAVORITE / C19 W+TOP2-POP: W ∪ market favourite / W ∪ the two shortest-odds horses (odds from the latest
    pre-start PAPER revision). C20 P2+TOP3-POP: P2 ∪ the three shortest-odds horses.
    Same-budget check: 馬単 with the same point count as the signed 馬単 set (heads = W order then added heads,
    seconds = P2 order then added; points split evenly over heads), settled on the official payout.
The formal Full29 has no market input; in-sample 18 of 35 W-missed winners were in the top 3 of the market.
Both read only the signed pre-race files (formal summary + full29 of the effective revision) and the result.
"""
import json
from pathlib import Path

PROFILE = 'KM-LOCAL-ROLE-SHADOW-v1.0-20261119'
WIN_INDICES = ('F3S-L', 'SRI-L', 'T3I-L', 'TPI-L', 'ZAI-WIN')
CONSENSUS = 2
PLACE_K = 6


def _eff(day_dir, key):
    d = Path(day_dir) / 'formal'
    return d / 'rev2' if (d / 'rev2' / f'{key}.result.json').exists() else d


def race(day_dir, key):
    d = _eff(day_dir, key)
    try:
        sm = json.loads((d / f'{key}.summary.json').read_text())
        res = json.loads((d / f'{key}.result.json').read_text())
        f29 = json.loads((d / f'{key}.full29.json').read_text())
    except (OSError, ValueError):
        return None
    if sm.get('no_bet') or len(res.get('order') or []) < 2:
        return None
    gone = set(res.get('non_starters') or []) | set(res.get('non_starters_inferred') or [])
    idx = {int(r['no']): r['indices'] for r in f29.get('runners') or [] if int(r['no']) not in gone}
    if not idx:
        return None
    roles = {int(h): v for h, v in (sm.get('roles') or {}).items()}
    W = {h for h, v in roles.items() if 'W' in v}
    P2 = {h for h, v in roles.items() if 'P2' in v}
    tops = {}
    for name in WIN_INDICES:
        vals = {h: v.get(name) for h, v in idx.items() if isinstance(v.get(name), (int, float))}
        if vals:
            best = max(vals.values())
            for h in [h for h, x in vals.items() if x == best]:
                tops[h] = tops.get(h, 0) + 1
    cons = {h for h, n in tops.items() if n >= CONSENSUS}
    place = sorted(idx, key=lambda h: -(idx[h].get('ZAI-PLACE') or 0))[:PLACE_K]
    w, s = int(res['order'][0]), int(res['order'][1])
    return {'race': key, 'winner': w, 'second': s, 'W': sorted(W), 'consensus': sorted(cons),
            'W_plus': sorted(W | cons), 'added_heads': len(cons - W),
            'win_in_W': w in W, 'win_in_W_plus': w in (W | cons),
            'P2': sorted(P2), 'P2_place': place, 'second_in_P2': s in P2, 'second_in_P2_place': s in place,
            'effective_revision': 'REVISION_2' if d.name == 'rev2' else 'REVISION_1'}


def _pops(day_dir, key):
    """Market order (shortest win odds first) from the latest pre-start PAPER revision of the race."""
    try:
        q = json.loads((Path(day_dir) / 'queue.json').read_text())
        ed = [e for e in q['races'][key]['editions'] if e.get('rev')]
        pred = json.loads((Path(day_dir) / 'rev' / f"{ed[-1]['rev']}.json").read_text())['prediction']
    except (OSError, ValueError, KeyError, IndexError):
        return []
    odds = {x['no']: x['win'] for x in pred.get('ranking') or [] if x.get('win')}
    return sorted(odds, key=odds.get)


def exacta_same_budget(heads, seconds, n_points):
    per = [n_points // len(heads) + (1 if i < n_points % len(heads) else 0) for i in range(len(heads))]
    out = []
    for h, k in zip(heads, per):
        out += [(h, s) for s in [x for x in seconds if x != h][:k]]
    return out


def tickets_market(day_dir, key, r, sm, res):
    pops = _pops(day_dir, key)
    if not pops:
        return None
    rank = [int(x) for x in sm.get('ranking') or []]
    order_w = [h for h in rank if h in r['W']]
    order_p2 = [h for h in rank if h in r['P2']]
    ex = [tuple(int(x) for x in t['selection']) for t in sm.get('tickets') or [] if t.get('bet_type') == 'EXACTA']
    pay = (res.get('payouts') or {}).get('EXACTA') or {}
    paid = lambda pairs: sum(v for k, v in pay.items() if tuple(int(x) for x in str(k).replace('(', '').replace(')', '')
                                                             .replace(' ', '').replace('-', ',').split(',') if x) in pairs)
    out = {'pops': pops[:3], 'exacta_points': len(ex), 'exacta_signed_payout': paid(set(ex))}
    for name, add_w, add_p in (('C18', pops[:1], []), ('C19', pops[:2], []), ('C20', [], pops[:3])):
        heads = order_w + [h for h in add_w if h not in order_w]
        secs = order_p2 + [h for h in add_p if h not in order_p2]
        cand = exacta_same_budget(heads, secs, len(ex)) if ex else []
        out[name] = {'W': heads, 'P2': secs, 'win_in_W': r['winner'] in heads, 'second_in_P2': r['second'] in secs,
                     'added_heads': len(heads) - len(order_w), 'added_seconds': len(secs) - len(order_p2),
                     'exacta_payout': paid(set(cand)), 'exacta_points': len(cand)}
    return out


def evaluate(root, since_day=None):
    rows = []
    for q in sorted(Path(root).glob('20*/queue.json')):
        day = q.parent
        if since_day and day.name < since_day:
            continue
        try:
            keys = sorted(json.loads(q.read_text())['races'])
        except (OSError, ValueError, KeyError):
            continue
        for k in keys:
            r = race(day, k)
            if r:
                r['day'] = day.name
                d = _eff(day, k)
                try:
                    r['market'] = tickets_market(day, k, r, json.loads((d / f'{k}.summary.json').read_text()),
                                                 json.loads((d / f'{k}.result.json').read_text()))
                except (OSError, ValueError):
                    r['market'] = None
                rows.append(r)
    out = summarize(rows)
    out['rows'] = rows
    return out


def summarize(rows):
    n = len(rows)
    pc = lambda f, rs: round(100 * sum(1 for r in rs if f(r)) / len(rs), 1) if rs else None
    whit = [r for r in rows if r['win_in_W']]
    return {'profile': PROFILE, 'races': n,
            'C16': {'win_in_W': pc(lambda r: r['win_in_W'], rows), 'win_in_W_plus': pc(lambda r: r['win_in_W_plus'], rows),
                    'rescued': sum(1 for r in rows if r['win_in_W_plus'] and not r['win_in_W']),
                    'avg_added_heads': round(sum(r['added_heads'] for r in rows) / n, 2) if n else None,
                    'races_with_added_head': sum(1 for r in rows if r['added_heads'])},
            'C17': {'races_with_winner_in_W': len(whit), 'second_in_P2': pc(lambda r: r['second_in_P2'], whit),
                    'second_in_P2_place': pc(lambda r: r['second_in_P2_place'], whit)},
            **{c: _market_summary(rows, c) for c in ('C18', 'C19', 'C20')},
            'production_change': 'NONE (evidence only)'}


def _market_summary(rows, c):
    m = [r for r in rows if r.get('market')]
    if not m:
        return {'races': 0}
    pts = sum(r['market']['exacta_points'] for r in m)
    pc = lambda f, rs: round(100 * sum(1 for r in rs if f(r)) / len(rs), 1) if rs else None
    whit = [r for r in m if r['win_in_W']]
    return {'races': len(m), 'win_in_W': pc(lambda r: r['win_in_W'], m), 'win_in_W_cand': pc(lambda r: r['market'][c]['win_in_W'], m),
            'second_in_P2_given_W': pc(lambda r: r['second_in_P2'], whit),
            'second_in_P2_cand_given_W': pc(lambda r: r['market'][c]['second_in_P2'], whit),
            'avg_added': round(sum(r['market'][c]['added_heads'] + r['market'][c]['added_seconds'] for r in m) / len(m), 2),
            'exacta_points': pts,
            'exacta_pfs_signed': round(100 * sum(r['market']['exacta_signed_payout'] for r in m) / (100 * pts), 1) if pts else None,
            'exacta_pfs_cand': round(100 * sum(r['market'][c]['exacta_payout'] for r in m) / (100 * pts), 1) if pts else None,
            'exacta_hits_signed': sum(1 for r in m if r['market']['exacta_signed_payout']),
            'exacta_hits_cand': sum(1 for r in m if r['market'][c]['exacta_payout'])}
