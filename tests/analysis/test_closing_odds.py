"""Offline fixtures only; network and manual collection are never executed."""
import ast
import hashlib
import json
import socket
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime/analysis"))
sys.path.insert(0, str(Path(__file__).parent))
import _benter_second_stage_legacy as legacy
import benter_second_stage as b
import closing_odds_reader as reader
import closing_odds_collect as collector
import closing_odds_analysis as closing
from test_benter_second_stage import stored_race, synthetic, write_json

RID = "KM-JRA-TKY-20261101-R09"
FIXTURE = ROOT / "tests/fixtures/analysis/jra_closing_odds_synthetic.html"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("NO_NETWORK_IN_RESEARCH_TESTS")
    monkeypatch.setattr(socket.socket, "connect", forbidden)


def capture(html=None, **kwargs):
    return reader.build_capture((html or FIXTURE.read_text()).encode("utf-8"), race_id=RID,
                                url="https://www.jra.go.jp/JRADB/accessO.html",
                                captured_at="2026-11-03T01:00:00+09:00", **kwargs)


def test_fullwidth_ties_cancellation_exclusion_nonfinisher_and_cap():
    value = capture(expected_active=[1, 2, 3, 4], expected_nonstarters={"5":"CANCELLED", "6":"EXCLUDED"})
    rows = value["parsed"]["runners"]
    assert value["parsed"]["n_active"] == 4
    assert [r["win_odds"] for r in rows] == [2.4, 3.8, 999.9, 12.3, None, None]
    assert rows[2]["display_capped_999_9"] is True
    assert rows[3]["status"] == "ACTIVE"  # A DNF actually ran; do not remove it.
    assert [r["status"] for r in rows[-2:]] == ["CANCELLED", "EXCLUDED"]
    assert reader.validate_capture(value, race_id=RID) == value


@pytest.mark.parametrize("replacement", ["---", "0.0", "NaN", "1000.0"])
def test_missing_or_invalid_active_price_is_not_dropped_or_imputed(replacement):
    with pytest.raises(ValueError, match="PRICE"):
        capture(FIXTURE.read_text().replace("２．４", replacement))


def test_popularity_alone_and_payout_are_never_a_price_source():
    with pytest.raises(ValueError, match="ODDS_TABLE"):
        capture(FIXTURE.read_text().replace("単勝オッズ</th>", "単勝人気</th>"))
    with pytest.raises(ValueError, match="STATUS_NOT_EXPLICIT"):
        capture(FIXTURE.read_text().replace("レース結果・確定単勝オッズ", "出馬表"))
    with pytest.raises(ValueError, match="STATUS_NOT_EXPLICIT"):
        capture(FIXTURE.read_text().replace("レース結果・確定単勝オッズ", "<a href='/results'>レース結果・最終オッズ</a>"))
    value = capture(FIXTURE.read_text().replace("<th>人気</th>", "<th>別項目</th>"))
    assert value["parsed"]["popularity_missing"] == 4
    assert all(r["popularity_rank"] is None for r in value["parsed"]["runners"])


def test_wrong_race_duplicate_rows_and_universe_are_rejected():
    with pytest.raises(ValueError, match="HEADER"):
        capture(FIXTURE.read_text().replace("９レース", "８レース"))
    with pytest.raises(ValueError, match="ROW_AMBIGUOUS"):
        capture(FIXTURE.read_text().replace("<td>２</td><td>テスト馬二", "<td>１</td><td>テスト馬二"))
    with pytest.raises(ValueError, match="ACTIVE_UNIVERSE"):
        capture(expected_active=[1, 2, 3])
    with pytest.raises(ValueError, match="NONSTARTER"):
        capture(expected_nonstarters={"5":"EXCLUDED", "6":"EXCLUDED"})
    with pytest.raises(ValueError, match="URL_NOT_OFFICIAL"):
        reader.build_capture(FIXTURE.read_bytes(), race_id=RID, url="https://example.com/odds", captured_at="2026-11-03T01:00:00Z")


def test_raw_and_parsed_integrity_atomic_no_overwrite(tmp_path):
    value = capture()
    target = reader.save_capture(tmp_path, value)
    before = target.read_bytes()
    with pytest.raises(FileExistsError):
        reader.save_capture(tmp_path, value)
    assert target.read_bytes() == before
    altered = json.loads(json.dumps(value))
    altered["parsed"]["runners"][0]["win_odds"] = 1.0
    with pytest.raises(ValueError, match="SHA_MISMATCH"):
        reader.validate_capture(altered, race_id=RID)
    altered["capture_sha256"] = reader.digest({k:v for k,v in altered.items() if k != "capture_sha256"})
    with pytest.raises(ValueError, match="RAW_OR_PARSED"):
        reader.validate_capture(altered, race_id=RID)
    # Strict charset decoding keeps the exact original raw bytes.
    html = FIXTURE.read_text().replace('charset="UTF-8"', 'charset="cp932"')
    value = reader.build_capture(html.encode("cp932"), race_id=RID, url="https://www.jra.go.jp/JRADB/accessD.html",
                                captured_at="2026-11-03T01:00:00Z", content_type="text/html; charset=cp932")
    assert reader.validate_capture(value, race_id=RID)["parsed"]["n_active"] == 4


