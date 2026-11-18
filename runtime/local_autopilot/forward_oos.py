"""LOCAL Forward OOS evaluation of the pre-registered candidates (profiles/KM_LOCAL_FORWARD_OOS_PREREG_*).

Counts only races whose official post time is on or after the pre-registration's first_eligible_post, so
known results used to form a hypothesis are never scored as OOS. Evidence only; no Production change.
"""
import json
import random
from datetime import datetime
from pathlib import Path

from runtime.local_autopilot import shadow_measure as sm

REPO = Path(__file__).resolve().parents[2]
PREREG = REPO / 'profiles' / 'KM_LOCAL_FORWARD_OOS_PREREG_20261117_R1.json'


def _post(root, day, key):
    try:
        q = json.loads((Path(root) / day / 'queue.json').read_text())
        return datetime.fromisoformat(q['races'][key]['post_current'])
    except (OSError, ValueError, KeyError):
        return None


def _diff_ci(pairs, n=500, seed=1):
    """pairs = [(inv_a, pay_a, inv_b, pay_b)] -> 95% CI of PFS(a) - PFS(b)."""
    if not pairs:
        return None
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        s = [pairs[rnd.randrange(len(pairs))] for _ in pairs]
        ia, pa, ib, pb = (sum(x[i] for x in s) for i in range(4))
        out.append((100 * pa / ia if ia else 0) - (100 * pb / ib if ib else 0))
    out.sort()
    return [round(out[int(0.025 * n)], 1), round(out[int(0.975 * n)], 1)]


def _stage(n, stages):
    done = [s for s in stages if n >= s]
    return f"{done[-1]}R到達" if done else f"{n}/{stages[0]}R"


