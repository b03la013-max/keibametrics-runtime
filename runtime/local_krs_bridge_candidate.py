from __future__ import annotations

import copy
import hashlib
import json
import math
from typing import Any, Dict, Iterable, List

PROFILE = "KM-LOCAL-KRS-HSV-BRIDGE-v0.1-CANDIDATE-20260923"

HSV_KEYS=[
"base_competitive_ability","class_strength","condition_fit","distance_fit","surface_fit",
"gate_reliability","initial_acceleration","position_intent","inside_cut_ability",
"outside_press_ability","leader_need","stalk_acceptance","crowd_tolerance",
"early_position_hold","midrace_hold","progression_ceiling","progression_timing",
"corner_acceleration","traffic_escape","sustained_speed","pressure_tolerance",
"front_friction_tolerance","long_move_tolerance","final_reserve","deceleration_risk",
"training_state","bodyweight_state","layoff_uncertainty","comment_state","data_confidence"
]
STATIC_KEYS=["tpi","zai_win","zai_place","sri","t3i","f3s","w_aki","p2_aki","p3_aki","asi","rsi"]


class LocalCandidateBridgeError(ValueError):
    pass


def _sha(x: Any) -> str:
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def _clamp(x: float) -> float:
    return max(0.0,min(100.0,float(x)))


def _mean(*xs: float) -> float:
    return sum(float(x) for x in xs)/len(xs)


def _idx(runner: Dict[str,Any], name: str) -> Dict[str,Any]:
    x=(runner.get("canonical_components") or {}).get(name)
    if not isinstance(x,dict):
        raise LocalCandidateBridgeError(f"INDEX_MISSING:{runner.get('runner_id')}:{name}")
    v=x.get("value")
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(float(v)):
        raise LocalCandidateBridgeError(f"INDEX_INVALID:{runner.get('runner_id')}:{name}:{v}")
    return x


def _feat(runner: Dict[str,Any], name: str) -> Dict[str,Any]:
    x=(runner.get("evidence_features") or {}).get(name)
    if not isinstance(x,dict) or not isinstance(x.get("score"),(int,float)):
        raise LocalCandidateBridgeError(f"FEATURE_MISSING:{runner.get('runner_id')}:{name}")
    return x


def _refs(items: Iterable[Dict[str,Any]]) -> List[str]:
    out=[]
    for x in items:
        out.extend(x.get("evidence_refs") or [])
    return sorted(set(str(z) for z in out if z))


def _prov(rule_id: str, sources: List[Dict[str,Any]], fact: str) -> Dict[str,Any]:
    return {
        "rule_id":rule_id,
        "evidence_refs":_refs(sources),
        "source_fact":fact,
        "bridge_profile":PROFILE,
        "candidate_only":True,
        "production_authority":False,
    }


