"""Read-only per-race first-failure classifier for a settled JRA day (NON-PRODUCTION research).

For every FINAL with an official RESULT it records Static rank / KRS SSR-W rank of
the actual 1st/2nd/3rd, the formal W/P2/P3 sets, the first role failure stage and
the capital outcome. Nothing here feeds Production.
"""
import argparse, glob, json
from pathlib import Path


def _roles(f, col):
    return [str(x['runner_id']) for x in f['role_registry'] if x['column'] == col and x['status'] != 'EXCLUDED']


def delivered_failure(top3, W, P2, tickets, investment, payout):
    """First material failure of the DELIVERED ticket set (LOCAL review.delivered_failure port):
    W miss -> P2 miss -> no live ticket -> hit but loss -> NONE. PAPER / NO-BET are not failures."""
    if not tickets:
        return 'NO_BET_OR_PAPER'
    if top3[0] not in W:
        return 'PREDICTION_ROLE_W'
    if top3[1] not in P2:
        return 'PREDICTION_ROLE_P2'
    if payout == 0:
        return 'TICKET_SELECTION'
    if payout < investment:
        return 'CAPITAL_EFFICIENCY'
    return 'NONE'


def ticket_coverage(top3, tickets):
    """Coverage of the settled ticket set itself (so flags describe the same object as the money)."""
    w, s, t = (top3 + [None, None, None])[:3]
    sel = [(x['bet_type'], [str(h) for h in x['selection']]) for x in tickets]
    ex = {tuple(v[:2]) for b, v in sel if b == 'EXACTA'}
    tri = {tuple(v[:3]) for b, v in sel if b == 'TRIFECTA'}
    trio = {frozenset(v[:3]) for b, v in sel if b == 'TRIO'}
    return {'ordered_pair': (w, s) in ex or any(v[:2] == (w, s) for v in tri),
            'top3_set': frozenset((w, s, t)) in trio or (w, s, t) in tri,
            'exact_order': (w, s, t) in tri}


def classify(root: Path, date8: str) -> list:
    out = []
    for p in sorted(glob.glob(str(root / f'runtime/final_artifacts/KM-JRA-*-{date8}-R*.json'))):
        rid = Path(p).stem
        rp = root / 'runtime/results' / f'{rid}.json'
        if not rp.exists():
            continue
        res = json.loads(rp.read_text())
        fo = [str(x) for x in res['official_result']['finish_order'][:3]]
        f = json.loads(Path(p).read_text())
        rank = [str(x) for x in f['static_prediction']['ranking']]
        srank = lambda h: rank.index(h) + 1 if h in rank else None
        summ = (f.get('krs_prediction_utility') or {}).get('summary') or []
        kr = [str(x['horse_no']) for x in sorted(summ, key=lambda x: -(x.get('SSR-W') or 0))]
        krank = lambda h: kr.index(h) + 1 if h in kr else None
        W, P2, P3 = _roles(f, 'W'), _roles(f, 'P2'), _roles(f, 'P3')
        aki = f['static_prediction'].get('aki_jra_v21') or {}
        w = fo[0]
        if w in W:
            stage = 'W_OK' if fo[1] in P2 else 'HEAD_LOCAL_P2'
            if stage == 'W_OK' and fo[2] not in P3:
                stage = 'THIRD'
            if stage == 'W_OK':
                stage = 'ROLES_OK'
        else:
            r = srank(w)
            stage = 'W_WIDTH_OR_ROLE(static<=3)' if r and r <= 3 else ('W_NEAR(4-6)' if r and r <= 6 else 'W_DISCOVERY(7+)')
        st = res.get('settlement') or {}
        pay = st.get('total_payout') or 0
        pl = st.get('profit_loss')
        inv = (pay - pl) if pl is not None else (st.get('total_investment') or 0)
        tickets = (f.get('final_ticket') or {}).get('tickets') or []
        out.append({'race_id': rid,
                    'delivered_failure': delivered_failure(fo, W, P2, tickets, inv, pay),
                    'ticket_coverage': ticket_coverage(fo, tickets) if tickets else None,
                    'role_width': {'field': len(rank), 'W': len(W), 'P2': len(P2), 'P3': len(P3)}, 'top3': fo, 'static_rank_top3': [srank(h) for h in fo],
                    'krs_ssrw_rank_winner': krank(w), 'W': W, 'P2': P2, 'P3': P3,
                    'W_static_ranks': [srank(h) for h in W], 'axis_rule': aki.get('axis_candidate_rule'),
                    'ASI': (aki.get('axes') or {}).get('ASI'), 'first_failure_stage': stage,
                    'tickets': len((f.get('final_ticket') or {}).get('tickets') or []),
                    'investment': inv, 'payout': pay,
                    'krs_winner_rescue_available': bool(krank(w) and krank(w) <= 3 and w not in W)})
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--date', required=True); ap.add_argument('--root', default='.')
    a = ap.parse_args()
    rows = classify(Path(a.root).resolve(), a.date.replace('-', ''))
    print(json.dumps({'profile': 'KM-JRA-DAY-FAILURE-FIXTURES-v1', 'production_effect': 'NONE',
                      'races': rows}, ensure_ascii=False, indent=1))
