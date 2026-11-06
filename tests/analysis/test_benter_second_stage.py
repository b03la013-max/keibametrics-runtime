"""Synthetic choice experiments, recorded-input eligibility and isolation."""
import ast
import csv
import hashlib
import json
import socket
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime/analysis"))
import benter_second_stage as b


def synthetic(n=500, *, seed=803, information=True, runners=8):
    rng = np.random.default_rng(seed)
    races = []
    for i in range(n):
        market_logits = rng.normal(0, 1, runners)
        m = np.exp(market_logits - market_logits.max()); m /= m.sum()
        raw = rng.normal(size=runners) if information else np.log(m) + rng.normal(0, .6, runners)
        z = (raw - raw.mean()) / raw.std()
        utility = 1.2 * np.log(m) + (1.1 * z if information else 0)
        p = np.exp(utility - utility.max()); p /= p.sum()
        winner = rng.choice(runners, p=p)
        y = np.zeros(runners); y[winner] = 1
        post = datetime.fromisoformat("2026-10-11T10:00:00+09:00") + timedelta(days=i // 40, minutes=i % 40)
        races.append(b.Race(f"KM-JRA-TKY-{post:%Y%m%d}-R{i:04d}", post.date().isoformat(), post.isoformat(),
                            tuple(str(j + 1) for j in range(runners)), 70 + 5 * raw, z, m, y))
    return races


def test_true_extra_information_has_positive_oos_lower_bound_and_passes_control():
    result = b.analyze(synthetic(), bootstrap_reps=1000, shuffle_reps=200)
    assert result["chronological"]["evaluation"]["delta_rho2"] > .05
    assert result["bootstrap"]["conditional_holdout"]["ci95"][0] > 0
    assert result["bootstrap"]["training_and_holdout_refit"]["ci95"][0] > 0
    assert result["decision"]["Yes_No"] == "Yes"
    assert len(result["date_block_5fold"]["folds"]) == 5
    assert all(row["training_races"] == sum(r.race_date < row["date"] for r in synthetic())
               for row in result["walk_forward"]["daily"])
    for rows in result["chronological"]["calibration"].values():
        assert len(rows) == 10
        assert sum(r["n_runners"] for r in rows) == 250 * 8


def test_market_plus_noise_has_no_detected_increment_and_unstable_a():
    result = b.analyze(synthetic(600, seed=1101, information=False), bootstrap_reps=1000, shuffle_reps=200)
    assert abs(result["chronological"]["evaluation"]["delta_rho2"]) < .015
    draws = result["bootstrap"]["refit_C_a"]["replicates"]
    assert min(draws) < 0 < max(draws)
    assert result["decision"]["Yes_No"] == "No"


def test_shuffle_is_near_zero_and_seed_and_count_are_effective():
    rs = synthetic(240, seed=11)
    market = {"full": b.Choices(rs).fit("M"), "train": b.Choices(rs[:120]).fit("M")}
    first = b.shuffle_control(rs, 120, repetitions=200, seed=b.SEED, market_fits=market)
    other_seed = b.shuffle_control(rs, 120, repetitions=19, seed=b.SEED + 1, market_fits=market)
    other_count = b.shuffle_control(rs, 120, repetitions=23, seed=b.SEED, market_fits=market)
    assert abs(first["chronological_out_of_sample"]["mean"]) < .015
    assert np.ptp(first["chronological_out_of_sample"]["replicates"]) > 1e-4
    assert first["chronological_out_of_sample"]["replicates"][:19] != other_seed["chronological_out_of_sample"]["replicates"]
    assert first["chronological_out_of_sample"]["p95"] != other_count["chronological_out_of_sample"]["p95"]


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False))


