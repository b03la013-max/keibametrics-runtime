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
    mode = request.get("aki_column_candidate")
    if mode is not None and mode not in {"HEAD_LOCAL_VNEXT_R1", "HEAD_LOCAL_VNEXT_R2"}:
        raise LocalAKIError("UNKNOWN_CANDIDATE_MODE")
    candidate = mode in {"HEAD_LOCAL_VNEXT_R1", "HEAD_LOCAL_VNEXT_R2"}
    # These historical policies failed performance acceptance. Keep their
    # exact replay calculations available, but never admit a new forward arm
    # merely because a caller supplies a future plan or changes its label.
    if candidate and request.get("aki_temporal_mode") == "FORWARD_PAPER":
        raise LocalAKIError("PERFORMANCE_REJECTED_ARM_FORWARD_FORBIDDEN:" + mode)
    original_roles = request.get("role_registry") or []
    allowed = {c: {str(r["runner_id"]) for r in original_roles
                    if r.get("column") == c and r.get("status") in
                    {"CORE", "PROTECTED", "CONDITIONAL", "RESIDUAL", "TAIL_PROTECTED"}}
               for c in ("W", "P2", "P3")}
    if candidate and not original_roles:
        raise LocalAKIError("FROZEN_PREDICTION_UNIVERSE_REQUIRED")
    by_id = {str(r["runner_id"]): r for r in runners}
    audit = {}
    scores = {c: {} for c in ("W", "P2", "P3")}
    axes = {}
    observed_field_scores = {c: {} for c in ("W", "P2", "P3")}
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
                observed_field_scores[c][rid] = number(cc[index]["value"])
                if not candidate or rid in allowed[c]:
                    scores[c][rid] = observed_field_scores[c][rid]

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
        role_span = high - low
        span = role_span
        if mode == "HEAD_LOCAL_VNEXT_R2" and c == "W":
            field = observed_field_scores[c]
            # Preserve the existing FIELD-relative reference scale. Role
            # admission limits who may be selected, not the score unit.
            span = max(field.values()) - min(field.values())
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

    if mode == "HEAD_LOCAL_VNEXT_R2":
        diagnostics["W"]["normalization_scope"] = "FULL_OBSERVED_ACTIVE_FIELD"
        diagnostics["W"]["admission_scope"] = "FROZEN_W_ROLE_UNIVERSE"
        diagnostics["W"]["role_score_span"] = (max(scores["W"].values()) - min(scores["W"].values())) if scores["W"] else None
        diagnostics["W"]["normalization_scores"] = observed_field_scores["W"]
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
    conditional_audit = None
    if candidate:
        # Reuse the existing continuous score-gap rule, within each frozen
        # material context. No result, odds, budget or new threshold enters it.
        def conditional(column, pool):
            values = {r: scores[column][r] for r in pool if r in scores[column]}
            if not values:
                return [], {"status": "NO_OBSERVED_ELIGIBLE_ROLE", "pool": []}
            order = sorted(values, key=lambda r: (-values[r], int(r)))
            leader = order[0]
            risk = max(axes[leader][p["role_axes"][column]], axes[leader]["RSI"])
            span = max(values.values()) - min(values.values())
            selected = [r for r in order if values[leader] - values[r] <= span * risk / 100]
            return selected, {"pool": order, "leader": leader, "risk": risk,
                              "score_span": span, "gap_limit": span * risk / 100,
                              "selected": selected}
        original_pairs = deepcopy(request.get("pair_dispositions") or [])
        original_thirds = deepcopy(request.get("third_dispositions") or [])
        pairs, thirds = [], []
        conditional_audit = {"heads": {}, "pairs": {}, "excluded_pairs": [],
                             "excluded_thirds": [], "prediction_universe_sha256": sha({
                                 "roles": original_roles, "pairs": original_pairs,
                                 "thirds": original_thirds}), "market_support": "NOT_USED / PRICE_MISSING"}
        for h in columns["W"]["selected"]:
            material = [x for x in original_pairs if str(x["head"]) == h
                        and str(x["second"]) != h and x.get("status") in {"PURCHASE", "PROTECT"}]
            selected, detail = conditional("P2", {str(x["second"]) for x in material})
            conditional_audit["heads"][h] = detail
            for x in material:
                second = str(x["second"])
                worlds = [t for t in original_thirds if str(t["head"]) == h and str(t["second"]) == second]
                if second not in selected:
                    conditional_audit["excluded_pairs"].append({**x,
                        "exclusion_reason": "COLUMN_GAP" if second in scores["P2"] else "NO_OBSERVED_ROLE_SUPPORT",
                        "lost_third_worlds": worlds, "removed_capital": None,
                        "krs_support": "MEASURE_AFTER_KRS / NOT_SELECTION_INPUT"})
                    continue
                pairs.append(x)
                pool = {str(t["third"]) for t in worlds if t.get("status") in {"PURCHASE", "PROTECT"}
                        and str(t["third"]) not in {h, second}}
                chosen, td = conditional("P3", pool)
                conditional_audit["pairs"][h + ">" + second] = td
                for t in worlds:
                    if str(t["third"]) in chosen and t.get("status") in {"PURCHASE", "PROTECT"}:
                        thirds.append(t)  # preserve Exact vs set protection
                    else:
                        conditional_audit["excluded_thirds"].append({**t,
                            "exclusion_reason": "SEMANTIC_ONLY" if t.get("status") not in {"PURCHASE", "PROTECT"}
                            else "COLUMN_GAP" if str(t["third"]) in scores["P3"] else "NO_OBSERVED_ROLE_SUPPORT"})
        for c, key, rows in (("P2", "second", pairs), ("P3", "third", thirds)):
            selected = sorted({str(x[key]) for x in rows}, key=int)
            columns[c] = {"main": selected, "additional": [], "selected": selected,
                          "selection_scope": "CONDITIONAL_UNION / SEE_LOCAL_DIAGNOSTICS"}
    missing_heads = set(columns["W"]["selected"]) - {x["head"] for x in pairs if x["status"] in {"PROTECT", "PURCHASE"}}
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
    if candidate:
        out["candidate_arm"] = mode
        out["conditional_audit"] = conditional_audit
        out["policy_sha256"] = sha({"original_policy": p, "candidate_mode": mode})
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
    if selection.get("candidate_arm"):
        q["role_registry"] = [deepcopy(r) for r in request["role_registry"]
                              if str(r["runner_id"]) in selection["columns"].get(r["column"], {}).get("selected", [])]
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
    requested_capital = q.get("capital_policy") or {}
    budget_abstention = (capital.get("compatibility") == "INCOMPATIBLE"
        and str(requested_capital.get("insufficient_action") or "NO_BET").upper() == "NO_BET")
    abstain = selection["status"] == "NO_BET" or budget_abstention
    if abstain:
        capital.update(decision="NO_BET", no_bet=True, paper_only=True,
                       terminal_reasons=selection["terminal_reasons"] +
                           (["REGISTERED_RACE_BUDGET_INSUFFICIENT"] if budget_abstention else []))
        capital.pop("sha256", None)
        capital["sha256"] = sha(capital)
    out = {"selection_sha256": selection["sha256"], "mec": mec, "mec_verification": check,
           "capital": capital, "paper_tickets": ([] if abstain else deepcopy(mec["tickets"])),
           "purchase_tickets": [], "purchase_authority": False}
    if selection.get("candidate_arm"):
        pair_keys = {(str(x["head"]), str(x["second"])) for x in selection["pair_dispositions"]}
        third_keys = {(str(x["head"]), str(x["second"]), str(x["third"])) for x in selection["third_dispositions"]}
        cells = []
        for row in request.get("pair_dispositions") or []:
            h, s = str(row["head"]), str(row["second"])
            kept = (h, s) in pair_keys and not abstain
            reason = ("KEPT_ORIGINAL_MATERIALITY" if kept else "NO_BET" if abstain
                      else "NON_MATERIAL_PAIR" if row.get("status") not in {"PURCHASE", "PROTECT"}
                      else "HEAD_COLUMN_NONSELECTED" if h not in selection["columns"]["W"]["selected"]
                      else "P2_OBSERVED_SUPPORT_MISSING" if s not in selection["eligible_role_scores"]["P2"]
                      else "HEAD_LOCAL_P2_SCORE_GAP")
            worlds = []
            for third in request.get("third_dispositions") or []:
                if (str(third["head"]), str(third["second"])) != (h, s):
                    continue
                t = str(third["third"])
                retained = kept and (h, s, t) in third_keys
                worlds.append({**deepcopy(third), "retained": retained,
                    "decision_reason": "KEPT_ORIGINAL_ORIENTATION" if retained else "PAIR_NONSELECTED" if not kept
                    else "NON_MATERIAL_THIRD" if third.get("status") not in {"PURCHASE", "PROTECT"}
                    else "P3_OBSERVED_SUPPORT_MISSING" if t not in selection["eligible_role_scores"]["P3"]
                    else "PAIR_LOCAL_P3_SCORE_GAP"})
            cells.append({**deepcopy(row), "retained": kept, "decision_reason": reason,
                          "third_worlds": worlds, "removed_capital": None,
                          "capital_measurement_status": "BASELINE_SIGNED_TICKET_BINDING_REQUIRED",
                          "market_support": "UNKNOWN / VERIFIED_PRESTART_PRICE_PANEL_NOT_SUPPLIED",
                          "krs_support": [deepcopy(x) for x in (utility or {}).get("actionable_ordered_pair_proposals", [])
                                          if (str(x["head"]), str(x["second"])) == (h, s)]})
        out["conversion_audit"] = {"status": "PAPER_MEASUREMENT / NOT_SELECTION_INPUT",
                                   "selection_sha256": selection["sha256"], "pair_cells": cells,
                                   "prediction_universe_sha256": selection["conditional_audit"]["prediction_universe_sha256"]}
        out["conversion_audit"]["sha256"] = sha(out["conversion_audit"])
    return out
