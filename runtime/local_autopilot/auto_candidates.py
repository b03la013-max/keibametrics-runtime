"""Automatic generation of improvement candidates from the daily reflection (Owner 2026-11-22 21:31 JST
「自動にして欲しいです。その形で作って欲しいです」 for Claude's 21:29 proposal).

Every race day, once all races are settled and auto_promote.decide has run:
  1. RETIRE: a generated candidate that has >= RETIRE_RACES races without being promoted, or >= MIN_RACES races
     with both PFS and PFS-without-the-largest-payout below what is delivered, is retired (frees a slot).
  2. GENERATE: from the day's improvement priority (review/daily_summary.json, P1 first, by impact), up to
     MAX_NEW_PER_DAY new candidates are drawn from the families mapped to each priority, in a fixed parameter
     order, skipping anything already registered (in any state) or identical to a fixed candidate. At most
     MAX_EVALUATING generated candidates are evaluated at the same time.
  3. Each new candidate is registered in <data root>/auto_candidates.json BEFORE its first eligible day (the next
     calendar day, 00:00 JST); the data branch commit is the timestamp. Only races from that day count.
Every candidate is a complete same-budget ticket set (formal_mix.gen_variant) built from the signed formal
summary, so auto_promote's fixed rules (100R, PFS, PFS without the largest payout, hits, >= 2 venues, no venue
much worse, automatic demotion) decide alone. The 29 indices, KRS, MEC, the 60-ticket cap and the purchase
policy (recommendation only) are untouched.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

from runtime.local_autopilot import formal_mix

PROFILE = 'KM-LOCAL-AUTO-CANDIDATES-v1.0-20261122'
MAX_EVALUATING = 6
MAX_NEW_PER_DAY = 2
RETIRE_RACES = 200
FAMILY_GRID = {   # family -> parameter sets in the order they are tried (the fixed C13/C15/C23/C24/C28 settings excluded)
    'TRIOBOX': [{'n': 5}, {'n': 4}],
    'WAXTRIO': [{'n': 5}, {'n': 4}],
    'THIRDK': [{'k': 2}, {'k': 4}],
    'WPLUS': [{'add': 1}, {'add': 3}],
    'P2PLUS': [{'add': 1}, {'add': 2}],
    'CORE': [{'n': 2}, {'n': 4}],
    'PAIRFULL': [{'pairs': 6}, {'pairs': 4}],
    'MKTP2': [{'blend': 50}, {'blend': 75}],
    'KRSCAP': [{'mode': 1}, {'mode': 2}],
}
PRIORITY_FAMILIES = {   # reflection priority id -> families that address it (same budget)
    'P1:HIT_BUT_LOSS': ['CORE', 'TRIOBOX', 'WAXTRIO'],
    'P1:ROLE_P2_MISS': ['MKTP2', 'P2PLUS', 'TRIOBOX'],
    'P1:ROLE_W_MISS': ['WPLUS'],
    'P1:ROLE_P3_MISS': ['THIRDK'],
    'P1:TICKET_ORDER_MISS': ['WAXTRIO', 'TRIOBOX'],
    'P1:CAP_LOST_HIT': ['PAIRFULL', 'KRSCAP', 'CORE'],   # from review/formal_eval.json (60-point cap dropped a hit)
}


def path(root):
    return Path(root) / 'auto_candidates.json'


def load(root):
    try:
        return json.loads(path(root).read_text())
    except (OSError, ValueError):
        return {'profile': PROFILE, 'candidates': {}, 'log': []}


def _priorities(day_dir):
    try:
        s = json.loads((Path(day_dir) / 'review' / 'daily_summary.json').read_text())
    except (OSError, ValueError):
        return []
    pr = [p for p in s.get('improvement_priority') or [] if p.get('id') in PRIORITY_FAMILIES]
    try:   # the cap's lost hits are measured by formal_eval, not by the per-race review (ChatGPT 11/22 21:45)
        live = json.loads((Path(day_dir) / 'review' / 'formal_eval.json').read_text())['aggregate']['LIVE_R54']
        if live.get('races_with_lost_hits'):
            pr.append({'id': 'P1:CAP_LOST_HIT', 'tier': 'P1', 'count': live['races_with_lost_hits'],
                       'impact_yen': int(live.get('payout_lost') or 0), 'title': '60点上限で的中券を失った'})
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return sorted(pr, key=lambda p: ({'P0': 0, 'P1': 1, 'P2': 2}.get(p.get('tier'), 3), -(p.get('impact_yen') or 0)))


def _retire(st, root, today, rows_fn, decision):
    from runtime.local_autopilot import auto_promote
    out = []
    active = ((auto_promote.load_state(root).get('active')) or {}).get('candidate')
    ev = (decision or {}).get('evaluated') or {}
    for cid, c in st['candidates'].items():
        if c.get('status') != 'EVALUATING' or cid == active:
            continue
        e = ev.get(cid)
        if not e:
            continue
        n = e['races']
        worse = e['candidate']['pfs'] < e['champion']['pfs'] and e['candidate']['pfs_ex_top1'] < e['champion']['pfs_ex_top1']
        if n >= RETIRE_RACES or (n >= auto_promote.MIN_RACES and worse):
            c.update(status='RETIRED', retired_on=today,
                     reason=f"{n}R：PFS {e['candidate']['pfs']}% 対 {e['champion']['pfs']}%、最大払戻除く "
                            f"{e['candidate']['pfs_ex_top1']}% 対 {e['champion']['pfs_ex_top1']}%")
            out.append(cid)
    for cid, c in st['candidates'].items():   # a promoted generated candidate is marked as such
        if cid == active and c.get('status') == 'EVALUATING':
            c['status'] = 'PROMOTED'
            c['promoted_on'] = today
    return out


def generate(st, root, today):
    from runtime.local_autopilot import auto_promote
    evaluating = [c for c in st['candidates'].values() if c.get('status') == 'EVALUATING']
    slots = min(MAX_NEW_PER_DAY, MAX_EVALUATING - len(evaluating))
    if slots <= 0:
        return []
    used = {c['variant'] for c in st['candidates'].values()} | {v for v, _ in auto_promote.CANDIDATES.values()}
    nxt = (date.fromisoformat(today) + timedelta(days=1)).isoformat()
    new = []
    for p in _priorities(Path(root) / today):
        for fam in PRIORITY_FAMILIES[p['id']]:
            for params in FAMILY_GRID[fam]:
                name = formal_mix.gen_name(fam, **params)
                if name in used:
                    continue
                cid = f"G{len(st['candidates']) + 1:03d}-{fam}-" + '-'.join(f'{k}{v}' for k, v in sorted(params.items()))
                st['candidates'][cid] = {
                    'variant': name, 'family': fam, 'params': params, 'status': 'EVALUATING',
                    'registered_at': datetime.now().astimezone().isoformat(),
                    'first_eligible_post': nxt + 'T00:00:00+09:00',
                    'origin': {'day': today, 'priority': p['id'], 'count': p.get('count'), 'impact_yen': p.get('impact_yen')}}
                used.add(name)
                new.append(cid)
                break
            if len(new) >= slots or (new and st['candidates'][new[-1]]['origin']['priority'] == p['id']):
                break
        if len(new) >= slots:
            break
    return new


def daily(root, today, decision=None, rows_fn=None):
    """Run after auto_promote.decide(root, today). Returns {'retired': [...], 'new': [...]} and saves the state."""
    st = load(root)
    st['profile'] = PROFILE
    st.setdefault('candidates', {})
    retired = _retire(st, root, today, rows_fn, decision)
    new = generate(st, root, today)
    st.setdefault('log', []).append({'day': today, 'retired': retired, 'new': new,
                                     'at': datetime.now().astimezone().isoformat()})
    st['log'] = st['log'][-200:]
    path(root).write_text(json.dumps(st, ensure_ascii=False, indent=1) + '\n')
    return {'retired': retired, 'new': new}


def md(root, res):
    st = load(root)
    C = st.get('candidates') or {}
    L = ['', '### 自動で作った改善案', '']
    for cid in res.get('new') or []:
        c = C[cid]
        L.append(f"- 新規登録：{cid}（{c['variant']}）← 反省 {c['origin']['priority']}（{c['origin']['count']}件・"
                 f"{c['origin']['impact_yen']:,}円）、{c['first_eligible_post'][:10]} から比較")
    for cid in res.get('retired') or []:
        L.append(f"- 引退：{cid}（{C[cid].get('reason')}）")
    ev = [k for k, c in C.items() if c.get('status') == 'EVALUATING']
    L.append(f"- 比較中の自動案：{len(ev)}／{MAX_EVALUATING}（{'・'.join(ev) or 'なし'}）")
    return '\n'.join(L) + '\n'