def stored_race(root, *, number=1, late_only=False, missing_odds=False, tie=False,
                cancellations=False, final_odds=False):
    rid = f"KM-JRA-TKY-20261011-R{number:02d}"
    post = datetime.fromisoformat(f"2026-10-11T{10 + number // 10:02d}:{number % 10:02d}:00+09:00")
    final = {"race_id": rid, "family_id": "JRA", "scheduled_post_at": post.isoformat(),
             "final_receipt": {"receipt": {"timestamp": (post - timedelta(minutes=5)).isoformat()}},
             "final_prediction_package": {"index_provenance_replay": {"runners": {str(i): {"zai_win": 50 + i} for i in range(1, 7)}}}}
    runners = [{"runner_id": str(i), "horse_no": i, "win_odds": 1.4 * i, "popularity_rank": i} for i in range(1, 7)]
    result = {"race_id": rid, "official_result": {"top3": [1, 2, 3], "finish_order": [1, 2, 3, 4, 5, 6], "refund_runner_ids": [], "non_finishers": []}}
    if cancellations:
        for i, status in [(7, "CANCELLED"), (8, "EXCLUDED")]:
            final["final_prediction_package"]["index_provenance_replay"]["runners"][str(i)] = {"zai_win": 100}
            runners.append({"runner_id": str(i), "horse_no": i, "win_odds": None})
            result["official_result"]["non_finishers"].append({"horse_no": i, "status": status})
            result["official_result"]["refund_runner_ids"].append(i)
    if missing_odds:
        runners[5]["win_odds"] = None
    if tie:
        result["official_result"].update(dead_heat=True, finish_groups=[{"finish": 1, "horse_numbers": [1, 2]},
                                                                     {"finish": 3, "horse_numbers": [3]}])
    if final_odds:
        result["official_result"]["final_odds"] = {"captured_at": (post + timedelta(minutes=3)).isoformat(),
                                                   "runners": [{**r, "win_odds": 2 * r["win_odds"]} for r in runners]}
    market = {"official": True, "captured_at": (post - timedelta(minutes=10)).isoformat(), "runners": runners}
    envelope = {"artifact": {"race_id": rid, "jra_official_market_observation": market}}
    source = root / "runtime/executions" / (rid + "-LIVE-R1") / "SOURCE/runs"
    if not late_only:
        write_json(source / "10/source_attempt_envelope.json", envelope)
    late = json.loads(json.dumps(envelope)); late["artifact"]["jra_official_market_observation"]["captured_at"] = (post - timedelta(minutes=2)).isoformat()
    late["artifact"]["jra_official_market_observation"]["runners"][0]["win_odds"] = 999
    write_json(source / "20/source_attempt_envelope.json", late)
    write_json(root / "runtime/final_artifacts" / (rid + ".json"), final)
    write_json(root / "runtime/results" / (rid + ".json"), result)
    return rid


def load_fixture(root):
    return b.Inputs(root).load(date(2026, 10, 11), date(2026, 11, 1), date(2026, 11, 3))


def test_cancellation_missing_odds_tie_and_post_signature_odds(tmp_path):
    cancelled = stored_race(tmp_path, number=1, cancellations=True)
    missing = stored_race(tmp_path, number=2, missing_odds=True)
    late = stored_race(tmp_path, number=3, late_only=True)
    tied = stored_race(tmp_path, number=4, tie=True)
    races, ledger, audit = load_fixture(tmp_path)
    assert [r.race_id for r in races["pre_signature"]] == [cancelled, tied]
    assert all(len(r.ids) == 6 and np.isclose(r.m.sum(), 1) for r in races["pre_signature"])
    assert audit["race_exclusion_counts"]["pre_signature"] == {"POST_SIGNATURE_ODDS_ONLY": 1, "WIN_ODDS_MISSING": 1}
    assert audit["runner_exclusion_counts"]["CANCELLED"] == audit["runner_exclusion_counts"]["EXCLUDED"] == 1
    assert np.array_equal(races["pre_signature"][1].y, [.5, .5, 0, 0, 0, 0])
    rows = [r for r in ledger if r["race_id"] == late]
    assert all(r["win_odds"] is None and r["odds_observed_at"] is None for r in rows)
    assert next(r for r in ledger if r["race_id"] == cancelled and r["runner_id"] == "1")["win_odds"] == 1.4
    assert all(r["minutes_to_post"] == 10 for r in ledger if not r["excluded_reason"])
    assert not races["final_odds"]


def test_explicit_final_odds_are_separate_and_not_inferred_from_late_capture(tmp_path):
    stored_race(tmp_path, final_odds=True)
    rs, _, _ = load_fixture(tmp_path)
    assert len(rs["final_odds"]) == len(rs["pre_signature"]) == 1
    # Multiplying every odd preserves probabilities; it must not replace primary prices.
    assert np.allclose(rs["final_odds"][0].m, rs["pre_signature"][0].m)
    result = b.run(tmp_path, date(2026, 10, 11), date(2026, 11, 1), date(2026, 11, 3), tmp_path.parent / (tmp_path.name + "_report"), bootstrap_reps=3, shuffle_reps=3)
    assert result["series"]["pre_signature"]["n_races"] == 1


def test_nonfinisher_is_not_removed_and_unresolved_dead_heat_is_not_guessed():
    official = {"top3": [1, 2, 3], "non_finishers": [{"horse_no": 4, "status": "DID_NOT_FINISH"}]}
    assert b.result_outcome(official)[1] == {}
    with pytest.raises(ValueError, match="DEAD_HEAT_FIRST_PLACE"):
        b.result_outcome({**official, "dead_heat": True})
    assert b.result_outcome({**official, "non_finishers": [{"horse_no": 4, "finish_status": "CANCELLED"}]})[1] == {"4": "CANCELLED"}
    with pytest.raises(ValueError, match="WINNER_REPRESENTATION"):
        b.result_outcome({**official, "finish_groups": [{"finish": 1, "horse_numbers": [2, 3]}]})
    with pytest.raises(ValueError, match="FINISH_GROUP_DUPLICATE"):
        b.result_outcome({**official, "finish_groups": [{"finish": 1, "horse_numbers": [1]}, {"finish": 2, "horse_numbers": [1]}]})


