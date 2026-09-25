from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Dict, List, Tuple

PROFILE = "KM-JRA-SOURCE-TO-EVIDENCE-FEATURE-COMPILER-v1.1-20260926"
POLICY_ID = "KM-JRA-SOURCE-TO-FEATURE-POLICY-v1.1-20260926"
BASE_INDICES = ["HPI","SSI","CFI","RFI","BVI","JTI","CSI","TRI","BWI","GCI","PRI","KGI","VMI"]

class SourceToFeatureError(ValueError):
    pass

def _sha(x: Any) -> str:
    return hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()

def _runner_profile(r: Dict[str, Any]) -> str | None:
    starts = r.get("career_starts")
    if starts is None:
        if r.get("newcomer") is True:
            starts = 0
        else:
            return None
    starts = int(starts)
    if starts <= 0:
        return "NEWCOMER"
    if starts <= 3:
        return "LOW_CAREER"
    return "ESTABLISHED"

def _official_runner_map(artifact: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    u = artifact.get("jra_official_runner_universe") or artifact.get("official_runner_universe") or {}
    out = {}
    for x in u.get("runners") or []:
        rid = str(x.get("runner_id") or x.get("horse_no") or "")
        if rid:
            out[rid] = x
    return out

def _tsl_runner_map(artifact: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    t = artifact.get("tsl_public_shadow_evidence") or {}
    return {str(x.get("horse_no")): x for x in (t.get("runners") or []) if x.get("horse_no") is not None}

def _feature(category: str, rule_id: str, refs: List[str], fact: str, *, authority: str) -> Dict[str, Any]:
    return {
        "category": str(category).upper(),
        "rule_id": str(rule_id),
        "evidence_refs": sorted(set(str(x) for x in refs if str(x))),
        "source_fact": str(fact),
        "source_authority": str(authority),
        "result_derived": False,
    }

def _shadow_observation(kind: str, refs: List[str], fact: str, payload: Dict[str, Any], authority: str) -> Dict[str, Any]:
    x = {
        "kind": kind,
        "evidence_refs": sorted(set(str(z) for z in refs if str(z))),
        "source_fact": str(fact),
        "payload": payload,
        "authority": authority,
        "production_authority": False,
        "prediction_authority": False,
    }
    x["sha256"] = _sha(x)
    return x

def _equal_weight_feature(rid: str, runner: Dict[str, Any], official: Dict[str, Dict[str, Any]], artifact: Dict[str, Any]):
    cur = official.get(rid) or {}
    w = cur.get("assigned_weight")
    if w is None:
        return None
    weights = []
    for x in official.values():
        if x.get("status", "ACTIVE") != "ACTIVE":
            continue
        if x.get("assigned_weight") is None:
            return None
        weights.append(float(x["assigned_weight"]))
    if len(weights) < 2 or max(weights) - min(weights) > 1e-9:
        return None
    ref = artifact.get("jra_official_runner_universe_sha256") or artifact.get("official_runner_universe_sha256")
    fact = f"JRA official assigned weight {float(w):g} kg; all active runners carry the same assigned weight."
    return _feature("NEUTRAL", "JRA-WEIGHT-EQUAL-CONDITION-v1", [ref, f"JRA:RUNNER:{rid}:ASSIGNED_WEIGHT"], fact, authority="JRA_OFFICIAL")

def _tsl_shadow(rid: str, tsl: Dict[str, Dict[str, Any]], artifact: Dict[str, Any]) -> List[Dict[str, Any]]:
    x = tsl.get(rid)
    if not x:
        return []
    ref = artifact.get("tsl_public_shadow_evidence_sha256")
    out = []
    out.append(_shadow_observation(
        "TSL_PUBLIC_RUNNER_SIGNAL",
        [ref, f"TSL:RUNNER:{rid}"],
        "Third-party TSL pre-race public signal captured; never a Production feature by itself.",
        {
            "mark": x.get("mark"),
            "win_vote": (x.get("win_vote") or {}).get("value"),
            "place_vote": (x.get("place_vote") or {}).get("value"),
            "quinella_vote": (x.get("quinella_vote") or {}).get("value"),
            "fracture": (x.get("fracture") or {}).get("value"),
            "competition": (x.get("competition") or {}).get("value"),
            "anomaly": (x.get("anomaly") or {}).get("value"),
        },
        "TSL_PUBLIC_NON_OFFICIAL",
    ))
    return out

FEATURE_SOURCE_FAMILY = {
    "recent_performance":"JRA_HORSE_HISTORY",
    "recent_speed":"JRA_HORSE_HISTORY",
    "class_performance":"JRA_HORSE_HISTORY",
    "opponent_strength":"JRA_HORSE_HISTORY",
    "finish_margin":"JRA_HORSE_HISTORY",
    "pace_resilience":"JRA_HORSE_HISTORY_DETAIL",
    "closing_quality":"JRA_HORSE_HISTORY_DETAIL",
    "speed_reliability":"JRA_HORSE_HISTORY",
    "recent_consistency":"JRA_HORSE_HISTORY",
    "same_course_fit":"JRA_HORSE_HISTORY",
    "same_distance_fit":"JRA_HORSE_HISTORY",
    "same_course_distance_quality":"JRA_HORSE_HISTORY",
    "official_recent_quality":"JRA_HORSE_HISTORY",
    "surface_fit":"JRA_HORSE_HISTORY",
    "going_fit":"JRA_HORSE_HISTORY",
    "bodyweight_history_quality":"JRA_HORSE_HISTORY",
    "bodyweight_range_fit":"JRA_HORSE_HISTORY",
    "bodyweight_delta_fit":"JRA_CURRENT_BODYWEIGHT",
    "weight_load_fit":"JRA_OFFICIAL_RACE_CARD",
    "course_geometry_fit":"VENUE_CANON",
    "similar_geometry_fit":"VENUE_CANON_PLUS_HISTORY",
    "turn_direction_fit":"VENUE_CANON_PLUS_HISTORY",
    "draw_course_fit":"VENUE_CANON_PLUS_DRAW",
    "distance_fit":"JRA_HORSE_HISTORY_OR_PEDIGREE",
    "pedigree_surface":"JRA_PEDIGREE_HISTORY",
    "pedigree_distance":"JRA_PEDIGREE_HISTORY",
    "pedigree_class":"JRA_PEDIGREE_HISTORY",
    "physical_pedigree_fit":"JRA_PEDIGREE_HISTORY",
    "maternal_class_signal":"JRA_PEDIGREE_HISTORY",
    "sire_track_signal":"JRA_PEDIGREE_HISTORY",
    "sire_newcomer_signal":"JRA_PEDIGREE_HISTORY",
    "sprint_pedigree":"JRA_PEDIGREE_HISTORY",
    "jockey_quality":"JRA_JOCKEY_STATS",
    "jockey_venue_fit":"JRA_JOCKEY_STATS",
    "jockey_style_fit":"JRA_JOCKEY_STYLE",
    "jockey_horse_fit":"JRA_HORSE_HISTORY",
    "trainer_jockey_fit":"JRA_TRAINER_JOCKEY_STATS",
    "trainer_quality":"JRA_TRAINER_STATS",
    "stable_trainer_class":"JRA_TRAINER_STATS",
    "stable_readiness":"TRAINER_COMMENT_OR_AUTHORIZED_SOURCE",
    "target_intent":"TRAINER_COMMENT_OR_AUTHORIZED_SOURCE",
    "stable_comment_state":"TRAINER_COMMENT_OR_AUTHORIZED_SOURCE",
    "preparation_continuity":"TRAINING_OR_STABLE_HISTORY",
    "rotation_fit":"JRA_HORSE_HISTORY",
    "layoff_readiness":"JRA_HORSE_HISTORY",
    "workout_capability":"JRA_TRAINING",
    "workout_speed":"JRA_TRAINING",
    "workout_partner_level":"JRA_TRAINING",
    "workout_finish":"JRA_TRAINING",
    "workout_consistency":"JRA_TRAINING",
    "workout_load":"JRA_TRAINING",
    "training_comments_quality":"JRA_TRAINING_OR_COMMENT",
    "physical_readiness":"JRA_BODYWEIGHT_TRAINING_OR_PADDOCK",
    "body_condition_comment":"PADDOCK_OR_AUTHORIZED_COMMENT",
    "equipment_effect":"JRA_EQUIPMENT_HISTORY",
    "same_day_track_fit":"JRA_SAME_DAY_RESULTS_PLUS_STYLE",
    "track_bias_fit":"JRA_SAME_DAY_RESULTS_PLUS_STYLE",
    "weather_fit":"JMA_PLUS_HORSE_WEATHER_HISTORY",
    "gate_quality":"PACE_MAP_OR_HISTORY",
    "dash_quality":"PACE_MAP_OR_HISTORY",
    "position_quality":"PACE_MAP_OR_HISTORY",
    "position_reproducibility":"JRA_HORSE_HISTORY_DETAIL",
    "pressure_resilience":"JRA_HORSE_HISTORY_DETAIL",
    "progression_ability":"JRA_HORSE_HISTORY_DETAIL",
    "forward_speed_comment":"AUTHORIZED_COMMENT_OR_PACE_MAP",
    "market_rank":"JRA_OFFICIAL_MARKET",
    "market_stability":"JRA_OFFICIAL_MARKET_TIME_SERIES",
    "market_mismatch":"JRA_OFFICIAL_MARKET_PLUS_MODEL",
    "expert_support":"AUTHORIZED_EXPERT_SOURCE",
    "external_index_support":"REGISTERED_EXTERNAL_SHADOW",
    "hidden_class":"JRA_HORSE_HISTORY",
}


AUTOMATION_CLASS = {
    "JRA_OFFICIAL_RACE_CARD":"ADAPTER_READY_OR_REQUEST_PROVIDED",
    "JRA_CURRENT_BODYWEIGHT":"ADAPTER_REQUIRED",
    "JRA_HORSE_HISTORY":"ADAPTER_REQUIRED",
    "JRA_HORSE_HISTORY_DETAIL":"ADAPTER_REQUIRED",
    "JRA_PEDIGREE_HISTORY":"ADAPTER_REQUIRED",
    "JRA_JOCKEY_STATS":"ADAPTER_REQUIRED",
    "JRA_JOCKEY_STYLE":"ADAPTER_REQUIRED",
    "JRA_TRAINER_JOCKEY_STATS":"ADAPTER_REQUIRED",
    "JRA_TRAINER_STATS":"ADAPTER_REQUIRED",
    "TRAINER_COMMENT_OR_AUTHORIZED_SOURCE":"ADAPTER_REQUIRED",
    "TRAINING_OR_STABLE_HISTORY":"ADAPTER_REQUIRED",
    "JRA_TRAINING":"ADAPTER_REQUIRED",
    "JRA_TRAINING_OR_COMMENT":"ADAPTER_REQUIRED",
    "JRA_BODYWEIGHT_TRAINING_OR_PADDOCK":"ADAPTER_REQUIRED",
    "PADDOCK_OR_AUTHORIZED_COMMENT":"ADAPTER_REQUIRED",
    "JRA_EQUIPMENT_HISTORY":"ADAPTER_REQUIRED",
    "JRA_SAME_DAY_RESULTS_PLUS_STYLE":"SHADOW_OR_ADAPTER_REQUIRED",
    "JMA_PLUS_HORSE_WEATHER_HISTORY":"SHADOW_OR_ADAPTER_REQUIRED",
    "PACE_MAP_OR_HISTORY":"ADAPTER_REQUIRED",
    "AUTHORIZED_COMMENT_OR_PACE_MAP":"ADAPTER_REQUIRED",
    "JRA_OFFICIAL_MARKET":"ADAPTER_REQUIRED",
    "JRA_OFFICIAL_MARKET_TIME_SERIES":"ADAPTER_REQUIRED",
    "JRA_OFFICIAL_MARKET_PLUS_MODEL":"ADAPTER_REQUIRED",
    "AUTHORIZED_EXPERT_SOURCE":"ADAPTER_REQUIRED",
    "REGISTERED_EXTERNAL_SHADOW":"SHADOW_ONLY",
    "VENUE_CANON":"VENUE_BINDING_REQUIRED",
    "VENUE_CANON_PLUS_HISTORY":"VENUE_BINDING_PLUS_HISTORY_REQUIRED",
    "VENUE_CANON_PLUS_DRAW":"VENUE_BINDING_REQUIRED",
    "JRA_HORSE_HISTORY_OR_PEDIGREE":"ADAPTER_REQUIRED",
}

def validate_feature_contract(mapping: Dict[str, Any], rule_registry: Dict[str, Any] | None = None) -> Dict[str, Any]:
    allowed = _allowed_features(mapping)
    mapped = set(FEATURE_SOURCE_FAMILY)
    missing_source_map = sorted(allowed - mapped)
    if missing_source_map:
        raise SourceToFeatureError("FEATURE_SOURCE_FAMILY_INCOMPLETE:"+",".join(missing_source_map))
    unclassified = sorted({FEATURE_SOURCE_FAMILY[f] for f in allowed if FEATURE_SOURCE_FAMILY[f] not in AUTOMATION_CLASS})
    if unclassified:
        raise SourceToFeatureError("SOURCE_FAMILY_AUTOMATION_CLASS_MISSING:"+",".join(unclassified))
    unregistered = []
    if rule_registry is not None:
        rules = rule_registry.get("feature_rules") or {}
        unregistered = sorted(allowed - set(rules))
        if unregistered:
            raise SourceToFeatureError("FEATURE_RULE_REGISTRY_INCOMPLETE:"+",".join(unregistered))
    return {
        "mapping_feature_count": len(allowed),
        "source_family_mapped_count": len(allowed),
        "rule_registry_bound_count": len(allowed)-len(unregistered) if rule_registry is not None else None,
        "missing_source_map": missing_source_map,
        "source_families": sorted({FEATURE_SOURCE_FAMILY[f] for f in allowed}),
    }

def _source_only_runner(runner: Dict[str, Any], generated: Dict[str, Any]) -> Dict[str, Any]:
    x = copy.deepcopy(runner)
    x["evidence_features"] = copy.deepcopy(generated)
    return x

def _automation_gap(coverage: Dict[str, Any]) -> Dict[str, Any]:
    by_source: Dict[str, List[Dict[str, Any]]] = {}
    seen = set()
    for data in (coverage.get("indices") or {}).values():
        for m in data.get("missing_features") or []:
            key=(m.get("feature"),m.get("source_family"))
            if key in seen:
                continue
            seen.add(key)
            fam=str(m.get("source_family") or "UNMAPPED_SOURCE_FAMILY")
            by_source.setdefault(fam,[]).append({
                "feature":m.get("feature"),
                "weight":m.get("weight"),
                "automation_class":AUTOMATION_CLASS.get(fam,"UNCLASSIFIED"),
            })
    for m in coverage.get("dcr_missing") or []:
        f=m.get("feature"); fam=str(m.get("source_family") or "EXPLICIT_DCR_INPUT")
        if f and (f,fam) not in seen:
            by_source.setdefault(fam,[]).append({
                "feature":f,
                "weight":None,
                "automation_class":AUTOMATION_CLASS.get(fam,"UNCLASSIFIED"),
                "dcr_component":m.get("component"),
            })
    return {
        "missing_source_family_count":len(by_source),
        "missing_source_families":sorted(by_source),
        "by_source_family":{k:sorted(v,key=lambda z:str(z.get("feature"))) for k,v in sorted(by_source.items())},
    }

def _allowed_features(mapping: Dict[str, Any]) -> set[str]:
    out = set()
    for prof in (mapping.get("index_profiles") or {}).values():
        for weights in prof.values():
            out.update(weights)
    for d in (mapping.get("dcr") or {}).values():
        if d.get("feature"):
            out.add(d["feature"])
        if d.get("newcomer_fallback_feature"):
            out.add(d["newcomer_fallback_feature"])
    return out

def _coverage_for_runner(runner: Dict[str, Any], mapping: Dict[str, Any]) -> Dict[str, Any]:
    profile = _runner_profile(runner)
    feats = set((runner.get("evidence_features") or {}).keys())
    if profile is None:
        return {
            "profile": None,
            "formal_base_ready": False,
            "error": "CAREER_STARTS_OR_NEWCOMER_STATUS_REQUIRED",
            "indices": {},
            "missing_source_families": ["JRA_HORSE_HISTORY"],
        }
    min_weight = float(mapping["profiles"][profile]["minimum_index_coverage_weight"])
    indices = {}
    missing_sources = set()
    ready = True
    for idx in BASE_INDICES:
        weights = mapping["index_profiles"][profile][idx]
        covered = sum(float(w) for f,w in weights.items() if f in feats)
        missing = [
            {"feature":f,"weight":float(w),"source_family":FEATURE_SOURCE_FAMILY.get(f,"UNMAPPED_SOURCE_FAMILY")}
            for f,w in sorted(weights.items(), key=lambda kv:-float(kv[1])) if f not in feats
        ]
        ok = covered + 1e-12 >= min_weight
        ready = ready and ok
        if not ok:
            for x in missing:
                missing_sources.add(x["source_family"])
        indices[idx] = {
            "covered_weight": round(covered, 6),
            "minimum_required_weight": min_weight,
            "pass": ok,
            "missing_features": missing,
        }
    dcr_missing = []
    explicit = runner.get("dcr_inputs") or {}
    for name,spec in (mapping.get("dcr") or {}).items():
        if name in explicit:
            continue
        f = spec.get("feature")
        fallback = spec.get("newcomer_fallback_feature")
        if f and f in feats:
            continue
        if profile == "NEWCOMER" and fallback and fallback in feats:
            continue
        if profile == "NEWCOMER" and "newcomer_default_points" in spec:
            continue
        dcr_missing.append({"component":name,"feature":f,"source_family":FEATURE_SOURCE_FAMILY.get(f,"UNMAPPED_SOURCE_FAMILY") if f else "EXPLICIT_DCR_INPUT"})
        if f:
            missing_sources.add(FEATURE_SOURCE_FAMILY.get(f,"UNMAPPED_SOURCE_FAMILY"))
    if dcr_missing:
        ready = False
    return {
        "profile": profile,
        "formal_base_ready": ready,
        "indices": indices,
        "dcr_missing": dcr_missing,
        "present_feature_count": len(feats),
        "missing_source_families": sorted(missing_sources),
    }

def _merge_generated(existing: Dict[str, Any], generated: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    out = copy.deepcopy(existing or {})
    conflicts = []
    for f,x in generated.items():
        if f not in out:
            out[f] = x
            continue
        old = out[f]
        if isinstance(old,dict) and (old.get("category") != x.get("category") or old.get("rule_id") != x.get("rule_id")):
            conflicts.append({
                "feature":f,
                "existing_category":old.get("category"),
                "existing_rule_id":old.get("rule_id"),
                "generated_category":x.get("category"),
                "generated_rule_id":x.get("rule_id"),
                "resolution":"EXISTING_PRESERVED / NO_SILENT_OVERWRITE",
            })
    return out, conflicts

def compile_source_to_features(source_artifact: Dict[str, Any], request_runners: List[Dict[str, Any]], mapping: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(source_artifact,dict) or source_artifact.get("family_id") not in {None,"JRA"}:
        raise SourceToFeatureError("JRA_SOURCE_ARTIFACT_REQUIRED")
    source_sha = str(source_artifact.get("source_snapshot_sha256") or "")
    if not source_sha:
        raise SourceToFeatureError("SOURCE_SNAPSHOT_SHA_MISSING")
    official = _official_runner_map(source_artifact)
    tsl = _tsl_runner_map(source_artifact)
    allowed = _allowed_features(mapping)
    contract = validate_feature_contract(mapping)
    runners_out = {}
    all_missing_sources = set()
    all_ready = True
    for r in request_runners or []:
        rid = str(r.get("runner_id") or r.get("horse_no") or "")
        if not rid:
            raise SourceToFeatureError("RUNNER_ID_MISSING")
        if rid not in official:
            raise SourceToFeatureError("SOURCE_RUNNER_NOT_IN_OFFICIAL_UNIVERSE:"+rid)
        generated = {}
        w = _equal_weight_feature(rid,r,official,source_artifact)
        if w is not None:
            generated["weight_load_fit"] = w
        generated = {k:v for k,v in generated.items() if k in allowed}
        merged, conflicts = _merge_generated(r.get("evidence_features") or {}, generated)
        shadow = _tsl_shadow(rid,tsl,source_artifact)
        source_only_coverage = _coverage_for_runner(_source_only_runner(r, generated),mapping)
        tmp = copy.deepcopy(r)
        tmp["evidence_features"] = merged
        coverage = _coverage_for_runner(tmp,mapping)
        gap = _automation_gap(source_only_coverage)
        all_ready = all_ready and bool(coverage.get("formal_base_ready"))
        all_missing_sources.update(coverage.get("missing_source_families") or [])
        runners_out[rid] = {
            "runner_name": str(r.get("name") or official[rid].get("name") or ""),
            "generated_production_features": generated,
            "generated_production_feature_count": len(generated),
            "shadow_observations": shadow,
            "shadow_observation_count": len(shadow),
            "merge_conflicts": conflicts,
            "merged_feature_count": len(merged),
            "source_only_coverage": source_only_coverage,
            "source_only_formal_base_ready": bool(source_only_coverage.get("formal_base_ready")),
            "automation_gap": gap,
            "coverage": coverage,
            "merged_evidence_features": merged,
        }
    out = {
        "profile": PROFILE,
        "policy_id": POLICY_ID,
        "race_id": source_artifact.get("race_id"),
        "source_snapshot_sha256": source_sha,
        "official_runner_universe_sha256": source_artifact.get("jra_official_runner_universe_sha256") or source_artifact.get("official_runner_universe_sha256"),
        "mapping_id": mapping.get("mapping_id"),
        "feature_contract": contract,
        "source_only_formal_base_ready": all(bool(x.get("source_only_formal_base_ready")) for x in runners_out.values()) if runners_out else False,
        "production_feature_principle": "ONLY_DETERMINISTIC_RULE_BOUND_FACTS_FROM_PRODUCTION_AUTHORIZED_SOURCES; NO_TSL_OR_JMA_SHADOW_INJECTION",
        "shadow_isolation": True,
        "runner_count": len(runners_out),
        "runners": runners_out,
        "formal_base_ready_after_merge": all_ready,
        "missing_source_families": sorted(all_missing_sources),
        "limitations": [
            "TSL/JMA/same-day derived shadow evidence is never injected into Production Evidence Features by this compiler.",
            "Missing evidence remains missing; UNKNOWN is never converted to WEAK or neutral 50.",
            "Historical performance, pedigree population rates, jockey/trainer statistics, workout and comments require separately verified adapters before automatic Production use.",
            "The compiler fills missing features only and never silently overwrites an existing valid feature classification.",
        ],
    }
    out["sha256"] = _sha(out)
    return out

def attach_source_features_to_request(request: Dict[str, Any], source_artifact: Dict[str, Any], mapping: Dict[str, Any]) -> Dict[str, Any]:
    req = copy.deepcopy(request)
    report = compile_source_to_features(source_artifact, req.get("runners") or [], mapping)
    by_id = {str(r.get("runner_id") or r.get("horse_no") or ""):r for r in req.get("runners") or []}
    for rid,rr in report["runners"].items():
        by_id[rid]["evidence_features"] = copy.deepcopy(rr["merged_evidence_features"])
        by_id[rid]["source_shadow_observations"] = copy.deepcopy(rr["shadow_observations"])
    req["source_to_evidence_feature_compiler"] = {
        k:v for k,v in report.items() if k != "runners"
    }
    req["source_to_evidence_feature_runner_coverage"] = {
        rid:{
            "generated_production_feature_count":rr["generated_production_feature_count"],
            "shadow_observation_count":rr["shadow_observation_count"],
            "merge_conflicts":rr["merge_conflicts"],
            "source_only_formal_base_ready":rr["source_only_formal_base_ready"],
            "source_only_coverage":rr["source_only_coverage"],
            "automation_gap":rr["automation_gap"],
            "coverage":rr["coverage"],
        } for rid,rr in report["runners"].items()
    }
    req["source_to_evidence_feature_sha256"] = report["sha256"]
    return req
