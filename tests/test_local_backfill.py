import json

from runtime.local_autopilot import backfill as bf
from runtime.local_autopilot import rakuten as rk

RES = '''<div id="raceInfomation"><span class="racePlace">大井</span><span class="num">1</span>R
<h2>テスト</h2><dd class="distance">ダ1,200m</dd><dl><dt>ダ：</dt><dd>稍重</dd></dl></div>
天候：曇
<ul class="raceNumber"><a href="/race_performance/list/RACEID/202611102015120101">1R</a>
<a href="/race_performance/list/RACEID/202611102015120102">2R</a></ul>
<tbody class="record"><tr class="box1"><td class="order">1</td><td class="position">1</td><td class="number">3</td><td class="horse">A</td></tr>
<tr class="box2"><td class="order">2</td><td class="position">2</td><td class="number">1</td></tr>
<tr class="box3"><td class="order">3</td><td class="position">3</td><td class="number">2</td></tr></tbody>
<table summary="払戻金"><tr><th scope="row">単勝</th><td class="number">3</td><td class="money">250円</td></tr>
<tr><th scope="row">三連複</th><td class="number">1-2-3</td><td class="money">1,230円</td></tr></table>'''


class FakeClient:
    def __init__(self, pages):
        self.pages, self.calls = pages, []

    def get(self, path):
        self.calls.append(path)
        if path in self.pages:
            return self.pages[path]
        raise rk.SourceStop('HTTP_404:' + path)


class FakeReader:
    def __init__(self, pages):
        self.client = FakeClient(pages)


def test_backfill_discovers_and_parses(tmp_path):
    pages = {'/race_card/list/RACEID/202611100000000000': '<a href="/race_card/list/RACEID/202611102015120100">大井</a>',
             '/race_performance/list/RACEID/202611102015120101': RES,
             '/race_performance/list/RACEID/202611102015120102': RES.replace('<span class="num">1</span>', '<span class="num">2</span>')}
    b = bf.Backfill(tmp_path, FakeReader(pages), window_start='2026-11-09', today='2026-11-11')
    b.run(10_000)
    st = json.loads((tmp_path / 'backfill' / 'state.json').read_text())
    assert st['days']['2026-11-10']['venues'] == {'20': '2026111020151201'}
    assert st['races']['202611102015120102']['status'] == 'DONE'
    rec = json.loads((tmp_path / 'backfill' / 'results' / '2026-11-10' / 'OHI_02.json').read_text())
    assert rec['result']['order'][:3] == [3, 1, 2]
    assert rec['result']['payouts']['TRIO'] == {'1-2-3': 1230}
    assert rec['header']['distance'] == 1200 and rec['header']['going'] == '稍重' and rec['header']['weather'] == '曇'
    assert rec['rows'][0]['horse'] == 'A' and rec['class'].startswith('HISTORICAL')
    assert st['complete'] is True


def test_backfill_stops_discovery_without_links(tmp_path):
    b = bf.Backfill(tmp_path, FakeReader({f'/race_card/list/RACEID/2026111{d}0000000000': '<a href="/x/1">x</a>' for d in range(10)}),
                    window_start='2026-11-01', today='2026-11-11')
    b.run(10_000)
    st = json.loads((tmp_path / 'backfill' / 'state.json').read_text())
    assert st['discovery'] == 'FAILED_SEE_PROBE' and len(st['days']) == bf.DISCOVERY_PROBE
    assert (tmp_path / 'backfill' / 'probe.json').exists()


def test_night_window():
    from datetime import datetime
    assert bf.is_night(datetime(2026, 11, 19, 2, 0)) and bf.is_night(datetime(2026, 11, 19, 22, 0))
    assert not bf.is_night(datetime(2026, 11, 19, 12, 0)) and not bf.is_night(datetime(2026, 11, 19, 8, 30))
