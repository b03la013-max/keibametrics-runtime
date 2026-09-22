from __future__ import annotations
import copy, hashlib, json

class LocalProvenanceError(ValueError): pass

def _sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def build(req):
    out=copy.deepcopy(req)
    rows=[]
    for r in out.get("runners") or []:
        rid=str(r.get("runner_id"))
        cc=r.get("canonical_components")
        if not isinstance(cc,dict): raise LocalProvenanceError(f"CANONICAL_COMPONENTS_MISSING:{rid}")
        for name,spec in cc.items():
            for k in ("value","rule_id","mapping_version","evidence_refs","source_fact"):
                if k not in spec: raise LocalProvenanceError(f"PROVENANCE_FIELD_MISSING:{rid}:{name}:{k}")
            rows.append({"runner_id":rid,"index":name,**copy.deepcopy(spec)})
    ledger={"race_id":out.get("race_id"),"family":"LOCAL","rows":rows}
    ledger["sha256"]=_sha(ledger)
    out["index_provenance_ledger"]=ledger
    out["index_provenance_hash"]=ledger["sha256"]
    return out
