"""Single-factor role candidate replay on settled JRA races (NON-PRODUCTION, known-result replay).

Each candidate changes ONE role decision on top of the frozen FINAL, then rebuilds
tickets with the Production MEC (build_mec_plan) and settles them with the
Production settle_final at official JRA payouts. Static ranking, indices, AKI
rules, MEC and capital code are untouched. Results are regression evidence only,
never forward OOS, and never alter a signed FINAL.

Candidates
- W_PLUS_STATIC2: when the formal W set has exactly one head, add the Static rank-2
  runner to W as PROTECTED (REVIEW). Tests the single-axis width limit.
- P2_KRS_HEAD_LOCAL: for every formal W head, add the most frequent KRS exacta
  second for that head (if not already a P2) as PROTECTED P2. Tests head-local P2.
- W_PLUS_MARKET1 / W_PLUS_MARKET_TOP3 (LOCAL C18/C19 port, 2026-11-20): add the official
  pre-cutoff market favourite (or favourites 1-3) missing from W. Market facts come only from
  the request's signed JRA official market observation captured before prediction_cutoff.
- W_PLUS_STATIC_SAME_COUNT_CONTROL (LOCAL C20): add as many runners as W_PLUS_MARKET_TOP3
  would, chosen by Static rank instead of the market, so width and signal are separable.
- P3_MARKET_TOP5 / P3_STATIC_SAME_COUNT_CONTROL (Owner 2026-11-21 18:58, 11/21 review P1): the
  third-placed runner sat at Static rank >= 8 in 10 of 15 settled races. Add the pre-cutoff market
  top-5 runners missing from P3 as PROTECTED thirds under every existing pair; the control adds the
  same number by Static rank.
- P2_MARKET_TOP3 / P2_STATIC_SAME_COUNT_CONTROL (11/21 review, ChatGPT cross-check: FKS P2 was the
  first failure in 4 of 6 races with the winner already in W): add the pre-cutoff market top-3 runners
  missing from P2 as PROTECTED seconds under every W head; the control adds the same number by Static rank.
- SKIP_HEAVY_GOING (11/21 review P2: 福島 0/6 on 稍重〜重): no bet when the signed pre-cutoff official
  going for the race is 重 or 不良. Selection only; tickets otherwise unchanged.
- DROP_TRIFECTA (11/22 review P1, ticket shape): keep the frozen Production EXACTA and TRIO tickets
  and drop every TRIFECTA ticket (no MEC rebuild). Forward 11/21-22: TRIFECTA 32,400 yen -> 0 while
  EXACTA returned 97%. Races whose tickets are all TRIFECTA become no-bet.
- CAP30 (11/22 review P0-04, ticket count): races with more than 30 Production tickets keep 30
  (CORE tier first, then Production order); fewer points at the same role sets, no MEC rebuild.
- W_PLUS_STATIC2_SAME_BUDGET (11/23 review P0-01, Owner approval 2026-11-23): W_PLUS_STATIC2, then the
  rebuilt MEC tickets are cut back to the Production ticket count (CORE tier first, then MEC order),
  so a wider W is compared at the same number of points. 11/23 diagnosis: the formal W set always equals
  the Static (ZAI_WIN) top-N and BASE mode keeps one head (normalized gap <= 0.35); the Static top-3
  winners left out of W were width losses, not a different ordering.
- EXACTA_ONLY (11/22 review P1, ticket shape): keep only the frozen Production EXACTA tickets (drop TRIFECTA
  and TRIO, no MEC rebuild). Separates "TRIFECTA is the drag" from "the whole trio/trifecta layer is".
- DRIVE01 (Drive 精読 2026-11-22, 中央フォルダ 07_攻略・情報源; recorded challengers, NON-PRODUCTION):
  P3_SHORTEN_SPRINT_FRONT (q552 短距離戦・高配当捕捉資料): today <= 1400m, last run >= 1600m, no
  recent run <= 1400m, and a last-run corner position within the first half of the field -> add to P3.
  P3_FIRST_DIRT_BIG_OUTER_FRONT (q554 複勝軸選定と穴馬激走パターン): dirt today, every recent run on
  turf, declared body weight >= 460kg, horse_no in the outer half, and some recent first-corner position
  within the first 40% of the field -> add to P3.
  W_WIND8_MARKET_TOP3 (q565 風の強い日の競馬): pre-cutoff JMA wind >= 8.0 m/s -> add the market top-3
  missing from W (no single-favourite axis on windy days).
  Each has a same-count control (P3 by market order / W by Static rank) in the same firing races.
  Race-card facts come only from the signed request snapshot frozen at or before prediction_cutoff.
"""
import argparse, copy, glob, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'runtime'), str(ROOT / 'runtime/jra_source_runtime'), str(ROOT / 'runtime/analysis')]
from minimum_efficient_coverage import build_mec_plan  # noqa: E402
from jra_production_postresult import settle_final  # noqa: E402

