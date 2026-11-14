from __future__ import annotations

import copy
import hashlib
import json
from math import isfinite

BASE = ["HPI","SSI","CFI","RFI","BVI","JTI","CSI","TRI","BWI","GCI","PRI","KGI","VMI"]
DERIVED = ["DCR","TPI","ZAI_WIN","ZAI_PLACE","SRI","F3S","T3I"]
DCR_COMPONENT_MAX = {
    "official_recent":25.0,
    "same_course_distance":20.0,
    "training_comments":15.0,
    "bodyweight_range":15.0,
    "same_day_gci":15.0,
    "late_market_changes":10.0,
}
FORMULA_REGISTRY = "index_formula_registry JRA v1.0"
BASE_MAPPING_VERSION = "JRA-v1.0-IPL-RULE-BASED"
TRACE_SCHEMA = "KM-JRA-SOURCE-FEATURE-INDEX-STATIC-TRACE-v1.0-20260927"


class IndexLedgerError(ValueError):
    pass


# Owner decision 2026-11-14 15:16 JST (上濵さん): pedigree first (BLOOD BIAS),
# odds-theory index one tier lower. v1.1 = v1.0 x 0.80 + BVI .15 + VMI .05,
# effective for races on/after 2026-11-15; earlier FINALs replay with v1.0.
ZAI_V11_EFFECTIVE_DATE = "20261115"
ZAI_WIN_WEIGHTS = {
    "v1.0": {"HPI": .20, "SSI": .17, "CFI": .10, "RFI": .08, "JTI": .05, "CSI": .05,
             "TRI": .05, "BWI": .05, "GCI": .08, "PRI": .12, "KGI": .05},
}
ZAI_PLACE_WEIGHTS = {
    "v1.0": {"HPI": .16, "SSI": .14, "CFI": .10, "RFI": .14, "JTI": .05, "CSI": .06,
             "TRI": .05, "BWI": .08, "GCI": .08, "PRI": .08, "KGI": .06},
}
for _table in (ZAI_WIN_WEIGHTS, ZAI_PLACE_WEIGHTS):
    _table["v1.1"] = {k: round(w * 0.80, 6) for k, w in _table["v1.0"].items()}
    _table["v1.1"].update({"BVI": 0.15, "VMI": 0.05})


def zai_formula_version(race_id) -> str:
    import re as _re
    m = _re.search(r"-(\d{8})-R\d{2}", str(race_id or ""))
    return "v1.1" if m and m.group(1) >= ZAI_V11_EFFECTIVE_DATE else "v1.0"


def _weighted_left_sum(vals, weights):
    # Plain left-to-right float addition, bit-identical to the original v1.0
    # expression (built-in sum() uses compensated summation on Python >= 3.12).
    total = None
    for k, w in weights.items():
        term = vals[k] * w
        total = term if total is None else total + term
    return total


def zai_win_value(vals, version="v1.0"):
    return _weighted_left_sum(vals, ZAI_WIN_WEIGHTS[version])


def zai_place_value(vals, version="v1.0"):
    return _weighted_left_sum(vals, ZAI_PLACE_WEIGHTS[version])


def _score(x, label, lo=0.0, hi=100.0):
    if not isinstance(x, (int, float)) or not isfinite(float(x)) or not (lo <= float(x) <= hi):
        raise IndexLedgerError(f"{label}_OUT_OF_RANGE:{x}")
    return float(x)


def _canonical_sha(obj):
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _base_component(index, spec, runner_id):
    if not isinstance(spec, dict):
        raise IndexLedgerError(f"BASE_INDEX_SPEC_MISSING:{runner_id}:{index}")
    value = _score(spec.get("value"), f"{runner_id}:{index}")
    rule_id = str(spec.get("rule_id") or "").strip()
    mapping_version = str(spec.get("mapping_version") or "").strip()
    evidence_refs = spec.get("evidence_refs")
    source_fact = str(spec.get("source_fact") or "").strip()
    if not rule_id:
        raise IndexLedgerError(f"BASE_INDEX_RULE_ID_MISSING:{runner_id}:{index}")
    if not mapping_version:
        raise IndexLedgerError(f"BASE_INDEX_MAPPING_VERSION_MISSING:{runner_id}:{index}")
    if not isinstance(evidence_refs, list) or not evidence_refs:
        raise IndexLedgerError(f"BASE_INDEX_EVIDENCE_MISSING:{runner_id}:{index}")
    if not source_fact:
        raise IndexLedgerError(f"BASE_INDEX_SOURCE_FACT_MISSING:{runner_id}:{index}")
    component = {
        "value": value,
        "rule_id": rule_id,
        "mapping_version": mapping_version,
        "evidence_refs": [str(x) for x in evidence_refs],
        "source_fact": source_fact,
        "adjustments": copy.deepcopy(spec.get("adjustments") or []),
    }
    # Preserve the calculator's observed/DCR audit through Full20 and Static.
    # These fields do not participate in any numerical formula.
    for key in ("components", "coverage_weight", "profile", "information_status", "dcr"):
        if key in spec:
            component[key] = copy.deepcopy(spec[key])
    return component


