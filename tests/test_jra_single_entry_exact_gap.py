import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from jra_execution_maturity_bridge import prepare_production_numerical, JRAMaturityBridgeError


class ProductionPreparationTest(unittest.TestCase):
    def setUp(self):
        self.intent = {"family_id":"JRA", "race_id":"GAP-TEST", "venue_id":"HSN",
                       "race_date":"2099-01-01", "race_no":1,
                       "prediction_cutoff":"2099-01-01T10:00:00+09:00",
                       "scheduled_post_at":"2099-01-01T10:15:00+09:00"}
        self.env = {"receipt_sha256":"a"*64,
                    "receipt":{"runtime_revision":"SOURCE-TEST"},
                    "artifact":{"family_id":"JRA", "race_id":"GAP-TEST",
                                "prediction_cutoff":self.intent["prediction_cutoff"],
                                "source_freeze_at":"2099-01-01T00:55:00Z",
                                "source_snapshot_sha256":"b"*64,
                                "jra_official_runner_universe":{"runners":[
                                    {"runner_id":"1", "name":"A", "assigned_weight":56},
                                    {"runner_id":"2", "name":"B", "assigned_weight":56}]},
                                "jra_official_race_card_detail":{"runners":[
                                    {"runner_id":"1", "career_record":{"starts":8}},
                                    {"runner_id":"2", "career_record":{"starts":8}},
                                    {"runner_id":"99", "career_record":{"starts":8}}]}}}

    def test_exact_gaps_no_shadow_neutralization_or_extra_runner(self):
        before = copy.deepcopy(self.env)
        report = prepare_production_numerical(self.intent, self.env)
        self.assertEqual(self.env, before)
        self.assertEqual(report["runner_universe"], ["1", "2"])
        self.assertFalse(report["production_full_numerical_ready"])
        self.assertIsNone(report["prepared_numerical_request"])
        self.assertFalse(report["candidate_numerics_used"])
        self.assertEqual(report["first_blocked_stage"], "PRODUCTION_FEATURE_INDEX_CLOSURE")
        for rid, row in report["source_feature_report"]["runners"].items():
            self.assertEqual(len(row["source_feature_trace"]["features"]), 71)
            self.assertIn(rid, {"1", "2"})
        self.assertTrue(report["exact_gaps"])
        self.assertFalse(report["source_only_full_numerical_ready"])
        self.assertEqual(report["numerical_closure_mode"], "BLOCKED")
        self.assertEqual(report["required_index_count"], 40)
        self.assertEqual(report["verified_full_index_count"], 0)
        plan = report["source_only_coverage_repair_plan"]
        self.assertEqual(plan["blocked_index_count"], report["base_index_coverage_diagnostic"]["blocked"])
        self.assertFalse(plan["production_authority_granted"])
        self.assertEqual(plan["static_owner_independent_blocker"],
                         "NO_AUTHORIZED_SOURCE_ONLY_STATIC_RANK_ROLE_DECISION_RULE_CONNECTED")
        for row in plan["conditional_repair_rows"]:
            self.assertFalse(row["closure_proven"])
            self.assertTrue(row["authorized_evaluators_required"])
            for needed in row["conditional_repair_features"]:
                self.assertIn(needed["fact_available"], (True, False, None))
                self.assertTrue(needed["feature"])
        coverage = report["base_index_coverage_diagnostic"]
        self.assertEqual(coverage["required"], 26)
        self.assertTrue(coverage["blocked"] > 0)
        self.assertFalse(coverage["all_base_index_coverage_met"])
        self.assertTrue(coverage["no_missing_value_imputation"])
        self.assertTrue(all(row["index_id"] and row["runner_id"] for row in coverage["rows"]))
        for gap in report["exact_gaps"]:
            self.assertIn("index_binding", gap)
            self.assertIn("missing_reason", gap)
            self.assertIsNone(gap["production_evaluator_available"])

    def test_duplicate_official_universe_rejected(self):
        self.env["artifact"]["jra_official_runner_universe"]["runners"].append({"runner_id":"1"})
        with self.assertRaisesRegex(JRAMaturityBridgeError, "OFFICIAL_UNIVERSE_INVALID"):
            prepare_production_numerical(self.intent, self.env)

    def test_source_substitution_rejected(self):
        self.env["artifact"]["race_id"] = "OTHER"
        with self.assertRaisesRegex(JRAMaturityBridgeError, "SOURCE_IDENTITY_MISMATCH"):
            prepare_production_numerical(self.intent, self.env)

    def supplemental(self):
        registry = json.loads((ROOT/"mapping/jra_evidence_feature_rule_registry_v1.1_20260922.json").read_text())
        features = {rid:{name:{"category":"NEUTRAL", "rule_id":rules[0],
                             "evidence_refs":["SUPP:TEST:"+rid+":"+name],
                             "source_fact":"Synthetic mechanical test only", "result_derived":False}
                       for name,rules in registry["feature_rules"].items()} for rid in ("1", "2")}
        pack = {"profile":"KM-JRA-SUPPLEMENTAL-EVIDENCE-PACK-v1.0-20260926",
                "family_id":"JRA", "race_id":self.intent["race_id"],
                "captured_at":"2099-01-01T09:50:00+09:00", "runner_features":features,
                "sources":[{"source_id":"TEST", "source_class":"SYNTHETIC_ACCEPTANCE_ONLY",
                            "authority":"MECHANICAL_TEST", "origin":"repo:mechanical-test",
                            "available_at":"2099-01-01T09:40:00+09:00",
                            "ingested_at":"2099-01-01T09:45:00+09:00",
                            "content_sha256":"c"*64, "production_use":"FACT_ONLY", "result_derived":False}]}
        pack["pack_sha256"] = hashlib.sha256(json.dumps(pack,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        return pack

    def test_existing_supplemental_closes_numerics_not_static_policy(self):
        self.intent["acceptance_only"] = True
        self.intent["supplemental_evidence_pack"] = self.supplemental()
        report = prepare_production_numerical(self.intent, self.env)
        self.assertTrue(report["production_full_numerical_ready"])
        # Acceptance-only supplemental numerics cannot pass the source-only gate.
        self.assertFalse(report["source_only_full_numerical_ready"])
        self.assertEqual(report["numerical_closure_mode"], "WITH_SUPPLEMENTAL_EVIDENCE")
        self.assertEqual(report["required_index_count"], 40)
        self.assertEqual(report["verified_full_index_count"], 40)
        owner = report["static_owner_candidate_diagnostic"]
        self.assertIsNone(report["static_owner_candidate_error"])
        self.assertIsNotNone(owner)
        self.assertTrue(owner["production_index_inputs_validated"])
        self.assertFalse(owner["static_prediction_production_authority"])
        self.assertFalse(owner["signed_static_freeze_verified"])
        self.assertEqual(len(owner["ranking"]), 2)
        coverage = report["base_index_coverage_diagnostic"]
        self.assertEqual(coverage["required"], 26)
        self.assertEqual(coverage["blocked"], 0)
        self.assertTrue(coverage["all_base_index_coverage_met"])
        self.assertFalse(report["static_generation_ready"])
        self.assertEqual(report["first_blocked_stage"], "PRODUCTION_STATIC_PREDICTION_OWNER")
        self.assertEqual(report["exact_gaps"], [])
        for r in report["prepared_numerical_request"]["runners"]:
            self.assertEqual(len(r["canonical_components"]), 20)
        self.assertNotIn("static_prediction", report["prepared_numerical_request"])

    def test_feature_authority_firewall_rejects_candidate_shadow_and_result_facts(self):
        from jra_evidence_to_base_production import load_mapping, build_production_ledger, ProductionMappingError
        self.intent["acceptance_only"] = True
        self.intent["supplemental_evidence_pack"] = self.supplemental()
        report = prepare_production_numerical(self.intent, self.env)
        self.assertTrue(report["production_full_numerical_ready"])
        mapping = load_mapping(str(ROOT/"mapping/jra_base_index_evidence_mapping_v1.0_20260921.json"))
        from copy import deepcopy
        base = report["prepared_numerical_request"]["runners"]
        for marker in (
            {"candidate_only": True},
            {"production_authority": False},
            {"result_derived": True},
            {"source_authority": "THIRD_PARTY_PUBLIC_SHADOW"},
        ):
            with self.subTest(marker=marker):
                rows = deepcopy(base)
                rows[0]["evidence_features"]["recent_performance"].update(marker)
                with self.assertRaises(ProductionMappingError):
                    build_production_ledger(self.intent["race_id"],rows,mapping)

    def test_synthetic_supplemental_never_enters_production(self):
        self.intent["supplemental_evidence_pack"] = self.supplemental()
        with self.assertRaisesRegex(ValueError, "SYNTHETIC_SOURCE_FORBIDDEN"):
            prepare_production_numerical(self.intent, self.env)

    def test_cli_persists_gap_before_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d/"intent.json").write_text(json.dumps(self.intent))
            (d/"source.json").write_text(json.dumps(self.env))
            proc = subprocess.run([sys.executable, str(ROOT/"runtime/jra_execution_maturity_bridge.py"),
                                   "build-formal", "--intent", str(d/"intent.json"),
                                   "--source-envelope", str(d/"source.json"),
                                   "--output", str(d/"formal.json")], cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse((d/"formal.json").exists())
            report = json.loads((d/"formal.json.exact-gap.json").read_text())
            self.assertTrue(report["exact_gaps"])
            self.assertIn("PRODUCTION_FEATURE_INDEX_CLOSURE", proc.stderr)


if __name__ == "__main__":
    unittest.main()
