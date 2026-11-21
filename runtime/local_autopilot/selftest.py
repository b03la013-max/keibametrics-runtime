"""Offline self-test for LOCAL autopilot settlement rules (no network).

python -m runtime.local_autopilot.selftest
"""
from runtime.local_autopilot import settle, sbo, engine
from datetime import date


def pred(tickets, ranking=(1, 2, 3, 4, 5)):
    return {'edition': '直前版', 'revision_id': 'T.r1', 'ticket_sha256': 'x', 'saved_at': 't',
            'prediction': {'ranking': [{'no': n} for n in ranking], 'tickets': tickets}}


def check():
    # 1) refund: horse 9 scratched (取消) -> its combinations refunded, not paid
    res = {'order': [1, 2, 3, 4], 'non_starters': [9], 'did_not_finish': [7],
           'payouts': {'WIDE': {(1, 2): 250, (1, 3): 400, (2, 3): 600}, 'TRIO': {(1, 2, 3): 1500},
                       'WIN': {(1,): 300}}}
    st = settle.settle_parsed(res, pred([{'k': 'ワイド', 'b': '1-2 / 1-9'},
                                         {'k': '三連複', 'b': '1-2-3 / 1-2-9 / 1-2-7'}]), 'p')
    assert st['invest'] == 500 and st['refund'] == 200 and st['effective_invest'] == 300, st
    assert st['payout'] == 250 + 1500, st  # 1-2-7: 7 started (中止) -> live, lost, no refund
    assert st['pfs'] == round(100 * 1750 / 300, 1)
    # 2) dead heat for 2nd: two exacta combinations published, both honoured
    res = {'order': [1, 2, 3], 'payouts': {'EXACTA': {(1, 2): 800, (1, 3): 900}}}
    st = settle.settle_parsed(res, pred([{'k': '馬単', 'b': '1→2,3'}]), 'p')
    assert st['payout'] == 1700 and st['invest'] == 200, st
    # 3) bet type not sold / not published -> marked, no phantom payout
    res = {'order': [1, 2, 3], 'payouts': {'WIN': {(1,): 200}}}
    st = settle.settle_parsed(res, pred([{'k': '三連単', 'b': '1→2→3'}]), 'p')
    assert st['tickets'][0]['status'] == 'NOT_SOLD_OR_NOT_PUBLISHED' and st['payout'] == 0
    # 4) everything refunded -> effective investment 0 -> PFS NULL (not 0%)
    res = {'order': [1, 2, 3], 'non_starters': [5], 'payouts': {'WIN': {(1,): 200}}}
    st = settle.settle_parsed(res, pred([{'k': '単勝', 'b': '5'}]), 'p')
    assert st['effective_invest'] == 0 and st['pfs'] is None, st
    # 5) place with 2 paid places (small field)
    res = {'order': [4, 1, 2], 'payouts': {'PLACE': {(4,): 110, (1,): 130}}}
    st = settle.settle_parsed(res, pred([{'k': '複勝', 'b': '1'}]), 'p')
    assert st['payout'] == 130
    # 6) frozen runner absent from every result row -> inferred non-starter refund
    res = {'order': [1, 2, 3], 'payouts': {'WIDE': {(1, 2): 300}}}
    pr = pred([{'k': 'ワイド', 'b': '1-2 / 1-6'}]); pr['runners'] = [{'no': n} for n in (1, 2, 3, 6)]
    st = settle.settle_parsed(res, pr, 'p')
    assert st['non_starters_inferred'] == [6] and st['refund'] == 100 and st['payout'] == 300, st
    # 7) SBO table parsing (synthetic page with the same structure) + VMI-L
    html = ('<table id="table"><tr><th>馬</th></tr>'
            '<tr><td rowspan="2">1</td><td rowspan="2">A</td><td>t</td><td>52.0</td><td>j</td><td><br /></td>'
            '<td class="center">88(5)</td><td>87(5)</td><td class="bgred">89(5)</td><td rowspan="2">88</td></tr>'
            '<tr><td>81-98</td><td>81-98</td><td>74-101</td></tr>'
            '<tr><td rowspan="2">2</td><td rowspan="2">B</td><td>t</td><td>54.0</td><td>j</td><td><br /></td>'
            '<td>*(0)</td><td>*(0)</td><td>*(0)</td><td>*</td></tr><tr><td></td><td></td><td></td></tr>'
            '<tr><td rowspan="2">3</td><td rowspan="2">C</td><td>t</td><td>54.0</td><td>j</td><td><br /></td>'
            '<td>80(3)</td><td>80(3)</td><td>80(3)</td><td>80</td></tr></table>')
    t = sbo.parse_table(html)
    assert t[1]['avg'] == 88 and t[2]['avg'] is None and t[3]['n'] == 3, t
    v = sbo.vmi(t, [1, 2, 3])
    assert v[2] is None and v[1] == 60.0 and v[3] == 44.0, v
    # 8) VMI blend changes F3S by the fixed prior weight only, unknown horse -> neutral 52
    runners = [{'horse_no': n, 'name': f'H{n}', 'frame_no': n, 'starts': [], 'current_jockey': 'x', 'trainer': 'y'}
               for n in (1, 2, 3)]
    race = {'venue_id': 'OHI', 'venue_name': '大井', 'distance': 1200, 'race_name': 'C3', 'class_text': ''}
    odds = {n: {'win': w} for n, w in ((1, 2.0), (2, 4.0), (3, 8.0))}
    a = {x['no']: x['F3S'] for x in engine.predict(race, runners, odds, date(2026, 11, 16))['rows']}
    b = {x['no']: x['F3S'] for x in engine.predict(race, runners, odds, date(2026, 11, 16), {'vmi': v})['rows']}
    w = engine.VMI_WEIGHT
    assert abs(b[1] - ((1 - w) * a[1] + w * 60)) < 1e-9 and abs(b[2] - ((1 - w) * a[2] + w * 52)) < 1e-9, (a, b)
    # 9) 競馬ブック bands: VERY_STRONG CCI + CAUTION TRI shift F3S by KB_WEIGHT x deviation
    c = {x['no']: x['F3S'] for x in engine.predict(race, runners, odds, date(2026, 11, 16),
                                                     {'kb': {1: {'cci': 'VERY_STRONG', 'tri': 'CAUTION'}}})['rows']}
    k = engine.KB_WEIGHT
    assert abs(c[1] - (a[1] + k * 14 - k * 7)) < 1e-9 and c[2] == a[2], (a, c)
    # 10) TM consensus / RT-CPU / pace: F3S shifts by fixed priors; 逃げ raises EVI toward 82
    e = {x['no']: x for x in engine.predict(race, runners, odds, date(2026, 11, 16),
                                              {'kb': {2: {'tm': 60.0, 'rt': 56.0, 'cpu': 60.0, 'pace': '逃げ'}}})['rows']}
    base2 = {x['no']: x for x in engine.predict(race, runners, odds, date(2026, 11, 16))['rows']}[2]
    assert e[2]['PACE'] == '逃げ' and e[2]['EVI'] > base2['EVI'] and e[2]['KBA'] == 58.0, e[2]
    # 11) 2026-11-16 水沢1R: both favorites round to F3S 66.4 and have
    # no market odds; raw F3S, not card number, must break the residual tie.
    near = [{'no': 6, 'F3S': 66.36071380121577, 'win': None},
            {'no': 9, 'F3S': 66.44349778353482, 'win': None}]
    assert [x['no'] for x in engine.rank_f3s(near)] == [9, 6]
    # Published odds still take priority within the existing rounded band.
    near[0]['win'], near[1]['win'] = 2.0, 3.0
    assert [x['no'] for x in engine.rank_f3s(near)] == [6, 9]
    print('SELFTEST_OK 11/11')


if __name__ == '__main__':
    check()
