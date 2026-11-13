"""FNB R8: evidence-quality census from frozen full29 cell provenance.

Diagnostic only. RULED-NEUTRAL is missing/incomparable transport, NOT a
weakness score. No policy weight, calibration or Production consumer changes.
"""
from collections import Counter


def census(materialized):
    runners=materialized.get("runners") or []
    required=materialized.get("required_indices") or []
    if len(required)!=29 or len(set(required))!=29 or not runners:
        raise ValueError("FNB_FULL29_GRID_REQUIRED")
    indices={name:Counter() for name in required}
    missing=Counter()
    cells=0
    for horse in runners:
        cc=horse["canonical_components"]
        if set(cc)!=set(required):
            raise ValueError("FNB_INDEX_MANIFEST_MISMATCH")
        for name in required:
            spec=cc[name]
            terminal=spec.get("terminal_status")
            if terminal not in ("CALCULATED","RULED-NEUTRAL"):
                raise ValueError("FNB_NON_NUMERIC_CELL:" + name)
            indices[name][terminal]+=1
            cells+=1
            if terminal=="RULED-NEUTRAL":
                components=spec.get("components") or []
                if not components:
                    missing[name + "::NO_COMPONENT_OR_FULLY_UNKNOWN"]+=1
                for c in components:
                    if c.get("missing"):
                        missing[name+"::"+str(c.get("component","UNKNOWN"))]+=1
    totals=materialized.get("numeric_coverage") or {}
    neutral=sum(v["RULED-NEUTRAL"] for v in indices.values())
    calc=sum(v["CALCULATED"] for v in indices.values())
    if (cells!=totals.get("required_count") or
            neutral!=totals.get("ruled_neutral_count") or
            calc!=totals.get("calculated_count")):
        raise ValueError("FNB_NEUTRAL_CENSUS_COUNTER_MISMATCH")
    return {"status":"FNB_FULL29_NUMERIC_EVIDENCE_CENSUS",
            "runner_count":len(runners),"cells":cells,
            "calculated":calc,"ruled_neutral":neutral,
            "index_counts":{k:dict(v) for k,v in indices.items()},
            "neutral_component_counts":dict(sorted(missing.items())),
            "neutral_is_not_low_ability":True,
            "model_accuracy_verified":False,
            "source_to_feature_independently_verified":False}
