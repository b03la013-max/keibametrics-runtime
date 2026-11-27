from runtime.local_autopilot import kag


def test_red_checks_and_response_table():
    rv = {'layers': {'ROLE': {'evidence': {'winner_pre_rank': 6, 'winner_in_W': False, 'second_in_P2': True}},
                     'INDEX': {'evidence': {'winner_rank_by_index': {'HPI-L': 1, 'TPI-L': 1, 'SRI-L': 1}, 'ruled_neutral_share': 0.4}},
                     'CAPITAL': {'evidence': {'hit_but_loss': True, 'pfs': 40}}}}
    fe = {'krs': {'winner_rank_krs_ssr_w': 1, 'winner_rank_static': 6}, 'cap': {'hits_lost': ['TRIFECTA:1>2>3']}}
    ra = {'w_miss': {'winner_market_rank': 2}, 'revision2_not_effective': {'status': 'HOLD'}}
    t = {c for c, _ in kag.race_challenges(rv, fe, ra)}
    assert t == {'R1_REV2_NOT_EFFECTIVE', 'R1_NEUTRAL_HEAVY', 'R2_INDEX_CONFLICT', 'R2_MARKET_WINNER_LOW',
                 'R3_KRS_NOT_CONNECTED', 'R4_CAP_DROPPED_HIT', 'R4_HIT_BUT_LOSS'}
    assert set(kag.RESPONSE) >= t


def test_pre_race_flags():
    f = {'runners': [{'no': h, 'indices': {k: (90 if h == 5 else 50 + h) for k in kag.MAIN}} for h in range(1, 7)]}
    assert kag.pre_race_flags(f, [1, 2, 3, 4, 5, 6]) == [5]
    assert kag.pre_race_flags(f, [5, 1, 2, 3, 4, 6]) == []