LIVE = ('CORE', 'PROTECTED')


def _live(f, col):
    return [str(x['runner_id']) for x in f['role_registry'] if x['column'] == col and x['status'] in LIVE]


def _promote(f, col, rid, tag):
    for x in f['role_registry']:
        if x['column'] == col and str(x['runner_id']) == str(rid):
            if x['status'] in LIVE:
                return False
            x.update(status='PROTECTED', review_mode='REVIEW', reason=f'SHADOW_CANDIDATE:{tag}')
            return True
    return False


def _mirror_pairs(f, new_head=None, new_second=None, tag=''):
    """Give an added head/second the same pair/third structure as the formal roles.

    Production AKI derives these from compiled pair facts that the FINAL does not
    store, so the replay marks them PROTECT with reason SHADOW_MIRRORED_STRUCTURE
    (no registered pair evidence evaluated)."""
    W, P2, P3 = _live(f, 'W'), _live(f, 'P2'), _live(f, 'P3')
    pairs, thirds = f.setdefault('pair_dispositions', []), f.setdefault('third_dispositions', [])
    have = {(str(x['head']), str(x['second'])) for x in pairs}
    added = []
    for h in W:
        for s in P2:
            if h == s or (h, s) in have or (new_head and h != new_head and s != new_second and new_second is None) :
                continue
            if new_head and h != new_head:
                continue
            if new_second and s != new_second:
                continue
            pairs.append({'head': h, 'second': s, 'status': 'PROTECT', 'reason': 'SHADOW_MIRRORED_STRUCTURE:' + tag,
                          'rule_matches': []})
            added.append((h, s))
    for h, s in added:
        for t in P3:
            if t not in {h, s}:
                thirds.append({'head': h, 'second': s, 'third': t, 'status': 'PROTECT',
                               'reason': 'SHADOW_MIRRORED_STRUCTURE:' + tag, 'rule_matches': []})
    if new_head and new_head not in [str(x) for x in f.get('purchased_heads') or []]:
        f['purchased_heads'] = list(f.get('purchased_heads') or []) + [new_head]


def w_plus_static2(f):
    W = _live(f, 'W')
    rank = [str(r) for r in f['static_prediction']['ranking']]
    if len(W) != 1 or len(rank) < 2:
        return False
    nxt = next((r for r in rank if r not in W), None)
    if not (nxt and _promote(f, 'W', nxt, 'W_PLUS_STATIC2')):
        return False
    _mirror_pairs(f, new_head=nxt, tag='W_PLUS_STATIC2')
    return True


def w_plus_static2_same_budget(f):
    n = len((f.get('final_ticket') or {}).get('tickets') or [])
    if not n or not w_plus_static2(f):
        return False
    f['_post_mec_cap'] = n
    return True


def _post_mec_cap(f, tickets):
    cap = f.get('_post_mec_cap')
    if not cap or len(tickets) <= cap:
        return tickets
    order = sorted(range(len(tickets)), key=lambda i: (tickets[i].get('mec_tier') != 'CORE', i))
    return [tickets[i] for i in sorted(order[:cap])]


def p2_krs_head_local(f):
    occ = (f.get('krs_prediction_utility') or {}).get('top_exacta_occurrence') or []
    changed = False
    P2 = set(_live(f, 'P2'))
    for head in _live(f, 'W'):
        seconds = [str(o['P2']) for o in occ if str(o['W']) == head and str(o['P2']) != head]
        pick = next((s for s in seconds if s not in P2), None)
        if pick and _promote(f, 'P2', pick, 'P2_KRS_HEAD_LOCAL'):
            P2.add(pick); changed = True
            _mirror_pairs(f, new_head=head, new_second=pick, tag='P2_KRS_HEAD_LOCAL')
    return changed


