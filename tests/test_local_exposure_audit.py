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


def test_trio_order_divergence():
    roles = {'W': [1], 'P2': [2, 5], 'P3': [3]}
    a = ex.audit(roles, [('馬単', [(1, 2)]), ('三連複', [(1, 2, 3), (1, 3, 5)])])
    assert a['trio_order_divergence'] == [(1, 5)]
    assert '1→5' in ex.line(a)
    b = ex.audit(roles, [('三連複', [(1, 3, 5)])])     # no ordered ticket at all → nothing to compare
    assert b['trio_order_divergence'] == []


def test_cell_coverage_fnb_v20():
    # 船橋 v2.0 第307・311条：W×P2 の並び（Expected Cell）と、馬単で買った並びの三連単3着の深さ
    roles = {'W': [4, 12], 'P2': [13], 'P3': [7]}
    tickets = [('馬単', [(12, 4), (4, 13)]), ('三連単', [(12, 4, 13), (12, 4, 7)])]
    a = ex.audit(roles, tickets)
    c = a['cells']
    assert c['expected'] == 4 and c['bought'] == 2
    assert c['missing'] == [(4, 12), (12, 13)]
    assert c['depth'][(12, 4)] == 2 and c['depth'][(4, 13)] == 0
    assert c['exacta_zero_depth'] == [(4, 13)]
    s = ex.line(a)
    assert '並び 2/4' in s and '4→12' in s and '三連単の3着が無い：4→13' in s
    assert ex.audit(roles, [('三連複', [(4, 7, 13)])])['cells'] is None   # no ordered ticket → no cell check


def test_marginal_contribution_ohi_v23():
    # 大井 v2.3 第326・329条：券ごとに「他の券に無いもの」を分類し、券種別の点数配分を出す（検算のみ）
    tickets = [('馬単', [(1, 2), (3, 1)]),
               ('三連複', [(1, 2, 4), (1, 2, 5)]),
               ('三連単', [(1, 2, 4), (1, 2, 6), (1, 4, 2), (2, 1, 4), (2, 4, 1), (4, 1, 2), (4, 2, 1)])]
    m = ex.marginal(tickets)
    lab = {(k, c): cls for k, c, cls in m['tickets']}
    assert lab[('馬単', (1, 2))] == 'STRUCTURAL_PROTECTION'      # 1→2 also first two of 三連単
    assert lab[('馬単', (3, 1))] == 'NEW_HEAD_PATH'              # 3 heads nothing else
    assert lab[('三連複', (1, 2, 4))] == 'REDUNDANT'             # all 6 orders bought as 三連単
    assert lab[('三連複', (1, 2, 5))] == 'NEW_SET'
    assert lab[('三連単', (1, 2, 6))] == 'NEW_THIRD'             # 1→2 known, {1,2,6} new
    assert lab[('三連単', (1, 2, 4))] == 'NEW_ORDER'             # {1,2,4} known from other tickets
    assert m['layer']['三連単'] == {'points': 7, 'share': round(7 / 11, 3)}
    assert sum(m['counts'].values()) == m['total'] == 11
    s = ex.marginal_line(m)
    assert '三連単 7点（64%）' in s and '他券で完全に重複 1' in s and '検算のみ' in s


def test_marginal_quinella_and_empty():
    m = ex.marginal([('馬連', [(1, 2), (3, 4)]), ('馬単', [(1, 2), (2, 1)])])
    lab = {(k, c): cls for k, c, cls in m['tickets']}
    assert lab[('馬連', (1, 2))] == 'REDUNDANT' and lab[('馬連', (3, 4))] == 'NEW_PAIR'
    assert ex.marginal([])['total'] == 0 and '券なし' in ex.marginal_line(ex.marginal([]))


