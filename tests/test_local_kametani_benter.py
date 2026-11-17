import math

from runtime.local_autopilot import bloodline_kametani as bk
from runtime.local_autopilot import shadow_measure as sm


def _ctx(**k):
    base = {'surface': 'DIRT', 'distance': 1200, 'sex': '牡', 'age': 4, 'damsire_type': None, 'last_finish': 5,
            'front': True, 'pop': 2, 'newcomer': False, 'going': '良'}
    base.update(k)
    return base


def test_clause_distance_surface_and_unknown_damsire():
    assert bk._clause('ダート1700m以上', _ctx()) == 'NO'
    assert bk._clause('ダート1700m以上', _ctx(distance=1800)) == 'MATCH'
    assert bk._clause('ダート1700m以上で母父が米国型', _ctx(distance=1800)) == 'UNKNOWN'
    assert bk._clause('ダート1700m以上で母父が米国型', _ctx(distance=1800, damsire_type={'country': '米国型', 'sunday': False})) == 'MATCH'


def test_jra_course_and_going_clauses():
    assert bk._clause('東京・阪神の湿ったダート', _ctx()) == 'NOT_LOCAL'
    assert bk._clause('湿ったダート', _ctx()) == 'NO'
    assert bk._clause('湿ったダート', _ctx(going='重')) == 'MATCH'


def test_rules_table_loads_nar_sires():
    t = bk.table()
    assert len(t) >= 90
    assert any('ヘニーヒューズ' in k for k in t)


def test_odds_gap_positions():
    assert sm.odds_gap({1: 1.5, 2: 4.0, 3: 5.0})[0] == 1
    assert sm.odds_gap({1: 2.0, 2: 2.5, 3: 6.0})[0] == 2
    assert sm.odds_gap({1: 2.0, 2: 2.5, 3: 3.0})[0] is None


def test_combine_and_harville_discount():
    q = {1: 0.5, 2: 0.3, 3: 0.2}
    p = {1: 0.2, 2: 0.3, 3: 0.5}
    assert abs(sum(sm._combine(q, p, 0.4, 0.8).values()) - 1) < 1e-9
    assert sm._combine(q, p, 0.0, 1.0) == q or all(abs(sm._combine(q, p, 0, 1)[k] - q[k]) < 1e-9 for k in q)
    plain = sm._harville_ll(q, [1, 2, 3], 1, 1)
    assert abs(plain - (math.log(0.3 / 0.5) + math.log(1.0))) < 1e-9
    assert sm._harville_ll(q, [1, 3, 2], 0.81, 0.65) > sm._harville_ll(q, [1, 3, 2], 1, 1)