def build_runner_bridge(runner: Dict[str,Any]) -> Dict[str,Any]:
    cc=runner.get("canonical_components") or {}
    observed_only=str(runner.get("candidate_missing_policy") or "").upper()=="OBSERVED_ONLY_RENORMALIZE"
    def v(name): return float(_idx(runner,name)["value"])
    def f(name): return float(_feat(runner,name)["score"])
    def isrc(*names): return [_idx(runner,n) for n in names]
    def fsrc(*names): return [_feat(runner,n) for n in names]
    def mean_idx(*names):
        if not observed_only:
            return _mean(*[v(n) for n in names])
        vals=[v(n) for n in names if float(_idx(runner,n).get("missingness_fraction",0.0)) < 1.0]
        return 52.0 if not vals else _mean(*vals)
    def mean_feat(*names):
        if not observed_only:
            return _mean(*[f(n) for n in names])
        vals=[f(n) for n in names if not bool(_feat(runner,n).get("missing"))]
        return 52.0 if not vals else _mean(*vals)

    values={}
    provenance={}

    def put(name,value,sources,fact):
        values[name]=round(_clamp(value),6)
        provenance[name]=_prov(f"LOCAL-KRS-CAND-v0.1-{name}",sources,fact)

    put("base_competitive_ability",v("HPI-L"),isrc("HPI-L"),"HPI-L")
    put("class_strength",v("NCI"),isrc("NCI"),"NCI")
    put("condition_fit",mean_idx("CSI-L","CCI","TRI","BWI-L"),isrc("CSI-L","CCI","TRI","BWI-L"),"mean CSI/CCI/TRI/BWI")
    put("distance_fit",v("CFIg-L"),isrc("CFIg-L"),"CFIg-L")
    put("surface_fit",mean_idx("CFIg-L","EVI/CEV"),isrc("CFIg-L","EVI/CEV"),"mean CFI/EVI")
    put("gate_reliability",mean_idx("RFIg-L","DCR"),isrc("RFIg-L","DCR"),"mean RFI/DCR")
    put("initial_acceleration",f("position_acquisition"),fsrc("position_acquisition"),"position acquisition component")
    put("position_intent",mean_feat("position_acquisition","leadership_stalk_acceptance"),fsrc("position_acquisition","leadership_stalk_acceptance"),"mean acquisition/leadership")
    put("inside_cut_ability",mean_feat("draw_style_fit","position_acquisition"),fsrc("draw_style_fit","position_acquisition"),"draw-style + acquisition")
    put("outside_press_ability",mean_feat("third_corner_progression","position_maintenance"),fsrc("third_corner_progression","position_maintenance"),"progression + maintenance")
    put("leader_need",f("leadership_stalk_acceptance"),fsrc("leadership_stalk_acceptance"),"leadership/stalk component")
    put("stalk_acceptance",f("leadership_stalk_acceptance"),fsrc("leadership_stalk_acceptance"),"leadership/stalk component")
    put("crowd_tolerance",f("kickback_traffic_tolerance"),fsrc("kickback_traffic_tolerance"),"traffic tolerance component")
    put("early_position_hold",f("position_maintenance"),fsrc("position_maintenance"),"position maintenance component")
    put("midrace_hold",_mean(mean_idx("RFIg-L"),mean_feat("position_maintenance")),isrc("RFIg-L")+fsrc("position_maintenance"),"mean RFI/maintenance")
    put("progression_ceiling",mean_idx("HPI-L","RFIg-L"),isrc("HPI-L","RFIg-L"),"mean HPI/RFI")
    put("progression_timing",_mean(mean_idx("JTI-L"),mean_feat("third_corner_progression")),isrc("JTI-L")+fsrc("third_corner_progression"),"JTI + progression")
    put("corner_acceleration",f("third_corner_progression"),fsrc("third_corner_progression"),"third-corner progression")
    put("traffic_escape",mean_feat("kickback_traffic_tolerance","third_corner_progression"),fsrc("kickback_traffic_tolerance","third_corner_progression"),"traffic + progression")
    put("sustained_speed",mean_idx("HPI-L","RFIg-L","CFIg-L"),isrc("HPI-L","RFIg-L","CFIg-L"),"mean HPI/RFI/CFI")
    put("pressure_tolerance",mean_idx("RFIg-L","NCI"),isrc("RFIg-L","NCI"),"mean RFI/NCI")
    put("front_friction_tolerance",mean_idx("RFIg-L","EVI/CEV"),isrc("RFIg-L","EVI/CEV"),"mean RFI/EVI")
    put("long_move_tolerance",mean_idx("RFIg-L","HPI-L","CFIg-L"),isrc("RFIg-L","HPI-L","CFIg-L"),"mean RFI/HPI/CFI")
    put("final_reserve",mean_idx("HPI-L","TRI","RFIg-L"),isrc("HPI-L","TRI","RFIg-L"),"mean HPI/TRI/RFI")
    put("deceleration_risk",100-mean_idx("RFIg-L","EVI/CEV","BWI-L"),isrc("RFIg-L","EVI/CEV","BWI-L"),"100-mean RFI/EVI/BWI; risk polarity")
    put("training_state",v("TRI"),isrc("TRI"),"TRI")
    put("bodyweight_state",v("BWI-L"),isrc("BWI-L"),"BWI-L")
    put("layoff_uncertainty",100-v("DCR"),isrc("DCR"),"100-DCR")
    put("comment_state",v("CCI"),isrc("CCI"),"CCI")
    put("data_confidence",v("DCR"),isrc("DCR"),"DCR")

    static={
      "tpi":v("TPI-L"),"zai_win":v("ZAI-WIN"),"zai_place":v("ZAI-PLACE"),
      "sri":v("SRI-L"),"t3i":v("T3I-L"),"f3s":v("F3S-L"),
      "w_aki":v("W-AKI"),"p2_aki":v("P2-AKI"),"p3_aki":v("P3-AKI"),
      "asi":v("ASI"),"rsi":v("RSI"),
    }
    static_prov={}
    static_map={"tpi":"TPI-L","zai_win":"ZAI-WIN","zai_place":"ZAI-PLACE","sri":"SRI-L",
                "t3i":"T3I-L","f3s":"F3S-L","w_aki":"W-AKI","p2_aki":"P2-AKI",
                "p3_aki":"P3-AKI","asi":"ASI","rsi":"RSI"}
    for k,idx in static_map.items():
        static_prov[k]=_prov(f"LOCAL-KRS-CAND-v0.1-static-{k}",[_idx(runner,idx)],idx)

    return {
      "hsv":values,
      "static":{k:round(_clamp(vv),6) for k,vv in static.items()},
      "provenance":{**provenance,**static_prov},
      "uncertainty_scale":round(1.0+max(0.0,70-v("DCR"))/100.0,6),
      "evidence":{
        "candidate_index_sha256":runner.get("candidate_index_sha256"),
        "candidate_evidence_sha256":runner.get("candidate_evidence_sha256"),
        "real_component_coverage_ratio":runner.get("candidate_feature_coverage_ratio"),
      }
    }


