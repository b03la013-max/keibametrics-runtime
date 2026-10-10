import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

from jra_source_only_closure_candidate import (
    CandidateClosureError,
    propose_official_observed_features,
    evaluate_static_owner_candidate,
    PRODUCTION_MAPPING,
)
from jra_index_provenance_builder import BASE, DERIVED, FORMULA_REGISTRY


def official_source():
    return {
        "family_id": "JRA",
        "race_id": "KYO-OOS-PROPOSAL",
        "source_snapshot_sha256": "official-source-snapshot-hash",
        "source_race_context": {"race_date": "2026-10-10"},
        "jra_race_context": {"venue_name": "京都", "distance_m": 1600, "surface": "芝"},
        "jra_official_runner_universe": {
            "runners": [
                {"runner_id": "1", "name": "Alpha"},
                {"runner_id": "2", "name": "Bravo"},
                {"runner_id": "3", "name": "Charlie"},
            ]
        },
        "jra_official_race_card_detail": {
            "runners": [
                {"runner_id": "1", "recent_runs": [
                    {"date": "2026-09-20", "finish": 1, "field_size": 10,
                     "venue": "京都", "distance_m": 1600, "surface": "芝"},
                    {"date": "2026-08-20", "finish": 3, "field_size": 12,
                     "venue": "京都", "distance_m": 1600, "surface": "芝"},
                    # Today's result must NEVER be used as prior history.
                    {"date": "2026-10-10", "finish": 1, "field_size": 9,
                     "venue": "京都", "distance_m": 1600, "surface": "芝"},
                ]},
                {"runner_id": "2", "recent_runs": [
                    {"date": "2026-09-20", "finish": 7, "field_size": 10,
                     "venue": "東京", "distance_m": 1800, "surface": "芝"},
                ]},
                {"runner_id": "3", "recent_runs": []},
                # Not in official universe. Must never be discovered as a runner.
                {"runner_id": "99", "recent_runs": [
                    {"date": "2026-09-20", "finish": 1, "field_size": 12},
                ]},
            ]
        }
    }


def test_source_observed_evaluation_with_restricted_temporal_universe():
    src = official_source()
    a = propose_official_observed_features(src)
    assert a["production_evaluator_authority"] is False
    assert a["production_feature_merge_allowed"] is False
    assert a["official_runner_ids"] == ["1", "2", "3"]
    f = a["runners"]["1"]["features"]
    assert set(f) == {
        "recent_performance", "recent_consistency",
        "same_course_fit", "same_distance_fit", "surface_fit"
    }
    assert f["recent_consistency"]["category"] == "VERY_STRONG"
    assert f["recent_consistency"]["sample_count"] == 2
    assert "2026-10-10" not in f["recent_consistency"]["source_fact"].split("source_dates=")[1].split("; all before")[0]
    for feature in f.values():
        assert feature["candidate_only"] is True
        assert feature["production_authority"] is False
        assert feature["evidence_refs"]
        assert "official-source-snapshot-hash" in feature["evidence_refs"]
    assert a["runners"]["2"]["observed_count"] == 0
    assert a["runners"]["3"]["observed_count"] == 0
    assert a == propose_official_observed_features(copy.deepcopy(src))


def test_source_observed_evaluation_rejects_nonofficial_or_unbound_source():
    x = official_source()
    x["jra_official_runner_universe"]["runners"][1]["runner_id"] = "1"
    with pytest.raises(CandidateClosureError, match="OFFICIAL_PDF_UNIVERSE_REQUIRED_UNIQUE"):
        propose_official_observed_features(x)
    x = official_source()
    x["source_snapshot_sha256"] = ""
    with pytest.raises(CandidateClosureError, match="SOURCE_BASIS_OR_DATE_MISSING"):
        propose_official_observed_features(x)


def numerical_request():
    runners = []
    for rid, win, place, third in (("1", 84, 82, 85), ("2", 70, 80, 78), ("3", 62, 66, 70)):
        cells = {}
        for index in BASE + DERIVED:
            score = win if index == "ZAI_WIN" else place if index == "ZAI_PLACE" else third if index == "T3I" else 65
            cells[index] = {
                "value": score,
                "mapping_version": PRODUCTION_MAPPING if index in BASE else FORMULA_REGISTRY,
                "rule_id": f"PRODUCTION-RULE-{index}",
                "evidence_refs": [f"JRA-SRC:{rid}:{index}"],
                "source_fact": "Observed before race",
            }
        runners.append({"runner_id": rid, "canonical_components": cells})
    return {"family_id": "JRA", "race_id": "KYO-CLOSURE", "runners": runners}


def test_full_numeric_input_produces_deterministic_candidate_static_roles_and_pairs():
    req = numerical_request()
    out = evaluate_static_owner_candidate(req, source_snapshot_sha256="JRA-SOURCE-HASH")
    assert out["status"] == "STATIC_OWNER_EXECUTED / CANDIDATE / NON-PRODUCTION"
    assert out["ranking"] == ["1", "2", "3"]
    assert out["production_index_inputs_validated"] is True
    assert out["static_prediction_production_authority"] is False
    assert out["signed_static_freeze_verified"] is False
    assert out["ticket_or_capital_authority"] is False
    assert out["role_registry"]
    assert out["pair_dispositions"]
    assert out["third_dispositions"]
    assert out == evaluate_static_owner_candidate(copy.deepcopy(req), source_snapshot_sha256="JRA-SOURCE-HASH")


def test_static_owner_rejects_candidate_numerics_missing_index_and_bad_provenance():
    req = numerical_request()
    req["runners"][0]["canonical_components"]["HPI"]["candidate_only"] = True
    with pytest.raises(CandidateClosureError, match="CANDIDATE_NUMERICAL_REJECTED"):
        evaluate_static_owner_candidate(req, source_snapshot_sha256="SOURCE")
    req = numerical_request()
    del req["runners"][0]["canonical_components"]["HPI"]
    with pytest.raises(CandidateClosureError, match="FULL20_REQUIRED"):
        evaluate_static_owner_candidate(req, source_snapshot_sha256="SOURCE")
    req = numerical_request()
    req["runners"][1]["canonical_components"]["SSI"]["mapping_version"] = "CANDIDATE"
    with pytest.raises(CandidateClosureError, match="NON_PRODUCTION_MAPPING"):
        evaluate_static_owner_candidate(req, source_snapshot_sha256="SOURCE")
