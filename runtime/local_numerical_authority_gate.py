from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


PROFILE = "KM-LOCAL-NUMERICAL-AUTHORITY-GATE-v1.0-20260923"


def _load(path: str | Path) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def assess(
    evidence_registry_path: str | Path = "mapping/local_evidence_feature_rule_registry_v1.0_20260922.json",
    mapping_registry_path: str | Path = "mapping/local_base_index_mapping_registry_v1.0_20260922.json",
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

    ready = (
        not explicitly_non_numerical
        and not missing_rules
        and not invalid_rules
        and bool(component_sets)
    )

    reasons = []
    if explicitly_non_numerical:
        reasons.append("EVIDENCE_RULE_REGISTRY_EXPLICITLY_NON_NUMERICAL")
    if missing_rules:
        reasons.append("COMPONENT_SCORE_RULES_MISSING")
    if invalid_rules:
        reasons.append("COMPONENT_SCORE_RULES_INVALID")

    return {
        "profile": PROFILE,
        "status": "READY" if ready else "NOT_READY",
        "full_numerical_authority": bool(ready),
        "evidence_registry_id": evidence.get("registry_id"),
        "evidence_registry_status": evidence_status,
        "mapping_registry_id": mapping.get("registry_id"),
        "mapping_registry_status": mapping_status,
        "component_index_count": len(component_sets),
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
            "Do not fabricate evidence scores. Formal execution may continue only "
            "as numerical-degraded/terminalized diagnostic until a separately "
            "approved numerical rule registry binds every required component."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(assess(), ensure_ascii=False, sort_keys=True, indent=2))
