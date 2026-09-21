import json,sys
sys.path.insert(0,"runtime")
from minimum_efficient_coverage import build_mec_plan, validate_mec_plan, MEC_PROFILE

assert MEC_PROFILE=="KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R3"

req=json.load(open("runtime/requests/KM-JRA-HSN-20260921-R12.json",encoding="utf-8"))
plan=build_mec_plan(req,strict_head_closure=False)
validate_mec_plan(plan)

assert plan["precompression_semantic_universe"] is True
assert plan["semantic_tail_floor_count"]>0
assert any(
    t["bet_type"]=="TRIO" and set(map(str,t["selection"]))=={"5","9","13"}
    for t in plan["tickets"]
), "R12_GLOBAL_P3_13_NOT_RESCUED_AS_5_9_13_TAIL_SET"

ov=[x for x in plan["soft_third_exclusions_overridden"]
    if str(x.get("head"))=="5" and str(x.get("second"))=="9" and str(x.get("third"))=="13"]
assert ov and ov[0]["mec_tier"]=="TAIL"
print("MEC_R3_PRECOMPRESSION_TAIL_FLOOR_PASS",plan["ticket_count"],plan["minimum_required_capital"])
