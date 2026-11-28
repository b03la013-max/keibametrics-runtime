"""Shadow portfolio test (prereg R5 C13): keep the formal roles, but give the 60-point budget a 三連複 path.

PAPER earns mostly from 三連複/ワイド (any order among a few horses); the formal signed tickets are ~95 %
order bets (三連単/馬単) that need a W horse to win. Variants, all 100 yen per point, built only from the
signed formal summary (roles + signed ticket order), settled on the official payouts:
  R54_60         : the signed formal tickets (champion)
  MIX_P2BOX20    : 三連複 box of the P2 set (<= 20 points) + the first signed tickets up to 60 in total
  P2BOX20_ONLY   : the 三連複 box alone
  MIX_WAXIS_TRIO : 三連複 sets from P2 containing at least one W horse + first signed tickets up to 60
  KEEP_MEC_TRIO20: (P1-C, 11/19 review: 6 hit tickets lost by the cap were 三連複/三連単 of the full MEC) the first
                   20 三連複 tickets of the signed full MEC in MEC order + the first delivered tickets up to 60
  THIRD3_BY_PAIR : (P1-3 conditional third retention) 三連単 W -> P2 -> third, the third limited to the 3 best-ranked
                   other horses, pairs taken in ranking order until 60 points; keeps more W/P2 pairs alive
Evidence only; no Production change.
"""
import json
from itertools import combinations
from pathlib import Path

from runtime.local_autopilot import shadow_measure as sm

PROFILE = 'KM-LOCAL-FORMAL-MIX-SHADOW-v1.0-20261118'
CAP = 60
P2_BOX_MAX = 6


def _p2(summary):
    rank = [int(n) for n in summary['ranking']]
    roles = summary['roles']
    p2 = [n for n in rank if 'P2' in roles.get(str(n), [])][:P2_BOX_MAX]
    w = [n for n in rank if 'W' in roles.get(str(n), [])]
    return p2, w


def signed(summary):
    """The delivered (post-cap) formal tickets: summary['tickets'] (signed_final_tickets is the pre-cap MEC)."""
    # an auto-promoted variant replaces summary['tickets']; the R54_60 champion stays in tickets_r54_60
    src = summary.get('tickets_r54_60') if summary.get('tickets_r54_60') is not None else summary.get('tickets')
    return [(t['bet_type'], [int(x) for x in t['selection']]) for t in src or []]


def variants(summary, gen_names=()):
    out = _fixed_variants(summary)
    for name in gen_names:
        try:
            out[name] = gen_variant(summary, name, out['R54_60'])
        except Exception:
            out[name] = out['R54_60']
    return out


def variant_of(summary, name):
    """One variant by name (fixed or generated GEN:...)."""
    if str(name).startswith('GEN:'):
        return variants(summary, (name,))[name]
    return _fixed_variants(summary)[name]


def parse_gen(name):
    """'GEN:TRIOBOX:n=5' -> ('TRIOBOX', {'n': 5})."""
    _, fam, *kv = str(name).split(':')
    params = {}
    for x in kv:
        k, v = x.split('=')
        params[k] = int(v)
    return fam, params


def gen_name(fam, **params):
    return 'GEN:' + fam + ''.join(f':{k}={v}' for k, v in sorted(params.items()))


