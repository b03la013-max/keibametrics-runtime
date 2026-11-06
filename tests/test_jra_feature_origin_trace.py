"""Metadata regression; no new numerical rule or source admission."""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from jra_source_to_evidence_features import _feature_origin, _build_feature_trace
from jra_evidence_to_base_production import build_production_ledger


def feature(rule, category="NEUTRAL", fact="published fact"):
    return {"rule_id": rule, "category": category, "source_fact": fact,
            "evidence_refs": ["SIGNED_SOURCE"], "source_authority": "JRA_OFFICIAL"}


def test_observed_inputs_do_not_make_the_category_a_direct_measurement():
    actual = _feature_origin(feature("JRA-BODYWEIGHT-DELTA-BAND-v1"))
    assert actual["evidence_origin_type"] == "OBSERVED_FACT"
    assert actual["value_type"] == "REGISTERED_CATEGORY_EVALUATION"
    assert actual["category_is_direct_measurement"] is False
    assert actual["new_raw_observation_credit"] is False


def test_readiness_gate_and_condition_proxies_stay_proxies():
    for rule in ("KM-JRA-OA-PREPARATION-CONTINUITY-v1",
                 "KM-JRA-OA-TARGET-INTENT-CONTINUITY-v1",
                 "KM-JRA-OA-START-NOT-BEHIND-RATE-v1",
                 "KM-JRA-OA-PHYSICAL-READINESS-BW-v1"):
        assert _feature_origin(feature(rule))["evidence_origin_type"] == "PROXY"


def test_registered_workout_rating_is_not_an_observed_clock():
    for rule in ("JRA-WORKOUT-CAPABILITY-COMMENT-v1", "KM-JRA-OA-WORKOUT-FINAL-RATING-v1"):
        assert _feature_origin(feature(rule))["evidence_origin_type"] == "REGISTERED_ASSESSMENT"


def test_distance_rule_requires_preserved_branch_evidence():
    rule = "KM-JRA-OA-DISTANCE-FIT-v1"
    assert _feature_origin(feature(rule, fact="same_surface_within_200m_normalized_finish=0.7; runs=2"))["evidence_origin_type"] == "REGISTERED_DERIVED_EVALUATION"
    # The fallback may name a damsire; the exact feature origin prefix matters.
    assert _feature_origin(feature(rule, fact="distance_fit (newcomer, sire distance record): pedigree_distance: damsire=X; normalized_finish=.7"))["evidence_origin_type"] == "EMPIRICAL_ESTIMATE"
    assert _feature_origin(feature(rule, fact="normalized_finish=.7"))["evidence_origin_type"] == "UNKNOWN"


def test_missing_neutral_and_unknown_rule_are_not_observations():
    assert _feature_origin(None)["evidence_origin_type"] == "MISSING"
    assert _feature_origin(feature("UNRECOGNIZED-RULE"))["evidence_origin_type"] == "UNKNOWN"
    assert _feature_origin(feature("UNRECOGNIZED-RULE"))["value_type"] == "UNKNOWN_CATEGORY_EVALUATION"
    # A neutral category is an evaluation, not proof of an authorized missing-data default.
    assert _feature_origin(feature("KM-JRA-SAME-DISTANCE-FIT-v1"))["evidence_origin_type"] == "REGISTERED_DERIVED_EVALUATION"


def test_absent_feature_and_published_history_do_not_prove_nonpublication():
    mapping = {"index_profiles": {"LOW_CAREER": {"CFI": {"same_distance_fit": 1.0}}}, "dcr": {}}
    runner = {"runner_id": "4", "career_starts": 1, "evidence_features": {}}
    trace = _build_feature_trace(runner, {}, {}, [], {"JRA_HORSE_HISTORY": {"fact_available": True, "run_count": 1}}, mapping)
    row = trace["features"]["same_distance_fit"]
    assert row["fact_available"] is True
    assert row["production_feature_state"] == "MISSING"
    assert row["source_nonpublication_status"] == "NOT_ESTABLISHED"
    assert trace["summary"]["legacy_dcr_missing_labels_prove_source_nonpublication"] is False


def test_non_numerical_trace_does_not_modify_feature_inputs_or_ledger():
    import json
    mapping = json.loads((ROOT / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json").read_text())
    runner = {"runner_id": "1", "career_starts": 1, "evidence_features": {}}
    before_runner = copy.deepcopy(runner)
    other = {"runner_id": "2", "career_starts": 1, "evidence_features": {}}
    before = build_production_ledger("T", [runner, other], mapping)
    _build_feature_trace(runner, {}, {}, [], {}, mapping)
    assert runner == before_runner
    assert build_production_ledger("T", [runner, other], mapping) == before
