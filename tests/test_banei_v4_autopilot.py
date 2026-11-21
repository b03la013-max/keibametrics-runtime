import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'runtime', 'banei_autopilot'))
import source  # noqa: E402
import run  # noqa: E402


def _row(no, name, load, bw, chg, pop, odds):
    start = ('<td class="race1"><div><span class="place">3</span></div>'
             '<span>帯広 26.10.26</span><br><span>Ｂ１－２</span><br><span>特別</span><br>'
             f'<span>200ダ {pop}人</span><br><span>西謙一 {load - 10}</span><br>'
             '<span>2:03.5 (10.2)</span><br><span>1048k 3番</span></td>')
    return (f'<tr class="box{no} odd"><td class="number">{no}</td>'
            f'<td class="name"><span class="mainHorse"><a href="#">{name}</a></span><div class="append">'
            f'<span class="rate">{odds}（{pop}人気）</span></div></td>'
            f'<td class="profile">牡5<br><a href="/jockey/detail/JOCKEYID/1">鈴木恵</a><br>{load}<br>西弘美</td>'
            f'<td class="weight">1030 | 1060</td><td class="weightDistance">{bw}<br>{chg:+d}</td>{start}</tr>')


def _card(n=8):
    rows = ''.join(_row(i, f'ウマ{i}', 700 - (20 if i == 5 else 0), 1050 + i, 4 - i, i, f'{1.5 + i:.1f}') for i in range(1, n + 1))
    return f'<html>馬場水分 1.4%<tbody class="raceCard">{rows}</tbody></html>'


def test_parse_card_ban():
    card = source.parse_card_ban(_card())
    assert len(card) == 8 and card[0]['load'] == 700 and card[4]['load'] == 680
    assert card[0]['body_weight'] == 1051 and card[0]['body_delta'] == 3 and card[0]['pop'] == 1
    s = card[0]['starts'][0]
    assert s['load'] == 690 and s['sec'] == 123.5 and s['body_weight'] == 1048 and s['finish'] == 3
    assert source.moisture_from_header(_card()) == 1.4


def test_speed_index_monotone_in_time():
    a = source.speed_index(120.0, 700, 1.5, 11, 'B1', False)
    b = source.speed_index(130.0, 700, 1.5, 11, 'B1', False)
    assert a > b


class FakeClient:
    def __init__(self, top):
        self.top = top

    def get(self, path):
        return self.top


class FakeReader:
    def __init__(self, day):
        d = day.replace('-', '')
        self.client = FakeClient(f'race_card/list/RACEID/{d}0303000001')
        self.d = d

    def card_page(self, rid):
        menu = ''.join(f'<a href="/RACEID/{self.d}03030000{i:02d}"><span class="num">{i}R</span>'
                       f'<span class="time">{9 + i}:00</span></a>' for i in range(1, 3))
        return '<ul class="raceNumber">' + menu.replace('<a href="/', '<a href="/race_card/list/') + '</ul>' + _card()

    def result_page(self, rid):
        return ''


def test_tick_predicts_inside_window(tmp_path, monkeypatch):
    day = '2026-11-21'
    out = tmp_path / day
    out.mkdir()
    rd = FakeReader(day)
    q = run.discover(rd, day, out)
    assert len(q['races']) == 2
    key = '01'
    post = datetime.fromisoformat(q['races'][key]['post'])
    monkeypatch.setattr(run, 'now_jst', lambda: post - timedelta(minutes=20))
    q = run.tick(day, out, rd, {})
    r = q['races'][key]
    assert r['state'] == 'PREDICTION_COMPLETE' and r['points'] <= 30
    assert r['formality'] == 'REFERENCE-RENDERED'           # no キンタロー feed -> not FORMAL
    assert (out / 'R01.md').read_text().count('三連複') >= 1


def test_kintaro_sample_if_present():
    import pytest
    p = os.environ.get('KM_BAN_KINTARO_SAMPLE')
    if not p or not os.path.exists(p):
        pytest.skip('no local キンタロー sample (PDFs are not committed)')
    import kintaro
    d = kintaro.parse(p)
    assert d and all('grades' in v for v in d.values())
    assert any(x['barrier_sec'] for v in d.values() for x in v['past'])