def build_candidate_krs(request: Dict[str,Any]) -> Dict[str,Any]:
    q=copy.deepcopy(request)
    summary=q.get("candidate_full_numerical_summary") or {}
    if summary.get("full_numerical_complete") is not True:
        raise LocalCandidateBridgeError("CANDIDATE_FULL_NUMERICAL_REQUIRED")
    runners=q.get("runners") or []
    bridge_runners={}
    horses=[]
    for r in runners:
        rid=str(r.get("runner_id"))
        b=build_runner_bridge(r)
        bridge_runners[rid]=b
        horses.append({
          "horse_no":int(rid),"name":str(r.get("name") or ""),
          "hsv":copy.deepcopy(b["hsv"]),"static":copy.deepcopy(b["static"]),
          "static_roles":copy.deepcopy(r.get("candidate_static_roles") or []),
          "uncertainty_scale":b["uncertainty_scale"],
          "evidence":copy.deepcopy(b["evidence"]),
        })
    race=copy.deepcopy(q.get("race") or {})
    current_state=q.get("candidate_current_state") or {}
    if current_state.get("official_going"):
        race["going"]=current_state["official_going"]
    if current_state.get("official_weather"):
        race["weather"]=current_state["official_weather"]
    q["candidate_local_krs_bridge"]={
      "profile":PROFILE,"family":"LOCAL","production_authority":False,
      "candidate_only":True,"runners":bridge_runners,
    }
    q["candidate_local_krs_bridge"]["sha256"]=_sha(q["candidate_local_krs_bridge"])
    q["candidate_krs_input_data"]={
      "race":race,
      "environment":copy.deepcopy(q.get("candidate_environment") or {}),
      "horses":horses,
      "simulation":{"run_count":int(q.get("run_count",5000)),"master_seed":int(q.get("seed",1))},
      "keibametrics_input_authority":{
        "input_mode":"FULL_NUMERICAL_CANDIDATE_SHADOW",
        "production_authority":False,
        "candidate_mapping":summary.get("mapping_id"),
        "candidate_summary_sha256":summary.get("sha256"),
        "bridge_profile":PROFILE,
      }
    }
    q["candidate_krs_input_sha256"]=_sha(q["candidate_krs_input_data"])
    return q


