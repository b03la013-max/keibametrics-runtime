from __future__ import annotations

import copy
import json
from datetime import datetime
from math import isfinite
from pathlib import Path

REQUIRED = ["HPI","SSI","CFI","RFI","BVI","JTI","CSI","TRI","BWI","GCI","PRI","KGI","VMI","DCR","TPI","ZAI_WIN","ZAI_PLACE","SRI","F3S","T3I"]


class KRSInputBridgeError(ValueError):
    pass


def _source_context(request):
    """Read already-frozen SOURCE context; never fetch or create a new admission gate."""
    source = request.get("source_snapshot") or {}
    if (not isinstance(source, dict) or source.get("family_id") != "JRA"
            or source.get("race_id") != request.get("race_id")
            or not request.get("source_snapshot_sha256")):
        return {}, "NO_BOUND_SOURCE_CONTEXT"
    from jra_source_runtime.source_acquisition import sha_obj
    source_sha = sha_obj({k:v for k,v in source.items() if k != "source_snapshot_sha256"})
    if (source_sha != request['source_snapshot_sha256']
            or source.get('source_snapshot_sha256',source_sha) != source_sha):
        return {}, "NO_BOUND_SOURCE_CONTEXT"
    try:
        freeze = datetime.fromisoformat(source["source_freeze_at"].replace("Z", "+00:00"))
        cutoff = datetime.fromisoformat(request["prediction_cutoff"].replace("Z", "+00:00"))
        source_cutoff = datetime.fromisoformat(source["prediction_cutoff"].replace("Z", "+00:00"))
        if not (freeze.tzinfo and cutoff.tzinfo and freeze <= cutoff == source_cutoff):
            return {}, "SOURCE_CONTEXT_TIME_INELIGIBLE"
        from jra_source_runtime.jra_observed_context import resolve_observed_context
        return resolve_observed_context(source), "FROZEN_SOURCE_CONTEXT"
    except (AttributeError, KeyError, TypeError, ValueError, OSError, EOFError):
        return {}, "SOURCE_CONTEXT_NOT_VERIFIABLE"


def _missing(value):
    return value is None or str(value).strip().lower() in ("", "unknown")


def _value(cc, name):
    x = cc.get(name)
    if not isinstance(x, dict):
        raise KRSInputBridgeError(f"CANONICAL_INDEX_MISSING:{name}")
    v=x.get("value")
    if not isinstance(v,(int,float)) or not isfinite(float(v)) or not 0 <= float(v) <= 100:
        raise KRSInputBridgeError(f"CANONICAL_INDEX_INVALID:{name}:{v}")
    if not x.get("rule_id") or not x.get("mapping_version") or not x.get("evidence_refs") or not x.get("source_fact"):
        raise KRSInputBridgeError(f"CANONICAL_PROVENANCE_INCOMPLETE:{name}")
    return float(v)


def _mean(*xs):
    return sum(xs)/len(xs)


