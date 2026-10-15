from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, Mapping

PROFILE_ID = "KM-FAMILY-OWNER-UTILITY-PFS-CONTINUOUS-IMPROVEMENT-20261007-R1"

PFS_LOSS_OWNERS = {
    "SOURCE_EVIDENCE",
    "NUMERICAL",
    "PREDICTION_ROLE",
    "PAIR_EXACT_CONNECTION",
    "KRS",
    "SEMANTIC_MEC",
    "TICKET",
    "CAPITAL",
    "EXECUTION_RESULT",
    "NONE_REALIZED_PFS_POSITIVE",
    "UNKNOWN",
}

FIRST_FAILURE_OWNER_MAP = {
    "SOURCE_ACQUISITION": "SOURCE_EVIDENCE",
    "SOURCE_TRUST_RECEIPT": "SOURCE_EVIDENCE",
    "SOURCE_TO_FEATURE": "SOURCE_EVIDENCE",
    "EVIDENCE_EVALUATOR": "SOURCE_EVIDENCE",
    "EVIDENCE": "SOURCE_EVIDENCE",
    "NUMERICAL_MAPPING": "NUMERICAL",
    "NUMERICAL_DISCRIMINATION": "NUMERICAL",
    "NUMERICAL": "NUMERICAL",
    "STATIC_PREDICTION": "PREDICTION_ROLE",
    "PREDICTION_ROLE_W": "PREDICTION_ROLE",
    "PREDICTION_ROLE_P2": "PREDICTION_ROLE",
    "PREDICTION_ROLE_P3": "PREDICTION_ROLE",
    "W_P2_P3": "PREDICTION_ROLE",
    "ORDERED_PAIR": "PAIR_EXACT_CONNECTION",
    "ORDERED_PAIR_CONVERSION": "PAIR_EXACT_CONNECTION",
    "PAIR_CONDITIONED_THIRD": "PAIR_EXACT_CONNECTION",
    "EXACT_ORIENTATION": "PAIR_EXACT_CONNECTION",
    "KRS": "KRS",
    "SEMANTIC_COMPRESSION": "SEMANTIC_MEC",
    "SEMANTIC": "SEMANTIC_MEC",
    "MEC": "SEMANTIC_MEC",
    "TICKET_CONVERSION": "TICKET",
    "TICKET": "TICKET",
    "CAPITAL": "CAPITAL",
    "CAPITAL_EFFICIENCY": "CAPITAL",
    "EXECUTION": "EXECUTION_RESULT",
    "RESULT_LEARNING": "EXECUTION_RESULT",
    "RESULT": "EXECUTION_RESULT",
    "SETTLEMENT": "EXECUTION_RESULT",
    "NONE": "NONE_REALIZED_PFS_POSITIVE",
}

FORBIDDEN_AUTOMATIONS = [
    "RETROACTIVE_PREDICTION_REWRITE",
    "AUTOMATIC_NUMERICAL_WEIGHT_CHANGE",
    "AUTOMATIC_KRS_AUTHORITY_PROMOTION",
    "AUTOMATIC_MEC_R3_CHANGE",
    "AUTOMATIC_CAPITAL_POLICY_CHANGE",
    "AUTOMATIC_VENUE_CANON_CHANGE",
    "RESULT_FIT_SHADOW_ARM_RESELECTION",
]


