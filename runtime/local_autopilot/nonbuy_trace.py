"""B1 非購入理由と経路の記録（Drive 精読 gap_tracker B1、2026-11-26 着手。証拠のみ・券面は変えない）。

実際の1-2-3着の組と、役割を持った各馬について、
  役割(W/P2/P3) → 署名済み全MECで生成されたか → 60点の上限後に残ったか（購入）
のどこで落ちたかを理由コード付きで記録する。予算で落ちたもの（CAPITAL）と、予想として外したもの（SEMANTIC）を
別の軸に分け、予算で落ちた券を「来ない」と説明しない（v4.13 第60・340・358・401・411条、q279 の非購入4分類）。

理由コード（実着順の組、券種ごと）：
  PURCHASED                    配信券面に含まれる
  BUDGET_COMPRESSED            全MECにはあったが上限（60点）で削られた＝CAPITAL-NONPURCHASED
  BET_TYPE_ABSENT              全MECにその券種が1枚も無い
  SEMANTIC_EXCLUDED_ROLE_W     勝ち馬が W に無い（以下、予想としての除外＝SEMANTIC）
  SEMANTIC_EXCLUDED_ROLE_P2    2着馬が P2 に無い（馬単・三連単）
  SEMANTIC_EXCLUDED_ROLE_P3    3着馬が P3 に無い（三連単）／3頭のどれかが役割外（三連複）
  NOT_GENERATED                役割には全員いたが組として生成されていない（FPP→Candidate の欠落）
役割馬ごと（NSD：評価馬の無言削除の検出）：
  PURCHASED / BUDGET_COMPRESSED（全MECには居たが配信に無い）/ NOT_GENERATED（役割はあるが全MECにも無い）

第2部（2026-11-26 03時台、gap n19・n24・n27・n51・n137 の残り。証拠のみ）：
  role_horses[*] に段ごとの券数と投資額（tickets_full / tickets_kept / stake_kept）
  order_uncertainty：実着順の3頭（馬単は1-2着の2頭）が、実際の向きで残ったか・別の向きだけ残ったか
      （園田 v2.8 第292条 Order-Uncertainty。ACTUAL_AND_OTHER / ACTUAL_ONLY / OTHER_ONLY / NONE）
  head_continuity：W の各馬が頭（馬単・三連単の1着）として 全MEC→配信 のどこまで残ったか
      （Daily Formal Review Rev6 Alternative Winner Continuity。HEAD_PURCHASED / HEAD_BUDGET_COMPRESSED / HEAD_NOT_GENERATED）

第3部（2026-11-26 06時台、gap n51・n70 の残り。証拠のみ）：
  ticket_hygiene：全MEC・配信の各券を正規化して、R2 完全統合仕様の非購入理由のうち
      DUPLICATE_NORMALIZED（券種＋正規化した組〔三連複は順不同〕が同じ券の2枚目以降）と
      INVALID_RUNNER（出走表に無い馬番・同じ馬が2回・頭数違い・読めない券）を数える。
      runners（出走馬番）が無いときは出走表照合を UNTESTED とし、重複・頭数だけを見る。
  width：幅の事前根（中央 v2.3 第399・414・366条 capital_width_precommit／Anti-Whiplash）の記録。
      役割の頭数（W/P2/P3）・券種ごとの点数と投資額を、全MEC（事前に署名された幅）と配信の両方で残し、
      aggregate で同じ場の前のレースが外れ／当たりだった後の配信点数の変化（whiplash）を比べる。
      幅は事前に決まっているはずなので、前走の当否で幅が揺れていれば記録に出る（券面は変えない）。
"""
from itertools import permutations
from collections import Counter

BET_TYPES = ('EXACTA', 'TRIO', 'TRIFECTA')
SIZE = {'EXACTA': 2, 'TRIO': 3, 'TRIFECTA': 3}
PROFILE = 'KM-LOCAL-B1-NONBUY-TRACE-v1 (evidence only; tickets unchanged)'


def _norm(tickets):
    out = []
    for t in tickets or []:
        if isinstance(t, dict):
            bt, sel = t.get('bet_type'), t.get('selection') or []
        else:
            bt, sel = t
        try:
            out.append((bt, tuple(int(x) for x in sel)))
        except (TypeError, ValueError):
            continue
    return out


