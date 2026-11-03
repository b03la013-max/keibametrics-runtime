"""Offline Base13 market-increment diagnostics; no Production imports or writes.

Runs Phase 0 unchanged and Phase 0.5 into one NEW asof directory. All fits are
research measurements, never new index values, predictions or betting policy.
"""
from __future__ import annotations

import argparse
import copy
import ast
import csv
import hashlib
import json
import math
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

try:
    from . import benter_second_stage as b
except ImportError:
    import benter_second_stage as b

INDICES = ("HPI", "SSI", "CFI", "RFI", "JTI", "CSI", "TRI", "BWI", "GCI", "PRI", "KGI", "BVI", "VMI")
SUPPLIED_WEIGHTS = dict(HPI=.20, SSI=.17, CFI=.10, RFI=.08, JTI=.05,
                        CSI=.05, TRI=.05, BWI=.05, GCI=.08, PRI=.12, KGI=.05)
LAMBDA_GRID = (.0001, .001, .01, .1, 1., 10., 100., 1000.)
REFERENCE_RATE = .25  # Reporting annotation only, never a numeric input rule.
REFERENCE_RESOLUTION = (
    "Owner確認によりClaude試算との差異は解決済み：監査側は開催日境界で分割し、"
    "ZAIは平均中心化のみ（標準偏差で割らない）。#362は発走順前後半・レース内標準化"
    "という指定法を維持する。監査側コードを独立に再実行したという意味ではない。"
)
CALENDAR_SOURCES = [
    "https://www.jra.go.jp/keiba/program/2026/pdf/nittei.pdf",
    "https://www.jra.go.jp/keiba/program/2027/pdf/nittei.pdf",
    "https://www.jra.go.jp/news/202609/092805.html",
]
# Manually verified against the official published day-allocation PDFs. This is
# an offline forecast calendar, NOT a Discovery feed, Day Plan or scheduler.
FORECAST_DATES = tuple(
    [f"2026-11-{d:02d}" for d in (7, 8, 14, 15, 21, 22, 23, 28, 29)] +
    [f"2026-12-{d:02d}" for d in (5, 6, 12, 13, 19, 20, 26, 27)] +
    [f"2027-01-{d:02d}" for d in (4, 9, 10, 11, 16, 17, 23, 24, 30, 31)] +
    [f"2027-02-{d:02d}" for d in (6, 7, 13, 14, 20, 21, 27, 28)] +
    [f"2027-03-{d:02d}" for d in (6, 7, 8, 13, 14, 20, 21, 22, 27, 28)]
)


def compact(value):
    """Keep distribution statistics; bulky bootstrap draws are not a new KPI."""
    if isinstance(value, dict):
        return {k: compact(v) for k, v in value.items() if k != "replicates"}
    if isinstance(value, list):
        return [compact(v) for v in value]
    return value


def holm(p_values):
    """Holm step-down adjusted p, including untestable hypotheses as p=1."""
    if any(not math.isfinite(p) or not 0 <= p <= 1 for p in p_values.values()):
        raise ValueError("INVALID_P_VALUE")
    ordered = sorted(p_values, key=lambda k: (p_values[k], k))
    adjusted, previous = {}, 0.
    for i, key in enumerate(ordered):
        previous = max(previous, (len(ordered) - i) * p_values[key])
        adjusted[key] = min(1., previous)
    return {key: adjusted[key] for key in p_values}


def strict_split(races):
    races = sorted(races, key=lambda r: (b.timestamp(r.post_at), r.race_id))
    split = len(races) // 2
    while split and b.timestamp(races[split - 1].post_at) == b.timestamp(races[split].post_at):
        split -= 1
    return races[:split], races[split:]


def trace_audit(value, trace):
    try:
        numeric = b.number(value)
    except (ValueError, TypeError):
        numeric = None
    trace = trace if isinstance(trace, dict) else {}
    texts = []

    def visit(item):
        if isinstance(item, str):
            texts.append(item.upper())
        elif isinstance(item, dict):
            for v in item.values():
                visit(v)
        elif isinstance(item, list):
            for v in item:
                visit(v)
    visit(trace)
    joined = " ".join(texts)
    rule = str(trace.get("rule_id", "")).upper()
    explicit = any(bool(trace.get(k)) for k in ("fallback", "is_fallback", "imputed", "is_imputed", "default_applied"))
    fallback = explicit or any(k in rule for k in ("FALLBACK", "DEFAULT", "NEUTRAL", "DCR", "INFORMATION-INSUFFICIENT"))
    exact = numeric == 50.
    return {"missing": numeric is None, "exact_50": exact,
            "fallback_or_DCR_rule": bool(fallback), "UNVALIDATED": "UNVALIDATED" in joined,
            "trace_missing": not bool(trace), "default_or_fallback_union": exact or bool(fallback),
            "rule_id": trace.get("rule_id"), "value": numeric,
            "coverage_weight": trace.get("coverage_weight"),
            "component_features": sorted({str(c["feature"]) for c in trace.get("components", [])
                                           if isinstance(c, dict) and c.get("feature")})}


def load_indices(root, races, phase0_rows, inputs, *, indices=INDICES):
    """Read the SAME active runners; missing values are never silently filled."""
    root = Path(root).resolve()
    lookup, observations, arrays = {}, defaultdict(list), {}
    for race in races:
        final = inputs.read(Path(root) / "runtime/final_artifacts" / (race.race_id + ".json"))
        runners = final["final_prediction_package"]["index_provenance_replay"]["runners"]
        matrix = np.full((len(race.ids), len(indices)), np.nan)
        for i, rid in enumerate(race.ids):
            runner = runners[rid]
            cells = {}
            for j, index in enumerate(indices):
                cell = trace_audit(runner.get("base_final_values", {}).get(index),
                                   runner.get("base_index_trace", {}).get(index))
                observations[index].append(cell); cells[index] = cell
                if not cell["missing"]:
                    matrix[i, j] = cell["value"]
            lookup[race.race_id, rid] = cells
        arrays[race.race_id] = matrix
    audit = {}
    for index in indices:
        cells = observations[index]; n = len(cells)
        counts = {key: sum(bool(c[key]) for c in cells) for key in
                  ("missing", "exact_50", "fallback_or_DCR_rule", "UNVALIDATED", "trace_missing", "default_or_fallback_union")}
        rate = counts["default_or_fallback_union"] / n if n else None
        audit[index] = {"n_runners": n, "counts": counts, "default_or_fallback_rate": rate,
                        "reference_only_high_default_rate": bool(rate is not None and rate >= REFERENCE_RATE),
                        "rule_id_counts": dict(sorted(Counter(c["rule_id"] or "MISSING" for c in cells).items())),
                        "component_feature_counts": dict(sorted(Counter(f for c in cells for f in c["component_features"]).items()))}
    rows = []
    for row in phase0_rows:
        if row["series"] != "pre_signature":
            continue
        cells = lookup.get((row["race_id"], row["runner_id"]))
        extended = dict(row)
        for index in indices:
            extended[index] = cells[index]["value"] if cells else None
            extended[index + "_audit_flags"] = ";".join(
                key for key in ("missing", "exact_50", "fallback_or_DCR_rule", "UNVALIDATED", "trace_missing")
                if cells and cells[index][key])
        rows.append(extended)
    return arrays, audit, rows


