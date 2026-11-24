import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import review  # noqa: E402


def _r(nw, w_in, s_in, stake, ret):
    return {'role_counts': None if nw is None else {'W': nw, 'P2': 3, 'P3': 5},
            'finishers': {'1': {'in_role': w_in}, '2': {'in_role': s_in}}, 'stake': stake, 'return': ret}


def test_role_counts():
    rows = [{'role_w': True, 'role_p2': True, 'role_p3': True}, {'role_w': False, 'role_p2': True, 'role_p3': True},
            {'role_p3': True}]
    assert review.role_counts(rows) == {'W': 1, 'P2': 2, 'P3': 3}
    assert review.role_counts([]) is None


def test_by_w_count_splits():
    revs = [_r(1, False, True, 3000, 0), _r(1, True, True, 3000, 9000), _r(2, True, False, 3000, 1500),
            _r(5, True, True, 3000, 0), _r(None, False, False, 0, 0)]
    t = review.by_w_count(revs)
    assert t['1'] == {'races': 2, 'winner_in_W': 1, 'second_in_P2': 2, 'stake': 6000, 'return': 9000, 'pfs': 150.0}
    assert t['2']['pfs'] == 50.0 and t['4+']['races'] == 1 and t['UNKNOWN']['pfs'] is None
    assert review.by_w_count([]) is None


def test_by_w_count_in_markdown():
    s = {'by_w_count': review.by_w_count([_r(1, True, True, 3000, 9000), _r(2, False, True, 3000, 0)]),
         'races': 2, 'missed': 0, 'stake': 6000, 'return': 9000, 'pfs': 150.0,
         'pfs_without_top1': None, 'trio_hit': 1, 'trio_pfs': None, 'exact_hit': 0, 'exact_pfs': None, 'honmei_win': 1,
         'honmei_top3': 1, 'winner_in_W': 1, 'second_in_P2': 2, 'third_in_P3': 0, 'ffl': {}, 'cause': {},
         'funnel': {k: 0 for k in ('winner_in_W', 'pair_in_tickets', 'trio_bought', 'exact_bought', 'profit')},
         'hit_but_loss': 0, 'extreme_hub': 0, 'hub_failed': 0, 'p0p1': {}, 'rev_audit': None}
    assert '- W の頭数別（R・勝ち馬∈W・2着∈P2・PFS）: W1頭 1R・1・1・300.0%／W2頭 1R・0・1・0.0%' in review._md('t', s)
