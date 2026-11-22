"""回収の頑健性の追加列（Drive 精読 B2・2026-11-23、証拠のみ）。

どの列も、配信・精算済みの券面と公式結果から事後に数えるだけで、券面・点数・予算・印は変えない。
出典（keibametrics-private-evidence drive_reading/gap_tracker.json の B2）:
  - KMS v1.3 Rev.1 Cross-Bet Redundancy Cost: 同じ骨格（同じ馬の組）を複数の券種で持つ追加投資額
  - 船橋 v2.0-FNB 第219・316条 Low-Payout Structure Sanity: 的中しても回収割れになる構造（損益分岐の倍率）
  - 大井 v2.3-OHI 第315〜316条 Set/Order の分離: 三連複の組は当たり三連単の着順は外れ、を別に数える
  - 地方 FORMAL-PRE-RACE Rev16 27節 Protection Burden Ratio: PROTECTION 層の資金 / 総資金
  - 地方 2026-11-21 全35R反省 P1-3: 的中赤字（的中したのに収支マイナス）
  - Drive「福島競馬場コース攻略」（n258）: 荒れ度の層ごとに PFS と的中赤字率を分けて出す。
    発走前の層は締切前に固定した出馬表の1番人気の単勝オッズ（2.0倍未満=SOLID／4.0倍未満=MID／それ以上=OPEN）、
    結果の層は三連複の払戻（1,000円以下=LOW／10,000円以下=MID／それ超=HIGH）。
"""
from collections import defaultdict

UNORDERED = {'TRIO', 'QUINELLA', 'WIDE', 'PLACE', 'BRACKET_QUINELLA'}
ORDERED = {'EXACTA', 'TRIFECTA', 'WIN'}
PRIMARY = {3: 'TRIO', 2: 'QUINELLA'}      # 同じ骨格の「基本の券種」。これ以外の券種で同じ組を持つ分を追加投資と数える
UNIT = 100
PRE_LAYERS = ((2.0, 'SOLID'), (4.0, 'MID'))       # 1番人気の単勝オッズ（締切前固定）
RESULT_LAYERS = ((1000, 'LOW'), (10000, 'MID'))   # 三連複の払戻（100円あたり）


def roughness(fav_odds, payouts):
    """荒れ度の層（n258、証拠のみ）。fav_odds: 締切前に固定した1番人気の単勝オッズ。"""
    pre = None
    if fav_odds:
        pre = next((name for lim, name in PRE_LAYERS if float(fav_odds) < lim), 'OPEN')
    trio = [int(v) for v in ((payouts or {}).get('TRIO') or {}).values() if v]
    res = next((name for lim, name in RESULT_LAYERS if max(trio) <= lim), 'HIGH') if trio else None
    return {'pre_race': pre, 'fav_odds': float(fav_odds) if fav_odds else None,
            'result': res, 'trio_payout': max(trio) if trio else None}


def _key(bt, sel):
    return '-'.join(map(str, sorted(sel) if bt in UNORDERED else sel))


