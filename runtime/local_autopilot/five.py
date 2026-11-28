"""KDP / KSP / KAP weekly measurements for LOCAL (Owner 2026-11-26 22:03 「永続的に実施してください」, ChatGPT
KDP・KSP・KAP v1.0, LOCAL part). Measurement only: rankings, roles, MEC, the 60-point cap, the purchase policy
(recommendation only) and the candidates are untouched. What already exists is reused, not rebuilt:
  KDP-04/05 conditional roles and conversion: role_shadow, nonbuy_trace (review), formal_eval (cap losses);
  KSP hit-but-loss / ex-top / redundancy: robustness; KAP-01 counterfactuals: formal_mix variants, kiep, krs_research;
  KAP-04 knowledge -> execution: drive_reading ledger + gap_tracker (private); KAP-05 lifecycle: auto_candidates;
  KAP-06 independent audit: everything is in the public data branch for ChatGPT to recompute.
New here:
  KSP-01/02  per variant, in post order: PFS, PFS without the top 1 / top 3 payouts, net, maximum drawdown and its
             length, longest losing streak, hit-but-loss share, daily CVaR(10 %), and a day-block bootstrap of the
             next 300 races from a virtual 300,000 yen bank (50 races of 60 points) (share of paths that reach 0, median end) — virtual only.
  KDP-01     does uncertainty show up as error? For three pre-race proxies fixed here (top-2 gap of the formal
             numerical overall, KRS robustness grade of the formal top horse, share of runners with a neutral SPD),
             the formal ranking's winner rank / top-3 AUC by tercile (low / mid / high uncertainty).
  KAP-03     drift: formal-ranking top-3 AUC per ISO week (all venues and per venue with >= 12 races); a week more
             than 2 SE below the long-run mean is flagged (a flag starts research, never a coefficient change).
"""
from __future__ import annotations

import json
import random
import statistics as st
from datetime import date
from pathlib import Path

PROFILE = 'KM-LOCAL-KDP-KSP-KAP-WEEKLY-v1.0-20261126'
BANK = 300_000   # = 50 races at the full 60 points (6,000 yen)
HORIZON = 300
N_BOOT = 1000
SEED = 20261126


