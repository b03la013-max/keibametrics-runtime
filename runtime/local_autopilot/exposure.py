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
    # I2.3 第4・8条 Reverse Bridge / Topology Divergence: a bought 三連複 holds a W→P2 order
    # that no 馬単 / 三連単 (first two) covers, while ordered tickets are bought at all
    first_two = exacta | {c[:2] for c in trifecta}
    divergence = []
    if first_two:
        for t in sorted(trio):
            for a in roles.get('W', []):
                for b in roles.get('P2', []) + [w for w in roles.get('W', []) if w != a]:
                    if a in t and b in t and (a, b) not in first_two and (a, b) not in divergence:
                        divergence.append((a, b))
    hub = None
    if n_multi:
        h, cnt = max(containing.items(), key=lambda kv: (kv[1], -kv[0]))
        hub = {'no': h, 'share': round(cnt / n_multi, 3), 'tickets': n_multi}
    extreme_hub = bool(hub and hub['share'] == 1.0 and len(roles.get('W', [])) > 1 and n_multi > 1)
    # I2.1 §9 TRI-CAPITAL-MONOCULTURE: several W, every 三連単 needs the same horse
    tri_common = set.intersection(*[set(c) for c in trifecta]) if len(trifecta) > 1 else set()
    tri_mono = sorted(tri_common) if (tri_common and len(roles.get('W', [])) > 1) else []
    cells = cell_coverage(roles, exacta, trifecta)
    return {'exposure': ex, 'global_zero': global_zero, 'w_without_head': w_no_head,
            'pair_trio_gaps': gaps, 'hub': hub, 'extreme_hub': extreme_hub, 'tri_monoculture': tri_mono,
            'trio_order_divergence': divergence, 'cells': cells}


def cell_coverage(roles, exacta, trifecta):
    """船橋 v2.0-FNB 第302・307・308・311条（Execution Compiler の Expected Cell Set、Pair Breadth／Depth）の検算。
    Expected pair cells = every W head × (P2 ∪ other W) second.  A cell is "bought" if some 馬単 or 三連単 has it as
    its first two.  For every bought ordered pair, depth = number of role horses bought as its 三連単 third.
    Evidence only: 『買わない』は許されるが『存在しない』は許されない — this lists the absent cells, it never adds one."""
    W, P2, P3 = roles.get('W', []), roles.get('P2', []), roles.get('P3', [])
    if not (exacta or trifecta):
        return None
    first_two = set(exacta) | {c[:2] for c in trifecta}
    expected = [(a, b) for a in W for b in P2 + W if b != a]
    expected = list(dict.fromkeys(expected))
    missing = [c for c in expected if c not in first_two]
    depth = {}
    if trifecta:
        role_set = set(W) | set(P2) | set(P3)
        for a, b in sorted(first_two):
            thirds = {c[2] for c in trifecta if c[:2] == (a, b)}
            depth[(a, b)] = len(thirds & role_set)
    zero_depth = [k for k, v in depth.items() if v == 0 and k in set(exacta)]
    # ばんえい v3.7-BAN Rev.1（帯広 2026-09-06 6R・7R 反省）：Third は馬単体ではなく並びごとに見る。
    # 馬単で買った並び A→B について、3着候補（P3、と W/P2）の馬 C が A→B→C に無いのに、別の並びの三連単では
    # 3着に買われている＝「別の並びで買ったから補償済み」とみなしてしまう形（Cross-Pair Compensation）を列挙する。
    cross_pair = []
    if trifecta:
        third_any = {c[2] for c in trifecta}
        cand = list(dict.fromkeys(P3 + P2 + W))
        for a, b in sorted(set(exacta)):
            thirds = {c[2] for c in trifecta if c[:2] == (a, b)}
            for h in cand:
                if h not in (a, b) and h not in thirds and h in third_any:
                    cross_pair.append((a, b, h))
    return {'expected': len(expected), 'bought': len(expected) - len(missing), 'missing': missing,
            'breadth': len(first_two), 'depth': depth, 'exacta_zero_depth': zero_depth,
            'cross_pair_third': cross_pair}


MC_ORDER = ('NEW_HEAD_PATH', 'NEW_PAIR', 'NEW_SET', 'NEW_THIRD', 'NEW_ORDER', 'STRUCTURAL_PROTECTION', 'REDUNDANT')
MC_JA = {'NEW_HEAD_PATH': '新しい1着', 'NEW_PAIR': '新しい1-2着の並び', 'NEW_SET': '新しい3頭の組',
         'NEW_THIRD': '既存の並びに新しい3着', 'NEW_ORDER': '既存の3頭の新しい着順',
         'STRUCTURAL_PROTECTION': '他券の保険', 'REDUNDANT': '他券で完全に重複'}


