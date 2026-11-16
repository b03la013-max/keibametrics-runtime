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
    out['production_change'] = 'NONE (Owner approval required for any promotion)'
    return out


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
        '', f"<sub>{o['production_change']}</sub>", ''])


def write(root):
    o = evaluate(root)
    (Path(root) / 'forward_oos_local.json').write_text(json.dumps(o, ensure_ascii=False, indent=1) + '\n')
    (Path(root) / 'forward_oos_local.md').write_text(md(o))
    return o
