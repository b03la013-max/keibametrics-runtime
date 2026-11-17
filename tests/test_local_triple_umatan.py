import json
from datetime import datetime, timedelta

from runtime.local_autopilot import triple_umatan as tu


def _day(tmp_path, n=12):
    q = {'races': {}}
    (tmp_path / 'rev').mkdir()
    base = datetime.fromisoformat('2026-11-18T15:00:00+09:00')
    for i in range(1, n + 1):
        k = f'OHI_{i:02d}'
        q['races'][k] = {'venue_id': 'OHI', 'venue_name': '大井', 'race_no': i,
                         'post_current': (base + timedelta(minutes=30 * i)).isoformat(),
                         'editions': [{'edition': '直前版', 'rev': f'{k}.r1'}]}
        rk = [{'no': j, 'p_win': p, 'win': 1 / p} for j, p in zip(range(1, 9), (0.4, 0.2, 0.12, 0.1, 0.08, 0.05, 0.03, 0.02))]
        (tmp_path / 'rev' / f'{k}.r1.json').write_text(json.dumps({'prediction': {'ranking': rk}}))
    return q


def test_legs_are_last_three_and_close_five_minutes_before_first(tmp_path):
    q = _day(tmp_path)
    ks = tu.legs(q, 'OHI')
    assert ks == ['OHI_10', 'OHI_11', 'OHI_12']
    assert tu.deadline(q, ks) == datetime.fromisoformat(q['races']['OHI_10']['post_current']) - timedelta(minutes=5)
    q10 = _day(tmp_path / 'x' if (tmp_path / 'x').mkdir() is None else tmp_path, 10)
    assert tu.legs(q10, 'OHI') == ['OHI_08', 'OHI_09', 'OHI_10']


def test_tiers_respect_caps_and_settle(tmp_path):
    q = _day(tmp_path)
    now = datetime.fromisoformat(q['races']['OHI_10']['post_current']) - timedelta(minutes=15)
    rec = tu.build(q, 'OHI', tmp_path, now)
    assert rec['status'] == 'BUILT'
    for name, cap in tu.TIERS:
        t = rec['tiers'][name]
        assert t['points'] <= cap and t['stake_yen'] == t['points'] * 50
        assert t['points'] == t['legs'][0]['points'] * t['legs'][1]['points'] * t['legs'][2]['points']
    assert rec['tiers']['S']['model_hit_prob'] <= rec['tiers']['L']['model_hit_prob']
    for k in ('OHI_10', 'OHI_11', 'OHI_12'):
        q['races'][k]['settlement'] = {'order': [1, 2, 3]}
    st = tu.settle(rec, q)
    assert st['tiers']['L']['hit'] is True and st['tiers']['L']['payout'] is None
    assert '締切' in tu.md(rec)


def test_exacta_harville():
    p = {1: 0.5, 2: 0.3, 3: 0.2}
    assert abs(tu.exacta(p, 1, 2) - 0.3) < 1e-9
    assert abs(sum(tu.exacta(p, i, j) for i in p for j in p if i != j) - 1) < 1e-9