def test_official_final_time_cell_and_frame_rowspan_preserve_horse_columns():
    html = '<h1>単勝・複勝オッズ 2026年11月1日 4回東京11日 9レース</h1>'
    html += '<div class="refresh_line"><div class="cell time"><strong>最終オッズ</strong></div></div>'
    html += '<table><tr><th>枠</th><th>馬番</th><th>馬名</th><th>単勝</th></tr>'
    html += '<tr><td rowspan="2">1</td><td>1</td><td>合成甲</td><td>2.4</td></tr>'
    html += '<tr><td>2</td><td>合成乙</td><td>3.8</td></tr></table>'
    value = capture(html, expected_active=[1,2])
    assert [(x['horse_no'],x['win_odds']) for x in value['parsed']['runners']] == [(1,2.4),(2,3.8)]
    assert value['parsed']['closing_marker'] == '最終オッズ'
    for changed in [html.replace('最終オッズ','10時20分現在'),
                    html.replace('<strong>最終オッズ</strong>','<a href="#">最終オッズ</a>'),
                    html.replace('class="cell time"','class="menu"')]:
        with pytest.raises(ValueError,match='STATUS_NOT_EXPLICIT'):
            capture(changed)
    with pytest.raises(ValueError,match='SPAN_INVALID'):
        capture(html.replace('rowspan="2"','rowspan="99"'))


def test_exact_observed_accessO_token_generic_menu_not_accepted():
    html = """<a onclick="return doAction('/JRADB/accessO.html','pw15oli00/6D')">オッズ</a>
    <a onclick="return doAction('/JRADB/accessO.html', 'pw151ouS306202604090320260927Z/15')">最終オッズ</a>"""
    action = collector.closing_action(html, "0620260409", "20260927", 3)
    assert action == ("/JRADB/accessO.html", "pw151ouS306202604090320260927Z/15")
    with pytest.raises(ValueError, match="NAVIGATION_NOT_UNIQUE"):
        collector.closing_action(html, "0620260409", "20260927", 4)
    with pytest.raises(ValueError, match="NAVIGATION_NOT_UNIQUE"):
        collector.closing_action(html + html.replace("Z/15", "Z/CA"), "0620260409", "20260927", 3)


@pytest.mark.parametrize("mode", ["00", "10"])
def test_actual_current_and_archive_day_links_require_exact_identity(mode):
    token = f"pw01srl{mode}082026041120261101/C0"
    html = f"<a onclick=\"doAction('/JRADB/accessS.html','{token}')\">対象日</a>"
    html += "<a onclick=\"doAction('/JRADB/accessS.html','pw01srl10052026041120261101/E2')\">隣の場</a>"
    assert collector.result_day_action(html, "0820260411", "20261101") == ("/JRADB/accessS.html", token)
    for key, day in [("0820260410", "20261101"), ("0820260411", "20261031")]:
        with pytest.raises(ValueError, match="DAY_NAVIGATION_NOT_UNIQUE"):
            collector.result_day_action(html, key, day)
    with pytest.raises(ValueError, match="DAY_NAVIGATION_NOT_UNIQUE"):
        collector.result_day_action(html.replace("/C0", "/C0BAD"), "0820260411", "20261101")
    with pytest.raises(ValueError, match="DAY_NAVIGATION_NOT_UNIQUE"):
        collector.result_day_action(html + html.replace("/C0", "/AB"), "0820260411", "20261101")


def test_archived_day_exposes_exact_closing_link_not_a_derived_result_token():
    token = "pw151ou1008202604110120261101Z/0F"
    html = f"<a onclick=\"return doAction('/JRADB/accessO.html','{token}')\">1レースオッズ</a>"
    assert collector.closing_action(html, "0820260411", "20261101", 1) == ("/JRADB/accessO.html", token)
    for key, day, no in [("0520260411", "20261101", 1), ("0820260411", "20261031", 1), ("0820260411", "20261101", 2)]:
        with pytest.raises(ValueError, match="NAVIGATION_NOT_UNIQUE"):
            collector.closing_action(html, key, day, no)
    with pytest.raises(ValueError, match="NAVIGATION_NOT_UNIQUE"):
        collector.closing_action(html.replace("Z/0F", "Z/0FBAD"), "0820260411", "20261101", 1)


