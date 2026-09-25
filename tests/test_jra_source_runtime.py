import base64,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"runtime"/"jra_source_runtime"
sys.path.insert(0,str(ROOT))

def test_jra_manifest_and_url():
    from jra_source_manifest import build_jra_manifest,race_card_url_from_meeting_key
    m=build_jra_manifest({"venue_id":"NKY","race_date":"2026-09-22","race_no":10,"jra_meeting_key":"0620260407"})
    assert m["family_id"]=="JRA"
    assert m["jra_venue_code"]=="06"
    assert any(x["source_id"]=="JRA-RACE-CARD" and x["required"] for x in m["sources"])
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

def test_source_allowlist_contains_tsl():
    import source_acquisition as s
    assert s._host_allowed("jra.k-ba.net")
    assert not s._host_allowed("example.invalid")
