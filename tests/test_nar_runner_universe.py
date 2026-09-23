import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"/"local_physical"))

from nar_runner_universe import (
    PROFILE,
    enrich_source_artifact,
    extract_runner_universe_from_tables,
    validate_krs_horses,
    validate_request_runners,
)


def sample_tables():
    return [[
        ["枠番","馬番","競走馬","騎手・調教師 馬主・生産牧場","オッズ 馬体重 変更情報"],
        ["前走","前々走"],
        ["1","1","タマモアマルフィ","近藤翔（高知）","4.5 (2人気)"],
        ["牝3","栗毛","04.23生","☆ 54.0"],
        ["カリフォルニアクローム","田中譲（高知）","488 (-1)"],
        ["2","2","パウラメロディーア","大澤誠（高知）","40.5 (6人気)"],
        ["牝3","栗毛","03.22生","55.0"],
        ["ビッグアーサー","田中譲（高知）","506 (+11)"],
        # rowspan-flattened frame: [馬番, 馬名, ...]
        ["3","ラブペイトー","岡村卓（高知）","57.1 (7人気)"],
        ["牝3","鹿毛","04.26生","55.0"],
        ["アメリカンペイトリオット","胡本友（高知）","427 (-16)"],
    ]]


def test_extract_official_runner_universe_with_rowspan_shape():
    rows=extract_runner_universe_from_tables(sample_tables())
    assert [x["runner_id"] for x in rows]==["1","2","3"]
    assert [x["name"] for x in rows]==["タマモアマルフィ","パウラメロディーア","ラブペイトー"]
    assert rows[0]["frame_no"]==1
    assert rows[2]["frame_no"] is None
    assert rows[0]["body_weight"]==488
    assert rows[0]["body_weight_change"]==-1
    assert rows[1]["body_weight"]==506
    assert rows[1]["body_weight_change"]==11
    assert rows[2]["body_weight"]==427
    assert rows[2]["body_weight_change"]==-16


def test_enrich_and_validate_request_runner_universe():
    art={
      "normalized_evidence":{
        "race_card_tables":{
          "value":sample_tables(),
          "source_id":"NAR-KCH-R03-RACE-CARD",
          "snapshot_sha256":"abc"
        }
      }
    }
    enrich_source_artifact(art)
    u=art["official_runner_universe"]
    assert u["profile"]==PROFILE
    assert u["runner_count"]==3
    assert len(u["runner_universe_sha256"])==64
    ok,errors=validate_request_runners(art,[
      {"runner_id":"1","name":"タマモアマルフィ"},
      {"runner_id":"2","name":"パウラメロディーア"},
      {"runner_id":"3","name":"ラブペイトー"},
    ])
    assert ok is True
    assert errors==[]


def test_runner_universe_missing_extra_and_name_mismatch_fail_closed():
    art={
      "normalized_evidence":{
        "race_card_tables":{
          "value":sample_tables(),
          "source_id":"NAR-KCH-R03-RACE-CARD",
          "snapshot_sha256":"abc"
        }
      }
    }
    enrich_source_artifact(art)
    ok,errors=validate_request_runners(art,[
      {"runner_id":"1","name":"別馬"},
      {"runner_id":"2","name":"パウラメロディーア"},
      {"runner_id":"4","name":"非公式馬"},
    ])
    assert ok is False
    assert any(x.startswith("REQUEST_RUNNERS_MISSING_OFFICIAL:3") for x in errors)
    assert any(x.startswith("REQUEST_RUNNERS_NOT_OFFICIAL:4") for x in errors)
    assert any(x.startswith("REQUEST_RUNNER_NAME_MISMATCH:1:") for x in errors)


def test_krs_horse_universe_uses_horse_no():
    art={
      "normalized_evidence":{
        "race_card_tables":{
          "value":sample_tables(),
          "source_id":"NAR-KCH-R03-RACE-CARD",
          "snapshot_sha256":"abc"
        }
      }
    }
    enrich_source_artifact(art)
    ok,errors=validate_krs_horses(art,{
      "horses":[
        {"horse_no":1,"name":"タマモアマルフィ"},
        {"horse_no":2,"name":"パウラメロディーア"},
        {"horse_no":3,"name":"ラブペイトー"},
      ]
    })
    assert ok is True
    assert errors==[]


