import datetime as dt, json, sys, urllib.error
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime/jra_source_runtime"))
import jra_results_backfill as B

PAGE = """<html><div class="race_header"><div class="date_line">2026年11月23日（月曜） 5回東京6日 発走時刻： 15時30分 天候 晴 芝 良</div>
<div class="race_title"><span class="race_name">テストS</span><div class="type"><div class="cell category">2歳</div>
<div class="cell class">オープン</div><div class="cell course">コース： 1,800 メートル （芝・左）</div></div></div></div>
<table><tr><th>着順</th><th>枠</th><th>馬番</th><th>馬名</th><th>性齢</th><th>負担重量</th><th>騎手名</th><th>タイム</th><th>着差</th>
<th>コーナー通過順位</th><th>推定上り</th><th>馬体重（増減）</th><th>調教師名</th><th>単勝人気</th></tr>
<tr><td>1</td><td><img alt="枠8"></td><td>12</td><td>ウマA</td><td>牡2</td><td>56.0</td><td>騎手A</td><td>1:47.1</td><td></td><td>12 9 10</td><td>32.5</td><td>474(-2)</td><td>調教A</td><td>6</td></tr>
<tr><td>中止</td><td><img alt="枠1"></td><td>1</td><td>ウマB</td><td>牝2</td><td>55.0</td><td>騎手B</td><td></td><td></td><td></td><td></td><td>420(計不)</td><td>調教B</td><td>3</td></tr>
</table></html>"""


def test_parse_result_page_facts_only():
    r = B.parse_result_page(PAGE)
    assert r["race"]["distance_m"] == 1800 and r["race"]["going"] == "良" and r["race"]["class_text"] == "オープン"
    a, b = r["runners"]
    assert (a["finish"], a["frame"], a["horse_no"], a["popularity"], a["body_weight_change"], a["passing"]) == (1, 8, 12, 6, -2, [12, 9, 10])
    assert b["finish"] is None and b["finish_label"] == "中止" and b["body_weight"] == 420 and b["body_weight_change"] is None


def test_client_refuses_fast_rate_and_honours_delay():
    with pytest.raises(ValueError):
        B.Client(delay=1.0)
    slept = []
    class Op:
        def open(self, req, timeout):
            raise urllib.error.HTTPError(req.full_url, 429, "x", {}, None)
    c = B.Client(opener=Op(), clock=lambda: 0.0, sleep=slept.append)
    with pytest.raises(B.Refused):
        c.get("/a")
    with pytest.raises(B.Refused):
        c.get("/b")
    assert slept == [3.0] and c.requests == 2


def test_run_holds_30_min_on_refusal_and_does_not_retry(tmp_path, monkeypatch):
    monkeypatch.setattr(B, "OUT", tmp_path)
    class C:
        requests = 0
        def get(self, path):
            self.requests += 1
            raise B.Refused("HTTP_403:" + path)
    out = B.run(dt.date(2026, 11, 1), 1, client=C(), start=dt.date(2026, 11, 20))
    assert out["status"] == "REFUSED_HOLD" and out["requests"] == 1
    st = json.loads((tmp_path / "state.json").read_text())
    assert st["refusals"][-1]["reason"].startswith("HTTP_403") and st["hold_until"]
    again = B.run(dt.date(2026, 11, 1), 1, client=C(), start=dt.date(2026, 11, 20))
    assert again["status"] == "HOLD"


def test_race_key():
    assert B.race_key("pw01sde1005202605061120261123/CF")["race_id"] == "KM-JRA-TKY-20261123-R11"
    with pytest.raises(ValueError):
        B.race_key("pw01sde1099202605061120261123/CF")


def test_entry_day_is_the_previous_sunday():
    import datetime as dt
    from jra_source_runtime import jra_results_backfill as B
    assert B._entry_day(dt.date(2026, 11, 26)) == dt.date(2026, 11, 22)  # Thursday
    assert B._entry_day(dt.date(2026, 11, 23)) == dt.date(2026, 11, 22)  # Monday
    assert B._entry_day(dt.date(2026, 11, 22)) == dt.date(2026, 11, 15)  # Sunday itself is not used (results may be partial)


def test_venue_codes_match_the_canonical_race_ids():
    import jra_race_day_resolver as R
    m = next(v for v in vars(R).values() if isinstance(v, dict) and v.get("04") == ("NGT", "新潟"))
    assert B.VENUES == {k: v[0] for k, v in m.items()}


def test_run_stops_cleanly_on_a_transient_network_drop(tmp_path, monkeypatch):
    import http.client
    monkeypatch.setattr(B, "OUT", tmp_path)
    class C:
        requests = 0
        def get(self, path):
            self.requests += 1
            raise http.client.RemoteDisconnected("Remote end closed connection without response")
    out = B.run(dt.date(2026, 11, 1), 1, client=C(), start=dt.date(2026, 11, 20))
    assert out["status"] == "NETWORK_STOP_RESUME_NEXT_RUN"
    st = json.loads((tmp_path / "state.json").read_text())
    assert st["network_stops"][-1]["reason"].startswith("NETWORK:RemoteDisconnected") and not st.get("hold_until")
