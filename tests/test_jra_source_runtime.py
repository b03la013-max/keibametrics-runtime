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
    import importlib.util
    spec=importlib.util.spec_from_file_location("jra_test_source_acquisition", ROOT/"source_acquisition.py")
    s=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s)
    assert s._host_allowed("www.jra.go.jp")
    assert s._host_allowed("www.jma.go.jp")
    assert s._host_allowed("jra.k-ba.net")
    assert s._host_allowed("race.netkeiba.com")
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


def test_jra_source_identity_binding():
    from runtime.jra_source_runtime.jra_source_identity import bind_source_identity as _bind_source_identity
    a={"profile":"X"}
    ctx={"family_id":"JRA","venue_id":"NKY","race_date":"2026-09-22","race_no":10}
    x=_bind_source_identity(a,"20260922-NKY-R10",ctx)
    assert x["family_id"]=="JRA"
    assert x["race_id"]=="20260922-NKY-R10"
    assert x["source_race_context"]["venue_id"]=="NKY"


def test_jra_race_card_detail_parser():
    from jra_race_card_detail import parse_race_card_detail
    raw="""<html><body>
    <a href="/JRADB/accessU.html?CNAME=pw01dud000000000001/AA">コウジハラ</a>
    <a href="#" onclick="return doAction('/JRADB/accessK.html', 'pw04kmk000001/BB');">M.ミシェル</a>
    <a href="#" onclick="return doAction('/JRADB/accessC.html', 'pw05cmk000001/CC');">西田 雄一郎</a>
    <a href="/JRADB/accessU.html?CNAME=pw01dud000000000002/DD">ビアフォーナウ</a>
    <a href="#" onclick="return doAction('/JRADB/accessK.html', 'pw04kmk000002/EE');">小林 美駒</a>
    <a href="#" onclick="return doAction('/JRADB/accessC.html', 'pw05cmk000002/FF');">池上 昌和</a>
    <table>
    <tr><th>枠</th><th>馬番</th><th>馬名 / 単勝オッズ(人気) 戦績 / 総賞金 / 馬体重 馬主名 / 生産者名 / 調教師名 / 血統</th><th>性齢/毛色 負担重量 騎手名</th><th>前走</th><th>前々走</th><th>3走前</th><th>4走前</th></tr>
    <tr><td>1</td><td>1</td><td>コウジハラ 5.7(2番人気) (1.1.1.3) 1,070万円 由井 健太郎 ヒダカフアーム 西田 雄一郎(美浦) 父：マテラスカイ 母：ローザビアンカ(母の父：ワイルドラッシュ)</td><td>牝3/栗 54.0kg M.ミシェル</td><td>2026年9月5日 中山 牝1勝クラス 3着 16頭5番8番人気 M.ミシェル 54.0kg 1200ダ 1:10.2 重 438kg 22 3F 36.4 マサノピンクレディ(0.5)</td><td>2026年7月26日 新潟 1勝クラス 9着 15頭9番9番人気 木幡 初也 53.0kg 1000芝 58.3 不良 440kg 3F 35.6 パレスドフィーヌ(1.0)</td><td></td><td></td></tr>
    <tr><td>2</td><td>2</td><td>ビアフォーナウ 11.4(5番人気) (1.0.1.17) 990万円 小林 由明 北洋牧場 池上 昌和(美浦) 父：バトルプラン 母：カリストーガ(母の父：ダノンシャンティ)</td><td>牝5/鹿 54.0kg 小林 美駒</td><td>2026年9月5日 中山 牝1勝クラス 13着 16頭11番12番人気 丸田 恭介 56.0kg 1200ダ 1:11.8 重 466kg 1515 3F 36.4 マサノピンクレディ(2.1)</td><td></td><td></td><td></td></tr>
    </table></body></html>""".encode("utf-8")
    x=parse_race_card_detail(raw,"text/html; charset=utf-8")
    assert x["runner_count"]==2
    a=x["runners"][0]
    assert a["horse_name"]=="コウジハラ"
    assert a["win_odds"]==5.7 and a["popularity_rank"]==2
    assert a["career_record"]["starts"]==6
    assert a["sire"]=="マテラスカイ" and a["damsire"]=="ワイルドラッシュ"
    assert a["assigned_weight"]==54.0 and a["jockey"]=="M.ミシェル"
    assert a["horse_profile_token"]=="pw01dud000000000001/AA"
    assert a["jockey_profile_token"]=="pw04kmk000001/BB"
    assert a["trainer_profile_token"]=="pw05cmk000001/CC"
    assert x["runners"][1]["jockey_profile_token"]=="pw04kmk000002/EE"
    assert x["runners"][1]["trainer_profile_token"]=="pw05cmk000002/FF"
    assert a["recent_runs"][0]["finish"]==3
    assert a["recent_runs"][0]["distance_m"]==1200
    assert a["recent_runs"][0]["surface"]=="ダ"
    assert a["recent_runs"][0]["body_weight"]==438
    assert a["recent_runs"][0]["final3f"]==36.4
    assert a["recent_runs"][0]["margin"]==0.5


