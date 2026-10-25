"""Small, regularized pedigree/environment research model; never Production BVI.

The labels are the normalized finishing positions printed in verified official
horse histories. They are NOT independently race-ID-verified training labels.
Until permanent identities and independent labels exist this is an exploratory
regularized baseline, not a hierarchical Bayesian model or a promoted policy.

One composite horse has total weight one. Class, field size, environment main
effects and strictly earlier individual form are fitted before parent effects.
Parent/environment interactions fit only the remaining residual. The fixed
protocol is not tuned on the historical validation/test partitions. Opponent
strength is unavailable: neither causal pedigree effects nor calibrated win
probabilities are claimed.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timezone
import copy
import hashlib
import json
import math
from statistics import mean
from pathlib import Path

from jra_owner_authorized_feature_rules import class_rank

PROFILE = "KM-JRA-BVI-ENV-SHADOW-v1-20261024"
VENUES = frozenset(("札幌", "函館", "福島", "新潟", "東京", "中山", "中京", "京都", "阪神", "小倉"))
GOINGS = frozenset(("良", "稍重", "重", "不良"))
PROTOCOL = {
    "profile": PROFILE,
    "model": "ORDERED_RESIDUAL_WEIGHTED_RIDGE_WITH_COMPOSITE_HORSE_CLUSTERS",
    "stage_order": ["CONTROL", "GENERAL", "ENVIRONMENT"],
    "penalty": {"CONTROL": 4.0, "GENERAL": 12.0, "ENVIRONMENT": 24.0,
                "SIRE_DAMSIRE_PAIR": 32.0},
    "minimum_runs": 12, "minimum_composite_offspring": 4,
    "distance_bucket_metres": 400, "coordinate_descent_sweeps": 400,
    "tolerance": 1e-10,
    "control_optimizer": "DENSE_CHOLESKY_CONTROL_STRICT_NORMAL_EQUATION_RESIDUAL",
    "label": "1-(finish-1)/(field_size-1)",
    "horse_weight": "1 / number_of_training_runs_of_exact_composite_horse",
    "ability": "shrunk_mean_of_strictly_earlier_label_dates; 3 neutral prior observations",
    "weather_policy": "EXCLUDED_PENDING_INDEPENDENT_INCREMENTAL_VALUE_AND_RACE_BINDING",
    "course_geometry_policy": "NO_INFERENCE_FROM_VENUE; EXPLICIT_MISSING",
    "opponent_strength": "UNAVAILABLE_NOT_CONTROLLED",
    "permanent_identity": "UNRESOLVED; NO_PRODUCTION_TRAINING_ELIGIBILITY",
    "historical_split_label_dates": ["2026-08-01", "2026-09-01", "2026-10-24"],
    "hyperparameter_optimization": False,
    "automatic_promotion": False,
}


def sha(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()


PROTOCOL_SHA256 = sha(PROTOCOL)


def _day(value):
    try:
        return date.fromisoformat(str(value))
    except (ValueError, TypeError):
        raise ValueError("BVI_ENV_LABEL_DATE_INVALID") from None


def _time(value):
    try:
        value = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if value.tzinfo is None:
            raise ValueError
        return value.astimezone(timezone.utc)
    except (ValueError, TypeError):
        raise ValueError("BVI_ENV_ACQUISITION_TIME_INVALID") from None


def _normal_finish(row):
    try:
        finish, field = int(row["finish"]), int(row["field_size"])
        if not 2 <= field <= 30 or not 1 <= finish <= field:
            raise ValueError
        return 1.0 - (finish - 1.0) / (field - 1.0)
    except (ValueError, TypeError, KeyError):
        raise ValueError("BVI_ENV_LABEL_INVALID") from None


def _run_key(row):
    # A race-name/date/course tuple is a provisional identity, not official ID.
    return (str(row.get("horse_id") or ""), str(row.get("date") or ""),
            str(row.get("venue") or ""), str(row.get("surface") or ""),
            row.get("distance_m"), str(row.get("race_name") or ""))


def _eligible_rows(dataset):
    """Recheck temporal bounds without pretending capture preceded label split."""
    cutoff = _time(dataset.get("prediction_cutoff"))
    target_day = _day(dataset.get("race_date"))
    unique, conflicts, going_conflicts = {}, set(), set()
    excluded = Counter()
    for raw in dataset.get("rows") or []:
        if not isinstance(raw, dict):
            raise ValueError("BVI_ENV_ROW_INVALID")
        captured = _time(raw.get("available_at"))
        if captured > cutoff:
            raise ValueError("BVI_ENV_POST_CUTOFF_ACQUISITION")
        when = _day(raw.get("date"))
        if when >= target_day:
            raise ValueError("BVI_ENV_TARGET_OR_FUTURE_LABEL")
        if raw.get("research_label_eligible") is False:
            excluded["RESEARCH_LABEL_PROVENANCE_QUARANTINED"] += 1
            continue
        if not raw.get("horse_id"):
            excluded["MISSING_COMPOSITE_HORSE_ID"] += 1
            continue
        if raw.get("venue") not in VENUES or raw.get("surface") not in ("芝", "ダ"):
            excluded["NON_JRA_CENTRAL_FLAT_CONTEXT"] += 1
            continue
        try:
            distance = int(raw.get("distance_m"))
            if not 800 <= distance <= 4500:
                raise ValueError
            target = _normal_finish(raw)
        except (ValueError, TypeError):
            excluded["INVALID_DISTANCE_OR_LABEL"] += 1
            continue
        row = copy.deepcopy(raw)
        row["distance_m"] = distance
        row["target"] = target
        row["class_rank"] = class_rank(row.get("race_name"))
        row["going"] = row.get("going") if row.get("going") in GOINGS else None
        key = _run_key(row)
        if key in conflicts:
            continue
        old = unique.get(key)
        label_identity = (row["target"], row.get("sire"), row.get("dam"), row.get("damsire"))
        if old is not None:
            previous = (old["target"], old.get("sire"), old.get("dam"), old.get("damsire"))
            if previous != label_identity:
                conflicts.add(key)
                unique.pop(key)
                excluded["CONFLICTING_DUPLICATE_KEY"] += 1
            else:
                excluded["DUPLICATE_SAME_HORSE_RUN"] += 1
                if old.get("going") and row.get("going") and old["going"] != row["going"]:
                    going_conflicts.add(key)
                    excluded["CONFLICTING_DUPLICATE_GOING"] += 1
                if key in going_conflicts:
                    old["going"] = None
                elif not old.get("going") and row.get("going"):
                    old["going"] = row["going"]
                # Multiple captured copies do not move knowledge backwards.
                if _time(row["available_at"]) > _time(old["available_at"]):
                    old["available_at"] = row["available_at"]
            continue
        unique[key] = row
    rows = sorted(unique.values(), key=lambda r: (_day(r["date"]), _run_key(r)))
    # Batch by day; a second observation on the same label date cannot leak.
    sums, counts = defaultdict(float), Counter()
    by_day = defaultdict(list)
    for row in rows:
        by_day[row["date"]].append(row)
    for day in sorted(by_day):
        for row in by_day[day]:
            h = row["horse_id"]
            row["prior_ability"] = (sums[h] + 1.5) / (counts[h] + 3)
            row["prior_ability_runs"] = counts[h]
        for row in by_day[day]:
            h = row["horse_id"]
            sums[h] += row["target"]
            counts[h] += 1
    return rows, dict(excluded)


def _term(factor, *values):
    return json.dumps([factor, *values], ensure_ascii=False, separators=(",", ":"))


def _features(row, stage):
    surface, venue, going = row.get("surface"), row.get("venue"), row.get("going")
    distance = row.get("distance_m")
    bucket = int(distance) // 400 * 400 if isinstance(distance, (int, float)) else None
    if stage == "CONTROL":
        out = {_term("intercept"): 1.0,
               _term("class", row.get("class_rank")): 1.0,
               _term("prior_ability"): float(row.get("prior_ability", 0.5)) - 0.5}
        if isinstance(row.get("field_size"), (int, float)):
            out[_term("field_size")] = (float(row["field_size"]) - 12) / 12
        for factor, value in (("surface", surface), ("venue", venue),
                              ("distance", bucket), ("going", going)):
            if value is not None and value != "":
                out[_term(factor, value)] = 1.0
        return out
    out = {}
    for parent_type in ("sire", "damsire"):
        parent = row.get(parent_type)
        if not parent:
            continue
        if stage == "GENERAL":
            out[_term(parent_type, str(parent))] = 1.0
        else:
            for factor, value in (("surface", surface), ("venue", venue),
                                  ("distance", bucket), ("going", going)):
                if value is not None and value != "":
                    # Going is never pooled indiscriminately between turf/dirt.
                    out[_term(parent_type + "_" + factor, str(parent), surface, value)] = 1.0
    if stage == "GENERAL" and row.get("sire") and row.get("damsire"):
        out[_term("sire_damsire_pair", str(row["sire"]), str(row["damsire"]))] = 1.0
    return out


def _fit_stage(rows, weights, residual, stage):
    columns, offspring = defaultdict(list), defaultdict(set)
    for i, row in enumerate(rows):
        for key, value in _features(row, stage).items():
            if value:
                columns[key].append((i, value))
                offspring[key].add(row["horse_id"])
    supported, rejected = {}, Counter()
    for key in sorted(columns):
        members = columns[key]
        if stage != "CONTROL" and (len(members) < PROTOCOL["minimum_runs"]
                                   or len(offspring[key]) < PROTOCOL["minimum_composite_offspring"]):
            rejected[json.loads(key)[0]] += 1
            continue
        supported[key] = members
    if stage == "CONTROL":
        return _fit_control_cholesky(rows, weights, residual, supported, offspring)
    fitted = [0.0] * len(rows)
    coefs = {k: 0.0 for k in supported}
    max_delta = 0.0
    sweeps = 0
    for sweep in range(PROTOCOL["coordinate_descent_sweeps"]):
        max_delta = 0.0
        for key, members in supported.items():
            factor = json.loads(key)[0]
            penalty = 0.0 if factor == "intercept" else PROTOCOL["penalty"][stage]
            if factor == "sire_damsire_pair":
                penalty = PROTOCOL["penalty"]["SIRE_DAMSIRE_PAIR"]
            old = coefs[key]
            denom = sum(weights[i] * value * value for i, value in members) + penalty
            numer = sum(weights[i] * value * (residual[i] - fitted[i] + old * value)
                        for i, value in members)
            new = numer / denom if denom else 0.0
            delta = new - old
            for i, value in members:
                fitted[i] += delta * value
            coefs[key] = new
            max_delta = max(max_delta, abs(delta))
        sweeps = sweep + 1
        if max_delta < PROTOCOL["tolerance"]:
            break
    terms = []
    for key in sorted(supported):
        members = supported[key]
        terms.append({"term": key, "factor": json.loads(key)[0],
                      "coefficient": round(coefs[key], 12),
                      "support": {"runs": len(members), "composite_offspring": len(offspring[key]),
                                  "effective_weight": round(sum(weights[i] for i, _ in members), 8)}})
    return {"terms": terms, "unsupported_groups": dict(rejected), "sweeps": sweeps,
            "converged": max_delta < PROTOCOL["tolerance"], "last_max_delta": max_delta}, fitted


def _solve_spd(matrix, rhs):
    """Deterministic dense Cholesky, only for the small CONTROL design.

    Parent/interactions keep the sparse solver. CONTROL has few categorical
    terms but nearly redundant category/intercept offsets: solving its exact
    same ridge normal equations avoids slow coordinate drift. No penalty,
    feature, target, label split or result-based tuning changes.
    """
    n = len(rhs)
    lower = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            value = matrix[i][j] - math.fsum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                if not math.isfinite(value) or value <= 0:
                    raise ValueError("BVI_ENV_CONTROL_NORMAL_MATRIX_NOT_SPD")
                lower[i][j] = math.sqrt(value)
            else:
                lower[i][j] = value / lower[j][j]
    forward = [0.0] * n
    for i in range(n):
        forward[i] = (rhs[i] - math.fsum(lower[i][j] * forward[j] for j in range(i))) / lower[i][i]
    coefs = [0.0] * n
    for i in reversed(range(n)):
        coefs[i] = (forward[i] - math.fsum(lower[j][i] * coefs[j] for j in range(i + 1, n))) / lower[i][i]
    if not all(math.isfinite(c) for c in coefs):
        raise ValueError("BVI_ENV_CONTROL_SOLUTION_NOT_FINITE")
    return coefs, min(lower[i][i] for i in range(n))


def _fit_control_cholesky(rows, weights, residual, supported, offspring):
    keys = list(supported)
    index = {key: j for j, key in enumerate(keys)}
    count = len(keys)
    matrix = [[0.0] * count for _ in range(count)]
    rhs = [0.0] * count
    design = []
    for row, weight, target in zip(rows, weights, residual):
        active = [(index[k], value) for k, value in _features(row, "CONTROL").items()
                  if k in index and value]
        design.append(active)
        for j, value in active:
            rhs[j] += weight * value * target
            for k, other in active:
                if k <= j:
                    matrix[j][k] += weight * value * other
    for j, key in enumerate(keys):
        if json.loads(key)[0] != "intercept":
            matrix[j][j] += PROTOCOL["penalty"]["CONTROL"]
        for k in range(j):
            matrix[k][j] = matrix[j][k]
    coefs, minimum_pivot = _solve_spd(matrix, rhs)
    equation_residual = max(abs(math.fsum(a * b for a, b in zip(row, coefs)) - target)
                            for row, target in zip(matrix, rhs))
    fitted = [math.fsum(coefs[j] * value for j, value in active) for active in design]
    terms = [{"term": key, "factor": json.loads(key)[0], "coefficient": coefs[j],
              "support": {"runs": len(supported[key]), "composite_offspring": len(offspring[key]),
                          "effective_weight": round(sum(weights[i] for i, _ in supported[key]), 8)}}
             for j, key in enumerate(keys)]
    return {"terms": terms, "unsupported_groups": {}, "sweeps": 1,
            "solver": "DENSE_CHOLESKY_CONTROL", "convergence_metric": "MAX_ABSOLUTE_NORMAL_EQUATION_RESIDUAL",
            "converged": equation_residual < PROTOCOL["tolerance"], "last_max_delta": equation_residual,
            "normal_equation_max_abs_residual": equation_residual,
            "normal_matrix_dimension": count, "minimum_cholesky_diagonal": minimum_pivot}, fitted


def _parent_distribution(rows, key):
    groups = defaultdict(lambda: {"runs": 0, "horses": set()})
    for row in rows:
        if row.get(key):
            groups[str(row[key])]["runs"] += 1
            groups[str(row[key])]["horses"].add(row["horse_id"])
    return [{"parent": parent, "runs": value["runs"], "composite_offspring": len(value["horses"]),
             "sample_eligible": value["runs"] >= PROTOCOL["minimum_runs"] and
                                len(value["horses"]) >= PROTOCOL["minimum_composite_offspring"]}
            for parent, value in sorted(groups.items())]


def train_model(dataset, *, train_before):
    """Fit only labels before ``train_before`` using the actual capture cutoff.

    A 2025 label acquired in Oct2026 is permitted in an Oct2026 research fit,
    but can NEVER be claimed as information available to a 2025 prediction.
    """
    boundary = _day(train_before)
    rows, exclusions = _eligible_rows(dataset)
    training = [r for r in rows if _day(r["date"]) < boundary]
    if not training:
        raise ValueError("BVI_ENV_NO_TRAINING_LABELS")
    per_horse = Counter(r["horse_id"] for r in training)
    weights = [1 / per_horse[r["horse_id"]] for r in training]
    residual = [r["target"] for r in training]
    stages = {}
    for stage in PROTOCOL["stage_order"]:
        stages[stage], fitted = _fit_stage(training, weights, residual, stage)
        residual = [target - value for target, value in zip(residual, fitted)]
    total_weight = sum(weights)
    residual_rms = math.sqrt(sum(w * err * err for w, err in zip(weights, residual)) / total_weight)
    model = {"profile": PROFILE, "protocol": copy.deepcopy(PROTOCOL), "protocol_sha256": PROTOCOL_SHA256,
             "train_before": boundary.isoformat(),
             "acquisition_cutoff": dataset["prediction_cutoff"],
             "source_prediction_cutoff": dataset["prediction_cutoff"],
             "dataset_race_date": dataset["race_date"],
             "dataset_sha256": dataset.get("dataset_sha256") or sha(dataset),
             "corpus_manifest_sha256": dataset.get("manifest_sha256") or dataset.get("corpus_manifest_sha256"),
             "training_rows_sha256": sha(training), "training_runs": len(training),
             "training_composite_offspring": len(per_horse),
             "training_total_horse_weight": round(total_weight, 8),
             "training_label_min": min(r["date"] for r in training),
             "training_label_max": max(r["date"] for r in training),
             "max_training_label_date": max(r["date"] for r in training),
             "model_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             "maximum_training_acquisition_at": max(training, key=lambda r: _time(r["available_at"]))["available_at"],
             "stage_models": stages, "residual_rms": residual_rms,
             "solver_converged": all(stage["converged"] for stage in stages.values()),
             "parent_distributions": {k: _parent_distribution(training, k) for k in ("sire", "damsire")},
             "excluded_rows": exclusions,
             "label_boundary_excluded_runs": len(rows) - len(training),
             "control_status": {"class": "OBSERVED_TEXT_CLASS_RANK_OR_UNKNOWN",
                                "individual_ability": "STRICTLY_EARLIER_LABEL_FORM_WITH_SHRINKAGE",
                                "opponent_strength": "UNAVAILABLE_NOT_CONTROLLED",
                                "weather": "NOT_ADOPTED_NO_INDEPENDENT_INCREMENTAL_VALUE",
                                "course_geometry": "NOT_ADOPTED_NO_EXACT_RACE_BOUND_OBSERVATIONS",
                                "direct_dam_effect": "NOT_ADOPTED_NO_VERIFIED_UNIQUE_MATERNAL_LINE_ID"},
             "research_fit_allowed": True, "model_training_eligibility": False,
             "training_eligibility_reason": "NO_PERMANENT_HORSE_IDS_OR_INDEPENDENT_RACE_LABELS; EXPLORATORY_REGULARIZED_BASELINE_ONLY",
             "production_authority": False, "purchase_authority": False,
             "historical_forward_oos_eligible": False, "automatic_promotion": False,
             "execution_time_claim": "CALLER_MUST_FREEZE_ACTUAL_MODEL_SAVE_TIME_AND_CODE_BEFORE_TARGET_CUTOFF"}
    model["model_sha256"] = sha(model)
    return model


def verify_model(model):
    if (model.get("profile") != PROFILE or model.get("protocol_sha256") != PROTOCOL_SHA256
            or model.get("protocol") != PROTOCOL or model.get("model_sha256") !=
            sha({k: v for k, v in model.items() if k != "model_sha256"})):
        raise ValueError("BVI_ENV_MODEL_OR_PROTOCOL_HASH_MISMATCH")
    if model.get("production_authority") or model.get("purchase_authority"):
        raise ValueError("BVI_ENV_MODEL_AUTHORITY_FORBIDDEN")
    return True


def prediction_input_sha(runner, environment):
    return sha({"runner": runner, "environment": environment})


def _prediction_row(runner, environment):
    row = copy.deepcopy(runner)
    for key in ("venue", "surface", "distance_m", "going", "field_size", "race_name"):
        row[key] = copy.deepcopy(environment.get(key))
    row["class_rank"] = class_rank(environment.get("race_name") or environment.get("race_class"))
    row["going"] = environment.get("going") if environment.get("going") in GOINGS else None
    try:
        row["distance_m"] = int(environment["distance_m"])
    except (KeyError, ValueError, TypeError):
        row["distance_m"] = None
    # Never consult the target outcome or a future runner history.
    row["prior_ability"] = 0.5
    target = environment.get("race_date") or environment.get("date")
    prior = []
    if target:
        day = _day(target)
        for run in runner.get("runs") or []:
            if _day(run.get("date")) < day:
                try:
                    prior.append(_normal_finish(run))
                except ValueError:
                    pass
    if prior:
        row["prior_ability"] = (sum(prior) + 1.5) / (len(prior) + 3)
    # Internal chronological evaluator supplies this computed value, never a
    # user-supplied current result. Public callers must use actual history.
    return row


def _predict_row(model, row):
    components, totals = [], {}
    for stage in PROTOCOL["stage_order"]:
        features = _features(row, stage)
        value = 0.0
        for term in model["stage_models"][stage]["terms"]:
            if term["term"] not in features:
                continue
            contribution = term["coefficient"] * features[term["term"]]
            value += contribution
            components.append({**copy.deepcopy(term), "stage": stage,
                               "value": features[term["term"]], "contribution": round(100 * contribution, 8),
                               "status": "SUPPORTED_REGULARIZED_RESEARCH_TERM"})
        totals[stage] = value
    clamp = lambda x: round(min(100.0, max(0.0, 100 * x)), 6)
    control, general = totals["CONTROL"], totals["GENERAL"]
    full = control + general + totals["ENVIRONMENT"]
    return clamp(full), clamp(control + general), clamp(control), components


def predict(model, runner, environment):
    verify_model(model)
    target_day = environment.get("race_date") or environment.get("date")
    if target_day and _day(target_day) <= _day(model["training_label_max"]):
        raise ValueError("BVI_ENV_MODEL_CONTAINS_TARGET_OR_FUTURE_LABEL")
    if environment.get("prediction_cutoff") and _time(model["acquisition_cutoff"]) > _time(environment["prediction_cutoff"]):
        raise ValueError("BVI_ENV_MODEL_DATA_POST_TARGET_CUTOFF")
    row = _prediction_row(runner, environment)
    score, general_score, control_score, components = _predict_row(model, row)
    general = [c for c in components if c["stage"] == "GENERAL"]
    interaction = [c for c in components if c["stage"] == "ENVIRONMENT"]
    reasons = ["EXPLORATORY_ONLY_NO_PERMANENT_IDS_OR_INDEPENDENT_RACE_LABELS",
               "OPPONENT_STRENGTH_UNAVAILABLE; NOT_A_CAUSAL_EFFECT",
               "WEATHER_AND_COURSE_GEOMETRY_NOT_ADOPTED"]
    missing = [k for k in ("venue", "surface", "distance_m", "going") if not row.get(k)]
    valid = bool(general and interaction and row.get("sire") and row.get("dam")
                 and row.get("surface") in ("芝", "ダ") and row.get("venue") in VENUES
                 and row.get("distance_m") is not None)
    solver_converged = (model.get("solver_converged") is True and
                        all(stage.get("converged") is True for stage in model["stage_models"].values()))
    if not solver_converged:
        valid = False
        reasons.append("NUMERICAL_SOLVER_NOT_CONVERGED; NO_ENVIRONMENT_OVERRIDE")
    if not general:
        reasons.append("INSUFFICIENT_GENERAL_PEDIGREE_SAMPLE")
    if not interaction:
        reasons.append("INSUFFICIENT_PEDIGREE_ENVIRONMENT_SAMPLE")
    if missing:
        reasons.append("EXPLICIT_MISSING_ENVIRONMENT:" + ",".join(missing))
    if not row.get("sire") or not row.get("dam"):
        reasons.append("UNRESOLVED_COMPOSITE_HORSE_IDENTITY")
    if not target_day:
        valid = False
        reasons.append("MISSING_TARGET_RACE_DATE")
    n = min((c["support"]["composite_offspring"] for c in interaction), default=0)
    # Cluster-count uncertainty proxy, NOT a calibrated confidence interval.
    se = 100 * model["residual_rms"] * math.sqrt(0.25 + 1 / max(n, 1))
    result = {"profile": PROFILE, "model_sha256": model["model_sha256"],
              "protocol_sha256": PROTOCOL_SHA256, "input_sha256": prediction_input_sha(runner, environment),
              "input": {"runner": copy.deepcopy(runner), "environment": copy.deepcopy(environment)},
              "runner_id": str(runner.get("runner_id") or ""), "horse_id": runner.get("horse_id"),
              "score": score if valid else None, "general_score": general_score,
              "control_score": control_score, "environment_increment": round(score - general_score, 6),
              "components": components,
              "counts": {"training_runs": model["training_runs"],
                         "training_composite_offspring": model["training_composite_offspring"],
                         "matched_general_terms": len(general), "matched_environment_terms": len(interaction),
                         "minimum_matched_composite_offspring": n},
              "uncertainty": {"kind": "EMPIRICAL_COMPOSITE_CLUSTER_BAND_NOT_CALIBRATED",
                              "standard_error_proxy": round(se, 6),
                              "lower": round(max(0.0, score - 1.96 * se), 6),
                              "upper": round(min(100.0, score + 1.96 * se), 6),
                              "calibrated": False, "confidence_interval_claimed": False},
              "usable_for_shadow_override": valid, "reasons": reasons,
              "solver_converged": solver_converged,
              "missing_environment": missing, "production_authority": False,
              "purchase_authority": False, "predictive_improvement_demonstrated": False}
    return result


def evaluate_chronological(dataset, *, train_before="2026-08-01", validation_before="2026-09-01",
                           test_before="2026-10-24"):
    """Frozen, no-tuning historical partitions; never a Forward OOS claim."""
    boundaries = tuple(_day(x) for x in (train_before, validation_before, test_before))
    if not boundaries[0] < boundaries[1] < boundaries[2]:
        raise ValueError("BVI_ENV_SPLIT_BOUNDARIES_INVALID")
    model = train_model(dataset, train_before=train_before)
    rows, exclusions = _eligible_rows(dataset)
    report = {"profile": PROFILE, "classification": "POST_CAPTURE_CHRONOLOGICAL_DIAGNOSTIC_NOT_FORWARD_OOS",
              "model_sha256": model["model_sha256"], "protocol_sha256": PROTOCOL_SHA256,
              "split_label_boundaries": [str(b) for b in boundaries],
              "hyperparameters_optimized": False, "coefficients_refitted_on_validation_or_test": False,
              "individual_form_updates": "PREQUENTIAL_STRICTLY_EARLIER_LABELS_ONLY; CAPTURE_NOT_BACKDATED",
              "partitions": {}, "excluded_rows": exclusions, "forward_oos_increment": 0,
              "production_authority": False, "predictive_improvement_demonstrated": False}
    for name, low, high in (("VALIDATION", boundaries[0], boundaries[1]),
                            ("TEST", boundaries[1], boundaries[2])):
        chosen = [r for r in rows if low <= _day(r["date"]) < high]
        group_errors = defaultdict(lambda: defaultdict(list))
        errors = defaultdict(list)
        support = 0
        for row in chosen:
            full, general, control, comp = _predict_row(model, row)
            target = 100 * row["target"]
            if any(c["stage"] == "ENVIRONMENT" for c in comp):
                support += 1
            for arm, value in (("CONTROL_ONLY", control), ("GENERAL_PEDIGREE", general), ("ENV_PEDIGREE", full)):
                error = (value - target) / 100
                errors[arm].append(error)
                for dimension in ("venue", "surface", "going", "distance_m", "sire", "damsire"):
                    group_errors[(dimension, str(row.get(dimension)))][arm].append(error)
        metrics = lambda values: {"n": len(values), "mae": mean(abs(e) for e in values) if values else None,
                                  "mse": mean(e * e for e in values) if values else None}
        groups = []
        for (dimension, value), arms in sorted(group_errors.items()):
            measured = {k: metrics(v) for k, v in arms.items()}
            groups.append({"dimension": dimension, "value": value, "errors": measured,
                           "environment_mse_increment": measured["ENV_PEDIGREE"]["mse"] - measured["GENERAL_PEDIGREE"]["mse"],
                           "improved_in_this_historical_partition": measured["ENV_PEDIGREE"]["mse"] < measured["GENERAL_PEDIGREE"]["mse"]})
        report["partitions"][name] = {"label_count": len(chosen),
                                        "composite_horses": len({r["horse_id"] for r in chosen}),
                                        "environment_term_supported_rows": support,
                                        "errors": {k: metrics(v) for k, v in errors.items()},
                                        "groups": groups,
                                        "unimproved_condition_count": sum(not g["improved_in_this_historical_partition"] for g in groups),
                                        "ticket_pfs": "NOT_MEASURED_NO_FROZEN_CANDIDATE_TICKETS_OR_INDEPENDENT_RACE_LABELS"}
    return report
