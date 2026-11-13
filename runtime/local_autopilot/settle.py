"""Post-result PAPER settlement for the LOCAL autopilot.

Reads the public Rakuten race result page (/race_performance/), extracts the
official finishing order and the official payouts, and settles the FROZEN
latest pre-cutoff paper tickets at a fixed 100 yen per combination.
  * Never edits the frozen prediction; writes a separate .result.json.
  * PFS = 100 * payout / investment; investment 0 -> PFS None (not 0%).
  * Settles only the revision frozen before cutoff (passed in by the caller).
  * 返還: a combination containing a horse that did not start (取消/除外 on the
    result page) is refunded and removed from the effective investment.
    競走中止 horses started: no refund. Refunds are never counted as payout.
  * Dead heats: every published winning combination is honoured.
This is a PAPER diagnostic: no purchase, no capital decision.
"""
from __future__ import annotations

import itertools
import json
import re
from pathlib import Path

from runtime.local_autopilot.rakuten import lines, nfkc, text

UNIT = 100
KIND = {'単勝': 'WIN', '複勝': 'PLACE', 'ワイド': 'WIDE', '馬連': 'QUINELLA', '馬単': 'EXACTA',
        '三連複': 'TRIO', '三連単': 'TRIFECTA', '枠連': 'BRACKET', '枠単': 'BRACKET_EXACTA'}


def nums(s):
    return [int(x) for x in re.findall(r'\d+', s)]


def expand(ticket):
    """Engine ticket text -> list of combination tuples (ordered for EXACTA/TRIFECTA)."""
    k, b = ticket['k'], ticket['b']
    if k in ('単勝', '複勝'):
        return [(n,) for n in nums(b)]
    if k in ('ワイド', '三連複', '馬連'):
        out = []
        for part in b.split('/'):
            c = tuple(sorted(nums(part)))
            if c and c not in out:
                out.append(c)
        return out
    if k in ('馬単', '三連単'):
        legs = [nums(x) for x in b.split('→')]
        out = []
        for c in itertools.product(*legs):
            if len(set(c)) == len(c) and c not in out:
                out.append(c)
        return out
    return []


PAY_NAMES = {'単勝': 'WIN', '複勝': 'PLACE', 'ワイド': 'WIDE', '馬複': 'QUINELLA', '馬連': 'QUINELLA',
             '馬単': 'EXACTA', '三連複': 'TRIO', '三連単': 'TRIFECTA', '枠複': 'BRACKET', '枠単': 'BRACKET_EXACTA'}
UNORDERED = {'WIDE', 'QUINELLA', 'TRIO', 'BRACKET'}


def parse_result(html):
    """Rakuten /race_performance/: order from <tbody class="record">, payouts
    from the 払戻金 table. Returns None until the result is published."""
    i = html.find('<tbody class="record">')
    body = html[i:html.find('</tbody>', i)] if i >= 0 else ''
    order = []
    non_starters, did_not_finish = [], []
    for row in re.split(r'<tr class="box', body)[1:]:
        pos = re.search(r'<td class="order">(.*?)</td>', row, re.S)
        num = re.search(r'<td class="number">\s*(\d{1,2})\s*</td>', row)
        if not (pos and num):
            continue
        ptxt = text(pos[1])
        if re.fullmatch(r'\d{1,2}', ptxt):
            order.append((int(ptxt), int(num[1])))
        elif any(k in ptxt for k in ('取消', '除外')):
            non_starters.append(int(num[1]))
        elif ptxt:
            did_not_finish.append(int(num[1]))
    order = [h for _, h in sorted(order)]
    j = html.find('summary="払戻金"')
    seg = html[j:html.find('</table>', j)] if j >= 0 else ''
    pays = {}
    for name, nums_html, money_html in re.findall(
            r'<th scope="row">([^<]+)</th>\s*<td class="number">(.*?)</td>\s*<td class="money">(.*?)</td>', seg, re.S):
        kind = PAY_NAMES.get(nfkc(name))
        if not kind:
            continue
        combos = [nfkc(x) for x in re.split(r'<br\s*/?>', nums_html) if nfkc(x)]
        yens = [int(re.sub(r'[^\d]', '', x)) for x in re.split(r'<br\s*/?>', money_html) if re.search(r'\d', x)]
        for c, y in zip(combos, yens):
            t = tuple(nums(c))
            pays.setdefault(kind, {})[tuple(sorted(t)) if kind in UNORDERED else t] = y
    if len(order) < 3 or not pays:
        return None
    return {'order': order, 'payouts': pays, 'non_starters': non_starters, 'did_not_finish': did_not_finish}


