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
