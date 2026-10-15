"""SOURCE two-point official observation for AKI-JRA v2.1 external_state."""
from copy import deepcopy
import datetime as dt
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "jra_source_runtime"))
from jra_market_observation import attach_aki_external_observations, EXTERNAL_TARGET_INTERVAL_SECONDS

UTC = dt.timezone.utc
T1 = dt.datetime(2026, 10, 12, 5, 50, 0, tzinfo=UTC)
CUTOFF = "2026-10-12T15:35:00+09:00"


def snap(sid, sha, at):
    return {"source_id": sid, "snapshot_sha256": sha, "fetched_at": at.isoformat(), "official": True,
            "authority": "JRA_OFFICIAL", "cutoff_relation": "PRE_CUTOFF", "raw_sha256": "r" + sha,
            "final_url": "https://www.jra.go.jp/JRADB/accessD.html"}


def detail(sha, odds, going="良"):
    return {"source_snapshot_sha256": sha, "race_environment": {"going": going},
            "runners": [{"runner_id": r, "horse_no": int(r), "win_odds": v} for r, v in odds.items()]}


def artifact(odds=None):
    odds = odds or {"1": 3.2, "2": 5.5, "3": 12.0}
    return {"jra_official_race_card_detail": detail("A" * 64, odds),
            "sources": [snap("JRA-OFFICIAL-RACE-CARD-DETAIL", "A" * 64, T1)],
            "jra_official_runner_universe": {"runners": [{"runner_id": r, "horse_no": int(r), "status": "ACTIVE"} for r in ("1", "2", "3")]}}


class Clock:
    def __init__(self, t):
        self.t = t
    def now(self):
        return self.t
    def sleep(self, s):
        self.t += dt.timedelta(seconds=s)


def run(art, odds2=None, going2="良", start=T1 + dt.timedelta(seconds=20), fail=False):
    c = Clock(start)
    def refetch():
        if fail:
            raise ValueError("HTTP 503")
        return detail("B" * 64, odds2 or {"1": 2.9, "2": 6.1, "3": 12.0}, going2), \
            snap("JRA-OFFICIAL-RACE-CARD-DETAIL-REOBSERVATION", "B" * 64, c.t)
    return attach_aki_external_observations(art, CUTOFF, refetch=refetch, sleep=c.sleep, now=c.now), c


def test_two_ordered_official_observations_published():
    out, c = run(artifact())
    series = out["aki_external_observations"]
    assert len(series) == 2 and out["aki_external_observation_status"]["status"] == "PASS"
    a, b = (dt.datetime.fromisoformat(x["observed_at"]) for x in series)
    assert (b - a).total_seconds() >= EXTERNAL_TARGET_INTERVAL_SECONDS >= 60
    for o in series:
        assert o["production_fact_authority"] is True and o["source_authority"] == "JRA_OFFICIAL"
        assert set(o["win_odds"]) == {"1", "2", "3"} and o["going"] == "良"
        assert o["evidence_refs"] and o["source_fact"]
    assert series[1]["win_odds"]["1"] == 2.9
    assert out["sources"][-1]["source_id"] == "JRA-OFFICIAL-RACE-CARD-DETAIL-REOBSERVATION"
    assert [s["source_id"] for s in out["sources"]].count("JRA-OFFICIAL-RACE-CARD-DETAIL") == 1


def test_incomplete_or_failed_second_observation_publishes_nothing():
    for kw, reason in (({"odds2": {"1": 2.9, "2": None, "3": 12.0}}, "SECOND:WIN_ODDS_MISSING:2"),
                       ({"going2": None}, "SECOND:GOING_NOT_PUBLISHED"),
                       ({"fail": True}, "REOBSERVATION_FAILED"),
                       ({"odds2": {"1": 2.9, "2": 6.0}}, "SECOND:RUNNER_SET_MISMATCH")):
        art = artifact()
        before = deepcopy(art["sources"])
        out, _ = run(art, **kw)
        assert "aki_external_observations" not in out
        assert out["aki_external_observation_status"]["reason"].startswith(reason)
        assert out["sources"] == before


def test_first_observation_incomplete_never_refetches():
    art = artifact({"1": 3.2, "2": None, "3": 12.0})
    out, _ = run(art, fail=True)
    assert out["aki_external_observation_status"]["reason"] == "FIRST:WIN_ODDS_MISSING:2"
    assert "aki_external_observations" not in out


def test_no_reobservation_when_too_close_to_cutoff():
    late = dt.datetime.fromisoformat(CUTOFF).astimezone(UTC) - dt.timedelta(seconds=90)
    art = artifact()
    art["sources"][0]["fetched_at"] = (late - dt.timedelta(seconds=10)).isoformat()
    out, _ = run(art, start=late)
    assert out["aki_external_observation_status"]["reason"] == "INSUFFICIENT_TIME_BEFORE_CUTOFF"
    assert "aki_external_observations" not in out
