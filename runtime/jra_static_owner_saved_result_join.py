"""Offline qualification and saved RESULT join for the existing Static shadow.

Uses the existing evaluator; never fetches, signs, dispatches or changes a
Production artifact. Callers must supply independently verified saved inputs.
Missing witnesses stay UNKNOWN. Fixed BVI D OOS is a different ledger.
"""
from datetime import timedelta


def gate(status, reason=None, **evidence):
    return {"status": status, "reason": reason, **evidence}


def _known_gate(value):
    if not isinstance(value, dict) or value.get("status") not in {"PASS", "FAIL", "UNKNOWN"}:
        return gate("UNKNOWN", "UNRECOGNIZED_GATE_STATUS", supplied_gate=value)
    return value


def _qualification_body(value):
    return {key: value[key] for key in ("race_id", "frozen_sha256", "verified_commit_at", "status", "checks")}


def qualify(pre, *, module, commit_at, source, code, scope, registration=None):
    checks = {}
    digest = module.sha
    checks["frozen_hash"] = gate("PASS" if pre.get("sha256") == digest(
        {k: v for k, v in pre.items() if k != "sha256"}) else "FAIL", "FROZEN_CANONICAL_HASH")
    cohort = (pre.get("profile") == module.PROFILE and pre.get("owner_profile") == module.OWNER_PROFILE
              and pre.get("candidate_only") is True and pre.get("production_authority") is False
              and pre.get("purchase_authority") is False and pre.get("signed_final_issued") is False)
    other_owner = (pre.get("profile") == module.PROFILE and pre.get("owner_profile") != module.OWNER_PROFILE)
    checks["research_cohort"] = gate("PASS" if cohort else "FAIL",
        "HISTORICAL_OWNER_PROFILE_DIFFERENT_FROM_CURRENT_EVALUATOR" if other_owner else "STATIC_OWNER_COHORT_AND_AUTHORITY")
    ranking = pre.get("ranking") or []
    market = pre.get("market_ranking") or []
    owner = pre.get("owner") or {}
    universe = (len(ranking) == len(set(ranking)) and len(ranking) >= 3
                and len(market) == len(set(market)) == len(ranking) and set(market) == set(ranking)
                and pre.get("full_index_count") == len(ranking) * 20
                and (owner.get("static_prediction") or {}).get("ranking") == ranking
                and owner.get("source_snapshot_sha256") == pre.get("source_snapshot_sha256")
                and owner.get("source_receipt_sha256") == pre.get("source_receipt_sha256")
                and owner.get("sha256") == digest({k: v for k, v in owner.items() if k != "sha256"}))
    checks["frozen_universe"] = gate("PASS" if universe else "FAIL", "FULL20_OWNER_SOURCE_UNIVERSE")
    try:
        frozen = module.time(pre["frozen_at"])
        cutoff = module.time(pre["prediction_cutoff"])
        post = module.time(pre["scheduled_post_at"])
        if not frozen <= cutoff < post:
            checks["prospective_witness"] = gate("FAIL", "FROZEN_OR_CUTOFF_AFTER_POST")
        elif not commit_at:
            checks["prospective_witness"] = gate("UNKNOWN", "GIT_COMMIT_WITNESS_MISSING")
        else:
            commit = module.time(commit_at)
            if frozen <= commit <= cutoff:
                checks["prospective_witness"] = gate("PASS", "GITHUB_PATH_HISTORY_BEFORE_CUTOFF")
            elif commit <= frozen < commit + timedelta(seconds=1) and commit.microsecond == 0:
                checks["prospective_witness"] = gate("UNKNOWN", "GIT_COMMIT_SECOND_PRECISION")
            else:
                checks["prospective_witness"] = gate("FAIL", "GIT_COMMIT_OUTSIDE_FROZEN_CUTOFF_INTERVAL")
    except (ValueError, KeyError, TypeError):
        checks["prospective_witness"] = gate("FAIL", "INVALID_TEMPORAL_FIELDS")
    checks["source"] = _known_gate(source)
    checks["code_policy_pin"] = _known_gate(code)
    checks["scope"] = _known_gate(scope)
    # The pre_result record is the existing research registration. A separate
    # Production intake record is reported, never made a new research gate.
    checks["research_registration"] = gate("PASS" if cohort and commit_at else "UNKNOWN",
        "EXISTING_PRE_RESULT_RESEARCH_REGISTRATION", production_intake=registration or "NOT_OBSERVED")
    statuses = {x["status"] for x in checks.values()}
    state = "INELIGIBLE" if "FAIL" in statuses else "UNKNOWN" if "UNKNOWN" in statuses else "ELIGIBLE_UNDER_EXISTING_RESEARCH_CONTRACT"
    if other_owner and checks["frozen_hash"]["status"] == "PASS":
        state = "OUTSIDE_CURRENT_OWNER_COHORT"
    result = {"race_id": pre.get("race_id"), "frozen_sha256": pre.get("sha256"), "verified_commit_at": commit_at, "status": state, "checks": checks,
              "fixed_bvi_d_oos_increment": 0, "production_effect": "NONE"}
    result["qualification_sha256"] = digest(_qualification_body(result))
    return result


