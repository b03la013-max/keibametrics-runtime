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
