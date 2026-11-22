"""B2 回収の頑健性の追加列（Drive 精読 2026-11-23）: evidence-only columns computed from delivered tickets."""
from runtime.local_autopilot import robustness as R


def T(bt, sel, tier=None, stake=100):
    return {'bet_type': bt, 'selection': sel, 'stake': stake, 'tier': tier}


PAY = {'TRIO': {'2-4-9': 1190}, 'TRIFECTA': {'2-4-9': 7140}, 'EXACTA': {'2-4': 900}}


def test_cross_bet_redundancy_counts_stake_outside_the_primary_bet_type():
    r = R.race([T('TRIO', [2, 4, 9]), T('TRIFECTA', [2, 4, 9]), T('TRIFECTA', [4, 2, 9]), T('TRIO', [2, 4, 7])],
               [2, 4, 9], PAY)
    c = r['cross_bet_redundancy']
    assert c['skeletons_in_two_or_more_bet_types'] == 1
    assert c['extra_stake'] == 200           # 三連単2点が三連複と同じ組
    assert c['extra_share'] == 0.5


def test_set_order_split_and_payout_by_bet_type():
    both = R.race([T('TRIO', [2, 4, 9]), T('TRIFECTA', [2, 4, 9])], [2, 4, 9], PAY)
    assert both['set_order'] == 'BOTH'
    assert both['by_bet_type']['TRIO']['payout'] == 1190 and both['by_bet_type']['TRIFECTA']['payout'] == 7140
    set_only = R.race([T('TRIO', [2, 4, 9]), T('TRIFECTA', [4, 2, 9])], [2, 4, 9], PAY)
    assert set_only['set_order'] == 'SET_ONLY'
    assert R.race([T('EXACTA', [2, 4])], [2, 4, 9], PAY)['set_order'] == 'NOT_BOUGHT'
    assert R.race([T('TRIO', [1, 4, 9])], [2, 4, 9], PAY)['set_order'] == 'NONE'


def test_low_payout_hit_but_loss_and_break_even_multiple():
    ts = [T('TRIO', [2, 4, 9])] + [T('TRIO', [1, 2, x]) for x in range(3, 18)]
    r = R.race(ts, [2, 4, 9], PAY)
    assert r['low_payout'] == {'break_even_multiple': 16.0, 'hit': True, 'hit_multiple': 11.9, 'hit_but_loss': True}


def test_protection_burden_only_when_every_ticket_has_a_tier():
    r = R.race([T('TRIO', [2, 4, 9], 'CORE'), T('TRIO', [1, 4, 9], 'PROTECTION')], [2, 4, 9], PAY)
    assert r['protection_burden_ratio'] == 0.5
    assert R.race([T('TRIO', [2, 4, 9], 'CORE'), T('TRIO', [1, 4, 9])], [2, 4, 9], PAY)['protection_burden_ratio'] is None


def test_aggregate_and_line_never_touch_tickets():
    ts = [T('TRIO', [2, 4, 9], 'CORE'), T('TRIFECTA', [2, 4, 9], 'PROTECTION')]
    before = [dict(t) for t in ts]
    rows = [R.race(ts, [2, 4, 9], PAY), R.race(ts, [1, 3, 5], {'TRIO': {'1-3-5': 500}}), None]
    assert ts == before
    a = R.aggregate(rows)
    assert a['races'] == 2 and a['hit_races'] == 1 and a['hit_but_loss_races'] == 0
    assert a['set_order'] == {'BOTH': 1, 'NONE': 1}
    assert a['by_bet_type']['TRIFECTA']['pfs'] == 3570.0
    assert a['evidence_only'] is True
    assert '回収の頑健性' in R.line(a)
    assert R.aggregate([None]) is None


def test_random_same_points_null_model():
    # 4頭立て（着順4頭）: 三連複 C(4,3)=4 通り、1点買えば期待払戻 = 1190/4
    r = R.race([T('TRIO', [2, 4, 9])], [2, 4, 9, 1], {'TRIO': {'2-4-9': 1190}})
    assert r['random_same_points'] == {'expected_payout': round(1190 / 4), 'field': 4}
    # 三連単 4*3*2=24 通り × 2点
    r2 = R.race([T('TRIFECTA', [2, 4, 9]), T('TRIFECTA', [4, 2, 9])], [2, 4, 9, 1], {'TRIFECTA': {'2-4-9': 7140}})
    assert r2['random_same_points']['expected_payout'] == round(2 / 24 * 7140)
    # 払戻表が無い券種があれば出さない
    assert R.race([T('EXACTA', [2, 4])], [2, 4, 9], {})['random_same_points']['expected_payout'] is None
    a = R.aggregate([r, r2])
    assert a['random_same_points']['races'] == 2
    assert a['random_same_points']['actual_pfs_same_races'] == round(100 * (1190 + 7140) / 300, 1)


def test_roughness_layers_pre_race_fav_odds_and_result_trio_payout():
    assert R.roughness(1.6, PAY) == {'pre_race': 'SOLID', 'fav_odds': 1.6, 'result': 'MID', 'trio_payout': 1190}
    assert R.roughness(3.0, {'TRIO': {'1-2-3': 800}})['pre_race'] == 'MID'
    assert R.roughness(4.0, {'TRIO': {'1-2-3': 800}})['result'] == 'LOW'
    assert R.roughness(5.2, {'TRIO': {'1-2-3': 25000}})[ 'pre_race'] == 'OPEN'
    assert R.roughness(None, {}) == {'pre_race': None, 'fav_odds': None, 'result': None, 'trio_payout': None}


def test_aggregate_splits_pfs_and_hit_but_loss_by_roughness_layer():
    ts = [T('TRIO', [2, 4, 9])] + [T('TRIO', [1, 2, x]) for x in range(3, 18)]
    a = R.race(ts, [2, 4, 9], PAY, fav_odds=1.5)              # SOLID, 的中赤字
    b = R.race([T('TRIO', [1, 4, 9])], [2, 4, 9], PAY, fav_odds=6.0)   # OPEN, 不的中
    agg = R.aggregate([a, b])
    pre = agg['by_roughness']['pre_race']
    assert pre['SOLID'] == {'races': 1, 'invest': 1600, 'payout': 1190, 'hit_races': 1, 'hit_but_loss_races': 1,
                            'pfs': 74.4, 'hit_but_loss_rate': 1.0}
    assert pre['OPEN']['pfs'] == 0.0 and pre['OPEN']['hit_but_loss_rate'] is None
    assert agg['by_roughness']['result']['MID']['races'] == 2
    assert '荒れ度' in R.line(agg)
    assert a['evidence_only'] is True
