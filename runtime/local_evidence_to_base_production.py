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
REGISTRY_ID="LOCAL-BASE-INDEX-MAPPING-REGISTRY-v1.1-20260923"
TERMINAL_STATUSES={"CALCULATED","RULED-NEUTRAL","RULED-HOLD","NOT-APPLICABLE"}
RULE_BOUND_INDICES={
"EVI/CEV","CCI","TRI","PRI","OPI-V","DRS","URP","HCS","ZAI-WIN","ZAI-PLACE",
"SRI-L","T3I-L","WCI","W-AKI","P2-AKI","P3-AKI","ASI","RSI"
}

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
      "terminal_status":"CALCULATED",
      "value":round(value,6),
      "rule_id":f"LOCAL-v4.12R3-{name}-WEIGHTED",
      "mapping_version":REGISTRY_ID,
      "evidence_refs":sorted(set(refs)),
      "source_fact":" | ".join(facts),
      "components":parts,
    }

def _default_terminal(name, venue_rule_registry):
    defaults=(venue_rule_registry or {}).get("default_terminals") or {}
    spec=defaults.get(name)
    if isinstance(spec,dict):
        x=copy.deepcopy(spec)
        x.setdefault("terminal_status","RULED-HOLD")
        x.setdefault("rule_id","LOCAL-UNSPECIFIED-NUMERIC-MAPPING-HOLD-v1")
        x.setdefault("evidence_refs",[f"LOCAL-CANON:{name}"])
        x.setdefault("source_fact",f"{name}: no complete Production numeric mapping is registered; preserve semantically and hold numeric claim.")
        x.setdefault("venue_formula_registry",str((venue_rule_registry or {}).get("registry_id") or ""))
        return x
    return {
      "terminal_status":"RULED-HOLD",
      "rule_id":"LOCAL-UNSPECIFIED-NUMERIC-MAPPING-HOLD-v1",
      "evidence_refs":[f"LOCAL-CANON:{name}"],
      "source_fact":f"{name}: no complete Production numeric mapping is registered; preserve semantically and hold numeric claim.",
      "venue_formula_registry":str((venue_rule_registry or {}).get("registry_id") or ""),
    }

def _external_index(name, spec, allowed_rule_ids, venue_rule_registry):
    if not isinstance(spec,dict):
        spec=_default_terminal(name,venue_rule_registry)
    status=str(spec.get("terminal_status") or ("CALCULATED" if "value" in spec else "RULED-HOLD")).upper()
    if status not in TERMINAL_STATUSES:
        raise LocalMappingError(f"EXTERNAL_INDEX_TERMINAL_INVALID:{name}:{status}")
    rid=str(spec.get("rule_id") or "")
    refs=spec.get("evidence_refs")
    fact=str(spec.get("source_fact") or "").strip()
    if not rid or not isinstance(refs,list) or not refs or not fact:
        raise LocalMappingError(f"EXTERNAL_INDEX_PROVENANCE_MISSING:{name}")
    out={
      "terminal_status":status,
      "rule_id":rid,
      "mapping_version":REGISTRY_ID,
      "evidence_refs":[str(x) for x in refs],
      "source_fact":fact,
      "venue_formula_registry":str(spec.get("venue_formula_registry") or (venue_rule_registry or {}).get("registry_id") or "")
    }
    if status in {"CALCULATED","RULED-NEUTRAL"}:
        v=spec.get("value")
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not isfinite(float(v)) or not 0 <= float(v) <= 100:
            raise LocalMappingError(f"EXTERNAL_INDEX_VALUE_INVALID:{name}:{v}")
        if status=="CALCULATED" and rid not in set(allowed_rule_ids or []):
            raise LocalMappingError(f"UNREGISTERED_VENUE_RULE:{name}:{rid}")
        out["value"]=round(float(v),6)
    return out

def _hold(name, reason, evidence_refs):
    return {
      "terminal_status":"RULED-HOLD",
      "rule_id":f"LOCAL-{name.replace('/','_')}-DEPENDENCY-HOLD-v1",
      "mapping_version":REGISTRY_ID,
      "evidence_refs":sorted(set(str(x) for x in evidence_refs if x)),
      "source_fact":reason,
    }

def _has_value(spec):
    return isinstance(spec,dict) and spec.get("terminal_status") in {"CALCULATED","RULED-NEUTRAL"} and isinstance(spec.get("value"),(int,float)) and not isinstance(spec.get("value"),bool)

