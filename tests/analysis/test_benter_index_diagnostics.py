"""Synthetic signal, multiple testing, temporal isolation and frozen-input IO."""
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
import benter_index_diagnostics as d


def synthetic(n=480, *, seed=493, per_day=40):
    rng = np.random.default_rng(seed); races = []; arrays = {}
    for i in range(n):
        lm = rng.normal(size=8); market = np.exp(lm - lm.max()); market /= market.sum()
        signal = rng.normal(size=8); signal = (signal - signal.mean()) / signal.std()
        values = 65 + 6 * rng.normal(size=(8, 13))
        values[:, 0] = 65 + 6 * signal
        values[:, 1] = 65 + 6 * (np.log(market) + .5 * rng.normal(size=8))
        utility = 1.25 * np.log(market) + 1.6 * signal
        p = np.exp(utility - utility.max()); p /= p.sum()
        y = np.zeros(8); y[rng.choice(8, p=p)] = 1
        post = datetime.fromisoformat("2026-10-11T10:00:00+09:00") + timedelta(days=i // per_day, minutes=i % per_day)
        rid = f"KM-JRA-TKY-{post:%Y%m%d}-R{i:04d}"
        zai = values[:, 1]; z = (zai - zai.mean()) / zai.std()
        races.append(b.Race(rid, post.date().isoformat(), post.isoformat(), tuple(str(i) for i in range(1, 9)), zai, z, market, y))
        arrays[rid] = values
    return races, arrays


def test_only_extra_information_index_has_material_positive_increment():
    races, arrays = synthetic()
    selected = ("HPI", "SSI", "CFI")
    slim = {k: v[:, :3] for k, v in arrays.items()}
    out = d.per_index(races, slim, {k: {} for k in selected}, indices=selected,
                      bootstrap_reps=1000, shuffle_reps=200)
    result = out["indices"]
    signal = result["HPI"]["measurement"]
    assert signal["chronological"]["evaluation"]["delta_rho2"] > .05
    assert signal["bootstrap"]["conditional_holdout"]["ci95"][0] > 0
    for k in ("SSI", "CFI"):
        assert abs(result[k]["measurement"]["chronological"]["evaluation"]["delta_rho2"]) < .02
        assert not result[k]["unadjusted_signal"]


def test_holm_step_down_is_monotone_and_200_draw_resolution_is_insufficient():
    assert d.holm({"a": .01, "b": .04, "c": .03}) == {"a": .03, "b": .06, "c": .06}
    assert d.holm({"a": .2, "b": .9, "c": 1}) == {"a": pytest.approx(.6), "b": 1, "c": 1}
    thirteen = {k: 1 / 201 for k in d.INDICES}
    assert all(v > .05 for v in d.holm(thirteen).values())
    with pytest.raises(ValueError, match="INVALID_P_VALUE"):
        d.holm({"a": float("nan")})


def test_nested_lambda_never_uses_future_dates_or_holdout_values():
    races, arrays = synthetic(120, per_day=15)
    first = d.joint_analysis(races, arrays, bootstrap_reps=5, grid=(.01, .1, 1.))
    train, test = d.strict_split(races)
    changed = {k: v.copy() for k, v in arrays.items()}
    for r in test:
        changed[r.race_id] *= -1000
    second = d.joint_analysis(races, changed, bootstrap_reps=5, grid=(.01, .1, 1.))
    assert first["tuning"] == second["tuning"]
    assert first["coefficients"] == second["coefficients"]
    for outer in first["walk_forward"]["daily"]:
        if "tuning" not in outer:
            continue
        assert all(day < outer["date"] for day in outer["tuning"]["selection_training_dates"])
        for inner in outer["tuning"]["inner_folds"]:
            assert all(day < inner["validation_date"] < outer["date"] for day in inner["training_dates"])
    assert all(day <= train[-1].race_date for day in first["tuning"]["selection_training_dates"])


def test_missing_default_and_unvalidated_are_distinct_not_imputed():
    assert d.trace_audit(None, {})["missing"]
    assert d.trace_audit(float("nan"), {})["missing"]
    neutral = d.trace_audit(50., {"rule_id": "OBSERVED_RULE", "fallback": False})
    assert neutral["exact_50"] and not neutral["fallback_or_DCR_rule"]
    fallback = d.trace_audit(58., {"rule_id": "KM-DCR-ART3-v1", "source_fact": "UNVALIDATED"})
    assert not fallback["exact_50"] and fallback["fallback_or_DCR_rule"] and fallback["UNVALIDATED"]
    observed = d.trace_audit(72., {"rule_id": "OBSERVED_RULE", "source_fact": "UNVALIDATED"})
    assert observed["UNVALIDATED"] and not observed["default_or_fallback_union"]
    np.testing.assert_array_equal(d.standardize(np.full((8, 13), 50.)), np.zeros((8, 13)))


def stored_cohort(root, *, n=24):
    rng = np.random.default_rng(211)
    for i in range(n):
        day = date(2026, 10, 11) + timedelta(days=i // 6)
        rid = f"KM-JRA-TKY-{day:%Y%m%d}-R{i % 6 + 1:02d}"
        post = datetime.fromisoformat(day.isoformat() + "T10:00:00+09:00") + timedelta(minutes=30 * (i % 6))
        base = rng.normal(65, 7, size=(6, 13))
        if i == 0:
            base[0, 0] = 50
        runners = {}
        for j in range(6):
            values = dict(zip(d.INDICES, map(float, base[j])))
            runners[str(j + 1)] = {"zai_win": sum(values[k] * w for k, w in d.SUPPLIED_WEIGHTS.items()),
                "base_final_values": values,
                "base_index_trace": {k: {"rule_id": "OBSERVED_RULE", "value": v,
                    "source_fact": "fixture UNVALIDATED" if k == "CFI" else "fixture observation"} for k, v in values.items()}}
        odds = [{"runner_id": str(j + 1), "horse_no": j + 1, "win_odds": float(2 + 1.7 * j)} for j in range(6)]
        winner = int(rng.integers(1, 7)); order = [winner] + [j for j in range(1, 7) if j != winner]
        objects = {
            f"runtime/final_artifacts/{rid}.json": {"race_id": rid, "family_id": "JRA", "scheduled_post_at": post.isoformat(),
                "final_receipt": {"receipt": {"timestamp": (post - timedelta(minutes=5)).isoformat()}},
                "final_prediction_package": {"index_provenance_replay": {"runners": runners}}},
            f"runtime/executions/{rid}-LIVE-R1/SOURCE/runs/1/source_attempt_envelope.json": {"artifact": {"race_id": rid,
                "jra_official_market_observation": {"official": True, "captured_at": (post - timedelta(minutes=20)).isoformat(), "runners": odds}}},
            f"runtime/results/{rid}.json": {"race_id": rid, "official_result": {"top3": order[:3], "finish_order": order}},
        }
        for name, value in objects.items():
            p = root / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(value))


def test_index_cell_audit_and_missing_race_exclusion(tmp_path):
    stored_cohort(tmp_path, n=6)
    inputs = b.Inputs(tmp_path); series, rows, _ = inputs.load(date(2026, 10, 11), date(2026, 10, 14), date(2026, 11, 3))
    p = next((tmp_path / "runtime/final_artifacts").glob('*.json'))
    f = json.loads(p.read_text()); f['final_prediction_package']['index_provenance_replay']['runners']['2']['base_final_values']['TRI'] = None
    p.write_text(json.dumps(f))
    arrays, audit, ledger = d.load_indices(tmp_path, series['pre_signature'], rows, inputs)
    assert audit['HPI']['counts']['exact_50'] == 1
    assert audit['CFI']['counts']['UNVALIDATED'] == 36
    assert audit['CFI']['counts']['default_or_fallback_union'] == 0
    assert audit['TRI']['counts']['missing'] == 1
    assert sum(not np.isfinite(x).all() for x in arrays.values()) == 1
    assert any(r['TRI'] is None and 'missing' in r['TRI_audit_flags'] for r in ledger)


def test_determinism_phase0_byte_compatibility_original_hashes_and_output_guard(tmp_path, monkeypatch):
    root = tmp_path / 'inputs'; stored_cohort(root)
    old = root / 'runtime/reports/benter_second_stage/2026-11-03/summary.md'
    old.parent.mkdir(parents=True); old.write_text('past asof must remain unchanged')
    originals = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
    def forbidden(*args, **kwargs): raise AssertionError('OFFLINE_ONLY')
    monkeypatch.setattr(socket.socket, 'connect', forbidden)
    for name in ['one', 'two']:
        d.run(root, date(2026, 10, 11), date(2026, 10, 14), date(2026, 11, 3), tmp_path / name, bootstrap_reps=4, shuffle_reps=4)
    for name in ['index_diagnostics.json', 'index_diagnostics.md', 'index_ledger.csv', 'summary.json', 'summary.md', 'ledger.csv']:
        assert (tmp_path/'one'/name).read_bytes() == (tmp_path/'two'/name).read_bytes()
    b.run(root, date(2026, 10, 11), date(2026, 10, 14), date(2026, 11, 3), tmp_path/'phase0', bootstrap_reps=4, shuffle_reps=4)
    assert (tmp_path/'one/summary.json').read_bytes() == (tmp_path/'phase0/summary.json').read_bytes()
    assert originals == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in originals}
    assert d.REFERENCE_RESOLUTION in (tmp_path/'one/summary.md').read_text()
    with pytest.raises(FileExistsError, match='NEW_DIRECTORY'):
        d.run(root, date(2026, 10, 11), date(2026, 10, 14), date(2026, 11, 3), tmp_path/'one')
    with pytest.raises(ValueError, match='PRODUCTION_TREE'):
        d.run(root, date(2026, 10, 11), date(2026, 10, 14), date(2026, 11, 3), root/'runtime/results/new')


