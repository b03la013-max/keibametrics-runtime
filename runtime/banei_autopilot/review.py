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


def cross_pair_third(exact, order):
    """Cross-Pair Compensation（v3.7-BAN Rev.2 起案根拠、帯広 2026-09-05 6R・7R）: 1-2着の並び（頭×P2）は三連単で
    買っていたのに、3着馬はその並びの3着に無く、別の並びの3着にだけ買っていた（別の並びの3着を補償とみなす誤り）。
    証拠のみ（券面・点数には影響しない）。"""
    if not exact or not order or len(order) < 3:
        return None
    w, s, t = (str(x) for x in order[:3])
    ex = [tuple(str(n) for n in x) for x in exact if len(x) == 3]
    pair_thirds = {x[2] for x in ex if x[0] == w and x[1] == s}
    other_thirds = {x[2] for x in ex if not (x[0] == w and x[1] == s)}
    return {'pair_bought': bool(pair_thirds), 'third_under_pair': t in pair_thirds,
            'third_elsewhere': t in other_thirds,
            'cross_pair_third': bool(pair_thirds) and t not in pair_thirds and t in other_thirds}


def role_set_coverage(rows, order):
    """役割の被覆と集合の大きさを一緒に保存する（地方 根幹思想 Rev1 §11 Coverage≠Discrimination・
    Scientific Reset §6）。無作為基準＝集合の頭数÷出走頭数（その頭数を無作為に選んだときの的中確率）。
    較正済みの conformal 集合ではない。証拠のみ（券面・点数には影響しない）。"""
    if not rows or not order or len(order) < 3:
        return None
    n = len(rows)
    out = {}
    for pos, role in (('1', 'role_w'), ('2', 'role_p2'), ('3', 'role_p3')):
        members = {str(x['no']) for x in rows if x.get(role)}
        out[role] = {'size': len(members), 'hit': str(order[int(pos) - 1]) in members,
                     'random_base': round(len(members) / n, 3) if n else None}
    return out


def top2_gap(rows, key='win_score'):
    """上位2頭の得点差（地方 KRS-Engine 運用接続規程 v1.6 Rev.4 の LOW-DISCRIMINATION を読み替え）。
    差が小さいレースは馬の区別がついていない。閾値は置かず、差の大小で◎の成績を分けて数えるだけ（証拠のみ）。"""
    sc = sorted((x.get(key) for x in rows or [] if x.get(key) is not None), reverse=True)
    return round(sc[0] - sc[1], 2) if len(sc) >= 2 else None


