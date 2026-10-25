import sys
import pytest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"/"local_physical"))

from nar_runner_universe import (
    PROFILE,
    enrich_source_artifact,
    extract_runner_universe_from_tables,
    enrich_unsigned_nankan_declared_artifact,
    validate_krs_horses,
    validate_request_runners,
)


def unsigned_nankan_sample(*, cancelled=False):
    """Reuse authored provider facts; no original HTML, HTTP or signing."""
    import hashlib
    from runtime import urw_nankan_reference_source as n
    from test_urw_nankan_reference_source import DAY, DAY_ID, NOW, detailed_card, program
    raw=detailed_card()
    if cancelled:
        raw=raw.replace(b'<td class="cs-odds">-</td>', '<td class="cs-odds">取消</td>'.encode(), 1)
    race=n.parse_program(program(),n.ORIGIN+'/program/'+DAY_ID+'.do',DAY)[0]
    receipt={'provider':n.PROVIDER,'url':n.ORIGIN+'/uma_shosai/'+DAY_ID+'01.do',
             'http_status':200,'fetched_at':NOW.isoformat(),'raw_sha256':hashlib.sha256(raw).hexdigest(),
             'source_policy':{'usage_scope':'USER_PERSONAL_NONCOMMERCIAL_PRIVATE_ONLY_NOT_PUBLIC_REDISTRIBUTION',
                              'classification':'TEST_SYNTHETIC_ONLY'}}
    source=n.build_unsigned_source_snapshot(raw,race,receipt,race_id='TEST-SYNTHETIC-NANKAN-UNSIGNED')
    return source,race,source['parsed_nankan_facts']


def test_unsigned_nankan_declared_adapter_preserves_provider_time_and_formal_boundary():
    import copy
    from runtime.local_physical.source_acquisition import verify_source_artifact
    source,race,facts=unsigned_nankan_sample(cancelled=True)
    before=copy.deepcopy(source)
    out=enrich_unsigned_nankan_declared_artifact(source,race,facts)
    assert source==before
    declared=out['declared_runner_universe']
    assert declared['provider']=='NANKAN_OFFICIAL' and declared['universe_type']=='DECLARED'
    assert declared['runner_count']==2 and [x['body_weight'] for x in declared['runners']]==[481,481]
    assert [x['status'] for x in out['runner_status_registry']]==['CANCELLED','ACTIVE_DECLARED']
    assert declared['source_fetched_at']==source['sources'][0]['fetched_at']
    assert out['declared_fact_binding']['input_source_snapshot_sha256']==source['source_snapshot_sha256']
    assert out['formal_ready'] is False and out['signed_source_claim'] is False and out['active_verified'] is False
    assert 'official_runner_universe' not in out and 'active_runner_universe' not in out
    assert verify_source_artifact(out)==(False,['SOURCE_NOT_FORMAL_READY'])
    assert validate_request_runners(out,[{'runner_id':'2','name':facts[1]['name']}])==(False,['OFFICIAL_RUNNER_UNIVERSE_MISSING'])


@pytest.mark.parametrize('damage',['provider','formal','formal_claim','public','raw','facts','context','source_id','relation','listed_name','time'])
def test_unsigned_nankan_adapter_refuses_rehashed_fact_identity_or_authority_changes(damage):
    import copy
    from runtime.local_physical.source_acquisition import sha_obj
    source,race,facts=unsigned_nankan_sample()
    facts=copy.deepcopy(facts)
    if damage=='provider':source['provider']='NAR_OFFICIAL'
    elif damage=='formal':source['formal_ready']=True
    elif damage=='formal_claim':source['formal_source_claim']=True
    elif damage=='public':source['public_redistribution_authorized']=True
    elif damage=='raw':source['sources'][0]['raw_gzip_b64']='not-an-archive'
    elif damage=='facts':facts[0]['current_body_weight']=999
    elif damage=='context':source['source_race_context']['race_no']=2
    elif damage=='source_id':
        source['sources'][0]['source_id']='NANKAN-CARD:WRONG-RACE'
        source['sources'][0]['snapshot_sha256']=sha_obj({k:v for k,v in source['sources'][0].items() if k!='snapshot_sha256'})
    elif damage=='relation':
        source['sources'][0]['cutoff_relation']='POST_CUTOFF'
        source['sources'][0]['snapshot_sha256']=sha_obj({k:v for k,v in source['sources'][0].items() if k!='snapshot_sha256'})
    elif damage=='listed_name':source['declared_runner_universe']={'runners':[{'runner_id':'1','name':'別馬'}]}
    elif damage=='time':source['prediction_cutoff']=source['scheduled_post_at']
    source['source_snapshot_sha256']=sha_obj({k:v for k,v in source.items() if k!='source_snapshot_sha256'})
    with pytest.raises(ValueError):enrich_unsigned_nankan_declared_artifact(source,race,facts)