def build_runner_input(runner):
    cc=runner.get("canonical_components")
    if not isinstance(cc,dict):
        raise KRSInputBridgeError(f"CANONICAL_COMPONENTS_MISSING:{runner.get('runner_id')}")
    vals={k:_value(cc,k) for k in REQUIRED}
    hsv={
        "base_competitive_ability":vals["HPI"],
        "class_strength":vals["KGI"],
        "condition_fit":_mean(vals["CSI"],vals["TRI"],vals["BWI"]),
        "distance_fit":vals["CFI"],
        "surface_fit":_mean(vals["CFI"],vals["GCI"]),
        "gate_reliability":vals["PRI"],
        "initial_acceleration":_mean(vals["SSI"],vals["PRI"]),
        "position_intent":vals["PRI"],
        "inside_cut_ability":_mean(vals["CFI"],vals["PRI"]),
        "outside_press_ability":_mean(vals["PRI"],vals["SSI"]),
        "leader_need":vals["PRI"],
        "stalk_acceptance":_mean(vals["RFI"],vals["PRI"]),
        "crowd_tolerance":vals["RFI"],
        "early_position_hold":_mean(vals["PRI"],vals["RFI"]),
        "midrace_hold":vals["RFI"],
        "progression_ceiling":_mean(vals["HPI"],vals["SSI"],vals["RFI"]),
        "progression_timing":_mean(vals["PRI"],vals["RFI"]),
        "corner_acceleration":_mean(vals["SSI"],vals["CFI"]),
        "traffic_escape":_mean(vals["PRI"],vals["RFI"]),
        "sustained_speed":_mean(vals["SSI"],vals["RFI"]),
        "pressure_tolerance":_mean(vals["RFI"],vals["KGI"]),
        "front_friction_tolerance":_mean(vals["RFI"],vals["SSI"]),
        "long_move_tolerance":_mean(vals["RFI"],vals["HPI"]),
        "final_reserve":_mean(vals["HPI"],vals["TRI"],vals["RFI"]),
        "deceleration_risk":100.0-_mean(vals["RFI"],vals["SSI"],vals["BWI"]),
        "training_state":vals["TRI"],
        "bodyweight_state":vals["BWI"],
        "layoff_uncertainty":100.0-vals["DCR"],
        "comment_state":vals["CSI"],
        "data_confidence":vals["DCR"],
    }
    static={
        "tpi":vals["TPI"],"zai_win":vals["ZAI_WIN"],"zai_place":vals["ZAI_PLACE"],
        "sri":vals["SRI"],"t3i":vals["T3I"],"f3s":vals["F3S"],
        "w_aki":vals["ZAI_WIN"],"p2_aki":vals["ZAI_PLACE"],"p3_aki":vals["T3I"],
        "asi":vals["F3S"],"rsi":vals["RFI"],
    }
    return {
        "horse_no":int(runner["runner_id"]),
        "name":str(runner.get("name") or ""),
        "hsv":{k:round(v,6) for k,v in hsv.items()},
        "static":{k:round(v,6) for k,v in static.items()},
        "static_roles":copy.deepcopy(runner.get("static_roles") or []),
        "uncertainty_scale":round(1.0 + max(0.0, 70.0-vals["DCR"])/100.0,6),
    }


def build_krs_input(request, bridge_profile="JRA-KRS-HSV-BRIDGE-v1.0-PRODUCTION-20260921"):
    req=copy.deepcopy(request)
    runners=req.get("runners")
    if not isinstance(runners,list) or len(runners)<2:
        raise KRSInputBridgeError("RUNNERS_INVALID")
    race=req.get("race") or req.get("race_identity") or {}
    race_id=req.get("race_id")
    if not race_id:
        raise KRSInputBridgeError("RACE_ID_MISSING")
    context, context_status = _source_context(req)
    environment=copy.deepcopy(req.get("environment") or {})
    if not environment:
        environment={
            "track":race.get("surface","unknown"),
            "weather":race.get("weather","unknown"),
            "source_cutoff":req.get("prediction_cutoff"),
        }
    # The existing builder looked only at the sparse request race dictionary,
    # so observed weather and going became unknown/null in all live inputs.
    # Fill missing metadata from the same frozen official SOURCE only. Explicit
    # simulation/environment choices, all HSV formulae and Physics are unchanged.
    filled = {}
    if _missing(environment.get("weather")) and context.get("weather"):
        environment["weather"] = context["weather"]
        filled["environment.weather"] = context["weather"]
    krs_race={
        "race_id":race_id,
        "venue":race.get("venue") or req.get("venue_id"),
        "surface":race.get("surface"),
        "distance":race.get("distance"),
        "course":race.get("course") or race.get("direction"),
        "going":race.get("going"),
        "class":race.get("class"),
    }
    for target, source_field in (("going", "going"), ("class", "race_class")):
        if _missing(krs_race.get(target)) and context.get(source_field):
            krs_race[target] = context[source_field]
            filled["race." + target] = context[source_field]
    req["krs_input_data"]={
        "race":krs_race,
        "environment":environment,
        "horses":[build_runner_input(r) for r in runners],
        "simulation":{
            "run_count":int(req.get("run_count",5000)),
            "master_seed":int(req.get("seed",1)),
        },
    }
    req["jra_adapter_mode"]="EXPLICIT_ENGINE_HSV"
    req["explicit_engine_hsv_provenance"]={
        "source_snapshot_sha256":req.get("source_snapshot_sha256"),
        "mapping_authority":bridge_profile,
        "canonical_index_mapping_authority":(req.get("base_index_mapping_authority") or {}).get("mapping_id"),
        "index_provenance_hash":req.get("index_provenance_hash"),
        "source_context_status":context_status,
        "observed_context_sha256":context.get("sha256"),
        "filled_source_context_fields":filled,
    }
    return req