def materialize_runner(runner, venue_rule_registry=None, required_indices=None):
    out=copy.deepcopy(runner)
    feats=out.get("evidence_features") or {}
    canonical={}
    for idx in WEIGHTS:
        canonical[idx]=_weighted(idx,feats)

    ext=out.get("canonical_external_indices") or {}
    allowed=(venue_rule_registry or {}).get("allowed_rule_ids") or {}
    required=set(required_indices or [])

    # Rule-bound indices are terminalized even when no complete numeric mapping exists.
    for name in sorted(RULE_BOUND_INDICES | (required & RULE_BOUND_INDICES)):
        canonical[name]=_external_index(name,ext.get(name),allowed.get(name),venue_rule_registry)

    # TPI-L is exact only when EVI/CEV has a usable rule-bound numeric terminal.
    evi=canonical.get("EVI/CEV")
    if _has_value(evi):
        v={k:canonical[k]["value"] for k in WEIGHTS}
        ev=evi["value"]
        linear=0.18*v["HPI-L"]+0.16*v["CFIg-L"]+0.14*v["RFIg-L"]+0.08*v["BVIg-L"]+0.08*v["JTI-L"]+0.08*v["CSI-L"]+0.08*v["BWI-L"]+0.10*v["NCI"]+0.10*ev
        min_major=min(v["HPI-L"],v["CFIg-L"],v["RFIg-L"],v["NCI"],ev,v["BWI-L"])
        penalty=max(0.0,(60.0-min_major)*0.5)
        canonical["TPI-L"]={
          "terminal_status":"CALCULATED",
          "value":round(max(0.0,min(100.0,linear-penalty)),6),
          "rule_id":"LOCAL-TPI-L-v4.12R3",
          "mapping_version":REGISTRY_ID,
          "evidence_refs":sorted(set(sum([canonical[k]["evidence_refs"] for k in ["HPI-L","CFIg-L","RFIg-L","BVIg-L","JTI-L","CSI-L","BWI-L","NCI","EVI/CEV"]],[]))),
          "source_fact":f"TPI_linear={linear:.6f};min_major={min_major:.6f};penalty={penalty:.6f}",
        }
    else:
        canonical["TPI-L"]=_hold("TPI-L","TPI-L exact formula is known, but EVI/CEV lacks a registered usable numeric terminal; numeric claim held.",(evi or {}).get("evidence_refs") or ["LOCAL-CANON:EVI/CEV"])

    # Exact F3S-L formula is preserved; it is calculated only when every dependency is numeric.
    deps=["SRI-L","TPI-L","EVI/CEV","RFIg-L","CFIg-L","NCI","T3I-L"]
    if all(_has_value(canonical.get(k)) for k in deps):
        val=(0.25*canonical["SRI-L"]["value"]+0.20*canonical["TPI-L"]["value"]+
             0.18*canonical["EVI/CEV"]["value"]+0.14*canonical["RFIg-L"]["value"]+
             0.12*canonical["CFIg-L"]["value"]+0.06*canonical["NCI"]["value"]+
             0.05*canonical["T3I-L"]["value"])
        canonical["F3S-L"]={
          "terminal_status":"CALCULATED","value":round(max(0.0,min(100.0,val)),6),
          "rule_id":"LOCAL-F3S-L-v4.12R3","mapping_version":REGISTRY_ID,
          "evidence_refs":sorted(set(sum([canonical[k]["evidence_refs"] for k in deps],[]))),
          "source_fact":"F3S-L exact v4.12 Rev.3 formula from SRI-L,TPI-L,EVI,RFIg-L,CFIg-L,NCI,T3I-L."
        }
    elif "F3S-L" in required or "F3S-L" in ext:
        refs=[]
        for k in deps: refs.extend((canonical.get(k) or {}).get("evidence_refs") or [])
        canonical["F3S-L"]=_hold("F3S-L","F3S-L exact formula is known, but one or more required dependencies are non-numeric terminals; numeric claim held.",refs or ["LOCAL-CANON:F3S-L"])

    # Explicit external values for non-derived names may override the default HOLD only through registered rules.
    for name,spec in ext.items():
        if name in {"TPI-L","F3S-L"}: continue
        if name not in RULE_BOUND_INDICES:
            canonical[name]=_external_index(name,spec,allowed.get(name),venue_rule_registry)

    out["canonical_components"]=canonical
    out["local_mapping_registry"]=REGISTRY_ID
    out["numeric_materialization_hash"]=_sha(canonical)
    return out

def materialize_request(req, required_indices):
    q=copy.deepcopy(req)
    vr=q.get("venue_formula_registry")
    if vr is None:
        vr={"registry_id":"LOCAL-TERMINAL-FALLBACK-v1","allowed_rule_ids":{}}
    if not isinstance(vr,dict) or not str(vr.get("registry_id") or ""):
        raise LocalMappingError("VENUE_FORMULA_REGISTRY_INVALID")
    runners=q.get("runners")
    if not isinstance(runners,list) or not runners:
        raise LocalMappingError("RUNNERS_REQUIRED")
    required=[str(x) for x in required_indices]
    q["runners"]=[materialize_runner(r,vr,required) for r in runners]

    rows=[]; unresolved=[]
    counts={k:0 for k in TERMINAL_STATUSES}
    for r in q["runners"]:
        cc=r["canonical_components"]
        rid=str(r.get("runner_id"))
        for idx in required:
            spec=cc.get(idx)
            if not isinstance(spec,dict):
                unresolved.append({"runner_id":rid,"index":idx,"reason":"TERMINAL-UNRESOLVED"})
                continue
            status=str(spec.get("terminal_status") or "").upper()
            if status not in TERMINAL_STATUSES:
                unresolved.append({"runner_id":rid,"index":idx,"reason":"TERMINAL-STATUS-INVALID"})
                continue
            counts[status]+=1
            rows.append({"runner_id":rid,"index":idx,"terminal_status":status})
    required_count=len(runners)*len(required)
    terminalized=sum(counts.values())
    q["required_indices"]=required
    q["numeric_coverage"]={
      "required_count":required_count,
      "terminalized_count":terminalized,
      "calculated_count":counts["CALCULATED"],
      "ruled_neutral_count":counts["RULED-NEUTRAL"],
      "ruled_hold_count":counts["RULED-HOLD"],
      "not_applicable_count":counts["NOT-APPLICABLE"],
      "unresolved_count":len(unresolved),
      "unresolved":unresolved,
    }
    q["full_terminalization"]=(len(unresolved)==0 and terminalized==required_count)
    q["full_numerical_calculation"]=(q["full_terminalization"] and counts["CALCULATED"]==required_count)
    q["local_mapping_registry"]=REGISTRY_ID
    q["index_terminalization_hash"]=_sha(rows)
    q["index_provenance_hash"]=_sha([r["canonical_components"] for r in q["runners"]])
    return q
