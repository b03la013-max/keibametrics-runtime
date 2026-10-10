"""No subscriber network. Exercise the Mac acceptance boundary with signed fixtures."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(ROOT / "scripts"))

from jra_bloodb_mac_acceptance import queue_spec, verify_capture
from jra_bloodb_mac_automation import run_one
from jra_bloodb_mac_collector import BloodBError
from test_jra_bloodb_mac_automation import FakeBrowser
from test_jra_bloodb_mac_collector import HTML
from test_jra_bloodb_signed_source_queue_sync import (
    fixture, RACE, NOW, OFFICIAL,
)
from jra_bloodb_signed_source_queue_sync import synchronize

LIVE_URL = "https://www.blood-b.com/main.php?rcode=2026101101010609"
HTML_OFFICIAL = (HTML.replace("テストホース一号", "血統テスト一号")
                     .replace("テストホース二号", "血統テスト二号"))


class LocalAcceptanceTests(unittest.TestCase):
    def populate(self, root: Path):
        fixture(root)
        q = root / "private" / "bloodb_queue.json"
        synchronize(root, q, now=NOW)
        spec = queue_spec(q, RACE)
        self.assertTrue(spec["signed_source_envelope_path"].endswith("source_receipt_envelope.json"))
        spec["bloodb_race_url"] = LIVE_URL
        destination = root / "private" / "captures"
        run_one(FakeBrowser(detail=HTML_OFFICIAL), spec, clock=lambda: NOW,
                private_root=destination)
        return q, spec, destination

    def test_capture_full_runner_identity_and_receipt_integrity(self):
        with tempfile.TemporaryDirectory() as directory:
            queue, spec, dest = self.populate(Path(directory))
            receipt = verify_capture(spec, private_root=dest)
            self.assertEqual(receipt["status"], "LOCAL_CAPTURE_ARTIFACT_INTEGRITY_VERIFIED")
            self.assertEqual(receipt["official_runner_count"], 2)
            self.assertEqual(receipt["matched_runner_count"], 2)
            self.assertFalse(receipt["bloodb_provider_attested"])
            self.assertFalse(receipt["jra_independent_oidc_attested_here"])
            self.assertFalse(receipt["production_bvi_authority"])
            self.assertEqual(receipt["oos_increment"], 0)
            self.assertFalse(receipt["paid_horse_rows_exported"])
            self.assertEqual(queue_spec(queue, RACE)["race_id"], RACE)

    def test_no_unsigned_or_ambiguous_queue_can_be_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            queue, spec, dest = self.populate(Path(directory))
            x = dict(spec)
            x.pop("signed_source_envelope_path")
            with self.assertRaisesRegex(BloodBError, "SIGNED_SOURCE_REQUIRED"):
                verify_capture(x, private_root=dest)
            x = dict(spec, jra_signed_source_artifact_sha256="0" * 64)
            with self.assertRaisesRegex(BloodBError, "QUEUE_SOURCE_HASH_MISMATCH"):
                verify_capture(x, private_root=dest)
            original = json.loads(queue.read_text())
            queue.write_text(json.dumps(original + original), encoding="utf-8")
            with self.assertRaisesRegex(BloodBError, "MISSING_OR_DUPLICATED"):
                queue_spec(queue, RACE)

    def test_raw_html_or_runner_or_binding_tampering_is_rejected(self):
        for target, field, newvalue, error in (
            ("subscriber_page.html", None, None, "HTML_SHA256_MISMATCH"),
            ("diagnostic.json", "horse_no", "99", "REPARSED_HTML_MISMATCH"),
            ("jra_source_binding.json", "bloodb_page_sha256", "0" * 64, "SOURCE_BINDING_MISMATCH"),
        ):
            with self.subTest(target=target):
                with tempfile.TemporaryDirectory() as directory:
                    _, spec, dest = self.populate(Path(directory))
                    path = dest / RACE / target
                    if target.endswith(".html"):
                        path.write_bytes(path.read_bytes() + b"\n<!-- forged -->")
                    else:
                        rec = json.loads(path.read_text(encoding="utf-8"))
                        if field == "horse_no":
                            rec["observations"][0][field] = newvalue
                        else:
                            rec[field] = newvalue
                        path.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
                    with self.assertRaisesRegex(BloodBError, error):
                        verify_capture(spec, private_root=dest)

    def test_paid_label_edit_with_unchanged_html_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            _, spec, dest = self.populate(Path(directory))
            path = dest / RACE / "diagnostic.json"
            record = json.loads(path.read_text(encoding="utf-8"))
            record["observations"][0]["observed_labels"]["相対指数"] = "999"
            path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(BloodBError, "REPARSED_HTML_MISMATCH"):
                verify_capture(spec, private_root=dest)

    def test_wrong_race_detail_url_cannot_be_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            _, spec, dest = self.populate(Path(directory))
            path = dest / RACE / "diagnostic.json"
            record = json.loads(path.read_text(encoding="utf-8"))
            record["origin_url"] = "https://www.blood-b.com/main.php?rcode=2026101101010610"
            path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(BloodBError, "RACE_DETAIL_IDENTITY_MISMATCH"):
                verify_capture(spec, private_root=dest)

    def test_cannot_accept_capture_predating_signed_source_or_after_cutoff(self):
        for replacement, error in (
            ("2026-10-10T09:00:00+09:00", "CAPTURE_PRECEDES_SIGNED_SOURCE"),
            ("2026-10-11T15:00:00+09:00", "TEMPORAL_OR_RACE_MISMATCH"),
        ):
            with self.subTest(replacement=replacement):
                with tempfile.TemporaryDirectory() as directory:
                    _, spec, dest = self.populate(Path(directory))
                    path = dest / RACE / "diagnostic.json"
                    rec = json.loads(path.read_text(encoding="utf-8"))
                    rec["captured_at"] = replacement
                    path.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
                    with self.assertRaisesRegex(BloodBError, error):
                        verify_capture(spec, private_root=dest)

    def test_external_symlink_and_wrong_capture_label_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            _, spec, dest = self.populate(Path(directory))
            path = dest / RACE / "summary.json"
            outside = dest / "external_private.json"
            outside.write_bytes(path.read_bytes())
            path.unlink()
            path.symlink_to(outside)
            with self.assertRaisesRegex(BloodBError, "SYMLINK"):
                verify_capture(spec, private_root=dest)


if __name__ == "__main__":
    unittest.main()