def standardize(matrix):
    std = matrix.std(axis=0, ddof=0)
    return np.divide(matrix - matrix.mean(axis=0), std, out=np.zeros_like(matrix), where=std > 0)


def label_multiple_testing(single):
    results = single["indices"]
    ps = {k: r["shuffle_p_one_sided"] for k, r in results.items()}
    adjusted = holm(ps)
    repetitions = single["multiple_testing"]["shuffle_repetitions"]
    sufficient = 1 / (repetitions + 1) <= .05 / len(results)
    for index, result in results.items():
        decision = result["measurement"]["decision"]
        unadjusted = decision["Yes_No"] == "Yes" and ps[index] <= .05
        result.update(holm_adjusted_p=adjusted[index], unadjusted_signal=unadjusted,
                      holm_reject=(unadjusted and adjusted[index] <= .05) if sufficient else None,
                      holm_decision="EVALUATED" if sufficient else "RESOLUTION_INSUFFICIENT",
                      interpretation="EXPLORATORY_ONLY_NOT_ADOPTION")
    single["multiple_testing"].update(
        method=f"HOLM_SHUFFLE_P_{len(results)}_RESOLUTION_EXPLICIT",
        n_hypotheses=len(results), alpha=.05, minimum_shuffle_p=1 / (repetitions + 1),
        first_holm_threshold=.05 / len(results),
        resolution_sufficient_for_any_rejection=sufficient,
        decision_method="RESOLUTION_LIMIT_LABEL_NOT_BOOTSTRAP_P",
        limitation="200 plus-one shuffle p values cannot resolve p<=0.05/13; the 200 runs remain descriptive controls.")
    return single


def per_index(races, arrays, audits, *, indices=INDICES, bootstrap_reps=1000, shuffle_reps=200, seed=b.SEED):
    results = {}
    for j, index in enumerate(indices):
        eligible = [replace(r, zai=arrays[r.race_id][:, j], z=standardize(arrays[r.race_id][:, j:j + 1])[:, 0])
                    for r in races if np.isfinite(arrays[r.race_id][:, j]).all()]
        measured = b.analyze(eligible, bootstrap_reps=bootstrap_reps, shuffle_reps=shuffle_reps, seed=seed)
        if "chronological" in measured:
            delta = measured["decision"]["delta_rho2"]
            null = measured["shuffle_control"]["chronological_out_of_sample"]["replicates"]
            p = (1 + sum(x >= delta for x in null)) / (1 + len(null))
        else:
            p = 1.
        results[index] = {"audit": audits[index], "measurement": compact(measured), "shuffle_p_one_sided": p,
                          "excluded_races_with_missing_index": len(races) - len(eligible)}
    return label_multiple_testing({"indices": results, "multiple_testing": {"shuffle_repetitions": shuffle_reps}})

@dataclass(frozen=True)
class VectorRace:
    race: b.Race
    x: np.ndarray


class MultiChoices:
    def __init__(self, races):
        if not races:
            raise ValueError("JOINT_NO_RACES")
        self.races = races
        self.base = b.Choices([r.race for r in races])
        self.x = np.column_stack((np.concatenate([r.x for r in races]), self.base.lm))
        self.target = np.add.reduceat(self.base.y[:, None] * self.x, self.base.starts, axis=0)

    def evaluate(self, coefficients):
        u = self.x @ np.asarray(coefficients)
        maxima = np.maximum.reduceat(u, self.base.starts)
        ex = np.exp(u - maxima[self.base.groups])
        den = np.add.reduceat(ex, self.base.starts)
        lp = u - maxima[self.base.groups] - np.log(den)[self.base.groups]
        return np.add.reduceat(self.base.y * lp, self.base.starts), ex / den[self.base.groups]

    def fit(self, strength, weights=None, *, beta_fixed=None):
        """L2 ONLY on index coefficients. Market beta is free or an offset."""
        if strength <= 0:
            raise ValueError("L2_STRENGTH_MUST_BE_POSITIVE")
        w = np.ones(len(self.races)) if weights is None else np.asarray(weights, float)
        if not np.isfinite(w).all() or np.any(w < 0) or w.sum() <= 0:
            raise ValueError("INVALID_RACE_WEIGHTS")
        n = self.x.shape[1] - 1
        # Reparameterization prevents a stiff Hessian when lambda is huge.
        scale = np.full(n, 1 / math.sqrt(max(1., strength)))
        mask = np.r_[np.ones(n), 0.]
        def unpack(eta):
            return np.r_[eta[:n] * scale, eta[-1] if beta_fixed is None else beta_fixed]
        derivative_scale = np.r_[scale, 1.] if beta_fixed is None else scale
        def objective(eta):
            theta = unpack(eta)
            ll, p = self.evaluate(theta)
            expected = np.add.reduceat(p[:, None] * self.x, self.base.starts, axis=0)
            gradient = np.sum(w[:, None] * (expected - self.target), axis=0) / w.sum()
            gradient += strength * mask * theta
            if beta_fixed is not None:
                gradient = gradient[:-1]
            return (-float(w @ ll) / w.sum() + .5 * strength * float(theta[:-1] @ theta[:-1]),
                    gradient * derivative_scale)
        initial = np.zeros(n + (beta_fixed is None))
        if beta_fixed is None:
            initial[-1] = 1.
        result = minimize(objective, initial, jac=True, method="BFGS", options={"gtol": 1e-8, "maxiter": 1000})
        gradient = float(np.max(np.abs(objective(result.x)[1])))
        theta = unpack(result.x)
        if not np.isfinite(theta).all() or gradient > 1e-6:
            raise ValueError("JOINT_L2_NOT_CONVERGED")
        return theta, {"optimizer_success": bool(result.success), "gradient_max_abs": gradient,
                       "market_beta_penalized": False, "market_beta_fixed": beta_fixed is not None}

