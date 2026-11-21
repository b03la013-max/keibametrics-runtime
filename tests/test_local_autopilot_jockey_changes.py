"""Isolated, no-network regressions for announced rider changes on LOCAL PAPER cards."""
from runtime.local_autopilot.rakuten import parse_card, parse_jockey_changes


def card(no=4, name="スピードソルジャー", notice="", anchored=False):
    rider = ('<a href="/jockey/detail/JOCKEYID/001234">井上瑛太</a>'
             if anchored else '<span>岡遼太郎</span>')
    return (
        '<html><div class="raceInformation">' + notice + '</div>'
        '<tbody class="raceCard">'
        '<tr class="box1 active">'
        f'<td class="number">{no}</td>'
        f'<td class="name"><span class="mainHorse"><a href="/horse">{name}</a></span></td>'
        f'<td class="profile"><span>牡7</span>{rider}<span>57.0</span></td>'
        '</tr></tbody></html>'
    )


def test_kaw_11_15_koc11_explicit_rider_change_repaired():
    html = card(notice='<p>4番 <strong>騎手変更</strong> 井上瑛太→岡遼太郎</p>')
    assert parse_jockey_changes(html) == {4: ('井上瑛太', '岡遼太郎')}
    active, excluded = parse_card(html)
    assert len(active) == 1 and not excluded
    assert active[0]['horse_no'] == 4
    assert active[0]['current_jockey'] == '岡遼太郎'
    assert active[0]['jockey_change_from'] == '井上瑛太'


def test_saga11_number9_change_separately_from_runner_text():
    html = card(no=9, name="ニシノヒンメル",
                notice='<div>9番 騎手変更 田中純→出水拓人</div>')
    active, _ = parse_card(html)
    assert active[0]['current_jockey'] == '出水拓人'


def test_do_not_infer_jockey_when_notice_is_absent():
    active, _ = parse_card(card())
    assert active[0]['current_jockey'] is None
    assert 'jockey_change_from' not in active[0]


def test_explicit_notice_overrides_old_anchor_without_leaking_to_other_number():
    html = card(anchored=True, notice='<div>4番 騎手変更 井上瑛太→岡遼太郎</div>')
    active, _ = parse_card(html)
    assert active[0]['current_jockey'] == '岡遼太郎'
    html = card(anchored=True, notice='<div>9番 騎手変更 田中純→出水拓人</div>')
    active, _ = parse_card(html)
    assert active[0]['current_jockey'] == '井上瑛太'


def test_do_not_consume_announcement_outside_race_header():
    html = card() + '<div>4番 騎手変更 井上瑛太→岡遼太郎</div>'
    assert parse_jockey_changes(html) == {}
