"""Zero-exposure terminal for a reproducible, authorized AKI selection stop.

No threshold changes, fallback runners, KRS execution or Signed FINAL. The
external Single Entry verifies SOURCE/OIDC; this module replays the exact
registered selector and preserves its positive-evidence failure.
"""
from copy import deepcopy
from pathlib import Path
import json

from jra_aki_capital_preflight import AKICapitalError, sha
from jra_aki_v21 import materialize, _select, _time
from jra_aki_dispatch import apply_authorized_v21
from jra_aki_v21_features import compile_features

PROFILE = "KM-JRA-PRODUCTION-AKI-SELECTION-NO-BET-TERMINAL-v1-20261012"
STAGE = "PRODUCTION_AKI_COLUMN_SELECTION"
ROUTE = "AKI_SELECTION_INSUFFICIENT_NO_BET"
ADMISSIBLE = {"AKI_EVIDENCE_SELECTED_COLUMN_EMPTY", "AKI_SINGLE_HEAD_FORBIDDEN"}


def _authority(manifest_id, root):
    # Resolve the recorded authority, not a newer manifest for an old race.
    name = str(manifest_id).replace("-", "_")
    if not name or any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_" for c in name):
        raise ValueError("AKI_NO_BET_AUTHORITY_ID_INVALID")
    obj = json.loads((Path(root) / "profiles" / (name + ".json")).read_text())
    if obj.get("manifest_id") != manifest_id:
        raise ValueError("AKI_NO_BET_AUTHORITY_MISMATCH")
    return obj


def diagnose(request, source, *, authority, root="."):
    """Require the real registered executor to reproduce an allowed stop."""
    try:
        apply_authorized_v21(request, source, authority, root=root)
    except AKICapitalError as exc:
        code = str(exc)
        if code not in ADMISSIBLE:
            raise
    else:
        raise ValueError("AKI_NO_BET_SELECTION_SUCCEEDED")
    activation = authority["family_scoped_authority"]["JRA"]["aki_v21_activation"]
    components = json.loads((Path(root) / activation["components"]["path"]).read_text())
    columns = json.loads((Path(root) / activation["columns"]["path"]).read_text())
    enriched = compile_features(request, source, components["feature_compiler_policy"])
    _, calculation = materialize(enriched, components,
                                 registry_hash=activation["components"]["sha256"])
    axes = calculation["axes"]
    triggers = {"W": "REVIEW" if axes["W-AKI"] >= 50 or axes["ASI"] < 65 else "BASE",
                "P2": "REVIEW" if axes["P2-AKI"] >= 50 or axes["RSI"] >= 60 else "BASE",
                "P3": "REVIEW" if axes["P3-AKI"] >= 50 or axes["RSI"] >= 60 else "BASE"}
    policy = components["feature_compiler_policy"]
    runner_values = {str(r["runner_id"]): r["canonical_components"] for r in request["runners"]}
    rows, selected = [], {c: [] for c in triggers}
    for rid in request["static_prediction"]["ranking"]:
        for c, mode in triggers.items():
            fact = enriched["aki_selection_features"]["runners"][rid][c]
            raw = fact["source_fact"]
            rules = list(columns["columns"][c]["BASE"])
            if mode == "REVIEW":
                rules += columns["columns"][c]["REVIEW"]
            matches = _select({c: fact}, rules, cutoff=_time(source["prediction_cutoff"]),
                              source_hash=source["source_snapshot_sha256"])
            if matches:
                selected[c].append(rid)
            reasons = []
            if raw["value"] < policy["role_quality_floor"]:
                reasons.append("ROLE_INDEX_BELOW_FLOOR")
            if raw["support_group_count"] < 2:
                reasons.append("SUPPORT_GROUP_COUNT_BELOW_TWO")
            if raw["normalized_gap"] > policy["column_gap"][c][mode]:
                reasons.append("ROLE_GAP_OUTSIDE_REGISTERED_RANGE")
            rows.append({"runner_id": rid, "column": c, "selected": bool(matches),
                         "category": fact["category"], "review_mode": mode,
                         "reasons": reasons,
                         "support_indices": {k: runner_values[rid][k]["value"] for k in policy["support_groups"][c]},
                         "support_floor": policy["support_floor"],
                         "role_quality_floor": policy["role_quality_floor"],
                         "gap_limit": policy["column_gap"][c][mode], **deepcopy(raw)})
    out = {"code": code, "stage": STAGE, "race_id": request["race_id"],
           "authority_manifest": authority["manifest_id"],
           "source_snapshot_sha256": source["source_snapshot_sha256"],
           "full20_sha256": sha(request["runners"]), "axes": axes,
           "triggers": triggers, "columns": selected,
           "empty_columns": [c for c, ids in selected.items() if not ids],
           "selection_ledger": rows, "registered_selector_reproduced": True}
    out["sha256"] = sha(out)
    return out


