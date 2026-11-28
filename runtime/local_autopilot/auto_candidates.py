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
KCP_MIN_GAIN = 0.02   # winner log loss improvement on the later days needed to register a KRS temperature
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
    'KRSW': [{'n': 1}, {'n': 2}],
    'TRIOPROT': [{'k': 6}, {'k': 12}, {'k': 18}],
}
KAG_FAMILIES = {   # KAG Purple SHADOW challenge type -> same-budget families (Owner 2026-11-28 23:32: improvements without approval)
    'R3_KRS_NOT_CONNECTED': ['KRSW', 'KRSCAP'],
    'R2_INDEX_CONFLICT': ['MKTP2', 'WPLUS'],
    'R3_P2_MISS_WITH_W': ['P2PLUS', 'MKTP2'],
    'R4_CAP_DROPPED_HIT': ['PAIRFULL', 'KRSCAP'],
    'R4_HIT_BUT_LOSS': ['TRIOPROT', 'CORE'],
    'R2_MARKET_WINNER_LOW': ['WPLUS'],
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


def _kcp(st, root, today, slots):
    """KCP (Owner 2026-11-26 21:25 「KCPは永続的に実施」): from the latest weekly KRS calibration report
    (<root>/krs_calib/<day>.json, krs_calib.weekly), when the temperature fitted on the earlier days lowers the
    later days' winner log loss by >= KCP_MIN_GAIN, register KRSCAP with that temperature (rounded to 0.05) as a
    NEW candidate. A registered candidate is never changed afterwards; a later, different T is a new candidate."""
    from runtime.local_autopilot import auto_promote
    if slots <= 0:
        return []
    reps = sorted((Path(root) / 'krs_calib').glob('20??-??-??.json'))
    if not reps:
        return []
    try:
        tk = json.loads(reps[-1].read_text())['temperature']['krs_w']
        T, a, b = float(tk['T_fitted_on_train']), float(tk['test_log_loss_identity']), float(tk['test_log_loss_tempered'])
    except (OSError, ValueError, KeyError, TypeError):
        return []
    if a - b < KCP_MIN_GAIN or abs(T - 1.0) < 0.1:
        return []
    t = int(round(T * 20)) * 5
    name = formal_mix.gen_name('KRSCAP', mode=1, t=t)
    used = {c['variant'] for c in st['candidates'].values()} | {v for v, _ in auto_promote.CANDIDATES.values()}
    if name in used:
        return []
    cid = f"G{len(st['candidates']) + 1:03d}-KRSCAP-mode1-t{t}"
    st['candidates'][cid] = {
        'variant': name, 'family': 'KRSCAP', 'params': {'mode': 1, 't': t}, 'status': 'EVALUATING',
        'registered_at': datetime.now().astimezone().isoformat(),
        'first_eligible_post': (date.fromisoformat(today) + timedelta(days=1)).isoformat() + 'T00:00:00+09:00',
        'origin': {'day': today, 'priority': 'KCP:CAL-05', 'count': None, 'impact_yen': 0,
                   'report': reps[-1].name, 'T': T, 'test_log_loss': [a, b]}}
    return [cid]


def _kiep(st, root, today, slots):
    """KIEP (Owner 2026-11-26 21:43 「永続的に実施」): an index whose neutralisation improves the formal-consumer top-3
    AUC on both the earlier and the later days (kiep.weekly report, DROP_HELPS) becomes GEN:IDXABL:drop=<n>."""
    from runtime.local_autopilot import auto_promote, kiep
    if slots <= 0:
        return []
    reps = sorted((Path(root) / 'kiep').glob('20??-??-??.json'))
    if not reps:
        return []
    try:
        ab = json.loads(reps[-1].read_text())['ablation']
    except (OSError, ValueError, KeyError):
        return []
    used = {c['variant'] for c in st['candidates'].values()} | {v for v, _ in auto_promote.CANDIDATES.values()}
    nxt = (date.fromisoformat(today) + timedelta(days=1)).isoformat() + 'T00:00:00+09:00'
    new = []
    try:
        sc = json.loads(reps[-1].read_text()).get('scale') or {}
    except (OSError, ValueError):
        sc = {}
    items = [(idx, x, 'IDXABL') for idx, x in ab.items() if x.get('verdict') == 'DROP_HELPS']
    items += [(idx, x, 'IDXSCL') for idx, x in (sc.get('rows') or {}).items() if x.get('verdict') == 'UP_HELPS']
    for idx, x, fam in sorted(items, key=lambda t: -(t[1]['test'].get('auc_gain') or 0)):
        if len(new) >= slots:
            continue
        n = kiep.INDEX_IDS.index(idx)
        name = (formal_mix.gen_name('IDXABL', drop=n) if fam == 'IDXABL' else
                formal_mix.gen_name('IDXSCL', i=n, s=int(round(100 * float(sc.get('factor') or kiep.SCALE)))))
        if name in used:
            continue
        cid = f"G{len(st['candidates']) + 1:03d}-{fam}-{idx.replace('/', '_')}"
        st['candidates'][cid] = {
            'variant': name, 'family': fam, 'params': {'index': idx, 'n': n},
            'status': 'EVALUATING', 'registered_at': datetime.now().astimezone().isoformat(), 'first_eligible_post': nxt,
            'origin': {'day': today, 'priority': 'KIEP:ABLATION', 'count': None, 'impact_yen': 0, 'report': reps[-1].name,
                       'index': idx, 'auc_gain': [x['train'].get('auc_gain'), x['test'].get('auc_gain')]}}
        used.add(name)
        new.append(cid)
    return new


def _kag(st, root, today, slots):
    """KAG (Owner 2026-11-27 22:49 永続; 2026-11-28 23:32 「改善は承認無しで進めて欲しい」): every challenge type that the
    latest Purple adjudication (<root>/<day>/review/kag.json, day <= today) marks SHADOW becomes, without any Owner
    review, the first not-yet-registered same-budget parameter set of its families. auto_promote then decides alone."""
    from runtime.local_autopilot import auto_promote
    if slots <= 0:
        return []
    reps = sorted(p for p in Path(root).glob('20??-??-??/review/kag.json') if p.parent.parent.name <= today)
    if not reps:
        return []
    try:
        pur = (json.loads(reps[-1].read_text()).get('adjudication') or {}).get('purple') or {}
    except (OSError, ValueError):
        return []
    used = {c['variant'] for c in st['candidates'].values()} | {v for v, _ in auto_promote.CANDIDATES.values()}
    nxt = (date.fromisoformat(today) + timedelta(days=1)).isoformat() + 'T00:00:00+09:00'
    new = []
    for t, x in sorted(pur.items(), key=lambda kv: -(kv[1].get('races_7d') or 0)):
        if x.get('purple') != 'SHADOW' or len(new) >= slots:
            continue
        if any(c.get('status') == 'EVALUATING' and c.get('origin', {}).get('priority') == 'KAG:' + t
               for c in st['candidates'].values()):
            continue   # one candidate per challenge type at a time; the next parameter set only after it is decided
        done = False
        for fam in KAG_FAMILIES.get(t, []):
            for params in FAMILY_GRID.get(fam, []):
                name = formal_mix.gen_name(fam, **params)
                if name in used:
                    continue
                cid = f"G{len(st['candidates']) + 1:03d}-{fam}-" + '-'.join(f'{k}{v}' for k, v in sorted(params.items()))
                st['candidates'][cid] = {
                    'variant': name, 'family': fam, 'params': params, 'status': 'EVALUATING',
                    'registered_at': datetime.now().astimezone().isoformat(), 'first_eligible_post': nxt,
                    'origin': {'day': today, 'priority': 'KAG:' + t, 'count': x.get('races_7d'), 'impact_yen': 0,
                               'report': str(reps[-1].relative_to(root))}}
                used.add(name)
                new.append(cid)
                done = True
                break
            if done:
                break
    return new


def daily(root, today, decision=None, rows_fn=None):
    """Run after auto_promote.decide(root, today). Returns {'retired': [...], 'new': [...]} and saves the state."""
    st = load(root)
    st['profile'] = PROFILE
    st.setdefault('candidates', {})
    retired = _retire(st, root, today, rows_fn, decision)
    new = generate(st, root, today)
    ev = sum(c.get('status') == 'EVALUATING' for c in st['candidates'].values())
    new += _kcp(st, root, today, min(MAX_NEW_PER_DAY - len(new), MAX_EVALUATING - ev))
    ev = sum(c.get('status') == 'EVALUATING' for c in st['candidates'].values())
    new += _kiep(st, root, today, min(MAX_NEW_PER_DAY - len(new), MAX_EVALUATING - ev))
    ev = sum(c.get('status') == 'EVALUATING' for c in st['candidates'].values())
    new += _kag(st, root, today, min(MAX_NEW_PER_DAY + 1 - len(new), MAX_EVALUATING - ev))
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
        if c['origin']['priority'].startswith('KIEP'):
            what = '無効化' if c['family'] == 'IDXABL' else '重みを上げた'
            L.append(f"- 新規登録：{cid}（{c['variant']}＝{c['origin']['index']} を{what}正式順位で60点）← KIEP 実計算 "
                     f"{c['origin']['report']}（3着内AUC 学習 {c['origin']['auc_gain'][0]:+} / 試験 {c['origin']['auc_gain'][1]:+}）、"
                     f"{c['first_eligible_post'][:10]} から比較")
            continue
        if c['origin']['priority'].startswith('KCP'):
            L.append(f"- 新規登録：{cid}（{c['variant']}）← KRS 較正測定 {c['origin']['report']}（T={c['origin']['T']}、"
                     f"試験の対数損失 {c['origin']['test_log_loss'][0]}→{c['origin']['test_log_loss'][1]}）、{c['first_eligible_post'][:10]} から比較")
            continue
        if c['origin']['priority'].startswith('KAG:'):
            L.append(f"- 新規登録：{cid}（{c['variant']}）← 三チーム統治 Purple の SHADOW 裁定 {c['origin']['priority'][4:]}"
                     f"（直近7日 {c['origin']['count']}件、承認不要）、{c['first_eligible_post'][:10]} から比較")
            continue
        L.append(f"- 新規登録：{cid}（{c['variant']}）← 反省 {c['origin']['priority']}（{c['origin']['count']}件・"
                 f"{c['origin']['impact_yen']:,}円）、{c['first_eligible_post'][:10]} から比較")
    for cid in res.get('retired') or []:
        L.append(f"- 引退：{cid}（{C[cid].get('reason')}）")
    ev = [k for k, c in C.items() if c.get('status') == 'EVALUATING']
    L.append(f"- 比較中の自動案：{len(ev)}／{MAX_EVALUATING}（{'・'.join(ev) or 'なし'}）")
    return '\n'.join(L) + '\n'
