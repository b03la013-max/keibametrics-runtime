import datetime as dt
import json
import sys
import tempfile
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime" / "jra_source_runtime"))
from jra_race_day_autopilot import tick, due
from jra_race_day_resolver import JST

RACES = [{"race_no": i, "post_time": f"{9 + i // 2:02d}:{(i % 2) * 30:02d}", "title": f"R{i}"} for i in range(1, 13)]


class TestAutopilot(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "runtime/jra_race_day_plan").mkdir(parents=True)
        (self.tmp / "runtime/jra_formal_intents").mkdir(parents=True)
        (self.tmp / "runtime/jra_race_day_plan/2026-10-11.json").write_text(json.dumps(
            {"entries": [{"venue": "東京", "races": [11, 12]}, {"venue": "京都", "races": [11]}]}))
        self.sent = []

    def run_at(self, hh, mm, resolve=None):
        now = dt.datetime(2026, 10, 11, hh, mm, tzinfo=JST)
        return tick(self.tmp, "2026-10-11", now,
                    resolve=resolve or (lambda d, v: ("0504202611", RACES)),
                    dispatch=lambda *a: self.sent.append(a))

    def test_window_and_exactly_once(self):
        self.assertEqual(due(dt.datetime(2026, 1, 1, 15, 0, tzinfo=JST), dt.datetime(2026, 1, 1, 13, 0, tzinfo=JST)), "WAIT")
        # R11 post 14:30 -> window 13:25..13:55
        out = self.run_at(13, 30)
        self.assertEqual([o["status"] for o in out if o["race_id"].endswith("R11")], ["DISPATCH", "DISPATCH"])
        self.assertEqual(len(self.sent), 2)
        again = self.run_at(13, 35)
        self.assertTrue(all(o["status"] != "DISPATCH" for o in again if o["race_id"].endswith("R11")))
        self.assertEqual(len(self.sent), 2)

    def test_missed_window_never_dispatches_late(self):
        out = self.run_at(14, 40)
        self.assertTrue(all(o["status"] in ("MISSED_WINDOW", "WAIT") for o in out))
        self.assertEqual(self.sent, [])

    def test_unavailable_card_is_reported(self):
        def boom(d, v):
            raise ValueError("JRA_RESOLVER_MEETING_NOT_UNIQUE:")
        out = self.run_at(13, 30, resolve=boom)
        self.assertTrue(all(o["status"].startswith("OFFICIAL_CARD_UNAVAILABLE") for o in out))
        self.assertEqual(self.sent, [])


if __name__ == "__main__":
    unittest.main()
