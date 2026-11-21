"""JRA official 馬場情報 / 開催お知らせ collector (record only). Fixtures copy the real 2026-11-21 page
structure (www.jra.go.jp, trimmed)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime/jra_source_runtime"))
import jra_official_daily as d  # noqa: E402

CUSHION = ('<div id="cushion_data_list"> <div id="rcA" title="東京"> <div class="unit"> <div class="time">11月21日（土曜）9時00分</div>'
           ' <div class="cushion">9.5</div> </div> <div class="unit"> <div class="time">11月20日（金曜）9時00分</div>'
           ' <div class="cushion">10.0</div> </div> </div><!-- /[#rcA] --> <div id="rcB" title="京都"> <div class="unit">'
           ' <div class="time">11月21日（土曜）6時00分</div> <div class="cushion">10.0</div> </div> </div><!-- /[#rcB] --> </div>')
MOIST = ('<div id="moist_data_list"> <div id="rcA" title="東京"> <div class="unit"> <div class="time">11月21日（土曜）8時30分</div>'
         ' <div class="turf"> <span class="mg" data-condition="hard">13.1</span> <span class="m4c" data-condition="hard">14.3</span> </div>'
         ' <div class="dirt"> <span class="mg" data-condition="wet">6.3</span> <span class="m4c" data-condition="wet">7.9</span> </div>'
         ' <ul class="note_list narrow mt10 moist_caution"> <li>注記：特になし</li> </ul> </div> </div><!-- /[#rcA] --> </div>')
BABA = ('<div id="contentsBody"><div class="main"><h2>第5回京都競馬第5日<span class="date">（2026年11月21日（土曜））</span></h2></div>'
        '<h3>馬場状態<span class="time">（11月20日（金曜）正午現在）</span></h3><div class="cell txt">天候：<strong>晴</strong></div>'
        '<div class="cell turf"><ul><li><div class="head"><h4>芝</h4></div><div class="content"><p>良</p></div></li></ul></div>'
        '<div class="cell dirt"><ul><li><div class="head"><h4>ダート</h4></div><div class="content"><p>稍重</p></div></li></ul></div>'
        '<div class="turf_length"><table><caption><div class="main">芝コースの芝丈</div></caption><tbody><tr><th>芝</th>'
        '<td>10<span>から</span>12</td><td>12<span>から</span>16</td></tr></tbody></table></div>'
        '<div class="course"><div class="head"><h3>使用コース</h3></div><div class="content"><p><strong>C</strong>コース（外に内柵を設置）</p></div></div>'
        '<div class="turf_condition"><div class="head"><h3>芝の状態</h3></div><div class="content"><p>概ね良好な状態です。</p></div></div>'
        '<script>var x="芝";</script></div>')
NOTICE = ('<h2>11月21日（土曜）　開催情報</h2><table class="basic"> <caption>5回京都5日</caption> <tbody>'
          '<tr class="change"><th scope="row">1</th><td><dl><dt>発走時刻変更</dt><dd> 10時00分<span class="kara">から</span>10時01分に変更 </dd></dl></td></tr>'
          '<tr><th scope="row">2</th><td> </td></tr>'
          '<tr class="change"><th scope="row">3</th><td><dl><dt>競走除外</dt><dd> 10番 スパイスオブライフ</dd></dl></td></tr>'
          '</tbody></table><h2>11月22日（日曜）　開催情報</h2><table class="basic"> <caption>3回福島5日</caption> <tbody>'
          '<tr class="change"><th scope="row">11</th><td><dl><dt>出走取消</dt><dd> 5番 フィーリウス</dd></dl>'
          '<dl><dt>騎手変更</dt><dd> 2番 テストホース</dd></dl></td></tr></tbody></table>')


def test_cushion_all_venues_with_times():
    c = d.parse_cushion(CUSHION)
    assert c["東京"][0] == {"measured_at": "11月21日（土曜）9時00分", "value": 9.5}
    assert c["東京"][1]["value"] == 10.0 and c["京都"][0]["value"] == 10.0


def test_moisture_goal_and_corner4():
    m = d.parse_moist(MOIST)["東京"][0]
    assert m["measured_at"] == "11月21日（土曜）8時30分"
    assert m["turf"] == {"goal_pct": 13.1, "corner4_pct": 14.3, "band": "hard"}
    assert m["dirt"]["goal_pct"] == 6.3 and m["dirt"]["band"] == "wet" and m["note"] == "特になし"


def test_venue_page_going_course_and_scripts_ignored():
    b = d.parse_baba(BABA)
    assert b["meeting"].startswith("第5回京都競馬第5日")
    assert b["condition_at"] == "11月20日（金曜）正午"
    assert b["weather"] == "晴" and b["going"] == {"turf": "良", "dirt": "稍重"}
    assert b["course_in_use"].startswith("C") and b["turf_condition"] == "概ね良好な状態です。"
    assert b["turf_length_cm"] == {"noshiba": "10から12", "yoshiba": "12から16"}


def test_notices_scratches_and_post_time_changes():
    n = d.parse_notices(NOTICE)["meetings"]
    kyo, fks = n
    assert kyo["meeting"] == "5回京都5日" and kyo["date_label"] == "11月21日（土曜）"
    assert kyo["races"]["2"] == []
    assert kyo["races"]["3"] == [{"type": "競走除外", "detail": "10番 スパイスオブライフ", "horse_no": 10, "horse_name": "スパイスオブライフ"}]
    assert kyo["races"]["1"][0]["type"] == "発走時刻変更"
    assert [i["type"] for i in fks["races"]["11"]] == ["出走取消", "騎手変更"]


def test_record_appends_only_on_change_and_rate_limits(tmp_path):
    pages = {"/keiba/baba/_data_cushion.html": CUSHION, "/keiba/baba/_data_moist.html": MOIST, "/JRADB/accessI.html": NOTICE}
    calls = []

    def fetch(path, data=None):
        calls.append(path)
        return pages.get(path, BABA)

    d._LAST["at"] = 0.0
    p = d.record(tmp_path, "2026-11-21", fetch=fetch, sleep=lambda s: None)
    assert p and len(calls) == 6
    assert d.record(tmp_path, "2026-11-21", fetch=fetch, sleep=lambda s: None) is None   # rate limit
    d.record(tmp_path, "2026-11-21", fetch=fetch, sleep=lambda s: None, force=True)
    doc = json.loads(p.read_text())
    assert doc["record_only"] is True and doc["production_effect"] == "NONE"
    assert len(doc["observations"]) == 1                                                 # unchanged -> no append
    pages["/JRADB/accessI.html"] = NOTICE.replace("5番 フィーリウス", "7番 ベツノウマ")
    d.record(tmp_path, "2026-11-21", fetch=fetch, sleep=lambda s: None, force=True)
    assert len(json.loads(p.read_text())["observations"]) == 2


def test_fetch_failures_are_recorded_not_raised(tmp_path):
    def fetch(path, data=None):
        raise OSError("blocked")
    d._LAST["at"] = 0.0
    p = d.record(tmp_path, "2026-11-22", fetch=fetch, sleep=lambda s: None)
    obs = json.loads(p.read_text())["observations"][0]
    assert len(obs["errors"]) == 6 and obs["notices"] is None