def gen_variant(summary, name, base=None):
    """Generated same-budget families (auto_candidates, Owner 2026-11-22 21:31). Each returns <= 60 points; the
    remaining points are the first delivered tickets, so every variant spends what the champion spends."""
    fam, k = parse_gen(name)
    p2, w = _p2(summary)
    base = base if base is not None else signed(summary)[:CAP]
    rank = [int(n) for n in summary['ranking']]
    fill = lambda extra: extra[:CAP] + [t for t in base if t not in extra][:max(0, CAP - len(extra[:CAP]))]
    if fam == 'TRIOBOX':        # 三連複 box of the top-n P2 horses
        return fill([('TRIO', sorted(c)) for c in combinations(p2[:k['n']], 3)])
    if fam == 'WAXTRIO':        # 三連複 of the top-n P2 that contain a W horse
        return fill([('TRIO', sorted(c)) for c in combinations(p2[:k['n']], 3) if set(c) & set(w)])
    if fam == 'THIRDK':         # 三連単 W -> P2 -> best-k other horses
        third = []
        for a in w:
            for b in p2:
                if b != a:
                    third += [('TRIFECTA', [a, b, c]) for c in [x for x in rank if x not in (a, b)][:k['k']]]
        return third[:CAP] if third else base
    if fam == 'KRSW':           # KAG Purple 2026-11-27 (Owner 22:53 「進めて」): W + KRS SSR-W top-n horses not in W
        kv = summary.get('_krs') or {}
        ssr = kv.get('ssr') or {}
        if not ssr:
            return base
        top = sorted(ssr, key=lambda h: -(ssr[h][0] or 0))[:k['n']]
        return w_plus_market(dict(summary, _market_order=top), base, rank, w, p2, add=k['n'])
    if fam == 'TRIOPROT':       # SCTP (Owner 2026-11-28 「実装してください」): C24 with k 三連複 protection tickets
        return trio_protect(w_plus_market(summary, base, rank, w, p2), rank, w, p2, k['k'])
    if fam == 'WPLUS':          # W + the `add` shortest-odds horses as extra heads (same rule as C24)
        return w_plus_market(summary, base, rank, w, p2, add=k['add'])
    if fam == 'P2PLUS':         # the `add` shortest-odds horses outside W/P2 as extra seconds behind each W head
        pops = [h for h in summary.get('_market_order') or [] if h not in w and h not in p2][:k['add']]
        extra = []
        for h in w:
            for b in pops:
                extra.append(('EXACTA', [h, b]))
                extra += [('TRIFECTA', [h, b, c]) for c in p2[:2] if c != h]
        extra = extra[:20]
        return [t for t in base if t not in extra][:max(0, CAP - len(extra))] + extra if extra else base
    if fam == 'PAIRFULL':       # (11/22 MIZ_12・SAG_04) the best W->P2 pairs, each with EVERY third horse
        pos = {h: i for i, h in enumerate(rank)}
        pairs = sorted([(a, b) for a in w for b in p2 if b != a], key=lambda ab: (pos.get(ab[0], 99) + pos.get(ab[1], 99),
                                                                                   pos.get(ab[0], 99)))[:k['pairs']]
        out = []
        for a, b in pairs:
            out += [('TRIFECTA', [a, b, c]) for c in rank if c not in (a, b)]
        out = out[:CAP]
        return out + [t for t in base if t not in out][:max(0, CAP - len(out))] if out else base
    if fam == 'MKTP2':          # (Owner 2026-11-23 22:22, head-local P2) the second-place set re-formed with the market:
        # on 227 settled formal races the market order separated the actual 2nd from the other non-winners with
        # AUC 0.741 against 0.651 for p2_score, so P2' = the same number of horses by a blend of market position
        # and model P2 position (blend = market share in %); W heads unchanged, 60 points rebuilt W->P2'->P2'/P3
        mo = summary.get('_market_order') or []
        if not mo:
            return base
        roles = summary.get('roles') or {}
        p3 = [int(h) for h in rank if 'P3' in (roles.get(str(h)) or [])]
        cand = [h for h in rank if h not in w or h in p2]
        bw = k['blend'] / 100.0
        bpos = {h: bw * (mo.index(h) if h in mo else len(mo)) + (1 - bw) * (p2.index(h) if h in p2 else len(p2) + rank.index(h))
                for h in rank}
        p2n = sorted(cand, key=lambda h: (bpos[h], rank.index(h)))[:len(p2)]
        thirds = sorted(set(p2n) | set(p3), key=lambda h: (bpos[h], rank.index(h)))
        pos = {h: i for i, h in enumerate(rank)}
        ex = sorted([(a, b) for a in w for b in p2n if a != b], key=lambda ab: (pos[ab[0]] + bpos[ab[1]]))[:6]
        tri = sorted([(a, b, c) for a in w for b in p2n for c in thirds if len({a, b, c}) == 3],
                     key=lambda t: (pos[t[0]] + bpos[t[1]] + bpos[t[2]]))
        out = [('EXACTA', [a, b]) for a, b in ex] + [('TRIFECTA', list(t)) for t in tri]
        out = out[:CAP]
        return out + [t for t in base if t not in out][:max(0, CAP - len(out))]
    if fam == 'KRSCAP':         # (Owner 2026-11-24 23:42) the 60 points chosen from the signed full MEC by the KRS
        # simulation instead of the Static rank sum: score = simulated occurrence of that exact order (top-20
        # trifecta/exacta tables) else the product of the per-horse SSR rates; 三連複 = sum of its 6 orders.
        # mode 1: KRS score only; mode 2: MEC tier first (CORE > PROTECTION > TAIL), KRS score within a tier
        kv = summary.get('_krs')
        if kv and k.get('t'):   # t = temperature x100 (KRS calibration baseline 2026-11-26: SSR-W over-confident, T=1.65)
            T = k['t'] / 100.0
            kv = {'tri': {c: f ** (1 / T) for c, f in kv['tri'].items()},
                  'ex': {c: f ** (1 / T) for c, f in kv['ex'].items()},
                  'ssr': {h: tuple(x ** (1 / T) for x in v) for h, v in kv['ssr'].items()}}
        mec = [(t['bet_type'], [int(x) for x in t['selection']], t.get('mec_tier')) for t in summary.get('signed_final_tickets') or []]
        if not kv or not mec:
            return base
        tier = {'CORE': 0, 'PROTECTION': 1, 'TAIL': 2}
        order = sorted(range(len(mec)), key=lambda i: ((tier.get(mec[i][2], 3) if k['mode'] == 2 else 0),
                                                      -krs_score(kv, mec[i][0], mec[i][1]), i))
        out = []
        for i in order:
            t = (mec[i][0], mec[i][1])
            if t not in out:
                out.append(t)
            if len(out) >= CAP:
                break
        return out
    if fam in ('IDXABL', 'IDXSCL'):   # KIEP (Owner 2026-11-26 21:43): the signed MEC capped to 60 like R54, ordered with the
        # formal ranking re-computed with index INDEX_IDS[drop] neutralised (race mean); needs summary['_abl_src']
        src = summary.get('_abl_src')
        mec = summary.get('signed_final_tickets') or []
        if not src or not mec:
            return base
        from runtime.local_autopilot import kiep
        from runtime.local_autopilot.formal_rakuten import cap_tickets
        try:
            rk = (kiep.ranking(src['full29'], src.get('ext') or {}, kiep.INDEX_IDS[k['drop']]) if fam == 'IDXABL' else
                  kiep.ranking(src['full29'], src.get('ext') or {}, kiep.INDEX_IDS[k['i']], k['s'] / 100.0))
        except Exception:
            return base
        capped = cap_tickets(mec, [str(h) for h in rk], CAP)
        return [(t['bet_type'], [int(x) for x in t['selection']]) for t in capped['tickets']]
    if fam == 'CORE':           # CORE_LAYER_60 with the core pair set = top-n P2
        return core_layer(summary, base, w, p2, core_n=k['n'])
    raise ValueError(f'unknown family {fam}')


