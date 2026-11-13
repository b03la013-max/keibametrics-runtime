import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/jra_source_runtime"))
import jra_source_retry_decision as d  # noqa: E402

PATH = "runtime/jra_source_requests/KM-JRA-FKS-20261114-R11-LIVE-R1.json"
TITLE = "JRA SOURCE " + PATH


def run(i, status="completed", conclusion="failure", title=TITLE):
    return {"databaseId": i, "displayTitle": title, "status": status, "conclusion": conclusion}


def test_single_completed_failure_retries():
    assert d.decide([run(10)], PATH) == "RETRY"


def test_newest_failure_after_older_failure_retries_caller_bounds_budget():
    assert d.decide([run(10), run(12, conclusion="timed_out")], PATH) == "RETRY"


def test_no_observed_run_waits():
    assert d.decide([], PATH) == "WAIT"
    assert d.decide([run(10, title="JRA SOURCE other.json")], PATH) == "WAIT"


def test_live_or_queued_run_never_overlaps():
    assert d.decide([run(10), run(11, status="in_progress", conclusion=None)], PATH) == "WAIT"
    assert d.decide([run(11, status="queued", conclusion=None)], PATH) == "WAIT"


def test_success_never_retries():
    assert d.decide([run(10), run(11, conclusion="success")], PATH) == "WAIT"
    assert d.decide([run(11, conclusion="success"), run(12)], PATH) == "WAIT"


def test_unobservable_input_waits():
    assert d.decide(None, PATH) == "WAIT"
    assert d.decide([{"displayTitle": TITLE, "status": "completed"}], PATH) == "WAIT"


def test_cli_reads_environment_and_defaults_to_wait():
    script = ROOT / "runtime/jra_source_runtime/jra_source_retry_decision.py"
    out = subprocess.run([sys.executable, str(script), "--request-path", PATH],
                         env={"RUNS_JSON": json.dumps([run(5)])}, capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "RETRY"
    out = subprocess.run([sys.executable, str(script), "--request-path", PATH],
                         env={"RUNS_JSON": "not json"}, capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "WAIT"


def test_workflow_retry_is_single_bounded_and_deadline_guarded():
    wf = (ROOT / ".github/workflows/km-jra-formal-single-entry.yml").read_text()
    start = wf.index("      - name: Wait for canonical Signed SOURCE\n")
    end = wf.index("      - name: Verify and bind Static to durable Signed SOURCE\n", start)
    step = wf[start:end]
    assert step.count("SOURCE_RETRY_USED=true") == 1
    assert 'SOURCE_RETRY_USED" = "false"' in step
    assert "SOURCE_RETRY_MIN_SECONDS=300" in step
    assert '$(( DEADLINE - NOW_S )) -ge "$SOURCE_RETRY_MIN_SECONDS"' in step
    assert '"$NOW_S" -lt "$CUTOFF"' in step
    assert 'jra_source_retry_decision.py' in step and '|| echo WAIT' in step
