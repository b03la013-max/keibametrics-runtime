from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable

from local_nar_evidence_candidate import compile_candidate_evidence
from local_fullnumerical_candidate import materialize_candidate, REQUIRED

PROFILE = "KM-LOCAL-PRODUCTION-NUMERICAL-MATERIALIZER-v1.0-20261008"
PRODUCTION_EVIDENCE_REGISTRY = "mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json"
PRODUCTION_MAPPING = "mapping/local_full_numerical_mapping_v1.0_production_20261008.json"

# The proven deterministic implementation is reused as code, but all runtime
# authority/provenance is rebound to the explicit Production registries above.
IMPLEMENTATION_EVIDENCE_REGISTRY = "mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json"
IMPLEMENTATION_MAPPING = "mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json"

PROD_REGISTRY_ID = "LOCAL-EVIDENCE-FEATURE-RULE-REGISTRY-v1.1-PRODUCTION-NUMERICAL-20261008"
PROD_MAPPING_ID = "LOCAL-FULL-NUMERICAL-MAPPING-v1.0-PRODUCTION-20261008"


class LocalProductionNumericalError(ValueError):
    pass


def _load(path: str | Path) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _sha(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _rule_core(rule: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "transform": rule.get("transform"),
        "formula": rule.get("formula"),
        "lookup_table": rule.get("lookup_table"),
        "range": rule.get("range"),
        "missing_rule": rule.get("missing_rule"),
        "result_derived_allowed": rule.get("result_derived_allowed"),
    }


def _assert_registry_equivalence() -> Dict[str, Any]:
    impl = _load(IMPLEMENTATION_EVIDENCE_REGISTRY)
    prod = _load(PRODUCTION_EVIDENCE_REGISTRY)
    if impl.get("common_component_sets") != prod.get("common_component_sets"):
        raise LocalProductionNumericalError("PRODUCTION_COMPONENT_WEIGHT_DRIFT")

    checked = 0
    for idx, comps in (impl.get("common_component_sets") or {}).items():
        for comp in comps:
            a = ((impl.get("component_score_rules") or {}).get(idx) or {}).get(comp)
            b = ((prod.get("component_score_rules") or {}).get(idx) or {}).get(comp)
            if not isinstance(a, dict) or not isinstance(b, dict):
                raise LocalProductionNumericalError(f"PRODUCTION_RULE_MISSING:{idx}.{comp}")
            if _rule_core(a) != _rule_core(b):
                raise LocalProductionNumericalError(f"PRODUCTION_RULE_TRANSFORM_DRIFT:{idx}.{comp}")
            checked += 1

    impl_map = _load(IMPLEMENTATION_MAPPING)
    prod_map = _load(PRODUCTION_MAPPING)
    if list(impl_map.get("required_indices") or []) != list(prod_map.get("required_indices") or []):
        raise LocalProductionNumericalError("PRODUCTION_REQUIRED_INDEX_DRIFT")
    if set(prod_map.get("required_indices") or []) != set(REQUIRED) or len(prod_map.get("required_indices") or []) != 29:
        raise LocalProductionNumericalError("PRODUCTION_REQUIRED_INDEX_SET_INVALID")
    return {
        "component_rule_count": checked,
        "required_index_count": 29,
        "implementation_registry": impl.get("registry_id"),
        "production_registry": prod.get("registry_id"),
        "implementation_mapping": impl_map.get("mapping_id"),
        "production_mapping": prod_map.get("mapping_id"),
        "transform_equivalent": True,
    }


def _production_rule_id(value: str) -> str:
    return (
        str(value)
        .replace("LOCAL-NUM-CAND-v0.1-", "LOCAL-NUM-PROD-v1.0-")
        .replace("LOCAL-TPI-L-v4.13R1-CANDIDATE-BINDING", "LOCAL-TPI-L-v4.13R1-PRODUCTION-BINDING")
        .replace("LOCAL-F3S-L-v4.13R1-CANDIDATE-BINDING", "LOCAL-F3S-L-v4.13R1-PRODUCTION-BINDING")
    )


def _rewrite(obj: Any) -> Any:
    if isinstance(obj, dict):
        out = {}
        for key, value in obj.items():
            if key == "rule_id" and isinstance(value, str):
                out[key] = _production_rule_id(value)
            elif key == "mapping_version":
                out[key] = PROD_MAPPING_ID
            elif key == "candidate_only":
                out[key] = False
            elif key == "production_authority":
                out[key] = True
            elif key == "calibration_status":
                out[key] = "UNCALIBRATED_RULE_BASED_PRODUCTION_NUMERICAL"
            else:
                out[key] = _rewrite(value)
        return out
    if isinstance(obj, list):
        return [_rewrite(x) for x in obj]
    if isinstance(obj, str):
        return _production_rule_id(obj)
    return obj


def _finite_numeric(value: Any) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
        and 0.0 <= float(value) <= 100.0
    )


