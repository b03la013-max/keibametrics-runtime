"""Decide whether the single-entry wait may dispatch one bounded SOURCE retry.

Input: ``gh run list --json databaseId,displayTitle,status,conclusion`` in the
RUNS_JSON environment variable.  Output on stdout: RETRY or WAIT.

RETRY only when at least one SOURCE run for exactly this request path was
observed, every such run has completed, and the newest one concluded
unsuccessfully.  An in-progress, queued, successful or unobservable run
always yields WAIT, so a retry can never overlap a live SOURCE attempt.  The
caller enforces the one-retry budget and the deadline margin.
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
    if any(r.get("conclusion") == "success" for r in matches):
        return "WAIT"
    return "RETRY" if matches[-1].get("conclusion") in FAILED else "WAIT"


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
