import sys
sys.path.insert(0,"runtime")
from capital_policy import resolve_capital_policy, CapitalPolicyError

m={"profile":"MEC","sha256":"x","minimum_required_capital":3200,"material_coverage_ratio":1.0}

# Family-wide user default: 10,000 yen hard race budget, no budget-fill expansion.
r=resolve_capital_policy({},m)
assert r["mode"]=="HARD_RACE_BUDGET"
assert r["capital_limit"]==10000
assert r["budget_source"]=="FAMILY_USER_DEFAULT"
assert r["decision"]=="EXECUTE_FULL_MEC"
assert r["required_capital"]==3200
assert r["unused_budget"]==6800
assert r["budget_fill_required"] is False
assert r["unused_budget_must_not_expand_tickets"] is True
assert r["final_ticket_stake_unit_yen"]==100
assert r["internal_allocation_precision"]=="DECIMAL_ALLOWED"
assert r["ticket_count_limit"]==100
assert r["no_bet"] is False

# Explicit race budget still overrides the family default.
r=resolve_capital_policy({"capital_policy":{"mode":"HARD_RACE_BUDGET","max_race_capital":4000}},m)
assert r["compatibility"]=="COMPATIBLE" and r["no_bet"] is False
assert r["budget_source"]=="REQUEST_EXPLICIT"

r=resolve_capital_policy({"capital_policy":{"mode":"HARD_RACE_BUDGET","max_race_capital":2000,"insufficient_action":"NO_BET"}},m)
assert r["compatibility"]=="INCOMPATIBLE" and r["no_bet"] is True and r["decision"]=="NO_BET"

r=resolve_capital_policy({"capital_policy":{"mode":"HARD_RACE_BUDGET","max_race_capital":2000,"insufficient_action":"PAPER"}},m)
assert r["paper_only"] is True and r["no_bet"] is True

# Family default above the 10,000-yen ceiling fails closed to PAPER rather than deleting MEC semantics.
large={"profile":"MEC","sha256":"y","minimum_required_capital":10100,"material_coverage_ratio":1.0}
r=resolve_capital_policy({},large)
assert r["compatibility"]=="INCOMPATIBLE"
assert r["decision"]=="PAPER"
assert r["paper_only"] is True and r["no_bet"] is True

# Unused budget must never be treated as a fill target.
try:
    resolve_capital_policy({"capital_policy":{
        "mode":"HARD_RACE_BUDGET",
        "max_race_capital":10000,
        "budget_fill_required":True
    }},m)
    raise AssertionError("BUDGET_FILL_REQUIRED_SHOULD_FAIL")
except CapitalPolicyError as e:
    assert "BUDGET_FILL_REQUIRED_FORBIDDEN" in str(e)

print("CAPITAL_POLICY_ACCEPTANCE_PASS")
