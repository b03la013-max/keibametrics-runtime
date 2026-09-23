import copy
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))

from local_candidate_numerical_authority import assess as assess_candidate
from local_numerical_authority_gate import assess as assess_production
from local_nar_evidence_candidate import compile_candidate_evidence
from local_fullnumerical_candidate import materialize_candidate, REQUIRED
from local_krs_bridge_candidate import build_candidate_krs, build_candidate_prediction, HSV_KEYS, STATIC_KEYS
from local_candidate_walkforward import evaluate as walkforward


def group(frame,no,name,jockey,odds,sexage,load,sire,trainer,bw,dam,damsire,starts):
    desc=[]; races=[]; rides=[]; contents=[]; margins=[]
    for s in starts:
        desc.append(f"{s['finish']} {s['date']} {s['going']} {s['field']}頭 {s['venue']} {s['course']} {s['horse_no']}番")
        races.append(s['race_name'])
        rides.append(f"{s['pop']}人 {s['bw']} {s['jockey']} {s['load']}")
        contents.append(f"{s['time']} {s['positions']} {s['final3f']}")
        margins.append(f"{s['margin']} {s['winner']}")
    primary=[str(frame),str(no),name,jockey,odds,"全","2-","2-","1-","10","左","2-","2-","1-","10",
             "右","0-","0-","0-","0","場","1-","1-","1-","7","距","1-","1-","0-","4","1:28.0","良1:28.2"]+desc
    meta=[sexage,"鹿毛","04.01生",f"{load} 1-1-0-2"]+races
    blood=[sire,trainer,bw]+rides
    content=[dam,"馬主"]+contents
    margin=[f"（{damsire}）","牧場",""]+margins
    return [primary,meta,blood,content,margin]


