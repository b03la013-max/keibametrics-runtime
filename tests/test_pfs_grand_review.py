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


# Single WIN/PLACE observations are explicitly non-Production and must not
# modify the preregistered hash-frozen PFS runtime above.
def _formal_single(race="KM-LOCAL-KAW-20261016-R01-LIVE-R1", investment=200, payout=0):
    return {"race_id": race, "formal_class": "FORMAL_PRE_RACE",
            "pfs_authority": "FROZEN-RECOMMENDATION-PFS",
            "investment": investment, "return": payout}


def _settled_single(tmp_path, race, breakdown, *, grade="FORMAL-PRE-RACE", suffix="one"):
    folder = tmp_path / "runtime/results"
    folder.mkdir(parents=True, exist_ok=True)
    record = {"race_id": race, "formal_grade": grade,
              "settlement": {"status": "SETTLED",
                             "pfs_authority": "FROZEN-RECOMMENDATION-PFS",
                             "bet_type_summary": breakdown}}
    (folder / (suffix + ".json")).write_text(json.dumps(record), encoding="utf-8")
    return folder


def test_local_single_zero_is_settled_loss_not_missing_or_actual_purchase(tmp_path):
    from research import local_single_win_place_review as review
    row = _formal_single()
    root = _settled_single(tmp_path, row["race_id"], [
        {"bet_type": "WIN", "investment": 100, "payout": 0},
        {"bet_type": "PLACE", "investment": 100, "payout": 0}])
    result = review.build_report([row], result_dir=root)
    assert result["purchase_inferred"] is False
    assert result["official_prestart_receipts_independently_verified"] is False
    assert result["qualifying_frozen_formal_races"] == 1
    assert result["races_with_single_type_records"] == 1
    for bt in ("WIN", "PLACE"):
        arm = result["bet_types"][bt]
        assert arm["aggregate"]["settled_race_count"] == 1
        assert arm["aggregate"]["investment"] == 100
        assert arm["aggregate"]["return"] == 0
        assert arm["aggregate"]["pfs_pct"] == 0.0
        assert arm["upper_and_lower_1pct_removed"]["status"] == "INSUFFICIENT_SAMPLE"


def test_local_single_unknown_type_is_not_zero_pfs(tmp_path):
    from research import local_single_win_place_review as review
    row = _formal_single()
    root = _settled_single(tmp_path, row["race_id"], [])
    result = review.build_report([row], result_dir=root)
    assert result["races_with_single_type_records"] == 0
    assert result["bet_types"]["WIN"]["aggregate"]["pfs_pct"] is None
    assert result["bet_types"]["PLACE"]["aggregate"]["pfs_pct"] is None


def test_local_single_reference_results_never_infer_frozen_ticket(tmp_path):
    from research import local_single_win_place_review as review
    row = _formal_single()
    row["formal_class"] = "OTHER"
    root = _settled_single(tmp_path, row["race_id"], [
        {"bet_type": "WIN", "investment": 100, "payout": 1300}])
    result = review.build_report([row], result_dir=root)
    assert result["qualifying_frozen_formal_races"] == 0
    assert result["bet_types"]["WIN"]["aggregate"]["pfs_pct"] is None


def test_local_single_symmetric_tail_trim_no_cherry_picking():
    from research import local_single_win_place_review as review
    rows = [{"race_id": f"R{i:03d}", "investment": 100,
             "return": (0 if i == 0 else 10000 if i == 99 else 100)}
            for i in range(100)]
    assert review._aggregate(rows)["pfs_pct"] == 198.0
    one = review._tail_check(rows, 1)
    three = review._tail_check(rows, 3)
    assert one["removed_each_side"] == 1 and one["aggregate"]["pfs_pct"] == 100.0
    assert three["removed_each_side"] == 3 and three["aggregate"]["pfs_pct"] == 100.0
    assert review._tail_check(rows[:10], 1)["status"] == "INSUFFICIENT_SAMPLE"


def test_local_single_duplicate_result_source_is_quarantined(tmp_path):
    from research import local_single_win_place_review as review
    row = _formal_single()
    root = _settled_single(tmp_path, row["race_id"], [{"bet_type": "WIN", "investment": 100, "payout": 0}])
    _settled_single(tmp_path, row["race_id"], [{"bet_type": "WIN", "investment": 100, "payout": 0}], suffix="two")
    report = review.build_report([row], result_dir=root)
    assert report["held"][0]["reason"] == "DUPLICATE_RESULT_SOURCE"
    assert report["bet_types"]["WIN"]["aggregate"]["pfs_pct"] is None


def test_local_single_requires_formal_frozen_settlement_source(tmp_path):
    from research import local_single_win_place_review as review
    row = _formal_single()
    root = _settled_single(tmp_path, row["race_id"], [
        {"bet_type": "WIN", "investment": 100, "payout": 0}], grade="POST-START-REPLAY")
    report = review.build_report([row], result_dir=root)
    assert report["held"][0]["reason"] == "FROZEN_PRESTART_TYPE_SOURCE_UNPROVEN"
    assert report["bet_types"]["WIN"]["aggregate"]["pfs_pct"] is None


def test_local_single_type_exceeding_frozen_total_is_quarantined(tmp_path):
    from research import local_single_win_place_review as review
    row = _formal_single(investment=100, payout=100)
    root = _settled_single(tmp_path, row["race_id"], [
        {"bet_type": "WIN", "investment": 100, "payout": 200}])
    report = review.build_report([row], result_dir=root)
    assert report["held"][0]["reason"] == "TYPE_BREAKDOWN_CONTRADICTS_FROZEN_TOTAL"
    assert report["bet_types"]["WIN"]["aggregate"]["pfs_pct"] is None


def test_local_single_dict_type_breakdown_preserves_zero(tmp_path):
    from research import local_single_win_place_review as review
    row = _formal_single(investment=100)
    root = tmp_path / "runtime/results"
    root.mkdir(parents=True)
    source = {"race_id": row["race_id"], "formal_grade": "FORMAL-PRE-RACE",
              "settlement": {"status": "SETTLED", "pfs_authority": "FROZEN-RECOMMENDATION-PFS",
                             "by_bet_type": {"WIN": {"investment": 100, "return": 0}}}}
    (root / "one.json").write_text(json.dumps(source))
    assert review.build_report([row], result_dir=root)["bet_types"]["WIN"]["aggregate"]["pfs_pct"] == 0.0


def test_local_single_invalid_money_never_enters_roi(tmp_path):
    from research import local_single_win_place_review as review
    assert review._number(True) is None
    assert review._number(float("nan")) is None
    assert review._number(float("inf")) is None
    row = _formal_single(investment=100)
    root = _settled_single(tmp_path, row["race_id"], [
        {"bet_type": "WIN", "investment": 100, "payout": float("nan")}])
    report = review.build_report([row], result_dir=root)
    assert report["held"][0]["reason"] == "TYPE_BREAKDOWN_CONTRADICTS_FROZEN_TOTAL"
