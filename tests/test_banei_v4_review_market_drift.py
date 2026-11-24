import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import review  # noqa: E402


def _ch():
    return {'diffs': [{'no': 3, 'field': 'odds', 'before': 5.0, 'after': 3.5},
                      {'no': 7, 'field': 'odds', 'before': 10.0, 'after': 14.0},
                      {'no': 1, 'field': 'odds', 'before': 2.0, 'after': 1.8},
                      {'no': 4, 'field': 'pop', 'before': 2, 'after': 3},
                      {'no': 9, 'field': 'odds', 'before': None, 'after': 8.0}]}


def test_shortened_and_drifted_against_result():
    m = review.market_drift(_ch(), [3, 7, 5], honmei=1)
    assert m['shortened'] == 2 and m['drifted'] == 1
    assert m['shortened_top3'] == 1 and m['drifted_top3'] == 1
    assert m['winner_move'] == 'short' and m['honmei_move'] == 'short'
    assert m['moves'][0]['no'] == 3 and m['moves'][0]['ratio'] == 0.7 and m['evidence_only'] is True
    n = review.market_drift(_ch(), [5, 6, 8], honmei=7)
    assert n['winner_move'] == 'none' and n['honmei_move'] == 'drift' and n['shortened_top3'] == 0


def test_missing_inputs():
    assert review.market_drift(None, [1, 2, 3]) is None
    assert review.market_drift({'error': 'x'}, [1, 2, 3]) is None
    assert review.market_drift(_ch(), [1, 2]) is None
    m = review.market_drift({'diffs': []}, [1, 2, 3], honmei=1)
    assert m['shortened'] == 0 and m['honmei_move'] is None


def test_summary_and_markdown():
    base = {'stake': 1000, 'return': 0, 'components': {'trio': [1000, 0], 'exact': [0, 0]}, 'ffl': 'W', 'cause': None,
            'proposals': [], 'trio_hit': False, 'exact_hit': False, 'honmei_finish': None,
            'finishers': {k: {'in_role': False, 'no': int(k), 'pop': 1} for k in '123'}}
    revs = [dict(base, market_drift=review.market_drift(_ch(), [3, 7, 5], honmei=1)),
            dict(base, market_drift=review.market_drift(_ch(), [5, 6, 8], honmei=7)),
            dict(base, market_drift=None)]
    s = review.summarize(revs, 0)
    d = s['market_drift']
    assert d['races'] == 2 and d['shortened'] == 4 and d['shortened_top3'] == 1 and d['drifted_top3'] == 1
    assert d['winner_move'] == {'short': 1, 'none': 1} and d['honmei_move'] == {'short': 1, 'drift': 1}
    assert '売れた馬 4頭のうち3着内 1' in review._md('t', s)
    assert review.summarize([dict(base)], 0)['market_drift'] is None
