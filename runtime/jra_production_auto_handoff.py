"""Authority-gated *mechanical* JRA Production Full20 -> Static -> PRE_KRS.

No fallback scores, no self-promotion, no signature forgery, no late freeze.
An absent or negative Current Authority gate stops before transport.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from jra_static_owner_executable import PROFILE as OWNER_PROFILE, compile_static_owner
from jra_krs_input_builder_production import build_krs_input
from formal_request_validator import (
    validate_pre_krs_request, validate_production_authority,
    validate_orchestration_ref,
)


class JRAProductionAutoHandoffError(ValueError):
    pass


def _canon(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()


def _iso(value):
    try:
        v = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return v.astimezone(timezone.utc) if v.tzinfo else None
    except (TypeError, ValueError):
        return None


def require_independent_owner_activation(current_authority, *, root="."):
    """Accept ONLY separately recorded, immutable and empirically cleared governance."""
    jra = ((current_authority.get("family_scoped_authority") or {}).get("JRA") or {})
    approval = jra.get("production_static_owner_activation") or {}
    if (approval.get("status") != "PRODUCTION_AUTHORIZED"
            or approval.get("profile") != OWNER_PROFILE
            or approval.get("automatic_promotion") is not False
            or approval.get("explicit_production_review") is not True
            or approval.get("forward_oos_eligible_races", 0) < 30
            or approval.get("market_baseline_superiority_proven") is not True):
        raise JRAProductionAutoHandoffError("JRA_PRODUCTION_STATIC_OWNER_NOT_AUTHORIZED")
    expected = hashlib.sha256(
        (Path(root) / "runtime/jra_static_owner_executable.py").read_bytes()
    ).hexdigest()
    if approval.get("policy_source_sha256") != expected:
        raise JRAProductionAutoHandoffError("JRA_STATIC_POLICY_CODE_FINGERPRINT_MISMATCH")
    review_sha = str(approval.get("independent_review_receipt_sha256") or "")
    if len(review_sha) != 64 or any(c not in "0123456789abcdef" for c in review_sha):
        raise JRAProductionAutoHandoffError("JRA_STATIC_INDEPENDENT_REVIEW_RECEIPT_REQUIRED")
    return approval


def compile_production_auto_handoff(intent, source_env, report, *, current_authority,
                                    frozen_at, root="."):
    """Only executed after signed SOURCE verification and complete official Full20.

    Produces the existing Formal Runner's PRE_KRS-compatible request; no
    external execution, KRS or FINAL is claimed by this local conversion.
    """
    if str(intent.get("family_id") or "") != "JRA":
        raise JRAProductionAutoHandoffError("JRA_ONLY")
    closure_mode = report.get("numerical_closure_mode")
    verified_supplement = (
        closure_mode == "WITH_SUPPLEMENTAL_EVIDENCE"
        and intent.get("acceptance_only") is not True
        and isinstance(intent.get("supplemental_evidence_pack"), dict)
    )
    if (report.get("production_full_numerical_ready") is not True
            or not (report.get("source_only_full_numerical_ready") is True or verified_supplement)
            or report.get("verified_full_index_count") != report.get("required_index_count")):
        raise JRAProductionAutoHandoffError("JRA_AUTHORIZED_FULL20_INCOMPLETE")
    require_independent_owner_activation(current_authority, root=root)
    owner = report.get("static_owner_executable_diagnostic")
    if not isinstance(owner, dict) or not owner.get("static_prediction"):
        raise JRAProductionAutoHandoffError("JRA_STATIC_OWNER_EXECUTION_NOT_AVAILABLE")
    official = source_env.get("artifact") or {}
    snap_sha = str(official.get("source_snapshot_sha256") or "")
    snap = {k: v for k, v in official.items() if k != "source_snapshot_sha256"}
    if not snap_sha or _canon(snap) != snap_sha:
        raise JRAProductionAutoHandoffError("JRA_SOURCE_SNAPSHOT_HASH_INVALID")
    if owner.get("source_snapshot_sha256") != snap_sha:
        raise JRAProductionAutoHandoffError("JRA_STATIC_SOURCE_BASIS_MISMATCH")
    if owner.get("source_receipt_sha256") != source_env.get("receipt_sha256"):
        raise JRAProductionAutoHandoffError("JRA_STATIC_SOURCE_RECEIPT_MISMATCH")
    # The external report is not a Static authority. Recalculate Static solely
    # from the already verified Production Full20 ledger, and require the exact
    # same immutable content hash before any PRE_KRS transport.
    prepared = report.get("prepared_numerical_request") or {}
    if prepared.get("family_id") != "JRA":
        raise JRAProductionAutoHandoffError("JRA_PREPARED_PRODUCTION_LEDGER_MISSING")
    try:
        canonical_owner = compile_static_owner(
            prepared,
            source_snapshot_sha256=snap_sha,
            source_receipt_sha256=source_env["receipt_sha256"],
            frozen_at=owner.get("frozen_at"),
            prediction_cutoff=intent["prediction_cutoff"],
        )
    except (ValueError, KeyError, TypeError) as exc:
        raise JRAProductionAutoHandoffError(
            "JRA_STATIC_PRODUCTION_LEDGER_RECOMPUTE_FAILED:" + str(exc)
        ) from exc
    declared_owner_sha = owner.get("sha256")
    actual_owner_sha = _canon({k: v for k, v in owner.items() if k != "sha256"})
    if (declared_owner_sha != actual_owner_sha
            or declared_owner_sha != canonical_owner.get("sha256")):
        raise JRAProductionAutoHandoffError("JRA_STATIC_OWNER_CONTENT_HASH_MISMATCH")
    freeze = _iso(frozen_at)
    cutoff = _iso(intent.get("prediction_cutoff"))
    dispatch = _iso(intent.get("external_dispatch_deadline_at"))
    post = _iso(intent.get("scheduled_post_at"))
    if not all((freeze, cutoff, dispatch, post)) or not freeze <= cutoff <= dispatch < post:
        raise JRAProductionAutoHandoffError("JRA_STATIC_OR_DISPATCH_TIME_INVALID")
    owner_frozen = _iso(owner.get("frozen_at"))
    if owner_frozen is None or owner_frozen > cutoff or owner_frozen > freeze:
        raise JRAProductionAutoHandoffError("JRA_STATIC_OWNER_FREEZE_AFTER_CUTOFF")
    if (str(official.get("race_id")) != str(intent.get("race_id"))
            or str(official.get("prediction_cutoff")) != str(intent.get("prediction_cutoff"))):
        raise JRAProductionAutoHandoffError("JRA_SIGNED_SOURCE_RACE_BINDING_MISMATCH")
    req = deepcopy(intent)
    req.update({
        "source_snapshot": snap, "source_snapshot_sha256": snap_sha,
        "runners": deepcopy(prepared["runners"]),
        "index_provenance_ledger": deepcopy(prepared["index_provenance_ledger"]),
        "index_provenance_hash": prepared["index_provenance_hash"],
        "numeric_calculation_requirement": "FULL_REQUIRED",
        "base_index_mapping_authority": deepcopy(prepared["base_index_mapping_authority"]),
    })
    # Runtime must supply an actual Base44 session. Never mint one here.
    validate_orchestration_ref(req)
    static = deepcopy(owner["static_prediction"])
    static.update(status="FROZEN-PRE-KRS / PRODUCTION", production_authority=True)
    req["static_prediction"] = static
    req["static_prediction_frozen"] = True
    for name in ("role_registry", "pair_dispositions", "third_dispositions"):
        req[name] = [
            {**deepcopy(item), "production_authority": True}
            for item in owner[name]
        ]
    req["purchased_heads"] = deepcopy(owner["purchased_heads"])
    req["head_nonselection_reasons"] = {}
    req["orientation_exclusions"] = []
    req["available_bet_types"] = ["EXACTA", "TRIO", "TRIFECTA"]
    req["static_owner_activation_binding"] = {
        "policy_id": OWNER_PROFILE,
        "independent_review_receipt_sha256": (
            current_authority["family_scoped_authority"]["JRA"]
            ["production_static_owner_activation"]["independent_review_receipt_sha256"]
        ),
        "production_effect": "AUTHORIZED_ONLY",
        "source_snapshot_sha256": snap_sha,
    }
    req = build_krs_input(req)
    validate_production_authority(req)
    validate_pre_krs_request(req)
    return req
