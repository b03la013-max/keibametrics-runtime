"""ばんえい版 反省会（post-result review）— 全レースの結果が出たら自動で作る。

反省・較正条項 v2.2 / KMS v2.2 の型（地方版 review.py と同じ P0/P1/P2）:
  P0 = 実行・情報の欠陥（締切超過・情報源欠落・FORMAL不成立・直前見直し失敗）→ コードの欠陥は夜間タスクが修正する
  P1 = 役割・接続の欠陥（勝ち馬がW外・2着がP2外・3着がP3外・穴印の未接続）→ 件数を数え、R30でOwnerへ判断材料
  P2 = 較正候補（券種別PFS・1枠外の取りこぼし・Rev1/Rev2）→ 影の計測のみ。単日では数値を変えない（R30/R100＋Owner承認）
原因コード C0 入力 / C1 指数 / C2 役割 / C3 接続 / C4 資金・幅 / C5 実券 / C6 較正。
"""
import json
from pathlib import Path

DECISION_STAGES = (30, 100)


def _j(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return None


def _ret(tk, pay, kind):
    k, src = ('TRIO', tk['trio']) if kind == 'trio' else ('TRIFECTA', tk['exact'])
    P = pay.get(k, {})
    return sum(P.get('-'.join(map(str, x)), 0) for x in src)


def race_review(out, key, r):
    res = _j(out / f'R{key}.result.json')
    eff = '.rev2' if r.get('effective') == 'rev2' else ''
    rec = _j(out / f'R{key}{eff}.json')
    if not res or not rec:
        return None
    ev, tk = rec['evaluation'], rec['tickets']
    rows = {str(x['no']): x for x in ev['rows']}
    w, s, t = (str(n) for n in res['order'][:3])
    marks = {str(k): v for k, v in (ev.get('marks') or {}).items()}

    def info(n, role):
        x = rows.get(n) or {}
        return {'no': int(n), 'mark': marks.get(n, ''), 'pop': x.get('pop'), 'win_rank': x.get('win_rank'),
                'place_rank': x.get('place_rank'), 'hole_rank': x.get('hole_rank'), 'in_role': bool(x.get(role))}
    fin = {'1': info(w, 'role_w'), '2': info(s, 'role_p2'), '3': info(t, 'role_p3')}
    trio_ret, ex_ret = _ret(tk, res['payouts'], 'trio'), _ret(tk, res['payouts'], 'exact')
    trio_st, ex_st = len(tk['trio']) * 100, len(tk['exact']) * 100
    import run as _run
    ffl = _run.first_failure(tk, res['order'])                  # recomputed (11/21 results carried a key-type bug)
    # 原因コード
    if r.get('state') == 'MISSED_DEADLINE':
        cause = 'C0'
    elif ffl == 'ROLE':
        cause = 'C1' if (fin['1']['win_rank'] or 99) > 5 else 'C2'
    elif ffl in ('HEAD-P2-TERMINAL', 'PAIR-P3-TERMINAL'):
        cause = 'C3'
    elif ffl == 'EXACT' or (ffl == 'NONE' and (res['pfs'] or 0) < 100):
        cause = 'C4'
    else:
        cause = None
    P = []
    feeds = set(rec.get('feeds_present') or [])
    for f in ('kintaro', 'sbo', 'keibabook'):
        if f not in feeds:
            P.append({'id': f'P0:FEED_MISSING:{f}', 'level': 'P0', 'what': f'{f} が予想に入っていない'})
    if tk['formality'] != 'FORMAL':
        P.append({'id': 'P0:NOT_FORMAL', 'level': 'P0', 'what': f"区分 {tk['formality']}"})
    c10 = (r.get('check10') or {}).get('decision', '')
    if 'CHECK_FAILED' in c10:
        P.append({'id': 'P0:CHECK10_FAILED', 'level': 'P0', 'what': c10})
    if not fin['1']['in_role']:
        P.append({'id': 'P1:ROLE_W_MISS', 'level': 'P1', 'what': '勝ち馬がW外', 'evidence': fin['1']})
    if not fin['2']['in_role']:
        P.append({'id': 'P1:ROLE_P2_MISS', 'level': 'P1', 'what': '2着馬がP2外', 'evidence': fin['2']})
    if not fin['3']['in_role']:
        P.append({'id': 'P1:ROLE_P3_MISS', 'level': 'P1', 'what': '3着馬がP3外', 'evidence': fin['3']})
    in_tk = {str(n) for c in tk['trio'] for n in c}
    for k, f in fin.items():
        if f['mark'] in ('穴', '注', '☆') and str(f['no']) not in in_tk:
            P.append({'id': 'P1:HOLE_NOT_LINKED', 'level': 'P1', 'what': f'{k}着の穴印馬が券面に無い', 'evidence': f})
    # P2: shadow measures (no money moved)
    near = {k: f[{'1': 'win_rank', '2': 'place_rank', '3': 'place_rank'}[k]] for k, f in fin.items() if not f['in_role']}
    P.append({'id': 'P2:COMPONENT_PFS', 'level': 'P2', 'what': '券種別の収支',
              'evidence': {'trio_stake': trio_st, 'trio_return': trio_ret, 'exact_stake': ex_st, 'exact_return': ex_ret}})
    if near:
        P.append({'id': 'P2:OUTSIDE_ROLE_RANK', 'level': 'P2', 'what': '役割外だった着順馬の順位', 'evidence': near})
    return {'key': key, 'order': res['order'][:3], 'pfs': res['pfs'], 'stake': res['stake'], 'return': res['return'],
            'ffl': ffl, 'cause': cause, 'formality': tk['formality'], 'revision': res.get('effective_revision'),
            'rev_audit': res.get('rev_audit'), 'paper': res.get('paper'), 'finishers': fin,
            'honmei': ev.get('honmei'), 'honmei_finish': next((i + 1 for i, n in enumerate(res['order'][:3])
                                                               if str(n) == str(ev.get('honmei'))), None),
            'trio_hit': trio_ret > 0, 'exact_hit': ex_ret > 0,
            'components': {'trio': [trio_st, trio_ret], 'exact': [ex_st, ex_ret]}, 'proposals': P}


def _pct(a, b):
    return round(100 * a / b, 1) if b else None


def summarize(revs, missed):
    S = sum(x['stake'] for x in revs)
    B = sum(x['return'] for x in revs)
    tr = [sum(x['components']['trio'][i] for x in revs) for i in (0, 1)]
    ex = [sum(x['components']['exact'][i] for x in revs) for i in (0, 1)]
    from collections import Counter
    ffl = Counter(x['ffl'] for x in revs)
    cause = Counter(x['cause'] for x in revs if x['cause'])
    p = Counter(pp['id'].split(':')[0] + ':' + pp['id'].split(':')[1] for x in revs for pp in x['proposals']
                if pp['level'] in ('P0', 'P1'))
    if missed:
        p['P0:MISSED_DEADLINE'] = missed                        # 予想を出せなかったレース（停止・遅延）
    top = sorted((x['return'] for x in revs), reverse=True)
    rev2 = [x for x in revs if x.get('rev_audit')]
    a = {k: sum(x['rev_audit'][k] for x in rev2) for k in ('rev1_stake', 'rev1_return', 'rev2_stake', 'rev2_return')} if rev2 else None
    return {'races': len(revs), 'missed': missed, 'stake': S, 'return': B, 'pfs': _pct(B, S),
            'pfs_without_top1': _pct(B - (top[0] if top else 0), S - (next((x['stake'] for x in revs if x['return'] == top[0]), 0) if top else 0)),
            'trio_hit': sum(x['trio_hit'] for x in revs), 'exact_hit': sum(x['exact_hit'] for x in revs),
            'trio_pfs': _pct(tr[1], tr[0]), 'exact_pfs': _pct(ex[1], ex[0]),
            'honmei_win': sum(x['honmei_finish'] == 1 for x in revs), 'honmei_top3': sum(bool(x['honmei_finish']) for x in revs),
            'winner_in_W': sum(x['finishers']['1']['in_role'] for x in revs),
            'second_in_P2': sum(x['finishers']['2']['in_role'] for x in revs),
            'third_in_P3': sum(x['finishers']['3']['in_role'] for x in revs),
            'ffl': dict(ffl), 'cause': dict(cause), 'p0p1': dict(p), 'rev_audit': a}


def _md(title, s, revs=None):
    L = [f'# {title}', '',
         f"- 精算 {s['races']}R（締切超過 {s['missed']}R）／投資 {s['stake']:,}円・払戻 {s['return']:,}円・PFS {s['pfs']}%"
         f"（最高配当1本を除くと {s['pfs_without_top1']}%）",
         f"- 三連複 的中 {s['trio_hit']}R・PFS {s['trio_pfs']}%／三連単 的中 {s['exact_hit']}R・PFS {s['exact_pfs']}%",
         f"- ◎ 1着 {s['honmei_win']}・3着内 {s['honmei_top3']}／勝ち馬∈W {s['winner_in_W']}・2着∈P2 {s['second_in_P2']}・3着∈P3 {s['third_in_P3']}",
         f"- 最初の断線: {s['ffl']}／原因コード: {s['cause']}",
         f"- P0/P1: {s['p0p1'] or 'なし'}"]
    if s['rev_audit']:
        a = s['rev_audit']
        L.append(f"- 直前見直し（修正版のレース）: Rev1 {a['rev1_return']:,}/{a['rev1_stake']:,}円 → Rev2 {a['rev2_return']:,}/{a['rev2_stake']:,}円")
    if revs:
        L += ['', '| R | 着順 | ◎ | 結果 | PFS | 断線 | 原因 | P0/P1 |', '|---|---|---|---|---|---|---|---|']
        for x in revs:
            hit = '三連単' if x['exact_hit'] else ('三連複' if x['trio_hit'] else '')
            pp = ' '.join(p['id'] for p in x['proposals'] if p['level'] in ('P0', 'P1'))
            L.append(f"| {int(x['key'])} | {'-'.join(map(str, x['order']))} | {x['honmei']} | {hit} | {x['pfs']} | "
                     f"{x['ffl']} | {x['cause'] or ''} | {pp} |")
    L += ['', '数値の変更は単日では行わない（R30/R100の未来レース比較＋Owner承認）。P0のコード欠陥は夜間の自動作業で修正する。']
    return '\n'.join(L) + '\n'


def daily(out, q):
    """Write review/R{key}.review.json for every settled race; when no race is still pending, write the
    daily summary and refresh the period summary under the parent output_ban/ folder."""
    rd = out / 'review'
    rd.mkdir(exist_ok=True)
    revs = []
    for key, r in sorted(q['races'].items()):
        if r.get('state') == 'SETTLED':
            rv = race_review(out, key, r)
            if rv:
                (rd / f'R{key}.review.json').write_text(json.dumps(rv, ensure_ascii=False, indent=1))
                revs.append(rv)
    pending = [k for k, r in q['races'].items() if r.get('state') not in ('SETTLED', 'MISSED_DEADLINE', 'NO_PREDICTION')]
    if pending or not revs:
        return False
    missed = sum(1 for r in q['races'].values() if r.get('state') == 'MISSED_DEADLINE')
    s = summarize(revs, missed)
    (rd / 'daily_summary.json').write_text(json.dumps(s, ensure_ascii=False, indent=1))
    (rd / 'daily_summary.md').write_text(_md(f"ばんえい 反省会 {q['day']}", s, revs))
    period(out.parent)
    return True


def period(root):
    revs, missed, days = [], 0, []
    for d in sorted(p for p in Path(root).iterdir() if (p / 'review' / 'daily_summary.json').exists()):
        days.append(d.name)
        revs += [_j(f) for f in sorted((d / 'review').glob('R*.review.json'))]
        missed += (_j(d / 'review' / 'daily_summary.json') or {}).get('missed', 0)
    revs = [x for x in revs if x]
    if not revs:
        return
    s = summarize(revs, missed)
    n = len(revs)
    stage = max([k for k in DECISION_STAGES if n >= k], default=None)
    s.update(days=days, decision_stage=stage)
    (Path(root) / 'review_period_summary.json').write_text(json.dumps(s, ensure_ascii=False, indent=1))
    head = f"ばんえい 累計反省（{days[0]}〜{days[-1]}・{n}R）"
    note = (f"\n**判断段階 R{stage} に到達**：P1件数・券種別PFS・Rev1/Rev2・仮の基準（derive.CUTS）を Owner に提示する。\n"
            if stage else f"\n次の判断段階まであと {min(k for k in DECISION_STAGES if k > n) - n}R。\n")
    (Path(root) / 'review_period_summary.md').write_text(_md(head, s) + note)
