"""FNB R9 as-of: reject future racing history before 29-index calculation."""
from __future__ import annotations

import inspect
import pytest

from runtime.local_fnb_r9_history_asof import assert_result_blind
from runtime import local_fullnumerical_production as production


def _case():
    request={"venue_id":"FNB","race_id":"KM-LOCAL-FNB-20261102-R01-LIVE-R1",
             "race_date":"2026-11-02",
             "prediction_cutoff":"2026-11-02T14:40:00+09:00",
             "runners":[{"runner_id":"1"}]}
    source={"source_freeze_at":"2026-11-02T14:00:00+09:00"}
    compiled={"runners":[{"runner_id":"1",
        "raw_candidate_evidence":{
            "race_card_fetched_at":"2026-11-02T13:55:00+09:00",
            "starts":[{"date":"26.10.19"},{"date":"26.09.23"}]}}]}
    return compiled,source,request


def test_r9_valid_past_history_with_explicit_unknown_count():
    compiled,source,request=_case()
    compiled["runners"][0]["raw_candidate_evidence"]["starts"].append({"date":"?"})
    proof=assert_result_blind(compiled,source,request)
    assert proof["status"]=="PRE_RACE_DATED_HISTORY_CHECKED"
    assert proof["dated_starts"]==2
    assert proof["undated_starts_unknown"]==1
    assert proof["post_result_start_used"] is False


@pytest.mark.parametrize("date",["26.11.02","26.11.03","2026-11-06"])
def test_r9_future_and_same_race_history_are_hard_hold(date):
    compiled,source,request=_case()
    compiled["runners"][0]["raw_candidate_evidence"]["starts"][0]["date"]=date
    with pytest.raises(ValueError,match="FNB_FUTURE_OR_SAME_RACE_HISTORICAL_START"):
        assert_result_blind(compiled,source,request)


def test_r9_unsorted_history_fails_instead_of_using_wrong_recency_weights():
    compiled,source,request=_case()
    compiled["runners"][0]["raw_candidate_evidence"]["starts"].reverse()
    with pytest.raises(ValueError,match="FNB_HISTORY_NOT_NEWEST_FIRST"):
        assert_result_blind(compiled,source,request)


def test_r9_source_fetched_after_cutoff_and_naive_timestamp_hold():
    compiled,source,request=_case()
    compiled["runners"][0]["raw_candidate_evidence"]["race_card_fetched_at"]=(
        "2026-11-02T14:41:00+09:00")
    with pytest.raises(ValueError,match="FNB_HISTORICAL_RAW_OBSERVED_AFTER_FREEZE"):
        assert_result_blind(compiled,source,request)
    compiled,source,request=_case()
    source["source_freeze_at"]="2026-11-02T14:00:00"
    with pytest.raises(ValueError,match="FNB_SOURCE_ASOF_NAIVE_TIMESTAMP"):
        assert_result_blind(compiled,source,request)


def test_r9_materializer_contains_fnb_only_asof_before_score_acceptance():
    code=inspect.getsource(production.materialize_production)
    assert 'if request.get("venue_id") == "FNB":' in code
    assert "assert_result_blind(compiled, source_artifact, request)" in code
    assert 'out["fnb_historical_asof_preflight"]' in code