def beta_constraint(choices, mode, weights=None):
    if mode == "free":
        return None
    if mode == "offset":
        return choices.base.fit("M", weights)["beta"]
    if mode == "features_only":
        return 0.
    raise ValueError("UNKNOWN_JOINT_MODE")


def select_lambda(training, *, grid=LAMBDA_GRID, mode="free"):
    """Nested date WF; offsets are fitted on each INNER training fold."""
    if not grid or any(x <= 0 for x in grid):
        raise ValueError("INVALID_LAMBDA_GRID")
    days = sorted({r.race.race_date for r in training})
    folds, losses = [], {float(x): [0., 0] for x in grid}
    for day in days:
        past = [r for r in training if r.race.race_date < day]
        now = [r for r in training if r.race.race_date == day]
        if not past:
            continue
        train, test = MultiChoices(past), MultiChoices(now)
        fixed = beta_constraint(train, mode)
        row = {"validation_date": day, "training_dates": sorted({r.race.race_date for r in past}),
               "training_races": len(past), "validation_races": len(now), "validation_LL": {},
               "mode": mode, "inner_training_beta_offset": fixed}
        assert max(row["training_dates"]) < day
        for strength in grid:
            theta, _ = train.fit(strength, beta_fixed=fixed)
            total = float(test.evaluate(theta)[0].sum())
            losses[strength][0] -= total; losses[strength][1] += len(now)
            row["validation_LL"][str(strength)] = total
        folds.append(row)
    selected = min(grid, key=lambda k: (losses[k][0] / losses[k][1], -k)) if folds else (1. if 1. in grid else max(grid))
    return {"selected_lambda": float(selected), "grid": list(grid), "inner_folds": folds,
            "status": "PAST_DATES_ONLY_SELECTED" if folds else "NO_INNER_HISTORY_FIXED_DEFAULT",
            "validation_mean_NLL": {str(k): v[0] / v[1] if v[1] else None for k, v in losses.items()},
            "objective": "MEAN_RACE_NLL_PLUS_LAMBDA_OVER_2_TIMES_INDEX_L2_ONLY",
            "market_beta_penalized": False, "mode": mode, "selection_training_dates": days}

def joint_score(test, theta, market):
    choices = MultiChoices(test)
    ll = float(choices.evaluate(theta)[0].sum())
    ll0 = float(choices.base.ll0.sum())
    lm = float(choices.base.evaluate("M", market)[0].sum())
    return {"n_races": len(test), "LL": ll, "LL0": ll0, "M_LL": lm,
            "rho2": 1 - ll / ll0, "M_rho2": 1 - lm / ll0, "delta_rho2": (lm - ll) / ll0}


def joint_analysis(races, arrays, *, indices=INDICES, bootstrap_reps=1000, seed=b.SEED, grid=LAMBDA_GRID, mode="free"):
    ordered = sorted(races, key=lambda r: (b.timestamp(r.post_at), r.race_id))
    training, testing = strict_split(ordered)
    vectors = {r.race_id: VectorRace(r, standardize(arrays[r.race_id])) for r in ordered
               if np.isfinite(arrays[r.race_id]).all()}
    train = [vectors[r.race_id] for r in training if r.race_id in vectors]
    test = [vectors[r.race_id] for r in testing if r.race_id in vectors]
    if not train or not test:
        return {"status": "INSUFFICIENT_COMPLETE_CASES", "n_races": len(vectors), "mode": mode}
    tuning = select_lambda(train, grid=grid, mode=mode)
    choices = MultiChoices(train); strength = tuning["selected_lambda"]
    fixed = beta_constraint(choices, mode)
    theta, optimizer = choices.fit(strength, beta_fixed=fixed)
    market = choices.base.fit("M")
    result = {"status": "EXPLORATORY_L2_NOT_PRODUCTION", "mode": mode,
              "n_races": len(vectors), "training_races": len(train), "test_races": len(test),
              "excluded_incomplete_races": len(ordered) - len(vectors),
              "tuning": tuning, "optimizer": optimizer, "chronological": joint_score(test, theta, market),
              "lambda_sensitivity": []}
    # The holdout curve is descriptive; lambda selection above never uses it.
    for value in grid:
        coef, _ = choices.fit(value, beta_fixed=fixed)
        result["lambda_sensitivity"].append({"lambda": value, "evaluation": joint_score(test, coef, market),
                                             "beta": float(coef[-1]), "index_coefficient_norm": float(np.linalg.norm(coef[:-1]))})
    rng = np.random.default_rng(seed); draws = []
    fixed_delta, refit_delta = [], []
    testing_choices = MultiChoices(test)
    original_c = testing_choices.evaluate(theta)[0]
    original_m = testing_choices.base.evaluate("M", market)[0]
    for _ in range(bootstrap_reps):
        w = np.bincount(rng.integers(0, len(train), len(train)), minlength=len(train))
        tw = np.bincount(rng.integers(0, len(test), len(test)), minlength=len(test))
        coef, _ = choices.fit(strength, w, beta_fixed=beta_constraint(choices, mode, w))
        draws.append(coef)
        ll0 = float(tw @ testing_choices.base.ll0)
        fixed_delta.append(float(tw @ (original_m - original_c)) / ll0)
        mfit = choices.base.fit("M", w)
        cm = testing_choices.evaluate(coef)[0]; mm = testing_choices.base.evaluate("M", mfit)[0]
        refit_delta.append(float(tw @ (mm - cm)) / ll0)
    draws = np.array(draws); names = list(indices) + ["ln_m"]
    result["coefficients"] = {k: {"coefficient": float(theta[j]),
            "sign_flip_fraction": float(np.mean(np.sign(draws[:, j]) != np.sign(theta[j]))),
            "bootstrap_ci95": [float(v) for v in np.quantile(draws[:, j], [.025, .975])],
            "positive_fraction": float(np.mean(draws[:, j] > 0)),
            "negative_fraction": float(np.mean(draws[:, j] < 0))} for j, k in enumerate(names)}
    result["bootstrap"] = {"repetitions": bootstrap_reps, "seed": seed,
            "conditional_holdout": compact(b.distribution(fixed_delta)),
            "training_and_holdout_refit": compact(b.distribution(refit_delta)),
            "lambda_held_fixed": strength,
            "interpretation": "SIGN_STABILITY_CONDITIONAL_ON_SELECTED_LAMBDA; offset beta refitted on each bootstrap training sample"}
    daily, ll, lm, ll0 = [], 0., 0., 0.
    vr = list(vectors.values())
    for day in sorted({r.race.race_date for r in vr}):
        past = [r for r in vr if r.race.race_date < day]; now = [r for r in vr if r.race.race_date == day]
        row = {"date": day, "training_races": len(past), "n_races": len(now)}
        if past:
            tuned = select_lambda(past, grid=grid, mode=mode); trained = MultiChoices(past)
            coef, _ = trained.fit(tuned["selected_lambda"], beta_fixed=beta_constraint(trained, mode))
            scored = joint_score(now, coef, trained.base.fit("M"))
            row.update(status="NESTED_PAST_DATES_ONLY", tuning=tuned, evaluation=scored,
                       coefficients={k: float(v) for k, v in zip(names, coef)})
            ll += scored["LL"]; lm += scored["M_LL"]; ll0 += scored["LL0"]
        else:
            row["status"] = "NO_PRIOR_TRAINING_NOT_SCORED"
        daily.append(row)
    result["walk_forward"] = {"daily": daily, "cumulative_delta_rho2": (lm - ll) / ll0 if ll0 else None,
                              "cumulative_LL0": ll0, "cumulative_LL": ll, "cumulative_M_LL": lm,
                              "cumulative_rho2": 1 - ll / ll0 if ll0 else None}
    return result

