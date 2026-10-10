"""Failure categories and externally verified completion remain independent."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from jra_single_entry_outcome import evidence_terminal_eligible, verify_formal_completion_summary


def fixture():
    request = {"race_id":"TEST", "family_id":"JRA", "scheduled_post_at":"2026-10-10T12:25:00+09:00", "runners":[{},{}], "source_snapshot_sha256":"a"*64,
               "run_count":20000}
    summary = {"status":"FULL_FORMAL_E2E_PASS", "race_id":"TEST", "family_id":"JRA",
               "temporal_formality":"FORMAL-PRE-RACE", "acceptance_only":False,
               "source_snapshot_sha256":"a"*64,
               "execution_stage_manifest":{"FINAL":{"status":"PASS"}},
               "all_mandatory_stages_verified":True,
               "all_mandatory_pre_race_stages_verified":True,
               "manifest":{"required_count":40, "calculated_count":40,
                           "ruled_hold_count":0, "not_applicable_count":0, "unresolved_count":0},
               "pre_krs":{"verified":True, "receipt_sha256":"b"*64},
               "krs":{"verified":True, "receipt_sha256":"c"*64,
                      "requested_run_count":20000, "actual_run_count":20000},
               "final":{"verified":True, "receipt_sha256":"d"*64,
                        "immutable_artifact_sha256":"e"*64,"receipt_timestamp":"2026-10-10T12:20:00+09:00"}}
    return request, summary


class OutcomeTests(unittest.TestCase):
    def test_static_and_integrity_failure_cannot_be_evidence_no_bet(self):
        gap = {"auto_handoff_error":"JRA_AUTHORIZED_FULL20_INCOMPLETE",
               "production_full_numerical_ready":False,
               "first_blocked_stage":"PRODUCTION_FEATURE_INDEX_CLOSURE",
               "partial_base_blocked_count":5}
        self.assertTrue(evidence_terminal_eligible(gap))
        for error in ("JRA_PRODUCTION_STATIC_OWNER_NOT_AUTHORIZED",
                      "JRA_SOURCE_SNAPSHOT_HASH_INVALID", "JRA_STATIC_OR_DISPATCH_TIME_INVALID"):
            self.assertFalse(evidence_terminal_eligible({**gap,"auto_handoff_error":error}))
        self.assertFalse(evidence_terminal_eligible({**gap,"production_full_numerical_ready":True}))
        self.assertFalse(evidence_terminal_eligible({**gap,"partial_base_blocked_count":0}))

    def test_canonical_verified_summary_completes_without_local_signature_claim(self):
        req, summary = fixture()
        result = verify_formal_completion_summary(summary, req)
        self.assertTrue(result["production_full_prediction_completed"])
        self.assertFalse(result["independent_signature_verification_by_this_function"])

    def test_default_5000_contract_is_preserved(self):
        req, summary = fixture()
        req.pop("run_count")
        summary["krs"].update(requested_run_count=5000,actual_run_count=5000)
        self.assertTrue(verify_formal_completion_summary(summary,req)["production_full_prediction_completed"])

    def test_run_success_is_not_enough_replay_count_signature_and_identity(self):
        req, summary = fixture()
        changes = (
            lambda x:x.update(acceptance_only=True),
            lambda x:x.update(temporal_formality="REPLAY"),
            lambda x:x.update(race_id="OTHER"),
            lambda x:x.update(source_snapshot_sha256="f"*64),
            lambda x:x["krs"].update(actual_run_count=5000),
            lambda x:x["final"].update(verified=False),
            lambda x:x["final"].update(receipt_timestamp="2026-10-10T12:25:00+09:00"),
            lambda x:x["final"].update(receipt_timestamp="2026-10-10T12:20:00"),
            lambda x:x["manifest"].update(calculated_count=20),
            lambda x:x["manifest"].update(ruled_hold_count=1),
            lambda x:x.update(all_mandatory_pre_race_stages_verified=False),
        )
        for change in changes:
            bad = deepcopy(summary); change(bad)
            with self.subTest(summary=bad), self.assertRaises(ValueError):
                verify_formal_completion_summary(bad, req)
        with self.assertRaises(ValueError):
            verify_formal_completion_summary({},req)
        with self.assertRaises(ValueError):
            verify_formal_completion_summary(summary,{**req,"acceptance_only":True})
