"""Candidate-only LOCAL Static Owner: prestart source and 29-index closure.

The output is a frozen paper hypothesis; it never proves a Production FINAL.
"""
from datetime import datetime, timezone

import pytest

from runtime.local_race_key_shadow_owner import ShadowOwnerError, compile_shadow


INDEXES = [
    "HPI-L", "CFIg-L", "RFIg-L", "BVIg-L", "JTI-L", "CSI-L",
    "BWI-L", "DCR", "NCI", "TPI-L", "EVI/CEV", "CCI",
    "TRI", "PRI", "OPI-V", "DRS", "URP", "HCS",
    "ZAI-WIN", "ZAI-PLACE", "SRI-L", "T3I-L", "F3S-L", "WCI",
    "W-AKI", "P2-AKI", "P3-AKI", "ASI", "RSI",
]


def fixture():
    ids = ["1", "2", "3", "4", "5", "6"]
    request = {
        "family_id": "LOCAL",
        "execution_id": "KM-LOCAL-KAW-20990101-R01-LIVE-R1",
        "race_id": "KM-LOCAL-KAW-20990101-R01-LIVE-R1",
        "prediction_cutoff": "2099-01-01T12:55:00+09:00",
    }
    source = {
        "receipt_sha256": "signed-external-source",
        "artifact": {
            "formal_ready": True,
            "source_snapshot_sha256": "snapshot",
            "source_freeze_at": "2099-01-01T03:40:00+00:00",
            "official_runner_universe": {"runners": [{"runner_id": rid} for rid in ids]},
        },
    }
    rows = []
    for n, rid in enumerate(ids):
        cc = {}
        for key in INDEXES:
            value = 52.0
            if key == "ZAI-WIN":
                value = [82, 72, 68, 64, 59, 53][n]
            if key == "ZAI-PLACE":
                value = [63, 70, 68, 62, 61, 55][n]
            if key == "T3I-L":
                value = [58, 61, 62, 60, 65, 64][n]
            cc[key] = {"value": value, "terminal_status": "CALCULATED"}
        if rid == "6":
            cc["T3I-L"]["terminal_status"] = "RULED-NEUTRAL"
            cc["T3I-L"]["value"] = 52
        rows.append({"runner_id": rid, "canonical_components": cc})
    numeric = {
        "strict_full_numerical_ready": True,
        "production_numerical_authority": {"prediction_consumption_authorized": False},
        "required_indices": list(INDEXES),
        "runners": rows,
        "index_provenance_hash": "numeric-sha",
    }
    now = datetime(2099, 1, 1, 3, 50, tzinfo=timezone.utc)
    return request, source, numeric, now


def test_frozen_shadow_is_all_runner_result_blind_no_production_claim():
    req, source, numeric, now = fixture()
    out = compile_shadow(req, source, numeric, now=now)
    assert out["ranking"] == ["1", "2", "3", "4", "5", "6"]
    assert out["shadow_width"]["band"] == "SHADOW_MEDIUM"
    assert out["shadow_width"]["heads"] == 2
    assert set(out["role_columns"]) == set(out["ranking"])
    assert out["source_receipt_sha256"] == source["receipt_sha256"]
    assert out["neutral_index_registry"]["6"] == ["T3I-L"]
    assert out["paper_ticket_count"] == len(out["paper_tickets"])
    assert out["paper_capital_yen"] == 100 * len(out["paper_tickets"])
    assert all(len(set(t["selection"])) == len(t["selection"]) for t in out["paper_tickets"])
    assert out["production_authority"] is False
    assert out["signed_final_claim"] is False
    assert out["actual_purchase"] is False
    assert out["prediction_consumption_authorized"] is False
    assert "NON-PRODUCTION" in out["status"]


