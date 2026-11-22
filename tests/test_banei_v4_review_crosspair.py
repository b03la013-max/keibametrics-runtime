import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import review  # noqa: E402


def test_cross_pair_third_detected():
    # 1-2 の並びは買っているが、3着の 5 は 1-2 の3着に無く、2-1-5 にだけある
    exact = [[1, 2, 3], [1, 2, 4], [2, 1, 5]]
    c = review.cross_pair_third(exact, [1, 2, 5])
    assert c['pair_bought'] and not c['third_under_pair'] and c['third_elsewhere'] and c['cross_pair_third']


def test_cross_pair_third_not_flagged_when_hit_or_pair_absent():
    exact = [[1, 2, 5], [2, 1, 3]]
    assert not review.cross_pair_third(exact, [1, 2, 5])['cross_pair_third']      # 的中
    assert not review.cross_pair_third(exact, [3, 1, 5])['cross_pair_third']      # 並びを買っていない
    assert not review.cross_pair_third([[1, 2, 3]], [1, 2, 4])['cross_pair_third']  # 3着馬がどこにも無い
    assert review.cross_pair_third([], [1, 2, 3]) is None


def test_cross_pair_third_string_keys():
    assert review.cross_pair_third([['1', '2', '3'], ['3', '1', '4']], ['1', '2', '4'])['cross_pair_third']
