"""Result-blind JRA selection candidates. No Production or purchase authority.

SELECTION_ONLY reuses the frozen MEC's unordered and exact-three evidence.
WITH_KRS_SETS adds observed joint sets independently of which horse won the
simulation. The stored occurrence list is truncated, so totals are support
within the visible list only. Neither arm estimates probability or EV.
"""
from collections import defaultdict
from math import isfinite

from jra_role_learning_shadow import EVIDENCE_GROUPS, POLICY, digest, instant, ticket_key

PROFILE = "JRA-TRIO-PRIMARY-SELECTION-RESEARCH-v1"
KINDS = {"EXACTA": 2, "TRIO": 3, "TRIFECTA": 3}


def _runner(value):
    if isinstance(value, bool) or not str(value).isascii() or not str(value).isdigit():
        raise ValueError("TRIO_RUNNER_ID_INVALID")
    number = int(value)
    if not 1 <= number <= 18 or str(number) != str(value):
        raise ValueError("TRIO_RUNNER_ID_INVALID")
    return number


def _key(ticket, active):
    kind = ticket["bet_type"]
    selection = tuple(_runner(n) for n in ticket["selection"])
    if kind not in KINDS or len(set(selection)) != KINDS[kind] or len(selection) != KINDS[kind]:
        raise ValueError("TRIO_TICKET_ARITY_INVALID")
    if not set(selection) <= active:
        raise ValueError("TRIO_TICKET_OUTSIDE_ACTIVE")
    return ticket_key(ticket)


def _place_frontier(traces, eligible):
    pairs = {}
    for n in eligible:
        trace = traces.get(str(n), {})
        axes = (trace.get("sri"), trace.get("zai_place"))
        if all(type(v) in (int, float) and isfinite(v) for v in axes):
            pairs[n] = axes
    # Use the two existing measures without numerical weights or a new floor.
    return sorted(n for n, (sri, place) in pairs.items() if not any(
        other_sri >= sri and other_place >= place
        and (other_sri > sri or other_place > place)
        for other_sri, other_place in pairs.values()
    ))


def _observed_sets(utility, active, run_count):
    result = defaultdict(dict)
    for row in utility["top_trifecta_occurrence"]:
        order = tuple(_runner(row[col]) for col in ("W", "P2", "P3"))
        count = row["count"]
        if len(set(order)) != 3 or not set(order) <= active or type(count) is not int or count <= 0:
            raise ValueError("TRIO_KRS_OCCURRENCE_INVALID")
        group = result[tuple(sorted(order))]
        if order in group:
            raise ValueError("TRIO_KRS_DUPLICATE_ORDER")
        group[order] = count
    if sum(sum(rows.values()) for rows in result.values()) > run_count:
        raise ValueError("TRIO_KRS_OCCURRENCE_OVER_RUN_COUNT")
    return result


def _independent_sets(observations, traces, features, hard_orders):
    """Screen joint sets with place evidence and a place axis, without Roles."""
    qualified = {}
    for runner, facts in features.items():
        trace = traces.get(str(runner), {})
        if not all(type(v) in (int, float) and isfinite(v)
                   for v in (trace.get("sri"), trace.get("zai_place"))):
            continue
        positive = {f["feature"]: f["evidence_refs"] for f in facts
                    if f.get("category") in POLICY["positive_categories"]
                    and f.get("evidence_refs") and not f.get("missing")
                    and not f.get("result_derived")}
        groups = {g: sorted(names & positive.keys()) for g, names in EVIDENCE_GROUPS.items()
                  if names & positive.keys()}
        if (len(set().union(*groups.values())) >= POLICY["minimum_distinct_observed_features"]
                and len(groups) >= POLICY["minimum_distinct_evidence_groups"]):
            qualified[runner] = {g: {name: positive[name] for name in names}
                                 for g, names in groups.items()}

    anchors = set(_place_frontier(traces, qualified))
    out = {}
    for sel, orders in observations.items():
        surviving = orders.keys() - hard_orders
        axis_options = sorted(anchors.intersection(sel))
        if axis_options and set(sel) <= qualified.keys() and surviving:
            out[sel] = {
                "single_place_axis_options": axis_options,
                "eligible_visible_joint_occurrences": sum(orders[order] for order in surviving),
                "place_evidence": {str(n): qualified[n] for n in sel},
            }
    return out


def _hard_orders(mec):
    return {tuple(_runner(row[k]) for k in ("head", "second", "third"))
            for row in mec.get("hard_third_exclusions_retained", [])}


