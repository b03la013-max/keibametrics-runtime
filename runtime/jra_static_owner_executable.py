"""Deterministic JRA Static Owner implementation pending independent promotion.

This converts a verified Production-formula Full20 ledger into a frozen,
source-bound rank/role/pair/third *candidate*. It is NOT authorized to issue
Production tickets until Current Authority explicitly admits the policy,
with forward OOS evidence. It never imports Candidate numerical material.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import hashlib
import json
import math

from jra_index_provenance_builder import BASE, DERIVED, FORMULA_REGISTRY

PROFILE = "JRA-STATIC-PREDICTION-OWNER-EXECUTABLE-CANDIDATE-20261010"
MAPPING = "JRA-EVIDENCE-TO-BASE-MAPPING-v1.0-PRODUCTION-20260921"
REQUIRED = set(BASE) | set(DERIVED)
COLUMNS = ("W", "P2", "P3")


class JRAStaticOwnerError(ValueError):
    pass


def _sha(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _time(v):
    try:
        d = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        return d if d.tzinfo else None
    except (TypeError, ValueError):
        return None


def _measure(row, name):
    v = row["canonical_components"][name]["value"]
    return float(v)


def _rank(runners, metric):
    return sorted((str(x["runner_id"]) for x in runners),
                  key=lambda rid: (-next(_measure(row, metric) for row in runners if str(row["runner_id"]) == rid),
                                   int(rid) if rid.isdigit() else rid))


def _cluster(runners, metric, *, exclude=frozenset()):
    order = [rid for rid in _rank(runners, metric) if rid not in exclude]
    if not order:
        return []
    val = {str(r["runner_id"]): _measure(r, metric) for r in runners}
    # An explicit score-gap distinction, never fixed by the bet budget.
    best = val[order[0]]
    return [rid for rid in order if best - val[rid] <= 7.0]


def compile_static_owner(request, *, source_snapshot_sha256, source_receipt_sha256,
                         frozen_at, prediction_cutoff):
    if request.get("family_id") != "JRA":
        raise JRAStaticOwnerError("JRA_ONLY")
    if not source_snapshot_sha256 or not source_receipt_sha256:
        raise JRAStaticOwnerError("SIGNED_SOURCE_BASIS_REQUIRED")
    freeze, cutoff = _time(frozen_at), _time(prediction_cutoff)
    if freeze is None or cutoff is None or freeze > cutoff:
        raise JRAStaticOwnerError("STATIC_FREEZE_AFTER_PREDICTION_CUTOFF")
    runners = request.get("runners")
    if not isinstance(runners, list) or len(runners) < 2:
        raise JRAStaticOwnerError("FULL_RUNNER_UNIVERSE_REQUIRED")
    ids = [str(x.get("runner_id") or "") for x in runners]
    if not all(ids) or len(ids) != len(set(ids)):
        raise JRAStaticOwnerError("RUNNER_UNIVERSE_INVALID")
    mapping = request.get("base_index_mapping_authority") or {}
    if mapping.get("production_authority") is not True or mapping.get("mapping_id") != MAPPING:
        raise JRAStaticOwnerError("PRODUCTION_NUMERICAL_AUTHORITY_REQUIRED")
    for row in runners:
        rid = str(row["runner_id"])
        cc = row.get("canonical_components") or {}
        if set(cc) != REQUIRED:
            raise JRAStaticOwnerError("FULL20_NOT_AVAILABLE:" + rid)
        for index, spec in cc.items():
            v = spec.get("value")
            if isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v) or not 0 <= v <= 100:
                raise JRAStaticOwnerError(f"INDEX_INVALID:{rid}:{index}")
            if spec.get("candidate_only") is True or spec.get("production_authority") is False:
                raise JRAStaticOwnerError(f"CANDIDATE_NUMERICAL_FORBIDDEN:{rid}:{index}")
            rule_mapping = MAPPING if index in BASE else FORMULA_REGISTRY
            if spec.get("mapping_version") != rule_mapping or not spec.get("rule_id") or not spec.get("evidence_refs") or not spec.get("source_fact"):
                raise JRAStaticOwnerError(f"INDEX_PROVENANCE_INVALID:{rid}:{index}")
    rank_w = _rank(runners, "ZAI_WIN")
    rank_p2 = _rank(runners, "ZAI_PLACE")
    rank_p3 = _rank(runners, "T3I")
    # Preserve structural order feasibility without using race bankroll to
    # choose widths. At least two distinct P2 and three P3 candidates are
    # needed for a complete 3-place semantic universe.
    p2_order = _rank(runners, "ZAI_PLACE")
    p3_order = _rank(runners, "T3I")
    active = {
        "W": _cluster(runners, "ZAI_WIN"),
        "P2": list(dict.fromkeys(_cluster(runners, "ZAI_PLACE") + p2_order[:min(2, len(runners))])),
        "P3": list(dict.fromkeys(_cluster(runners, "T3I") + p3_order[:min(3, len(runners))])),
    }
    # Do not let two-runner exact sequences artificially include the same horse.
    role_registry = [
        {"runner_id": rid, "column": col,
         "status": "CORE" if rid == active[col][0] else "PROTECTED" if rid in active[col] else "EXCLUDED",
         "reason": "FROZEN_INDEX_SCORE_CLUSTER",
         "authority": PROFILE, "production_authority": False}
        for rid in ids for col in COLUMNS
    ]
    pairs = []
    thirds = []
    for h in active["W"]:
        second_candidates = _cluster(runners, "ZAI_PLACE", exclude={h})
        for s in [rid for rid in active["P2"] if rid != h]:
            purchased = s in second_candidates
            pairs.append({"head": h, "second": s,
                          "status": "PURCHASE" if purchased else "PROTECT",
                          "reason": "FROZEN_PAIR_SCORE_CLUSTER",
                          "authority": PROFILE, "production_authority": False})
            if not purchased:
                continue
            third_candidates = _cluster(runners, "T3I", exclude={h, s})
            for t in [rid for rid in active["P3"] if rid not in {h, s}]:
                thirds.append({"head": h, "second": s, "third": t,
                               "status": "PURCHASE" if t in third_candidates else "PROTECT",
                               "reason": "FROZEN_PAIR_LOCAL_THIRD_SCORE_CLUSTER",
                               "authority": PROFILE, "production_authority": False})
    sp = {
        "ranking": rank_w,
        "roles": {rid: [col for col in COLUMNS if rid in active[col]] for rid in rank_w},
        "status": "FROZEN-PRE-KRS / CANDIDATE",
        "authority": PROFILE,
        "production_authority": False,
    }
    result = {
        "profile": PROFILE,
        "race_id": request.get("race_id"),
        "source_snapshot_sha256": source_snapshot_sha256,
        "source_receipt_sha256": source_receipt_sha256,
        "frozen_at": frozen_at,
        "static_prediction": sp,
        "role_registry": role_registry,
        "pair_dispositions": pairs,
        "third_dispositions": thirds,
        "purchased_heads": active["W"],
        "active_columns": active,
        "full_index_count": len(runners) * 20,
        "candidate_policy": True,
        "production_authority": False,
        "purchase_authority": False,
        "promotion_gate": "FROZEN_UNKNOWN_FUTURE_OOS_PLUS_CURRENT_AUTHORITY",
    }
    result["sha256"] = _sha(result)
    return result
