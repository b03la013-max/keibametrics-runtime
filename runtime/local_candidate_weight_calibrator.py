from __future__ import annotations

import copy
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

PROFILE="KM-LOCAL-WEIGHT-CALIBRATION-v0.2-CANDIDATE-20260923-URW-DAY1"
DEFAULT_REGISTRY="mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json"
DEFAULT_MAPPING="mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json"

ROLE_FACTORS={
    "W":["ZAI-WIN","SRI-L","WCI","ASI","INV:W-AKI"],
    "P2":["ZAI-PLACE","SRI-L","F3S-L","ASI","INV:P2-AKI"],
    "P3":["T3I-L","F3S-L","ZAI-PLACE","ASI","INV:P3-AKI"],
}
ROLE_TARGET_POS={"W":0,"P2":1,"P3":2}
TOP3_RELEVANCE=[1.0,0.65,0.45]


class CalibrationError(ValueError):
    pass


def _load(path):
    with open(path,encoding="utf-8") as f: return json.load(f)


def _sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def _mean(xs):
    xs=[float(x) for x in xs]
    return None if not xs else sum(xs)/len(xs)


def _sd(xs):
    xs=[float(x) for x in xs]
    if len(xs)<2: return 0.0
    return statistics.pstdev(xs)


def _clip(x,lo=-2.0,hi=2.0):
    return max(lo,min(hi,float(x)))


def _candidate_feature(runner,comp):
    x=(runner.get("evidence_features") or {}).get(comp)
    if not isinstance(x,dict) or x.get("missing") is True:
        return None
    v=x.get("score")
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(float(v)):
        return None
    return float(v)


def _candidate_index(runner,name):
    inverse=False
    if name.startswith("INV:"):
        inverse=True; name=name[4:]
    x=(runner.get("canonical_components") or {}).get(name)
    if not isinstance(x,dict):
        return None
    v=x.get("value")
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(float(v)):
        return None
    v=float(v)
    return 100-v if inverse else v


def _runner_map(q):
    return {str(r.get("runner_id")):r for r in (q.get("runners") or [])}


def _role_separation(values: Dict[str,float], target: str, top3: List[str]) -> float|None:
    if target not in values:
        return None
    controls=[v for rid,v in values.items() if rid not in set(top3)]
    allv=list(values.values())
    if len(controls)<3 or len(allv)<5:
        return None
    sd=_sd(allv)
    if sd<1e-9:
        return None
    return _clip((values[target]-_mean(controls))/sd)


def _calibration_strength(n_races:int, prior_races:int, max_amplitude:float, signal:float)->Tuple[float,float]:
    reliability=n_races/max(1.0,n_races+prior_races)
    delta=max_amplitude*reliability*math.tanh(float(signal))
    return reliability,delta