def _load(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return None


# ------------------------------------------------------------------ KSP
def risk(seq):
    """seq: [(day, invest, payout)] in post order."""
    inv = sum(x[1] for x in seq)
    pays = sorted((x[2] for x in seq), reverse=True)
    pay = sum(pays)
    bal = peak = 0
    mdd = cur_len = mdd_len = 0
    streak = best = 0
    hbl = hits = 0
    for _, i, p in seq:
        bal += p - i
        if bal > peak:
            peak, cur_len = bal, 0
        else:
            cur_len += 1
        if peak - bal > mdd:
            mdd = peak - bal
        mdd_len = max(mdd_len, cur_len)
        streak = streak + 1 if p == 0 else 0
        best = max(best, streak)
        if p > 0:
            hits += 1
            hbl += p < i
    days = {}
    for d, i, p in seq:
        days[d] = days.get(d, 0) + p - i
    dl = sorted(days.values())
    k = max(1, len(dl) // 10)
    pct = lambda x: round(100 * x / inv, 2) if inv else None
    return {'races': len(seq), 'invest': inv, 'payout': pay, 'net': pay - inv, 'pfs': pct(pay),
            'pfs_ex_top1': pct(pay - sum(pays[:1])), 'pfs_ex_top3': pct(pay - sum(pays[:3])),
            'max_drawdown': mdd, 'longest_underwater_races': mdd_len, 'longest_losing_streak': best,
            'hit_races': hits, 'hit_but_loss_share': round(hbl / hits, 3) if hits else None,
            'daily_cvar10': round(sum(dl[:k]) / k) if dl else None, 'days': len(dl)}


def ruin(seq, bank=BANK, horizon=HORIZON, n=N_BOOT, seed=SEED):
    """Day-block bootstrap: whole race days are resampled (races of one day stay together)."""
    byday = {}
    for d, i, p in seq:
        byday.setdefault(d, []).append(p - i)
    blocks = list(byday.values())
    if not blocks:
        return None
    rng = random.Random(seed)
    ruined, ends = 0, []
    for _ in range(n):
        b, cnt, dead = bank, 0, False
        while cnt < horizon:
            for x in rng.choice(blocks):
                b += x
                cnt += 1
                if b <= 0:
                    dead = True
                    break
                if cnt >= horizon:
                    break
            if dead:
                break
        ruined += dead
        ends.append(max(b, 0))
    return {'bank': bank, 'horizon_races': horizon, 'paths': n, 'ruin_share': round(ruined / n, 3),
            'median_end': round(st.median(ends)), 'p10_end': round(sorted(ends)[n // 10])}


def ksp(root):
    from runtime.local_autopilot import auto_promote, formal_mix
    rows = formal_mix.races(root)
    q = {}
    for r in rows:
        qq = _load(Path(root) / r['day'] / 'queue.json') or {}
        q[(r['day'], r['key'])] = ((qq.get('races') or {}).get(r['key']) or {}).get('post_current') or ''
    rows.sort(key=lambda r: (r['day'], q.get((r['day'], r['key'])), r['key']))
    act = ((auto_promote.load_state(root).get('active')) or {}).get('variant')
    names = ['R54_60'] + ([act] if act and act != 'R54_60' else [])
    names += sorted({k for r in rows for k in r if k not in ('day', 'key') and k not in names and isinstance(r[k], tuple)})
    out = {}
    for nm in names:
        seq = [(r['day'], r[nm][0], r[nm][1]) for r in rows if nm in r and isinstance(r[nm], tuple)]
        if len(seq) < 30:
            continue
        out[nm] = dict(risk(seq), ruin=ruin(seq))
    return {'active': act, 'variants': out}


# ------------------------------------------------------------------ KDP-01
def _auc_t3(rank, order):
    top = set(order[:3])
    pos = {h: i for i, h in enumerate(rank)}
    P = [pos[h] for h in rank if h in top]
    N = [pos[h] for h in rank if h not in top]
    if not P or not N:
        return None
    return sum(1.0 if p < n else 0.5 if p == n else 0.0 for p in P for n in N) / (len(P) * len(N))


def _race_rows(root):
    out = []
    for sp in sorted(Path(root).glob('20??-??-??/formal/*.summary.json')):
        key, fd = sp.name.split('.')[0], sp.parent
        dd = fd.parent
        res = _load(dd / f'{key}.result.json')
        sm = _load(sp)
        if not res or not sm or not res.get('order') or sm.get('no_bet'):
            continue
        gone = set(res.get('non_starters') or [])
        order = [int(x) for x in res['order'] if int(x) not in gone]
        rank = [int(x) for x in sm.get('ranking') or [] if int(x) not in gone]
        if len(order) < 5 or not rank:
            continue
        num = _load(fd / f'{key}.numerical_prediction.json') or {}
        ov = sorted((float(x['overall']) for x in num.get('runner_scores') or []), reverse=True)
        ku = _load(fd / f'{key}.krs_prediction_utility.json') or {}
        rob = {int(x['horse_no']): x.get('Robustness') for x in ku.get('summary') or []}
        fu = _load(fd / f'{key}.full29.json') or {}
        spd = [(x.get('indices') or {}) for x in fu.get('runners') or []]
        neutral = (sum(1 for v in spd if abs(float(v.get('EVI/CEV', 52)) - 52) < 1e-6) / len(spd)) if spd else None
        out.append({'day': dd.name, 'venue': key.split('_')[0], 'key': key, 'order': order, 'rank': rank,
                    'gap': (ov[0] - ov[1]) if len(ov) > 1 else None, 'robust': rob.get(rank[0]), 'neutral': neutral})
    return out


def kdp(rows):
    def terc(vals, high_is_uncertain):
        xs = sorted(v for v in vals if v is not None)
        if len(xs) < 30:
            return None
        a, b = xs[len(xs) // 3], xs[2 * len(xs) // 3]
        return lambda v: None if v is None else (('LOW', 'MID', 'HIGH') if high_is_uncertain else ('HIGH', 'MID', 'LOW'))[
            0 if v <= a else 1 if v <= b else 2]
    grade = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    proxies = {'top2_gap': ([r['gap'] for r in rows], False, lambda r: r['gap']),
               'krs_robustness': ([grade.get(r['robust']) for r in rows], True, lambda r: grade.get(r['robust'])),
               'neutral_share': ([r['neutral'] for r in rows], True, lambda r: r['neutral'])}
    out = {}
    for nm, (vals, hi, get) in proxies.items():
        f = terc(vals, hi)
        if not f:
            continue
        g = {}
        for r in rows:
            band = f(get(r))
            if band:
                g.setdefault(band, []).append(r)
        out[nm] = {b: {'races': len(x), 'winner_top1': round(sum(r['rank'][0] == r['order'][0] for r in x) / len(x), 3),
                       'winner_in_top3': round(sum(r['order'][0] in r['rank'][:3] for r in x) / len(x), 3),
                       'auc_top3': round(st.mean([a for a in (_auc_t3(r['rank'], r['order']) for r in x) if a is not None]), 3)}
                   for b, x in sorted(g.items())}
        lo, hi_ = out[nm].get('LOW'), out[nm].get('HIGH')
        out[nm]['works'] = bool(lo and hi_ and lo['auc_top3'] > hi_['auc_top3'] and lo['winner_in_top3'] > hi_['winner_in_top3'])
    return out


# ------------------------------------------------------------------ KAP-03
def drift(rows):
    def weekly(xs):
        wk = {}
        for r in xs:
            y, w, _ = date.fromisoformat(r['day']).isocalendar()
            a = _auc_t3(r['rank'], r['order'])
            if a is not None:
                wk.setdefault(f'{y}-W{w:02d}', []).append(a)
        allv = [a for v in wk.values() for a in v]
        if len(allv) < 20:
            return None
        m, sd = st.mean(allv), st.pstdev(allv)
        res = {}
        for k, v in sorted(wk.items()):
            se = sd / len(v) ** 0.5
            res[k] = {'races': len(v), 'auc_top3': round(st.mean(v), 3), 'flag': st.mean(v) < m - 2 * se and len(v) >= 12}
        return {'long_run': round(m, 3), 'weeks': res}
    out = {'ALL': weekly(rows)}
    for v in sorted({r['venue'] for r in rows}):
        x = [r for r in rows if r['venue'] == v]
        if len(x) >= 24:
            out[v] = weekly(x)
    return {k: v for k, v in out.items() if v}


def evaluate(root):
    rows = _race_rows(root)
    rep = {'profile': PROFILE, 'races': len(rows), 'days': sorted({r['day'] for r in rows})}
    try:
        rep['ksp'] = ksp(root)
    except Exception as exc:
        rep['ksp_error'] = f'{type(exc).__name__}:{str(exc)[:120]}'
    rep['kdp_uncertainty'] = kdp(rows)
    rep['kap_drift'] = drift(rows)
    try:   # KSP-03 budget-changing research series (Owner 2026-11-26 22:31)
        from runtime.local_autopilot import budget_series
        rep['budget_series'] = budget_series.report(root)
    except Exception as exc:
        rep['budget_series_error'] = f'{type(exc).__name__}:{str(exc)[:120]}'
    try:   # SCTP 三連複保護層 (Owner 2026-11-28)
        from runtime.local_autopilot import sctp
        rep['sctp'] = sctp.report(root)
    except Exception as exc:
        rep['sctp_error'] = f'{type(exc).__name__}:{str(exc)[:120]}'
    return rep


def md(rep):
    from runtime.local_autopilot.index_health import VENUE_JA
    if not rep.get('races'):
        return '### KDP・KSP・KAP 週次測定\n\n対象レースなし\n'
    L = [f"### KDP・KSP・KAP 週次測定（{rep['days'][0]}〜{rep['days'][-1]}・確定{rep['races']}R）", '',
         '測定のみ。順位・役割・MEC・60点上限・購入方針（推薦のみ・実購入なし）は変更していません。', '',
         '**KSP 生存（仮想精算・1点100円）**', '',
         '| 方式 | R | PFS | 最大払戻除く | 上位3除く | 最大ドローダウン | 最長連敗 | 的中赤字率 | 仮想30万円（50R分）・次300Rで0円到達の割合 |',
         '|---|---|---|---|---|---|---|---|---|']
    k = (rep.get('ksp') or {}).get('variants') or {}
    act = (rep.get('ksp') or {}).get('active')
    for nm, x in list(k.items())[:12]:
        ru = x.get('ruin') or {}
        L.append(f"| {nm}{'（配信中）' if nm == act else ''} | {x['races']} | {x['pfs']}% | {x['pfs_ex_top1']}% | {x['pfs_ex_top3']}% | "
                 f"{x['max_drawdown']:,}円 | {x['longest_losing_streak']}R | {x['hit_but_loss_share']} | {ru.get('ruin_share')} |")
    L += ['', '**KDP 不確実性が誤差に表れるか（不確実性 低→高、正式順位）**', '']
    nmj = {'top2_gap': '1位と2位の総合点差（小さいほど不確実）', 'krs_robustness': 'KRS の頑健度（D ほど不確実）',
           'neutral_share': '展開情報が中立のままの馬の割合'}
    for nm, x in (rep.get('kdp_uncertainty') or {}).items():
        parts = [f"{b} 勝ち馬3位内 {x[b]['winner_in_top3']}・AUC {x[b]['auc_top3']}（{x[b]['races']}R）" for b in ('LOW', 'MID', 'HIGH') if b in x]
        L.append(f"- {nmj[nm]}：{'／'.join(parts)} → {'**誤差の大きいレースを見分けられている**' if x['works'] else '見分けられていない'}")
    L += ['', '**KAP 環境変化（週ごとの正式順位 3着内AUC）**', '']
    for v, x in (rep.get('kap_drift') or {}).items():
        wk = x['weeks']
        flags = [w for w, y in wk.items() if y['flag']]
        L.append(f"- {'全場' if v == 'ALL' else VENUE_JA.get(v, v)}：長期 {x['long_run']}／" +
                 '、'.join(f"{w} {y['auc_top3']}（{y['races']}R）" for w, y in wk.items()) +
                 (f" → **低下の兆候 {'・'.join(flags)}**（研究のきっかけ。係数は変えない）" if flags else ''))
    if rep.get('budget_series'):
        from runtime.local_autopilot import budget_series
        L.append(budget_series.md(rep['budget_series']))
    if rep.get('sctp'):
        from runtime.local_autopilot import sctp
        L.append(sctp.md(rep['sctp']))
    return '\n'.join(L) + '\n'


def weekly(root, today):
    d = Path(root) / 'five'
    d.mkdir(exist_ok=True)
    wk = date.fromisoformat(today).isocalendar()[:2]
    for f in d.glob('20??-??-??.json'):
        if date.fromisoformat(f.stem).isocalendar()[:2] == wk:
            return None
    rep = evaluate(root)
    rep['day'] = today
    (d / f'{today}.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1) + '\n')
    text = md(rep)
    (d / f'{today}.md').write_text(text)
    return text
