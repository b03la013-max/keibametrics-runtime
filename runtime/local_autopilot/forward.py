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


def observation(root):
    """Per venue: share of runners whose official-29 cell was CALCULATED (not
    rule-neutral) for each index, from the shadow files (candidate arithmetic)."""
    out = {}
    for day in sorted(p for p in Path(root).iterdir() if p.is_dir() and p.name[:2] == '20'):
        for f in day.glob('*.shadow29.json'):
            try:
                s = json.loads(f.read_text())
            except ValueError:
                continue
            if s.get('error') or not s.get('runner_count'):
                continue
            v = out.setdefault(f.name[:3], {'runners': 0, 'neutral': Counter()})
            v['runners'] += s['runner_count']
            v['neutral'].update(s.get('non_calculated_by_index') or {})
    idx = sorted({k for v in out.values() for k in v['neutral']})
    return {venue: {'runners': v['runners'],
                    'observed_rate': {k: round(1 - v['neutral'].get(k, 0) / v['runners'], 3) for k in idx}}
            for venue, v in sorted(out.items())}, idx


def _owner_gate():
    """Owner decision on LOCAL numerical consumption, read from the family authority files."""
    repo = Path(__file__).resolve().parents[2] / 'profiles'
    best = None
    for p in sorted(repo.glob('KM_FAMILY_CURRENT_AUTHORITY_*.json')):
        try:
            d = json.loads(p.read_text())
        except ValueError:
            continue
        b = ((d.get('family_scoped_authority') or {}).get('LOCAL') or {}).get('numerical_consumption_boundary') or {}
        if b.get('krs_input_authority') is True:
            best = (d.get('manifest_id'), d.get('effective_at'))
    if best:
        return {'owner_review': 'OWNER_APPROVED (2026-11-16)', 'authorized': True, 'authority': best[0], 'effective_at': best[1]}
    return {'owner_review': 'NOT_PERFORMED', 'authorized': False}


