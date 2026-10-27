"""Offline adversarial tests for the *reported* chronological aggregate audit.

The original large per-run dataset is intentionally not required or reproduced.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import partition_integrity as audit

REPORT = HERE / "evidence/current_corpus_evaluation.json"


@pytest.fixture
def report():
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_current_report_reconciles_both_time_partitions_without_promotion(report):
    out = audit.audit_report(report)
    val, test = out["partitions"]["VALIDATION"], out["partitions"]["TEST"]
    assert val["all"]["n"] == 1546
    assert test["all"]["n"] == 2771
    assert val["train_disjoint_proxy_rows"] == 254
    assert test["train_disjoint_proxy_rows"] == 790
    assert val["training_overlap_proxy_horses"] == 1085
    assert test["training_overlap_proxy_horses"] == 1590
    assert val["all"]["delta_mse_env_minus_general"] == pytest.approx(0.0005567182893991274, abs=1e-13)
    assert test["all"]["delta_mse_env_minus_general"] == pytest.approx(0.00023512173673650993, abs=1e-13)
    assert val["reported_train_disjoint_composite_horses"]["delta_mse_env_minus_general"] > 0
    assert test["reported_train_disjoint_composite_horses"]["delta_mse_env_minus_general"] < 0
    assert out["unseen_horse_effect_direction_consistent"] is False
    assert out["future_incremental_value_proven"] is False
    assert out["promotion_authorized"] is False
    assert out["forward_oos_increment"] == 0
    assert out["independent_race_label_verified"] is False


@pytest.mark.parametrize("mutator,reason", [
    (lambda x: x.update(production_effect="PRODUCTION"), "NONPRODUCTION_SAFETY_CONTRACT_FAILED"),
    (lambda x: x.update(eligible_permanent_horse_ids=1), "INDEPENDENT_ID_OR_LABEL_STATUS_CHANGED"),
    (lambda x: x.update(forward_oos_increment=1), "NONPRODUCTION_SAFETY_CONTRACT_FAILED"),
    (lambda x: x.update(predictive_improvement_demonstrated=True), "INCUMBENT_REJECTION_NOT_PRESERVED"),
    (lambda x: x.update(protocol_sha256="0" * 64), "PROTOCOL_SHA_MISMATCH"),
    (lambda x: x["partitions"]["TEST"]["arms"]["GENERAL_ONLY"].update(mse=0.6), "HORSE_SEEN_WEIGHTED_AGGREGATE_MISMATCH"),
    (lambda x: x["partitions"]["TEST"]["groups"]["horse_seen"]["False"]["GENERAL_ONLY"].update(n=789), "MODEL_SAMPLE_MISMATCH"),
    (lambda x: x["partitions"]["TEST"]["groups"]["horse_seen"]["False"]["GENERAL_ONLY"].update(composite_horses=661), "COMPOSITE_HORSE_COUNT_NONPARTITION"),
    (lambda x: x["partitions"]["TEST"]["groups"]["venue"]["東京"]["GENERAL_ONLY"].update(mse=0.1), "GROUP_WEIGHTED_AGGREGATE_MISMATCH"),
])
def test_adversarial_distortion_fails_closed(report, mutator, reason):
    forged = copy.deepcopy(report)
    mutator(forged)
    with pytest.raises(ValueError, match=reason):
        audit.audit_report(forged)


def test_unavailable_probability_scores_are_not_fake_zero(report):
    out = audit.audit_report(report)
    assert out["brier"] is None and out["logloss"] is None
    assert "CONTINUOUS_FINISH_RANK_PROXY" in out["probability_metric_status"]
    assert out["negative_controls"]["independent_second_placebo"] == "NOT_EXECUTED"
    assert out["significance_test"].startswith("NOT_RUN")
    assert out["validation_test_horse_disjoint"] == "NOT_ESTABLISHED"


def test_cli_preserves_raw_evidence_and_writes_only_external_output(tmp_path):
    before = REPORT.read_bytes()
    output = tmp_path / "bvi_partition_integrity.json"
    subprocess.run([sys.executable, str(HERE / "partition_integrity.py"),
                    "--input", str(REPORT), "--output", str(output)], check=True,
                   capture_output=True, text=True)
    actual = json.loads(output.read_text(encoding="utf-8"))
    assert actual["source_report_raw_sha256"] == hashlib.sha256(before).hexdigest()
    assert REPORT.read_bytes() == before
    assert actual["partitions"]["TEST"]["reported_train_disjoint_composite_horses"]["n"] == 790
    assert actual["classification"].endswith("NOT_FORWARD_OOS")