def _derived(value, rule_id, evidence_refs, source_fact):
    return {
        "value": round(float(value), 6),
        "rule_id": rule_id,
        "mapping_version": FORMULA_REGISTRY,
        "evidence_refs": list(evidence_refs),
        "source_fact": source_fact,
        "adjustments": [],
    }


def _dcr(dcr, runner_id):
    if not isinstance(dcr, dict):
        raise IndexLedgerError(f"DCR_LEDGER_MISSING:{runner_id}")
    comps = dcr.get("components")
    if not isinstance(comps, dict):
        raise IndexLedgerError(f"DCR_COMPONENTS_MISSING:{runner_id}")
    total = 0.0
    refs = []
    for k, maximum in DCR_COMPONENT_MAX.items():
        c = comps.get(k)
        if not isinstance(c, dict):
            raise IndexLedgerError(f"DCR_COMPONENT_MISSING:{runner_id}:{k}")
        points = _score(c.get("points"), f"DCR:{runner_id}:{k}", 0.0, maximum)
        er = c.get("evidence_refs")
        if not isinstance(er, list) or not er:
            raise IndexLedgerError(f"DCR_EVIDENCE_MISSING:{runner_id}:{k}")
        total += points
        refs.extend(str(x) for x in er)
    declared = dcr.get("score")
    if declared is not None and abs(_score(declared, f"DCR:{runner_id}:score") - total) > 1e-6:
        raise IndexLedgerError(f"DCR_RECONCILIATION_FAIL:{runner_id}:{declared}!={total}")
    return total, 0.70 + 0.30 * total / 100.0, sorted(set(refs))


