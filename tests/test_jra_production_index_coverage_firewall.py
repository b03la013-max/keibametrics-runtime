"""Production index coverage cannot treat unapproved facts as available."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

from jra_evidence_to_base_production import load_mapping, ProductionMappingError
from jra_execution_maturity_bridge import _production_index_coverage_diagnostic

MAPPING_PATH = ROOT / "mapping" / "jra_base_index_evidence_mapping_v1.0_20260921.json"


def feature(name: str) -> dict:
    return {
        "category": "STRONG",
        "rule_id": f"JRA-OFFICIAL-TEST-{name}-v1",
        "evidence_refs": [f"JRA:SIGNED:PRE-RACE:{name}"],
        "source_fact": f"Official observed pre-race {name}",
        "source_authority": "JRA_OFFICIAL",
    }


class ProductionCoverageFirewallTest(unittest.TestCase):
    def setUp(self):
        self.mapping = load_mapping(MAPPING_PATH)
        self.runner = {
            "runner_id": "1",
            "career_starts": 0,
            # Newcomer HPI: 0.28 + 0.18 = 0.46 >= 0.34.
            "evidence_features": {
                "workout_capability": feature("workout_capability"),
                "pedigree_class": feature("pedigree_class"),
            },
        }

    def hpi(self, runner):
        return next(x for x in _production_index_coverage_diagnostic([runner], self.mapping)["rows"]
                    if x["index_id"] == "HPI")

    def test_real_production_authorized_evidence_can_close_coverage(self):
        row = self.hpi(self.runner)
        self.assertEqual(row["status"], "COVERAGE_THRESHOLD_MET")
        self.assertAlmostEqual(row["coverage_weight"], .46)

    def test_nonproduction_and_postresult_evidence_never_count(self):
        variants = (
            {"candidate_only": True},
            {"production_authority": False},
            {"result_derived": True},
            {"source_authority": "THIRD_PARTY_PUBLIC_SHADOW"},
            {"source_authority": "TSL_NON_PRODUCTION"},
            {"category": "FABRICATED_CATEGORY"},
            {"evidence_refs": []},
            {"source_fact": ""},
            {"rule_id": ""},
        )
        for variant in variants:
            with self.subTest(variant=variant):
                bad = deepcopy(self.runner)
                bad["evidence_features"]["workout_capability"].update(variant)
                row = self.hpi(bad)
                self.assertEqual(row["status"], "BLOCKED")
                self.assertAlmostEqual(row["coverage_weight"], .18)
                missed = next(x for x in row["missing_features"] if x["feature"] == "workout_capability")
                self.assertTrue(missed["validation_reason"])

    def test_absent_evidence_is_not_a_neutral_score(self):
        bad = deepcopy(self.runner)
        del bad["evidence_features"]["workout_capability"]
        row = self.hpi(bad)
        self.assertEqual(row["status"], "BLOCKED")
        self.assertAlmostEqual(row["coverage_weight"], .18)
        self.assertNotIn("workout_capability", row["available_features"])

    def test_runner_coverage_cannot_invent_production_owner(self):
        report = _production_index_coverage_diagnostic([self.runner], self.mapping)
        self.assertEqual(report["authority"], "DIAGNOSTIC_ONLY / PRODUCTION_MAPPING_UNCHANGED")
        self.assertTrue(report["no_missing_value_imputation"])


if __name__ == "__main__":
    unittest.main()