def build_candidate(final, *, budget_yen, include_krs_sets=False, preserve_base_single_head=False,
                    include_independent_sets=False):
    """Apply a budget cap without adding exposure to make amounts match."""
    if type(budget_yen) is not int or budget_yen < 0 or budget_yen % 100:
        raise ValueError("TRIO_RESEARCH_BUDGET_INVALID")
    if any(type(flag) is not bool for flag in
           (include_krs_sets, preserve_base_single_head, include_independent_sets)):
        raise ValueError("TRIO_RESEARCH_SCOPE_INVALID")
    if include_krs_sets and include_independent_sets:
        raise ValueError("TRIO_RESEARCH_ARMS_MUST_REMAIN_SEPARATE")
    race = final["race_id"]
    if not race.startswith("KM-JRA-") or final["temporal_mode"] != "FORMAL-PRE-RACE":
        raise ValueError("TRIO_RESEARCH_JRA_FINAL_REQUIRED")
    if final["sha256"] != digest({k: v for k, v in final.items() if k != "sha256"}):
        raise ValueError("TRIO_RESEARCH_FINAL_HASH_MISMATCH")
    static = final["static_prediction"]
    active = {_runner(n) for n in static["ranking"]}
    if len(active) != len(static["ranking"]) or {_runner(n) for n in static["roles"]} != active:
        raise ValueError("TRIO_RESEARCH_ACTIVE_UNIVERSE_MISMATCH")
    ft = final["final_ticket"]
    baseline = {}
    for ticket in ft["tickets"]:
        key = _key(ticket, active)
        stake = ticket["stake"]
        if key in baseline or type(stake) is not int or stake <= 0 or stake % 100:
            raise ValueError("TRIO_RESEARCH_CANONICAL_STAKE_INVALID")
        baseline[key] = ticket
    if sum(t["stake"] for t in baseline.values()) != ft["total_investment"]:
        raise ValueError("TRIO_RESEARCH_FROZEN_INVESTMENT_MISMATCH")
    receipt = final["krs_run_receipt"]
    utility = final["krs_prediction_utility"]
    run_count = receipt["receipt"]["actual_run_count"]
    if (receipt["receipt"]["race_id"] != race or utility["race_id"] != race
            or type(run_count) is not int or run_count <= 0):
        raise ValueError("TRIO_RESEARCH_KRS_BINDING")
    observations = _observed_sets(utility, active, run_count)
    roles = {int(n): set(cols) for n, cols in static["roles"].items()}
    placed = {n for n, cols in roles.items() if cols & {"W", "P2", "P3"}}
    traces = final["final_prediction_package"]["index_provenance_replay"]["runners"]
    anchors = _place_frontier(traces, placed)
    mec = final["minimum_efficient_coverage"]
    # The pre-capital MEC is available even for PAPER. Keep it as diagnostic
    # evidence while the original gate still determines zero exposure.
    units = {u["id"]: u for u in mec["coverage_units"]}
    sets = defaultdict(set)
    for ticket in mec["tickets"]:
        kind, sel = _key(ticket, active)
        evidence_kinds = {units[uid]["kind"] for uid in ticket["coverage_ids"]}
        if kind == "TRIO" and "TAIL_SET" in evidence_kinds:
            sets[sel].add("FROZEN_UNORDERED_SET")
        elif kind == "TRIFECTA" and "EXACT_THIRD" in evidence_kinds:
            sets[tuple(sorted(sel))].add("FROZEN_EXACT_SET_PROJECTION")
    if include_krs_sets or include_independent_sets:
        hard_orders = _hard_orders(mec)
    if include_krs_sets:
        for sel, orders in observations.items():
            if (set(sel) <= placed and set(sel).intersection(anchors)
                    and orders.keys() - hard_orders):
                sets[sel].add("KRS_JOINT_SET_PLACE_FRONTIER")
    independent = {}
    if include_independent_sets:
        if {_runner(n) for n in traces} != active:
            raise ValueError("TRIO_RESEARCH_PLACE_UNIVERSE_MISMATCH")
        features = {int(n): [c for index in trace["base_index_trace"].values()
                             for c in index.get("components", [])]
                    for n, trace in traces.items()}
        independent = _independent_sets(observations, traces, features, hard_orders)
        for sel in independent:
            sets[sel].add("INDEPENDENT_JOINT_PLACE_SUPPORT")

    def support(sel):
        return sum(observations.get(sel, {}).values())

    ordered_sets = sorted(sets, key=lambda sel: (
        ("TRIO", sel) not in baseline,
        "FROZEN_UNORDERED_SET" not in sets[sel],
        -(independent[sel]["eligible_visible_joint_occurrences"] if sel in independent else support(sel)),
        sel,
    ))
    gate = final["capital_policy_decision"]
    if type(gate.get("capital_limit")) is int:
        budget_yen = min(budget_yen, gate["capital_limit"])
    paper = gate.get("paper_only") is True
    no_bet = paper or gate.get("no_bet") is True or ft.get("no_bet") is True
    remaining = 0 if no_bet else budget_yen
    tickets = []
    rejected = []
    ordered_exceptions = []
    pair_support = {(_runner(row["W"]), _runner(row["P2"]))
                    for row in utility["top_exacta_occurrence"] if row["count"] > 0}
    exact_pairs = {sel[:2] for kind, sel in baseline if kind == "TRIFECTA"}
    aki = final["final_prediction_package"]["aki_column_selection"]
    base_single_head = (preserve_base_single_head and len(aki["columns"]["W"]) == 1
                        and aki["triggers"] == {"W": "BASE", "P2": "BASE", "P3": "BASE"})
    ordered_additions = []
    for (kind, sel), ticket in baseline.items():
        if kind == "TRIO":
            continue
        expected = "EXACT_THIRD" if kind == "TRIFECTA" else "ORDERED_PAIR"
        if not any(uid in units and units[uid]["tier"] == "CORE" and units[uid]["kind"] == expected
                   and tuple(_runner(n) for n in units[uid]["parts"]) == sel
                   for uid in ticket.get("coverage_ids", [])):
            continue
        if kind == "TRIFECTA":
            counts = observations.get(tuple(sorted(sel)), {})
            supported = counts.get(sel, 0) > max((n for key, n in counts.items() if key != sel), default=0)
        else:
            supported = sel in pair_support
        if not supported:
            continue
        row = {"bet_type": kind, "selection": list(sel), "stake": ticket["stake"]}
        if base_single_head or (kind == "EXACTA" and sel not in exact_pairs):
            ordered_exceptions.append({
                **row,
                "reason": "BASE_SINGLE_W_AND_OBSERVED_ORDER" if base_single_head
                else "REGISTERED_PAIR_WITHOUT_ORDERED_THIRD",
            })
        else:
            ordered_additions.append(row)

    trio_stake = mec["minimum_unit_stake"]
    if type(trio_stake) is not int or trio_stake <= 0 or trio_stake % 100:
        raise ValueError("TRIO_RESEARCH_STAKE_UNIT_INVALID")

    # Preserve native trios before funding independently supported ordered
    # exceptions, then consider the remaining unordered combinations.
    native = [sel for sel in ordered_sets if ("TRIO", sel) in baseline]
    additions = [sel for sel in ordered_sets if ("TRIO", sel) not in baseline]
    stream = (
        [{"bet_type": "TRIO", "selection": list(sel), "stake": baseline[("TRIO", sel)]["stake"]}
         for sel in native]
        + [{k: v for k, v in row.items() if k != "reason"} for row in ordered_exceptions]
        + [{"bet_type": "TRIO", "selection": list(sel), "stake": trio_stake} for sel in additions]
        + ordered_additions
    )
    for row in stream:
        if row["stake"] > remaining:
            if row["bet_type"] == "TRIO":
                rejected.append(row["selection"])
            continue
        tickets.append(row)
        remaining -= row["stake"]

    trio_sets = [set(t["selection"]) for t in tickets if t["bet_type"] == "TRIO"]
    out = {
        "profile": PROFILE, "race_id": race, "baseline_final_sha256": final["sha256"],
        "source_sha256": final["source_snapshot_sha256"], "cutoff": final["prediction_cutoff"],
        "krs_receipt_sha256": receipt["receipt_sha256"], "krs_utility_sha256": utility["sha256"],
        "arm": "INDEPENDENT_JOINT_PLACE" if include_independent_sets else
               "WITH_KRS_SETS" if include_krs_sets else "SELECTION_ONLY",
        "budget_yen": budget_yen, "preserve_base_single_head": preserve_base_single_head, "tickets": tickets,
        "total_investment": sum(t["stake"] for t in tickets),
        "paper": paper, "no_bet": no_bet,
        "place_frontier": anchors,
        "common_trio_horses": sorted(set.intersection(*trio_sets)) if trio_sets else [],
        "trio_candidates": [
            {"set": list(sel), "evidence": sorted(sets[sel]), "visible_joint_occurrences": support(sel),
             "has_visible_winner_outside_official_w": any("W" not in roles[order[0]]
                                                          for order in observations.get(sel, {})),
             **({"independent_place": independent[sel]} if sel in independent else {})}
            for sel in ordered_sets
        ],
        "trio_candidates_unfunded": rejected,
        "ordered_exception_evidence": ordered_exceptions,
        "price_eligibility": "NOT_EVALUATED",
        "capture_authority": "RESEARCH_ONLY_REQUIRES_SEPARATE_PRE_RESULT_WITNESS",
        "signature_trust": "CALLER_MUST_VERIFY_ARCHIVED_FINAL_AND_KRS_SIGNATURES",
        "production_effect": "NONE", "purchase_authority": False, "oos_eligible": False,
    }
    out["sha256"] = digest(out)
    return out


