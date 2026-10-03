import sys
sys.path.insert(0,"runtime")

from jra_source_candidate_semantics import build_candidate_semantics, PROFILE
from minimum_efficient_coverage import build_mec_plan, validate_mec_plan
from capital_policy import resolve_capital_policy

def runner(i):
    base=100-i
    return {
      "runner_id":str(i),
      "canonical_components":{
        "ZAI_WIN":{"value":base},
        "ZAI_PLACE":{"value":base-0.1},
        "T3I":{"value":base-0.2},
      }
    }

req={
  "race_id":"TEST-JRA-WIDTH-16",
  "family_id":"JRA",
  "runners":[runner(i) for i in range(1,17)],
}
sem=build_candidate_semantics(req)
freeze=sem["candidate_semantic_freeze"]
assert PROFILE=="KM-JRA-SOURCE-DERIVED-CANDIDATE-SEMANTICS-v0.2-20261003-WIDTH-BALANCED"
assert len(freeze["w_active"])==3
assert len(freeze["p2_active"])==6
assert len(freeze["p3_active"])==8
assert freeze["width_policy"]["target_capital_band_yen"]==[5000,10000]
assert freeze["width_policy"]["budget_fill_forbidden"] is True

mec=build_mec_plan(sem,None,strict_head_closure=True,min_stake=100)
validate_mec_plan(mec)
assert mec["ticket_count"]==66, mec["ticket_count"]
assert mec["minimum_required_capital"]==6600, mec["minimum_required_capital"]

cap=resolve_capital_policy(sem,mec)
assert cap["capital_limit"]==10000
assert cap["decision"]=="EXECUTE_FULL_MEC"
assert cap["required_capital"]==6600
assert cap["unused_budget"]==3400
assert cap["budget_fill_required"] is False
assert cap["unused_budget_must_not_expand_tickets"] is True

# Small fields are not padded merely to hit 5,000 yen.
small={
  "race_id":"TEST-JRA-WIDTH-5",
  "family_id":"JRA",
  "runners":[runner(i) for i in range(1,6)],
}
ssem=build_candidate_semantics(small)
smec=build_mec_plan(ssem,None,strict_head_closure=True,min_stake=100)
validate_mec_plan(smec)
assert smec["minimum_required_capital"]<5000
scap=resolve_capital_policy(ssem,smec)
assert scap["decision"]=="EXECUTE_FULL_MEC"
assert scap["unused_budget_must_not_expand_tickets"] is True

print("JRA_WIDTH_BALANCED_ACCEPTANCE_PASS",mec["ticket_count"],mec["minimum_required_capital"],smec["ticket_count"],smec["minimum_required_capital"])
