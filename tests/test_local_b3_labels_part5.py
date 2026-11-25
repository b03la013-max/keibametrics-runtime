"""B3 fifth part (2026-11-25 15): BMONTH（生まれ月×新馬戦/2歳戦）as its own EXT component at weight 0."""
from runtime.local_autopilot import b3_labels as b3
from runtime.local_autopilot import ext_connect as ec
from runtime.local_autopilot import ext_model as em


def test_birth_month_parsing_and_bands():
    assert b3.birth_month('2024-03-15') == 3
    assert b3.birth_month('2024/6/1') == 6
    assert b3.birth_month('20240115') == 1
    assert b3.birth_month('アアア|2024/05/02') == 5
    assert b3.birth_month('アアア|') is None and b3.birth_month(None) is None and b3.birth_month('2024-13-01') is None
    assert [b3.month_band(m) for m in (1, 3, 4, 5, 6, 12)] == ['M1_3', 'M1_3', 'M4_5', 'M4_5', 'M6P', 'M6P']
    assert b3.month_band(None) is None


def test_bmonth_only_two_year_olds_with_birth():
    cur = {'age': 2, 'pop': 1, 'birth': '2024-02-10', 'shinba': True}
    assert b3.labels5(cur, []) == [('BMONTH', 'SHINBA|M1_3|1-2')]
    assert b3.labels5(dict(cur, shinba=False, pop=7, birth='2024/06/20'), [{'d': 1}]) == [('BMONTH', '2YO|M6P|6+')]
    assert b3.labels5(dict(cur, age=3), []) == []
    assert b3.labels5(dict(cur, birth=None), []) == []
    assert b3.labels5(dict(cur, pop=None), []) == []
    assert b3.labels5(dict(cur, age='x'), []) == []


def test_bmonth_is_own_component_at_zero():
    cur = {'date': '2026-11-25', 'venue': 'MON', 'distance': 850, 'going': '良', 'sex': '牝', 'pop': 4, 'age': 2,
           'birth': '2024-04-30', 'shinba': False}
    cl = dict(em.cand_labels(cur, []))
    assert cl['BMONTH'] == '2YO|M4_5|3-5'
    assert 'BMONTH' not in {n for n, _ in em.labels(cur, [])}
    assert em.CAND_COMPONENTS['BMONTH'] == 'BMO' == b3.COMPONENTS5['BMONTH']
    assert 'BMO' in ec.MEASURED and 'BMO' in ec.FIT_NAMES and ec.DEFAULT_BETA['BMO'] == 0.0
    assert all(ec.DEFAULT_BETA[k] == v for k, v in {'JKY': 0.35, 'FRM': 0.3, 'HRS': 0.0, 'PAT': 0.3, 'SPD': 0.8}.items())


def test_rows_use_birth_from_horse_key_and_shinba_from_cond():
    def race(rid, day, cond, runners):
        return {'race_id': rid, 'date': day, 'venue': 'MON', 'race_no': 1, 'distance': 850, 'going': '良', 'cond': cond,
                'field': len(runners), 'first_corner': {r['no']: r['no'] for r in runners},
                'last_corner': {r['no']: r['no'] for r in runners}, 'runners': runners}
    R = lambda no, name, b, age, fin: {'no': no, 'name': name, 'horse_key': f'{name}|{b}', 'age': age, 'status': 'RAN',
                                       'finish': fin, 'pop': no, 'time': 55.0 + fin}
    races = {'a': race('a', '2026-07-01', '2歳新馬', [R(1, 'アアア', '2024/01/20', 2, 1), R(2, 'イイイ', '2024/06/05', 2, 2)]),
             'b': race('b', '2026-08-01', 'C3', [R(1, 'ウウウ', '2023/02/01', 3, 1), R(2, 'エエエ', '', 2, 2)])}
    rows, _ = em._rows(races, {})
    got = {r['horse']: dict(r['cand_labels']).get('BMONTH') for r in rows}
    assert got[em.key('アアア')] == 'SHINBA|M1_3|1-2' and got[em.key('イイイ')] == 'SHINBA|M6P|1-2'
    assert got[em.key('ウウウ')] is None and got[em.key('エエエ')] is None


def test_prereg5_registered_before_measurement():
    assert b3.PREREG5['registered'] == '2026-11-25T15' and b3.PREREG5['labels'] == ['BMONTH']
    assert 'weight 0.0' in b3.PREREG5['rule']
