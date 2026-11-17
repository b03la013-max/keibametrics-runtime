"""AKI (荒れ具合) audit: does the PAPER AKI-v2 score predict how rough the race actually ended, and does the
formation it picks (form a-b-c = 三連単 1着上位a / 2着上位b / 3着上位c) beat a fixed formation?
Compared with a plain market baseline (favourite win odds). Evidence only; no Production change.
"""
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from statistics import median

from runtime.local_autopilot import shadow_measure as sm

PROFILE = 'KM-LOCAL-AKI-AUDIT-v1.0-20261118'
FORMS = ('1-2-4', '1-2-5', '1-3-6', '1-3-7', '2-2-6', '2-3-7', '2-4-8')


def rows(root, days=None):
    out = []
    for x in sm.load(root):
        if days and x['day'] not in days:
            continue
        res, pred = x['res'], x['pred']
        aki = pred.get('aki') or {}
        ns = set(res.get('non_starters') or []) | set(res.get('non_starters_inferred') or [])
        rk = [r for r in pred.get('ranking') or [] if r['no'] not in ns]
        odds = {r['no']: r['win'] for r in rk if r.get('win')}
        if aki.get('total') is None or len(rk) < 5 or len(res['order']) < 3:
            continue
        pops = sorted(odds, key=odds.get)
        o = [int(v) for v in res['order'][:3]]
        tri = list((res['payouts'].get('TRIFECTA') or {}).values())
        trio = list((res['payouts'].get('TRIO') or {}).values())
        out.append({'day': x['day'], 'key': x['key'], 'total': aki['total'], 'W': aki.get('W'), 'P': aki.get('P'),
                    'RSI': aki.get('RSI'), 'type': aki.get('type'), 'form': aki.get('form'),
                    'rank': [r['no'] for r in rk], 'order': o, 'ns': ns, 'payouts': res['payouts'],
                    'fav_odds': odds[pops[0]] if pops else None,
                    'fav_out3': bool(pops) and pops[0] not in o, 'fav_won': bool(pops) and pops[0] == o[0],
                    'winner_pop': pops.index(o[0]) + 1 if o[0] in pops else None,
                    'tri': tri[0] if tri else None, 'trio': trio[0] if trio else None})
    return out


def auc(xs, ys):
    """P(score of a positive > score of a negative); ties 0.5."""
    pos = [x for x, y in zip(xs, ys) if y and x is not None]
    neg = [x for x, y in zip(xs, ys) if not y and x is not None]
    if not pos or not neg:
        return None
    s = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in pos for n in neg)
    return round(s / (len(pos) * len(neg)), 3)


def spearman(xs, ys):
    pr = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pr) < 5:
        return None
    rk = lambda v: {i: r for r, i in enumerate(sorted(range(len(v)), key=lambda k: v[k]))}
    a, b = rk([p[0] for p in pr]), rk([p[1] for p in pr])
    n = len(pr)
    d = sum((a[i] - b[i]) ** 2 for i in range(n))
    return round(1 - 6 * d / (n * (n * n - 1)), 3)


def form_tickets(rank, form):
    a, b, c = map(int, form.split('-'))
    return [('TRIFECTA', [i, j, k]) for i in rank[:a] for j in rank[:b] for k in rank[:c] if len({i, j, k}) == 3]


def group(rs):
    if not rs:
        return None
    tri = [r['tri'] for r in rs if r['tri']]
    return {'races': len(rs), 'fav_win_rate': round(100 * sum(r['fav_won'] for r in rs) / len(rs), 1),
            'fav_out_of_top3_rate': round(100 * sum(r['fav_out3'] for r in rs) / len(rs), 1),
            'winner_pop_mean': round(sum(r['winner_pop'] or 0 for r in rs) / len(rs), 2),
            'trifecta_median': median(tri) if tri else None,
            'trifecta_10k_rate': round(100 * sum(t >= 10000 for t in tri) / len(tri), 1) if tri else None,
            'trifecta_100k_rate': round(100 * sum(t >= 100000 for t in tri) / len(tri), 1) if tri else None}


def band(t):
    return '<35' if t < 35 else '35-49' if t < 50 else '50-64' if t < 65 else '65+'


