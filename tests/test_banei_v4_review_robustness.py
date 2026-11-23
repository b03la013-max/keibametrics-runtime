import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import review  # noqa: E402


def _r(stake, ret):
    return {'stake': stake, 'return': ret}


def test_payout_robustness_drops_top_returns_and_streak():
    revs = [_r(1000, 0), _r(1000, 0), _r(1000, 5000), _r(1000, 0), _r(1000, 0), _r(1000, 0), _r(1000, 1500), _r(0, 0)]
    r = review.payout_robustness(revs)
    assert r['races'] == 7 and r['profit_races'] == 2
    assert r['pfs_without_top1'] == 25.0       # 1500/6000
    assert r['pfs_without_top2'] == 0.0        # 0/5000
    assert r['pfs_without_top3'] == 0.0
    assert r['longest_losing_streak'] == 3


def test_payout_robustness_small_samples():
    assert review.payout_robustness([]) is None
    assert review.payout_robustness([_r(0, 0)]) is None
    r = review.payout_robustness([_r(1000, 3000)])
    assert r['pfs_without_top1'] is None and r['longest_losing_streak'] == 0


def test_robustness_in_markdown():
    s = {'robustness': review.payout_robustness([_r(1000, 0), _r(1000, 4000), _r(1000, 0), _r(1000, 1200)]),
         'races': 4, 'missed': 0, 'stake': 4000, 'return': 5200, 'pfs': 130.0,
         'pfs_without_top1': 40.0, 'trio_hit': 0, 'trio_pfs': None, 'exact_hit': 0, 'exact_pfs': None, 'honmei_win': 0,
         'honmei_top3': 0, 'winner_in_W': 0, 'second_in_P2': 0, 'third_in_P3': 0, 'ffl': {}, 'cause': {},
         'funnel': {k: 0 for k in ('winner_in_W', 'pair_in_tickets', 'trio_bought', 'exact_bought', 'profit')},
         'hit_but_loss': 0, 'extreme_hub': 0, 'hub_failed': 0, 'p0p1': {}, 'rev_audit': None}
    md = review._md('t', s)
    assert '回収の頑健性（購入 4R）: 上位払戻を除いた PFS 1R除き 40.0%・2R除き 0.0%' in md
    assert '最長連敗 1R' in md
