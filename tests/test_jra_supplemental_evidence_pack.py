import copy, hashlib, json, sys
sys.path.insert(0,"runtime")
from jra_supplemental_evidence_pack import apply_supplemental_evidence_pack, SupplementalEvidenceError

mapping=json.load(open("mapping/jra_base_index_evidence_mapping_v1.0_20260921.json",encoding="utf-8"))
req={
 "race_id":"TEST-JRA-1","prediction_cutoff":"2026-09-26T15:30:00+09:00",
 "runners":[{"runner_id":"1","name":"A","evidence_features":{}}]
}
pack={
 "profile":"KM-JRA-SUPPLEMENTAL-EVIDENCE-PACK-v1.0-20260926",
 "family_id":"JRA","race_id":"TEST-JRA-1","captured_at":"2026-09-26T15:20:00+09:00",
 "sources":[{
   "source_id":"S1","source_class":"AUTHORIZED_PRE_RACE_FACT","authority":"USER_PROVIDED_PRE_RACE",
   "origin":"https://example.invalid/pre-race","available_at":"2026-09-26T15:10:00+09:00",
   "ingested_at":"2026-09-26T15:20:00+09:00","content_sha256":"a"*64,
   "production_use":"FACT_ONLY","result_derived":False
 }],
 "runner_features":{"1":{"recent_consistency":{
   "category":"POSITIVE","rule_id":"JRA-RECENT-CONSISTENCY-RATE-v1",
   "evidence_refs":["SUPP:S1:runner:1"],"source_fact":"Top3 rate pre-race fact.","result_derived":False
 }}}
}
raw=json.dumps(pack,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
pack["pack_sha256"]=hashlib.sha256(raw).hexdigest()
out,att=apply_supplemental_evidence_pack(req,pack,mapping)
assert out["runners"][0]["evidence_features"]["recent_consistency"]["category"]=="POSITIVE"
assert att["feature_count"]==1 and att["new_rule_created"] is False

bad=copy.deepcopy(pack); bad["runner_features"]["1"]["recent_consistency"]["rule_id"]="UNREGISTERED"
m={k:v for k,v in bad.items() if k!="pack_sha256"}
bad["pack_sha256"]=hashlib.sha256(json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
try:
  apply_supplemental_evidence_pack(req,bad,mapping)
  raise AssertionError("must fail")
except SupplementalEvidenceError as e:
  assert "UNREGISTERED" in str(e)
print("JRA_SUPPLEMENTAL_EVIDENCE_PACK_PASS")
