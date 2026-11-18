import json

from runtime.local_autopilot import class_move as cm
from runtime.local_autopilot import shadow_measure as sm


def _s(race_name, fin, venue='川崎'):
    return {'race_name': race_name, 'finish': fin, 'venue': venue}


def test_promotion_split_by_previous_finish():
    assert cm.classify('B3(一)', [_s('C1(一)', 1)])[0] == 'PROMOTED_AFTER_WIN'
    assert cm.classify('B3(一)', [_s('C1(二)', 2)])[0] == 'PROMOTED_AFTER_2ND'
    assert cm.classify('B3', [_s('C1', 4)])[0] == 'PROMOTED_AFTER_3RD_OR_WORSE'
    assert cm.classify('B3', [_s('C1', None)])[0] == 'PROMOTED_UNKNOWN_FINISH'


def test_demotion_board_in_upper_class():
    assert cm.classify('C1', [_s('B3', 3)])[0] == 'DEMOTED_AFTER_3RD'
    assert cm.classify('C1', [_s('B3', 9), _s('B3', 5)])[0] == 'DEMOTED_BOARD_IN_UPPER'
    assert cm.classify('C1', [_s('B3', 9), _s('B3', 7)])[0] == 'DEMOTED_NO_BOARD_IN_UPPER'


def test_same_unknown_jra_and_no_prior():
    assert cm.classify('C1(一)', [_s('C1(二)', 2)])[0] == 'SAME_CLASS'     # group difference is not a class move
    assert cm.classify('一般', [_s('C1', 1)])[0] == 'UNKNOWN'               # unreadable class is never guessed
    assert cm.classify('C3', [_s('未勝利', 3, venue='東京')])[0] == 'JRA_TRANSFER_FIRST'
    assert cm.classify('C3', [])[0] == 'NO_PRIOR'


def test_race_evidence_shape():
    ev = cm.race_evidence({'venue_id': 'KAW', 'race_name': 'B3'},
                          [{'horse_no': 4, 'starts': [_s('C1', 1)]}, {'horse_no': 7, 'starts': []}])
    assert ev['status'] == 'OK' and ev['nankan'] is True
    assert ev['by_horse']['4']['label'] == 'PROMOTED_AFTER_WIN' and ev['by_horse']['7']['label'] == 'NO_PRIOR'


def test_shadow_measure_groups_class_move_retroactively(tmp_path):
    day = tmp_path / '2026-11-17'
    (day / 'rev').mkdir(parents=True)
    ranking = [{'no': n, 'win': float(n)} for n in range(1, 7)]
    prior = {'1': [_s('C1', 1)], '2': [_s('C1', 5)], '3': [_s('B2', 4)]}
    (day / 'rev' / 'KAW_01.r1.json').write_text(json.dumps({'prediction': {'ranking': ranking, 'prior_runs': prior}}))
    (day / 'KAW_01.json').write_text(json.dumps({'race': {'race_name': 'B3(一)'}}))
    (day / 'KAW_01.result.json').write_text(json.dumps({
        'revision': 'KAW_01.r1', 'order': [2, 1, 3], 'effective_invest': 0, 'payout': 0,
        'payouts': {'WIN': {'2': 900}, 'PLACE': {'2': 300, '1': 150, '3': 200}}}))
    o = sm.measure(tmp_path)
    c = o['class_move']
    assert c['PROMOTED_AFTER_WIN']['races'] == 1 and c['PROMOTED_AFTER_WIN']['top3_rate'] == 100.0
    assert c['NANKAN:PROMOTED_AFTER_3RD_OR_WORSE']['win_rate'] == 100.0
    assert c['DEMOTED_BOARD_IN_UPPER']['races'] == 1
    assert 'NANKAN:PROMOTED_AFTER_WIN' in c
