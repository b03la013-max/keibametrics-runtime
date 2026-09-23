from __future__ import annotations
import copy, hashlib, json

class LocalProvenanceError(ValueError): pass

TERMINAL_STATUSES={"CALCULATED","RULED-NEUTRAL","RULED-HOLD","NOT-APPLICABLE"}

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
            for k in ("terminal_status","rule_id","mapping_version","evidence_refs","source_fact"):
                if k not in spec: raise LocalProvenanceError(f"PROVENANCE_FIELD_MISSING:{rid}:{name}:{k}")
            status=str(spec.get("terminal_status") or "").upper()
            if status not in TERMINAL_STATUSES:
                raise LocalProvenanceError(f"TERMINAL_STATUS_INVALID:{rid}:{name}:{status}")
            if status in {"CALCULATED","RULED-NEUTRAL"} and "value" not in spec:
                raise LocalProvenanceError(f"NUMERIC_TERMINAL_VALUE_MISSING:{rid}:{name}")
            rows.append({"runner_id":rid,"index":name,**copy.deepcopy(spec)})
    ledger={
      "race_id":out.get("race_id"),"family":"LOCAL","rows":rows,
      "full_terminalization":bool(out.get("full_terminalization")),
      "full_numerical_calculation":bool(out.get("full_numerical_calculation")),
      "numeric_coverage":copy.deepcopy(out.get("numeric_coverage") or {})
    }
    ledger["sha256"]=_sha(ledger)
    out["index_provenance_ledger"]=ledger
    out["index_provenance_hash"]=ledger["sha256"]
    return out