def test_detail_runner_universe_fallback():
    from jra_race_card_detail import runner_universes_from_detail
    d={"source_snapshot_sha256":"D","runners":[
      {"runner_id":"1","horse_no":1,"frame_no":1,"status":"ACTIVE","horse_name":"A","sex":"牝","age":3,"assigned_weight":54.0,"jockey":"J","current_body_weight":470,"current_body_weight_change":2},
      {"runner_id":"2","horse_no":2,"frame_no":2,"status":"CANCELLED","horse_name":"B","sex":"牡","age":4,"assigned_weight":57.0,"jockey":"K","current_body_weight":480,"current_body_weight_change":0}
    ]}
    declared,active=runner_universes_from_detail(d)
    assert declared["runner_count"]==2
    assert active["runner_count"]==1
    assert active["runners"][0]["name"]=="A"
    assert active["runners"][0]["source"]=="JRA_OFFICIAL_JRADB_DETAIL"


def test_person_profile_parser_current_year_stats():
    import sys
    sys.path.insert(0,str(ROOT/"runtime"/"jra_source_runtime"))
    from jra_person_stats import parse_person_profile
    html="""<html><body><div>調教師情報 西田 雄一郎 （ニシダ）</div><table>
    <tr><th></th><th>1着</th><th>2着</th><th>3着</th><th>4着</th><th>5着</th><th>着外</th><th>出走回数</th><th>勝率</th><th>連対率</th><th>3着内率</th></tr>
    <tr><td>平地</td><td>11</td><td>7</td><td>11</td><td>11</td><td>15</td><td>126</td><td>181</td><td>0.061</td><td>0.099</td><td>0.160</td></tr>
    </table></body></html>""".encode("utf-8")
    r=parse_person_profile(html,"text/html; charset=utf-8","trainer","T")
    assert r["name"]=="西田 雄一郎"
    assert r["current_year_flat"]["starts"]==181
    assert r["current_year_flat"]["top3_rate"]==0.160


def test_registered_common_race_id_derives_from_jra_meeting_key():
    import sys
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    p=str(root/"runtime"/"jra_source_runtime")
    if p not in sys.path:
        sys.path.insert(0,p)
    from jra_registered_common import _discover_race_id
    rid,snap=_discover_race_id("HSN","2026-09-26",12,"2026-09-26T16:20:00+09:00","0920260408")
    assert rid=="202609040812"
    assert snap is None


def test_jra_official_pdf_parser_prefers_explicit_r_prefix_header():
    from jra_official_pdf import parse_runner_universe_from_pages
    page="""NEWCOMER YO2
（3頭）
（外・右・芝Turf）
R4 メイクデビュー中山
馬齢重量
白
1
牝2
F2
鹿53
（2023年）
リゼスカーレット
小林
美駒
Rize Scarlet（JPN）
黒
2
牝2
F2
鹿54
（2024年）
アイファーティアラ
長浜
鴻緒
Eifer Tiara（JPN）
赤
3
牝2
F2
鹿55
（1996年）
マルジョレーヌ
柴田
大知
Marjolaine（JPN）
コース
レコード
"""
    u=parse_runner_universe_from_pages([page],4)
    assert [(x["horse_no"],x["name"]) for x in u["runners"]]==[
        (1,"リゼスカーレット"),(2,"アイファーティアラ"),(3,"マルジョレーヌ")
    ]


def test_jra_horse_history_accepts_official_no_prior_runs():
    from jra_horse_history import parse_horse_history
    raw="""<html><body><h1>競走馬情報 リゼスカーレット</h1>
    <div>出走レース</div><p>該当するデータがありません。</p>
    </body></html>""".encode("utf-8")
    x=parse_horse_history(raw,"text/html; charset=utf-8")
    assert x["status"]=="NO_PRIOR_RUNS"
    assert x["run_count"]==0
    assert x["runs"]==[]


