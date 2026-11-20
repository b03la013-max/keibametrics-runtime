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
    return [(t['bet_type'], [int(x) for x in t['selection']]) for t in summary.get('tickets') or []]


def variants(summary):
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
            'KEEP_MEC_TRIO20': fill(mec_trio), 'THIRD3_BY_PAIR': third[:CAP]}


def races(root, since=None):
    out = []
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
        for name, t in variants(summ).items():
            i, p, h = sm.settle(t, res['payouts'], ns)
            row[name] = (i, p, h, len(t))
        out.append(row)
    return out


def evaluate(root, since=None):
    rs = races(root, since)
    agg = {}
    for name in ('R54_60', 'MIX_P2BOX20', 'P2BOX20_ONLY', 'MIX_WAXIS_TRIO', 'KEEP_MEC_TRIO20', 'THIRD3_BY_PAIR'):
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