def krs_view(util):
    """krs_prediction_utility -> {'tri': {(a,b,c): f}, 'ex': {(a,b): f}, 'ssr': {h: (W, P2, P3)}} (uncalibrated
    simulation occurrence rates, used only to ORDER tickets inside the same 60-point budget)."""
    if not util:
        return None
    tri = {(int(x['W']), int(x['P2']), int(x['P3'])): float(x['frequency']) for x in util.get('top_trifecta_occurrence') or []}
    ex = {(int(x['W']), int(x['P2'])): float(x['frequency']) for x in util.get('top_exacta_occurrence') or []}
    ssr = {int(x['horse_no']): (float(x.get('SSR-W') or 0), float(x.get('SSR-P2') or 0), float(x.get('SSR-P3') or 0))
           for x in util.get('summary') or []}
    return {'tri': tri, 'ex': ex, 'ssr': ssr} if ssr else None


def krs_score(kv, bt, sel):
    g = lambda h, i: kv['ssr'].get(h, (0, 0, 0))[i]
    if bt == 'TRIFECTA' and len(sel) == 3:
        return kv['tri'].get(tuple(sel), g(sel[0], 0) * g(sel[1], 1) * g(sel[2], 2))
    if bt == 'EXACTA' and len(sel) == 2:
        return kv['ex'].get(tuple(sel), g(sel[0], 0) * g(sel[1], 1))
    if bt == 'TRIO' and len(sel) == 3:
        from itertools import permutations
        return sum(krs_score(kv, 'TRIFECTA', list(p)) for p in permutations(sel))
    if bt == 'QUINELLA' and len(sel) == 2:
        return krs_score(kv, 'EXACTA', sel) + krs_score(kv, 'EXACTA', sel[::-1])
    return 0.0


