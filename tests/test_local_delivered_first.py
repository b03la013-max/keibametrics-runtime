from runtime.local_autopilot import run


def test_profitable_delivered_race_is_none():
    sm = {'roles': {'7': ['W'], '5': ['P2'], '9': ['P3']}, 'tickets': [{'bet_type': 'TRIFECTA', 'selection': [7, 5, 9]}]}
    st = {'effective_invest': 6000, 'payout': 15320, 'invest': 6000}
    assert run._delivered_first(sm, {'order': [7, 5, 9]}, st) == 'NONE'
    st['payout'] = 900
    assert run._delivered_first(sm, {'order': [7, 5, 9]}, st) == 'CAPITAL_EFFICIENCY'
    assert run._delivered_first(sm, {'order': [3, 5, 9]}, st) == 'PREDICTION_ROLE_W'