def test_cross_pair_third_banei_v37():
    # 帯広 2026-09-06 7R：10→1 を馬単で買い、3 は 3→9→10 の頭／別の並びでは3着に使うのに 10→1→3 が無い
    roles = {'W': [10, 9], 'P2': [1], 'P3': [3, 5]}
    tickets = [('馬単', [(10, 1), (9, 10)]),
               ('三連単', [(10, 1, 9), (9, 10, 3), (10, 9, 5)])]
    c = ex.audit(roles, tickets)['cells']
    assert (10, 1, 3) in c['cross_pair_third'] and (10, 1, 5) in c['cross_pair_third']
    assert (9, 10, 5) in c['cross_pair_third'] and (9, 10, 3) not in c['cross_pair_third']
    assert all(h not in (a, b) for a, b, h in c['cross_pair_third'])
    assert '10→1→3' in ex.line(ex.audit(roles, tickets))
    # 3着候補がどの三連単でも3着に無いなら「補償の誤認」ではないので出さない
    d = ex.audit({'W': [1], 'P2': [2], 'P3': [7]}, [('馬単', [(1, 2)]), ('三連単', [(1, 2, 3)])])['cells']
    assert d['cross_pair_third'] == []


def test_hub_failure_sonoda_v28():
    # 園田 v2.8 第561条の型：40点中34点が同じ馬依存 → 点数が多くても1つの World
    roles = {'W': [3, 6, 5], 'P2': [1, 2], 'P3': [9]}
    tickets = [('三連単', [(6, 3, 1), (6, 3, 2), (6, 1, 2), (3, 6, 1), (5, 6, 1)]), ('馬単', [(3, 5), (6, 3)])]
    a = ex.audit(roles, tickets)
    hf = a['hub_failure']
    assert a['hub']['no'] == 6 and hf['hub'] == 6
    assert hf['points'] == 7 and hf['live_points'] == 1 and hf['dead_share'] == round(6 / 7, 3)
    assert hf['w_head_live'] == [3] and hf['w_dead'] == [5]
    s = ex.line(a)
    assert '6番が3着外なら残る点 1/7' in s and '他の1着候補：5' in s


def test_hub_failure_unordered_keeps_world_and_empty():
    roles = {'W': [1, 2], 'P2': [3], 'P3': []}
    a = ex.audit(roles, [('三連複', [(1, 2, 3), (2, 3, 4)]), ('馬単', [(1, 3)])])
    hf = a['hub_failure']
    assert hf['hub'] == 2 or hf['hub'] == 3
    assert ex.hub_failure(roles, [], 1) is None
    assert ex.audit(roles, [])['hub_failure'] is None


def test_quinella_one_way_and_p2_no_second_sonoda_v26():
    roles = {'W': [1, 2], 'P2': [3, 5], 'P3': [4]}
    tickets = [('馬連', [(1, 2), (1, 3)]), ('馬単', [(1, 2), (1, 3)]), ('三連単', [(1, 2, 5), (2, 1, 3)])]
    a = ex.audit(roles, tickets)
    assert a['quinella_one_way'] == []        # 1→2 and 2→1 both present (2→1 via 三連単)
    assert a['p2_no_second'] == [5]           # 5 only as a 三連単 third
    t2 = [('馬連', [(1, 2)]), ('馬単', [(2, 1)]), ('三連複', [(1, 2, 3)])]
    a2 = ex.audit(roles, t2)
    assert a2['quinella_one_way'] == [(2, 1)]
    assert a2['p2_no_second'] == [3]           # 3 only in 三連複 → never bought as a 2nd
    s = ex.line(a2)
    assert '2→1のみ' in s and '第430条' in s


def test_quinella_one_way_needs_ordered_tickets():
    roles = {'W': [1, 2], 'P2': [3], 'P3': []}
    a = ex.audit(roles, [('馬連', [(1, 2)]), ('三連複', [(1, 2, 3)])])
    assert a['quinella_one_way'] == [] and a['p2_no_second'] == []


def test_concentration_krs_v15_art85():
    c = ex.concentration([0.25, 0.25, 0.25, 0.25])
    assert abs(c['normalized_entropy_W'] - 1.0) < 1e-9 and abs(c['top1_share'] - 0.25) < 1e-9
    c2 = ex.concentration([0.7, 0.1, 0.1, 0.1, None])
    assert c2['n'] == 4 and abs(c2['top2_cumulative_share'] - 0.8) < 1e-9 and c2['normalized_entropy_W'] < 0.8
    assert ex.concentration([1.0]) is None
    s = ex.concentration_line(c2)
    assert '第85条' in s and '最上位 70%' in s and '閾値なし' in s
    assert '計算不可' in ex.concentration_line(None)
