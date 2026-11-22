"""B2 n268 市場ミラーとの差（Drive 精読 2026-11-23 リメイク版#11、証拠のみ）。"""
from runtime.local_autopilot import robustness as R


def T(bt, sel, stake=100):
    return {'bet_type': bt, 'selection': sel, 'stake': stake}


PAY = {'TRIO': {'2-4-9': 1190}, 'TRIFECTA': {'2-4-9': 7140}}


def test_mirror_swaps_model_rank_k_for_popularity_rank_k():
    # 予測順 9,2,4,7 ／ 人気順 2,4,9,7 → 9→2, 2→4, 4→9
    m = R.market_mirror([T('TRIO', [9, 2, 7]), T('TRIFECTA', [9, 2, 4])], PAY, [9, 2, 4, 7], [2, 4, 9, 7])
    assert m['payout'] == 0                    # 実績：三連複 9-2-7・三連単 9→2→4 とも外れ
    assert m['mirror_payout'] == 7140          # ミラー：三連単 2→4→9 が的中、三連複 2-4-7 は外れ
    assert m['stake'] == 200 and m['same_as_market'] is False


def test_unmapped_horse_gives_none_and_identity_mapping_flagged():
    assert R.market_mirror([T('TRIO', [2, 4, 11])], PAY, [2, 4, 9], [2, 4, 9]) is None
    m = R.market_mirror([T('TRIO', [2, 4, 9])], PAY, [2, 4, 9], [2, 4, 9])
    assert m['payout'] == m['mirror_payout'] == 1190 and m['same_as_market'] is True


def test_race_and_aggregate_carry_mirror_with_ci_and_without_best():
    a = R.race([T('TRIO', [2, 4, 9])], [2, 4, 9], PAY, mirror={'model_order': [2, 4, 9, 7], 'pop_order': [7, 2, 4, 9]})
    b = R.race([T('TRIO', [1, 3, 5])], [2, 4, 9], PAY, mirror={'model_order': [1, 3, 5], 'pop_order': [2, 4, 9]})
    assert a['market_mirror']['mirror_payout'] == 0 and b['market_mirror']['mirror_payout'] == 1190
    s = R.aggregate([a, b])['market_mirror']
    assert s['races'] == 2 and s['pfs'] == 595.0 and s['mirror_pfs'] == 595.0 and s['delta'] == 0.0
    lo, hi = s['delta_ci95']
    assert lo <= s['delta'] <= hi
    assert s['delta_without_best'] == -1190.0  # 実績の最高払戻 R を除くと b だけ
    assert 'Δ' in R.line(R.aggregate([a, b]))
    assert R.race([T('TRIO', [2, 4, 9])], [2, 4, 9], PAY)['market_mirror'] is None
