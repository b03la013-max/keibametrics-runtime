"""FNB R9: 63-component source-to-recorded-feature lineage audit.

Each horse's 63 existing deterministic component records are checked against
the frozen Registry, race, official card snapshot and pre-cutoff observation
time. THIS IS NOT AN INDEPENDENT REIMPLEMENTATION OF ALL 63 SOURCE->SCORE
TRANSFORMS. That separate empirical proof remains required for promotion.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import math

PROFILE="KM-FNB-R9-63-COMPONENT-RECORD-LINEAGE-v1"


def _time(value):
    try:
        t=datetime.fromisoformat(str(value).replace("Z","+00:00"))
    except (ValueError,TypeError) as exc:
        raise ValueError("EVIDENCE_TIMESTAMP_INVALID") from exc
    if t.tzinfo is None:
        raise ValueError("EVIDENCE_TIMESTAMP_NAIVE")
    return t.astimezone(timezone.utc)


def audit_63(materialized, registry, intent, source_artifact):
    issues=[]
    evidence={}
    def fail(code):
        issues.append(code)
    if not all(isinstance(x,dict) for x in
               (materialized,registry,intent,source_artifact)):
        return {"status":"FEATURE_LINEAGE_HOLD","issues":["INPUT_OBJECT_REQUIRED"],
                "recorded_components_verified":0,"independent_63_transforms":False}
    sets=registry.get("common_component_sets") or {}
    rules=registry.get("component_score_rules") or {}
    required=[(idx,comp) for idx,components in sets.items()
              for comp in (components if isinstance(components,dict) else {})]
    if (len(required)!=63 or len(set(comp for _,comp in required))!=63):
        fail("REGISTRY_63_DISTINCT_COMPONENTS_REQUIRED")
    if (intent.get("venue_id")!="FNB" or
            (source_artifact.get("source_race_context") or {}).get("venue_id")!="FNB" or
            source_artifact.get("race_id")!=intent.get("race_id")):
        fail("FNB_SOURCE_OR_INTENT_RACE_IDENTITY_INVALID")
    cutoff=None
    freeze=None
    try:
        cutoff=_time(intent["prediction_cutoff"])
        freeze=_time(source_artifact["source_freeze_at"])
        if not freeze < cutoff:
            fail("SOURCE_FREEZE_NOT_BEFORE_CUTOFF")
    except (ValueError,KeyError,TypeError) as exc:
        fail("SOURCE_TEMPORAL_LINEAGE_INVALID:"+str(exc))
    valid_cards=[x for x in source_artifact.get("sources",[]) if
                 isinstance(x,dict) and x.get("official") is True
                 and x.get("source_class")=="OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT"]
    if len(valid_cards)!=1:
        fail("ONE_OFFICIAL_FNB_CARD_REQUIRED")
        valid_card={}
    else:
        valid_card=valid_cards[0]
    known=(valid_card.get("source_id"),valid_card.get("snapshot_sha256"))
    rows=materialized.get("runners")
    rows=rows if isinstance(rows,list) else []
    expected=intent.get("runners")
    expected=expected if isinstance(expected,list) else []
    if (not rows or len(rows)!=len(expected) or
            len({str(r.get("runner_id")) for r in rows})!=len(rows) or
            {str(r.get("runner_id")) for r in rows}!=
            {str(r.get("runner_id")) for r in expected}):
        fail("FROZEN_ACTIVE_RUNNER_UNIVERSE_MISMATCH")
    counts=Counter()
    missing=Counter()
    for row in rows:
        rid=str(row.get("runner_id"))
        feats=row.get("evidence_features")
        if not isinstance(feats,dict):
            fail("FEATURE_MAP_MISSING:"+rid)
            continue
        if set(feats)!={name for _,name in required}:
            fail("FEATURE_63_SET_MISMATCH:"+rid)
        for idx,comp in required:
            key=f"{rid}:{idx}.{comp}"
            rule=(rules.get(idx) or {}).get(comp)
            rec=feats.get(comp)
            if not isinstance(rec,dict) or not isinstance(rule,dict):
                fail("RULE_OR_FEATURE_MISSING:"+key)
                continue
            value=rec.get("score")
            if (rec.get("rule_id")!=rule.get("rule_id") or
                    type(value) not in (int,float) or
                    not math.isfinite(value) or not 0<=value<=100 or
                    type(rec.get("missing")) is not bool or
                    not isinstance(rec.get("source_fact"),str) or
                    not rec["source_fact"].strip() or
                    type(rec.get("coverage")) not in (int,float) or
                    not 0<=rec["coverage"]<=1 or
                    not isinstance(rec.get("evidence_refs"),list) or
                    not all(x in rec["evidence_refs"] for x in known if x)):
                fail("FEATURE_RULE_VALUE_OR_PROVENANCE_INVALID:"+key)
                continue
            try:
                observed=_time(rec.get("source_timestamp"))
                if (freeze is not None and observed>freeze or
                        cutoff is not None and observed>=cutoff):
                    raise ValueError("FEATURE_OBSERVED_AFTER_SOURCE_FREEZE_OR_CUTOFF")
            except ValueError as exc:
                fail("FEATURE_TIME_INVALID:"+key+":"+str(exc))
                continue
            if rec["missing"] and abs(float(value)-52.0)>0.000001:
                fail("UNKNOWN_NEUTRAL_SCORE_NOT_52:"+key)
                continue
            counts[idx]+=1
            if rec["missing"]:
                missing[idx]+=1
    expected_cells=63*len(rows)
    verified=sum(counts.values())
    if verified!=expected_cells:
        fail("COMPONENT_63_COVERAGE_INCOMPLETE")
    return {"profile":PROFILE,
            "status":"ALL_63_COMPONENT_RECORDS_LINEAGE_VERIFIED" if not issues else
                     "FEATURE_LINEAGE_HOLD",
            "race_id":intent.get("race_id"),"runner_count":len(rows),
            "expected_component_records":expected_cells,
            "recorded_components_verified":verified,
            "verified_by_index":dict(counts),
            "missing_by_index":dict(missing),
            "missing_not_weak":True,
            "official_card_source_id":valid_card.get("source_id"),
            "official_card_snapshot_sha256":valid_card.get("snapshot_sha256"),
            "source_to_feature_transform_arithmetic_independently_verified":False,
            "external_receipt_signature_and_license_verified":False,
            "prediction_krs_ticket_capital_authorized":False,
            "registered_oos":False,
            "issues":issues[:80],
            "additional_issue_count":max(0,len(issues)-80)}
