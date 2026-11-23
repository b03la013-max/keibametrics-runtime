"""Verify the research Runner, or process one scheduled KAW dispatch tick."""

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from runtime.family_authority_guard import resolve_current_authority
from runtime.local_private_checkpoint import (
    BINDING_ENV,
    BINDING_SHA_ENV,
    ROOT,
    PrivateCheckpoint,
    code_sha256,
    private_directory,
    private_file,
)
from runtime.local_race_key_intake import JST

MOUNT_ROOT = Path("/data/km-local-kaw")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dispatch-once", action="store_true",
                      help="Run one approved KAW race-day tick on this private service")
    mode.add_argument("--check-binding", action="store_true",
                      help="Validate the configured Binding without dispatching")
    args = parser.parse_args(argv)
    subprocess.run(
        [sys.executable, "-m", "runtime.local_race_entry", "--help"],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    authority_path, _ = resolve_current_authority()
    root = private_directory(MOUNT_ROOT)
    probe = private_file(root / "bootstrap_probe.json")
    probe_bytes = probe.read_bytes()
    record = json.loads(probe_bytes)
    nonce_sha = hashlib.sha256(record["nonce"].encode()).hexdigest()
    if nonce_sha != record["sha256"]:
        raise SystemExit("KAW_RESEARCH_PRIVATE_READBACK_MISMATCH")

    print(json.dumps({
        "status": "KAW_RUNNER_STARTUP_PASS",
        "commit_sha": os.environ.get("RAILWAY_GIT_COMMIT_SHA"),
        "runtime_code_sha256": code_sha256(),
        "authority": authority_path.name,
        "probe_sha256": nonce_sha,
        "readback_sha256": hashlib.sha256(probe_bytes).hexdigest(),
    }, sort_keys=True))

    if args.dispatch_once and os.environ.get("KM_LOCAL_AUTONOMOUS_ENABLED") != "true":
        print("KAW_RUNNER_DISPATCH_NOT_ACTIVATED")
        return 2
    configured = bool(os.environ.get(BINDING_ENV) and os.environ.get(BINDING_SHA_ENV))
    if not (args.dispatch_once or args.check_binding):
        print("KAW_RUNNER_BINDING_NOT_CHECKED" if configured else "KAW_RUNNER_WAITING_FOR_BINDING")
        return 0
    if not configured:
        print("KAW_RUNNER_WAITING_FOR_BINDING")
        return 2
    private = PrivateCheckpoint.from_env()
    if not private.root.is_relative_to(root):
        print("KAW_RUNNER_DISPATCH_BINDING_OUTSIDE_MOUNT" if args.dispatch_once
              else "KAW_RUNNER_CHECK_BINDING_OUTSIDE_MOUNT")
        return 2
    print("KAW_RUNNER_BINDING_VALIDATED")
    if args.dispatch_once:
        from runtime.local_race_day_dispatcher import private_kaw_day

        now = datetime.now(JST)
        report = private_kaw_day(ROOT, now.date().isoformat(), 120, now=now, execute=True, private=private)
        print(json.dumps({k: report[k] for k in ("status", "race_date", "first_stop_stage", "dispatch_count")}))
        return 0 if report["status"] == "PRIVATE_NANKAN_DAY_DISPATCH_OBSERVED" else 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