def formal_oos(root):
    """Formal Production ledger (unknown-future, pre-start Signed FINAL only).

    Two measurements per settled formal race:
      * formal: the Signed FINAL (Static Owner roles + MEC tickets) settlement and
        whether the Runtime-signed RESULT receipt was verified;
      * numerical_shadow: the Production Full29 materialization (not consumed, R52)
        ranked by F3S-L, scored against the official order -- the OOS evidence the
        R52 boundary requires before any numerical->prediction/KRS/ticket/capital
        consumption promotion (which additionally needs human Owner review)."""
    rows = []
    for day, key, r in _races(root):
        f = r.get('formal') or {}
        if f.get('status') != 'SIGNED_FINAL':
            continue
        row = {'day': day.name, 'race': key, 'final_receipt': f.get('final_receipt_sha256', '')[:16],
               'settled': False}
        fs, st = r.get('formal_settlement') or {}, r.get('settlement') or {}
        if fs and st.get('order'):
            order = st['order']
            row.update(settled=True, eff=fs.get('effective_invest'), pay=fs.get('payout'),
                       result_receipt_verified=bool(fs.get('result_receipt_verified')),
                       first_material_failure=fs.get('first_material_failure'))
            try:
                sm = json.loads((day / 'formal' / f'{key}.summary.json').read_text())
                rank = [int(x) for x in sm.get('ranking') or []]
                row['formal_win'] = int(bool(rank) and rank[0] == order[0])
                row['formal_top3_capture'] = len(set(rank[:3]) & set(order[:3]))
            except (OSError, ValueError):
                pass
            try:
                fz = json.loads((day / 'formal' / f'{key}.full29.json').read_text())
                n29 = [x['no'] for x in sorted(fz['runners'], key=lambda x: -(x['indices'].get('F3S-L') or 0))]
                row['num_win'] = int(bool(n29) and n29[0] == order[0])
                row['num_top3_capture'] = len(set(n29[:3]) & set(order[:3]))
                row['full29_classification'] = fz.get('classification')
            except (OSError, ValueError, KeyError):
                pass
        rows.append(row)
    done = [x for x in rows if x['settled']]
    eff = sum(x.get('eff') or 0 for x in done)
    pay = sum(x.get('pay') or 0 for x in done)
    prod = [x for x in done if x.get('full29_classification') == 'FULL29_PRODUCTION_NUMERICAL_MATERIALIZATION']
    return {'classification': 'LOCAL_FORMAL_PRODUCTION_FORWARD_OOS (Signed FINAL, recommendation only, no purchase)',
            'signed_final_races': len(rows), 'settled_races': len(done),
            'result_receipt_verified': sum(1 for x in done if x.get('result_receipt_verified')),
            'effective_invest': eff, 'payout': pay, 'pfs': round(100 * pay / eff, 1) if eff else None,
            'formal_win_hits': sum(x.get('formal_win', 0) for x in done),
            'numerical_shadow': {'races': len(prod), 'win_hits': sum(x.get('num_win', 0) for x in prod),
                                 'top3_capture_sum': sum(x.get('num_top3_capture', 0) for x in prod),
                                 'formal_top3_capture_sum': sum(x.get('formal_top3_capture', 0) for x in prod)},
            'consumption_promotion_gate': {
                'rule': 'R52: numerical consumption requires separate genuine unknown-future OOS + human (Owner) review',
                'min_settled_production_numerical_races': 100,
                'threshold_basis': 'PROPOSED (較正・検証運用条項 第12条: 100件以上・目的事象20件以上・訓練/検証分離); Owner decides',
                'evidence_ready': len(prod) >= 100, **_owner_gate()},
            'races': rows}


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
    obs, idx = observation(root)
    s['observation'] = obs
    (Path(root) / 'forward_summary.json').write_text(json.dumps(s, ensure_ascii=False, indent=1) + '\n')
    L += ['', '## 全29指数の観測率（場別・CALCULATEDの比率。それ以外は全頭が規則中立）', '',
          '| 場 | 頭数 | ' + ' | '.join(idx) + ' |', '|---|---|' + '---|' * len(idx)]
    for v, o in obs.items():
        L.append(f"| {v} | {o['runners']} | " + ' | '.join(f"{o['observed_rate'][k]:.0%}" for k in idx) + ' |')
    fo = formal_oos(root)
    s['formal'] = fo
    (Path(root) / 'forward_summary.json').write_text(json.dumps(s, ensure_ascii=False, indent=1) + '\n')
    ns, g = fo['numerical_shadow'], fo['consumption_promotion_gate']
    L += ['', '## 正式Production（署名FINAL・未知未来・推薦試算・実購入なし）', '',
          f"- 署名FINAL {fo['signed_final_races']}R／精算 {fo['settled_races']}R／署名RESULT検証 {fo['result_receipt_verified']}R",
          f"- 実効投資 {fo['effective_invest']:,}円／払戻 {fo['payout']:,}円／PFS {fo['pfs']}%／正式◎1着 {fo['formal_win_hits']}",
          f"- 正式29指数（Production計算器・未消費）のF3S-L順：{ns['races']}R中 1着的中 {ns['win_hits']}／上位3頭の3着内捕捉 {ns['top3_capture_sum']}（正式Static {ns['formal_top3_capture_sum']}）",
          f"- 数値Consumer昇格ゲート：精算 {ns['races']}/{g['min_settled_production_numerical_races']}R・Ownerレビュー {g['owner_review']}・承認 {g['authorized']}",
          '', '| 日付 | Race | FINAL | 精算 | 投資 | 払戻 | RESULT署名 | 第一失敗 |', '|---|---|---|---|---|---|---|---|']
    for x in fo['races']:
        L.append(f"| {x['day']} | {x['race']} | `{x['final_receipt']}` | {'済' if x['settled'] else '待'} | "
                 f"{x.get('eff', '–')} | {x.get('pay', '–')} | {x.get('result_receipt_verified', '–')} | {x.get('first_material_failure', '–')} |")
    (Path(root) / 'forward_summary.md').write_text('\n'.join(L) + '\n')
    return s
