import copy, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
from common_exact_continuity_shadow import (
    build_shadow,bind_shadow_to_trace,verify_signed_final_binding,settle_shadow,PROFILE,CANDIDATE_ID
)

def req():
    return {
      "race_id":"LOCAL-TEST-R1","temporal_mode":"FORMAL-PRE-RACE",
      "scheduled_post_at":"2099-01-01T12:00:00+09:00",
      "oos_policy":{"acceptance_only":False,"request_oos_eligible":True},
      "pair_dispositions":[
        {"head":"7","second":"2","status":"PROTECT","reason":"MATERIAL_PAIR"},
        {"head":"7","second":"8","status":"PURCHASE","reason":"CORE_PAIR"},
      ],
      "third_dispositions":[
        {"head":"7","second":"8","third":"2","status":"PURCHASE","reason":"CORE_EXACT"},
      ],
      "static_prediction":{"roles":{"2":["P2","P3"],"7":["W","P2","P3"],"8":["P2","P3"]}},
    }

def test_build_gap_and_krs_arms():
    q=req()
    final_package={"ranking":["7","2","8"],"roles":q["static_prediction"]["roles"]}
    final_ticket={"tickets":[
      {"bet_type":"EXACTA","selection":[7,2],"stake":100,"mec_tier":"PROTECTION"},
      {"bet_type":"EXACTA","selection":[7,8],"stake":100,"mec_tier":"CORE"},
      {"bet_type":"TRIFECTA","selection":[7,8,2],"stake":100,"mec_tier":"CORE"},
    ]}
    krs={"top_trifecta_occurrence":[
      {"W":7,"P2":2,"P3":8,"count":100,"frequency":0.1},
      {"W":7,"P2":8,"P3":2,"count":90,"frequency":0.09},
    ]}
    sh=build_shadow(q,final_ticket,final_package,krs,"2099-01-01T02:00:00+00:00","BASIS")
    assert sh["profile"]==PROFILE and sh["candidate_id"]==CANDIDATE_ID
    assert "7>2>8" in sh["arms"]["CONTINUITY_ALL"]
    assert "7>2>8" in sh["arms"]["KRS_TOP1"]
    assert "7>8>2" not in sh["arms"]["CONTINUITY_ALL"]
    assert sh["production_effect"]=="NONE"
    assert sh["automatic_purchase"] is False
    assert sh["capital_width_diagnostics"]["oos_arm"] is False

def test_signed_final_binding_and_settlement():
    q=req();fp={"ranking":["7","2","8"],"roles":q["static_prediction"]["roles"]}
    ft={"tickets":[{"bet_type":"EXACTA","selection":[7,2],"stake":100}]}
    ku={"top_trifecta_occurrence":[{"W":7,"P2":2,"P3":8,"count":100,"frequency":0.1}]}
    sh=build_shadow(q,ft,fp,ku,"2099-01-01T02:00:00+00:00","BASIS")
    trace=bind_shadow_to_trace({},sh)
    env={"artifact":{"ticket_transport_trace":trace},"receipt":{"phase":"FINAL","status":"PASS","artifact_sha256":"FA"},"receipt_sha256":"FR"}
    att=verify_signed_final_binding(env,sh)
    assert att["valid"] is True
    res=settle_shadow(sh,[7,2,8],{"TRIFECTA":1080},1000,500,True)
    assert res["oos_eligible"] is True
    assert res["arms"]["CONTINUITY_ALL"]["rescue_hit"] is True
    assert res["arms"]["KRS_TOP1"]["rescue_hit"] is True


def test_mutated_content_cannot_retain_bound_sha():
    import pytest
    q=req();sh=build_shadow(q,{'tickets':[]},{'roles':q['static_prediction']['roles']},{},'2099-01-01T02:00:00Z','B')
    env={'receipt':{'phase':'FINAL','status':'PASS'},'artifact':{'ticket_transport_trace':bind_shadow_to_trace({},sh)}}
    sh['arms']['CONTINUITY_ALL'].append('1>2>3')
    with pytest.raises(AssertionError,match='CONTENT_HASH_MISMATCH'):
        verify_signed_final_binding(env,sh)
    with pytest.raises(AssertionError,match='CONTENT_HASH_MISMATCH'):
        settle_shadow(sh,[1,2,3],{'TRIFECTA':1000},100,0,True)


def test_missing_payout_is_not_zero_return():
    import pytest
    q=req();sh=build_shadow(q,{'tickets':[]},{'roles':q['static_prediction']['roles']},{},'2099-01-01T02:00:00Z','B')
    with pytest.raises(AssertionError,match='OFFICIAL_PAYOUT_REQUIRED'):
        settle_shadow(sh,[7,2,8],{},100,0,True)


def test_tracker_accepts_valid_lineage_rejects_mutation(monkeypatch,tmp_path):
    import json,hashlib
    from common_exact_continuity_oos_tracker import build_status
    q=req();sh=build_shadow(q,{'tickets':[]},{'roles':q['static_prediction']['roles']},{},'2099-01-01T02:00:00Z','B')
    res=settle_shadow(sh,[7,2,8],{'TRIFECTA':1000},100,0,True)
    line={'race_id':q['race_id'],'lineage_type':'COMMON_EXACT_CONTINUITY_SIGNED_FINAL_BOUND',
          'binding_valid':True,'shadow_sha256':sh['sha256'],'basis_sha256':'B','production_effect':'NONE'}
    line['sha256']=hashlib.sha256(json.dumps(line,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    monkeypatch.chdir(tmp_path)
    for folder,obj in [('common_exact_continuity_shadow_artifacts',sh),('common_exact_continuity_shadow_results',res),('common_exact_continuity_shadow_lineage',line),('family_result_requests',{'race_id':q['race_id'],'official_result_verified':True})]:
        p=tmp_path/'runtime'/folder;p.mkdir(parents=True)
        (p/(q['race_id']+'.json')).write_text(json.dumps(obj))
    assert build_status()['eligible_races']==1
    p=tmp_path/'runtime/common_exact_continuity_shadow_results'/(q['race_id']+'.json')
    res['arms']['KRS_TOP1']['return']=99999999;p.write_text(json.dumps(res))
    status=build_status()
    assert status['eligible_races']==0
    assert status['errors'][0]['reason']=='CONTENT_HASH_MISMATCH'
