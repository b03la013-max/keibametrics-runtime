import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import review  # noqa: E402


def _r(r1, r2, r3):
    return {'finishers': {'1': {'win_rank': r1, 'place_rank': r1 + 1, 'hole_rank': None},
                          '2': {'win_rank': r2, 'place_rank': r2, 'hole_rank': 4},
                          '3': {'win_rank': r3, 'place_rank': None, 'hole_rank': 1}}}


def test_rank_discrimination_counts_and_means():
    d = review.rank_discrimination([_r(1, 3, 7), _r(2, 6, 4)])
    assert d['1']['win_rank'] == {'n': 2, 'top1': 1, 'top3': 2, 'top5': 2, 'mean': 1.5}
    assert d['1']['place_rank'] == {'n': 2, 'top1': 0, 'top3': 2, 'top5': 2, 'mean': 2.5}
    assert 'hole_rank' not in d['1']                      # missing ranks are not counted as anything
    assert d['2']['win_rank']['top3'] == 1 and d['2']['win_rank']['mean'] == 4.5
    assert d['3']['hole_rank'] == {'n': 2, 'top1': 2, 'top3': 2, 'top5': 2, 'mean': 1.0}
    assert 'place_rank' not in d['3']


def test_rank_discrimination_empty():
    assert review.rank_discrimination([]) is None
    assert review.rank_discrimination([{'finishers': {}}]) is None


def test_md_line_renders():
    s = {'rank_discrimination': review.rank_discrimination([_r(1, 3, 7)]),
         'races': 1, 'missed': 0, 'stake': 0, 'return': 0, 'pfs': None,
         'pfs_without_top1': None, 'trio_hit': 0, 'trio_pfs': None, 'exact_hit': 0, 'exact_pfs': None, 'honmei_win': 0,
         'honmei_top3': 0, 'winner_in_W': 0, 'second_in_P2': 0, 'third_in_P3': 0, 'ffl': {}, 'cause': {},
         'funnel': {k: 0 for k in ('winner_in_W', 'pair_in_tickets', 'trio_bought', 'exact_bought', 'profit')},
         'hit_but_loss': 0, 'extreme_hub': 0, 'hub_failed': 0, 'p0p1': {}, 'rev_audit': None}
    line = [ln for ln in review._md('t', s).splitlines() if '指数順位' in ln]
    assert line and '1着 勝 1.0・1・1・1/1・連 2.0・0・1・1/1' in line[0] and '3着 勝 7.0・0・0・0/1・穴 1.0・1・1・1/1' in line[0]