def odds_sensitivity(races, final_races, rows, primary):
    by_race = {r["race_id"]: float(r["minutes_to_post"]) for r in rows
               if r["series"] == "pre_signature" and not r["excluded_reason"]}
    minutes = [by_race[r.race_id] for r in races]
    training, testing = strict_split(races)
    fitted = {m: primary["chronological"]["evaluation"]["models"][m]["parameters"] for m in b.MODELS} if "chronological" in primary else None
    bins = []
    for label, lo, hi in [("<=10", -math.inf, 10), ("10< t <=30", 10, 30), ("30< t <=60", 30, 60), (">60", 60, math.inf)]:
        selected = [r for r in races if lo < by_race[r.race_id] <= hi]
        held = [r for r in testing if lo < by_race[r.race_id] <= hi]
        row = {"minutes_band": label, "n_races": len(selected), "holdout_races": len(held)}
        if selected:
            c = b.Choices(selected); f = c.fit("M"); ll = float(c.evaluate("M", f)[0].sum())
            row.update(full_band_refitted_M_rho2=1 - ll / float(c.ll0.sum()), full_band_beta=f["beta"])
        if held and fitted:
            row["fixed_global_training_holdout"] = b.scores(b.Choices(held), fitted)
        bins.append(row)
    pairs = set(r.race_id for r in races) & set(r.race_id for r in final_races)
    final = {"n_available_final_odds_races": len(final_races), "paired_races": len(pairs),
             "status": "FINAL_ODDS_NOT_AVAILABLE" if not pairs else "PAIRED_SECONDARY_ONLY"}
    if pairs:
        fmap = {r.race_id: r for r in final_races}
        for name, remap in (("pre_signature", {r.race_id: r for r in races}), ("final_odds", fmap)):
            train = [remap[r.race_id] for r in training if r.race_id in pairs]
            test = [remap[r.race_id] for r in testing if r.race_id in pairs]
            if train and test:
                final[name] = b.scores(b.Choices(test), b.fit_models(b.Choices(train)))
        if all(s in final for s in ("pre_signature", "final_odds")):
            final["holdout_M_rho2_difference"] = final["final_odds"]["models"]["M"]["rho2"] - final["pre_signature"]["models"]["M"]["rho2"]
            final["holdout_ZAI_delta_rho2_difference"] = final["final_odds"]["delta_rho2"] - final["pre_signature"]["delta_rho2"]
    return {"n_races": len(minutes), "minutes_to_post": {"minimum": min(minutes) if minutes else None,
            "median": float(np.median(minutes)) if minutes else None, "maximum": max(minutes) if minutes else None},
            "bands": bins, "secondary_final_odds": final,
            "causal_timing_effect": "UNDETERMINED_WITHOUT_PAIRED_OBSERVATION_TIMES; bands confound race composition",
            "final_odds_source_research": {
                "existing_provider": "JRA_OFFICIAL", "new_provider_required": False,
                "existing_parser": "runtime/jra_source_runtime/jra_market_observation.py",
                "missing_binding": "No explicit final-odds capture/classifier/RESULT attachment is present in these input files; acquisition changes are SPEC only.",
                "official_documentation": "https://www.jra.go.jp/faq/pop02/1_1.html",
                "alternative_requires_owner_license_review": "https://jra-van.jp/dlb/ddata.html",
                "new_acquisition_implemented": False}}


def weights_from_source(root, inputs):
    root = Path(root).resolve()
    path = Path(root) / "runtime/jra_index_provenance_builder.py"
    if not path.exists():
        return {"status": "SOURCE_FILE_NOT_AVAILABLE", "weights": None}
    raw = path.read_bytes(); inputs.manifest[path.relative_to(inputs.root).as_posix()] = hashlib.sha256(raw).hexdigest()
    tree = ast.parse(raw.decode()); found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "zai_win" for t in node.targets):
            terms = {}
            for term in ast.walk(node.value):
                if isinstance(term, ast.BinOp) and isinstance(term.op, ast.Mult):
                    a, c = term.left, term.right
                    if isinstance(a, ast.Subscript) and isinstance(a.value, ast.Name) and a.value.id == "vals" and isinstance(a.slice, ast.Constant) and isinstance(c, ast.Constant):
                        terms[a.slice.value] = float(c.value)
            found.append(terms)
    if len(found) != 1 or not found[0]:
        return {"status": "FORMULA_SOURCE_AMBIGUOUS", "weights": None}
    weights = {k: found[0].get(k, 0.) for k in INDICES}
    return {"status": "READ_ONLY_AST_VERIFIED", "path": path.relative_to(inputs.root).as_posix(), "sha256": hashlib.sha256(raw).hexdigest(),
            "weights": weights, "supplied_weights_match": all(weights[k] == v for k, v in SUPPLIED_WEIGHTS.items()),
            "BVI_note": "BVI weight was omitted from the supplied list; the stored direct ZAI_WIN formula does not include BVI (direct coefficient 0).",
            "VMI_note": "VMI is outside direct ZAI_WIN (0); both indices can still enter other Derived indices."}


