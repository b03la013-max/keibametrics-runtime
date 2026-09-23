from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

PROFILE="KM-LOCAL-NUMERICAL-CANDIDATE-AUTHORITY-v0.1-20260923"
EVIDENCE="mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json"
MAPPING="mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json"


def _load(path):
    with open(path,encoding="utf-8") as f:
        return json.load(f)


def assess(evidence_path: str|Path=EVIDENCE, mapping_path: str|Path=MAPPING) -> Dict[str,Any]:
    e=_load(evidence_path); m=_load(mapping_path)
    sets=e.get("common_component_sets") or {}
    rules=e.get("component_score_rules") or {}
    missing=[]; invalid=[]
    count=0; bound=0
    for idx,comps in sets.items():
        for comp in comps:
            count+=1
            r=(rules.get(idx) or {}).get(comp)
            if not isinstance(r,dict):
                missing.append(f"{idx}.{comp}"); continue
            if not r.get("rule_id") or not r.get("transform"):
                invalid.append(f"{idx}.{comp}"); continue
            if r.get("result_derived_allowed") is not False:
                invalid.append(f"RESULT_DERIVED_NOT_EXPLICITLY_FORBIDDEN:{idx}.{comp}"); continue
            bound+=1
    required=list(m.get("required_indices") or [])
    implementation_ready=(
        "CANDIDATE" in str(e.get("status",""))
        and "CANDIDATE" in str(m.get("status",""))
        and count>0 and bound==count and not missing and not invalid
        and len(required)==29 and len(set(required))==29
    )
    return {
      "profile":PROFILE,
      "status":"IMPLEMENTATION_READY_NON_PRODUCTION" if implementation_ready else "NOT_READY",
      "implementation_ready":implementation_ready,
      "production_ready":False,
      "automatic_production_promotion":False,
      "component_rule_count":count,
      "bound_component_rule_count":bound,
      "missing_component_rules":missing,
      "invalid_component_rules":invalid,
      "required_index_count":len(required),
      "evidence_registry_id":e.get("registry_id"),
      "mapping_id":m.get("mapping_id"),
      "calibration_status":"OOS_NOT_ESTABLISHED",
      "production_blockers":[
        "candidate transformations are uncalibrated",
        "candidate-only equal-factor aggregations require time-ordered OOS validation",
        "role-width policy requires OOS calibration",
        "human promotion review required"
      ],
      "policy":"Implementation readiness is not Production authority. Production gate remains unchanged until explicit promotion.",
    }


if __name__=="__main__":
    print(json.dumps(assess(),ensure_ascii=False,indent=2,sort_keys=True))
