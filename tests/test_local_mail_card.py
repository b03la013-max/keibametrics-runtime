import pytest

pytest.importorskip('PIL')
from runtime.local_autopilot import mail_card, run  # noqa: E402

REV = {'prediction': {'ranking': [{'no': 3, 'name': 'アオ', 'mark': '◎', 'role': '1着候補', 'p_win': 0.3},
                                  {'no': 5, 'name': 'ミドリ', 'mark': '○', 'role': '2着候補', 'p_win': 0.2},
                                  {'no': 1, 'name': 'キ', 'mark': '', 'role': '×', 'p_win': 0.01}],
                      'tickets': [{'k': '三連単', 'pt': 12}], 'race_cond': {'distance': 1400, 'going': '良'}}}


def _font_ok():
    try:
        mail_card._font(20)
        return True
    except OSError:
        return False


def test_paper_card_renders_and_link(tmp_path, monkeypatch):
    if not _font_ok():
        pytest.skip('no CJK font')
    monkeypatch.setattr(mail_card, 'publish', lambda png, rp, tok, repo, branch='local-autopilot-data':
                        f'https://raw.example/{rp}' if png.exists() and png.stat().st_size > 1000 else None)
    line = run._mail_card(mail_card.paper_card(REV, '大井1R', '15:00', '14:57', '直前版'), '2026-11-25', 'OHI_01.r2.paper')
    assert line.startswith('![大井1R](https://raw.example/output/2026-11-25/cards/OHI_01.r2.paper.png)')


def test_card_failure_never_blocks(monkeypatch):
    monkeypatch.setattr(mail_card, 'render', lambda *a: (_ for _ in ()).throw(OSError('NO_CJK_FONT')))
    assert run._mail_card({'title': 'x'}, '2026-11-25', 'x') == ''
    monkeypatch.setenv('KM_LOCAL_MAIL_CARD', '0')
    assert run._mail_card({'title': 'x'}, '2026-11-25', 'x') == ''


def test_formal_card_roles():
    sm = {'marks': {'3': '◎', '5': '○'}, 'roles': {'3': ['W'], '5': ['P2']}, 'ranking': ['3', '5', '1'],
          'tickets': [{'bet_type': 'TRIFECTA'}, {'bet_type': 'EXACTA'}, {'bet_type': 'TRIFECTA'}]}
    c = mail_card.formal_card(sm, {3: {'name': 'アオ'}}, '大井1R', '15:00', '14:57')
    assert [h['no'] for h in c['horses']] == [3, 5] and dict(c['tickets']) == {'三連単': 2, '馬単': 1}
    assert c['invest'] == 300 and c['kind'] == 'FORMAL'


def test_jra_and_ban_cards():
    fin = {'scheduled_post_at': '2026-11-23T16:05:00+09:00', 'prediction_cutoff': '2026-11-23T16:00:00+09:00',
           'final_prediction_package': {'ranking': ['1', '8', '4'], 'roles': {'1': ['W', 'P2'], '8': ['P2'], '4': []}},
           'final_ticket': {'tickets': [{'bet_type': 'EXACTA'}, {'bet_type': 'TRIO'}], 'total_investment': 300}}
    env = {'artifact': {'jra_official_race_card_detail': {'race_context': {'venue_name': '東京', 'race_no': 12,
           'surface': '芝', 'distance_m': 1600, 'going': '良'}, 'runners': [{'horse_no': 1, 'horse_name': 'A', 'frame_no': 1}]}}}
    c = mail_card.jra_card(fin, env)
    assert c['system'] == 'JRA' and c['title'] == '東京12R' and c['invest'] == 300 and [h['no'] for h in c['horses']] == [1, 8]
    rec = {'race': {'no': 12, 'post': '2026-11-23T20:05:00+09:00'}, 'header': {'race_no': 12, 'going': '2.4%'},
           'evaluation': {'marks': {'6': '◎', '4': '穴'}, 'rows': [
               {'no': 6, 'name': 'X', 'win_rank': 1, 'role_w': 'STRONG'}, {'no': 4, 'name': 'Y', 'win_rank': 2, 'role_p3': 'BUY'},
               {'no': 2, 'name': 'Z', 'win_rank': 3}]},
           'tickets': {'trio': [[1, 2, 6]], 'exact': [[6, 1, 2], [6, 2, 1]], 'stake': 300, 'formality': 'FORMAL'}}
    b = mail_card.ban_card(rec)
    assert b['system'] == 'BAN' and [h['role'] for h in b['horses']] == ['1着候補', '3着候補'] and b['invest'] == 300
    assert dict(b['tickets']) == {'三連複': 1, '三連単': 2} and b['marks'][0] == ('◎', 6)


def test_jra_delivery_card_never_blocks(tmp_path):
    import sys
    sys.path.insert(0, 'runtime')
    import jra_owner_issue_delivery as j
    assert j.card('KM-JRA-TKY-20261123-R12', tmp_path / 'missing.json') == ''


def test_jra_card_marks_follow_the_signed_static_ranking():
    final = {'scheduled_post_at': '2026-11-29T15:40:00+09:00', 'prediction_cutoff': '2026-11-29T15:30:00+09:00',
             'final_prediction_package': {'ranking': ['7', '3', '12', '1', '5'],
                                          'roles': {'7': ['W', 'P2', 'P3'], '3': ['W', 'P2', 'P3'], '12': ['P2', 'P3'],
                                                    '1': ['P3'], '5': []}},
             'final_ticket': {'tickets': [{'bet_type': 'EXACTA', 'selection': [7, 3]}], 'total_investment': 100}}
    env = {'artifact': {'jra_official_race_card_detail': {
        'race_context': {'venue_name': '東京', 'race_no': 12, 'surface': '芝', 'distance_m': 2400},
        'runners': [{'horse_no': n, 'horse_name': f'H{n}'} for n in (1, 3, 5, 7, 12)]}}}
    c = mail_card.jra_card(final, env)
    assert c['marks'][:3] == [('◎', 7), ('○', 3), ('▲', 12)] and ('△', 1) in c['marks']
    assert all(no != 5 for _, no in c['marks'])  # △ only for role holders
    assert {h['no']: h['mark'] for h in c['horses']} == {7: '◎', 3: '○', 12: '▲', 1: '△'}