def _stakes(tickets):
    out = []
    for t in tickets or []:
        st = 100
        if isinstance(t, dict):
            try:
                st = int(t.get('stake') or 100)
            except (TypeError, ValueError):
                st = 100
        out.append(st)
    return out


def _with_stake(tickets):
    n = _norm(tickets)
    if len(n) != len(tickets or []):   # 読めない券があった：投資額は 100 円/点で数える
        return [(b, sel, 100) for b, sel in n]
    return [(b, sel, st) for (b, sel), st in zip(n, _stakes(tickets))]


def _order_uncertainty(order, full, kept):
    w, s, t = order[:3]
    out = {}
    for bt, horses in (('EXACTA', (w, s)), ('TRIFECTA', (w, s, t))):
        actual = tuple(horses)
        others = {p for p in permutations(horses) if p != actual}
        def look(tks):
            sels = {tuple(sel) for b, sel in tks if b == bt}
            return actual in sels, sorted(list(p) for p in others & sels)
        a_k, o_k = look(kept)
        a_f, o_f = look(full)
        code = ('ACTUAL_AND_OTHER' if a_k and o_k else 'ACTUAL_ONLY' if a_k else
                'OTHER_ONLY' if o_k else 'NONE')
        out[bt] = {'kept': code, 'actual_in_full': a_f, 'other_orders_full': len(o_f),
                   'other_orders_kept': o_k}
    return out


def _head_continuity(order, roles, full, kept):
    out = {}
    for h, rs in sorted(roles.items()):
        if 'W' not in rs:
            continue
        def cnt(tks, bt):
            return sum(1 for b, sel in tks if b == bt and sel and sel[0] == h)
        pf, pk = cnt(full, 'EXACTA'), cnt(kept, 'EXACTA')
        tf, tk = cnt(full, 'TRIFECTA'), cnt(kept, 'TRIFECTA')
        term = ('HEAD_PURCHASED' if pk + tk else 'HEAD_BUDGET_COMPRESSED' if pf + tf else 'HEAD_NOT_GENERATED')
        out[str(h)] = {'is_winner': bool(order) and order[0] == h, 'exacta_full': pf, 'exacta_kept': pk,
                       'trifecta_full': tf, 'trifecta_kept': tk, 'terminal': term}
    return out


def _hygiene(tickets, runners):
    """券の並び（正規化前）を見て、重複と無効な馬番を数える。"""
    rs = {int(x) for x in runners} if runners else None
    seen, dup, inv, kinds = set(), 0, 0, Counter()
    for t in tickets or []:
        if isinstance(t, dict):
            bt, sel = t.get('bet_type'), t.get('selection') or []
        else:
            bt, sel = (list(t) + [None, None])[:2]
        try:
            sel = [int(x) for x in sel or []]
        except (TypeError, ValueError):
            inv += 1
            kinds['UNPARSEABLE'] += 1
            continue
        bad = None
        if bt in SIZE and len(sel) != SIZE[bt]:
            bad = 'WRONG_SIZE'
        elif len(set(sel)) != len(sel):
            bad = 'REPEATED_HORSE'
        elif rs is not None and any(h not in rs for h in sel):
            bad = 'NOT_IN_FIELD'
        if bad:
            inv += 1
            kinds[bad] += 1
            continue
        key = (bt, tuple(sorted(sel)) if bt == 'TRIO' else tuple(sel))
        if key in seen:
            dup += 1
        seen.add(key)
    return {'tickets': len(tickets or []), 'unique_valid': len(seen), 'DUPLICATE_NORMALIZED': dup,
            'INVALID_RUNNER': inv, 'invalid_kinds': dict(kinds),
            'field_check': 'TESTED' if rs is not None else 'UNTESTED'}


def _width(roles, full, kept, kept_st):
    def side(tks, st=None):
        d = {bt: sum(1 for b, _ in tks if b == bt) for bt in BET_TYPES}
        d['total'] = len(tks)
        if st is not None:
            d['stake'] = sum(x for _, _, x in st)
        return d
    return {'roles': {r: sum(1 for v in roles.values() if r in v) for r in ('W', 'P2', 'P3')},
            'full_mec': side(full), 'delivered': side(kept, kept_st)}


