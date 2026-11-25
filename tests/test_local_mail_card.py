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