def test_unsigned_nankan_declared_facts_reach_shared_candidate_29_arithmetic_only():
    from runtime.local_nar_evidence_candidate import compile_parsed_candidate_evidence
    from runtime.local_fullnumerical_candidate import materialize_candidate
    source,race,facts=unsigned_nankan_sample()
    out=enrich_unsigned_nankan_declared_artifact(source,race,facts)
    normalized=out['normalized_evidence']['nankan_runner_facts']
    raw={r['runner_id']:{**r,'race_card_source_id':normalized['source_id'],
                         'race_card_snapshot_sha256':normalized['snapshot_sha256'],
                         'race_card_fetched_at':normalized['fetched_at']} for r in normalized['value']}
    request={'race':{**race,'venue':'URW','class':'C3'},
             'runners':[{'runner_id':r['runner_id'],'name':r['name']} for r in facts]}
    result=materialize_candidate(compile_parsed_candidate_evidence(out,request,raw))
    assert result['candidate_full_numerical_summary']['required_count']==58
    assert result['candidate_full_numerical_summary']['unresolved_count']==0
    assert result['candidate_full_numerical_summary']['production_authority'] is False
    assert normalized['snapshot_sha256']==out['sources'][0]['snapshot_sha256']


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


@pytest.mark.parametrize("where", ["final_ticket", "minimum_efficient_coverage", "ranking", "nested_mec",
                                   "malformed_ticket", "malformed_ranking", "malformed_fpp"])
def test_runtime_final_stops_scratched_references_before_signing(where):
    _runtime_final_boundary(where)


def test_runtime_final_active_tickets_reach_existing_handler_without_new_signer():
    _runtime_final_boundary(None)


def _runtime_final_boundary(where):
    # Execute the existing endpoint body with a non-signing legacy stub.
    # No private key or app import is needed; signature validation is separate.
    import ast, copy, types
    code = (ROOT / "runtime/local_physical/app_v15.py").read_text()
    node = next(n for n in ast.parse(code).body if isinstance(n, ast.FunctionDef) and n.name == "final")
    node.decorator_list = []
    node.args.args[0].annotation = None
    artifact = {"normalized_evidence": {"race_card_tables": {
        "value": sample_tables_with_explicit_cancel_2(), "source_id": "OFFICIAL_CARD"}}}
    enrich_source_artifact(artifact)
    artifact["source_manifest_profile"] = "KM-LOCAL-NAR-SOURCE-MANIFEST-v1.0-20260923"
    called = []
    legacy = types.SimpleNamespace(validate_family=lambda p: None,
        final=lambda p: called.append(copy.deepcopy(p)) or {"receipt": {"status": "NO_SIGNING_TEST"}})
    class EndpointHold(Exception):
        def __init__(self, status, detail):
            super().__init__(detail)
    scope = {"legacy": legacy, "_require_source_receipt": lambda *a: {"artifact": artifact},
             "HTTPException": EndpointHold, "NAR_MANIFEST_PROFILE": artifact["source_manifest_profile"]}
    exec(compile(ast.Module(body=[node], type_ignores=[]), "existing_final_endpoint", "exec"), scope)
    payload = {"race_id": "CONTRACT_FIXTURE", "final_prediction_package": {"ranking": [1, 3]},
               "final_ticket": {"tickets": [{"selection": [1, 3], "stake": 100}]},
               "minimum_efficient_coverage": {"tickets": [{"selection": [1, 3], "stake": 100}]}}
    if where == "malformed_ticket":
        payload["final_ticket"]["tickets"] = ["invalid"]
    elif where == "malformed_ranking":
        payload["final_prediction_package"]["ranking"] = 9
    elif where == "malformed_fpp":
        payload["final_prediction_package"] = ["invalid"]
    elif where == "ranking":
        payload["final_prediction_package"]["ranking"].append(2)
    elif where == "nested_mec":
        payload["final_prediction_package"]["minimum_efficient_coverage"] = {"tickets": [{"selection": [1, 2]}]}
    elif where:
        payload[where]["tickets"][0]["selection"] = [1, 2]
    if where:
        with pytest.raises(EndpointHold, match="SOURCE_FINAL_RUNNER_UNIVERSE_MISMATCH"):
            scope["final"](payload)
        assert called == []
    else:
        scope["final"](payload)
        assert called == [payload]
