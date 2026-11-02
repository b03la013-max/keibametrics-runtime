"""Offline Base13 market-increment diagnostics; no Production imports or writes.

Runs Phase 0 unchanged and Phase 0.5 into one NEW asof directory. All fits are
research measurements, never new index values, predictions or betting policy.
"""
from __future__ import annotations

import argparse
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
LAMBDA_GRID = (.0001, .001, .01, .1, 1., 10.)
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
            "coverage_weight": trace.get("coverage_weight")}


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
                        "rule_id_counts": dict(sorted(Counter(c["rule_id"] or "MISSING" for c in cells).items()))}
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


def per_index(races, arrays, audits, *, indices=INDICES, bootstrap_reps=1000, shuffle_reps=200, seed=b.SEED):
    results, p_values = {}, {}
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
        p_values[index] = p
        results[index] = {"audit": audits[index], "measurement": compact(measured), "shuffle_p_one_sided": p,
                          "excluded_races_with_missing_index": len(races) - len(eligible)}
    adjusted = holm(p_values)
    for index, result in results.items():
        decision = result["measurement"]["decision"]
        unadjusted = decision["Yes_No"] == "Yes" and p_values[index] <= .05
        reject = unadjusted and adjusted[index] <= .05
        result.update(holm_adjusted_p=adjusted[index], unadjusted_signal=unadjusted,
                      holm_reject=reject, interpretation="EXPLORATORY_SIGNAL_NOT_ADOPTION" if reject else
                      "CANDIDATE_ONLY_AFTER_MULTIPLE_TESTING" if unadjusted else "NO_CONFIRMED_INCREMENT")
    return {"indices": results, "multiple_testing": {"method": f"HOLM_STEP_DOWN_{len(indices)}_ONE_SIDED_SHUFFLE_P_VALUES",
            "n_hypotheses": len(indices), "alpha": .05, "minimum_shuffle_p": 1 / (shuffle_reps + 1),
            "first_holm_threshold": .05 / len(indices),
            "resolution_sufficient_for_any_rejection": 1 / (shuffle_reps + 1) <= .05 / len(indices),
            "limitation": "200 shuffles cannot resolve p<=0.05/13 with the plus-one correction; lack of Holm rejection is not proof of no information."}}


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

    def fit(self, strength, weights=None):
        if strength <= 0:
            raise ValueError("L2_STRENGTH_MUST_BE_POSITIVE")
        w = np.ones(len(self.races)) if weights is None else np.asarray(weights, float)
        if not np.isfinite(w).all() or np.any(w < 0) or w.sum() <= 0:
            raise ValueError("INVALID_RACE_WEIGHTS")
        def objective(theta):
            ll, p = self.evaluate(theta)
            expected = np.add.reduceat(p[:, None] * self.x, self.base.starts, axis=0)
            return (-float(w @ ll) / w.sum() + .5 * strength * float(theta @ theta),
                    np.sum(w[:, None] * (expected - self.target), axis=0) / w.sum() + strength * theta)
        initial = np.zeros(self.x.shape[1]); initial[-1] = 1.
        result = minimize(objective, initial, jac=True, method="BFGS", options={"gtol": 1e-8, "maxiter": 1000})
        gradient = float(np.max(np.abs(objective(result.x)[1])))
        if not np.isfinite(result.x).all() or gradient > 1e-6:
            raise ValueError("JOINT_L2_NOT_CONVERGED")
        return result.x, {"optimizer_success": bool(result.success), "gradient_max_abs": gradient}