def p2_static_next_control(f):
    """Control for P2_KRS_HEAD_LOCAL: same number of added P2 per head, chosen by Static rank."""
    rank = [str(r) for r in f['static_prediction']['ranking']]
    P2 = set(_live(f, 'P2'))
    changed = False
    for head in _live(f, 'W'):
        pick = next((r for r in rank if r != head and r not in P2), None)
        if pick and _promote(f, 'P2', pick, 'P2_STATIC_NEXT_CONTROL'):
            P2.add(pick); changed = True
            _mirror_pairs(f, new_head=head, new_second=pick, tag='P2_STATIC_NEXT_CONTROL')
    return changed


def market_ranking(f, root=ROOT):
    """Official popularity order captured before the prediction cutoff, else None."""
    import datetime as dt
    rq = root / 'runtime/requests' / f"{f['race_id']}-LIVE-R1-FORMAL.json"
    if not rq.exists():
        return None
    m = (json.loads(rq.read_text()).get('source_snapshot') or {}).get('jra_official_market_observation') or {}
    try:
        if m.get('status') != 'PASS' or dt.datetime.fromisoformat(m['captured_at']) > dt.datetime.fromisoformat(f['prediction_cutoff']):
            return None
    except (KeyError, TypeError, ValueError):
        return None
    rs = [r for r in m.get('runners') or [] if isinstance(r.get('popularity_rank'), int)]
    return [str(r['runner_id']) for r in sorted(rs, key=lambda r: r['popularity_rank'])] or None


def _add_heads(f, picks, tag):
    added = [r for r in picks if _promote(f, 'W', r, tag)]
    for r in added:
        _mirror_pairs(f, new_head=r, tag=tag)
    return bool(added)


def _market_missing(f, n):
    mk = market_ranking(f)
    return None if mk is None else [r for r in mk[:n] if r not in _live(f, 'W')]


def w_plus_market1(f):
    miss = _market_missing(f, 1)
    return bool(miss) and _add_heads(f, miss, 'W_PLUS_MARKET1')


def w_plus_market_top3(f):
    miss = _market_missing(f, 3)
    return bool(miss) and _add_heads(f, miss, 'W_PLUS_MARKET_TOP3')


def w_plus_static_same_count_control(f):
    miss = _market_missing(f, 3)
    if not miss:
        return False
    W = _live(f, 'W')
    picks = [r for r in (str(x) for x in f['static_prediction']['ranking']) if r not in W][:len(miss)]
    return _add_heads(f, picks, 'W_PLUS_STATIC_SAME_COUNT_CONTROL')


def _add_thirds(f, picks, tag):
    added = [r for r in picks if _promote(f, 'P3', r, tag)]
    if not added:
        return False
    thirds = f.setdefault('third_dispositions', [])
    have = {(str(x['head']), str(x['second']), str(x['third'])) for x in thirds}
    for pr in f.get('pair_dispositions') or []:
        h, s2 = str(pr['head']), str(pr['second'])
        for t in added:
            if t not in (h, s2) and (h, s2, t) not in have:
                thirds.append({'head': h, 'second': s2, 'third': t, 'status': 'PROTECT',
                               'reason': 'SHADOW_CANDIDATE:' + tag, 'rule_matches': []})
    return True


def _p3_market_missing(f, n):
    mk = market_ranking(f)
    if mk is None:
        return None
    taken = set(_live(f, 'P3'))
    return [r for r in mk[:n] if r not in taken]


def p3_market_top5(f):
    miss = _p3_market_missing(f, 5)
    return bool(miss) and _add_thirds(f, miss, 'P3_MARKET_TOP5')


def p3_static_same_count_control(f):
    miss = _p3_market_missing(f, 5)
    if not miss:
        return False
    taken = set(_live(f, 'P3'))
    picks = [r for r in (str(x) for x in f['static_prediction']['ranking']) if r not in taken][:len(miss)]
    return _add_thirds(f, picks, 'P3_STATIC_SAME_COUNT_CONTROL')


def _add_seconds(f, picks, tag):
    added = [r for r in picks if _promote(f, 'P2', r, tag)]
    for r in added:
        for h in _live(f, 'W'):
            if h != r:
                _mirror_pairs(f, new_head=h, new_second=r, tag=tag)
    return bool(added)


