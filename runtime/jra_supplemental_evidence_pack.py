from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
import re
from typing import Any, Dict

PROFILE = "KM-JRA-SUPPLEMENTAL-EVIDENCE-PACK-v1.0-20260926"
HEX64 = re.compile(r"^[0-9a-f]{64}$")

class SupplementalEvidenceError(ValueError):
    pass

def _sha(x: Any) -> str:
    raw=json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def _time(x: Any) -> dt.datetime:
    try:
        return dt.datetime.fromisoformat(str(x).replace("Z","+00:00"))
    except Exception as exc:
        raise SupplementalEvidenceError("BAD_TIMESTAMP:"+str(x)) from exc

def _allowed_features(mapping: Dict[str,Any]):
    out=set()
    for profile in (mapping.get("index_profiles") or {}).values():
        for weights in profile.values():
            out.update(weights)
    for spec in (mapping.get("dcr") or {}).values():
        if spec.get("feature"): out.add(spec["feature"])
        if spec.get("newcomer_fallback_feature"): out.add(spec["newcomer_fallback_feature"])
    return out

def _load_registry(path="mapping/jra_evidence_feature_rule_registry_v1.1_20260922.json"):
    with open(path,encoding="utf-8") as f:
        x=json.load(f)
    if not isinstance(x.get("feature_rules"),dict):
        raise SupplementalEvidenceError("RULE_REGISTRY_INVALID")
    return x