def join_saved_result(pre, qualification, request, envelope, *, module, verify_receipt, signer, commit_at):
    """Verify an existing signed RESULT and call the existing Static evaluator.

    A matched result and a qualified OOS evaluation are independent outputs.
    Invalid inputs raise, so failed validation cannot become a zero outcome.
    """
    if (qualification.get("race_id") != pre.get("race_id")
            or qualification.get("frozen_sha256") != pre.get("sha256")
            or qualification.get("verified_commit_at") != commit_at
            or qualification.get("qualification_sha256") != module.sha(_qualification_body(qualification))):
        raise ValueError("SAVED_RESULT_QUALIFICATION_BINDING_MISMATCH")
    if (qualification.get("status") == "ELIGIBLE_UNDER_EXISTING_RESEARCH_CONTRACT"
            and any(x.get("status") != "PASS" for x in qualification["checks"].values())):
        raise ValueError("SAVED_RESULT_QUALIFICATION_GATE_NOT_PASS")
    if request.get("race_id") != pre.get("race_id"):
        raise ValueError("SAVED_RESULT_RACE_MISMATCH")
    receipt = verify_receipt(envelope, signer, pre["race_id"], "RESULT")
    if receipt.get("artifact_sha256") != module.sha(request):
        raise ValueError("SAVED_RESULT_ARTIFACT_HASH_MISMATCH")
    official = request.get("official_result") or {}
    if official.get("status") != "OFFICIAL" or official.get("result_use") != "POST-RACE":
        raise ValueError("SAVED_RESULT_NOT_OFFICIAL_POST_RACE")
    observed = official.get("captured_at")
    if not observed or not module.time(pre["scheduled_post_at"]) < module.time(observed) <= module.time(receipt["timestamp"]):
        raise ValueError("SAVED_RESULT_OBSERVED_TIME_INVALID")
    top3 = [str(x) for x in official.get("top3") or []]
    if len(top3) != 3 or len(set(top3)) != 3 or not set(top3).issubset(pre["ranking"]):
        raise ValueError("SAVED_RESULT_UNIVERSE_MISMATCH")
    finish_order = [str(x) for x in official.get("finish_order") or []]
    if finish_order and (finish_order[:3] != top3 or len(finish_order) != len(set(finish_order))
                         or not set(finish_order).issubset(pre["ranking"])):
        raise ValueError("SAVED_RESULT_FINISH_ORDER_MISMATCH")
    out = {"race_id": pre["race_id"], "signed_result_matched": True,
           "result_artifact_sha256": receipt["artifact_sha256"],
           "result_receipt_sha256": envelope["receipt_sha256"],
           "result_captured_at": observed, "top3": top3,
           "static_shadow_evaluation_created": False, "fixed_bvi_d_oos_increment": 0,
           "production_effect": "NONE"}
    if qualification["status"] == "ELIGIBLE_UNDER_EXISTING_RESEARCH_CONTRACT":
        evaluated = module.evaluate(pre, top3, result_sha256=receipt["artifact_sha256"],
                                    observed_at=observed, git_commit_at=commit_at)
        out.update(static_shadow_evaluation_created=True, evaluation=evaluated)
    else:
        out["evaluation_blocker"] = qualification["status"]
    return out
