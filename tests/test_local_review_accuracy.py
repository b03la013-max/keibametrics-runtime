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
