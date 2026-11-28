"""KeibaMetrics BAN ticket compiler — v4.0-BAN spec 第4章・第5章.

Order is irreversible (v3.7 Rev.2 'Universe First, Capital Second, Rendered Truth Last'):
 1 role inventory  2 every W gets a head terminal  3 Head x P2 terminal  4 Pair x Third terminal
 5 canonical universe freeze  6 per-ticket-type capital  7 compression from weak duplicates
 8 bidirectional closure (Pair+Trio -> Exact, Exact -> Pair)  9 mechanical expansion = truth.
Owner policy: 三連複 + 三連単, every race, cap 30 unique points (3,000円) per race.
"""
from itertools import combinations, permutations

CAP_TOTAL = 30
EXACT_RULE = None               # production None（1着固定）; shadow: 'BY_W'（正本 BAN-TAG: W1頭→1-3-5、2頭→2-3-4、3頭以上→三連単なし）/'2HEAD'（常に上位W2頭を頭に 2-3-4）
EXACTA_PRODUCTION_READY = False  # 馬単の本番対応（発走前オッズ・券面ツリー・精算・FORMAL）が入ったら True。registry はそれまで SINGLE_MODE を昇格させない
SINGLE_MODE = None              # production None（三連複・三連単のまま）。shadow 'A'/'B'/'C'：馬単・三連単主戦／三連複保険（Owner 2026-11-28 21:46、同じ30点）
# 同じ30点の配分（2026-11-28 事前固定の研究用。本番の購入方針ではない）: (馬単, 三連単, 三連複) の上限
SINGLE_BUDGET = {'A': (12, 8, 10), 'B': (6, 16, 8), 'PROTECT': (8, 8, 14)}
EXACT_PICK = None               # production None; shadow 'UNIVERSE': 同じ点数のまま三連単を W×P2×P3 の全組合せから強い順に選ぶ（◎頭固定をやめる）
TRIO_FILL = None                # production None; shadow True: 圧縮後に上限30点に満たなければ、役割の全組合せ（W×P2×P3）の三連複を強い順に足す（EXACT_BY_W の「三連単なし→30点は三連複へ」を同じ30点で測る、2026-11-28 反省会）
FORCE_TRIO_AXIS = None          # production None; challengers AXIS2 sets 2 (◎○2頭軸＋◎抜き○ライン)                      # Owner 2026-11-18 (= v2.2-BAN 標準型 総実点数30)
UNIT = 100


def shape(asi, aki):
    """BAN-CAP (v2.2 第73条) + 三連複の考え方. Returns (label, trio_shape, exact_shape)."""
    if asi >= 80 and aki <= 39:
        return 'SELECT', (1, 2, 4), (1, 3, 5)
    if asi >= 65:
        return 'STANDARD', (1, 2, 6), (1, 3, 5)
    if asi >= 50:
        return 'UPSET-GUARD', (2, 3, 7), (2, 3, 4)
    return 'LOW-CONFIDENCE', (2, 3, 7), None          # 三連単不発動 (BAN-TAG / BAN-JDA)


def _col(order, k, exclude=()):
    return [h for h in order if h not in exclude][:k]


