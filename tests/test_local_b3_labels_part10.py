"""B3 tenth part (2026-11-26 21): FAVJRADIRT（上位人気×中央でのダート経験）at weight 0 (n79 remainder)."""
from runtime.local_autopilot import b3_labels as b3
from runtime.local_autopilot import ext_connect as ec
from runtime.local_autopilot import ext_model as em

ST = [{'venue': '東京', 'date': '26.05.02', 'distance': 1600, 'surface': 'TURF'},
      {'venue': '中山', 'date': '26.03.10', 'distance': 1800, 'surface': 'DIRT'},
      {'venue': '大井', 'date': '26.10.01', 'distance': 1200, 'surface': 'DIRT'},
      {'venue': '阪神', 'date': '26.12.01', 'distance': 1400, 'surface': 'DIRT'}]


def test_jra_starts_filters_venue_and_date():
    js = b3.jra_starts(ST, '2026-11-26')
    assert js == [('2026-05-02', 'TURF'), ('2026-03-10', 'DIRT')]
    assert b3.jra_starts([{'venue': '京都', 'date': '26.01.05', 'distance': None, 'surface': 'DIRT'}], '2026-11-26') \
        == [('2026-01-05', None)]
    assert b3.jra_starts([{'venue': '東京', 'date': 'bad'}], '2026-11-26') == [] and b3.jra_starts(None) == []


def test_labels10_bands():
    turf = [('2026-05-02', 'TURF')]
    assert b3.labels10({'pop': 1, 'jra_starts': turf}, []) == [('FAVJRADIRT', 'NODIRT|FIRSTNAR|1')]
    assert b3.labels10({'pop': 2, 'jra_starts': turf + [('2026-03-10', 'DIRT')]}, [{'date': '2026-10-01'}]) \
        == [('FAVJRADIRT', 'DIRT|SEENNAR|2')]
    assert b3.labels10({'pop': 1, 'jra_starts': [('2026-01-05', None)]}, []) == [('FAVJRADIRT', 'UNKNOWN|FIRSTNAR|1')]
    assert b3.labels10({'pop': 3, 'jra_starts': turf}, []) == [] and b3.labels10({'pop': 1, 'jra_starts': []}, []) == []


def test_own_component_at_zero_and_not_in_pat():
    c = b3.COMPONENTS10['FAVJRADIRT']
    assert em.CAND_COMPONENTS['FAVJRADIRT'] == c and c in ec.MEASURED and c in ec.FIT_NAMES and ec.DEFAULT_BETA[c] == 0.0
    cur = {'date': '2026-11-26', 'venue': 'OHI', 'distance': 1200, 'going': '良', 'sex': '牡', 'pop': 1, 'age': 4,
           'jra_starts': [('2026-05-02', 'TURF')]}
    assert dict(em.cand_labels(cur, []))['FAVJRADIRT'] == 'NODIRT|FIRSTNAR|1'
    assert 'FAVJRADIRT' not in {n for n, _ in em.labels(cur, [])}
    assert all(ec.DEFAULT_BETA[k] == v for k, v in {'JKY': 0.35, 'FRM': 0.3, 'HRS': 0.0, 'PAT': 0.3, 'SPD': 0.8}.items())


def test_historical_rows_have_no_jra_label():
    rs = [{'no': i + 1, 'name': n, 'status': 'RAN', 'finish': i + 1, 'pop': i + 1, 'time': 70.0 + i}
          for i, n in enumerate(['アア', 'イイ'])]
    race = {'race_id': 'a', 'date': '2026-10-01', 'venue': 'OHI', 'race_no': 1, 'distance': 1200, 'going': '良',
            'cond': 'C3', 'field': 2, 'first_corner': {}, 'last_corner': {}, 'runners': rs, 'payouts': {}}
    rows, _ = em._rows({'a': race}, {})
    assert all('FAVJRADIRT' not in dict(r['cand_labels']) for r in rows)


def test_race_ext_passes_card_jra_starts():
    src = open(ec.__file__, encoding='utf-8').read()
    assert "'jra_starts': b3i.jra_starts(x.get('starts'), day)" in src


def test_prereg10_registered_before_measurement():
    assert b3.PREREG10['registered'] == '2026-11-26T21' and b3.PREREG10['labels'] == ['FAVJRADIRT']
    assert 'weight 0.0' in b3.PREREG10['rule']