def evaluate(root, prereg_path=PREREG):
    pre = json.loads(Path(prereg_path).read_text())
    start = datetime.fromisoformat(pre['first_eligible_post'])
    rows = [x for x in sm.load(root) if (_post(root, x['day'], x['key']) or start.replace(year=1900)) >= start]
    c1, c2a, c2n, c3f, c3h = [], [], [], [], []
    for x in rows:
        res, pred = x['res'], x['pred']
        ns = set(res.get('non_starters') or []) | set(res.get('non_starters_inferred') or [])
        ranking = pred.get('ranking') or []
        rank = [r['no'] for r in ranking if r['no'] not in ns]
        odds = {r['no']: r.get('win') for r in ranking if r['no'] not in ns and r.get('win')}
        if len(rank) < 5 or not odds:
            continue
        fav = min(odds, key=odds.get)
        cand = sm.settle(sm.strategies(rank, fav)['TRIO_1番人気軸_PAPER上位4流し'], res['payouts'], ns)
        c1.append((cand[0], cand[1], res.get('effective_invest') or 0, res.get('payout') or 0, x['key'], x['day']))
        dfv = pred.get('danger_fav') or {}
        if dfv.get('status') == 'OK' and dfv.get('favorite_no') == fav:
            (c2a if dfv['danger_rank'] == 'A' else c2n if dfv['danger_rank'] == 'NONE' else []).append(sm._role(res, fav))
        if rank[0] != fav:
            c3f.append(sm._role(res, fav))
            c3h.append(sm._role(res, rank[0]))
    out = {'profile': pre['profile'] + '-EVAL', 'first_eligible_post': pre['first_eligible_post'],
           'eligible_races': len(c1), 'candidates': {}}
    ia, pa, ib, pb = (sum(x[i] for x in c1) for i in range(4))
    top = max((x[1] for x in c1), default=0)
    out['candidates']['C1-FAV-AXIS-TRIO'] = {
        'races': len(c1), 'stage': _stage(len(c1), pre['stages']),
        'candidate': {'invest': ia, 'payout': pa, 'pfs': round(100 * pa / ia, 1) if ia else None},
        'champion': {'invest': ib, 'payout': pb, 'pfs': round(100 * pb / ib, 1) if ib else None},
        'pfs_diff_95ci': _diff_ci([x[:4] for x in c1]),
        'top1_payout_share': round(100 * top / pa, 1) if pa else None}
    a, n = sm._rolesum(c2a), sm._rolesum(c2n)
    out['candidates']['C2-DANGER-FAV-RANK-A'] = {
        'rank_a': a, 'rank_none': n, 'stage': _stage(len([x for x in c2a + c2n if x]), pre['stages']),
        'win_rate_diff_none_minus_a': round(n['win_rate'] - a['win_rate'], 1) if a and n else None}
    f, h = sm._rolesum(c3f), sm._rolesum(c3h)
    out['candidates']['C3-FAV-AS-W-WHEN-DIVERGED'] = {
        'favorite': f, 'honmei': h, 'stage': _stage(len([x for x in c3f if x]), pre['stages']),
        'win_rate_diff_fav_minus_honmei': round(f['win_rate'] - h['win_rate'], 1) if f and h else None}
    live = []
    for p in sorted(Path(root).glob('20*/review/formal_eval.json')):
        try:
            live += [r['cap'] for r in json.loads(p.read_text())['races'] if r['cap']['mode'] == 'LIVE_R54']
        except (ValueError, KeyError):
            continue
    s = lambda k: sum(x[k] for x in live)
    out['candidates']['C4-LOCAL-CAP-60'] = {
        'races': len(live), 'stage': _stage(len(live), pre['stages']),
        'pfs_full': round(100 * s('payout_full') / s('invest_full'), 1) if live and s('invest_full') else None,
        'pfs_capped': round(100 * s('payout_capped') / s('invest_capped'), 1) if live and s('invest_capped') else None,
        'invest_saved': s('invest_saved') if live else 0,
        'races_with_lost_hits': sum(1 for x in live if x['hits_lost'])}
    pre2 = PREREG.with_name('KM_LOCAL_FORWARD_OOS_PREREG_20261117_R2.json')
    if pre2.exists():
        p2 = json.loads(pre2.read_text())
        start2 = p2['first_eligible_post'][:10]
        small, revs = {}, []
        for p in sorted(Path(root).glob('20*/review/formal_eval.json')):
            if p.parent.parent.name < start2:
                continue
            try:
                rows_ = json.loads(p.read_text())['races']
            except (ValueError, KeyError):
                continue
            for r in rows_:
                for c, v in (r.get('small') or {}).items():
                    small.setdefault(c, []).append((v['invest'], v['payout']))
                small.setdefault('R54_60', []).append((r['cap']['invest_capped'], r['cap']['payout_capped']))
                if r.get('check10_vs_rev1'):
                    revs.append(r['check10_vs_rev1'])
        pf = lambda xs: round(100 * sum(b for _, b in xs) / sum(a for a, _ in xs), 1) if xs and sum(a for a, _ in xs) else None
        n = len(small.get('R54_60', []))
        out['candidates']['C5-SMALL-POINTS'] = {'races': n, 'stage': _stage(n, p2['stages']),
                                                 'pfs': {c: pf(v) for c, v in small.items()}}
        out['candidates']['C6-CHECK10-REVISION'] = {
            'revised_races': len(revs), 'stage': _stage(len(revs), p2['stages']),
            'pfs_rev1': pf([(x['rev1']['invest'], x['rev1']['payout']) for x in revs]),
            'pfs_rev2': pf([(x['rev2']['invest'], x['rev2']['payout']) for x in revs]),
            'winner_rank_better': sum(1 for x in revs if (x['winner_rank_rev2'] or 99) < (x['winner_rank_rev1'] or 99)),
            'winner_rank_worse': sum(1 for x in revs if (x['winner_rank_rev2'] or 99) > (x['winner_rank_rev1'] or 99))}
    pre3 = PREREG.with_name('KM_LOCAL_FORWARD_OOS_PREREG_20261118_R3.json')
    if pre3.exists():
        out['candidates'].update(evaluate_r3(root, json.loads(pre3.read_text())))
    pre4 = PREREG.with_name('KM_LOCAL_FORWARD_OOS_PREREG_20261118_R4.json')
    if pre4.exists():
        from runtime.local_autopilot import aki_audit
        p4 = json.loads(pre4.read_text())
        days = {x['day'] for x in sm.load(root) if x['day'] >= p4['first_eligible_post'][:10]}
        a = aki_audit.audit(root, days) if days else {'races': 0}
        n = a.get('races', 0)
        tf = a.get('trifecta_formation') or {}
        au = a.get('auc') or {}
        out['candidates']['C11-FIXED-2-4-8-VS-AKI-FORM'] = {
            'races': n, 'stage': _stage(n, p4['stages']),
            'pfs_fixed_248': (tf.get('2-4-8') or {}).get('pfs'), 'pfs_aki_chosen': (tf.get('AKI_CHOSEN') or {}).get('pfs')}
        out['candidates']['C12-AKI-VS-MARKET-ROUGHNESS'] = {
            'races': n, 'stage': _stage(n, p4['stages']),
            'auc_aki': (au.get('AKI_total') or {}).get('fav_out_of_top3'),
            'auc_market': (au.get('MARKET_fav_odds') or {}).get('fav_out_of_top3')}
    pre5 = PREREG.with_name('KM_LOCAL_FORWARD_OOS_PREREG_20261118_R5.json')
    if pre5.exists():
        from runtime.local_autopilot import formal_mix
        p5 = json.loads(pre5.read_text())
        ev = formal_mix.evaluate(root, since=datetime.fromisoformat(p5['first_eligible_post']))
        v = ev['variants']
        n = ev['races']
        for cid, name in (('C13-FORMAL-MIX-P2BOX20', 'MIX_P2BOX20'), ('C14-FORMAL-P2BOX20-ONLY', 'P2BOX20_ONLY'),
                          ('C15-FORMAL-MIX-WAXIS-TRIO', 'MIX_WAXIS_TRIO')):
            out['candidates'][cid] = {'races': n, 'stage': _stage(n, p5['stages']), 'candidate': v.get(name), 'champion': v.get('R54_60')}
    pre6 = PREREG.with_name('KM_LOCAL_FORWARD_OOS_PREREG_20261119_R6.json')
    if pre6.exists():
        from runtime.local_autopilot import role_shadow
        p6 = json.loads(pre6.read_text())
        start6 = datetime.fromisoformat(p6['first_eligible_post'])
        rs = role_shadow.evaluate(root, since_day=p6['first_eligible_post'][:10])
        rows = [r for r in rs['rows'] if (_post(root, r['day'], r['race']) or start6.replace(year=1900)) >= start6]
        ev = role_shadow.summarize(rows)
        for cid, k in (('C16-W-INDEX-CONSENSUS', 'C16'), ('C17-P2-ZAI-PLACE', 'C17'), ('C18-W-PLUS-FAVORITE', 'C18'),
                       ('C19-W-PLUS-TOP2-POP', 'C19'), ('C20-P2-PLUS-TOP3-POP', 'C20')):
            out['candidates'][cid] = dict(ev[k], stage=_stage(len(rows), p6['stages']))
    out['production_change'] = 'NONE (Owner approval required for any promotion)'
    return out


