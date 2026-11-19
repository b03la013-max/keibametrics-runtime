import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, "runtime/analysis")
import jra_kametani_match as km

RULES = Path("research/kametani/sire_rules_jra_v1.json")


def test_rules_are_reproducible_and_have_no_not_local_scene():
    before = RULES.read_text()
    subprocess.run([sys.executable, "research/kametani/build_rules_jra_v1.py"], check=True, capture_output=True)
    assert RULES.read_text() == before
    d = json.loads(before)
    assert not any(a.get("jra") for e in d["entries"] for s in ("buy", "caution") for a in e[s])


def _ctx(**kw):
    km.rules()
    c = {"surface": "DIRT", "distance": 1400, "venue": "東京", "going": "良", "sex": "牡", "age": 4, "year": 2026,
         "cls": "1win", "damsire_type": None, "starts": [], "newcomer": False, "front": None, "pop": 5, "frame": 3}
    c.update(kw)
    return c


def test_jra_course_keys():
    assert km.check({"S": "D", "straight": "long"}, _ctx())[0] == "MATCH"
    assert km.check({"S": "D", "straight": "long"}, _ctx(venue="中山"))[0] == "NO"
    assert km.check({"S": "T", "straight": "long"}, _ctx(surface="TURF", venue="京都"))[0] == "UNKNOWN"  # inner/outer
    assert km.check({"root": 1}, _ctx(distance=1600))[0] == "MATCH"
    assert km.check({"cls": "low"}, _ctx(cls="2win+"))[0] == "NO"
    assert km.check({"venue": ["東京"], "wet": 1}, _ctx(going="重"))[0] == "MATCH"


def test_measure_is_non_production():
    rep, rows = km.measure(["20261115"])
    assert rep["production_effect"] == "NONE" and rep["races"] > 0
    assert {r["state"] for r in rows} <= {"BUY", "CAUTION", "BOTH", "NONE", "UNCOVERED"}
