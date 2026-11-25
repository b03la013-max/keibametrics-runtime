from runtime.local_autopilot import nonbuy_trace as nb


def T(bt, *sel, stake=100):
    return {'bet_type': bt, 'selection': list(sel), 'stake': stake}


ROLES = {1: ['W'], 2: ['W', 'P2'], 3: ['P3'], 4: ['P2', 'P3']}
FULL = [T('EXACTA', 1, 2), T('EXACTA', 2, 1), T('EXACTA', 1, 4),
        T('TRIFECTA', 1, 2, 3), T('TRIFECTA', 2, 1, 3), T('TRIFECTA', 2, 4, 3), T('TRIO', 1, 2, 3)]


def test_order_uncertainty_other_direction_only():
    kept = [T('EXACTA', 2, 1), T('TRIFECTA', 2, 1, 3)]
    r = nb.race([1, 2, 3], ROLES, FULL, kept)
    ou = r['order_uncertainty']
    assert ou['EXACTA']['kept'] == 'OTHER_ONLY' and ou['EXACTA']['actual_in_full'] is True
    assert ou['TRIFECTA']['kept'] == 'OTHER_ONLY' and ou['TRIFECTA']['other_orders_kept'] == [[2, 1, 3]]
    r = nb.race([1, 2, 3], ROLES, FULL, FULL)
    assert r['order_uncertainty']['EXACTA']['kept'] == 'ACTUAL_AND_OTHER'
    r = nb.race([1, 2, 3], ROLES, FULL, [T('EXACTA', 1, 2)])
    assert r['order_uncertainty']['EXACTA']['kept'] == 'ACTUAL_ONLY'
    assert r['order_uncertainty']['TRIFECTA']['kept'] == 'NONE'


def test_head_continuity_for_each_w():
    kept = [T('EXACTA', 2, 1), T('TRIFECTA', 2, 4, 3)]
    r = nb.race([1, 2, 3], ROLES, FULL, kept)
    hc = r['head_continuity']
    assert set(hc) == {'1', '2'}
    assert hc['1']['terminal'] == 'HEAD_BUDGET_COMPRESSED' and hc['1']['is_winner'] is True
    assert hc['1']['exacta_full'] == 2 and hc['1']['exacta_kept'] == 0
    assert hc['2']['terminal'] == 'HEAD_PURCHASED'
    r = nb.race([1, 2, 3], {1: ['W'], 5: ['W']}, FULL, kept)
    assert r['head_continuity']['5']['terminal'] == 'HEAD_NOT_GENERATED'


def test_stage_tickets_and_stake():
    kept = [T('EXACTA', 2, 1, stake=300), T('TRIFECTA', 2, 4, 3, stake=200)]
    r = nb.race([1, 2, 3], ROLES, FULL, kept)
    h = r['role_horses']
    assert h['2']['tickets_full'] == 6 and h['2']['tickets_kept'] == 2 and h['2']['stake_kept'] == 500
    assert h['1']['stake_kept'] == 300 and h['3']['stake_kept'] == 200
    # tuple 形式（stake 無し）は 100 円/点
    r = nb.race([1, 2, 3], ROLES, FULL, [('EXACTA', [2, 1])])
    assert r['role_horses']['1']['stake_kept'] == 100


def test_aggregate_part2_and_existing_keys_unchanged():
    kept = [T('EXACTA', 2, 1), T('TRIFECTA', 2, 1, 3)]
    r1 = nb.race([1, 2, 3], ROLES, FULL, kept)
    r2 = nb.race([1, 2, 3], ROLES, FULL, FULL)
    a = nb.aggregate([r1, r2])
    assert a['order_uncertainty']['EXACTA'] == {'OTHER_ONLY': 1, 'ACTUAL_AND_OTHER': 1}
    assert a['head_continuity']['winner_w'] == {'HEAD_BUDGET_COMPRESSED': 1, 'HEAD_PURCHASED': 1}
    assert r1['actual_combination']['EXACTA'] == {'terminal': 'BUDGET_COMPRESSED', 'axis': 'CAPITAL'}
    assert a['races'] == 2


def test_part2_does_not_change_tickets():
    kept = [T('EXACTA', 2, 1)]
    snap = [dict(t, selection=list(t['selection'])) for t in kept]
    nb.race([1, 2, 3], ROLES, FULL, kept)
    assert kept == snap
