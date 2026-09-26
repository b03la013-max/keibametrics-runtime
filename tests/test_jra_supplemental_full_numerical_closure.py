import hashlib, json, sys
sys.path.insert(0,"runtime")
from jra_supplemental_evidence_pack import apply_supplemental_evidence_pack
from evidence_feature_compiler import compile_evidence_feature_ledger
from jra_evidence_to_base_production import load_mapping, build_production_ledger
from jra_index_provenance_builder import materialize_index_provenance

mapping=load_mapping("mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")
registry=json.load(open("mapping/jra_evidence_feature_rule_registry_v1.1_20260922.json",encoding="utf-8"))
allowed=set()
for profile in mapping["index_profiles"].values():
    for weights in profile.values(): allowed.update(weights)
for spec in mapping["dcr"].values():
    if spec.get("feature"): allowed.add(spec["feature"])
    if spec.get("newcomer_fallback_feature"): allowed.add(spec["newcomer_fallback_feature"])

runners=[{"runner_id":"1","name":"A","career_starts":10,"evidence_features":{}},
         {"runner_id":"2","name":"B","career_starts":10,"evidence_features":{}}]
req={"race_id":"TEST-JRA-FULL-NUM","prediction_cutoff":"2026-09-26T15:30:00+09:00","acceptance_only":True,"runners":runners}
features={}
for rid in ("1","2"):
    features[rid]={}
    for f in sorted(allowed):
        rule=registry["feature_rules"][f][0]
        features[rid][f]={
          "category":"NEUTRAL","rule_id":rule,
          "evidence_refs":["SUPP:SYNTH:"+rid+":"+f],
          "source_fact":"Synthetic mechanical acceptance fact for schema/numerical closure only.",
          "result_derived":False
        }
pack={
 "profile":"KM-JRA-SUPPLEMENTAL-EVIDENCE-PACK-v1.0-20260926",
 "family_id":"JRA","race_id":req["race_id"],"captured_at":"2026-09-26T15:20:00+09:00",
 "sources":[{
   "source_id":"SYNTH","source_class":"SYNTHETIC_ACCEPTANCE_ONLY","authority":"MECHANICAL_TEST",
   "origin":"repo:test_jra_supplemental_full_numerical_closure",
   "available_at":"2026-09-26T15:00:00+09:00","ingested_at":"2026-09-26T15:10:00+09:00",
   "content_sha256":"b"*64,"production_use":"FACT_ONLY","result_derived":False
 }],
 "runner_features":features
}
pack["pack_sha256"]=hashlib.sha256(json.dumps(pack,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
req,att=apply_supplemental_evidence_pack(req,pack,mapping)
ledger=compile_evidence_feature_ledger(req["race_id"],"c"*64,req["runners"],mapping)
prod=build_production_ledger(req["race_id"],req["runners"],mapping)
req["index_provenance_ledger"]=prod
req=materialize_index_provenance(req)
assert att["feature_count"]==len(allowed)*2
assert ledger["runner_count"]==2
assert req["numeric_calculation_requirement"]=="FULL_REQUIRED"
for r in req["runners"]:
    assert len(r["canonical_components"])==20
    assert all((x.get("value") is not None) for x in r["canonical_components"].values())
print("JRA_SUPPLEMENTAL_FULL_NUMERICAL_CLOSURE_PASS",len(allowed),att["feature_count"])