def test_network_requires_owner_and_preflight_and_respects_robots(monkeypatch):
    with pytest.raises(ValueError, match="OWNER_APPROVAL"):
        collector.OfficialClient(approval_ref=None, robots_reviewed=True, terms_reviewed=True)
    with pytest.raises(ValueError, match="OWNER_APPROVAL"):
        collector.OfficialClient(approval_ref="Owner record", robots_reviewed=False, terms_reviewed=True)
    client = collector.OfficialClient(approval_ref="TEST_ONLY", robots_reviewed=True, terms_reviewed=True)
    with pytest.raises(ValueError, match="ROBOTS_PERMISSION"):
        client.get("https://www.jra.go.jp/JRADB/accessO.html")
    with pytest.raises(ValueError, match="ALLOWLISTED"):
        client.get("https://www.jra.go.jp.evil.example/robots.txt")
    monkeypatch.setattr(client, "_request", lambda *a, **k: (b"User-agent: *\nDisallow: /JRADB/\n", "text/plain", "2026-11-03T00:00:00Z"))
    with pytest.raises(ValueError, match="ROBOTS_DENIES"):
        client.load_robots()


def test_each_request_is_rate_limited_and_bounded(monkeypatch):
    client = collector.OfficialClient(approval_ref="TEST_ONLY", robots_reviewed=True, terms_reviewed=True, max_requests=2)
    client.robots = collector.urllib.robotparser.RobotFileParser()
    client.robots.parse(["User-agent: *", "Allow: /"])
    class Response:
        status = 200
        headers = {"Content-Type":"text/html"}
        def __init__(self, url): self.url = url
        def geturl(self): return self.url
        def read(self, size): return b"fixture only"
        def __enter__(self): return self
        def __exit__(self, *args): pass
    monkeypatch.setattr(client.opener, "open", lambda request, **kwargs: Response(request.full_url))
    sleeps = []
    monkeypatch.setattr(collector.time, "monotonic", lambda: 10.0)
    monkeypatch.setattr(collector.time, "sleep", sleeps.append)
    client.get("https://www.jra.go.jp/JRADB/accessO.html")
    client.post(("/JRADB/accessD.html", "OBSERVED_ONLY"), "https://www.jra.go.jp/JRADB/accessS.html")
    assert sleeps == [5.0]
    with pytest.raises(ValueError, match="BUDGET"):
        client.get("https://www.jra.go.jp/JRADB/accessO.html")


def test_existing_capture_causes_zero_requests(tmp_path):
    value = capture()
    reader.save_capture(tmp_path / "runtime/closing_odds", value)
    class Forbidden:
        def load_robots(self): raise AssertionError("NO_REFETCH")
    result = collector.collect(tmp_path, [{"race_id": RID}], Forbidden())
    assert result["requests"] == result["saved"] == 0
    assert result["skipped_existing"] == 1


def test_offline_archived_day_to_closing_collection_without_result_request(tmp_path):
    day_token = 'pw01srl10052026041120261101/E2'
    odds_token = 'pw151ou1005202604110920261101Z/B7'
    def link(path, token):
        return f"<a onclick=\"doAction('{path}','{token}')\">合成リンク</a>".encode()
    class SavedWebsite:
        count = 0
        requests = []
        def load_robots(self): self.count += 1
        def get(self, url):
            assert url == 'https://www.jra.go.jp/keiba/calendar2026/2026/11/1101.html'
            self.count += 1
            return link('/JRADB/accessS.html','pw01sli00/AF'), 'text/html', '2026-11-03T01:00:00Z'
        def post(self, action, referer):
            self.count += 1
            self.requests.append(action)
            if action[1] == 'pw01sli00/AF': raw = link('/JRADB/accessS.html',day_token)
            elif action[1] == day_token: raw = link('/JRADB/accessO.html',odds_token)
            elif action[1] == odds_token: raw = FIXTURE.read_bytes()
            else: raise AssertionError('UNOBSERVED_OR_UNNECESSARY_REQUEST')
            return raw, 'text/html; charset=utf-8', '2026-11-03T01:00:00Z'
    website = SavedWebsite()
    plan = [dict(race_id=RID, race_date='2026-11-01', post_at='2026-11-01T14:25:00+09:00',
                 meeting_key='0520260411', active_runner_ids=['1','2','3','4'], nonstarters={'5':'CANCELLED','6':'EXCLUDED'})]
    result = collector.collect(tmp_path,plan,website)
    assert result['saved'] == 1 and result['failures'] == [] and result['requests'] == 5
    assert website.requests == [('/JRADB/accessS.html','pw01sli00/AF'),
                                ('/JRADB/accessS.html',day_token),('/JRADB/accessO.html',odds_token)]


