import json, sys
sys.path.insert(0,"runtime")
from minimum_efficient_coverage import build_mec_plan, validate_mec_plan, MECError, MEC_PROFILE

def base_req(family):
    return {
      "race_id":f"TEST-{family}",
      "family_id":family,
      "available_bet_types":["WIN","PLACE","QUINELLA","WIDE","EXACTA","TRIO","TRIFECTA"],
      "role_registry":[
        {"runner_id":"1","column":"W","status":"CORE"},
        {"runner_id":"1","column":"P2","status":"PROTECTED"},
        {"runner_id":"1","column":"P3","status":"PROTECTED"},
        {"runner_id":"2","column":"W","status":"EXCLUDED","reason":"NO_W"},
        {"runner_id":"2","column":"P2","status":"CORE"},
        {"runner_id":"2","column":"P3","status":"PROTECTED"},
        {"runner_id":"3","column":"W","status":"EXCLUDED","reason":"NO_W"},
        {"runner_id":"3","column":"P2","status":"PROTECTED"},
        {"runner_id":"3","column":"P3","status":"CORE"},
        {"runner_id":"4","column":"W","status":"EXCLUDED","reason":"NO_W"},
        {"runner_id":"4","column":"P2","status":"PROTECTED"},
        {"runner_id":"4","column":"P3","status":"PROTECTED"},
      ],
      "purchased_heads":["1"],
      "pair_dispositions":[
        {"head":"1","second":"2","status":"PURCHASE","reason":"PRIMARY_ORDERED_PAIR"},
        {"head":"1","second":"3","status":"PROTECT","reason":"SECOND_COLUMN_PROTECTION"},
        {"head":"1","second":"4","status":"PROTECT","reason":"EXPECTED_PAIR_TERMINALIZATION_CORRECTNESS_REPAIR"},
      ],
      "third_dispositions":[
        {"head":"1","second":"2","third":"3","status":"PURCHASE","reason":"PAIR_LOCAL_MATERIAL_THIRD"},
        {"head":"1","second":"2","third":"4","status":"PROTECT","reason":"PAIR_LOCAL_TAIL_PROTECTION"},
      ],
      "orientation_exclusions":[
        {"head":"1","second":"2","third":"3","reason":"BUDGET-NONSELECTED_ORIENTATION_UNDER_FIXED_CAPITAL"}
      ],
      "head_nonselection_reasons":{}
    }

for fam in ["JRA","LOCAL","BAN"]:
    p=build_mec_plan(base_req(fam),strict_head_closure=True)
    v=validate_mec_plan(p)
    assert p["profile"]==MEC_PROFILE
    assert p["fixed_ticket_cap"] is None
    assert p["material_coverage_ratio"]==1.0
    assert p["ticket_count"]>=4
    assert p["minimum_required_capital"]==100*p["ticket_count"]
    assert p["precompression_semantic_universe"] is True
    assert p["semantic_tail_floor_count"]>=1
    assert any(t["bet_type"]=="TRIFECTA" and t["selection"]==[1,2,3] for t in p["tickets"])
    assert any(t["bet_type"]=="TRIO" and set(t["selection"])=={1,2,4} for t in p["tickets"])
    # Global P3 must survive under the protected 1>3 pair even though no pair-local
    # third row was supplied: R3 synthesizes a TAIL set rather than silently dropping it.
    assert any(t["bet_type"]=="TRIO" and set(t["selection"])=={1,2,3} for t in p["tickets"])
    assert any(x["mec_action"]=="IGNORED_BUDGET_ONLY" for x in p["budget_only_orientation_exclusions_ignored"])
    assert v["mec_verified"] is True


# Legacy venue transport sometimes serialized a global P3 tail as TAIL_PROTECTED.
# MEC-R3 must treat that as the existing RESIDUAL semantic role, not silently drop it.
alias_req=base_req("LOCAL")
for row in alias_req["role_registry"]:
    if row["runner_id"]=="4" and row["column"]=="P3":
        row["status"]="TAIL_PROTECTED"
alias_plan=build_mec_plan(alias_req,strict_head_closure=True)
assert any(t["bet_type"]=="TRIO" and set(t["selection"])=={1,2,4} for t in alias_plan["tickets"])
assert alias_plan["material_coverage_ratio"]==1.0

bad=base_req("JRA")
bad["role_registry"].append({"runner_id":"5","column":"W","status":"CORE"})
bad["role_registry"].append({"runner_id":"5","column":"P2","status":"PROTECTED"})
bad["role_registry"].append({"runner_id":"5","column":"P3","status":"PROTECTED"})
bad["head_nonselection_reasons"]={"5":"BUDGET-NONSELECTED"}
try:
    build_mec_plan(bad,strict_head_closure=True)
    raise AssertionError("strict head closure should fail")
except MECError as e:
    assert "ACTIVE_W_WITHOUT_MATERIAL_PAIR_CLOSURE" in str(e)

print("MEC_UNIT_ACCEPTANCE_PASS")
