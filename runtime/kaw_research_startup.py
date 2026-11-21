"""Verify the KAW Runner and its existing private mount on research deployment."""

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
    PrivateCheckpoint,
    code_sha256,
    private_directory,
    private_file,
)


def main():
    subprocess.run(
        [sys.executable, "-m", "runtime.local_race_entry", "--help"],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    authority_path, _ = resolve_current_authority()
    root = private_directory(Path("/data/km-local-kaw"))
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

    if not (os.environ.get(BINDING_ENV) and os.environ.get(BINDING_SHA_ENV)):
        print("KAW_RUNNER_WAITING_FOR_BINDING")
        return
    PrivateCheckpoint.from_env()
    print("KAW_RUNNER_BINDING_VALIDATED")


if __name__ == "__main__":
    main()
