"""Offline self-test for LOCAL autopilot settlement rules (no network).

python -m runtime.local_autopilot.selftest
"""
from runtime.local_autopilot import settle


def pred(tickets, ranking=(1, 2, 3, 4, 5)):
    return {'edition': '直前版', 'revision_id': 'T.r1', 'ticket_sha256': 'x', 'saved_at': 't',
            'prediction': {'ranking': [{'no': n} for n in ranking], 'tickets': tickets}}


def check():
    # 1) refund: horse 9 scratched (取消) -> its combinations refunded, not paid
    res = {'order': [1, 2, 3, 4], 'non_starters': [9], 'did_not_finish': [7],
           'payouts': {'WIDE': {(1, 2): 250, (1, 3): 400, (2, 3): 600}, 'TRIO': {(1, 2, 3): 1500},
                       'WIN': {(1,): 300}}}
    st = settle.settle_parsed(res, pred([{'k': 'ワイド', 'b': '1-2 / 1-9'},
                                         {'k': '三連複', 'b': '1-2-3 / 1-2-9 / 1-2-7'}]), 'p')
    assert st['invest'] == 500 and st['refund'] == 200 and st['effective_invest'] == 300, st
    assert st['payout'] == 250 + 1500, st  # 1-2-7: 7 started (中止) -> live, lost, no refund
    assert st['pfs'] == round(100 * 1750 / 300, 1)
    # 2) dead heat for 2nd: two exacta combinations published, both honoured
    res = {'order': [1, 2, 3], 'payouts': {'EXACTA': {(1, 2): 800, (1, 3): 900}}}
    st = settle.settle_parsed(res, pred([{'k': '馬単', 'b': '1→2,3'}]), 'p')
    assert st['payout'] == 1700 and st['invest'] == 200, st
    # 3) bet type not sold / not published -> marked, no phantom payout
    res = {'order': [1, 2, 3], 'payouts': {'WIN': {(1,): 200}}}
    st = settle.settle_parsed(res, pred([{'k': '三連単', 'b': '1→2→3'}]), 'p')
    assert st['tickets'][0]['status'] == 'NOT_SOLD_OR_NOT_PUBLISHED' and st['payout'] == 0
    # 4) everything refunded -> effective investment 0 -> PFS NULL (not 0%)
    res = {'order': [1, 2, 3], 'non_starters': [5], 'payouts': {'WIN': {(1,): 200}}}
    st = settle.settle_parsed(res, pred([{'k': '単勝', 'b': '5'}]), 'p')
    assert st['effective_invest'] == 0 and st['pfs'] is None, st
    # 5) place with 2 paid places (small field)
    res = {'order': [4, 1, 2], 'payouts': {'PLACE': {(4,): 110, (1,): 130}}}
    st = settle.settle_parsed(res, pred([{'k': '複勝', 'b': '1'}]), 'p')
    assert st['payout'] == 130
    # 6) frozen runner absent from every result row -> inferred non-starter refund
    res = {'order': [1, 2, 3], 'payouts': {'WIDE': {(1, 2): 300}}}
    pr = pred([{'k': 'ワイド', 'b': '1-2 / 1-6'}]); pr['runners'] = [{'no': n} for n in (1, 2, 3, 6)]
    st = settle.settle_parsed(res, pr, 'p')
    assert st['non_starters_inferred'] == [6] and st['refund'] == 100 and st['payout'] == 300, st
    print('SELFTEST_OK 6/6')


if __name__ == '__main__':
    check()
