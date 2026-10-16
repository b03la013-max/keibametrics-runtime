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