def fixture():
    starts1=[
      dict(finish=2,date="26.09.01",going="重",field=12,venue="浦和",course="左1400",horse_no=1,race_name="Ｃ１",pop=2,bw=470,jockey="騎手A",load=56.0,time="1:28.4",positions="2-2-2-2",final3f="38.0",margin=0.2,winner="馬X"),
      dict(finish=1,date="26.08.01",going="良",field=10,venue="浦和",course="左1400",horse_no=3,race_name="Ｃ１",pop=1,bw=468,jockey="騎手A",load=56.0,time="1:28.0",positions="1-1-1-1",final3f="37.8",margin=0.0,winner="自身"),
      dict(finish=3,date="26.07.01",going="稍重",field=11,venue="川崎ナ",course="左1400",horse_no=4,race_name="Ｃ１",pop=3,bw=469,jockey="騎手B",load=56.0,time="1:29.0",positions="3-3-3-3",final3f="38.5",margin=0.5,winner="馬Y"),
      dict(finish=4,date="26.06.01",going="良",field=12,venue="浦和",course="左1500",horse_no=5,race_name="Ｃ１",pop=4,bw=467,jockey="騎手A",load=56.0,time="1:37.0",positions="3-3-4-4",final3f="39.0",margin=0.8,winner="馬Z"),
      dict(finish=2,date="26.05.01",going="重",field=12,venue="浦和",course="左1400",horse_no=2,race_name="Ｃ２",pop=2,bw=466,jockey="騎手A",load=56.0,time="1:28.8",positions="2-2-2-2",final3f="38.2",margin=0.1,winner="馬Q"),
    ]
    starts2=[
      dict(finish=5,date="26.09.02",going="重",field=12,venue="浦和",course="左1400",horse_no=8,race_name="Ｃ１",pop=6,bw=500,jockey="騎手C",load=55.0,time="1:29.4",positions="8-8-7-5",final3f="38.1",margin=1.0,winner="馬A"),
      dict(finish=3,date="26.08.05",going="良",field=12,venue="浦和",course="左1400",horse_no=9,race_name="Ｃ１",pop=5,bw=498,jockey="騎手C",load=55.0,time="1:28.8",positions="7-7-5-3",final3f="38.0",margin=0.5,winner="馬B"),
      dict(finish=2,date="26.07.05",going="重",field=10,venue="川崎ナ",course="左1400",horse_no=7,race_name="Ｃ１",pop=7,bw=496,jockey="騎手C",load=55.0,time="1:28.7",positions="8-7-5-2",final3f="37.7",margin=0.2,winner="馬C"),
      dict(finish=6,date="26.06.05",going="稍重",field=12,venue="浦和",course="左1500",horse_no=10,race_name="Ｃ１",pop=8,bw=499,jockey="騎手D",load=55.0,time="1:38.0",positions="9-9-8-6",final3f="39.1",margin=1.4,winner="馬D"),
      dict(finish=4,date="26.05.05",going="良",field=12,venue="浦和",course="左1400",horse_no=11,race_name="Ｃ２",pop=9,bw=497,jockey="騎手C",load=55.0,time="1:29.1",positions="10-10-7-4",final3f="38.0",margin=0.7,winner="馬E"),
    ]
    starts3=[
      dict(finish=8,date="26.09.03",going="重",field=12,venue="浦和",course="左1400",horse_no=12,race_name="Ｃ１",pop=8,bw=450,jockey="騎手E",load=54.0,time="1:30.0",positions="4-5-7-8",final3f="40.0",margin=1.8,winner="馬F"),
      dict(finish=7,date="26.08.03",going="良",field=12,venue="浦和",course="左1400",horse_no=10,race_name="Ｃ１",pop=10,bw=452,jockey="騎手F",load=54.0,time="1:29.8",positions="5-6-7-7",final3f="39.5",margin=1.5,winner="馬G"),
      dict(finish=4,date="26.07.03",going="重",field=10,venue="船橋ナ",course="左1500",horse_no=6,race_name="Ｃ２",pop=5,bw=451,jockey="騎手E",load=54.0,time="1:38.2",positions="4-4-4-4",final3f="39.0",margin=0.8,winner="馬H"),
      dict(finish=9,date="26.06.03",going="稍重",field=12,venue="浦和",course="左1400",horse_no=7,race_name="Ｃ１",pop=11,bw=449,jockey="騎手E",load=54.0,time="1:30.2",positions="4-5-7-9",final3f="40.2",margin=2.0,winner="馬I"),
      dict(finish=5,date="26.05.03",going="良",field=12,venue="浦和",course="左1400",horse_no=5,race_name="Ｃ２",pop=7,bw=448,jockey="騎手E",load=54.0,time="1:29.4",positions="3-3-4-5",final3f="39.2",margin=1.0,winner="馬J"),
    ]
    table=[["枠番","馬番","競走馬","騎手・調教師 馬主・生産牧場","オッズ 馬体重 変更情報","着別成績 最高タイム","競走成績"],
           ["前走","前々走","3走前","4走前","5走前"]]
    table+=group(1,1,"候補A","騎手A（浦和）","2.5 (1人気)","牡4",56.0,"父A","厩舎A（浦和）","472 (+2)","母A","母父A",starts1)
    table+=group(2,2,"候補B","騎手C（浦和）","4.5 (2人気)","牡5",55.0,"父B","厩舎B（浦和）","502 (+2)","母B","母父B",starts2)
    table+=group(3,3,"候補C","騎手E（浦和）","12.0 (3人気)","牝4",54.0,"父C","厩舎C（浦和）","453 (+3)","母C","母父C",starts3)
    source={
      "source_snapshot_sha256":"SRC-SHA",
      "official_runner_universe_sha256":"UNIV-SHA",
      "source_freeze_at":"2026-09-23T00:00:00+00:00",
      "normalized_evidence":{
        "race_card_tables":{"value":[table],"source_id":"NAR-TEST-CARD","snapshot_sha256":"CARD-SHA","fetched_at":"2026-09-23T00:00:00+00:00"},
        "odds_tables":{"value":[[]],"source_id":"NAR-TEST-ODDS","snapshot_sha256":"ODDS-SHA","fetched_at":"2026-09-23T00:00:00+00:00"},
        "track_condition":{"value":"重"},"weather":{"value":"雨"},
        "same_day_r01_result_tables":{"value":[[]]},
      }
    }
    request={
      "race_id":"LOCAL-CAND-TEST-R1","venue_id":"URW","race_date":"2026-09-23","race_no":2,
      "race":{"race_id":"LOCAL-CAND-TEST-R1","venue":"URW","venue_id":"URW","race_date":"2026-09-23",
              "distance":1400,"surface":"dirt","going":"重","class":"C1"},
      "environment":{"front_candidate_count":2},
      "run_count":5000,"seed":123,
      "runners":[
        {"runner_id":"1","name":"候補A","static_roles":[]},
        {"runner_id":"2","name":"候補B","static_roles":[]},
        {"runner_id":"3","name":"候補C","static_roles":[]},
      ]
    }
    return source,request


