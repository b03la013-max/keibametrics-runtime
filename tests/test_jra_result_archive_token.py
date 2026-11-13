import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/jra_source_runtime"))
sys.path.insert(0, str(ROOT / "runtime"))
import jra_same_day_results as m  # noqa: E402

KEY, DAY = "0520260501", "20261107"


class Picked(Exception):
    pass


def pick(monkeypatch, html, race_no=2):
    def fake(opener, token, referer):
        raise Picked(token)
    monkeypatch.setattr(m, "_result_post", fake)
    with pytest.raises(Picked) as got:
        m._fetch_race(None, "ref", html, KEY, DAY, race_no, "2026-11-07T10:20:00+09:00")
    return str(got.value)


def test_same_day_token_still_selected(monkeypatch):
    html = f'<a onclick="doAction(\'/JRADB/accessS.html\',\'pw01sde01{KEY}02{DAY}/AB\')">2R</a>'
    assert pick(monkeypatch, html) == f"pw01sde01{KEY}02{DAY}/AB"


def test_archive_page_token_selected(monkeypatch):
    html = (f"pw01sde10{KEY}01{DAY}/11 pw01sde10{KEY}02{DAY}/C4 pw01sde10{KEY}12{DAY}/7F")
    assert pick(monkeypatch, html) == f"pw01sde10{KEY}02{DAY}/C4"


def test_other_race_day_or_meeting_never_selected(monkeypatch):
    html = f"pw01sde10{KEY}12{DAY}/7F pw01sde10{KEY}0220261108/AA pw01sde100520260502" + f"02{DAY}/BB"
    monkeypatch.setattr(m, "_result_post", lambda *a: pytest.fail("no send"))
    with pytest.raises(ValueError, match="RACE_TOKEN_NOT_FOUND:2"):
        m._fetch_race(None, "ref", html, KEY, DAY, 2, "x")


def test_same_day_code_keeps_priority_over_archive(monkeypatch):
    html = f"pw01sde10{KEY}02{DAY}/C4 pw01sde01{KEY}02{DAY}/AB"
    assert pick(monkeypatch, html) == f"pw01sde01{KEY}02{DAY}/AB"


def test_two_distinct_tokens_of_one_code_fail_closed(monkeypatch):
    html = f"pw01sde10{KEY}02{DAY}/AB pw01sde10{KEY}02{DAY}/C4"
    monkeypatch.setattr(m, "_result_post", lambda *a: pytest.fail("no send"))
    with pytest.raises(ValueError, match="AMBIGUOUS"):
        m._fetch_race(None, "ref", html, KEY, DAY, 2, "x")


def test_unpublished_page_code_rejected(monkeypatch):
    html = f"pw01sde99{KEY}02{DAY}/AB"
    monkeypatch.setattr(m, "_result_post", lambda *a: pytest.fail("no send"))
    with pytest.raises(ValueError, match="NOT_FOUND"):
        m._fetch_race(None, "ref", html, KEY, DAY, 2, "x")
