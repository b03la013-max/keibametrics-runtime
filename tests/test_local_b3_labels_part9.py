"""B3 ninth part (2026-11-26 18): FAVLOAD（上位人気×斤量の前走差）at weight 0, and label_pop_table returns (n259)."""
from runtime.local_autopilot import b3_labels as b3
from runtime.local_autopilot import ext_connect as ec
from runtime.local_autopilot import ext_model as em
from runtime.local_autopilot import rakuten


def test_load_parse_and_band():
    assert b3.load_of('56.0') == 56.0 and b3.load_of('▲54') == 54.0 and b3.load_of(55) == 55.0
    assert b3.load_of(None) is None and b3.load_of('') is None and b3.load_of(480) is None
    assert b3.load_band(54.0, 56.0) == 'DEC' and b3.load_band(56.0, 56.5) == 'SAME'
    assert b3.load_band(57.0, 56.0) == 'INC' and b3.load_band(56.0, None) == 'NOPREV' and b3.load_band(None, 56) is None


def test_labels9_fav_only():
    h = [{'load': '56.0'}]
    assert b3.labels9({'pop': 1, 'load': 54.0}, h) == [('FAVLOAD', 'DEC|1')]
    assert b3.labels9({'pop': 2, 'load': 56.0}, h) == [('FAVLOAD', 'SAME|2')]
    assert b3.labels9({'pop': 1, 'load': 56.0}, []) == [('FAVLOAD', 'NOPREV|1')]
    assert b3.labels9({'pop': 3, 'load': 54.0}, h) == [] and b3.labels9({'pop': 1}, h) == []


def test_own_component_at_zero():
    c = b3.COMPONENTS9['FAVLOAD']
    assert em.CAND_COMPONENTS['FAVLOAD'] == c and c in ec.MEASURED and c in ec.FIT_NAMES and ec.DEFAULT_BETA[c] == 0.0
    cur = {'date': '2026-11-26', 'venue': 'OHI', 'distance': 1200, 'going': '良', 'sex': '牡', 'pop': 1, 'age': 4,
           'load': 54.0}
    assert dict(em.cand_labels(cur, [{'date': '2026-11-01', 'finish': 2, 'load': 56.0}]))['FAVLOAD'] == 'DEC|1'
    assert 'FAVLOAD' not in {n for n, _ in em.labels(cur, [])}
    assert all(ec.DEFAULT_BETA[k] == v for k, v in {'JKY': 0.35, 'FRM': 0.3, 'HRS': 0.0, 'PAT': 0.3, 'SPD': 0.8}.items())


def test_rows_use_previous_load_and_carry_payouts():
    def race(rid, day, loads, pays):
        rs = [{'no': i + 1, 'name': n, 'status': 'RAN', 'finish': i + 1, 'pop': i + 1, 'time': 70.0 + i, 'load': loads[i]}
              for i, n in enumerate(['アア', 'イイ', 'ウウ'])]
        return {'race_id': rid, 'date': day, 'venue': 'OHI', 'race_no': 1, 'distance': 1200, 'going': '良',
                'cond': 'C3', 'field': 3, 'first_corner': {}, 'last_corner': {}, 'runners': rs, 'payouts': pays}
    a = race('a', '2026-10-01', ['56.0', '55.0', '54.0'], {})
    b = race('b', '2026-11-01', ['54.0', '55.0', '56.0'], {'WIN': {'1': 250}, 'PLACE': {'1': 120, '2': 150, '3': 300}})
    rows, _ = em._rows({'a': a, 'b': b}, {})
    get = lambda rid, nm: next(r for r in rows if r['race_id'] == rid and r['horse'] == em.key(nm))
    assert dict(get('a', 'アア')['cand_labels'])['FAVLOAD'] == 'NOPREV|1'
    assert dict(get('b', 'アア')['cand_labels'])['FAVLOAD'] == 'DEC|1'
    assert dict(get('b', 'イイ')['cand_labels'])['FAVLOAD'] == 'SAME|2'
    assert 'FAVLOAD' not in dict(get('b', 'ウウ')['cand_labels'])
    r = get('b', 'アア')
    assert r['pay_known'] and r['pay_win'] == 250 and r['pay_place'] == 120
    assert not get('a', 'アア')['pay_known'] and get('a', 'アア')['pay_win'] == 0
    assert 'pay_win' not in str(em.labels({'pop': 1}, []))


def test_add_returns_uses_paid_races_only():
    rows = [{'pop': 1, 'pay_known': True, 'pay_win': 300, 'pay_place': 130, 'cand_labels': [('FAVLOAD', 'DEC|1')]},
            {'pop': 1, 'pay_known': True, 'pay_win': 0, 'pay_place': 0, 'cand_labels': [('FAVLOAD', 'DEC|1')]},
            {'pop': 1, 'pay_known': False, 'pay_win': 0, 'pay_place': 0, 'cand_labels': [('FAVLOAD', 'DEC|1')]},
            {'pop': 7, 'pay_known': True, 'pay_win': 0, 'pay_place': 400, 'cand_labels': [('INTV', '<=14')]}]
    t = b3.add_returns({'FAVLOAD=DEC|1': {'1-2': {'n': 3, 'top3': 1, 'exp': 1.5, 'ae': 0.667}}}, rows)
    d = t['FAVLOAD=DEC|1']['1-2']
    assert d['n'] == 3 and d['n_pay'] == 2 and d['win_ret'] == 150.0 and d['place_ret'] == 65.0
    assert t['INTV=<=14']['6+']['place_ret'] == 400.0
    assert set(b3.add_returns({}, rows, names={'INTV'})) == {'INTV=<=14'}


def test_card_start_keeps_load():
    assert "out['ride_load'] = float(m[2])" in open(rakuten.__file__, encoding='utf-8').read()
    assert ec.card_history({'starts': [{'date': '26.11.01', 'venue': '大井', 'distance': 1200, 'finish': 2,
                                        'ride_load': 56.0}]}, '2026-11-26')[0]['load'] == 56.0


def test_prereg9_registered_before_measurement():
    assert b3.PREREG9['registered'] == '2026-11-26T18' and b3.PREREG9['labels'] == ['FAVLOAD']
    assert 'weight 0.0' in b3.PREREG9['rule']
