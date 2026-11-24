"""B3 third part (2026-11-25 06): CLSFIN（組×着順）as its own EXT component at weight 0, and label_pop_table."""
from runtime.local_autopilot import b3_labels as b3
from runtime.local_autopilot import ext_connect as ec
from runtime.local_autopilot import ext_model as em


def test_level_of_reads_kumi_forms():
    a, b = b3.level_of('C3(八)'), b3.level_of('C3(一)')
    assert a < b
    assert b3.level_of('C2三') == b3.level_of('C2(三)')
    assert b3.level_of('C3-10') == b3.level_of('C3(十)')
    assert b3.level_of('C3 10組') == b3.level_of('C3(十)')
    assert b3.level_of('Ｃ３（八）') == a
    assert b3.level_of('B1') > b3.level_of('C1') and b3.level_of('2歳') is None and b3.level_of(None) is None
    assert b3._kanji_num('十二') == 12 and b3._kanji_num('二十') == 20 and b3._kanji_num('7') == 7


def H(lvl, finish):
    return {'date': '2026-10-01', 'lvl': lvl, 'finish': finish}


def test_clsfin_moves_and_best_at_or_above():
    c8, c5, c1 = b3.level_of('C3(八)'), b3.level_of('C3(五)'), b3.level_of('C3(一)')
    # 今回 C3(五)：前走 C3(八) で2着（格上へ）、同格以上の直近3走は C3(一) の 5着だけ
    lab = dict(b3.labels3({'lvl': c5}, [H(c1, 5), H(c8, 2)]))
    assert lab == {'CLSFIN': 'UP|1-3|4-6'}
    assert dict(b3.labels3({'lvl': c8}, [H(c5, 9)])) == {'CLSFIN': 'DOWN|7+|7+'}
    assert dict(b3.labels3({'lvl': c5}, [H(c5, 1)])) == {'CLSFIN': 'SAME|1-3|1-3'}
    assert dict(b3.labels3({'lvl': c1}, [H(c8, 1)])) == {'CLSFIN': 'UP|1-3|NONE'}
    assert b3.labels3({'lvl': None}, [H(c8, 1)]) == [] and b3.labels3({'lvl': c1}, []) == []
    assert b3.labels3({'lvl': c1}, [H(None, 1)]) == []


def test_clsfin_is_own_component_at_zero():
    cur = {'date': '2026-11-25', 'venue': 'URW', 'distance': 1400, 'going': '良', 'lvl': 1.0, 'sex': '牡', 'pop': 3}
    hist = [dict(H(0.5, 2), venue='URW', distance=1400, early=0.5)]
    cl = dict(em.cand_labels(cur, hist))
    assert cl['CLSFIN'] == 'UP|1-3|NONE'
    assert 'CLSFIN' not in {n for n, _ in em.labels(cur, hist)}
    assert em.CAND_COMPONENTS['CLSFIN'] == 'CLF' == b3.COMPONENTS3['CLSFIN']
    assert 'CLF' in ec.MEASURED and 'CLF' in ec.FIT_NAMES and ec.DEFAULT_BETA['CLF'] == 0.0
    assert all(ec.DEFAULT_BETA[k] == v for k, v in {'JKY': 0.35, 'FRM': 0.3, 'HRS': 0.0, 'PAT': 0.3, 'SPD': 0.8}.items())
    r = {'venue': 'URW', 'band': 'SHORT', 'going': 'DRY', 'distance': 800, 'sire': None, 'damsire': None,
         'jockey': None, 'trainer': None, 'frame': None, 'horse': None, 'bwchg': None, 'age': None, 'season': 'AUT',
         'sex': '牡', 'spd_band': 'NA', 'labels': [], 'cand_labels': [('CLSFIN', 'UP|1-3|NONE')], 'pop': 2, 'fband': 'MID'}
    comp = em.components({('P', 'CLSFIN', 'UP|1-3|NONE'): [400, 150, 100.0]}, r)
    assert 'CLF' in comp and 'PAT' not in comp


def test_rows_carry_level_for_history():
    races = {'a': {'race_id': 'a', 'date': '2026-10-01', 'venue': 'URW', 'race_no': 1, 'distance': 1400, 'going': '良',
                   'cond': 'C3(八)', 'field': 2, 'first_corner': {1: 1, 2: 2}, 'last_corner': {1: 1, 2: 2},
                   'runners': [{'no': 1, 'name': 'アアア', 'status': 'RAN', 'finish': 1, 'pop': 1, 'time': 90.0},
                               {'no': 2, 'name': 'イイイ', 'status': 'RAN', 'finish': 2, 'pop': 2, 'time': 90.5}]},
             'b': {'race_id': 'b', 'date': '2026-10-20', 'venue': 'URW', 'race_no': 1, 'distance': 1400, 'going': '良',
                   'cond': 'C3(五)', 'field': 2, 'first_corner': {1: 1, 2: 2}, 'last_corner': {1: 1, 2: 2},
                   'runners': [{'no': 1, 'name': 'アアア', 'status': 'RAN', 'finish': 2, 'pop': 1, 'time': 90.0},
                               {'no': 2, 'name': 'イイイ', 'status': 'RAN', 'finish': 1, 'pop': 2, 'time': 89.5}]}}
    rows, hist = em._rows(races, {})
    later = [r for r in rows if r['date'] == '2026-10-20']
    assert all(dict(r['cand_labels']).get('CLSFIN', '').startswith('UP|1-3|') for r in later)
    assert all(h['lvl'] is not None for v in hist.values() for h in v)


def test_label_pop_table():
    rows = [{'venue': 'URW', 'pop': 1, 'fband': 'MID', 'top3': True, 'cand_labels': [('CLSFIN', 'UP|1-3|NONE')]},
            {'venue': 'URW', 'pop': 7, 'fband': 'MID', 'top3': True, 'cand_labels': [('CLSFIN', 'UP|1-3|NONE')]},
            {'venue': 'URW', 'pop': 8, 'fband': 'MID', 'top3': False, 'cand_labels': [('CLSFIN', 'UP|1-3|NONE'), ('INTV', '<=14')]},
            {'venue': 'XXX', 'pop': 1, 'fband': 'MID', 'top3': True, 'cand_labels': [('CLSFIN', 'UP|1-3|NONE')]}]
    exp = {('URW', 1, 'MID'): 0.6, ('URW', 7, 'MID'): 0.2, ('URW', 8, 'MID'): 0.2}
    t = b3.label_pop_table(rows, exp)
    assert t['CLSFIN=UP|1-3|NONE']['1-2'] == {'n': 1, 'top3': 1, 'exp': 0.6, 'ae': 1.667}
    assert t['CLSFIN=UP|1-3|NONE']['6+'] == {'n': 2, 'top3': 1, 'exp': 0.4, 'ae': 2.5}
    assert t['INTV=<=14']['6+']['n'] == 1
    assert set(b3.label_pop_table(rows, exp, names={'INTV'})) == {'INTV=<=14'}
