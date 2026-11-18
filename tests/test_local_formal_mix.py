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
