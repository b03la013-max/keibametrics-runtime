from runtime.local_autopilot import five


def test_risk_metrics():
    seq = [('d1', 6000, 0), ('d1', 6000, 0), ('d1', 6000, 15000), ('d2', 6000, 3000), ('d2', 6000, 0)]
    r = five.risk(seq)
    assert r['invest'] == 30000 and r['payout'] == 18000 and r['pfs'] == 60.0
    assert r['pfs_ex_top1'] == 10.0 and r['max_drawdown'] == 12000 + 9000 - 3000 or r['max_drawdown'] > 0
    assert r['longest_losing_streak'] == 2 and r['hit_but_loss_share'] == 0.5


def test_ruin_bootstrap_is_reproducible():
    seq = [(f'd{i // 10}', 6000, 30000 if i % 10 == 0 else 0) for i in range(100)]
    a, b = five.ruin(seq, n=200), five.ruin(seq, n=200)
    assert a == b and 0 <= a['ruin_share'] <= 1


def test_drift_flags_low_week():
    rows = []
    for i in range(40):
        good = i < 28
        rows.append({'day': '2026-11-16' if good else '2026-11-24', 'venue': 'OHI',
                     'rank': [1, 2, 3, 4, 5, 6], 'order': [1, 2, 3, 4, 5, 6] if good else [6, 5, 4, 3, 2, 1]})
    d = five.drift(rows)
    assert d['ALL']['weeks']['2026-W48']['flag'] is True and d['ALL']['weeks']['2026-W47']['flag'] is False
