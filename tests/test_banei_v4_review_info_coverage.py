import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import review  # noqa: E402


def test_info_coverage_race():
    rows = [{'dcr': 90, 'tpi': 50.0}, {'dcr': 60, 'tpi': None}, {'dcr': None, 'tpi': 48.0}]
    c = review.info_coverage(rows)
    assert c == {'dcr_mean': 75.0, 'dcr_min': 60, 'tpi_unknown': 1, 'field': 3}
    assert review.info_coverage([]) is None


def _r(m, hf, w, stake, ret, unk=0):
    return {'info_coverage': None if m is None else {'dcr_mean': m, 'tpi_unknown': unk}, 'honmei_finish': hf,
            'finishers': {'1': {'in_role': w}}, 'stake': stake, 'return': ret}


def test_by_info_coverage_bands():
    t = review.by_info_coverage([_r(60, None, False, 1000, 0, 2), _r(69.9, 1, True, 1000, 3000),
                                 _r(70, 2, True, 1000, 0), _r(90, 1, True, 1000, 1500), _r(None, None, False, 0, 0)])
    assert t['<70'] == {'races': 2, 'honmei_win': 1, 'honmei_top3': 1, 'winner_in_W': 1, 'tpi_unknown': 2,
                        'stake': 2000, 'return': 3000, 'pfs': 150.0}
    assert t['70-84']['honmei_top3'] == 1 and t['85+']['pfs'] == 150.0
    assert t['UNKNOWN']['pfs'] is None
    assert review.by_info_coverage([]) is None


def test_by_info_coverage_markdown():
    s = {'by_info_coverage': review.by_info_coverage([_r(90, 1, True, 1000, 2000), _r(50, None, False, 1000, 0, 3)]),
         'races': 2, 'missed': 0, 'stake': 2000, 'return': 2000, 'pfs': 100.0,
         'pfs_without_top1': None, 'trio_hit': 1, 'trio_pfs': None, 'exact_hit': 0, 'exact_pfs': None, 'honmei_win': 1,
         'honmei_top3': 1, 'winner_in_W': 1, 'second_in_P2': 0, 'third_in_P3': 0, 'ffl': {}, 'cause': {},
         'funnel': {k: 0 for k in ('winner_in_W', 'pair_in_tickets', 'trio_bought', 'exact_bought', 'profit')},
         'hit_but_loss': 0, 'extreme_hub': 0, 'hub_failed': 0, 'p0p1': {}, 'rev_audit': None}
    md = review._md('t', s)
    assert '- 情報充足帯別（DCR平均：R・◎1着・◎3着内・勝ち馬∈W・TPI欠け頭数・PFS）: <70 1R・0・0・0・3・0.0%／85+ 1R・1・1・1・0・200.0%' in md
