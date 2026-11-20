"""Directional role exposure audit (evidence only; never adds, drops or re-weights a ticket).

Source: Drive 精読 2026-11-20 — 地方 I2.2 Executable Governance（第4〜6条 / Compiler v1.3 §4-6 / Runtime v1.4 §4-6,9）:
  - Directional Exposure: rebuild each horse's head / 2nd / 3rd / unordered exposure from the delivered tickets.
    "the horse appears somewhere" is not role coverage.
  - Protected Global Zero: a W / P2 / P3 role horse with total exposure 0 → flagged (here: review flag, not a block).
  - Pair-Trio Intersection: 馬単 A→B bought and 三連複 {A,B,C} bought with C a role horse, while 三連単 is also bought
    but A→B→C is absent → listed as an unmaterialized ordered third (review only).
  - Extreme Hub: more than one W but every ticket needs the same horse → hub_share 100%.
Inputs: roles {'W': [no], 'P2': [no], 'P3': [no]} and tickets [(bet_type, [combo tuples])] as in ticket_tree.
"""
ROLE_OF = {'1着候補': 'W', '2着候補': 'P2', '3着候補': 'P3'}
ORDERED = {'馬単', '三連単'}


def roles_from_order(order):
    out = {'W': [], 'P2': [], 'P3': []}
    for x in order:
        r = ROLE_OF.get(x.get('role'))
        if r:
            out[r].append(x['no'])
    return out


def audit(roles, tickets):
    role_horses = [h for k in ('W', 'P2', 'P3') for h in roles.get(k, [])]
    ex = {}

    def e(h):
        return ex.setdefault(h, {'head': 0, 'second': 0, 'third': 0, 'unordered': 0, 'single': 0, 'total': 0})

    n_multi = 0
    containing = {}
    for kind, combos in tickets:
        for c in combos:
            c = tuple(c)
            if len(c) > 1:
                n_multi += 1
                for h in set(c):
                    containing[h] = containing.get(h, 0) + 1
            for i, h in enumerate(c):
                r = e(h)
                r['total'] += 1
                if len(c) == 1:
                    r['single'] += 1
                elif kind in ORDERED:
                    r[('head', 'second', 'third')[i]] += 1
                else:
                    r['unordered'] += 1
    global_zero = [{'no': h, 'role': k} for k in ('W', 'P2', 'P3') for h in roles.get(k, [])
                   if ex.get(h, {}).get('total', 0) == 0]
    # W horses never placed at the head of an ordered ticket while ordered tickets exist
    has_ordered = any(kind in ORDERED and combos for kind, combos in tickets)
    w_no_head = [h for h in roles.get('W', []) if has_ordered and ex.get(h, {}).get('head', 0) == 0
                 and ex.get(h, {}).get('total', 0) > 0]
    # pair-trio intersection
    exacta = {tuple(c) for kind, cs in tickets if kind == '馬単' for c in cs}
    trio = {tuple(sorted(c)) for kind, cs in tickets if kind == '三連複' for c in cs}
    trifecta = {tuple(c) for kind, cs in tickets if kind == '三連単' for c in cs}
    gaps = []
    if trifecta:
        for a, b in sorted(exacta):
            for t in sorted(trio):
                if a in t and b in t:
                    c = [x for x in t if x not in (a, b)][0]
                    if c in role_horses and (a, b, c) not in trifecta:
                        gaps.append((a, b, c))
    hub = None
    if n_multi:
        h, cnt = max(containing.items(), key=lambda kv: (kv[1], -kv[0]))
        hub = {'no': h, 'share': round(cnt / n_multi, 3), 'tickets': n_multi}
    extreme_hub = bool(hub and hub['share'] == 1.0 and len(roles.get('W', [])) > 1 and n_multi > 1)
    # I2.1 §9 TRI-CAPITAL-MONOCULTURE: several W, every 三連単 needs the same horse
    tri_common = set.intersection(*[set(c) for c in trifecta]) if len(trifecta) > 1 else set()
    tri_mono = sorted(tri_common) if (tri_common and len(roles.get('W', [])) > 1) else []
    return {'exposure': ex, 'global_zero': global_zero, 'w_without_head': w_no_head,
            'pair_trio_gaps': gaps, 'hub': hub, 'extreme_hub': extreme_hub, 'tri_monoculture': tri_mono}


def line(a):
    """One-line Japanese summary for the PAPER report details."""
    p = []
    p.append('役割馬の全券種0：' + ('なし' if not a['global_zero'] else
                               '、'.join(f"{z['role']} {z['no']}" for z in a['global_zero'])))
    if a['w_without_head']:
        p.append('1着候補なのに着順指定券の頭に無い：' + '、'.join(map(str, a['w_without_head'])))
    if a['pair_trio_gaps']:
        p.append('馬単＋三連複は買っているのに三連単に無い並び：' + '／'.join('→'.join(map(str, g)) for g in a['pair_trio_gaps'][:6])
                 + (f" ほか{len(a['pair_trio_gaps']) - 6}" if len(a['pair_trio_gaps']) > 6 else ''))
    if a['hub']:
        p.append(f"最多出現 {a['hub']['no']}番（{a['hub']['share'] * 100:.0f}%／{a['hub']['tickets']}点）"
                 + ('・1着候補が複数なのに全点が同じ馬（Extreme Hub）' if a['extreme_hub'] else ''))
    if a.get('tri_monoculture'):
        p.append('三連単の全点に同じ馬（' + '・'.join(map(str, a['tri_monoculture'])) + '番、1着候補は複数）')
    return '- 役割と券面の対応（I2.2 Directional Exposure・検算のみ、買い目は変えない）：' + '／'.join(p)
