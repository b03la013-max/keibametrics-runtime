from __future__ import annotations

import copy
import hashlib
import json
from math import isfinite

BASE = ["HPI","SSI","CFI","RFI","BVI","JTI","CSI","TRI","BWI","GCI","PRI","KGI","VMI"]
FORMULA_REGISTRY = "index_formula_registry JRA v1.0"


class ProductionMappingError(ValueError):
    pass


def _sha(obj):
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_mapping(path):
    with open(path, encoding="utf-8") as f:
        mapping = json.load(f)
    status = str(mapping.get("status", ""))
    if not status.startswith("PRODUCTION"):
        raise ProductionMappingError("MAPPING_NOT_PRODUCTION")
    return mapping


def _profile_for_runner(runner):
    starts = runner.get("career_starts")
    if starts is None:
        if runner.get("newcomer") is True:
            starts = 0
        else:
            raise ProductionMappingError(f"CAREER_STARTS_MISSING:{runner.get('runner_id')}")
    starts = int(starts)
    if starts <= 0:
        return "NEWCOMER"
    if starts <= 3:
        return "LOW_CAREER"
    return "ESTABLISHED"


def _feature_score(feature_name, features, mapping):
    spec = features.get(feature_name)
    if spec is None:
        return None
    if not isinstance(spec, dict):
        raise ProductionMappingError(f"FEATURE_NOT_OBJECT:{feature_name}")
    category = str(spec.get("category") or "").strip().upper()
    scale = mapping["category_scale"]
    if category not in scale:
        raise ProductionMappingError(f"FEATURE_CATEGORY_INVALID:{feature_name}:{category}")
    evidence_refs = spec.get("evidence_refs")
    source_fact = str(spec.get("source_fact") or "").strip()
    rule_id = str(spec.get("rule_id") or "").strip()
    if not isinstance(evidence_refs, list) or not evidence_refs:
        raise ProductionMappingError(f"FEATURE_EVIDENCE_MISSING:{feature_name}")
    if not source_fact:
        raise ProductionMappingError(f"FEATURE_SOURCE_FACT_MISSING:{feature_name}")
    if not rule_id:
        raise ProductionMappingError(f"FEATURE_RULE_ID_MISSING:{feature_name}")
    return {
        "score": float(scale[category]),
        "category": category,
        "evidence_refs": [str(x) for x in evidence_refs],
        "source_fact": source_fact,
        "rule_id": rule_id,
    }


def _weighted_index(index, profile, features, mapping):
    weights = mapping["index_profiles"][profile][index]
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
            "feature_rule_id": scored["rule_id"],
            "category": scored["category"],
            "category_score": scored["score"],
            "weighted_contribution": round(scored["score"] * weight, 6),
            "evidence_refs": scored["evidence_refs"],
            "source_fact": scored["source_fact"],
        })
        evidence_refs.extend(scored["evidence_refs"])
        source_facts.append(f"{feature_name}={scored['category']}:{scored['source_fact']}")

    minimum = float(mapping["profiles"][profile]["minimum_index_coverage_weight"])
    if covered + 1e-12 < minimum:
        raise ProductionMappingError(
            f"INDEX_EVIDENCE_COVERAGE_LOW:{profile}:{index}:{covered:.6f}<{minimum:.6f}"
        )

    value = numerator / covered
    return {
        "value": round(value, 6),
        "rule_id": f"JRA-PROD-EVIDENCE-{profile}-{index}-v1.0",
        "mapping_version": mapping["mapping_id"],
        "evidence_refs": sorted(set(evidence_refs)),
        "source_fact": " | ".join(source_facts),
        "adjustments": [],
        "components": components,
        "coverage_weight": round(covered, 6),
        "profile": profile,
    }


def _dcr_component(points, maximum, evidence_refs, source_fact, rule_id):
    points = float(points)
    maximum = float(maximum)
    if not isfinite(points) or not 0.0 <= points <= maximum:
        raise ProductionMappingError(f"DCR_POINTS_OUT_OF_RANGE:{points}/{maximum}")
    if not evidence_refs:
        raise ProductionMappingError("DCR_EVIDENCE_MISSING")
    if not rule_id:
        raise ProductionMappingError("DCR_RULE_ID_MISSING")
    return {
        "points": round(points, 6),
        "evidence_refs": sorted(set(str(x) for x in evidence_refs)),
        "source_fact": str(source_fact),
        "rule_id": str(rule_id),
    }


