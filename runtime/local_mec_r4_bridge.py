from __future__ import annotations

import copy, hashlib, json
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from mec_r4_shadow import build_mec_r4_shadow, settle_mec_r4_shadow

PROFILE="KM-LOCAL-MEC-R4-SIGNED-FINAL-BRIDGE-v1.0-20260924"


def _canon(x: Any) -> str:
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))


def sha_obj(x: Any) -> str:
    return hashlib.sha256(_canon(x).encode("utf-8")).hexdigest()


def _dt(s: Any):
    return datetime.fromisoformat(str(s).replace("Z","+00:00"))


def build_basis(req: Dict[str,Any], final_ticket: Dict[str,Any], mec: Dict[str,Any],
                final_prediction_package: Dict[str,Any]) -> Dict[str,Any]:
    rid=str(req.get("race_id") or "")
    if not rid:
        raise AssertionError("LOCAL_MEC_R4_RACE_ID_MISSING")
    basis={
        "race_id":rid,
        "scheduled_post_at":req.get("scheduled_post_at"),
        "temporal_mode":req.get("temporal_mode"),
        "minimum_efficient_coverage":copy.deepcopy(mec),
        "static_prediction":copy.deepcopy(req.get("static_prediction") or {}),
        "final_prediction_package":copy.deepcopy(final_prediction_package or {}),
        "third_dispositions":copy.deepcopy(req.get("third_dispositions") or []),
        "pair_dispositions":copy.deepcopy(req.get("pair_dispositions") or []),
        "final_ticket":copy.deepcopy(final_ticket or {}),
    }
    basis["sha256"]=sha_obj({k:v for k,v in basis.items() if k!="sha256"})
    return basis


def build_pre_result_shadow(req: Dict[str,Any], final_ticket: Dict[str,Any], mec: Dict[str,Any],
                            final_prediction_package: Dict[str,Any],
                            generated_at: str|None=None) -> Tuple[Dict[str,Any],Dict[str,Any]]:
    generated_at=generated_at or datetime.now(timezone.utc).isoformat()
    basis=build_basis(req,final_ticket,mec,final_prediction_package)
    shadow=build_mec_r4_shadow(basis,generated_at=generated_at)
    shadow["local_bridge_profile"]=PROFILE
    shadow["local_basis_sha256"]=basis["sha256"]
    shadow["temporal_class"]="FORMAL-PRE-RACE-SHADOW"
    shadow["oos_eligible_if_signed_final_bound"]=True
    shadow["production_effect"]="NONE"
    shadow["sha256"]=sha_obj({k:v for k,v in shadow.items() if k!="sha256"})
    return shadow,basis


def bind_shadow_to_trace(trace: Dict[str,Any], shadow: Dict[str,Any], basis: Dict[str,Any]) -> Dict[str,Any]:
    out=copy.deepcopy(trace or {})
    out["mec_r4_shadow_binding"]={
        "profile":shadow.get("profile"),
        "candidate_id":shadow.get("candidate_id"),
        "bridge_profile":PROFILE,
        "shadow_sha256":shadow.get("sha256"),
        "basis_sha256":basis.get("sha256"),
        "generated_at":shadow.get("generated_at"),
        "scheduled_post_at":shadow.get("scheduled_post_at"),
        "temporal_mode":shadow.get("temporal_mode"),
        "production_effect":"NONE",
    }
    return out


def verify_signed_final_binding(final_envelope: Dict[str,Any], shadow: Dict[str,Any]) -> Dict[str,Any]:
    receipt=final_envelope.get("receipt") or {}
    art=final_envelope.get("artifact") or {}
    if receipt.get("phase")!="FINAL" or receipt.get("status")!="PASS":
        raise AssertionError("LOCAL_MEC_R4_FINAL_RECEIPT_NOT_PASS")
    binding=(art.get("ticket_transport_trace") or {}).get("mec_r4_shadow_binding") or {}
    if binding.get("shadow_sha256")!=shadow.get("sha256"):
        raise AssertionError("LOCAL_MEC_R4_SHADOW_SHA_NOT_BOUND")
    if binding.get("basis_sha256")!=shadow.get("local_basis_sha256"):
        raise AssertionError("LOCAL_MEC_R4_BASIS_SHA_NOT_BOUND")
    if str(binding.get("production_effect"))!="NONE":
        raise AssertionError("LOCAL_MEC_R4_PRODUCTION_EFFECT_FORBIDDEN")
    if str(shadow.get("temporal_mode") or "").upper()!="FORMAL-PRE-RACE":
        raise AssertionError("LOCAL_MEC_R4_NOT_FORMAL_PRE_RACE")
    gen=_dt(shadow.get("generated_at"))
    post=_dt(shadow.get("scheduled_post_at"))
    if not gen < post:
        raise AssertionError("LOCAL_MEC_R4_SHADOW_NOT_PRE_RESULT")
    return {
        "profile":PROFILE,
        "valid":True,
        "race_id":shadow.get("race_id"),
        "shadow_sha256":shadow.get("sha256"),
        "basis_sha256":shadow.get("local_basis_sha256"),
        "final_receipt_sha256":final_envelope.get("receipt_sha256"),
        "final_artifact_sha256":receipt.get("artifact_sha256"),
        "generated_at":shadow.get("generated_at"),
        "scheduled_post_at":shadow.get("scheduled_post_at"),
        "temporal_mode":shadow.get("temporal_mode"),
        "production_effect":"NONE",
        "sha256":None,
    }


def build_replay_shadow(req: Dict[str,Any], final_envelope: Dict[str,Any], generated_at: str|None=None):
    art=final_envelope.get("artifact") or {}
    shadow,basis=build_pre_result_shadow(
        req,
        art.get("final_ticket") or {},
        art.get("minimum_efficient_coverage") or {},
        art.get("final_prediction_package") or {},
        generated_at=generated_at,
    )
    shadow["temporal_class"]="POST-RESULT-POLICY-FROZEN-REPLAY"
    shadow["oos_eligible_if_signed_final_bound"]=False
    shadow["retrospective_notice"]="MEC-R4 policy was preregistered before the race, but this concrete arm artifact was not frozen/bound before result; never count as forward OOS."
    shadow["source_signed_final_receipt_sha256"]=final_envelope.get("receipt_sha256")
    shadow["source_signed_final_artifact_sha256"]=(final_envelope.get("receipt") or {}).get("artifact_sha256")
    shadow["sha256"]=sha_obj({k:v for k,v in shadow.items() if k!="sha256"})
    return shadow,basis


def settle_replay(shadow: Dict[str,Any], result_request: Dict[str,Any]) -> Dict[str,Any]:
    result={
        "official_result":{
            "status":"OFFICIAL_OR_USER_SUPPLIED_OFFICIAL",
            "top3":[int(x) for x in (result_request.get("finish_order") or [])[:3]],
            "payouts_per_100_yen":{str(k).upper():int(v) for k,v in (result_request.get("payouts") or {}).items()},
        }
    }
    out=settle_mec_r4_shadow(shadow,result)
    out["temporal_class"]="POST-RESULT-POLICY-FROZEN-REPLAY"
    out["oos_eligible"]=False
    out["result_available_at"]=result_request.get("result_available_at")
    out["sha256"]=sha_obj({k:v for k,v in out.items() if k!="sha256"})
    return out
