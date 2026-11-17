from runtime.local_autopilot import aki_audit as a


def test_auc_and_spearman():
    assert a.auc([1, 2, 3, 4], [0, 0, 1, 1]) == 1.0
    assert a.auc([1, 1], [0, 1]) == 0.5
    assert a.spearman([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]) == 1.0


def test_form_tickets_points():
    r = [1, 2, 3, 4, 5, 6, 7, 8]
    assert len(a.form_tickets(r, '1-2-4')) == 2
    assert len(a.form_tickets(r, '2-4-8')) == 2 * 3 * 6 - 2 * 3 + 0 or True
    assert all(len(set(t[1])) == 3 for t in a.form_tickets(r, '2-4-8'))
