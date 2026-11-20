from runtime.local_autopilot import exposure as ex
from runtime.local_autopilot import ticket_tree as tt


def test_directional_exposure_and_zero():
    roles = {'W': [4, 7], 'P2': [2], 'P3': [9]}
    tickets = [('馬単', tt.parse('馬単', '4→2,7')), ('三連複', tt.parse('三連複', '2-4-7'))]
    a = ex.audit(roles, tickets)
    assert a['exposure'][4]['head'] == 2 and a['exposure'][7]['second'] == 1
    assert a['exposure'][2]['unordered'] == 1
    assert a['global_zero'] == [{'no': 9, 'role': 'P3'}]
    assert a['w_without_head'] == [7]
    assert a['pair_trio_gaps'] == []          # no 三連単 bought → nothing to intersect
    assert a['hub']['no'] == 4 and a['hub']['share'] == 1.0
    assert a['extreme_hub']


def test_pair_trio_gap_only_when_trifecta_bought():
    roles = {'W': [1], 'P2': [2], 'P3': [3]}
    tickets = [('馬単', [(1, 2)]), ('三連複', [(1, 2, 3)]), ('三連単', [(1, 3, 2)])]
    a = ex.audit(roles, tickets)
    assert a['pair_trio_gaps'] == [(1, 2, 3)]
    assert not a['extreme_hub']               # only one W
    s = ex.line(a)
    assert '1→2→3' in s and '全券種0：なし' in s


def test_roles_from_order_and_no_tickets():
    order = [{'no': 5, 'role': '1着候補'}, {'no': 3, 'role': '2着候補'}, {'no': 8, 'role': '×'}]
    r = ex.roles_from_order(order)
    assert r == {'W': [5], 'P2': [3], 'P3': []}
    a = ex.audit(r, [])
    assert a['hub'] is None and len(a['global_zero']) == 2
    assert '検算のみ' in ex.line(a)


def test_trifecta_monoculture():
    roles = {'W': [1, 2], 'P2': [3], 'P3': [4]}
    a = ex.audit(roles, [('三連単', [(1, 3, 4), (3, 1, 4), (1, 4, 3)])])
    assert a['tri_monoculture'] == [1, 3, 4]
    assert '三連単の全点に同じ馬' in ex.line(a)
    b = ex.audit(roles, [('三連単', [(1, 3, 4), (2, 3, 5)])])
    assert b['tri_monoculture'] == [3]
