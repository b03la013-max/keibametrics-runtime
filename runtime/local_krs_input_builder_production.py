from __future__ import annotations
import copy, hashlib, json
from math import isfinite

class LocalKRSBridgeError(ValueError): pass

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

def _sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def _valid(v,k):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not isfinite(float(v)) or not 0<=float(v)<=100:
        raise LocalKRSBridgeError(f"KRS_VALUE_INVALID:{k}:{v}")
    return round(float(v),6)

def build(req):
    q=copy.deepcopy(req)
    bridge=q.get("local_krs_bridge")
    if not isinstance(bridge,dict) or not bridge.get("bridge_id"):
        raise LocalKRSBridgeError("LOCAL_KRS_BRIDGE_ARTIFACT_REQUIRED")
    if str(bridge.get("family") or "").upper()!="LOCAL":
        raise LocalKRSBridgeError("LOCAL_KRS_BRIDGE_FAMILY_MISMATCH")
    runners=q.get("runners") or []
    horses=[]
    for r in runners:
        rid=str(r.get("runner_id"))
        per=(bridge.get("runners") or {}).get(rid)
        if not isinstance(per,dict): raise LocalKRSBridgeError(f"RUNNER_BRIDGE_MISSING:{rid}")
        hsv=per.get("hsv") or {}; static=per.get("static") or {}
        if set(hsv)!=set(HSV_KEYS): raise LocalKRSBridgeError(f"HSV_SCHEMA_MISMATCH:{rid}")
        if set(static)!=set(STATIC_KEYS): raise LocalKRSBridgeError(f"STATIC_SCHEMA_MISMATCH:{rid}")
        prov=per.get("provenance") or {}
        for key in list(HSV_KEYS)+list(STATIC_KEYS):
            if key not in prov or not str((prov[key] or {}).get("rule_id") or "") or not (prov[key] or {}).get("evidence_refs"):
                raise LocalKRSBridgeError(f"KRS_PROVENANCE_MISSING:{rid}:{key}")
        horses.append({
          "horse_no":int(rid),"name":str(r.get("name") or ""),
          "hsv":{k:_valid(v,k) for k,v in hsv.items()},
          "static":{k:_valid(v,k) for k,v in static.items()},
          "static_roles":copy.deepcopy(r.get("static_roles") or []),
          "uncertainty_scale":_valid(per.get("uncertainty_scale",50),"uncertainty_scale")/50.0,
          "evidence":copy.deepcopy(per.get("evidence") or {})
        })
    q["krs_input_data"]={
      "race":copy.deepcopy(q.get("race") or q.get("race_identity") or {}),
      "environment":copy.deepcopy(q.get("environment") or {}),
      "horses":horses,
      "simulation":{"run_count":int(q.get("run_count",5000)),"master_seed":int(q.get("seed",1))}
    }
    q["local_krs_bridge_id"]=bridge["bridge_id"]
    q["local_krs_input_sha256"]=_sha(q["krs_input_data"])
    return q
