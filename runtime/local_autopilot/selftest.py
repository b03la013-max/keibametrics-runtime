"""Offline self-test for LOCAL autopilot settlement rules (no network).

python -m runtime.local_autopilot.selftest
"""
from runtime.local_autopilot import engine, settle


def pred(tickets, ranking=(1, 2, 3, 4, 5)):
    return {'edition': '直前版', 'revision_id': 'T.r1', 'ticket_sha256': 'x', 'saved_at': 't',
            'prediction': {'ranking': [{'no': n} for n in ranking], 'tickets': tickets}}



def check_probability():
    # Real frozen SAG_05 2026-11-15 prestart shape: four odds were present
    # (one at 1.0), seven odds missing. Legacy mixture summed to 1.35543.
    f3s = [71.556821859212, 71.1674335718002, 69.60935226790131,
           67.7550092463947, 66.52697304587575, 63.704243409636135,
           62.00186269216131, 61.789531697859275, 58.63369282963493,
           50.69997006167512, 48.299246050292865]
    odds = [0, 0, 1.0, 0, 10.4, 0, 0, 10.4, 0, 10.4, 0]
    rows = [{'F3S': score, 'win': price} for score, price in zip(f3s, odds)]
    assert engine.assign_win_probabilities(rows) is False
    assert abs(sum(r['p_win'] for r in rows) - 1.0) < 1e-12
    assert all(r['p_market'] is None and r['p_win'] == r['p_model'] for r in rows)

    # No market at all: exact softmax fallback, including F3S ties.
    missing = [{'F3S': 52.0, 'win': None} for _ in range(5)]
    assert engine.assign_win_probabilities(missing) is False
    assert all(abs(r['p_win'] - 0.2) < 1e-12 for r in missing)

    # Complete market: retain the original 50:50 model-market blend.
    complete = [{'F3S': 65.0, 'win': 2.0}, {'F3S': 64.0, 'win': 3.0},
                {'F3S': 60.0, 'win': 6.0}]
    assert engine.assign_win_probabilities(complete) is True
    assert abs(sum(r['p_win'] for r in complete) - 1.0) < 1e-12
    assert all(abs(r['p_win'] - 0.5 * (r['p_model'] + r['p_market'])) < 1e-12
               for r in complete)


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
    check_probability()
    print('SELFTEST_OK 9/9')


if __name__ == '__main__':
    check()