def select_lambda(training, *, grid=LAMBDA_GRID):
    """Inner expanding-date validation sees ONLY the supplied training races."""
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
        row = {"validation_date": day, "training_dates": sorted({r.race.race_date for r in past}),
               "training_races": len(past), "validation_races": len(now), "validation_LL": {}}
        assert max(row["training_dates"]) < day
        for strength in grid:
            theta, _ = train.fit(strength)
            total = float(test.evaluate(theta)[0].sum())
            losses[strength][0] -= total; losses[strength][1] += len(now)
            row["validation_LL"][str(strength)] = total
        folds.append(row)
    if folds:
        selected = min(grid, key=lambda k: (losses[k][0] / losses[k][1], -k))
    else:
        selected = 1. if 1. in grid else max(grid)
    return {"selected_lambda": float(selected), "grid": list(grid), "inner_folds": folds,
            "status": "PAST_DATES_ONLY_SELECTED" if folds else "NO_INNER_HISTORY_FIXED_DEFAULT",
            "validation_mean_NLL": {str(k): v[0] / v[1] if v[1] else None for k, v in losses.items()},
            "objective": "MEAN_RACE_NLL_PLUS_LAMBDA_OVER_2_TIMES_L2_ALL_14_COEFFICIENTS",
            "selection_training_dates": days}


def joint_score(test, theta, market):
    choices = MultiChoices(test)
    ll = float(choices.evaluate(theta)[0].sum())
    ll0 = float(choices.base.ll0.sum())
    lm = float(choices.base.evaluate("M", market)[0].sum())
    return {"n_races": len(test), "LL": ll, "LL0": ll0, "M_LL": lm,
            "rho2": 1 - ll / ll0, "M_rho2": 1 - lm / ll0, "delta_rho2": (lm - ll) / ll0}


def joint_analysis(races, arrays, *, indices=INDICES, bootstrap_reps=1000, seed=b.SEED, grid=LAMBDA_GRID):
    ordered = sorted(races, key=lambda r: (b.timestamp(r.post_at), r.race_id))
    training, testing = strict_split(ordered)
    vectors = {r.race_id: VectorRace(r, standardize(arrays[r.race_id])) for r in ordered
               if np.isfinite(arrays[r.race_id]).all()}
    train = [vectors[r.race_id] for r in training if r.race_id in vectors]
    test = [vectors[r.race_id] for r in testing if r.race_id in vectors]
    if not train or not test:
        return {"status": "INSUFFICIENT_COMPLETE_CASES", "n_races": len(vectors)}
    tuning = select_lambda(train, grid=grid)
    choices = MultiChoices(train); strength = tuning["selected_lambda"]
    theta, optimizer = choices.fit(strength)
    market = choices.base.fit("M")
    result = {"status": "EXPLORATORY_L2_NOT_PRODUCTION", "n_races": len(vectors), "training_races": len(train),
              "test_races": len(test), "excluded_incomplete_races": len(ordered) - len(vectors),
              "tuning": tuning, "optimizer": optimizer, "chronological": joint_score(test, theta, market)}
    rng = np.random.default_rng(seed); draws = []
    fixed_delta, refit_delta = [], []
    testing_choices = MultiChoices(test)
    original_c = testing_choices.evaluate(theta)[0]
    original_m = testing_choices.base.evaluate("M", market)[0]
    for _ in range(bootstrap_reps):
        w = np.bincount(rng.integers(0, len(train), len(train)), minlength=len(train))
        tw = np.bincount(rng.integers(0, len(test), len(test)), minlength=len(test))
        coef, _ = choices.fit(strength, w); draws.append(coef)
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
            "interpretation": "COEFFICIENT_SIGN_STABILITY_CONDITIONAL_ON_TRAINING_SELECTED_LAMBDA; not post-selection confidence"}
    daily, ll, lm, ll0 = [], 0., 0., 0.
    vr = list(vectors.values())
    for day in sorted({r.race.race_date for r in vr}):
        past = [r for r in vr if r.race.race_date < day]; now = [r for r in vr if r.race.race_date == day]
        row = {"date": day, "training_races": len(past), "n_races": len(now)}
        if past:
            tuned = select_lambda(past, grid=grid); trained = MultiChoices(past)
            coef, _ = trained.fit(tuned["selected_lambda"])
            scored = joint_score(now, coef, trained.base.fit("M"))
            row.update(status="NESTED_PAST_DATES_ONLY", tuning=tuned, evaluation=scored,
                       coefficients={k: float(v) for k, v in zip(names, coef)})
            ll += scored["LL"]; lm += scored["M_LL"]; ll0 += scored["LL0"]
        else:
            row["status"] = "NO_PRIOR_TRAINING_NOT_SCORED"
        daily.append(row)
    result["walk_forward"] = {"daily": daily, "cumulative_delta_rho2": (lm - ll) / ll0 if ll0 else None,
                              "cumulative_LL0": ll0, "cumulative_LL": ll, "cumulative_M_LL": lm}
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


