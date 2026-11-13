"""PAPER market-provenance regression: text must match actually available odds."""
from runtime.local_autopilot import run


def test_model_only_when_all_market_odds_are_missing():
    rows = [{'p_market': None}, {'p_market': None}]
    msg = run.probability_source_note(rows)
    assert 'softmaxのみ' in msg
    assert '50:50合成' not in msg
    assert '市場確率なし' in msg


def test_partial_market_coverage_is_not_claimed_as_full_blend():
    rows = [{'p_market': 0.6}, {'p_market': None}, {'p_market': None}]
    msg = run.probability_source_note(rows)
    assert '1/3頭' in msg
    assert '100%未保証' in msg


def test_full_market_coverage_is_labelled_fifty_fifty():
    rows = [{'p_market': 0.6}, {'p_market': 0.4}]
    msg = run.probability_source_note(rows)
    assert '50:50合成' in msg
    assert 'のみ' not in msg


def test_render_never_claims_odds_acquired_when_all_missing():
    r = {
        'mark': '◎', 'no': 1, 'name': 'test horse', 'jockey': None,
        'win': None, 'pop': '', 'TPIF': 52, 'SRI': 52, 'EVI': 52,
        'NCI': 52, 'T3I': 52, 'F3S': 52, 'OPI': 52,
        'p_win': 1.0, 'p_market': None, 'role': '1着候補', 'flags': [],
    }
    res = {
        'aki': {'W': 0, 'P': 0, 'ASI': 0, 'RSI': 0, 'katai': 0, 'total': 0,
                'type': 'A', 'form': '1-2-4'},
        'rows': [r], 'order': [r], 'pace': '不明', 'race_type': '混合型',
        'wci': 0, 'fuan': 0, 'fuan_reasons': [], 'reversal': 0,
        'gate': '不安あり', 'tan_ev': None, 'quad': 4, 'checks': {}, 'tickets': [],
    }
    race = {'venue_name': '佐賀', 'race_no': 1,
            'post_current': '2026-11-14T15:20:00+09:00', 'distance': 900}
    text = run.render(race, res, '朝版', '2026-11-13T21:28:00+09:00')
    assert '出馬表取得 21:28／単勝オッズ 0/1頭' in text
    assert 'softmaxのみ' in text
    assert '50:50合成' not in text
    assert '100%' in text  # display stays unchanged, only provenance is repaired
    assert '| UNKNOWN（未取得） |' in text
    assert '騎手情報未取得：1番test horse' in text
    assert '役割・券面は暫定' in text
    r['jockey'] = '確認済騎手'
    known = run.render(race, res, '朝版', '2026-11-13T21:28:00+09:00')
    assert '| 確認済騎手 |' in known
    assert '騎手情報未取得' not in known
