"""R8 independent arithmetic witness covering 29 LOCAL indices, not features.

Distinct Decimal formulas audit each frozen numerical value. This does NOT
independently rederive source-to-feature transforms or validate prediction,
KRS, odds probabilities, purchased tickets, issuer signature or future OOS.
"""
from decimal import Decimal
from runtime.local_fnb_r7_arithmetic_witness import verify_arithmetic
from runtime.local_fnb_r8_arithmetic_first import D, initial, price, val
from runtime.local_fnb_r8_arithmetic_roles import roles

EXTRA = ("EVI/CEV","CCI","TRI","DRS","URP","HCS","PRI","OPI-V",
         "W-AKI","P2-AKI","P3-AKI","ASI","T3I-L",
         "ZAI-WIN","ZAI-PLACE","RSI","WCI")
EPSILON=D("0.000015")


def verify_29(materialized, evidence_registry, mapping):
    basic=verify_arithmetic(materialized,evidence_registry,mapping)
    failures=list(basic["issues"])
    checked=0
    runners=materialized.get("runners") or []
    if basic["status"]!="12_OF_29_INDEPENDENT_ARITHMETIC_VERIFIED":
        failures.append("R7_12_INDEX_ARITHMETIC_NOT_VERIFIED")
    missing = mapping.get("missing_semantics") or {}
    # The original candidate v0.1 declares these same neutral-included
    # semantics before the later production registry added the policy key.
    # Accept only that exact governed legacy document shape. This does not
    # turn a candidate mapping into production or change the arithmetic.
    legacy_candidate = (mapping.get("mapping_id") ==
            "LOCAL-FULL-NUMERICAL-MAPPING-v0.1-CANDIDATE-20260923"
        and missing == {"neutral_score": 52,
            "interpretation": "UNKNOWN / INCOMPARABLE, never WEAK",
            "dcr_carries_missingness": True})
    if (missing.get("policy") !=
            "CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE"
            and not legacy_candidate):
        failures.append("NUMERIC_MAPPING_POLICY_UNRECOGNIZED")
    ranks=price(runners) if runners else {}
    env=(materialized.get("numerical_environment") or
         (materialized.get("candidate_environment") if legacy_candidate else None) or {})
    # Rebuild the already governed front-count input from the feature grid.
    # Candidate v0.1 emits candidate_environment, while Production emits
    # numerical_environment; missing that alias used to audit every candidate
    # as pressure=0 even when observed front-running facts were present.
    count=sum(1 for runner in runners
        if not (runner.get("evidence_features", {}).get("position_acquisition") or {}).get("missing", True)
        and D(str((runner.get("evidence_features", {}).get("position_acquisition") or {}).get("score",0))) >= D(70))
    if env and D(str(env.get("front_candidate_count",0))) != D(count):
        failures.append("FRONT_COUNT_ENVIRONMENT_DIFFERS_FROM_RECORDED_FEATURES")
    pressure=min(D(100),max(D(0),D(100)*D(str(count or 0))/D(max(1,len(runners)))))
    for runner in runners:
        rid=str(runner.get("runner_id"))
        try:
            expected=initial(runner,pressure)
            expected.update(ranks[rid])
            expected.update(roles(runner,ranks[rid],pressure,len(runners)))
            if set(expected)!=set(EXTRA):
                raise ValueError("EXTRA_17_FORMULAS_INCOMPLETE")
            for name in EXTRA:
                actual=val(runner,name)
                if abs(actual-expected[name])>EPSILON:
                    raise ValueError(f"{name}:ACTUAL_{actual}:EXPECTED_{expected[name]}")
                checked+=1
        except (ValueError,KeyError,TypeError,ArithmeticError) as exc:
            failures.append(f"R{rid}:{exc}")
    total=basic["checked_cells"]+checked
    required=len(runners)*29
    if total!=required:
        failures.append("FULL_29_INDEX_ARITHMETIC_COVERAGE_MISSING")
    return {
        "status":"29_OF_29_RECORDED_FEATURE_ARITHMETIC_PASS"
            if not failures else "PARTIAL_ARITHMETIC_HOLD",
        "runners":len(runners), "basic_12_index_cells":basic["checked_cells"],
        "extra_17_index_cells":checked, "checked_cells":total,
        "expected_cells":required, "issues":failures[:70],
        "source_to_feature_independent_recalculation":"NOT_PERFORMED",
        "issuer_signature_and_license":"NOT_VERIFIED",
        "prediction_krs_ticket_capital_authorized":False,
        "future_oos_registered":False}