def audit(root, days=None):
    rs = rows(root, days)
    out = {'profile': PROFILE, 'races': len(rs), 'days': sorted({r['day'] for r in rs}),
           'production_change': 'NONE (evidence only)'}
    if not rs:
        return out
    out['by_type'] = {t: group([r for r in rs if r['type'] == t]) for t in sorted({r['type'] for r in rs})}
    out['by_total_band'] = {b: group([r for r in rs if band(r['total']) == b]) for b in ('<35', '35-49', '50-64', '65+')}
    labels = {'fav_out_of_top3': [r['fav_out3'] for r in rs], 'fav_not_win': [not r['fav_won'] for r in rs],
              'trifecta>=10000': [(r['tri'] or 0) >= 10000 for r in rs]}
    scores = {'AKI_total': [r['total'] for r in rs], 'AKI_W': [r['W'] for r in rs], 'AKI_P': [r['P'] for r in rs],
              'AKI_RSI': [r['RSI'] for r in rs], 'MARKET_fav_odds': [r['fav_odds'] for r in rs]}
    out['auc'] = {s: {l: auc(v, y) for l, y in labels.items()} for s, v in scores.items()}
    lt = [math.log(r['tri']) if r['tri'] else None for r in rs]
    out['spearman_vs_log_trifecta'] = {s: spearman(v, lt) for s, v in scores.items()}
    fm = {}
    for f in FORMS + ('AKI_CHOSEN',):
        inv = pay = hit = 0
        for r in rs:
            i, p, h = sm.settle(form_tickets(r['rank'], r['form'] if f == 'AKI_CHOSEN' else f), r['payouts'], r['ns'])
            inv, pay, hit = inv + i, pay + p, hit + h
        fm[f] = {'points_per_race': round(inv / 100 / len(rs), 1), 'hit_rate': round(100 * hit / len(rs), 1),
                 'pfs': round(100 * pay / inv, 1) if inv else None}
    out['trifecta_formation'] = fm
    return out


def md(o):
    if not o.get('races'):
        return '# AKI 荒れ具合 検証\n\n- データなし\n'
    L = [f"# AKI 荒れ具合 検証（{o['days'][0]}〜{o['days'][-1]}、{o['races']}R、PAPER凍結予想）", '',
         '## AKI区分別の実際の荒れ方', '', '| 区分 | Race | 1番人気勝率 | 1番人気3着外 | 勝ち馬平均人気 | 3連単中央値 | 1万円以上 | 10万円以上 |',
         '|---|---|---|---|---|---|---|---|']
    for name, d in (('型', o['by_type']), ('合計点', o['by_total_band'])):
        for k, v in d.items():
            if v:
                L.append(f"| {name} {k} | {v['races']} | {v['fav_win_rate']}% | {v['fav_out_of_top3_rate']}% | "
                         f"{v['winner_pop_mean']} | {v['trifecta_median']:,}円 | {v['trifecta_10k_rate']}% | {v['trifecta_100k_rate']}% |")
    L += ['', '## 荒れの予測力（AUC：0.5=当てずっぽう、1.0=完全）', '', '| 指標 | 1番人気3着外 | 1番人気が負け | 3連単1万円以上 | 3連単配当との順位相関 |',
          '|---|---|---|---|---|']
    for s, d in o['auc'].items():
        L.append(f"| {s} | {d['fav_out_of_top3']} | {d['fav_not_win']} | {d['trifecta>=10000']} | {o['spearman_vs_log_trifecta'][s]} |")
    L += ['', '## 3連単フォーメーション（PAPER順位、100円/点）', '', '| 形 | 1R平均点数 | 的中率 | 回収率 |', '|---|---|---|---|']
    for f, v in o['trifecta_formation'].items():
        L.append(f"| {f} | {v['points_per_race']} | {v['hit_rate']}% | {v['pfs']}% |")
    L += ['', f"<sub>{o['production_change']}</sub>", '']
    return '\n'.join(L)


def write(root):
    o = audit(root)
    (Path(root) / 'aki_audit.json').write_text(json.dumps(o, ensure_ascii=False, indent=1) + '\n')
    (Path(root) / 'aki_audit.md').write_text(md(o))
    return o


if __name__ == '__main__':
    print(md(audit(sys.argv[1])))