def _race_no(key):
    try:
        return str(key).rsplit('_', 1)[0], int(str(key).rsplit('_R', 1)[1])
    except (IndexError, ValueError):
        return None, None


def _target(bt, order):
    w, s, t = order[:3]
    if bt == 'EXACTA':
        return (w, s)
    if bt == 'TRIFECTA':
        return (w, s, t)
    return frozenset((w, s, t))


def _contains(tks, bt, target):
    for b, sel in tks:
        if b != bt:
            continue
        key = frozenset(sel) if bt == 'TRIO' else tuple(sel)
        if key == target:
            return True
    return False


def _semantic(bt, order, roles):
    w, s, t = order[:3]
    has = lambda h, r: r in (roles.get(h) or [])
    if bt == 'TRIO':
        if not all(roles.get(h) for h in (w, s, t)):
            return 'SEMANTIC_EXCLUDED_ROLE_P3'
        return None
    if not has(w, 'W'):
        return 'SEMANTIC_EXCLUDED_ROLE_W'
    if not has(s, 'P2'):
        return 'SEMANTIC_EXCLUDED_ROLE_P2'
    if bt == 'TRIFECTA' and not has(t, 'P3'):
        return 'SEMANTIC_EXCLUDED_ROLE_P3'
    return None


def race(order, roles, full_mec, delivered, runners=None, key=None):
    """order: 実着順 [1着,2着,3着,...]、roles: {馬番: ['W','P2',...]}、full_mec / delivered: 券のリスト。
    runners: 出走馬番（任意。INVALID_RUNNER の出走表照合）、key: レースキー（任意。whiplash の並び）。"""
    order = [int(x) for x in order or []]
    if len(order) < 3:
        return None
    roles = {int(k): list(v or []) for k, v in (roles or {}).items()}
    full, kept = _norm(full_mec), _norm(delivered)
    if not full:
        full = list(kept)   # 全MECの配列が無い（PAPER 等）：上限による削除は観測できない
    per_bt = {}
    for bt in BET_TYPES:
        tgt = _target(bt, order)
        if _contains(kept, bt, tgt):
            code = 'PURCHASED'
        elif _contains(full, bt, tgt):
            code = 'BUDGET_COMPRESSED'
        elif not any(b == bt for b, _ in full):
            code = 'BET_TYPE_ABSENT'
        else:
            code = _semantic(bt, order, roles) or 'NOT_GENERATED'
        per_bt[bt] = {'terminal': code, 'axis': _axis(code)}
    horses = {}
    in_full = {h for _, sel in full for h in sel}
    in_kept = {h for _, sel in kept for h in sel}
    for h, rs in sorted(roles.items()):
        if not rs:
            continue
        horses[str(h)] = {'roles': rs, 'finish': order.index(h) + 1 if h in order else None,
                          'terminal': 'PURCHASED' if h in in_kept else 'BUDGET_COMPRESSED' if h in in_full else 'NOT_GENERATED'}
    kept_st = _with_stake(delivered)
    for k, v in horses.items():
        h = int(k)
        v['tickets_full'] = sum(1 for _, sel in full if h in sel)
        v['tickets_kept'] = sum(1 for _, sel in kept if h in sel)
        v['stake_kept'] = sum(st for _, sel, st in kept_st if h in sel)
    silent = sorted(int(h) for h, v in horses.items() if v['terminal'] != 'PURCHASED')
    return {'profile': PROFILE, 'actual_combination': per_bt,
            'role_horses': horses, 'role_horses_not_purchased': silent,
            'order_uncertainty': _order_uncertainty(order, full, kept),
            'head_continuity': _head_continuity(order, roles, full, kept),
            'full_mec_observed': bool(_norm(full_mec)),
            'ticket_hygiene': {'full_mec': _hygiene(full_mec, runners) if _norm(full_mec) else None,
                               'delivered': _hygiene(delivered, runners)},
            'width': dict(_width(roles, full, kept, kept_st), key=key),
            'note': 'CAPITAL（予算で落ちた）と SEMANTIC（予想で外した）を分けた記録。正式券面・点数・閾値は変えない'}


