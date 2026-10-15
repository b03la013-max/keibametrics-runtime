from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


PROFILE = "KM-LOCAL-NUMERICAL-AUTHORITY-GATE-v1.0-20260923"


def _load(path: str | Path) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def assess(
    evidence_registry_path: str | Path = "mapping/local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json",
    mapping_registry_path: str | Path = "mapping/local_full_numerical_mapping_v1.0_production_20261008.json",
) -> Dict[str, Any]:
    evidence = _load(evidence_registry_path)
    mapping = _load(mapping_registry_path)

    component_sets = evidence.get("common_component_sets") or {}
    score_rules = evidence.get("component_score_rules") or {}

    missing_rules = []
    invalid_rules = []
    for index_name, components in component_sets.items():
        if not isinstance(components, dict):
            invalid_rules.append(f"COMPONENT_SET_INVALID:{index_name}")
            continue
        per_index = score_rules.get(index_name) if isinstance(score_rules, dict) else None
        for component_name in components:
            rule = per_index.get(component_name) if isinstance(per_index, dict) else None
            key = f"{index_name}.{component_name}"
            if not isinstance(rule, dict):
                missing_rules.append(key)
                continue
            if not str(rule.get("rule_id") or "").strip():
                invalid_rules.append("RULE_ID_MISSING:" + key)
            if not str(rule.get("transform") or rule.get("formula") or rule.get("lookup_table") or "").strip():
                invalid_rules.append("NUMERIC_TRANSFORM_MISSING:" + key)

    evidence_status = str(evidence.get("status") or "")
    mapping_status = str(mapping.get("status") or "")
    explicitly_non_numerical = "NON-NUMERICAL" in evidence_status.upper()
    required_indices = list(mapping.get("required_indices") or [])
    full_29_index_manifest = len(required_indices) == 29 and len(set(required_indices)) == 29
    production_registry = "PRODUCTION-NUMERICAL-AUTHORITY" in evidence_status.upper()
    production_mapping = "PRODUCTION-NUMERICAL-AUTHORITY" in mapping_status.upper()
    strict_terminal_policy = str(mapping.get("strict_numerical_terminal_policy") or "")

    ready = (
        not explicitly_non_numerical
        and not missing_rules
        and not invalid_rules
        and bool(component_sets)
        and full_29_index_manifest
        and production_registry
        and production_mapping
        and strict_terminal_policy == "CALCULATED_OR_RULED_NEUTRAL"
    )

    reasons = []
    if explicitly_non_numerical:
        reasons.append("EVIDENCE_RULE_REGISTRY_EXPLICITLY_NON_NUMERICAL")
    if missing_rules:
        reasons.append("COMPONENT_SCORE_RULES_MISSING")
    if invalid_rules:
        reasons.append("COMPONENT_SCORE_RULES_INVALID")
    if not full_29_index_manifest:
        reasons.append("FULL_29_INDEX_MANIFEST_INVALID")
    if not production_registry:
        reasons.append("EVIDENCE_REGISTRY_NOT_PRODUCTION_NUMERICAL_AUTHORITY")
    if not production_mapping:
        reasons.append("MAPPING_NOT_PRODUCTION_NUMERICAL_AUTHORITY")
    if strict_terminal_policy != "CALCULATED_OR_RULED_NEUTRAL":
        reasons.append("STRICT_NUMERICAL_TERMINAL_POLICY_INVALID")

    return {
        "profile": PROFILE,
        "status": "READY" if ready else "NOT_READY",
        "full_numerical_authority": bool(ready),
        "evidence_registry_id": evidence.get("registry_id"),
        "evidence_registry_status": evidence_status,
        "mapping_registry_id": mapping.get("registry_id"),
        "mapping_registry_status": mapping_status,
        "component_index_count": len(component_sets),
        "required_index_count": len(required_indices),
        "required_indices": required_indices,
        "strict_numeric_terminal_policy": strict_terminal_policy,
        "prediction_consumption_authorized": False,
        "krs_consumption_authorized": False,
        "ticket_consumption_authorized": False,
        "capital_consumption_authorized": False,
        "calibration_status": str(mapping.get("calibration_status") or "UNCALIBRATED_RULE_BASED_PRODUCTION_NUMERICAL"),
        "required_component_rule_count": sum(len(x) for x in component_sets.values() if isinstance(x, dict)),
        "bound_component_rule_count": (
            sum(
                1
                for idx, comps in component_sets.items()
                for comp in (comps if isinstance(comps, dict) else {})
                if isinstance((score_rules.get(idx) or {}).get(comp), dict)
            )
            if isinstance(score_rules, dict)
            else 0
        ),
        "missing_component_rules": missing_rules,
        "invalid_component_rules": invalid_rules,
        "reasons": reasons,
        "policy": (
            "Production numerical materialization is READY only when all 63 deterministic component rules "
            "and the full 29-index manifest are bound. RULED-NEUTRAL is an authorized numeric terminal for "
            "UNKNOWN/incomparable evidence and must remain explicitly distinguishable from CALCULATED. "
            "Numerical readiness alone does not authorize Prediction/KRS/Ticket/Capital behavior changes."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(assess(), ensure_ascii=False, sort_keys=True, indent=2))
