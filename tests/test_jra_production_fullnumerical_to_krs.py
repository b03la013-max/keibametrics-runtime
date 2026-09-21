import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(HERE/"runtime"))
from jra_evidence_to_base_production import load_mapping, attach_production_ledger_to_request
from jra_index_provenance_builder import materialize_index_provenance
from jra_krs_input_builder_production import build_krs_input

M=load_mapping(HERE/"mapping"/"jra_base_index_evidence_mapping_v1.0_20260921.json")
keys=set()
for p in M["index_profiles"].values():
    for w in p.values(): keys.update(w)
for d in M["dcr"].values():
    if d.get("feature"): keys.add(d["feature"])
    if d.get("newcomer_fallback_feature"): keys.add(d["newcomer_fallback_feature"])

def feats(tag,cat):
    return {k:{"category":cat,"evidence_refs":[f"{tag}:{k}"],"source_fact":f"pre-race {k}","rule_id":f"TEST-{k}-v1"} for k in keys}

runners=[
 {"runner_id":"1","name":"EST","career_starts":10,"evidence_features":feats("E","STRONG"),"dcr_inputs":{"official_recent":{"points":23,"evidence_refs":["E:r"],"source_fact":"10 starts","rule_id":"DCR-E-R"},"same_course_distance":{"points":18,"evidence_refs":["E:c"],"source_fact":"course history","rule_id":"DCR-E-C"}}},
 {"runner_id":"2","name":"LOW","career_starts":2,"evidence_features":feats("L","POSITIVE"),"dcr_inputs":{"official_recent":{"points":15,"evidence_refs":["L:r"],"source_fact":"2 starts","rule_id":"DCR-L-R"},"same_course_distance":{"points":8,"evidence_refs":["L:c"],"source_fact":"limited history","rule_id":"DCR-L-C"}}},
 {"runner_id":"3","name":"NEW","career_starts":0,"newcomer":True,"evidence_features":feats("N","NEUTRAL")}
]
req={
 "race_id":"KM-JRA-PROD-KRS-BRIDGE-SELFTEST",
 "venue_id":"HSN",
 "source_snapshot_sha256":"a"*64,
 "prediction_cutoff":"2026-09-21T14:00:00+09:00",
 "run_count":5000,
 "seed":20260921,
 "race":{"venue":"阪神","surface":"dirt","distance":1400,"course":"right","going":"good","class":"2win"},
 "environment":{"track":"dirt","weather":"cloudy","source_cutoff":"2026-09-21T14:00:00+09:00"},
 "runners":runners
}
req=attach_production_ledger_to_request(req,M)
req=materialize_index_provenance(req)
req=build_krs_input(req)
assert req["jra_adapter_mode"]=="EXPLICIT_ENGINE_HSV"
assert len(req["krs_input_data"]["horses"])==3
for h in req["krs_input_data"]["horses"]:
    assert len(h["hsv"])==30, len(h["hsv"])
    assert len(h["static"])==11, len(h["static"])
    assert all(0 <= float(v) <= 100 for v in h["hsv"].values())
    assert all(0 <= float(v) <= 100 for v in h["static"].values())
assert req["explicit_engine_hsv_provenance"]["mapping_authority"]=="JRA-KRS-HSV-BRIDGE-v1.0-PRODUCTION-20260921"
print("JRA_PRODUCTION_20_INDEX_TO_30HSV_11STATIC_PASS")