@pytest.mark.parametrize("target", [
    "SOURCE_AFTER_CUTOFF", "NOW_AFTER_CUTOFF", "UNSIGNED",
    "UNKNOWN_NUMERIC", "CHANGED_UNIVERSE", "MISSING_INDEX", "FAMILY",
    "WRONG_RACE_ID", "MISSING_REQUIRED", "NUMERIC_PROMOTED",
])
def test_invalid_baselines_fail_closed(target):
    req, source, numeric, now = fixture()
    if target == "SOURCE_AFTER_CUTOFF":
        source["artifact"]["source_freeze_at"] = "2099-01-01T04:01:00+00:00"
    if target == "NOW_AFTER_CUTOFF":
        now = datetime(2099, 1, 1, 4, 0, tzinfo=timezone.utc)
    if target == "UNSIGNED":
        source["receipt_sha256"] = ""
    if target == "UNKNOWN_NUMERIC":
        numeric["runners"][0]["canonical_components"]["ZAI-WIN"]["terminal_status"] = "UNRESOLVED"
    if target == "CHANGED_UNIVERSE":
        source["artifact"]["official_runner_universe"]["runners"].pop()
    if target == "MISSING_INDEX":
        numeric["runners"][2]["canonical_components"].pop("RSI")
    if target == "FAMILY":
        req["family_id"] = "JRA"
    if target == "WRONG_RACE_ID":
        req["race_id"] = "OTHER-RACE"
    if target == "MISSING_REQUIRED":
        numeric["required_indices"].pop()
    if target == "NUMERIC_PROMOTED":
        numeric["production_numerical_authority"]["prediction_consumption_authorized"] = True
    with pytest.raises(ShadowOwnerError):
        compile_shadow(req, source, numeric, now=now)


def test_repeatable_prestart_sha_when_freeze_instant_is_same():
    req, source, numeric, now = fixture()
    left = compile_shadow(req, source, numeric, now=now)
    right = compile_shadow(req, source, numeric, now=now)
    assert left == right
    assert left["sha256"] == right["sha256"]


def test_candidate_ranking_not_a_probability():
    req, source, numeric, now = fixture()
    p = compile_shadow(req, source, numeric, now=now)
    assert "probability" not in p
    assert p["promotable_without_forward_oos"] is False
    assert p["pair_conditioning_statement"].startswith("Provisional")


def test_unknown_p3_is_protected_without_treating_neutral_as_weak():
    req, source, numeric, now = fixture()
    # Wide winner separation narrows the candidate's third row to five.
    numeric["runners"][0]["canonical_components"]["ZAI-WIN"]["value"] = 96
    shadow = compile_shadow(req, source, numeric, now=now)
    assert shadow["shadow_width"]["band"] == "SHADOW_NARROW"
    assert shadow["p3_unknown_protection"] == "6"
    assert "P3" in shadow["role_columns"]["6"]
    assert shadow["neutral_index_registry"]["6"] == ["T3I-L"]
    assert shadow["prediction_consumption_authorized"] is False


def test_unknown_winner_cell_does_not_change_observed_gap_or_paper_paths():
    req, source, numeric, now = fixture()
    for row, value in zip(numeric["runners"], [62, 46, 45, 44, 43, 42]):
        row["canonical_components"]["ZAI-WIN"]["value"] = value
    control = compile_shadow(req, source, numeric, now=now)
    assert control["shadow_width"]["winner_spread"] == 16
    assert control["winner_head_local_pairs"] == [
        {"head": "1", "second": "2"}, {"head": "1", "second": "3"},
    ]

    numeric["runners"][-1]["canonical_components"]["ZAI-WIN"] = {
        "value": 52, "terminal_status": "RULED-NEUTRAL",
    }
    shadow = compile_shadow(req, source, numeric, now=now)
    assert shadow["shadow_width"] == control["shadow_width"]
    assert shadow["paper_tickets"] == control["paper_tickets"]
    assert shadow["paper_capital_yen"] == control["paper_capital_yen"]
    assert shadow["ranking"][-1] == "6"
    assert shadow["p3_unknown_protection"] == "6"
    assert shadow["neutral_index_registry"]["6"] == ["ZAI-WIN", "T3I-L"]