def render_markdown(s):
    lines = ["# 指数別の市場上積み診断・Phase 0.5", "",
        "SPEC / CODE: 実装済。CIはPRのRun証拠で確認。DEPLOYED / LIVE: 未実施。", "",
        f"{s['period']['from']}〜{s['period']['to']}、asof {s['period']['asof']}。{s['cohort']['n_races']}R・{s['cohort']['n_runners']}頭。",
        "既存の指数・重み・Policy・券面に変更なし。500R到達後に同じ設計で再検証する。", "",
        REFERENCE_RESOLUTION, "", "## 指数別・後半評価", "",
        "補完率は『50.0ちょうど又は明示fallback/DCR規則』の和集合。50.0だけで補完と断定しない。25%以上は参考表示（分析上の注記）。", "",
        "| 指数 | 補完等率 | 欠損頭 | 50頭 | fallback/DCR頭 | UNVALIDATED頭 | 単独ρ² | Δρ² | 95%区間 | shuffle95%点 | Holm p | 判定 | WF累積 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---:|"]
    for k in INDICES:
        r = s["single_index"]["indices"][k]; a = r["audit"]; m = r["measurement"]
        if "chronological" not in m:
            lines.append(f"| {k} | — | {a['counts']['missing']} | — | — | — | — | — | — | — | — | 未評価 | — |")
            continue
        e = m["chronological"]["evaluation"]; interval = m["bootstrap"]["conditional_holdout"]["ci95"]
        note = "参考/" if a["reference_only_high_default_rate"] else ""
        label = "Holm通過・研究候補" if r["holm_reject"] else "候補止まり" if r["unadjusted_signal"] else "上積み未確認"
        lines.append(f"| {k} | {a['default_or_fallback_rate']:.1%} | {a['counts']['missing']} | {a['counts']['exact_50']} | {a['counts']['fallback_or_DCR_rule']} | {a['counts']['UNVALIDATED']} | {e['models']['F']['rho2']:.6f} | {e['delta_rho2']:.6f} | [{interval[0]:.6f}, {interval[1]:.6f}] | {m['decision']['shuffle_p95']:.6f} | {r['holm_adjusted_p']:.6f} | {note}{label} | {m['walk_forward']['cumulative_delta_rho2']:.6f} |")
    mt = s["single_index"]["multiple_testing"]
    lines += ["", f"Holmの分解能：最小p={mt['minimum_shuffle_p']:.6f}、最初の閾値={mt['first_holm_threshold']:.6f}。200対照ではHolm有意判定に届かない。対照数を増やす案は提案に留め、今回の200回は維持。", "",
              "## 同時L2モデル", ""]
    joint = s["joint_L2"]
    if "chronological" in joint:
        e = joint["chronological"]
        lines += [f"後半Δρ²={e['delta_rho2']:.8f}、λ={joint['tuning']['selected_lambda']}。λは学習期間内の開催日WFで選び、日次WFも各日より前だけで選び直す。",
                  f"累積WF Δρ²={joint['walk_forward']['cumulative_delta_rho2']:.8f}。L2は13係数と市場βを含む全14係数へ適用。", "",
                  "| 指数 | 現行ZAI直接重み | L2係数（レース内1SD） | bootstrap符号変化率 |", "|---|---:|---:|---:|"]
        weights = s["current_weights"].get("weights") or {}
        for k in list(INDICES) + ["ln_m"]:
            c = joint["coefficients"][k]
            w = weights.get(k, "対象外")
            lines.append(f"| {k} | {w} | {c['coefficient']:.6f} | {c['sign_flip_fraction']:.1%} |")
        lines += ["", "現行重みは元指数の1点あたり、L2はレース内1SDあたり。尺度が異なり、そのまま置換できない。BVI/VMIは現行ZAI_WINの直接式に入らない。",
                  "符号変化率は学習側bootstrap 1000回で、学習内で選んだλを固定した条件付き診断。正則化選択自体の不確実性を含む採用保証ではない。", ""]
    timing = s["odds_sensitivity"]
    lines += ["## オッズ観測時点", "", f"発走前分数（Frozen予定発走基準）：{timing['minutes_to_post']}。", "",
              "| 帯（分） | 全R | 帯内再推定Mρ²（学習内） | 後半R | 固定学習Mρ² | 固定学習ZAI Δρ² |", "|---|---:|---:|---:|---:|---:|"]
    for r in timing["bands"]:
        e = r.get("fixed_global_training_holdout")
        lines.append(f"| {r['minutes_band']} | {r['n_races']} | {r.get('full_band_refitted_M_rho2','—')} | {r['holdout_races']} | {e['models']['M']['rho2'] if e else '—'} | {e['delta_rho2'] if e else '—'} |")
    lines += ["", f"明示的な確定オッズ：{timing['secondary_final_odds']['n_available_final_odds_races']}R。主系列との時点差の影響は、対応する複数時点がなく未確定。帯別差にはRace構成の差も混在する。",
              "既存JRA公式サイトが最終オッズを公開している。現行保存入力には確定として分類・結合された系列がない。新Providerは必須ではなく、既存取得元への取得/Reader結合追加がSPECとして必要。今回は取得を実装しない。", "",
              "## データ到達見通し", "", "| 日付 | 管理R | FINAL | 適格R | FINAL除外理由 | FINALなしの元Status |", "|---|---:|---:|---:|---|---|"]
    arr = s["arrival"]
    for r in arr["daily"]:
        lines.append(f"| {r['date']} | {r['managed_status_races']} | {r['FINAL_files']} | {r['eligible_races']} | {r['FINAL_exclusion_reasons']} | {r['no_FINAL_original_status_counts']} |")
    lines += ["", f"実績平均：{arr['mean_eligible_races_per_raceday']:.3f}R/開催日。1開催日は全場をまとめた同一日。", "",
              "| シナリオ（将来のみ） | R/日 | 目標 | 追加開催日 | 推計到達日 | 短縮開催日 | 短縮暦日 |", "|---|---:|---:|---:|---|---:|---:|"]
    for name, r in arr["scenarios"].items():
        for e in r["estimates"]:
            lines.append(f"| {name} | {r['races_per_raceday']:.3f} | {e['target']} | {e['additional_racedays']} | {e['estimated_date']} | {e['racedays_saved_vs_baseline']} | {e['calendar_days_saved_vs_baseline']} |")
    lines += ["", "公式公表日割に同じ平均ペースを当てた条件付き見積もり。過去の署名なしRaceを事前成功へ復元する計画ではなく、正規NO-BETや障害Scopeを解除する案でもない。", ""]
    lines += ["- " + x for x in arr["top3_actions_proposal_only"]]
    lines += ["", "## バックフィルSPEC", "", "**条件付き可**：発走前Raw・観測オッズ・当時のCorpus/Rule/Codeが完全に残る場合、別REPLAY母数として実行可能。現在のページや後年Corpusから欠落した当時情報は復元できない。正式178Rや真正OOSへ加算しない。",
              "在庫・時点証明1〜2人日、完全入力がある場合のAdapter2〜4人日、レビュー・回帰1〜2人日、合計4〜8人日の工数見積もり。未実装。", "",
              "## Base13優先順位案（提案のみ）", ""]
    for p in s["priority_proposal"]:
        lines.append(f"- {p['rank']}: {p['index']} — 後半Δρ²={p['delta_rho2']:.6f}、WF={p['walk_forward_delta']:.6f}、補完等率={p['default_rate']:.1%}。{p['proposal']}")
    lines += ["", "未知未来500Rで再検証するまで採用しない。係数・閾値・KRS Physics・Capitalは変更しない。", "", "## 未確定仕様と解釈", ""]
    lines += ["- " + x for x in s["method_notes"]]
    lines += ["", "## 正規情報源", ""]
    lines += ["- " + u for u in arr["calendar_sources"] + [timing["final_odds_source_research"]["official_documentation"], timing["final_odds_source_research"]["alternative_requires_owner_license_review"]]]
    return "\n".join(lines) + "\n"


