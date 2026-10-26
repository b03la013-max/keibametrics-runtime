"""Mock navigation only: unresolved HTTP 200 bodies never prove no meeting."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "runtime"), str(ROOT / "runtime/jra_source_runtime")]
import jra_pedigree_harvest
from jra_race_day_resolver import resolve_meetings


def observed_navigation(monkeypatch, body):
    calls = []

    class Client:
        def __init__(self, **kwargs):
            assert kwargs == {"delay": 1.0}

        def get(self, url):
            calls.append(("GET", url))
            return "doAction('/JRADB/accessD.html','OBSERVED_ENTRY')"

        def post(self, path, token):
            calls.append(("POST", path, token))
            return body

    monkeypatch.setattr(jra_pedigree_harvest, "_Client", Client)
    return calls


@pytest.mark.parametrize("body", [
    "<html>Service unavailable</html>",
    "<html><form>Sign in</form></html>",
    "",
    "pw01drl00052026040320261031/",  # incomplete observed checksum
    "pw01drl00052026040320261340/AB",  # unresolved date, not an empty day
    "pw01drl00992026040320261031/AB",  # unknown target venue cannot disappear
    "pw01drl00052026040320261025/AB pw01drl00992026040320261031/CD",
])
def test_unresolved_200_navigation_never_returns_empty_meetings(monkeypatch, body):
    calls = observed_navigation(monkeypatch, body)
    with pytest.raises(ValueError, match="MEETING_UNIVERSE_UNRESOLVED"):
        resolve_meetings("2026-10-31")
    assert len(calls) == 2  # one calendar GET and its existing navigation POST


def test_existing_official_day_tokens_preserve_the_requested_venue_universe(monkeypatch):
    observed_navigation(monkeypatch, " ".join([
        "pw01drl00082026040320261031/AB",
        "pw01drl00052026040320261031/CD",
        "pw01drl00042026040320261031/EF",
        "pw01drl00052026040320261031/CD",
        "pw01drl00062026040320261025/01",
    ]))
    assert resolve_meetings("2026-10-31") == ["新潟", "東京", "京都"]


@pytest.mark.parametrize("other_days", [
    ["20261031", "20261101"],  # target outside observed navigation range
    ["20261024", "20261031"],  # absence inside the range is not completeness
])
def test_other_dates_do_not_prove_a_nonmeeting_target(monkeypatch, other_days):
    calls = observed_navigation(monkeypatch, " ".join(
        "pw01drl000520260403" + day + "/AB" for day in other_days))
    with pytest.raises(ValueError, match="MEETING_UNIVERSE_UNRESOLVED"):
        resolve_meetings("2026-10-26")
    assert len(calls) == 2
