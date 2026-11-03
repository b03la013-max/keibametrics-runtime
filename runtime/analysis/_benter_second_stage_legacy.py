"""Offline conditional-logit measurement. Never imported by a Production path.

Only stored FINAL / SOURCE attempts / RESULT JSON are read. No network, keys,
signing, recommendation, settlement or Production module imports are used.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass, replace
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import minimize

JST = timezone(timedelta(hours=9))
SEED = 20261103
RACE_ID = re.compile(r"KM-JRA-[A-Z]{3}-(\d{8})-R\d{2}")
MODELS = {"M": ("beta",), "F": ("a",), "C": ("a", "beta")}


def timestamp(value):
    t = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("TIMESTAMP_TIMEZONE_MISSING")
    return t


def number(value):
    if isinstance(value, bool) or value is None:
        raise ValueError("NUMERIC_VALUE_MISSING")
    x = float(value)
    if not math.isfinite(x):
        raise ValueError("NUMERIC_VALUE_NONFINITE")
    return x


def runner_id(value):
    if isinstance(value, bool) or not re.fullmatch(r"[0-9]+", str(value)):
        raise ValueError("RUNNER_ID_INVALID")
    n = int(value)
    if not 1 <= n <= 18:
        raise ValueError("RUNNER_ID_INVALID")
    return str(n)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


@dataclass(frozen=True)
class Race:
    race_id: str
    race_date: str
    post_at: str
    ids: tuple[str, ...]
    zai: np.ndarray
    z: np.ndarray
    m: np.ndarray
    y: np.ndarray


class Choices:
    """Vectorized per-race softmax; bootstrap weights count whole races."""
    def __init__(self, races):
        self.races = races
        self.starts = np.r_[0, np.cumsum([len(r.ids) for r in races])[:-1]].astype(int)
        self.counts = np.array([len(r.ids) for r in races])
        self.groups = np.repeat(np.arange(len(races)), self.counts)
        self.z = np.concatenate([r.z for r in races])
        self.lm = np.log(np.concatenate([r.m for r in races]))
        self.y = np.concatenate([r.y for r in races])
        self.ll0 = -np.log(self.counts)

    def evaluate(self, model, parameters):
        a = parameters.get("a", 0.0)
        beta = parameters.get("beta", 0.0)
        u = a * self.z + beta * self.lm
        maxima = np.maximum.reduceat(u, self.starts)
        ex = np.exp(u - maxima[self.groups])
        normalizers = np.add.reduceat(ex, self.starts)
        lp = u - maxima[self.groups] - np.log(normalizers)[self.groups]
        p = ex / normalizers[self.groups]
        ll = np.add.reduceat(self.y * lp, self.starts)
        return ll, p

    def fit(self, model, weights=None):
        weights = np.ones(len(self.races)) if weights is None else np.asarray(weights, float)
        if not np.isfinite(weights).all() or np.any(weights < 0) or weights.sum() <= 0:
            raise ValueError("INVALID_RACE_WEIGHTS")
        x = np.column_stack([self.z if key == "a" else self.lm for key in MODELS[model]])
        target = np.add.reduceat(self.y[:, None] * x, self.starts, axis=0)

        def objective(theta):
            params = dict(zip(MODELS[model], theta))
            ll, p = self.evaluate(model, params)
            expected = np.add.reduceat(p[:, None] * x, self.starts, axis=0)
            return (-float(weights @ ll) / weights.sum(),
                    np.sum(weights[:, None] * (expected - target), axis=0) / weights.sum())

        initial = np.array([0.0 if k == "a" else 1.0 for k in MODELS[model]])
        result = minimize(objective, initial, jac=True, method="BFGS",
                          options={"gtol": 1e-8, "maxiter": 1000})
        _, gradient = objective(result.x)
        stationary = float(np.max(np.abs(gradient))) <= 1e-6
        if not np.isfinite(result.x).all() or not stationary:
            raise ValueError("CONDITIONAL_LOGIT_NOT_CONVERGED:" + model)
        return {**{k: float(v) for k, v in zip(MODELS[model], result.x)},
                "converged": True, "optimizer_success": bool(result.success),
                "gradient_max_abs": float(np.max(np.abs(gradient))),
                "design_rank": int(np.linalg.matrix_rank(x - np.repeat(
                    np.add.reduceat(x, self.starts, axis=0) / self.counts[:, None], self.counts, axis=0))),
                "large_parameter_warning": bool(np.max(np.abs(result.x)) > 50)}


def scores(choices, fitted, weights=None):
    w = np.ones(len(choices.races)) if weights is None else np.asarray(weights, float)
    ll0 = float(w @ choices.ll0)
    models = {}
    for model, params in fitted.items():
        ll, _ = choices.evaluate(model, params)
        total = float(w @ ll)
        models[model] = {"LL": total, "LL0": ll0, "rho2": 1 - total / ll0,
                         "parameters": params}
    return {"n_races": int(w.sum()), "models": models,
            "delta_rho2": models["C"]["rho2"] - models["M"]["rho2"]}


def fit_models(choices):
    return {model: choices.fit(model) for model in MODELS}


def calibration(choices, fitted):
    out = {}
    for model, params in fitted.items():
        _, p = choices.evaluate(model, params)
        bins = []
        for i, ix in enumerate(np.array_split(np.argsort(p, kind="stable"), 10), 1):
            if not len(ix):
                continue
            bins.append({"decile": i, "n_runners": len(ix),
                         "predicted_min": float(p[ix].min()), "predicted_max": float(p[ix].max()),
                         "mean_probability": float(p[ix].mean()),
                         "observed_win_weight": float(choices.y[ix].sum()),
                         "observed_win_rate": float(choices.y[ix].mean())})
        out[model] = bins
    return out


def distribution(values):
    a = np.asarray(values, float)
    return {"n": len(a), "mean": float(a.mean()), "p05": float(np.quantile(a, .05)),
            "p95": float(np.quantile(a, .95)), "ci95": [float(x) for x in np.quantile(a, [.025, .975])],
            "replicates": [float(x) for x in a]}


def bootstrap(train, test, fitted, *, repetitions, seed):
    """Paired holdout race bootstrap plus separate train+test refit interval."""
    rng = np.random.default_rng(seed)
    fixed, refitted, a_draws = [], [], []
    n, nt = len(train.races), len(test.races)
    for _ in range(repetitions):
        tw = np.bincount(rng.integers(0, nt, nt), minlength=nt)
        fixed.append(scores(test, fitted, tw)["delta_rho2"])
        rw = np.bincount(rng.integers(0, n, n), minlength=n)
        f = {m: train.fit(m, rw) for m in ("M", "C")}
        refitted.append(scores(test, f, tw)["delta_rho2"])
        a_draws.append(f["C"]["a"])
    return {"unit": "RACE", "seed": seed, "repetitions": repetitions,
            "primary": "PAIRED_HOLDOUT_RACES_FIXED_TRAINED_PARAMETERS",
            "conditional_holdout": distribution(fixed),
            "training_and_holdout_refit": distribution(refitted),
            "refit_C_a": distribution(a_draws)}


def shuffle_control(races, split, *, repetitions, seed, market_fits):
    rng = np.random.default_rng(seed)
    full, oos, a_draws = [], [], []
    for _ in range(repetitions):
        shuffled = [replace(r, z=r.z[rng.permutation(len(r.ids))]) for r in races]
        all_choices = Choices(shuffled)
        combined = all_choices.fit("C")
        full.append(scores(all_choices, {"M": market_fits["full"], "C": combined})["delta_rho2"])
        training, testing = Choices(shuffled[:split]), Choices(shuffled[split:])
        cf = training.fit("C")
        oos.append(scores(testing, {"M": market_fits["train"], "C": cf})["delta_rho2"])
        a_draws.append(cf["a"])
    return {"seed": seed, "repetitions": repetitions,
            "method": "INDEPENDENT_WITHIN_RACE_Z_PERMUTATION_IN_TRAIN_AND_TEST_C_REFITTED",
            "full_in_sample": distribution(full), "chronological_out_of_sample": distribution(oos),
            "training_C_a": distribution(a_draws)}


def analyze(races, *, bootstrap_reps=1000, shuffle_reps=200, seed=SEED):
    if bootstrap_reps < 2 or shuffle_reps < 2:
        raise ValueError("AT_LEAST_TWO_RESAMPLES_REQUIRED")
    races = sorted(races, key=lambda r: (timestamp(r.post_at), r.race_id))
    if len({r.race_id for r in races}) != len(races):
        raise ValueError("DUPLICATE_RACE_IN_SERIES")
    if not races:
        return {"status": "NO_ELIGIBLE_RACES", "n_races": 0, "n_runners": 0,
                "decision": {"Yes_No": "No", "reason": "INSUFFICIENT_DATA"}}
    all_choices = Choices(races)
    full_fit = fit_models(all_choices)
    result = {"status": "MEASURED_NOT_PRODUCTION", "n_races": len(races),
              "n_runners": sum(len(r.ids) for r in races),
              "first_place_dead_heat_races": int(sum(np.count_nonzero(r.y) > 1 for r in races)),
              "full_in_sample": scores(all_choices, full_fit),
              "full_calibration": calibration(all_choices, full_fit)}
    split = len(races) // 2
    # Do not train on a race starting at the same instant as a test race.
    while split and timestamp(races[split - 1].post_at) == timestamp(races[split].post_at):
        split -= 1
    if not split:
        result["decision"] = {"Yes_No": "No", "reason": "NO_STRICT_TEMPORAL_SPLIT"}
        return result
    train, test = Choices(races[:split]), Choices(races[split:])
    trained = fit_models(train)
    result["chronological"] = {"training_races": split, "test_races": len(races) - split,
                               "train_last_post_at": races[split - 1].post_at,
                               "test_first_post_at": races[split].post_at,
                               "evaluation": scores(test, trained),
                               "calibration": calibration(test, trained)}
    result["bootstrap"] = bootstrap(train, test, trained, repetitions=bootstrap_reps, seed=seed)
    result["shuffle_control"] = shuffle_control(races, split, repetitions=shuffle_reps, seed=seed,
                                                  market_fits={"full": full_fit["M"], "train": trained["M"]})
    days = sorted({r.race_date for r in races})
    daily, cumulative = [], {m: 0.0 for m in MODELS}
    cumulative_ll0 = 0.0
    for day in days:
        before = [r for r in races if r.race_date < day]
        today = Choices([r for r in races if r.race_date == day])
        row = {"date": day, "n_races": len(today.races), "training_races": len(before)}
        if before:
            f = fit_models(Choices(before))
            evaluation = scores(today, f)
            row.update(status="OUT_OF_SAMPLE", evaluation=evaluation,
                       beta_bias_note="BETA_GT_1_FAVOURITE_LONGSHOT_BIAS_DIAGNOSTIC_ONLY" if f["M"]["beta"] > 1 else None)
            for m in MODELS:
                cumulative[m] += evaluation["models"][m]["LL"]
            cumulative_ll0 += evaluation["models"]["M"]["LL0"]
        else:
            row["status"] = "NO_PRIOR_TRAINING_NOT_SCORED"
        daily.append(row)
    result["walk_forward"] = {"daily": daily, "cumulative_LL0": cumulative_ll0,
                              "cumulative_LL": cumulative,
                              "cumulative_rho2": {m: 1 - ll / cumulative_ll0 for m, ll in cumulative.items()} if cumulative_ll0 else None,
                              "cumulative_delta_rho2": (cumulative["M"] - cumulative["C"]) / cumulative_ll0 if cumulative_ll0 else None}
    folds = []
    if len(days) >= 5:
        for k, held_out in enumerate(np.array_split(np.array(days), 5), 1):
            held = set(held_out)
            f = fit_models(Choices([r for r in races if r.race_date not in held]))
            evaluation = scores(Choices([r for r in races if r.race_date in held]), f)
            folds.append({"fold": k, "test_dates": sorted(held), "evaluation": evaluation})
    result["date_block_5fold"] = {"status": "MEASURED" if folds else "FEWER_THAN_FIVE_DATES",
                                  "interpretation": "DATE_BLOCK_CV_NOT_FORWARD_ONLY_TRAINING_MAY_INCLUDE_LATER_DATES",
                                  "folds": folds,
                                  "mean_delta_rho2": float(np.mean([f["evaluation"]["delta_rho2"] for f in folds])) if folds else None}
    delta = result["chronological"]["evaluation"]["delta_rho2"]
    low = result["bootstrap"]["conditional_holdout"]["ci95"][0]
    threshold = result["shuffle_control"]["chronological_out_of_sample"]["p95"]
    result["decision"] = {"Yes_No": "Yes" if low > 0 and delta > threshold else "No",
                          "primary_KPI": "CHRONOLOGICAL_OUT_OF_SAMPLE_DELTA_RHO2",
                          "delta_rho2": delta, "ci95_lower_gt_zero": bool(low > 0),
                          "shuffle_p95": threshold, "delta_gt_shuffle_p95": bool(delta > threshold),
                          "production_change_authority": False}
    return result


def reference_comparison(races, primary):
    """Disclose supplied approximate benchmarks; never use them to choose a fit."""
    if "chronological" not in primary:
        return {"status": "INSUFFICIENT_DATA"}
    full = primary["full_in_sample"]; holdout = primary["chronological"]["evaluation"]
    supplied = {"n_races": 178, "full_M_rho2": .27, "holdout_M_rho2": .35,
                "full_F_rho2": .10, "holdout_F_rho2": .086,
                "holdout_delta_rho2": -.0098, "holdout_ci95": [-.0177, -.0016],
                "CV_mean_delta_rho2": -.0015, "full_C_a": -.004, "full_C_beta": 1.34}
    measured = {"n_races": len(races), "full_M_rho2": full["models"]["M"]["rho2"],
                "holdout_M_rho2": holdout["models"]["M"]["rho2"],
                "full_F_rho2": full["models"]["F"]["rho2"],
                "holdout_F_rho2": holdout["models"]["F"]["rho2"],
                "holdout_delta_rho2": holdout["delta_rho2"],
                "holdout_ci95": primary["bootstrap"]["conditional_holdout"]["ci95"],
                "CV_mean_delta_rho2": primary["date_block_5fold"]["mean_delta_rho2"],
                "full_C_a": full["models"]["C"]["parameters"]["a"],
                "full_C_beta": full["models"]["C"]["parameters"]["beta"]}
    raw = Choices([replace(r, z=r.zai) for r in races])
    raw_fit = scores(raw, fit_models(raw))
    return {"supplied_approximate_Claude_estimates": supplied, "specified_method": measured,
            "raw_scale_diagnostic_only_not_primary": raw_fit,
            "explanation": [
                f"主実装は{len(races)}R、発走順{primary['chronological']['training_races']}/{primary['chronological']['test_races']}、レース内母標準偏差で標準化、署名以前の最終観測。監査側のRace一覧・分割境界・コード・CI再標本化法は未提供。",
                "同一入力を未標準化ZAIで全期間推定するとa=-0.004付近になるが、これは異なる設計の補助診断。主KPIへ採用しない。",
                "主結果の検証ρ²/Δρ²/CIは提示値と未一致。レース数は概数と一致、主系列に署名後オッズの採用やオッズ欠損除外はない。原因をオッズ時点や除外規則と断定する証拠はない。",
                "分割境界や尺度が与える影響はあるが、監査の実因確定には監査側のコード又はtrain/test Race ID・odds SHAが必要。数値合わせのための境界・係数変更は行わない。",
            ]}


def result_outcome(official):
    """Only non-starters are removed; a DNF remains a losing choice."""
    excluded, finish = {}, {}
    for row in official.get("non_finishers", []):
        rid = runner_id(row.get("runner_id", row.get("horse_no")))
        status = str(row.get("status") or row.get("finish_status") or row.get("reason") or row.get("raw_finish_label") or "").upper()
        if status in {"CANCELLED", "SCRATCHED", "出走取消", "取消"}:
            excluded[rid] = "CANCELLED"
        elif status in {"EXCLUDED", "競走除外", "除外"}:
            excluded[rid] = "EXCLUDED"
    for rid in official.get("refund_runner_ids", []):
        excluded.setdefault(runner_id(rid), "OFFICIAL_NON_STARTER_REFUND")
    groups = official.get("finish_groups")
    orders = official.get("top3_orders")
    top = official.get("top3") or []
    for position, rid in enumerate(official.get("finish_order", top), 1):
        if isinstance(rid, dict):
            finish[runner_id(rid.get("runner_id", rid.get("horse_no")))] = int(rid["finish"])
        else:
            finish[runner_id(rid)] = position
    if groups:
        grouped_ids = []
        for group in groups:
            for rid in group["horse_numbers"]:
                identity = runner_id(rid)
                grouped_ids.append(identity)
                finish[identity] = int(group["finish"])
        if len(grouped_ids) != len(set(grouped_ids)):
            raise ValueError("RESULT_FINISH_GROUP_DUPLICATE")
        winners = {runner_id(rid) for group in groups if int(group["finish"]) == 1 for rid in group["horse_numbers"]}
        if top and runner_id(top[0]) not in winners:
            raise ValueError("RESULT_WINNER_REPRESENTATION_MISMATCH")
        if orders and {runner_id(order[0]) for order in orders} != winners:
            raise ValueError("RESULT_WINNER_REPRESENTATION_MISMATCH")
    elif orders:
        winners = {runner_id(order[0]) for order in orders}
        # Do not invent finish positions at tied lower places.
        positions = {}
        for order in orders:
            for pos, rid in enumerate(order, 1):
                positions.setdefault(runner_id(rid), []).append(pos)
        for rid, pos in positions.items():
            finish[rid] = min(pos)
    elif official.get("dead_heat"):
        raise ValueError("DEAD_HEAT_FIRST_PLACE_UNRESOLVED")
    elif top:
        winners = {runner_id(top[0])}
    else:
        raise ValueError("OFFICIAL_WINNER_MISSING")
    if not winners or winners & set(excluded):
        raise ValueError("WINNER_NON_STARTER_CONFLICT")
    return winners, excluded, finish


def market_rows(observation):
    rows = {}
    for r in observation.get("runners", []):
        rid = runner_id(r.get("runner_id", r.get("horse_no")))
        if r.get("horse_no") is not None and runner_id(r["horse_no"]) != rid:
            raise ValueError("MARKET_RUNNER_IDENTITY_MISMATCH")
        if rid in rows:
            raise ValueError("MARKET_RUNNER_DUPLICATE")
        rows[rid] = r
    return rows


class Inputs:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.manifest = {}

    def read(self, path):
        data = path.read_bytes()
        self.manifest[path.relative_to(self.root).as_posix()] = hashlib.sha256(data).hexdigest()
        return json.loads(data)

    def load(self, start, end, asof):
        races = {"pre_signature": [], "final_odds": []}
        ledger, exclusions, observations = [], [], []
        discovered = 0
        last_date = min(end, asof)
        asof_end = datetime.combine(asof, time.max, tzinfo=JST)
        for path in sorted((self.root / "runtime/final_artifacts").glob("KM-JRA-*.json")):
            match = RACE_ID.fullmatch(path.stem)
            if not match or not start <= date.fromisoformat(match[1][:4] + "-" + match[1][4:6] + "-" + match[1][6:]) <= last_date:
                continue
            discovered += 1
            final = self.read(path)
            rid = path.stem
            models = final.get("final_prediction_package", {}).get("index_provenance_replay", {}).get("runners", {})
            if any(runner_id(k) != k for k in models):
                raise ValueError("MODEL_RUNNER_IDENTITY_INVALID:" + path.name)
            if final.get("race_id") != rid or final.get("family_id", "JRA") != "JRA":
                raise ValueError("FINAL_RACE_IDENTITY_MISMATCH:" + path.name)
            result_path = self.root / "runtime/results" / path.name
            result = self.read(result_path) if result_path.exists() else None
            if result is not None and result.get("race_id") != rid:
                raise ValueError("RESULT_RACE_IDENTITY_MISMATCH:" + path.name)
            candidates, rejected = [], []
            for source in sorted((self.root / "runtime/executions" / (rid + "-LIVE-R1") / "SOURCE/runs").glob("*/source_attempt_envelope.json")):
                artifact = self.read(source).get("artifact", {})
                if artifact.get("race_id") != rid:
                    raise ValueError("SOURCE_RACE_IDENTITY_MISMATCH:" + str(source))
                market = artifact.get("jra_official_market_observation")
                if not market:
                    continue
                try:
                    when = timestamp(market.get("captured_at", market.get("observed_at")))
                    if market.get("official") is not True:
                        raise ValueError("MARKET_NOT_OFFICIAL")
                    market_rows(market)
                    candidates.append((when, source.relative_to(self.root).as_posix(), market))
                except (ValueError, TypeError) as exc:
                    rejected.append({"path": source.relative_to(self.root).as_posix(), "reason": str(exc)})
            try:
                signed = timestamp(final["final_receipt"]["receipt"]["timestamp"])
                post = timestamp(final["scheduled_post_at"])
                if signed >= post:
                    raise ValueError("FINAL_NOT_PRE_RACE")
                clock_error = None
            except (KeyError, ValueError, TypeError):
                signed = post = None
                clock_error = "FINAL_SIGNATURE_OR_POST_TIME_INVALID"
            try:
                winners, cancelled, finish = result_outcome(result["official_result"]) if result else (set(), {}, {})
                outcome_error = None if result else "RESULT_MISSING"
                captured = (result or {}).get("official_result", {}).get("captured_at")
                if captured and timestamp(captured) > asof_end:
                    outcome_error = "RESULT_AFTER_ASOF"
            except (KeyError, ValueError, TypeError) as exc:
                winners, cancelled, finish = set(), {}, {}
                outcome_error = "RESULT_INVALID:" + str(exc)
            eligible = [x for x in candidates if signed is not None and x[0] <= signed]
            chosen = max(eligible, key=lambda x: (x[0], x[1])) if eligible else None
            ambiguous = False
            if chosen:
                peers = [market_rows(x[2]) for x in eligible if x[0] == chosen[0]]
                # Comparison only: nonfinite prices are rejected below, never
                # serialized into outputs or silently replaced by older odds.
                ambiguous = len({json.dumps(x, ensure_ascii=False, sort_keys=True, allow_nan=True) for x in peers}) > 1
            final_candidates = [x for x in candidates if x[0] <= asof_end and
                                (x[2].get("is_final") is True or x[2].get("odds_type") == "FINAL")]
            official = (result or {}).get("official_result", {})
            if official.get("final_odds"):
                fo = official["final_odds"]
                if isinstance(fo, list):
                    fo = {"runners": fo, "captured_at": official.get("captured_at")}
                try:
                    when = timestamp(fo.get("captured_at", fo.get("observed_at")))
                    if when <= asof_end:
                        final_candidates.append((when, result_path.relative_to(self.root).as_posix(), fo))
                except (ValueError, TypeError):
                    rejected.append({"path": result_path.relative_to(self.root).as_posix(), "reason": "FINAL_ODDS_TIMESTAMP_INVALID"})
            final_chosen = max(final_candidates, key=lambda x: (x[0], x[1])) if final_candidates else None
            observations.append({"race_id": rid, "signature_at": signed.isoformat() if signed else None,
                                 "stored_final_freeze_at": final.get("final_freeze_timestamp"),
                                 "candidates": len(candidates), "after_signature_candidates": sum(signed is not None and x[0] > signed for x in candidates),
                                 "selected_pre_signature_path": chosen[1] if chosen else None,
                                 "rejected_candidates": rejected})
            for series, selected in (("pre_signature", chosen), ("final_odds", final_chosen)):
                reason = clock_error or outcome_error
                if not models:
                    reason = reason or "MODEL_RUNNERS_MISSING"
                if not selected:
                    reason = reason or ("FINAL_ODDS_NOT_AVAILABLE" if series == "final_odds" else
                                        "POST_SIGNATURE_ODDS_ONLY" if candidates and signed else "ODDS_OBSERVATION_MISSING")
                if ambiguous and series == "pre_signature":
                    reason = reason or "LATEST_ODDS_TIMESTAMP_AMBIGUOUS"
                mr = market_rows(selected[2]) if selected else {}
                ids = set(models) | set(mr) | set(cancelled) | set(finish)
                active = sorted(ids - set(cancelled), key=int)
                if not reason and (not winners <= set(active) or len(active) < 2):
                    reason = "ACTIVE_WINNER_UNIVERSE_INVALID"
                raw_zai, odds = {}, {}
                for horse in active:
                    try:
                        raw_zai[horse] = number(models.get(horse, {}).get("zai_win"))
                    except (TypeError, ValueError):
                        reason = reason or "MODEL_VALUE_MISSING"
                    try:
                        odds[horse] = number(mr.get(horse, {}).get("win_odds"))
                        if odds[horse] <= 0:
                            raise ValueError("NONPOSITIVE_ODDS")
                    except (TypeError, ValueError):
                        odds.pop(horse, None)
                        reason = reason or "WIN_ODDS_MISSING"
                if reason:
                    exclusions.append({"series": series, "race_id": rid, "reason": reason,
                                       "n_runners": len(ids), "odds_observed_at": selected[0].isoformat() if selected else None})
                    z, market = {}, {}
                else:
                    values = np.array([raw_zai[i] for i in active])
                    standard = (values - values.mean()) / values.std(ddof=0) if values.std(ddof=0) else np.zeros(len(values))
                    inverse = 1 / np.array([odds[i] for i in active])
                    probs = inverse / inverse.sum()
                    z, market = dict(zip(active, standard)), dict(zip(active, probs))
                    y = np.array([1 / len(winners) if i in winners else 0 for i in active])
                    races[series].append(Race(rid, post.astimezone(JST).date().isoformat(), final["scheduled_post_at"],
                                               tuple(active), values, standard, probs, y))
                # The secondary series is separate, never substituted into the primary ledger.
                if series == "final_odds" and not selected:
                    continue
                for horse in sorted(ids, key=int):
                    ledger.append({"series": series, "segment": "JRA", "race_id": rid,
                                   "post_at": final.get("scheduled_post_at"), "runner_id": horse, "horse_no": int(horse),
                                   "zai_win": raw_zai.get(horse), "z": z.get(horse), "win_odds": odds.get(horse), "m": market.get(horse),
                                   "odds_observed_at": selected[0].isoformat() if selected else None,
                                   "minutes_to_post": (post - selected[0]).total_seconds() / 60 if post and selected else None,
                                   "finish_pos": finish.get(horse), "winner_weight": 1 / len(winners) if horse in winners else 0,
                                   "excluded_reason": cancelled.get(horse, reason),
                                   "source_path": selected[1] if selected else None})
        return races, ledger, {"discovered_FINAL_races": discovered, "excluded_races": exclusions,
                               "race_exclusion_counts": {s: dict(sorted(Counter(x["reason"] for x in exclusions if x["series"] == s).items())) for s in races},
                               "runner_exclusion_counts": dict(sorted(Counter(r["excluded_reason"] for r in ledger if r["series"] == "pre_signature" and r["excluded_reason"]).items())),
                               "observation_selection": observations}


def render_markdown(summary):
    main = summary["series"]["pre_signature"]
    lines = ["# ベンター第2段階・オフライン市場結合テスト", "",
             "SPEC: PASS / CODE: 実装済 / CI: 別途Run証拠 / DEPLOYED: 未実施 / LIVE: 未実施", "",
             f"対象 {summary['period']['from']}〜{summary['period']['to']} / asof {summary['period']['asof']}。",
             "予測・重み・買い目・資金配分への反映なし。過去の署名済み原本の上書きなし。", "",
             f"主系列：{main['n_races']}レース・{main.get('n_runners', 0)}頭。第一着同着 {main.get('first_place_dead_heat_races', 0)}レース。", "",
             "| 評価 | M ρ² | F ρ² | C ρ² | Δρ² |", "|---|---:|---:|---:|---:|"]
    def metrics(label, score):
        ms = score["models"]
        return f"| {label} | {ms['M']['rho2']:.8f} | {ms['F']['rho2']:.8f} | {ms['C']['rho2']:.8f} | {score['delta_rho2']:.8f} |"
    if "full_in_sample" in main:
        lines.append(metrics("全期間・学習内", main["full_in_sample"]))
    if "chronological" in main:
        lines.append(metrics("前半学習・後半評価", main["chronological"]["evaluation"]))
        interval = main["bootstrap"]["conditional_holdout"]["ci95"]
        refit = main["bootstrap"]["training_and_holdout_refit"]["ci95"]
        lines += ["", f"後半Δρ²の95%区間（固定学習・レース再標本化）：{interval}。",
                  f"学習側も再推定した補助区間：{refit}。",
                  f"シャッフル対照200回相当（実回数 {summary['configuration']['shuffle_reps']}）：平均 {main['shuffle_control']['chronological_out_of_sample']['mean']:.8f} / 95%点 {main['shuffle_control']['chronological_out_of_sample']['p95']:.8f}。",
                  f"判定：**{main['decision']['Yes_No']}**（区間下限>0、かつ同じ後半評価のシャッフル95%点を上回るか）。", "",
                  "| モデル | 全期間 a | 全期間 β |", "|---|---:|---:|"]
        for m, v in main["full_in_sample"]["models"].items():
            p = v["parameters"]
            lines.append(f"| {m} | {p.get('a', '—')} | {p.get('beta', '—')} |")
        lines += ["", "β>1は本命・大穴バイアスの参考診断であり、運用変更の根拠にはしない。", "",
                  "## 開催日ウォークフォワード", "", "その日より前の開催日だけで学習。初日は学習データがなく評価しない。", "",
                  "| 日付 | 学習R | 評価R | Δρ² | C a | C β |", "|---|---:|---:|---:|---:|---:|"]
        for row in main["walk_forward"]["daily"]:
            e = row.get("evaluation")
            cp = e["models"]["C"]["parameters"] if e else {}
            lines.append(f"| {row['date']} | {row['training_races']} | {row['n_races']} | {e['delta_rho2'] if e else '未評価'} | {cp.get('a','—')} | {cp.get('beta','—')} |")
        lines += ["", f"累積Δρ²：{main['walk_forward']['cumulative_delta_rho2']}。", "",
                  "## 日付ブロック5分割", "", "これは前向き限定ではない補助CV。各foldの学習には評価日より後の開催日も含み得る。", "",
                  "| fold | 評価日 | Δρ² | C a | C β |", "|---|---|---:|---:|---:|"]
        for fold in main["date_block_5fold"]["folds"]:
            e = fold["evaluation"]; cp = e["models"]["C"]["parameters"]
            lines.append(f"| {fold['fold']} | {', '.join(fold['test_dates'])} | {e['delta_rho2']} | {cp['a']} | {cp['beta']} |")
        lines += ["", f"fold単純平均Δρ²：{main['date_block_5fold']['mean_delta_rho2']}。", "",
                  "## 後半評価の校正表（等件数10分位）", "",
                  "| モデル | 分位 | 頭数 | 平均予測確率 | 観測勝利重み率 |", "|---|---:|---:|---:|---:|"]
        for model, bins in main["chronological"]["calibration"].items():
            for b in bins:
                lines.append(f"| {model} | {b['decile']} | {b['n_runners']} | {b['mean_probability']:.6f} | {b['observed_win_rate']:.6f} |")
    comparison = summary["reference_reproduction"]
    if "specified_method" in comparison:
        lines += ["", "## Claude試算との比較", "", "| 指標 | 提示概数 | 指定法の実測 |", "|---|---:|---:|"]
        for key, value in comparison["specified_method"].items():
            lines.append(f"| {key} | {comparison['supplied_approximate_Claude_estimates'][key]} | {value} |")
        raw = comparison["raw_scale_diagnostic_only_not_primary"]
        lines += ["", f"未標準化ZAIの全期間補助診断：Fρ²={raw['models']['F']['rho2']:.8f}、C a={raw['models']['C']['parameters']['a']:.8f}、C β={raw['models']['C']['parameters']['beta']:.8f}。主KPIではない。", ""]
        lines += ["- " + note for note in comparison["explanation"]]
    lines += ["", "## 除外と時点", "", "主系列のレース除外：`" + canonical(summary["input_audit"]["race_exclusion_counts"]["pre_signature"]) + "`。",
              "主系列の馬単位除外：`" + canonical(summary["input_audit"]["runner_exclusion_counts"]) + "`。",
              f"副系列final_odds：{summary['series']['final_odds']['n_races']}R。明示的な確定オッズのみ。主系列へ混合しない。", "",
              "## 解釈・未確定仕様", ""]
    lines += ["- " + s for s in summary["method_notes"]]
    lines += ["", "## 更新方法", "", "新しい出力先を指定して手動実行する。既存ディレクトリへは書かない。自動スケジュールは未実装・承認待ち。", "", "```bash",
              "python runtime/analysis/benter_second_stage.py --from 2026-10-11 --to YYYY-MM-DD --asof YYYY-MM-DD --out runtime/reports/benter_second_stage/YYYY-MM-DD-new", "```", ""]
    return "\n".join(lines)


def run(root, start, end, asof, out, *, bootstrap_reps=1000, shuffle_reps=200, seed=SEED):
    root, out = Path(root).resolve(), Path(out).resolve()
    if start > end or end > asof:
        raise ValueError("REQUIRE_FROM_LE_TO_LE_ASOF")
    if out.exists():
        raise FileExistsError("OUTPUT_MUST_BE_NEW_DIRECTORY")
    if out.is_relative_to(root) and not out.is_relative_to(root / "runtime/reports/benter_second_stage"):
        raise ValueError("OUTPUT_IN_INPUT_OR_PRODUCTION_TREE_FORBIDDEN")
    inputs = Inputs(root)
    races, ledger, audit = inputs.load(start, end, asof)
    summary = {"schema": "BENTER_SECOND_STAGE_OFFLINE_V1", "classification": "OFFLINE_ANALYSIS_ONLY_NOT_PRODUCTION",
               "period": {"from": start.isoformat(), "to": end.isoformat(), "asof": asof.isoformat(), "timezone": "Asia/Tokyo"},
               "configuration": {"bootstrap_reps": bootstrap_reps, "shuffle_reps": shuffle_reps, "seed": seed,
                                 "z_standard_deviation_ddof": 0, "parameter_constraints": "NONE", "regularization": "NONE"},
               "software": {"numpy": np.__version__, "scipy": scipy.__version__, "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
               "segments": {"included": ["JRA"], "excluded": ["KRS", "LOCAL"]},
               "series": {s: analyze(rs, bootstrap_reps=bootstrap_reps, shuffle_reps=shuffle_reps, seed=seed) for s, rs in races.items()},
               "input_audit": audit, "input_files_sha256": dict(sorted(inputs.manifest.items())),
               "method_notes": [
                   "署名時刻はfinal_receipt.receipt.timestamp。別のfinal_freeze_timestampも監査欄へ保存し、同一時刻と仮定しない。暗号署名自体の再検証は本集計では行わない。",
                   "主系列は署名以前の最後の公式market snapshotを選択。同時刻の不一致は除外。馬ごとの古い値への混合・欠損の穴埋めは行わない。",
                   "取消・除外後、全Active馬のモデルとオッズが揃うレースだけを共通母数へ入れる。DNFは出走した負け馬として残す。",
                   "開催日と発走までの分数はFrozen scheduled_post_at基準。公式変更後の実発走時刻を別情報から推測しない。",
                   "主KPIと判定は前半学習・後半評価。同時発走を跨がない。全期間ρ²は学習内で、結合の増分が非負になりやすいため単独で判定しない。",
                   "主95%区間は学習係数固定のpaired後半レースbootstrap。曖昧な再学習の扱いは、学習レースも再抽出・再推定した補助区間を別掲。",
                   "シャッフルは各レース内のzを独立に入替え、結合モデルを再推定。主判定は同じ後半評価の対照95%点と比較。",
                   "結果の1着同着は各1/k。保存されたfinish_order/finish_groupsがない馬のfinish_posは空欄とし、4着以下を捏造しない。",
                   "確定オッズは明示的なis_final/odds_type=FINAL又はofficial_result.final_oddsのみ。発走後という時刻だけでは確定と認めない。",
                   "開催日5分割CVは補助診断で、前向きウォークフォワードとは分離。結果提供時刻の完全なasof履歴は入力仕様にないため、当時入手済みの証明や真正Forward OOSとは呼ばない。",
                   "生成時刻はgeneration.jsonへ分離。summary.jsonは同じ入力・コード・ソフトウェア・seedでバイト再現可能。",
               ]}
    summary["reference_reproduction"] = reference_comparison(races["pre_signature"], summary["series"]["pre_signature"])
    # Finish calculations and serialization before making the new directory.
    summary_text = json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    markdown = render_markdown(summary)
    out.mkdir(parents=True, exist_ok=False)
    (out / "summary.json").write_text(summary_text, encoding="utf-8")
    (out / "summary.md").write_text(markdown, encoding="utf-8")
    fields = ["race_id", "post_at", "runner_id", "horse_no", "zai_win", "z", "win_odds", "m", "odds_observed_at", "minutes_to_post", "finish_pos", "excluded_reason", "segment", "series", "winner_weight", "source_path"]
    with (out / "ledger.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(r for r in ledger if r["series"] == "pre_signature")
    if any(r["series"] == "final_odds" for r in ledger):
        with (out / "ledger_final_odds.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader(); writer.writerows(r for r in ledger if r["series"] == "final_odds")
    (out / "generation.json").write_text(json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(), "not_part_of_deterministic_summary": True}, sort_keys=True) + "\n")
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
    p.add_argument("--seed", type=int, default=SEED)
    a = p.parse_args(argv)
    summary = run(a.root, a.start, a.end, a.asof, a.out, bootstrap_reps=a.bootstrap_reps, shuffle_reps=a.shuffle_reps, seed=a.seed)
    primary = summary["series"]["pre_signature"]
    print(canonical({"n_races": primary["n_races"], "n_runners": primary.get("n_runners", 0), "decision": primary["decision"], "output": str(a.out)}))


if __name__ == "__main__":
    main()