def _p2_market_missing(f, n):
    mk = market_ranking(f)
    if mk is None:
        return None
    taken = set(_live(f, 'P2'))
    return [r for r in mk[:n] if r not in taken]


def p2_market_top3(f):
    miss = _p2_market_missing(f, 3)
    return bool(miss) and _add_seconds(f, miss, 'P2_MARKET_TOP3')


def p2_static_same_count_control(f):
    miss = _p2_market_missing(f, 3)
    if not miss:
        return False
    taken = set(_live(f, 'P2'))
    picks = [r for r in (str(x) for x in f['static_prediction']['ranking']) if r not in taken][:len(miss)]
    return _add_seconds(f, picks, 'P2_STATIC_SAME_COUNT_CONTROL')


def official_going(f, root=ROOT):
    """Latest signed JRA official going observed before the prediction cutoff, else None."""
    import datetime as dt
    rq = root / 'runtime/requests' / f"{f['race_id']}-LIVE-R1-FORMAL.json"
    if not rq.exists():
        return None
    obs = (json.loads(rq.read_text()).get('source_snapshot') or {}).get('aki_external_observations') or []
    try:
        cut = dt.datetime.fromisoformat(f['prediction_cutoff'])
        ok = [o for o in obs if o.get('going') and o.get('source_authority') == 'JRA_OFFICIAL'
              and dt.datetime.fromisoformat(o['observed_at']) <= cut]
    except (KeyError, TypeError, ValueError):
        return None
    return max(ok, key=lambda o: o['observed_at'])['going'] if ok else None


def skip_heavy_going(f):
    if official_going(f) not in ('重', '不良'):
        return False
    f['_skip_bet'] = True
    return True


def drop_trifecta(f):
    tk = (f.get('final_ticket') or {}).get('tickets') or []
    if not any(t.get('bet_type') == 'TRIFECTA' for t in tk):
        return False
    f['_drop_bet_types'] = ['TRIFECTA']
    return True


def exacta_only(f):
    tk = (f.get('final_ticket') or {}).get('tickets') or []
    if not any(t.get('bet_type') in ('TRIFECTA', 'TRIO') for t in tk):
        return False
    f['_drop_bet_types'] = ['TRIFECTA', 'TRIO']
    return True


CAP_POINTS = 30


def cap30(f):
    """11/22 review P0-04 (ticket count): keep at most 30 Production tickets, CORE tier first, then the
    Production order; no MEC rebuild, no new tickets. Tests 'fewer points' at the same role sets."""
    tk = (f.get('final_ticket') or {}).get('tickets') or []
    if len(tk) <= CAP_POINTS:
        return False
    f['_cap_tickets'] = CAP_POINTS
    return True


def _filtered_tickets(f):
    """Production tickets minus the arm's dropped bet types / beyond the arm's cap (no MEC rebuild)."""
    drop = set(f.get('_drop_bet_types') or [])
    tk = [t for t in (f.get('final_ticket') or {}).get('tickets') or [] if t.get('bet_type') not in drop]
    cap = f.get('_cap_tickets')
    if cap:
        order = sorted(range(len(tk)), key=lambda i: (tk[i].get('mec_tier') != 'CORE', i))
        tk = [tk[i] for i in sorted(order[:cap])]
    return tk, sum(int(t.get('stake', 100)) for t in tk)


# ---- DRIVE01 recorded challengers (Drive 精読 2026-11-22) ----
def _dt(x):
    import datetime as dt
    return dt.datetime.fromisoformat(str(x).replace('Z', '+00:00'))


def _request_snapshot(f, root=ROOT):
    rq = root / 'runtime/requests' / f"{f['race_id']}-LIVE-R1-FORMAL.json"
    if not rq.exists():
        return None
    ss = json.loads(rq.read_text()).get('source_snapshot') or {}
    try:
        if _dt(ss['source_freeze_at']) > _dt(f['prediction_cutoff']):
            return None
    except (KeyError, TypeError, ValueError):
        return None
    return ss


def race_card(f, root=ROOT):
    """(race_context, {runner_id: runner}) from the official card frozen before the cutoff, else None."""
    ss = _request_snapshot(f, root)
    card = (ss or {}).get('jra_official_race_card_detail') or {}
    if not card.get('runners'):
        return None
    return card.get('race_context') or {}, {str(r['horse_no']): r for r in card['runners'] if r.get('horse_no') is not None}


