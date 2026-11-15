"""Supplemental identity hypotheses cannot become verified current IDs."""
from datetime import date
from decimal import Decimal

from runtime.local_fnb_csv_composite_numeric import materialize_composite_reference
from test_local_fnb_csv_preliminary_numeric import sample, NOW


def index(*, future=False, ambiguous=False):
    day = date(2026, 11, 4) if future else date(2026, 10, 1)
    start = {"date": day.strftime("%y.%m.%d"), "finish": 1, "field_size": 2,
        "venue": "船橋", "distance": 1200, "surface": "DIRT", "direction": "LEFT", "going": "良",
        "race_name": "Ｃ２五六", "ride_jockey": "合成騎手", "ride_popularity": 1,
        "ride_body_weight": 450, "ride_carried_weight": 53,
        "content_positions": [2,1], "content_time_seconds": 75,
        "margin": 0.1, "class_score": 58, "class_parse_state": "PARSED_CLASS_ORDINAL", "finish_score": 100}
    own = {"date": day, "finish": 1, "field_size": 2, "venue": "船橋", "distance": 1200,
        "surface": "DIRT", "direction": "LEFT", "going": "良", "race_name": "Ｃ２五六",
        "jockey": "合成騎手", "popularity": 1, "body_weight": 450, "carried_weight": Decimal(53),
        "positions": [2,1], "time_seconds": Decimal(75), "margin": Decimal("0.1"),
        "class_score": Decimal(58), "class_state": "PARSED_CLASS_ORDINAL", "finish_score": Decimal(100)}
    return {"receipt": {"as_of": "2026-11-03T14:23:36+00:00", "target_year": 2026,
        "current_permanent_ids_inferred": False, "source_or_consumer_authority_granted": False},
        "entries": {("合成馬1","合成父","合成母","合成母父","牡3"): {
        "status": "HOLD_AMBIGUOUS_ID" if ambiguous else "UNIQUE_ARCHIVED_COMPOSITE_HYPOTHESIS",
        "archived_observed_id": "SYNTHETIC_ARCHIVE_ID", "starts": [start], "independent_history": [own],
        "source_refs": ["SYNTHETIC_OLD_RAW", "a"*64, "b"*64], "provenance": [{"source_raw_sha256": "b"*64}]}}}


def test_explicit_research_hypothesis_consumes_dated_history_with_witness_and_no_identity_promotion():
    raw, capture, race = sample()
    result = materialize_composite_reference(raw, capture=capture, race=race, archive_index=index(), now=NOW)
    summary = result["summary"]
    assert summary["composite_hypotheses_consumed"] == summary["history_starts_consumed"] == 1
    assert summary["component_records"] == summary["component_matches"] == 126
    assert summary["base_index_records"] == summary["base_index_matches"] == 18
    assert summary["new_nonmissing_hypothesis_components"] > 0
    assert summary["arithmetic29"]["status"] == "29_OF_29_RECORDED_FEATURE_ARITHMETIC_PASS"
    assert result["raw_field"]["1"]["horse_id"] is None
    assert result["identity_hypotheses"]["1"]["current_identity_verified"] is False
    feature = result["numerical"]["runners"][0]["evidence_features"]["recent_finish"]
    assert feature["score"] == 100
    assert "SYNTHETIC_OLD_RAW" in feature["evidence_refs"]
    assert summary["formal_source_admitted"] is False
    assert summary["registered_oos_increment"] == summary["live_accepted_races"] == 0


def test_same_day_history_and_ambiguous_identity_do_not_enter_scores():
    raw, capture, race = sample()
    for options in ({"future": True}, {"ambiguous": True}):
        result = materialize_composite_reference(raw, capture=capture, race=race, archive_index=index(**options), now=NOW)
        assert result["summary"]["history_starts_consumed"] == 0
        assert result["summary"]["new_nonmissing_hypothesis_components"] == 0
        assert result["numerical"]["runners"][0]["evidence_features"]["recent_finish"]["missing"] is True