@pytest.mark.parametrize("observed_count", [0, 1])
def test_unknown_winner_gap_uses_existing_wide_band_without_inventing_a_spread(observed_count):
    req, source, numeric, now = fixture()
    for row in numeric["runners"][observed_count:]:
        row["canonical_components"]["ZAI-WIN"] = {"value": 52, "terminal_status": "RULED-NEUTRAL"}
    shadow = compile_shadow(req, source, numeric, now=now)
    assert shadow["shadow_width"]["winner_spread"] is None
    assert shadow["shadow_width"]["band"] == "SHADOW_WIDE"
    assert shadow["production_authority"] is False


def test_calculated_tie_has_zero_gap_and_keeps_wide_band():
    req, source, numeric, now = fixture()
    numeric["runners"][1]["canonical_components"]["ZAI-WIN"]["value"] = 82
    out = compile_shadow(req, source, numeric, now=now)
    assert out["ranking"][:2] == ["1", "2"]
    assert out["shadow_width"]["winner_spread"] == 0
    assert out["shadow_width"]["band"] == "SHADOW_WIDE"


@pytest.mark.parametrize("all_neutral", [False, True])
def test_neutral_payload_values_do_not_change_paper_selection(all_neutral):
    req, source, numeric, now = fixture()
    relevant = ("ZAI-WIN", "ZAI-PLACE", "T3I-L")
    rows = numeric["runners"] if all_neutral else numeric["runners"][-2:]
    for row in rows:
        for index in relevant:
            row["canonical_components"][index] = {"value": 52, "terminal_status": "RULED-NEUTRAL"}
    baseline = compile_shadow(req, source, numeric, now=now)
    for position, row in enumerate(rows):
        for index in relevant:
            row["canonical_components"][index]["value"] = 0 if position % 2 else 100
    assert compile_shadow(req, source, numeric, now=now) == baseline


def test_third_protection_and_tickets_are_independent_of_runner_order():
    req, source, numeric, now = fixture()
    numeric["runners"][0]["canonical_components"]["ZAI-WIN"]["value"] = 96
    numeric["runners"][0]["canonical_components"]["T3I-L"].update(
        terminal_status="RULED-NEUTRAL", value=52,
    )
    runners = numeric["runners"]
    runners.append({
        "runner_id": "7", "canonical_components": {
            index: {"value": 55, "terminal_status": "CALCULATED"} for index in INDEXES
        },
    })
    official = source["artifact"]["official_runner_universe"]["runners"]
    official.append({"runner_id": "7"})

    expected = compile_shadow(req, source, numeric, now=now)
    assert expected["p3_unknown_protection"] == "6"
    assert expected["winner_head_local_pairs"] == [
        {"head": "1", "second": "2"}, {"head": "1", "second": "3"},
    ]
    assert expected["paper_ticket_count"] == 10
    assert {tuple(row["selection"]) for row in expected["paper_tickets"]
            if row["bet_type"] == "TRIFECTA" and row["selection"][-1] == "6"} == {
        ("1", "2", "6"), ("1", "3", "6"),
    }
    runners.reverse()
    official.reverse()
    assert compile_shadow(req, source, numeric, now=now) == expected


def test_official_withdrawal_requires_new_numerical_universe():
    req, source, numeric, now = fixture()
    official = source["artifact"]["official_runner_universe"]["runners"]
    official.pop(0)
    with pytest.raises(ShadowOwnerError, match="FULL_RUNNER_UNIVERSE_MISMATCH"):
        compile_shadow(req, source, numeric, now=now)

    numeric["runners"].pop(0)
    out = compile_shadow(req, source, numeric, now=now)
    assert "1" not in out["role_columns"]
    assert all("1" not in row["selection"] for row in out["paper_tickets"])
    assert out["paper_capital_yen"] == 100 * out["paper_ticket_count"]


def test_ruled_hold_is_not_neutral():
    req, source, numeric, now = fixture()
    numeric["runners"][-1]["canonical_components"]["ZAI-WIN"] = {
        "value": None, "terminal_status": "RULED-HOLD",
    }
    with pytest.raises(ShadowOwnerError, match="INDEX_NOT_TERMINAL:6:ZAI-WIN"):
        compile_shadow(req, source, numeric, now=now)
