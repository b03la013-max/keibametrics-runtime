import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import review  # noqa: E402


def _r(gap, nw, w_in, stake, ret):
    return {'top2_gap': gap, 'role_counts': None if nw is None else {'W': nw, 'P2': 3, 'P3': 5},
            'finishers': {'1': {'in_role': w_in}}, 'stake': stake, 'return': ret}


def test_by_gap_wcount_cells():
    revs = [_r(1.0, 1, False, 3000, 0), _r(5.0, 1, False, 3000, 0), _r(6.0, 2, True, 3000, 6000),
            _r(0.5, 2, True, 3000, 1500), _r(None, 1, True, 3000, 0), _r(4.0, None, True, 3000, 0)]
    t = review.by_gap_wcount(revs)
    assert t['median'] == 4.0
    c = t['cells']
    assert c['LOW:W1'] == {'races': 1, 'winner_in_W': 0, 'stake': 3000, 'return': 0, 'pfs': 0.0}
    assert c['HIGH:W1']['races'] == 1 and c['HIGH:W2+']['pfs'] == 200.0 and c['LOW:W2+']['pfs'] == 50.0
    assert sum(d['races'] for d in c.values()) == 4          # gap または W が無いレースは数えない


def test_by_gap_wcount_empty():
    assert review.by_gap_wcount([]) is None
    assert review.by_gap_wcount([_r(None, 1, True, 3000, 0)]) is None


def test_by_gap_wcount_in_markdown():
    s = {'by_gap_wcount': review.by_gap_wcount([_r(1.0, 1, True, 3000, 9000), _r(3.0, 2, False, 3000, 0)]),
         'races': 2, 'missed': 0, 'stake': 6000, 'return': 9000, 'pfs': 150.0,
         'pfs_without_top1': None, 'trio_hit': 1, 'trio_pfs': None, 'exact_hit': 0, 'exact_pfs': None, 'honmei_win': 1,
         'honmei_top3': 1, 'winner_in_W': 1, 'second_in_P2': 1, 'third_in_P3': 0, 'ffl': {}, 'cause': {},
         'funnel': {k: 0 for k in ('winner_in_W', 'pair_in_tickets', 'trio_bought', 'exact_bought', 'profit')},
         'hit_but_loss': 0, 'extreme_hub': 0, 'hub_failed': 0, 'p0p1': {}, 'rev_audit': None}
    md = review._md('t', s)
    assert '- 確信度×W の頭数（上位2頭の得点差 中央値 3.0：R・勝ち馬∈W・PFS）: 差が大きい・W2+ 1R・0・0.0%／差が小さい・W1 1R・1・300.0%' in md
