import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"/"local_physical"))

from source_acquisition import snapshot_from_bytes
from nar_auxiliary_evidence import (
    PROFILE,
    build_same_day_bias,
    discover_entity_registry,
    parse_horse_profile,
    parse_person_profile,
)


def _snap(source_id, source_class, raw):
    spec={
        "source_id":source_id,
        "url":"https://www.keiba.go.jp/KeibaWeb/DataRoom/Test",
        "source_class":source_class,
        "authority":"NAR_OFFICIAL",
        "priority":100,
        "official":True,
        "required":False,
        "extract":[],
    }
    s,e=snapshot_from_bytes(
        spec,raw.encode("utf-8"),final_url=spec["url"],status_code=200,
        headers={"content-type":"text/html; charset=utf-8"},
        fetched_at="2026-09-24T00:00:00+00:00",
        prediction_cutoff="2026-09-24T01:00:00+00:00",
    )
    assert e==[]
    return s


def test_discover_entity_registry_from_official_race_card_links():
    html="""
    <html><body>
      <a href="../DataRoom/HorseMarkInfo?k_lineageLoginCode=H001">テストホースA</a>
      <a href="../DataRoom/RiderMark?k_riderLicenseNo=R001">騎手A</a>
      <a href="../DataRoom/TrainerMark?k_trainerLicenseNo=T001">調教師A</a>
      <a href="../DataRoom/HorseMarkInfo?k_lineageLoginCode=H002">テストホースB</a>
      <a href="../DataRoom/RiderMark?k_riderLicenseNo=R002">騎手B</a>
      <a href="../DataRoom/TrainerMark?k_trainerLicenseNo=T002">調教師B</a>
    </body></html>
    """
    s=_snap("RACE","OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT",html)
    s["final_url"]="https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/DebaTable?x=1"
    art={
      "sources":[s],
      "declared_runner_universe":{"runners":[
        {"runner_id":"1","horse_no":1,"name":"テストホースA"},
        {"runner_id":"2","horse_no":2,"name":"テストホースB"},
      ]}
    }
    rows=discover_entity_registry(art)
    assert [x["runner_id"] for x in rows]==["1","2"]
    assert rows[0]["horse_lineage_login_code"]=="H001"
    assert rows[0]["rider_license_no"]=="R001"
    assert rows[0]["trainer_license_no"]=="T001"
    assert rows[1]["rider_name"]=="騎手B"


def test_parse_horse_profile_history():
    html="""
    <table>
      <tr><th>年月日</th><th>競馬場</th><th>R</th><th>競走名</th><th>格組</th><th>距離</th><th>天候・馬場</th><th>頭数</th><th>枠</th><th>馬番</th><th>人気</th><th>着順</th><th>タイム</th><th>差</th><th>上3F</th><th>体重</th><th>騎手(所属)</th><th>重量</th><th>調教師</th><th>収得賞金</th><th>1着馬または(2着馬)</th></tr>
      <tr><td>2026/09/13</td><td>高知</td><td>3</td><td>３歳－６</td><td>３歳</td><td>1400</td><td>曇</td><td>不良</td><td></td><td>12</td><td>1</td><td>1</td><td>2</td><td>4</td><td>1:32.3</td><td>1.1</td><td>40.1</td><td>488</td><td>近藤翔 (高知)</td><td>54.0</td><td>田中譲</td><td>120,000</td><td>サンライズジャッジ</td></tr>
    </table>
    """
    out=parse_horse_profile(_snap("NAR-HORSE-H001","OFFICIAL_HORSE_HISTORY_PROFILE",html))
    assert out["history_count"]==1
    r=out["history"][0]
    assert r["venue"]=="高知"
    assert r["distance"]==1400
    assert r["going"]=="不良"
    assert r["field_size"]==12
    assert r["finish"]==4
    assert r["body_weight"]==488


def test_parse_rider_trainer_performance_rows():
    html="""
    <table><tr><td>所属</td><td>高知</td></tr><tr><td>生年月日</td><td>2000/01/01</td></tr></table>
    <table>
      <tr><th>着別回数</th><th>1着</th><th>2着</th><th>3着</th><th>4着</th><th>5着</th><th>着外</th><th>合計</th><th>勝率</th><th>連対率</th></tr>
      <tr><td>生涯成績</td></tr>
      <tr><td>地方競馬</td><td>81</td><td>73</td><td>90</td><td>90</td><td>101</td><td>570</td><td>1005</td><td>8.1%</td><td>15.3%</td></tr>
      <tr><td>2026年</td><td>10</td><td>12</td><td>8</td><td>7</td><td>5</td><td>58</td><td>100</td><td>10.0%</td><td>22.0%</td></tr>
    </table>
    """
    out=parse_person_profile(_snap("NAR-RIDER-R001","OFFICIAL_RIDER_PROFILE",html))
    assert out["identity"]["所属"]=="高知"
    assert out["lifetime_local"]["total"]==1005
    assert out["lifetime_local"]["win_rate_pct"]==8.1
    assert out["latest_year"]["total"]==100


def test_same_day_bias_uses_prior_result_tables_only():
    table=[
      ["着順","枠","馬番","馬名","コーナー 通過順"],
      ["1","1","1","A","1-1-1-1"],
      ["2","6","6","B","5-4-3-2"],
      ["3","7","7","C","7-6-5-3"],
      ["4","2","2","D","2-2-2-4"],
    ]
    art={"normalized_evidence":{
      "same_day_r01_result_tables":{"value":[table],"source_id":"R1","snapshot_sha256":"abc"},
      "race_card_tables":{"value":[],"source_id":"CURRENT","snapshot_sha256":"def"},
    }}
    out=build_same_day_bias(art)
    assert out["production_authority"] is False
    assert out["races_observed"]==1
    assert out["top3_observations"]==3
    assert out["front_at_last_corner_top3_rate"]==1.0
    assert out["leader_at_last_corner_win_rate"]==1.0
    assert len(out["sha256"])==64


def test_profile_constant_is_auxiliary_not_production():
    assert PROFILE=="KM-LOCAL-NAR-AUXILIARY-EVIDENCE-v1.0-20260924"
