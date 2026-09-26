import copy,sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))
from formal_request_validator import validate_production_authority, FormalValidationError

def production_req():
    return {
      "base_index_mapping_authority":{
        "mapping_id":"JRA-EVIDENCE-TO-BASE-MAPPING-v1.0-PRODUCTION-20260921",
        "status":"ACTIVE / PRODUCTION / NUMERICAL",
        "production_authority":True,
      },
      "runners":[
        {"runner_id":"1","canonical_components":{
          "HPI":{"value":70,"production_authority":True}
        }}
      ],
      "explicit_engine_hsv_provenance":{"production_authority":True},
      "static_prediction":{"production_authority":True},
      "role_registry":[{"runner_id":"1","column":"W","production_authority":True}],
      "pair_dispositions":[],
      "third_dispositions":[],
    }

def test_production_authority_accepts_production_only():
    out=validate_production_authority(production_req())
    assert out["production_authority_verified"] is True
    assert out["candidate_leakage_detected"] is False

@pytest.mark.parametrize("mutator,expected",[
  (lambda r:r["base_index_mapping_authority"].update({"production_authority":False}),"NON_PRODUCTION_NUMERICAL_AUTHORITY_FORBIDDEN"),
  (lambda r:r["base_index_mapping_authority"].update({"status":"CANDIDATE / NON-PRODUCTION"}),"NON_PRODUCTION_MAPPING_STATUS_FORBIDDEN"),
  (lambda r:r["runners"][0]["canonical_components"]["HPI"].update({"candidate_only":True,"production_authority":False}),"CANDIDATE_CANONICAL_COMPONENT_FORBIDDEN"),
  (lambda r:r["explicit_engine_hsv_provenance"].update({"candidate_only":True,"production_authority":False}),"CANDIDATE_HSV_PROVENANCE_FORBIDDEN"),
  (lambda r:r["static_prediction"].update({"production_authority":False}),"NON_PRODUCTION_STATIC_PREDICTION_FORBIDDEN"),
])
def test_production_authority_rejects_candidate_leakage(mutator,expected):
    req=production_req();mutator(req)
    with pytest.raises(FormalValidationError,match=expected):
        validate_production_authority(req)