def _fixed_variants(summary):
    p2, w = _p2(summary)
    box = [('TRIO', sorted(c)) for c in combinations(p2, 3)]
    wax = [t for t in box if set(t[1]) & set(w)]
    base = signed(summary)
    fill = lambda extra: extra + [t for t in base if t not in extra][:max(0, CAP - len(extra))]
    mec_trio = [('TRIO', sorted(int(x) for x in t['selection'])) for t in summary.get('signed_final_tickets') or []
                if t.get('bet_type') == 'TRIO'][:20]
    rank = [int(n) for n in summary['ranking']]
    third = []
    for a in w:
        for b in p2:
            if b == a:
                continue
            third += [('TRIFECTA', [a, b, c]) for c in [x for x in rank if x not in (a, b)][:3]]
    return {'R54_60': base[:CAP], 'MIX_P2BOX20': fill(box), 'P2BOX20_ONLY': box, 'MIX_WAXIS_TRIO': fill(wax),
            'KEEP_MEC_TRIO20': fill(mec_trio), 'THIRD3_BY_PAIR': third[:CAP],
            'W_PLUS_TOP2POP_60': w_plus_market(summary, base, rank, w, p2),
            'CORE_LAYER_60': core_layer(summary, base, w, p2),
            'NOBET_LOWINFO': [] if low_info(summary) else base[:CAP]}


LOW_INFO_SPD_SHARE = 0.5


def low_info(summary):
    """C27 (KAW 第382条 arm B, Owner 2026-11-21 23:57): the race is information-poor when fewer than half of the
    field has an own NAR speed figure (EXT status spd_horses / field). Unknown before EXT (11/22) -> not low."""
    st = ((summary.get('ext_connection') or {}).get('status') or {})
    n = len(summary.get('ranking') or [])
    if not n or st.get('spd_horses') is None:
        return False
    return st['spd_horses'] / n < LOW_INFO_SPD_SHARE


def core_layer(summary, base, w, p2, core_n=3):
    """C28 (FNB 第313〜315条 3層Capital / OHI 第331条 Capital 4層, Owner 2026-11-21 23:57): the same 60 points
    re-drawn from the signed full MEC (pre-cap) by layer: 1) head in W and second in the top-3 P2 (Core-Pair Deep),
    2) head in W and second in P2 (Head-local Wide), 3) the rest in MEC order (Peripheral Thin). Stable within a
    layer (MEC order). Falls back to the delivered tickets when the MEC is not stored."""
    mec = [(t['bet_type'], [int(x) for x in t['selection']]) for t in summary.get('signed_final_tickets') or []]
    if not mec:
        return base[:CAP]
    core2 = set(p2[:core_n])

    def layer(t):
        sel = t[1]
        if t[0] in ('TRIO', 'QUINELLA', 'WIDE'):
            hw = bool(set(sel) & set(w))
            return 0 if hw and len(set(sel) & core2) >= 1 else 1 if hw else 2
        head, second = sel[0], sel[1] if len(sel) > 1 else None
        if head in w and second in core2:
            return 0
        return 1 if head in w and second in p2 else 2
    order = sorted(range(len(mec)), key=lambda i: (layer(mec[i]), i))
    out = []
    for i in order:
        if mec[i] not in out:
            out.append(mec[i])
        if len(out) >= CAP:
            break
    return out