def calibrate(pre_result: Dict[str,Dict[str,Any]], outcomes: Dict[str,Dict[str,Any]],
              registry_path=DEFAULT_REGISTRY, mapping_path=DEFAULT_MAPPING,
              *, prior_races:int=26, max_component_amplitude:float=0.25,
              max_role_amplitude:float=0.25)->Dict[str,Any]:
    reg=_load(registry_path); mapping=_load(mapping_path)
    common=reg.get("common_component_sets") or {}
    if not common: raise CalibrationError("COMPONENT_SETS_MISSING")
    labels=sorted(set(pre_result)&set(outcomes))
    if not labels: raise CalibrationError("NO_MATCHED_RACES")

    # Component outcome separation. Result data is loaded only after every pre-result candidate
    # matrix has been frozen by the calling workflow.
    component_stats={}
    for idx,comps in common.items():
        for comp in comps:
            race_signals=[]
            role_observations=[]
            for label in labels:
                q=pre_result[label]; top3=list(map(str,outcomes[label]["top3"]))
                rm=_runner_map(q)
                values={}
                for rid,r in rm.items():
                    v=_candidate_feature(r,comp)
                    if v is not None: values[rid]=v
                weighted=[]; wsum=0.0
                for pos,target in enumerate(top3):
                    z=_role_separation(values,target,top3)
                    if z is None: continue
                    w=TOP3_RELEVANCE[pos]
                    weighted.append(z*w); wsum+=w
                    role_observations.append({"race":label,"position":pos+1,"z":z})
                if weighted and wsum>0:
                    race_signals.append(sum(weighted)/wsum)
            signal=_mean(race_signals) if race_signals else 0.0
            reliability,delta=_calibration_strength(len(race_signals),prior_races,max_component_amplitude,signal)
            component_stats[f"{idx}.{comp}"]={
                "index":idx,"component":comp,
                "baseline_weight":float(comps[comp]),
                "race_count":len(race_signals),
                "role_observation_count":len(role_observations),
                "mean_separation_z":round(signal,6),
                "reliability":round(reliability,6),
                "raw_multiplier":round(1+delta,8),
                "role_observations":role_observations,
            }

    calibrated_sets={}
    for idx,comps in common.items():
        target_sum=sum(float(x) for x in comps.values())
        raw={}
        for comp,w in comps.items():
            mult=component_stats[f"{idx}.{comp}"]["raw_multiplier"]
            raw[comp]=float(w)*mult
        rawsum=sum(raw.values()) or 1.0
        calibrated_sets[idx]={comp:round(v*target_sum/rawsum,6) for comp,v in raw.items()}
        for comp in comps:
            component_stats[f"{idx}.{comp}"]["calibrated_weight"]=calibrated_sets[idx][comp]
            component_stats[f"{idx}.{comp}"]["weight_change_pct"]=round(
                100*(calibrated_sets[idx][comp]/float(comps[comp])-1),6
            )

    # Role-score factor calibration is separate from base-index component calibration.
    role_profiles={}
    for role,factors in ROLE_FACTORS.items():
        signals={}
        target_pos=ROLE_TARGET_POS[role]
        for factor in factors:
            race_signals=[]
            for label in labels:
                q=pre_result[label]; top3=list(map(str,outcomes[label]["top3"]))
                target=top3[target_pos]; rm=_runner_map(q)
                values={}
                for rid,r in rm.items():
                    v=_candidate_index(r,factor)
                    if v is not None: values[rid]=v
                z=_role_separation(values,target,top3)
                if z is not None: race_signals.append(z)
            signal=_mean(race_signals) if race_signals else 0.0
            reliability,delta=_calibration_strength(len(race_signals),prior_races,max_role_amplitude,signal)
            signals[factor]={
              "race_count":len(race_signals),"mean_separation_z":round(signal,6),
              "reliability":round(reliability,6),"raw_weight":round(1+delta,8)
            }
        denom=sum(x["raw_weight"] for x in signals.values()) or len(signals)
        weights={factor:signals[factor]["raw_weight"]/denom for factor in factors}
        role_profiles[role]={
          "factors":factors,
          "weights":{k:round(v,8) for k,v in weights.items()},
          "signals":signals,
          "baseline":"equal weights",
          "calibration_status":"RETROSPECTIVE_DAY_CALIBRATED_NON_OOS"
        }

    calibrated_registry=copy.deepcopy(reg)
    calibrated_registry["registry_id"]="LOCAL-EVIDENCE-FEATURE-RULE-REGISTRY-v0.2-CANDIDATE-20260923-URW-DAY-CALIBRATED"
    calibrated_registry["predecessor"]=reg.get("registry_id")
    calibrated_registry["status"]="CANDIDATE / RETROSPECTIVE-DAY-CALIBRATED / NON-PRODUCTION / NON-OOS / SHRUNK / OOS-REQUIRED"
    calibrated_registry["common_component_sets"]=calibrated_sets
    calibrated_registry["calibration_metadata"]={
      "profile":PROFILE,"race_labels":labels,"race_count":len(labels),
      "prior_races":prior_races,"max_component_amplitude":max_component_amplitude,
      "method":"within-race top3-vs-nontop3 standardized separation; position relevance 1.00/0.65/0.45; R30 shrinkage",
      "result_derived_weight_definition":True,
      "result_derived_feature_values":False,
      "oos_eligible":False,
      "automatic_production_promotion":False,
      "component_stats_sha256":_sha(component_stats),
    }

    calibrated_mapping=copy.deepcopy(mapping)
    calibrated_mapping["mapping_id"]="LOCAL-FULL-NUMERICAL-MAPPING-v0.2-CANDIDATE-20260923-URW-DAY-CALIBRATED"
    calibrated_mapping["predecessor"]=mapping.get("mapping_id")
    calibrated_mapping["status"]="CANDIDATE / RETROSPECTIVE-DAY-CALIBRATED / NON-PRODUCTION / NON-OOS / OOS-REQUIRED"
    calibrated_mapping["evidence_registry"]=calibrated_registry["registry_id"]
    calibrated_mapping["candidate_role_weights"]=role_profiles
    calibrated_mapping["calibration_metadata"]={
      "profile":PROFILE,"race_labels":labels,"race_count":len(labels),
      "prior_races":prior_races,"max_role_amplitude":max_role_amplitude,
      "method":"role-target vs non-top3 within-race standardized separation with R30 shrinkage",
      "exact_canon_formulas_changed":False,
      "recency_weights_changed":False,
      "neutral_missing_semantics_changed":False,
      "market_ability_separation_changed":False,
      "result_derived_weight_definition":True,
      "oos_eligible":False,
      "automatic_production_promotion":False,
    }

    ranked_changes=sorted(component_stats.values(),key=lambda x:abs(x["weight_change_pct"]),reverse=True)
    out={
      "profile":PROFILE,
      "status":"RETROSPECTIVE_CALIBRATION_COMPLETE / NON_PRODUCTION / NON_OOS / DUAL_SHADOW_REQUIRED",
      "race_labels":labels,
      "race_count":len(labels),
      "excluded_policy":"Only races with immutable pre-result Signed SOURCE artifacts may enter the calibration set.",
      "component_stats":component_stats,
      "largest_component_changes":ranked_changes[:20],
      "role_profiles":role_profiles,
      "calibrated_registry":calibrated_registry,
      "calibrated_mapping":calibrated_mapping,
      "safety":{
        "production_mutation":False,
        "exact_canon_formula_change":False,
        "recency_weight_change":False,
        "market_into_ability":False,
        "unknown_semantics_change":False,
        "same_race_prediction_rewrite":False,
        "automatic_promotion":False,
      },
      "next_gate":"Freeze v0.1 and v0.2 before future unknown races; compare OOS until R30 then human review."
    }
    out["sha256"]=_sha({k:v for k,v in out.items() if k!="sha256"})
    return out


