"""LOCAL shadow measurement (evidence only, Owner adoption required for any use).

Replays fixed, formula-only ticket allocations on the FROZEN PAPER predictions (the settled revision) against
the official payouts already stored in <day>/<key>.result.json. Nothing here reselects horses, fits a
parameter or feeds back into ranking, tickets, KRS or capital. It answers:
  1. ticket-type allocation baseline (JRA audit: allocation matters more than index tweaks)
  2. payout-band recovery (◎ win-odds band) before any calibration
  3. NO-BET candidates: PAPER PFS split by pre-race flags that already exist (gate / race_type / fuan)
  4. market: favorite vs ◎ (予想ファースト・オッズセカンド; danger-favorite checks)
  5. body weight change of the winner/◎ (only where the revision persisted bw; from 2026-11-17 on)
Usage: python -m runtime.local_autopilot.shadow_measure <output_root> [<out_stem>]
"""
import json
import random
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

PROFILE = 'KM-LOCAL-SHADOW-MEASURE-v1.0-20261117'
UNIT = 100


def _key(nos, ordered=False):
    return '-'.join(map(str, nos if ordered else sorted(nos)))


def strategies(rank, fav):
    t = rank
    s = {
        'WIN_◎': [('WIN', [t[0]])],
        'PLACE_◎': [('PLACE', [t[0]])],
        'WIDE_◎-2,3': [('WIDE', [t[0], x]) for x in t[1:3]],
        'QUINELLA_◎-2,3,4': [('QUINELLA', [t[0], x]) for x in t[1:4]],
        'TRIO_BOX_top4': [('TRIO', list(c)) for c in combinations(t[:4], 3)],
        'TRIO_◎軸_2-5流し': [('TRIO', [t[0], a, b]) for a, b in combinations(t[1:5], 2)],
        'TRIFECTA_◎→2,3→2-5': [('TRIFECTA', [t[0], a, b]) for a in t[1:3] for b in t[1:5] if b != a],
    }
    if fav is not None:
        s['WIN_1番人気'] = [('WIN', [fav])]
        s['PLACE_1番人気'] = [('PLACE', [fav])]
    return s


def settle(tickets, payouts, non_starters):
    inv = pay = 0
    hit = False
    for bet, nos in tickets:
        if any(n in non_starters for n in nos):
            continue  # refunded
        inv += UNIT
        p = (payouts.get(bet) or {}).get(_key(nos, bet in ('TRIFECTA', 'EXACTA')))
        if p:
            pay += p
            hit = True
    return inv, pay, hit


def load(root):
    rows = []
    for rp in sorted(Path(root).glob('20*/*.result.json')):
        if rp.name.endswith('.prev.json') or '.result.' not in rp.name[-12:]:
            pass
        try:
            res = json.loads(rp.read_text())
        except ValueError:
            continue
        if not res.get('payouts') or not res.get('order'):
            continue
        day = rp.parent
        key = rp.name.split('.')[0]
        revp = day / 'rev' / f"{res.get('revision')}.json"
        pred = json.loads(revp.read_text()) if revp.exists() else json.loads((day / f'{key}.json').read_text())
        rows.append({'day': day.name, 'key': key, 'res': res, 'pred': pred.get('prediction') or {}})
    return rows


def boot_ci(pairs, n=500, seed=1):
    if not pairs:
        return None
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        smp = [pairs[rnd.randrange(len(pairs))] for _ in pairs]
        i = sum(a for a, _ in smp)
        out.append(100 * sum(b for _, b in smp) / i if i else 0)
    out.sort()
    return [round(out[int(0.025 * n)], 1), round(out[int(0.975 * n)], 1)]


def band(o):
    if o is None:
        return 'unknown'
    return '<2.0' if o < 2 else '2.0-4.9' if o < 5 else '5.0-9.9' if o < 10 else '10.0+'