def jma_wind(f, root=ROOT):
    """JMA wind speed (m/s) observed at or before the prediction cutoff, else None."""
    ss = _request_snapshot(f, root)
    o = ((ss or {}).get('jma_weather_evidence') or {}).get('observation') or {}
    try:
        if o.get('wind_speed_ms') is None or _dt(o['observed_at_jst']) > _dt(f['prediction_cutoff']):
            return None
    except (KeyError, TypeError, ValueError):
        return None
    return float(o['wind_speed_ms'])


def _field(run):
    return run.get('field_size') or 0


def shorten_sprint_front(ctx, r):
    runs = r.get('recent_runs') or []
    if not runs or not ctx.get('distance_m') or ctx['distance_m'] > 1400:
        return False
    last = runs[0]
    if (last.get('distance_m') or 0) < 1600 or any((x.get('distance_m') or 9999) <= 1400 for x in runs):
        return False
    pp, n = last.get('passing_positions') or [], _field(last)
    return bool(pp and n and min(pp) <= 0.5 * n)


def first_dirt_big_outer_front(ctx, r, field_n):
    runs = r.get('recent_runs') or []
    if ctx.get('surface') != 'ダ' or not runs or any(x.get('surface') != '芝' for x in runs):
        return False
    if (r.get('current_body_weight') or 0) < 460 or not field_n or (r.get('horse_no') or 0) <= field_n / 2:
        return False
    return any((x.get('passing_positions') or [None])[0] is not None and _field(x)
               and x['passing_positions'][0] <= 0.4 * _field(x) for x in runs)


def _drive_p3_picks(f, rule):
    rc = race_card(f)
    if rc is None:
        return None
    ctx, runners = rc
    taken = set(_live(f, 'P3'))
    if rule == 'SHORTEN':
        hits = [k for k, r in runners.items() if shorten_sprint_front(ctx, r)]
    else:
        hits = [k for k, r in runners.items() if first_dirt_big_outer_front(ctx, r, len(runners))]
    return [k for k in sorted(hits, key=int) if k not in taken]


def _p3_same_count_market(f, n, tag):
    order = market_ranking(f) or [str(x) for x in f['static_prediction']['ranking']]
    taken = set(_live(f, 'P3'))
    return _add_thirds(f, [r for r in order if r not in taken][:n], tag)


def p3_shorten_sprint_front(f):
    picks = _drive_p3_picks(f, 'SHORTEN')
    return bool(picks) and _add_thirds(f, picks, 'P3_SHORTEN_SPRINT_FRONT')


def p3_shorten_same_count_control(f):
    picks = _drive_p3_picks(f, 'SHORTEN')
    return bool(picks) and _p3_same_count_market(f, len(picks), 'P3_SHORTEN_SAME_COUNT_CONTROL')


def p3_first_dirt_big_outer_front(f):
    picks = _drive_p3_picks(f, 'FIRST_DIRT')
    return bool(picks) and _add_thirds(f, picks, 'P3_FIRST_DIRT_BIG_OUTER_FRONT')


def p3_first_dirt_same_count_control(f):
    picks = _drive_p3_picks(f, 'FIRST_DIRT')
    return bool(picks) and _p3_same_count_market(f, len(picks), 'P3_FIRST_DIRT_SAME_COUNT_CONTROL')


WIND_MS = 8.0


def w_wind8_market_top3(f):
    w = jma_wind(f)
    if w is None or w < WIND_MS:
        return False
    miss = _market_missing(f, 3)
    return bool(miss) and _add_heads(f, miss, 'W_WIND8_MARKET_TOP3')


def w_wind8_static_same_count_control(f):
    w = jma_wind(f)
    if w is None or w < WIND_MS:
        return False
    miss = _market_missing(f, 3)
    if not miss:
        return False
    W = _live(f, 'W')
    picks = [r for r in (str(x) for x in f['static_prediction']['ranking']) if r not in W][:len(miss)]
    return _add_heads(f, picks, 'W_WIND8_STATIC_SAME_COUNT_CONTROL')


