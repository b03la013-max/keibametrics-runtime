import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))

from jra_index_provenance_builder import materialize_index_provenance,BASE,DCR_COMPONENT_MAX

def _base_spec(index):
    return {
        "value":80.0,
        "rule_id":f"RULE-{index}",
        "mapping_version":"MAP-v1",
        "evidence_refs":[f"E-{index}"],
        "source_fact":f"fact-{index}",
        "coverage_weight":0.8,
        "components":[{
            "feature":"recent_performance",
            "weight":0.2,
            "feature_rule_id":"FEATURE-RULE-v1",
            "category":"STRONG",
            "category_score":85.0,
            "weighted_contribution":17.0,
            "evidence_refs":["SRC-HIST"],
            "source_fact":"recent performance fact"
        }]
    }

def test_index_provenance_replay_preserves_feature_contributions_and_static_rank():
    dcr_components={}
    for name,maximum in DCR_COMPONENT_MAX.items():
        points=min(5.0,float(maximum))
        dcr_components[name]={
            "points":points,
            "evidence_refs":[f"DCR-{name}"],
            "source_fact":f"dcr fact {name}",
            "rule_id":f"DCR-RULE-{name}"
        }
    dcr_score=sum(x["points"] for x in dcr_components.values())
    req={
        "runners":[{"runner_id":"1","name":"A"}],
        "static_prediction":{"ranking":["1"],"roles":{"W":["1"],"P2":[],"P3":[]}},
        "index_provenance_ledger":{
            "formula_registry":"index_formula_registry JRA v1.0",
            "runners":{
                "1":{
                    "base_indices":{idx:_base_spec(idx) for idx in BASE},
                    "dcr":{"score":dcr_score,"components":dcr_components},
                    "weak_penalty_major_indices":["HPI","SSI"],
                    "scenario_fit":{"value":80.0,"evidence_refs":["SCENARIO"]}
                }
            }
        }
    }
    out=materialize_index_provenance(req)
    replay=out["index_provenance_replay"]
    assert replay["trace_schema"]=="KM-JRA-SOURCE-FEATURE-INDEX-STATIC-TRACE-v1.0-20260927"
    rr=replay["runners"]["1"]
    assert rr["static_rank"]==1
    assert rr["static_roles"]==["W"]
    assert rr["source_to_index_trace_complete"] is True
    assert rr["base_index_trace"]["HPI"]["components"][0]["feature"]=="recent_performance"
    assert rr["base_index_trace"]["HPI"]["components"][0]["weighted_contribution"]==17.0
    assert rr["derived_index_trace"]["TPI"]["value"]==rr["tpi_final"]
    assert replay["trace_complete_runner_count"]==1
    assert replay["trace_incomplete_runner_count"]==0
    assert out["index_provenance_hash"]==replay["sha256"]
