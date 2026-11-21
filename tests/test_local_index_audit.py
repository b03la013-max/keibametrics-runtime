import json

from runtime.local_autopilot import index_audit as ia


def test_auc_and_audit(tmp_path):
    d = tmp_path / '2026-11-20' / 'formal'
    d.mkdir(parents=True)
    runners = [{'no': n, 'indices': {'GOOD': 100 - n, 'BAD': n, 'FLAT': 52}} for n in range(1, 9)]
    (d / 'OHI_01.full29.json').write_text(json.dumps({'runners': runners}))
    (d / 'OHI_01.result.json').write_text(json.dumps({'order': [1, 2, 3]}))
    rs = ia.races(tmp_path)
    assert len(rs) == 1
    o = ia.audit(rs)
    assert o['GOOD']['auc_win'] == 1.0 and o['GOOD']['best_win_rate'] == 1.0
    assert o['BAD']['auc_top3'] == 0.0 and o['FLAT']['constant_rate'] == 1.0 and o['FLAT']['auc_win'] is None
    assert ia.auc({1: 5, 2: 5}, {1}) == 0.5
    assert '| GOOD |' in ia.md(o, 1)
