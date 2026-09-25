import base64,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"runtime"/"jra_source_runtime"
sys.path.insert(0,str(ROOT))

def test_jra_manifest_and_url():
    from jra_source_manifest import build_jra_manifest,race_card_url_from_meeting_key
    m=build_jra_manifest({"venue_id":"NKY","race_date":"2026-09-22","race_no":10,"jra_meeting_key":"0620260407"})
    assert m["family_id"]=="JRA"
    assert m["jra_venue_code"]=="06"
    assert m["required_official_runner_adapter"]=="JRA_OFFICIAL_RACE_PDF"
    assert any(x["source_id"]=="JRA-RACE-CARD-HTML-AUX" and not x["required"] for x in m["sources"])
    assert "pw01dde0106202604071020260922" in race_card_url_from_meeting_key("0620260407","2026-09-22",10)

def test_runner_parser():
    from jra_runner_universe import extract_from_tables
    rows=[["枠","馬番","馬名 / 単勝オッズ(人気)","性齢/負担重量/騎手"],
          ["1","1","ネオロマーネ7.7(4番人気) (0.0.0.0) 476 kg(+2)","牡2 55.0 内田博幸"],
          ["2","3","テストホース (1.0.0.2)","牝3 55.0 騎手"]]
    r=extract_from_tables([rows])
    assert [x["horse_no"] for x in r]==[1,3]
    assert r[0]["name"]=="ネオロマーネ"

def test_tsl_parser():
    from tsl_public_shadow_evidence import parse_tsl_html
    raw="""<html><body><h1>中山 10R 15:10 1800m ダ</h1><table>
    <tr><th>馬番</th><th>印</th><th>馬名</th><th>単勝</th><th>複勝</th><th>馬連</th><th>断層</th><th>拮抗</th><th>異常</th></tr>
    <tr><td>1</td><td>◎</td><td>サンプルワン</td><td>20.1</td><td>15.0</td><td>12.2</td><td>1.5</td><td>0.2</td><td>0</td></tr>
    <tr><td>2</td><td>○</td><td>サンプルツー</td><td>15.2</td><td>11.0</td><td>8.4</td><td>1.1</td><td>0.5</td><td>1</td></tr>
    </table><p>軸：1(90)</p><p>本線：2(80)</p></body></html>""".encode()
    x=parse_tsl_html(raw,"text/html; charset=utf-8")
    assert len(x["runners"])==2
    assert x["runners"][0]["horse_no"]==1
    assert x["runners"][0]["win_vote"]["value"]==20.1

def test_source_allowlist_is_jra_family_isolated_and_contains_tsl():
    import source_acquisition as s
    assert s._host_allowed("www.jra.go.jp")
    assert s._host_allowed("www.jma.go.jp")
    assert s._host_allowed("jra.k-ba.net")
    # LOCAL/NAR and SBO hosts are forbidden in the JRA source runtime.
    assert not s._host_allowed("nar.k-ba.net")
    assert not s._host_allowed("www.keiba.go.jp")
    assert not s._host_allowed("www.tokyocitykeiba.com")
    assert not s._host_allowed("example.invalid")


def test_jra_point_in_time_population_seed():
    from jra_population_seed import build_population_seed
    artifact={
      "jra_auxiliary_evidence_sha256":"AUXSHA",
      "jra_auxiliary_evidence":{
        "race_card_population_seed":{
          "seeds":[
            {"runner_id":"1","horse_no":1,"horse_name":"A","sire":"S1","dam":"D1","damsire":"DS1","body_weight":480,"body_weight_change":2},
            {"runner_id":"2","horse_no":2,"horse_name":"B","sire":"S1","dam":"D2","damsire":"DS2","body_weight":470,"body_weight_change":-4}
          ]
        }
      }
    }
    x=build_population_seed(artifact)
    assert x["runner_count"]==2
    assert x["population_fit_ready"] is False
    assert x["production_authority"] is False
    assert x["sire_field_counts"]==[{"sire":"S1","field_count":2}]


def test_jra_official_pdf_url_and_runner_parser():
    from jra_official_pdf import official_pdf_url, parse_runner_universe_from_pages
    assert official_pdf_url("2026-09-22","NKY","0620260407")=="https://www.jra.go.jp/keiba/rpdf/pdf/20260922-04nakayama07.pdf"
    page="""2026年4中山7
2006 MEMORIAL DEEP IMPACT CUP
1，600
（3頭）
（芝Turf・右・外）
2006メモリアルディープインパクトカップ
10R
負担重量は、3歳56
白
1
牡6
H6
黒鹿58
（2008年）9，000，000
フミサウンド
三浦
皇成39，834，000
1
Kosei Miura
Fumi Sound（JPN）
黒
2
牡5
H5
芦58
（2011年）9，000，000
レッドレナート
横山
和生37，109，000
2
Kazuo Yokoyama
Red Renato（JPN）
赤
3
牝4
F4
栗56
（2019年）9，000，000
エ
リ
ム
原田
和真16，379，000
4
Kazuma Harada
Elim（JPN）
コース
レコード
"""
    u=parse_runner_universe_from_pages([page],10)
    assert u["runner_count"]==3
    assert [(x["horse_no"],x["name"]) for x in u["runners"]]==[(1,"フミサウンド"),(2,"レッドレナート"),(3,"エリム")]
    assert u["runners"][0]["frame_no"]==1
    assert u["runners"][0]["sex"]=="牡" and u["runners"][0]["age"]==6
    assert u["runners"][0]["assigned_weight"]==58.0
    assert u["runners"][0]["jockey"]=="三浦皇成"
    assert u["runners"][2]["frame_no"]==3
    assert u["runners"][2]["assigned_weight"]==56.0


def test_jra_official_race_context_parser():
    from jra_race_context import parse_race_context
    txt="2026年9月22日 4回中山7日 9 レース 鋸山特別 3歳以上2勝クラス 1,800 （ダ）（牝）定量 14時10分 10 レース 2006メモリアル ディープインパクトカップ 3歳以上2勝クラス 1,600 （芝・外）定量 14時50分 11 レース JRAアニバーサリーステークス 3歳以上3勝クラス 1,800 （ダ）ハンデ 15時30分 12 レース 3歳以上1勝クラス 1,200 （ダ）定量 16時10分 表示モード"
    x=parse_race_context(txt,"NKY","2026-09-22",10)
    assert x["distance_m"]==1600
    assert x["surface"]=="芝"
    assert x["course_variant"]=="外"
    assert x["weight_rule"]=="定量"
    assert x["race_class"]=="2勝クラス"
    assert x["start_time"]=="14:50"
    assert x["scheduled_post_at"].startswith("2026-09-22T14:50:00")
