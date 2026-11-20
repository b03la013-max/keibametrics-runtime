"""Revision-2 audit and winner diagnosis (ChatGPT 11/20 review P0-A / P0-B). Evidence only.

For every race whose formal prediction was re-signed as Revision 2 (formal/rev2/), compare with Revision 1:
  * revision_reasons, source_freeze_at of both
  * input changes: win odds per horse (the only input that changed in the 11/20 sample), scratches
  * winner rank in the formal ranking R1 -> R2, winner inside W in R1 / R2
  * the 29 indices that moved for the winner (R1 -> R2)
  * same-budget replay: payout of the R1 delivered tickets vs the R2 delivered tickets on the official result
And for every settled race whose winner was outside W (effective revision): the winner's formal rank, the indices
that had it in their top 3, its market rank, and whether its odds shortened between the revisions.
Plus a "late money" table: horses whose win odds shortened by >= 25 % between R1 and R2 vs the rest (win and
top-3 rates) -- the formal indices PRI / OPI-V move against such horses (SON_09 11/20: 7.8 -> 5.0, PRI 90 -> 60).
Nothing here feeds Production.
"""
import json
from pathlib import Path

PROFILE = 'KM-LOCAL-REVISION-AUDIT-v1.0-20261121'
SHORTEN = 0.75


