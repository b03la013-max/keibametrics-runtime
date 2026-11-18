import math

from runtime.local_autopilot import bloodline_kametani as bk
from runtime.local_autopilot import shadow_measure as sm


def _ctx(**k):
    base = {'surface': 'DIRT', 'distance': 1200, 'going': '良', 'sex': '牝', 'age': 4, 'damsire_type': None,
            'starts': [{'finish': 5, 'distance': 1400, 'surface': 'DIRT', 'ride_body_weight': 470}], 'newcomer': False,
            'front': True, 'pop': 2, 'frame': 3}
    base.update(k)
    return base


US = {'country': '米国型', 'sunday': False, 'kingmambo': False}


def test_all_conditions_of_a_scene_are_required():
    # 001 フィレンツェファイア: ダート1200m以下 AND 母米国型 AND 牡馬 (ChatGPT-reported v1 false match)
    alt = {'S': 'D', 'd': [0, 1200], 'ds': 'US', 'sex': 'M'}
    assert bk.check(alt, _ctx())[0] == 'NO'                                  # mare: sex fails
    assert bk.check(alt, _ctx(sex='牡'))[0] == 'UNKNOWN'                     # damsire class unknown
    assert bk.check(alt, _ctx(sex='牡', damsire_type=US))[0] == 'MATCH'
    assert bk.check(alt, _ctx(sex='牡', damsire_type=US, distance=1400))[0] == 'NO'


def test_unreadable_and_jra_scenes_never_match():
    assert bk.check({'S': 'D', 'x': ['直線の長いダート']}, _ctx())[0] == 'UNKNOWN'
    assert bk.check({'jra': 1}, _ctx())[0] == 'NOT_LOCAL'
    assert bk.check({'S': 'D', 'wet': 1}, _ctx(going='重'))[0] == 'MATCH'
    assert bk.check({'S': 'D', 'chg': 'short'}, _ctx())[0] == 'MATCH'      # 1400 -> 1200


def test_v1_false_match_is_gone():
    r = {'horse_no': 1, 'sire': 'フィレンツェファイア', 'damsire': 'X', 'sex_age': '牝3', 'age': 3, 'starts': [], 'popularity': 5}
    ev = bk.evaluate(r, {'surface': 'DIRT', 'distance': 1200})
    assert ev['buy_match'] is False


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
