from __future__ import annotations
import hashlib, json

PROFILE="KM-JRA-EVIDENCE-FEATURE-COMPILER-v1.1-20260922"

class EvidenceCompilerError(ValueError):
    pass

def _sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

RULE_REGISTRY_PATH="mapping/jra_evidence_feature_rule_registry_v1.1_20260922.json"

def _load_rule_registry(path=RULE_REGISTRY_PATH):
    with open(path,encoding="utf-8") as f:
        x=json.load(f)
    rules=x.get("feature_rules")
    if not isinstance(rules,dict) or not rules:
        raise EvidenceCompilerError("FEATURE_RULE_REGISTRY_INVALID")
    return x

def _allowed_features(mapping):
    out=set()
    for profile in (mapping.get("index_profiles") or {}).values():
        for weights in profile.values():
            out.update(weights.keys())
    for spec in (mapping.get("dcr") or {}).values():
        if spec.get("feature"): out.add(spec["feature"])
        if spec.get("newcomer_fallback_feature"): out.add(spec["newcomer_fallback_feature"])
    return out

def _assert_registry_closure(mapping, rule_registry):
    required=_allowed_features(mapping)
    registered=set((rule_registry.get("feature_rules") or {}).keys())
    missing=sorted(required-registered)
    if missing:
        raise EvidenceCompilerError("FEATURE_RULE_REGISTRY_MAPPING_GAP:"+",".join(missing))
    contract=rule_registry.get("mapping_contract") or {}
    expected=contract.get("mapping_id")
    actual=mapping.get("mapping_id")
    if expected and expected!=actual:
        raise EvidenceCompilerError(f"FEATURE_RULE_REGISTRY_MAPPING_ID_MISMATCH:{expected}!={actual}")
    return {"required_count":len(required),"registered_count":len(registered),"missing":[]}

def compile_evidence_feature_ledger(race_id, source_snapshot_sha256, runners, mapping, rule_registry=None):
    if not race_id:
        raise EvidenceCompilerError("RACE_ID_MISSING")
    if not source_snapshot_sha256:
        raise EvidenceCompilerError("SOURCE_SNAPSHOT_SHA_MISSING")
    cats=set((mapping.get("category_scale") or {}).keys())
    allowed=_allowed_features(mapping)
    rr=rule_registry or _load_rule_registry()
    feature_rules=rr["feature_rules"]
    closure=_assert_registry_closure(mapping,rr)
    out={
      "profile":PROFILE,
      "race_id":str(race_id),
      "source_snapshot_sha256":str(source_snapshot_sha256),
      "mapping_id":mapping.get("mapping_id"),
      "rule_registry_id":rr.get("registry_id"),
      "classification_authority":"RULE_BOUND_CATEGORY",
      "registry_mapping_closure":closure,
      "freehand_numeric_score_allowed":False,
      "runners":{}
    }
    for r in runners or []:
        rid=str(r.get("runner_id") or "")
        if not rid: raise EvidenceCompilerError("RUNNER_ID_MISSING")
        feats=r.get("evidence_features")
        if not isinstance(feats,dict) or not feats:
            raise EvidenceCompilerError(f"EVIDENCE_FEATURES_MISSING:{rid}")
        norm={}
        for feature,x in sorted(feats.items()):
            if feature not in allowed:
                raise EvidenceCompilerError(f"FEATURE_NOT_IN_PRODUCTION_RULE_UNIVERSE:{rid}:{feature}")
            if not isinstance(x,dict):
                raise EvidenceCompilerError(f"FEATURE_NOT_OBJECT:{rid}:{feature}")
            cat=str(x.get("category") or "").upper()
            if cat not in cats:
                raise EvidenceCompilerError(f"BAD_CATEGORY:{rid}:{feature}:{cat}")
            refs=x.get("evidence_refs")
            fact=str(x.get("source_fact") or "").strip()
            rule=str(x.get("rule_id") or "").strip()
            allowed_rules=set(map(str,feature_rules.get(feature) or []))
            if not allowed_rules:
                raise EvidenceCompilerError(f"FEATURE_RULES_UNREGISTERED:{rid}:{feature}")
            if not isinstance(refs,list) or not refs or any(not str(z).strip() for z in refs):
                raise EvidenceCompilerError(f"EVIDENCE_REFS_MISSING:{rid}:{feature}")
            if not fact:
                raise EvidenceCompilerError(f"SOURCE_FACT_MISSING:{rid}:{feature}")
            if rule not in allowed_rules:
                raise EvidenceCompilerError(f"UNREGISTERED_RULE_ID:{rid}:{feature}:{rule}")
            if x.get("result_derived") is True:
                raise EvidenceCompilerError(f"RESULT_DERIVED_FEATURE_FORBIDDEN:{rid}:{feature}")
            norm[feature]={
              "category":cat,
              "rule_id":rule,
              "evidence_refs":sorted(set(str(z) for z in refs)),
              "source_fact":fact,
              "source_fact_sha256":hashlib.sha256(fact.encode()).hexdigest()
            }
        out["runners"][rid]={
          "feature_count":len(norm),
          "features":norm,
          "runner_feature_ledger_sha256":_sha(norm)
        }
    out["runner_count"]=len(out["runners"])
    out["sha256"]=_sha(out)
    return out

def verify_attestation(attestation, race_id, source_snapshot_sha256, runners, mapping):
    rebuilt=compile_evidence_feature_ledger(race_id,source_snapshot_sha256,runners,mapping)
    if not isinstance(attestation,dict):
        raise EvidenceCompilerError("ATTESTATION_MISSING")
    if str(attestation.get("sha256") or "")!=rebuilt["sha256"]:
        raise EvidenceCompilerError(f"ATTESTATION_SHA_MISMATCH:{attestation.get('sha256')}!={rebuilt['sha256']}")
    return rebuilt
