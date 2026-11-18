from runtime.local_autopilot import sire_stats as ss


def test_score_is_market_adjusted_and_shrunk():
    assert round(ss._score([100, 30.0, 30]), 2) == 52.0          # actual == expected
    hi, lo = ss._score([100, 30.0, 45]), ss._score([100, 30.0, 15])
    assert hi > 52 > lo and 30 <= lo and hi <= 75
    assert abs(ss._score([10, 3.0, 6]) - 52) < abs(ss._score([100, 30.0, 60]) - 52)   # fewer starts -> nearer 52


def test_lookup_backs_off_to_the_most_specific_cell_with_enough_starts():
    st = {'cells': {'sire|X|V|大井': [40, 12.0, 18], 'sire|X|ALL': [200, 60.0, 70], 'sire|X|V_B_G|大井|S|WET': [10, 3.0, 5]}}
    r = ss.lookup(st, 'sire', 'X', '大井', 'DIRT', 1200, '重')
    assert r['level'] == 'V' and r['n'] == 40
    r = ss.lookup(st, 'sire', 'X', '川崎', 'DIRT', 1200, '良')
    assert r['level'] == 'ALL'
    assert ss.lookup(st, 'sire', 'Y', '大井', 'DIRT', 1200, '良') is None


def test_race_evidence_weights():
    st = {'before_day': '2026-11-19', 'records': 1, 'cells': {'sire|X|ALL': [200, 60.0, 90]}}
    ev = ss.race_evidence({'venue_name': '大井', 'surface': 'DIRT', 'distance': 1200, 'going': '良'},
                          [{'horse_no': 1, 'sire': 'X', 'damsire': None}, {'horse_no': 2, 'sire': 'Z'}], st)
    a, b = ev['by_horse']['1'], ev['by_horse']['2']
    assert a['observed_weight'] == 40 and a['bvi_l_r2'] > 52 and b['bvi_l_r2'] == 52 and b['observed_weight'] == 0