def evaluate_r3(root, p3):
    import math
    start = datetime.fromisoformat(p3['first_eligible_post'])
    fv = p3['frozen_values']
    kb_buy, kb_ctl, g_hi, g_lo, ll = [], [], [], [], {'market': [], 'model': [], 'combined': []}
    hv = {'plain': [], 'discount': []}
    for x in sm.load(root):
        if (_post(root, x['day'], x['key']) or start.replace(year=1900)) < start:
            continue
        res, pred = x['res'], x['pred']
        ns = set(res.get('non_starters') or []) | set(res.get('non_starters_inferred') or [])
        ranking = pred.get('ranking') or []
        kg = pred.get('kametani') or {}
        if not str(kg.get('profile', '')).startswith('KM-LOCAL-KAMETANI-PEDIGREE-EVIDENCE-v2'):
            kg = {}                  # v1 (split at '／', OR) mis-classified scenes: excluded from C7 (amendment A1)
        for no, ev in (kg.get('by_horse') or {}).items():
            if int(no) in ns:
                continue
            if ev['buy_match'] and not ev['caution_match']:
                kb_buy.append(sm._role(res, int(no)))
            elif not ev['buy_match'] and not ev['caution_match']:
                kb_ctl.append(sm._role(res, int(no)))
        odds = {r['no']: r.get('win') for r in ranking if r['no'] not in ns and r.get('win')}
        if len(odds) >= 2:
            o = sorted(odds.values())
            fav = min(odds, key=odds.get)
            (g_hi if o[1] / o[0] >= fv['gap12_threshold'] else g_lo).append(sm._role(res, fav))
        pq = sm._probs(ranking, ns)
        w = int(res['order'][0])
        if pq and w in pq[0]:
            c = sm._combine(pq[0], pq[1], fv['benter_weights_model_a'], fv['benter_weights_market_b'])
            for k, pr in (('market', pq[0]), ('model', pq[1]), ('combined', c)):
                ll[k].append(-math.log(pr[w]))
            order = [int(v) for v in res['order']]
            a = sm._harville_ll(pq[1], order, 1.0, 1.0)
            b = sm._harville_ll(pq[1], order, *fv['harville_discount'])
            if a is not None and b is not None:
                hv['plain'].append(-a)
                hv['discount'].append(-b)
    avg = lambda v: round(sum(v) / len(v), 4) if v else None
    b, c = sm._rolesum(kb_buy), sm._rolesum(kb_ctl)
    hi, lo = sm._rolesum(g_hi), sm._rolesum(g_lo)
    return {
        'C7-KAMETANI-BUY-MATCH': {'buy_match': b, 'control': c, 'stage': _stage(len([v for v in kb_buy if v]), p3['stages']),
                                  'top3_diff': round(b['top3_rate'] - c['top3_rate'], 1) if b and c else None},
        'C8-ODDS-GAP-FAVORITE': {'gap12_hi': hi, 'gap12_lo': lo, 'stage': _stage(len([v for v in g_hi + g_lo if v]), p3['stages']),
                                 'fav_win_diff': round(hi['win_rate'] - lo['win_rate'], 1) if hi and lo else None},
        'C9-BENTER-COMBINATION': {'races': len(ll['market']), 'stage': _stage(len(ll['market']), p3['stages']),
                                  **{f'logloss_{k}': avg(v) for k, v in ll.items()}},
        'C10-HARVILLE-DISCOUNT': {'races': len(hv['plain']), 'stage': _stage(len(hv['plain']), p3['stages']),
                                  'logloss_plain': avg(hv['plain']), 'logloss_discount': avg(hv['discount'])}}


