from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from runtime.local_evidence_to_base_production import materialize_request, LocalMappingError
from runtime.local_index_provenance_builder import build as build_provenance

app=FastAPI(title="KeibaMetrics LOCAL Numerical Runtime",version="1.0.0")

@app.get("/health")
def health():
    return {
      "status":"READY",
      "family":"LOCAL",
      "profile":"KM-LOCAL-FULLPIPELINE-CORRECTNESS-HARDENING-20260922-R1",
      "mapping_registry":"LOCAL-BASE-INDEX-MAPPING-REGISTRY-v1.0-20260922",
      "mode":"FORMULA-PRESERVING / FAIL-CLOSED",
      "krs_authority":False
    }

@app.post("/calculate-local")
def calculate_local(payload: Dict[str,Any]):
    try:
        required=payload.get("required_indices")
        if not isinstance(required,list) or not required:
            raise LocalMappingError("REQUIRED_INDEX_MANIFEST_REQUIRED")
        out=materialize_request(payload,required)
        out=build_provenance(out)
        return {
          "status":"PASS" if out["full_numerical_calculation"] else "PARTIAL",
          "family":"LOCAL",
          "mapping_registry":out["local_mapping_registry"],
          "numeric_coverage":out["numeric_coverage"],
          "full_numerical_calculation":out["full_numerical_calculation"],
          "index_provenance_hash":out["index_provenance_hash"],
          "runners":out["runners"]
        }
    except (LocalMappingError,ValueError,TypeError) as e:
        raise HTTPException(status_code=422,detail=str(e))
