import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import review  # noqa: E402


def test_result_orders_dead_heat_from_trifecta_payouts():
    # 帯広 2026-11-23 4R：10→6→7・8（3着同着）
    res = {'order': [10, 6, 7, 8, 5], 'payouts': {'TRIFECTA': {'10-6-7': 11990, '10-6-8': 12740},
                                                   'TRIO': {'6-7-10': 1840, '6-8-10': 2060}}}
    assert review.result_orders(res) == [(10, 6, 7), (10, 6, 8)]


def test_result_orders_single():
    assert review.result_orders({'order': [3, 7, 5, 1], 'payouts': {'TRIFECTA': {'3-7-5': 9000}}}) == [(3, 7, 5)]
    assert review.result_orders({'order': [3, 7, 5], 'payouts': {}}) == [(3, 7, 5)]
    assert review.result_orders({'order': [3], 'payouts': {}}) == []


def _rows():
    # 7R 型：◎7 W、▲2 P2、穴1 は P3 外
    return [{'no': 7, 'role_w': True}, {'no': 2, 'role_p2': True}, {'no': 1}, {'no': 5, 'role_p3': True}]


def test_failure_chain_records_every_layer():
    tk = {'trio': [[2, 5, 7]], 'exact': [[7, 2, 5]]}
    c = review.failure_chain(_rows(), {'7': '◎', '2': '▲', '1': '穴'}, tk, [7, 2, 1])
    assert c['layers']['HORSE'] and c['layers']['ROLE_W'] and c['layers']['ROLE_P2']
    assert c['layers']['HEAD'] and c['layers']['ORDERED_PAIR']
    assert c['failed'] == ['ROLE_P3', 'TRIO', 'THIRD'] and c['first'] == 'ROLE_P3'


def test_failure_chain_no_exact_and_hit():
    tk = {'trio': [[1, 2, 7]], 'exact': []}
    rows = _rows() + [{'no': 1, 'role_p3': True}]
    rows = [r for r in rows if not (r['no'] == 1 and 'role_p3' not in r)]
    c = review.failure_chain(rows, {'7': '◎', '2': '▲', '1': '穴'}, tk, [7, 2, 1])
    assert c['first'] == 'NONE' and c['layers']['HEAD'] is None and c['layers']['THIRD'] is None
    assert review.failure_chain(rows, {}, tk, [7, 2]) is None


def test_failure_chain_unmarked_horse():
    tk = {'trio': [[2, 5, 7]], 'exact': [[7, 2, 5]]}
    c = review.failure_chain(_rows(), {'7': '◎', '2': '▲'}, tk, [7, 2, 1])
    assert c['first'] == 'HORSE'