def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("pre_result_json")
    p.add_argument("outcomes_json")
    p.add_argument("--out-dir",required=True)
    p.add_argument("--registry",default=DEFAULT_REGISTRY)
    p.add_argument("--mapping",default=DEFAULT_MAPPING)
    a=p.parse_args()
    pre=_load(a.pre_result_json); outcomes=_load(a.outcomes_json)
    result=calibrate(pre,outcomes,a.registry,a.mapping)
    out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
    (out/"calibration_report.json").write_text(json.dumps({k:v for k,v in result.items() if k not in {"calibrated_registry","calibrated_mapping"}},ensure_ascii=False,indent=2,sort_keys=True),encoding="utf-8")
    (out/"local_evidence_feature_rule_registry_v0.2_candidate_20260923_urw_day_calibrated.json").write_text(json.dumps(result["calibrated_registry"],ensure_ascii=False,indent=2,sort_keys=True),encoding="utf-8")
    (out/"local_full_numerical_mapping_v0.2_candidate_20260923_urw_day_calibrated.json").write_text(json.dumps(result["calibrated_mapping"],ensure_ascii=False,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({
      "profile":result["profile"],"status":result["status"],"race_count":result["race_count"],
      "sha256":result["sha256"],"largest_component_changes":result["largest_component_changes"][:10],
      "role_weights":{k:v["weights"] for k,v in result["role_profiles"].items()}
    },ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
