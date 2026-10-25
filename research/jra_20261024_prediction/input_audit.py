"""Descriptive research over the original frozen request and KRS summary.

This module neither admits a Source nor changes a Production feature. Missing
segment/tactical measurements remain unknown rather than synthesized.
"""
from collections import Counter

from candidates import ROLES, ROLE_INDEX


def _surface(value):
    return "ダート" if value in {"ダ", "ダート"} else value


def race_input_audit(request, final, projections, baseline_roles):
    source = request["source_snapshot"]
    context = source.get("jra_race_context") or {}
    market = source.get("jra_official_market_observation") or {}
    utility = (final or {}).get("krs_prediction_utility") or {}
    summaries = {str(r["horse_no"]): r for r in utility.get("summary", [])}
    market_rows = {str(r["runner_id"]): r for r in market.get("runners", [])}
    common = source.get("jra_registered_common") or {}
    workout = common.get("workout") or {}
    workout_rows = {str(r["runner_id"]): r for r in workout.get("runners", [])}
    widths = {role: sum(role in x for x in baseline_roles.values()) for role in ROLES}
    selection = {
        name: {
            role: set(arm["ranking"][role][:widths[role]]) for role in ROLES
        }
        for name, arm in projections["arms"].items()
    }
    runners = []
    for runner in request["runners"]:
        horse = str(runner["runner_id"])
        features = runner.get("evidence_features") or {}
        cells = runner["canonical_components"]
        simulation = summaries.get(horse) or {}
        runners.append({
            "runner_id": horse,
            "role_indices": {role: cells[key]["value"]
                             for role, key in ROLE_INDEX.items()},
            "market": {key: market_rows.get(horse, {}).get(key)
                       for key in ["popularity_rank", "win_odds"]},
            "baseline_roles": baseline_roles.get(horse, []),
            "role_migration": {
                name: {
                    "selected_roles": [r for r in ROLES if horse in sel[r]],
                    "P3_TO_W": "P3" in baseline_roles.get(horse, []) and
                               "W" not in baseline_roles.get(horse, []) and
                               horse in sel["W"],
                    "P3_TO_P2": "P3" in baseline_roles.get(horse, []) and
                                "P2" not in baseline_roles.get(horse, []) and
                                horse in sel["P2"],
                    "P2_TO_W": "P2" in baseline_roles.get(horse, []) and
                               "W" not in baseline_roles.get(horse, []) and
                               horse in sel["W"],
                }
                for name, sel in selection.items()
            },
            "frozen_krs": {
                "positions_and_strategy_shares": simulation.get("positions"),
                "role_rates": {key: simulation.get(key) for key in
                               ["SSR-W", "SSR-P2", "SSR-T3"]},
                "not_calibrated_probability": True,
            },
            "observed_feature_counts": {
                key: value.get("observation_count")
                for key, value in features.items()
            },
            "workout_or_start_preparation_features": {
                key: value for key, value in features.items()
                if any(part in key for part in
                       ["workout", "training", "start_preparation", "gate"])
            },
            "registered_workout_observation": {
                key: workout_rows.get(horse, {}).get(key)
                for key in ["assessment", "rating", "course", "final1f",
                            "workout_time_raw", "gait"]
            },
            "registered_workout_gait_equals_horse_name": bool(
                workout_rows.get(horse, {}).get("gait") and
                workout_rows[horse]["gait"] ==
                workout_rows[horse].get("horse_name")),
            "gci_evidence": cells["GCI"].get("components", []),
        })
    same_day = source.get("jra_official_same_day_results") or {}
    prior_races = []
    for race in (same_day.get("races") or {}).values():
        environment = race.get("race_environment") or {}
        prior_races.append({
            "race_no": race.get("race_no"),
            "scheduled_post_hhmm": race.get("scheduled_post_hhmm"),
            "environment": environment,
            "same_surface": _surface(environment.get("surface")) ==
                            _surface(context.get("surface")),
            "same_distance": environment.get("distance_m") ==
                             context.get("distance_m"),
            "same_going": environment.get("going") == context.get("going"),
            "source_snapshot_sha256": race.get("source_snapshot_sha256"),
            "race_sha256": race.get("sha256"),
        })
    world_pairs = utility.get("actionable_ordered_pair_proposals") or []
    world_thirds = utility.get("actionable_pair_third_proposals") or []
    return {
        "race_id": request["race_id"],
        "context": context,
        "source_freeze_at": source["source_freeze_at"],
        "aki_axes": (request.get("static_prediction") or {}).get(
            "aki_jra_v21", {}).get("axes"),
        "aki_information_gate": request.get("aki_information_gate"),
        "market_captured_at": market.get("captured_at"),
        "market_stability_proven": False,
        "market_replacement_rule": "NONE; market is descriptive only",
        "factor_observation_scope": "New factors use JRA_OFFICIAL features only; frozen Static preserves registered-common features",
        "newcomer_workout_coverage": {
            "schema": workout.get("schema"),
            "registered_observations": len(workout_rows),
            "assessment_observations": sum(bool(x.get("assessment")) for x in workout_rows.values()),
            "numeric_final1f_observations": sum(isinstance(x.get("final1f"), (float, int)) for x in workout_rows.values()),
            "clock_observations": sum(bool(x.get("workout_time_raw")) for x in workout_rows.values()),
            "load_paired_response_start_readiness": "UNKNOWN; not synthesized from comments",
        },
        "same_day_gci": {
            "frozen_source_races": prior_races,
            "races": len(prior_races),
            "same_surface_races": sum(x["same_surface"] for x in prior_races),
            "same_surface_distance_going_races": sum(
                x["same_surface"] and x["same_distance"] and x["same_going"]
                for x in prior_races),
            "distance_transfer_validated": False,
            "independent_timestamp_reverification": "OWNER_SOURCE_AUDIT",
        },
        "frozen_krs_worlds": {
            "scenario_names": utility.get("scenario_worlds", []),
            "strategy_names": sorted({
                key for row in summaries.values()
                for key in row.get("positions", {}).get("strategy_share", {})
            }),
            "recorded_pair_world_support": world_pairs,
            "recorded_third_world_support": world_thirds,
            "physics_or_seed_recomputed": False,
            "new_world_created": False,
            "world_specific_outcome_rates": "UNKNOWN; not in saved FINAL summary",
        },
        "mechanism_limits": [
            "No independent speed trajectory or segment timestamps",
            "No validated downhill/hill/rail/straight causal effect",
            "No independent tactical-change labels",
            "Newcomer workout/start-preparation absent remains missing",
        ],
        "runners": runners,
    }


def migration_summary(audits):
    counts = {}
    for race in audits:
        for runner in race["runners"]:
            for name, migration in runner["role_migration"].items():
                count = counts.setdefault(name, Counter())
                for movement in ["P3_TO_W", "P3_TO_P2", "P2_TO_W"]:
                    count[movement] += migration[movement]
    return {name: dict(count) for name, count in counts.items()}
