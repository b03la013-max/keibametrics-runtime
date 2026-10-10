"""JRA Production evidence-insufficient NO_BET decision with terminal Full20 accounting.

This is NOT a Signed FINAL or a reconstructed race prediction. It is a
canonical, tamper-evident *zero-exposure* decision for a source-verified JRA
race whose mandatory numeric contract cannot be closed. Its artifact is
separately attested by the external GitHub OIDC execution.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import math

BASE = ("HPI","SSI","CFI","RFI","BVI","JTI","CSI",
        "TRI","BWI","GCI","PRI","KGI","VMI")
DERIVED = ("DCR","TPI","ZAI_WIN","ZAI_PLACE","SRI","F3S","T3I")
TERMINAL = {"CALCULATED", "RULED-HOLD"}
PROFILE = "KM-JRA-PRODUCTION-EVIDENCE-NO-BET-TERMINAL-v1-20261010"


class JRANoBetTerminalError(ValueError):
    pass


def digest(x):
    return sha256(json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",",":")).encode()).hexdigest()


def _parse_time(x):
    try:
        d = datetime.fromisoformat(str(x).replace("Z","+00:00"))
        return d.astimezone(timezone.utc) if d.tzinfo else None
    except (ValueError, TypeError):
        return None


def build_no_bet_terminal(intent, report, *, source_receipt_verified=False,
                          created_at=None, lineage="LIVE"):
    if intent.get("family_id") != "JRA" or report.get("family_id") != "JRA":
        raise JRANoBetTerminalError("JRA_ONLY")
    rid = str(intent.get("race_id") or "")
    if not rid or report.get("race_id") != rid:
        raise JRANoBetTerminalError("RACE_ID_MISMATCH")
    if source_receipt_verified is not True:
        raise JRANoBetTerminalError("SIGNED_SOURCE_VERIFICATION_REQUIRED")
    source = report.get("source_checkpoint_manifest") or {}
    if (source.get("race_id") != rid
            or source.get("prediction_cutoff") != intent.get("prediction_cutoff")
            or not source.get("source_snapshot_sha256")
            or not source.get("receipt_sha256")):
        raise JRANoBetTerminalError("SOURCE_CHECKPOINT_INVALID")
    snapshot = _parse_time(source.get("source_freeze_at"))
    cutoff = _parse_time(intent.get("prediction_cutoff"))
    post = _parse_time(intent.get("scheduled_post_at"))
    created = _parse_time(created_at or datetime.now(timezone.utc).isoformat())
    if not (snapshot and cutoff and post and created) or not snapshot <= cutoff < post:
        raise JRANoBetTerminalError("SOURCE_TEMPORAL_INVALID")
    if (report.get("production_full_numerical_ready") is True
            and report.get("source_only_full_numerical_ready") is True):
        raise JRANoBetTerminalError("FULL20_READY_USE_FORMAL_LIVE_PATH")
    ids = [str(x) for x in report.get("runner_universe") or []]
    if len(ids) < 2 or "" in ids or len(ids) != len(set(ids)):
        raise JRANoBetTerminalError("RUNNER_UNIVERSE_INVALID")
    partial = report.get("partial_production_base_calculation") or {}
    source_rows = partial.get("runners") or {}
    if set(source_rows) != set(ids):
        raise JRANoBetTerminalError("PARTIAL_BASE_UNIVERSE_MISMATCH")
    runners = {}
    counted = 0
    blocked = 0
    for runner_id in ids:
        src = (source_rows[runner_id].get("indices") or {})
        if set(src) != set(BASE):
            raise JRANoBetTerminalError("BASE13_INCOMPLETE:" + runner_id)
        row = {}
        for name in BASE:
            value = src[name]
            state = str(value.get("status") or "")
            if state == "CALCULATED":
                num = value.get("value")
                if (isinstance(num, bool) or not isinstance(num, (float,int))
                        or not math.isfinite(num) or not 0 <= num <= 100
                        or not value.get("evidence_refs")
                        or not value.get("rule_id")):
                    raise JRANoBetTerminalError("BASE_CALCULATED_PROVENANCE_INVALID:" + runner_id+":"+name)
                row[name] = {
                    "terminal_status":"CALCULATED",
                    "value":num,
                    "rule_id":value["rule_id"],
                    "evidence_refs":value["evidence_refs"],
                    "source_fact":value.get("source_fact"),
                }
                counted += 1
            elif state == "BLOCKED":
                if value.get("value") is not None or not value.get("reason"):
                    raise JRANoBetTerminalError("BASE_HOLD_VALUE_OR_REASON_INVALID:" + runner_id+":"+name)
                row[name] = {
                    "terminal_status":"RULED-HOLD",
                    "reason":value["reason"],
                    "value":None,
                    "rule_id":"JRA-EXISTING-FULL-REQUIRED-EVIDENCE-GATE",
                    "evidence_refs":[source["receipt_sha256"]],
                }
                blocked += 1
            else:
                raise JRANoBetTerminalError("BASE_UNRESOLVED:"+runner_id+":"+name)
        for name in DERIVED:
            row[name] = {
                "terminal_status":"RULED-HOLD",
                "reason":"DEPENDENCY_BASE13_NOT_FULLY_CALCULATED",
                "rule_id":"JRA-DERIVED-FULL20-DEPENDENCY-GATE",
                "value":None,
                "evidence_refs":[source["receipt_sha256"]],
            }
        runners[runner_id] = row
    if counted != partial.get("calculated_base_cells") or blocked != partial.get("blocked_base_cells"):
        raise JRANoBetTerminalError("PARTIAL_BASE_COUNTS_MISMATCH")
    expected = len(ids)*len(BASE)
    if counted + blocked != expected or blocked <= 0:
        raise JRANoBetTerminalError("NO_BET_BLOCKING_EVIDENCE_NOT_ESTABLISHED")
    # Do not silently present a computed decision made after the race as OOS.
    pre_cutoff = created <= cutoff and created <= post
    if lineage == "LIVE" and not pre_cutoff:
        raise JRANoBetTerminalError("LIVE_NO_BET_DECISION_AFTER_CUTOFF")
    if lineage not in ("LIVE", "HISTORICAL_DIAGNOSTIC"):
        raise JRANoBetTerminalError("TEMPORAL_LINEAGE_UNKNOWN")
    classification = "PRE_CUTOFF" if pre_cutoff else "POST_CUTOFF_HISTORICAL"
    out = {
        "profile":PROFILE,
        "race_id":rid,
        "family_id":"JRA",
        "lineage":lineage,
        "temporal_classification":classification,
        "source_execution_id":source.get("source_execution_id"),
        "source_snapshot_sha256":source["source_snapshot_sha256"],
        "signed_source_receipt_sha256":source["receipt_sha256"],
        "source_checkpoint_manifest_sha256":source.get("sha256"),
        "numerical_mapping_id":report.get("mapping_id"),
        "required_index_count":len(ids)*20,
        "base_calculated_count":counted,
        "base_held_count":blocked,
        "derived_held_count":len(ids)*7,
        "terminal_index_count":len(ids)*20,
        "unresolved_count":0,
        "index_universe":runners,
        "decision":"NO_BET",
        "decision_reason":"PRODUCTION_FULL20_EVIDENCE_INSUFFICIENT",
        "first_blocked_stage":report.get("first_blocked_stage"),
        "production_full20_ready":False,
        "formal_full_prediction_completed":False,
        "pre_krs_executed":False,
        "krs_executed":False,
        "signed_final_verified":False,
        "purchase_authority":False,
        "total_investment":0,
        "tickets":[],
        "candidate_predictions_not_production":True,
        "source_verified":True,
        "created_at":created.isoformat(),
        "report_sha256":report.get("sha256"),
        "evidence_attestation_required":"INDEPENDENT_GITHUB_OIDC_ARTIFACT_ATTESTATION",
    }
    out["sha256"] = digest(out)
    return out
