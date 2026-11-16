import json

from runtime.local_autopilot import forward_oos as fo


def _day(root, day, post, payout):
    d = root / day
    (d / 'rev').mkdir(parents=True)
    (d / 'queue.json').write_text(json.dumps({'races': {'OHI_01': {'post_current': post}}}))
    rk = [{'no': n, 'win': w} for n, w in ((1, 3.0), (2, 1.8), (3, 6.0), (4, 9.0), (5, 12.0))]
    (d / 'rev' / 'OHI_01.r2.json').write_text(json.dumps({'prediction': {'ranking': rk}}))
    (d / 'OHI_01.result.json').write_text(json.dumps({'revision': 'OHI_01.r2', 'order': [2, 1, 3, 4, 5],
        'payouts': {'WIN': {'2': 180}, 'PLACE': {'2': 110}, 'TRIO': {'1-2-3': payout}},
        'effective_invest': 600, 'payout': 0}))


def test_only_post_freeze_races_count(tmp_path):
    _day(tmp_path, '2026-11-16', '2026-11-16T20:00:00+09:00', 9990)   # replay day: excluded
    _day(tmp_path, '2026-11-17', '2026-11-17T15:00:00+09:00', 1000)
    o = fo.evaluate(tmp_path)
    c1 = o['candidates']['C1-FAV-AXIS-TRIO']
    assert o['eligible_races'] == 1 and c1['candidate']['payout'] == 1000
    c3 = o['candidates']['C3-FAV-AS-W-WHEN-DIVERGED']
    assert c3['favorite']['win_rate'] == 100.0 and c3['honmei']['win_rate'] == 0.0