def materialize_production(
    source_artifact: Dict[str, Any],
    request: Dict[str, Any],
    required_indices: Iterable[str],
) -> Dict[str, Any]:
    equivalence = _assert_registry_equivalence()
    required = [str(x) for x in required_indices]
    if len(required) != 29 or set(required) != set(REQUIRED):
        raise LocalProductionNumericalError(
            f"FULL_29_INDEX_MANIFEST_REQUIRED:{len(required)}:{sorted(set(REQUIRED)-set(required))}"
        )

    # Compile source-derived evidence using the Production rule IDs.
    compiled = compile_candidate_evidence(
        source_artifact,
        copy.deepcopy(request),
        PRODUCTION_EVIDENCE_REGISTRY,
    )

    # Reuse the already regression-tested deterministic arithmetic engine. Its
    # implementation registries are transform-equivalent to the promoted
    # Production registries; the result is rebound below to Production authority.
    impl = materialize_candidate(
        compiled,
        IMPLEMENTATION_EVIDENCE_REGISTRY,
        IMPLEMENTATION_MAPPING,
    )

    out = copy.deepcopy(impl)
    out["runners"] = _rewrite(out.get("runners") or [])

    rows = []
    counts = {"CALCULATED": 0, "RULED-NEUTRAL": 0, "RULED-HOLD": 0, "NOT-APPLICABLE": 0}
    unresolved = []
    for runner in out["runners"]:
        rid = str(runner.get("runner_id"))
        canonical = runner.get("canonical_components") or {}
        for idx in required:
            spec = canonical.get(idx)
            if not isinstance(spec, dict):
                unresolved.append({"runner_id": rid, "index": idx, "reason": "TERMINAL_MISSING"})
                continue
            status = str(spec.get("terminal_status") or "").upper()
            if status not in counts:
                unresolved.append({"runner_id": rid, "index": idx, "reason": f"STATUS_INVALID:{status}"})
                continue
            if status in {"CALCULATED", "RULED-NEUTRAL"} and not _finite_numeric(spec.get("value")):
                unresolved.append({"runner_id": rid, "index": idx, "reason": "FINITE_VALUE_REQUIRED"})
                continue
            if not spec.get("rule_id") or not spec.get("evidence_refs") or not spec.get("source_fact"):
                unresolved.append({"runner_id": rid, "index": idx, "reason": "PROVENANCE_INCOMPLETE"})
                continue
            counts[status] += 1
            rows.append({
                "runner_id": rid,
                "index": idx,
                "terminal_status": status,
                "value": spec.get("value"),
                "rule_id": spec.get("rule_id"),
            })

        # Preserve the useful coverage audit under Production names.
        runner["numerical_feature_coverage_ratio"] = runner.pop("candidate_feature_coverage_ratio", None)
        runner["numerical_missing_count"] = runner.pop("candidate_missing_count", None)
        runner["numerical_missing_components"] = runner.pop("candidate_missing_components", None)
        runner["numerical_missingness_saturation"] = runner.pop("candidate_missingness_saturation", None)
        runner["numerical_index_sha256"] = _sha(canonical)
        runner["production_numerical_authority"] = True

    required_count = len(out["runners"]) * len(required)
    numeric_value_count = counts["CALCULATED"] + counts["RULED-NEUTRAL"]
    full_terminalization = len(unresolved) == 0 and sum(counts.values()) == required_count
    full_numerical_closure = (
        full_terminalization
        and counts["RULED-HOLD"] == 0
        and counts["NOT-APPLICABLE"] == 0
        and numeric_value_count == required_count
    )

    out["required_indices"] = required
    out["numeric_coverage"] = {
        "required_count": required_count,
        "terminalized_count": sum(counts.values()),
        "calculated_count": counts["CALCULATED"],
        "ruled_neutral_count": counts["RULED-NEUTRAL"],
        "ruled_hold_count": counts["RULED-HOLD"],
        "not_applicable_count": counts["NOT-APPLICABLE"],
        "numeric_value_count": numeric_value_count,
        "unresolved_count": len(unresolved),
        "unresolved": unresolved,
    }
    out["full_terminalization"] = full_terminalization
    out["full_numerical_calculation"] = counts["CALCULATED"] == required_count and full_terminalization
    out["full_numerical_closure"] = full_numerical_closure
    out["strict_full_numerical_ready"] = full_numerical_closure
    out["local_mapping_registry"] = PROD_MAPPING_ID
    out["numerical_evidence_registry"] = PROD_REGISTRY_ID
    out["production_numerical_authority"] = {
        "profile": PROFILE,
        "status": "READY / PRODUCTION-NUMERICAL / FULL-29-INDEX-CLOSURE / UNCALIBRATED-RULE-BASED",
        "evidence_registry_id": PROD_REGISTRY_ID,
        "mapping_id": PROD_MAPPING_ID,
        "strict_numeric_terminal_policy": "CALCULATED_OR_RULED_NEUTRAL",
        "prediction_consumption_authorized": False,
        "krs_consumption_authorized": False,
        "ticket_consumption_authorized": False,
        "capital_consumption_authorized": False,
        "implementation_equivalence": equivalence,
    }
    out["production_numerical_summary"] = {
        "required_indices": required,
        "required_count": required_count,
        "calculated_count": counts["CALCULATED"],
        "ruled_neutral_count": counts["RULED-NEUTRAL"],
        "ruled_hold_count": counts["RULED-HOLD"],
        "numeric_value_count": numeric_value_count,
        "unresolved_count": len(unresolved),
        "full_numerical_closure": full_numerical_closure,
        "mapping_id": PROD_MAPPING_ID,
        "evidence_registry_id": PROD_REGISTRY_ID,
        "calibration_status": "UNCALIBRATED_RULE_BASED_PRODUCTION_NUMERICAL",
        "missing_semantics": "RULED-NEUTRAL is a transport value for UNKNOWN/INCOMPARABLE evidence, not an ability estimate.",
        "prediction_consumption_authorized": False,
        "sha256": None,
    }
    out["production_numerical_summary"]["sha256"] = _sha(out["production_numerical_summary"])
    out["index_terminalization_hash"] = _sha(rows)
    out["index_provenance_hash"] = _sha([r.get("canonical_components") or {} for r in out["runners"]])

    # Remove candidate authority claims. Internal raw evidence labels may remain
    # for audit compatibility, but they cannot confer Candidate/Production scope.
    out.pop("candidate_full_numerical_summary", None)
    out.pop("candidate_role_weight_profile", None)
    out.pop("candidate_role_weight_profile_sha256", None)
    if isinstance(out.get("candidate_evidence_compiler"), dict):
        compiler = _rewrite(out["candidate_evidence_compiler"])
        compiler["profile"] = PROFILE + "-EVIDENCE-COMPILER"
        compiler["registry_id"] = PROD_REGISTRY_ID
        compiler["production_authority"] = True
        compiler["prediction_authority"] = False
        out["production_evidence_compiler"] = compiler
    out.pop("candidate_evidence_compiler", None)
    if isinstance(out.get("candidate_environment"), dict):
        env = _rewrite(out.pop("candidate_environment"))
        env["production_numerical_authority"] = True
        out["numerical_environment"] = env
    if isinstance(out.get("candidate_current_state"), dict):
        out["numerical_current_state"] = _rewrite(out.pop("candidate_current_state"))

    if not full_numerical_closure:
        raise LocalProductionNumericalError(
            "PRODUCTION_NUMERICAL_CLOSURE_FAILED:" + json.dumps(out["numeric_coverage"], ensure_ascii=False)
        )
    return out
