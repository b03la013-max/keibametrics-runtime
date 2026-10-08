from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

from family_pfs_regression_readout import (
    RegressionEvidenceError,
    _git_blob_sha,
    build_regression_readout,
)

MANIFEST = ROOT / "research/common/KM-FAMILY-OHI-20261008-DAY-REGRESSION-R1.json"


def test_real_ohi_regression_measures_pfs_not_only_hits():
    readout = build_regression_readout(ROOT, MANIFEST)
    s = readout["frozen_recommendation_scorecard"]
    agg = s["aggregate"]
    assert agg["race_count"] == 10
    assert agg["investment"] == 317000
    assert agg["return"] == 71870
    assert agg["profit_loss"] == -245130
    assert agg["pfs"] == pytest.approx(22.67192429, abs=0.01)
    assert agg["hit_races"] == 9
    assert agg["hit_but_loss_count"] == 9
    assert s["first_material_failure_frequency"] == {
        "CAPITAL_EFFICIENCY": 6,
        "PREDICTION_ROLE_W": 2,
        "ORDERED_PAIR_CONVERSION": 2,
    }
    assert readout["prediction_capture"] == {
        "winner_w_capture": 8,
        "second_p2_capture": 10,
        "third_p3_capture": 10,
    }
    assert readout["conversion_capture"] == {
        "purchased_trio_hit": 4,
        "ordered_pair_hit": 6,
        "exact_oriented_hit": 6,
    }
    assert s["by_bet_type"]["EXACTA"]["investment"] == 34200
    assert s["by_bet_type"]["TRIFECTA"]["investment"] == 166700
    assert s["by_bet_type"]["TRIO"]["investment"] == 116100
    assert s["by_bet_type"]["EXACTA"]["return"] == 6510
    assert s["by_bet_type"]["TRIFECTA"]["return"] == 37840
    assert s["by_bet_type"]["TRIO"]["return"] == 27520
    assert readout["no_bet_reference"]["pfs"] is None
    assert readout["no_bet_reference"]["avoided_frozen_recommendation_loss_in_hindsight"] == 245130
    assert readout["actual_purchase_pfs"] is None
    assert readout["automatic_promotion"] is False
    assert readout["production_change_authorized"] is False
    assert len(readout["source_races"]) == 10
    assert "R12" in readout["excluded"]
    assert "NOT-NEW-OOS-CREDIT" in readout["status"]
    assert readout["verification_class"].endswith("NOT_INDEPENDENT_SIGNATURE_VERIFICATION")
    assert readout["existing_shadow"]["mec_r5"]["eligible_races"] == 30
    assert readout["existing_shadow"]["mec_r4"]["eligible_races"] == 8


def _tmp_basis(tmp_path):
    repo = tmp_path
    p = repo / "runtime/executions/TEST-R01/RESULT/runs/snapshot/result_summary.json"
    p.parent.mkdir(parents=True)
    signed_review = {
        "race_id": "TEST-R01",
        "sha256": "signed-review",
        "final_receipt_sha256": "frozen-final",
        "capital": {
            "settlement_status": "COMPLETE",
            "investment": 100,
            "return": 0,
            "pfs": 0.0,
            "hit": False,
            "hit_but_loss": False,
        },
        "conversion": {"matching_ticket_types": [], "ordered_pair_ticket_coverage": False, "ordered_exact_ticket_coverage": False},
        "failure_localization": {"first_material_failure": "PREDICTION_ROLE_W"},
    }
    summary = {
        "race_id": "TEST-R01",
        "result_receipt": "signed-result",
        "verified": True,
        "investment": 100,
        "return": 0,
        "winning_tickets": [],
        "by_type": {"EXACTA": {"investment": 100, "return": 0}},
        "automatic_post_result_review": signed_review,
    }
    p.write_text(json.dumps(summary, sort_keys=True), encoding="utf-8")
    manifest = {
        "profile_id": "TEST",
        "status": "REGRESSION-EVIDENCE / NOT-NEW-OOS-CREDIT",
        "verified_result_records": [{
            "race_id": "TEST-R01",
            "result_summary_path": str(p.relative_to(repo)),
            "result_summary_git_blob_sha": _git_blob_sha(p.read_bytes()),
            "investment_yen": 100,
            "return_yen": 0,
            "expected_purchased_trio": False,
            "first_material_failure": "PREDICTION_ROLE_W",
        }],
        "day_totals": {
            "races": 1, "investment_yen": 100,
            "return_yen": 0, "hit_races": 0,
            "hit_but_loss_races": 0,
        },
        "first_failure_counts": {"PREDICTION_ROLE_W": 1},
    }
    m = repo / "fixture.json"
    m.write_text(json.dumps(manifest), encoding="utf-8")
    return repo, p, m, summary, manifest


def test_missing_and_tampered_frozen_results_fail_closed(tmp_path):
    root, source, fixture, summary, manifest = _tmp_basis(tmp_path)
    x = build_regression_readout(root, fixture)
    assert x["frozen_recommendation_scorecard"]["aggregate"]["pfs"] == 0
    assert x["no_bet_reference"]["pfs"] is None

    source.write_text(source.read_text() + " ", encoding="utf-8")
    with pytest.raises(RegressionEvidenceError, match="FROZEN_RESULT_BLOB_CHANGED"):
        build_regression_readout(root, fixture)
    source.unlink()
    with pytest.raises(RegressionEvidenceError, match="EVIDENCE_NOT_READABLE"):
        build_regression_readout(root, fixture)


def test_no_double_count_no_result_time_ticket_reselection(tmp_path):
    root, source, fixture, summary, manifest = _tmp_basis(tmp_path)
    bad = copy.deepcopy(manifest)
    bad["verified_result_records"].append(copy.deepcopy(bad["verified_result_records"][0]))
    fixture.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(RegressionEvidenceError, match="DUPLICATE_OR_MISSING_RACE"):
        build_regression_readout(root, fixture)

    bad = copy.deepcopy(manifest)
    bad["verified_result_records"][0]["result_summary_path"] = "../secrets.json"
    fixture.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(RegressionEvidenceError, match="EVIDENCE_PATH_REJECTED"):
        build_regression_readout(root, fixture)


def test_missing_result_binding_and_unsettled_amount_are_not_zero(tmp_path):
    root, source, fixture, summary, manifest = _tmp_basis(tmp_path)
    for change, error in [
        (lambda s: s.update({"verified": False}), "RESULT_VERIFIED_STATUS_MISSING"),
        (lambda s: s["automatic_post_result_review"]["capital"].update({"settlement_status": "PENDING"}), "INCOMPLETE_SETTLEMENT"),
        (lambda s: s.update({"return": 10}), "MANIFEST_AMOUNT_CONFLICT"),
    ]:
        altered = copy.deepcopy(summary)
        change(altered)
        source.write_text(json.dumps(altered, sort_keys=True), encoding="utf-8")
        broken = copy.deepcopy(manifest)
        broken["verified_result_records"][0]["result_summary_git_blob_sha"] = _git_blob_sha(source.read_bytes())
        fixture.write_text(json.dumps(broken), encoding="utf-8")
        with pytest.raises(RegressionEvidenceError, match=error):
            build_regression_readout(root, fixture)
