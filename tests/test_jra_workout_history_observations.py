"""Dated workout Raw retention; no numerical rule or feed-admission change."""
from copy import deepcopy
import base64
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch

import pytest

ROOT = Path(os.environ.get("KM_TEST_REPO_ROOT", Path(__file__).resolve().parents[1]))
sys.path[:0] = [str(ROOT / "runtime"), str(ROOT / "runtime/jra_source_runtime")]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


candidate = load("workout_history_under_test", Path(os.environ.get(
    "KM_HISTORY_CANDIDATE_MODULE", ROOT / "runtime/jra_source_runtime/jra_registered_common.py")))
REQUEST = Path(os.environ.get("KM_HISTORY_ORIGINAL_REQUEST", ROOT / "runtime/requests/KM-JRA-TKY-20261031-R06-LIVE-R1-FORMAL.json"))


def source_and_snapshots():
    q = json.loads(REQUEST.read_text())
    source = q["source_snapshot"]
    snaps = [s for s in source["sources"] if s["source_id"].startswith("NETKEIBA-WORKOUT-")]
    assert len(snaps) == 4
    decoded = {}
    for snapshot in snaps:
        raw = gzip.decompress(base64.b64decode(snapshot["raw_gzip_b64"], validate=True))
        assert hashlib.sha256(raw).hexdigest() == snapshot["raw_sha256"]
        decoded[snapshot["source_id"]] = (raw, snapshot)
    return q, source, decoded


def test_actual_18_dated_rows_keep_official_identity_and_three_repeated_rows_are_deduplicated():
    before_digest = hashlib.sha256(REQUEST.read_bytes()).hexdigest()
    q, source, snaps = source_and_snapshots()
    retained = {}
    for sid, (raw, snapshot) in snaps.items():
        now = candidate.parse_workout(raw, snapshot["content_type"], source["jra_official_runner_universe"])
        candidate._retain_workout_observations(retained, now, snapshot)
    history = retained["observed_workout_history"]
    rows = history["records"]
    assert history["record_count"] == 18
    assert {rid: sum(r["runner_id"] == rid for r in rows) for rid in ("1", "2", "3")} == {"1": 7, "2": 9, "3": 2}
    assert {(r["runner_id"], r["horse_name"]) for r in rows} == {
        ("1", "ソニックキャット"), ("2", "ジオストラテジー"), ("3", "オルブライト")}
    assert sum(len(r["source_refs"]) - 1 for r in rows) == 3
    assert sum(r["workout_date"] == "2026-10-28" for r in rows) == 3
    assert all(r["workout_date"] < "2026-10-31" for r in rows)
    assert history["production_feature_admission"] is False
    assert all(set(r).isdisjoint({"category", "index_value", "rule_id", "score"}) for r in rows)
    assert hashlib.sha256(REQUEST.read_bytes()).hexdigest() == before_digest


def test_latest_rows_and_numerical_feed_reconciliation_are_unchanged():
    q, source, snaps = source_and_snapshots()
    # Golden normalized payload digests from exact PR350 blob
    # 58566d3a3f885b6338d36a147cdd8c1d9c56b613, over the verified retained Raw.
    expected = {"NETKEIBA-WORKOUT-0": "bb8facdfad1afbd2b0c854ecb6b7bf5ea56f6b6953df0d3fd44ed9510fbeddca",
                "NETKEIBA-WORKOUT-1": "bb8facdfad1afbd2b0c854ecb6b7bf5ea56f6b6953df0d3fd44ed9510fbeddca",
                "NETKEIBA-WORKOUT-2": "0ed38895e4ba6685ec267c5221b48f7c834c9e9485266ac552a4c8b7f91e761b",
                "NETKEIBA-WORKOUT-3": "0ed38895e4ba6685ec267c5221b48f7c834c9e9485266ac552a4c8b7f91e761b"}
    for sid, (raw, snapshot) in snaps.items():
        new = candidate.parse_workout(raw, snapshot["content_type"], source["jra_official_runner_universe"])
        new.pop("observed_workout_history", None)
        assert candidate.sha_obj(new) == expected[sid]
        reconciled = candidate._reconcile(new, source)
        assert reconciled["verified"] is False
        assert reconciled["official_count"] == 15
        assert reconciled["source_count"] == (16 if sid.endswith(("-0", "-1")) else 3)


