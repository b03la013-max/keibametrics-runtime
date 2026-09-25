import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"/"jra_source_runtime"))
from jra_horse_history import parse_horse_history

def test_parse_official_horse_history():
    raw="""<html><table><tr><th>年月日</th><th>場</th><th>レース名</th><th>距離</th><th>馬場</th><th>頭数</th><th>人気</th><th>着順</th><th>騎手名</th><th>負担重量</th><th>馬体重</th><th>タイム</th><th>Rt</th><th>1着馬（2着馬）</th></tr>
<tr><td>2026年9月13日</td><td>中山</td><td>3歳上2勝クラス</td><td>ダ1800</td><td>重</td><td>13</td><td>5</td><td>9</td><td>松山 弘平</td><td>58.0</td><td>486</td><td>1:53.4</td><td>99</td><td>ジェイエルモーダル</td></tr></table></html>""".encode()
    x=parse_horse_history(raw,"text/html; charset=utf-8")
    assert x["run_count"]==1
    r=x["runs"][0]
    assert r["date"]=="2026-09-13"
    assert r["venue"]=="中山"
    assert r["surface"]=="ダ"
    assert r["distance_m"]==1800
    assert r["finish"]==9
    assert r["jockey"]=="松山 弘平"
    assert r["rating"]==99