CANDIDATES = {'W_PLUS_STATIC2': w_plus_static2, 'P2_KRS_HEAD_LOCAL': p2_krs_head_local,
              'P2_STATIC_NEXT_CONTROL': p2_static_next_control, 'W_PLUS_MARKET1': w_plus_market1,
              'W_PLUS_MARKET_TOP3': w_plus_market_top3,
              'W_PLUS_STATIC_SAME_COUNT_CONTROL': w_plus_static_same_count_control,
              'P3_MARKET_TOP5': p3_market_top5, 'P3_STATIC_SAME_COUNT_CONTROL': p3_static_same_count_control,
              'SKIP_HEAVY_GOING': skip_heavy_going,
              'P2_MARKET_TOP3': p2_market_top3, 'P2_STATIC_SAME_COUNT_CONTROL': p2_static_same_count_control,
              'DROP_TRIFECTA': drop_trifecta, 'EXACTA_ONLY': exacta_only, 'CAP30': cap30,
              'W_PLUS_STATIC2_SAME_BUDGET': w_plus_static2_same_budget,
              # DRIVE01 (Drive 精読 2026-11-22, recorded challengers; profiles/KM_JRA_FORWARD_OOS_PREREG_20261128_DRIVE01.json)
              'P3_SHORTEN_SPRINT_FRONT': p3_shorten_sprint_front,
              'P3_SHORTEN_SAME_COUNT_CONTROL': p3_shorten_same_count_control,
              'P3_FIRST_DIRT_BIG_OUTER_FRONT': p3_first_dirt_big_outer_front,
              'P3_FIRST_DIRT_SAME_COUNT_CONTROL': p3_first_dirt_same_count_control,
              'W_WIND8_MARKET_TOP3': w_wind8_market_top3,
              'W_WIND8_STATIC_SAME_COUNT_CONTROL': w_wind8_static_same_count_control}


def _settle(f, official):
    s = settle_final(f, official)
    return s.get('effective_investment', s.get('total_investment', 0)) or 0, s.get('total_payout', 0) or 0


def run(dates, root=ROOT):
    rows = []
    for d in dates:
        for p in sorted(glob.glob(str(root / f'runtime/final_artifacts/KM-JRA-*-{d}-R*.json'))):
            rid = Path(p).stem
            rp = root / 'runtime/results' / f'{rid}.json'
            if not rp.exists():
                continue
            final = json.loads(Path(p).read_text())
            if not (final.get('final_ticket') or {}).get('tickets'):
                continue  # PAPER / NO-BET: not in the paid denominator
            official = json.loads(rp.read_text())['official_result']
            top3 = [str(x) for x in official['finish_order'][:3]]
            base_inv, base_pay = _settle(final, official)
            mk = market_ranking(final, root)
            row = {'race_id': rid, 'top3': top3, 'baseline': {'investment': base_inv, 'payout': base_pay,
                   'W_hit': top3[0] in _live(final, 'W'), 'P2_hit': top3[1] in _live(final, 'P2')},
                   'winner_market_rank': mk.index(top3[0]) + 1 if mk and top3[0] in mk else None}
            for name, fn in CANDIDATES.items():
                f = copy.deepcopy(final)
                if not fn(f):
                    row[name] = None
                    continue
                if f.get('_skip_bet'):
                    row[name] = {'investment': 0, 'payout': 0, 'W_hit': row['baseline']['W_hit'],
                                 'P2_hit': row['baseline']['P2_hit'], 'tickets': 0, 'skipped': True}
                    continue
                if f.get('_drop_bet_types') or f.get('_cap_tickets'):
                    tk, inv0 = _filtered_tickets(f)
                    f['final_ticket'] = {**f['final_ticket'], 'tickets': tk, 'total_investment': inv0}
                    inv, pay = _settle(f, official) if tk else (0, 0)
                    row[name] = {'investment': inv, 'payout': pay, 'W_hit': row['baseline']['W_hit'],
                                 'P2_hit': row['baseline']['P2_hit'], 'tickets': len(tk), 'skipped': not tk}
                    continue
                try:
                    mec = build_mec_plan(f)
                except Exception as exc:  # MEC refusal is itself a result
                    row[name] = {'mec_refused': str(exc)[:160], 'investment': row['baseline']['investment'],
                                 'payout': row['baseline']['payout'], 'W_hit': row['baseline']['W_hit'],
                                 'P2_hit': row['baseline']['P2_hit']}
                    continue
                tk = _post_mec_cap(f, mec['tickets'])
                f['final_ticket'] = {**f['final_ticket'], 'tickets': tk,
                                     'total_investment': sum(int(t.get('stake', 100)) for t in tk)
                                     if f.get('_post_mec_cap') else mec['minimum_required_capital']}
                inv, pay = _settle(f, official)
                row[name] = {'investment': inv, 'payout': pay, 'W_hit': top3[0] in _live(f, 'W'),
                             'P2_hit': top3[1] in _live(f, 'P2'), 'tickets': len(tk)}
            rows.append(row)
    return rows


