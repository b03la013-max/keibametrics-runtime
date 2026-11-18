from runtime.local_autopilot import ticket_tree as tt


def test_wide_axis_and_partners():
    lines, pts = tt.render('ワイド', tt.parse('ワイド', '10-6 / 10-9'))
    assert lines == ['ワイド', '軸', '└─ 10', '相手', '├─ 6', '└─ 9'] and pts == 2


def test_exacta_columns_keep_prediction_order_and_drop_same_horse():
    lines, pts = tt.render('馬単', tt.parse('馬単', '4→2,6,10'))
    assert lines == ['馬単（1着固定）', '1着', '└─ 4', '2着', '├─ 2', '├─ 6', '└─ 10'] and pts == 3
    lines, pts = tt.render('馬単', [(1, 6), (6, 1), (1, 7), (6, 7)])
    assert pts == 4 and '1着' in lines and '2着' in lines


def test_trio_formation_points_are_real_points():
    combos = tt.parse('三連複', '1-6-9 / 1-8-9 / 1-4-9 / 1-6-8 / 1-4-6')
    lines, pts = tt.render('三連複', combos)
    assert pts == 5 and lines[1] == '1列目'
    exp = tt._expand('三連複', [[1], [6, 9], [1, 6, 9, 8, 4]])
    assert exp == {tuple(sorted(c)) for c in combos}


def test_non_formation_trifecta_is_grouped_vertically_and_no_circled_digits():
    lines, pts = tt.render('三連単', [(1, 10, 4), (1, 10, 6), (1, 4, 10), (6, 1, 10)])
    text = '\n'.join(lines)
    assert pts == 4 and '1着 1' in text and '2着 10' in text
    assert not any(ch in text for ch in '①②③④⑤⑥⑦⑧⑨⑩') and '→' not in text and '-' not in text.replace('─', '')


def test_block_footer():
    txt, total = tt.block([('単勝', [(4,)], None), ('ワイド', [(4, 2), (4, 6)], None)])
    assert total == 3 and '合計　3点（300円）' in txt and 'ペーパー' in txt and '算出不可' in txt
