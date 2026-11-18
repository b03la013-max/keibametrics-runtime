"""Privacy regression: LOCAL PAPER must never publish to a public GitHub issue."""
import copy
import os
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from runtime.local_autopilot import run


class PrivateDeliveryTest(unittest.TestCase):
    def test_configured_public_issue_never_sends_or_marks_owner_reached(self):
        race = {
            "post_current": "2026-11-16T11:45:00+09:00",
            "delivery_attempts": 0,
            "delivered_rev": None,
            "editions": [{
                "rev": "MIZ_01.r1",
                "edition": "直前版",
                "delivery": {"PUSH_VERIFIED": True, "LINK_AVAILABLE": "https://example.invalid/paper"},
            }],
        }
        queue = {"races": {"MIZ_01": race}}
        original = copy.deepcopy(queue)
        with patch.dict(os.environ, {
            "KM_LOCAL_DELIVERY_ISSUE": "424",
            "GH_TOKEN": "test-placeholder-not-a-real-secret",
        }):
            with patch.object(run, "_gh", side_effect=AssertionError("outbound GitHub API is forbidden")) as request:
                changed = run.deliver(
                    queue, Path("/nonexistent-private-test"),
                    datetime(2026, 11, 15, 14, 0, tzinfo=timezone.utc),
                )
        self.assertFalse(changed)
        self.assertEqual(queue, original)
        request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
