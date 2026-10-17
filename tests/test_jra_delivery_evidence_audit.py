import unittest

from runtime.jra_delivery_evidence_audit import _sha, audit_delivery


def seal(obj):
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


if __name__ == "__main__":
    unittest.main()
