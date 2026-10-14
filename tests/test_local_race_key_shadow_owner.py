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
