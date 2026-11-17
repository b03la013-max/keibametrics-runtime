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
import math
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
        o = [x for x in t if x != fav]   # PAPER order without the favorite: same partners, favorite as axis
        s['WIDE_1番人気-PAPER上位2'] = [('WIDE', [fav, x]) for x in o[:2]]
        s['QUINELLA_1番人気-PAPER上位3'] = [('QUINELLA', [fav, x]) for x in o[:3]]
        s['TRIO_1番人気軸_PAPER上位4流し'] = [('TRIO', [fav, a, b]) for a, b in combinations(o[:4], 2)]
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


def _role(res, no):
    """(won, top3, win payout, place payout) of one horse, 100-yen units."""
    if no is None:
        return None
    pay = res['payouts']
    return (no == res['order'][0], no in res['order'][:3],
            (pay.get('WIN') or {}).get(str(no)) or 0, (pay.get('PLACE') or {}).get(str(no)) or 0)


def _rolesum(xs):
    xs = [x for x in xs if x]
    if not xs:
        return None
    n = len(xs)
    return {'races': n, 'win_rate': round(100 * sum(x[0] for x in xs) / n, 1),
            'top3_rate': round(100 * sum(x[1] for x in xs) / n, 1),
            'win_pfs': round(sum(x[2] for x in xs) / n, 1), 'place_pfs': round(sum(x[3] for x in xs) / n, 1),
            'win_pfs_95ci': boot_ci([(100, x[2]) for x in xs]), 'place_pfs_95ci': boot_ci([(100, x[3]) for x in xs])}


GAP = 2.0        # 馬券購入法: adjacent popularity odds ratio >= 2.0 is an オッズの断層


def odds_gap(odds):
    """First 断層 among the top-6 favourites: k = number of horses above the gap (None = no gap)."""
    o = sorted(odds.values())[:6]
    for k in range(1, len(o)):
        if o[k] / o[k - 1] >= GAP:
            return k, round(o[1] / o[0], 2) if len(o) > 1 else None
    return None, round(o[1] / o[0], 2) if len(o) > 1 else None


def _probs(rank_rows, ns):
    """(market q, model p) normalised over starters with both values."""
    rows = [r for r in rank_rows if r['no'] not in ns and r.get('win') and r.get('p_win')]
    if len(rows) < 3:
        return None
    iq = {r['no']: 1 / r['win'] for r in rows}
    ip = {r['no']: max(float(r['p_win']), 1e-4) for r in rows}
    return ({k: v / sum(iq.values()) for k, v in iq.items()}, {k: v / sum(ip.values()) for k, v in ip.items()})


def _combine(q, p, a, b):
    z = {k: math.exp(b * math.log(q[k]) + a * math.log(p[k])) for k in q}
    t = sum(z.values())
    return {k: v / t for k, v in z.items()}


def _harville_ll(pr, order, lam2, lam3):
    """log-likelihood of the observed 2nd/3rd under discounted Harville (prob ∝ pr^λ among the rest)."""
    ll = 0.0
    for pos, lam in ((1, lam2), (2, lam3)):
        if len(order) <= pos or order[pos] not in pr:
            return None
        rest = {k: pr[k] ** lam for k in pr if k not in order[:pos]}
        ll += math.log(rest[order[pos]] / sum(rest.values()))
    return ll


def benter(rows_q):
    """Benter information test: does the PAPER model add to the market? Leave-one-day-out fit of
    log P = a*log p_model + b*log q_market (grid), scored by winner log-loss on the held-out day."""
    grid = [(a / 10, b / 10) for a in range(0, 16) for b in range(0, 16) if a or b]
    ll = lambda rows, a, b: -sum(math.log(_combine(q, p, a, b)[w]) for q, p, w, _ in rows) / len(rows)
    days = sorted({d for *_, d in rows_q})
    held, fits = [], {}
    for d in days:
        train = [x for x in rows_q if x[3] != d]
        test = [x for x in rows_q if x[3] == d]
        if len(train) < 20:
            continue
        a, b = min(grid, key=lambda g: ll(train, *g))
        fits[d] = [a, b]
        held += [(x, a, b) for x in test]
    n = len(held)
    if not n:
        return {'status': 'INSUFFICIENT', 'races': len(rows_q)}
    m = lambda f: round(-sum(math.log(f(x, a, b)) for x, a, b in held) / n, 4)
    return {'races': n, 'days': days, 'fits_by_heldout_day': fits,
            'logloss_market': m(lambda x, a, b: x[0][x[2]]), 'logloss_model': m(lambda x, a, b: x[1][x[2]]),
            'logloss_combined_oos': m(lambda x, a, b: _combine(x[0], x[1], a, b)[x[2]]),
            'reading': 'combined < market means the model carries information the odds do not (Benter); '
                       'no EV/Kelly use until calibration is approved'}


