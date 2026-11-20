from runtime.local_autopilot import formal_mix as fm


def _summary():
    roles = {'1': ['W', 'P2', 'P3'], '2': ['W', 'P2', 'P3'], '3': ['P2', 'P3'], '4': ['P2', 'P3'], '5': ['P3']}
    tickets = [{'bet_type': 'TRIFECTA', 'selection': [1, 2, n]} for n in (3, 4, 5)] * 20
    return {'ranking': ['1', '2', '3', '4', '5'], 'roles': roles, 'tickets': tickets[:60],
            'signed_final_tickets': tickets * 2}


def test_signed_uses_delivered_post_cap_tickets():
    assert len(fm.signed(_summary())) == 60


def test_variants_respect_cap_and_box():
    v = fm.variants(_summary())
    assert len(v['P2BOX20_ONLY']) == 4                         # C(4,3)
    assert all(t[0] == 'TRIO' for t in v['P2BOX20_ONLY'])
    assert len(v['MIX_P2BOX20']) <= 60 and v['MIX_P2BOX20'][:4] == v['P2BOX20_ONLY']
    assert all(set(t[1]) & {1, 2} for t in v['MIX_WAXIS_TRIO'] if t[0] == 'TRIO')


def test_new_variants_and_rev2_effective(tmp_path):
    import json as _j
    from runtime.local_autopilot import formal_mix as _fm
    day = tmp_path / '2026-11-19' / 'formal'
    (day / 'rev2').mkdir(parents=True)
    summ = {'ranking': ['1', '2', '3', '4'], 'roles': {'1': ['W', 'P2', 'P3'], '2': ['P2', 'P3'], '3': ['P2', 'P3'], '4': ['P3']},
            'tickets': [{'bet_type': 'EXACTA', 'selection': [1, 2]}],
            'signed_final_tickets': [{'bet_type': 'TRIO', 'selection': [1, 2, 3]}, {'bet_type': 'EXACTA', 'selection': [1, 2]}]}
    (day / 'K_01.summary.json').write_text(_j.dumps(summ))
    (day / 'rev2' / 'K_01.summary.json').write_text(_j.dumps(summ))
    (day / 'rev2' / 'K_01.result.json').write_text(_j.dumps({'order': [1, 3, 2], 'payouts': {'TRIO': {'1-2-3': 500}}}))
    rs = _fm.races(tmp_path)
    assert len(rs) == 1                                   # result only under rev2 must still be counted
    v = _fm.variants(summ)
    assert ('TRIO', [1, 2, 3]) in v['KEEP_MEC_TRIO20'] and v['THIRD3_BY_PAIR'][0] == ('TRIFECTA', [1, 2, 3])
    assert rs[0]['KEEP_MEC_TRIO20'][1] == 500
    ev = _fm.evaluate(tmp_path)['variants']['R54_60']
    assert 'pfs_ex_top1' in ev and 'hit_but_loss' in ev