def materialize_index_provenance(req: dict) -> dict:
    req = copy.deepcopy(req)
    ledger = req.get("index_provenance_ledger")
    if not isinstance(ledger, dict):
        return req
    if str(ledger.get("formula_registry")) != FORMULA_REGISTRY:
        raise IndexLedgerError("FORMULA_REGISTRY_MISMATCH")
    rows = ledger.get("runners")
    if not isinstance(rows, dict):
        raise IndexLedgerError("INDEX_LEDGER_RUNNERS_MISSING")
    runner_by_id = {str(r.get("runner_id")): r for r in req.get("runners", [])}
    if set(rows) != set(runner_by_id):
        raise IndexLedgerError(f"INDEX_LEDGER_RUNNER_UNIVERSE_MISMATCH:{sorted(rows)}!={sorted(runner_by_id)}")

    sp = req.get("static_prediction") or {}
    ranking = [str(x) for x in (sp.get("ranking") or [])]
    static_rank_by_id = {rid: pos + 1 for pos, rid in enumerate(ranking)}
    static_roles = sp.get("roles") or {}
    replay = {
        "formula_registry": FORMULA_REGISTRY,
        "trace_schema": TRACE_SCHEMA,
        "static_ranking": ranking,
        "runners": {},
    }

    for rid, spec in rows.items():
        if not isinstance(spec, dict):
            raise IndexLedgerError(f"INDEX_LEDGER_BAD_RUNNER:{rid}")
        base_specs = spec.get("base_indices")
        if not isinstance(base_specs, dict):
            raise IndexLedgerError(f"BASE_INDICES_MISSING:{rid}")
        canonical = {}
        vals = {}
        all_refs = []

        for idx in BASE:
            c = _base_component(idx, base_specs.get(idx), rid)
            canonical[idx] = c
            vals[idx] = c["value"]
            all_refs.extend(c["evidence_refs"])

        dcr_score, dcr_factor, dcr_refs = _dcr(spec.get("dcr"), rid)
        canonical["DCR"] = _derived(
            dcr_score,
            "JRA-DCR-SCORE-v1",
            dcr_refs,
            "DCR-score six-component replay",
        )
        all_refs.extend(dcr_refs)

        major = spec.get("weak_penalty_major_indices")
        if not isinstance(major, list) or len(major) < 2 or any(x not in vals for x in major):
            raise IndexLedgerError(f"WEAK_PENALTY_MAJOR_INDEX_SET_INVALID:{rid}")
        ordered = sorted(vals[x] for x in major)
        l1, l2 = ordered[0], ordered[1]
        weak = 0.40 * max(0.0, 60.0 - l1) + 0.20 * max(0.0, 65.0 - l2)

        tpi_base = (
            vals["HPI"]*.15 + vals["SSI"]*.14 + vals["CFI"]*.10 + vals["RFI"]*.10 +
            vals["BVI"]*.05 + vals["JTI"]*.06 + vals["CSI"]*.05 + vals["TRI"]*.07 +
            vals["BWI"]*.06 + vals["GCI"]*.08 + vals["PRI"]*.08 + vals["KGI"]*.06
        )
        tpi_weak = tpi_base - weak
        tpi = 50.0 + (tpi_weak - 50.0) * dcr_factor
        zai_version = zai_formula_version(req.get("race_id"))
        zai_win = zai_win_value(vals, zai_version)
        zai_place = zai_place_value(vals, zai_version)
        sri = zai_place*.45 + tpi*.25 + vals["RFI"]*.10 + vals["PRI"]*.08 + vals["KGI"]*.07 + vals["BWI"]*.05

        scenario = spec.get("scenario_fit")
        if not isinstance(scenario, dict):
            raise IndexLedgerError(f"SCENARIO_FIT_MISSING:{rid}")
        scenario_value = _score(scenario.get("value"), f"SCENARIO_FIT:{rid}")
        scenario_refs = scenario.get("evidence_refs")
        if not isinstance(scenario_refs, list) or not scenario_refs:
            raise IndexLedgerError(f"SCENARIO_FIT_EVIDENCE_MISSING:{rid}")
        f3s = zai_win*.30 + zai_place*.25 + tpi*.25 + sri*.15 + scenario_value*.05
        t3i = zai_place*.35 + tpi*.20 + vals["RFI"]*.15 + vals["PRI"]*.10 + vals["GCI"]*.08 + vals["CFI"]*.07 + vals["VMI"]*.05

        formula_refs = sorted(set(all_refs))
        canonical["TPI"] = _derived(tpi, "JRA-TPI-FINAL-v1.0", formula_refs, f"TPI replay; weak={weak:.6f}; dcr_factor={dcr_factor:.6f}")
        suffix = "" if zai_version == "v1.0" else f" ({zai_version}: Owner 2026-11-14 BVI .15 VMI .05)"
        canonical["ZAI_WIN"] = _derived(zai_win, f"JRA-ZAI-WIN-{zai_version}", formula_refs,
                                        "ZAI-WIN fixed formula replay" + suffix)
        canonical["ZAI_PLACE"] = _derived(zai_place, f"JRA-ZAI-PLACE-{zai_version}", formula_refs,
                                          "ZAI-PLACE fixed formula replay" + suffix)
        canonical["SRI"] = _derived(sri, "JRA-SRI-v1.0", formula_refs, "SRI fixed formula replay")
        canonical["F3S"] = _derived(f3s, "JRA-F3S-v1.0", sorted(set(formula_refs + [str(x) for x in scenario_refs])), "F3S fixed formula replay")
        canonical["T3I"] = _derived(t3i, "JRA-T3I-v1.0", formula_refs, "T3I fixed formula replay")

        runner_by_id[rid]["canonical_components"] = canonical
        base_index_trace = {}
        trace_complete = True
        for idx in BASE:
            raw = base_specs.get(idx) or {}
            components = copy.deepcopy(raw.get("components") or [])
            if not components:
                trace_complete = False
            base_index_trace[idx] = {
                "value": vals[idx],
                "rule_id": canonical[idx]["rule_id"],
                "mapping_version": canonical[idx]["mapping_version"],
                "coverage_weight": raw.get("coverage_weight"),
                "components": components,
                "evidence_refs": copy.deepcopy(canonical[idx]["evidence_refs"]),
                "source_fact": canonical[idx]["source_fact"],
            }
            for key in ("profile", "information_status", "dcr"):
                if key in raw:
                    base_index_trace[idx][key] = copy.deepcopy(raw[key])

        derived_index_trace = {
            "DCR": copy.deepcopy(canonical["DCR"]),
            "TPI": copy.deepcopy(canonical["TPI"]),
            "ZAI_WIN": copy.deepcopy(canonical["ZAI_WIN"]),
            "ZAI_PLACE": copy.deepcopy(canonical["ZAI_PLACE"]),
            "SRI": copy.deepcopy(canonical["SRI"]),
            "F3S": copy.deepcopy(canonical["F3S"]),
            "T3I": copy.deepcopy(canonical["T3I"]),
        }
        runner_roles = sorted(
            str(role) for role, ids in static_roles.items()
            if isinstance(ids, list) and rid in {str(x) for x in ids}
        )

        replay["runners"][rid] = {
            "base_final_values": {k: vals[k] for k in BASE},
            "base_index_trace": base_index_trace,
            "derived_index_trace": derived_index_trace,
            "source_to_index_trace_complete": trace_complete,
            "static_rank": static_rank_by_id.get(rid),
            "static_roles": runner_roles,
            "dcr_score": dcr_score,
            "dcr_factor": round(dcr_factor, 6),
            "weak_penalty": round(weak, 6),
            "tpi_base": round(tpi_base, 6),
            "tpi_final": round(tpi, 6),
            "zai_win": round(zai_win, 6),
            "zai_place": round(zai_place, 6),
            "sri": round(sri, 6),
            "f3s": round(f3s, 6),
            "t3i": round(t3i, 6),
        }

    replay["trace_complete_runner_count"] = sum(
        1 for x in replay["runners"].values() if x.get("source_to_index_trace_complete")
    )
    replay["trace_incomplete_runner_count"] = len(replay["runners"]) - replay["trace_complete_runner_count"]
    replay["sha256"] = _canonical_sha(replay)
    req["index_provenance_replay"] = replay
    req["index_provenance_hash"] = replay["sha256"]
    req["numeric_calculation_requirement"] = "FULL_REQUIRED"
    return req
