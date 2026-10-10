"""Offline tests for Blood-B one-command Mac last-mile acceptance."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "runtime"))
from jra_bloodb_mac_final_acceptance import (
    accept_one, main, select_race, SOURCE_LEVEL,
)
from jra_bloodb_mac_collector import BloodBError

NOW = datetime(2026, 10, 10, 13, 0, tzinfo=timezone.utc)
HASH = "a" * 64


def spec(*, race_id="KM-JRA-KYO-20261011-R09", minutes=20):
    return {
        "race_id": race_id,
        "prediction_cutoff": (NOW + timedelta(minutes=minutes)).isoformat(),
        "signed_source_envelope_path": "/private/never-upload-source.json",
        "jra_signed_source_artifact_sha256": HASH,
        "production_authority": False,
    }


def loader(_):
    return ([{"horse_no": 1}, {"horse_no": 2}], {
        "level": SOURCE_LEVEL, "source_artifact_sha256": HASH,
    })


class FinalAcceptanceTests(unittest.TestCase):
    def queue(self, root, rows):
        path = Path(root) / "bloodb_queue.json"
        path.write_text(json.dumps(rows), encoding="utf-8")
        os.chmod(path, 0o600)
        return path

    def test_chooses_earliest_future_verified_source(self):
        with tempfile.TemporaryDirectory() as folder:
            later = spec(race_id="KM-JRA-KYO-20261011-R10", minutes=45)
            earlier = spec()
            selected = select_race(self.queue(folder, [later, earlier]),
                                   now=NOW, source_loader=loader)
            self.assertEqual(selected["race_id"], earlier["race_id"])

    def test_expired_or_non_diagnostic_never_eligible(self):
        with tempfile.TemporaryDirectory() as folder:
            p = self.queue(folder, [spec(minutes=-1)])
            with self.assertRaisesRegex(BloodBError, "NO_VERIFIED_FUTURE"):
                select_race(p, now=NOW, source_loader=loader)
            item = spec()
            item["production_authority"] = True
            with self.assertRaisesRegex(BloodBError, "NON_DIAGNOSTIC"):
                select_race(self.queue(folder, [item]), now=NOW, source_loader=loader)

    def test_bad_signature_binding_or_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            item = spec()
            def forged(_):
                return ([{"horse_no": 1}, {"horse_no": 2}], {
                    "level": SOURCE_LEVEL, "source_artifact_sha256": "b" * 64,
                })
            with self.assertRaisesRegex(BloodBError, "SOURCE_IDENTITY"):
                select_race(self.queue(folder, [item]), now=NOW, source_loader=forged)
            with self.assertRaisesRegex(BloodBError, "DUPLICATED"):
                select_race(self.queue(folder, [item, item]), now=NOW, source_loader=loader)

    def test_no_provider_permission_blocks_before_queue_or_browser(self):
        with patch("jra_bloodb_mac_final_acceptance.platform.system", return_value="Darwin"), \
             patch("jra_bloodb_mac_final_acceptance.synchronize") as sync:
            self.assertEqual(main(["live"]), 2)
            sync.assert_not_called()

    def test_probe_failure_does_not_capture(self):
        with tempfile.TemporaryDirectory() as folder:
            calls = []
            with self.assertRaisesRegex(BloodBError, "PROBE_BLOCKED"):
                accept_one(object(), spec(), private_root=Path(folder),
                           probe=lambda *_: {"status": "BLOCKED", "block_reason": "BLOODB_LOGIN_REQUIRED"},
                           capture=lambda *_args, **_kw: calls.append("captured"))
            self.assertEqual(calls, [])

    def test_verified_capture_is_diagnostic_only_and_no_paid_output(self):
        with tempfile.TemporaryDirectory() as folder:
            calls = []
            def capture(*args, **kwargs):
                calls.append("capture")
            def verify(*args, **kwargs):
                calls.append("verify")
                return {"status": "LOCAL_CAPTURE_ARTIFACT_INTEGRITY_VERIFIED",
                        "production_bvi_authority": False,
                        "matched_runner_count": 2, "official_runner_count": 2,
                        "jra_ed25519_envelope_reverified": True}
            result = accept_one(object(), spec(), private_root=Path(folder),
                                probe=lambda *_: {"status": "LOCAL_MEMBER_DOM_SCHEMA_COMPATIBLE"},
                                capture=capture, verify=verify)
            self.assertEqual(calls, ["capture", "verify"])
            self.assertFalse(result["production_authority"])
            self.assertFalse(result["production_bvi_authority"])
            self.assertEqual(result["oos_increment"], 0)
            self.assertFalse(result["paid_data_exported"])
            self.assertNotIn("observations", json.dumps(result))

    def test_existing_capture_audited_without_duplicate_fetch(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / spec()["race_id"]).mkdir()
            result = accept_one(object(), spec(), private_root=Path(folder),
                                probe=lambda *_: self.fail("unexpected paid probe"),
                                capture=lambda *_args, **_kw: self.fail("unexpected duplicate capture"),
                                verify=lambda *_args, **_kw: {
                                    "status": "LOCAL_CAPTURE_ARTIFACT_INTEGRITY_VERIFIED",
                                    "production_bvi_authority": False,
                                    "matched_runner_count": 2,
                                    "official_runner_count": 2,
                                    "jra_ed25519_envelope_reverified": True,
                                })
            self.assertEqual(result["stage"], "ALREADY_CAPTURED_REVERIFIED")


if __name__ == "__main__":
    unittest.main()
