import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import review  # noqa: E402


def _r(pop, hf, stake, ret):
    return {'honmei_pop': pop, 'honmei_finish': hf, 'stake': stake, 'return': ret}


def test_by_honmei_pop_band_splits():
    revs = [_r(1, 1, 1000, 2000), _r(1, None, 1000, 0), _r(3, 2, 1000, 500), _r(5, 3, 1000, 0), _r(9, 1, 1000, 9000), _r(None, None, 0, 0)]
    t = review.by_honmei_pop_band(revs)
    assert t['1'] == {'races': 2, 'honmei_win': 1, 'honmei_top3': 1, 'stake': 2000, 'return': 2000, 'pfs': 100.0}
    assert t['2-3']['honmei_top3'] == 1 and t['2-3']['pfs'] == 50.0
    assert t['4-6']['races'] == 1 and t['7+']['honmei_win'] == 1
    assert t['UNKNOWN']['pfs'] is None


def test_by_honmei_pop_band_empty():
    assert review.by_honmei_pop_band([]) is None


def test_by_honmei_pop_band_markdown_order():
    s = {'by_honmei_pop_band': review.by_honmei_pop_band([_r(7, None, 1000, 0), _r(1, 1, 1000, 3000)]),
         'races': 2, 'missed': 0, 'stake': 2000, 'return': 3000, 'pfs': 150.0,
         'pfs_without_top1': None, 'trio_hit': 1, 'trio_pfs': None, 'exact_hit': 0, 'exact_pfs': None, 'honmei_win': 1,
         'honmei_top3': 1, 'winner_in_W': 1, 'second_in_P2': 0, 'third_in_P3': 0, 'ffl': {}, 'cause': {},
         'funnel': {k: 0 for k in ('winner_in_W', 'pair_in_tickets', 'trio_bought', 'exact_bought', 'profit')},
         'hit_but_loss': 0, 'extreme_hub': 0, 'hub_failed': 0, 'p0p1': {}, 'rev_audit': None}
    assert '- ◎の人気帯別（R・◎1着・◎3着内・PFS）: 1番人気 1R・1・1・300.0%／7+番人気 1R・0・0・0.0%' in review._md('t', s)
