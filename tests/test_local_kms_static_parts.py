from runtime.local_autopilot import review as rv


def test_kms_role_capture_with_selectivity():
    # 10頭立て、W 2頭・P2 3頭・P3 4頭。1着=W、2着=P2、3着=P3 → 16*8/9 + 13*7/9 + 11*6/9
    ranking = list(range(1, 11))
    roles = {1: ['W'], 2: ['W', 'P2'], 3: ['P2'], 4: ['P2'], 5: ['P3'], 6: ['P3'], 7: ['P3'], 8: ['P3']}
    r = rv.kms_static_parts(ranking, roles, [1, 3, 5])
    assert r['role_40'] == round(16 * 8 / 9 + 13 * 7 / 9 + 11 * 6 / 9, 2)
    assert r['rank_20'] == round(9 * 1 + 6 * 7 / 9 + 5 * 5 / 9, 2)
    assert r['sel'] == {'W': round(8 / 9, 3), 'P2': round(7 / 9, 3), 'P3': round(6 / 9, 3)}


def test_kms_multi_role_takes_best_and_all_horses_role_zero():
    ranking = [1, 2, 3, 4]
    # 2着の馬 2 は W と P2 の両方 → P2 の 13*SEL を採る（二重加点しない）
    roles = {1: ['W'], 2: ['W', 'P2']}
    r = rv.kms_static_parts(ranking, roles, [1, 2, 4])
    assert r['role_40'] == round(16 * 2 / 3 + 13 * 3 / 3, 2)
    # 全頭を P3 にすると SEL=0 → 3着捕捉の得点も0
    r2 = rv.kms_static_parts(ranking, {h: ['P3'] for h in ranking}, [1, 2, 3])
    assert r2['role_40'] == 0.0
    assert rv.kms_static_parts([1], {}, [1]) is None
    assert rv.kms_static_parts(ranking, roles, [1, 2]) is None