def record_selection_failure(report, request, source, authority, *, root="."):
    """Capture proof without modifying signed SOURCE or the activated selector."""
    req = {k: deepcopy(request[k]) for k in ("family_id", "race_id", "prediction_cutoff",
            "source_snapshot_sha256", "runners", "static_prediction")}
    src = {k: deepcopy(source[k]) for k in ("family_id", "race_id", "prediction_cutoff",
            "source_snapshot_sha256", "source_freeze_at")}
    for k in ("conflicts", "aki_external_observations"):
        if k in source:
            src[k] = deepcopy(source[k])
    report["aki_selection_failure"] = {
        "request": req, "source": src, "authority_manifest": authority["manifest_id"],
        "diagnostic": diagnose(req, src, authority=authority, root=root)}


def verify_failure(report, *, root="."):
    proof = report.get("aki_selection_failure") or {}
    authority = _authority(proof.get("authority_manifest"), root)
    from jra_production_auto_handoff import require_independent_owner_activation
    require_independent_owner_activation(authority, root=root)
    request, source = proof["request"], proof["source"]
    prepared = report.get("prepared_numerical_request") or {}
    checkpoint = report.get("source_checkpoint_manifest") or {}
    if (report.get("production_full_numerical_ready") is not True
            or report.get("verified_full_index_count") != report.get("required_index_count")
            or request["race_id"] != report.get("race_id")
            or request["runners"] != prepared.get("runners")
            or request["static_prediction"]["ranking"] != (
                report.get("static_owner_executable_diagnostic") or {}).get("static_prediction", {}).get("ranking")
            or proof["authority_manifest"] != report.get("current_authority_manifest")
            or source["source_snapshot_sha256"] != checkpoint.get("source_snapshot_sha256")
            or source["prediction_cutoff"] != checkpoint.get("prediction_cutoff")
            or source["source_freeze_at"] != checkpoint.get("source_freeze_at")):
        raise ValueError("AKI_NO_BET_REPORT_BINDING_INVALID")
    diagnostic = diagnose(request, source, authority=authority, root=root)
    if proof.get("diagnostic") != diagnostic or report.get("auto_handoff_error") != diagnostic["code"]:
        raise ValueError("AKI_NO_BET_FAILURE_NOT_REPRODUCIBLE")
    return diagnostic


def terminal_eligible(report, *, root="."):
    if report.get("auto_handoff_error") not in ADMISSIBLE:
        return False
    try:
        verify_failure(report, root=root)
        return (report.get("static_owner_activation_status") or {}).get("authorized") is True
    except (ValueError, KeyError, TypeError, OSError):
        return False


def build_aki_no_bet_terminal(intent, report, *, source_receipt_verified=False,
                              created_at=None, lineage="LIVE", root="."):
    from jra_production_no_bet_terminal import _check_source_and_time, JRANoBetTerminalError
    rid, checkpoint, cutoff, post, created = _check_source_and_time(
        intent, report, source_receipt_verified, created_at)
    if not terminal_eligible(report, root=root):
        raise JRANoBetTerminalError("AKI_NO_BET_PROOF_REQUIRED")
    if lineage not in ("LIVE", "HISTORICAL_DIAGNOSTIC") or (
            lineage == "LIVE" and (created > cutoff or intent.get("acceptance_only") is True)):
        raise JRANoBetTerminalError("AKI_NO_BET_LIVE_TEMPORAL_INVALID")
    out = {"profile": PROFILE, "family_id": "JRA", "race_id": rid,
           "lineage": lineage, "temporal_classification": "PRE_CUTOFF" if created <= cutoff else "POST_CUTOFF_HISTORICAL",
           "created_at": created.isoformat(), "prediction_cutoff": cutoff.isoformat(),
           "scheduled_post_at": post.isoformat(), "source_freeze_at": checkpoint["source_freeze_at"],
           "source_snapshot_sha256": checkpoint["source_snapshot_sha256"],
           "signed_source_receipt_sha256": checkpoint["receipt_sha256"],
           "source_execution_id": checkpoint.get("source_execution_id"), "source_verified": True,
           "report_sha256": report.get("sha256"), "failure_report": deepcopy(report),
           "decision": "NO_BET", "decision_reason": report["auto_handoff_error"],
           "first_blocked_stage": STAGE, "production_full20_ready": True,
           "required_index_count": report["required_index_count"],
           "index_universe": {str(r["runner_id"]): {
               k: {**deepcopy(v), "terminal_status": "CALCULATED"}
               for k, v in r["canonical_components"].items()}
               for r in report["prepared_numerical_request"]["runners"]},
           "terminal_index_count": report["verified_full_index_count"],
           "base_calculated_count": len(report["runner_universe"]) * 13,
           "derived_calculated_count": len(report["runner_universe"]) * 7,
           "base_held_count": 0, "derived_held_count": 0, "unresolved_count": 0,
           "formal_full_prediction_completed": False, "pre_krs_executed": False,
           "krs_executed": False, "signed_final_verified": False, "purchase_authority": False,
           "total_investment": 0, "tickets": [],
           "evidence_attestation_required": "INDEPENDENT_GITHUB_OIDC_ARTIFACT_ATTESTATION"}
    out["sha256"] = sha(out)
    verify_aki_no_bet_terminal(out, root=root)
    return out


