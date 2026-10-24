"""Isolated synthetic model regressions; no fixture is Production evidence."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from jra_bvi_env_shadow import (PROTOCOL_SHA256, _eligible_rows, evaluate_chronological,
                                predict, prediction_input_sha, sha, train_model, verify_model)


def dataset():
    rows = []
    training_dates = ("2026-01-03", "2026-03-03", "2026-05-03", "2026-06-03", "2026-06-23", "2026-07-03")
    for i in range(8):
        for j, day in enumerate(training_dates + ("2026-08-04", "2026-09-04", "2026-10-04")):
            dirt = j % 2 == 1
            rows.append({"horse_id": "composite-" + str(i), "sire": "父A" if i < 4 else "父B",
                         "dam": "母" + str(i), "damsire": "母父A" if i < 4 else "母父B",
                         "date": day, "venue": "東京" if dirt else "京都", "surface": "ダ" if dirt else "芝",
                         "distance_m": 1800 if dirt else 1600, "going": "重" if dirt else "良",
                         "race_name": "2勝クラス", "finish": 2 if (i < 4) != dirt else 9,
                         "field_size": 12, "body_weight": 480, "available_at": "2026-10-24T10:00:00Z",
                         "race_identity_status": "COMPOSITE_NOT_OFFICIAL_RACE_ID", "official_race_id": None,
                         "provenance": []})
    return {"prediction_cutoff": "2026-10-24T15:00:00Z", "race_date": "2026-10-25",
            "manifest_sha256": "a" * 64, "rows": rows}


def runner():
    return {"runner_id": "3", "horse_id": "new-composite", "horse_name": "検証馬",
            "sire": "父A", "dam": "母新", "damsire": "母父A", "runs": []}


def environment():
    return {"race_date": "2026-10-25", "prediction_cutoff": "2026-10-25T00:00:00Z",
            "venue": "京都", "surface": "芝", "distance_m": 1600, "going": "良",
            "race_name": "2勝クラス", "field_size": 12}


class ModelResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = dataset()
        cls.model = train_model(cls.data, train_before="2026-08-01")

    def test_fixed_label_split_does_not_require_acquisition_before_past_label_date(self):
        m = self.model
        self.assertEqual(m["training_runs"], 48)
        self.assertEqual(m["training_composite_offspring"], 8)
        self.assertEqual(m["training_total_horse_weight"], 8)
        self.assertEqual(m["training_label_max"], "2026-07-03")
        self.assertEqual(m["maximum_training_acquisition_at"], "2026-10-24T10:00:00Z")
        self.assertFalse(m["historical_forward_oos_eligible"])
        self.assertFalse(m["model_training_eligibility"])
        self.assertFalse(m["production_authority"])

    def test_determinism_and_json_round_trip(self):
        again = train_model(self.data, train_before="2026-08-01")
        self.assertEqual(self.model, again)
        self.assertTrue(verify_model(json.loads(json.dumps(again))))
        shuffled = copy.deepcopy(self.data)
        shuffled["rows"].reverse()
        other = train_model(shuffled, train_before="2026-08-01")
        self.assertEqual(again["stage_models"], other["stage_models"])
        self.assertEqual(again["training_rows_sha256"], other["training_rows_sha256"])

    def test_actual_capture_cutoff_enforced(self):
        bad = copy.deepcopy(self.data)
        bad["rows"][0]["available_at"] = "2026-10-25T01:00:00Z"
        with self.assertRaisesRegex(ValueError, "POST_CUTOFF_ACQUISITION"):
            train_model(bad, train_before="2026-08-01")

    def test_provenance_quarantined_labels_excluded_from_research_fit(self):
        bad = copy.deepcopy(self.data)
        bad["rows"][0]["research_label_eligible"] = False
        model = train_model(bad, train_before="2026-08-01")
        self.assertEqual(model["training_runs"], 47)
        self.assertEqual(model["excluded_rows"]["RESEARCH_LABEL_PROVENANCE_QUARANTINED"], 1)

    def test_future_labels_rejected(self):
        bad = copy.deepcopy(self.data)
        bad["rows"][0]["date"] = "2026-10-25"
        with self.assertRaisesRegex(ValueError, "TARGET_OR_FUTURE_LABEL"):
            train_model(bad, train_before="2026-08-01")

    def test_no_naive_datetimes(self):
        bad = copy.deepcopy(self.data)
        bad["prediction_cutoff"] = "2026-10-24T15:00:00"
        with self.assertRaisesRegex(ValueError, "ACQUISITION_TIME_INVALID"):
            train_model(bad, train_before="2026-08-01")

    def test_duplicate_run_not_new_offspring(self):
        dup = copy.deepcopy(self.data)
        dup["rows"] += copy.deepcopy(dup["rows"])
        model = train_model(dup, train_before="2026-08-01")
        self.assertEqual(model["training_runs"], 48)
        self.assertEqual(model["training_composite_offspring"], 8)
        self.assertEqual(model["stage_models"], self.model["stage_models"])

    def test_one_repeated_horse_cannot_meet_offspring_threshold(self):
        one = copy.deepcopy(self.data)
        one["rows"] = [r for r in one["rows"] if r["horse_id"] == "composite-0"]
        model = train_model(one, train_before="2026-08-01")
        result = predict(model, runner(), environment())
        self.assertFalse(result["usable_for_shadow_override"])
        self.assertIsNone(result["score"])
        self.assertEqual(model["stage_models"]["GENERAL"]["terms"], [])
        self.assertEqual(model["training_total_horse_weight"], 1)

    def test_conflicting_duplicate_label_quarantined(self):
        bad = copy.deepcopy(self.data)
        row = copy.deepcopy(bad["rows"][0]); row["finish"] = 12
        bad["rows"].append(row)
        model = train_model(bad, train_before="2026-08-01")
        self.assertEqual(model["training_runs"], 47)
        self.assertEqual(model["excluded_rows"]["CONFLICTING_DUPLICATE_KEY"], 1)

    def test_duplicate_going_conflict_cannot_be_restored_by_third_copy(self):
        bad = copy.deepcopy(self.data)
        first = copy.deepcopy(bad["rows"][0]); second = copy.deepcopy(first)
        second["going"] = "重"
        bad["rows"] = [first, second, copy.deepcopy(first)]
        rows, exclusions = _eligible_rows(bad)
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0]["going"])
        self.assertEqual(exclusions["CONFLICTING_DUPLICATE_GOING"], 1)

    def test_same_day_results_do_not_update_ability(self):
        same = copy.deepcopy(self.data)
        first = copy.deepcopy(same["rows"][0]); second = copy.deepcopy(first)
        second["venue"] = "中京"; second["finish"] = 12
        same["rows"] = [first, second]
        rows, _ = _eligible_rows(same)
        self.assertEqual([r["prior_ability"] for r in rows], [0.5, 0.5])
        self.assertEqual([r["prior_ability_runs"] for r in rows], [0, 0])

    def test_model_tamper_and_authority_rejected(self):
        for field, value in (("residual_rms", 0), ("production_authority", True), ("protocol_sha256", "x")):
            bad = copy.deepcopy(self.model); bad[field] = value
            with self.assertRaises(ValueError):
                predict(bad, runner(), environment())

    def test_score_components_and_uncertainty_are_research_only(self):
        result = predict(self.model, runner(), environment())
        self.assertTrue(result["usable_for_shadow_override"])
        self.assertTrue(0 <= result["score"] <= 100)
        self.assertLessEqual(result["uncertainty"]["lower"], result["score"])
        self.assertGreaterEqual(result["uncertainty"]["upper"], result["score"])
        self.assertFalse(result["uncertainty"]["calibrated"])
        self.assertGreater(result["counts"]["matched_environment_terms"], 0)
        self.assertEqual(result["protocol_sha256"], PROTOCOL_SHA256)
        self.assertEqual(result["input_sha256"], prediction_input_sha(runner(), environment()))
        self.assertFalse(result["production_authority"])
        self.assertFalse(result["predictive_improvement_demonstrated"])
        self.assertTrue(result["solver_converged"])

    def test_unconverged_fit_declines_shadow_override(self):
        model = copy.deepcopy(self.model)
        model["stage_models"]["CONTROL"]["converged"] = False
        model["solver_converged"] = False
        model["model_sha256"] = sha({k: v for k, v in model.items() if k != "model_sha256"})
        result = predict(model, runner(), environment())
        self.assertFalse(result["usable_for_shadow_override"])
        self.assertIsNone(result["score"])
        self.assertFalse(result["solver_converged"])
        self.assertIn("NUMERICAL_SOLVER_NOT_CONVERGED; NO_ENVIRONMENT_OVERRIDE", result["reasons"])

    def test_false_convergence_summary_cannot_override_stage_failure(self):
        model = copy.deepcopy(self.model)
        model["stage_models"]["CONTROL"]["converged"] = False
        model["model_sha256"] = sha({k: v for k, v in model.items() if k != "model_sha256"})
        result = predict(model, runner(), environment())
        self.assertFalse(result["usable_for_shadow_override"])
        self.assertFalse(result["solver_converged"])

    def test_never_fill_missing_parents_with_invented_bloodline(self):
        horse = runner(); horse["sire"] = None
        result = predict(self.model, horse, environment())
        self.assertFalse(result["usable_for_shadow_override"])
        self.assertIsNone(result["score"])

    def test_weather_does_not_infer_going(self):
        env = environment(); env["going"] = None; env["weather"] = "雨"
        result = predict(self.model, runner(), env)
        self.assertIn("going", result["missing_environment"])
        self.assertFalse(any(c["factor"].endswith("_going") for c in result["components"]))
        self.assertFalse(any(c["factor"] == "weather" for c in result["components"]))

    def test_unsupported_context_not_extrapolated(self):
        env = environment(); env["venue"] = "非公式場"
        self.assertFalse(predict(self.model, runner(), env)["usable_for_shadow_override"])

    def test_parent_environment_override_cannot_change_runner_identity(self):
        env = environment(); env["sire"] = "父B"
        result = predict(self.model, runner(), env)
        terms = [json.loads(c["term"]) for c in result["components"] if c["factor"] == "sire"]
        self.assertEqual(terms, [["sire", "父A"]])

    def test_prediction_rejects_training_containing_target_label(self):
        env = environment(); env["race_date"] = "2026-07-03"
        with self.assertRaisesRegex(ValueError, "CONTAINS_TARGET_OR_FUTURE_LABEL"):
            predict(self.model, runner(), env)

    def test_prediction_rejects_capture_after_target_cutoff(self):
        env = environment(); env["prediction_cutoff"] = "2026-10-24T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "MODEL_DATA_POST_TARGET_CUTOFF"):
            predict(self.model, runner(), env)

    def test_runner_future_history_not_used_in_current_ability(self):
        horse = runner(); horse["runs"] = [{"date": "2026-10-26", "finish": 1, "field_size": 12}]
        a = predict(self.model, horse, environment())
        b = predict(self.model, runner(), environment())
        self.assertEqual(a["score"], b["score"])

    def test_historical_partitions_do_not_refit_or_claim_forward_oos(self):
        report = evaluate_chronological(self.data)
        self.assertEqual(report["forward_oos_increment"], 0)
        self.assertFalse(report["hyperparameters_optimized"])
        self.assertFalse(report["coefficients_refitted_on_validation_or_test"])
        self.assertEqual(report["partitions"]["VALIDATION"]["label_count"], 8)
        self.assertEqual(report["partitions"]["TEST"]["label_count"], 16)
        self.assertTrue(report["partitions"]["TEST"]["groups"])
        for split in report["partitions"].values():
            self.assertIn("GENERAL_PEDIGREE", split["errors"])
            self.assertIn("ENV_PEDIGREE", split["errors"])
            self.assertIn("NOT_MEASURED", split["ticket_pfs"])

    def test_invalid_split_rejected(self):
        with self.assertRaisesRegex(ValueError, "SPLIT_BOUNDARIES_INVALID"):
            evaluate_chronological(self.data, train_before="2026-09-01", validation_before="2026-08-01")

    def test_shrinkage_suppresses_extreme_low_support(self):
        # Three runs from each of four horses is only the minimum; an extreme
        # condition cannot become an unregularized perfect-performance claim.
        small = copy.deepcopy(self.data)
        small["rows"] = [r for r in small["rows"] if r["sire"] == "父A" and r["surface"] == "芝"]
        for row in small["rows"]: row["finish"] = 1
        model = train_model(small, train_before="2026-08-01")
        environment_terms = model["stage_models"]["ENVIRONMENT"]["terms"]
        self.assertTrue(environment_terms)
        self.assertTrue(all(abs(t["coefficient"]) < 0.05 for t in environment_terms))


if __name__ == "__main__":
    unittest.main()
