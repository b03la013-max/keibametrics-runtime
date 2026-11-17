"""Post-RESULT detailed review for LOCAL (地方版) races. No network, no Production change.

Re-uses what the existing closed loop already produced and only joins / reads it:
  * PAPER: frozen pre-cutoff revision (rev/<rev>.json) + its settlement (<key>.result.json)
  * FORMAL: Signed FINAL summary/receipt, the formal settlement (formal/<key>.result.json) and the
    Runtime-signed RESULT receipt, whose artifact carries post_result_learning's automatic review
    and next-race learning state (KM-FAMILY-POSTRESULT-CLOSED-LOOP-v1.0)
  * Production Full29 (formal/<key>.full29.json) for index-level evidence

Writes review/<key>.review.json + .md (sha256-bound to the FINAL receipt and result revision),
review/daily_summary.{json,md}, and review/period_summary.{json,md} (weekly / monthly).
Proposals are PROPOSED only: adoption needs genuine forward OOS + Owner review (R53); nothing here
changes a numeric policy, the Owner Static, the KRS Engine, parameter_map, MEC or capital.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

PROFILE = 'KM-LOCAL-POSTRESULT-DETAILED-REVIEW-v1.0-20261116'
ADOPTION = 'PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)'
PAPER_KIND = {'単勝': 'WIN', '複勝': 'PLACE', 'ワイド': 'WIDE', '馬連': 'QUINELLA', '馬単': 'EXACTA',
              '三連複': 'TRIO', '三連単': 'TRIFECTA'}
INDEX_KEYS = ('F3S-L', 'TPI-L', 'SRI-L', 'NCI-L', 'EVI-L', 'T3I-L', 'CFI-L', 'RFI-L', 'HPI-L')


def _sha(x):
    return hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _load(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return None


def _band(distance):
    try:
        d = int(distance)
    except (TypeError, ValueError):
        return 'UNKNOWN'
    return 'SPRINT(<=1300)' if d <= 1300 else 'MILE(1301-1700)' if d <= 1700 else 'MIDDLE(1701-2100)' if d <= 2100 else 'LONG(>2100)'


def _pairs_thirds(tickets):
    """Ordered head>second pairs and (head,second,third) / {trio} coverage of a ticket list
    given as (bet_type, selection[int])."""
    pairs, tri, trio, win = set(), set(), set(), set()
    for bt, sel in tickets:
        if bt in ('EXACTA', 'TRIFECTA') and len(sel) >= 2:
            pairs.add((sel[0], sel[1]))
        if bt == 'TRIFECTA' and len(sel) == 3:
            tri.add(tuple(sel))
        if bt == 'TRIO' and len(sel) == 3:
            trio.add(frozenset(sel))
        if bt == 'WIN' and sel:
            win.add(sel[0])
    return pairs, tri, trio, win


def _paper_tickets(pred):
    import itertools
    out = []
    for t in pred.get('tickets') or []:
        bt = PAPER_KIND.get(t.get('k'))
        b = str(t.get('b') or '')
        if not bt:
            continue
        if bt in ('EXACTA', 'TRIFECTA'):
            legs = [[int(x) for x in leg.replace('、', ',').split(',') if x.strip().isdigit()] for leg in b.split('→')]
            for c in itertools.product(*legs):
                if len(set(c)) == len(c):
                    out.append((bt, list(c)))
        else:
            for part in b.split('/'):
                sel = [int(x) for x in part.replace(',', '-').split('-') if x.strip().isdigit()]
                if sel:
                    out.append((bt, sel))
    return out


def _track(name, ranking, roles, tickets, order, settle_row, marks=None):
    """Common evaluation of one decision track (PAPER or FORMAL) against the official order."""
    pos = {h: i + 1 for i, h in enumerate(order)}
    rank = {h: i + 1 for i, h in enumerate(ranking)}
    w, s, t = (order + [None, None, None])[:3]
    pairs, tri, trio, win = _pairs_thirds(tickets)
    heads = {p[0] for p in pairs} | win
    horses = [{'no': h, 'pre_rank': rank[h], 'mark': (marks or {}).get(str(h)) or (marks or {}).get(h),
               'roles': roles.get(h, []), 'finish': pos.get(h)} for h in ranking]
    ev = {
        'winner_pre_rank': rank.get(w), 'second_pre_rank': rank.get(s), 'third_pre_rank': rank.get(t),
        'winner_in_W': 'W' in roles.get(w, []), 'second_in_P2': 'P2' in roles.get(s, []),
        'third_in_P3': 'P3' in roles.get(t, []),
        'top3_capture': len(set(ranking[:3]) & {w, s, t}), 'top4_capture': len(set(ranking[:4]) & {w, s, t}),
        'winner_is_ticket_head': w in heads,
        'head_local_p2': (w, s) in pairs if w in heads else None,
        'pair_conditioned_third': ((w, s, t) in tri or frozenset((w, s, t)) in trio) if (w, s) in pairs or
        frozenset((w, s, t)) in trio else None,
        'trio_set_covered': frozenset((w, s, t)) in trio or (w, s, t) in tri,
    }
    st = settle_row or {}
    eff = st.get('effective_invest', st.get('invest'))
    money = {'invest': st.get('invest'), 'refund': st.get('refund'), 'effective_invest': eff,
             'payout': st.get('payout'), 'profit_loss': (st.get('payout') or 0) - (eff or 0) if eff is not None else None,
             'pfs': round(100 * st['payout'] / eff, 1) if eff else None,
             'no_bet': bool(eff == 0), 'no_bet_reason': st.get('no_bet_reason') or ('NO_TICKETS' if eff == 0 else None)}
    return {'track': name, 'ranking': ranking, 'horses': horses, 'evaluation': ev, 'settlement': money,
            'first_failure': (st.get('diagnosis') or {}).get('first_failure')}


def _index_evidence(full29, order):
    """Where the actual top3 sat on the Production Full29 indices (not consumed by ranking; evidence only)."""
    if not full29 or not full29.get('runners'):
        return {'status': 'UNKNOWN', 'reason': 'NO_PRODUCTION_FULL29'}
    rows = {int(r['no']): r['indices'] for r in full29['runners']}
    out = {}
    for idx in INDEX_KEYS:
        vals = sorted(((v.get(idx) if v.get(idx) is not None else -1), h) for h, v in rows.items())
        order_by = [h for _, h in sorted(vals, reverse=True)]
        if not any(v.get(idx) is not None for v in rows.values()):
            continue
        out[idx] = {'winner_rank': order_by.index(order[0]) + 1 if order and order[0] in order_by else None,
                    'top3_in_index_top3': len(set(order_by[:3]) & set(order[:3]))}
    cov = full29.get('numeric_coverage') or {}
    neutral = cov.get('ruled_neutral_count'), cov.get('required_count')
    best = sorted(((v['winner_rank'] or 99, k) for k, v in out.items()))[:3]
    return {'status': 'OBSERVED', 'per_index': out, 'ruled_neutral_share': (round(neutral[0] / neutral[1], 3)
            if neutral[0] is not None and neutral[1] else None),
            'indices_ranking_winner_best': [k for _, k in best]}


def _proposal(pid, tier, layer, title, evidence, scope, falsify, oos, metric):
    return {'id': pid, 'tier': tier, 'layer': layer, 'title': title, 'evidence': evidence, 'scope': scope,
            'falsification': falsify, 'next_forward_oos': oos, 'expected_metric': metric, 'status': ADOPTION}


def build(day_dir, key, r):
    day_dir = Path(day_dir)
    st = r.get('settlement') or {}
    order = [int(x) for x in st.get('order') or []]
    if len(order) < 3:
        return None
    venue = r.get('venue_id') or key[:3]
    f = r.get('formal') or {}
    from runtime.local_autopilot.checkpoint10 import effective_dir
    fdir = effective_dir(day_dir, key)    # Revision 2 when the T-10 check re-signed, else Revision 1
    sm = _load(fdir / f'{key}.summary.json') if f.get('status') == 'SIGNED_FINAL' else None
    src = _load(fdir / f'{key}.source_receipt.json') if sm else None
    head = ((src or {}).get('artifact') or {}).get('rakuten_card_header') or {}
    distance = head.get('distance') or r.get('distance')
    scope = {'venue': venue, 'distance': distance, 'distance_band': _band(distance), 'surface': head.get('surface')}

    # PAPER (frozen pre-cutoff revision)
    rev = st.get('revision')
    pf = _load(day_dir / 'rev' / f'{rev}.json') if rev else None
    paper = None
    if pf:
        pred = pf['prediction']
        rk = [int(x['no']) for x in pred['ranking']]
        pr = pf.get('roles') or {}
        proles = defaultdict(list)
        for role in ('W', 'P2', 'P3'):
            v = pr.get(role)
            for h in (v if isinstance(v, list) else [v]):
                if h is not None:
                    proles[int(h)].append(role)
        prow = dict(st)
        prow['diagnosis'] = st.get('diagnosis')
        paper = _track('PAPER', rk, proles, _paper_tickets(pred), order, prow,
                       {str(x['no']): x.get('mark') for x in pred['ranking']})
        paper['refs'] = {'revision': rev, 'ticket_sha256': pf.get('ticket_sha256'), 'frozen_at': pf.get('frozen_at')}
        paper['pace_view'] = pred.get('pace')

    # FORMAL (Signed FINAL + signed RESULT)
    formal, auto, learning, rr = None, None, None, None
    if sm:
        fr = _load(fdir / f'{key}.result.json') or {}
        rr = _load(fdir / f'{key}.result_receipt.json') or {}
        art = rr.get('artifact') or {}
        auto = art.get('automatic_post_result_review')
        learning = art.get('automatic_next_race_learning_state')
        froles = {int(h): v for h, v in (sm.get('roles') or {}).items()}
        ft = [(t['bet_type'], [int(x) for x in t['selection']]) for t in sm.get('tickets') or []]
        fs = dict(fr)
        fs['no_bet_reason'] = 'CAPITAL_POLICY_NO_BET' if sm.get('no_bet') else None
        formal = _track('FORMAL_RECOMMENDATION', [int(x) for x in sm.get('ranking') or []], froles, ft, order, fs,
                        sm.get('marks'))
        formal['refs'] = {'final_receipt_sha256': sm.get('final_receipt_sha256'),
                          'result_receipt_sha256': rr.get('receipt_sha256'),
                          'result_receipt_verified': (r.get('formal_settlement') or {}).get('result_receipt_verified'),
                          'krs_input_mode': sm.get('krs_input_mode'), 'authority': (sm.get('authority') or {}).get('manifest_id'),
                          'prediction_consumer': sm.get('prediction_consumer'),
                          'local_ticket_cap_sha256': sm.get('local_ticket_cap_sha256'),
                          'signed_final_ticket_count': sm.get('signed_final_ticket_count'),
                          'signed_final_total_investment': sm.get('signed_final_total_investment'),
                          'signed_final_settlement': fr.get('signed_final_settlement')}
        formal['first_material_failure'] = ((auto or {}).get('failure_localization') or {}).get('first_material_failure')
    full29 = _load(fdir / f'{key}.full29.json') if sm else None
    idx_ev = _index_evidence(full29, order)

    # layer analysis
    layers = {}
    layers['SOURCE'] = ({'status': 'OK', 'evidence': 'Signed SOURCE frozen before cutoff; runner universe matched'}
                        if sm else {'status': 'UNKNOWN', 'evidence': 'no formal SOURCE for this race (PAPER only)'})
    if st.get('non_starters') or st.get('non_starters_inferred'):
        layers['SOURCE'] = {'status': 'ISSUE', 'evidence': f"non-starters after freeze {st.get('non_starters') or st.get('non_starters_inferred')}"}
    if idx_ev['status'] == 'OBSERVED':
        wr = {k: v['winner_rank'] for k, v in idx_ev['per_index'].items()}
        layers['INDEX'] = {'status': 'OBSERVED', 'evidence': {'winner_rank_by_index': wr,
                           'ruled_neutral_share': idx_ev['ruled_neutral_share']}}
    else:
        layers['INDEX'] = {'status': 'UNKNOWN', 'evidence': idx_ev.get('reason')}
    layers['DAY_STATE'] = {'status': 'UNKNOWN', 'evidence': 'body weight / paddock / track-bias effect not measured in the frozen artifacts'}
    layers['PACE'] = {'status': 'UNKNOWN', 'evidence': {'paper_pace_view': (paper or {}).get('pace_view'),
                      'note': 'actual running positions not in the stored result; cannot confirm'}}
    main = formal or paper
    e = main['evaluation']
    layers['ROLE'] = {'status': 'OK' if e['winner_in_W'] and e['second_in_P2'] and e['third_in_P3'] else 'ISSUE',
                      'evidence': {k: e[k] for k in ('winner_pre_rank', 'second_pre_rank', 'third_pre_rank',
                                                     'winner_in_W', 'second_in_P2', 'third_in_P3')}}
    kr = ((auto or {}).get('krs') or {})
    layers['KRS'] = {'status': 'UNKNOWN' if (kr.get('post_result_evaluation') or {}).get('classification') in (None, 'NOT_AVAILABLE')
                     else 'OBSERVED', 'evidence': kr or {'research_krs': list((r.get('research_krs') or {}).keys())}}
    conv = (auto or {}).get('conversion') or {}
    layers['TICKET'] = {'status': 'OK' if main['settlement']['payout'] else 'ISSUE',
                        'evidence': {'head_local_p2': e['head_local_p2'], 'pair_conditioned_third': e['pair_conditioned_third'],
                                     'trio_set_covered': e['trio_set_covered'], **{k: conv.get(k) for k in
                                     ('ordered_pair_ticket_coverage', 'top3_set_ticket_coverage', 'ordered_exact_ticket_coverage')}}}
    cap = (auto or {}).get('capital') or {}
    m = main['settlement']
    layers['CAPITAL'] = {'status': 'OK' if (m['pfs'] or 0) >= 100 else 'ISSUE' if m['effective_invest'] else 'UNKNOWN',
                         'evidence': {'pfs': m['pfs'], 'profit_loss': m['profit_loss'], 'hit_but_loss': cap.get('hit_but_loss'),
                                      'tickets': len(formal['horses']) if False else (sm or {}).get('ticket_count')}}

    correct = [k for k, ok in (('winner_in_W', e['winner_in_W']), ('second_in_P2', e['second_in_P2']),
                               ('third_in_P3', e['third_in_P3']), ('winner_is_ticket_head', e['winner_is_ticket_head']),
                               ('head_local_p2', e['head_local_p2']), ('pair_conditioned_third', e['pair_conditioned_third']),
                               ('trio_set_covered', e['trio_set_covered']), ('payout_positive', bool(m['payout'])),
                               ('pfs_at_least_100', (m['pfs'] or 0) >= 100)) if ok]
    first = (formal or {}).get('first_material_failure') or main.get('first_failure') or 'UNKNOWN'

    # proposals
    P = []
    if sm and not (formal['refs'].get('result_receipt_verified')):
        P.append(_proposal('P0:RESULT_RECEIPT_UNVERIFIED', 'P0', 'EXECUTION', 'Signed RESULT not verified',
                           'formal settlement exists without a verified RESULT receipt', scope,
                           'next 20 formal races all carry verified RESULT receipts', 'monitor FORMAL_RESULT log + receipts',
                           'RESULT receipt verification rate = 100%'))
    if f and f.get('status') != 'SIGNED_FINAL':
        P.append(_proposal(f"P0:FORMAL_HOLD:{f.get('first_failed_stage')}", 'P0', 'EXECUTION',
                           'Formal path held before Signed FINAL', f"{f.get('first_failed_stage')}: {str(f.get('error'))[:160]}",
                           scope, 'next 20 eligible races reach Signed FINAL', 'formal completion rate per venue',
                           'formal Signed FINAL rate'))
    if sm and layers['KRS']['status'] == 'UNKNOWN':
        P.append(_proposal('P0:KRS_UTILITY_NOT_AVAILABLE', 'P0', 'KRS', 'KRS post-result evaluation not available',
                           'automatic review krs.post_result_evaluation = NOT_AVAILABLE (utility not frozen in FINAL)', scope,
                           'next formal races carry krs_prediction_utility in the FINAL package',
                           'check FINAL package krs_prediction_utility_shadow presence', 'KRS evaluation availability rate'))
    if not e['winner_in_W']:
        alt = []
        if paper and formal and paper['evaluation']['winner_pre_rank'] == 1:
            alt.append('PAPER ◎ was the winner')
        if idx_ev['status'] == 'OBSERVED':
            alt += [f"{k} ranked the winner #{v['winner_rank']}" for k, v in idx_ev['per_index'].items()
                    if v['winner_rank'] == 1]
        P.append(_proposal('P1:ROLE_W_MISS', 'P1', 'ROLE', 'Winner outside W',
                           {'winner_pre_rank': e['winner_pre_rank'], 'alternative_signals_that_had_winner_top': alt}, scope,
                           'over >=30 forward races at this venue/band the alternative signal top-1 does not beat the current '
                           'W set on W-capture', 'shadow-score the alternative signal vs current W on every forward race '
                           '(frozen pre-cutoff, same venue/distance band)', 'W-capture rate, PFS'))
    elif not e['second_in_P2']:
        P.append(_proposal('P1:ROLE_P2_MISS', 'P1', 'ROLE', 'Second outside P2', {'second_pre_rank': e['second_pre_rank']},
                           scope, '>=30 forward races: widening P2 by the next-ranked runner adds < its ticket cost in payout',
                           'counterfactual P2+1 on frozen forward races (no reselection)', 'P2 capture, PFS'))
    elif not e['third_in_P3']:
        P.append(_proposal('P1:ROLE_P3_MISS', 'P1', 'ROLE', 'Third outside P3', {'third_pre_rank': e['third_pre_rank']},
                           scope, '>=30 forward races: P3 tail extension does not raise PFS', 'counterfactual P3 tail on frozen races',
                           'P3 capture, PFS'))
    if e['winner_in_W'] and e['second_in_P2'] and e['head_local_p2'] is False:
        P.append(_proposal('P1:HEAD_LOCAL_P2_CONVERSION', 'P1', 'TICKET', 'Roles captured but ordered pair not ticketed',
                           conv or e, scope, '>=30 races: MEC ordered-pair coverage already complete when roles hit',
                           'audit MEC coverage on frozen FINALs where W/P2 hit', 'ordered-pair conversion rate'))
    if m['payout'] and (m['pfs'] or 0) < 100:
        P.append(_proposal('P1:HIT_BUT_LOSS', 'P1', 'CAPITAL', 'Hit but PFS < 100', {'pfs': m['pfs'],
                           'tickets': (sm or {}).get('ticket_count'), 'payout': m['payout']}, scope,
                           '>=30 hit races: ticket-count reduction would also remove the hit',
                           'counterfactual MEC compression on frozen settled arms (no reselection)', 'PFS on hit races'))
    P.append(_proposal('P2:CALIBRATION_BACKLOG', 'P2', 'CALIBRATION',
                       'Probability / EV / Kelly not computable (uncalibrated)', 'calibration status UNCALIBRATED',
                       scope, 'n/a until >=100 runners and >=20 target events per stratum (較正・検証運用条項 第12条)',
                       'accumulate frozen predictions + results per venue/distance band; Brier/ECE once thresholds met',
                       'Brier score, ECE, capture'))
    if idx_ev['status'] == 'OBSERVED' and (idx_ev.get('ruled_neutral_share') or 0) > 0.15:
        P.append(_proposal('P2:INDEX_OBSERVATION_COVERAGE', 'P2', 'INDEX', 'High RULED-NEUTRAL share in Full29',
                           {'ruled_neutral_share': idx_ev['ruled_neutral_share']}, scope,
                           'ruled-neutral share falls below 15% without source changes',
                           'per-venue observation rate in forward_summary', 'CALCULATED share'))

    body = {'profile': PROFILE, 'race_key': key, 'race_date': r.get('race_date') or day_dir.name, 'venue': venue,
            'race_no': r.get('race_no'), 'post': r.get('post_current'), 'scope': scope,
            'official_result': {'order': order, 'top3': order[:3], 'non_starters': st.get('non_starters'),
                                'payouts': {k: v for k, v in (_load(day_dir / f'{key}.result.json') or {}).get('payouts', {}).items()
                                            if k in ('WIN', 'EXACTA', 'TRIO', 'TRIFECTA')}},
            'paper': paper, 'formal_recommendation': formal, 'actual_purchase': 'NONE (no real purchase)',
            'automatic_post_result_review_sha256': (auto or {}).get('sha256'),
            'learning_state': ({'state_id': learning.get('state_id'), 'sha256': learning.get('sha256'),
                                'shadow_candidates': learning.get('shadow_candidates'),
                                'production_change_authorized': learning.get('production_change_authorized')} if learning else None),
            'index_evidence': idx_ev, 'layers': layers, 'correct_items': correct,
            'first_material_failure': first, 'proposals': P,
            'next_research_link': {'aggregated_in': ['review/daily_summary.json', 'review/period_summary.json'],
                                   'proposal_ids': [p['id'] for p in P]},
            'adoption_rule': ADOPTION}
    body['sha256'] = _sha(body)
    return body


def _md(b):
    fm, pa = b.get('formal_recommendation'), b.get('paper')
    L = [f"# {b['race_date']} {b['race_key']} 詳細反省（自動・実購入なし）", '',
         f"- 公式着順：{'-'.join(map(str, b['official_result']['order'][:5]))}（上位3頭 {b['official_result']['top3']}）",
         f"- 距離帯：{b['scope']['distance_band']}／第一実質失敗：**{b['first_material_failure']}**",
         f"- 正しく判断できた項目：{', '.join(b['correct_items']) or 'なし'}", '']
    for t in (pa, fm):
        if not t:
            continue
        e, m = t['evaluation'], t['settlement']
        L += [f"## {t['track']}", '',
              f"- 1着の事前順位 {e['winner_pre_rank']}／2着 {e['second_pre_rank']}／3着 {e['third_pre_rank']}；"
              f"W {e['winner_in_W']}・P2 {e['second_in_P2']}・P3 {e['third_in_P3']}",
              f"- Top3捕捉 {e['top3_capture']}／Top4捕捉 {e['top4_capture']}；Head-local P2 {e['head_local_p2']}；"
              f"Pair条件付き3着 {e['pair_conditioned_third']}",
              f"- 投資 {m['effective_invest']}／返還 {m['refund']}／払戻 {m['payout']}／損益 {m['profit_loss']}／PFS {m['pfs']}%"
              + (f"／NO-BET {m['no_bet_reason']}" if m['no_bet'] else ''),
              f"- 参照：{json.dumps(t.get('refs'), ensure_ascii=False)}", '']
    L += ['## 工程別', '', '| 工程 | 状態 | 根拠 |', '|---|---|---|']
    for k, v in b['layers'].items():
        L.append(f"| {k} | {v['status']} | {json.dumps(v['evidence'], ensure_ascii=False)[:180]} |")
    L += ['', '## 改善提案（PROPOSED・自動採用なし）', '', '| ID | 区分 | 根拠 | 反証条件 | 次のForward OOS | 指標 |', '|---|---|---|---|---|---|']
    for p in b['proposals']:
        L.append(f"| {p['id']} | {p['tier']} | {json.dumps(p['evidence'], ensure_ascii=False)[:120]} | {p['falsification'][:80]} | "
                 f"{p['next_forward_oos'][:80]} | {p['expected_metric']} |")
    L += ['', f"<sub>review sha256 `{b['sha256'][:16]}`／Learning State `{(b.get('learning_state') or {}).get('sha256', '')[:12]}`</sub>"]
    return '\n'.join(L) + '\n'


def write_race(day_dir, key, r):
    b = build(day_dir, key, r)
    if b is None:
        return None
    d = Path(day_dir) / 'review'
    d.mkdir(exist_ok=True)
    (d / f'{key}.review.json').write_text(json.dumps(b, ensure_ascii=False, indent=1) + '\n')
    (d / f'{key}.review.md').write_text(_md(b))
    return b


def _impact(b):
    t = b.get('formal_recommendation') or b.get('paper') or {}
    pl = (t.get('settlement') or {}).get('profit_loss')
    return -pl if isinstance(pl, (int, float)) and pl < 0 else 0


ACC_KEYS = ('winner_pre_rank_1', 'winner_in_top3', 'winner_in_W', 'second_in_P2', 'third_in_P3',
            'winner_is_ticket_head', 'trio_set_covered')


def _accuracy(reviews):
    """Accuracy measured separately from PFS (vision: 精度・回収・規格を別々に測る). Rates in %, per track,
    overall and per venue. Evidence only: never consumed by ranking, tickets or capital."""
    def one(bs, track):
        ev = [(b.get(track) or {}).get('evaluation') for b in bs]
        ev = [e for e in ev if e]
        if not ev:
            return None
        flag = {'winner_pre_rank_1': lambda e: e.get('winner_pre_rank') == 1,
                'winner_in_top3': lambda e: isinstance(e.get('winner_pre_rank'), int) and e['winner_pre_rank'] <= 3}
        out = {'races': len(ev)}
        for k in ACC_KEYS:
            f = flag.get(k, lambda e, k=k: e.get(k) is True)
            out[k] = round(100 * sum(1 for e in ev if f(e)) / len(ev), 1)
        out['mean_top3_capture'] = round(sum(e.get('top3_capture') or 0 for e in ev) / len(ev), 2)
        return out
    venues = sorted({b['venue'] for b in reviews})
    return {track: {'all': one(reviews, track),
                    'by_venue': {v: one([b for b in reviews if b['venue'] == v], track) for v in venues}}
            for track in ('paper', 'formal_recommendation')}


def _aggregate(reviews):
    by_venue = defaultdict(lambda: {'races': 0, 'paper_eff': 0, 'paper_pay': 0, 'formal_eff': 0, 'formal_pay': 0,
                                    'first_failure': Counter()})
    props = defaultdict(lambda: {'count': 0, 'impact_yen': 0, 'races': [], 'tier': None, 'layer': None, 'title': None})
    for b in reviews:
        v = by_venue[b['venue']]
        v['races'] += 1
        for tk, ek, pk in (('paper', 'paper_eff', 'paper_pay'), ('formal_recommendation', 'formal_eff', 'formal_pay')):
            m = (b.get(tk) or {}).get('settlement') or {}
            v[ek] += m.get('effective_invest') or 0
            v[pk] += m.get('payout') or 0
        v['first_failure'][b['first_material_failure']] += 1
        for p in b['proposals']:
            a = props[p['id']]
            a['count'] += 1
            a['impact_yen'] += _impact(b)
            a['races'].append(f"{b['race_date']}:{b['race_key']}")
            a['tier'], a['layer'], a['title'] = p['tier'], p['layer'], p['title']
    venues = {}
    for k, v in sorted(by_venue.items()):
        venues[k] = {'races': v['races'], 'paper_pfs': round(100 * v['paper_pay'] / v['paper_eff'], 1) if v['paper_eff'] else None,
                     'formal_pfs': round(100 * v['formal_pay'] / v['formal_eff'], 1) if v['formal_eff'] else None,
                     'paper_effective_invest': v['paper_eff'], 'paper_payout': v['paper_pay'],
                     'formal_effective_invest': v['formal_eff'], 'formal_payout': v['formal_pay'],
                     'first_failure': dict(v['first_failure'])}
    tier_rank = {'P0': 0, 'P1': 1, 'P2': 2}
    ranked = sorted(({'id': k, **{x: y for x, y in a.items() if x != 'races'}, 'race_count': len(a['races']),
                      'evidence_strength': 'RECURRING' if a['count'] >= 3 else 'SINGLE_OR_FEW (過大評価しない)'}
                     for k, a in props.items()),
                    key=lambda x: (tier_rank.get(x['tier'], 9), -x['count'], -x['impact_yen']))
    tot = lambda f: sum(v[f] for v in venues.values())
    return {'races': len(reviews), 'by_venue': venues, 'accuracy': _accuracy(reviews),
            'all_local': {'paper_pfs': round(100 * tot('paper_payout') / tot('paper_effective_invest'), 1) if tot('paper_effective_invest') else None,
                          'formal_pfs': round(100 * tot('formal_payout') / tot('formal_effective_invest'), 1) if tot('formal_effective_invest') else None,
                          'first_failure': dict(sum((Counter(v['first_failure']) for v in venues.values()), Counter()))},
            'improvement_priority': ranked, 'adoption_rule': ADOPTION}


def _audit(day_dir, q):
    """日次自律監査 6項目 (Delivery / 計算完走 / 精度 / PFS / Learning / 障害・改善), from existing artifacts."""
    from runtime.local_autopilot import delivery_ledger
    led = delivery_ledger.build(q, day_dir)['summary']
    races = q['races'].values()
    formal = [r['formal'] for r in races if r.get('formal')]
    full29 = len(list((day_dir / 'formal').glob('*.full29.json'))) if (day_dir / 'formal').exists() else 0
    fset = [r['formal_settlement'] for r in races if (r.get('formal_settlement') or {}).get('result_receipt_verified')]
    bind = []
    for p in sorted((day_dir / 'formal').glob('*.summary.json')) if (day_dir / 'formal').exists() else []:
        try:
            bind.append(len(json.loads(p.read_text()).get('learning_state_bindings') or []))
        except ValueError:
            pass
    fo = Path(day_dir).parent / 'forward_oos_local.json'
    oos = json.loads(fo.read_text())['candidates'] if fo.exists() else None
    return {
        '1_delivery': {'races_managed': led['races_managed'], 'formal_eligible_attempted': led['formal']['attempted'],
                       'paper_prestart_submitted': led['paper']['submitted_prestart'],
                       'formal_prestart_submitted': led['formal']['submitted_prestart'],
                       'user_reached_owner_confirmed': led['paper']['user_reached_owner_confirmed']
                       + led['formal']['user_reached_owner_confirmed']},
        '2_computation': {'full29': full29, 'signed_final': sum(1 for f in formal if f.get('status') == 'SIGNED_FINAL'),
                          'krs_5000': sum(1 for f in formal if f.get('krs_actual_run_count') == 5000),
                          'no_bet': sum(1 for f in formal if f.get('no_bet')),
                          'hold': dict(Counter(f.get('first_failed_stage') or 'UNKNOWN' for f in formal
                                               if f.get('status') != 'SIGNED_FINAL'))},
        '3_accuracy': 'see accuracy',
        '4_pfs': {'paper_pfs': None, 'formal_pfs': None, 'actual_purchase': 'NONE (実購入なし)'},
        '5_learning': {'result_receipts_verified': len(fset),
                       'learning_states_saved': sum(1 for x in fset if x.get('learning_state_id')),
                       'formal_races_binding_prior_states': sum(1 for b in bind if b),
                       'production_change_authorized': False},
        '6_failures': {'first_stops': led['first_stops'], 'formal_stops': led.get('formal_stops'),
                       'oos_progress': {k: v.get('stage') for k, v in (oos or {}).items()}},
    }


def write_daily(day_dir, q):
    day_dir = Path(day_dir)
    reviews = [json.loads(p.read_text()) for p in sorted((day_dir / 'review').glob('*.review.json'))] \
        if (day_dir / 'review').exists() else []
    if not reviews:
        return None
    terminal = all(r.get('settlement') or r.get('status') in ('MISSED_DEADLINE', 'SOURCE_HOLD', 'PREDICTION_FAILURE')
                   for r in q['races'].values())
    s = {'profile': PROFILE + '-DAILY', 'race_date': day_dir.name, 'complete_day': terminal, **_aggregate(reviews)}
    try:
        s['daily_audit'] = _audit(day_dir, q)
    except Exception as exc:  # the audit never blocks the review summary
        s['daily_audit'] = {'error': f'{type(exc).__name__}:{str(exc)[:120]}'}
    s['sha256'] = _sha(s)
    (day_dir / 'review' / 'daily_summary.json').write_text(json.dumps(s, ensure_ascii=False, indent=1) + '\n')
    (day_dir / 'review' / 'daily_summary.md').write_text(_summary_md(f"{day_dir.name} 日次総括" + ('' if terminal else '（途中）'), s))
    return s


def _summary_md(title, s):
    L = [f"# 地方版 {title}（自動・推薦試算・実購入なし）", '',
         f"- 反省済みRace {s['races']}／PAPER PFS {s['all_local']['paper_pfs']}%／正式推薦 PFS {s['all_local']['formal_pfs']}%",
         f"- 第一失敗：{s['all_local']['first_failure']}", '', '| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |', '|---|---|---|---|---|']
    for k, v in s['by_venue'].items():
        L.append(f"| {k} | {v['races']} | {v['paper_pfs']} | {v['formal_pfs']} | {v['first_failure']} |")
    au = s.get('daily_audit') or {}
    if au and 'error' not in au:
        d1, d2, d5, d6 = au['1_delivery'], au['2_computation'], au['5_learning'], au['6_failures']
        L += ['', '## 日次自律監査', '',
              f"1. 配送：管理 {d1['races_managed']}R／PAPER発走前送信 {d1['paper_prestart_submitted']}／正式試行 "
              f"{d1['formal_eligible_attempted']}・発走前送信 {d1['formal_prestart_submitted']}／本人確認 {d1['user_reached_owner_confirmed']}",
              f"2. 計算完走：Full29 {d2['full29']}／Signed FINAL {d2['signed_final']}／KRS5000 {d2['krs_5000']}／NO-BET {d2['no_bet']}"
              f"／HOLD {d2['hold'] or 'なし'}",
              '3. 精度：下表', f"4. PFS：PAPER {s['all_local']['paper_pfs']}%／正式推薦 {s['all_local']['formal_pfs']}%／実購入なし",
              f"5. Learning：RESULT署名検証 {d5['result_receipts_verified']}／学習状態保存 {d5['learning_states_saved']}"
              f"／前Raceの学習状態を結合した正式Race {d5['formal_races_binding_prior_states']}（Production変更なし）",
              f"6. 障害・改善：停止 {d6['first_stops'] or 'なし'}／正式停止 {d6['formal_stops'] or 'なし'}／OOS進捗 {d6['oos_progress']}"]
    acc = s.get('accuracy') or {}
    L += ['', '## 精度（回収とは別に測定）', '',
          '| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for track, label in (('paper', 'PAPER'), ('formal_recommendation', '正式推薦')):
        a = (acc.get(track) or {}).get('all')
        if a:
            L.append(f"| {label} | {a['races']} | " + ' | '.join(f"{a[k]}%" for k in ACC_KEYS) + f" | {a['mean_top3_capture']} |")
    L += ['', '## 改善優先順位（P0→P1→P2、件数・影響額順）', '', '| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |', '|---|---|---|---|---|']
    for p in s['improvement_priority'][:20]:
        L.append(f"| {p['id']} | {p['tier']} | {p['count']} | {p['impact_yen']:,} | {p['evidence_strength']} |")
    L += ['', f"<sub>{s['adoption_rule']}</sub>"]
    return '\n'.join(L) + '\n'


def write_periods(root):
    root = Path(root)
    reviews = []
    for p in sorted(root.glob('20*/review/*.review.json')):
        try:
            reviews.append(json.loads(p.read_text()))
        except ValueError:
            continue
    if not reviews:
        return None
    weeks, months = defaultdict(list), defaultdict(list)
    for b in reviews:
        d = date.fromisoformat(b['race_date'])
        y, w, _ = d.isocalendar()
        weeks[f'{y}-W{w:02d}'].append(b)
        months[d.strftime('%Y-%m')].append(b)
    out = {'profile': PROFILE + '-PERIOD', 'weekly': {k: _aggregate(v) for k, v in sorted(weeks.items())},
           'monthly': {k: _aggregate(v) for k, v in sorted(months.items())}}
    out['sha256'] = _sha(out)
    (root / 'review_period_summary.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    L = []
    for label, grp in (('週次', out['weekly']), ('月次', out['monthly'])):
        for k, s in list(grp.items())[-2:]:
            L.append(_summary_md(f'{label} {k}', s))
    (root / 'review_period_summary.md').write_text('\n'.join(L))
    return out
