"""Decide whether the single-entry wait may dispatch one bounded SOURCE retry.

Input: ``gh run list --json databaseId,displayTitle,status,conclusion`` in the
RUNS_JSON environment variable.  Output on stdout: RETRY or WAIT.

RETRY only when exactly ONE SOURCE run for exactly this request path is
visible on GitHub, it has completed, and it concluded unsuccessfully.  The
retry budget is therefore derived from durable provider state, not from a
worker-local flag: once a retry run exists (two visible runs), every later
worker, restarted job or parallel waiter for the same request sees WAIT.
An in-progress, queued, successful or unobservable run always yields WAIT,
so a retry can never overlap a live SOURCE attempt.  The caller enforces the
deadline margin; its local flag only avoids repeated API reads.
"""
import argparse
import json
import os
import sys

FAILED = {"failure", "cancelled", "timed_out", "startup_failure"}


def decide(runs, request_path):
    if not isinstance(runs, list) or not request_path:
        return "WAIT"
    title = "JRA SOURCE " + request_path
    matches = [r for r in runs if isinstance(r, dict) and r.get("displayTitle") == title]
    if not matches:
        return "WAIT"
    try:
        matches.sort(key=lambda r: int(r["databaseId"]))
    except (KeyError, TypeError, ValueError):
        return "WAIT"
    if any(r.get("status") != "completed" for r in matches):
        return "WAIT"
    if len(matches) != 1:
        return "WAIT"
    return "RETRY" if matches[0].get("conclusion") in FAILED else "WAIT"


CLAIM_DIR = "runtime/jra_source_retry_claims"


def _git(args, cwd, env=None, check=True, input_text=None):
    import subprocess
    return subprocess.run(["git", *args], cwd=cwd, env=env, check=check, text=True,
                          input=input_text, capture_output=True)


def claim_retry(execution_id, request_path, worker_run_id, *, cwd=".", remote="origin",
                branch="main", attempts=3):
    """Atomically create the single retry claim on the remote branch.

    Create-if-absent on the shared Git ref: the claim commit is built with a
    private index on top of the freshly fetched remote head (the working tree
    and the caller's HEAD are untouched) and pushed as a fast-forward.  A
    concurrent worker that pushed first makes our push non-fast-forward; we
    re-fetch, see its claim and return LOST.  Only CLAIMED authorizes one
    dispatch.  Any git error returns LOST (fail closed: no retry).
    """
    import re
    import tempfile
    safe = re.sub(r"[^A-Za-z0-9._-]", "-", str(execution_id))
    if not safe or not request_path:
        return "LOST"
    path = f"{CLAIM_DIR}/{safe}.json"
    body = json.dumps({"execution_id": execution_id, "request_path": request_path,
                       "retry_ordinal": 1, "claimed_by_run_id": str(worker_run_id),
                       "purpose": "SINGLE_BOUNDED_SOURCE_RETRY"}, sort_keys=True) + "\n"
    try:
        for _ in range(max(1, attempts)):
            _git(["fetch", "-q", remote, branch], cwd)
            base = _git(["rev-parse", "FETCH_HEAD"], cwd).stdout.strip()
            if _git(["cat-file", "-e", f"{base}:{path}"], cwd, check=False).returncode == 0:
                return "LOST"
            blob = _git(["hash-object", "-w", "--stdin"], cwd, input_text=body).stdout.strip()
            with tempfile.NamedTemporaryFile(prefix="km-retry-index-") as index:
                env = {**os.environ, "GIT_INDEX_FILE": index.name}
                _git(["read-tree", base], cwd, env=env)
                _git(["update-index", "--add", "--cacheinfo", f"100644,{blob},{path}"], cwd, env=env)
                tree = _git(["write-tree"], cwd, env=env).stdout.strip()
            commit = _git(["-c", "user.name=keibametrics-runtime",
                           "-c", "user.email=actions@users.noreply.github.com",
                           "commit-tree", tree, "-p", base, "-m",
                           f"execution: claim single SOURCE retry {safe} [skip ci]"], cwd).stdout.strip()
            if _git(["push", "-q", remote, f"{commit}:refs/heads/{branch}"], cwd, check=False).returncode == 0:
                return "CLAIMED"
        return "LOST"
    except Exception:
        return "LOST"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--request-path", required=True)
    parser.add_argument("--claim-execution-id")
    parser.add_argument("--worker-run-id", default="")
    args = parser.parse_args(argv)
    if args.claim_execution_id:
        print(claim_retry(args.claim_execution_id, args.request_path, args.worker_run_id))
        return 0
    try:
        runs = json.loads(os.environ.get("RUNS_JSON") or "null")
    except ValueError:
        runs = None
    print(decide(runs, args.request_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
