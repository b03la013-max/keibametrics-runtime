import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import review  # noqa: E402


def test_winner_off_ticket_flags_uncovered_points():
    tk = {'points': 12, 'trio': [(1, 2, 3), (1, 2, 4)], 'exact': [(1, 2, 3)]}
    w = review.winner_off_ticket(tk, 7, 1200)
    assert w == {'winner_on_ticket': False, 'points': 12, 'wasted_points': 12, 'wasted_stake': 1200}
    ok = review.winner_off_ticket(tk, 4, 1200)
    assert ok['winner_on_ticket'] is True and ok['wasted_points'] == 0 and ok['wasted_stake'] == 0


def test_winner_off_ticket_none_without_points():
    assert review.winner_off_ticket({'points': 0, 'trio': [], 'exact': []}, 1) is None
    assert review.winner_off_ticket({'points': 3, 'trio': [(1, 2, 3)], 'exact': []}, None) is None


def test_summary_counts_and_markdown():
    base = {'stake': 1000, 'return': 0, 'components': {'trio': [1000, 0], 'exact': [0, 0]}, 'ffl': 'W', 'cause': None,
            'proposals': [], 'trio_hit': False, 'exact_hit': False, 'honmei_finish': None,
            'finishers': {k: {'in_role': False, 'no': int(k), 'pop': 1} for k in '123'}}
    revs = [dict(base, exposure={'winner_off_ticket': {'winner_on_ticket': False, 'wasted_stake': 1000}}),
            dict(base, exposure={'winner_off_ticket': {'winner_on_ticket': True, 'wasted_stake': 0}}),
            dict(base, exposure={})]
    s = review.summarize(revs, 0)
    assert s['winner_off_ticket'] == 1 and s['winner_off_ticket_stake'] == 1000
    assert '勝ち馬が券面に無いまま買った 1R（1,000円）' in review._md('t', s)
