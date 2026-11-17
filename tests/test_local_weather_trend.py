import json
from datetime import datetime, timedelta, timezone

from runtime.local_autopilot import day_trend, weather

JST = timezone(timedelta(hours=9))


def test_weather_observe_and_diff(tmp_path):
    (tmp_path / 'amedastable.json').write_text(json.dumps({
        '44132': {'type': 'A', 'kjName': '東京', 'lat': [35, 41.5], 'lon': [139, 45.0], 'alt': 25},
        '99999': {'type': 'C', 'kjName': '遠方', 'lat': [43, 0], 'lon': [141, 0], 'alt': 5}}))
    calls = []

    def fetch(url):
        calls.append(url)
        if url.endswith('202611181450' + '00.json'):
            raise OSError('not yet')
        return json.dumps({'44132': {'temp': [12.5, 0], 'precipitation10m': [0.5, 0], 'wind': [3.2, 0],
                                     'humidity': [80, 0]}}).encode()
    freeze = datetime(2026, 11, 18, 14, 55, tzinfo=JST)
    o = weather.observe('OHI', freeze, tmp_path, fetch=fetch, now=freeze + timedelta(minutes=1))
    assert o['status'] == 'CAPTURED' and o['station']['station_id'] == '44132'
    assert o['observed_at'].startswith('2026-11-18T14:40') and o['available_before_cutoff']
    assert o['observation']['precipitation_10m_mm'] == 0.5
    b = json.loads(json.dumps(o)); b['observation']['wind_speed_ms'] = 6.0
    assert weather.diff(o, b) == {'wind_speed_ms': [3.2, 6.0]}


def test_day_trend_uses_only_races_settled_before_freeze(tmp_path):
    (tmp_path / 'rev').mkdir()
    q = {'races': {}}
    for i, (settled, w) in enumerate((('2026-11-18T15:20:00+09:00', 3), ('2026-11-18T16:20:00+09:00', 5)), 1):
        key = f'OHI_0{i}'
        q['races'][key] = {'venue_id': 'OHI', 'settlement': {'order': [w, 1, 2], 'settled_at': settled,
                                                             'revision': f'{key}.r2'}}
        pred = {'ranking': [{'no': 3, 'win': 1.5, 'frame': 2}, {'no': 5, 'win': 4.0, 'frame': 6}],
                'prior_runs': {'3': [{'content_positions': [1, 1], 'field_size': 12}]}}
        (tmp_path / 'rev' / f'{key}.r2.json').write_text(json.dumps({'prediction': pred}))
    (tmp_path / 'queue.json').write_text(json.dumps(q))
    t = day_trend.build(tmp_path, 'OHI', datetime(2026, 11, 18, 16, 0, tzinfo=JST))
    assert t['races_used'] == ['OHI_01'] and t['winner_front_share'] == 1.0 and t['favorite_win_share'] == 1.0
    assert t['uncertainty'] == 'HIGH'
