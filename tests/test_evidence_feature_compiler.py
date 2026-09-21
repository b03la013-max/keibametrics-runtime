import copy,json,sys
sys.path.insert(0,"runtime")
from evidence_feature_compiler import compile_evidence_feature_ledger, EvidenceCompilerError
from jra_evidence_to_base_production import load_mapping

req=json.load(open("runtime/requests/KM-JRA-HSN-20260921-R12.json",encoding="utf-8"))
mp=load_mapping("mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")
a=compile_evidence_feature_ledger(req["race_id"],req["source_snapshot_sha256"],req["runners"],mp)
assert a["runner_count"]==15
assert a["freehand_numeric_score_allowed"] is False
bad=copy.deepcopy(req["runners"])
bad[0]["evidence_features"]["recent_performance"]["rule_id"]="FREEHAND"
try:
    compile_evidence_feature_ledger(req["race_id"],req["source_snapshot_sha256"],bad,mp)
    raise AssertionError("tampered rule must fail")
except EvidenceCompilerError as e:
    assert "UNREGISTERED_RULE_ID" in str(e)
print("EVIDENCE_FEATURE_COMPILER_ACCEPTANCE_PASS",a["sha256"])
