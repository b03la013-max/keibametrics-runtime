import copy, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))
from jra_supplemental_evidence_pack import apply_supplemental_evidence_pack, SupplementalEvidenceError
from jra_evidence_to_base_production import load_mapping

def sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def pack():
    p={
      "profile":"KM-JRA-SUPPLEMENTAL-EVIDENCE-PACK-v1.0-20260926",
      "family_id":"JRA",
      "race_id":"R",
      "captured_at":"2026-09-26T10:00:00+09:00",
      "sources":[{
        "source_id":"SYN","source_class":"SYNTHETIC_ACCEPTANCE_ONLY","authority":"MECHANICAL_TEST",
        "origin":"acceptance://synthetic","content_sha256":"a"*64,
        "available_at":"2026-09-26T09:59:00+09:00","ingested_at":"2026-09-26T10:00:00+09:00",
        "production_use":"FACT_ONLY","result_derived":False
      }],
      "runner_features":{"1":{"weight_load_fit":{
        "category":"NEUTRAL","rule_id":"JRA-WEIGHT-EQUAL-CONDITION-v1",
        "evidence_refs":["SUPP:SYN:1"],"source_fact":"mechanical acceptance fact","result_derived":False
      }}}
    }
    p["pack_sha256"]=sha(p)
    return p

mapping=load_mapping(str(ROOT/"mapping"/"jra_base_index_evidence_mapping_v1.0_20260921.json"))
base={"race_id":"R","prediction_cutoff":"2026-09-26T10:01:00+09:00","runners":[{"runner_id":"1","evidence_features":{}}]}

try:
    apply_supplemental_evidence_pack(copy.deepcopy(base),pack(),mapping)
    raise AssertionError("production synthetic source unexpectedly accepted")
except SupplementalEvidenceError as e:
    assert "SUPPLEMENTAL_SYNTHETIC_SOURCE_FORBIDDEN_IN_PRODUCTION" in str(e)

acc=copy.deepcopy(base); acc["acceptance_only"]=True
out,att=apply_supplemental_evidence_pack(acc,pack(),mapping)
assert out["runners"][0]["evidence_features"]["weight_load_fit"]["category"]=="NEUTRAL"
assert att["feature_count"]==1
print("JRA_SUPPLEMENTAL_PRODUCTION_SOURCE_GATE_PASS")
