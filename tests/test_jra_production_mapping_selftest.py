import json, os, sys, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(HERE/"runtime"))
from jra_evidence_to_base_production import load_mapping, attach_production_ledger_to_request
from jra_index_provenance_builder import materialize_index_provenance

M=load_mapping(HERE/"mapping"/"jra_base_index_evidence_mapping_v1.0_20260921.json")
cats=["STRONG","POSITIVE","NEUTRAL"]
all_features=set()
for p in M["index_profiles"].values():
    for w in p.values(): all_features.update(w)
for d in M["dcr"].values():
    if d.get("feature"): all_features.add(d["feature"])
    if d.get("newcomer_fallback_feature"): all_features.add(d["newcomer_fallback_feature"])

def features(tag, cat):
    return {k:{"category":cat,"evidence_refs":[f"{tag}:{k}"],"source_fact":f"synthetic pre-race fact {k}","rule_id":f"TEST-{k}-v1"} for k in all_features}

runners=[
 {"runner_id":"1","name":"EST","career_starts":12,"evidence_features":features("E","STRONG"),
  "dcr_inputs":{"official_recent":{"points":23,"evidence_refs":["E:recent"],"source_fact":"12 starts","rule_id":"TEST-DCR-RECENT"},
                "same_course_distance":{"points":18,"evidence_refs":["E:course"],"source_fact":"course history","rule_id":"TEST-DCR-COURSE"}}},
 {"runner_id":"2","name":"LOW","career_starts":2,"evidence_features":features("L","POSITIVE"),
  "dcr_inputs":{"official_recent":{"points":15,"evidence_refs":["L:recent"],"source_fact":"2 starts","rule_id":"TEST-DCR-RECENT"},
                "same_course_distance":{"points":8,"evidence_refs":["L:course"],"source_fact":"limited course history","rule_id":"TEST-DCR-COURSE"}}},
 {"runner_id":"3","name":"NEW","career_starts":0,"newcomer":True,"evidence_features":features("N","NEUTRAL")}
]
req={"race_id":"KM-SELFTEST-JRA-PROD-MAP-R1","runners":runners}
req=attach_production_ledger_to_request(req,M)
req=materialize_index_provenance(req)
assert req["numeric_calculation_requirement"]=="FULL_REQUIRED"
assert len(req["runners"])==3
for r in req["runners"]:
    cc=r["canonical_components"]
    assert len(cc)==20, (r["runner_id"],len(cc))
    for k,v in cc.items():
        assert isinstance(v["value"],(int,float)), (r["runner_id"],k)
        assert 0 <= v["value"] <= 100, (r["runner_id"],k,v["value"])
        assert v["evidence_refs"], (r["runner_id"],k)
        assert v["rule_id"] and v["mapping_version"] and v["source_fact"]
print(json.dumps({"status":"PASS","mapping_id":M["mapping_id"],"profiles":[req["index_provenance_ledger"]["runners"][x]["profile"] for x in ["1","2","3"]],"runner_count":3,"required_count":60,"calculated_count":60,"ruled_hold_count":0,"unresolved_count":0,"index_provenance_hash":req["index_provenance_hash"]},ensure_ascii=False))
