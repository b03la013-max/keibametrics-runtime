import json

from runtime.local_autopilot import going_rotation as gr
from runtime.local_autopilot import shadow_measure as sm


def _s(distance, first_pos):
    return {'distance': distance, 'content_positions': [first_pos] if first_pos else [], 'finish': 5}


def test_going_class():
    assert gr.going_class('不良') == 'WET' and gr.going_class('重') == 'WET'
    assert gr.going_class('稍重') == 'DAMP' and gr.going_class('良') == 'DRY'
    assert gr.going_class(None) == 'UNKNOWN' and gr.going_class('') == 'UNKNOWN'


def test_claim_groups():
    assert gr.classify('重', 1400, [_s(1200, 2)]) == ('WET:EXTEND:FRONT', {
        'claim': 'CLAIM_WET_EXTEND_FRONT', 'cur_distance': 1400, 'prev_distance': 1200, 'prev_first_pos': 2})
    assert gr.classify('不良', 1600, [_s(1400, 8)])[1]['claim'] == 'COUNTER_WET_EXTEND_BACK'
    assert gr.classify('良', 1400, [_s(1700, 9)])[1]['claim'] == 'CLAIM_DRY_SHORTEN_OR_SAME'
    assert gr.classify('良', 1450, [_s(1400, 1)])[0] == 'DRY:SAME:FRONT'      # 50 m is the same distance
    assert gr.classify('良', 1600, [_s(1400, 1)])[1]['claim'] == 'DRY_EXTEND'
    assert gr.classify('稍重', 1600, [_s(1400, 1)])[1]['claim'] == 'OTHER'


def test_unknown_is_never_guessed():
    assert gr.classify('重', None, [_s(1200, 2)])[0] == 'WET:UNKNOWN:FRONT'
    assert gr.classify('重', 1400, [_s(None, 2)])[0] == 'WET:UNKNOWN:FRONT'
    assert gr.classify('重', 1400, [_s(1200, None)])[0] == 'WET:EXTEND:UNKNOWN'
    assert gr.classify('重', 1400, [_s(1200, None)])[1]['claim'] == 'OTHER'
    assert gr.classify('良', 1400, [])[0] == 'DRY:NO_PRIOR:NA'


def test_shadow_measure_groups_going_rotation(tmp_path):
    day = tmp_path / '2026-11-18'
    (day / 'rev').mkdir(parents=True)
    ranking = [{'no': n, 'win': float(n)} for n in range(1, 7)]
    prior = {'1': [_s(1200, 1)], '2': [_s(1200, 9)], '3': [_s(1400, 3)]}
    (day / 'rev' / 'URW_01.r1.json').write_text(json.dumps({'prediction': {'ranking': ranking, 'prior_runs': prior}}))
    (day / 'URW_01.json').write_text(json.dumps({'race': {'race_name': 'C3', 'going': '重', 'distance': 1400}}))
    (day / 'URW_01.result.json').write_text(json.dumps({
        'revision': 'URW_01.r1', 'order': [1, 3, 2], 'effective_invest': 0, 'payout': 0,
        'payouts': {'WIN': {'1': 450}, 'PLACE': {'1': 150, '3': 200, '2': 300}}}))
    o = sm.measure(tmp_path)
    g = o['going_rotation']
    assert g['claim:CLAIM_WET_EXTEND_FRONT']['win_rate'] == 100.0 and g['claim:CLAIM_WET_EXTEND_FRONT']['win_pfs'] == 450.0
    assert g['claim:COUNTER_WET_EXTEND_BACK']['top3_rate'] == 100.0
    assert g['WET:SAME:FRONT']['races'] == 1
    assert '馬場×距離ローテ' in sm.md(o)


def test_shadow_measure_without_going(tmp_path):
    day = tmp_path / '2026-11-18'
    (day / 'rev').mkdir(parents=True)
    ranking = [{'no': n, 'win': float(n)} for n in range(1, 7)]
    (day / 'rev' / 'URW_01.r1.json').write_text(json.dumps({'prediction': {'ranking': ranking, 'prior_runs': {'1': [_s(1200, 1)]}}}))
    (day / 'URW_01.json').write_text(json.dumps({'race': {'race_name': 'C3'}}))
    (day / 'URW_01.result.json').write_text(json.dumps({
        'revision': 'URW_01.r1', 'order': [1, 3, 2], 'effective_invest': 0, 'payout': 0,
        'payouts': {'WIN': {'1': 450}, 'PLACE': {'1': 150}}}))
    assert sm.measure(tmp_path)['going_rotation'] == 'NO_GOING_OR_PRIOR_RUNS'


def test_frame_band_groups(tmp_path):
    assert (sm.frame_band(1), sm.frame_band(2), sm.frame_band(3), sm.frame_band(6), sm.frame_band(7)) == \
        ('INNER', 'INNER', 'MID', 'MID', 'OUTER')
    day = tmp_path / '2026-11-18'
    (day / 'rev').mkdir(parents=True)
    ranking = [{'no': n, 'win': float(n), 'frame': n} for n in range(1, 8)] + [{'no': 8, 'win': 9.0}]
    (day / 'rev' / 'FNB_01.r1.json').write_text(json.dumps({'prediction': {'ranking': ranking}}))
    (day / 'FNB_01.json').write_text(json.dumps({'race': {'race_name': 'C3', 'distance': 1200}}))
    (day / 'FNB_01.result.json').write_text(json.dumps({
        'revision': 'FNB_01.r1', 'order': [7, 1, 4], 'effective_invest': 0, 'payout': 0,
        'payouts': {'WIN': {'7': 800}, 'PLACE': {'7': 250, '1': 120, '4': 180}}}))
    f = sm.measure(tmp_path)['frame_band']
    assert f['FNB:OUTER']['races'] == 1 and f['FNB:OUTER']['win_rate'] == 100.0
    assert f['FNB:1200m:INNER']['races'] == 2 and f['FNB:1200m:INNER']['top3_rate'] == 50.0
    assert f['FNB:MID']['races'] == 4            # horse 8 has no frame and is not counted