def verify_aki_no_bet_terminal(terminal, *, race_id=None, require_live=False, root="."):
    from jra_production_no_bet_terminal import JRANoBetTerminalError
    def require(ok, code):
        if not ok:
            raise JRANoBetTerminalError(code)
    require(terminal.get("profile") == PROFILE and terminal.get("family_id") == "JRA", "AKI_NO_BET_PROFILE_INVALID")
    require(terminal.get("sha256") == sha({k:v for k,v in terminal.items() if k != "sha256"}), "NO_BET_SHA256_MISMATCH")
    require(race_id is None or race_id == terminal.get("race_id"), "NO_BET_RACE_MISMATCH")
    require(terminal.get("source_verified") is True, "NO_BET_SOURCE_UNVERIFIED")
    require(terminal.get("decision") == "NO_BET" and terminal.get("total_investment") == 0
            and terminal.get("tickets") == [], "NO_BET_NONZERO_EXPOSURE")
    require(all(terminal.get(k) is False for k in ("formal_full_prediction_completed", "pre_krs_executed",
            "krs_executed", "signed_final_verified", "purchase_authority")), "NO_BET_FALSE_FORMAL_COMPLETION")
    require(terminal.get("lineage") in ("LIVE", "HISTORICAL_DIAGNOSTIC"), "NO_BET_LINEAGE_INVALID")
    created, cutoff, post, freeze = [_time(terminal[k]) for k in
                                    ("created_at", "prediction_cutoff", "scheduled_post_at", "source_freeze_at")]
    pre = created <= cutoff
    require(freeze <= cutoff < post and (terminal["lineage"] != "LIVE" or pre), "NO_BET_TEMPORAL_INVALID")
    require(terminal.get("temporal_classification") == ("PRE_CUTOFF" if pre else "POST_CUTOFF_HISTORICAL"), "NO_BET_TEMPORAL_LABEL_INVALID")
    require(not require_live or (terminal["lineage"] == "LIVE" and pre), "NO_BET_NOT_FORWARD_LIVE")
    report = terminal["failure_report"]
    diagnostic = verify_failure(report, root=root)
    require(terminal_eligible(report, root=root), "AKI_NO_BET_PROOF_REQUIRED")
    checkpoint = report["source_checkpoint_manifest"]
    require(terminal["race_id"] == report["race_id"] and terminal["decision_reason"] == diagnostic["code"]
            and terminal["first_blocked_stage"] == STAGE and terminal["production_full20_ready"] is True,
            "AKI_NO_BET_IDENTITY_INVALID")
    require(terminal["report_sha256"] == report.get("sha256")
            and report.get("sha256") == sha({k:v for k,v in report.items() if k != "sha256"}), "AKI_NO_BET_REPORT_HASH_INVALID")
    require(terminal["source_snapshot_sha256"] == checkpoint["source_snapshot_sha256"]
            and terminal["signed_source_receipt_sha256"] == checkpoint["receipt_sha256"]
            and freeze == _time(checkpoint["source_freeze_at"])
            and cutoff == _time(checkpoint["prediction_cutoff"]), "AKI_NO_BET_SOURCE_BINDING_INVALID")
    rows = report["prepared_numerical_request"]["runners"]
    require(terminal.get("index_universe") == {str(r["runner_id"]): {
        k: {**v, "terminal_status": "CALCULATED"} for k,v in r["canonical_components"].items()}
        for r in rows}, "AKI_NO_BET_INDEX_LEDGER_MISMATCH")
    ids = [str(r["runner_id"]) for r in rows]
    require(set(ids) == set(map(str, report["runner_universe"])) and len(ids) == len(set(ids)), "NO_BET_RUNNER_UNIVERSE_INVALID")
    for r in rows:
        for c in r["canonical_components"].values():
            require(c.get("terminal_status", "CALCULATED") == "CALCULATED"
                    and c.get("candidate_only") is not True and c.get("production_authority") is not False,
                    "AKI_NO_BET_FULL20_NOT_PRODUCTION")
    n = len(ids)
    require(n >= 3 and terminal["required_index_count"] == terminal["terminal_index_count"] == n*20
            and report["required_index_count"] == n*20 and terminal["base_calculated_count"] == n*13
            and terminal["derived_calculated_count"] == n*7
            and all(terminal[k] == 0 for k in ("base_held_count", "derived_held_count", "unresolved_count")),
            "NO_BET_INDEX_COUNTS_INVALID")
    return {"status": "VERIFIED_ZERO_EXPOSURE_DECISION_ONLY", "race_id": terminal["race_id"],
            "decision_reason": diagnostic["code"], "first_blocked_stage": STAGE,
            "lineage": terminal["lineage"], "actual_full20": True, "terminal_index_count": n*20,
            "calculated_base_count": n*13, "calculated_derived_count": n*7,
            "held_base_count": 0, "held_derived_count": 0,
            "signed_final_verified": False, "total_investment": 0, "terminal_sha256": terminal["sha256"]}