def apply_supplemental_evidence_pack(request: Dict[str,Any], pack: Dict[str,Any], mapping: Dict[str,Any]):
    req=copy.deepcopy(request)
    if not isinstance(pack,dict):
        raise SupplementalEvidenceError("SUPPLEMENTAL_PACK_MISSING")
    if str(pack.get("profile")) != PROFILE:
        raise SupplementalEvidenceError("SUPPLEMENTAL_PROFILE_MISMATCH")
    if str(pack.get("family_id") or "JRA").upper()!="JRA":
        raise SupplementalEvidenceError("SUPPLEMENTAL_FAMILY_MISMATCH")
    if str(pack.get("race_id") or "") != str(req.get("race_id") or ""):
        raise SupplementalEvidenceError("SUPPLEMENTAL_RACE_ID_MISMATCH")

    declared=str(pack.get("pack_sha256") or "")
    material={k:v for k,v in pack.items() if k!="pack_sha256"}
    actual=_sha(material)
    if declared != actual:
        raise SupplementalEvidenceError(f"SUPPLEMENTAL_PACK_SHA_MISMATCH:{declared}!={actual}")

    cutoff=_time(req.get("prediction_cutoff"))
    captured=_time(pack.get("captured_at"))
    if captured > cutoff:
        raise SupplementalEvidenceError("SUPPLEMENTAL_CAPTURED_AFTER_PREDICTION_CUTOFF")

    sources=pack.get("sources")
    if not isinstance(sources,list) or not sources:
        raise SupplementalEvidenceError("SUPPLEMENTAL_SOURCES_MISSING")
    source_ids={}
    for s in sources:
        if not isinstance(s,dict):
            raise SupplementalEvidenceError("SUPPLEMENTAL_SOURCE_BAD")
        sid=str(s.get("source_id") or "").strip()
        if not sid or sid in source_ids:
            raise SupplementalEvidenceError("SUPPLEMENTAL_SOURCE_ID_BAD_OR_DUPLICATE:"+sid)
        authority=str(s.get("authority") or "").strip()
        source_class=str(s.get("source_class") or "").strip()
        origin=str(s.get("origin") or "").strip()
        digest=str(s.get("content_sha256") or "")
        if not authority or not source_class or not origin:
            raise SupplementalEvidenceError("SUPPLEMENTAL_SOURCE_LINEAGE_INCOMPLETE:"+sid)
        if not HEX64.fullmatch(digest):
            raise SupplementalEvidenceError("SUPPLEMENTAL_SOURCE_SHA_INVALID:"+sid)
        for tk in ("available_at","ingested_at"):
            t=_time(s.get(tk))
            if t > cutoff:
                raise SupplementalEvidenceError(f"SUPPLEMENTAL_SOURCE_POST_CUTOFF:{sid}:{tk}")
        if bool(s.get("result_derived")):
            raise SupplementalEvidenceError("SUPPLEMENTAL_RESULT_DERIVED_SOURCE_FORBIDDEN:"+sid)
        if str(s.get("production_use") or "").upper() not in {"ALLOWED","FACT_ONLY"}:
            raise SupplementalEvidenceError("SUPPLEMENTAL_SOURCE_NOT_PRODUCTION_AUTHORIZED:"+sid)
        source_ids[sid]=s

    runners=req.get("runners")
    if not isinstance(runners,list) or not runners:
        raise SupplementalEvidenceError("RUNNERS_MISSING")
    runner_by={str(r.get("runner_id")):r for r in runners}
    features_by=pack.get("runner_features")
    if not isinstance(features_by,dict):
        raise SupplementalEvidenceError("SUPPLEMENTAL_RUNNER_FEATURES_MISSING")
    if not set(features_by).issubset(set(runner_by)):
        raise SupplementalEvidenceError("SUPPLEMENTAL_RUNNER_UNIVERSE_MISMATCH")

    registry=_load_registry()
    feature_rules=registry["feature_rules"]
    allowed=_allowed_features(mapping)
    cats=set((mapping.get("category_scale") or {}).keys())
    feature_count=0
    refs_used=set()

    for rid,feats in features_by.items():
        if not isinstance(feats,dict):
            raise SupplementalEvidenceError("SUPPLEMENTAL_FEATURE_SET_BAD:"+rid)
        dst=runner_by[rid].setdefault("evidence_features",{})
        for name,spec in feats.items():
            if name not in allowed:
                raise SupplementalEvidenceError(f"SUPPLEMENTAL_FEATURE_NOT_IN_MAPPING:{rid}:{name}")
            if not isinstance(spec,dict):
                raise SupplementalEvidenceError(f"SUPPLEMENTAL_FEATURE_BAD:{rid}:{name}")
            cat=str(spec.get("category") or "").upper()
            rule=str(spec.get("rule_id") or "").strip()
            refs=spec.get("evidence_refs")
            fact=str(spec.get("source_fact") or "").strip()
            if cat not in cats:
                raise SupplementalEvidenceError(f"SUPPLEMENTAL_CATEGORY_BAD:{rid}:{name}:{cat}")
            if rule not in set(map(str,feature_rules.get(name) or [])):
                raise SupplementalEvidenceError(f"SUPPLEMENTAL_RULE_UNREGISTERED:{rid}:{name}:{rule}")
            if not isinstance(refs,list) or not refs:
                raise SupplementalEvidenceError(f"SUPPLEMENTAL_EVIDENCE_REFS_MISSING:{rid}:{name}")
            linked=False
            for ref in refs:
                rr=str(ref)
                if rr.startswith("SUPP:"):
                    parts=rr.split(":")
                    if len(parts)>=2 and parts[1] in source_ids:
                        linked=True
                        refs_used.add(parts[1])
            if not linked:
                raise SupplementalEvidenceError(f"SUPPLEMENTAL_FEATURE_SOURCE_NOT_LINKED:{rid}:{name}")
            if not fact:
                raise SupplementalEvidenceError(f"SUPPLEMENTAL_SOURCE_FACT_MISSING:{rid}:{name}")
            if bool(spec.get("result_derived")):
                raise SupplementalEvidenceError(f"SUPPLEMENTAL_RESULT_DERIVED_FEATURE_FORBIDDEN:{rid}:{name}")
            normalized={
              "category":cat,
              "rule_id":rule,
              "evidence_refs":sorted(set(map(str,refs))),
              "source_fact":fact,
              "result_derived":False,
              "supplemental_pack_sha256":actual
            }
            old=dst.get(name)
            if old is not None and old != normalized:
                raise SupplementalEvidenceError(f"SUPPLEMENTAL_FEATURE_CONFLICT:{rid}:{name}")
            dst[name]=normalized
            feature_count+=1

    attestation={
      "profile":PROFILE,
      "race_id":req.get("race_id"),
      "pack_sha256":actual,
      "source_count":len(source_ids),
      "source_ids":sorted(source_ids),
      "referenced_source_count":len(refs_used),
      "runner_count_with_supplement":len(features_by),
      "feature_count":feature_count,
      "prediction_cutoff":req.get("prediction_cutoff"),
      "captured_at":pack.get("captured_at"),
      "rule_registry_id":registry.get("registry_id"),
      "mapping_id":mapping.get("mapping_id"),
      "production_effect":"INPUT_PROVENANCE_AND_RULE_BINDING_ONLY",
      "new_rule_created":False,
      "new_weight_created":False,
      "result_derived":False
    }
    attestation["sha256"]=_sha(attestation)
    req["supplemental_evidence_pack_attestation"]=attestation
    return req,attestation
