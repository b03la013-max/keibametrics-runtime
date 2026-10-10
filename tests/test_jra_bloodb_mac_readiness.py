"""No network, no paid HTML. Local BloodB readiness is never Production."""
from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from datetime import datetime

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from jra_bloodb_mac_readiness import readiness, SOURCE_FILES

NOW=datetime.fromisoformat("2026-10-10T23:00:00+09:00")

class ReadinessTests(unittest.TestCase):
    def test_no_mac_or_no_private_session_never_fake_acceptance(self):
        with tempfile.TemporaryDirectory() as root:
            r=readiness(repo=Path(root),home=Path(root)/"home",now=NOW,os_name="Linux")
            self.assertEqual(r["status"],"BLOCKED_UNTIL_USER_MAC_LIVE_ACCEPTANCE")
            self.assertFalse(r["production_authority"])
            self.assertFalse(r["live_member_dom_acceptance_run"])
            self.assertFalse(r["paid_content_exported"])
            self.assertIn("NOT_MACOS_EXECUTION_HOST",r["blockers"])
            self.assertIn("PROVIDER_AUTOMATION_PERMISSION_NOT_INDEPENDENTLY_VERIFIED",r["blockers"])
            self.assertIn("REAL_SUBSCRIBER_DOM_ACCEPTANCE_NOT_OBSERVED",r["blockers"])
            self.assertEqual(r["eligible_future_queue_count"],0)

    def test_future_signed_queue_count_and_no_private_content_exposed(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            home=root/"home"
            home.mkdir(mode=0o700)
            (home/"browser_bloodb").mkdir(mode=0o700)
            for name in SOURCE_FILES:
                p=root/name
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text("placeholder",encoding="utf-8")
            source=root/"dummy-source.json"
            source.write_text("test",encoding="utf-8")
            q=home/"bloodb_queue.json"
            data=[
              {"race_id":"KM-JRA-KYO-20261011-R09",
               "prediction_cutoff":"2026-10-11T14:00:00+09:00",
               "signed_source_envelope_path":str(source)},
              {"race_id":"KM-JRA-TKY-20261009-R09",
               "prediction_cutoff":"2026-10-09T14:00:00+09:00"},
            ]
            q.write_text(json.dumps(data),encoding="utf-8")
            os.chmod(q,0o600)
            result=readiness(repo=root,home=home,now=NOW,os_name="Darwin")
            self.assertTrue(result["mac_os"])
            self.assertTrue(result["repository_complete"])
            self.assertTrue(result["private_queue_valid"])
            self.assertEqual(result["eligible_future_queue_count"],1)
            self.assertEqual(result["expired_queue_count"],1)
            self.assertEqual(result["source_file_missing_count"],0)
            self.assertFalse(result["live_member_dom_acceptance_run"])
            self.assertFalse(result["provider_permission_independent_proof"])
            report=json.dumps(result,ensure_ascii=False)
            self.assertNotIn(str(source),report)
            self.assertNotIn("KM-JRA-KYO-20261011-R09",report)
            self.assertNotIn("DataBuyer",report)

    def test_queue_public_perms_and_path_injection_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            home=root/"home"
            home.mkdir(mode=0o700)
            q=home/"bloodb_queue.json"
            q.write_text(json.dumps([{
                "race_id":"../../private/exfiltration",
                "prediction_cutoff":"2026-10-11T14:00:00+09:00",
            }]))
            os.chmod(q,0o600)
            r=readiness(repo=root,home=home,now=NOW,os_name="Darwin")
            self.assertFalse(r["private_queue_valid"])
            q.write_text("[]")
            os.chmod(q,0o644)
            r2=readiness(repo=root,home=home,now=NOW,os_name="Darwin")
            self.assertFalse(r2["private_queue_valid"])

if __name__=="__main__":
    unittest.main()
