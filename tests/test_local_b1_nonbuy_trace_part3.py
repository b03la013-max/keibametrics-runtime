from runtime.local_autopilot import nonbuy_trace as nb


def T(bt, *sel, stake=100):
    return {'bet_type': bt, 'selection': list(sel), 'stake': stake}


ROLES = {1: ['W'], 2: ['W', 'P2'], 3: ['P3'], 4: ['P2', 'P3']}


def test_duplicate_normalized_trio_is_order_free():
    kept = [T('TRIO', 1, 2, 3), T('TRIO', 3, 2, 1), T('EXACTA', 1, 2), T('EXACTA', 2, 1), T('EXACTA', 1, 2)]
    r = nb.race([1, 2, 3], ROLES, [], kept, runners=[1, 2, 3, 4])
    h = r['ticket_hygiene']['delivered']
    assert h['DUPLICATE_NORMALIZED'] == 2 and h['INVALID_RUNNER'] == 0 and h['unique_valid'] == 3
    assert r['ticket_hygiene']['full_mec'] is None


def test_invalid_runner_kinds():
    kept = [T('EXACTA', 1, 9), T('TRIFECTA', 1, 1, 2), T('TRIO', 1, 2), T('EXACTA', 'x', 2), T('EXACTA', 1, 2)]
    r = nb.race([1, 2, 3], ROLES, kept, kept, runners=[1, 2, 3, 4])
    h = r['ticket_hygiene']['delivered']
    assert h['INVALID_RUNNER'] == 4 and h['field_check'] == 'TESTED'
    assert h['invalid_kinds'] == {'NOT_IN_FIELD': 1, 'REPEATED_HORSE': 1, 'WRONG_SIZE': 1, 'UNPARSEABLE': 1}
    r = nb.race([1, 2, 3], ROLES, [], [T('EXACTA', 1, 9)])
    assert r['ticket_hygiene']['delivered']['field_check'] == 'UNTESTED'
    assert r['ticket_hygiene']['delivered']['INVALID_RUNNER'] == 0


def test_width_records_roles_and_stake():
    full = [T('EXACTA', 1, 2), T('EXACTA', 2, 1), T('TRIFECTA', 1, 2, 3)]
    r = nb.race([1, 2, 3], ROLES, full, [T('EXACTA', 1, 2, stake=300)], key='OHI_20261126_R03')
    w = r['width']
    assert w['roles'] == {'W': 2, 'P2': 2, 'P3': 2}
    assert w['full_mec']['total'] == 3 and w['full_mec']['TRIFECTA'] == 1
    assert w['delivered'] == {'EXACTA': 1, 'TRIO': 0, 'TRIFECTA': 0, 'total': 1, 'stake': 300}
    assert w['key'] == 'OHI_20261126_R03'


def test_whiplash_after_hit_and_miss_same_venue_consecutive_only():
    hit = [T('EXACTA', 1, 2)]
    miss = [T('EXACTA', 4, 2)]
    a = nb.race([1, 2, 3], ROLES, [], hit, key='OHI_20261126_R01')            # 当たり 1点
    b = nb.race([1, 2, 3], ROLES, [], miss * 1 + [T('EXACTA', 2, 4), T('EXACTA', 4, 1)], key='OHI_20261126_R02')  # 外れ 3点
    c = nb.race([1, 2, 3], ROLES, [], miss, key='OHI_20261126_R03')           # 外れ 1点
    d = nb.race([1, 2, 3], ROLES, [], hit, key='KAW_20261126_R04')            # 別の場：組にしない
    e = nb.race([1, 2, 3], ROLES, [], hit, key='OHI_20261126_R05')            # R04 が無い：組にしない
    w = nb.whiplash([c, a, d, b, e])
    assert w['pairs'] == 2
    assert w['AFTER_HIT']['n'] == 1 and w['AFTER_HIT']['mean_delivered_change'] == 2
    assert w['AFTER_MISS']['n'] == 1 and w['AFTER_MISS']['mean_abs_delivered_change'] == 2
    agg = nb.aggregate([a, b, c])
    assert agg['width_whiplash']['pairs'] == 2
    assert agg['ticket_hygiene']['delivered.DUPLICATE_NORMALIZED'] == 0


def test_old_keys_unchanged():
    r = nb.race([1, 2, 3], ROLES, [], [T('EXACTA', 1, 2)])
    for k in ('actual_combination', 'role_horses', 'order_uncertainty', 'head_continuity', 'full_mec_observed'):
        assert k in r
    assert r['actual_combination']['EXACTA']['terminal'] == 'PURCHASED'
    assert nb.whiplash([r])['pairs'] == 0