def _axis(code):
    if code == 'PURCHASED':
        return 'PURCHASED'
    if code == 'BUDGET_COMPRESSED':
        return 'CAPITAL'
    if code.startswith('SEMANTIC'):
        return 'SEMANTIC'
    return 'STRUCTURE'   # BET_TYPE_ABSENT / NOT_GENERATED


def aggregate(traces):
    traces = [t for t in traces if t]
    out = {'races': len(traces), 'by_bet_type': {}, 'axis': Counter(),
           'role_horse_terminal': Counter(), 'races_with_budget_compressed_hit': 0}
    for bt in BET_TYPES:
        c = Counter(t['actual_combination'][bt]['terminal'] for t in traces)
        out['by_bet_type'][bt] = dict(c)
        out['axis'].update(t['actual_combination'][bt]['axis'] for t in traces)
    for t in traces:
        out['role_horse_terminal'].update(v['terminal'] for v in t['role_horses'].values())
        if any(v['terminal'] == 'BUDGET_COMPRESSED' for v in t['actual_combination'].values()):
            out['races_with_budget_compressed_hit'] += 1
    ou = {bt: Counter() for bt in ('EXACTA', 'TRIFECTA')}
    hc, hc_win = Counter(), Counter()
    for t in traces:
        for bt, v in (t.get('order_uncertainty') or {}).items():
            ou[bt][v['kept']] += 1
        for v in (t.get('head_continuity') or {}).values():
            hc[v['terminal']] += 1
            if v['is_winner']:
                hc_win[v['terminal']] += 1
    out['order_uncertainty'] = {bt: dict(c) for bt, c in ou.items()}
    out['head_continuity'] = {'all_w': dict(hc), 'winner_w': dict(hc_win)}
    hy = Counter()
    for t in traces:
        for side, v in (t.get('ticket_hygiene') or {}).items():
            if v:
                hy[f'{side}.DUPLICATE_NORMALIZED'] += v['DUPLICATE_NORMALIZED']
                hy[f'{side}.INVALID_RUNNER'] += v['INVALID_RUNNER']
                hy[f'{side}.races_with_issue'] += int(bool(v['DUPLICATE_NORMALIZED'] or v['INVALID_RUNNER']))
    out['ticket_hygiene'] = dict(hy)
    out['width_whiplash'] = whiplash(traces)
    out['axis'] = dict(out['axis'])
    out['role_horse_terminal'] = dict(out['role_horse_terminal'])
    return out


def _hit(t):
    return any(v['terminal'] == 'PURCHASED' for v in (t.get('actual_combination') or {}).values())


def whiplash(traces):
    """同じ場で連続する2レース（R番号が1つ違い）について、前のレースの当否ごとに配信点数・全MEC点数の変化を集計。"""
    rows = []
    for t in traces:
        w = t.get('width') or {}
        v, n = _race_no(w.get('key'))
        if v is None:
            continue
        rows.append((v, n, _hit(t), w['delivered']['total'], w['full_mec']['total']))
    rows.sort()
    agg = {'AFTER_HIT': [], 'AFTER_MISS': []}
    for a, b in zip(rows, rows[1:]):
        if a[0] != b[0] or b[1] != a[1] + 1:
            continue
        agg['AFTER_HIT' if a[2] else 'AFTER_MISS'].append((b[3] - a[3], b[4] - a[4]))
    out = {'pairs': sum(len(x) for x in agg.values())}
    for k, xs in agg.items():
        out[k] = {'n': len(xs),
                  'mean_delivered_change': round(sum(d for d, _ in xs) / len(xs), 2) if xs else None,
                  'mean_abs_delivered_change': round(sum(abs(d) for d, _ in xs) / len(xs), 2) if xs else None,
                  'mean_full_mec_change': round(sum(f for _, f in xs) / len(xs), 2) if xs else None}
    out['note'] = '幅は事前に決まるはず（capital_width_precommit）。AFTER_MISS で点数が大きく動けば Anti-Whiplash の確認対象。件数が少ないうちは判断しない'
    return out
