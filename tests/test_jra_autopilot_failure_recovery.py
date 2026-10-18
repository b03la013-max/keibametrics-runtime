"""The live-day GitHub worker must recover from a failed status publish.

These guards protect the operational failure path; they do not assert that
GitHub delivers workflow_run events without delay or authorize late FINALs.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/km-jra-autopilot-failure-recovery.yml").read_text(encoding="utf-8")
CANONICAL = (ROOT / ".github/workflows/km-jra-race-day-autopilot.yml").read_text(encoding="utf-8")


def test_abnormal_exit_is_an_immediate_recovery_signal():
    assert "workflow_run:" in WORKFLOW
    assert "KeibaMetrics JRA Race-Day Autopilot" in WORKFLOW
    assert "types: [completed]" in WORKFLOW
    assert "conclusion == 'failure'" in WORKFLOW
    assert "conclusion == 'timed_out'" in WORKFLOW
    assert "head_branch == 'main'" in WORKFLOW


def test_recovery_only_dispatches_canonical_bounded_worker():
    assert "gh workflow run km-jra-race-day-autopilot.yml" in WORKFLOW
    assert '-f mode=loop' in WORKFLOW
    assert "RECOVERY_LIMIT_REACHED" in WORKFLOW
    assert "RECENT_FAILURES >= 3" in WORKFLOW
    assert "HHMM >= 1730" in WORKFLOW
    assert "HHMM < 830" in WORKFLOW
    assert "final_artifacts/" not in WORKFLOW
    assert "jra_formal_intents/" not in WORKFLOW
    assert "cancel-in-progress: false" in WORKFLOW
    assert "Continue with fresh worker before hosted job limit" in CANONICAL
    assert "if: always()" in CANONICAL


def test_actual_dynamic_run_names_route_by_verified_workflow_path():
    import json
    import yaml
    events=json.loads((ROOT/"tests/fixtures/jra_completion_actual_runs_20261017.json").read_text())
    workflow=yaml.safe_load(WORKFLOW)
    jobs=workflow["jobs"]
    def permits(job,event):
        expression=jobs[job]["if"].strip().removeprefix("${{").removesuffix("}}").strip()
        for key in ("path","name","head_branch","conclusion"):
            expression=expression.replace("github.event.workflow_run."+key,repr(event.get(key)))
        expression=expression.replace("&&"," and ").replace("||"," or ").replace("\n"," ")
        return eval(expression,{"__builtins__":{}},{})
    resolver,autopilot=events
    assert resolver["name"]=="JRA intent 東京 2026-10-17 R8"
    assert autopilot["name"]=="JRA race-day autopilot 2026-10-17 loop"
    assert permits("reconcile-resolver",resolver)
    assert not permits("restart-worker",resolver)
    assert permits("restart-worker",autopilot)
    assert not permits("reconcile-resolver",autopilot)
    for event in events:
        other={**event,"head_branch":"untrusted"}
        assert not permits("restart-worker",other)
        assert not permits("reconcile-resolver",other)
