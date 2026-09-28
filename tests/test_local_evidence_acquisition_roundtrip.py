import pytest

from runtime.local_evidence_acquisition_roundtrip import (
    EvidenceRoundTripError,
    build_evidence_acquisition_ledger,
)


def base_req():
    return {
        "race_id": "FUN-TEST-R1",
        "runners": [{"runner_id": "1"}, {"runner_id": "2"}],
        "required_evidence_manifest": [
            {"runner_id": "1", "evidence_key": "runner.1.bodyweight", "required": True},
            {"runner_id": "2", "evidence_key": "runner.2.bodyweight", "required": True},
            {"runner_id": "1", "evidence_key": "runner.1.training", "required": True, "source_id": "BOOK"},
        ],
    }


def test_found_and_missing_are_terminal_without_fabrication():
    req = base_req()
    src = {
        "normalized_evidence": {
            "runner": {"1": {"bodyweight": {"value": 500, "source_id": "NAR", "authority": "OFFICIAL"}}}
        },
        "snapshots": [{"source_id": "BOOK", "http_status": 403, "stale": False}],
    }
    led = build_evidence_acquisition_ledger(req, src)
    assert led["full_terminalization"] is True
    assert led["unresolved_count"] == 0
    assert led["found_count"] == 1
    assert led["missing_count"] == 1
    assert led["not_available_count"] == 1
    missing = [r for r in led["rows"] if r["status"] != "FOUND"]
    assert all(r["value_present"] is False for r in missing)


def test_explicit_conflict_terminalizes_with_reason():
    req = base_req()
    req["evidence_acquisition_dispositions"] = [
        {"runner_id": "2", "evidence_key": "runner.2.bodyweight", "status": "CONFLICT", "reason": "equal-priority official conflict"},
        {"runner_id": "1", "evidence_key": "runner.1.training", "status": "NOT-AVAILABLE", "reason": "access dependent"},
    ]
    src = {"normalized_evidence": {"runner": {"1": {"bodyweight": {"value": 500, "source_id": "NAR", "authority": "OFFICIAL"}}}}}
    led = build_evidence_acquisition_ledger(req, src)
    assert led["conflict_count"] == 1
    assert led["not_available_count"] == 1


def test_found_cannot_be_self_declared_without_source_value():
    req = base_req()
    req["evidence_acquisition_dispositions"] = [
        {"runner_id": "2", "evidence_key": "runner.2.bodyweight", "status": "FOUND", "reason": "trust me"}
    ]
    with pytest.raises(EvidenceRoundTripError):
        build_evidence_acquisition_ledger(req, {"normalized_evidence": {}})


def test_duplicate_required_cell_fails():
    req = base_req()
    req["required_evidence_manifest"].append(dict(req["required_evidence_manifest"][0]))
    with pytest.raises(EvidenceRoundTripError):
        build_evidence_acquisition_ledger(req, {"normalized_evidence": {}})



def test_no_standalone_declaration_is_not_a_failure():
    req = {
        "race_id": "FUN-NO-DECL-R1",
        "runners": [{"runner_id": "1"}, {"runner_id": "2"}],
    }
    led = build_evidence_acquisition_ledger(req, {"formal_ready": True, "normalized_evidence": {}})
    assert led["status"] == "NOT_DECLARED"
    assert led["declaration_present"] is False
    assert led["required_evidence_count"] == 0
    assert led["unresolved_count"] == 0
    assert led["full_terminalization"] is True
    assert led["numerical_authority_effect"] == "NONE"


def test_explicit_empty_manifest_is_invalid_not_silently_ignored():
    req = {
        "race_id": "FUN-EMPTY-DECL-R1",
        "runners": [{"runner_id": "1"}],
        "required_evidence_manifest": [],
    }
    with pytest.raises(EvidenceRoundTripError, match="REQUIRED_EVIDENCE_MANIFEST_EMPTY"):
        build_evidence_acquisition_ledger(req, {"normalized_evidence": {}})


def test_empty_runner_declaration_is_invalid():
    req = {
        "race_id": "FUN-EMPTY-RUNNER-DECL-R1",
        "runners": [{"runner_id": "1", "required_evidence": []}],
    }
    with pytest.raises(EvidenceRoundTripError, match="RUNNER_REQUIRED_EVIDENCE_EMPTY"):
        build_evidence_acquisition_ledger(req, {"normalized_evidence": {}})