def test_registered_common_workout_selects_official_universe_matching_table():
    from jra_registered_common import parse_workout
    raw="""<html><body>
    <table>
      <tr><th>馬番</th><th>馬名</th><th>評価</th></tr>
      <tr><td>1</td><td>ドナチャージ</td><td>B</td></tr>
      <tr><td>2</td><td>エコロブラン</td><td>C</td></tr>
    </table>
    <table>
      <tr><th>馬番</th><th>馬名</th><th>評価</th></tr>
      <tr><td>1</td><td>リゼスカーレット</td><td>B</td></tr>
      <tr><td>2</td><td>アイファーティアラ</td><td>C</td></tr>
    </table>
    </body></html>""".encode("utf-8")
    official={"runners":[
      {"horse_no":1,"name":"リゼスカーレット"},
      {"horse_no":2,"name":"アイファーティアラ"},
    ]}
    x=parse_workout(raw,"text/html; charset=utf-8",official)
    assert [r["horse_name"] for r in x["runners"]]==["リゼスカーレット","アイファーティアラ"]


def _fictional_spanned_workout(*,numbers=(1,2,3),days=('2026/10/21','2026/10/28'),duplicate=False):
    header='<tr>'+''.join('<th>'+x+'</th>' for x in ['枠','馬番','印','馬名','日付','コース','馬場','乗り役','調教タイム','位置','脚色'])+'<th colspan="2">評価</th><th>映像</th></tr>'
    rows=[]
    for no in numbers:
        actual=list(days)+([days[-1]] if duplicate else [])
        span=1+len(actual)
        rows.append(f'<tr><td rowspan="{span}">{min(no,8)}</td><td rowspan="{span}">{no}</td><td rowspan="{span}">--</td><td rowspan="{span}">テスト{no} 前走</td><td colspan="25">時計ではない説明</td></tr>')
        for day in actual:
            seconds='11.8' if day==max(days) else '12.5'
            rows.append(f'<tr><td>{day}(水)</td><td>ＣＷ</td><td>良</td><td>助手</td><td>81.0(15.0) 66.0(15.0) {seconds}({seconds})</td><td>7</td><td>馬也</td><td>動き良好</td><td>B</td><td></td></tr>')
    return ('<html><table>'+header+''.join(rows)+'</table></html>').encode()


def test_workout_spans_bind_printed_identity_course_clock_and_history():
    from jra_registered_common import parse_workout
    rows=parse_workout(_fictional_spanned_workout(numbers=(1,9)),observed_at='2026-11-01T00:00:00+00:00')['runners']
    assert [x['horse_no'] for x in rows]==[1,9]
    assert all(x['course']=='ＣＷ' and x['final1f']==11.8 and x['gait']=='馬也' and x['rating']=='B' for x in rows)
    assert all(x['workout_date']=='2026-10-28' and [h['workout_date'] for h in x['workout_history']]==['2026-10-28','2026-10-21'] for x in rows)
    assert all(x['assessment']=='動き良好' for x in rows)


def test_workout_visible_partial_rows_do_not_complete_official_universe():
    from jra_registered_common import parse_workout,_reconcile
    expected={'runners':[{'horse_no':no,'name':f'テスト{no}'} for no in range(1,18)]}
    parsed=parse_workout(_fictional_spanned_workout(),official_universe=expected)
    assert parsed['runner_count']==3
    gate=_reconcile(parsed,{'jra_official_runner_universe':expected})
    assert gate['verified'] is False
    assert len(gate['errors'])==14


def test_workout_exact_repeated_observation_is_not_a_second_history_sample():
    from jra_registered_common import parse_workout
    parsed=parse_workout(_fictional_spanned_workout(duplicate=True))
    assert all(len(x['workout_history'])==2 for x in parsed['runners'])


def test_workout_conflicting_latest_date_is_rejected():
    import pytest
    from jra_registered_common import parse_workout
    raw=_fictional_spanned_workout(numbers=(1,),duplicate=True)
    # Same printed date with different observed clock cannot be selected by order.
    old=b'11.8(11.8)';at=raw.rfind(old);raw=raw[:at]+b'11.7(11.7)'+raw[at+len(old):]
    with pytest.raises(ValueError,match='LATEST_DATE_AMBIGUOUS'):parse_workout(raw)


