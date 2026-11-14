import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(ROOT / "runtime" / "jra_source_runtime"))

from jra_candidate_postresult_closedloop import JRA_INTENT_VENUE_IDS  # noqa: E402
from jra_race_day_resolver import VENUES  # noqa: E402


def test_every_resolver_venue_id_is_accepted():
    assert {vid for vid, _ in VENUES.values()} <= JRA_INTENT_VENUE_IDS


def test_fukushima_accepted():
    assert "FKS" in JRA_INTENT_VENUE_IDS
