"""Independent Decimal witness for governed LOCAL numerical arithmetic.

R7 checks the 9 base weighted-index cells and the three explicitly specified
derived arithmetic cells (TPI-L, SRI-L, F3S-L) against rule-bound SOURCE
features. It does not replay SOURCE->feature transforms or certify the
remaining 17 indices. The consumer authority remains completely untouched.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
import json
import math
from pathlib import Path

PROFILE = "KM-FNB-R7-INDEPENDENT-ARITHMETIC-12-OF-29-v1"
BASE = ("HPI-L", "CFIg-L", "RFIg-L", "BVIg-L", "JTI-L",
        "CSI-L", "BWI-L", "DCR", "NCI")
TPI = (("HPI-L", "0.18"), ("CFIg-L", "0.16"),
       ("RFIg-L", "0.14"), ("BVIg-L", "0.08"),
       ("JTI-L", "0.08"), ("CSI-L", "0.08"),
       ("BWI-L", "0.08"), ("NCI", "0.10"), ("EVI/CEV", "0.10"))
SRI = (("TPI-L", "0.20"), ("RFIg-L", "0.18"),
       ("EVI/CEV", "0.18"), ("CFIg-L", "0.15"),
       ("NCI", "0.12"), ("BWI-L", "0.10"),
       ("JTI-L", "0.05"), ("CSI-L", "0.02"))
F3S = (("SRI-L", "0.25"), ("TPI-L", "0.20"),
       ("EVI/CEV", "0.18"), ("RFIg-L", "0.14"),
       ("CFIg-L", "0.12"), ("NCI", "0.06"),
       ("T3I-L", "0.05"))
VALIDATED = BASE + ("TPI-L", "SRI-L", "F3S-L")
QUANT = Decimal("0.000001")
EPSILON = Decimal("0.000002")


def d(value):
    if type(value) not in (int, float, str) or isinstance(value, str) and not value:
        raise ValueError("ARITHMETIC_NON_NUMERIC")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("ARITHMETIC_NON_NUMERIC") from exc
    if not result.is_finite() or result < 0 or result > 100:
        raise ValueError("ARITHMETIC_VALUE_OUT_OF_RANGE")
    return result


def clamp(v):
    return max(Decimal(0), min(Decimal(100), v))


def weighted(cc, items):
    return sum((d(cc[k]["value"]) * Decimal(w) for k, w in items), Decimal(0))


def verify_arithmetic(materialized: dict, evidence_registry: dict,
                      mapping: dict) -> dict:
    problems = []
    checked = 0
    rows = materialized.get("runners") if isinstance(materialized, dict) else None
    if not isinstance(rows, list) or not rows:
        return {"profile": PROFILE, "status": "PARTIAL_ARITHMETIC_HOLD",
                "checked_cells": 0, "independent_derived_indices": list(VALIDATED),
                "issues": ["RUNNER_GRID_MISSING"], "full_29_arithmetic_verified": False,
                "consumer_authorized": False, "formula_input_transforms_verified": False}
    reg = evidence_registry.get("common_component_sets") if isinstance(evidence_registry, dict) else None
    formulas = mapping.get("exact_canon_formulas") if isinstance(mapping, dict) else None
    if (not isinstance(reg, dict) or not all(x in reg for x in BASE)
            or not isinstance(formulas, dict)
            or any(x not in formulas for x in ("TPI-L","SRI-L","F3S-L"))):
        problems.append("FROZEN_PRODUCTION_NUMERICAL_FORMULAS_MISSING")
    if mapping.get("missing_semantics", {}).get("policy") == "OBSERVED_ONLY_RENORMALIZE":
        problems.append("R7_LEGACY_DENOMINATOR_WITNESS_NOT_APPLICABLE")
    for runner in rows:
        rid = str((runner or {}).get("runner_id"))
        try:
            cc = runner["canonical_components"]
            feats = runner["evidence_features"]
            if not isinstance(cc, dict) or not isinstance(feats, dict):
                raise ValueError("CANONICAL_OR_FEATURE_GRID_MISSING")
            for idx in BASE:
                if idx not in reg or idx not in cc:
                    raise ValueError("BASE_RULE_OR_CELL_MISSING:" + idx)
                weights = reg[idx]
                components = cc[idx].get("components")
                if not isinstance(weights, dict) or not isinstance(components, list):
                    raise ValueError("BASE_COMPONENTS_MISSING:" + idx)
                if {x.get("component") for x in components if isinstance(x, dict)} != set(weights):
                    raise ValueError("BASE_COMPONENT_NAME_DRIFT:" + idx)
                for comp in components:
                    k = comp["component"]
                    if k not in feats:
                        raise ValueError("BASE_SOURCE_FEATURE_MISSING:" + idx + ":" + k)
                    if (d(comp["weight"]) != d(weights[k])
                            or d(comp["score"]) != d(feats[k]["score"])
                            or bool(comp["missing"]) != bool(feats[k].get("missing"))):
                        raise ValueError("BASE_COMPONENT_FEATURE_MISMATCH:" + idx + ":" + k)
                den = sum((d(w) for w in weights.values()), Decimal(0))
                if den <= 0:
                    raise ValueError("BAD_BASE_WEIGHT_DENOMINATOR:" + idx)
                raw = sum((d(feats[k]["score"]) * d(w) for k,w in weights.items()),
                          Decimal(0)) / den
                expected = clamp(raw)
                actual = d(cc[idx]["value"])
                if abs(actual-expected) > EPSILON:
                    raise ValueError("BASE_ARITHMETIC_MISMATCH:" + idx)
                checked += 1
            # Use the 6-decimal stored base values, as the governing first pass
            # does; do not use unrounded raw features to mask a wrong TPI.
            major = ("HPI-L","CFIg-L","RFIg-L","NCI","EVI/CEV","BWI-L")
            min_major = min(d(cc[k]["value"]) for k in major)
            penalty = max(Decimal(0), (Decimal(60)-min_major)*Decimal("0.5"))
            predicted = clamp(weighted(cc,TPI) - penalty)
            if abs(d(cc["TPI-L"]["value"]) - predicted) > EPSILON:
                raise ValueError("TPI_INDEPENDENT_FORMULA_MISMATCH")
            checked += 1
            sri_penalty = max(Decimal(0),
                              (Decimal(60)-d(cc["DCR"]["value"]))*Decimal("0.25"))
            predicted = clamp(weighted(cc,SRI) - sri_penalty)
            if abs(d(cc["SRI-L"]["value"]) - predicted) > EPSILON:
                raise ValueError("SRI_INDEPENDENT_FORMULA_MISMATCH")
            checked += 1
            predicted = clamp(weighted(cc,F3S))
            if abs(d(cc["F3S-L"]["value"]) - predicted) > EPSILON:
                raise ValueError("F3S_INDEPENDENT_FORMULA_MISMATCH")
            checked += 1
        except (ValueError, KeyError, TypeError, InvalidOperation) as exc:
            problems.append("HORSE_" + rid + ":" + str(exc))
    expected = len(rows) * len(VALIDATED)
    if checked != expected:
        problems.append("INDEPENDENT_ARITHMETIC_COVERAGE_INCOMPLETE")
    return {
        "profile": PROFILE,
        "status": "12_OF_29_INDEPENDENT_ARITHMETIC_VERIFIED" if not problems else
                  "PARTIAL_ARITHMETIC_HOLD",
        "runners": len(rows), "checked_cells": checked,
        "expected_checked_cells": expected,
        "independent_derived_indices": list(VALIDATED),
        "independent_arithmetic_scope":
            "9_BASE_WEIGHTED_PLUS_TPI_SRI_F3S_FROM_EXISTING_RECORDED_FEATURES",
        "full_29_arithmetic_verified": False,
        "source_to_feature_transform_independently_verified": False,
        "official_source_licensing": "NOT_VERIFIED",
        "consumer_authorized": False,
        "unknown_future_oos_registered": False,
        "issues": problems[:60],
        "additional_issue_count": max(0, len(problems)-60)
    }
