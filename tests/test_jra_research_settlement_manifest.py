"""Failure injection for the existing postresult workflow's mandatory gate."""
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
import jra_research_settlement_manifest as m


def child(profile, rows, code=0, **extra):
    body = {"profile": profile, "processed": rows, **extra}
    return [sys.executable, "-c", "import json;print(json.dumps(" + repr(body) + "));raise SystemExit(" + str(code) + ")"]


def run_successful_static_and_env(tmp_path, directory):
    m.run_stage("static_owner", child(m.STAGE_PROFILES["static_owner"], [
        {"race_id": "B", "status": "DIAGNOSTIC_SETTLED_NOT_OOS", "oos_eligible": False}]), directory=directory, root=tmp_path)
    m.run_stage("bvi_env", child(m.STAGE_PROFILES["bvi_env"], [], environment_candidate={
        "profile": "KM-JRA-BVI-ENV-FOUR-ARM-FORWARD-SHADOW-v1", "eligible_settled_races": 0, "cohorts": {}}),
        directory=directory, root=tmp_path)


@pytest.mark.parametrize("exitcode", [0, 1])
def test_internal_race_failure_is_partial_and_required_gate_fails_even_if_process_green(tmp_path, exitcode):
    directory = tmp_path / "stages"
    report = m.run_stage("source_candidate", child(m.STAGE_PROFILES["source_candidate"], [
        {"race_id": "A", "status": "BLOCKED", "reason": "JRA_RESULT_DAY_TOKEN_NOT_FOUND"}], exitcode),
        directory=directory, root=tmp_path)
    assert report["manifest"]["failure_count"] == 1
    # An independent race/stage continues after the injected failure.
    run_successful_static_and_env(tmp_path, directory)
    complete = m.collect(directory)
    assert complete["status"] == "PARTIAL"
    assert complete["success_count"] == 1 and complete["failure_count"] == 1 and complete["unresolved_count"] == 1
    assert complete["cohort_counts_pooled"] is False
    path = tmp_path / "manifest.json"; path.write_text(json.dumps(complete))
    result = subprocess.run([sys.executable, str(ROOT / "runtime/jra_research_settlement_manifest.py"),
                             "gate", "--manifest", str(path)], capture_output=True, text=True)
    assert result.returncode == 2


def test_retry_is_distinct_and_does_not_become_a_second_failure(tmp_path):
    directory = tmp_path / "stages"
    m.run_stage("source_candidate", child(m.STAGE_PROFILES["source_candidate"], [
        {"race_id": "A", "status": "PENDING", "retryable": True}], 2), directory=directory, root=tmp_path)
    run_successful_static_and_env(tmp_path, directory)
    out = m.collect(directory)
    assert out["retry_count"] == 1 and out["unresolved_count"] == 1 and out["failure_count"] == 0


def test_missing_stage_unstructured_child_and_failed_persistence_are_not_hidden(tmp_path):
    directory = tmp_path / "stages"
    m.run_stage("source_candidate", [sys.executable, "-c", "print('{}')"], directory=directory, root=tmp_path)
    out = m.collect(directory, required_outcomes={"persistence": "failure"})
    assert out["status"] == "BLOCKED"
    assert out["failure_count"] == 4 and out["unresolved_count"] == 4
    assert out["required_stages"]["source_candidate"]["status"] == "BLOCKED"
    assert out["required_stages"]["static_owner"]["status"] == "NOT_EXECUTED"


def test_missing_result_for_due_fixed_env_prediction_is_explicitly_pending(tmp_path):
    folder = tmp_path / "runtime/jra_static_owner_forward_oos/RACE"; folder.mkdir(parents=True)
    (folder / "pedigree_env_pre_result.json").write_text(json.dumps({"race_id": "RACE", "scheduled_post_at": "2026-01-01T00:00:00Z"}))
    report = m.run_stage("bvi_env", child(m.STAGE_PROFILES["bvi_env"], [], environment_candidate={
        "profile": "KM-JRA-BVI-ENV-FOUR-ARM-FORWARD-SHADOW-v1", "eligible_settled_races": 0, "cohorts": {}}),
        directory=tmp_path / "stages", root=tmp_path)
    assert report["manifest"]["status"] == "PENDING" and report["manifest"]["retry_count"] == 1


def test_workflow_preserves_cron_always_audits_and_has_mandatory_final_gate():
    workflow = yaml.load((ROOT / ".github/workflows/km-jra-candidate-auto-postresult-closedloop.yml").read_text(), Loader=yaml.BaseLoader)
    assert workflow["on"]["schedule"] == [{"cron": "0,30 1-12 * * *"}]
    steps = workflow["jobs"]["result-to-learning"]["steps"]
    audit = next(step for step in steps if step.get("id") == "research_audit")
    assert "always()" in audit["if"] and "--settlement-manifest" in audit["run"]
    assert "always()" in steps[-1]["if"] and steps[-1]["run"].endswith(" gate")
    assert "continue-on-error" not in steps[-1]
    assert any("upload-artifact" in step.get("uses", "") and "always()" in step.get("if", "") for step in steps)
