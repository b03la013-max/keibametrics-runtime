from __future__ import annotations

import hashlib
import json
from math import isfinite

BASE = ["HPI","SSI","CFI","RFI","BVI","JTI","CSI","TRI","BWI","GCI","PRI","KGI","VMI"]


class CandidateMappingError(ValueError):
    pass


def _sha(obj):
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_mapping(path):
    with open(path, encoding="utf-8") as f:
        mapping = json.load(f)
    if not str(mapping.get("status", "")).startswith("C4-CANDIDATE"):
        raise CandidateMappingError("MAPPING_NOT_C4_CANDIDATE")
    return mapping


def _feature_score(feature_name, features, mapping):
    spec = features.get(feature_name)
    if spec is None:
        return None
    if not isinstance(spec, dict):
        raise CandidateMappingError(f"FEATURE_NOT_OBJECT:{feature_name}")
    category = str(spec.get("category") or "").strip().upper()
    scale = mapping["category_scale"]
    if category not in scale:
        raise CandidateMappingError(f"FEATURE_CATEGORY_INVALID:{feature_name}:{category}")
    evidence_refs = spec.get("evidence_refs")
    source_fact = str(spec.get("source_fact") or "").strip()
    if not isinstance(evidence_refs, list) or not evidence_refs:
        raise CandidateMappingError(f"FEATURE_EVIDENCE_MISSING:{feature_name}")
    if not source_fact:
        raise CandidateMappingError(f"FEATURE_SOURCE_FACT_MISSING:{feature_name}")
    return {
        "score": float(scale[category]),
        "category": category,
        "evidence_refs": [str(x) for x in evidence_refs],
        "source_fact": source_fact,
    }


def _weighted_index(index, features, mapping):
    weights = mapping["indices"][index]
    numerator = 0.0
    covered = 0.0
    components = []
    evidence_refs = []
    source_facts = []

    for feature_name, weight in weights.items():
        scored = _feature_score(feature_name, features, mapping)
        if scored is None:
            continue
        weight = float(weight)
        numerator += scored["score"] * weight
        covered += weight
        components.append({
            "feature": feature_name,
            "weight": weight,
            "category": scored["category"],
            "category_score": scored["score"],
            "weighted_contribution": round(scored["score"] * weight, 6),
            "evidence_refs": scored["evidence_refs"],
            "source_fact": scored["source_fact"],
        })
        evidence_refs.extend(scored["evidence_refs"])
        source_facts.append(f"{feature_name}={scored['category']}:{scored['source_fact']}")

    minimum = float(mapping.get("minimum_coverage_weight", 0.5))
    if covered + 1e-12 < minimum:
        raise CandidateMappingError(
            f"INDEX_EVIDENCE_COVERAGE_LOW:{index}:{covered:.6f}<{minimum:.6f}"
        )

    value = numerator / covered
    return {
        "value": round(value, 6),
        "rule_id": f"JRA-C4-EVIDENCE-{index}-v0.1",
        "mapping_version": mapping["mapping_id"],
        "evidence_refs": sorted(set(evidence_refs)),
        "source_fact": " | ".join(source_facts),
        "adjustments": [],
        "components": components,
        "coverage_weight": round(covered, 6),
    }


def _dcr_component(points, maximum, evidence_refs, source_fact):
    points = float(points)
    maximum = float(maximum)
    if not isfinite(points) or not 0.0 <= points <= maximum:
        raise CandidateMappingError(f"DCR_POINTS_OUT_OF_RANGE:{points}/{maximum}")
    if not evidence_refs:
        raise CandidateMappingError("DCR_EVIDENCE_MISSING")
    return {
        "points": round(points, 6),
        "evidence_refs": sorted(set(str(x) for x in evidence_refs)),
        "source_fact": source_fact,
    }


def _category_to_points(feature_name, maximum, features, mapping):
    scored = _feature_score(feature_name, features, mapping)
    if scored is None:
        return None
    points = float(maximum) * scored["score"] / 100.0
    return _dcr_component(points, maximum, scored["evidence_refs"], scored["source_fact"])


def build_candidate_ledger(race_id, runners, mapping):
    if not race_id:
        raise CandidateMappingError("RACE_ID_MISSING")

    ledger = {
        "mapping_id": mapping["mapping_id"],
        "mapping_status": mapping["status"],
        "formula_registry": "index_formula_registry JRA v1.0",
        "race_id": race_id,
        "runners": {},
    }

    for runner in runners:
        runner_id = str(runner.get("runner_id") or "")
        if not runner_id:
            raise CandidateMappingError("RUNNER_ID_MISSING")
        features = runner.get("evidence_features")
        if not isinstance(features, dict):
            raise CandidateMappingError(f"EVIDENCE_FEATURES_MISSING:{runner_id}")

        base = {index: _weighted_index(index, features, mapping) for index in BASE}

        dcr_components = {}
        for component_name, spec in mapping["dcr"].items():
            maximum = float(spec["max_points"])
            if "feature" in spec:
                component = _category_to_points(
                    spec["feature"], maximum, features, mapping
                )
                if component is None:
                    raise CandidateMappingError(
                        f"DCR_FEATURE_MISSING:{runner_id}:{spec['feature']}"
                    )
                dcr_components[component_name] = component
            else:
                points = float(spec.get("newcomer_default_points", 0.0))
                dcr_components[component_name] = _dcr_component(
                    points,
                    maximum,
                    [f"{race_id}:{runner_id}:NEWCOMER_STATUS"],
                    "newcomer has no realized official prior-race or same-course/distance evidence",
                )

        dcr_score = round(sum(x["points"] for x in dcr_components.values()), 6)

        scenario_value = 0.0
        scenario_refs = []
        scenario_facts = []
        for index, weight in mapping["scenario_fit"].items():
            scenario_value += base[index]["value"] * float(weight)
            scenario_refs.extend(base[index]["evidence_refs"])
            scenario_facts.append(f"{index}={base[index]['value']:.6f}")

        scenario_fit = {
            "value": round(scenario_value, 6),
            "evidence_refs": sorted(set(scenario_refs)),
            "source_fact": "candidate scenario fit from " + ", ".join(scenario_facts),
        }

        ledger["runners"][runner_id] = {
            "runner_name": str(runner.get("name") or ""),
            "base_indices": base,
            "dcr": {"score": dcr_score, "components": dcr_components},
            "weak_penalty_major_indices": list(mapping["weak_penalty_major_indices"]),
            "scenario_fit": scenario_fit,
            "feature_snapshot_sha256": _sha(features),
        }

    ledger["sha256"] = _sha(ledger)
    return ledger


def attach_candidate_ledger_to_request(request, mapping):
    request = json.loads(json.dumps(request, ensure_ascii=False))
    request["index_provenance_ledger"] = build_candidate_ledger(
        request["race_id"], request["runners"], mapping
    )
    request["numeric_calculation_requirement"] = "FULL_REQUIRED"
    request["base_index_mapping_authority"] = {
        "mapping_id": mapping["mapping_id"],
        "status": mapping["status"],
        "production_authority": False,
    }
    return request
