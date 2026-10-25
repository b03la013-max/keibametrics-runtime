from __future__ import annotations

from typing import Optional


def failure_stage_for(code: object) -> str:
    """Stable operational stage, alongside the existing compatibility classes."""
    value = str(code or '').upper()
    for terms, stage in (
        (('DELIVERY', 'NOTIFICATION', 'USER_ACK'), 'DELIVERY'),
        (('DEADLINE', 'CUTOFF', 'POST_START', 'PRESTART_WINDOW', 'LATENCY', 'COMPLETED_AFTER'), 'LATENCY'),
        (('NUMERICAL', 'INDEX_', 'TERMINALIZATION'), 'NUMERICAL'),
        (('DATED_', 'ACTIVATION', 'PRE_DISPATCH_DATED', 'PHASE_B_', 'PHASE_C_'), 'ACTIVATION'),
        (('AUTHORITY', 'AUTHORIZATION', 'VENUE_OWNER', 'OWNER_SCOPE'), 'AUTHORIZATION'),
        (('REGISTRATION', 'INTENT_', 'CLAIM_'), 'REGISTRATION'),
        (('PRE_KRS', 'KRS_'), 'KRS'),
        (('MEC_',), 'MEC'), (('TICKET_',), 'TICKET'), (('CAPITAL_',), 'CAPITAL'),
        (('FINAL_',), 'FINAL'),
        (('RUNNER', 'UNIVERSE'), 'RUNNER'),
        (('SOURCE', 'OFFICIAL_CARD', 'OFFICIAL_POST'), 'SOURCE'),
        (('STATIC_', 'PREDICTION', 'REFERENCE_'), 'PREDICTION'),
    ):
        if any(term in value for term in terms):
            return stage
    return 'RUNTIME'


def failure_class_for(code: object) -> str:
    code = str(code or "")
    if code in {"PRODUCTION_STATIC_OWNER_REQUIRED", "STATIC_PREDICTION_FREEZE_REQUIRED", "STATIC_PREDICTION_NOT_FROZEN"}:
        return "PREDICTION_OWNER_INPUT_REQUIRED"
    if code == "OFFICIAL_TRACK_CONDITION_MISMATCH_REFORECAST_REQUIRED":
        return "CURRENT_STATE_REFORECAST"
    if code in {"OFFICIAL_POST_TIME_MISMATCH", "RACE_IDENTITY_MISMATCH"}:
        return "RACE_IDENTITY_REFORECAST"
    if code.startswith("STATIC_SOURCE_BASIS_"):
        return "SOURCE_STATIC_BINDING"
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
    value = str(code or '')
    stage = failure_stage_for(value)
    if stage in {'AUTHORIZATION', 'ACTIVATION'}:
        return 'HOLD_AWAIT_EXPLICIT_APPLICABLE_AUTHORITY_NO_AUTOMATIC_RETRY'
    if stage == 'DELIVERY':
        return 'REUSE_VERIFIED_FINAL_RETRY_APPROVED_DELIVERY_ONLY_NO_REPREDICTION'
    if (value.startswith(('RUNNER_UNIVERSE_', 'CURRENT_AUTHORITY_', 'AUTHORITY_',
                          'RUNTIME_FINGERPRINT_', 'CHECKPOINT_'))
            or any(part in value for part in ('SIGNATURE', 'RECEIPT_VERIFY', 'HASH_MISMATCH'))):
        return 'HOLD_RECONCILE_IDENTITY_AUTHORITY_SIGNATURE_NO_AUTOMATIC_RETRY'
    klass = failure_class_for(code)
    if klass == "PREDICTION_OWNER_INPUT_REQUIRED":
        return "AWAIT_AUTHORIZED_FROZEN_STATIC_INPUT_NO_AUTOMATIC_OWNER_PROMOTION"
    if klass == "CURRENT_STATE_REFORECAST":
        return "REUSE_DURABLE_SOURCE_REFRESH_CURRENT_STATE_REBUILD_STATIC_THEN_RETRY_FORMAL"
    if klass == "RACE_IDENTITY_REFORECAST":
        return "REUSE_DURABLE_SOURCE_REFRESH_RACE_IDENTITY_REBUILD_STATIC_THEN_RETRY_FORMAL"
    if klass == "SOURCE_STATIC_BINDING":
        return "REUSE_DURABLE_SOURCE_REBIND_STATIC_PROVENANCE_THEN_RETRY_FORMAL"
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
