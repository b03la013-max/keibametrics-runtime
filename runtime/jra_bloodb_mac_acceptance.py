"""Verify a private Blood-B subscriber capture against its exact JRA signed SOURCE.

No paid content, cookies, horse-level labels or credentials leave the Mac.
This is *local diagnostic artifact integrity*, not provider attestation, OIDC
verification, Production BVI authority, or a real-page CI acceptance claim.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re

from jra_bloodb_mac_collector import (
    BloodBError, PRIVATE, PROFILE, HOME, FIELDS, allowed_page,
    namekey, official_universe, parse_rendered, private_dir, utc_time,
    playwright_sync,
)
from jra_bloodb_mac_automation import load_official, run_one

PROFILE_ID = "BLOODB-MAC-LOCAL-CAPTURE-ACCEPTANCE-v0.1"
REQUIRED = ("subscriber_page.html", "diagnostic.json", "summary.json",
            "jra_source_binding.json")


def _safe_json(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise BloodBError("BLOODB_ACCEPTANCE_JSON_INVALID")
    return obj


def _private_file(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise BloodBError("BLOODB_ACCEPTANCE_FILE_MISSING_OR_SYMLINK")
    if path.stat().st_mode & 0o077:
        raise BloodBError("BLOODB_ACCEPTANCE_PRIVATE_FILE_PERMISSIONS")


def queue_spec(queue_path: Path, race_id: str) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_.-]{4,120}", race_id):
        raise BloodBError("BLOODB_ACCEPTANCE_RACE_ID_UNSAFE")
    queue_path = queue_path.expanduser()
    _private_file(queue_path)
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    if not isinstance(queue, list) or len(queue) > 80:
        raise BloodBError("BLOODB_ACCEPTANCE_QUEUE_INVALID")
    matches = [x for x in queue if isinstance(x, dict) and x.get("race_id") == race_id]
    if len(matches) != 1:
        raise BloodBError("BLOODB_ACCEPTANCE_QUEUE_RACE_MISSING_OR_DUPLICATED")
    spec = matches[0]
    if not spec.get("signed_source_envelope_path") or spec.get("production_authority") is not False:
        raise BloodBError("BLOODB_ACCEPTANCE_SIGNED_QUEUE_REQUIRED")
    return spec


def verify_capture(spec: dict, *, private_root: Path = PRIVATE) -> dict:
    """Offline integrity audit; safe to run after the race without OOS credit.

    The record is not independently signed by Blood-B. The signed JRA SOURCE
    is checked again, and every retained horse must match the official universe.
    """
    race_id = str(spec.get("race_id", ""))
    if not re.fullmatch(r"[A-Za-z0-9_.-]{4,120}", race_id):
        raise BloodBError("BLOODB_ACCEPTANCE_RACE_ID_UNSAFE")
    if not spec.get("signed_source_envelope_path"):
        raise BloodBError("BLOODB_ACCEPTANCE_SIGNED_SOURCE_REQUIRED")
    official, source = load_official(spec)
    if source["level"] != "SOURCE_ED25519_ONLY_NOT_INDEPENDENT_OIDC_ATTESTED_HERE":
        raise BloodBError("BLOODB_ACCEPTANCE_UNTRUSTED_SOURCE_LEVEL")
    if spec.get("jra_signed_source_artifact_sha256") != source["source_artifact_sha256"]:
        raise BloodBError("BLOODB_ACCEPTANCE_QUEUE_SOURCE_HASH_MISMATCH")

    root = private_root.expanduser().resolve()
    dest = root / race_id
    if dest.is_symlink() or not dest.is_dir() or dest.stat().st_mode & 0o077:
        raise BloodBError("BLOODB_ACCEPTANCE_PRIVATE_CAPTURE_NOT_FOUND")
    for filename in REQUIRED:
        _private_file(dest / filename)
    raw = (dest / "subscriber_page.html").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    detail = _safe_json(dest / "diagnostic.json")
    summary = _safe_json(dest / "summary.json")
    binding = _safe_json(dest / "jra_source_binding.json")
    cutoff = utc_time(spec["prediction_cutoff"])
    captured = utc_time(detail["captured_at"])
    if captured >= cutoff or detail.get("race_date") != spec["race_date"]:
        raise BloodBError("BLOODB_ACCEPTANCE_TEMPORAL_OR_RACE_MISMATCH")
    if detail.get("prediction_cutoff") != spec["prediction_cutoff"]:
        raise BloodBError("BLOODB_ACCEPTANCE_CUTOFF_MISMATCH")
    env = _safe_json(Path(spec["signed_source_envelope_path"]))
    frozen = utc_time(env["artifact"]["source_freeze_at"])
    if frozen > captured:
        raise BloodBError("BLOODB_ACCEPTANCE_CAPTURE_PRECEDES_SIGNED_SOURCE")
    if detail.get("raw_sha256") != digest or summary.get("raw_sha256") != digest:
        raise BloodBError("BLOODB_ACCEPTANCE_HTML_SHA256_MISMATCH")
    # Re-parse the immutable captured bytes. A diagnostic row or paid-label
    # edit must not pass by merely preserving raw HTML and its SHA-256.
    recomputed = parse_rendered(raw.decode("utf-8"), official)
    if any(detail.get(key) != recomputed[key] for key in
           ("horse_count", "observations", "parser", "observed_labels")):
        raise BloodBError("BLOODB_ACCEPTANCE_REPARSED_HTML_MISMATCH")
    if binding.get("bloodb_page_sha256") != digest or binding.get("jra_official_source") != source:
        raise BloodBError("BLOODB_ACCEPTANCE_SOURCE_BINDING_MISMATCH")
    if detail.get("race_id") != race_id or summary.get("race_id") != race_id or binding.get("race_id") != race_id:
        raise BloodBError("BLOODB_ACCEPTANCE_RACE_ID_MISMATCH")
    if detail.get("capture_method") != "MEMBER_AUTHENTICATED_RENDERED_DOM":
        raise BloodBError("BLOODB_ACCEPTANCE_CAPTURE_METHOD_MISMATCH")
    origin = allowed_page(detail.get("origin_url", ""))
    from urllib.parse import urlparse, parse_qs
    observed_rcode = parse_qs(urlparse(origin).query).get("rcode", [None])[0]
    if (not observed_rcode or observed_rcode[:8] != spec["race_date"].replace("-", "") or
            int(observed_rcode[-2:]) != int(spec["race_no"])):
        raise BloodBError("BLOODB_ACCEPTANCE_RACE_DETAIL_IDENTITY_MISMATCH")
    if (detail.get("production_authority") is not False or
            detail.get("bvi_population_authority") is not False or
            detail.get("signed_final") is not False or detail.get("oos_increment") != 0 or
            summary.get("production_authority") is not False or
            summary.get("upload_to_github") is not False or
            binding.get("production_authority") is not False or
            binding.get("signed_final") is not False):
        raise BloodBError("BLOODB_ACCEPTANCE_DIAGNOSTIC_FIREWALL_INVALID")
    names = official_universe(official)
    observations = detail.get("observations")
    if not isinstance(observations, list) or len(observations) != len(names):
        raise BloodBError("BLOODB_ACCEPTANCE_FULL_RUNNER_COVERAGE_FAILED")
    matched = set()
    observed_labels = set()
    for row in observations:
        if not isinstance(row, dict):
            raise BloodBError("BLOODB_ACCEPTANCE_HORSE_ROW_INVALID")
        horse = namekey(row.get("horse_name"))
        if horse not in names or horse in matched or str(row.get("horse_no")) != names[horse]:
            raise BloodBError("BLOODB_ACCEPTANCE_HORSE_IDENTITY_FAILED")
        matched.add(horse)
        labels = row.get("observed_labels")
        if not isinstance(labels, dict) or any(x not in FIELDS for x in labels):
            raise BloodBError("BLOODB_ACCEPTANCE_UNKNOWN_LABEL")
        observed_labels.update(labels)
    if (matched != set(names) or
            summary.get("runner_count") != len(names) or detail.get("horse_count") != len(names) or
            set(detail.get("observed_labels", [])) != observed_labels or
            set(summary.get("labels", [])) != observed_labels):
        raise BloodBError("BLOODB_ACCEPTANCE_COVERAGE_OR_SCHEMA_MISMATCH")
    return {
        "status": "LOCAL_CAPTURE_ARTIFACT_INTEGRITY_VERIFIED",
        "profile": PROFILE_ID, "race_id": race_id,
        "official_runner_count": len(names), "matched_runner_count": len(matched),
        "observed_header_names": sorted(observed_labels),
        "capture_before_cutoff": True, "jra_ed25519_envelope_reverified": True,
        "jra_independent_oidc_attested_here": False,
        "bloodb_provider_attested": False,
        "provider_automation_permission_independently_verified": False,
        "actual_member_html_accepted_locally": True,
        "production_bvi_authority": False, "production_prediction_authority": False,
        "actual_purchase_authority": False, "oos_increment": 0,
        "paid_horse_rows_exported": False, "raw_html_exported": False,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Mac-only local Blood-B acceptance; no member data output")
    p.add_argument("mode", choices=("status", "live"))
    p.add_argument("--race-id", required=True)
    p.add_argument("--queue", type=Path, default=HOME / "bloodb_queue.json")
    p.add_argument("--profile", type=Path, default=PROFILE)
    p.add_argument("--private-dir", type=Path, default=PRIVATE)
    p.add_argument("--provider-permission-confirmed", action="store_true")
    args = p.parse_args(argv)
    spec = queue_spec(args.queue, args.race_id)
    if args.mode == "live":
        if not args.provider_permission_confirmed:
            raise BloodBError("PROVIDER_AUTOMATED_ACCESS_PERMISSION_MUST_BE_CONFIRMED")
        if datetime.now(timezone.utc) >= utc_time(spec["prediction_cutoff"]):
            raise BloodBError("BLOODB_PREDICTION_CUTOFF_EXPIRED")
        if not args.profile.expanduser().is_dir():
            raise BloodBError("BLOODB_LOCAL_SUBSCRIBER_LOGIN_PROFILE_REQUIRED")
        with playwright_sync()() as pl:
            context = pl.chromium.launch_persistent_context(
                str(private_dir(args.profile)), headless=True,
                accept_downloads=False)
            try:
                run_one(context, spec, private_root=args.private_dir)
            finally:
                context.close()
    report = verify_capture(spec, private_root=args.private_dir)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
