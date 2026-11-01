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
