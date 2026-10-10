"""JRA Production official feature extraction must be source- and time-bound."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

from jra_official_fact_evaluator_production import official_production_observations
from jra_source_to_evidence_features import compile_source_to_features
from jra_evidence_to_base_production import load_mapping


def source():
    histories = [
        {"date": "2026-09-10", "finish": 1, "field_size": 10, "venue": "東京", "distance_m": 1800, "surface": "芝", "going": "良", "rating": 94},
        {"date": "2026-09-01", "finish": 3, "field_size": 12, "venue": "東京", "distance_m": 1800, "surface": "芝", "going": "良", "rating": 90},
        {"date": "2026-10-10", "finish": 1, "field_size": 12, "venue": "東京", "distance_m": 1800, "surface": "芝", "going": "良"},
    ]
    return {
        "family_id": "JRA",
        "race_id": "KM-JRA-TKY-20261010-R05",
        "source_snapshot_sha256": "a"*64,
        "source_freeze_at": "2026-10-10T12:08:42+09:00",
        "prediction_cutoff": "2026-10-10T12:18:00+09:00",
        "source_race_context": {"race_date": "2026-10-10"},
        "jra_race_context": {"venue_name": "東京", "distance_m": 1800, "surface": "芝", "going": "良"},
        "jra_official_runner_universe": {"runners": [
            {"runner_id": "1", "name": "A", "status": "ACTIVE", "assigned_weight": 56},
            {"runner_id": "2", "name": "B", "status": "ACTIVE", "assigned_weight": 56},
        ]},
        "jra_official_race_card_detail": {"runners": [
            {"runner_id": "1", "career_record": {"starts": 2}},
            {"runner_id": "2", "career_record": {"starts": 0}},
        ]},
        "jra_official_horse_history": {"runners": {
            "1": {"runs": histories},
            "2": {"runs": []},
        }},
        "jra_official_person_stats": {"runners": {
            "1": {
                "jockey_matched": True,
                "jockey": {"current_year_flat": {"starts": 125, "wins": 22, "win_rate": 17.6}},
                "trainer_matched": True,
                "trainer": {"current_year_flat": {"starts": 50, "wins": 9, "win_rate": 18.0}},
            },
            "2": {
                "jockey_matched": False,
                "jockey": {"current_year_flat": {"starts": 200, "win_rate": 35}},
                "trainer_matched": True,
                "trainer": {"current_year_flat": {"starts": 9, "win_rate": 22}},
            },
        }},
    }


class TestOfficialProductionEvaluator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((ROOT / "mapping/jra_evidence_feature_rule_registry_v1.1_20260922.json").read_text(encoding="utf-8"))
        cls.mapping = load_mapping(ROOT / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")

    def test_observed_history_and_person_go_to_production_not_current_result(self):
        out = official_production_observations(source(), self.registry)
        x = out["1"]
        self.assertEqual(x["recent_performance"]["observation_count"], 2)
        self.assertEqual(x["recent_consistency"]["observation_count"], 2)
        self.assertEqual(x["same_course_fit"]["observation_count"], 2)
        self.assertEqual(x["jockey_quality"]["observation_count"], 125)
        self.assertEqual(x["trainer_quality"]["observation_count"], 50)
        self.assertTrue(all(y["production_authority"] for y in x.values()))
        self.assertTrue(all(y["source_authority"] == "JRA_OFFICIAL" for y in x.values()))
        self.assertNotIn("recent_performance", out["2"])
        self.assertNotIn("jockey_quality", out["2"])

    def test_compiler_uses_existing_mapping_and_never_fake_fills_newcomer(self):
        src = source()
        runners = [{"runner_id": "1", "name": "A", "career_starts": 2},
                   {"runner_id": "2", "name": "B", "newcomer": True}]
        report = compile_source_to_features(src, runners, self.mapping)
        generated = report["runners"]["1"]["generated_production_features"]
        self.assertIn("recent_performance", generated)
        self.assertIn("jockey_quality", generated)
        self.assertNotIn("recent_performance", report["runners"]["2"]["generated_production_features"])
        self.assertFalse(report["source_only_formal_base_ready"])

    def test_poststart_and_same_race_observations_never_create_features(self):
        src = source()
        src["jra_official_horse_history"]["runners"]["1"]["runs"] = src["jra_official_horse_history"]["runners"]["1"]["runs"][2:]
        x = official_production_observations(src, self.registry)
        self.assertNotIn("recent_performance", x["1"])
        src = source()
        src["source_freeze_at"] = "2026-10-10T12:35:00+09:00"
        self.assertEqual(official_production_observations(src, self.registry), {})

    def test_real_jra_percentage_under_one_is_not_fraction(self):
        src = source()
        stats = src["jra_official_person_stats"]["runners"]["1"]["jockey"]["current_year_flat"]
        stats.update(starts=1000, wins=8, win_rate=0.8)
        result = official_production_observations(src, self.registry)
        self.assertEqual(result["1"]["jockey_quality"]["category"], "WEAK")
        self.assertIn("ratio=0.008000", result["1"]["jockey_quality"]["source_fact"])
        # A forged percentage inconsistent with wins/starts must be discarded.
        stats["win_rate"] = 18.0
        self.assertNotIn("jockey_quality", official_production_observations(src, self.registry)["1"])

    def test_recent_speed_uses_registered_actual_history_rt_and_peer_group(self):
        src = source()
        original = src["jra_official_horse_history"]["runners"]["1"]["runs"]
        active = src["jra_official_runner_universe"]["runners"]
        details = src["jra_official_race_card_detail"]["runners"]
        for rid, mean_rt in (("3", 65), ("4", 80), ("5", 110)):
            active.append({"runner_id": rid, "status": "ACTIVE"})
            details.append({"runner_id": rid, "career_record": {"starts": 2}})
            src["jra_official_horse_history"]["runners"][rid] = {
                "runs": [{**original[0], "rating": mean_rt},
                         {**original[1], "rating": mean_rt}]
            }
        # Horse 2 is a true newcomer; only four independently observed peers.
        got = official_production_observations(src, self.registry)
        self.assertEqual(got["1"]["recent_speed"]["rule_id"],
                         "JRA-EVIDENCE-PERCENTILE-RECENT-SPEED-v1")
        self.assertEqual(got["1"]["recent_speed"]["observation_count"], 2)
        self.assertNotIn("recent_speed", got["2"])
        self.assertNotIn("2026-10-10", got["1"]["recent_speed"]["source_fact"])
        src["jra_official_horse_history"]["runners"]["5"]["runs"] = []
        self.assertNotIn("recent_speed", official_production_observations(src, self.registry)["1"])

    def test_official_rotation_and_bodyweight_from_actual_prior_runs(self):
        src=source()
        row=src["jra_official_race_card_detail"]["runners"][0]
        row["current_body_weight"]=500
        runs=src["jra_official_horse_history"]["runners"]["1"]["runs"]
        runs[0]["body_weight"]=498
        runs[1]["body_weight"]=494
        out=official_production_observations(src,self.registry)["1"]
        self.assertEqual(out["rotation_fit"]["rule_id"],"KM-JRA-ROTATION-FIT-v1")
        self.assertIn("days_to_target_race=30",out["rotation_fit"]["source_fact"])
        self.assertEqual(out["rotation_fit"]["category"],"STRONG")
        self.assertEqual(out["bodyweight_range_fit"]["category"],"STRONG")
        self.assertEqual(out["bodyweight_range_fit"]["observation_count"],2)
        self.assertIn("signed_delta=+4.0 kg",out["bodyweight_range_fit"]["source_fact"])
        src["jra_official_horse_history"]["runners"]["1"]["runs"][1].pop("body_weight")
        out=official_production_observations(src,self.registry)["1"]
        self.assertNotIn("bodyweight_range_fit",out)
        self.assertIn("rotation_fit",out)

    def test_no_phantom_rotation_for_debut_or_future_only(self):
        src=source()
        out=official_production_observations(src,self.registry)
        self.assertNotIn("rotation_fit",out["2"])
        src["jra_official_horse_history"]["runners"]["1"]["runs"]=[
            src["jra_official_horse_history"]["runners"]["1"]["runs"][2]
        ]
        self.assertNotIn("rotation_fit",official_production_observations(src,self.registry)["1"])

    def test_registry_identity_and_ambiguous_person_rate_fail_closed(self):
        src = source()
        src["jra_official_person_stats"]["runners"]["1"]["jockey"]["current_year_flat"]["win_rate"] = 1.0
        result = official_production_observations(src, self.registry)
        self.assertNotIn("jockey_quality", result["1"])
        bad = copy.deepcopy(self.registry)
        bad["feature_rules"]["recent_performance"] = []
        with self.assertRaisesRegex(ValueError, "RULE_NOT_REGISTERED"):
            official_production_observations(src, bad)


if __name__ == "__main__":
    unittest.main()
