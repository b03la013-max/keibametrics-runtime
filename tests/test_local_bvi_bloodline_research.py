import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from local_bvi_bloodline_research import evaluate, load_dataset
from local_fullnumerical_production import materialize_production

NOW = "2026-10-12T07:00:00+00:00"


def test_known_pedigree_matches_both_categories_without_age2_double_counting():
    r = evaluate({"sire": "ホッコータルマエ", "damsire": "キングカメハメハ"}, {"venue": "OHI"}, NOW)
    assert r["connection_status"] == "CONNECTED"
    assert r["research_observed_weight"] == 50
    assert r["research_components"]["sire"]["year_count"] == 5
    assert r["research_components"]["damsire"]["year_count"] == 5
    assert r["research_value"] > 52
    assert r["formal_value"] == 52
    assert not r["prediction_authority"]
    assert not r["venue_reference_rows"]  # Ohi population is not in this dataset.


@pytest.mark.parametrize("as_of", [None, "bad", "2026-10-12", "2026-10-12T06:44:17Z", "2025-12-31T23:59:59+09:00"])
def test_pre_collection_and_unknown_freeze_cannot_consume_future_data(as_of):
    r = evaluate({"sire": "ホッコータルマエ"}, {"venue": "SAG"}, as_of)
    assert r["connection_status"] == "TEMPORAL_BLOCKED"
    assert r["research_value"] is None
    assert r["source_refs"] == []


def test_unlisted_bloodline_is_unknown_neutral_not_zero():
    r = evaluate({"sire": "未掲載の種牡馬", "damsire": None}, {"venue": "NGY"}, NOW)
    assert r["research_value"] == 52
    assert r["research_status"] == "UNKNOWN"
    assert r["research_observed_weight"] == 0
    assert r["research_components"]["sire"]["status"] == "UNKNOWN"


def test_duplicate_supplement_publications_never_change_score():
    dataset = load_dataset()
    raw, race = {"sire": "ロードカナロア"}, {"venue": "NGY"}
    a = evaluate(raw, race, NOW, dataset)
    modified = copy.deepcopy(dataset)
    modified[1]["supplement"] *= 2
    b = evaluate(raw, race, NOW, modified)
    assert a["venue_reference_rows"]
    assert len(b["venue_reference_rows"]) == 2 * len(a["venue_reference_rows"])
    assert a["research_value"] == b["research_value"]
    assert a["formal_value"] == b["formal_value"] == 52
    assert "NO_ERA_OR_SURFACE_INFERENCE" in a["venue_reference_policy"]


def test_dataset_hash_is_checked(tmp_path):
    manifest, _ = load_dataset()
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    (tmp_path / manifest["data_file"]).write_text("{}")
    with pytest.raises(ValueError, match="HASH_MISMATCH"):
        load_dataset(tmp_path / "manifest.json")


def test_production_connection_preserves_historical_bvi_and_prediction():
    request = json.loads((ROOT / "runtime/formal_intents/KM-LOCAL-OHI-20261007-R01-LIVE-R1.json").read_text())
    source = json.loads((ROOT / "runtime/executions/KM-LOCAL-OHI-20261007-R01-LIVE-R1/FORMAL/runs/37571596254-formal/source_receipt_envelope.json").read_text())["artifact"]
    result = materialize_production(source, request, request["required_indices"])
    assert result["static_prediction"] == request["static_prediction"]
    assert result["bloodline_bvi_connection"]["connected_runners"] == 0
    assert result["numeric_coverage"]["numeric_value_count"] == 348
    for r in result["runners"]:
        bvi = r["canonical_components"]["BVIg-L"]
        assert bvi["value"] == 52
        assert bvi["terminal_status"] == "RULED-NEUTRAL"
        assert r["bloodline_bvi_research"]["research_value"] is None


def test_connection_with_simulated_post_collection_freeze_is_research_only():
    request = json.loads((ROOT / "runtime/formal_intents/KM-LOCAL-OHI-20261007-R01-LIVE-R1.json").read_text())
    source = json.loads((ROOT / "runtime/executions/KM-LOCAL-OHI-20261007-R01-LIVE-R1/FORMAL/runs/37571596254-formal/source_receipt_envelope.json").read_text())["artifact"]
    before = materialize_production(source, request, request["required_indices"])
    simulated = copy.deepcopy(source)
    simulated["source_freeze_at"] = NOW  # Integration simulation, not a genuine new source receipt.
    after = materialize_production(simulated, request, request["required_indices"])
    assert after["bloodline_bvi_connection"]["connected_runners"] == 12
    audit = after["production_numerical_summary"]["bloodline_bvi_research"]
    assert len(audit) == 12
    assert audit[0]["research_value"] == after["runners"][0]["bloodline_bvi_research"]["research_value"]
    assert any(r["bloodline_bvi_research"]["research_observed_weight"] for r in after["runners"])
    assert [r["canonical_components"]["BVIg-L"]["value"] for r in before["runners"]] == [
        r["canonical_components"]["BVIg-L"]["value"] for r in after["runners"]]
    assert after["static_prediction"] == before["static_prediction"]
