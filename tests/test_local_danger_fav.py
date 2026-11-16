from runtime.local_autopilot import danger_fav as df


def _r(no, odds, starts, frame=1, jockey='森泰斗', chg=0):
    return {'horse_no': no, 'win_odds': odds, 'frame_no': frame, 'current_jockey': jockey,
            'current_body_weight_change': chg, 'starts': starts}


def _s(venue, dist, fin, pos, field=12, d='26.10.20', jockey='森泰'):
    return {'venue': venue, 'distance': dist, 'finish': fin, 'finish_text': str(fin), 'field_size': field,
            'content_positions': pos, 'date': d, 'ride_jockey': jockey}


RACE = {'venue_name': '川崎', 'distance': 1500, 'race_date': '2026-11-17'}


def test_rank_a_first_course_and_distance():
    fav = _r(3, 1.8, [_s('大井', 1200, 1, [1, 1])], frame=8)
    o = df.flags(RACE, [fav, _r(1, 3.5, [_s('川崎', 1500, 2, [3, 3])]), _r(2, 9.0, [])])
    assert o['favorite_no'] == 3 and o['danger_rank'] == 'A'
    f = o['flags']
    assert f['first_course'] and f['first_distance'] and f['outer_frame_small_track']
    assert f['last_lost'] is False and f['jockey_change'] is False
    assert f['workout_or_stable_caution'] is None   # no Keibabook: unknown, never guessed


def test_keibabook_labels_override_and_none_rank():
    fav = _r(5, 1.5, [_s('川崎', 1500, 1, [2, 2], d='26.11.01')])
    kb = {5: {'course_first': False, 'style': '先行', 'tri': 'STRONG', 'cci': 'NEUTRAL', 'tm': 70, 'pace': '好位'},
          6: {'tm': 50}}
    o = df.flags(RACE, [fav, _r(6, 4.0, []), _r(7, 8.0, [])], kb)
    assert o['danger_rank'] == 'NONE' and o['flags']['closer_style'] is False
    assert o['flags']['press_not_top'] is False and o['flags']['layoff'] is False


def test_no_odds():
    assert df.flags(RACE, [_r(1, None, [])])['status'] == 'NO_ODDS'
