from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from local_aki_columns import build, decision, verify, LocalAKIError
from local_fullnumerical_production import materialize_production


@pytest.fixture
def real():
    req = json.loads((ROOT / "runtime/formal_intents/KM-LOCAL-KAW-20261012-R11-LIVE-R1.json").read_text())
    source = json.loads((ROOT / "runtime/executions/KM-LOCAL-KAW-20261012-R11-LIVE-R1/FORMAL/runs/38238690895-formal/source_receipt_envelope.json").read_text())["artifact"]
    req["source_snapshot_sha256"] = source["source_snapshot_sha256"]
    return materialize_production(source, req, req["required_indices"]), source


def test_real_source_independent_recompilation_and_mec(real):
    q, s = real
    x = build(q, s)
    assert verify(q, s, x)["status"] == "PASS"
    d = decision(q, x)
    assert d["mec_verification"]["mec_verified"]
    assert d["capital"]["paper_only"]
    assert not d["purchase_tickets"]
    assert d["mec"]["ticket_count"] == 10


def test_budget_never_changes_selection(real):
    q, s = real
    a = build(q, s)
    for cap in (0, 100, 100000):
        q["capital_policy"] = {"mode": "HARD_RACE_BUDGET", "max_race_capital": cap}
        b = build(q, s)
        assert a == b
        assert decision(q, b)["paper_tickets"] == decision(q, a)["paper_tickets"]


@pytest.mark.parametrize("family", ["BAN", "JRA"])
def test_family_isolation(real, family):
    q, s = real
    q["family_id"] = family
    with pytest.raises(LocalAKIError, match="LOCAL_ONLY"):
        build(q, s)


@pytest.mark.parametrize("problem", ["duplicate", "missing", "nan", "source", "scratch"])
def test_conflict_and_cancellation_are_explicit(real, problem):
    q, s = real
    if problem == "duplicate": q["runners"].append(deepcopy(q["runners"][0]))
    if problem == "missing": q["runners"][0]["canonical_components"].pop("RSI")
    if problem == "nan": q["runners"][0]["canonical_components"]["RSI"]["value"] = float("nan")
    if problem == "source": q["source_snapshot_sha256"] = "wrong"
    if problem == "scratch": q["runners"].pop()
    with pytest.raises(LocalAKIError): build(q, s)


def test_missing_cannot_admit_even_with_high_risk(real):
    q, s = real
    for r in q["runners"]:
        for f in r["evidence_features"].values(): f["missing"] = True
        for i in ("W-AKI", "P2-AKI", "P3-AKI", "RSI"): r["canonical_components"][i]["value"] = 100
    x = build(q, s)
    assert x["status"] == "NO_BET"
    assert all(not col["selected"] for col in x["columns"].values())
    assert decision(q, x)["capital"]["decision"] == "NO_BET"


def test_higher_risk_widens_observed_columns_without_fixed_count(real):
    q, s = real
    for r in q["runners"]:
        for i in ("W-AKI", "P2-AKI", "P3-AKI", "RSI"): r["canonical_components"][i]["value"] = 0
        r["canonical_components"]["ASI"]["value"] = 100
    low = build(q, s)
    for r in q["runners"]:
        for i in ("W-AKI", "P2-AKI", "P3-AKI", "RSI"): r["canonical_components"][i]["value"] = 75
    high = build(q, s)
    # A changed head universe can change structural exclusions in later
    # columns. Compare breadth, not identical conditional membership.
    for c in ("W", "P2", "P3"):
        assert len(low["columns"][c]["selected"]) <= len(high["columns"][c]["selected"])
    assert any(len(high["columns"][c]["selected"]) > len(low["columns"][c]["selected"]) for c in ("W", "P2", "P3"))


def test_quiet_race_anchors_are_distinct_observed_roles(real):
    q, s = real
    for r in q["runners"]:
        for i in ("W-AKI", "P2-AKI", "P3-AKI", "RSI"): r["canonical_components"][i]["value"] = 0
        r["canonical_components"]["ASI"]["value"] = 100
    x = build(q, s)
    assert x["status"] == "PAPER"
    selected = [x["columns"][c]["selected"] for c in ("W", "P2", "P3")]
    assert all(len(c) == 1 for c in selected)
    assert len({c[0] for c in selected}) == 3
    assert decision(q, x)["mec"]["ticket_count"] == 2


def test_axis_failure_is_no_bet_and_preserves_supported_head(real):
    q, s = real
    for r in q["runners"]:
        rid = str(r["runner_id"])
        r["canonical_components"]["ZAI-WIN"]["value"] = 100 if rid == "2" else 0
        r["canonical_components"]["W-AKI"]["value"] = 0
        r["canonical_components"]["ASI"]["value"] = 49
    x = build(q, s)
    assert x["columns"]["W"]["selected"] == ["2"]
    assert x["status"] == "NO_BET"


def test_input_tampering_detected_against_source(real):
    q, s = real
    x = build(q, s)
    q["runners"][0]["canonical_components"]["W-AKI"]["value"] += 1
    # Independent SOURCE rebuild still produces original selection.
    assert verify(q, s, x)["status"] == "PASS"
    with pytest.raises(LocalAKIError, match="RECOMPUTATION"):
        verify(q, s, build(q, s))


@pytest.mark.parametrize("n", [3, 6, 12, 18])
def test_field_sizes_combinatorics_and_ties_without_fixed_width(real, n):
    q, s = real
    # Explicit synthetic parity fixture, never an actual race or OOS result.
    r = q["runners"][0]
    q["runners"] = [deepcopy(r) for _ in range(n)]
    for i, horse in enumerate(q["runners"], 1):
        horse["runner_id"] = str(i)
        horse["horse_no"] = i
    s["active_runner_universe"] = {"runners": [{"horse_no":i} for i in range(1,n+1)]}
    x = build(q, s)
    assert all(len(c["selected"]) == n for c in x["columns"].values())
    d = decision(q, x)
    assert d["mec"]["ticket_count"] == n*(n-1) + n*(n-1)*(n-2)//6
    assert not any(t["bet_type"] == "TRIFECTA" for t in d["paper_tickets"])
