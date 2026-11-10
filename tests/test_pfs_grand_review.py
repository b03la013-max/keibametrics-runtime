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


def test_formal_single_win_place_report_uses_only_declared_frozen_stakes():
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import pfs_grand_review as p
    formal={"race_id":"KM-LOCAL-KAW-20261016-R01-LIVE-R1","date":"20261016",
            "formal_class":"FORMAL_PRE_RACE","pfs_authority":"FROZEN-RECOMMENDATION-PFS",
            "investment":200,"return":0,"bet_types":{
                "WIN":{"investment":100,"return":0},
                "PLACE":{"investment":100,"return":0}}}
    hypothetical_reference={**formal,"race_id":"KM-LOCAL-KAW-20261016-R02-LIVE-R1",
                            "formal_class":"OTHER",
                            "investment":200,"return":2000}
    measured=p._single_axis([formal,hypothetical_reference])
    assert measured["actual_purchase_inferred"] is False
    for bt in ("WIN","PLACE"):
        arm=measured["types"][bt]
        assert arm["settled_bet_races"]==1
        assert arm["aggregate"]["investment"]==100
        assert arm["aggregate"]["return"]==0
        assert arm["aggregate"]["investment_weighted_pfs"]==0.0
        assert arm["excluding_top_bottom_1pct"]["status"]=="INSUFFICIENT_SAMPLE"


def test_single_type_missing_is_unknown_not_zero_pfs():
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import pfs_grand_review as p
    formal={"race_id":"KM-LOCAL-KAW-20261016-R03-LIVE-R1",
            "formal_class":"FORMAL_PRE_RACE","pfs_authority":"FROZEN-RECOMMENDATION-PFS",
            "investment":300,"return":150,"bet_types":{}}
    single=p._single_axis([formal])
    assert single["types"]["WIN"]["aggregate"]["investment_weighted_pfs"] is None
    assert single["types"]["PLACE"]["aggregate"]["investment_weighted_pfs"] is None
    assert single["types"]["WIN"]["status"]=="NO_VERIFIED_SINGLE_TYPE_OBSERVATIONS"


def test_formal_win_place_tail_exclusion_is_symmetric_not_optimal_selection():
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import pfs_grand_review as p
    rows=[]
    for i in range(100):
        ret=0 if i==0 else (10000 if i==99 else 100)
        rows.append({"race_id":f"KM-LOCAL-KAW-20261016-R{i+1:03d}",
                     "date":"20261016","formal_class":"FORMAL_PRE_RACE",
                     "pfs_authority":"FROZEN-RECOMMENDATION-PFS",
                     "investment":100,"return":ret,
                     "bet_types":{"PLACE":{"investment":100,"return":ret}}})
    arm=p._single_axis(rows)["types"]["PLACE"]
    assert arm["aggregate"]["investment_weighted_pfs"]==198.0
    assert arm["excluding_top_bottom_1pct"]["excluded_each_tail"]==1
    assert arm["excluding_top_bottom_1pct"]["aggregate"]["investment_weighted_pfs"]==100.0
    assert arm["excluding_top_bottom_3pct"]["excluded_each_tail"]==3
    assert arm["excluding_top_bottom_3pct"]["aggregate"]["investment_weighted_pfs"]==100.0


def test_single_type_inconsistent_with_canonical_total_is_held():
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import pfs_grand_review as p
    row={"race_id":"KM-LOCAL-KAW-20261016-R02-LIVE-R1",
         "formal_class":"FORMAL_PRE_RACE","pfs_authority":"FROZEN-RECOMMENDATION-PFS",
         "investment":100,"return":100,
         "bet_types":{"WIN":{"investment":100,"return":200}}}
    arm=p._single_axis([row])["types"]["WIN"]
    assert arm["settled_bet_races"]==0
    assert arm["held"][0]["reason"]=="SINGLE_TYPE_SETTLEMENT_CONTRADICTS_CANONICAL_TOTAL"
    assert arm["aggregate"]["investment_weighted_pfs"] is None


def test_zero_payout_record_preserved_in_full_report(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for d in ["runtime/performance_ledger","runtime/reviews","runtime/reviews_auto","runtime/results"]:
        Path(d).mkdir(parents=True,exist_ok=True)
    race_id="KM-LOCAL-KAW-20261016-R03-LIVE-R1"
    result={"race_id":race_id,"formal_grade":"FORMAL-PRE-RACE",
            "settlement":{"status":"SETTLED",
                          "pfs_authority":"FROZEN-RECOMMENDATION-PFS",
                          "total_investment":200,"total_payout":0,"pfs":0,
                          "bet_type_summary":[
                              {"bet_type":"WIN","investment":100,"payout":0},
                              {"bet_type":"PLACE","investment":100,"payout":0}]}}
    Path("runtime/results/result.json").write_text(json.dumps(result),encoding="utf-8")
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import pfs_grand_review as p
    report=p.build_report()
    assert len(report["records"])==1
    assert report["records"][0]["bet_types"]["WIN"]["return"]==0
    assert report["records"][0]["bet_types"]["PLACE"]["return"]==0
    singles=report["formal_pre_race_single_win_place"]["types"]
    assert singles["WIN"]["aggregate"]["investment_weighted_pfs"]==0.0
    assert singles["PLACE"]["aggregate"]["investment_weighted_pfs"]==0.0
    assert report["model_comparison_eligible_single_win_place"]["types"]["WIN"]["status"]=="NO_VERIFIED_SINGLE_TYPE_OBSERVATIONS"


def test_result_dict_bet_type_breakdown_keeps_explicit_zero(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for d in ["runtime/performance_ledger","runtime/reviews","runtime/reviews_auto","runtime/results"]:
        Path(d).mkdir(parents=True,exist_ok=True)
    item={"race_id":"KM-LOCAL-KAW-20261016-R04-LIVE-R1","formal_grade":"FORMAL-PRE-RACE",
          "settlement":{"status":"SETTLED","pfs_authority":"FROZEN-RECOMMENDATION-PFS",
                        "total_investment":100,"total_payout":0,
                        "by_bet_type":{"WIN":{"investment":100,"return":0}}}}
    Path("runtime/results/result.json").write_text(json.dumps(item),encoding="utf-8")
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import pfs_grand_review as p
    records=p.canonical_records()
    assert records[0]["bet_types"]["WIN"]=={"investment":100.0,"return":0.0}
    assert p._single_axis(records)["types"]["WIN"]["aggregate"]["investment_weighted_pfs"]==0.0


def test_bool_and_nan_are_never_settled_financial_evidence():
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
    import pfs_grand_review as p
    assert p._num(True) is None
    assert p._num(False) is None
    assert p._num(float("nan")) is None
    assert p._num(float("inf")) is None
