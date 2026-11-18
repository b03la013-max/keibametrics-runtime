from runtime.local_autopilot import role_shadow as rs


def test_exacta_same_budget_keeps_point_count_and_skips_same_horse():
    c = rs.exacta_same_budget([3, 2, 5, 1], [3, 2, 5, 1, 4, 6], 15)
    assert len(c) == 15 and all(a != b for a, b in c)
    assert [a for a, _ in c].count(3) == 4 and [a for a, _ in c].count(1) == 3


def test_summarize_counts():
    rows = [{'win_in_W': False, 'win_in_W_plus': True, 'added_heads': 1, 'second_in_P2': True, 'second_in_P2_place': True,
             'market': {'exacta_points': 15, 'exacta_signed_payout': 0,
                        **{c: {'win_in_W': True, 'second_in_P2': True, 'added_heads': 1, 'added_seconds': 0,
                               'exacta_payout': 900} for c in ('C18', 'C19', 'C20')}}}]
    s = rs.summarize(rows)
    assert s['C16']['rescued'] == 1 and s['C18']['win_in_W_cand'] == 100.0 and s['C18']['exacta_pfs_cand'] == 60.0
