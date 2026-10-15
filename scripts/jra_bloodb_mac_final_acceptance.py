"""Run the existing Blood-B signed-queue -> private DOM probe -> live acceptance.

Operator-owned Mac only. Paid pages are accessed solely after explicit provider
permission assertion. No paid rows, account material or authentication state
leave the Mac; this script never grants Production BVI/Prediction authority.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import json
import platform
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

from jra_bloodb_mac_collector import (
    BloodBError, HOME, PRIVATE, PROFILE, private_dir, playwright_sync, utc_time,
)
from jra_bloodb_mac_automation import load_official, run_one
from jra_bloodb_mac_acceptance import verify_capture
from jra_bloodb_mac_probe import probe_context
from jra_bloodb_signed_source_queue_sync import synchronize

SOURCE_LEVEL = "SOURCE_ED25519_ONLY_NOT_INDEPENDENT_OIDC_ATTESTED_HERE"


def select_race(queue_path: Path, *, now: datetime, race_id: str | None = None,
                window_minutes: int = 65, source_loader=load_official) -> dict:
    """Select only a verified, future, SOURCE-bound Race from the private queue."""
    if now.tzinfo is None:
        raise BloodBError("BLOODB_FINAL_TIMEZONE_REQUIRED")
    if not 1 <= window_minutes <= 180:
        raise BloodBError("BLOODB_FINAL_WINDOW_INVALID")
    if race_id is not None and not re.fullmatch(r"[A-Za-z0-9_.-]{4,120}", race_id):
        raise BloodBError("BLOODB_FINAL_RACE_ID_INVALID")
    if queue_path.is_symlink() or not queue_path.is_file() or queue_path.stat().st_mode & 0o077:
        raise BloodBError("BLOODB_FINAL_PRIVATE_QUEUE_REQUIRED")
    rows = json.loads(queue_path.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or len(rows) > 80:
        raise BloodBError("BLOODB_FINAL_QUEUE_INVALID")
    seen = set()
    eligible = []
    for spec in rows:
        if not isinstance(spec, dict):
            raise BloodBError("BLOODB_FINAL_QUEUE_ROW_INVALID")
        rid = str(spec.get("race_id") or "")
        if not re.fullmatch(r"[A-Za-z0-9_.-]{4,120}", rid) or rid in seen:
            raise BloodBError("BLOODB_FINAL_QUEUE_ID_DUPLICATED_OR_UNSAFE")
        seen.add(rid)
        if race_id is not None and rid != race_id:
            continue
        if spec.get("production_authority") is not False:
            raise BloodBError("BLOODB_FINAL_NON_DIAGNOSTIC_QUEUE_FORBIDDEN")
        cutoff = utc_time(spec.get("prediction_cutoff"))
        if not now < cutoff <= now + timedelta(minutes=window_minutes):
            if race_id == rid:
                raise BloodBError("BLOODB_FINAL_OUTSIDE_FUTURE_WINDOW")
            continue
        if not spec.get("signed_source_envelope_path") or not spec.get("jra_signed_source_artifact_sha256"):
            raise BloodBError("BLOODB_FINAL_SIGNED_SOURCE_REQUIRED")
        runners, provenance = source_loader(spec)
        if (provenance.get("level") != SOURCE_LEVEL
                or provenance.get("source_artifact_sha256") != spec["jra_signed_source_artifact_sha256"]
                or len(runners) < 2):
            raise BloodBError("BLOODB_FINAL_SOURCE_IDENTITY_NOT_VERIFIED")
        eligible.append((cutoff, spec))
    if race_id is not None and race_id not in seen:
        raise BloodBError("BLOODB_FINAL_REQUESTED_RACE_NOT_IN_QUEUE")
    if not eligible:
        raise BloodBError("BLOODB_FINAL_NO_VERIFIED_FUTURE_RACE_IN_WINDOW")
    eligible.sort(key=lambda item: (item[0], item[1]["race_id"]))
    return eligible[0][1]


def accept_one(context, spec: dict, *, private_root: Path = PRIVATE,
               probe=probe_context, capture=run_one, verify=verify_capture) -> dict:
    """Probe must PASS before capture; re-verify locally after capture."""
    race_id = spec["race_id"]
    dest = private_root.expanduser() / race_id
    if dest.is_symlink():
        raise BloodBError("BLOODB_FINAL_CAPTURE_SYMLINK_FORBIDDEN")
    if dest.exists():
        receipt = verify(spec, private_root=private_root)
        stage = "ALREADY_CAPTURED_REVERIFIED"
    else:
        precheck = probe(context, spec)
        if precheck.get("status") != "LOCAL_MEMBER_DOM_SCHEMA_COMPATIBLE":
            reason = str(precheck.get("block_reason") or "UNSUPPORTED_MEMBER_DOM")
            safe = reason.split(":")[0]
            if not re.fullmatch(r"[A-Z0-9_]{3,90}", safe):
                safe = "UNSUPPORTED_MEMBER_DOM"
            raise BloodBError("BLOODB_FINAL_PROBE_BLOCKED_" + safe)
        capture(context, spec, private_root=private_root)
        receipt = verify(spec, private_root=private_root)
        stage = "PROBE_CAPTURE_REVERIFIED"
    if (receipt.get("status") != "LOCAL_CAPTURE_ARTIFACT_INTEGRITY_VERIFIED"
            or receipt.get("production_bvi_authority") is not False
            or receipt.get("matched_runner_count") != receipt.get("official_runner_count")):
        raise BloodBError("BLOODB_FINAL_ACCEPTANCE_INTEGRITY_INVALID")
    return {
        "status": "MAC_LOCAL_BLOODB_ACCEPTANCE_VERIFIED",
        "stage": stage,
        "race_id": race_id,
        "matched_runner_count": receipt["matched_runner_count"],
        "jra_ed25519_envelope_reverified": receipt["jra_ed25519_envelope_reverified"],
        "provider_permission": "OPERATOR_ASSERTION_NOT_PROVIDER_ATTESTATION",
        "provider_signed": False,
        "production_authority": False,
        "production_bvi_authority": False,
        "oos_increment": 0,
        "paid_data_exported": False,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("offline", "live"))
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--queue", type=Path, default=HOME / "bloodb_queue.json")
    parser.add_argument("--profile", type=Path, default=PROFILE)
    parser.add_argument("--private-dir", type=Path, default=PRIVATE)
    parser.add_argument("--race-id")
    parser.add_argument("--window-minutes", type=int, default=65)
    parser.add_argument("--provider-permission-confirmed", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.mode == "live":
            if platform.system() != "Darwin":
                raise BloodBError("BLOODB_FINAL_MACOS_REQUIRED")
            if not args.provider_permission_confirmed:
                raise BloodBError("BLOODB_FINAL_PROVIDER_PERMISSION_REQUIRED")
            if not args.profile.expanduser().is_dir():
                raise BloodBError("BLOODB_FINAL_LOCAL_SUBSCRIBER_PROFILE_REQUIRED")
        report = synchronize(args.repo.expanduser().resolve(), args.queue.expanduser(),
                             dry_run=args.mode == "offline")
        if args.mode == "offline":
            print(json.dumps({
                "status": "OFFLINE_SIGNED_QUEUE_INSPECTED", "source": report,
                "subscriber_access_attempted": False, "production_authority": False,
            }, ensure_ascii=False, sort_keys=True))
            return 0
        queue = args.queue.expanduser()
        spec = select_race(queue, now=datetime.now(timezone.utc), race_id=args.race_id,
                           window_minutes=args.window_minutes)
        with playwright_sync()() as playwright:
            context = playwright.chromium.launch_persistent_context(
                str(private_dir(args.profile)), headless=True, accept_downloads=False)
            try:
                result = accept_one(context, spec, private_root=args.private_dir)
            finally:
                context.close()
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (BloodBError, OSError, ValueError, KeyError, TypeError) as exc:
        reason = str(exc).split(":")[0]
        if not re.fullmatch(r"[A-Z0-9_]{3,100}", reason):
            reason = "LOCAL_ACCEPTANCE_ERROR"
        print(json.dumps({
            "status": "BLOCKED", "reason": reason, "production_authority": False,
            "paid_data_exported": False,
        }, ensure_ascii=False, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