def test_latest_eligible_observation_selected_and_same_time_conflicts_rejected(tmp_path):
    rid = stored_race(tmp_path)
    source = tmp_path / "runtime/executions" / (rid + "-LIVE-R1") / "SOURCE/runs"
    v = json.loads((source / "10/source_attempt_envelope.json").read_text())
    market = v["artifact"]["jra_official_market_observation"]
    market["captured_at"] = (b.timestamp(market["captured_at"]) + timedelta(minutes=4)).isoformat()
    market["runners"][0]["win_odds"] = 2.8
    write_json(source / "15/source_attempt_envelope.json", v)
    rs, rows, _ = load_fixture(tmp_path)
    assert len(rs["pre_signature"]) == 1
    assert next(r for r in rows if r["runner_id"] == "1")["win_odds"] == 2.8
    v["artifact"]["jra_official_market_observation"]["runners"][0]["win_odds"] = 3.2
    write_json(source / "16/source_attempt_envelope.json", v)
    rs, _, audit = load_fixture(tmp_path)
    assert not rs["pre_signature"]
    assert audit["race_exclusion_counts"]["pre_signature"] == {"LATEST_ODDS_TIMESTAMP_AMBIGUOUS": 1}


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf")])
def test_invalid_prices_are_not_imputed_or_used(tmp_path, value):
    rid = stored_race(tmp_path)
    p = tmp_path / "runtime/executions" / (rid + "-LIVE-R1") / "SOURCE/runs/10/source_attempt_envelope.json"
    v = json.loads(p.read_text());v["artifact"]["jra_official_market_observation"]["runners"][1]["win_odds"] = value;write_json(p, v)
    rs, _, audit = load_fixture(tmp_path)
    assert not rs["pre_signature"]
    assert audit["race_exclusion_counts"]["pre_signature"] == {"WIN_ODDS_MISSING": 1}


def test_determinism_full_output_guard_and_no_network(tmp_path, monkeypatch):
    root = tmp_path / "data"
    rs = synthetic(80, seed=30, runners=6)
    # Reuse realistic file schemas but use stochastic results to avoid artificial separation.
    for i, r in enumerate(rs, 1):
        rid = stored_race(root, number=i)
        p = root / "runtime/results" / (rid + ".json");v = json.loads(p.read_text())
        winner = int(r.ids[np.argmax(r.y)])
        order = [winner] + [k for k in range(1, 7) if k != winner]
        v["official_result"].update(top3=order[:3], finish_order=order); write_json(p, v)
    paths = list(root.rglob("*.json")); hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    def forbidden(*args, **kwargs): raise AssertionError("OFFLINE_ONLY")
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    for name in ["one", "two"]:
        b.run(root, date(2026, 10, 11), date(2026, 11, 1), date(2026, 11, 3), tmp_path / name, bootstrap_reps=8, shuffle_reps=8)
    assert (tmp_path / "one/summary.json").read_bytes() == (tmp_path / "two/summary.json").read_bytes()
    assert (tmp_path / "one/ledger.csv").read_bytes() == (tmp_path / "two/ledger.csv").read_bytes()
    assert hashes == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    with pytest.raises(FileExistsError, match="NEW_DIRECTORY"):
        b.run(root, date(2026, 10, 11), date(2026, 11, 1), date(2026, 11, 3), tmp_path / "one")
    with pytest.raises(ValueError, match="PRODUCTION_TREE"):
        b.run(root, date(2026, 10, 11), date(2026, 11, 1), date(2026, 11, 3), root / "runtime/results/new")
    with (tmp_path / "one/ledger.csv").open() as f:
        rows = list(csv.DictReader(f))
    assert len({(r["race_id"], r["runner_id"]) for r in rows}) == len(rows)


def test_uniform_market_and_constant_model_have_zero_gain():
    rs = synthetic(30)
    rs = [b.replace(r, m=np.full(len(r.ids), 1 / len(r.ids)), z=np.zeros(len(r.ids))) for r in rs]
    c = b.Choices(rs); score = b.scores(c, b.fit_models(c))
    assert abs(score["delta_rho2"]) < 1e-12
    assert all(abs(v["rho2"]) < 1e-12 for v in score["models"].values())


def test_core_imports_only_standard_math_libraries_and_has_no_production_hook():
    source = (ROOT / "runtime/analysis/benter_second_stage.py").read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom): assert not (node.module or "").startswith("jra_")
        if isinstance(node, ast.Import): assert not any(n.name.startswith("jra_") for n in node.names)
    for name in ["jra_delivery.py", "jra_production_postresult.py", "jra_source_runtime/jra_race_day_autopilot.py"]:
        path = ROOT / "runtime" / name
        if path.exists(): assert "benter_second_stage" not in path.read_text()