def trio_protect(main, rank, w, p2, k):
    """SCTP 単系主戦・三連複保護層 (same budget): the k lowest-priority 三連単 of `main` (largest sum of formal ranking
    positions, later first on ties) are replaced by k 三連複 not already in `main`, taken first from W∪P2 and then
    from the ranking top-6 (fewest horses outside W∪P2, then smallest ranking-position sum). Points never grow."""
    pos = {h: i for i, h in enumerate(rank)}
    core = list(dict.fromkeys(list(w) + list(p2)))
    pool = list(dict.fromkeys(core + list(rank[:6])))
    have = {tuple(sorted(t[1])) for t in main if t[0] == 'TRIO'}
    trios = sorted((tuple(sorted(c)) for c in combinations(pool, 3)),
                   key=lambda c: (sum(1 for x in c if x not in core), sum(pos.get(x, 99) for x in c), c))
    add = [('TRIO', list(c)) for c in trios if c not in have][:k]
    tri = [i for i, t in enumerate(main) if t[0] == 'TRIFECTA']
    drop = set(sorted(tri, key=lambda i: (-sum(pos.get(x, 99) for x in main[i][1]), -i))[:len(add)])
    add = add[:len(drop)]
    return [t for i, t in enumerate(main) if i not in drop] + add


def w_plus_market(summary, base, rank, w, p2, add=2):
    """C24 (same budget, full ticket): W' = W + the `add` shortest-odds horses (pre-race odds of the latest PAPER
    revision, stored by forward_oos as summary['_market_order']). The added heads get a share of the 60 points
    proportional to their number among W'; those points replace the LAST delivered tickets. Added tickets:
    3 馬単 head -> P2 first, then 三連単 head -> P2 (ranking order) -> best-2 thirds; capped by the combinations
    available (small fields give the added heads fewer points; the rest stays delivered tickets)."""
    pops = summary.get('_market_order') or []
    added = [h for h in pops[:add] if h not in w]
    if not added:
        return base[:CAP]
    k = round(CAP * len(added) / (len(w) + len(added)))
    extra = []
    per = [k // len(added) + (1 if i < k % len(added) else 0) for i in range(len(added))]
    for h, n in zip(added, per):
        seconds = [b for b in (p2 + rank) if b != h]
        seconds = list(dict.fromkeys(seconds))
        mine = []
        for b in seconds:
            for c in [x for x in rank if x not in (h, b)][:2]:
                mine.append(('TRIFECTA', [h, b, c]))
        mine = [('EXACTA', [h, b]) for b in seconds[:3]] + mine
        extra += mine[:n]
    keep = [t for t in base if t not in extra][:max(0, CAP - len(extra))]
    return keep + extra


def races(root, since=None):
    out = []
    gen = _gen_names(root)
    for sp in sorted(Path(root).glob('20*/formal/*.summary.json')):
        key = sp.name.split('.')[0]
        row_day = sp.parent.parent.name
        eff = sp.parent / 'rev2'                      # effective revision: a signed Revision 2 replaces Revision 1
        d = eff if (eff / f'{key}.result.json').exists() else sp.parent
        try:
            res = json.loads((d / f'{key}.result.json').read_text())
            summ = json.loads(((d if (d / f'{key}.summary.json').exists() else sp.parent) / f'{key}.summary.json').read_text())
        except (OSError, ValueError):
            continue
        if summ.get('no_bet') or not res.get('order'):
            continue
        if since:
            try:
                q = json.loads((Path(root) / row_day / 'queue.json').read_text())
                from datetime import datetime
                if datetime.fromisoformat(q['races'][key]['post_current']) < since:
                    continue
            except (OSError, ValueError, KeyError):
                continue
        ns = set(res.get('non_starters') or []) | set(res.get('non_starters_inferred') or [])
        row = {'day': row_day, 'key': key}
        summ['_market_order'] = _market_order(Path(root) / row_day, key)
        for kp in (sp.parent / f'{key}.krs_prediction_utility.json', Path(root) / row_day / 'formal' / f'{key}.krs_prediction_utility.json'):
            if kp.exists():
                try:
                    summ['_krs'] = krs_view(json.loads(kp.read_text()))
                except (OSError, ValueError, KeyError, TypeError):
                    pass
                break
        if any(str(g).startswith(('GEN:IDXABL', 'GEN:IDXSCL')) for g in gen):   # KIEP: frozen Full29 + EXT of the effective revision
            fd = d if (d / f'{key}.full29.json').exists() else sp.parent
            try:
                ec = json.loads((fd / f'{key}.ext_connection.json').read_text()) if (fd / f'{key}.ext_connection.json').exists() else {}
                summ['_abl_src'] = {'full29': json.loads((fd / f'{key}.full29.json').read_text()), 'ext': ec.get('runners') or {}}
            except (OSError, ValueError):
                pass
        for name, t in variants(summ, gen).items():
            i, p, h = sm.settle(t, res['payouts'], ns)
            row[name] = (i, p, h, len(t))
        # REV1_MIX (evidence only, Owner 2026-11-23 22:22): what the delivered policy would have paid had the
        # Revision 1 tickets been kept (only races with a signed Revision 2; otherwise identical by definition)
        try:
            if d == eff:
                s1 = json.loads((sp.parent / f'{key}.summary.json').read_text())
                s1['_market_order'] = summ['_market_order']
                t = variant_of(s1, 'MIX_P2BOX20')
            else:
                t = variant_of(summ, 'MIX_P2BOX20')
            i, p, h = sm.settle(t, res['payouts'], ns)
            row['REV1_MIX'] = (i, p, h, len(t))
        except Exception:
            pass
        out.append(row)
    return out


def _gen_names(root):
    """Generated variants to compute: the auto candidates AND the fixed auto_promote candidates written as GEN names
    (C29/C30/C31 ...; before 2026-11-27 these were missing here, so their rows were never computed)."""
    names = []
    try:
        st = json.loads((Path(root) / 'auto_candidates.json').read_text())
        names += [c['variant'] for c in (st.get('candidates') or {}).values()]
    except (OSError, ValueError, KeyError):
        pass
    try:
        from runtime.local_autopilot import auto_promote
        names += [v for v, _ in auto_promote.CANDIDATES.values() if str(v).startswith('GEN:')]
    except Exception:
        pass
    return tuple(dict.fromkeys(names))


def _market_order(day_dir, key):
    try:
        from runtime.local_autopilot import role_shadow
        return role_shadow._pops(day_dir, key)
    except Exception:
        return []


def evaluate(root, since=None):
    rs = races(root, since)
    agg = {}
    for name in ('R54_60', 'MIX_P2BOX20', 'P2BOX20_ONLY', 'MIX_WAXIS_TRIO', 'KEEP_MEC_TRIO20', 'THIRD3_BY_PAIR', 'W_PLUS_TOP2POP_60',
                 'CORE_LAYER_60', 'NOBET_LOWINFO'):
        v = [r[name] for r in rs]
        inv, pay = sum(x[0] for x in v), sum(x[1] for x in v)
        top = max((x[1] for x in v), default=0)
        vs = sorted(v, key=lambda x: -x[1])
        inv_x, pay_x = sum(x[0] for x in vs[1:]), sum(x[1] for x in vs[1:])
        agg[name] = {'races': len(v), 'invest': inv, 'payout': pay, 'pfs': round(100 * pay / inv, 1) if inv else None,
                     'pfs_ex_top1': round(100 * pay_x / inv_x, 1) if inv_x else None,
                     'hit_but_loss': sum(1 for x in v if x[2] and x[1] < x[0]),
                     'hit_races': sum(1 for x in v if x[2]), 'points_per_race': round(sum(x[3] for x in v) / len(v), 1) if v else None,
                     'top1_payout_share': round(100 * top / pay, 1) if pay else None,
                     'pfs_ci95': sm.boot_ci([(x[0], x[1]) for x in v]) if v else None}
    return {'profile': PROFILE, 'races': len(rs), 'variants': agg, 'production_change': 'NONE (evidence only)'}
