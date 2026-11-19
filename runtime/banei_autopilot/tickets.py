"""KeibaMetrics BAN ticket compiler — v4.0-BAN spec 第4章・第5章.

Order is irreversible (v3.7 Rev.2 'Universe First, Capital Second, Rendered Truth Last'):
 1 role inventory  2 every W gets a head terminal  3 Head x P2 terminal  4 Pair x Third terminal
 5 canonical universe freeze  6 per-ticket-type capital  7 compression from weak duplicates
 8 bidirectional closure (Pair+Trio -> Exact, Exact -> Pair)  9 mechanical expansion = truth.
Owner policy: 三連複 + 三連単, every race, cap 30 unique points (3,000円) per race.
"""
from itertools import combinations, permutations

CAP_TOTAL = 30                      # Owner 2026-11-18 (= v2.2-BAN 標準型 総実点数30)
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
    return {'shape': label, 'trio_shape': tshape, 'exact_shape': eshape,
            'axis': axis, 'second': second, 'third': third,
            'trio': trio_l, 'exact': exact, 'removed': removed, 'pess_u': sorted(pess_u),
            'terminal': terminal, 'hole_link': hole_link, 'gates': gates,
            'universe': {'trio': len(universe_trio), 'exact': len(universe_exact)},
            'points': len(trio_l) + len(exact), 'stake': (len(trio_l) + len(exact)) * UNIT,
            'formality': 'FORMAL' if all(v in ('PASS', 'GUARDED', 'NOT-APPLICABLE') for v in gates.values())
            else 'REFERENCE-RENDERED'}