def test_existing_acquisition_attempts_retain_partial_history_but_cannot_admit_three_of_fifteen():
    q, source, snaps = source_and_snapshots()
    def acquire(module):
        def fetch(url, cutoff, source_id, source_class):
            if source_id not in snaps:
                raise ValueError("OFFLINE_SPEED_UNAVAILABLE")
            raw, snapshot = snaps[source_id]
            return raw, {"content-type": snapshot["content_type"]}, deepcopy(snapshot)
        artifact = {"source_race_context": deepcopy(source["source_race_context"]),
                    "jra_official_runner_universe": deepcopy(source["jra_official_runner_universe"])}
        with patch.object(module, "_discover_race_id", return_value=("202605041006", None)), patch.object(module, "_fetch", side_effect=fetch) as fetched:
            result, errors = module.enrich_with_registered_common(artifact, q["prediction_cutoff"], require_workout=True)
        assert fetched.call_count == 5  # existing four workout URLs plus speed
        return result["jra_registered_common"], errors
    new, new_errors = acquire(candidate)
    history = new.pop("observed_workout_history")
    new.pop("sha256")
    # The same legacy blob's complete acquisition output is unchanged after
    # removing only the new observation field and its enclosing digest.
    assert candidate.sha_obj(new) == "5bf28811bedc13ef24ec3999aa55ce877a43c5d4d1a75b59eb5382115f8182e3"
    assert len(new_errors) == 1 and new_errors[0].startswith("NETKEIBA_WORKOUT_NO_COMPLETE_UNIVERSE:")
    assert new["workout"] is None
    assert new["workout_selection"]["attempt_count"] == 4
    assert history["record_count"] == 18
    assert history["production_feature_admission"] is False


def synthetic(number_rowspan=2, horse_name="試験馬"):
    return f'''<table><tr><th>馬番</th><th>馬名</th><th>日付</th><th>コース</th><th>馬場</th><th>乗り役</th><th>調教タイム</th><th>位置</th><th>脚色</th><th colspan="2">評価</th></tr>
    <tr><td rowspan="{number_rowspan}">1</td><td rowspan="2">{horse_name}</td><td>2026/10/28(水)</td><td>美坂</td><td>良</td><td>助手</td><td>53.8(14.6)12.5(12.5) 内相手馬と併入</td><td>2</td><td>仕掛</td><td>順調</td><td>B</td></tr>
    <tr><td>2026/10/25(日)</td><td>美Ｗ</td><td>稍</td><td>助手</td><td>56.1(15.0)12.9(12.9)</td><td>6</td><td>馬也</td><td>順調</td><td>C</td></tr></table>'''.encode()


def test_rowspan_child_row_cannot_drift_to_another_horse():
    universe = {"runners": [{"runner_id": "1", "name": "試験馬"}]}
    observations = candidate.parse_workout_history(synthetic(), "text/html; charset=utf-8", universe)
    assert len(observations["records"]) == 2
    assert all(row["runner_id"] == "1" and row["horse_name"] == "試験馬" for row in observations["records"])
    assert observations["official_identity_verified"] is True


def test_pr350_declared_cancellation_repair_and_first_complete_selection_are_preserved():
    q, source, snaps = source_and_snapshots()
    def fetch(url, cutoff, source_id, source_class):
        if source_id not in snaps:
            raise ValueError("OFFLINE_SPEED_UNAVAILABLE")
        raw, snapshot = snaps[source_id]
        return raw, {"content-type": snapshot["content_type"]}, deepcopy(snapshot)
    artifact = {key: deepcopy(source[key]) for key in ("source_race_context", "jra_race_context",
                "jra_declared_runner_universe", "jra_official_runner_universe")}
    with patch.object(candidate, "_discover_race_id", return_value=("202605041006", None)), patch.object(candidate, "_fetch", side_effect=fetch) as fetched:
        result, errors = candidate.enrich_with_registered_common(artifact, q["prediction_cutoff"], require_workout=True)
    base = result["jra_registered_common"]
    base.pop("sha256")
    assert candidate.sha_obj(base) == "f8bc7095465f5b52ce1384976c599a2a95eebe54aa5c68d89c52e9fa54ddac11"
    assert errors == []
    assert base["workout"]["runner_count"] == 15
    assert base["workout_selection"]["attempt_count"] == 1
    assert fetched.call_count == 2  # same single complete workout page plus speed
    assert "observed_workout_history" not in base


@pytest.mark.parametrize("case", ["wrong_name", "broken_rowspan", "bad_date"])
def test_history_rejects_ambiguous_identity_or_date_without_synthesizing_rows(case):
    universe = {"runners": [{"runner_id": "1", "name": "試験馬"}]}
    raw = synthetic(horse_name="別馬") if case == "wrong_name" else synthetic(number_rowspan=1) if case == "broken_rowspan" else synthetic().replace(b"2026/10/25", b"2026/99/25")
    with pytest.raises(ValueError):
        candidate.parse_workout_history(raw, "text/html; charset=utf-8", universe)


def test_speed_parser_retains_original_rowspan_safety_bound():
    reader = candidate._SpeedTables()
    with pytest.raises(ValueError, match="SPEED_HEADER_INVALID_SPAN"):
        reader.feed('<table><tr><td rowspan="9">x</td></tr></table>')