def settle(html, prediction_path, settled_at=None):
    res = parse_result(html)
    if res is None:
        return None
    return settle_parsed(res, json.loads(Path(prediction_path).read_text()), str(prediction_path), settled_at)


def settle_parsed(res, pred, prediction_ref, settled_at=None):
    p = pred['prediction']
    order = res['order']
    top3 = set(order[:3])
    rank = [x['no'] for x in p['ranking']]
    gone = set(res.get('non_starters') or [])
    inferred = []
    frozen_runners = {x['no'] for x in pred.get('runners') or []}
    if frozen_runners and len(order) >= 0.6 * len(frozen_runners):  # in the frozen field but on no result row -> did not start
        inferred = sorted(frozen_runners - set(order) - set(res.get('did_not_finish') or []) - gone)
        gone |= set(inferred)
    tickets = []
    gross = refund = payout = 0
    for t in p['tickets']:
        kind = KIND.get(t['k'])
        combos = [tuple(sorted(c)) if kind in UNORDERED else c for c in expand(t)]
        table = res['payouts'].get(kind, {})
        if not table and combos:
            status = 'NOT_SOLD_OR_NOT_PUBLISHED'
        else:
            status = 'SETTLED'
        refunded = [c for c in combos if gone & set(c)]
        live = [c for c in combos if c not in refunded]
        hits = [c for c in live if c in table]
        inv = UNIT * len(combos)
        ref = UNIT * len(refunded)
        pay = sum(table[c] * UNIT // 100 for c in hits)
        gross += inv
        refund += ref
        payout += pay
        tickets.append({'k': t['k'], 'b': t['b'], 'combinations': len(combos), 'refunded': [list(c) for c in refunded],
                        'hits': [list(c) for c in hits], 'invest': inv, 'refund': ref, 'effective_invest': inv - ref,
                        'payout': pay, 'status': status})
    effective = gross - refund
    return {'classification': 'PAPER_SETTLEMENT_FIXED_100_YEN', 'edition': pred['edition'],
            'prediction_ref': prediction_ref, 'revision': pred.get('revision_id'),
            'ticket_sha256': pred.get('ticket_sha256'), 'prediction_saved_at': pred.get('saved_at'),
            'settled_at': settled_at, 'order': order,
            'non_starters': sorted(gone), 'non_starters_inferred': inferred, 'did_not_finish': res.get('did_not_finish', []),
            'payouts': {k: {'-'.join(map(str, c)): v for c, v in d.items()} for k, d in res['payouts'].items()},
            'winner_hit': rank[0] == order[0], 'win_hit': int(rank[0] == order[0]),
            'top_in3': int(rank[0] in top3), 'top3_capture': len(top3 & set(rank[:3])),
            'top4_capture': len(top3 & set(rank[:4])), 'top5_capture': len(top3 & set(rank[:5])),
            'top6_capture': len(top3 & set(rank[:6])),
            'ordered_pair': int(rank[:2] == order[:2]), 'exact_triple': int(rank[:3] == order[:3]),
            'p2_hit': int(len(rank) > 1 and rank[1] == order[1]), 'p3_hit': int(len(rank) > 2 and rank[2] == order[2]),
            'tickets': tickets, 'invest': gross, 'refund': refund, 'effective_invest': effective, 'payout': payout,
            'pfs': round(100 * payout / effective, 1) if effective else None}