def _j(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return None


def _odds(receipt):
    try:
        rs = receipt['artifact']['active_runner_universe']['runners']
    except (TypeError, KeyError):
        return {}
    out = {}
    for x in rs:
        no = x.get('horse_no') or x.get('no')
        try:
            out[int(no)] = float(x.get('win_odds'))
        except (TypeError, ValueError):
            continue
    return out


def _idx(full29):
    return {int(x['no']): x['indices'] for x in (full29 or {}).get('runners') or []}


def _replay(summary, res):
    from runtime.local_autopilot import formal_mix, shadow_measure as sm
    ns = set(res.get('non_starters') or []) | set(res.get('non_starters_inferred') or [])
    return sm.settle(formal_mix.variants(summary)['R54_60'], res['payouts'], ns)[1]


def race(day_dir, key):
    d1, d2 = Path(day_dir) / 'formal', Path(day_dir) / 'formal' / 'rev2'
    s1, s2 = _j(d1 / f'{key}.summary.json'), _j(d2 / f'{key}.summary.json')
    res = _j(d2 / f'{key}.result.json') or _j(d1 / f'{key}.result.json')
    if not s1 or not res or len(res.get('order') or []) < 3:
        return None
    w = int(res['order'][0])
    rank1 = [int(x) for x in s1.get('ranking') or []]
    roles1 = {int(h): v for h, v in (s1.get('roles') or {}).items()}
    out = {'race': key, 'winner': w, 'order': [int(x) for x in res['order'][:3]],
           'winner_rank_r1': rank1.index(w) + 1 if w in rank1 else None,
           'winner_in_W_r1': 'W' in roles1.get(w, [])}
    o1 = _odds(_j(d1 / f'{key}.source_receipt.json'))
    if s2:
        rank2 = [int(x) for x in s2.get('ranking') or []]
        roles2 = {int(h): v for h, v in (s2.get('roles') or {}).items()}
        o2 = _odds(_j(d2 / f'{key}.source_receipt.json'))
        i1, i2 = _idx(_j(d1 / f'{key}.full29.json')), _idx(_j(d2 / f'{key}.full29.json'))
        moved = {k: [round(i1[w][k], 1), round(i2[w][k], 1)] for k in (i1.get(w) or {})
                 if isinstance(i1[w].get(k), (int, float)) and isinstance((i2.get(w) or {}).get(k), (int, float))
                 and abs(i1[w][k] - i2[w][k]) >= 0.5}
        out.update({'revision2': True, 'revision_reasons': s2.get('revision_reasons'),
                    'winner_rank_r2': rank2.index(w) + 1 if w in rank2 else None,
                    'winner_in_W_r2': 'W' in roles2.get(w, []),
                    'winner_odds': [o1.get(w), o2.get(w)], 'winner_indices_moved': moved,
                    'odds_changed': sum(1 for h in o1 if h in o2 and o1[h] != o2[h]),
                    'shortened': sorted(h for h in o1 if h in o2 and o1[h] and o2[h] <= SHORTEN * o1[h]),
                    'odds_r1': o1, 'odds_r2': o2})
        try:
            out['replay_payout_r1_r2'] = [_replay(s1, res), _replay(s2, res)]
        except Exception:
            out['replay_payout_r1_r2'] = None
    else:
        out['revision2'] = False
    eff_roles = {int(h): v for h, v in ((s2 or s1).get('roles') or {}).items()}
    if 'W' not in eff_roles.get(w, []):
        i = _idx(_j((d2 if s2 else d1) / f'{key}.full29.json'))
        tops = []
        for name in sorted({k for v in i.values() for k, x in v.items() if isinstance(x, (int, float))}):
            vals = {h: v.get(name) for h, v in i.items() if isinstance(v.get(name), (int, float))}
            if len(set(vals.values())) > 1 and w in sorted(vals, key=lambda h: -vals[h])[:3]:
                tops.append(name)
        odds = out.get('odds_r2') or o1
        mrank = sorted(odds, key=odds.get).index(w) + 1 if w in odds else None
        out['w_miss'] = {'winner_market_rank': mrank, 'indices_with_winner_top3': tops,
                         'winner_rank_effective': out.get('winner_rank_r2') or out['winner_rank_r1']}
    return out


def day(day_dir):
    q = _j(Path(day_dir) / 'queue.json') or {}
    rows = [r for r in (race(day_dir, k) for k in sorted(q.get('races') or {})) if r]
    rev = [r for r in rows if r.get('revision2')]
    late = {'shortened': [0, 0, 0], 'other': [0, 0, 0]}
    for r in rev:
        for h in r['odds_r1']:
            g = late['shortened' if h in r['shortened'] else 'other']
            g[0] += 1
            g[1] += h == r['order'][0]
            g[2] += h in r['order']
    rate = lambda a, i: round(100 * a[i] / a[0], 1) if a[0] else None
    summ = {'profile': PROFILE, 'races': len(rows), 'revision2': len(rev),
            'winner_rank_better': sum(1 for r in rev if r['winner_rank_r2'] and r['winner_rank_r1'] and r['winner_rank_r2'] < r['winner_rank_r1']),
            'winner_rank_worse': sum(1 for r in rev if r['winner_rank_r2'] and r['winner_rank_r1'] and r['winner_rank_r2'] > r['winner_rank_r1']),
            'w_lost_by_rev2': sum(1 for r in rev if r['winner_in_W_r1'] and not r['winner_in_W_r2']),
            'w_gained_by_rev2': sum(1 for r in rev if not r['winner_in_W_r1'] and r['winner_in_W_r2']),
            'replay_payout_r1': sum((r.get('replay_payout_r1_r2') or [0, 0])[0] for r in rev),
            'replay_payout_r2': sum((r.get('replay_payout_r1_r2') or [0, 0])[1] for r in rev),
            'late_money': {k: {'horses': v[0], 'win_rate': rate(v, 1), 'top3_rate': rate(v, 2)} for k, v in late.items()},
            'w_miss': sum(1 for r in rows if r.get('w_miss')),
            'w_miss_market_top3': sum(1 for r in rows if r.get('w_miss') and (r['w_miss']['winner_market_rank'] or 99) <= 3),
            'production_change': 'NONE (evidence only)'}
    return {'summary': summ, 'races': rows}


def md(out, date):
    s = out['summary']
    L = [f'# 修正版（Rev2）監査と勝ち馬漏れの診断 {date}（証拠のみ）', '',
         f"対象 {s['races']}R、うちRev2 {s['revision2']}R。勝ち馬の順位：改善 {s['winner_rank_better']}R／悪化 {s['winner_rank_worse']}R。"
         f"Rev2でWから外れた勝ち馬 {s['w_lost_by_rev2']}R／Rev2でWに入った勝ち馬 {s['w_gained_by_rev2']}R。"
         f"同じ60点の払戻：Rev1 {s['replay_payout_r1']:,}円 → Rev2 {s['replay_payout_r2']:,}円。", '',
         (lambda a, b: f"直前に買われた馬（Rev1→Rev2で単勝が25%以上短縮）{a['horses']}頭：勝率 {a['win_rate']}%・3着内 {a['top3_rate']}%"
                       f"／その他 {b['horses']}頭：勝率 {b['win_rate']}%・3着内 {b['top3_rate']}%（1日分は参考）")(s['late_money']['shortened'], s['late_money']['other']), '',
         f"勝ち馬がW外：{s['w_miss']}R（うち市場の上位3頭 {s['w_miss_market_top3']}R）", '',
         '| R | 勝ち馬 | 順位R1→R2 | W R1/R2 | 単勝R1→R2 | 動いた指数（勝ち馬） | 60点払戻R1→R2 |', '|---|---|---|---|---|---|---|']
    for r in out['races']:
        if not r.get('revision2'):
            continue
        mv = ', '.join(f"{k} {a}→{b}" for k, (a, b) in list(r['winner_indices_moved'].items())[:4])
        L.append(f"| {r['race']} | {r['winner']} | {r['winner_rank_r1']}→{r['winner_rank_r2']} | "
                 f"{'○' if r['winner_in_W_r1'] else '×'}/{'○' if r['winner_in_W_r2'] else '×'} | "
                 f"{r['winner_odds'][0]}→{r['winner_odds'][1]} | {mv} | "
                 f"{'→'.join(f'{x:,}' for x in (r.get('replay_payout_r1_r2') or []))} |")
    L += ['', '## 勝ち馬がWの外だったレース', '', '| R | 勝ち馬 | 正式順位 | 市場順位 | 勝ち馬を上位3頭に入れていた指数 |', '|---|---|---|---|---|']
    for r in out['races']:
        m = r.get('w_miss')
        if m:
            L.append(f"| {r['race']} | {r['winner']} | {m['winner_rank_effective']} | {m['winner_market_rank']} | {', '.join(m['indices_with_winner_top3']) or '-'} |")
    return '\n'.join(L) + '\n'


def write_daily(day_dir):
    out = day(day_dir)
    rv = Path(day_dir) / 'review'
    rv.mkdir(exist_ok=True)
    (rv / 'revision_audit.json').write_text(json.dumps(out, ensure_ascii=False) + '\n')
    (rv / 'revision_audit.md').write_text(md(out, Path(day_dir).name))
    return out
