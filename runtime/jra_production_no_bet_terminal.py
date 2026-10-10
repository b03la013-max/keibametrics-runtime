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
    if report.get("production_full_numerical_ready") is True:
        # Actual Full20 (source-only or verified supplemental) is never an
        # evidence-insufficient decision: route to the Formal path or to the
        # distinct Static-Owner-unauthorized terminal instead.
        raise JRANoBetTerminalError("FULL20_READY_USE_FORMAL_LIVE_PATH_OR_STATIC_NO_BET")
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


STATIC_PROFILE = "KM-JRA-PRODUCTION-STATIC-OWNER-UNAUTHORIZED-NO-BET-TERMINAL-v1-20261010"


def _check_source_and_time(intent, report, source_receipt_verified, created_at):
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
    return rid, source, cutoff, post, created


def build_static_unauthorized_no_bet_terminal(intent, report, *, owner_status,
                                              source_receipt_verified=False,
                                              created_at=None, lineage="LIVE"):
    """Zero-exposure terminal for Actual Full20 with an unapproved Static Owner.

    Distinct from the evidence-insufficient NO_BET: every Runner x 20 index is
    an Actual CALCULATED Production value, and the ONLY reason for zero
    exposure is that no independently authorized Static Owner exists. The
    Candidate Static output is deliberately not recorded as a prediction.
    """
    rid, source, cutoff, post, created = _check_source_and_time(
        intent, report, source_receipt_verified, created_at)
    if not isinstance(owner_status, dict) or owner_status.get("authorized") is not False:
        raise JRANoBetTerminalError("STATIC_OWNER_AUTHORIZED_USE_FORMAL_LIVE_PATH")
    if (report.get("production_full_numerical_ready") is not True
            or report.get("verified_full_index_count") != report.get("required_index_count")):
        raise JRANoBetTerminalError("FULL20_NOT_READY_USE_EVIDENCE_NO_BET")
    if intent.get("acceptance_only") is True and lineage == "LIVE":
        raise JRANoBetTerminalError("ACCEPTANCE_ONLY_CANNOT_BE_LIVE")
    ids = [str(x) for x in report.get("runner_universe") or []]
    if len(ids) < 2 or "" in ids or len(ids) != len(set(ids)):
        raise JRANoBetTerminalError("RUNNER_UNIVERSE_INVALID")
    prepared = report.get("prepared_numerical_request") or {}
    rows = {str(r.get("runner_id")): r for r in prepared.get("runners") or []}
    if set(rows) != set(ids):
        raise JRANoBetTerminalError("FULL20_UNIVERSE_MISMATCH")
    runners = {}
    for runner_id in ids:
        cc = rows[runner_id].get("canonical_components") or {}
        if set(cc) != set(BASE) | set(DERIVED):
            raise JRANoBetTerminalError("FULL20_INCOMPLETE:" + runner_id)
        row = {}
        for name in BASE + DERIVED:
            c = cc[name]
            num = c.get("value")
            if (str(c.get("terminal_status") or "CALCULATED").upper() != "CALCULATED"
                    or isinstance(num, bool) or not isinstance(num, (int, float))
                    or not math.isfinite(num) or not 0 <= num <= 100
                    or c.get("candidate_only") is True or c.get("production_authority") is False
                    or not c.get("rule_id") or not c.get("evidence_refs")
                    or not str(c.get("source_fact") or "").strip()):
                raise JRANoBetTerminalError("FULL20_CELL_NOT_ACTUAL:" + runner_id + ":" + name)
            row[name] = {"terminal_status": "CALCULATED", "value": num,
                         "rule_id": c["rule_id"], "evidence_refs": c["evidence_refs"],
                         "source_fact": c["source_fact"]}
        runners[runner_id] = row
    pre_cutoff = created <= cutoff and created <= post
    if lineage == "LIVE" and not pre_cutoff:
        raise JRANoBetTerminalError("LIVE_NO_BET_DECISION_AFTER_CUTOFF")
    if lineage not in ("LIVE", "HISTORICAL_DIAGNOSTIC", "ACCEPTANCE_ONLY"):
        raise JRANoBetTerminalError("TEMPORAL_LINEAGE_UNKNOWN")
    n = len(ids)
    out = {
        "profile": STATIC_PROFILE,
        "race_id": rid,
        "family_id": "JRA",
        "lineage": lineage,
        "temporal_classification": "PRE_CUTOFF" if pre_cutoff else "POST_CUTOFF_HISTORICAL",
        "source_execution_id": source.get("source_execution_id"),
        "source_snapshot_sha256": source["source_snapshot_sha256"],
        "signed_source_receipt_sha256": source["receipt_sha256"],
        "source_checkpoint_manifest_sha256": source.get("sha256"),
        "numerical_mapping_id": report.get("mapping_id"),
        "numerical_closure_mode": report.get("numerical_closure_mode"),
        "required_index_count": n * 20,
        "base_calculated_count": n * len(BASE),
        "base_held_count": 0,
        "derived_calculated_count": n * len(DERIVED),
        "derived_held_count": 0,
        "terminal_index_count": n * 20,
        "unresolved_count": 0,
        "index_universe": runners,
        "decision": "NO_BET",
        "decision_reason": "PRODUCTION_STATIC_OWNER_NOT_AUTHORIZED",
        "static_owner_activation_reason": owner_status.get("reason"),
        "first_blocked_stage": "PRODUCTION_STATIC_PREDICTION_OWNER",
        "production_full20_ready": True,
        "static_prediction_issued": False,
        "candidate_static_recorded_as_prediction": False,
        "formal_full_prediction_completed": False,
        "pre_krs_executed": False,
        "krs_executed": False,
        "signed_final_verified": False,
        "purchase_authority": False,
        "total_investment": 0,
        "tickets": [],
        "source_verified": True,
        "created_at": created.isoformat(),
        "report_sha256": report.get("sha256"),
        "evidence_attestation_required": "INDEPENDENT_GITHUB_OIDC_ARTIFACT_ATTESTATION",
    }
    out["sha256"] = digest(out)
    return out


