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
