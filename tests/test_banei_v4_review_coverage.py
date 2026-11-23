import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import review  # noqa: E402

ROWS = [{'no': 1, 'role_w': 'STRONG', 'role_p2': True, 'role_p3': True, 'win_score': 10.0},
        {'no': 2, 'role_w': 'STRONG', 'role_p2': True, 'role_p3': True, 'win_score': 9.5},
        {'no': 3, 'role_w': None, 'role_p2': True, 'role_p3': True, 'win_score': 7.0},
        {'no': 4, 'role_w': None, 'role_p2': False, 'role_p3': False, 'win_score': 5.0}]


def test_role_set_coverage_with_random_base():
    c = review.role_set_coverage(ROWS, [3, 1, 4])
    assert c['role_w'] == {'size': 2, 'hit': False, 'random_base': 0.5}
    assert c['role_p2']['hit'] and c['role_p2']['size'] == 3 and c['role_p2']['random_base'] == 0.75
    assert not c['role_p3']['hit']
    assert review.role_set_coverage([], [1, 2, 3]) is None


def test_top2_gap():
    assert review.top2_gap(ROWS) == 0.5
    assert review.top2_gap([{'no': 1, 'win_score': 3}]) is None


def test_coverage_summary_splits_by_median_gap():
    revs = [{'role_coverage': review.role_set_coverage(ROWS, [1, 2, 3]), 'top2_gap': 0.5, 'honmei_finish': 1},
            {'role_coverage': review.role_set_coverage(ROWS, [4, 3, 2]), 'top2_gap': 3.0, 'honmei_finish': None},
            {'role_coverage': None, 'top2_gap': None, 'honmei_finish': 2}]
    s = review.coverage_summary(revs)
    assert s['role_w']['races'] == 2 and s['role_w']['hit_rate'] == 0.5 and s['role_w']['random_base'] == 0.5
    assert s['top2_gap']['median'] == 3.0 and s['top2_gap']['low_races'] == 1 and s['top2_gap']['low_honmei_win'] == 1
    assert review.coverage_summary([{}]) is None
