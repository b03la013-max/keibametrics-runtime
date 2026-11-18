from runtime.local_autopilot import review, settle


def test_delivered_failure_uses_the_delivered_tickets_sequentially():
    roles = {1: ['W', 'P2', 'P3'], 2: ['W', 'P2', 'P3'], 3: ['P2', 'P3'], 4: ['P3']}
    t = [('EXACTA', [1, 2])]
    f = lambda order, eff, pay: review.delivered_failure(roles, t, order, {'effective_invest': eff, 'payout': pay})
    assert f([4, 1, 2], 6000, 0) == 'PREDICTION_ROLE_W'
    assert f([1, 4, 2], 6000, 0) == 'PREDICTION_ROLE_P2'
    assert f([1, 3, 2], 6000, 0) == 'TICKET_SELECTION'
    assert f([1, 2, 3], 6000, 2010) == 'CAPITAL_EFFICIENCY'     # KSM_10 11/18: capped 60 lost money
    assert f([1, 2, 3], 6000, 6200) == 'NONE'                   # SON_11 11/18: capped 60 made 200 yen
    assert review.delivered_failure(roles, [], [1, 2, 3], {'no_bet_reason': 'X'}) == 'NO_BET'


def test_pre_freeze_scratch_is_not_a_did_not_finish():
    res = {'order': [10, 4, 8, 6, 7, 3, 5, 1], 'did_not_finish': [2, 9], 'non_starters': [],
           'payouts': {'EXACTA': {(10, 4): 310}}}
    pred = {'edition': '直前版', 'revision_id': 'r1', 'ticket_sha256': 'x', 'saved_at': 't',
            'runners': [{'no': n} for n in (10, 4, 8, 6, 7, 3, 5, 1)],
            'prediction': {'ranking': [{'no': 10}, {'no': 4}], 'tickets': [{'k': '馬単', 'b': '10-4', 'pt': 1}]}}
    st = settle.settle_parsed(res, pred, 'x')
    assert st['did_not_finish'] == [] and st['non_starters_pre_freeze'] == [2, 9]
    assert st['refund'] == 0