def coverage_summary(revs):
    """累計：役割ごとの的中率と無作為基準の平均、上位2頭の差（中央値で上下に分けた◎1着数）。"""
    cov = [x['role_coverage'] for x in revs if x.get('role_coverage')]
    res = {}
    for role in ('role_w', 'role_p2', 'role_p3'):
        c = [x[role] for x in cov]
        if c:
            res[role] = {'races': len(c), 'hit_rate': round(sum(x['hit'] for x in c) / len(c), 3),
                         'random_base': round(sum(x['random_base'] or 0 for x in c) / len(c), 3),
                         'mean_size': round(sum(x['size'] for x in c) / len(c), 2)}
    g = sorted(x['top2_gap'] for x in revs if x.get('top2_gap') is not None)
    if g:
        med = g[len(g) // 2]
        lo = [x for x in revs if x.get('top2_gap') is not None and x['top2_gap'] < med]
        hi = [x for x in revs if x.get('top2_gap') is not None and x['top2_gap'] >= med]
        res['top2_gap'] = {'median': med, 'low_races': len(lo), 'low_honmei_win': sum(x['honmei_finish'] == 1 for x in lo),
                           'high_races': len(hi), 'high_honmei_win': sum(x['honmei_finish'] == 1 for x in hi)}
    return res or None


def longshot_lane_trend(revs, min_pop=6, split=5):
    """人気薄の好走馬だけで走路の偏りを読む（Owner 追加 YouTube「トラックバイアスって何？」2026-11-23 精読：
    1〜3番人気の決着は能力で決まっただけかもしれないので偏りの根拠にせず、6番人気以下で3着内に来た馬の通り道を見る）。
    ばんえいでは馬番＝走路番号なので、内側（1〜split）と外側（split+1〜）の占有を、3着内の全馬と比べて数える。
    閾値・補正は置かない。証拠のみ（券面・点数には影響しない）。"""
    allf, ls = [0, 0], [0, 0]
    for x in revs:
        for f in (x.get('finishers') or {}).values():
            no, pop = f.get('no'), f.get('pop')
            if no is None:
                continue
            side = 0 if int(no) <= split else 1
            allf[side] += 1
            if pop is not None and int(pop) >= min_pop:
                ls[side] += 1
    if not sum(ls):
        return None
    return {'min_pop': min_pop, 'split': split, 'longshot_inner': ls[0], 'longshot_outer': ls[1],
            'longshot_inner_share': round(ls[0] / sum(ls), 3),
            'all_inner_share': round(allf[0] / sum(allf), 3) if sum(allf) else None, 'all_top3': sum(allf)}


def result_orders(res):
    """同着を含む成立着順（11/23 ChatGPT 反省 P0-2：4R 3着 7・8 同着）。三連単の払戻組番が2つ以上あれば
    そのすべてを、無ければ order の先頭3頭を返す。精算（run.settle_race）は払戻表の全組を見るので正しいが、
    反省の first_failure・役割の当否は order[:3] だけを見ていた。証拠のみ。"""
    tri = ((res or {}).get('payouts') or {}).get('TRIFECTA') or {}
    outs = []
    for k in tri:
        try:
            o = tuple(int(x) for x in str(k).split('-'))
        except ValueError:
            continue
        if len(o) == 3 and o not in outs:
            outs.append(o)
    base = tuple(int(x) for x in (res or {}).get('order', [])[:3])
    if len(outs) >= 2:
        return sorted(outs, key=lambda o: (o != base, o))
    return [base] if len(base) == 3 else []


CHAIN = ('HORSE', 'ROLE_W', 'ROLE_P2', 'ROLE_P3', 'TRIO', 'HEAD', 'ORDERED_PAIR', 'THIRD')


def winner_off_ticket(tk, winner, stake=None):
    """勝ち馬が券面のどの組にも入らないまま点数を使ったか（中央 11/23 反省 P0-05「W 被覆なしの点数拡張」の読み替え。証拠のみ）。"""
    if winner is None or not tk.get('points'):
        return None
    on = any(winner in x for x in (tk.get('trio') or [])) or any(winner in x for x in (tk.get('exact') or []))
    return {'winner_on_ticket': on, 'points': tk['points'], 'wasted_points': 0 if on else tk['points'],
            'wasted_stake': 0 if on or stake is None else stake}


def axis_dependency(tk, order):
    """二頭軸の共倒れ監査（Drive q461「JRA_20261107_P0_P2_Verification」京都2R：三連複の全券が2頭の同時好走に依存して全損、の読み替え）。
    tickets.axis が2頭（◎○二頭軸）のとき、両軸を含む券の点数・割合、両軸とも3着内だったか、片軸が3着外で両軸依存の券が全部外れたか。
    1頭軸のときは軸を含む券の割合と軸の3着内だけ。証拠のみ（券面・点数・見送りには使わない）。"""
    axis = [int(a) for a in (tk.get('axis') or [])]
    if not axis or not order or len(order) < 3:
        return None
    top3 = {int(n) for n in order[:3]}
    tix = [tuple(int(n) for n in x) for x in (tk.get('trio') or [])] + [tuple(int(n) for n in x) for x in (tk.get('exact') or [])]
    if not tix:
        return None
    dep = [x for x in tix if all(a in x for a in axis)]
    in3 = [a in top3 for a in axis]
    out = {'axis': axis, 'n_axis': len(axis), 'tickets': len(tix), 'axis_tickets': len(dep),
           'axis_share': round(len(dep) / len(tix), 2), 'axis_in_top3': sum(in3),
           'all_axis_top3': all(in3)}
    out['axis_wipeout'] = bool(dep) and not out['all_axis_top3']      # 軸依存の券は1点も当たらない
    out['wipeout_points'] = len(dep) if out['axis_wipeout'] else 0
    out['co_failure'] = len(axis) >= 2 and not any(in3)                # 二頭軸が両方とも3着外
    return out


def failure_chain(rows, marks, tk, order):
    """断線の多層記録（11/23 ChatGPT 反省 P0-5：単一の first_failure だけで原因を決めない）。
    HORSE（3頭とも印内）→ ROLE_W/P2/P3（着順ごとの役割）→ TRIO（三連複の組）→ HEAD（三連単の頭に勝ち馬）
    → ORDERED_PAIR（1→2着の並び）→ THIRD（1→2→3着の並び）の各層の成否を全部残し、欠けた層の一覧と最初の欠損を返す。
    三連単を買っていないレースは HEAD 以降を None。証拠のみ（券面・点数には影響しない）。"""
    if not order or len(order) < 3:
        return None
    w, s, t = (str(x) for x in order[:3])
    R = {str(x['no']): x for x in (rows or [])}
    mk = {str(k): v for k, v in (marks or {}).items()}
    ex = [tuple(str(n) for n in x) for x in (tk.get('exact') or []) if len(x) == 3]
    trio = {tuple(sorted(str(n) for n in x)) for x in (tk.get('trio') or [])}
    st = {'HORSE': all(mk.get(n) for n in (w, s, t)),
          'ROLE_W': bool((R.get(w) or {}).get('role_w')),
          'ROLE_P2': bool((R.get(s) or {}).get('role_p2')),
          'ROLE_P3': bool((R.get(t) or {}).get('role_p3')),
          'TRIO': tuple(sorted((w, s, t))) in trio if trio else None,
          'HEAD': any(x[0] == w for x in ex) if ex else None,
          'ORDERED_PAIR': any(x[:2] == (w, s) for x in ex) if ex else None,
          'THIRD': (w, s, t) in set(ex) if ex else None}
    failed = [k for k in CHAIN if st[k] is False]
    return {'layers': st, 'failed': failed, 'first': failed[0] if failed else 'NONE'}


def market_drift(changes, order, honmei=None):
    """直前見直しの2時点オッズ（check10 の変更台帳 changes の odds の before/after）から、オッズが下がった馬（売れた）・
    上がった馬（売れなかった）と3着内の対応を残す（中央 next_execution_prompt §P1-02「同一レース内2時点の市場」の読み替え。
    証拠のみ、閾値なし、本番の点数・印・券面には使わない）。"""
    if not changes or not isinstance(changes, dict) or not isinstance(changes.get('diffs'), list) or len(order) < 3:
        return None
    top3 = {str(n) for n in order[:3]}
    short, drift = [], []
    for d in changes['diffs']:
        if d.get('field') != 'odds':
            continue
        a, b = d.get('before'), d.get('after')
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)) or a <= 0 or a == b:
            continue
        (short if b < a else drift).append({'no': d.get('no'), 'before': a, 'after': b, 'ratio': round(b / a, 3)})
    hon = next((x for x in short + drift if str(x['no']) == str(honmei)), None) if honmei is not None else None
    return {'shortened': len(short), 'drifted': len(drift),
            'shortened_top3': sum(1 for x in short if str(x['no']) in top3),
            'drifted_top3': sum(1 for x in drift if str(x['no']) in top3),
            'winner_move': next(('short' if x in short else 'drift' for x in short + drift if str(x['no']) == str(order[0])), 'none'),
            'honmei_move': None if hon is None else ('short' if hon in short else 'drift'),
            'moves': sorted(short + drift, key=lambda x: x['ratio'])[:6], 'evidence_only': True}


