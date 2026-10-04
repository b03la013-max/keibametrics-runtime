from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Dict, Iterable, List, Tuple

PROFILE = "KM-JRA-CANDIDATE-RISK-BUDGET-SEMANTIC-EXPANSION-v0.1-20261004"
BASE_SEMANTIC_PROFILE = "KM-JRA-SOURCE-DERIVED-CANDIDATE-SEMANTICS-v0.2-20261003-WIDTH-BALANCED"
ACTIVE = {"CORE", "PROTECTED", "CONDITIONAL", "RESIDUAL"}
ROLE_ORDER = {"W": 0, "P2": 1, "P3": 2}

# These are only diagnostic dimensions already materialized in the Candidate lane.
# No new numerical formula or Production weight is introduced here.
MULTI_AXIS = (
    "ZAI_WIN", "ZAI_PLACE", "T3I", "F3S", "SRI", "DCR",
    "SSI", "CFI", "RFI", "GCI", "PRI", "VMI", "BWI",
)
EXTREME_AXES = ("SSI", "CFI", "RFI", "GCI", "PRI", "VMI", "BWI", "DCR")


class RiskBudgetExpansionError(ValueError):
    pass


def _sha(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _value(runner: Dict[str, Any], name: str) -> float | None:
    row = (runner.get("canonical_components") or {}).get(name)
    if not isinstance(row, dict) or row.get("value") is None:
        return None
    try:
        return float(row["value"])
    except (TypeError, ValueError):
        return None


def _rank_map(runners: List[Dict[str, Any]], name: str) -> Dict[str, int]:
    rows = []
    for r in runners:
        v = _value(r, name)
        if v is None:
            continue
        rows.append((str(r["runner_id"]), v))
    rows.sort(key=lambda x: (-x[1], int(x[0]) if x[0].isdigit() else x[0]))
    return {rid: i + 1 for i, (rid, _) in enumerate(rows)}


def _active(req: Dict[str, Any], column: str) -> set[str]:
    return {
        str(x["runner_id"])
        for x in (req.get("role_registry") or [])
        if str(x.get("column")) == column and str(x.get("status")) in ACTIVE
    }


def _budget_limit(req: Dict[str, Any]) -> tuple[int, str]:
    p = req.get("capital_policy")
    if isinstance(p, dict) and str(p.get("mode") or "").upper() == "HARD_RACE_BUDGET":
        cap = p.get("max_race_capital")
        if isinstance(cap, int) and cap > 0:
            return cap, "REQUEST_EXPLICIT"
    try:
        from capital_policy import load_family_default_capital_policy
        p = load_family_default_capital_policy()
        cap = int(p.get("max_race_capital") or 0)
        if cap > 0:
            return cap, "FAMILY_USER_DEFAULT"
    except Exception:
        pass
    return 10000, "SAFE_FALLBACK_10000"


def _proposal_candidates(req: Dict[str, Any]) -> List[Dict[str, Any]]:
    runners = req.get("runners") or []
    by = {str(r["runner_id"]): r for r in runners}
    rank = {name: _rank_map(runners, name) for name in MULTI_AXIS}
    active_w, active_p2, active_p3 = _active(req, "W"), _active(req, "P2"), _active(req, "P3")
    proposals: List[Dict[str, Any]] = []

    for rid, r in by.items():
        top5 = [name for name in MULTI_AXIS if rank.get(name, {}).get(rid, 999) <= 5]
        top8 = [name for name in MULTI_AXIS if rank.get(name, {}).get(rid, 999) <= 8]
        extreme = [name for name in EXTREME_AXES if rank.get(name, {}).get(rid, 999) <= 2]

        if rid not in active_w:
            reasons = []
            if rank.get("ZAI_WIN", {}).get(rid, 999) <= 5:
                reasons.append("ZAI_WIN_TOP5")
            if rid in active_p2 or rid in active_p3:
                reasons.append("ADJACENT_ROLE_ACTIVE")
            if len(top5) >= 3:
                reasons.append("MULTI_AXIS_TOP5")
            if len(extreme) >= 1:
                reasons.append("DIMENSION_EXTREMUM")
            if len(reasons) >= 2:
                score = (
                    130
                    - 7 * rank.get("ZAI_WIN", {}).get(rid, 20)
                    + 4 * len(top5)
                    + 6 * len(extreme)
                    + (8 if rid in active_p2 or rid in active_p3 else 0)
                )
                proposals.append({
                    "runner_id": rid, "column": "W", "score": score,
                    "reasons": reasons, "rank": rank.get("ZAI_WIN", {}).get(rid),
                    "top5_axes": top5, "extreme_axes": extreme,
                })

        if rid not in active_p2:
            reasons = []
            if rank.get("ZAI_PLACE", {}).get(rid, 999) <= 8:
                reasons.append("ZAI_PLACE_TOP8")
            if rid in active_p3:
                reasons.append("P3_ACTIVE")
            if len(top8) >= 4:
                reasons.append("MULTI_AXIS_TOP8")
            if len(extreme) >= 1:
                reasons.append("DIMENSION_EXTREMUM")
            if len(reasons) >= 2:
                score = (
                    115
                    - 5 * rank.get("ZAI_PLACE", {}).get(rid, 20)
                    + 3 * len(top8)
                    + 5 * len(extreme)
                    + (7 if rid in active_p3 else 0)
                )
                proposals.append({
                    "runner_id": rid, "column": "P2", "score": score,
                    "reasons": reasons, "rank": rank.get("ZAI_PLACE", {}).get(rid),
                    "top8_axes": top8, "extreme_axes": extreme,
                })

        if rid not in active_p3:
            reasons = []
            if rank.get("T3I", {}).get(rid, 999) <= 10:
                reasons.append("T3I_TOP10")
            if len(top8) >= 4:
                reasons.append("MULTI_AXIS_TOP8")
            if len(extreme) >= 1:
                reasons.append("DIMENSION_EXTREMUM")
            if len(reasons) >= 2:
                score = (
                    100
                    - 4 * rank.get("T3I", {}).get(rid, 20)
                    + 3 * len(top8)
                    + 6 * len(extreme)
                )
                proposals.append({
                    "runner_id": rid, "column": "P3", "score": score,
                    "reasons": reasons, "rank": rank.get("T3I", {}).get(rid),
                    "top8_axes": top8, "extreme_axes": extreme,
                })

    proposals.sort(
        key=lambda x: (-float(x["score"]), ROLE_ORDER[x["column"]],
                       int(x["runner_id"]) if x["runner_id"].isdigit() else x["runner_id"])
    )
    return proposals


def _set_role(req: Dict[str, Any], rid: str, column: str, proposal: Dict[str, Any]) -> None:
    found = False
    for row in req.get("role_registry") or []:
        if str(row.get("runner_id")) == rid and str(row.get("column")) == column:
            if str(row.get("status")) in ACTIVE:
                return
            row["base_status"] = row.get("status")
            row["base_reason"] = row.get("reason")
            row["status"] = "CONDITIONAL"
            row["reason"] = "RISK_BUDGET_REAUDIT:" + "+".join(proposal["reasons"])
            row["semantic_overlay_authority"] = PROFILE
            row["production_authority"] = False
            found = True
            break
    if not found:
        req.setdefault("role_registry", []).append({
            "runner_id": rid,
            "column": column,
            "status": "CONDITIONAL",
            "reason": "RISK_BUDGET_REAUDIT:" + "+".join(proposal["reasons"]),
            "authority": BASE_SEMANTIC_PROFILE,
            "semantic_overlay_authority": PROFILE,
            "production_authority": False,
        })

    sp = req.setdefault("static_prediction", {})
    roles = sp.setdefault("roles", {})
    current = list(roles.get(rid) or [])
    if column not in current:
        current.append(column)
    roles[rid] = sorted(set(current), key=lambda x: ROLE_ORDER.get(x, 99))
    sp["risk_budget_semantic_overlay"] = PROFILE


def _ensure_pair(req: Dict[str, Any], head: str, second: str, source_role: str) -> None:
    for row in req.get("pair_dispositions") or []:
        if str(row.get("head")) == head and str(row.get("second")) == second:
            return
    req.setdefault("pair_dispositions", []).append({
        "head": head,
        "second": second,
        "status": "PROTECT",
        "reason": "RISK_BUDGET_ROLE_BRIDGE_PROTECTION:" + source_role,
        "authority": PROFILE,
        "production_authority": False,
    })


def _apply_proposal(req: Dict[str, Any], proposal: Dict[str, Any]) -> None:
    rid, column = str(proposal["runner_id"]), str(proposal["column"])
    _set_role(req, rid, column, proposal)

    runners = req.get("runners") or []
    zwin = _rank_map(runners, "ZAI_WIN")
    zplace = _rank_map(runners, "ZAI_PLACE")
    active_w = sorted(_active(req, "W"), key=lambda x: (zwin.get(x, 999), int(x) if x.isdigit() else x))
    active_p2 = sorted(_active(req, "P2"), key=lambda x: (zplace.get(x, 999), int(x) if x.isdigit() else x))

    if column == "W":
        seconds = [x for x in active_p2 if x != rid][:2]
        for second in seconds:
            _ensure_pair(req, rid, second, "W")
        ph = [str(x) for x in (req.get("purchased_heads") or [])]
        if rid not in ph:
            ph.append(rid)
        req["purchased_heads"] = ph
    elif column == "P2":
        heads = [x for x in active_w if x != rid][:2]
        for head in heads:
            _ensure_pair(req, head, rid, "P2")
    # Global P3 expansion needs no invented pair-local exact orientation.
    # MEC-R3's pre-compression tail floor will preserve it under material pairs.


def expand_candidate_semantics_with_risk_budget(
    request: Dict[str, Any],
    *,
    budget_limit: int | None = None,
    min_stake: int = 100,
) -> Dict[str, Any]:
    """Expand only evidence-supported Candidate alternatives before KRS freeze.

    This is a Candidate/Common behavior change, not a Production change.
    The 10k policy is a ceiling, never a spending target: proposals are accepted
    only when they have independent pre-result signals and add semantic coverage.
    """
    try:
        from minimum_efficient_coverage import build_mec_plan, validate_mec_plan
    except ImportError:
        from .minimum_efficient_coverage import build_mec_plan, validate_mec_plan

    req = copy.deepcopy(request)
    base_profile = str((req.get("candidate_semantic_freeze") or {}).get("profile") or "")
    if base_profile and base_profile != BASE_SEMANTIC_PROFILE:
        raise RiskBudgetExpansionError("BASE_CANDIDATE_SEMANTIC_PROFILE_MISMATCH:" + base_profile)

    resolved_budget, budget_source = _budget_limit(req)
    cap = int(budget_limit if budget_limit is not None else resolved_budget)
    if cap <= 0 or cap % 100:
        raise RiskBudgetExpansionError("RISK_BUDGET_MUST_BE_POSITIVE_100_YEN_INCREMENT")

    base_mec = build_mec_plan(req, None, strict_head_closure=True, min_stake=min_stake)
    validate_mec_plan(base_mec)
    current_capital = int(base_mec["minimum_required_capital"])
    baseline_units = int(base_mec["coverage_unit_count"])

    proposals = _proposal_candidates(req)
    accepted = []
    rejected = []

    if current_capital < cap:
        for proposal in proposals:
            trial = copy.deepcopy(req)
            _apply_proposal(trial, proposal)
            try:
                trial_mec = build_mec_plan(trial, None, strict_head_closure=True, min_stake=min_stake)
                validate_mec_plan(trial_mec)
            except Exception as exc:
                rejected.append({**proposal, "decision": "REJECT", "reason": "MEC_INVALID:" + str(exc)})
                continue
            trial_capital = int(trial_mec["minimum_required_capital"])
            trial_units = int(trial_mec["coverage_unit_count"])
            marginal_units = trial_units - baseline_units
            marginal_capital = trial_capital - current_capital

            if trial_capital > cap:
                rejected.append({
                    **proposal, "decision": "REJECT", "reason": "RISK_BUDGET_LIMIT",
                    "trial_required_capital": trial_capital,
                })
                continue
            if marginal_units <= 0 or marginal_capital <= 0:
                rejected.append({
                    **proposal, "decision": "REJECT", "reason": "NO_NEW_MATERIAL_SEMANTIC_COVERAGE",
                    "trial_required_capital": trial_capital,
                })
                continue

            req = trial
            current_capital = trial_capital
            baseline_units = trial_units
            accepted.append({
                **proposal,
                "decision": "ACCEPT",
                "required_capital_after": current_capital,
                "marginal_capital": marginal_capital,
                "marginal_coverage_units": marginal_units,
            })
            if current_capital >= cap:
                break

    final_mec = build_mec_plan(req, None, strict_head_closure=True, min_stake=min_stake)
    validate_mec_plan(final_mec)

    manifest = {
        "profile": PROFILE,
        "status": "ACTIVE-CANDIDATE / NON-PRODUCTION / PRE-KRS / FORWARD-OOS-COHORT",
        "race_id": req.get("race_id"),
        "base_semantic_profile": base_profile or BASE_SEMANTIC_PROFILE,
        "budget_limit": cap,
        "budget_source": budget_source,
        "budget_semantics": "RISK_BUDGET_CEILING_NOT_SPENDING_TARGET",
        "budget_fill_forbidden": True,
        "base_required_capital": int(base_mec["minimum_required_capital"]),
        "expanded_required_capital": int(final_mec["minimum_required_capital"]),
        "unused_budget": max(0, cap - int(final_mec["minimum_required_capital"])),
        "base_ticket_count": int(base_mec["ticket_count"]),
        "expanded_ticket_count": int(final_mec["ticket_count"]),
        "accepted_proposals": accepted,
        "rejected_proposals": rejected,
        "proposal_count": len(proposals),
        "accepted_count": len(accepted),
        "stop_rule": "NO_MORE_PRE_RESULT_SIGNAL_SUPPORTED_PROPOSALS_OR_NEXT_PROPOSAL_EXCEEDS_RISK_BUDGET",
        "production_effect": "NONE",
        "production_numerical_change": False,
        "production_semantic_change": False,
        "candidate_behavior_change": True,
        "krs_capital_authority": False,
        "mec_r3_profile_unchanged": True,
        "automatic_production_promotion": False,
    }
    manifest["sha256"] = _sha(manifest)
    req["candidate_risk_budget_expansion"] = manifest
    req["candidate_policy_cohort"] = "JRA-CANDIDATE-v0.2+RISK-BUDGET-v0.1"

    freeze = req.setdefault("candidate_semantic_freeze", {})
    freeze["risk_budget_expansion_profile"] = PROFILE
    freeze["risk_budget_expansion_sha256"] = manifest["sha256"]
    freeze["risk_budget_limit_yen"] = cap
    freeze["risk_budget_required_capital_preview_yen"] = int(final_mec["minimum_required_capital"])
    freeze["risk_budget_unused_yen"] = manifest["unused_budget"]
    freeze["risk_budget_accepted_count"] = len(accepted)
    freeze["policy_cohort"] = req["candidate_policy_cohort"]
    freeze["sha256"] = _sha({k: v for k, v in freeze.items() if k != "sha256"})

    fpp = req.setdefault("final_prediction_package", {})
    fpp["role_registry"] = copy.deepcopy(req.get("role_registry") or [])
    fpp["pair_dispositions"] = copy.deepcopy(req.get("pair_dispositions") or [])
    fpp["third_dispositions"] = copy.deepcopy(req.get("third_dispositions") or [])
    fpp["static_prediction"] = copy.deepcopy(req.get("static_prediction") or {})
    fpp["candidate_semantic_freeze_sha256"] = freeze["sha256"]
    fpp["risk_budget_expansion_profile"] = PROFILE
    fpp["risk_budget_expansion_sha256"] = manifest["sha256"]
    fpp["notice"] = (
        "Candidate-only pre-KRS semantic expansion. 10,000 yen is a ceiling, not a fill target. "
        "Production Static/Role/Pair/Third and MEC-R3 authority are unchanged."
    )
    return req
