"""B3 seventh part (2026-11-26 12): LEADCLASH（前走逃げ×同型の有無）as an own EXT component at weight 0."""
from runtime.local_autopilot import b3_labels as b3
from runtime.local_autopilot import ext_connect as ec
from runtime.local_autopilot import ext_model as em


def test_front_type():
    assert b3.is_front_type([{'early': 0.5}, {'early': 0.0}])
    assert b3.is_front_type([{'early': 0.1}, {'early': 0.2}, {'early': 0.4}])   # mean 0.233
    assert not b3.is_front_type([{'early': 0.5}, {'early': 0.1}])
    assert not b3.is_front_type([{'early': 0.1}]) and not b3.is_front_type([]) and not b3.is_front_type(None)


def test_labels7_values():
    led_won = [{'early': 0.3, 'finish': 4}, {'early': 0.0, 'finish': 1}]
    assert b3.labels7({'field_front_n': 1}, led_won) == [('LEADCLASH', 'WON|ALONE')]
    assert b3.labels7({'field_front_n': 3}, led_won) == [('LEADCLASH', 'WON|CLASH')]
    led_lost = [{'early': 0.0, 'finish': 5}]
    assert b3.labels7({'field_front_n': 2}, led_lost) == [('LEADCLASH', 'LOST|CLASH')]
    assert b3.labels7({'field_front_n': 0}, led_lost) == [('LEADCLASH', 'LOST|ALONE')]
    assert b3.labels7({'field_front_n': 2}, [{'early': 0.2, 'finish': 1}]) == []   # 前走は逃げていない
    assert b3.labels7({}, led_lost) == [] and b3.labels7({'field_front_n': 2}, []) == []


def test_own_component_at_zero_and_not_in_pat():
    cur = {'date': '2026-11-26', 'venue': 'OHI', 'distance': 1200, 'going': '良', 'sex': '牡', 'pop': 4, 'age': 4,
           'field_front_n': 2}
    cl = dict(em.cand_labels(cur, [{'date': '2026-11-01', 'venue': 'OHI', 'distance': 1200, 'early': 0.0, 'finish': 1}]))
    assert cl['LEADCLASH'] == 'WON|CLASH'
    assert 'LEADCLASH' not in {n for n, _ in em.labels(cur, [])}
    c = b3.COMPONENTS7['LEADCLASH']
    assert em.CAND_COMPONENTS['LEADCLASH'] == c and c in ec.MEASURED and c in ec.FIT_NAMES and ec.DEFAULT_BETA[c] == 0.0
    assert all(ec.DEFAULT_BETA[k] == v for k, v in {'JKY': 0.35, 'FRM': 0.3, 'HRS': 0.0, 'PAT': 0.3, 'SPD': 0.8}.items())


def test_rows_count_front_types_before_the_race():
    def race(rid, day, fc, runners):
        return {'race_id': rid, 'date': day, 'venue': 'OHI', 'race_no': 1, 'distance': 1200, 'going': '良', 'cond': 'C3',
                'field': len(runners), 'first_corner': fc, 'last_corner': fc, 'runners': runners}
    R = lambda no, name, fin: {'no': no, 'name': name, 'status': 'RAN', 'finish': fin, 'pop': no, 'time': 70.0 + fin}
    names = ['アア', 'イイ', 'ウウ', 'エエ']
    # race a: アア leads (1st corner 1) and wins; イイ second at the corner
    a = race('a', '2026-10-01', {1: 1, 2: 2, 3: 3, 4: 4}, [R(i + 1, n, i + 1) for i, n in enumerate(names)])
    # race b: ウウ leads and loses
    b = race('b', '2026-10-15', {1: 2, 2: 3, 3: 1, 4: 4}, [R(i + 1, n, [2, 3, 4, 1][i]) for i, n in enumerate(names)])
    c = race('c', '2026-11-01', {1: 1, 2: 2, 3: 3, 4: 4}, [R(i + 1, n, i + 1) for i, n in enumerate(names)])
    rows, _ = em._rows({'a': a, 'b': b, 'c': c}, {})
    got = lambda rid, nm: dict(next(r for r in rows if r['race_id'] == rid and r['horse'] == em.key(nm))['cand_labels'])
    assert 'LEADCLASH' not in got('a', 'アア')            # no history yet
    assert got('b', 'アア')['LEADCLASH'] == 'WON|ALONE'   # only アア is a front type before race b
    assert got('c', 'ウウ')['LEADCLASH'] == 'LOST|CLASH'  # アア (mean early 0.17) and ウウ are front types
    assert 'LEADCLASH' not in got('c', 'アア')            # アア did not lead in race b


def test_prereg7_registered_before_measurement():
    assert b3.PREREG7['registered'] == '2026-11-26T12' and b3.PREREG7['labels'] == ['LEADCLASH']
    assert 'weight 0.0' in b3.PREREG7['rule']