def test_odds_bands_and_final_odds_paired_secondary():
    races, _ = synthetic(120)
    rows = [{'series':'pre_signature','race_id':r.race_id,'minutes_to_post':5 if i<40 else 20 if i<80 else 45,'excluded_reason':None} for i,r in enumerate(races)]
    primary = b.analyze(races, bootstrap_reps=3, shuffle_reps=3)
    secondary = [b.replace(r, m=np.sqrt(r.m)/np.sqrt(r.m).sum()) for r in races]
    timing = d.odds_sensitivity(races, secondary, rows, primary)
    assert timing['minutes_to_post'] == {'minimum':5,'median':20.,'maximum':45}
    assert [x['n_races'] for x in timing['bands']] == [40,40,40,0]
    assert timing['secondary_final_odds']['paired_races'] == 120
    assert 'holdout_M_rho2_difference' in timing['secondary_final_odds']
    assert d.odds_sensitivity(races, [], rows, primary)['secondary_final_odds']['status'] == 'FINAL_ODDS_NOT_AVAILABLE'


def test_production_import_isolation():
    tree = __import__('ast').parse((ROOT/'runtime/analysis/benter_index_diagnostics.py').read_text())
    for node in __import__('ast').walk(tree):
        if isinstance(node, __import__('ast').ImportFrom):
            assert not (node.module or '').startswith('jra_')
        if isinstance(node, __import__('ast').Import):
            assert not any(n.name.startswith('jra_') for n in node.names)
