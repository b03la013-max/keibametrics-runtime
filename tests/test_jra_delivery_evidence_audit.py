import unittest
import json
import tempfile
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO

from runtime.jra_delivery_evidence_audit import _sha, audit_delivery


def seal(obj):
    obj.pop("sha256", None)
    obj["sha256"] = _sha(obj)
    return obj


class DeliveryAuditTest(unittest.TestCase):
    def setUp(self):
        self.final = {"race_id": "KM-JRA-TKY-20261018-R01",
                      "sha256": "a" * 64,
                      "scheduled_post_at": "2026-10-18T10:00:00+09:00"}
        self.pub = seal({"race_id": self.final["race_id"],
                         "final_sha256": self.final["sha256"], "tree_sha256": "b" * 64})
        self.available = seal({"race_id": self.final["race_id"],
                               "final_sha256": self.final["sha256"],
                               "tree_sha256": "b" * 64, "http_status": 200,
                               "availability_verified_at": "2026-10-18T09:55:00+09:00",
                               "availability_verified_before_post": True})

    def test_publication_is_not_receipt(self):
        result = audit_delivery(final=self.final, publication=self.pub)
        self.assertEqual(result["recipient_acknowledged"], "UNVERIFIED")
        self.assertEqual(result["canonical_availability"], "UNVERIFIED")

    def test_readback_not_user_receipt(self):
        result = audit_delivery(final=self.final, publication=self.pub,
                                availability=self.available)
        self.assertEqual(result["canonical_availability"], "READBACK_RECORDED")
        self.assertEqual(result["recipient_acknowledged"], "UNVERIFIED")

    def test_forged_temporal_claim_fails(self):
        bad = dict(self.available, availability_verified_before_post=False)
        seal(bad)
        with self.assertRaisesRegex(ValueError, "TEMPORAL_CLAIM"):
            audit_delivery(final=self.final, publication=self.pub, availability=bad)

    def test_ack_requires_provider_and_matching_message(self):
        ack = seal({"race_id": self.final["race_id"], "final_sha256": self.final["sha256"],
                    "provider_message_id": "m1", "ack_status": "RECEIVED",
                    "received_at": "2026-10-18T09:59:00+09:00"})
        with self.assertRaisesRegex(ValueError, "WITHOUT_NOTIFICATION"):
            audit_delivery(final=self.final, recipient_ack=ack)
        note = seal({"race_id": self.final["race_id"], "final_sha256": self.final["sha256"],
                     "provider_message_id": "m2", "provider_status": "ACCEPTED",
                     "provider_accepted_at": "2026-10-18T09:57:00+09:00"})
        with self.assertRaisesRegex(ValueError, "ACK_BINDING"):
            audit_delivery(final=self.final, notification=note, recipient_ack=ack)

    def test_ack_is_record_not_independent_trust(self):
        note = seal({"race_id": self.final["race_id"], "final_sha256": self.final["sha256"],
                     "provider_message_id": "m1", "provider_status": "ACCEPTED",
                     "provider_accepted_at": "2026-10-18T09:57:00+09:00"})
        ack = seal({"race_id": self.final["race_id"], "final_sha256": self.final["sha256"],
                    "provider_message_id": "m1", "ack_status": "RECEIVED",
                    "received_at": "2026-10-18T09:59:00+09:00"})
        result = audit_delivery(final=self.final, notification=note, recipient_ack=ack)
        self.assertEqual(result["pre_post_delivery"], "ACK_BEFORE_POST_RECORDED")
        self.assertFalse(result["final_signature_independently_verified"])



    def test_ack_cannot_precede_provider_acceptance(self):
        note = seal({"race_id": self.final["race_id"], "final_sha256": self.final["sha256"],
                     "provider_message_id": "m1", "provider_status": "ACCEPTED",
                     "provider_accepted_at": "2026-10-18T09:57:00+09:00"})
        ack = seal({"race_id": self.final["race_id"], "final_sha256": self.final["sha256"],
                    "provider_message_id": "m1", "ack_status": "RECEIVED",
                    "received_at": "2026-10-18T09:56:00+09:00"})
        with self.assertRaisesRegex(ValueError, "ACK_BEFORE_PROVIDER"):
            audit_delivery(final=self.final, notification=note, recipient_ack=ack)

    def test_existing_jra_publication_schema_and_availability(self):
        publication = seal({
            "profile": "KM-JRA-CANONICAL-FINAL-PUBLICATION-v1",
            "race_id": self.final["race_id"], "final_sha256": self.final["sha256"],
            "tree_sha256": "b" * 64, "channel": "GITHUB_CANONICAL_AND_STEP_SUMMARY",
            "notification_sent_at": None, "user_received_at": None,
            "user_delivery_verified": False, "actual_purchase_status": "UNVERIFIED",
        })
        availability = seal({
            "race_id": self.final["race_id"], "final_sha256": self.final["sha256"],
            "tree_sha256": publication["tree_sha256"], "channel": "GITHUB_CANONICAL",
            "availability_verified_at": "2026-10-18T09:55:00+09:00",
            "availability_verified_before_post": True, "http_status": 200,
            "user_delivery_verified": False, "user_received_at": None,
        })
        result = audit_delivery(final=self.final, publication=publication, availability=availability)
        self.assertEqual(result["canonical_availability"], "READBACK_RECORDED")
        self.assertEqual(result["notification_sent"], "UNVERIFIED")
        self.assertEqual(result["recipient_acknowledged"], "UNVERIFIED")
        self.assertEqual(result["pre_post_delivery"], "UNVERIFIED")

    def test_read_only_cli(self):
        from runtime.jra_delivery_evidence_audit import main
        with tempfile.TemporaryDirectory() as directory:
            final_path = Path(directory) / "final.json"
            final_path.write_text(json.dumps(self.final), encoding="utf-8")
            stdout = StringIO()
            with redirect_stdout(stdout):
                result = main(["--final", str(final_path)])
            self.assertEqual(result["recipient_acknowledged"], "UNVERIFIED")
            self.assertEqual(json.loads(stdout.getvalue())["race_id"], self.final["race_id"])
            self.assertEqual(json.loads(final_path.read_text()), self.final)

if __name__ == "__main__":
    unittest.main()