def md(o):
    c = o['candidates']
    c1, c2, c3, c4 = (c[k] for k in ('C1-FAV-AXIS-TRIO', 'C2-DANGER-FAV-RANK-A', 'C3-FAV-AS-W-WHEN-DIVERGED', 'C4-LOCAL-CAP-60'))
    r = lambda v, k: (v or {}).get(k)
    return '\n'.join([
        f"# 地方版 Forward OOS（事前登録 {o['first_eligible_post'][:16]} 以降のRaceのみ）", '',
        f"- C1 3連複1番人気軸 vs PAPER実買い目：{c1['stage']}／候補 {c1['candidate']['pfs']}% 対 現行 {c1['champion']['pfs']}%"
        f"／差の95%CI {c1['pfs_diff_95ci']}／最大1R依存 {c1['top1_payout_share']}%",
        f"- C2 危険度A の1番人気：{c2['stage']}／勝率 A {r(c2['rank_a'], 'win_rate')}%（{r(c2['rank_a'], 'races')}R）"
        f" 対 NONE {r(c2['rank_none'], 'win_rate')}%（{r(c2['rank_none'], 'races')}R）",
        f"- C3 ◎≠1番人気：{c3['stage']}／勝率 1番人気 {r(c3['favorite'], 'win_rate')}% 対 ◎ {r(c3['honmei'], 'win_rate')}%",
        f"- C4 60点上限（実運用）：{c4['stage']}／全MEC {c4['pfs_full']}% 対 上限後 {c4['pfs_capped']}%"
        f"／投資削減 {c4['invest_saved']:,}円／的中を失ったRace {c4['races_with_lost_hits']}",
        *([f"- C5 少点数：{c.get('C5-SMALL-POINTS', {}).get('stage')}／回収率 {c.get('C5-SMALL-POINTS', {}).get('pfs')}"] if 'C5-SMALL-POINTS' in c else []),
        *([f"- C6 10分前改訂：{c['C6-CHECK10-REVISION']['stage']}／Rev1 {c['C6-CHECK10-REVISION']['pfs_rev1']}% 対 Rev2 "
           f"{c['C6-CHECK10-REVISION']['pfs_rev2']}%／1着順位 改善{c['C6-CHECK10-REVISION']['winner_rank_better']}・悪化"
           f"{c['C6-CHECK10-REVISION']['winner_rank_worse']}"] if 'C6-CHECK10-REVISION' in c else []),
        *(_md_r3(c) if 'C7-KAMETANI-BUY-MATCH' in c else []),
        *([f"- C11 3連単 固定2-4-8 対 AKI選択：{c['C11-FIXED-2-4-8-VS-AKI-FORM']['stage']}／回収率 "
           f"{c['C11-FIXED-2-4-8-VS-AKI-FORM']['pfs_fixed_248']}% 対 {c['C11-FIXED-2-4-8-VS-AKI-FORM']['pfs_aki_chosen']}%",
           f"- C12 荒れ予測 AKI 対 1番人気オッズ（AUC）：{c['C12-AKI-VS-MARKET-ROUGHNESS']['stage']}／"
           f"{c['C12-AKI-VS-MARKET-ROUGHNESS']['auc_aki']} 対 {c['C12-AKI-VS-MARKET-ROUGHNESS']['auc_market']}"]
          if 'C11-FIXED-2-4-8-VS-AKI-FORM' in c else []),
        *([f"- C18 W＋1番人気：{c['C18-W-PLUS-FAVORITE']['stage']}／勝ち馬捕捉 {c['C18-W-PLUS-FAVORITE'].get('win_in_W_cand')}% 対 "
           f"{c['C18-W-PLUS-FAVORITE'].get('win_in_W')}%／同点数馬単 {c['C18-W-PLUS-FAVORITE'].get('exacta_pfs_cand')}% 対 "
           f"{c['C18-W-PLUS-FAVORITE'].get('exacta_pfs_signed')}%",
           f"- C19 W＋人気上位2：{c['C19-W-PLUS-TOP2-POP']['stage']}／勝ち馬捕捉 {c['C19-W-PLUS-TOP2-POP'].get('win_in_W_cand')}%"
           f"／同点数馬単 {c['C19-W-PLUS-TOP2-POP'].get('exacta_pfs_cand')}%",
           f"- C20 P2＋人気上位3：{c['C20-P2-PLUS-TOP3-POP']['stage']}／2着捕捉（勝ち馬W内）"
           f"{c['C20-P2-PLUS-TOP3-POP'].get('second_in_P2_cand_given_W')}% 対 {c['C20-P2-PLUS-TOP3-POP'].get('second_in_P2_given_W')}%"]
          if 'C18-W-PLUS-FAVORITE' in c else []),
        *([f"- {cid} 正式役割の三連複経路：{c[cid]['stage']}／回収率 {(c[cid]['candidate'] or {}).get('pfs')}% 対 正式60点 "
           f"{(c[cid]['champion'] or {}).get('pfs')}%／的中R {(c[cid]['candidate'] or {}).get('hit_races')} 対 "
           f"{(c[cid]['champion'] or {}).get('hit_races')}" for cid in ('C13-FORMAL-MIX-P2BOX20', 'C14-FORMAL-P2BOX20-ONLY',
                                                              'C15-FORMAL-MIX-WAXIS-TRIO') if cid in c]),
        '', f"<sub>{o['production_change']}</sub>", ''])