def arrival_forecast(races, audit, root, inputs, *, asof):
    root = Path(root).resolve()
    eligible = {r.race_id for r in races}; daily = []
    errors = {r["race_id"]: r["reason"] for r in audit["excluded_races"] if r["series"] == "pre_signature"}
    observed = defaultdict(set)
    for r in audit["observation_selection"]:
        rid = r["race_id"]; d = rid.split("-")[3]
        observed[d[:4] + "-" + d[4:6] + "-" + d[6:]].add(rid)
    total_technical = 0
    for day, finals in sorted(observed.items()):
        path = Path(root) / "runtime/jra_race_day_status" / (day + ".json")
        status = inputs.read(path) if path.exists() else {}
        managed = [r for r in status.get("races", []) if b.RACE_ID.fullmatch(r.get("race_id", ""))]
        no_final = [r for r in managed if r["race_id"] not in finals]
        technical = [r for r in no_final if r.get("state") in {
            "SOURCE_FAILED", "FORMAL_FAILED", "PRODUCTION_BLOCKED", "RESOLVER_DEADLINE_EXCEEDED", "MISSED_WINDOW"}
            and "障害" not in r.get("title", "")]
        total_technical += len(technical)
        daily.append({"date": day, "eligible_races": len(finals & eligible), "FINAL_files": len(finals),
            "FINAL_exclusion_reasons": dict(sorted(Counter(errors[r] for r in finals if r in errors).items())),
            "managed_status_races": len(managed) if status else None,
            "no_FINAL_original_status_counts": dict(sorted(Counter(r.get("state", "UNKNOWN") for r in no_final).items())),
            "technical_future_recovery_upper_bound": len(technical),
            "technical_race_ids": [r["race_id"] for r in technical],
            "source_status_path": path.relative_to(inputs.root).as_posix() if path.exists() else None})
    days = len(daily); n = len(races)
    future = [d for d in FORECAST_DATES if d > asof.isoformat()]
    def estimate(target, rate):
        required = max(0, math.ceil((target - n) / rate)) if rate else None
        day = asof.isoformat() if required == 0 else future[required - 1] if required is not None and required <= len(future) else None
        return {"target": target, "additional_racedays": required, "estimated_date": day,
                "status": "PACE_SCENARIO_NOT_GUARANTEE" if day else "CALENDAR_HORIZON_INSUFFICIENT"}
    baseline = n / days if days else 0
    result_gap = sum(row["FINAL_exclusion_reasons"].get("RESULT_MISSING", 0) for row in daily)
    scenarios = {}
    for name, extra in [("observed_pace", 0), ("future_RESULT_gaps_closed", result_gap),
                        ("future_technical_failures_closed_upper_bound", total_technical),
                        ("both_future_gaps_closed_upper_bound", result_gap + total_technical)]:
        rate = (n + extra) / days if days else 0
        scenarios[name] = {"races_per_raceday": rate, "extra_historical_rate_equivalent": extra,
                           "estimates": [estimate(t, rate) for t in (500, 1000)]}
    for scenario in scenarios.values():
        for row, base in zip(scenario["estimates"], scenarios["observed_pace"]["estimates"]):
            row["racedays_saved_vs_baseline"] = base["additional_racedays"] - row["additional_racedays"] if row["additional_racedays"] is not None else None
            row["calendar_days_saved_vs_baseline"] = (date.fromisoformat(base["estimated_date"]) - date.fromisoformat(row["estimated_date"])).days if base["estimated_date"] and row["estimated_date"] else None
    return {"daily": daily, "n_racedays": days, "eligible_races": n, "mean_eligible_races_per_raceday": baseline,
            "scenarios": scenarios, "calendar_sources": CALENDAR_SOURCES,
            "forecast_calendar": future, "calendar_verified_asof": "2026-11-03",
            "notes": ["One raceday means one calendar date across all JRA venues, not venue-days.",
                      "Future pace is extrapolated from eight observed days; cancellations, venue mix and system uptime can change it.",
                      "Technical closure is a future upper-bound scenario, not permission or evidence to recreate past FINALs.",
                      "Original Status enums are preserved; NO-BET, PAPER and jump scope are not reclassified for sample growth.",
                      "The 2027 published calendar is subject to official approval/changes; this static offline calendar is not an automated schedule."],
            "top3_actions_proposal_only": [
                "Close RESULT storage/navigation failures for existing pre-race FINALs, preserving timestamps and receipts.",
                "Prevent SOURCE/cancellation parser failures and preserve raw evidence before deadlines; never backdate FINAL.",
                "Remove resolver/deadline/legitimate-scope execution failures prospectively; retain valid NO-BET and SCOPE_HOLD."],
            "backfill_SPEC": {
                "classification": "CONDITIONALLY_FEASIBLE_FOR_SEPARATE_REPLAY_COHORT_NOT_ORIGINAL_LIVE",
                "required_inputs": ["Original pre-post SOURCE bytes with SHA and observation time", "As-of evidence/corpus/rule/code versions", "Frozen runner identity/cancellations", "Contemporaneous pre-freeze market snapshot", "Official RESULT kept outside feature computation"],
                "cannot_recover": ["Unarchived pre-race odds from a current result page", "Unversioned later corpus/person statistics", "Missing pre-race information or absent authentic freeze/signature"],
                "leakage_controls": ["Pin every feature effective time before post", "Outcome-blind feature replay with original code and rules", "Separate REPLAY ledger and KPI; no addition to 178 original or Forward OOS", "Raw/index/final original SHA unchanged"],
                "effort_estimate_engineering_days_not_commitment": {"inventory_and_temporal_proof": [1, 2], "offline_replay_adapter_if_inputs_complete": [2, 4], "independent_review_and_regression": [1, 2], "total": [4, 8]},
                "implemented": False}}


def reconcile_phase0_markdown(text):
    lines = text.splitlines(); out = []; inserted = False
    prefixes = ("- 主実装は", "- 同一入力を未標準化", "- 主結果の検証", "- 分割境界や尺度")
    for line in lines:
        if line.startswith(prefixes):
            if not inserted:
                out += ["- " + REFERENCE_RESOLUTION,
                        "- 過去asofとPhase 0 summary.jsonのバイト再現性を保持。旧JSONの未確定説明は履歴であり、Phase 0.5のreference_resolutionが訂正を記録する。"]
                inserted = True
        else:
            out.append(line)
    return "\n".join(out) + "\n"


