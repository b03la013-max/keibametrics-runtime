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


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--request-path", required=True)
    args = parser.parse_args(argv)
    try:
        runs = json.loads(os.environ.get("RUNS_JSON") or "null")
    except ValueError:
        runs = None
    print(decide(runs, args.request_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