def build_candidate_prediction(request: Dict[str,Any]) -> Dict[str,Any]:
    q=copy.deepcopy(request)
    runners=q.get("runners") or []
    if not runners:
        raise LocalCandidateBridgeError("RUNNERS_REQUIRED")
    rows=[]
    role_profile=q.get("candidate_role_weight_profile") or {}
    def role_score(cc,role,baseline):
        prof=role_profile.get(role) if isinstance(role_profile,dict) else None
        weights=(prof or {}).get("weights") if isinstance(prof,dict) else None
        if not isinstance(weights,dict) or not weights:
            return _mean(*baseline), {"mode":"EQUAL_BASELINE","weights":None}
        def factor_value(name):
            if str(name).startswith("INV:"):
                return 100-float(cc[str(name)[4:]]["value"])
            return float(cc[str(name)]["value"])
        denom=sum(float(x) for x in weights.values())
        if denom<=0:
            return _mean(*baseline), {"mode":"EQUAL_BASELINE_BAD_PROFILE","weights":weights}
        val=sum(factor_value(name)*float(weight) for name,weight in weights.items())/denom
        return val, {"mode":"CALIBRATED_ROLE_WEIGHTS","weights":weights}
    for r in runners:
        cc=r.get("canonical_components") or {}
        def v(n): return float(cc[n]["value"])
        w,wmeta=role_score(cc,"W",[v("ZAI-WIN"),v("SRI-L"),v("WCI"),v("ASI"),100-v("W-AKI")])
        p2,p2meta=role_score(cc,"P2",[v("ZAI-PLACE"),v("SRI-L"),v("F3S-L"),v("ASI"),100-v("P2-AKI")])
        p3,p3meta=role_score(cc,"P3",[v("T3I-L"),v("F3S-L"),v("ZAI-PLACE"),v("ASI"),100-v("P3-AKI")])
        overall=_mean(w,p2,p3)
        rows.append({"runner_id":str(r["runner_id"]),"name":r.get("name"),"w_score":w,"p2_score":p2,"p3_score":p3,"overall":overall,
                     "role_weight_modes":{"W":wmeta,"P2":p2meta,"P3":p3meta}})
    ranking=[x["runner_id"] for x in sorted(rows,key=lambda x:(-x["overall"],int(x["runner_id"])))]
    n=len(rows)
    # Widths are candidate-only and deliberately broad until OOS calibration.
    import math as _math
    nw=max(2,_math.ceil(n*0.40)); np2=max(nw,_math.ceil(n*0.67)); np3=max(np2,_math.ceil(n*0.85))
    W=ranking[:nw]; P2=ranking[:np2]; P3=ranking[:np3]
    role_map={}
    for rid in ranking:
        rr=[]
        if rid in W: rr.append("W")
        if rid in P2: rr.append("P2")
        if rid in P3: rr.append("P3")
        role_map[rid]=rr
    for r in q.get("runners") or []:
        r["candidate_static_roles"]=role_map.get(str(r.get("runner_id")),[])
    mapping_id=str((q.get("candidate_full_numerical_summary") or {}).get("mapping_id") or "")
    if "v0.3" in mapping_id:
        prediction_profile="KM-LOCAL-NUMERICAL-STATIC-PREDICTION-v0.3-EVIDENCE-ROUTING-20260925"
    elif role_profile:
        prediction_profile="KM-LOCAL-NUMERICAL-STATIC-PREDICTION-v0.2-CALIBRATED"
    else:
        prediction_profile="KM-LOCAL-NUMERICAL-STATIC-PREDICTION-v0.1-CANDIDATE-20260923"
    q["candidate_static_prediction"]={
      "profile":prediction_profile,
      "production_authority":False,
      "ranking":ranking,"W":W,"P2":P2,"P3":P3,
      "role_width_policy":{"W":"top 40%","P2":"top 67%","P3":"top 85%","status":"UNVALIDATED_CANDIDATE"},
      "runner_scores":rows,
      "roles":role_map,
      "role_weight_profile_sha256":q.get("candidate_role_weight_profile_sha256"),
      "note":"Role widths remain unvalidated. Calibrated role weights, when present, are retrospective non-OOS and never overwrite Production prediction."
    }
    q["candidate_static_prediction"]["sha256"]=_sha(q["candidate_static_prediction"])
    return q