def _sha(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _unique(values: Iterable[str]) -> list[str]:
    out: list[str] = []
    seen = set()
    for raw in values:
        value = str(raw)
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return out


def _float_or_none(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_layer_loss_evidence(layer_loss_evidence: Mapping[str, Any] | None) -> Dict[str, float]:
    if not isinstance(layer_loss_evidence, Mapping):
        return {}
    out: Dict[str, float] = {}
    for owner, value in layer_loss_evidence.items():
        owner = str(owner).upper()
        if owner not in PFS_LOSS_OWNERS or owner in {"NONE_REALIZED_PFS_POSITIVE", "UNKNOWN"}:
            continue
        val = _float_or_none(value)
        if val is not None and val >= 0:
            out[owner] = val
    return out


def _first_failure(review: Mapping[str, Any]) -> str:
    failure = review.get("failure_localization") or {}
    return str(
        failure.get("first_material_failure")
        or failure.get("primary_failure")
        or "UNRESOLVED"
    ).upper()


def _pfs(review: Mapping[str, Any]) -> float | None:
    capital = review.get("capital") or {}
    return _float_or_none(capital.get("pfs"))


def _hit_but_loss(review: Mapping[str, Any]) -> bool:
    capital = review.get("capital") or {}
    if capital.get("hit_but_loss") is not None:
        return bool(capital.get("hit_but_loss"))
    pfs = _pfs(review)
    hit = bool(capital.get("hit"))
    return bool(hit and pfs is not None and pfs < 100.0)


def classify_dominant_pfs_loss_owner(
    review: Mapping[str, Any],
    *,
    layer_loss_evidence: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Conservative PFS-loss localization.

    Explicit loss evidence wins. Without it, the function only makes narrow
    inferences from settled PFS, hit-but-loss and the already-frozen first
    material failure. It returns UNKNOWN rather than inventing a causal owner.
    """

    pfs = _pfs(review)
    first = _first_failure(review)
    explicit = _normalize_layer_loss_evidence(layer_loss_evidence)

    if explicit:
        owner, loss = max(explicit.items(), key=lambda item: item[1])
        return {
            "owner": owner,
            "basis": "EXPLICIT_LAYER_LOSS_EVIDENCE",
            "loss_value": loss,
            "confidence": "HIGH",
            "evidence": explicit,
        }

    if pfs is not None and pfs >= 100.0:
        return {
            "owner": "NONE_REALIZED_PFS_POSITIVE",
            "basis": "SETTLED_PFS_GE_100",
            "loss_value": None,
            "confidence": "HIGH",
            "evidence": {},
        }

    if _hit_but_loss(review):
        return {
            "owner": "CAPITAL",
            "basis": "HIT_BUT_LOSS",
            "loss_value": None,
            "confidence": "MEDIUM",
            "evidence": {},
        }

    mapped = FIRST_FAILURE_OWNER_MAP.get(first)
    if mapped and mapped != "NONE_REALIZED_PFS_POSITIVE":
        return {
            "owner": mapped,
            "basis": "FIRST_MATERIAL_FAILURE_FALLBACK",
            "loss_value": None,
            "confidence": "MEDIUM",
            "evidence": {},
        }

    return {
        "owner": "UNKNOWN",
        "basis": "INSUFFICIENT_CAUSAL_EVIDENCE",
        "loss_value": None,
        "confidence": "LOW",
        "evidence": {},
    }


def build_pfs_improvement_assessment(
    review: Mapping[str, Any],
    *,
    layer_loss_evidence: Mapping[str, Any] | None = None,
    correctness_bug: bool = False,
    candidate_forward_evidence: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    if not isinstance(review, Mapping):
        raise ValueError("REVIEW_NOT_OBJECT")

    race_id = str(review.get("race_id") or "")
    first = _first_failure(review)
    pfs = _pfs(review)
    hit_but_loss = _hit_but_loss(review)
    dominant = classify_dominant_pfs_loss_owner(
        review, layer_loss_evidence=layer_loss_evidence
    )

    if pfs is None:
        pfs_status = "UNKNOWN"
    elif pfs >= 100.0:
        pfs_status = "PROFITABLE"
    else:
        pfs_status = "LOSS"

    routes: list[str] = []
    test_tracks: list[str] = []
    keep: list[str] = []
    reject: list[str] = []

    if correctness_bug:
        routes.append("REPAIR_NOW")

    if first == "NONE" and pfs_status == "PROFITABLE":
        routes.append("KEEP")
        keep.append("CURRENT_PRODUCTION_BEHAVIOR_FOR_THIS_RACE")

    if first.startswith("PREDICTION_ROLE_"):
        routes.append("TEST_NEXT")
        test_tracks.append("WINNER_ROLE_MIGRATION")
    elif first == "ORDERED_PAIR_CONVERSION":
        routes.append("TEST_NEXT")
        test_tracks.append("PAIR_RESIDUAL")
    elif first in {"PAIR_CONDITIONED_THIRD", "EXACT_ORIENTATION"}:
        routes.append("TEST_NEXT")
        test_tracks.append("PAIR_LOCAL_SELECTIVE_EXACT")
    elif first == "KRS":
        routes.append("TEST_NEXT")
        test_tracks.append("KRS_INCREMENTAL_UTILITY")
    elif first in {"MEC", "SEMANTIC_COMPRESSION", "TICKET", "TICKET_CONVERSION"}:
        routes.append("TEST_NEXT")
        test_tracks.append("SEMANTIC_TO_TICKET_CONVERSION")

    if hit_but_loss or dominant["owner"] == "CAPITAL":
        routes.append("TEST_NEXT")
        test_tracks.append("RACE_CONDITIONAL_CAPITAL_LAYER_SELECTION")

    if pfs_status == "LOSS" and not test_tracks and not correctness_bug:
        routes.append("TEST_NEXT")
        test_tracks.append("PFS_LOSS_OWNER_REVIEW")

    candidate = dict(candidate_forward_evidence or {})
    forward_ready = bool(candidate.get("genuine_unknown_oos_ready"))
    human_review = bool(candidate.get("human_review_ready"))
    robustness_ready = bool(candidate.get("robustness_ready"))
    if forward_ready and human_review and robustness_ready:
        routes.append("PROMOTION_REVIEW")

    # Production remains frozen until explicit authority update.
    routes.append("DO_NOT_CHANGE")
    reject.extend(
        [
            "RESULT_FIT",
            "SINGLE_RACE_AUTOMATIC_POLICY_CHANGE",
            "SINGLE_DAY_AUTOMATIC_POLICY_CHANGE",
            "AUTOMATIC_CANDIDATE_PROMOTION",
        ]
    )

    routes = _unique(routes)
    test_tracks = _unique(test_tracks)
    keep = _unique(keep)
    reject = _unique(reject)

    no_stagnation = bool(
        set(routes)
        & {"REPAIR_NOW", "TEST_NEXT", "SIMPLIFY_OR_REJECT", "PROMOTION_REVIEW"}
    ) or (pfs_status == "PROFITABLE" and "KEEP" in routes)

    out = {
        "profile": PROFILE_ID,
        "race_id": race_id,
        "owner_utility": {
            "primary_metric": "LONG_RUN_PFS",
            "supporting_metrics": [
                "CAPITAL_SUSTAINABILITY",
                "DRAWDOWN",
                "CAPITAL_EFFICIENCY",
                "PREDICTION_UTILITY",
                "SEMANTIC_PRESERVATION",
                "UNKNOWN_FUTURE_OOS_GENERALIZATION",
            ],
            "unconstrained_pfs_maximization": False,
        },
        "first_material_failure": first,
        "dominant_pfs_loss_owner": dominant,
        "pfs": pfs,
        "pfs_status": pfs_status,
        "hit_but_loss": hit_but_loss,
        "learning_routes": routes,
        "test_next_tracks": test_tracks,
        "keep": keep,
        "reject": reject,
        "no_stagnation_satisfied": no_stagnation,
        "principles": [
            "SEMANTIC_UNIVERSE != PURCHASED_UNIVERSE",
            "UNKNOWN != WEAK",
            "UNKNOWN != MUST_PURCHASE",
            "EVERY_RACE_LEARNS != EVERY_RACE_ADDS_A_RULE",
            "EVERY_RACE_LEARNS != EVERY_RACE_CHANGES_NOTHING",
        ],
        "candidate_forward_evidence": {
            "genuine_unknown_oos_ready": forward_ready,
            "human_review_ready": human_review,
            "robustness_ready": robustness_ready,
        },
        "production_change_authorized": False,
        "automatic_promotion": False,
        "forbidden": FORBIDDEN_AUTOMATIONS,
    }
    out["sha256"] = _sha(out)
    return out


def apply_to_review(
    review: Mapping[str, Any],
    *,
    layer_loss_evidence: Mapping[str, Any] | None = None,
    correctness_bug: bool = False,
    candidate_forward_evidence: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    out = dict(review)
    out["pfs_improvement"] = build_pfs_improvement_assessment(
        review,
        layer_loss_evidence=layer_loss_evidence,
        correctness_bug=correctness_bug,
        candidate_forward_evidence=candidate_forward_evidence,
    )
    return out
