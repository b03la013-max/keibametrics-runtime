from __future__ import annotations
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"/"jra_source_runtime"))

from jra_same_day_results import parse_result_detail

def test_parse_official_same_day_result_detail():
    html="""
    <html><body>
    発走時刻： 15時45分 天候 雨 ダート 良
    コース： 2,000 メートル （ダート・右）
    <table>
      <tr><th>着順</th><th>枠</th><th>馬 番</th><th>馬名</th><th>性齢</th><th>負担 重量</th><th>騎手名</th><th>タイム</th><th>着差</th><th>コーナー 通過順位</th><th>推定上り</th></tr>
      <tr><td>1</td><td>6</td><td>11</td><td>ヴァルツァーシャル</td><td>牡7</td><td>58.5</td><td>斎藤 新</td><td>2:05.3</td><td></td><td>9 10 9 8</td><td>36.4</td></tr>
      <tr><td>2</td><td>5</td><td>9</td><td>ルシュヴァルドール</td><td>牡5</td><td>57.0</td><td>坂井 瑠星</td><td>2:05.4</td><td>クビ</td><td>3 3 2 2</td><td>37.0</td></tr>
    </table>
    <table><tr><td>ハロンタイム</td><td>12.6 - 11.4 - 12.1</td></tr></table>
    </body></html>
    """.encode("utf-8")
    out=parse_result_detail(html,"text/html; charset=UTF-8")
    assert out["runner_count"]==2
    assert out["runners"][0]["horse_no"]==11
    assert out["runners"][0]["finish"]==1
    assert out["runners"][0]["passing_positions"]==[9,10,9,8]
    assert out["runners"][0]["final3f"]==36.4
    assert out["race_environment"]["surface"]=="ダート"
    assert out["race_environment"]["going"]=="良"
    assert out["race_environment"]["distance_m"]==2000
    assert out["result_derived"] is True
    assert out["production_fact_authority"] is True
