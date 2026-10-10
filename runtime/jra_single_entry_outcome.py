"""Single Entry outcome accounting; never a signature verifier or promotion."""
from __future__ import annotations

from datetime import datetime


def evidence_terminal_eligible(report):
    """Only a demonstrated missing Base evidence failure can use this terminal."""
    return (
        # The numerical gate is evaluated first; an unapproved Owner may be
        # appended as an independent blocker ("|INDEPENDENT_BLOCKERS:...").
        str(report.get("auto_handoff_error") or "").split("|", 1)[0] == "JRA_AUTHORIZED_FULL20_INCOMPLETE"
        and report.get("production_full_numerical_ready") is False
        and report.get("first_blocked_stage") == "PRODUCTION_FEATURE_INDEX_CLOSURE"
        and report.get("partial_base_blocked_count", 0) > 0
    )


def verify_formal_completion_summary(summary, request):
    """Validate the canonical external worker's verification summary.

    The caller must obtain this artifact from the successful canonical run.
    This content check does not independently verify cryptographic signatures.
    Replay and acceptance success cannot become Production pre-race success.
    """
    def require(ok, reason):
        if not ok:
            raise ValueError("JRA_SINGLE_ENTRY_COMPLETION_" + reason)

    require(summary.get("status") == "FULL_FORMAL_E2E_PASS", "STATUS")
    require(summary.get("race_id") == request.get("race_id")
            and summary.get("family_id") == "JRA"
            and request.get("family_id") == "JRA", "IDENTITY")
    require(summary.get("temporal_formality") == "FORMAL-PRE-RACE"
            and summary.get("acceptance_only") is False
            and request.get("temporal_mode", "FORMAL-PRE-RACE") == "FORMAL-PRE-RACE"
            and request.get("acceptance_only") is not True, "REPLAY_OR_ACCEPTANCE")
    require(summary.get("source_snapshot_sha256") == request.get("source_snapshot_sha256")
            and bool(request.get("source_snapshot_sha256")), "SOURCE_BINDING")
    stages = summary.get("execution_stage_manifest") or {}
    require(bool(stages) and all(x.get("status") == "PASS" for x in stages.values())
            and summary.get("all_mandatory_stages_verified") is True
            and summary.get("all_mandatory_pre_race_stages_verified") is True, "STAGES")
    manifest = summary.get("manifest") or {}
    required = len(request.get("runners") or []) * 20
    require(required > 0 and manifest.get("required_count") == required
            and manifest.get("calculated_count") == required
            and all(manifest.get(k) == 0 for k in (
                "ruled_hold_count", "not_applicable_count", "unresolved_count")), "FULL20")
    for phase in ("pre_krs", "krs", "final"):
        receipt = summary.get(phase) or {}
        require(receipt.get("verified") is True
                and len(str(receipt.get("receipt_sha256") or "")) == 64,
                phase.upper() + "_VERIFICATION")
    krs = summary["krs"]
    count = request.get("run_count", 5000)
    require(krs.get("requested_run_count") == count
            and krs.get("actual_run_count") == count
            and type(count) is int and count in (5000, 20000), "KRS_COUNT")
    try:
        final_time = datetime.fromisoformat(str(summary["final"].get("receipt_timestamp")).replace("Z", "+00:00"))
        post = datetime.fromisoformat(str(request.get("scheduled_post_at")).replace("Z", "+00:00"))
        require(final_time.tzinfo is not None and post.tzinfo is not None
                and final_time < post, "FINAL_AFTER_POST")
    except (TypeError, ValueError) as exc:
        raise ValueError("JRA_SINGLE_ENTRY_COMPLETION_FINAL_TIME_INVALID") from exc
    require(len(str(summary["final"].get("immutable_artifact_sha256") or "")) == 64,
            "IMMUTABLE_FINAL")
    return {"production_full_prediction_completed": True,
            "status": "FORMAL_COMPLETE", "race_id": summary["race_id"],
            "signed_final_receipt_sha256": summary["final"]["receipt_sha256"],
            "verification_owner": "CANONICAL_EXTERNAL_FORMAL_RUNNER",
            "independent_signature_verification_by_this_function": False}
