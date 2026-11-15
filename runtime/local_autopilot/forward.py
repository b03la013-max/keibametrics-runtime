"""Forward OOS summary for the LOCAL PAPER autopilot (all days, no network).

Counts only revisions frozen before cutoff (the settled revision) and their
official-result settlement. Reports recommended (PAPER, 100 yen/point) PFS
with the stability measures the 11/15 directive requires: profitable-race
rate, PFS without the single largest payout, max drawdown, bet coverage,
W/P2/P3 capture and the first-failure distribution. Never a real purchase.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from runtime.local_autopilot.settle import diagnose


def _races(root):
    for day in sorted(p for p in Path(root).iterdir() if p.is_dir() and p.name[:2] == '20'):
        qp = day / 'queue.json'
        if not qp.exists():
            continue
        q = json.loads(qp.read_text())
        for key, r in sorted(q['races'].items(), key=lambda kv: kv[1]['post_current']):
            yield day, key, r


def summarize(root):
    rows, cum, peak, mdd = [], 0, 0, 0
    fails, days = Counter(), {}
    for day, key, r in _races(root):
        d = days.setdefault(day.name, {'races': 0, 'prestart': 0, 'settled': 0, 'eff': 0, 'pay': 0})
        d['races'] += 1
        d['prestart'] += int(any(e.get('before_cutoff') for e in r['editions']))
        st = r.get('settlement')
        if not st:
            continue
        rev = st.get('revision')
        fp = day / 'rev' / f'{rev}.json' if rev else day / f'{key}.json'
        if not fp.exists():
            continue
        rank = [x['no'] for x in json.loads(fp.read_text())['prediction']['ranking']]
        dg = st.get('diagnosis') or diagnose(rank, st['order'], st['payout'] > 0)
        eff = st.get('effective_invest', st['invest'])
        cum += st['payout'] - eff
        peak = max(peak, cum)
        mdd = max(mdd, peak - cum)
        fails[dg['first_failure']] += 1
        d['settled'] += 1
        d['eff'] += eff
        d['pay'] += st['payout']
        rows.append({'day': day.name, 'race': key, 'eff': eff, 'pay': st['payout'], 'dg': dg,
                     'win': st.get('win_hit', 0), 'p2': int(dg['second_rank'] == 2), 'p3': int(dg['third_rank'] == 3)})
    n = len(rows)
    eff = sum(x['eff'] for x in rows)
    pay = sum(x['pay'] for x in rows)
    top = max((x['pay'] for x in rows), default=0)
    bets = sum(1 for x in rows if x['eff'] > 0)
    return {'classification': 'LOCAL_PAPER_FORWARD_OOS (pre-cutoff frozen revisions; not real purchases)',
            'settled_races': n, 'effective_invest': eff, 'payout': pay,
            'pfs': round(100 * pay / eff, 1) if eff else None,
            'pfs_without_max_payout': round(100 * (pay - top) / eff, 1) if eff else None,
            'max_single_payout': top, 'max_drawdown': mdd,
            'profitable_race_rate': round(sum(1 for x in rows if x['pay'] > x['eff']) / n, 3) if n else None,
            'bet_coverage': round(bets / n, 3) if n else None,
            'w_hit': sum(x['win'] for x in rows), 'p2_exact': sum(x['p2'] for x in rows),
            'p3_exact': sum(x['p3'] for x in rows), 'first_failure': dict(fails),
            'milestones': {k: n >= k for k in (30, 100, 500)}, 'days': days}


def write(root):
    s = summarize(root)
    (Path(root) / 'forward_summary.json').write_text(json.dumps(s, ensure_ascii=False, indent=1) + '\n')
    L = ['# LOCAL Forward OOS（PAPER・推薦試算・実購入なし）', '',
         f"- 精算Race {s['settled_races']}（R30 {'達成' if s['milestones'][30] else '未達'}／R100 {'達成' if s['milestones'][100] else '未達'}／R500 {'達成' if s['milestones'][500] else '未達'}）",
         f"- 実効投資 {s['effective_invest']:,}円／払戻 {s['payout']:,}円／**PFS {s['pfs']}%**（最大払戻 {s['max_single_payout']:,}円を除くと {s['pfs_without_max_payout']}%）",
         f"- 最大ドローダウン {s['max_drawdown']:,}円／黒字Race率 {s['profitable_race_rate']}／Bet Coverage {s['bet_coverage']}",
         f"- W的中 {s['w_hit']}／P2一致 {s['p2_exact']}／P3一致 {s['p3_exact']}",
         f"- 第一失敗の分布：{s['first_failure']}", '', '| 日付 | Race | 締切前 | 精算 | 実効投資 | 払戻 | PFS |', '|---|---|---|---|---|---|---|']
    for k, d in s['days'].items():
        L.append(f"| {k} | {d['races']} | {d['prestart']} | {d['settled']} | {d['eff']:,} | {d['pay']:,} | "
                 f"{round(100 * d['pay'] / d['eff'], 1) if d['eff'] else '–'}% |")
    (Path(root) / 'forward_summary.md').write_text('\n'.join(L) + '\n')
    return s