def quality_axes(single):
    rows = []
    for index in INDICES:
        r = single["indices"][index]; audit = r["audit"]; n = audit["n_runners"]
        measurement = r["measurement"]; hold = measurement.get("chronological", {}).get("evaluation")
        rows.append({"index": index, "n_runners": n, "missing": audit["counts"]["missing"],
            "exact_50_rate": audit["counts"]["exact_50"] / n if n else None,
            "default_or_fallback_rate": audit["default_or_fallback_rate"],
            "fallback_DCR_rate": audit["counts"]["fallback_or_DCR_rule"] / n if n else None,
            "UNVALIDATED_rate": audit["counts"]["UNVALIDATED"] / n if n else None,
            "standalone_rho2_full": measurement.get("full_in_sample", {}).get("models", {}).get("F", {}).get("rho2"),
            "standalone_rho2_holdout": hold["models"]["F"]["rho2"] if hold else None,
            "market_derived_control": index == "VMI",
            "component_feature_counts": audit.get("component_feature_counts", {}) if index == "VMI" else {}})
    return {"status": "MARKET_INCREMENT_NOT_DISTINGUISHABLE_NO_RANKING", "rows": rows,
            "standalone_definition": "No explicit ln(m) covariate; NOT evidence of independence from market. VMI is a market-derived control.",
            "production_change": False}


def reuse_single_index(path, inputs, races, audits, start, end, asof, bootstrap_reps, shuffle_reps, seed):
    path = Path(path).resolve()
    if not path.is_relative_to(inputs.root):
        raise ValueError("CACHE_MUST_BE_WITHIN_INPUT_REPOSITORY")
    old = inputs.read(path)
    if old["period"] != {"from": start.isoformat(), "to": end.isoformat(), "asof": asof.isoformat(), "timezone": "Asia/Tokyo"}:
        raise ValueError("CACHE_PERIOD_MISMATCH")
    conf = old["configuration"]
    if (conf["bootstrap_reps"], conf["shuffle_reps"], conf["seed"]) != (bootstrap_reps, shuffle_reps, seed):
        raise ValueError("CACHE_RESAMPLING_MISMATCH")
    actual_ids = [r.race_id for r in sorted(races, key=lambda r: (b.timestamp(r.post_at), r.race_id))]
    if old["cohort"]["race_ids"] != actual_ids:
        raise ValueError("CACHE_COHORT_MISMATCH")
    for name, expected in old["input_files_sha256"].items():
        source = (inputs.root / name).resolve()
        if not source.is_relative_to(inputs.root) or hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            raise ValueError("CACHE_INPUT_SHA_MISMATCH:" + name)
    single = copy.deepcopy(old["single_index"])
    for index in INDICES:
        single["indices"][index]["audit"] = audits[index]
    single["multiple_testing"]["shuffle_repetitions"] = shuffle_reps
    single["reuse_provenance"] = {"path": path.relative_to(inputs.root).as_posix(),
        "sha256": inputs.manifest[path.relative_to(inputs.root).as_posix()],
        "input_SHA_verified": True, "unchanged_MFC_contract": True}
    return label_multiple_testing(single), old


def render_markdown(s):
    lines = ["# Phase 0.6 — 指数診断の設計修正", "",
        "SPEC / CODE: 実装済。CIはPR Runで検収。DEPLOYED / LIVE: 未実施。", "",
        f"{s['period']['from']}〜{s['period']['to']} / asof {s['period']['asof']}。{s['cohort']['n_races']}R・{s['cohort']['n_runners']}頭。",
        "本番の指数・重み・買い目に変更なし。市場上積みでBase13の優先順位を付けない。", "",
        "## 旧設計の訂正", "",
        "旧Phase0.5の後半Δρ²=-0.0889239663、WF=-0.0534915444、β=0.374985839は、市場βまで正則化した設計欠陥による値。指数の効果として解釈しない。元asofは変更せず履歴として保持。", "",
        "## 修正L2の後半評価とWF", "",
        "| 方式 | λ | 後半Δρ² | 95%区間 | WF累積Δρ² | β |",
        "|---|---:|---:|---|---:|---:|"]
    for key, label in [("joint_L2", "指数のみL2・β罰則なし"), ("joint_L2_offset", "M推定βをオフセット")]:
        j = s[key]
        if "chronological" not in j:
            continue
        ci = j["bootstrap"]["conditional_holdout"]["ci95"]
        lines.append(f"| {label} | {j['tuning']['selected_lambda']} | {j['chronological']['delta_rho2']:.8f} | [{ci[0]:.8f}, {ci[1]:.8f}] | {j['walk_forward']['cumulative_delta_rho2']:.8f} | {j['coefficients']['ln_m']['coefficient']:.8f} |")
    lines += ["", "λは各外側学習区間内の開催日WFのみで選択。オフセットβも内側学習区間ごとにMから推定し、内側評価日や外側後半を使用しない。", "",
              "| λ | β罰則なしΔρ² | オフセットΔρ² |", "|---|---:|---:|"]
    free = s["joint_L2"].get("lambda_sensitivity", []); offset = s["joint_L2_offset"].get("lambda_sensitivity", [])
    for a, c in zip(free, offset):
        lines.append(f"| {a['lambda']} | {a['evaluation']['delta_rho2']:.9f} | {c['evaluation']['delta_rho2']:.9f} |")
    lines += ["", "この後半曲線は感度表示のみ。λ選択には使わない。λ→∞で指数係数が0へ向かい、両方式ともMへ一致することを試験する。", "",
              "## 係数と符号変化率", "",
              "| 指数 | 現行重み | β罰則なし係数 | 符号変化率 | オフセット係数 | 符号変化率 |",
              "|---|---:|---:|---:|---:|---:|"]
    for index in list(INDICES) + ["ln_m"]:
        if "coefficients" not in s["joint_L2"]:
            continue
        a = s["joint_L2"]["coefficients"][index]; c = s["joint_L2_offset"]["coefficients"][index]
        weight = (s["current_weights"].get("weights") or {}).get(index, "—")
        lines.append(f"| {index} | {weight} | {a['coefficient']:.8f} | {a['sign_flip_fraction']:.1%} | {c['coefficient']:.8f} | {c['sign_flip_fraction']:.1%} |")
    lines += ["", "係数はレース内1SDあたり。現行重みと尺度が異なる。符号変化率は学習内選択済みλを固定した1000回bootstrap。", "",
              "## 指数別検定", "",
              "200回シャッフルは記述対照として維持。Holmはbootstrap pへ変更せず、13検定に分解能が足りないことを判定欄へ明示する。", "",
              "| 指数 | 後半Δρ² | 95%区間 | shuffle95%点 | Holm判定 | WF累積 |",
              "|---|---:|---|---:|---|---:|"]
    for index in INDICES:
        r = s["single_index"]["indices"][index]; m = r["measurement"]
        if "chronological" not in m:
            continue
        ci = m["bootstrap"]["conditional_holdout"]["ci95"]
        label = "200対照では分解能不足" if r["holm_decision"] == "RESOLUTION_INSUFFICIENT" else str(r["holm_reject"])
        lines.append(f"| {index} | {m['decision']['delta_rho2']:.8f} | [{ci[0]:.8f}, {ci[1]:.8f}] | {m['decision']['shuffle_p95']:.8f} | {label} | {m['walk_forward']['cumulative_delta_rho2']:.8f} |")
    lines += ["", "最小p=1/201、Holm初期閾値=.05/13。分解能不足を有意差なしの証明としない。今回の補正前の正の上積みも未確認。", "",
              "## Base13の2軸表（順位なし）", "",
              "単独ρ²はln mを明示的に入れないモデルの予測力であり、市場との独立性を示す値ではない。50.0単独では補完と断定せず、fallback/DCRとUNVALIDATEDを分離。", "",
              "| 指数 | 補完等率 | fallback/DCR率 | UNVALIDATED率 | 単独ρ²（全期間） | 単独ρ²（後半） | 市場由来対照 |",
              "|---|---:|---:|---:|---:|---:|---|"]
    for r in s["base13_quality_predictive_axes"]["rows"]:
        lines.append(f"| {r['index']} | {r['default_or_fallback_rate']:.1%} | {r['fallback_DCR_rate']:.1%} | {r['UNVALIDATED_rate']:.1%} | {r['standalone_rho2_full']} | {r['standalone_rho2_holdout']} | {'VMI: 市場の言い換え対照' if r['market_derived_control'] else '—'} |")
    vmi = s["VMI_market_control"]
    lines += ["", "実際に消費されたVMI成分件数：" + b.canonical(vmi["observed_component_features"]) + "。",
              "登録Manifestにはexpert_support等もあるが、現在のVMI消費と将来の別データ構成を混同しない。", "",
              "## ZAI_WINの合成効率", "",
              "| モデル（市場変数ln mなし） | 後半単独ρ² |", "|---|---:|"]
    for name, value in s["composition_efficiency"]["holdout_rho2"].items():
        lines.append(f"| {name} | {value} |")
    lines += ["", "F-joint13はVMIを含むため市場由来情報を含む。VMIを除いたF-joint12を補助として併記。単独予測力の改善と市場上積みは別で、新係数・重みは実装しない。", "",
              "## 運用・未確定事項", "",
              "確定オッズは別PRのコード/fixture試験まで。外部取得Workflow、11/7〜11/8の手動更新例は実行していない。200R超でΔρ²区間下限・WF累積・β安定性を確認し、500R前に採用判断しない。", ""]
    lines += ["- " + x for x in s["method_notes"]]
    return "\n".join(lines) + "\n"

