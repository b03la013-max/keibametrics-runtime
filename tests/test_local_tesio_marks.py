from datetime import datetime, timedelta, timezone

from runtime.capture import tesio_marks as tm

JST = timezone(timedelta(hours=9))
PAGE = """<table class="table table-bordered yosou-data"><tr><th>枠</th><th>馬</th><th>馬名</th><th>重量</th><th>騎手</th><th colspan=3>印</th></tr>
<tr><th>松尾</th><th>よこ<br>てん</th><th>多田</th></tr>
<tr><td rowspan=1>1</td><td>1</td><td>A</td><td>56</td><td>x</td><td>△</td><td>△</td><td>△</td></tr>
<tr><td>2</td><td>2</td><td>B</td><td>56</td><td>y</td><td>◎</td><td>◎</td><td>○</td></tr>
<tr><td rowspan=2>3</td><td>3</td><td>C</td><td>54</td><td>z</td><td>○</td><td>△</td><td>◎</td></tr>
<tr><td>4</td><td>D</td><td>54</td><td>☆w</td><td></td><td></td><td></td></tr>
<tr><td>5</td><td>5</td><td>E</td><td>54</td><td>v</td><td>▲</td><td>▲</td><td>▲</td></tr></table>"""


def test_parse_rowspan_safe():
    m = tm.parse(PAGE)
    assert sorted(m) == [1, 2, 3, 4, 5]
    assert m[2] == ['◎', '◎', '○'] and m[4] == ['', '', '']


def test_index_order():
    idx = tm.tm_index(tm.parse(PAGE))
    assert idx[2] > idx[3] > idx[5] > idx[1] > idx[4]


def test_for_race_cache_and_cutoff(tmp_path):
    dl = datetime(2026, 11, 22, 12, 0, tzinfo=JST)
    out, meta = tm.for_race(tmp_path, '2026-11-22', 'MIZ', 1, dl + timedelta(days=3650), fetcher=lambda d, r: PAGE)
    assert meta['status'] == 'USED_FRESH' and out[2]['src'] == 'tesio'
    out2, meta2 = tm.for_race(tmp_path, '2026-11-22', 'MIZ', 1, dl + timedelta(days=3650), fetcher=None)
    assert meta2['status'] == 'USED_CACHE' and out2 == out
    late, m3 = tm.for_race(tmp_path / 'x', '2026-11-22', 'MIZ', 1, dl - timedelta(days=3650), fetcher=lambda d, r: PAGE)
    assert late is None and m3['status'] == 'FETCHED_AFTER_CUTOFF'


def test_not_applicable_and_error(tmp_path):
    dl = datetime(2030, 1, 1, tzinfo=JST)
    assert tm.for_race(tmp_path, '2026-11-22', 'OHI', 1, dl)[1]['status'] == 'NOT_APPLICABLE'
    def boom(d, r):
        raise OSError('HTTP 403')
    assert tm.for_race(tmp_path, '2026-11-22', 'MOR', 1, dl, fetcher=boom)[1]['status'] == 'UNAVAILABLE'
