import json, os
from pathlib import Path

def test_pfs_grand_review_dedup_and_formal_split(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for d in ["runtime/performance_ledger","runtime/reviews","runtime/reviews_auto","runtime/results"]:
        Path(d).mkdir(parents=True,exist_ok=True)

    rid="20260922-NKY-R99"
    ledger={
      "race_id":rid,
      "formal_grade":"FORMAL-PRE-RACE / FULL_FORMAL_E2E_PASS",
      "model_comparison_eligibility":"ELIGIBLE",
      "pfs_authority":"FROZEN-RECOMMENDATION-PFS",
      "investment":1000,"return":1200,"pfs":120.0
    }
    review={
      "race_id":rid,
      "formal_grade":"FORMAL-PRE-RACE",
      "model_comparison_eligibility":"ELIGIBLE",
      "measurement":{"pfs_authority":"FROZEN-RECOMMENDATION-PFS","investment":1000,"return":1200,"pfs":120.0}
    }
    result={
      "race_id":rid,
      "settlement":{"status":"SETTLED","pfs_authority":"FROZEN-RECOMMENDATION-PFS","total_investment":1000,"total_payout":1200,"pfs":120.0},
      "frozen_prediction_ref":{"final_status":"FORMAL-PRE-RACE"},
      "learning_event":{"model_comparison_eligibility":"ELIGIBLE"}
    }
    Path("runtime/performance_ledger/x.json").write_text(json.dumps(ledger),encoding="utf-8")
    Path("runtime/reviews/x.json").write_text(json.dumps(review),encoding="utf-8")
    Path("runtime/results/x.json").write_text(json.dumps(result),encoding="utf-8")

    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import pfs_grand_review as p

    rows=p.canonical_records()
    assert len(rows)==1
    assert rows[0]["source_path"].startswith("runtime/performance_ledger/")
    r=p.build_report()
    assert r["cohorts"]["ALL_FROZEN_RECOMMENDATION"]["race_count"]==1
    assert r["cohorts"]["FORMAL_PRE_RACE"]["investment_weighted_pfs"]==120.0
    assert r["cohorts"]["MODEL_COMPARISON_ELIGIBLE"]["investment_weighted_pfs"]==120.0

def test_post_start_is_not_formal_pre_race(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("runtime/performance_ledger").mkdir(parents=True,exist_ok=True)
    for d in ["runtime/reviews","runtime/reviews_auto","runtime/results"]:
        Path(d).mkdir(parents=True,exist_ok=True)
    x={
      "race_id":"20260922-NKY-R98",
      "formal_grade":"POST-START-REPLAY / FULL_FORMAL_E2E_PASS",
      "model_comparison_eligibility":"INELIGIBLE",
      "pfs_authority":"FROZEN-RECOMMENDATION-PFS",
      "investment":1000,"return":500,"pfs":50.0
    }
    Path("runtime/performance_ledger/x.json").write_text(json.dumps(x),encoding="utf-8")

    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import importlib, pfs_grand_review
    importlib.reload(pfs_grand_review)
    r=pfs_grand_review.build_report()
    assert r["cohorts"]["ALL_FROZEN_RECOMMENDATION"]["race_count"]==1
    assert r["cohorts"]["FORMAL_PRE_RACE"]["race_count"]==0


def test_auto_review_capital_authority_counts_as_frozen_recommendation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for d in ["runtime/performance_ledger","runtime/reviews","runtime/reviews_auto","runtime/results"]:
        Path(d).mkdir(parents=True,exist_ok=True)

    x={
      "race_id":"20260921-HSN-R11",
      "formal_grade":"POST-START-REPLAY",
      "capital":{
        "authority":"FROZEN-RECOMMENDATION-PFS",
        "investment":1400,
        "return":1420,
        "pfs":101.428571429
      }
    }
    Path("runtime/reviews_auto/x.json").write_text(json.dumps(x),encoding="utf-8")

    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import importlib, pfs_grand_review
    importlib.reload(pfs_grand_review)
    r=pfs_grand_review.build_report()
    assert r["cohorts"]["ALL_FROZEN_RECOMMENDATION"]["race_count"]==1
    assert r["cohorts"]["ALL_FROZEN_RECOMMENDATION"]["investment"]==1400
    assert r["cohorts"]["ALL_FROZEN_RECOMMENDATION"]["return"]==1420


def test_source_candidate_oos_pfs_is_separate_and_tier_measured(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for d in ["runtime/performance_ledger","runtime/reviews","runtime/reviews_auto","runtime/results",
              "runtime/source_candidate_results"]:
        Path(d).mkdir(parents=True,exist_ok=True)
    rid="KM-JRA-HSN-20990101-R01"
    od=Path("runtime/source_candidate_oos")/rid
    od.mkdir(parents=True,exist_ok=True)
    (od/"result_evaluation.json").write_text(json.dumps({
      "race_id":rid,"oos_eligible":True,"result_evaluation":{"actual_top3":[1,2,3]}
    }),encoding="utf-8")
    (od/"candidate_final.json").write_text(json.dumps({
      "race_id":rid,"candidate_only":True,
      "mec":{"tickets":[
        {"bet_type":"EXACTA","selection":[1,2],"stake":100,"mec_tier":"CORE"},
        {"bet_type":"TRIO","selection":[1,2,3],"stake":100,"mec_tier":"PROTECTION"},
        {"bet_type":"TRIO","selection":[1,2,4],"stake":100,"mec_tier":"TAIL"}
      ]}
    }),encoding="utf-8")
    Path("runtime/source_candidate_results",rid+".json").write_text(json.dumps({
      "race_id":rid,
      "settlement":{
        "status":"SETTLED",
        "pfs_authority":"CANDIDATE-FROZEN-RECOMMENDATION-PFS",
        "actual_ticket_status":"UNVERIFIED",
        "total_investment":300,"total_payout":900,"pfs":300.0,
        "winning_tickets":[
          {"bet_type":"TRIO","selection":[1,2,3],"stake":100,"payout_per_100":900,"payout":900}
        ],
        "bet_type_summary":[
          {"bet_type":"EXACTA","investment":100,"payout":0},
          {"bet_type":"TRIO","investment":200,"payout":900}
        ]
      }
    }),encoding="utf-8")

    import sys, importlib
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import pfs_grand_review
    importlib.reload(pfs_grand_review)
    r=pfs_grand_review.build_report()
    assert r["cohorts"]["FORMAL_PRE_RACE"]["race_count"]==0
    c=r["candidate_forward_oos"]
    assert c["eligible_race_count"]==1
    assert c["settled_race_count"]==1
    assert c["aggregate"]["investment_weighted_pfs"]==300.0
    assert c["mec_capital_density"]["tiers"]["TAIL"]["capital_share_pct"]==33.333333
    assert c["tier_pfs"]["tiers"]["CORE"]["pfs"]==0.0
    assert c["tier_pfs"]["tiers"]["PROTECTION"]["pfs"]==900.0
    assert c["tier_pfs"]["tiers"]["TAIL"]["pfs"]==0.0
    assert c["production_effect"]=="NONE"


def test_auto_postresult_settlement_updates_candidate_and_tiers_without_actual_promotion(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for path in ("runtime/performance_ledger", "runtime/reviews",
                 "runtime/reviews_auto", "runtime/results", "runtime/source_candidate_oos"):
        Path(path).mkdir(parents=True, exist_ok=True)
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import pfs_grand_review as p
    rid="KM-JRA-KYO-20990101-R03"
    home=Path("runtime/source_candidate_oos")/rid
    home.mkdir(parents=True)
    source="signed-source-sha"
    pre={"race_id":rid,"oos_eligible":True,"candidate_final_verified":True,
         "source_snapshot_sha256":source}
    pre["sha256"]=p._sha(pre)
    final={"race_id":rid,"candidate_only":True,"source_snapshot_sha256":source,
           "mec":{"tickets":[
             {"bet_type":"EXACTA","selection":[4,8],"stake":100,"mec_tier":"CORE"},
             {"bet_type":"TRIFECTA","selection":[4,8,3],"stake":100,"mec_tier":"PROTECTION"},
           ]}}
    final["sha256"]=p._sha(final)
    settlement={
        "race_id":rid,"status":"SETTLED_FROZEN_CANDIDATE_RECOMMENDATION",
        "production_effect":"NONE","automatic_promotion":False,
        "actual_purchase_status":"UNVERIFIED",
        "frozen_pre_result_sha256":pre["sha256"],
        "frozen_candidate_final_sha256":final["sha256"],
        "recommended_stake_yen":200,"recommended_return_yen":850,
        "purchased_ticket_count":2,
        "frozen_tickets":[
          {"bet_type":"EXACTA","selection":[4,8],"stake":100,"recommended_return":0},
          {"bet_type":"TRIFECTA","selection":[4,8,3],"stake":100,"recommended_return":850},
        ],
    }
    settlement["sha256"]=p._sha(settlement)
    evaluated={"race_id":rid,"oos_eligible":True,
               "settlement_sha256":settlement["sha256"]}
    evaluated["sha256"]=p._sha(evaluated)
    for n,doc in (("pre_result.json",pre),("candidate_final.json",final),
                  ("settlement.json",settlement),("result_evaluation.json",evaluated)):
        (home/n).write_text(json.dumps(doc),encoding="utf-8")
    report=p.build_report()
    c=report["candidate_forward_oos"]
    assert c["eligible_race_count"]==1
    assert c["settled_race_count"]==1
    assert c["aggregate"]["investment"]==200
    assert c["aggregate"]["return"]==850
    assert c["aggregate"]["investment_weighted_pfs"]==425.0
    assert c["tier_pfs"]["tiers"]["CORE"]["return"]==0
    assert c["tier_pfs"]["tiers"]["PROTECTION"]["return"]==850
    assert report["actual_pfs"]["verified_race_count"]==0
    assert report["cohorts"]["FORMAL_PRE_RACE"]["race_count"]==0

    # A legacy RESULT for the same race must not double the Candidate PFS.
    Path("runtime/source_candidate_results").mkdir(parents=True)
    legacy={"race_id":rid,"settlement":{
      "status":"SETTLED","total_investment":200,"total_payout":850,
      "pfs_authority":"CANDIDATE-FROZEN-RECOMMENDATION-PFS"}}
    (Path("runtime/source_candidate_results")/(rid+".json")).write_text(
        json.dumps(legacy),encoding="utf-8")
    report=p.build_report()
    assert report["candidate_forward_oos"]["settled_race_count"]==1
    assert report["candidate_forward_oos"]["aggregate"]["investment"]==200

    legacy["settlement"]["total_payout"]=900
    (Path("runtime/source_candidate_results")/(rid+".json")).write_text(
        json.dumps(legacy),encoding="utf-8")
    import pytest
    with pytest.raises(ValueError,match="CANDIDATE_PFS_DOUBLE_SOURCE_CONFLICT"):
        p.build_report()


def test_live_repo_kyoto_r03_immutable_candidate_settlement_is_aggregatable(monkeypatch):
    repo=Path(__file__).resolve().parents[1]
    monkeypatch.chdir(repo)
    import sys
    sys.path.insert(0,str(repo/"runtime"))
    import pfs_grand_review as p
    rows={x["race_id"]:x for x in p._candidate_automatic_settlements()}
    rid="KM-JRA-KYO-20261010-R03"
    assert rid in rows
    assert rows[rid]["investment"]==1400
    assert rows[rid]["return"]==0
    assert rows[rid]["actual_ticket_status"]=="UNVERIFIED"
    merged=[x for x in p._candidate_forward_records() if x["race_id"]==rid]
    assert len(merged)==1
    assert merged[0]["formal_class"]=="FROZEN_OOS_CANDIDATE"