def run(root, start, end, asof, out, *, bootstrap_reps=1000, shuffle_reps=200, seed=b.SEED, reuse_single=None):
    root, out = Path(root).resolve(), Path(out).resolve()
    if out.exists():
        raise FileExistsError("OUTPUT_MUST_BE_NEW_DIRECTORY")
    if start > end or end > asof:
        raise ValueError("REQUIRE_FROM_LE_TO_LE_ASOF")
    if out.is_relative_to(root) and not out.is_relative_to(root / "runtime/reports/benter_second_stage"):
        raise ValueError("OUTPUT_IN_INPUT_OR_PRODUCTION_TREE_FORBIDDEN")
    inputs = b.Inputs(root); series, rows, audit = inputs.load(start, end, asof)
    races = series["pre_signature"]
    if not races:
        raise ValueError("NO_ELIGIBLE_PHASE0_COHORT")
    arrays, audits, ledger = load_indices(root, races, rows, inputs)
    previous = None
    if reuse_single is not None:
        single, previous = reuse_single_index(reuse_single, inputs, races, audits, start, end, asof, bootstrap_reps, shuffle_reps, seed)
    else:
        single = per_index(races, arrays, audits, bootstrap_reps=bootstrap_reps, shuffle_reps=shuffle_reps, seed=seed)
    joint = joint_analysis(races, arrays, bootstrap_reps=bootstrap_reps, seed=seed, mode="free")
    offset = joint_analysis(races, arrays, bootstrap_reps=bootstrap_reps, seed=seed, mode="offset")
    features = joint_analysis(races, arrays, bootstrap_reps=bootstrap_reps, seed=seed, mode="features_only")
    no_vmi_indices = tuple(k for k in INDICES if k != "VMI")
    no_vmi = {k: np.delete(v, INDICES.index("VMI"), axis=1) for k, v in arrays.items()}
    features_no_vmi = joint_analysis(races, no_vmi, indices=no_vmi_indices, bootstrap_reps=bootstrap_reps, seed=seed, mode="features_only")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".benter-index-", dir=out.parent) as temp:
        staged = Path(temp) / "new-asof"
        phase0 = b.run(root, start, end, asof, staged, bootstrap_reps=bootstrap_reps, shuffle_reps=shuffle_reps, seed=seed)
        assert phase0["input_files_sha256"] == {k: v for k, v in inputs.manifest.items() if k in phase0["input_files_sha256"]}
        timing = odds_sensitivity(races, series["final_odds"], rows, phase0["series"]["pre_signature"])
        arrival = arrival_forecast(races, audit, root, inputs, asof=asof)
        weights = weights_from_source(root, inputs)
        mapping_path = root / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json"
        mapping = inputs.read(mapping_path) if mapping_path.exists() else {}
        declared_vmi = {k: v["VMI"] for k, v in mapping.get("index_profiles", {}).items() if isinstance(v, dict) and "VMI" in v}
        legacy_path = root / "runtime/reports/benter_second_stage/2026-11-03-phase05/index_diagnostics.json"
        legacy = previous if previous is not None else inputs.read(legacy_path) if legacy_path.exists() else None
        legacy_joint = legacy["joint_L2"] if legacy else None
        legacy_defect = {"status": "DESIGN_DEFECT_MARKET_BETA_PENALIZED_NOT_INDEX_EFFECT",
            "historical_period": "2026-10-11/2026-11-01",
            "source_path": legacy_path.relative_to(root).as_posix() if legacy_path.exists() else None,
            "old_holdout_delta_rho2": legacy_joint["chronological"]["delta_rho2"] if legacy_joint else -.08892396626557722,
            "old_WF_delta_rho2": legacy_joint["walk_forward"]["cumulative_delta_rho2"] if legacy_joint else -.053491544425462584,
            "old_beta": legacy_joint["coefficients"]["ln_m"]["coefficient"] if legacy_joint else .37498583861061147}
        p0 = phase0["series"]["pre_signature"]
        composition = {"interpretation": "No explicit market covariate is NOT statistical independence from market",
            "holdout_rho2": {
                "ZAI_WIN": p0.get("chronological", {}).get("evaluation", {}).get("models", {}).get("F", {}).get("rho2"),
                "JTI": single["indices"]["JTI"]["measurement"].get("chronological", {}).get("evaluation", {}).get("models", {}).get("F", {}).get("rho2"),
                "KGI": single["indices"]["KGI"]["measurement"].get("chronological", {}).get("evaluation", {}).get("models", {}).get("F", {}).get("rho2"),
                "F_joint13_includes_market_derived_VMI": features.get("chronological", {}).get("rho2"),
                "F_joint12_excludes_VMI": features_no_vmi.get("chronological", {}).get("rho2")},
            "weight_change_implemented": False}
        summary = {"schema": "BENTER_INDEX_DIAGNOSTICS_OFFLINE_V2_PHASE06", "classification": "OFFLINE_RESEARCH_NOT_PRODUCTION",
            "period": phase0["period"], "cohort": {"n_races": len(races), "n_runners": sum(len(r.ids) for r in races),
                "race_ids": [r.race_id for r in sorted(races, key=lambda r: (b.timestamp(r.post_at), r.race_id))],
                "same_phase0_rules": True, "phase0_input_file_count": len(phase0["input_files_sha256"])},
            "configuration": {"indices": list(INDICES), "bootstrap_reps": bootstrap_reps, "shuffle_reps": shuffle_reps,
                "seed": seed, "high_default_reference_annotation_threshold": REFERENCE_RATE,
                "primary_KPI": "CHRONOLOGICAL_OUT_OF_SAMPLE_INCREMENT", "lambda_grid": list(LAMBDA_GRID),
                "market_beta_penalized": False},
            "single_index": single, "joint_L2": joint, "joint_L2_offset": offset,
            "F_joint": features, "F_joint_without_VMI": features_no_vmi,
            "legacy_design_defect": legacy_defect, "composition_efficiency": composition,
            "base13_quality_predictive_axes": quality_axes(single),
            "VMI_market_control": {"role": "MARKET_REPHRASING_CONTROL",
                "observed_component_features": audits["VMI"].get("component_feature_counts", {}),
                "declared_manifest_profiles": declared_vmi,
                "evidence_path": "final_prediction_package.index_provenance_replay.runners[*].base_index_trace.VMI.components",
                "not_an_independent_non_market_signal": True},
            "odds_sensitivity": timing, "arrival": arrival, "current_weights": weights,
            "priority_proposal": {"status": "MARKET_INCREMENT_NOT_DISTINGUISHABLE", "ranking": None,
                                  "replacement": "DATA_QUALITY_X_STANDALONE_RHO2", "production_change": False},
            "reference_resolution": {"status": "CLOSED_BY_OWNER_EXPLANATION", "explanation": REFERENCE_RESOLUTION,
                "independent_Claude_code_reexecution": False, "old_phase0_asof_unchanged": True},
            "software": {"numpy": np.__version__, "scipy": b.scipy.__version__,
                "phase06_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "phase0_code_sha256": hashlib.sha256(Path(getattr(b, "CALCULATOR_SOURCE", b.__file__)).read_bytes()).hexdigest()},
            "input_files_sha256": dict(sorted(inputs.manifest.items())),
            "phase0_summary_sha256": hashlib.sha256((staged / "summary.json").read_bytes()).hexdigest(),
            "method_notes": [
                "50.0単独で補完と断定しない。fallback/DCRとUNVALIDATEDは別集計。値欠損0は原典実測100%ではない。",
                "指数別のM/F/C、1000回bootstrap、200対照の分布は#362と同じ。検定法は変えずHolm判定の分解能不足を明示する方式を選択。",
                "市場βの罰則は0。オフセット版のβは各内側/外側/再標本化学習区間だけでMから推定。λ候補は100、1000を追加し、後半曲線でλを選ばない。",
                "F-jointはβ=0で13指数のL2のみ。VMIを含むため市場由来情報を含む。VMI除外12指数版は補助診断。",
                "単独ρ²は市場との独立性を証明しない。点推定で改修優先順位を付けず、データ品質と単独予測力の2軸を示す。",
                "符号変化率は選択済みλ固定のbootstrapで、モデル選択の不確実性を全部含む区間ではない。",
                "旧-0.0889等は市場βまで縮約した設計欠陥による値として保持し、指数の効果と解釈しない。旧asof・Frozen原本は上書きしない。",
                "オッズ時点効果と確定オッズ比較は未確定。新しい外部取得、本番Workflow、将来更新例は実行しない。",
                "手設定重み・Policy・Base13/Derived7・AKI・MEC・Capital・買い目は変更しない。真正Forward OOSや実購入PFSは成立させない。",
            ]}
        changed = [p for p, h in inputs.manifest.items() if hashlib.sha256((root / p).read_bytes()).hexdigest() != h]
        if changed:
            raise ValueError("INPUT_SHA_CHANGED_DURING_ANALYSIS:" + ",".join(changed))
        (staged / "index_diagnostics.json").write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n", encoding="utf-8")
        (staged / "index_diagnostics.md").write_text(render_markdown(summary), encoding="utf-8")
        phase0_md = staged / "summary.md"
        phase0_md.write_text(reconcile_phase0_markdown(phase0_md.read_text()), encoding="utf-8")
        with (staged / "index_ledger.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(ledger[0]), lineterminator="\n")
            writer.writeheader(); writer.writerows(ledger)
        staged.rename(out)
    return summary

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--from", dest="start", type=date.fromisoformat, required=True)
    p.add_argument("--to", dest="end", type=date.fromisoformat, required=True)
    p.add_argument("--asof", type=date.fromisoformat, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument("--bootstrap-reps", type=int, default=1000)
    p.add_argument("--shuffle-reps", type=int, default=200)
    p.add_argument("--seed", type=int, default=b.SEED)
    p.add_argument("--reuse-single", type=Path, help="Reuse only SHA-verified unchanged per-index statistics")
    a = p.parse_args(argv)
    s = run(a.root, a.start, a.end, a.asof, a.out, bootstrap_reps=a.bootstrap_reps, shuffle_reps=a.shuffle_reps, seed=a.seed, reuse_single=a.reuse_single)
    print(b.canonical({"n_races": s["cohort"]["n_races"], "n_runners": s["cohort"]["n_runners"],
        "joint_holdout_delta_rho2": s["joint_L2"].get("chronological", {}).get("delta_rho2"), "output": str(a.out)}))


if __name__ == "__main__":
    main()