def compile_race(ev):
    rows = {r['no']: r for r in ev['rows']}
    nos = list(rows)
    win = [r['no'] for r in sorted(ev['rows'], key=lambda r: r['win_rank'])]
    place = [r['no'] for r in sorted(ev['rows'], key=lambda r: r['place_rank'])]
    hole = [r['no'] for r in sorted(ev['rows'], key=lambda r: r['hole_rank'])]
    honmei = ev['honmei']
    label, tshape, eshape = shape(ev['asi'], ev['aki'])
    if EXACT_RULE and eshape:                                     # shadow only (production None)
        nw = sum(1 for n in win if rows[n]['role_w'] in ('STRONG', 'CONDITIONAL'))
        if EXACT_RULE == 'BY_W':
            eshape = (1, 3, 5) if nw <= 1 else (2, 3, 4) if nw == 2 else None
        elif EXACT_RULE == '2HEAD':
            eshape = (2, 3, 4)
    if FORCE_TRIO_AXIS and tshape and tshape[0] < FORCE_TRIO_AXIS:     # shadow only (production None)
        tshape = (FORCE_TRIO_AXIS,) + tuple(tshape[1:])

    # 1-5: role-valid universe (all legal cells) and its frozen terminal ledger
    W = [n for n in win if rows[n]['role_w']]
    P2 = [n for n in place if rows[n]['role_p2']]
    P3 = [n for n in nos if rows[n]['role_p3']] or nos
    universe_exact = [(a, b, c) for a in W for b in P2 for c in P3 if len({a, b, c}) == 3]
    universe_trio = sorted({tuple(sorted(x)) for x in universe_exact})

    # 6: 三連複 formation (axis order: honmei first, then win/place order; ◎○ two-axis keeps ○ lines)
    a_n, b_n, c_n = tshape
    axis = [honmei] + _col(win, a_n - 1, (honmei,))
    second = _col([honmei] + place, b_n, ()) if a_n == 1 else _col(place, b_n, axis) + axis
    second = list(dict.fromkeys(axis + second))[:max(b_n, len(axis)) + (0 if a_n == 1 else 1)]
    second = second + [n for n in place if rows[n].get('phv') and n not in second]   # 4-19 PHV-B: 2列目にも配置
    third = list(dict.fromkeys(second + _col(place + hole, c_n + 2)))
    trio = set()
    for x in axis:
        for y in second:
            for z in third:
                if len({x, y, z}) == 3:
                    trio.add(tuple(sorted((x, y, z))))
    if a_n == 2 and len(axis) == 2:
        # 2頭軸の是正: ◎が着外でも○から拾う → ○ x 2列目 x 3列目 (without ◎) is kept explicitly
        o = axis[1]
        for y in second:
            for z in third:
                if len({o, y, z}) == 3 and honmei not in (y, z):
                    trio.add(tuple(sorted((o, y, z))))

    # 6: 三連単 (only when the 1st column converges; BAN-TAG)
    exact = []
    if eshape:
        e1, e2, e3 = eshape
        heads = [n for n in win if rows[n]['role_w'] in ('STRONG', 'CONDITIONAL')][:e1] or [honmei]
        if honmei not in heads:
            heads = [honmei] + heads[:e1 - 1]
        seconds = _col(place, e2 + len(heads), ())
        thirds = _col(place + hole, e3 + len(heads) + 1, ())
        exact = [(a, b, c) for a in heads for b in seconds for c in thirds if len({a, b, c}) == 3]
        if EXACT_PICK == 'UNIVERSE' and exact:                    # shadow only: same point count, chosen from the universe
            strength = lambda c: (rows[c[0]]['win_rank'] + rows[c[1]]['place_rank'] + rows[c[2]]['place_rank'],
                                  rows[c[0]]['win_rank'], c)
            exact = sorted(universe_exact, key=strength)[:len(exact)] or exact

    # 8: bidirectional closure — every bought exact's trio is in 三連複 (BAN-EPRC / CTFP),
    #    and Pair+Trio -> Exact candidates are marked PESS-U when the trio is unique for that head.
    for e in exact:
        trio.add(tuple(sorted(e)))
    pess_u = set()
    for e in exact:
        same_head = [x for x in exact if x[0] == e[0] and set(x) == set(e)]
        if len(same_head) == 1:
            pess_u.add(e)

    # BAN-HAC / BAN-HSC: each S3H hole horse gets one representative trio (◎ + best partner + hole)
    protected = set()
    partner = next((n for n in place if n != honmei), None)
    for h in ev['s3h']:
        if partner and not any(h in t for t in trio):
            t = tuple(sorted((honmei, partner, h)))
            if len(set(t)) == 3:
                trio.add(t)
                protected.add(t)

    # 7: compression to the cap — weak duplicates first (BAN-PRN / BAN-CRP / BAN-MCSS)
    weight = lambda c: sum(rows[n]['place_rank'] for n in c)          # larger = weaker
    removed = []
    def total():
        return len(trio) + len(exact)
    # (a) 三連単: thin third branches that duplicate a head already covered, never PESS-U of honmei line
    for e in sorted(exact, key=lambda c: (-rows[c[2]]['place_rank'], -rows[c[1]]['place_rank'])):
        if total() <= CAP_TOTAL:
            break
        if e in pess_u and e[0] == honmei and rows[e[1]]['place_rank'] <= 3:
            continue
        exact.remove(e)
        removed.append(('三連単', e, 'REDUNDANT-THIN-THIRD'))
    # (b) 三連複: drop the weakest combos that do not contain honmei or the ○ axis
    keep = set(axis)
    for t in sorted(trio, key=lambda c: -weight(c)):
        if total() <= CAP_TOTAL:
            break
        if t in protected or (keep & set(t) and any(tuple(sorted(e)) == t for e in exact)):
            continue                                             # hole link / closure backing an exact
        trio.discard(t)
        removed.append(('三連複', t, 'LOW-MATERIALITY'))
    # (c) last resort: stop 三連単 entirely (BAN-PRN 6)
    while total() > CAP_TOTAL and exact:
        e = exact.pop()
        removed.append(('三連単', e, 'CAP-STOP-EXACT'))
    if TRIO_FILL:                                                  # shadow only (production None)
        roled = sorted(set(W) | set(P2) | set(P3))                # 役割のある馬だけ（W×P2×P3 → 役割馬3頭の組の順）
        extra = sorted(set(combinations(roled, 3)) - set(universe_trio), key=lambda c: (weight(c), c))
        for t in sorted(universe_trio, key=lambda c: (weight(c), c)) + extra:
            if total() >= CAP_TOTAL:
                break
            trio.add(tuple(t))

    # terminal ledger: every W has a head terminal; every BUY P3 appears somewhere or has a reason
    terminal = {}
    for n in W:
        in_exact = any(e[0] == n for e in exact)
        in_trio = any(n in t for t in trio)
        terminal[n] = ('HEAD-PURCHASED' if in_exact else 'HEAD-COMPENSATED-TRIO' if in_trio
                       else 'HEAD-REASONED-ZERO:CAP')
    hole_link = {n: any(n in t for t in trio) or any(n in e for e in exact) for n in ev['s3h']}
    trio_l = sorted(trio, key=lambda c: (weight(c), c))
    gates = {
        'G-ROLE': 'PASS' if all(v != 'UNRESOLVED' for v in terminal.values()) else 'FAIL',
        'G-CONNECT': 'PASS' if all(tuple(sorted(e)) in trio for e in exact) else 'FAIL',
        'G-FREEZE': 'PASS' if universe_trio else 'FAIL',
        'G-CAPITAL': 'PASS' if len(trio_l) + len(exact) <= CAP_TOTAL else 'FAIL',
        'G-HOLE': 'PASS' if all(hole_link.values()) else 'GUARDED',
    }
    if SINGLE_MODE:                                                    # shadow only
        trio_l, exact, exacta, single = _single_alloc(ev, rows, trio_l, exact)
        out = {'shape': label, 'trio_shape': tshape, 'exact_shape': eshape, 'axis': axis, 'second': second, 'third': third,
               'trio': trio_l, 'exact': exact, 'exacta': exacta, 'single': single, 'removed': removed,
               'pess_u': sorted(pess_u), 'terminal': terminal, 'hole_link': hole_link, 'gates': gates,
               'universe': {'trio': len(universe_trio), 'exact': len(universe_exact)},
               'exposure': _exposure(trio_l, exact),
               'points': len(trio_l) + len(exact) + len(exacta), 'stake': (len(trio_l) + len(exact) + len(exacta)) * UNIT,
               'formality': 'REFERENCE-RENDERED'}
        return out
    return {'shape': label, 'trio_shape': tshape, 'exact_shape': eshape,
            'axis': axis, 'second': second, 'third': third,
            'trio': trio_l, 'exact': exact, 'removed': removed, 'pess_u': sorted(pess_u),
            'terminal': terminal, 'hole_link': hole_link, 'gates': gates,
            'universe': {'trio': len(universe_trio), 'exact': len(universe_exact)},
            'exposure': _exposure(trio_l, exact),
            'points': len(trio_l) + len(exact), 'stake': (len(trio_l) + len(exact)) * UNIT,
            'formality': 'FORMAL' if all(v in ('PASS', 'GUARDED', 'NOT-APPLICABLE') for v in gates.values())
            else 'REFERENCE-RENDERED'}


