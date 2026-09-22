from __future__ import annotations
import copy, hashlib, json
from math import isfinite
from runtime.local_evidence_feature_normalizer_production import validate_feature

class LocalMappingError(ValueError):
    pass

WEIGHTS={
"HPI-L":{"recent_finish":20,"finish_margin":15,"passing_position_content":20,"class_level":15,"opponent_strength":15,"repeatability":15},
"CFIg-L":{"same_venue":25,"same_distance":20,"similar_distance":15,"course_geometry":15,"turn_direction":10,"draw_style_fit":10,"going_fit":5},
"RFIg-L":{"running_style_repro":15,"position_acquisition":15,"position_maintenance":15,"third_corner_progression":15,"leadership_stalk_acceptance":10,"kickback_traffic_tolerance":10,"going_adaptation":10,"jockey_reproducibility":10},
"BVIg-L":{"sire_fit":30,"damsire_fit":20,"distance_sustain":15,"distance_trait":10,"surface_sand_fit":15,"venue_stat":5,"physical_style_fit":5},
"JTI-L":{"venue_recent":25,"distance_record":15,"stable_combo":15,"position_acquisition_skill":15,"progression_timing_skill":10,"favorite_reliability":10,"longshot_record":10},
"CSI-L":{"stable_venue_class_distance":25,"transfer_preparation":15,"layoff_preparation":15,"jockey_use_continuity":10,"cci_specificity":15,"tri_vertical_comparison":15,"rotation_management":5},
"BWI-L":{"good_weight_range":25,"weight_change_reason_rate":15,"carried_weight":15,"age_growth":10,"interval":10,"fatigue_rebound":10,"transport_season":5,"paddock":10},
"DCR":{"official_recent_coverage":25,"same_venue_distance_comparability":20,"training_comment_trial":15,"bodyweight_range_coverage":15,"same_day_gci_coverage":15,"late_odds_changes_coverage":10},
"NCI":{"current_class":20,"previous_class":15,"recent_opponent_class":20,"race_set_level":15,"class_change_pressure":10,"transfer_class":10,"class_relative_time":10},
}
REGISTRY_ID="LOCAL-BASE-INDEX-MAPPING-REGISTRY-v1.0-20260922"

def _sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def _weighted(name, features):
    parts=[]; total=0.0; denom=0.0; refs=[]; facts=[]
    for fname,w in WEIGHTS[name].items():
        if fname not in features:
            raise LocalMappingError(f"REQUIRED_COMPONENT_MISSING:{name}:{fname}")
        s=validate_feature(fname,features[fname])
        total += s["score"]*w
        denom += w
        refs.extend(s["evidence_refs"])
        facts.append(f"{fname}={s['score']}:{s['source_fact']}")
        parts.append({"feature":fname,"weight":w,**s})
    if denom<=0: raise LocalMappingError(f"BAD_WEIGHT_SUM:{name}")
    value=total/denom
    return {
      "value":round(value,6),
      "rule_id":f"LOCAL-v4.12R3-{name}-WEIGHTED",
      "mapping_version":REGISTRY_ID,
      "evidence_refs":sorted(set(refs)),
      "source_fact":" | ".join(facts),
      "components":parts,
    }

def _external_index(name, spec, allowed_rule_ids):
    if not isinstance(spec,dict):
        raise LocalMappingError(f"EXTERNAL_INDEX_MISSING:{name}")
    v=spec.get("value")
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not isfinite(float(v)) or not 0 <= float(v) <= 100:
        raise LocalMappingError(f"EXTERNAL_INDEX_VALUE_INVALID:{name}:{v}")
    rid=str(spec.get("rule_id") or "")
    if rid not in set(allowed_rule_ids or []):
        raise LocalMappingError(f"UNREGISTERED_VENUE_RULE:{name}:{rid}")
    refs=spec.get("evidence_refs")
    if not isinstance(refs,list) or not refs or not str(spec.get("source_fact") or "").strip():
        raise LocalMappingError(f"EXTERNAL_INDEX_PROVENANCE_MISSING:{name}")
    return {
      "value":round(float(v),6),"rule_id":rid,"mapping_version":REGISTRY_ID,
      "evidence_refs":[str(x) for x in refs],"source_fact":str(spec["source_fact"]),
      "venue_formula_registry":str(spec.get("venue_formula_registry") or "")
    }

