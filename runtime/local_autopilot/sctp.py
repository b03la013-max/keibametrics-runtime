"""SCTP 単系主戦・三連複保護層 measurement (Owner 2026-11-28 「どうしますか？実装してください」). Research: the
candidates C32-C34 (GEN:TRIOPROT:k=6/12/18 = C24 with 10/20/30 % of the 60 points as 三連複) are compared with the
delivered C24 by auto_promote at the same budget; this report adds what the trio layer did race by race:
  rescue   = C24 paid 0 and the variant paid > 0
  opp_cost = C24 paid more than the variant (the replaced 三連単 would have paid)
  net      = variant payout - C24 payout
by venue and by field size. C13 (MIX_P2BOX20, 三連複 box + R54) is shown as the existing trio-including control.
Races before the first eligible day of the prereg (R16) are an in-sample reference only.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PREREG = 'KM_LOCAL_FORWARD_OOS_PREREG_20261129_R16.json'
BASE = 'W_PLUS_TOP2POP_60'
ARMS = {'C32 三連複10%': 'GEN:TRIOPROT:k=6', 'C33 三連複20%': 'GEN:TRIOPROT:k=12', 'C34 三連複30%': 'GEN:TRIOPROT:k=18',
        'C13 対照（R54+三連複box）': 'MIX_P2BOX20'}


def _first():
    try:
        return json.loads((REPO / 'profiles' / PREREG).read_text())['first_eligible_post'][:10]
    except (OSError, ValueError, KeyError):
        return '2026-11-29'


def _field(root, day, key):
    try:
        s = json.loads((Path(root) / day / 'formal' / f'{key}.summary.json').read_text())
        n = len(s.get('ranking') or [])
    except (OSError, ValueError):
        return '?'
    return '≤8頭' if n <= 8 else ('9-11頭' if n <= 11 else '12頭以上')


def compare(rows, arm, root=None):
    rs = [r for r in rows if BASE in r and arm in r]
    out = {'races': len(rs), 'invest_c24': sum(r[BASE][0] for r in rs), 'invest': sum(r[arm][0] for r in rs),
           'pay_c24': sum(r[BASE][1] for r in rs), 'pay': sum(r[arm][1] for r in rs),
           'rescue': 0, 'rescue_pay': 0, 'opp_cost': 0, 'opp_cost_pay': 0, 'by_venue': {}, 'by_field': {}}
    for r in rs:
        b, v = r[BASE][1], r[arm][1]
        if b == 0 and v > 0:
            out['rescue'] += 1
            out['rescue_pay'] += v
        if b > v:
            out['opp_cost'] += 1
            out['opp_cost_pay'] += b - v
        for grp, g in (('by_venue', r['key'].split('_')[0]), ('by_field', _field(root, r['day'], r['key']) if root else '?')):
            d = out[grp].setdefault(g, {'races': 0, 'net': 0})
            d['races'] += 1
            d['net'] += v - b
    out['net'] = out['pay'] - out['pay_c24']
    out['pfs_c24'] = round(100 * out['pay_c24'] / out['invest_c24'], 1) if out['invest_c24'] else None
    out['pfs'] = round(100 * out['pay'] / out['invest'], 1) if out['invest'] else None
    return out


def report(root, rows=None):
    if rows is None:
        from runtime.local_autopilot import formal_mix
        rows = formal_mix.races(root)
    first = _first()
    rep = {'prereg': PREREG, 'first_eligible_day': first, 'base': 'C24（配信中）', 'forward': {}, 'reference': {}}
    fw = [r for r in rows if r['day'] >= first]
    ref = [r for r in rows if r['day'] < first]
    for label, arm in ARMS.items():
        rep['forward'][label] = compare(fw, arm, root)
        rep['reference'][label] = compare(ref, arm, root)
    return rep


def md(rep):
    L = ['## SCTP 単系主戦・三連複保護層（研究・同一60点・C24比較）', '',
         f"Forward は {rep['first_eligible_day']} 以降（prereg {rep['prereg']}）。採否は auto_promote の100R同予算規則のみ。", '',
         '| 系 | 区分 | R | PFS(C24) | PFS | 救済R(払戻) | 機会損失R(差額) | 差引 |', '|---|---|---|---|---|---|---|---|']
    for part, name in (('forward', 'Forward'), ('reference', '参考(in-sample)')):
        for label, c in rep[part].items():
            L.append(f"| {label} | {name} | {c['races']} | {c['pfs_c24']} | {c['pfs']} | {c['rescue']}({c['rescue_pay']}) | "
                     f"{c['opp_cost']}({c['opp_cost_pay']}) | {c['net']:+d} |")
    L.append('')
    for label, c in rep['forward'].items():
        if c['races']:
            v = ', '.join(f"{k} {d['net']:+d}({d['races']}R)" for k, d in sorted(c['by_venue'].items()))
            f = ', '.join(f"{k} {d['net']:+d}({d['races']}R)" for k, d in sorted(c['by_field'].items()))
            L.append(f"- {label} 場別: {v} ／ 頭数別: {f}")
    return '\n'.join(L) + '\n'
