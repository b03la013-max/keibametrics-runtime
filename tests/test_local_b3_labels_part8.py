"""B3 eighth part (2026-11-26 15): FAVH2H（上位人気×同じ相手との比較）as an own EXT component at weight 0."""
from runtime.local_autopilot import b3_labels as b3
from runtime.local_autopilot import ext_connect as ec
from runtime.local_autopilot import ext_model as em


def P(day, fin, venue='OHI', dist=1200, field=8):
    return {'date': day, 'venue': venue, 'distance': dist, 'field': field, 'finish': fin}


def test_h2h_uses_most_recent_common_race():
    me = [P('2026-09-01', 1), P('2026-10-01', 5)]
    a = [P('2026-09-01', 3), P('2026-10-01', 2)]        # latest meeting: a 2nd, me 5th -> beaten
    b = [P('2026-09-01', 4)]                            # only the older meeting: me 1st -> ahead
    c = [P('2026-10-01', 1, field=12)]                  # different field size -> not the same race
    assert b3.h2h(me, [a, b, c]) == (2, 1)
    assert b3.h2h(me, []) == (0, 0) and b3.h2h([], [a]) == (0, 0)
    assert b3.meet_key({'date': '2026-10-01', 'venue': 'OHI', 'distance': 1200}) is None


def test_labels8_values_and_fav_only():
    assert b3.labels8({'pop': 1, 'h2h': (0, 0)}, []) == [('FAVH2H', 'NOMEET')]
    assert b3.labels8({'pop': 2, 'h2h': (3, 0)}, []) == [('FAVH2H', 'BEATALL')]
    assert b3.labels8({'pop': 1, 'h2h': (3, 1)}, []) == [('FAVH2H', 'LOST1')]
    assert b3.labels8({'pop': 1, 'h2h': (3, 2)}, []) == [('FAVH2H', 'LOST2+')]
    assert b3.labels8({'pop': 3, 'h2h': (3, 2)}, []) == [] and b3.labels8({'pop': 1}, []) == []


def test_own_component_at_zero_and_not_in_pat():
    c = b3.COMPONENTS8['FAVH2H']
    assert em.CAND_COMPONENTS['FAVH2H'] == c and c in ec.MEASURED and c in ec.FIT_NAMES and ec.DEFAULT_BETA[c] == 0.0
    cur = {'date': '2026-11-26', 'venue': 'OHI', 'distance': 1200, 'going': '良', 'sex': '牡', 'pop': 1, 'age': 4,
           'h2h': (2, 1)}
    assert dict(em.cand_labels(cur, [P('2026-11-01', 2)]))['FAVH2H'] == 'LOST1'
    assert 'FAVH2H' not in {n for n, _ in em.labels(cur, [])}
    assert all(ec.DEFAULT_BETA[k] == v for k, v in {'JKY': 0.35, 'FRM': 0.3, 'HRS': 0.0, 'PAT': 0.3, 'SPD': 0.8}.items())


def test_rows_compare_only_with_pre_race_meetings():
    def race(rid, day, order):
        rs = [{'no': i + 1, 'name': n, 'status': 'RAN', 'finish': order[i], 'pop': order[i], 'time': 70.0 + order[i]}
              for i, n in enumerate(['アア', 'イイ', 'ウウ'])]
        return {'race_id': rid, 'date': day, 'venue': 'OHI', 'race_no': 1, 'distance': 1200, 'going': '良',
                'cond': 'C3', 'field': 3, 'first_corner': {}, 'last_corner': {}, 'runners': rs}
    a = race('a', '2026-10-01', [2, 1, 3])   # イイ beats アア
    b = race('b', '2026-11-01', [1, 2, 3])   # アア is favourite (pop 1)
    rows, _ = em._rows({'a': a, 'b': b}, {})
    got = lambda rid, nm: dict(next(r for r in rows if r['race_id'] == rid and r['horse'] == em.key(nm))['cand_labels'])
    assert got('a', 'イイ')['FAVH2H'] == 'NOMEET'   # first meeting: nothing known before race a
    assert got('b', 'アア')['FAVH2H'] == 'LOST1'    # イイ finished ahead in race a
    assert got('b', 'イイ')['FAVH2H'] == 'BEATALL'
    assert 'FAVH2H' not in got('b', 'ウウ')         # 3番人気


def test_prereg8_registered_before_measurement():
    assert b3.PREREG8['registered'] == '2026-11-26T15' and b3.PREREG8['labels'] == ['FAVH2H']
    assert 'weight 0.0' in b3.PREREG8['rule']
