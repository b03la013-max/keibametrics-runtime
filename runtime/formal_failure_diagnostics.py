from __future__ import annotations

from typing import Optional


def failure_class_for(code: object) -> str:
    code = str(code or "")
    if code == "OFFICIAL_TRACK_CONDITION_MISMATCH_REFORECAST_REQUIRED":
        return "CURRENT_STATE_REFORECAST"
    if code in {"OFFICIAL_POST_TIME_MISMATCH", "RACE_IDENTITY_MISMATCH"}:
        return "RACE_IDENTITY_REFORECAST"
    if code.startswith(("RUNTIME_", "GATEWAY_")):
        return "INFRASTRUCTURE_COMPATIBILITY"
    if code.startswith(("SOURCE_", "RUNNER_UNIVERSE_")):
        return "SOURCE_OR_RUNNER_UNIVERSE"
    if code.startswith(("EVIDENCE_ACQUISITION_", "EVIDENCE_FEATURE_")):
        return "EVIDENCE_CONFORMANCE"
    if code.startswith(("DEADLINE_", "POST_START", "FINAL_RECEIPT_POST_START", "MEC_FINAL_FREEZE_POST_START")):
        return "TEMPORAL_GUARD"
    if code.startswith(("FULL_NUMERICAL_AUTHORITY_", "UNAUTHORIZED_FULL_NUMERICAL", "LOCAL_INDEX_TERMINALIZATION")):
        return "NUMERICAL_AUTHORITY_OR_MATERIALIZATION"
    if code.startswith(("PRE_KRS_", "KRS_")):
        return "KRS_EXECUTION"
    if code.startswith(("MEC_", "CAPITAL_", "TICKET_")):
        return "DECISION_OR_CAPITAL"
    if code.startswith(("FINAL_", "IMMUTABLE_FINAL_")):
        return "FINALIZATION"
    return "EXECUTION_CONFORMANCE"


def resume_hint_for(code: object) -> str:
    klass = failure_class_for(code)
    if klass == "CURRENT_STATE_REFORECAST":
        return "REUSE_DURABLE_SOURCE_REFRESH_CURRENT_STATE_REBUILD_STATIC_THEN_RETRY_FORMAL"
    if klass == "RACE_IDENTITY_REFORECAST":
        return "REUSE_DURABLE_SOURCE_REFRESH_RACE_IDENTITY_REBUILD_STATIC_THEN_RETRY_FORMAL"
    if klass == "SOURCE_OR_RUNNER_UNIVERSE":
        return "RETRY_SAME_EXECUTION_ID_FROM_SOURCE"
    if klass == "EVIDENCE_CONFORMANCE":
        return "REPAIR_DECLARED_EVIDENCE_CONTRACT_THEN_RETRY_SAME_EXECUTION_ID_REUSING_SOURCE"
    if klass in {"KRS_EXECUTION", "DECISION_OR_CAPITAL", "FINALIZATION", "NUMERICAL_AUTHORITY_OR_MATERIALIZATION"}:
        return "RETRY_SAME_EXECUTION_ID_REUSING_DURABLE_SOURCE"
    if klass == "TEMPORAL_GUARD":
        return "DO_NOT_CLAIM_FORMAL_PRE_RACE_AFTER_DEADLINE"
    if klass == "INFRASTRUCTURE_COMPATIBILITY":
        return "REPAIR_RUNTIME_GATEWAY_THEN_RETRY_SAME_EXECUTION_ID"
    return "RETRY_SAME_EXECUTION_ID_FROM_LAST_DURABLE_PHASE"