def _verify_static_unauthorized(terminal):
    forbidden = ("formal_full_prediction_completed", "pre_krs_executed", "krs_executed",
                 "signed_final_verified", "purchase_authority", "static_prediction_issued",
                 "candidate_static_recorded_as_prediction")
    if any(terminal.get(k) is not False for k in forbidden):
        raise JRANoBetTerminalError("NO_BET_FALSE_FORMAL_COMPLETION")
    if terminal.get("production_full20_ready") is not True:
        raise JRANoBetTerminalError("STATIC_NO_BET_REQUIRES_ACTUAL_FULL20")
    if terminal.get("decision_reason") != "PRODUCTION_STATIC_OWNER_NOT_AUTHORIZED":
        raise JRANoBetTerminalError("STATIC_NO_BET_REASON_INVALID")
    universe = terminal.get("index_universe")
    if not isinstance(universe, dict) or len(universe) < 2 or any(not r for r in universe):
        raise JRANoBetTerminalError("NO_BET_RUNNER_UNIVERSE_INVALID")
    count = 0
    for rid, slots in universe.items():
        if not isinstance(slots, dict) or set(slots) != set(BASE) | set(DERIVED):
            raise JRANoBetTerminalError("NO_BET_INDEX_UNIVERSE_INCOMPLETE:" + str(rid))
        for name, cell in slots.items():
            value = cell.get("value")
            if (cell.get("terminal_status") != "CALCULATED"
                    or isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value) or not 0 <= value <= 100
                    or not cell.get("rule_id") or not cell.get("evidence_refs")
                    or not cell.get("source_fact")):
                raise JRANoBetTerminalError("STATIC_NO_BET_CELL_NOT_ACTUAL:" + rid + ":" + name)
            count += 1
    n = len(universe)
    if (count != n * 20 or terminal.get("terminal_index_count") != n * 20
            or terminal.get("required_index_count") != n * 20
            or terminal.get("base_calculated_count") != n * len(BASE)
            or terminal.get("derived_calculated_count") != n * len(DERIVED)
            or terminal.get("base_held_count") != 0
            or terminal.get("derived_held_count") != 0
            or terminal.get("unresolved_count") != 0):
        raise JRANoBetTerminalError("NO_BET_INDEX_COUNTS_INVALID")
    return {
        "status": "VERIFIED_ZERO_EXPOSURE_DECISION_ONLY",
        "decision_reason": terminal["decision_reason"],
        "race_id": terminal["race_id"],
        "lineage": terminal["lineage"],
        "terminal_index_count": count,
        "calculated_base_count": n * len(BASE),
        "calculated_derived_count": n * len(DERIVED),
        "held_base_count": 0,
        "held_derived_count": 0,
        "actual_full20": True,
        "signed_final_verified": False,
        "total_investment": 0,
        "terminal_sha256": terminal["sha256"],
    }


