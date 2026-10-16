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
        out = self.run_at(13, 45)
        self.assertEqual([o["status"] for o in out if o["race_id"].endswith("R11")], ["DISPATCH", "DISPATCH"])
        self.assertEqual(len(self.sent), 2)
        again = self.run_at(13, 50)
        self.assertTrue(all(o["status"] != "DISPATCH" for o in again if o["race_id"].endswith("R11")))
        self.assertEqual(len(self.sent), 2)
        sched = json.loads((self.tmp / "runtime/jra_race_day_plan/2026-10-11.schedule.json").read_text())
        self.assertEqual(sched["KM-JRA-TKY-20261011-R11"]["post"], "2026-10-11T14:30:00+09:00")

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


class TestResolverClientRate(unittest.TestCase):
    def test_resolver_uses_a_permitted_polite_rate(self):
        import jra_pedigree_harvest as h
        import jra_race_day_resolver as r
        seen = []
        class Stop(Exception):
            pass
        class Fake(h._Client):
            def __init__(self, delay=1.0):
                super().__init__(delay=delay)  # raises if too fast
                seen.append(delay)
            def get(self, *a, **k):
                raise Stop()
        orig = h._Client
        h._Client = Fake
        try:
            with self.assertRaises(Stop):
                r.resolve_day("2026-10-11", "東京")
        finally:
            h._Client = orig
        self.assertTrue(seen and seen[0] >= 0.7)


class TestAllRacesAndStatus(unittest.TestCase):
    def test_all_races_plan_and_status_index(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "runtime/jra_formal_intents").mkdir(parents=True)
        (tmp / "runtime/jra_race_day_plan").mkdir(parents=True)
        (tmp / "runtime/jra_race_day_plan/2026-10-11.json").write_text(json.dumps({"all_races": True}))
        sent = []
        now = dt.datetime(2026, 10, 11, 13, 45, tzinfo=JST)
        out = tick(tmp, "2026-10-11", now, meetings=lambda d: ["東京", "京都"],
                   resolve=lambda d, v: ("x", RACES), dispatch=lambda *a: sent.append(a))
        self.assertEqual(len(out), 24)
        self.assertEqual(sorted(a[:2] for a in sent), [("京都", 11), ("東京", 11)])
        idx = json.loads((tmp / "runtime/jra_race_day_status/2026-10-11.json").read_text())
        states = {r["race_id"]: r["state"] for r in idx["races"]}
        self.assertEqual(states["KM-JRA-TKY-20261011-R11"], "DISPATCHED_RUNNING")
        self.assertEqual(states["KM-JRA-TKY-20261011-R01"], "MISSED_WINDOW")
        self.assertEqual(states["KM-JRA-TKY-20261011-R12"], "WAITING")
        self.assertTrue((tmp / "runtime/jra_race_day_status/2026-10-11.md").exists())

    def test_no_plan_and_no_default_does_nothing(self):
        tmp = Path(tempfile.mkdtemp())
        now = dt.datetime(2026, 10, 11, 13, 30, tzinfo=JST)
        self.assertEqual(tick(tmp, "2026-10-11", now, meetings=lambda d: ["東京"],
                              resolve=lambda d, v: ("x", RACES), dispatch=lambda *a: None), [])

    def test_non_race_day_stops_without_writing(self):
        tmp = Path(tempfile.mkdtemp())
        now = dt.datetime(2026, 10, 13, 8, 30, tzinfo=JST)
        sent = []
        for cache in (None, {}):
            out = tick(tmp, "2026-10-13", now, meetings=lambda d: [], resolve=lambda d, v: ("x", RACES),
                       dispatch=lambda *a: sent.append(a), default_all=True, cache=cache)
            self.assertEqual(out, [{"race_id": "2026-10-13", "status": "NO_OFFICIAL_MEETINGS"}])
        self.assertEqual(sent, [])
        self.assertFalse((tmp / "runtime/jra_race_day_status").exists())
        self.assertFalse((tmp / "runtime/jra_race_day_plan/2026-10-13.state.json").exists())

    def test_calendar_failure_is_reported_not_raised(self):
        tmp = Path(tempfile.mkdtemp())
        def boom(d):
            raise ValueError("JRA_RESOLVER_ENTRY_TOKEN_NOT_FOUND")
        now = dt.datetime(2026, 10, 11, 13, 30, tzinfo=JST)
        out = tick(tmp, "2026-10-11", now, meetings=boom, resolve=lambda d, v: ("x", RACES),
                   dispatch=lambda *a: None, default_all=True)
        self.assertTrue(out[0]["status"].startswith("OFFICIAL_CALENDAR_UNAVAILABLE"))