def test_sbo_ban_table_and_blend():
    import engine
    html = ('<p>馬場: 2.7%</p><table id="table"><tr><th>馬番</th></tr>'
            '<tr><td>1</td><td>A</td><td>t</td><td>715</td><td>j</td><td></td><td>92(5)</td><td>62(4)</td><td>81</td></tr>'
            '<tr><td>2</td><td>B</td><td>t</td><td>705</td><td>j</td><td></td><td>-(0)</td><td>70(1)</td><td>75</td></tr></table>')
    t, m = source.parse_sbo_ban(html)
    assert m == 2.7 and t[1] == {'recent': 92.0, 'track': 62.0, 'avg': 81.0, 'n_recent': 5, 'n_track': 4}
    assert t[2]['recent'] is None
    idx, src = engine.base_indices({'idx_sbo': t[1], 'own_past': [{'idx': 80, 'moisture': 2.7}]}, 2.7)
    assert src['recent'] == 'SBO+OWN' and idx['recent'] == round(0.3 * 92 + 0.7 * 80, 2)
    idx, src = engine.base_indices({'idx_sbo': t[1]}, 2.7)
    assert idx == {'recent': 92.0, 'track': 62.0, 'avg': 81.0} and set(src.values()) == {'SBO'}


def test_cci_band():
    assert source.cci_band('上位争い', '本来の姿に戻って') == 'VERY_STRONG'
    assert source.cci_band('ここも様子見', '追走いっぱい') == 'CAUTION'
    assert source.cci_band('障害次第') == 'NEUTRAL'          # conditional is not weak (v2.3 第63条)
    assert source.cci_band(None) is None


def test_nar_good_bw_range_fallback_and_pct(tmp_path):
    import sys
    sys.path.insert(0, 'runtime/banei_autopilot')
    import source
    (tmp_path / 'ban_racelist.csv').write_text(
        '﻿競馬場,競走年月日,レース番号,レース名,条件,馬場\n帯広ば,20261001,1,C1-1,一般,1.5\n帯広ば,20261008,1,C1-1,一般,2.0\n', encoding='utf-8')
    (tmp_path / 'ban_horselist.csv').write_text(
        '﻿競馬場,競走年月日,レース番号,馬名,負担重量,馬体重,着順,タイム\n'
        '帯広ば,20261001,1,テスト,700,1000,2,2000\n帯広ば,20261008,1,テスト,700,1030,1,2100\n', encoding='utf-8')
    hist = source.nar_history(tmp_path)
    assert hist['テスト'][0]['finish'] == 1 and hist['テスト'][0]['body_weight'] == 1030
    card = [{'no': 1, 'name': 'テスト', 'starts': [], 'good_bw_range': None, 'body_weight': 1040, 'body_delta': 10}]
    h = source.build_horses(card, 2.0, '2026-11-21', hist, {}, 1)[0]
    assert h['good_bw_range'] == (1000, 1030) and h['good_bw_src'] == 'NAR'
    assert h['body_delta_pct'] == round(100 * 10 / 1030, 2) and h['nar_starts'] == 2


def test_check10_keeps_rev1_when_nothing_changes_and_revises_on_change(tmp_path, monkeypatch):
    day = '2026-11-21'
    out = tmp_path / day
    out.mkdir()
    rd = FakeReader(day)
    q = run.discover(rd, day, out)
    post = datetime.fromisoformat(q['races']['01']['post'])
    monkeypatch.setattr(run, 'now_jst', lambda: post - timedelta(minutes=20))
    q = run.tick(day, out, rd, {})
    q['races']['01']['delivered'] = 'x'                       # no issue env in tests
    run.dump(out / 'queue.json', q)
    monkeypatch.setattr(run, 'now_jst', lambda: post - timedelta(minutes=9))
    q = run.tick(day, out, rd, {})
    c = q['races']['01']['check10']
    assert c['decision'].startswith('KEEP_REVISION_1') and q['races']['01'].get('effective') is None
    # a scratch before post -> Revision 2 (Rev1 file kept)
    q['races']['01'].pop('check10')
    run.dump(out / 'queue.json', q)
    orig = rd.card_page
    rd.card_page = lambda rid: orig(rid).replace('<td class="number">3</td>', '<td class="number">取消</td>')
    q = run.tick(day, out, rd, {})
    r = q['races']['01']
    assert r['check10']['decision'].startswith('REVISION_2') and r['effective'] == 'rev2'
    assert '出走馬の変更（取消・除外）' in r['check10']['reasons']
    assert (out / 'R01.json').exists() and (out / 'R01.rev2.json').exists()