def verify_no_bet_terminal(terminal, *, race_id=None, require_live=False):
    """Verify complete, zero-investment terminal without equating it to FINAL.

    Cryptographic SOURCE and OIDC attestations are independently verified by
    the external runner; this deterministic validator verifies their claimed
    decision content, index universe, and zero-capital invariants.
    """
    if not isinstance(terminal, dict):
        raise JRANoBetTerminalError("NO_BET_TERMINAL_REQUIRED")
    if terminal.get("profile") not in (PROFILE, STATIC_PROFILE) or terminal.get("family_id") != "JRA":
        raise JRANoBetTerminalError("NO_BET_PROFILE_OR_FAMILY_INVALID")
    if terminal.get("profile") == STATIC_PROFILE:
        if race_id is not None and str(terminal.get("race_id")) != str(race_id):
            raise JRANoBetTerminalError("NO_BET_RACE_MISMATCH")
        if terminal.get("sha256") != digest({k: v for k, v in terminal.items() if k != "sha256"}):
            raise JRANoBetTerminalError("NO_BET_SHA256_MISMATCH")
        if terminal.get("source_verified") is not True or not terminal.get("signed_source_receipt_sha256"):
            raise JRANoBetTerminalError("NO_BET_SOURCE_UNVERIFIED")
        if require_live and (terminal.get("lineage") != "LIVE"
                             or terminal.get("temporal_classification") != "PRE_CUTOFF"):
            raise JRANoBetTerminalError("NO_BET_NOT_FORWARD_LIVE")
        if terminal.get("lineage") not in ("LIVE", "HISTORICAL_DIAGNOSTIC", "ACCEPTANCE_ONLY"):
            raise JRANoBetTerminalError("NO_BET_LINEAGE_INVALID")
        if terminal.get("decision") != "NO_BET":
            raise JRANoBetTerminalError("NO_BET_DECISION_MISMATCH")
        if terminal.get("total_investment") != 0 or terminal.get("tickets") != []:
            raise JRANoBetTerminalError("NO_BET_NONZERO_EXPOSURE")
        return _verify_static_unauthorized(terminal)
    if race_id is not None and str(terminal.get("race_id")) != str(race_id):
        raise JRANoBetTerminalError("NO_BET_RACE_MISMATCH")
    if terminal.get("sha256") != digest({k: v for k, v in terminal.items() if k != "sha256"}):
        raise JRANoBetTerminalError("NO_BET_SHA256_MISMATCH")
    if terminal.get("source_verified") is not True or not terminal.get("signed_source_receipt_sha256"):
        raise JRANoBetTerminalError("NO_BET_SOURCE_UNVERIFIED")
    if require_live and (
        terminal.get("lineage") != "LIVE"
        or terminal.get("temporal_classification") != "PRE_CUTOFF"
    ):
        raise JRANoBetTerminalError("NO_BET_NOT_FORWARD_LIVE")
    if terminal.get("lineage") not in ("LIVE", "HISTORICAL_DIAGNOSTIC"):
        raise JRANoBetTerminalError("NO_BET_LINEAGE_INVALID")
    if terminal.get("decision") != "NO_BET":
        raise JRANoBetTerminalError("NO_BET_DECISION_MISMATCH")
    forbidden = (
        "formal_full_prediction_completed",
        "pre_krs_executed",
        "krs_executed",
        "signed_final_verified",
        "purchase_authority",
        "production_full20_ready",
    )
    if any(terminal.get(k) is not False for k in forbidden):
        raise JRANoBetTerminalError("NO_BET_FALSE_FORMAL_COMPLETION")
    if terminal.get("total_investment") != 0 or terminal.get("tickets") != []:
        raise JRANoBetTerminalError("NO_BET_NONZERO_EXPOSURE")
    universe = terminal.get("index_universe")
    if not isinstance(universe, dict) or len(universe) < 2:
        raise JRANoBetTerminalError("NO_BET_RUNNER_UNIVERSE_INVALID")
    if len(universe) != len(set(universe)) or any(not rid for rid in universe):
        raise JRANoBetTerminalError("NO_BET_DUPLICATE_RUNNER")
    count, calculated, held, derived_held = 0, 0, 0, 0
    for rid, slots in universe.items():
        if not isinstance(slots, dict) or set(slots) != set(BASE) | set(DERIVED):
            raise JRANoBetTerminalError("NO_BET_INDEX_UNIVERSE_INCOMPLETE:" + str(rid))
        for name in BASE:
            cell = slots[name]
            state = cell.get("terminal_status")
            if state == "CALCULATED":
                value = cell.get("value")
                if (isinstance(value, bool) or not isinstance(value, (float, int))
                        or not math.isfinite(value) or not 0 <= value <= 100
                        or not cell.get("rule_id") or not cell.get("evidence_refs")
                        or not cell.get("source_fact")):
                    raise JRANoBetTerminalError("NO_BET_CALCULATED_INVALID:" + rid + ":" + name)
                calculated += 1
            elif state == "RULED-HOLD":
                if cell.get("value") is not None or not cell.get("reason"):
                    raise JRANoBetTerminalError("NO_BET_HOLD_HAS_VALUE:" + rid + ":" + name)
                held += 1
            else:
                raise JRANoBetTerminalError("NO_BET_BASE_NOT_TERMINAL:" + rid + ":" + name)
            count += 1
        for name in DERIVED:
            cell = slots[name]
            if (cell.get("terminal_status") != "RULED-HOLD"
                    or cell.get("value") is not None
                    or not cell.get("reason")):
                raise JRANoBetTerminalError("NO_BET_DERIVED_NOT_HELD:" + rid + ":" + name)
            derived_held += 1
            count += 1
    required = len(universe) * 20
    if (count != required or terminal.get("terminal_index_count") != required
            or terminal.get("required_index_count") != required
            or terminal.get("base_calculated_count") != calculated
            or terminal.get("base_held_count") != held
            or terminal.get("derived_held_count") != derived_held
            or terminal.get("unresolved_count") != 0
            or held < 1):
        raise JRANoBetTerminalError("NO_BET_INDEX_COUNTS_INVALID")
    return {
        "status": "VERIFIED_ZERO_EXPOSURE_DECISION_ONLY",
        "race_id": terminal["race_id"],
        "lineage": terminal["lineage"],
        "terminal_index_count": count,
        "calculated_base_count": calculated,
        "held_base_count": held,
        "held_derived_count": derived_held,
        "signed_final_verified": False,
        "total_investment": 0,
        "terminal_sha256": terminal["sha256"],
    }
