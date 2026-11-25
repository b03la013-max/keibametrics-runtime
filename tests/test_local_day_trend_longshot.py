import json
from datetime import datetime, timedelta, timezone

from runtime.local_autopilot import day_trend

JST = timezone(timedelta(hours=9))


def _setup(tmp_path, races):
    (tmp_path / 'rev').mkdir()
    q = {'races': {}}
    for key, settled, order, pred in races:
        q['races'][key] = {'venue_id': 'OHI', 'settlement': {'order': order, 'settled_at': settled,
                                                             'revision': f'{key}.r1'}}
        (tmp_path / 'rev' / f'{key}.r1.json').write_text(json.dumps({'prediction': pred}))
    (tmp_path / 'queue.json').write_text(json.dumps(q))


def _pred(n=8):
    rk = [{'no': i, 'win': float(i * 2), 'frame': (i + 1) // 2} for i in range(1, n + 1)]
    prior = {str(i): [{'content_positions': [1 if i % 2 else 10], 'field_size': 12}] for i in range(1, n + 1)}
    return {'ranking': rk, 'prior_runs': prior}


def test_longshot_only_counts_pop6_or_lower(tmp_path):
    # 3着内：1番人気(1)・7番人気(7, 先行, 4枠)・8番人気(8, 差し, 4枠)
    _setup(tmp_path, [('OHI_01', '2026-11-25T15:00:00+09:00', [1, 7, 8], _pred())])
    t = day_trend.build(tmp_path, 'OHI', datetime(2026, 11, 25, 16, 0, tzinfo=JST))
    ls = t['longshot_top3']
    assert ls['n_top3'] == 3 and ls['n_longshot_top3'] == 2
    assert ls['longshot_front_share'] == 0.5 and ls['longshot_closer_share'] == 0.5
    assert ls['longshot_inner_frame_share'] == 1.0
    assert ls['top3_front_share'] == round(2 / 3, 2)
    assert ls['uncertainty'] == 'HIGH'


def test_longshot_none_when_all_favorites(tmp_path):
    _setup(tmp_path, [('OHI_01', '2026-11-25T15:00:00+09:00', [1, 2, 3], _pred())])
    ls = day_trend.build(tmp_path, 'OHI', datetime(2026, 11, 25, 16, 0, tzinfo=JST))['longshot_top3']
    assert ls['n_longshot_top3'] == 0 and ls['longshot_front_share'] is None


def test_longshot_ignores_races_settled_after_freeze(tmp_path):
    _setup(tmp_path, [('OHI_01', '2026-11-25T15:00:00+09:00', [1, 2, 3], _pred()),
                      ('OHI_02', '2026-11-25T17:00:00+09:00', [7, 8, 6], _pred())])
    t = day_trend.build(tmp_path, 'OHI', datetime(2026, 11, 25, 16, 0, tzinfo=JST))
    assert t['races_used'] == ['OHI_01'] and t['longshot_top3']['n_longshot_top3'] == 0


def test_existing_keys_unchanged(tmp_path):
    _setup(tmp_path, [('OHI_01', '2026-11-25T15:00:00+09:00', [1, 7, 8], _pred())])
    t = day_trend.build(tmp_path, 'OHI', datetime(2026, 11, 25, 16, 0, tzinfo=JST))
    assert t['winner_front_share'] == 1.0 and t['favorite_win_share'] == 1.0
    assert t['production_effect'].startswith('NONE')
