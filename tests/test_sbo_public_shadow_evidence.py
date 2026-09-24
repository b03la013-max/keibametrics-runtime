import copy
import datetime
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"/"local_physical"))

import sbo_public_shadow_evidence as sbo

HTML = """<!doctype html><html><body>
<h3>浦和競馬 第1競走 1400m 13:30発走 馬場: 良</h3>
<table>
<tr><th>馬番</th><th>馬名</th><th>調教師</th><th>負担重量</th><th>騎手</th><th>馬体重</th><th>近走指数</th><th>距離指数</th><th>馬場指数</th><th>平均指数</th></tr>
<tr><td>1</td><td>テストワン</td><td>甲</td><td>56.0</td><td>騎手A</td><td>474(-6)</td><td>55(5)</td><td>60(3)</td><td>57(5)</td><td>58</td></tr>
<tr><td>2</td><td>テストツー 3ヶ月前</td><td>乙</td><td>54.0</td><td>騎手B</td><td>490(8)</td><td>74(5)</td><td>*(0)</td><td>84(5)</td><td>79</td></tr>
<tr><td>3</td><td>テストスリー</td><td>丙</td><td>55.0</td><td>騎手C</td><td>500(0)</td><td>70(4)</td><td>71(2)</td><td>72(3)</td><td>71</td></tr>
</table>
<h3>推奨買い目</h3>
<div>軸: 2(79)</div>
<div>本線: 3(71) 1(58)</div>
<div>おさえ: 1(58)</div>
<div>基本: 軸-本線</div>
</body></html>""".encode("utf-8")


def test_build_sbo_url_uses_nar_family_code():
    assert sbo.build_sbo_url("URW","2026-09-24",10) == "https://nar.k-ba.net/20260924/18/10/table.html"


def test_parse_sbo_index_table_and_recommendation():
    x=sbo.parse_sbo_html(HTML)
    assert len(x["runners"])==3
    assert x["runners"][1]["horse_name"]=="テストツー"
    assert x["runners"][1]["recent_index"]["value"]==74
    assert x["runners"][1]["distance_index"]["value"] is None
    assert x["runners"][1]["distance_index"]["sample_count"]==0
    assert x["average_index_ranking"][0]["horse_no"]==2
    assert x["recommendation_groups"]["axis"][0]["horse_no"]==2
    assert x["race_meta"]["distance_m"]==1400
    assert x["race_meta"]["start_time"]=="13:30"


def test_build_shadow_is_non_authoritative_minimal_and_runner_matched(monkeypatch):
    monkeypatch.setattr(sbo, "_fetch", lambda url, timeout=sbo.DEFAULT_TIMEOUT, max_bytes=sbo.DEFAULT_MAX_BYTES: (
        HTML,
        {"content-type":"text/html; charset=utf-8"},
        "ROBOTS_ABSENT_HTTP_404",
    ))
    art={
      "source_race_context":{"venue_id":"URW","race_date":"2099-09-24","race_no":1},
      "normalized_evidence":{"start_time":{"value":"13:30"}},
      "official_runner_universe":{
        "runners":[
          {"runner_id":"1","name":"テストワン","status":"ACTIVE"},
          {"runner_id":"2","name":"テストツー","status":"ACTIVE"},
          {"runner_id":"3","name":"テストスリー","status":"ACTIVE"},
        ]
      }
    }
    out,errs=sbo.build_sbo_shadow_evidence(art,"2099-09-24T04:20:00+00:00")
    assert errs==[]
    ev=out["sbo_public_shadow_evidence"]
    assert ev["production_authority"] is False
    assert ev["prediction_authority"] is False
    assert ev["runner_universe_match"]["status"]=="MATCHED"
    assert ev["status"]=="CAPTURED_PRE_RACE_SHADOW"
    assert ev["oos_eligible"] is True
    assert "raw_gzip_b64" not in ev
    assert "raw_html" not in ev
    assert out["sbo_public_shadow_evidence_sha256"]==sbo.sha_obj(ev)


def test_runner_mismatch_never_becomes_oos_eligible(monkeypatch):
    monkeypatch.setattr(sbo, "_fetch", lambda *a,**k:(HTML,{"content-type":"text/html; charset=utf-8"},"ROBOTS_ABSENT_HTTP_404"))
    art={
      "source_race_context":{"venue_id":"URW","race_date":"2099-09-24","race_no":1},
      "normalized_evidence":{"start_time":{"value":"13:30"}},
      "official_runner_universe":{"runners":[
        {"runner_id":"1","name":"別名","status":"ACTIVE"},
        {"runner_id":"2","name":"テストツー","status":"ACTIVE"},
        {"runner_id":"3","name":"テストスリー","status":"ACTIVE"},
      ]}
    }
    out,errs=sbo.build_sbo_shadow_evidence(art,"2099-09-24T04:20:00+00:00")
    assert errs==[]
    ev=out["sbo_public_shadow_evidence"]
    assert ev["runner_universe_match"]["status"]=="MISMATCH"
    assert ev["oos_eligible"] is False
    assert any("SBO_RUNNER_NAME_MISMATCH" in x for x in ev["warnings"])