def measure(root):
    rows = load(root)
    strat = defaultdict(list)
    hits = defaultdict(int)
    bands = defaultdict(lambda: defaultdict(list))
    flags = defaultdict(lambda: defaultdict(list))
    market = defaultdict(int)
    bw = defaultdict(list)
    for x in rows:
        res, pred = x['res'], x['pred']
        ranking = pred.get('ranking') or []
        ns = set(res.get('non_starters') or []) | set(res.get('non_starters_inferred') or [])
        rank = [r['no'] for r in ranking if r['no'] not in ns]
        if len(rank) < 5:
            continue
        odds = {r['no']: r.get('win') for r in ranking if r['no'] not in ns and r.get('win')}
        fav = min(odds, key=odds.get) if odds else None
        w = res['order'][0]
        actual = (res.get('effective_invest') or 0, res.get('payout') or 0)
        strat['PAPER_実買い目'].append(actual)
        hits['PAPER_実買い目'] += 1 if actual[1] > 0 else 0
        for name, tks in strategies(rank, fav).items():
            inv, pay, hit = settle(tks, res['payouts'], ns)
            strat[name].append((inv, pay))
            hits[name] += hit
            if name in ('WIN_◎', 'PLACE_◎', 'TRIO_◎軸_2-5流し'):
                bands[name][band(odds.get(rank[0]))].append((inv, pay))
        bands['PAPER_実買い目'][band(odds.get(rank[0]))].append(actual)
        for fk, fv in (('gate', pred.get('gate')), ('race_type', pred.get('race_type')),
                       ('fuan>0', (pred.get('fuan') or 0) > 0), ('aki.type', (pred.get('aki') or {}).get('type')),
                       ('venue', x['key'].split('_')[0])):
            flags[fk][str(fv)].append(actual)
        market['races'] += 1
        market['fav_won'] += w == fav
        market['honmei_won'] += w == rank[0]
        market['honmei_is_fav'] += rank[0] == fav
        if rank[0] != fav:
            market['diverge'] += 1
            market['diverge_fav_won'] += w == fav
            market['diverge_honmei_won'] += w == rank[0]
            market['diverge_fav_out_of_top3'] += fav not in res['order'][:3]
        for r in ranking:
            if r.get('bw_change') is not None:
                bw['winner' if r['no'] == w else 'others'].append(abs(r['bw_change']))

    def summ(pairs, h=None):
        i = sum(a for a, _ in pairs)
        p = sum(b for _, b in pairs)
        d = {'races': len(pairs), 'invest': i, 'payout': p, 'pfs': round(100 * p / i, 1) if i else None,
             'pfs_95ci_bootstrap': boot_ci(pairs)}
        if h is not None:
            d['hit_rate'] = round(100 * h / len(pairs), 1) if pairs else None
        return d

    out = {'profile': PROFILE, 'scope': 'SHADOW / PAPER frozen predictions / formula-only allocations / evidence only',
           'adoption_rule': 'No automatic adoption. Any change to tickets, capital or NO-BET needs Owner approval '
                            'after forward OOS (>= 100 races) confirms it.',
           'races': len(strat['PAPER_実買い目']),
           'days': sorted({x['day'] for x in rows}),
           'allocation': {k: summ(v, hits[k]) for k, v in strat.items()},
           'payout_band_by_honmei_win_odds': {k: {b: summ(v) for b, v in sorted(d.items())} for k, d in bands.items()},
           'paper_pfs_by_prerace_flag': {k: {f: summ(v) for f, v in sorted(d.items())} for k, d in flags.items()},
           'market': {**dict(market),
                      'fav_win_rate': round(100 * market['fav_won'] / market['races'], 1) if market['races'] else None,
                      'honmei_win_rate': round(100 * market['honmei_won'] / market['races'], 1) if market['races'] else None},
           'body_weight': {k: {'n': len(v), 'mean_abs_change_kg': round(sum(v) / len(v), 2) if v else None}
                           for k, v in bw.items()} or 'NOT_PERSISTED_BEFORE_2026-11-17'}
    return out


def md(o):
    L = [f"# 地方版 影計測（{o['days'][0]}〜{o['days'][-1]}、{o['races']}R、PAPER凍結予想・実購入なし）", '',
         f"<sub>{o['adoption_rule']}</sub>", '', '## 券種配分（固定式・100円/点）', '',
         '| 方式 | Race | 投資 | 払戻 | 回収率 | 95%CI | 的中率 |', '|---|---|---|---|---|---|---|']
    for k, v in sorted(o['allocation'].items(), key=lambda kv: -(kv[1]['pfs'] or 0)):
        L.append(f"| {k} | {v['races']} | {v['invest']:,} | {v['payout']:,} | {v['pfs']}% | {v['pfs_95ci_bootstrap']} | {v.get('hit_rate')}% |")
    L += ['', '## ◎の単勝オッズ帯別 回収率', '', '| 方式 | 帯 | Race | 回収率 | 95%CI |', '|---|---|---|---|---|']
    for k, d in o['payout_band_by_honmei_win_odds'].items():
        for b, v in d.items():
            L.append(f"| {k} | {b} | {v['races']} | {v['pfs']}% | {v['pfs_95ci_bootstrap']} |")
    L += ['', '## 見送り候補（既存の事前フラグ別 PAPER回収率）', '', '| フラグ | 値 | Race | 回収率 | 95%CI |', '|---|---|---|---|---|']
    for k, d in o['paper_pfs_by_prerace_flag'].items():
        for f, v in d.items():
            L.append(f"| {k} | {f} | {v['races']} | {v['pfs']}% | {v['pfs_95ci_bootstrap']} |")
    m = o['market']
    L += ['', '## 市場（1番人気 vs ◎）', '',
          f"- 1番人気の勝率 {m.get('fav_win_rate')}%／◎の勝率 {m.get('honmei_win_rate')}%／◎=1番人気 {m.get('honmei_is_fav')}R",
          f"- ◎≠1番人気 {m.get('diverge')}R：1番人気が勝利 {m.get('diverge_fav_won')}R、◎が勝利 {m.get('diverge_honmei_won')}R、"
          f"1番人気が3着外 {m.get('diverge_fav_out_of_top3')}R",
          '', f"## 馬体重：{o['body_weight']}", '']
    return '\n'.join(L)


if __name__ == '__main__':
    root = Path(sys.argv[1])
    stem = Path(sys.argv[2]) if len(sys.argv) > 2 else root / 'shadow_measure'
    o = measure(root)
    stem.with_suffix('.json').write_text(json.dumps(o, ensure_ascii=False, indent=1) + '\n')
    stem.with_suffix('.md').write_text(md(o))
    print(md(o))
