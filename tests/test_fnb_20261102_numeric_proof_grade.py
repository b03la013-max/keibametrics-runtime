"""FNB C1: numerical-quality claims must not be inferred from lifecycle PASS."""
from runtime.local_race_key_gate import attest_numeric_quality


def report(required, calculated, neutral=0, hold=0, na=0, unresolved=0):
    return {"completion": {"complete": True, "numeric_coverage": {
        "required_count": required, "calculated_count": calculated,
        "ruled_neutral_count": neutral, "ruled_hold_count": hold,
        "not_applicable_count": na, "unresolved_count": unresolved}}}


def test_fnb_20261002_historical_348_all_held_is_not_numerical_success():
    r = attest_numeric_quality(report(348, 0, hold=348))
    assert r["status"] == "NUMERICAL_HELD_OR_UNRESOLVED"
    assert not r["reported_numeric_value_closure"]
    assert not r["all_cells_calculated"]


def test_all_ruled_neutral_is_not_full_calculated():
    r = attest_numeric_quality(report(29, 0, neutral=29))
    assert r["status"] == "NUMERICAL_RULED_NEUTRAL_ONLY"
    assert r["reported_numeric_value_closure"]
    assert not r["all_cells_calculated"]


def test_mixed_calculated_neutral_preserves_quality_distinction():
    r = attest_numeric_quality(report(29, 20, neutral=9))
    assert r["status"] == "NUMERICAL_CALCULATED_WITH_RULED_NEUTRAL"
    assert r["reported_numeric_value_closure"]
    assert not r["all_cells_calculated"]


def test_all_calculated_does_not_claim_independent_evidence_proof():
    r = attest_numeric_quality(report(29, 29))
    assert r["status"] == "NUMERICAL_ALL_CALCULATED_REPORTED"
    assert r["all_cells_calculated"]
    assert r["independent_evidence_verification"] == "NOT_PERFORMED"


def test_missing_coverage_is_not_treated_as_pass():
    r = attest_numeric_quality({"status": "FULL_LIFECYCLE_EXECUTION_PASS",
                                "completion": {"complete": True}})
    assert r["status"] == "NUMERICAL_COUNTS_NOT_REPORTED"
    assert not r["reported_numeric_value_closure"]


def test_count_mismatch_is_not_allowed():
    r = attest_numeric_quality(report(348, 200, neutral=147))
    assert r["status"] == "NUMERICAL_COUNTS_INVALID"


def test_not_applicable_is_not_full_required_closure():
    r = attest_numeric_quality(report(29, 28, na=1))
    assert r["status"] == "NUMERICAL_NOT_APPLICABLE_PRESENT"
    assert not r["reported_numeric_value_closure"]


def test_bad_values_bools_negatives_and_zeros_are_rejected():
    for bad in [True, -1, "29", None]:
        r = report(29, 29)
        r["completion"]["numeric_coverage"]["calculated_count"] = bad
        assert attest_numeric_quality(r)["status"] == "NUMERICAL_COUNTS_INVALID"
    assert attest_numeric_quality(report(0, 0))["status"] == "NUMERICAL_COUNTS_INVALID"

def test_race_key_certification_wires_numeric_quality_without_changing_lifecycle():
    import inspect
    from runtime.local_race_key_gate import certify
    src = inspect.getsource(certify)
    assert '"numeric_evidence_quality": attest_numeric_quality(entry_report)' in src


def test_historical_fnb_r04_checkpoint_facts_reproduce_real_calculated_zero():
    """Uses the archived 2026-10-02 FNB immutable execution, not a synthetic count."""
    import json
    from pathlib import Path
    from runtime.local_race_key_gate import attest_frozen_numeric_counts
    root = Path(__file__).resolve().parents[1]
    eid = "LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"
    folder = root / "runtime" / "executions" / eid / "FORMAL" / "runs" / "36976101101-formal"
    original_report = json.loads((root / "runtime" / "execution_reports" / eid /
                                  "36976101101-formal.json").read_text(encoding="utf-8"))
    materialized = json.loads((folder / "numerical_materialization_summary.json").read_text(encoding="utf-8"))
    mandatory = json.loads((folder / "mandatory_stage_manifest.json").read_text(encoding="utf-8"))
    assert original_report["completion"]["complete"] is True
    assert materialized["numeric_coverage"]["required_count"] == 348
    assert materialized["numeric_coverage"]["calculated_count"] == 0
    assert materialized["numeric_coverage"]["ruled_hold_count"] == 348
    assert attest_numeric_quality(original_report)["status"] == "NUMERICAL_HELD_OR_UNRESOLVED"
    proof = attest_frozen_numeric_counts(original_report, materialized, mandatory)
    assert proof["status"] == "NUMERICAL_FROZEN_COUNTS_CONSISTENT"
    assert proof["consistency_verified"] is True
    assert proof["independent_index_evaluation"] == "NOT_PERFORMED"


def test_counterfeit_report_count_rejected_against_frozen_numeric_artifact():
    from runtime.local_race_key_gate import attest_frozen_numeric_counts
    original = report(348, 0, hold=348)
    mat = {"numeric_coverage": original["completion"]["numeric_coverage"].copy()}
    mandatory = {"numeric_coverage": mat["numeric_coverage"].copy()}
    corrupt = report(348, 348)
    assert attest_frozen_numeric_counts(corrupt, mat, mandatory)["status"] == (
        "NUMERICAL_FROZEN_COUNTS_MISMATCH")
    # A checkpoint inconsistent with another checkpoint is also rejected.
    mandatory["numeric_coverage"]["calculated_count"] = 1
    assert attest_frozen_numeric_counts(original, mat, mandatory)["consistency_verified"] is False


def test_missing_numeric_checkpoint_must_not_be_fabricated():
    from runtime.local_race_key_gate import attest_frozen_numeric_counts
    base = report(348, 0, hold=348)
    p = attest_frozen_numeric_counts(base, None, None)
    assert p["status"] == "NUMERICAL_FROZEN_CHECKPOINT_UNAVAILABLE"
    assert p["consistency_verified"] is False
    assert p["independent_index_evaluation"] == "NOT_PERFORMED"
    assert attest_frozen_numeric_counts(base, {"numeric_coverage": {}}, {"numeric_coverage": {}})[
        "status"] == "NUMERICAL_FROZEN_COUNTS_MISMATCH"