def test_concurrent_capture_writers_publish_exactly_one_file(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    value = capture()
    def publish(_):
        try:
            reader.save_capture(tmp_path, value)
            return "NEW"
        except FileExistsError:
            return "EXISTS"
    with ThreadPoolExecutor(max_workers=4) as pool:
        outcomes = list(pool.map(publish, range(4)))
    assert outcomes.count("NEW") == 1 and outcomes.count("EXISTS") == 3
    reader.validate_capture(json.loads((tmp_path / (RID + ".json")).read_text()), race_id=RID)


def dataset(root, n=40):
    rs = synthetic(n, seed=30, runners=6)
    for i, race in enumerate(rs, 1):
        rid = stored_race(root, number=i)
        path = root / "runtime/results" / (rid + ".json")
        value = json.loads(path.read_text())
        winner = int(race.ids[np.argmax(race.y)])
        order = [winner] + [k for k in range(1, 7) if k != winner]
        value["official_result"].update(top3=order[:3], finish_order=order)
        write_json(path, value)


def test_legacy_bytes_and_default_and_closing_zero_are_identical(tmp_path):
    assert hashlib.sha256(Path(legacy.__file__).read_bytes()).hexdigest() == "d1e24264cd3f26a7e874d7e782e1b83e1bdee291b29b1c9ef5b174c9106eb1e7"
    root = tmp_path / "data"
    dataset(root)
    hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*.json")}
    args = ["--from","2026-10-11","--to","2026-11-01","--asof","2026-11-03","--root",str(root),
            "--bootstrap-reps","4","--shuffle-reps","4"]
    legacy.main(args + ["--out", str(tmp_path / "legacy")])
    b.main(args + ["--out", str(tmp_path / "default")])
    b.main(args + ["--series","closing","--out",str(tmp_path / "closing")])
    for name in ("summary.json", "summary.md", "ledger.csv"):
        assert (tmp_path / "legacy" / name).read_bytes() == (tmp_path / "default" / name).read_bytes()
        assert (tmp_path / "default" / name).read_bytes() == (tmp_path / "closing" / name).read_bytes()
    value = json.loads((tmp_path / "closing/closing_comparison.json").read_text())
    assert value["n_closing_races"] == 0 and value["n_primary_races"] == 40
    assert value["closing"]["n_races"] == 0
    assert value["exclusion_counts"] == {"CLOSING_NOT_STORED": 40}
    assert hashes == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in hashes}
    with pytest.raises(FileExistsError):
        closing.run(root, date(2026,10,11), date(2026,11,1), date(2026,11,3), tmp_path / "closing")


def test_paired_series_reads_validated_captures_and_rejects_temporal_or_identity_gaps(tmp_path):
    root = tmp_path / "data"
    dataset(root, 40)
    rid = "KM-JRA-TKY-20261011-R01"
    html = "<h2>2026年10月11日 4回東京1日 1レース</h2><h3>最終オッズ</h3>"
    html += "<table><tr><th>馬番</th><th>単勝オッズ</th></tr>"
    html += "".join(f"<tr><td>{i}</td><td>{i*2.1}</td></tr>" for i in range(1,7)) + "</table>"
    value = reader.build_capture(html.encode(), race_id=rid, url="https://www.jra.go.jp/JRADB/accessO.html",
                                 captured_at="2026-11-03T01:00:00+09:00", expected_active=range(1,7))
    reader.save_capture(root / "runtime/closing_odds", value)
    report, rows = closing.compare(root, date(2026,10,11), date(2026,11,1), date(2026,11,3), bootstrap_reps=3, shuffle_reps=3)
    assert report["n_closing_races"] == 1
    assert len(rows) == 6 and sum(r["m"] for r in rows) == pytest.approx(1)
    assert rows[0]["minutes_to_post"] < 0
    report2, _ = closing.compare(root, date(2026,10,11), date(2026,11,1), date(2026,11,2), bootstrap_reps=3, shuffle_reps=3)
    assert report2["n_closing_races"] == 0
    assert report2["exclusion_counts"]["CLOSING_CAPTURE_AFTER_ASOF"] == 1


def test_no_production_imports_and_manual_only_workflow():
    for name in ["closing_odds_reader.py", "closing_odds_collect.py", "closing_odds_analysis.py", "benter_second_stage.py"]:
        tree = ast.parse((ROOT / "runtime/analysis" / name).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom): assert not (node.module or "").startswith("jra_")
            if isinstance(node, ast.Import): assert not any(x.name.startswith("jra_") for x in node.names)
    source = (ROOT / ".github/workflows/km-jra-closing-odds-manual.yml").read_text()
    assert "workflow_dispatch:" in source and "contents: read" in source
    assert "schedule:" not in source and "contents: write" not in source and "pull_request:" not in source
