"""LOCAL AKI column experiment. Numerical authority is not decision authority.

No JRA coefficients, rank percentages, ticket caps, budget-driven pruning or
neutral-evidence admission. Outputs are PAPER/replay until separately enacted.
"""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import math

from minimum_efficient_coverage import build_mec_plan, validate_mec_plan
from capital_policy import resolve_capital_policy

PROFILE = "KM-LOCAL-AKI-COLUMNS-PAPER-20261012-R1"
POLICY = Path(__file__).resolve().parents[1] / "profiles/local_aki_columns_20261012_R1.json"


class LocalAKIError(ValueError):
    pass


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                   separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def number(value):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise LocalAKIError("NONFINITE_NUMBER")
    if not 0 <= value <= 100:
        raise LocalAKIError("NUMBER_OUT_OF_SCALE")
    return float(value)


def observed(feature):
    return (isinstance(feature, dict) and feature.get("missing") is False
            and bool(feature.get("evidence_refs")) and bool(feature.get("source_fact"))
            and bool(feature.get("rule_id")))


def build(request, source, *, policy=None):
    """All source signature/temporal checks belong to the calling formal runner.

    This function additionally checks universe and source identity. No caller
    flag can promote its output to Production or purchase authority.
    """
    p = deepcopy(policy) if policy is not None else json.loads(POLICY.read_text())
    if p.get("profile") != PROFILE or p.get("purchase_authority") is not False:
        raise LocalAKIError("POLICY_AUTHORITY_INVALID")
    if request.get("family_id") != "LOCAL":
        raise LocalAKIError("LOCAL_ONLY_BAN_EXCLUDED")
    source_hash = source.get("source_snapshot_sha256")
    if not source_hash or request.get("source_snapshot_sha256") != source_hash:
        raise LocalAKIError("SOURCE_BINDING_MISMATCH")
    required = json.loads((POLICY.parents[1] / p["numerical_mapping"]).read_text())["required_indices"]
    runners = request.get("runners") or []
    ids = [str(r.get("runner_id")) for r in runners]
    if not ids or len(ids) != len(set(ids)) or any(not r.isdigit() for r in ids):
        raise LocalAKIError("RUNNER_UNIVERSE_INVALID")
    official = source.get("active_runner_universe") or source.get("official_runner_universe") or {}
    official_ids = {str(r.get("horse_no", r.get("runner_id"))) for r in official.get("active_runners", [])}
    # Runtime versions use runners + active_horse_numbers, not always active_runners.
    if not official_ids:
        official_ids = {str(i) for i in official.get("active_horse_numbers", [])}
    if not official_ids:
        official_ids = {str(r.get("horse_no")) for r in official.get("runners", [])
                        if r.get("status", "ACTIVE") == "ACTIVE"}
    if not official_ids:
        raise LocalAKIError("OFFICIAL_UNIVERSE_REQUIRED")
    if official_ids != set(ids):
        raise LocalAKIError("OFFICIAL_UNIVERSE_MISMATCH")
    by_id = {str(r["runner_id"]): r for r in runners}
    audit = {}
    scores = {c: {} for c in ("W", "P2", "P3")}
    axes = {}
    for rid, r in by_id.items():
        cc = r.get("canonical_components") or {}
        for idx in required:
            x = cc.get(idx) or {}
            number(x.get("value"))
            if (x.get("terminal_status") not in {"CALCULATED", "RULED-NEUTRAL"}
                    or not x.get("rule_id") or not x.get("evidence_refs") or not x.get("source_fact")):
                raise LocalAKIError("FULL_INDEX_PROVENANCE_REQUIRED:" + rid + ":" + idx)
        features = r.get("evidence_features") or {}
        groups = {name: [f for f in names if observed(features.get(f))]
                  for name, names in p["support_groups"].items()}
        supported = sum(bool(v) for v in groups.values()) >= p["minimum_support_groups"]
        audit[rid] = {"observed_groups": groups, "eligible": supported,
                      "missing_fraction": {k: cc[k].get("missingness_fraction") for k in required},
                      "index_sha256": sha(cc), "missing_is_positive": False}
        axes[rid] = {k: number(cc[k]["value"]) for k in p["axes"]}
        for c, index in p["role_indices"].items():
            # Composite scores carry transport neutrals. Fully neutral composites
            # cannot admit a horse even when unrelated observations are present.
            if supported and cc[index].get("terminal_status") == "CALCULATED" and cc[index].get("missingness_fraction", 0) < 1:
                scores[c][rid] = number(cc[index]["value"])

    columns, diagnostics = {}, {}
    for c, values in scores.items():
        # A sole W cannot finish second/third in its own path. Use the best
        # eligible remaining role score as anchor, rather than leaving all
        # three quiet-race columns on the same horse or adding a rank floor.
        structural_exclusions = set()
        if c != "W" and len(columns["W"]["selected"]) == 1:
            structural_exclusions.update(columns["W"]["selected"])
            if c == "P3" and len(columns["P2"]["selected"]) == 1:
                structural_exclusions.update(columns["P2"]["selected"])
        values = {r: v for r, v in values.items() if r not in structural_exclusions}
        if not values:
            columns[c] = {"main": [], "additional": [], "selected": []}
            diagnostics[c] = {"status": "NO_OBSERVED_ELIGIBLE_ROLE"}
            continue
        order = sorted(values, key=lambda rid: (-values[rid], int(rid)))
        leader = order[0]
        high, low = max(values.values()), min(values.values())
        # Continuous, field-relative evidence score gap. Risk never creates
        # eligibility. RSI enters via max, so shared uncertainty is not summed.
        risk = axes[leader][p["role_axes"][c]]
        if c == "W":
            risk = max(risk, 100 - axes[leader]["ASI"])
        else:
            risk = max(risk, axes[leader]["RSI"])
        span = high - low
        main = [rid for rid in order if values[rid] == high]
        additional = [rid for rid in order if rid not in main and high - values[rid] <= span * risk / 100]
        selected = main + additional
        gate = "PASS"
        if c == "W" and axes[leader]["ASI"] < p["single_axis_min_asi"] and len(selected) == 1:
            # No fabricated second head. Explicit terminal instead of crashing
            # the remainder of the race day or filling from a rank floor.
            gate = "SINGLE_HEAD_FORBIDDEN_NO_SUPPORTED_ALTERNATIVE"
        columns[c] = {"main": main, "additional": additional, "selected": selected}
        diagnostics[c] = {"leader": leader, "risk": risk, "score_span": span,
                          "gap_limit": span * risk / 100, "status": gate,
                          "structural_exclusions": sorted(structural_exclusions),
                          "information_uncertainty": 100 - number(by_id[leader]["canonical_components"]["DCR"]["value"]),
                          "score_parity": span == 0, "budget_used": False}

    pairs, thirds = [], []
    for h in columns["W"]["selected"]:
        for s in columns["P2"]["selected"]:
            if h == s:
                continue
            # Conditional relation has an explicit observed position channel,
            # rather than admission by global column membership alone.
            sf = by_id[s].get("evidence_features") or {}
            hf = by_id[h].get("evidence_features") or {}
            refs = [f for f in p["pair_features"] if observed(sf.get(f))]
            hrefs = [f for f in p["head_features"] if observed(hf.get(f))]
            qualified = bool(refs and hrefs)
            pairs.append({"head": h, "second": s, "status": "PROTECT" if qualified else "SEMANTIC_ONLY",
                          "reason": "OBSERVED_HEAD_LOCAL_POSITION_SUPPORT" if qualified else "UNOBSERVED_PAIR_CONTEXT",
                          "evidence_refs": sorted({x for r, fs in ((sf, refs), (hf, hrefs)) for f in fs for x in r[f]["evidence_refs"]}),
                          "local_rule": PROFILE, "purchase_authority": False})
            if not qualified:
                continue
            for t in columns["P3"]["selected"]:
                if t in {h, s}:
                    continue
                tf = by_id[t].get("evidence_features") or {}
                tr = [f for f in p["third_features"] if observed(tf.get(f))]
                thirds.append({"head": h, "second": s, "third": t,
                               "status": "PROTECT" if tr else "SEMANTIC_ONLY",
                               "reason": "OBSERVED_PAIR_CONDITIONED_RESERVE_SUPPORT" if tr else "GLOBAL_P3_TAIL_ONLY",
                               "evidence_refs": sorted({x for f in tr for x in tf[f]["evidence_refs"]}),
                               "local_rule": PROFILE, "purchase_authority": False})
    missing_heads = set(columns["W"]["selected"]) - {x["head"] for x in pairs if x["status"] == "PROTECT"}
    reasons = [x["status"] for x in diagnostics.values() if x["status"] != "PASS"]
    if missing_heads:
        reasons.append("HEAD_WITHOUT_OBSERVED_PAIR:" + ",".join(sorted(missing_heads)))
    out = {"profile": PROFILE, "status": "NO_BET" if reasons else "PAPER",
           "race_id": request["race_id"], "source_snapshot_sha256": source_hash,
           "policy_sha256": sha(p), "numerical_mapping_sha256": hashlib.sha256((POLICY.parents[1] / p["numerical_mapping"]).read_bytes()).hexdigest(),
           "input_sha256": sha({"runners": runners, "source": source_hash}),
           "columns": columns, "column_diagnostics": diagnostics, "runner_audit": audit,
           "runner_axes": axes, "eligible_role_scores": scores,
           "pair_dispositions": pairs, "third_dispositions": thirds,
           "terminal_reasons": reasons, "production_authority": False,
           "purchase_authority": False, "validation_status": "UNVALIDATED_RULE_BASED",
           "oos_effect": "NONE_UNLESS_NEW_PRE_RESULT_PREREGISTERED_RUN"}
    out["sha256"] = sha(out)
    return out


