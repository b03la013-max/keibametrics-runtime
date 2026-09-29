from __future__ import annotations
import copy, hashlib, json
from local_nar_evidence_candidate import compile_candidate_evidence
from local_fullnumerical_candidate import materialize_candidate
from local_krs_bridge_candidate import build_candidate_krs

PROFILE="KM-LOCAL-SOURCE-DERIVED-KRS-TECHNICAL-PROXY-v1.0-20260929"

class LocalSourceDerivedProxyError(ValueError):
    pass

def _sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def build(request, source_artifact):
    if not isinstance(source_artifact,dict) or source_artifact.get("formal_ready") is not True:
        raise LocalSourceDerivedProxyError("SIGNED_SOURCE_FORMAL_READY_REQUIRED")
    source_sha=str(source_artifact.get("source_snapshot_sha256") or "").strip()
    if not source_sha:
        raise LocalSourceDerivedProxyError("SOURCE_SNAPSHOT_SHA_REQUIRED")
    q=compile_candidate_evidence(source_artifact,copy.deepcopy(request))
    q=materialize_candidate(q)
    q=build_candidate_krs(q)
    cand=q.get("candidate_local_krs_bridge") or {}
    rows=cand.get("runners") or {}
    request_ids={str(r.get("runner_id")) for r in (request.get("runners") or [])}
    if set(rows)!=request_ids:
        raise LocalSourceDerivedProxyError("SOURCE_DERIVED_PROXY_RUNNER_UNIVERSE_MISMATCH")
    out_rows={}
    for rid,b in rows.items():
        prov=copy.deepcopy(b.get("provenance") or {})
        for key,p in prov.items():
            p["technical_proxy_diagnostic"]=True
            p["production_authority"]=False
            p["source_snapshot_sha256"]=source_sha
            p["upstream_candidate_profile"]=cand.get("profile")
        out_rows[rid]={
            "hsv":copy.deepcopy(b["hsv"]),
            "static":copy.deepcopy(b["static"]),
            "provenance":prov,
            # production bridge normalizes this field by /50. Preserve the
            # candidate bridge's 1.x uncertainty scale without changing KRS physics.
            "uncertainty_scale":min(100.0,max(0.0,float(b.get("uncertainty_scale",1.0))*50.0)),
            "evidence":{
                **copy.deepcopy(b.get("evidence") or {}),
                "authority":"TECHNICAL_PROXY_DIAGNOSTIC_ONLY",
                "production_authority":False,
                "source_snapshot_sha256":source_sha,
                "source_derived":True,
            },
        }
    bridge={
        "bridge_id":PROFILE+":"+source_sha[:16],
        "profile":PROFILE,
        "family":"LOCAL",
        "technical_proxy_mode":True,
        "proxy_reason":"Production numerical authority is NOT_READY. Values are derived from the verified race SOURCE through the existing unvalidated candidate evidence/mapping path solely to keep KRS transport diagnostic and provenance-bearing; they have zero Production numerical or prediction authority.",
        "production_authority":False,
        "source_derived":True,
        "source_snapshot_sha256":source_sha,
        "upstream_candidate_bridge_profile":cand.get("profile"),
        "upstream_candidate_mapping":(q.get("candidate_full_numerical_summary") or {}).get("mapping_id"),
        "runners":out_rows,
    }
    bridge["sha256"]=_sha(bridge)
    return bridge
