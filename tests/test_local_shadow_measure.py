from runtime.local_autopilot import shadow_measure as sm


def test_settle_keys_and_refund():
    pay = {'WIN': {'3': 450}, 'TRIO': {'1-3-7': 1200}, 'TRIFECTA': {'3-1-7': 5000}}
    assert sm.settle([('WIN', [3])], pay, set()) == (100, 450, True)
    assert sm.settle([('TRIO', [7, 3, 1])], pay, set()) == (100, 1200, True)
    assert sm.settle([('TRIFECTA', [1, 3, 7])], pay, set()) == (100, 0, False)
    assert sm.settle([('TRIFECTA', [3, 1, 7]), ('WIN', [9])], pay, {9}) == (100, 5000, True)


def test_strategy_counts():
    s = sm.strategies([5, 2, 8, 1, 4, 6], 2)
    assert len(s['TRIO_BOX_top4']) == 4 and len(s['TRIO_◎軸_2-5流し']) == 6
    assert len(s['TRIFECTA_◎→2,3→2-5']) == 6 and s['WIN_1番人気'] == [('WIN', [2])]
