"""Budget-changing research series (Owner 2026-11-26 22:31 「する」): fewer points or no bet in races the formal
prediction itself marks as uncertain. RESEARCH ONLY: never auto-promoted (auto_promote compares the same budget only),
the 60-point cap, the purchase policy and the delivery are untouched. Thresholds and series are frozen in
profiles/KM_LOCAL_BUDGET_SERIES_PREREG_20261127.json; races before its first eligible day are an in-sample reference.
"""
from __future__ import annotations

import json
from pathlib import Path

from runtime.local_autopilot import five
from runtime.local_autopilot import shadow_measure as sm

REPO = Path(__file__).resolve().parents[2]
PREREG = json.loads((REPO / 'profiles' / 'KM_LOCAL_BUDGET_SERIES_PREREG_20261127.json').read_text())
GAP = PREREG['thresholds']['top2_gap_low']
FIRST = PREREG['first_eligible_day']
HALF = 30


def _half(tickets, ranking, n=HALF):
    tier = {'CORE': 0, 'PROTECTION': 1, 'TAIL': 2}
    pos = {int(h): i for i, h in enumerate(ranking)}
    order = sorted(range(len(tickets)), key=lambda i: (tier.get(str(tickets[i].get('mec_tier')), 3),
                                                        sum(pos.get(int(x), 99) for x in tickets[i]['selection']), i))
    return [tickets[i] for i in order[:n]]


def series(root):
    """-> {'forward': {series: [(day, inv, pay)]}, 'reference': {...}} in post order."""
    rows = {(r['day'], r['key']): r for r in five._race_rows(root)}
    out = {'forward': {}, 'reference': {}}
    for sp in sorted(Path(root).glob('20??-??-??/formal/*.summary.json')):
        key, day = sp.name.split('.')[0], sp.parent.parent.name
        r = rows.get((day, key))
        sm_ = five._load(sp) or {}
        res = five._load(sp.parent.parent / f'{key}.result.json') or {}
        if not r or not res.get('payouts') or not sm_.get('tickets'):
            continue
        ns = set(res.get('non_starters') or []) | set(res.get('non_starters_inferred') or [])
        tk = sm_['tickets']
        rank = [int(x) for x in sm_.get('ranking') or []]
        low_gap = r['gap'] is not None and r['gap'] <= GAP
        krs_d = r['robust'] == 'D'
        plan = {'B0_DELIVERED': tk, 'B1_GAP_SKIP': [] if low_gap else tk, 'B2_GAP_HALF': _half(tk, rank) if low_gap else tk,
                'B3_KRSD_SKIP': [] if krs_d else tk, 'B4_ANY_HALF': _half(tk, rank) if (low_gap or krs_d) else tk,
                'B5_ALL20': _half(tk, rank, 20), 'B6_ALL30': _half(tk, rank, 30)}
        bucket = out['forward' if day >= FIRST else 'reference']
        for nm, t in plan.items():
            inv, pay, _ = sm.settle([(x['bet_type'], [int(y) for y in x['selection']]) for x in t], res['payouts'], ns)
            bucket.setdefault(nm, []).append((day, inv, pay))
    return out


def report(root):
    s = series(root)
    return {ph: {nm: dict(five.risk(seq), ruin=five.ruin(seq) if seq else None, skipped=sum(1 for x in seq if x[1] == 0))
                 for nm, seq in d.items()} for ph, d in s.items()}


def md(rep):
    L = ['', '**KSP-03 予算を変える研究系列（研究のみ・自動採用なし・判断は Owner）**', '',
         f'1位と2位の差 <= {GAP}（事前固定）または KRS 頑健度 D のレースで、見送り／上位30点に減らした場合。', '',
         '| 期間 | 系列 | R | 見送り | 投資 | PFS | 最大払戻除く | 最大ドローダウン | 仮想30万円・300Rで0円 |', '|---|---|---|---|---|---|---|---|---|']
    for ph, lab in (('forward', f'{FIRST}〜（判断用）'), ('reference', '〜11/26（参考）')):
        for nm, x in (rep.get(ph) or {}).items():
            L.append(f"| {lab} | {nm} | {x['races']} | {x['skipped']} | {x['invest']:,}円 | {x['pfs']}% | {x['pfs_ex_top1']}% | "
                     f"{x['max_drawdown']:,}円 | {(x.get('ruin') or {}).get('ruin_share')} |")
    return '\n'.join(L) + '\n'