def market_drift_summary(revs):
    """market_drift の集計：見直しで2時点オッズがあったR数、売れた馬・売れなかった馬それぞれの頭数と3着内数、勝ち馬の動き。"""
    xs = [x['market_drift'] for x in revs if x.get('market_drift')]
    if not xs:
        return None
    from collections import Counter
    out = {'races': len(xs)}
    for k in ('shortened', 'drifted', 'shortened_top3', 'drifted_top3'):
        out[k] = sum(x[k] for x in xs)
    out['winner_move'] = dict(Counter(x['winner_move'] for x in xs))
    out['honmei_move'] = dict(Counter(x['honmei_move'] or 'none' for x in xs))
    return out


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
        return {'no': int(n), 'mark': marks.get(n, ''), 'dcr': x.get('dcr'), 'pop': x.get('pop'), 'win_rank': x.get('win_rank'),
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
        # 情報不足（2歳・出走経験が少ない等で DCR<70）を能力不足と混同しない（11/21 ChatGPT反省 P1-2）
        wdcr = (rows.get(w) or {}).get('dcr')
        cause = 'C0-INFO' if (wdcr is not None and wdcr < 70) else ('C1' if (fin['1']['win_rank'] or 99) > 5 else 'C2')
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
    shadow = shadow_metrics(out, key, eff, res, rec)
    # 変換ファネル（FNB 第227条ほか）: 勝ち馬をWに → 1-2着の組 → 三連複 → 三連単 → 収支プラス
    w_, s_, t_ = res['order'][:3]
    funnel = {'winner_in_W': fin['1']['in_role'],
              'pair_in_tickets': any(len(x) == 3 and x[0] == w_ and x[1] == s_ for x in tk['exact'])
              or any({w_, s_} <= set(x) for x in tk['trio']),
              'trio_bought': trio_ret > 0, 'exact_bought': ex_ret > 0, 'profit': (res['return'] or 0) > (res['stake'] or 0)}
    # 着順馬ごとの経路（Formal Post-Race Review 16〜18節の簡易版）: 役割 → 三連複に入ったか → 三連単に入ったか
    for k, f in fin.items():
        n_ = f['no']
        f['in_trio_tickets'] = any(n_ in x for x in tk['trio'])
        f['in_exact_tickets'] = any(n_ in x for x in tk['exact'])
        f['xdi'] = bool((rows.get(str(n_)) or {}).get('xdi'))
    # 一極集中（園田 第559-561条・exposure）: 最多出現馬の三連複占有率、その馬が3着外なら残る点数
    cnt = {}
    for x in tk['trio']:
        for n_ in x:
            cnt[n_] = cnt.get(n_, 0) + 1
    hub = max(cnt, key=cnt.get) if cnt else None
    hub_share = round(cnt[hub] / len(tk['trio']), 2) if hub else None
    exposure = {'hub': hub, 'hub_share': hub_share, 'extreme_hub': bool(hub_share and hub_share >= 0.9),
                'hub_failed': bool(hub and hub not in res['order'][:3])}
    exposure['winner_off_ticket'] = winner_off_ticket(tk, w_, res.get('stake'))
    exposure['axis_dependency'] = axis_dependency(tk, res['order'])
    cpt = cross_pair_third(tk['exact'], res['order'])
    exposure['cross_pair_third'] = bool(cpt and cpt['cross_pair_third'])
    if exposure['cross_pair_third']:
        P.append({'id': 'P2:CROSS_PAIR_THIRD', 'level': 'P2',
                  'what': '1-2着の並びは三連単で買ったが、3着馬は別の並びの3着にだけ入っていた', 'evidence': cpt})
    # 安すぎる買い目（FNB 第219条 Low-Payout Structure）: 発走前オッズで、当たっても投資額に届かない券の割合
    od = _j(out / f'R{key}.odds.json')
    low = None
    if od:
        stake_all = tk['points'] * 100
        tri = [od.get('sanrenfuku', {}).get('-'.join(map(str, sorted(x)))) for x in tk['trio']]
        exa = [od.get('sanrentan', {}).get('-'.join(map(str, x))) for x in tk['exact']]
        known = [o for o in tri + exa if o]
        low = {'tickets_with_odds': len(known), 'below_stake': sum(1 for o in known if o * 100 < stake_all),
               'trio_min': min([o for o in tri if o], default=None), 'exact_min': min([o for o in exa if o], default=None),
               'odds_at': od.get('fetched_at')}
        if known and low['below_stake'] / len(known) >= 0.5:
            P.append({'id': 'P2:LOW_PAYOUT_STRUCTURE', 'level': 'P2',
                      'what': '発走前オッズで券の半数以上が当たっても投資割れ', 'evidence': low})
    if (res['return'] or 0) > 0 and (res['return'] or 0) < (res['stake'] or 0):
        P.append({'id': 'P2:HIT_BUT_LOSS', 'level': 'P2', 'what': '的中したが投資割れ（点数の広さ・低配当）',
                  'evidence': {'stake': res['stake'], 'return': res['return'], 'points': tk['points']}})
    xdi_miss = [f for f in fin.values() if f['xdi']]
    if xdi_miss:
        P.append({'id': 'P1:XDI_FINISHER', 'level': 'P1', 'what': '水分ボンバー上位3頭なのに内部下位半分だった馬が3着内',
                  'evidence': xdi_miss})
    chain = failure_chain(ev['rows'], ev.get('marks'), tk, res['order'])
    orders = result_orders(res)
    dead_heat = None
    if len(orders) >= 2:
        dead_heat = {'orders': [list(o) for o in orders],
                     'ffl_by_order': {'-'.join(map(str, o)): _run.first_failure(tk, list(o)) for o in orders},
                     'chain_by_order': {'-'.join(map(str, o)): (failure_chain(ev['rows'], ev.get('marks'), tk, list(o)) or {}).get('first')
                                        for o in orders}}
        P.append({'id': 'P0:DEAD_HEAT', 'level': 'P0', 'what': '3着以内に同着：成立着順ごとに断線を記録', 'evidence': dead_heat})
    return {'key': key, 'order': res['order'][:3], 'shadow': shadow, 'chain': chain, 'dead_heat': dead_heat, 'funnel': funnel, 'exposure': exposure,
            'low_payout': low,
            'refund': res.get('refund'),
            'moisture_band': ev.get('moisture_band'), 'field': len(ev['rows']), 'pfs': res['pfs'], 'stake': res['stake'], 'return': res['return'],
            'ffl': ffl, 'cause': cause, 'formality': tk['formality'], 'revision': res.get('effective_revision'),
            'rev_audit': res.get('rev_audit'), 'paper': res.get('paper'), 'finishers': fin,
            'honmei': ev.get('honmei'), 'honmei_pop': (rows.get(str(ev.get('honmei'))) or {}).get('pop'),
            'honmei_finish': next((i + 1 for i, n in enumerate(res['order'][:3])
                                                               if str(n) == str(ev.get('honmei'))), None),
            'trio_hit': trio_ret > 0, 'exact_hit': ex_ret > 0,
            'role_coverage': role_set_coverage(ev['rows'], res['order']), 'top2_gap': top2_gap(ev['rows']),
            'info_coverage': info_coverage(ev['rows']),
            'market_drift': market_drift((r.get('check10') or {}).get('changes'), res['order'], ev.get('honmei')),
            'components': {'trio': [trio_st, trio_ret], 'exact': [ex_st, ex_ret]}, 'proposals': P}


def shadow_metrics(out, key, eff, res, rec):
    """Same yardsticks for BASE and every pre-registered challenger (challengers.PREREG)."""
    sh = _j(out / f'R{key}{eff}.shadow.json')
    if not sh:
        return None
    w, s, t = res['order'][:3]
    pay = res['payouts']
    m = {}
    for cid, c in sh['candidates'].items():
        if 'error' in c:
            m[cid] = {'error': c['error']}
            continue
        wo, po = c['win_order'], c['place_order']
        tr = sum(pay.get('TRIO', {}).get('-'.join(map(str, x)), 0) for x in c['trio'])
        ex = sum(pay.get('TRIFECTA', {}).get('-'.join(map(str, x)), 0) for x in c['exact'])
        m[cid] = {'winner_win_rank': wo.index(w) + 1 if w in wo else None,
                  'top3_in_place5': sum(1 for n in (w, s, t) if n in po[:5]),
                  'honmei_top3': c['honmei'] in (w, s, t),
                  'trio_hit': tr > 0, 'exact_hit': ex > 0,
                  'stake': c['points'] * 100, 'return': tr + ex}
    return m


def shadow_table(revs):
    """Aggregate challenger metrics over races where both BASE and the candidate exist."""
    from statistics import mean
    agg = {}
    for x in revs:
        for cid, m in (x.get('shadow') or {}).items():
            if 'error' not in m:
                agg.setdefault(cid, []).append((m, x.get('moisture_band')))
    rows = []
    for cid, L in agg.items():
        ms = [m for m, _ in L]
        n = len(ms)
        st, rt = sum(m['stake'] for m in ms), sum(m['return'] for m in ms)
        top = max((m['return'] for m in ms), default=0)
        wr = [m['winner_win_rank'] for m in ms if m['winner_win_rank']]
        band = {}
        for m, b in L:
            band.setdefault(b, []).append(m['winner_win_rank'] or 9)
        rows.append({'id': cid, 'n': n, 'winner_rank_mean': round(mean(wr), 2) if wr else None,
                     'winner_top1': sum(1 for v in wr if v == 1), 'winner_top3': sum(1 for v in wr if v <= 3),
                     'top3_in_place5_mean': round(mean(m['top3_in_place5'] for m in ms), 2),
                     'honmei_top3': sum(m['honmei_top3'] for m in ms), 'trio_hit': sum(m['trio_hit'] for m in ms),
                     'exact_hit': sum(m['exact_hit'] for m in ms), 'stake': st, 'return': rt, 'pfs': _pct(rt, st),
                     'pfs_ex_top1': _pct(rt - top, st), 'winner_rank_by_band': {k: round(mean(v), 2) for k, v in band.items()}})
    return sorted(rows, key=lambda r: (r['id'] != 'BASE', r['id']))


def _shadow_md(rows, registered=None):
    """registered: challenger_registry.json の candidates（registry.py が後から登録した候補の内容・状態を表に出す）。"""
    import challengers
    C = dict(challengers.PREREG['candidates'])
    C.update({k: v for k, v in (registered or {}).items() if isinstance(v, dict)})
    L = ['| 候補 | 内容 | 状態 | R | 勝ち馬の評価順位(平均) | 1位 | 3位内 | 3着内馬の複順位5位内(平均) | ◎3着内 | 三連複 | 三連単 | PFS | 最高1本除く |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        c = C.get(r['id'], {})
        L.append(f"| {r['id']} | {c.get('what', '')} | {c.get('status', '')} | {r['n']} | {r['winner_rank_mean']} | {r['winner_top1']} | "
                 f"{r['winner_top3']} | {r['top3_in_place5_mean']} | {r['honmei_top3']} | {r['trio_hit']} | {r['exact_hit']} | "
                 f"{r['pfs']} | {r['pfs_ex_top1']} |")
    return '\n'.join(L) + '\n'


def _pct(a, b):
    return round(100 * a / b, 1) if b else None


def payout_robustness(revs, k=3):
    """上位払戻 1..k レースを除いた PFS・最長連敗・収支プラスの R 数（証拠のみ、本番の点数・券面に影響しない）。
    出典：Drive 園田 v2.6-SON 改定要約（単一レース依存）・地方版 forward.robustness の読み替え（帯広1場）。"""
    bought = [x for x in revs if (x.get('stake') or 0) > 0]
    if not bought:
        return None
    order = sorted(range(len(bought)), key=lambda i: bought[i]['return'], reverse=True)
    S = sum(x['stake'] for x in bought)
    B = sum(x['return'] for x in bought)
    out = {'races': len(bought), 'profit_races': sum(1 for x in bought if x['return'] > x['stake'])}
    for n in range(1, k + 1):
        drop = order[:n]
        s_ = S - sum(bought[i]['stake'] for i in drop)
        b_ = B - sum(bought[i]['return'] for i in drop)
        out[f'pfs_without_top{n}'] = _pct(b_, s_) if len(bought) > n else None
    run = best = 0
    for x in bought:
        run = run + 1 if x['return'] == 0 else 0
        best = max(best, run)
    out['longest_losing_streak'] = best
    return out


def by_moisture_band(revs):
    """水分帯（engine.moisture_band）ごとの本番の成績：R数・◎1着・◎3着内・勝ち馬∈W・投資・払戻・PFS（証拠のみ、閾値なし）。
    出典：Drive YouTube（q-1052 同水分帯・別水分帯の実績の分離）の読み替え。単日・少数Rでは数値を変えない（R30/R100＋Owner承認）。"""
    out = {}
    for x in revs:
        b = x.get('moisture_band') or 'UNKNOWN'
        d = out.setdefault(b, {'races': 0, 'honmei_win': 0, 'honmei_top3': 0, 'winner_in_W': 0, 'stake': 0, 'return': 0})
        d['races'] += 1
        d['honmei_win'] += int(x.get('honmei_finish') == 1)
        d['honmei_top3'] += int(bool(x.get('honmei_finish')))
        d['winner_in_W'] += int(bool(((x.get('finishers') or {}).get('1') or {}).get('in_role')))
        d['stake'] += x.get('stake') or 0
        d['return'] += x.get('return') or 0
    for d in out.values():
        d['pfs'] = _pct(d['return'], d['stake'])
    return out or None


POP_BANDS = (('1', 1, 1), ('2-3', 2, 3), ('4-6', 4, 6), ('7+', 7, 99))


def by_honmei_pop_band(revs):
    """◎の人気帯（1番人気・2-3・4-6・7番人気以下）ごとの本番の成績：R数・◎1着・◎3着内・投資・払戻・PFS（証拠のみ、閾値なし）。
    出典：Drive「馬券購入法」（q424 単勝オッズ帯別の回収率）と亀谷「スマート出馬表」（q425 人気で調整して比べる）の読み替え。
    ばんえいは人気帯で本命を選び直さない（本番の点数・印・券面には使わない）。"""
    out = {}
    for x in revs:
        try:
            pop = int(x.get('honmei_pop'))
        except (TypeError, ValueError):
            pop = None
        b = next((n for n, lo, hi in POP_BANDS if pop is not None and lo <= pop <= hi), 'UNKNOWN')
        d = out.setdefault(b, {'races': 0, 'honmei_win': 0, 'honmei_top3': 0, 'stake': 0, 'return': 0})
        d['races'] += 1
        d['honmei_win'] += int(x.get('honmei_finish') == 1)
        d['honmei_top3'] += int(bool(x.get('honmei_finish')))
        d['stake'] += x.get('stake') or 0
        d['return'] += x.get('return') or 0
    for d in out.values():
        d['pfs'] = _pct(d['return'], d['stake'])
    return out or None


def info_coverage(rows):
    """レースの情報充足（各馬の DCR の平均・最小、TPI が欠けて中立で埋めた頭数）。証拠のみ。
    出典：Drive「JRA Complete Audit Brief」（q448 Base13 構成充足 61.90%、欠測を中立で埋めた値を能力と読まない）の読み替え。"""
    d = [x['dcr'] for x in (rows or []) if x.get('dcr') is not None]
    if not rows:
        return None
    return {'dcr_mean': round(sum(d) / len(d), 1) if d else None, 'dcr_min': min(d) if d else None,
            'tpi_unknown': sum(1 for x in rows if x.get('tpi') is None), 'field': len(rows)}


DCR_BANDS = (('<70', 0, 70), ('70-84', 70, 85), ('85+', 85, 101))


def by_info_coverage(revs):
    """情報充足帯（レースの DCR 平均 <70・70-84・85+）ごとの本番の成績：R・◎1着・◎3着内・勝ち馬∈W・PFS（証拠のみ、閾値なし）。
    情報が薄いレースの成績を能力評価の失敗と混同しないための物差し。本番の点数・印・券面・見送りには使わない。"""
    out = {}
    for x in revs:
        m = (x.get('info_coverage') or {}).get('dcr_mean')
        b = next((n for n, lo, hi in DCR_BANDS if m is not None and lo <= m < hi), 'UNKNOWN')
        d = out.setdefault(b, {'races': 0, 'honmei_win': 0, 'honmei_top3': 0, 'winner_in_W': 0, 'tpi_unknown': 0,
                               'stake': 0, 'return': 0})
        d['races'] += 1
        d['honmei_win'] += int(x.get('honmei_finish') == 1)
        d['honmei_top3'] += int(bool(x.get('honmei_finish')))
        d['winner_in_W'] += int(bool(((x.get('finishers') or {}).get('1') or {}).get('in_role')))
        d['tpi_unknown'] += (x.get('info_coverage') or {}).get('tpi_unknown') or 0
        d['stake'] += x.get('stake') or 0
        d['return'] += x.get('return') or 0
    for d in out.values():
        d['pfs'] = _pct(d['return'], d['stake'])
    return out or None


def axis_dependency_summary(revs):
    """axis_dependency の集計：軸の頭数別に R数・軸依存の券の平均割合・全損R（片軸以上が3着外）・全損点数・二頭とも3着外のR。"""
    out = {}
    for x in revs:
        a = (x.get('exposure') or {}).get('axis_dependency')
        if not a:
            continue
        d = out.setdefault(str(a['n_axis']), {'races': 0, 'share_sum': 0.0, 'all_axis_top3': 0, 'wipeout': 0,
                                              'wipeout_points': 0, 'co_failure': 0})
        d['races'] += 1
        d['share_sum'] += a['axis_share']
        d['all_axis_top3'] += int(a['all_axis_top3'])
        d['wipeout'] += int(a['axis_wipeout'])
        d['wipeout_points'] += a['wipeout_points']
        d['co_failure'] += int(a['co_failure'])
    for d in out.values():
        d['axis_share_mean'] = round(d.pop('share_sum') / d['races'], 2)
    return out or None


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
            'ffl': dict(ffl), 'cause': dict(cause), 'p0p1': dict(p), 'rev_audit': a,
            'funnel': {k: sum(1 for x in revs if (x.get('funnel') or {}).get(k)) for k in
                       ('winner_in_W', 'pair_in_tickets', 'trio_bought', 'exact_bought', 'profit')},
            'hit_but_loss': sum(1 for x in revs if 0 < x['return'] < x['stake']),
            'extreme_hub': sum(1 for x in revs if (x.get('exposure') or {}).get('extreme_hub')),
            'hub_failed': sum(1 for x in revs if (x.get('exposure') or {}).get('hub_failed')),
            'cross_pair_third': sum(1 for x in revs if (x.get('exposure') or {}).get('cross_pair_third')),
            'winner_off_ticket': sum(1 for x in revs if ((x.get('exposure') or {}).get('winner_off_ticket') or {}).get('winner_on_ticket') is False),
            'winner_off_ticket_stake': sum(((x.get('exposure') or {}).get('winner_off_ticket') or {}).get('wasted_stake') or 0 for x in revs),
            'coverage': coverage_summary(revs), 'longshot_lane': longshot_lane_trend(revs),
            'chain_failed': {k: sum(1 for x in revs if k in ((x.get('chain') or {}).get('failed') or [])) for k in CHAIN},
            'chain_first': dict(Counter((x.get('chain') or {}).get('first') for x in revs if x.get('chain'))),
            'dead_heat': sum(1 for x in revs if x.get('dead_heat')),
            'robustness': payout_robustness(revs), 'by_moisture_band': by_moisture_band(revs),
            'by_honmei_pop_band': by_honmei_pop_band(revs), 'by_info_coverage': by_info_coverage(revs),
            'axis_dependency': axis_dependency_summary(revs), 'market_drift': market_drift_summary(revs)}


def _md(title, s, revs=None):
    L = [f'# {title}', '',
         f"- 精算 {s['races']}R（締切超過 {s['missed']}R）／投資 {s['stake']:,}円・払戻 {s['return']:,}円・PFS {s['pfs']}%"
         f"（最高配当1本を除くと {s['pfs_without_top1']}%）",
         f"- 三連複 的中 {s['trio_hit']}R・PFS {s['trio_pfs']}%／三連単 的中 {s['exact_hit']}R・PFS {s['exact_pfs']}%",
         f"- ◎ 1着 {s['honmei_win']}・3着内 {s['honmei_top3']}／勝ち馬∈W {s['winner_in_W']}・2着∈P2 {s['second_in_P2']}・3着∈P3 {s['third_in_P3']}",
         f"- 最初の断線: {s['ffl']}／原因コード: {s['cause']}",
         f"- 断線の多層記録（欠けた層ごとのレース数）: {s.get('chain_failed')}／最初の欠損: {s.get('chain_first')}／同着 {s.get('dead_heat', 0)}R",
         f"- 変換ファネル: 勝ち馬∈W {s['funnel']['winner_in_W']} → 1-2着の組 {s['funnel']['pair_in_tickets']} → 三連複 {s['funnel']['trio_bought']}"
         f" → 三連単 {s['funnel']['exact_bought']} → 収支プラス {s['funnel']['profit']}／的中したが投資割れ {s['hit_but_loss']}"
         f"／一極集中 {s['extreme_hub']}・最多出現馬が3着外 {s['hub_failed']}"
         f"／勝ち馬が券面に無いまま買った {s.get('winner_off_ticket', 0)}R（{s.get('winner_off_ticket_stake', 0):,}円）",
         f"- P0/P1: {s['p0p1'] or 'なし'}"]
    cv = s.get('coverage') or {}
    if any(k in cv for k in ('role_w', 'role_p2', 'role_p3')):
        L.append('- 役割の被覆（的中率／無作為基準・平均頭数）: ' + '・'.join(
            f"{nm} {cv[k]['hit_rate']:.0%}／{cv[k]['random_base']:.0%}・{cv[k]['mean_size']}頭"
            for k, nm in (('role_w', 'W'), ('role_p2', 'P2'), ('role_p3', 'P3')) if k in cv))
    if cv.get('top2_gap'):
        g = cv['top2_gap']
        L.append(f"- 上位2頭の得点差（中央値 {g['median']}）: 差が小さい {g['low_races']}R の◎1着 {g['low_honmei_win']}"
                 f"／差が大きい {g['high_races']}R の◎1着 {g['high_honmei_win']}")
    if s.get('longshot_lane'):
        g = s['longshot_lane']
        L.append(f"- 人気薄（{g['min_pop']}番人気以下）の3着内 {g['longshot_inner'] + g['longshot_outer']}頭の走路: "
                 f"内側1〜{g['split']} {g['longshot_inner_share']:.0%}（3着内の全馬 {g['all_inner_share']:.0%}）")
    if s.get('robustness'):
        r = s['robustness']
        L.append(f"- 回収の頑健性（購入 {r['races']}R）: 上位払戻を除いた PFS 1R除き {r['pfs_without_top1']}%"
                 f"・2R除き {r['pfs_without_top2']}%・3R除き {r['pfs_without_top3']}%"
                 f"／収支プラス {r['profit_races']}R／最長連敗 {r['longest_losing_streak']}R")
    if s.get('by_moisture_band'):
        L.append('- 水分帯別（R・◎1着・◎3着内・勝ち馬∈W・PFS）: ' + '／'.join(
            f"{b} {d['races']}R・{d['honmei_win']}・{d['honmei_top3']}・{d['winner_in_W']}・{d['pfs']}%"
            for b, d in sorted(s['by_moisture_band'].items())))
    if s.get('by_honmei_pop_band'):
        order = [n for n, _, _ in POP_BANDS] + ['UNKNOWN']
        L.append('- ◎の人気帯別（R・◎1着・◎3着内・PFS）: ' + '／'.join(
            f"{b}番人気 {d['races']}R・{d['honmei_win']}・{d['honmei_top3']}・{d['pfs']}%"
            for b, d in sorted(s['by_honmei_pop_band'].items(), key=lambda kv: order.index(kv[0]))))
    if s.get('by_info_coverage'):
        order = [n for n, _, _ in DCR_BANDS] + ['UNKNOWN']
        L.append('- 情報充足帯別（DCR平均：R・◎1着・◎3着内・勝ち馬∈W・TPI欠け頭数・PFS）: ' + '／'.join(
            f"{b} {d['races']}R・{d['honmei_win']}・{d['honmei_top3']}・{d['winner_in_W']}・{d['tpi_unknown']}・{d['pfs']}%"
            for b, d in sorted(s['by_info_coverage'].items(), key=lambda kv: order.index(kv[0]))))
    if s.get('axis_dependency'):
        L.append('- 軸への依存（軸の頭数：R・軸を含む券の平均割合・全軸3着内・軸依存の券が全損・その点数・二頭とも3着外）: ' + '／'.join(
            f"{k}頭軸 {d['races']}R・{d['axis_share_mean']:.0%}・{d['all_axis_top3']}・{d['wipeout']}R・{d['wipeout_points']}点・{d['co_failure']}R"
            for k, d in sorted(s['axis_dependency'].items())))
    if s.get('market_drift'):
        m = s['market_drift']
        L.append(f"- 直前2時点のオッズ（見直しのあった {m['races']}R）: 売れた馬 {m['shortened']}頭のうち3着内 {m['shortened_top3']}"
                 f"／売れなかった馬 {m['drifted']}頭のうち3着内 {m['drifted_top3']}／勝ち馬の動き {m['winner_move']}／◎の動き {m['honmei_move']}")
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
    L += ['', '本番の数値は手で変えない。影の候補式と未知のレースで比べ、事前に固定した条件（registry.PROMOTE：同じ本番で100R以上ほか）を満たせば自動昇格、悪化すれば自動で戻す。P0のコード欠陥は夜間の自動作業で修正する。']
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
    sh = shadow_table(revs)
    if sh:
        import challengers
        (Path(root) / 'forward_oos_ban.json').write_text(json.dumps({'prereg': challengers.PREREG, 'table': sh},
                                                                   ensure_ascii=False, indent=1))
        (Path(root) / 'forward_oos_ban.md').write_text(
            f"# ばんえい 影の候補式の比較（未知のレース・発走前に固定）\n\n{days[0]}〜{days[-1]}・{n}R。"
            f"登録 {challengers.PREREG['registered_at']}。{challengers.PREREG['decision']}\n\n"
            + _shadow_md(sh, (_j(Path(root) / 'challenger_registry.json') or {}).get('candidates'))
            + "\n勝ち馬の評価順位は小さいほど良い。PFSは高配当1本で大きく動くため、R100未満では順位の物差しを主に見る。\n")