def materialize_runner(runner, venue_rule_registry=None):
    out=copy.deepcopy(runner)
    feats=out.get("evidence_features") or {}
    canonical={}
    for idx in WEIGHTS:
        canonical[idx]=_weighted(idx,feats)

    ext=out.get("canonical_external_indices") or {}
    allowed=(venue_rule_registry or {}).get("allowed_rule_ids") or {}
    # EVI/CEV is needed for common TPI; its venue formula/translation remains venue-owned.
    evi=_external_index("EVI/CEV",ext.get("EVI/CEV"),allowed.get("EVI/CEV"))
    canonical["EVI/CEV"]=evi

    v={k:canonical[k]["value"] for k in WEIGHTS}
    ev=evi["value"]
    linear=0.18*v["HPI-L"]+0.16*v["CFIg-L"]+0.14*v["RFIg-L"]+0.08*v["BVIg-L"]+0.08*v["JTI-L"]+0.08*v["CSI-L"]+0.08*v["BWI-L"]+0.10*v["NCI"]+0.10*ev
    min_major=min(v["HPI-L"],v["CFIg-L"],v["RFIg-L"],v["NCI"],ev,v["BWI-L"])
    tpi=linear-max(0.0,(60.0-min_major)*0.5)
    canonical["TPI-L"]={
      "value":round(max(0.0,min(100.0,tpi)),6),
      "rule_id":"LOCAL-TPI-L-v4.12R3",
      "mapping_version":REGISTRY_ID,
      "evidence_refs":sorted(set(sum([canonical[k]["evidence_refs"] for k in ["HPI-L","CFIg-L","RFIg-L","BVIg-L","JTI-L","CSI-L","BWI-L","NCI","EVI/CEV"]],[]))),
      "source_fact":f"TPI_linear={linear:.6f};min_major={min_major:.6f};penalty={max(0.0,(60.0-min_major)*0.5):.6f}",
    }

    # Any other required numerical indices must come from an explicit venue/canonical rule registry.
    for name,spec in ext.items():
        if name=="EVI/CEV": continue
        canonical[name]=_external_index(name,spec,allowed.get(name))

    out["canonical_components"]=canonical
    out["local_mapping_registry"]=REGISTRY_ID
    out["numeric_materialization_hash"]=_sha(canonical)
    return out

def materialize_request(req, required_indices):
    q=copy.deepcopy(req)
    vr=q.get("venue_formula_registry")
    if not isinstance(vr,dict) or not str(vr.get("registry_id") or ""):
        raise LocalMappingError("VENUE_FORMULA_REGISTRY_REQUIRED")
    runners=q.get("runners")
    if not isinstance(runners,list) or not runners:
        raise LocalMappingError("RUNNERS_REQUIRED")
    q["runners"]=[materialize_runner(r,vr) for r in runners]
    unresolved=[]
    for r in q["runners"]:
        cc=r["canonical_components"]
        for idx in required_indices:
            if idx not in cc:
                unresolved.append({"runner_id":str(r.get("runner_id")),"index":idx,"reason":"FORMULA-UNRESOLVED"})
    q["required_indices"]=list(required_indices)
    q["numeric_coverage"]={
      "required_count":len(runners)*len(required_indices),
      "calculated_count":len(runners)*len(required_indices)-len(unresolved),
      "unresolved_count":len(unresolved),
      "unresolved":unresolved,
    }
    q["full_numerical_calculation"]=len(unresolved)==0
    q["local_mapping_registry"]=REGISTRY_ID
    q["index_provenance_hash"]=_sha([r["canonical_components"] for r in q["runners"]])
    return q
