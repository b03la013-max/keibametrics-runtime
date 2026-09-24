import json
from pathlib import Path

def _write(path,obj):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj),encoding="utf-8")

def _arm(inv=100,ret=120):
    return {"status":"SETTLED","investment":inv,"return":ret,"profit_loss":ret-inv,"pfs":ret/inv*100,"ticket_count":1}

def _official(rid):
    _write(f"runtime/family_result_requests/{rid}-RESULT.json",{
      "race_id":rid,"official_result_verified":True,
      "source":"TEST_OFFICIAL_RESULT","official_result_verification_ref":"TEST:OFFICIAL"
    })

def test_mec_r4_oos_counts_only_preregistered_formal_pre_race(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import importlib, mec_r4_oos_tracker as m
    importlib.reload(m)
    monkeypatch.setattr(m,"ACTIVATION_AT","2026-09-22T21:08:00+09:00")

    arms={a:_arm() for a in m.EXPECTED_ARMS}

    # Eligible.
    rid="20260923-NKY-R01"
    _official(rid)
    final={"sha256":"FINAL1","final_ticket":{"tickets":[{"bet_type":"EXACTA","selection":[1,2],"stake":100}]}}
    shadow={
      "profile":m.CANDIDATE_PROFILE,"candidate_id":m.CANDIDATE_ID,
      "production_effect":"NONE","source_immutable_final_sha256":"FINAL1",
      "generated_at":"2026-09-23T10:00:00+09:00",
      "temporal_mode":"FORMAL-PRE-RACE","scheduled_post_at":"2026-09-23T10:10:00+09:00",
      "sha256":"SH1"
    }
    result={"race_id":rid,"sha256":"SET1","arms":arms}
    _write(f"runtime/final_artifacts/{rid}.json",final)
    _write(f"runtime/mec_shadow_artifacts/{rid}.json",shadow)
    _write(f"runtime/mec_shadow_results/{rid}.json",result)
    _write(f"runtime/results/{rid}.json",{"race_id":rid,"official_result":{"top3":[1,2,3],"payouts":{"exacta":{"1>2":150},"trio":{"1-2-3":200},"trifecta":{"1>2>3":500}}},"settlement":{"status":"SETTLED","total_investment":100,"total_payout":150}})

    # Post-start: never eligible.
    rid2="20260923-NKY-R02"
    _write(f"runtime/final_artifacts/{rid2}.json",{"sha256":"FINAL2","final_ticket":{"tickets":[]}})
    _write(f"runtime/mec_shadow_artifacts/{rid2}.json",{
      **shadow,"source_immutable_final_sha256":"FINAL2","sha256":"SH2",
      "temporal_mode":"POST-START-REPLAY"
    })
    _write(f"runtime/mec_shadow_results/{rid2}.json",{"race_id":rid2,"sha256":"SET2","arms":arms})

    # Before preregistration activation: never eligible.
    rid3="20260922-NKY-R03"
    _write(f"runtime/final_artifacts/{rid3}.json",{"sha256":"FINAL3","final_ticket":{"tickets":[]}})
    _write(f"runtime/mec_shadow_artifacts/{rid3}.json",{
      **shadow,"source_immutable_final_sha256":"FINAL3","sha256":"SH3",
      "generated_at":"2026-09-22T20:00:00+09:00",
      "scheduled_post_at":"2026-09-22T20:10:00+09:00"
    })
    _write(f"runtime/mec_shadow_results/{rid3}.json",{"race_id":rid3,"sha256":"SET3","arms":arms})

    out=m.build_status()
    assert out["eligible_races"]==1
    assert out["remaining_races"]==29
    assert out["entries"][0]["race_id"]=="20260923-NKY-R01"
    assert out["aggregates"]["CPSS_ALL"]["investment_weighted_pfs"]==120.0
    assert out["aggregates"]["PRODUCTION_BASELINE_R3"]["investment_weighted_pfs"]==150.0
    assert out["comparison_vs_production"]["CPSS_ALL"]["pfs_points"]==-30.0

def test_arm_set_mismatch_is_rejected(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import importlib, mec_r4_oos_tracker as m
    importlib.reload(m)

    rid="20260923-NKY-R04"
    _official(rid)
    _write(f"runtime/final_artifacts/{rid}.json",{"sha256":"F","final_ticket":{"tickets":[]}})
    _write(f"runtime/mec_shadow_artifacts/{rid}.json",{
      "profile":m.CANDIDATE_PROFILE,"candidate_id":m.CANDIDATE_ID,"production_effect":"NONE",
      "source_immutable_final_sha256":"F","generated_at":"2026-09-23T11:00:00+09:00",
      "temporal_mode":"FORMAL-PRE-RACE","scheduled_post_at":"2026-09-23T11:10:00+09:00","sha256":"S"
    })
    _write(f"runtime/mec_shadow_results/{rid}.json",{
      "race_id":rid,"sha256":"R","arms":{"CPSS_ALL":_arm()}
    })
    out=m.build_status()
    assert out["eligible_races"]==0
    assert any(x["reason"]=="ARM_SET_MISMATCH" for x in out["errors"])


def test_local_signed_final_bound_lineage_is_eligible(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import importlib, mec_r4_oos_tracker as m
    importlib.reload(m)

    rid="URW-20260924-R01-FORMAL-R1"
    _official(rid)
    shadow={
      "profile":m.CANDIDATE_PROFILE,"candidate_id":m.CANDIDATE_ID,
      "production_effect":"NONE","source_immutable_final_sha256":"BASIS1",
      "generated_at":"2026-09-24T10:00:00+09:00",
      "temporal_mode":"FORMAL-PRE-RACE","scheduled_post_at":"2026-09-24T10:10:00+09:00",
      "sha256":"SHLOCAL",
      "arms":{a:{"core_structure_retention_ratio":1.0,"semantic_information_retention_ratio":1.0,"generic_tail_capital_avoided":0} for a in m.EXPECTED_ARMS}
    }
    arms={a:_arm(inv=100,ret=200) for a in m.EXPECTED_ARMS}
    _write(f"runtime/mec_shadow_artifacts/{rid}.json",shadow)
    _write(f"runtime/mec_shadow_results/{rid}.json",{"race_id":rid,"sha256":"SETLOCAL","arms":arms})
    prod_result={"official_result":{"top3":[1,2,3],"payouts":{"exacta":{"1>2":150},"trio":{"1-2-3":200},"trifecta":{"1>2>3":500}}}}
    _write(f"runtime/mec_shadow_lineage/{rid}.json",{
      "lineage_type":"LOCAL_SIGNED_FINAL_BOUND","race_id":rid,
      "binding_valid":True,"shadow_sha256":"SHLOCAL","basis_sha256":"BASIS1",
      "final_receipt_sha256":"FR","final_artifact_sha256":"FA",
      "production_tickets":[{"bet_type":"EXACTA","selection":[1,2],"stake":100}],
      "production_result":prod_result,
      "production_settlement":{"status":"SETTLED","total_investment":100,"total_payout":150}
    })
    out=m.build_status()
    assert out["eligible_races"]==1
    assert out["entries"][0]["lineage_type"]=="LOCAL_SIGNED_FINAL_BOUND"
    assert out["entries"][0]["source_final_sha256"]=="FA"
    assert out["aggregates"]["PRODUCTION_BASELINE_R3"]["investment_weighted_pfs"]==150.0
    assert out["aggregates"]["CPSS_ALL"]["investment_weighted_pfs"]==200.0


def test_local_unbound_shadow_is_rejected(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import importlib, mec_r4_oos_tracker as m
    importlib.reload(m)

    rid="URW-20260924-R02-FORMAL-R1"
    _official(rid)
    shadow={
      "profile":m.CANDIDATE_PROFILE,"candidate_id":m.CANDIDATE_ID,
      "production_effect":"NONE","source_immutable_final_sha256":"BASIS2",
      "generated_at":"2026-09-24T11:00:00+09:00",
      "temporal_mode":"FORMAL-PRE-RACE","scheduled_post_at":"2026-09-24T11:10:00+09:00",
      "sha256":"SH2","arms":{}
    }
    _write(f"runtime/mec_shadow_artifacts/{rid}.json",shadow)
    _write(f"runtime/mec_shadow_results/{rid}.json",{"race_id":rid,"sha256":"SET2","arms":{a:_arm() for a in m.EXPECTED_ARMS}})
    _write(f"runtime/mec_shadow_lineage/{rid}.json",{
      "lineage_type":"LOCAL_SIGNED_FINAL_BOUND","race_id":rid,
      "binding_valid":False,"shadow_sha256":"SH2","basis_sha256":"BASIS2"
    })
    out=m.build_status()
    assert out["eligible_races"]==0
    assert any(x["reason"]=="LOCAL_SIGNED_FINAL_BINDING_INVALID" for x in out["errors"])

def test_result_authority_is_required_for_oos_admission(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import importlib, mec_r4_oos_tracker as m
    importlib.reload(m)
    rid="URW-20260924-R99-FORMAL-R1"
    shadow={
      "profile":m.CANDIDATE_PROFILE,"candidate_id":m.CANDIDATE_ID,
      "production_effect":"NONE","source_immutable_final_sha256":"B99",
      "generated_at":"2026-09-24T12:00:00+09:00",
      "temporal_mode":"FORMAL-PRE-RACE","scheduled_post_at":"2026-09-24T12:10:00+09:00",
      "sha256":"S99","arms":{a:{"core_structure_retention_ratio":1.0,"semantic_information_retention_ratio":1.0,"generic_tail_capital_avoided":0} for a in m.EXPECTED_ARMS}
    }
    _write(f"runtime/mec_shadow_artifacts/{rid}.json",shadow)
    _write(f"runtime/mec_shadow_results/{rid}.json",{"race_id":rid,"sha256":"SET99","arms":{a:_arm() for a in m.EXPECTED_ARMS}})
    _write(f"runtime/mec_shadow_lineage/{rid}.json",{
      "lineage_type":"LOCAL_SIGNED_FINAL_BOUND","binding_valid":True,
      "shadow_sha256":"S99","basis_sha256":"B99","final_receipt_sha256":"FR99","final_artifact_sha256":"FA99",
      "production_tickets":[],"production_result":{},"production_settlement":{"status":"SETTLED","total_investment":0,"total_payout":0}
    })
    out=m.build_status()
    assert out["eligible_races"]==0
    assert out["held_races"]==1
    assert out["held"][0]["reason"]=="RESULT_AUTHORITY_NOT_VERIFIED"