def _md_r3(c):
    g = lambda d, k: (d or {}).get(k)
    c7, c8, c9, c10 = (c[k] for k in ('C7-KAMETANI-BUY-MATCH', 'C8-ODDS-GAP-FAVORITE', 'C9-BENTER-COMBINATION', 'C10-HARVILLE-DISCOUNT'))
    return [f"- C7 亀谷 買い条件該当：{c7['stage']}／3着内率 該当 {g(c7['buy_match'], 'top3_rate')}%（{g(c7['buy_match'], 'races')}頭）"
            f" 対 非該当 {g(c7['control'], 'top3_rate')}%／複勝回収 {g(c7['buy_match'], 'place_pfs')}%",
            f"- C8 オッズ断層（2番人気/1番人気 ≥ 2.5）：{c8['stage']}／1番人気勝率 断層あり {g(c8['gap12_hi'], 'win_rate')}%"
            f" 対 なし {g(c8['gap12_lo'], 'win_rate')}%",
            f"- C9 Benter結合：{c9['stage']}／勝ち馬対数損失 市場 {c9['logloss_market']}・モデル {c9['logloss_model']}・結合 {c9['logloss_combined']}",
            f"- C10 Harville割引：{c10['stage']}／2・3着対数損失 通常 {c10['logloss_plain']} 対 割引 {c10['logloss_discount']}"]


def write(root):
    o = evaluate(root)
    (Path(root) / 'forward_oos_local.json').write_text(json.dumps(o, ensure_ascii=False, indent=1) + '\n')
    (Path(root) / 'forward_oos_local.md').write_text(md(o))
    return o