def test_candidate_rule_registry_is_63_of_63_and_nonproduction():
    out=assess_candidate()
    assert out["implementation_ready"] is True
    assert out["production_ready"] is False
    assert out["component_rule_count"]==63
    assert out["bound_component_rule_count"]==63
    assert out["required_index_count"]==29


def test_current_production_authority_remains_not_ready():
    out=assess_production()
    assert out["full_numerical_authority"] is False
    assert out["status"]=="NOT_READY"


def test_end_to_end_source_to_29_to_30hsv_11static_is_deterministic():
    source,request=fixture()
    c1=compile_candidate_evidence(source,request)
    c2=compile_candidate_evidence(source,request)
    assert json.dumps(c1,sort_keys=True,ensure_ascii=False)==json.dumps(c2,sort_keys=True,ensure_ascii=False)
    assert all(len(r["evidence_features"])==63 for r in c1["runners"])
    # Missing pedigree/training evidence is explicit neutral, not a weak ability value.
    a=c1["runners"][0]
    assert a["evidence_features"]["sire_fit"]["score"]==52
    assert a["evidence_features"]["sire_fit"]["missing"] is True
    assert a["evidence_features"]["training_comment_trial"]["score"]==0

    n=materialize_candidate(c1)
    s=n["candidate_full_numerical_summary"]
    assert s["required_count"]==3*29
    assert s["calculated_count"]==3*29
    assert s["unresolved_count"]==0
    assert s["full_numerical_complete"] is True
    assert all(set(r["canonical_components"])==set(REQUIRED) for r in n["runners"])

    n=build_candidate_prediction(n)
    b=build_candidate_krs(n)
    assert len(b["candidate_krs_input_data"]["horses"])==3
    for h in b["candidate_krs_input_data"]["horses"]:
        assert set(h["hsv"])==set(HSV_KEYS)
        assert set(h["static"])==set(STATIC_KEYS)
        assert b["candidate_krs_input_data"]["race"]["going"]=="重"

    p=build_candidate_prediction(b)
    assert len(p["candidate_static_prediction"]["ranking"])==3
    assert p["candidate_static_prediction"]["production_authority"] is False


def test_market_cannot_change_hpi_or_tpi_but_can_change_price_diagnostics():
    source,request=fixture()
    c=compile_candidate_evidence(source,request)
    a=materialize_candidate(c)
    before={r["runner_id"]:(r["canonical_components"]["HPI-L"]["value"],r["canonical_components"]["TPI-L"]["value"],r["canonical_components"]["OPI-V"]["value"]) for r in a["runners"]}
    # Modify only market popularity in candidate raw evidence; evidence ability components are untouched.
    c2=copy.deepcopy(c)
    pops={"1":3,"2":1,"3":2}
    for r in c2["runners"]:
        r["raw_candidate_evidence"]["popularity"]=pops[r["runner_id"]]
    b=materialize_candidate(c2)
    after={r["runner_id"]:(r["canonical_components"]["HPI-L"]["value"],r["canonical_components"]["TPI-L"]["value"],r["canonical_components"]["OPI-V"]["value"]) for r in b["runners"]}
    assert all(before[k][0]==after[k][0] and before[k][1]==after[k][1] for k in before)
    assert any(before[k][2]!=after[k][2] for k in before)


def test_walkforward_enforces_temporal_order_and_never_auto_promotes():
    events=[]
    for i in range(3):
        events.append({
          "race_id":f"R{i+1}",
          "prediction_frozen_at":f"2026-09-{20+i:02d}T10:00:00+09:00",
          "result_available_at":f"2026-09-{20+i:02d}T11:00:00+09:00",
          "candidate_prediction":{"ranking":["1","2","3"],"W":["1"],"P2":["1","2"],"P3":["1","2","3"]},
          "actual_top3":["1","2","3"],
          "candidate_mapping_id":"LOCAL-FULL-NUMERICAL-MAPPING-v0.1-CANDIDATE-20260923",
          "source_snapshot_sha256":f"S{i}","result_derived_feature_count":0,
        })
    out=walkforward(events)
    assert out["winner_capture_rate"]==1.0
    assert out["promotion_review_ready"] is False
    assert out["automatic_promotion"] is False
    assert out["status"]=="WAITING_R30"
