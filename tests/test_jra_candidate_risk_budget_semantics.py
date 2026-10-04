import sys
sys.path.insert(0, "runtime")

from jra_source_candidate_semantics import build_candidate_semantics
from jra_candidate_risk_budget_semantics import (
    expand_candidate_semantics_with_risk_budget,
    PROFILE,
)
from minimum_efficient_coverage import build_mec_plan, validate_mec_plan
from capital_policy import resolve_capital_policy


def runner(i):
    base = 100 - i
    return {
        "runner_id": str(i),
        "canonical_components": {
            "ZAI_WIN": {"value": base},
            "ZAI_PLACE": {"value": base - 0.1},
            "T3I": {"value": base - 0.2},
            "F3S": {"value": base - 0.3},
            "SRI": {"value": base - 0.4},
            "DCR": {"value": base - 0.5},
            "SSI": {"value": base - 0.6},
            "CFI": {"value": base - 0.7},
            "RFI": {"value": base - 0.8},
            "GCI": {"value": base - 0.9},
            "PRI": {"value": base - 1.0},
            "VMI": {"value": base - 1.1},
            "BWI": {"value": base - 1.2},
        },
    }


def test_risk_budget_expands_meaningful_semantics_but_not_past_cap():
    req = {
        "race_id": "TEST-JRA-RISK-BUDGET-16",
        "family_id": "JRA",
        "runners": [runner(i) for i in range(1, 17)],
    }
    base = build_candidate_semantics(req)
    base_mec = build_mec_plan(base, None, strict_head_closure=True, min_stake=100)
    validate_mec_plan(base_mec)
    assert base_mec["minimum_required_capital"] == 6600

    expanded = expand_candidate_semantics_with_risk_budget(base, budget_limit=10000)
    manifest = expanded["candidate_risk_budget_expansion"]
    final_mec = build_mec_plan(expanded, None, strict_head_closure=True, min_stake=100)
    validate_mec_plan(final_mec)

    assert manifest["profile"] == PROFILE
    assert manifest["accepted_count"] > 0
    assert final_mec["minimum_required_capital"] > base_mec["minimum_required_capital"]
    assert final_mec["minimum_required_capital"] <= 10000
    assert manifest["budget_fill_forbidden"] is True
    assert manifest["unused_budget"] == 10000 - final_mec["minimum_required_capital"]
    assert expanded["candidate_policy_cohort"] == "JRA-CANDIDATE-v0.2+RISK-BUDGET-v0.1"

    cap = resolve_capital_policy(expanded, final_mec)
    assert cap["decision"] == "EXECUTE_FULL_MEC"
    assert cap["capital_limit"] == 10000
    assert cap["required_capital"] == final_mec["minimum_required_capital"]


def test_risk_budget_does_not_force_fill_when_no_supported_frontier():
    # Three-runner field: base semantics already activates every runner in all columns.
    req = {
        "race_id": "TEST-JRA-RISK-BUDGET-3",
        "family_id": "JRA",
        "runners": [runner(i) for i in range(1, 4)],
    }
    base = build_candidate_semantics(req)
    expanded = expand_candidate_semantics_with_risk_budget(base, budget_limit=10000)
    manifest = expanded["candidate_risk_budget_expansion"]
    final_mec = build_mec_plan(expanded, None, strict_head_closure=True, min_stake=100)
    validate_mec_plan(final_mec)

    assert manifest["accepted_count"] == 0
    assert final_mec["minimum_required_capital"] < 10000
    assert manifest["unused_budget"] > 0


if __name__ == "__main__":
    test_risk_budget_expands_meaningful_semantics_but_not_past_cap()
    test_risk_budget_does_not_force_fill_when_no_supported_frontier()
    print("JRA_RISK_BUDGET_SEMANTIC_EXPANSION_PASS")
