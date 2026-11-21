from runtime.local_autopilot import auto_promote, formal_mix as fm


def _summ(spd=None, n=8):
    mec = [{'bet_type': 'TRIFECTA', 'selection': [5, 6, 7]}, {'bet_type': 'TRIFECTA', 'selection': [1, 4, 2]},
           {'bet_type': 'EXACTA', 'selection': [1, 2]}, {'bet_type': 'TRIO', 'selection': [3, 5, 6]}]
    s = {'ranking': [str(i) for i in range(1, n + 1)],
         'roles': {'1': ['W'], '2': ['P2'], '3': ['P2'], '4': ['P2'], '5': ['P2']},
         'tickets': mec[:2], 'signed_final_tickets': mec}
    if spd is not None:
        s['ext_connection'] = {'status': {'spd_horses': spd}}
    return s


def test_core_layer_orders_by_layer():
    v = fm.variants(_summ())['CORE_LAYER_60']
    assert v[0] == ('TRIFECTA', [1, 4, 2]) or v[0] == ('EXACTA', [1, 2])
    assert ('TRIFECTA', [5, 6, 7]) == v[-1] or ('TRIO', [3, 5, 6]) == v[-1]
    assert len(v) == 4


def test_core_layer_falls_back_without_mec():
    s = _summ(); s['signed_final_tickets'] = []
    assert fm.variants(s)['CORE_LAYER_60'] == fm.signed(s)


def test_nobet_lowinfo():
    assert fm.variants(_summ(spd=3))['NOBET_LOWINFO'] == []
    assert fm.variants(_summ(spd=4))['NOBET_LOWINFO'] == fm.signed(_summ())
    assert fm.variants(_summ())['NOBET_LOWINFO'] == fm.signed(_summ())   # before EXT: never low


def test_c28_registered_with_prereg():
    import json
    v, f = auto_promote.CANDIDATES['C28-CORE-LAYER-60']
    p = json.loads((auto_promote.REPO / 'profiles' / f).read_text())
    assert v == 'CORE_LAYER_60' and p['first_eligible_post'].startswith('2026-11-22')
