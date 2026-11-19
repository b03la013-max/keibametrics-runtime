from runtime.local_autopilot.forward import robustness


def test_guardrails():
    rows = [{'eff': 600, 'pay': 0}, {'eff': 600, 'pay': 300}, {'eff': 0, 'pay': 0},
            {'eff': 600, 'pay': 0}, {'eff': 600, 'pay': 3000}, {'eff': 600, 'pay': 1200}]
    o = robustness(rows)
    assert o['bet_races'] == 5 and o['hit_races'] == 3
    assert o['pfs_without_top1'] == round(100 * 1500 / 3000, 1)
    assert o['pfs_without_top2'] == 10.0 and o['pfs_without_top3'] == 0.0
    assert o['max_loss_streak'] == 3          # 0, 300(<600), [eff0 skipped], 0
    assert o['median_race_pfs'] == 50.0
    assert o['any_hit_but_loss_rate'] == round(1 / 3, 3)


def test_empty():
    o = robustness([])
    assert o['pfs_without_top1'] is None and o['median_race_pfs'] is None and o['any_hit_but_loss_rate'] is None


def test_leave_one_day_out():
    rows = [{'day': '2026-11-10', 'eff': 1000, 'pay': 5000},
            {'day': '2026-11-11', 'eff': 1000, 'pay': 0},
            {'day': '2026-11-12', 'eff': 1000, 'pay': 200}]
    lo = robustness(rows)['leave_one_day_out']
    assert lo['days'] == 3 and lo['min_pfs'] == 10.0 and lo['max_pfs'] == 260.0
    assert lo['most_dependent_day'] == '2026-11-10' and lo['crosses_100'] is True
    one = robustness([{'day': 'd', 'eff': 100, 'pay': 0}])['leave_one_day_out']
    assert one['days'] == 1 and one['min_pfs'] is None and one['crosses_100'] is False