def race(tickets, order, payouts=None, effective_invest=None, payout=None, fav_odds=None):
    """tickets: [{'bet_type', 'selection':[int], 'stake':int, 'tier':str|None}] (delivered set only).
    order: official finishing order. payouts: {'TRIO': {'4-8-14': 2120}, ...} (per 100 yen)."""
    order = [int(x) for x in order or []]
    payouts = payouts or {}
    total = sum(int(t.get('stake') or UNIT) for t in tickets)
    # 1) 券種をまたぐ同一骨格
    groups = defaultdict(list)
    for t in tickets:
        sel = [int(x) for x in t['selection']]
        if len(sel) in (2, 3):
            groups[(len(sel), frozenset(sel))].append(t)
    multi, extra = 0, 0
    for (n, _), ts in groups.items():
        kinds = {t['bet_type'] for t in ts}
        if len(kinds) < 2:
            continue
        multi += 1
        prim = PRIMARY[n] if PRIMARY[n] in kinds else sorted(kinds)[0]
        extra += sum(int(t.get('stake') or UNIT) for t in ts if t['bet_type'] != prim)
    # 2) Protection Burden Ratio（tier が券面に書かれているときだけ）
    tiers = [t.get('tier') for t in tickets]
    tier_stake = defaultdict(int)
    for t in tickets:
        tier_stake[t.get('tier') or 'UNKNOWN'] += int(t.get('stake') or UNIT)
    prot = (round(sum(int(t.get('stake') or UNIT) for t in tickets if t.get('tier') == 'PROTECTION') / total, 3)
            if total and all(tiers) else None)        # 一部でも層が不明なら出さない（自動昇格の券面は層を持たない）
    # 3) Set / Order の分離と券種別の収支
    w3 = order[:3]
    trio_bought = any(t['bet_type'] == 'TRIO' for t in tickets)
    tri_bought = any(t['bet_type'] == 'TRIFECTA' for t in tickets)
    set_hit = len(w3) == 3 and any(t['bet_type'] in ('TRIO', 'TRIFECTA') and len(t['selection']) == 3
                                   and frozenset(map(int, t['selection'])) == frozenset(w3) for t in tickets)
    order_hit = len(w3) == 3 and any(t['bet_type'] == 'TRIFECTA' and [int(x) for x in t['selection']] == w3
                                     for t in tickets)
    set_order = ('NOT_BOUGHT' if not (trio_bought or tri_bought) else 'BOTH' if order_hit
                 else 'SET_ONLY' if set_hit else 'NONE')
    by_type = defaultdict(lambda: {'points': 0, 'stake': 0, 'payout': 0})
    for t in tickets:
        bt, st = t['bet_type'], int(t.get('stake') or UNIT)
        b = by_type[bt]
        b['points'] += 1
        b['stake'] += st
        pay = (payouts.get(bt) or {}).get(_key(bt, [int(x) for x in t['selection']]))
        if pay:
            b['payout'] += int(pay) * st // UNIT
    for b in by_type.values():
        b['pfs'] = round(100 * b['payout'] / b['stake'], 1) if b['stake'] else None
    # 5) 同じ点数を無作為に選んだときの期待払戻（ヌルモデル、Drive「確率シミュレーション大学」第3・7・8講）：
    #    券種ごとに 点数 / 全組合せ数 × その券種の払戻合計。出走頭数は着順の頭数（取消は除かれる）
    nf = len(order)
    combos = {'WIN': nf, 'PLACE': nf, 'QUINELLA': nf * (nf - 1) // 2, 'WIDE': nf * (nf - 1) // 2,
              'EXACTA': nf * (nf - 1), 'TRIO': nf * (nf - 1) * (nf - 2) // 6, 'TRIFECTA': nf * (nf - 1) * (nf - 2)}
    rnd, rnd_ok = 0.0, bool(by_type)
    for k, b in by_type.items():
        c = combos.get(k)
        if not c or k not in payouts:
            rnd_ok = False
            continue
        rnd += b['points'] / c * sum(int(v) for v in payouts[k].values()) * (b['stake'] / b['points']) / UNIT
    # 4) 低配当構造：1点の的中で収支が合うのに必要な倍率と、実際の的中の倍率
    eff = total if effective_invest is None else effective_invest
    pay = sum(b['payout'] for b in by_type.values()) if payout is None else payout
    return {
        'points': len(tickets), 'stake': total,
        'cross_bet_redundancy': {'skeletons_in_two_or_more_bet_types': multi, 'extra_stake': extra,
                                 'extra_share': round(extra / total, 3) if total else None},
        'protection_burden_ratio': prot, 'stake_by_tier': dict(tier_stake),
        'set_order': set_order,
        'by_bet_type': {k: dict(v) for k, v in sorted(by_type.items())},
        'low_payout': {'break_even_multiple': round(eff / UNIT, 1) if eff else None,
                       'hit': bool(pay), 'hit_multiple': round(pay / UNIT, 1) if pay else None,
                       'hit_but_loss': bool(pay and eff and pay < eff)},
        'random_same_points': {'expected_payout': round(rnd) if rnd_ok else None, 'field': nf},
        'roughness': dict(roughness(fav_odds, payouts), effective_invest=eff, payout=pay),
        'evidence_only': True,
    }


def aggregate(rows):
    """rows: list of race() outputs (None skipped). Sums for the daily / period summary."""
    rows = [r for r in rows if r]
    if not rows:
        return None
    stake = sum(r['stake'] for r in rows)
    extra = sum(r['cross_bet_redundancy']['extra_stake'] for r in rows)
    pb = [(r['protection_burden_ratio'], r['stake']) for r in rows if r['protection_burden_ratio'] is not None]
    so = defaultdict(int)
    bt = defaultdict(lambda: {'points': 0, 'stake': 0, 'payout': 0})
    for r in rows:
        so[r['set_order']] += 1
        for k, v in r['by_bet_type'].items():
            for f in ('points', 'stake', 'payout'):
                bt[k][f] += v[f]
    for v in bt.values():
        v['pfs'] = round(100 * v['payout'] / v['stake'], 1) if v['stake'] else None
    hits = [r for r in rows if r['low_payout']['hit']]
    rr = [r for r in rows if (r.get('random_same_points') or {}).get('expected_payout') is not None]
    rs = sum(r['stake'] for r in rr)
    act = sum(sum(v['payout'] for v in r['by_bet_type'].values()) for r in rr)
    lay = {'pre_race': defaultdict(lambda: {'races': 0, 'invest': 0, 'payout': 0, 'hit_races': 0, 'hit_but_loss_races': 0}),
           'result': defaultdict(lambda: {'races': 0, 'invest': 0, 'payout': 0, 'hit_races': 0, 'hit_but_loss_races': 0})}
    for r in rows:
        rg = r.get('roughness') or {}
        for dim in ('pre_race', 'result'):
            b = lay[dim][rg.get(dim) or 'UNKNOWN']
            b['races'] += 1
            b['invest'] += rg.get('effective_invest') or 0
            b['payout'] += rg.get('payout') or 0
            b['hit_races'] += bool(r['low_payout']['hit'])
            b['hit_but_loss_races'] += bool(r['low_payout']['hit_but_loss'])
    by_rough = {dim: {k: dict(v, pfs=round(100 * v['payout'] / v['invest'], 1) if v['invest'] else None,
                              hit_but_loss_rate=round(v['hit_but_loss_races'] / v['hit_races'], 3) if v['hit_races'] else None)
                      for k, v in sorted(d.items())} for dim, d in lay.items()}
    return {'races': len(rows), 'stake': stake, 'by_roughness': by_rough,
            'cross_bet_extra_stake': extra, 'cross_bet_extra_share': round(extra / stake, 3) if stake else None,
            'protection_burden_ratio': round(sum(p * s for p, s in pb) / sum(s for _, s in pb), 3) if pb else None,
            'protection_races': len(pb),
            'set_order': dict(so), 'by_bet_type': {k: dict(v) for k, v in sorted(bt.items())},
            'hit_races': len(hits), 'hit_but_loss_races': sum(1 for r in hits if r['low_payout']['hit_but_loss']),
            'random_same_points': {'races': len(rr), 'pfs': round(100 * sum(r['random_same_points']['expected_payout'] for r in rr) / rs, 1) if rs else None,
                                   'actual_pfs_same_races': round(100 * act / rs, 1) if rs else None},
            'mean_break_even_multiple': round(sum(r['low_payout']['break_even_multiple'] or 0 for r in rows) / len(rows), 1),
            'evidence_only': True}


def line(a):
    if not a:
        return '- 回収の頑健性（B2・証拠のみ）：対象なし'
    bt = '／'.join(f"{k} {v['points']}点 PFS {v['pfs']}%" for k, v in a['by_bet_type'].items())
    so = a['set_order']
    return (f"- 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 {a['cross_bet_extra_stake']:,}円"
            f"（{(a['cross_bet_extra_share'] or 0) * 100:.1f}%）／保護層の資金比率 {a['protection_burden_ratio']}"
            f"（{a['protection_races']}R）／組だけ的中（三連単は外れ）{so.get('SET_ONLY', 0)}R・着順まで的中 {so.get('BOTH', 0)}R"
            f"／的中 {a['hit_races']}R のうち的中赤字 {a['hit_but_loss_races']}R／損益分岐の倍率 平均 {a['mean_break_even_multiple']}倍"
            f"／同じ点数を無作為に選んだ場合の期待PFS {(a.get('random_same_points') or {}).get('pfs')}%（同じ{(a.get('random_same_points') or {}).get('races')}Rの実績 {(a.get('random_same_points') or {}).get('actual_pfs_same_races')}%）"
            f"／券種別 {bt}"
            + ('／荒れ度（発走前・1番人気オッズ）' + '／'.join(f"{k} {v['races']}R PFS {v['pfs']}% 的中赤字 {v['hit_but_loss_races']}/{v['hit_races']}"
                                             for k, v in (a.get('by_roughness') or {}).get('pre_race', {}).items())
               if a.get('by_roughness') else ''))
