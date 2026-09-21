from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

from jra_candidate_fullnumerical_materializer import materialize_full_numerical
from jra_evidence_to_base_candidate import load_mapping

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

def feature(name, category):
    return {
        "category": category,
        "evidence_refs": [f"FIXTURE:{name}"],
        "source_fact": f"fixture {name}={category}",
    }

def runner(rid, category):
    return {
        "runner_id": str(rid),
        "name": f"FIXTURE-{rid}",
        "newcomer": True,
        "evidence_features": {name: feature(name, category) for name in FEATURE_NAMES},
    }

def test_candidate_materializer_reaches_300_of_300_for_15_runners():
    mapping = load_mapping(MAPPING)
    request = {
        "race_id": "JRA-C4-300-OF-300-SELFTEST",
        "runners": [runner(i, "STRONG" if i % 2 else "POSITIVE") for i in range(1, 16)],
    }
    result = materialize_full_numerical(request, mapping)
    summary = result["candidate_full_numerical_summary"]
    assert summary["required_count"] == 300
    assert summary["calculated_count"] == 300
    assert summary["ruled_hold_count"] == 0
    assert summary["unresolved_count"] == 0
    assert summary["full_numerical_complete"] is True
    assert summary["production_authority"] is False
