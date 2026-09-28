from runtime.formal_failure_diagnostics import failure_class_for, resume_hint_for


def test_track_condition_mismatch_requires_reforecast_not_generic_retry():
    code = "OFFICIAL_TRACK_CONDITION_MISMATCH_REFORECAST_REQUIRED"
    assert failure_class_for(code) == "CURRENT_STATE_REFORECAST"
    assert resume_hint_for(code) == (
        "REUSE_DURABLE_SOURCE_REFRESH_CURRENT_STATE_REBUILD_STATIC_THEN_RETRY_FORMAL"
    )


def test_official_post_mismatch_is_race_identity_reforecast():
    code = "OFFICIAL_POST_TIME_MISMATCH"
    assert failure_class_for(code) == "RACE_IDENTITY_REFORECAST"
    assert resume_hint_for(code) == (
        "REUSE_DURABLE_SOURCE_REFRESH_RACE_IDENTITY_REBUILD_STATIC_THEN_RETRY_FORMAL"
    )


def test_evidence_roundtrip_failure_has_specific_class():
    code = "EVIDENCE_ACQUISITION_ROUNDTRIP_FAILED"
    assert failure_class_for(code) == "EVIDENCE_CONFORMANCE"
    assert resume_hint_for(code) == (
        "REPAIR_DECLARED_EVIDENCE_CONTRACT_THEN_RETRY_SAME_EXECUTION_ID_REUSING_SOURCE"
    )


def test_known_runtime_and_krs_classes_remain_stable():
    assert failure_class_for("RUNTIME_GATEWAY_COMPATIBILITY_FAILED") == "INFRASTRUCTURE_COMPATIBILITY"
    assert failure_class_for("KRS_RECEIPT_VERIFY_FAILED") == "KRS_EXECUTION"