def _single_alloc(ev, rows, base_trio, base_exact):
    """馬単・三連単を主戦、三連複を保険にした同じ30点の配分（SINGLE_MODE の影の候補だけ）。

    予想（印・役割・順位）は本番と同じものを使い、券面だけを組み替える。
    - 1着候補: W（role_w）を勝ちの順位で全部。◎だけを1着に固定しない
    - 馬単: 1着候補 × 2着候補（role_p2 か role_w）を、勝ち順位＋複勝順位の小さい順
    - 三連単: 1着候補 × 2着候補 × 3着候補（role_p3・p2・w）を、勝ち順位＋複勝順位×2 の小さい順
    - 三連複（保険）: 選んだ三連単の3頭の組を先に入れ（着順の入れ替わりを守る）、残りを本番の三連複の順で足す
    - モード: A＝馬単重点、B＝三連単重点、C＝レースの型（intel.race_structure）で 一強→B・二強/三強→A・混戦→保護（三連複厚め）
    点数は合計30点以内。足りない券種の余りは三連複に回す。
    """
    import intel
    mode = SINGLE_MODE
    struct = intel.race_structure(list(rows.values()))
    if mode == 'C':
        key = {'ONE': 'B', 'TWO': 'A', 'THREE': 'A'}.get(struct, 'PROTECT')
    else:
        key = mode
    b_ex, b_tri, b_trio = SINGLE_BUDGET[key]
    hon = ev.get('honmei')
    wr = lambda n: rows[n]['win_rank']
    pr = lambda n: rows[n]['place_rank']
    heads = sorted([n for n, r in rows.items() if r.get('role_w')], key=wr) or ([hon] if hon in rows else [])
    seconds = sorted([n for n, r in rows.items() if r.get('role_p2') or r.get('role_w')], key=pr)
    thirds = sorted([n for n, r in rows.items() if r.get('role_p3') or r.get('role_p2') or r.get('role_w')], key=pr)
    exacta_u = sorted({(a, b) for a in heads for b in seconds if a != b}, key=lambda c: (wr(c[0]) + pr(c[1]), c))
    tri_u = sorted({(a, b, c) for a in heads for b in seconds for c in thirds if len({a, b, c}) == 3},
                   key=lambda c: (wr(c[0]) + 2 * pr(c[1]) + pr(c[2]), c))
    exacta = exacta_u[:b_ex]
    exact = tri_u[:b_tri]
    trio_room = CAP_TOTAL - len(exacta) - len(exact)
    trio = []
    for t in [tuple(sorted(e)) for e in exact] + [tuple(x) for x in base_trio]:
        if t not in trio and len(trio) < min(trio_room, b_trio + (b_ex - len(exacta)) + (b_tri - len(exact))):
            trio.append(t)
    single = {'mode': mode, 'used': key, 'structure': struct, 'budget': {'exacta': b_ex, 'trifecta': b_tri, 'trio': b_trio},
              'heads': heads, 'points': {'exacta': len(exacta), 'trifecta': len(exact), 'trio': len(trio)}}
    return [list(t) for t in trio], [tuple(e) for e in exact], [tuple(e) for e in exacta], single


def _exposure(trio, exact):
    """horse_role_exposure_trace (KRS-BAN Compiler v1.3.0; evidence only): per horse, how many bought
    三連単 have it as HEAD / P2 / P3 and how many 三連複 contain it. Single-hub dependence is visible here."""
    out = {}
    for t in trio:
        for n in t:
            out.setdefault(str(n), {'head': 0, 'p2': 0, 'p3': 0, 'trio': 0})['trio'] += 1
    for e in exact:
        for k, n in zip(('head', 'p2', 'p3'), e):
            out.setdefault(str(n), {'head': 0, 'p2': 0, 'p3': 0, 'trio': 0})[k] += 1
    return dict(sorted(out.items(), key=lambda kv: int(kv[0])))
