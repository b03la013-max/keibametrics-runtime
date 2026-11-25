from runtime.local_autopilot import nonbuy_trace as nb


def T(bt, *sel):
    return {'bet_type': bt, 'selection': list(sel)}


ROLES = {1: ['W'], 2: ['P2'], 3: ['P3'], 4: ['P2', 'P3'], 5: ['P3']}
FULL = [T('EXACTA', 1, 2), T('EXACTA', 1, 4), T('TRIO', 1, 2, 3), T('TRIFECTA', 1, 2, 3), T('TRIFECTA', 1, 4, 3)]


def test_purchased_vs_budget_compressed():
    kept = [T('EXACTA', 1, 2), T('TRIO', 1, 2, 3)]
    r = nb.race([1, 2, 3], ROLES, FULL, kept)
    ac = r['actual_combination']
    assert ac['EXACTA']['terminal'] == 'PURCHASED'
    assert ac['TRIO']['terminal'] == 'PURCHASED'
    assert ac['TRIFECTA'] == {'terminal': 'BUDGET_COMPRESSED', 'axis': 'CAPITAL'}
    assert r['role_horses']['4']['terminal'] == 'BUDGET_COMPRESSED'
    assert r['role_horses']['5']['terminal'] == 'NOT_GENERATED'
    assert r['role_horses_not_purchased'] == [4, 5]


def test_semantic_axes_are_separate_from_capital():
    r = nb.race([2, 1, 3], ROLES, FULL, FULL)
    assert r['actual_combination']['EXACTA']['terminal'] == 'SEMANTIC_EXCLUDED_ROLE_W'
    assert r['actual_combination']['TRIO']['terminal'] == 'PURCHASED'
    r = nb.race([1, 3, 2], ROLES, FULL, FULL)
    assert r['actual_combination']['EXACTA']['terminal'] == 'SEMANTIC_EXCLUDED_ROLE_P2'
    r = nb.race([1, 2, 9], ROLES, FULL, FULL)
    assert r['actual_combination']['TRIFECTA']['terminal'] == 'SEMANTIC_EXCLUDED_ROLE_P3'
    assert r['actual_combination']['TRIO']['terminal'] == 'SEMANTIC_EXCLUDED_ROLE_P3'


def test_not_generated_and_bet_type_absent():
    full = [T('EXACTA', 1, 2), T('TRIFECTA', 1, 2, 3)]
    r = nb.race([1, 4, 5], ROLES, full, full)
    assert r['actual_combination']['EXACTA']['terminal'] == 'NOT_GENERATED'
    assert r['actual_combination']['TRIO']['terminal'] == 'BET_TYPE_ABSENT'
    assert r['actual_combination']['TRIFECTA']['axis'] == 'STRUCTURE'


def test_paper_without_full_mec_and_aggregate():
    kept = [('EXACTA', [1, 2]), ('TRIO', [1, 2, 3])]
    r = nb.race([1, 2, 3], ROLES, [], kept)
    assert r['full_mec_observed'] is False
    assert r['actual_combination']['TRIFECTA']['terminal'] == 'BET_TYPE_ABSENT'
    a = nb.aggregate([r, nb.race([1, 2, 3], ROLES, FULL, kept), None])
    assert a['races'] == 2 and a['races_with_budget_compressed_hit'] == 1
    assert a['axis']['PURCHASED'] == 4
    assert nb.race([1, 2], ROLES, FULL, kept) is None


def test_trace_does_not_change_tickets():
    kept = [T('EXACTA', 1, 2)]
    snap = [dict(t, selection=list(t['selection'])) for t in kept]
    nb.race([1, 2, 3], ROLES, FULL, kept)
    assert kept == snap
