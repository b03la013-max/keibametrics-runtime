import copy, json, sys
sys.path.insert(0, "runtime")
from evidence_feature_compiler import compile_evidence_feature_ledger, EvidenceCompilerError, PROFILE
from jra_evidence_to_base_production import load_mapping

MAPPING_PATH="mapping/jra_base_index_evidence_mapping_v1.0_20260921.json"
REGISTRY_PATH="mapping/jra_evidence_feature_rule_registry_v1.1_20260922.json"

mp=load_mapping(MAPPING_PATH)
rr=json.load(open(REGISTRY_PATH,encoding="utf-8"))

required=set()
for profile in mp["index_profiles"].values():
    for weights in profile.values():
        required.update(weights.keys())
for spec in mp.get("dcr",{}).values():
    if spec.get("feature"):
        required.add(spec["feature"])
    if spec.get("newcomer_fallback_feature"):
        required.add(spec["newcomer_fallback_feature"])

registered=set(rr["feature_rules"])
missing=sorted(required-registered)
assert len(required)==71, len(required)
assert len(registered)==71, len(registered)
assert missing==[], missing
assert rr["mapping_contract"]["mapping_id"]==mp["mapping_id"]
assert rr["mapping_contract"]["required_feature_count"]==71
assert PROFILE=="KM-JRA-EVIDENCE-FEATURE-COMPILER-v1.1-20260922"

runner=[{
  "runner_id":"N1",
  "evidence_features":{
    "pedigree_class":{
      "category":"STRONG",
      "rule_id":"KM-JRA-PEDIGREE-CLASS-v1",
      "evidence_refs":["TEST:PEDIGREE"],
      "source_fact":"pre-race pedigree class evidence"
    }
  }
}]
out=compile_evidence_feature_ledger("TEST-JRA-REGISTRY-CLOSURE","abc123",runner,mp,rr)
assert out["registry_mapping_closure"]["required_count"]==71
assert out["registry_mapping_closure"]["missing"]==[]

broken=copy.deepcopy(rr)
del broken["feature_rules"]["pedigree_class"]
try:
    compile_evidence_feature_ledger("TEST-JRA-REGISTRY-GAP","abc123",runner,mp,broken)
    raise AssertionError("mapping-registry gap must fail before race compilation")
except EvidenceCompilerError as e:
    assert "FEATURE_RULE_REGISTRY_MAPPING_GAP:pedigree_class" in str(e)

print("JRA_EVIDENCE_RULE_REGISTRY_CLOSURE_PASS", len(required), out["sha256"])
