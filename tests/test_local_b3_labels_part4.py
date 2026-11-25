"""B3 fourth part (2026-11-25 09): DEBINF（新馬の情報量区分、第374条）as its own EXT component at weight 0."""
from runtime.local_autopilot import b3_labels as b3
from runtime.local_autopilot import ext_connect as ec
from runtime.local_autopilot import ext_model as em


def test_info_class_and_field_info():
    assert b3.info_class(0.0) == 'TB' and b3.info_class(0.3) == 'PC' and b3.info_class(0.5) == 'ED'
    assert b3.info_class(None) is None
    assert b3.field_info(0, 8) == (0.0, True)
    assert b3.field_info(8, 8) == (1.0, False)
    assert b3.field_info(0, 0) == (None, False)


def test_debinf_only_when_debut_in_field():
    cur = {'pop': 1, 'field_hist_share': 0.0, 'field_has_debut': True}
    assert b3.labels4(cur, []) == [('DEBINF', 'TB|N|1-2')]
    cur = {'pop': 4, 'field_hist_share': 0.75, 'field_has_debut': True}
    assert b3.labels4(cur, [{'date': '2026-10-01'}]) == [('DEBINF', 'ED|H|3-5')]
    assert b3.labels4(dict(cur, pop=7, field_hist_share=0.2), []) == [('DEBINF', 'PC|N|6+')]
    assert b3.labels4({'pop': 1, 'field_hist_share': 1.0, 'field_has_debut': False}, [{'d': 1}]) == []
    assert b3.labels4({'pop': None, 'field_hist_share': 0.0, 'field_has_debut': True}, []) == []


def test_debinf_is_own_component_at_zero():
    cur = {'date': '2026-11-25', 'venue': 'MON', 'distance': 850, 'going': '良', 'sex': '牝', 'pop': 2,
           'field_hist_share': 0.0, 'field_has_debut': True}
    cl = dict(em.cand_labels(cur, []))
    assert cl['DEBINF'] == 'TB|N|1-2'
    assert 'DEBINF' not in {n for n, _ in em.labels(cur, [])}
    assert em.CAND_COMPONENTS['DEBINF'] == 'DBI' == b3.COMPONENTS4['DEBINF']
    assert 'DBI' in ec.MEASURED and 'DBI' in ec.FIT_NAMES and ec.DEFAULT_BETA['DBI'] == 0.0
    assert all(ec.DEFAULT_BETA[k] == v for k, v in {'JKY': 0.35, 'FRM': 0.3, 'HRS': 0.0, 'PAT': 0.3, 'SPD': 0.8}.items())
    r = {'venue': 'MON', 'band': 'SHORT', 'going': 'DRY', 'distance': 850, 'sire': None, 'damsire': None,
         'jockey': None, 'trainer': None, 'frame': None, 'horse': None, 'bwchg': None, 'age': None, 'season': 'AUT',
         'sex': '牝', 'spd_band': 'NA', 'labels': [], 'cand_labels': [('DEBINF', 'TB|N|1-2')], 'pop': 2, 'fband': 'MID'}
    comp = em.components({('P', 'DEBINF', 'TB|N|1-2'): [400, 150, 100.0]}, r)
    assert 'DBI' in comp and 'PAT' not in comp


def _race(rid, day, runners):
    return {'race_id': rid, 'date': day, 'venue': 'MON', 'race_no': 1, 'distance': 850, 'going': '良', 'cond': '2歳新馬',
            'field': len(runners), 'first_corner': {r['no']: r['no'] for r in runners},
            'last_corner': {r['no']: r['no'] for r in runners}, 'runners': runners}


def test_rows_mark_field_information():
    R = lambda no, name, fin: {'no': no, 'name': name, 'status': 'RAN', 'finish': fin, 'pop': no, 'time': 55.0 + fin}
    races = {'a': _race('a', '2026-10-01', [R(1, 'アアア', 1), R(2, 'イイイ', 2)]),
             'b': _race('b', '2026-10-20', [R(1, 'アアア', 2), R(2, 'ウウウ', 1), R(3, 'エエエ', 3)])}
    rows, _ = em._rows(races, {})
    first = {r['horse']: dict(r['cand_labels']).get('DEBINF') for r in rows if r['date'] == '2026-10-01'}
    assert set(first.values()) == {'TB|N|1-2'}
    later = {r['horse']: dict(r['cand_labels']).get('DEBINF') for r in rows if r['date'] == '2026-10-20'}
    assert later[em.key('アアア')] == 'PC|H|1-2'
    assert later[em.key('ウウウ')] == 'PC|N|1-2' and later[em.key('エエエ')] == 'PC|N|3-5'


def test_prereg4_registered_before_measurement():
    assert b3.PREREG4['registered'] == '2026-11-25T09' and b3.PREREG4['labels'] == ['DEBINF']
    assert 'weight 0.0' in b3.PREREG4['rule']