def run(root, start, end, asof, out, *, bootstrap_reps=1000, shuffle_reps=200, seed=b.SEED):
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
    single = per_index(races, arrays, audits, bootstrap_reps=bootstrap_reps, shuffle_reps=shuffle_reps, seed=seed)
    joint = joint_analysis(races, arrays, bootstrap_reps=bootstrap_reps, seed=seed)
    # Phase 0 functions and file bytes are untouched. Its own report is created
    # in an owned staging directory and published together with Phase 0.5.
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".benter-index-", dir=out.parent) as temp:
        staged = Path(temp) / "new-asof"
        phase0 = b.run(root, start, end, asof, staged, bootstrap_reps=bootstrap_reps, shuffle_reps=shuffle_reps, seed=seed)
        assert phase0["input_files_sha256"] == {k: v for k, v in inputs.manifest.items() if k in phase0["input_files_sha256"]}
        timing = odds_sensitivity(races, series["final_odds"], rows, phase0["series"]["pre_signature"])
        arrival = arrival_forecast(races, audit, root, inputs, asof=asof)
        weights = weights_from_source(root, inputs)
        priority = []
        ranked = sorted(INDICES, key=lambda k: (-single["indices"][k]["measurement"].get("decision", {}).get("delta_rho2", -math.inf), k))
        for i, k in enumerate(ranked, 1):
            r = single["indices"][k]; m = r["measurement"]
            if "chronological" not in m:
                continue
            priority.append({"rank": i, "index": k, "delta_rho2": m["decision"]["delta_rho2"],
                "walk_forward_delta": m["walk_forward"]["cumulative_delta_rho2"], "default_rate": r["audit"]["default_or_fallback_rate"],
                "proposal": "適格Evidenceの保持・時点とConsumer接続を先に点検し、500Rで同じ設計を再試験。重み採用はしない。"})
        summary = {"schema": "BENTER_INDEX_DIAGNOSTICS_OFFLINE_V1", "classification": "OFFLINE_RESEARCH_NOT_PRODUCTION",
            "period": phase0["period"], "cohort": {"n_races": len(races), "n_runners": sum(len(r.ids) for r in races),
                "race_ids": [r.race_id for r in sorted(races, key=lambda r: (b.timestamp(r.post_at), r.race_id))],
                "same_phase0_rules": True, "phase0_input_file_count": len(phase0["input_files_sha256"])},
            "configuration": {"indices": list(INDICES), "bootstrap_reps": bootstrap_reps, "shuffle_reps": shuffle_reps,
                "seed": seed, "high_default_reference_annotation_threshold": REFERENCE_RATE,
                "primary_KPI": "CHRONOLOGICAL_OUT_OF_SAMPLE_INCREMENT", "lambda_grid": list(LAMBDA_GRID)},
            "single_index": single, "joint_L2": joint, "odds_sensitivity": timing, "arrival": arrival,
            "current_weights": weights, "priority_proposal": priority,
            "reference_resolution": {"status": "CLOSED_BY_OWNER_EXPLANATION", "explanation": REFERENCE_RESOLUTION,
                "independent_Claude_code_reexecution": False, "old_phase0_asof_unchanged": True},
            "software": {"numpy": np.__version__, "scipy": b.scipy.__version__,
                "phase05_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "phase0_code_sha256": hashlib.sha256(Path(b.__file__).read_bytes()).hexdigest()},
            "input_files_sha256": dict(sorted(inputs.manifest.items())),
            "phase0_summary_sha256": hashlib.sha256((staged / "summary.json").read_bytes()).hexdigest(),
            "method_notes": [
                "50.0ちょうどは既定値候補の指標であり、単独では補完と断定しない。fallback/DCRとUNVALIDATEDは別列・和集合を明示。UNVALIDATEDは欠損や無許可の断定ではない。",
                "真の欠損は新たに補完せず、その指数又は同時モデルからRace全体を除外。同じ178Rを基準に減少があれば明記。",
                "補完等率25%以上の参考注記は今回の表示上の分析基準。Productionの閾値・数値規則ではない。",
                "単独ρ²・Δρ²・bootstrap・shuffleは#362と同じ発走順前後半。日付WFと日付ブロックCVは別の診断。",
                "Holm pは(1+shuffle>=観測の回数)/(B+1)。200回・13検定では分解能不足。Holm非有意を情報なしの証明と解釈しない。",
                "L2候補λは事前固定。選択は外側学習データ内の過去開催日→次開催日のみ。全14係数（市場βも含む）を正則化し、未来の開催日は選択に使わない。",
                "同時モデルのbootstrapは学習内選択済みλを固定。符号変化率は条件付き診断であり、係数の因果効果・新Production重みではない。",
                "市場を含む相関した指数の係数と現行の元スコア重みは尺度・目的が異なる。係数の大小をそのまま採用しない。",
                "オッズ時点帯はRace構成と交絡。確定オッズ又は同一Raceの複数時点がなく、時点に対するKPIの不変性は未証明。",
                "既存signed/Frozen SOURCE・FINAL・RESULTは読取のみ。暗号署名の再検証、真正Forward OOS、実購入PFSを成立させる処理ではない。",
                "Phase0 summary.jsonは変更しない。Owner説明による未再現注記訂正は新asofのsummary.mdとreference_resolutionに記録し、過去asofは保存する。",
            ]}
        # Independent read-back protects every input, including newly read Status
        # and formula text, before any completed output directory is published.
        changed = [p for p, h in inputs.manifest.items() if hashlib.sha256((root / p).read_bytes()).hexdigest() != h]
        if changed:
            raise ValueError("INPUT_SHA_CHANGED_DURING_ANALYSIS:" + ",".join(changed))
        (staged / "index_diagnostics.json").write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        (staged / "index_diagnostics.md").write_text(render_markdown(summary), encoding="utf-8")
        phase0_md = staged / "summary.md"
        phase0_md.write_text(reconcile_phase0_markdown(phase0_md.read_text()), encoding="utf-8")
        with (staged / "index_ledger.csv").open("w", encoding="utf-8", newline="") as handle:
            fields = list(ledger[0])
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
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
    a = p.parse_args(argv)
    s = run(a.root, a.start, a.end, a.asof, a.out, bootstrap_reps=a.bootstrap_reps, shuffle_reps=a.shuffle_reps, seed=a.seed)
    print(b.canonical({"n_races": s["cohort"]["n_races"], "n_runners": s["cohort"]["n_runners"],
        "joint_holdout_delta_rho2": s["joint_L2"].get("chronological", {}).get("delta_rho2"), "output": str(a.out)}))


if __name__ == "__main__":
    main()