def sample_odds_tables_without_runner_2():
    return [[
        ["馬番","馬名","単勝"],
        ["1","タマモアマルフィ","4.5"],
        ["3","ラブペイトー","57.1"],
    ]]


def sample_tables_with_explicit_cancel_2():
    rows=sample_tables()
    rows[0].insert(8,["2","パウラメロディーア","出走取消"])
    return rows


def test_declared_and_active_universe_are_separate_when_odds_omits_cancelled_runner():
    art={
      "normalized_evidence":{
        "race_card_tables":{
          "value":sample_tables(),
          "source_id":"NAR-KCH-R03-RACE-CARD",
          "snapshot_sha256":"abc"
        },
        "odds_tables":{
          "value":sample_odds_tables_without_runner_2(),
          "source_id":"NAR-KCH-R03-ODDS-TANFUKU",
          "snapshot_sha256":"def"
        }
      }
    }
    enrich_source_artifact(art)
    declared=art["declared_runner_universe"]
    active=art["active_runner_universe"]
    assert [x["runner_id"] for x in declared["runners"]]==["1","2","3"]
    assert [x["runner_id"] for x in active["runners"]]==["1","3"]
    assert art["official_runner_universe"]["universe_type"]=="ACTIVE"
    st={x["runner_id"]:x for x in art["runner_status_registry"]}
    assert st["1"]["status"]=="ACTIVE"
    assert st["2"]["status"]=="INACTIVE"
    assert st["2"]["reason"]=="ABSENT_FROM_OFFICIAL_ACTIVE_BETTING_UNIVERSE"
    assert st["3"]["status"]=="ACTIVE"


def test_explicit_cancellation_is_declared_but_not_active_without_odds():
    art={
      "normalized_evidence":{
        "race_card_tables":{
          "value":sample_tables_with_explicit_cancel_2(),
          "source_id":"NAR-KCH-R03-RACE-CARD",
          "snapshot_sha256":"abc"
        }
      }
    }
    enrich_source_artifact(art)
    assert [x["runner_id"] for x in art["declared_runner_universe"]["runners"]]==["1","2","3"]
    assert [x["runner_id"] for x in art["active_runner_universe"]["runners"]]==["1","3"]
    st={x["runner_id"]:x for x in art["runner_status_registry"]}
    assert st["2"]["status"]=="CANCELLED"
    assert st["2"]["reason"]=="EXPLICIT_RACE_CARD_CANCELLATION"


def test_request_validation_uses_active_not_declared_universe():
    art={
      "normalized_evidence":{
        "race_card_tables":{
          "value":sample_tables(),
          "source_id":"NAR-KCH-R03-RACE-CARD",
          "snapshot_sha256":"abc"
        },
        "odds_tables":{
          "value":sample_odds_tables_without_runner_2(),
          "source_id":"NAR-KCH-R03-ODDS-TANFUKU",
          "snapshot_sha256":"def"
        }
      }
    }
    enrich_source_artifact(art)
    ok,errors=validate_request_runners(art,[
      {"runner_id":"1","name":"タマモアマルフィ"},
      {"runner_id":"3","name":"ラブペイトー"},
    ])
    assert ok is True
    assert errors==[]
    ok2,errors2=validate_request_runners(art,[
      {"runner_id":"1","name":"タマモアマルフィ"},
      {"runner_id":"2","name":"パウラメロディーア"},
      {"runner_id":"3","name":"ラブペイトー"},
    ])
    assert ok2 is False
    assert any(x.startswith("REQUEST_RUNNERS_NOT_OFFICIAL:2") for x in errors2)


def test_noncontiguous_active_numbers_are_preserved_after_scratch():
    art={
      "normalized_evidence":{
        "race_card_tables":{
          "value":sample_tables(),
          "source_id":"NAR-KCH-R03-RACE-CARD",
          "snapshot_sha256":"abc"
        },
        "odds_tables":{
          "value":sample_odds_tables_without_runner_2(),
          "source_id":"NAR-KCH-R03-ODDS-TANFUKU",
          "snapshot_sha256":"def"
        }
      }
    }
    enrich_source_artifact(art)
    assert [x["horse_no"] for x in art["active_runner_universe"]["runners"]]==[1,3]
