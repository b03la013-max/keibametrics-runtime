import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

from jra_evidence_to_base_candidate import (
    CandidateMappingError,
    attach_candidate_ledger_to_request,
    load_mapping,
)
from jra_index_provenance_builder import materialize_index_provenance

MAPPING = ROOT / "mapping" / "jra_base_index_evidence_mapping_v0.1_candidate_20260921.json"

FEATURE_NAMES = [
    "workout_capability","pedigree_class_proxy","gate_quality","dash_quality",
    "stable_readiness","jockey_quality","physical_readiness","workout_speed",
    "sprint_pedigree","forward_speed_comment","surface_fit","distance_fit",
    "turn_direction_fit","course_geometry_fit","workout_consistency",
    "preparation_continuity","surface_pedigree","distance_pedigree",
    "sire_newcomer_signal","maternal_class_signal","physical_pedigree_fit",
    "jockey_venue_fit","jockey_style_fit","trainer_quality","target_intent",
    "workout_partner_level","workout_finish","bodyweight_suitability",
    "bodyweight_vs_estimate","equipment_state","going_fit","same_day_track_fit",
    "draw_course_fit","pressure_resilience","stable_trainer_class","market_rank",
    "market_stability","public_expert_support","external_index_support",
    "training_comments_quality"
]

def feature(category, ref):
    return {
        "category": category,
        "evidence_refs": [ref],
        "source_fact": f"fixture fact {ref} -> {category}",
    }

def runner(rid, category):
    return {
        "runner_id": str(rid),
        "name": f"FIXTURE-{rid}",
        "newcomer": True,
        "evidence_features": {
            name: feature(category, f"E{rid}-{name}") for name in FEATURE_NAMES
        },
    }

def test_full_candidate_mapping_can_materialize_20_indices_per_runner():
    mapping = load_mapping(MAPPING)
    request = {
        "race_id": "JRA-C4-MAPPING-SELFTEST",
        "runners": [runner(1, "STRONG"), runner(2, "POSITIVE")],
    }
    request = attach_candidate_ledger_to_request(request, mapping)
    request = materialize_index_provenance(request)

    assert request["numeric_calculation_requirement"] == "FULL_REQUIRED"
    assert request["base_index_mapping_authority"]["production_authority"] is False
    assert len(request["runners"]) == 2
    for r in request["runners"]:
        canonical = r["canonical_components"]
        assert len(canonical) == 20
        for name, spec in canonical.items():
            assert 0 <= spec["value"] <= 100
            assert spec["rule_id"]
            assert spec["mapping_version"]
            assert spec["evidence_refs"]
            assert spec["source_fact"]

def test_mapping_is_deterministic():
    mapping = load_mapping(MAPPING)
    req = {"race_id": "DET", "runners": [runner(1, "STRONG"), runner(2, "POSITIVE")]}
    a = attach_candidate_ledger_to_request(req, mapping)["index_provenance_ledger"]
    b = attach_candidate_ledger_to_request(req, mapping)["index_provenance_ledger"]
    assert a["sha256"] == b["sha256"]
    assert a == b

def test_freehand_numeric_without_category_is_rejected():
    mapping = load_mapping(MAPPING)
    bad = runner(1, "STRONG")
    bad["evidence_features"]["gate_quality"] = {
        "value": 83,
        "evidence_refs": ["BAD"],
        "source_fact": "freehand numeric value",
    }
    try:
        attach_candidate_ledger_to_request({"race_id": "BAD", "runners": [bad]}, mapping)
    except CandidateMappingError as e:
        assert "FEATURE_CATEGORY_INVALID:gate_quality" in str(e)
    else:
        raise AssertionError("freehand numeric feature was not rejected")