def marginal(tickets):
    """大井 v2.3-OHI 第326・329条（v2.0 第227条、v1.8 第150条 Portfolio Efficiency）の検算：
    each delivered ticket is labelled by what it adds that the OTHER delivered tickets do not already hold
    (NEW_HEAD_PATH / NEW_PAIR / NEW_SET / NEW_THIRD / NEW_ORDER / STRUCTURAL_PROTECTION / REDUNDANT), plus the
    points per bet type (= capital share at the flat 100-yen stake).  REDUNDANT is strict: every finish the ticket
    hits is already hit by other tickets (三連複 with all 6 三連単 orders, 馬連 with both 馬単 orders, a duplicate).
    Evidence only — REDUNDANT is not forbidden and nothing is added, removed or re-weighted."""
    items = [(kind, tuple(c)) for kind, combos in tickets for c in combos]
    by_kind = {}
    for kind, c in items:
        by_kind[kind] = by_kind.get(kind, 0) + 1
    total = len(items)
    out = []
    seen = set()
    for i, (kind, c) in enumerate(items):
        others = items[:i] + items[i + 1:]
        key = (kind, tuple(sorted(c)) if kind in ('三連複', '馬連', 'ワイド', '複勝') else c)
        if key in seen:
            out.append((kind, c, 'REDUNDANT'))
            continue
        seen.add(key)
        o_heads = {x[0] for k, x in others if k in ORDERED or k == '単勝'}
        o_pairs = {x[:2] for k, x in others if k in ORDERED and len(x) >= 2}
        o_upairs = {frozenset(x[:2]) for k, x in others if len(x) >= 2 and k in ('馬連', 'ワイド')} | \
                   {frozenset(p) for k, x in others if k == '三連複' for p in ((x[0], x[1]), (x[0], x[2]), (x[1], x[2]))}
        o_sets = {frozenset(x) for k, x in others if len(x) == 3}
        o_tri = {x for k, x in others if k == '三連単'}
        o_ex = {x for k, x in others if k == '馬単'}
        if kind == '三連複':
            perms = {(a, b, d) for a in c for b in c for d in c if len({a, b, d}) == 3}
            cls = 'REDUNDANT' if perms <= o_tri else ('NEW_SET' if frozenset(c) not in o_sets else 'STRUCTURAL_PROTECTION')
        elif kind == '馬連':
            a, b = c
            cls = 'REDUNDANT' if {(a, b), (b, a)} <= o_ex else (
                'NEW_PAIR' if frozenset(c) not in o_upairs and (a, b) not in o_pairs and (b, a) not in o_pairs
                else 'STRUCTURAL_PROTECTION')
        elif kind == '馬単':
            a, b = c
            cls = ('NEW_HEAD_PATH' if a not in o_heads else
                   'NEW_PAIR' if (a, b) not in o_pairs and frozenset(c) not in o_upairs else 'STRUCTURAL_PROTECTION')
        elif kind == '三連単':
            a, b, d = c
            cls = ('NEW_HEAD_PATH' if a not in o_heads else
                   'NEW_PAIR' if (a, b) not in o_pairs else
                   'NEW_ORDER' if frozenset(c) in o_sets else 'NEW_THIRD')
        elif kind == '単勝':
            cls = 'NEW_HEAD_PATH' if c[0] not in o_heads else 'STRUCTURAL_PROTECTION'
        else:                                   # ワイド・複勝: wider hit sets, never strictly covered here
            cls = 'STRUCTURAL_PROTECTION' if any(set(c) <= set(x) for k, x in others) else 'NEW_PAIR' if len(c) == 2 else 'NEW_HEAD_PATH'
        out.append((kind, c, cls))
    counts = {k: 0 for k in MC_ORDER}
    for _, _, cls in out:
        counts[cls] += 1
    layer = {k: {'points': n, 'share': round(n / total, 3)} for k, n in by_kind.items()} if total else {}
    return {'tickets': out, 'counts': counts, 'layer': layer, 'total': total}


def marginal_line(m):
    if not m['total']:
        return '- 券ごとの追加分（大井 v2.3 第329条・検算のみ）：券なし'
    lay = '／'.join(f"{k} {v['points']}点（{v['share'] * 100:.0f}%）" for k, v in m['layer'].items())
    cnt = '／'.join(f"{MC_JA[k]} {m['counts'][k]}" for k in MC_ORDER if m['counts'][k])
    return f'- 券種の配分と券ごとの追加分（大井 v2.3 第326・329条・検算のみ、買い目は変えない）：{lay}。{cnt}'


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
    if a.get('trio_order_divergence'):
        p.append('三連複にある1着候補→2着候補の並びが馬単・三連単の1-2着に無い：'
                 + '／'.join('→'.join(map(str, g)) for g in a['trio_order_divergence'][:6]))
    if a.get('tri_monoculture'):
        p.append('三連単の全点に同じ馬（' + '・'.join(map(str, a['tri_monoculture'])) + '番、1着候補は複数）')
    c = a.get('cells')
    if c and c['expected']:
        t = f"1着候補×2着候補の並び {c['bought']}/{c['expected']}"
        if c['missing']:
            t += '（無い並び：' + '／'.join('→'.join(map(str, m)) for m in c['missing'][:6]) + (
                f" ほか{len(c['missing']) - 6}" if len(c['missing']) > 6 else '') + '）'
        if c['exacta_zero_depth']:
            t += '・馬単で買った並びに三連単の3着が無い：' + '／'.join('→'.join(map(str, m)) for m in c['exacta_zero_depth'][:6])
        if c.get('cross_pair_third'):
            cp = c['cross_pair_third']
            t += '・別の並びでは3着に買っているが馬単の並びの3着に無い（ばんえい v3.7 Pair-local Third）：' + '／'.join(
                '→'.join(map(str, m)) for m in cp[:6]) + (f" ほか{len(cp) - 6}" if len(cp) > 6 else '')
        p.append(t)
    return '- 役割と券面の対応（I2.2 Directional Exposure・検算のみ、買い目は変えない）：' + '／'.join(p)