def measure(root, days=None):
    rows = [x for x in load(root) if days is None or x['day'] in days]
    hv = defaultdict(lambda: defaultdict(list))      # group -> role -> [(won, top3, win pay, place pay)]
    dz = defaultdict(lambda: defaultdict(list))      # danger-fav: group -> role -> [...]
    strat = defaultdict(list)
    hits = defaultdict(int)
    bands = defaultdict(lambda: defaultdict(list))
    flags = defaultdict(lambda: defaultdict(list))
    market = defaultdict(int)
    bw = defaultdict(list)
    kg = defaultdict(list)          # 亀谷 sire rules: group -> [role]
    gp = defaultdict(lambda: defaultdict(list))   # odds 断層: group -> role -> [...]
    bq, hv_ll = [], defaultdict(float)
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
        fo = odds.get(fav)
        for g in ('ALL', 'venue:' + x['key'].split('_')[0], 'fav_odds:' + band(fo), 'day:' + x['day'],
                  'honmei_is_fav' if rank[0] == fav else 'honmei_not_fav'):
            hv[g]['◎'].append(_role(res, rank[0]))
            hv[g]['1番人気'].append(_role(res, fav))
            if rank[0] != fav:
                hv[g]['◎≠人気時の◎'].append(_role(res, rank[0]))
        dfv = pred.get('danger_fav') or {}
        if dfv.get('status') == 'OK' and dfv.get('favorite_no') == fav:
            groups = ['rank:' + dfv['danger_rank']] + [f"{k}={v}" for k, v in sorted(dfv['flags'].items()) if v is not None]
            for g in groups:
                dz[g]['1番人気'].append(_role(res, fav))
                dz[g]['2番人気'].append(_role(res, dfv.get('second_no')))
                dz[g]['◎'].append(_role(res, rank[0]))
        for no, ev in ((pred.get('kametani') or {}).get('by_horse') or {}).items():
            if int(no) in ns:
                continue
            g = 'buy_match' if ev['buy_match'] and not ev['caution_match'] else 'caution_match' if ev['caution_match'] and not ev['buy_match'] \
                else 'both' if ev['buy_match'] else 'covered_no_match'
            kg[g].append(_role(res, int(no)))
            if ev['buy_match'] and int(no) not in rank[:3]:
                kg['buy_match_outside_paper_top3'].append(_role(res, int(no)))
        if odds:
            k, r12 = odds_gap(odds)
            pops = sorted(odds, key=odds.get)
            for g in ('gap_after:' + str(k), 'gap12>=2.5' if r12 and r12 >= 2.5 else 'gap12<2.5'):
                gp[g]['1番人気'].append(_role(res, fav))
                gp[g]['2番人気'].append(_role(res, pops[1] if len(pops) > 1 else None))
                gp[g]['◎'].append(_role(res, rank[0]))
                gp[g]['_winner_within_gap'].append((k is not None and w in pops[:k], False, 0, 0))
        pq = _probs(ranking, ns)
        if pq and w in pq[0]:
            bq.append((pq[0], pq[1], w, x['day']))
            for lab, l2, l3 in (('harville', 1.0, 1.0), ('benter_0.81_0.65', 0.81, 0.65)):
                for src, pr in (('market', pq[0]), ('model', pq[1])):
                    v = _harville_ll(pr, [int(o) for o in res['order']], l2, l3)
                    if v is not None:
                        hv_ll[f'{src}:{lab}'] += v
                        hv_ll[f'{src}:{lab}:n'] += 1
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
           'honmei_vs_favorite': {g: {role: _rolesum(v) for role, v in d.items()} for g, d in sorted(hv.items())},
           'danger_favorite': ({g: {role: _rolesum(v) for role, v in d.items()} for g, d in sorted(dz.items())}
                               or 'NOT_PERSISTED_BEFORE_2026-11-17'),
           'body_weight': {k: {'n': len(v), 'mean_abs_change_kg': round(sum(v) / len(v), 2) if v else None}
                           for k, v in bw.items()} or 'NOT_PERSISTED_BEFORE_2026-11-17',
           'kametani_sire_rules': {g: _rolesum(v) for g, v in sorted(kg.items())} or 'NOT_PERSISTED_BEFORE_2026-11-18',
           'odds_gap': {g: {role: _rolesum(v) for role, v in d.items()} for g, d in sorted(gp.items())},
           'benter_information_test': benter(bq),
           'place_order_model': {k.rsplit(':', 1)[0] if k.endswith(':n') else k:
                                 (round(-hv_ll[k] / hv_ll[k + ':n'], 4) if not k.endswith(':n') and hv_ll.get(k + ':n') else None)
                                 for k in hv_ll if not k.endswith(':n')}}
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
          '', '## ◎ vs 1番人気（勝率・3着内率・単勝/複勝回収率）', '',
          '| 区分 | 対象 | Race | 勝率 | 3着内率 | 単勝回収 | 単勝95%CI | 複勝回収 |', '|---|---|---|---|---|---|---|---|']
    for g, d in o['honmei_vs_favorite'].items():
        if g.startswith('day:') and len(o['days']) > 1:
            continue
        for role, v in d.items():
            if v:
                L.append(f"| {g} | {role} | {v['races']} | {v['win_rate']}% | {v['top3_rate']}% | {v['win_pfs']}% | "
                         f"{v['win_pfs_95ci']} | {v['place_pfs']}% |")
    L += ['', '## 危険な1番人気（フラグ別の1番人気・2番人気・◎の成績）', '']
    if isinstance(o['danger_favorite'], dict):
        L += ['| 条件 | 対象 | Race | 勝率 | 3着内率 | 単勝回収 | 複勝回収 |', '|---|---|---|---|---|---|---|']
        for g, d in o['danger_favorite'].items():
            for role, v in d.items():
                if v:
                    L.append(f"| {g} | {role} | {v['races']} | {v['win_rate']}% | {v['top3_rate']}% | {v['win_pfs']}% | {v['place_pfs']}% |")
    else:
        L.append(f"- {o['danger_favorite']}")
    L += ['', f"## 馬体重：{o['body_weight']}", '', '## 亀谷血統辞典 種牡馬ルール該当（著者主張・NAR未検証）', '']
    if isinstance(o.get('kametani_sire_rules'), dict):
        L += ['| 区分 | 頭数 | 勝率 | 3着内率 | 単勝回収 | 複勝回収 |', '|---|---|---|---|---|---|']
        for g, v in o['kametani_sire_rules'].items():
            if v:
                L.append(f"| {g} | {v['races']} | {v['win_rate']}% | {v['top3_rate']}% | {v['win_pfs']}% | {v['place_pfs']}% |")
    else:
        L.append(f"- {o.get('kametani_sire_rules')}")
    L += ['', '## オッズの断層（隣接人気の単勝オッズ比 ≥ 2.0）', '',
          '| 区分 | 対象 | Race | 勝率 | 3着内率 | 単勝回収 | 複勝回収 |', '|---|---|---|---|---|---|---|']
    for g, d in (o.get('odds_gap') or {}).items():
        for role, v in d.items():
            if v and role != '_winner_within_gap':
                L.append(f"| {g} | {role} | {v['races']} | {v['win_rate']}% | {v['top3_rate']}% | {v['win_pfs']}% | {v['place_pfs']}% |")
            elif v:
                L.append(f"| {g} | 勝ち馬が断層より上 | {v['races']} | {v['win_rate']}% | | | |")
    b = o.get('benter_information_test') or {}
    L += ['', '## Benter情報量テスト（日単位の交差検証、勝ち馬の対数損失・小さいほど良い）', '',
          f"- 市場のみ {b.get('logloss_market')}／モデルのみ {b.get('logloss_model')}／結合（検証日外で推定）{b.get('logloss_combined_oos')}"
          f"（{b.get('races', 0)}R）", f"- 2・3着の確率モデル（対数損失）：{o.get('place_order_model')}", '']
    return '\n'.join(L)


def write_daily(root, day):
    """Per-day shadow file next to the daily review (allocation / NO-BET / ◎ vs 1番人気 / 危険な1番人気)."""
    root = Path(root)
    o = measure(root, days={day})
    if not o['races']:
        return None
    d = root / day / 'review'
    d.mkdir(parents=True, exist_ok=True)
    (d / 'shadow_daily.json').write_text(json.dumps(o, ensure_ascii=False, indent=1) + '\n')
    (d / 'shadow_daily.md').write_text(md(o).replace('# 地方版 影計測', '# 地方版 日次影計測', 1))
    return o


if __name__ == '__main__':
    root = Path(sys.argv[1])
    stem = Path(sys.argv[2]) if len(sys.argv) > 2 else root / 'shadow_measure'
    o = measure(root)
    stem.with_suffix('.json').write_text(json.dumps(o, ensure_ascii=False, indent=1) + '\n')
    stem.with_suffix('.md').write_text(md(o))
    print(md(o))
