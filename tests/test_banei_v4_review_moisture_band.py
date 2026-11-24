import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import review  # noqa: E402


def _r(band, hf, w_in, stake, ret):
    return {'moisture_band': band, 'honmei_finish': hf, 'finishers': {'1': {'in_role': w_in}}, 'stake': stake, 'return': ret}


def test_by_moisture_band_splits_counts_and_pfs():
    revs = [_r('DRY', 1, True, 1000, 3000), _r('DRY', None, False, 1000, 0), _r('WET', 3, True, 2000, 1000), _r(None, 2, True, 0, 0)]
    t = review.by_moisture_band(revs)
    assert t['DRY'] == {'races': 2, 'honmei_win': 1, 'honmei_top3': 1, 'winner_in_W': 1, 'stake': 2000, 'return': 3000, 'pfs': 150.0}
    assert t['WET']['honmei_top3'] == 1 and t['WET']['pfs'] == 50.0
    assert t['UNKNOWN']['races'] == 1 and t['UNKNOWN']['pfs'] is None


def test_by_moisture_band_empty():
    assert review.by_moisture_band([]) is None


def test_by_moisture_band_in_markdown():
    s = {'by_moisture_band': review.by_moisture_band([_r('DRY', 1, True, 1000, 3000)]),
         'races': 1, 'missed': 0, 'stake': 1000, 'return': 3000, 'pfs': 300.0,
         'pfs_without_top1': None, 'trio_hit': 1, 'trio_pfs': None, 'exact_hit': 0, 'exact_pfs': None, 'honmei_win': 1,
         'honmei_top3': 1, 'winner_in_W': 1, 'second_in_P2': 0, 'third_in_P3': 0, 'ffl': {}, 'cause': {},
         'funnel': {k: 0 for k in ('winner_in_W', 'pair_in_tickets', 'trio_bought', 'exact_bought', 'profit')},
         'hit_but_loss': 0, 'extreme_hub': 0, 'hub_failed': 0, 'p0p1': {}, 'rev_audit': None}
    assert '- 水分帯別（R・◎1着・◎3着内・勝ち馬∈W・PFS）: DRY 1R・1・1・1・300.0%' in review._md('t', s)
