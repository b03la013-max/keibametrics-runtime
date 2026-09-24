from __future__ import annotations
import json

class FamilyRuntimeError(ValueError):
    pass

def load_contracts(path="profiles/family_runtime_contracts_20260924_R9.json"):
    with open(path,encoding="utf-8") as f:
        return json.load(f)

def resolve_family_runtime(request, contracts):
    fam=str(request.get("family_id") or "").upper()
    cfg=(contracts.get("families") or {}).get(fam)
    if not cfg:
        raise FamilyRuntimeError(f"UNKNOWN_FAMILY:{fam}")
    if fam=="JRA":
        return {"family":fam,"executable":True,"contract":cfg,"external_endpoint":cfg.get("external_endpoint"),"source":"CANONICAL_CONTRACT"}

    if fam=="LOCAL":
        endpoint=str(cfg.get("external_endpoint") or "").rstrip("/")
        required=["engine_sha256","parameter_map_sha256","signed_receipt_authority","runtime"]
        missing=[k for k in required if not str(cfg.get(k) or "").strip()]
        if not endpoint.startswith("https://"):
            raise FamilyRuntimeError("LOCAL_CANONICAL_EXTERNAL_ENDPOINT_INVALID")
        if missing:
            raise FamilyRuntimeError(f"LOCAL_CANONICAL_CONTRACT_INCOMPLETE:{missing}")
        return {
          "family":fam,
          "executable":True,
          "contract":cfg,
          "external_endpoint":endpoint,
          "source":"CANONICAL_VERIFIED_LOCAL_CONTRACT"
        }

    att=request.get("family_runtime_attestation")
    if not isinstance(att,dict):
        raise FamilyRuntimeError(f"{fam}_RUNTIME_ATTESTATION_MISSING")
    required=cfg.get("required_attestation") or []
    missing=[k for k in required if not str(att.get(k) or "").strip()]
    if missing:
        raise FamilyRuntimeError(f"{fam}_RUNTIME_ATTESTATION_INCOMPLETE:{missing}")
    if str(att.get("family") or fam).upper()!=fam:
        raise FamilyRuntimeError(f"{fam}_ATTESTATION_FAMILY_MISMATCH")

    if fam=="BAN":
        expected=str(cfg.get("parameter_numeric_fingerprint_sha256") or "")
        actual=str(att.get("parameter_map_sha256_or_fingerprint") or "")
        if expected and actual!=expected:
            raise FamilyRuntimeError(f"BAN_PARAMETER_FINGERPRINT_MISMATCH:{actual}!={expected}")

    endpoint=str(att.get("external_endpoint") or "").rstrip("/")
    if not endpoint.startswith("https://"):
        raise FamilyRuntimeError(f"{fam}_EXTERNAL_ENDPOINT_NOT_HTTPS")

    return {
      "family":fam,
      "executable":True,
      "contract":cfg,
      "runtime_attestation":att,
      "external_endpoint":endpoint,
      "source":"SIGNED_EXTERNAL_ATTESTATION_REQUIRED"
    }
