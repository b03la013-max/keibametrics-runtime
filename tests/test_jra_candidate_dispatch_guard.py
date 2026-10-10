"""Prospective candidate dispatch cannot backdate an expired race."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from jra_candidate_dispatch_guard import (
    JRACandidateDispatchGuardError, candidate_dispatch_decision,
)


def fixture():
    intent = {
        "family_id": "JRA",
        "race_id": "KM-JRA-TKY-20261010-R05",
        "temporal_mode": "FORMAL-PRE-RACE",
        "acceptance_only": False,
        "prediction_cutoff": "2026-10-10T12:18:00+09:00",
        "external_dispatch_deadline_at": "2026-10-10T12:22:00+09:00",
        "scheduled_post_at": "2026-10-10T12:25:00+09:00",
    }
    checkpoint = {
        "race_id": intent["race_id"],
        "prediction_cutoff": intent["prediction_cutoff"],
        "source_freeze_at": "2026-10-10T03:08:42+00:00",
        "receipt_sha256": "a"*64,
        "source_snapshot_sha256": "b"*64,
    }
    return intent, checkpoint


class TestJRAProspectiveDispatch(unittest.TestCase):
    def test_timed_live_candidate_can_dispatch(self):
        intent, checkpoint = fixture()
        result = candidate_dispatch_decision(
            intent, checkpoint, now="2026-10-10T12:12:00+09:00"
        )
        self.assertTrue(result["dispatch"])
        self.assertEqual(result["classification"], "PROSPECTIVE_CANDIDATE_ONLY")

    def test_boundary_at_cutoff_and_post_race_never_dispatch(self):
        intent, checkpoint = fixture()
        for time in (
            "2026-10-10T12:18:00+09:00",
            "2026-10-10T03:20:00+00:00",
            "2026-10-10T12:22:00+09:00",
            "2026-10-10T12:25:00+09:00",
            "2026-10-10T13:18:00+09:00",
        ):
            with self.subTest(time=time):
                status = candidate_dispatch_decision(intent, checkpoint, now=time)
                self.assertFalse(status["dispatch"])
                self.assertEqual(status["reason"], "PREDICTION_CUTOFF_EXPIRED")

    def test_simulation_and_replay_never_gain_forward_status(self):
        intent, checkpoint = fixture()
        intent["acceptance_only"] = True
        self.assertFalse(candidate_dispatch_decision(
            intent, checkpoint, now="2026-10-10T12:12:00+09:00"
        )["dispatch"])
        intent["acceptance_only"] = False
        intent["temporal_mode"] = "REPLAY"
        self.assertFalse(candidate_dispatch_decision(
            intent, checkpoint, now="2026-10-10T12:12:00+09:00"
        )["dispatch"])

    def test_missing_or_misbound_verified_source_cannot_dispatch(self):
        intent, checkpoint = fixture()
        for patch in ({"race_id": "OTHER"}, {"receipt_sha256": ""},
                      {"prediction_cutoff": "2026-10-10T12:19:00+09:00"}):
            with self.subTest(patch=patch):
                bad = deepcopy(checkpoint)
                bad.update(patch)
                with self.assertRaises(JRACandidateDispatchGuardError):
                    candidate_dispatch_decision(
                        intent, bad, now="2026-10-10T12:12:00+09:00"
                    )

    def test_bad_timezone_and_cutoff_order_cannot_dispatch(self):
        intent, checkpoint = fixture()
        intent["external_dispatch_deadline_at"] = "2026-10-10T12:13:00"
        with self.assertRaisesRegex(JRACandidateDispatchGuardError, "TIME_MISSING_TIMEZONE"):
            candidate_dispatch_decision(
                intent, checkpoint, now="2026-10-10T12:12:00+09:00"
            )
        intent["external_dispatch_deadline_at"] = "2026-10-10T12:15:00+09:00"
        with self.assertRaisesRegex(JRACandidateDispatchGuardError, "TEMPORAL_CONTRACT_INVALID"):
            candidate_dispatch_decision(
                intent, checkpoint, now="2026-10-10T12:12:00+09:00"
            )


if __name__ == "__main__":
    unittest.main()