def verify(request, source, selection):
    # Recompile all 29 indices from SOURCE, rather than trusting supplied AKI
    # or just rerunning the selector against mutable precomputed scores.
    from local_fullnumerical_production import materialize_production
    independently_materialized = materialize_production(source, request, request["required_indices"])
    if build(independently_materialized, source) != selection:
        raise LocalAKIError("INDEPENDENT_RECOMPUTATION_MISMATCH")
    return {"status": "PASS", "selection_sha256": selection["sha256"]}


def decision(request, selection, utility=None):
    q = deepcopy(request)
    q["role_registry"] = [{"runner_id": r, "column": c, "status": "PROTECTED"}
                          for c, col in selection["columns"].items() for r in col["selected"]]
    q["pair_dispositions"] = deepcopy(selection["pair_dispositions"])
    q["third_dispositions"] = deepcopy(selection["third_dispositions"])
    # Existing R3 keeps global P3 tails; no soft exclusion to shrink the portfolio.
    mec = build_mec_plan(q, utility, strict_head_closure=selection["status"] != "NO_BET")
    check = validate_mec_plan(mec)
    if not check["mec_verified"]:
        raise LocalAKIError("MEC_VERIFICATION_FAILED")
    q["aki_information_gate"] = {"action": "PAPER", "status": "UNVALIDATED",
                                 "reason": "LOCAL_NUMERICAL_CONSUMPTION_NOT_PROMOTED"}
    capital = resolve_capital_policy(q, mec)
    if selection["status"] == "NO_BET":
        capital.update(decision="NO_BET", no_bet=True, paper_only=True,
                       terminal_reasons=selection["terminal_reasons"])
        capital.pop("sha256", None)
        capital["sha256"] = sha(capital)
    return {"selection_sha256": selection["sha256"], "mec": mec, "mec_verification": check,
            "capital": capital, "paper_tickets": deepcopy(mec["tickets"]),
            "purchase_tickets": [], "purchase_authority": False}
