from runtime.local_autopilot import strata


def test_going_class_and_keys():
    assert strata.going_class('不良') == 'WET' and strata.going_class('重') == 'WET'
    assert strata.going_class('稍重') == 'DAMP' and strata.going_class('良') == 'DRY'
    k = strata.keys('OHI', {'distance': 1200, 'going_class': 'WET'})
    assert k == {'venue': 'OHI', 'venue_distance': 'OHI:1200m', 'venue_going': 'OHI:WET'}


def test_split_flags_small_cells():
    rows = [{'strata': strata.keys('OHI', {'distance': 1200, 'going_class': 'DRY'})} for _ in range(12)] + \
           [{'strata': strata.keys('OHI', {'distance': 1600, 'going_class': 'DRY'})}]
    out = strata.split(rows, lambda rs: {})
    assert out['venue']['OHI']['races'] == 13 and out['venue_distance']['OHI:1200m']['decides']
    assert not out['venue_distance']['OHI:1600m']['decides']