def _category_to_points(feature_name, maximum, features, mapping):
    scored = _feature_score(feature_name, features, mapping)
    if scored is None:
        return None
    points = float(maximum) * scored["score"] / 100.0
    return _dcr_component(points, maximum, scored["evidence_refs"], scored["source_fact"], scored["rule_id"])


def _dcr_for_runner(runner, profile, features, mapping):
    explicit = runner.get("dcr_inputs") or {}
    out = {}
    for name, spec in mapping["dcr"].items():
        maximum = float(spec["max_points"])
        if name in explicit:
            x = explicit[name]
            if not isinstance(x, dict):
                raise ProductionMappingError(f"DCR_INPUT_NOT_OBJECT:{runner.get('runner_id')}:{name}")
            out[name] = _dcr_component(
                x.get("points"), maximum, x.get("evidence_refs") or [],
                x.get("source_fact") or "", x.get("rule_id") or ""
            )
            continue

        feature = spec.get("feature")
        if feature:
            c = _category_to_points(feature, maximum, features, mapping)
            if c is not None:
                out[name] = c
                continue

        if profile == "NEWCOMER" and "newcomer_fallback_feature" in spec:
            c = _category_to_points(spec["newcomer_fallback_feature"], maximum, features, mapping)
            if c is not None:
                out[name] = c
                continue

        if profile == "NEWCOMER" and "newcomer_default_points" in spec:
            out[name] = _dcr_component(
                spec["newcomer_default_points"], maximum,
                [f"{runner.get('runner_id')}:NEWCOMER_STATUS"],
                "No realized pre-race history exists for this DCR component; uncertainty retained.",
                "JRA-DCR-NEWCOMER-NO-HISTORY-v1"
            )
            continue

        raise ProductionMappingError(f"DCR_COMPONENT_UNRESOLVED:{runner.get('runner_id')}:{name}")
    return out


def build_production_ledger(race_id, runners, mapping):
    if not race_id:
        raise ProductionMappingError("RACE_ID_MISSING")
    if not isinstance(runners, list) or len(runners) < 2:
        raise ProductionMappingError("RUNNERS_INVALID")

    ledger = {
        "mapping_id": mapping["mapping_id"],
        "mapping_status": mapping["status"],
        "calibration_status": mapping.get("calibration_status"),
        "formula_registry": FORMULA_REGISTRY,
        "race_id": race_id,
        "runners": {},
    }

    ids = []
    for runner in runners:
        rid = str(runner.get("runner_id") or "")
        if not rid:
            raise ProductionMappingError("RUNNER_ID_MISSING")
        if rid in ids:
            raise ProductionMappingError(f"DUPLICATE_RUNNER_ID:{rid}")
        ids.append(rid)

        features = runner.get("evidence_features")
        if not isinstance(features, dict):
            raise ProductionMappingError(f"EVIDENCE_FEATURES_MISSING:{rid}")

        profile = _profile_for_runner(runner)
        base = {idx: _weighted_index(idx, profile, features, mapping) for idx in BASE}
        dcr_components = _dcr_for_runner(runner, profile, features, mapping)
        dcr_score = round(sum(x["points"] for x in dcr_components.values()), 6)

        scenario_value = 0.0
        scenario_refs = []
        for idx, weight in mapping["scenario_fit"].items():
            scenario_value += base[idx]["value"] * float(weight)
            scenario_refs.extend(base[idx]["evidence_refs"])

        ledger["runners"][rid] = {
            "runner_name": str(runner.get("name") or ""),
            "profile": profile,
            "career_starts": int(runner.get("career_starts", 0 if runner.get("newcomer") else 4)),
            "base_indices": base,
            "dcr": {"score": dcr_score, "components": dcr_components},
            "weak_penalty_major_indices": list(mapping["weak_penalty_major_indices"]),
            "scenario_fit": {
                "value": round(scenario_value, 6),
                "evidence_refs": sorted(set(scenario_refs)),
                "source_fact": "Production scenario fit from fixed JRA v1.0 mapping."
            },
            "feature_snapshot_sha256": _sha(features),
        }

    ledger["sha256"] = _sha(ledger)
    return ledger


def attach_production_ledger_to_request(request, mapping):
    request = copy.deepcopy(request)
    request["index_provenance_ledger"] = build_production_ledger(
        request["race_id"], request["runners"], mapping
    )
    request["numeric_calculation_requirement"] = "FULL_REQUIRED"
    request["base_index_mapping_authority"] = {
        "mapping_id": mapping["mapping_id"],
        "status": mapping["status"],
        "production_authority": True,
        "calibration_status": mapping.get("calibration_status"),
    }
    return request
