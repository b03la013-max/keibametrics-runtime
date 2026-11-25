"""B3 sixth part (2026-11-25 18): FAVAWAY / FAVWET / FAVLIGHT（危険な人気馬の細目）as own EXT components at weight 0."""
from runtime.local_autopilot import b3_labels as b3
from runtime.local_autopilot import ext_connect as ec
from runtime.local_autopilot import ext_model as em


def test_bw_rel_bands():
    ws = [420, 440, 460, 480, 500, 520]
    assert b3.bw_rel(420, ws) == 'LIGHT' and b3.bw_rel(440, ws) == 'LIGHT'
    assert b3.bw_rel(460, ws) == 'MID' and b3.bw_rel(480, ws) == 'MID'
    assert b3.bw_rel(500, ws) == 'HEAVY' and b3.bw_rel(520, ws) == 'HEAVY'
    assert b3.bw_rel(450, [450, 460, 470]) is None and b3.bw_rel(None, ws) is None
    assert b3.bw_rel(450, [450] * 6) == 'MID'


def test_labels6_only_for_top_two_popularity():
    hist = [{'venue': 'URW', 'early': 0.8}, {'venue': 'URW', 'early': 0.7}, {'venue': 'KAW', 'early': 0.6}]
    cur = {'pop': 1, 'venue': 'OHI', 'going': '重', 'bw': 430, 'field_bws': [430, 450, 470, 490, 510, 530]}
    assert b3.labels6(cur, hist) == [('FAVAWAY', 'FIRST'), ('FAVWET', 'WET|CLOSER'), ('FAVLIGHT', 'LIGHT')]
    got = dict(b3.labels6(dict(cur, venue='KAW', going='稍重', bw=530, pop=2), [{'venue': 'KAW', 'early': 0.1}]))
    assert got == {'FAVAWAY': 'SEEN', 'FAVWET': 'DAMP|OTHER', 'FAVLIGHT': 'HEAVY'}
    assert b3.labels6(dict(cur, pop=3), hist) == [] and b3.labels6(dict(cur, pop=None), hist) == []
    assert b3.labels6(dict(cur, field_bws=None), []) == []   # debut: no history -> no FAVAWAY / FAVWET


def test_own_components_at_zero_and_not_in_pat():
    cur = {'date': '2026-11-25', 'venue': 'OHI', 'distance': 1200, 'going': '不良', 'sex': '牡', 'pop': 1, 'age': 4,
           'bw': 520, 'field_bws': [440, 460, 480, 500, 520]}
    cl = dict(em.cand_labels(cur, [{'date': '2026-11-01', 'venue': 'URW', 'distance': 1400, 'early': 0.2, 'bw': 518}]))
    assert cl['FAVAWAY'] == 'FIRST' and cl['FAVWET'] == 'WET|OTHER' and cl['FAVLIGHT'] == 'HEAVY'
    assert not ({'FAVAWAY', 'FAVWET', 'FAVLIGHT'} & {n for n, _ in em.labels(cur, [])})
    for k, c in b3.COMPONENTS6.items():
        assert em.CAND_COMPONENTS[k] == c and c in ec.MEASURED and c in ec.FIT_NAMES and ec.DEFAULT_BETA[c] == 0.0
    assert all(ec.DEFAULT_BETA[k] == v for k, v in {'JKY': 0.35, 'FRM': 0.3, 'HRS': 0.0, 'PAT': 0.3, 'SPD': 0.8}.items())


def test_rows_carry_field_body_weights():
    def race(rid, day, venue, runners):
        return {'race_id': rid, 'date': day, 'venue': venue, 'race_no': 1, 'distance': 1200, 'going': '良', 'cond': 'C3',
                'field': len(runners), 'first_corner': {r['no']: r['no'] for r in runners},
                'last_corner': {r['no']: r['no'] for r in runners}, 'runners': runners}
    R = lambda no, name, bw: {'no': no, 'name': name, 'status': 'RAN', 'finish': no, 'pop': no, 'time': 70.0 + no, 'bw': bw}
    names = ['アア', 'イイ', 'ウウ', 'エエ', 'オオ', 'カカ']
    races = {'a': race('a', '2026-10-01', 'URW', [R(i + 1, n, 450 + 10 * i) for i, n in enumerate(names)]),
             'b': race('b', '2026-11-01', 'OHI', [R(i + 1, n, 500 - 10 * i) for i, n in enumerate(names)])}
    rows, _ = em._rows(races, {})
    b = {r['horse']: dict(r['cand_labels']) for r in rows if r['race_id'] == 'b'}
    assert b[em.key('アア')]['FAVLIGHT'] == 'HEAVY' and b[em.key('アア')]['FAVAWAY'] == 'FIRST'
    assert b[em.key('イイ')]['FAVLIGHT'] == 'HEAVY'
    assert 'FAVLIGHT' not in b[em.key('ウウ')]   # 3番人気
    a = {r['horse']: dict(r['cand_labels']) for r in rows if r['race_id'] == 'a'}
    assert 'FAVAWAY' not in a[em.key('アア')] and a[em.key('アア')]['FAVLIGHT'] == 'LIGHT'


def test_prereg6_registered_before_measurement():
    assert b3.PREREG6['registered'] == '2026-11-25T18' and b3.PREREG6['labels'] == ['FAVAWAY', 'FAVWET', 'FAVLIGHT']
    assert 'weight 0.0' in b3.PREREG6['rule']