def summarize(rows):
    out = {}
    for name in ['baseline', *CANDIDATES]:
        changed = [r for r in rows if r.get(name)] if name != 'baseline' else rows
        tot = lambda key, rs, side: sum((r[side] if r.get(side) else r['baseline'])[key] for r in rs)
        if name == 'baseline':
            inv, pay = tot('investment', rows, 'baseline'), tot('payout', rows, 'baseline')
            wh = sum(r['baseline']['W_hit'] for r in rows); p2 = sum(r['baseline']['P2_hit'] for r in rows)
        else:
            inv = sum((r[name] or r['baseline'])['investment'] for r in rows)
            pay = sum((r[name] or r['baseline'])['payout'] for r in rows)
            wh = sum((r[name] or r['baseline'])['W_hit'] for r in rows)
            p2 = sum((r[name] or r['baseline'])['P2_hit'] for r in rows)
        pays = sorted(((r[name] or r['baseline']) if name != 'baseline' else r['baseline'])['payout'] for r in rows)
        out[name] = {'races': len(rows), 'changed_races': len(changed) if name != 'baseline' else 0,
                     'investment': inv, 'payout': pay, 'pfs': round(pay / inv * 100, 2) if inv else None,
                     'pfs_excl_max_payout': round((pay - pays[-1]) / inv * 100, 2) if inv and pays else None,
                     'W_hit': wh, 'P2_hit': p2,
                     'hit_races': sum(1 for r in rows if ((r[name] or r['baseline']) if name != 'baseline' else r['baseline'])['payout'] > 0)}
    miss = [r for r in rows if not r['baseline']['W_hit']]
    out['winner_outside_W'] = {'races': len(miss),
                               'market_rank_1_3': sum(1 for r in miss if (r.get('winner_market_rank') or 99) <= 3),
                               'market_unknown': sum(1 for r in miss if r.get('winner_market_rank') is None)}
    return out


# ---- Forward OOS: freeze candidate tickets before post, evaluate after RESULT ----
FWD = 'runtime/jra_role_candidate_forward'


def _sha(obj):
    import hashlib
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def freeze_forward(date8, root=ROOT, now=None):
    """Freeze every candidate's role set and tickets for FINALs whose post time is still ahead.

    Never freezes after the scheduled post (or for races already resulted); existing
    freezes are immutable."""
    import datetime as dt
    now = now or dt.datetime.now(dt.timezone.utc)
    made = []
    for p in sorted(glob.glob(str(root / f'runtime/final_artifacts/KM-JRA-*-{date8}-R*.json'))):
        rid = Path(p).stem
        out = root / FWD / rid / 'pre_result.json'
        if out.exists() or (root / 'runtime/results' / f'{rid}.json').exists():
            continue
        final = json.loads(Path(p).read_text())
        post = dt.datetime.fromisoformat(final['scheduled_post_at'])
        if now >= post:
            continue
        body = {'profile': 'KM-JRA-ROLE-CANDIDATE-FORWARD-v1', 'race_id': rid, 'final_sha256': final.get('sha256'),
                'scheduled_post_at': final['scheduled_post_at'], 'frozen_at': now.isoformat(),
                'code_sha256': _sha(Path(__file__).read_text()), 'production_effect': 'NONE', 'arms': {}}
        for name, fn in CANDIDATES.items():
            f = copy.deepcopy(final)
            if not (final.get('final_ticket') or {}).get('tickets') or not fn(f):
                body['arms'][name] = None
                continue
            if f.get('_skip_bet'):
                body['arms'][name] = {'W': _live(f, 'W'), 'P2': _live(f, 'P2'), 'P3': _live(f, 'P3'),
                                      'tickets': [], 'investment': 0, 'skipped': True}
                continue
            if f.get('_drop_bet_types') or f.get('_cap_tickets'):
                tk, inv0 = _filtered_tickets(f)
                body['arms'][name] = {'W': _live(f, 'W'), 'P2': _live(f, 'P2'), 'P3': _live(f, 'P3'),
                                      'tickets': tk, 'investment': inv0, 'skipped': not tk,
                                      'dropped_bet_types': f.get('_drop_bet_types'), 'cap_tickets': f.get('_cap_tickets')}
                continue
            try:
                mec = build_mec_plan(f)
            except Exception as exc:
                body['arms'][name] = {'mec_refused': str(exc)[:160]}
                continue
            tk = _post_mec_cap(f, mec['tickets'])
            body['arms'][name] = {'W': _live(f, 'W'), 'P2': _live(f, 'P2'), 'P3': _live(f, 'P3'),
                                  'tickets': tk,
                                  'investment': sum(int(t.get('stake', 100)) for t in tk)
                                  if f.get('_post_mec_cap') else mec['minimum_required_capital'],
                                  'post_mec_cap': f.get('_post_mec_cap')}
        body['sha256'] = _sha(body)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(body, ensure_ascii=False, indent=1) + '\n')
        made.append(rid)
    return made


