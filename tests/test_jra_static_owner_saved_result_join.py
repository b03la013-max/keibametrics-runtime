"""Meaningful regressions for the offline saved RESULT boundary."""
import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"
sys.dont_write_bytecode = True
sys.path.insert(0, str(RUNTIME))
import jra_static_owner_forward_oos as old
from jra_static_owner_saved_result_join import gate, qualify, join_saved_result


class SavedJoinTests(unittest.TestCase):
    def setUp(self):
        owner = {"static_prediction": {"ranking": ["1", "2", "3"]},
                 "source_snapshot_sha256": "a" * 64, "source_receipt_sha256": "b" * 64}
        owner["sha256"] = old.sha(owner)
        self.pre = {"profile": old.PROFILE, "owner_profile": old.OWNER_PROFILE,
            "race_id": "KM-JRA-TKY-20261031-R12", "candidate_only": True,
            "production_authority": False, "purchase_authority": False,
            "signed_final_issued": False, "source_snapshot_sha256": "a" * 64,
            "source_receipt_sha256": "b" * 64, "owner": owner,
            "frozen_at": "2026-10-31T06:00:00+00:00", "prediction_cutoff": "2026-10-31T07:10:00+00:00",
            "scheduled_post_at": "2026-10-31T07:15:00+00:00", "ranking": ["1", "2", "3"],
            "market_ranking": ["3", "2", "1"], "full_index_count": 60, "policy_fingerprint": "c" * 64}
        self.pre["sha256"] = old.sha(self.pre)
        self.commit = "2026-10-31T06:00:01+00:00"
        self.request = {"race_id": self.pre["race_id"], "official_result": {"status": "OFFICIAL",
            "result_use": "POST-RACE", "top3": [1, 2, 3], "finish_order": [1, 2, 3],
            "captured_at": "2026-10-31T07:20:00+00:00"}}
        self.envelope = {"receipt_sha256": "d" * 64, "receipt": {
            "artifact_sha256": old.sha(self.request), "timestamp": "2026-10-31T07:20:01+00:00"}}

    def qualify(self, **kwargs):
        args = dict(module=old, commit_at=self.commit, source=gate("PASS"), code=gate("PASS"), scope=gate("PASS"))
        args.update(kwargs)
        return qualify(self.pre, **args)

    def join(self, **kwargs):
        args = dict(module=old, verify_receipt=lambda envelope, *a: envelope["receipt"], signer={}, commit_at=self.commit)
        args.update(kwargs)
        return join_saved_result(self.pre, self.qualify(), self.request, self.envelope, **args)

    def test_existing_evaluator_reused_without_source_mutation(self):
        before = copy.deepcopy((self.pre, self.request, self.envelope))
        out = self.join()
        self.assertTrue(out["static_shadow_evaluation_created"])
        self.assertEqual(out["fixed_bvi_d_oos_increment"], 0)
        self.assertEqual(before, (self.pre, self.request, self.envelope))

    def test_hash_corruption_fails_qualification(self):
        self.pre["ranking"] = ["2", "1", "3"]
        self.assertEqual(self.qualify()["status"], "INELIGIBLE")

    def test_same_second_commit_is_unknown_not_late(self):
        self.pre["frozen_at"] = "2026-10-31T06:00:00.300000+00:00"
        self.pre["sha256"] = old.sha({k: v for k, v in self.pre.items() if k != "sha256"})
        q = self.qualify(commit_at="2026-10-31T06:00:00+00:00")
        self.assertEqual(q["status"], "UNKNOWN")
        self.assertEqual(q["checks"]["prospective_witness"]["reason"], "GIT_COMMIT_SECOND_PRECISION")

    def test_late_commit_and_jump_scope_fail(self):
        self.assertEqual(self.qualify(commit_at="2026-10-31T07:11:00+00:00")["status"], "INELIGIBLE")
        self.assertEqual(self.qualify(scope=gate("FAIL", "DEDICATED_JUMP_OWNER_NOT_ESTABLISHED"))["status"], "INELIGIBLE")

    def test_missing_source_remains_unknown(self):
        self.assertEqual(self.qualify(source=gate("UNKNOWN", "SOURCE_MISSING"))["status"], "UNKNOWN")

    def test_unrecognized_gate_status_does_not_pass(self):
        for status in ("BLOCKED", "READY", None):
            self.assertEqual(self.qualify(source=gate(status))["status"], "UNKNOWN")

    def test_qualification_bound_to_same_race_and_original_hash(self):
        for field, wrong in (("race_id", "KM-JRA-KYO-20261031-R12"), ("frozen_sha256", "0" * 64)):
            q = self.qualify()
            q[field] = wrong
            with self.assertRaisesRegex(ValueError, "QUALIFICATION_BINDING"):
                join_saved_result(self.pre, q, self.request, self.envelope, module=old,
                    verify_receipt=lambda e, *a: e["receipt"], signer={}, commit_at=self.commit)

    def test_changed_checks_cannot_reuse_qualification_hash(self):
        q = self.qualify()
        q["checks"]["source"] = gate("UNKNOWN")
        with self.assertRaisesRegex(ValueError, "QUALIFICATION_BINDING"):
            join_saved_result(self.pre, q, self.request, self.envelope, module=old,
                verify_receipt=lambda e, *a: e["receipt"], signer={}, commit_at=self.commit)

    def test_commit_witness_cannot_be_substituted_at_join(self):
        with self.assertRaisesRegex(ValueError, "QUALIFICATION_BINDING"):
            self.join(commit_at="2026-10-31T06:00:02+00:00")

    def test_historical_owner_is_separate_cohort_not_invalid_original(self):
        self.pre["owner_profile"] = "JRA-HISTORICAL-OWNER"
        self.pre["sha256"] = old.sha({k: v for k, v in self.pre.items() if k != "sha256"})
        q = self.qualify()
        self.assertEqual(q["status"], "OUTSIDE_CURRENT_OWNER_COHORT")
        self.assertEqual(q["checks"]["frozen_hash"]["status"], "PASS")

    def test_wrong_race_or_artifact_hash_rejected(self):
        self.request["race_id"] = "other"
        with self.assertRaisesRegex(ValueError, "RACE_MISMATCH"): self.join()
        self.request["race_id"] = self.pre["race_id"]
        self.envelope["receipt"]["artifact_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "HASH_MISMATCH"): self.join()

    def test_bad_signature_exception_propagates(self):
        def reject(*a): raise ValueError("SIGNATURE_INVALID")
        with self.assertRaisesRegex(ValueError, "SIGNATURE_INVALID"): self.join(verify_receipt=reject)

    def test_result_observed_before_post_or_wrong_universe_rejected(self):
        self.request["official_result"]["captured_at"] = "2026-10-31T07:10:00+00:00"
        self.envelope["receipt"]["artifact_sha256"] = old.sha(self.request)
        with self.assertRaisesRegex(ValueError, "OBSERVED_TIME"): self.join()
        self.request["official_result"]["captured_at"] = "2026-10-31T07:20:00+00:00"
        self.request["official_result"]["top3"] = [1, 2, 4]
        self.envelope["receipt"]["artifact_sha256"] = old.sha(self.request)
        with self.assertRaisesRegex(ValueError, "UNIVERSE"): self.join()


if __name__ == "__main__": unittest.main()
