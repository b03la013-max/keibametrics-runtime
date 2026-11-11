"""Regression for an ordinal REFERENCE cohort, never a production scorecard."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from tools.local_reference_diagnostic import evaluate


COHORT = {
    "classification": "POSTRESULT_DIAGNOSTIC",
    "reference_sha256": "fixture digest",
    "races": [
        {"race_no": 1, "predicted_order": [1, 2, 3, 4], "actual_order": [1, 2, 3, 4]},
        {"race_no": 2, "predicted_order": [1, 2, 3, 4], "actual_order": [4, 3, 2, 1]},
    ],
}


def test_point_forecast_metrics_and_pfs_boundaries():
    result = evaluate(None, COHORT)
    assert result["original_reference_bytes_verified"] is False
    assert result["race_count"] == 2 and result["runner_count"] == 8
    assert result["position_matches"] == [1, 1, 1]
    assert result["top3_capture"] == 5 and result["top3_set_matches"] == 1
    assert result["ordered_pair_matches"] == result["exact_order_matches"] == 1
    assert [r["spearman_full_order"] for r in result["rows"]] == [1, -1]
    assert result["rows"][1]["third_after_correct_pair"] is None
    assert result["formal_pfs"] is result["reference_pfs"] is None
    assert result["actual_purchase_pfs"] == "UNKNOWN" and result["new_oos_credit"] == 0


@pytest.mark.parametrize("mutation", ["empty", "duplicate_race", "duplicate_prediction", "incomplete_result", "formal"])
def test_ineligible_cohort_does_not_receive_quality_credit(mutation):
    cohort = copy.deepcopy(COHORT)
    if mutation == "empty":
        cohort["races"] = []
    elif mutation == "duplicate_race":
        cohort["races"].append(cohort["races"][0])
    elif mutation == "duplicate_prediction":
        cohort["races"][0]["predicted_order"][0] = cohort["races"][0]["predicted_order"][1]
    elif mutation == "incomplete_result":
        cohort["races"][0]["actual_order"].pop()
    else:
        cohort["classification"] = "FORMAL"
    with pytest.raises(ValueError):
        evaluate(None, cohort)


def test_original_bytes_and_rank_binding(tmp_path):
    raw = b"## 1R\xef\xbd\x9cfixture\n| 1 | 1 A | x |\n| 2 | 2 B | x |\n| 3 | 3 C | x |\n"
    path = tmp_path / "reference.md"
    path.write_bytes(raw)
    cohort = {"classification": "POSTRESULT_DIAGNOSTIC", "reference_sha256": hashlib.sha256(raw).hexdigest(),
              "races": [{"race_no": 1, "predicted_order": [1, 2, 3], "actual_order": [1, 2, 3]}]}
    assert evaluate(path, cohort)["original_reference_bytes_verified"] is True
    path.write_bytes(raw + b"changed")
    with pytest.raises(ValueError, match="REFERENCE_SHA_MISMATCH"):
        evaluate(path, cohort)
    path.write_bytes(raw)
    cohort["races"][0]["predicted_order"] = [2, 1, 3]
    with pytest.raises(ValueError, match="REFERENCE_RANKS_MISMATCH"):
        evaluate(path, cohort)


@pytest.mark.parametrize(("field", "value"), [
    ("race_no", True), ("race_no", 1.0),
    ("predicted_order", [1.0, 2, 3, 4]), ("actual_order", [True, 2, 3, 4]),
])
def test_noninteger_id_cannot_alias_an_official_race_or_runner(field, value):
    cohort = copy.deepcopy(COHORT)
    cohort["races"][0][field] = value
    with pytest.raises(ValueError, match="RESULT_.*_ID_INVALID"):
        evaluate(None, cohort)


@pytest.mark.parametrize(("field", "value"), [
    ("cancelled", [4]), ("excluded", [4]), ("did_not_finish", [4]),
    ("dead_heat", True), ("race_abandoned", True),
])
def test_nonordinal_result_is_not_scored_even_with_a_complete_order(field, value):
    cohort = copy.deepcopy(COHORT)
    cohort["races"][0][field] = value
    with pytest.raises(ValueError, match="RESULT_NOT_STRICT_ORDINAL"):
        evaluate(None, cohort)


def test_result_observation_and_publication_follow_effective_freeze():
    cohort = copy.deepcopy(COHORT)
    cohort["result_observed_at"] = "2026-11-10T09:00:00Z"
    race = cohort["races"][0]
    race["effective_freeze"] = "2026-11-10T16:45:00+09:00"
    race["result_publication_time"] = "2026-11-10T17:50:00+09:00"
    assert evaluate(None, cohort)["exact_order_matches"] == 1

    race["result_publication_time"] = "2026-11-10T16:40:00+09:00"
    with pytest.raises(ValueError, match="RESULT_TIME_ORDER_INVALID"):
        evaluate(None, cohort)
    race["result_publication_time"] = None
    race["effective_freeze"] = "2026-11-10T18:00:00+09:00"
    with pytest.raises(ValueError, match="RESULT_TIME_ORDER_INVALID"):
        evaluate(None, cohort)
    race["effective_freeze"] = "2026-11-10T16:45:00"
    with pytest.raises(ValueError, match="RESULT_TIMESTAMP_INVALID"):
        evaluate(None, cohort)
