import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import review  # noqa: E402


def test_two_axis_wipeout_when_one_axis_fails():
    tk = {'axis': [3, 11], 'trio': [(3, 11, 1), (3, 11, 5), (3, 11, 7), (3, 1, 5)], 'exact': [(3, 11, 1)]}
    a = review.axis_dependency(tk, [3, 1, 5])
    assert a['n_axis'] == 2 and a['tickets'] == 5 and a['axis_tickets'] == 4 and a['axis_share'] == 0.8
    assert a['axis_in_top3'] == 1 and a['all_axis_top3'] is False
    assert a['axis_wipeout'] is True and a['wipeout_points'] == 4 and a['co_failure'] is False
    b = review.axis_dependency(tk, [9, 8, 7])
    assert b['co_failure'] is True and b['axis_in_top3'] == 0
    ok = review.axis_dependency(tk, [11, 3, 7])
    assert ok['all_axis_top3'] is True and ok['axis_wipeout'] is False and ok['wipeout_points'] == 0


def test_single_axis_and_missing_inputs():
    tk = {'axis': [4], 'trio': [(4, 1, 2), (1, 2, 3)], 'exact': []}
    a = review.axis_dependency(tk, [1, 2, 3])
    assert a['n_axis'] == 1 and a['axis_share'] == 0.5 and a['axis_wipeout'] is True and a['co_failure'] is False
    assert review.axis_dependency({'trio': [(1, 2, 3)]}, [1, 2, 3]) is None
    assert review.axis_dependency({'axis': [1], 'trio': [], 'exact': []}, [1, 2, 3]) is None
    assert review.axis_dependency(tk, [1, 2]) is None


def test_summary_and_markdown():
    base = {'stake': 1000, 'return': 0, 'components': {'trio': [1000, 0], 'exact': [0, 0]}, 'ffl': 'W', 'cause': None,
            'proposals': [], 'trio_hit': False, 'exact_hit': False, 'honmei_finish': None,
            'finishers': {k: {'in_role': False, 'no': int(k), 'pop': 1} for k in '123'}}
    tk = {'axis': [3, 11], 'trio': [(3, 11, 1), (3, 1, 5)], 'exact': []}
    revs = [dict(base, exposure={'axis_dependency': review.axis_dependency(tk, [3, 1, 5])}),
            dict(base, exposure={'axis_dependency': review.axis_dependency(tk, [3, 11, 5])}),
            dict(base, exposure={})]
    s = review.summarize(revs, 0)
    d = s['axis_dependency']['2']
    assert d == {'races': 2, 'all_axis_top3': 1, 'wipeout': 1, 'wipeout_points': 1, 'co_failure': 0, 'axis_share_mean': 0.5}
    assert '2頭軸 2R・50%・1・1R・1点・0R' in review._md('t', s)
    assert review.summarize([dict(base, exposure={})], 0)['axis_dependency'] is None
