"""Automatic adoption of the 地方版 improvements that are not same-budget ticket variants
(Owner 上濵さん 2026-11-28 23:37 「改善は承認無しで進めて欲しい」). auto_promote already adopts same-budget ticket variants
without approval; this module does the same for the two research tracks that still waited for the Owner:

  BUDGET  KSP-03 point-reducing series (budget_series B2_GAP_HALF / B4_ANY_HALF / B5_ALL20 / B6_ALL30).
          The no-bet series B1/B3 stay research only: the Owner's purchase policy is 毎レース購入 (2026-11-15).
          Adopt when, on >=100 forward races after its first eligible day: PFS > B0, PFS without the largest payout
          > B0, net result (payout - invest) >= B0's, and the series is better on >=2 venues with >=12 races.
          Probation: the next 100 races of its own; reverted when PFS without the largest payout falls below B0.
  KRS     KCP CAL-01/02 KRS input variant (krs_research HOLD15). Adopt when, on >=100 re-run races, the variant has a
          lower SSR-W log loss than the formal KRS and a top-3 AUC that is not lower. When adopted, the formal KRS is
          run on the variant input; the nightly research re-runs the BASE input so the probation compares the same
          races; reverted when BASE has the lower log loss over the next 100 races.

Never changes: 三布告, the 60-point cap (budgets only go down), real purchases, KRS engine / parameter_map (only the
KRS *input* variant), the delivery. Every switch is posted to the delivery issue by run.py.
Rollback: delete output/auto_policy.json 'budget' / 'krs' entries, or set KM_LOCAL_AUTO_POLICY=0.
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path

PROFILE = 'KM-LOCAL-AUTO-POLICY-v1.0-20261128'
FIRST_ELIGIBLE = '2026-11-29'          # races decided from here are the forward sample of this rule
MIN_RACES = 100
MIN_VENUE_RACES = 12
MIN_VENUES = 2
BUDGET_SERIES = ('B2_GAP_HALF', 'B4_ANY_HALF', 'B5_ALL20', 'B6_ALL30')
KRS_VARIANTS = ('HOLD15',)


def _enabled():
    return os.environ.get('KM_LOCAL_AUTO_POLICY', '1') != '0'


def path(root):
    return Path(root) / 'auto_policy.json'


def load(root):
    try:
        return json.loads(path(root).read_text())
    except (OSError, ValueError):
        return {'profile': PROFILE, 'budget': None, 'krs': None, 'history': [], 'blocked': {}}


def _save(root, st):
    st['profile'] = PROFILE
    path(root).write_text(json.dumps(st, ensure_ascii=False, indent=1) + '\n')


def active(st, kind, race_date):
    a = (st or {}).get(kind)
    return a if a and str(race_date) >= a['effective_from'] else None


def _agg(rows, nm):
    v = [r[nm] for r in rows]
    inv, pay = sum(x[0] for x in v), sum(x[1] for x in v)
    pays = sorted((x[1] for x in v), reverse=True)
    inv_x = inv - (next((x[0] for x in v if x[1] == pays[0]), 0) if pays else 0)
    pay_x = pay - (pays[0] if pays else 0)
    return {'races': len(v), 'invest': inv, 'payout': pay, 'net': pay - inv,
            'pfs': round(100 * pay / inv, 2) if inv else 0.0, 'pfs_ex_top1': round(100 * pay_x / inv_x, 2) if inv_x else 0.0}


def budget_compare(rows, nm):
    c, b = _agg(rows, nm), _agg(rows, 'B0_DELIVERED')
    better = []
    for v in sorted({r['key'].split('_')[0] for r in rows}):
        rs = [r for r in rows if r['key'].split('_')[0] == v]
        if len(rs) >= MIN_VENUE_RACES and _agg(rs, nm)['pfs'] > _agg(rs, 'B0_DELIVERED')['pfs']:
            better.append(v)
    checks = {'races': len(rows) >= MIN_RACES, 'pfs': c['pfs'] > b['pfs'], 'pfs_ex_top1': c['pfs_ex_top1'] > b['pfs_ex_top1'],
              'net': c['net'] >= b['net'], 'venues_better': len(better) >= MIN_VENUES}
    return {'series': c, 'base': b, 'venues_better': better, 'checks': checks, 'passes': all(checks.values())}


def decide_budget(root, today, rows=None):
    from runtime.local_autopilot import budget_series
    st = load(root)
    rows = rows if rows is not None else budget_series.race_rows(root)
    nxt = (date.fromisoformat(today) + timedelta(days=1)).isoformat()
    rec = {'kind': 'BUDGET', 'day': today, 'action': 'KEEP'}
    a = st.get('budget')
    if a:
        rs = [r for r in rows if r['day'] >= a['effective_from'] and a['series'] in r]
        cmpd = budget_compare(rs, a['series'])
        rec.update(action='PROBATION', series=a['series'], races=len(rs), detail=cmpd)
        if len(rs) >= MIN_RACES and cmpd['series']['pfs_ex_top1'] < cmpd['base']['pfs_ex_top1']:
            st['budget'] = None
            st.setdefault('blocked', {})['BUDGET:' + a['series']] = nxt
            rec.update(action='REVERT', effective_from=nxt)
    else:
        best = None
        for nm in BUDGET_SERIES:
            start = max(FIRST_ELIGIBLE, st.get('blocked', {}).get('BUDGET:' + nm, ''))
            rs = [r for r in rows if r['day'] >= start and nm in r]
            cmpd = budget_compare(rs, nm)
            rec.setdefault('evaluated', {})[nm] = {'races': len(rs), 'checks': cmpd['checks'], 'pfs': cmpd['series']['pfs'],
                                                   'base_pfs': cmpd['base']['pfs']}
            if cmpd['passes'] and (best is None or cmpd['series']['pfs_ex_top1'] > best[1]['series']['pfs_ex_top1']):
                best = (nm, cmpd)
        if best:
            st['budget'] = {'series': best[0], 'effective_from': nxt, 'adopted_on': today}
            rec.update(action='ADOPT', series=best[0], effective_from=nxt)
    if rec['action'] in ('ADOPT', 'REVERT'):
        st['history'] = (st.get('history') or [])[-100:] + [{k: rec[k] for k in rec if k not in ('evaluated', 'detail')}]
    st['last_budget'] = {k: rec[k] for k in rec if k != 'detail'}
    _save(root, st)
    return rec


def apply_budget(capped, ranking, numerical, krs_utility, root, race_date):
    """Live: reduce the capped tickets by the adopted series (never adds tickets). Returns capped unchanged when no
    series is active or the race does not meet the series condition."""
    if not _enabled() or not capped:
        return capped, None
    a = active(load(root), 'budget', race_date)
    if not a:
        return capped, None
    from runtime.local_autopilot import budget_series
    ov = sorted((float(x['overall']) for x in (numerical or {}).get('runner_scores') or []), reverse=True)
    gap = (ov[0] - ov[1]) if len(ov) > 1 else None
    rob = {int(x['horse_no']): x.get('Robustness') for x in (krs_utility or {}).get('summary') or []}
    rank = [int(x) for x in ranking]
    plan = budget_series.plan_for(capped['tickets'], rank, gap, rob.get(rank[0]) if rank else None)
    t = plan[a['series']]
    if len(t) >= len(capped['tickets']) or not t:
        return capped, {'series': a['series'], 'applied': False}
    new = dict(capped, tickets=t, kept_count=len(t), kept_investment=100 * len(t),
               tickets_before_budget=capped['tickets'], budget_policy={'profile': PROFILE, **a, 'applied': True})
    new.pop('sha256', None)
    return new, new['budget_policy']


# ---------------------------------------------------------------- KRS input
def decide_krs(root, today, cmp=None):
    from runtime.local_autopilot import krs_calib
    st = load(root)
    nxt = (date.fromisoformat(today) + timedelta(days=1)).isoformat()
    rec = {'kind': 'KRS', 'day': today, 'action': 'KEEP'}
    cmp = cmp if cmp is not None else krs_calib.compare_variants(root)
    a = st.get('krs')
    if a:
        x = cmp.get('BASE') or {}
        f, b = x.get('formal') or {}, x.get('BASE') or {}
        rec.update(action='PROBATION', variant=a['variant'], races=b.get('races', 0))
        if (b.get('races') or 0) >= MIN_RACES and b.get('log_loss') is not None and f.get('log_loss') is not None \
                and b['log_loss'] < f['log_loss']:
            st['krs'] = None
            # the re-run sample of the variant is cumulative, so a reverted variant waits 60 days before it can return
            st.setdefault('blocked', {})['KRS:' + a['variant']] = (date.fromisoformat(today) + timedelta(days=60)).isoformat()
            rec.update(action='REVERT', effective_from=nxt)
    else:
        for nm in KRS_VARIANTS:
            x = cmp.get(nm) or {}
            f, v = x.get('formal') or {}, x.get(nm) or {}
            ok = ((v.get('races') or 0) >= MIN_RACES and None not in (v.get('log_loss'), f.get('log_loss'))
                  and v['log_loss'] < f['log_loss'] and (v.get('auc_top3') or 0) >= (f.get('auc_top3') or 0)
                  and today >= st.get('blocked', {}).get('KRS:' + nm, ''))
            rec.setdefault('evaluated', {})[nm] = {'races': v.get('races'), 'log_loss': v.get('log_loss'),
                                                   'formal_log_loss': f.get('log_loss'), 'passes': ok}
            if ok:
                st['krs'] = {'variant': nm, 'effective_from': nxt, 'adopted_on': today}
                rec.update(action='ADOPT', variant=nm, effective_from=nxt)
                break
    if rec['action'] in ('ADOPT', 'REVERT'):
        st['history'] = (st.get('history') or [])[-100:] + [{k: rec[k] for k in rec if k != 'evaluated'}]
    st['last_krs'] = rec
    _save(root, st)
    return rec


def krs_input_for(kin, root, race_date):
    """Live: the KRS input the formal KRS runs on (the adopted variant, or the base input)."""
    if not _enabled():
        return kin, None
    a = active(load(root), 'krs', race_date)
    if not a:
        return kin, None
    from runtime.local_autopilot import krs_research
    return krs_research.variant_input(kin, a['variant']), a['variant']


def md(recs):
    L = ['## 自動の改善採否（承認不要・Owner 2026-11-28）', '']
    for r in recs:
        if not r:
            continue
        what = r.get('series') or r.get('variant') or ''
        lab = {'ADOPT': f"**採用** {what}（{r.get('effective_from')} から）", 'REVERT': f"**取り消し** {what}（{r.get('effective_from')} から元に戻す）",
               'PROBATION': f"試用中 {what}（{r.get('races')}R）", 'KEEP': '変更なし'}[r['action']]
        L.append(f"- {'点数を減らす系列' if r['kind'] == 'BUDGET' else 'KRS の入力'}：{lab}")
        for nm, e in (r.get('evaluated') or {}).items():
            L.append(f"  - {nm}：{e.get('races')}R" + (f"・PFS {e.get('pfs')}%（配信 {e.get('base_pfs')}%）" if 'pfs' in e else
                                                     f"・対数損失 {e.get('log_loss')}（正式 {e.get('formal_log_loss')}）"))
    return '\n'.join(L) + '\n'
