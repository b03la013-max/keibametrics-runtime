"""Existing R51 actual-course requirement; no new bands or feed admission."""
from copy import deepcopy
import importlib.util
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(os.environ.get("KM_TEST_REPO_ROOT", Path(__file__).resolve().parents[1]))
sys.path[:0] = [str(ROOT / "runtime"), str(ROOT / "runtime/jra_source_runtime")]
MODULE = Path(os.environ.get("KM_WORKOUT_FEATURE_MODULE", ROOT / "runtime/jra_source_to_evidence_features.py"))
spec = importlib.util.spec_from_file_location("workout_actual_course_under_test", MODULE)
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)


def source(course="美坂", final1f=12.5):
    return {
        "jra_official_runner_universe": {"runners": [
            {"runner_id": "1", "name": "ALPHA", "status": "ACTIVE"},
            {"runner_id": "2", "name": "BETA", "status": "ACTIVE"}]},
        "jra_registered_common": {"workout": {
            "source_snapshot_sha256": "a" * 64,
            "runners": [
                {"runner_id": "1", "horse_name": "ALPHA", "assessment": "順調", "course": course, "final1f": final1f},
                {"runner_id": "2", "horse_name": "BETA", "assessment": "順調", "course": "美坂", "final1f": None}]}}
    }


@pytest.mark.parametrize("course", [None, "", "   ", "unknown", "UNKNOWN", " Unknown ",
                                    "不明", "不詳", "未取得", "未確認", "未公表", "未発表", "N/A", " n/a "])
def test_observed_clock_without_observed_course_cannot_create_workout_speed(course):
    artifact = source(course=course)
    before = deepcopy(artifact)
    features = candidate._registered_common_workout_features("1", artifact)
    assert "workout_speed" not in features
    assert features["workout_capability"]["category"] == "STRONG"
    assert artifact == before


def test_actual_saka_clock_uses_existing_production_band_without_new_rule():
    feature = candidate._registered_common_workout_features("1", source())["workout_speed"]
    assert feature["category"] == "STRONG"
    assert feature["rule_id"] == "JRA-WORKOUT-FINAL1F-BAND-v1"
    assert set(feature["evidence_refs"]) == {"a" * 64, "REGISTERED_JRA_COMMON:WORKOUT:1"}


@pytest.mark.parametrize("course", ["美Ｗ", "美Ｐ", "栗Ｐ", "函館芝", "追分ダート", "UNKNOWN FARM TRAINING", "UNKNOWN TRACK"])
def test_actual_other_course_keeps_existing_normalizer_default(course):
    feature = candidate._registered_common_workout_features("1", source(course=course, final1f=12.2))["workout_speed"]
    assert feature["category"] == "NEUTRAL"
    assert feature["rule_id"] == "JRA-WORKOUT-FINAL1F-BAND-v1"


@pytest.mark.parametrize("course,expected", [("CW", "POSITIVE"), ("栗ＣＷ", "POSITIVE"), ("美坂", "STRONG")])
def test_existing_known_course_bands_are_unchanged(course, expected):
    assert candidate._registered_common_workout_features("1", source(course=course, final1f=12.5))["workout_speed"]["category"] == expected


def test_clock_missing_stays_missing():
    features = candidate._registered_common_workout_features("1", source(final1f=None))
    assert "workout_speed" not in features


def test_partial_feed_is_still_rejected_even_with_actual_clock_and_course():
    artifact = source()
    artifact["jra_registered_common"]["workout"]["runners"].pop()
    assert candidate._registered_common_workout_features("1", artifact) == {}


@pytest.mark.parametrize("course", ["unknown", "UNKNOWN", "不明"])
def test_existing_raw_parser_preserves_sentinel_text_instead_of_normalizing_to_none(course):
    from jra_source_runtime.jra_registered_common import parse_workout
    raw = ("<table><tr><th>馬番</th><th>馬名</th><th>コース</th><th>調教タイム</th><th>短評</th><th>評価</th></tr>"
           f"<tr><td>1</td><td>ALPHA</td><td>{course}</td><td>12.5</td><td>順調</td><td>B</td></tr>"
           "<tr><td>2</td><td>BETA</td><td>美坂</td><td>12.5</td><td>順調</td><td>B</td></tr></table>").encode()
    parsed = parse_workout(raw, "text/html; charset=utf-8")
    assert parsed["runners"][0]["course"] == course
    assert parsed["runners"][0]["final1f"] == 12.5


@pytest.mark.parametrize("order", ["source_first", "krs_first"])
def test_fresh_process_import_orders_have_no_cycle_or_external_side_effects(order, tmp_path):
    script = r'''
import importlib.util, socket, subprocess, sys, urllib.request
sys.dont_write_bytecode = True
def forbidden(*args, **kwargs):
    raise AssertionError("IMPORT_EXTERNAL_SIDE_EFFECT_FORBIDDEN")
socket.create_connection = forbidden
socket.getaddrinfo = forbidden
socket.socket.connect = forbidden
socket.socket.connect_ex = forbidden
urllib.request.urlopen = forbidden
subprocess.Popen = forbidden
module_path, runtime_path, order = sys.argv[1:]
sys.path[:0] = [runtime_path, runtime_path + "/jra_source_runtime"]
if order == "krs_first":
    import jra_krs_input_builder_production
spec = importlib.util.spec_from_file_location("jra_source_to_evidence_features", module_path)
source = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = source
spec.loader.exec_module(source)
import jra_krs_input_builder_production as krs
assert source._missing_jra_value is krs._missing
assert source._missing_jra_value(" UNKNOWN ")
print("IMPORT_ORDER_OK", order)
'''
    result = subprocess.run([sys.executable, "-c", script, str(MODULE), str(ROOT / "runtime"), order],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "IMPORT_ORDER_OK " + order
    assert list(tmp_path.iterdir()) == []