def evaluate_forward(root=ROOT):
    rows = []
    for p in sorted(glob.glob(str(root / FWD / '*' / 'pre_result.json'))):
        pre = json.loads(Path(p).read_text())
        rid = pre['race_id']
        rp = root / 'runtime/results' / f'{rid}.json'
        if not rp.exists():
            continue
        official = json.loads(rp.read_text())['official_result']
        if not official.get('captured_at') or pre['frozen_at'] >= official['captured_at']:
            continue  # only freezes made before the result count as forward OOS
        final = json.loads((root / 'runtime/final_artifacts' / f'{rid}.json').read_text())
        if not (final.get('final_ticket') or {}).get('tickets'):
            continue
        base_inv, base_pay = _settle(final, official)
        row = {'race_id': rid, 'baseline': {'investment': base_inv, 'payout': base_pay}}
        for name, arm in pre['arms'].items():
            if not arm or 'tickets' not in arm:
                row[name] = None
                continue
            if arm.get('skipped'):
                row[name] = {'investment': 0, 'payout': 0}
                continue
            f = copy.deepcopy(final)
            f['final_ticket'] = {**f['final_ticket'], 'tickets': arm['tickets'], 'total_investment': arm['investment']}
            inv, pay = _settle(f, official)
            row[name] = {'investment': inv, 'payout': pay}
        rows.append(row)
    agg = {}
    for name in ['baseline', *CANDIDATES]:
        inv = sum((r.get(name) or r['baseline'])['investment'] for r in rows)
        pay = sum((r.get(name) or r['baseline'])['payout'] for r in rows)
        agg[name] = {'races': len(rows), 'investment': inv, 'payout': pay,
                     'pfs': round(pay / inv * 100, 2) if inv else None}
    from jra_oos_strata import conditions, keys, split, venue_rule
    for r in rows:
        r['strata'] = keys(r['race_id'], conditions(root, r['race_id']))
    by_arm = {}
    for name in CANDIDATES:
        live = [r for r in rows if r.get(name)]
        if live:  # effect = net profit change vs the frozen Production tickets (yen)
            sp = split(live, lambda r, n=name: (r[n]['payout'] - r[n]['investment'])
                       - (r['baseline']['payout'] - r['baseline']['investment']))
            by_arm[name] = {'strata': sp, 'venue_rule': venue_rule(sp)}
    return {'classification': 'FORWARD_OOS (frozen before result)', 'note': 'no significance claim below 100 races',
            'summary': agg, 'by_arm': by_arm}


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] in ('freeze', 'evaluate'):
    if sys.argv[1] == 'freeze':
        print(json.dumps({'frozen': freeze_forward(sys.argv[2].replace('-', ''))}))
    else:
        print(json.dumps(evaluate_forward(), ensure_ascii=False, indent=1))
    sys.exit(0)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--dates', nargs='+', required=True); ap.add_argument('--out')
    a = ap.parse_args()
    rows = run([d.replace('-', '') for d in a.dates])
    rep = {'profile': 'KM-JRA-ROLE-CANDIDATE-REPLAY-v1', 'classification': 'KNOWN_RESULT_REPLAY / NOT_FORWARD_OOS / NON_PRODUCTION',
           'summary': summarize(rows), 'races': rows}
    if a.out:
        Path(a.out).write_text(json.dumps(rep, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps(rep['summary'], ensure_ascii=False, indent=1))
