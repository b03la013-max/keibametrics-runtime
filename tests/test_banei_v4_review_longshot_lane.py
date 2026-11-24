import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import review  # noqa: E402


def _rev(fin):
    return {'finishers': {str(i + 1): {'no': no, 'pop': pop} for i, (no, pop) in enumerate(fin)}}


def test_longshot_lane_counts_only_low_popularity_finishers():
    revs = [_rev([(1, 1), (8, 7), (9, 2)]), _rev([(2, 6), (3, 3), (10, 9)])]
    g = review.longshot_lane_trend(revs)
    assert g['longshot_inner'] == 1 and g['longshot_outer'] == 2
    assert g['longshot_inner_share'] == 0.333 and g['all_inner_share'] == 0.5 and g['all_top3'] == 6


def test_longshot_lane_none_without_longshots():
    assert review.longshot_lane_trend([_rev([(1, 1), (2, 2), (3, 3)])]) is None
    assert review.longshot_lane_trend([{}]) is None


def test_longshot_lane_in_markdown():
    revs = [_rev([(1, 1), (8, 7), (9, 2)])]
    s = {'longshot_lane': review.longshot_lane_trend(revs), 'races': 1, 'missed': 0, 'stake': 0, 'return': 0, 'pfs': None,
         'pfs_without_top1': None, 'trio_hit': 0, 'trio_pfs': None, 'exact_hit': 0, 'exact_pfs': None, 'honmei_win': 0,
         'honmei_top3': 0, 'winner_in_W': 0, 'second_in_P2': 0, 'third_in_P3': 0, 'ffl': {}, 'cause': {},
         'funnel': {k: 0 for k in ('winner_in_W', 'pair_in_tickets', 'trio_bought', 'exact_bought', 'profit')},
         'hit_but_loss': 0, 'extreme_hub': 0, 'hub_failed': 0, 'p0p1': {}, 'rev_audit': None}
    assert '人気薄（6番人気以下）の3着内 1頭の走路' in review._md('t', s)
