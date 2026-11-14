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


def test_retry_budget_is_durable_across_workers_and_restarts():
    # A second visible run means the single retry was already dispatched by
    # some worker; a restarted or parallel waiter must never send a third.
    assert d.decide([run(10), run(12, conclusion="timed_out")], PATH) == "WAIT"
    assert d.decide([run(10), run(12)], PATH) == "WAIT"
    assert d.decide([run(10, conclusion="timed_out")], PATH) == "RETRY"


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


def _repo(tmp_path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
    seed = tmp_path / "seed"
    subprocess.run(["git", "clone", "-q", str(remote), str(seed)], check=True)
    (seed / "README").write_text("x\n")
    subprocess.run(["git", "-C", str(seed), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(seed), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init"], check=True)
    subprocess.run(["git", "-C", str(seed), "push", "-q", "origin", "HEAD:main"], check=True)
    clones = []
    for name in ("w1", "w2"):
        c = tmp_path / name
        subprocess.run(["git", "clone", "-q", str(remote), str(c)], check=True)
        clones.append(c)
    return remote, clones


def test_claim_is_create_if_absent_across_workers(tmp_path):
    remote, (w1, w2) = _repo(tmp_path)
    head_before = subprocess.run(["git", "-C", str(w1), "rev-parse", "HEAD"], capture_output=True, text=True).stdout
    assert d.claim_retry("KM-JRA-FKS-20261114-R11-LIVE-R1", PATH, "111", cwd=w1) == "CLAIMED"
    # Second worker (stale clone, restarted job, or parallel waiter) cannot claim again.
    assert d.claim_retry("KM-JRA-FKS-20261114-R11-LIVE-R1", PATH, "222", cwd=w2) == "LOST"
    assert d.claim_retry("KM-JRA-FKS-20261114-R11-LIVE-R1", PATH, "111", cwd=w1) == "LOST"
    # Caller working tree and HEAD untouched; claim is on the remote branch.
    assert subprocess.run(["git", "-C", str(w1), "rev-parse", "HEAD"], capture_output=True, text=True).stdout == head_before
    shown = subprocess.run(["git", "--git-dir", str(remote), "show",
                            "main:runtime/jra_source_retry_claims/KM-JRA-FKS-20261114-R11-LIVE-R1.json"],
                           capture_output=True, text=True, check=True).stdout
    assert json.loads(shown)["claimed_by_run_id"] == "111"
    # A different race keeps its own budget.
    assert d.claim_retry("KM-JRA-KYO-20261114-R01-LIVE-R1", PATH, "222", cwd=w2) == "CLAIMED"


def test_concurrent_claims_have_exactly_one_winner(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    remote, clones = _repo(tmp_path)
    extra = []
    for i in range(4):
        c = tmp_path / f"p{i}"
        subprocess.run(["git", "clone", "-q", str(remote), str(c)], check=True)
        extra.append(c)
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda c: d.claim_retry("KM-JRA-TKY-20261114-R05-LIVE-R1", PATH, str(c), cwd=c),
                                clones + extra))
    assert results.count("CLAIMED") == 1 and results.count("LOST") == 5


def test_claim_fails_closed_without_remote(tmp_path):
    assert d.claim_retry("KM-JRA-X-LIVE-R1", PATH, "1", cwd=tmp_path) == "LOST"
    assert d.claim_retry("", PATH, "1", cwd=tmp_path) == "LOST"


def test_workflow_dispatches_retry_only_after_claim():
    wf = (ROOT / ".github/workflows/km-jra-formal-single-entry.yml").read_text()
    start = wf.index("      - name: Wait for canonical Signed SOURCE\n")
    step = wf[start:wf.index("      - name: Verify and bind Static to durable Signed SOURCE\n", start)]
    claim = step.index("--claim-execution-id")
    sends = [i for i in range(len(step)) if step.startswith("gh workflow run km-jra-source-first-runner.yml", i)]
    assert len(sends) == 2  # original redispatch + claimed retry
    assert sends[1] > claim and 'if [ "$CLAIM" = "CLAIMED" ]' in step[claim:sends[1]]
    assert "|| echo LOST" in step