def build_pair_gap_reference(gap, pre, final, *, signer, budget_yen):
    """Result-blind replay of the separate, previously frozen Candidate lane.

    The caller provides trust anchored outside these inputs and an immutable
    archive. The Production gap establishes the failure and common SOURCE;
    its indices are never mixed with the Candidate simulator's indices.
    """
    from jra_candidate_krs_plan import ENGINE_SHA256, INPUT_CLASS, MODE_BY_COUNT
    from jra_presentation import _receipt
    from jra_source_candidate_oos import _compact_objective_trace

    if type(budget_yen) is not int or budget_yen < 0 or budget_yen % 100:
        raise ValueError("TRIO_RESEARCH_BUDGET_INVALID")
    source = gap["source_checkpoint_manifest"]
    objective = final["candidate_source_objective_shadow"]
    utility, mec, gate = (final[k] for k in ("krs_utility", "mec", "capital"))
    for obj in (gap, source, pre, final, objective, utility, mec, gate):
        if obj["sha256"] != digest({k: v for k, v in obj.items() if k != "sha256"}):
            raise ValueError("TRIO_RESEARCH_FROZEN_HASH_MISMATCH")
    race = gap["race_id"]
    terminal = gap["production_blocker_classification"]["terminal_route"]
    active = {_runner(n) for n in gap["runner_universe"]}
    if (not race.startswith("KM-JRA-") or len(active) != len(gap["runner_universe"])
            or gap["production_full_numerical_ready"] is not True
            or gap["verified_full_index_count"] != 20 * len(active)
            or gap["first_blocked_stage"] != "PRODUCTION_AKI_COLUMN_SELECTION"
            or gap["auto_handoff_error"] != "AKI_SELECTED_HEAD_WITHOUT_MATERIAL_PAIR"
            or terminal != "FAIL_CLOSED_NO_TERMINAL"):
        raise ValueError("TRIO_RESEARCH_PAIR_GAP_REQUIRED")
    if (any(obj["race_id"] != race for obj in (source, pre, final, utility, mec))
            or any(obj["source_snapshot_sha256"] != source["source_snapshot_sha256"]
                   for obj in (pre, final, objective))
            or pre["sha256"] != final["oos_pre_result_record_sha256"]
            or pre["candidate_krs_utility_sha256"] != utility["sha256"]
            or pre["candidate_krs_utility_shadow"] != utility
            or pre["candidate_mec_sha256"] != mec["sha256"]
            or pre["current_authority_manifest"] != gap["current_authority_manifest"]
            or pre["candidate_objective_trace"] != _compact_objective_trace(final)
            or final["candidate_source_objective_sha256"] != objective["sha256"]
            or gate["mec_sha256"] != mec["sha256"]
            or final["candidate_only"] is not True or final["production_effect"] != "NONE"
            or pre["candidate_final_verified"] is not True or pre["acceptance_only"] is not False
            or final["temporal_mode"] != "FORMAL-PRE-RACE"
            or pre["scheduled_post_at"] != final["scheduled_post_at"]):
        raise ValueError("TRIO_RESEARCH_CANDIDATE_ARCHIVE_BINDING")
    prepared = _receipt(final["pre_krs_receipt"], signer, race, "PRE_KRS")
    krs = _receipt(final["krs_run_receipt"], signer, race, "KRS")
    signed_final = _receipt(final["final_receipt"], signer, race, "FINAL")
    run_count = krs["actual_run_count"]
    if (prepared["receipt_sha256"] != pre["candidate_pre_krs_receipt_sha256"]
            or krs["receipt_sha256"] != pre["candidate_krs_receipt_sha256"]
            or signed_final["receipt_sha256"] != pre["candidate_final_receipt_sha256"]
            or signed_final["timestamp"] != pre["candidate_final_receipt_timestamp"]
            or krs["engine_sha256"] != ENGINE_SHA256 or krs["input_class"] != INPUT_CLASS
            or run_count != pre["candidate_krs_actual_run_count"]
            or run_count != utility["snapshot"]["run_count"]
            or run_count != krs["requested_run_count"] or MODE_BY_COUNT.get(run_count) != krs["mode"]
            or krs["seed"] != utility["snapshot"]["master_seed"]
            or not (instant(source["source_freeze_at"]) <= instant(pre["frozen_at"])
                    <= instant(prepared["timestamp"]) <= instant(krs["timestamp"])
                    <= instant(signed_final["timestamp"]) <= instant(source["prediction_cutoff"])
                    < instant(pre["scheduled_post_at"]))):
        raise ValueError("TRIO_RESEARCH_CANDIDATE_RECEIPT_BINDING")
    runners = objective["runners"]
    numerical = final["candidate_numerical_summary"]
    ranking = list(map(_runner, final["static_prediction"]["ranking"]))
    if (set(ranking) != active or len(ranking) != len(active)
            or list(map(_runner, pre["ranking"])) != ranking
            or {_runner(n) for n in runners} != active
            or numerical["source_objective_sha256"] != objective["sha256"]
            or numerical["source_snapshot_sha256"] != source["source_snapshot_sha256"]
            or numerical["full_numerical_complete"] is not True
            or numerical["calculated_count"] != 20 * len(active)
            or any(len(r["all_20_diagnostic_values"]) != 20
                   or any(type(v) not in (int, float) or not isfinite(v)
                          for v in r["all_20_diagnostic_values"].values())
                   or any(r["derived_indices"][k] != r["all_20_diagnostic_values"][k]
                          for k in ("SRI", "ZAI_PLACE"))
                   for r in runners.values())):
        raise ValueError("TRIO_RESEARCH_CANDIDATE_FULL20_OR_UNIVERSE_MISMATCH")
    traces = {n: {"sri": r["derived_indices"]["SRI"], "zai_place": r["derived_indices"]["ZAI_PLACE"]}
              for n, r in runners.items()}
    features = {int(n): r["features"].values() for n, r in runners.items()}
    sets = _independent_sets(_observed_sets(utility, active, run_count), traces, features, _hard_orders(mec))
    sets = sorted(sets.items(), key=lambda row: (-row[1]["eligible_visible_joint_occurrences"], row[0]))

    stake, cap = mec["minimum_unit_stake"], gate["capital_limit"]
    if (type(stake) is not int or stake <= 0 or stake % 100
            or type(cap) is not int or cap < 0 or cap % 100):
        raise ValueError("TRIO_RESEARCH_ARCHIVED_CAPITAL_INVALID")
    budget_yen = min(budget_yen, cap)
    zero_exposure = gate["paper_only"] is True or gate["no_bet"] is True
    slots = 0 if zero_exposure else budget_yen // stake
    tickets = [{"bet_type": "TRIO", "selection": list(sel), "stake": stake} for sel, _ in sets[:slots]]
    out = {
        "profile": PROFILE, "arm": "PAIR_GAP_INDEPENDENT_JOINT_PLACE",
        "race_id": race, "source_sha256": source["source_snapshot_sha256"],
        "cutoff": source["prediction_cutoff"], "source_gap_sha256": gap["sha256"],
        "production_terminal": terminal, "candidate_final_sha256": final["sha256"],
        "candidate_krs_receipt_sha256": krs["receipt_sha256"], "candidate_run_count": run_count,
        "candidate_receipt_signatures_verified": True, "budget_yen": budget_yen, "tickets": tickets,
        "total_investment": sum(t["stake"] for t in tickets), "paper_gate": zero_exposure,
        "trio_candidates": [{"set": list(sel), **proof} for sel, proof in sets],
        "research_terminal": ("SOURCE_CANDIDATE_PAPER_GATE" if zero_exposure else
                              "VIRTUAL_SELECTION" if tickets else
                              "CAP_INSUFFICIENT" if sets else "NO_QUALIFIED_JOINT_SET"),
        "formation_scope": "ONE_PLACE_AXIS_OPTIONS_ONLY_NO_TWO_AXIS_FIXED_AUTHORITY",
        "price_eligibility": "NOT_EVALUATED", "production_effect": "NONE",
        "purchase_authority": False, "oos_eligible": False,
    }
    out["sha256"] = digest(out)
    return out
