from runtime.local_autopilot import review


def _b(venue, rank, w, head):
    return {'venue': venue, 'paper': {'evaluation': {'winner_pre_rank': rank, 'winner_in_W': w, 'second_in_P2': False,
                                                      'third_in_P3': False, 'winner_is_ticket_head': head,
                                                      'trio_set_covered': False, 'top3_capture': 1}}}


def test_accuracy_rates_separate_from_pfs():
    a = review._accuracy([_b('OHI', 1, True, True), _b('OHI', 4, False, False), _b('KNZ', 2, False, False)])
    p = a['paper']['all']
    assert p['races'] == 3
    assert p['winner_pre_rank_1'] == 33.3
    assert p['winner_in_top3'] == 66.7
    assert p['winner_is_ticket_head'] == 33.3
    assert a['paper']['by_venue']['OHI']['races'] == 2
    assert a['formal_recommendation']['all'] is None


def test_role_set_coverage_reports_size_and_random_baseline():
    def e(win_w, size_w, field):
        return {'winner_in_W': win_w, 'second_in_P2': False, 'third_in_P3': True,
                'role_set_size': {'W': size_w, 'P2': 2, 'P3': 0}, 'field_size': field}
    rs = review.role_set_coverage([e(True, 2, 10), e(False, 4, 10)])
    assert rs['W'] == {'races': 2, 'mean_size': 3.0, 'coverage': 50.0, 'random_baseline': 30.0, 'lift': 20.0,
                       'empty_set_races': 0}
    assert rs['P3']['empty_set_races'] == 2 and rs['P3']['random_baseline'] == 0.0
    assert review.role_set_coverage([{'winner_in_W': True}]) is None


def test_track_carries_role_set_size():
    t = review._track('paper', [3, 1, 2, 4], {3: ['W'], 1: ['W', 'P2'], 2: ['P3']}, [], [1, 3, 2], {})
    assert t['evaluation']['role_set_size'] == {'W': 2, 'P2': 1, 'P3': 1}
    assert t['evaluation']['field_size'] == 4
