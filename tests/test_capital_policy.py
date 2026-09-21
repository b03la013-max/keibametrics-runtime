import sys
sys.path.insert(0,"runtime")
from capital_policy import resolve_capital_policy, CapitalPolicyError
m={"profile":"MEC","sha256":"x","minimum_required_capital":3200,"material_coverage_ratio":1.0}
r=resolve_capital_policy({},m)
assert r["mode"]=="RECOMMENDATION_ONLY" and r["no_bet"] is False
r=resolve_capital_policy({"capital_policy":{"mode":"HARD_RACE_BUDGET","max_race_capital":4000}},m)
assert r["compatibility"]=="COMPATIBLE" and r["no_bet"] is False
r=resolve_capital_policy({"capital_policy":{"mode":"HARD_RACE_BUDGET","max_race_capital":2000,"insufficient_action":"NO_BET"}},m)
assert r["compatibility"]=="INCOMPATIBLE" and r["no_bet"] is True and r["decision"]=="NO_BET"
r=resolve_capital_policy({"capital_policy":{"mode":"HARD_RACE_BUDGET","max_race_capital":2000,"insufficient_action":"PAPER"}},m)
assert r["paper_only"] is True and r["no_bet"] is True
print("CAPITAL_POLICY_ACCEPTANCE_PASS")
