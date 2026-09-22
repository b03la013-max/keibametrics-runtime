from __future__ import annotations
from math import isfinite

class LocalEvidenceError(ValueError):
    pass

REQUIRED_FIELDS=("score","rule_id","evidence_refs","source_fact","source_timestamp")

def feature(score, rule_id, evidence_refs, source_fact, source_timestamp):
    if isinstance(score,bool) or not isinstance(score,(int,float)) or not isfinite(float(score)) or not 0 <= float(score) <= 100:
        raise LocalEvidenceError(f"SCORE_NOT_0_100:{score}")
    if not str(rule_id).strip():
        raise LocalEvidenceError("RULE_ID_REQUIRED")
    if not isinstance(evidence_refs,list) or not evidence_refs:
        raise LocalEvidenceError("EVIDENCE_REFS_REQUIRED")
    if not str(source_fact).strip():
        raise LocalEvidenceError("SOURCE_FACT_REQUIRED")
    if not str(source_timestamp).strip():
        raise LocalEvidenceError("SOURCE_TIMESTAMP_REQUIRED")
    return {
        "score":round(float(score),6),
        "rule_id":str(rule_id),
        "evidence_refs":[str(x) for x in evidence_refs],
        "source_fact":str(source_fact),
        "source_timestamp":str(source_timestamp),
    }

def validate_feature(name, spec):
    if not isinstance(spec,dict):
        raise LocalEvidenceError(f"FEATURE_NOT_OBJECT:{name}")
    missing=[k for k in REQUIRED_FIELDS if k not in spec]
    if missing:
        raise LocalEvidenceError(f"FEATURE_FIELDS_MISSING:{name}:{missing}")
    return feature(spec["score"],spec["rule_id"],spec["evidence_refs"],spec["source_fact"],spec["source_timestamp"])