def test_workout_later_training_date_cannot_precede_observation():
    import pytest
    from jra_registered_common import parse_workout
    with pytest.raises(ValueError,match='DATE_AFTER_OBSERVATION'):
        parse_workout(_fictional_spanned_workout(),observed_at='2026-10-20T23:00:00+00:00')
    # JRA observation dates are JST, including observations before UTC midnight.
    rows=parse_workout(_fictional_spanned_workout(days=('2026/10/28',)),observed_at='2026-10-27T23:30:00+00:00')['runners']
    assert rows[0]['workout_date']=='2026-10-28'


def test_workout_single_digit_or_invalid_dates_cannot_escape_temporal_check():
    import pytest
    from jra_registered_common import parse_workout
    for day in ('2026/11/2','2026/02/30','翌日',''):
        with pytest.raises(ValueError,match='DATE_AFTER_OBSERVATION|DATE_INVALID'):
            parse_workout(_fictional_spanned_workout(days=(day,)),observed_at='2026-11-01T00:00:00+00:00')
    x=parse_workout(_fictional_spanned_workout(days=('2026/1/2',)),observed_at='2026-11-01T00:00:00+00:00')
    assert x['runners'][0]['workout_date']=='2026-01-02'


def test_workout_compact_assessment_contract_is_unchanged():
    from jra_registered_common import parse_workout
    raw='<table><tr><th>馬番</th><th>馬名</th><th>評価</th></tr><tr><td>1</td><td>テスト</td><td>B</td></tr></table>'.encode()
    x=parse_workout(raw)
    assert x['schema']=='COMPACT_ASSESSMENT' and x['runner_count']==1
    assert x['runners'][0]=={'runner_id':'1','horse_no':1,'horse_name':'テスト','course':'','workout_time_raw':'','final1f':None,'gait':'','assessment':'テスト','rating':'B'}


def test_workout_span_limit_does_not_relax_existing_speed_parser():
    import pytest
    from jra_registered_common import _SpeedTables,parse_workout
    raw=_fictional_spanned_workout(numbers=(1,),days=tuple(f'2026/10/{d:02d}' for d in range(1,11)))
    with pytest.raises(ValueError,match='SPEED_HEADER_INVALID_SPAN'):_SpeedTables().feed(raw.decode())
    assert len(parse_workout(raw)['runners'][0]['workout_history'])==10


def test_workout_history_reaches_observation_retention_without_full_feed_admission():
    from jra_registered_common import parse_workout,_retain_workout_observations,_reconcile
    import hashlib
    raw=_fictional_spanned_workout(duplicate=True)
    official={'runners':[{'horse_no':no,'name':f'テスト{no}'} for no in range(1,18)]}
    candidate=parse_workout(raw,official_universe=official,observed_at='2026-11-01T00:00:00+00:00')
    observed=candidate['observed_workout_history']
    assert observed['record_count']==6 and observed['observed_runner_count']==3
    assert observed['official_identity_verified'] is True
    assert observed['full_official_universe_match'] is False
    assert observed['production_feature_admission'] is False
    snap={'source_id':'TEST-WORKOUT','snapshot_sha256':'snapshot-1','raw_sha256':hashlib.sha256(raw).hexdigest(),'fetched_at':'2026-11-01T00:00:00+00:00','cutoff_relation':'PRE_CUTOFF'}
    base={}
    _retain_workout_observations(base,candidate,snap)
    _retain_workout_observations(base,candidate,{**snap,'snapshot_sha256':'snapshot-2'})
    retained=base['observed_workout_history']
    assert retained['record_count']==6
    assert all(len(x['source_refs'])==2 for x in retained['records'])
    assert retained['production_feature_admission'] is False
    assert _reconcile(candidate,{'jra_official_runner_universe':official})['verified'] is False


def test_workout_observation_history_does_not_admit_future_or_wrong_identity():
    from jra_registered_common import parse_workout_history
    import pytest
    with pytest.raises(ValueError,match='DATE_AFTER_OBSERVATION'):
        parse_workout_history(_fictional_spanned_workout(days=('2026/11/2',)),observed_at='2026-11-01T00:00:00+00:00')
    wrong={'runners':[{'horse_no':no,'name':f'ベツ{no}'} for no in range(1,4)]}
    with pytest.raises(ValueError,match='OFFICIAL_IDENTITY_MISMATCH'):
        parse_workout_history(_fictional_spanned_workout(),official_universe=wrong)
