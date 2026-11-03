"""Correctness fixtures only: none of these manufactured rows is LIVE evidence."""
import copy
import importlib.util
import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("base15", ROOT / "runtime/local_base15_research_candidates.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture(component):
    """Known arithmetic, source/ID/condition gates, no real-observation claim."""
    s = m.SPEC_BY_COMPONENT[component]
    sha = "a" * 64
    selector = dict(provider="NAR", fixed_at="2026-09-01T00:00:00+09:00",
                    population_complete=True, complete_twelve_months=True,
                    population_window_start="2025-10-02T12:00:00+09:00",
                    exact_conditions=dict(venue="FNB", distance_m=1500, surface="DIRT", going="GOOD", **{"class": "C3"}, sand_era="ERA-OBSERVED"),
                    condition_race_ids=[f"SYNTHETIC-R{i}" for i in range(30)])
    contrasts = {"distance_trait": ("distance_m", 1500, 1200),
                 "surface_sand_fit": ("going", "GOOD", "HEAVY"),
                 "venue_stat": ("venue", "FNB", "KAW")}
    if s["component"] in contrasts:
        f, a, b = contrasts[s["component"]]
        selector["contrast_fields"] = [f]
        selector["contrast"] = dict(field=f, target=a, reference=b)
        selector["condition_race_ids"] = [f"SYNTHETIC-R{i}" for i in range(60)]
    entities = []
    for e in range(4):
        ent = dict(entity_id=f"SYNTHETIC-ENTITY-{e}", horse_id=f"NAR:HORSE{e}",
                   jockey_active_verified=True, rows=[])
        for name in s["identity_fields"]:
            ent[name] = f"NAR:{name.upper()}{e}"
        for i in range(len(selector["condition_race_ids"])):
            row = dict(selector["exact_conditions"], source_sha256=sha,
                       event_at=f"2026-09-{i%30+1:02d}T12:00:00+09:00", race_id=f"SYNTHETIC-R{i}",
                       horse_id=ent["horse_id"], field_size=10, finish=(e + i % 10) % 10 + 1,
                       last_corner_rank=6, last_corner_name="4C", body_weight_kg=450+i,
                       style_fraction=0.25, style_basis="PRE_FREEZE_SINGLETON_HISTORY",
                       work_type="TRAINING", effort="EASY", work_time_seconds=50.0+i%3,
                       good_run_preparation=True)
            for name in s["identity_fields"]:
                if name in ("parent_id", "sire_id", "damsire_id", "stable_id", "jockey_id"):
                    row[name] = ent[name]
            if s["component"] in contrasts:
                f, a, b = contrasts[s["component"]]
                row[f] = a if i % 2 else b
            ent["rows"].append(row)
        ent["current"] = dict(horse_id=ent["horse_id"], source_sha256=sha,
                              event_at="2026-10-01T12:00:00+09:00",
                              baseline_horse_id=ent["horse_id"], baseline_source_sha256=sha,
                              baseline_event_at="2026-09-15T12:00:00+09:00",
                              target_body_weight_kg=464, target_style_fraction=0.25,
                              style_basis="PRE_FREEZE_SINGLETON_HISTORY",
                              comment_text="SYNTHETIC complete time/condition/comparison/caveat",
                              coding_protocol=m.CODING_PROTOCOL,
                              independent_coder_agreement=True,
                              explicit_time=True, explicit_condition=True,
                              explicit_comparison=e != 3, explicit_uncertainty=True,
                              work_type="TRAINING", effort="EASY", distance_m=1500,
                              work_time_seconds=51.0+e,
                              current_weight_kg=452, previous_weight_kg=450, official_delta_kg=2,
                              reason_evidence_id="SYNTHETIC-NOT-MEASURED",
                              reason_source_sha256=sha, reason_event_at="2026-10-01T11:00:00+09:00",
                              reason_independent_of_delta=True,
                              reason_expected_delta_low_kg=0, reason_expected_delta_high_kg=3,
                              age_years=3, sex="M", prior_muscle_grade=1,
                              current_muscle_grade=1 if e else 2,
                              growth_cause_evidence_id="SYNTHETIC-NOT-MEASURED",
                              growth_cause_source_sha256=sha, growth_cause_event_at="2026-10-01T11:00:00+09:00",
                              fatigue_excluded=True, excess_fat_excluded=True,
                              transport_departure_at="2026-10-01T09:00:00+09:00",
                              transport_arrival_at="2026-10-01T10:00:00+09:00",
                              season_match_id="SYNTHETIC_MATCHED_WINDOW",
                              prior_state_grade=1, current_state_grade=1,
                              observer_ids=["SYNTHETIC:A", "SYNTHETIC:B"],
                              grades={d: [1, 1] for d in ("abdomen", "hindquarters", "coat", "gait", "arousal", "sweat")})
        for name in ("speaker_id", "transport_id"):
            if name in ent:
                ent["current"][name] = ent[name]
        if "parent_id" in ent:
            ent["current"]["parent_id"] = ent["parent_id"]
        entities.append(ent)
    return dict(classification=m.CLASSIFICATION, freeze_at="2026-10-02T12:00:00+09:00",
                selector=selector, selector_sha256=m.canonical_sha256(selector),
                sources={sha: dict(raw_sha256=sha, source_id="SYNTHETIC-NOT-MEASURED",
                                   observed_at="2026-10-01T12:00:00+09:00", qualification="ELIGIBLE_PRIVATE_RESEARCH")},
                target=entities[0], references=entities[1:])


class CandidateTests(unittest.TestCase):
    def evaluate(self, c, p):
        return m.evaluate_candidate(c, p)

    def test_all_fifteen_have_complete_recipes_and_do_not_grant_adoption(self):
        self.assertEqual(len(m.RULE_SPECS), 15)
        for c in m.SPEC_BY_COMPONENT:
            with self.subTest(c=c):
                r = self.evaluate(c, fixture(c))
                self.assertEqual(r["status"], "CALCULATED_RESEARCH_UNADOPTED", r)
                self.assertTrue(0 <= r["score"] <= 100)
                self.assertFalse(r["production_adopted"])
                self.assertFalse(r["formal_consumer_enabled"])
                self.assertIsNone(r["statistical_confidence_interval"])
                self.assertFalse(r["provider_permission_verified_here"])

    def test_all_tied_observations_remain_exactly_fifty(self):
        c = "BWI-L.paddock"
        self.assertEqual(self.evaluate(c, fixture(c))["score"], 50)

    def test_percentile_is_independently_counted(self):
        c = "CSI-L.tri_vertical_comparison"
        r = self.evaluate(c, fixture(c))
        # target=0 from median51; reference=-.5,-1,-1.5 => all lower.
        self.assertEqual(r["score"], 100)
        self.assertEqual(r["raw_metric"], 0)

    def test_missing_is_null_never_formal_neutral(self):
        for c in m.SPEC_BY_COMPONENT:
            with self.subTest(c=c):
                p = fixture(c)
                p["selector"]["population_complete"] = False
                p["selector_sha256"] = m.canonical_sha256(p["selector"])
                r = self.evaluate(c, p)
                self.assertEqual(r["status"], "UNKNOWN")
                self.assertIsNone(r["score"])
                self.assertIsNone(r["raw_metric"])

    def test_undeclared_or_mutated_selector_is_rejected(self):
        c = "BVIg-L.sire_fit"
        p = fixture(c)
        p["selector"]["exact_conditions"]["class"] = "B2"
        self.assertIn("SELECTOR_SHA_MISMATCH", self.evaluate(c, p)["missing_reasons"])

    def test_post_freeze_source_and_current_fact_are_rejected(self):
        c = "BWI-L.paddock"
        p = fixture(c)
        p["target"]["current"]["event_at"] = p["freeze_at"]
        self.assertIn("POST_FREEZE_SOURCE_OR_EVENT", self.evaluate(c, p)["missing_reasons"])

    def test_source_cannot_contain_a_later_observed_event(self):
        c = "BWI-L.paddock"
        p = fixture(c)
        p["target"]["current"]["event_at"] = "2026-10-01T13:00:00+09:00"
        self.assertIn("EVENT_AFTER_SOURCE_OBSERVATION", self.evaluate(c, p)["missing_reasons"])

    def test_nonpositive_observation_units_are_unknown(self):
        cases = [("BVIg-L.physical_style_fit", "body_weight_kg"),
                 ("CSI-L.tri_vertical_comparison", "work_time_seconds"),
                 ("BVIg-L.sire_fit", "distance_m")]
        for c, key in cases:
            with self.subTest(c=c, key=key):
                p = fixture(c)
                p["target"]["rows"][0][key] = -1
                self.assertIsNone(self.evaluate(c, p)["score"])
        p = fixture(c)
        p["sources"]["a"*64]["observed_at"] = "2026-10-03T00:00:00+09:00"
        self.assertIn("POST_FREEZE_SOURCE_OR_EVENT", self.evaluate(c, p)["missing_reasons"])

    def test_name_only_parent_identity_is_rejected(self):
        c = "BVIg-L.sire_fit"
        p = fixture(c)
        p["target"]["sire_id"] = "Well-known sire name"
        self.assertIn("PERMANENT_PROVIDER_ID_REQUIRED:sire_id", self.evaluate(c, p)["missing_reasons"])

    def test_condition_thirty_is_not_replaced_by_reference_entity_three(self):
        c = "BVIg-L.sire_fit"
        p = fixture(c)
        p["selector"]["condition_race_ids"] = p["selector"]["condition_race_ids"][:29]
        p["selector_sha256"] = m.canonical_sha256(p["selector"])
        self.assertIn("ARTICLE67_CONDITION_SET_BELOW_30_RACES", self.evaluate(c, p)["missing_reasons"])

    def test_declared_but_unrepresented_thirty_races_are_rejected(self):
        c = "BVIg-L.sire_fit"
        p = fixture(c)
        for e in [p["target"]]+p["references"]:
            e["rows"] = e["rows"][:1]
        self.assertIn("FIXED_RACE_FRAME_NOT_FULLY_REPRESENTED", self.evaluate(c, p)["missing_reasons"])

    def test_duplicate_row_and_reference_self_leakage_rejected(self):
        c = "BVIg-L.sire_fit"
        p = fixture(c)
        p["target"]["rows"].append(copy.deepcopy(p["target"]["rows"][0]))
        self.assertIn("DUPLICATE_RACE_HORSE_ROW", self.evaluate(c, p)["missing_reasons"])
        p = fixture(c)
        p["references"][0]["entity_id"] = p["target"]["entity_id"]
        self.assertIn("REFERENCE_ENTITIES_NOT_DISTINCT_OR_SELF_INCLUDED", self.evaluate(c, p)["missing_reasons"])

    def test_reference_aliases_do_not_create_independent_parent_identities(self):
        c = "BVIg-L.sire_fit"
        p = fixture(c)
        p["references"][0]["sire_id"] = p["target"]["sire_id"]
        self.assertIn("PERMANENT_REFERENCE_IDENTITIES_NOT_DISTINCT", self.evaluate(c, p)["missing_reasons"])

    def test_same_horse_current_components_reject_other_horse_history(self):
        c = "BWI-L.age_growth"
        p = fixture(c)
        p["target"]["rows"][0]["horse_id"] = "NAR:OTHER"
        self.assertIn("SAME_HORSE_ROW_IDENTITY_MISMATCH", self.evaluate(c, p)["missing_reasons"])

    def test_contrast_thirty_must_be_target_condition_not_combined(self):
        c = "BVIg-L.distance_trait"
        p = fixture(c)
        for e in [p["target"]]+p["references"]:
            for row in e["rows"]:
                row["distance_m"] = 1200
            e["rows"][0]["distance_m"] = 1500
        self.assertIn("ARTICLE67_TARGET_CONDITION_SET_BELOW_30_RACES", self.evaluate(c, p)["missing_reasons"])

    def test_grouped_rank_never_collapses_to_a_scalar(self):
        c = "BVIg-L.distance_sustain"
        for v in ([3, 4], "3-4", True, math.nan, math.inf):
            p = fixture(c)
            p["target"]["rows"][0]["last_corner_rank"] = v
            self.assertIsNone(self.evaluate(c, p)["score"])

    def test_zero_range_does_not_invent_variation(self):
        c = "CSI-L.tri_vertical_comparison"
        p = fixture(c)
        for r in p["target"]["rows"]:
            r["work_time_seconds"] = 51
        self.assertIn("INSUFFICIENT_SAME_HORSE_GOOD_PREPARATION_RANGE", self.evaluate(c, p)["missing_reasons"])

    def test_weight_reason_is_not_inferred_from_delta(self):
        c = "BWI-L.weight_change_reason_rate"
        p = fixture(c)
        p["target"]["current"]["reason_independent_of_delta"] = False
        self.assertIn("INDEPENDENT_REASON_EVIDENCE_REQUIRED", self.evaluate(c, p)["missing_reasons"])

    def test_transport_cannot_happen_after_the_current_state_observation(self):
        c = "BWI-L.transport_season"
        p = fixture(c)
        p["target"]["current"]["transport_arrival_at"] = "2026-10-01T13:00:00+09:00"
        self.assertIn("ACTUAL_TRANSPORT_TIMING_INVALID", self.evaluate(c, p)["missing_reasons"])

    def test_physical_fit_does_not_infer_parenthood_from_name(self):
        c = "BVIg-L.physical_style_fit"
        p = fixture(c)
        p["target"]["current"]["parent_id"] = "NAR:DIFFERENT_PARENT"
        self.assertIn("TARGET_PARENT_RELATION_IDENTITY_MISMATCH", self.evaluate(c, p)["missing_reasons"])

    def test_weight_formula_preserves_official_reconciliation(self):
        c = "BWI-L.weight_change_reason_rate"
        p = fixture(c)
        self.assertAlmostEqual(self.evaluate(c, p)["observation_detail"]["article68_raw_delta_pct"], 100*2/450)
        p["target"]["current"]["official_delta_kg"] = 1
        self.assertIn("OFFICIAL_WEIGHT_DELTA_INCONSISTENT", self.evaluate(c, p)["missing_reasons"])

    def test_comment_specificity_is_quality_only(self):
        c = "CSI-L.cci_specificity"
        r = self.evaluate(c, fixture(c))
        self.assertEqual(r["intended_consumer"], "EVIDENCE_QUALITY_ONLY_NO_ABILITY_UPLIFT")

    def test_paddock_disagreement_and_same_observer_are_unknown(self):
        c = "BWI-L.paddock"
        p = fixture(c)
        p["target"]["current"]["grades"]["gait"] = [0, 2]
        self.assertIn("PADDOCK_OBSERVER_DISAGREEMENT", self.evaluate(c, p)["missing_reasons"])
        p = fixture(c)
        p["target"]["current"]["observer_ids"] = ["A", "A"]
        self.assertIn("TWO_INDEPENDENT_OBSERVERS_REQUIRED", self.evaluate(c, p)["missing_reasons"])

    def test_state_baselines_require_same_horse_prior_time_and_bound_source(self):
        for c in ("BWI-L.paddock", "BWI-L.age_growth", "BWI-L.transport_season"):
            with self.subTest(c=c):
                p = fixture(c)
                p["target"]["current"].pop("baseline_source_sha256")
                self.assertIsNone(self.evaluate(c, p)["score"])
                p = fixture(c)
                p["target"]["current"]["baseline_horse_id"] = "NAR:OTHER"
                self.assertIn("BASELINE_SAME_HORSE_IDENTITY_MISMATCH", self.evaluate(c, p)["missing_reasons"])
                p = fixture(c)
                p["target"]["current"]["baseline_event_at"] = p["target"]["current"]["event_at"]
                self.assertIn("BASELINE_NOT_PRIOR_TO_CURRENT_OBSERVATION", self.evaluate(c, p)["missing_reasons"])

    def test_twelve_month_and_active_status_are_independent_requirements(self):
        c = "JTI-L.stable_combo"
        p = fixture(c)
        p["target"]["jockey_active_verified"] = False
        self.assertIn("CURRENT_JOCKEY_OR_COMPLETE_TWELVE_MONTH_FRAME_UNVERIFIED", self.evaluate(c, p)["missing_reasons"])

    def test_profile_json_is_exact_code_specification(self):
        actual = json.loads((ROOT / "profiles/local_base15_research_candidates_v0.1_20261103.json").read_text())
        self.assertEqual(actual, m.research_specification())


if __name__ == "__main__":
    unittest.main()
