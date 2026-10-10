"""Regression for Tokyo 2026-10-10 R05 (20k requested, SIM-STD ran 5k)."""
from __future__ import annotations

import copy
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runtime"))
from jra_candidate_krs_plan import (
    CandidateKRSConformanceError,
    ENGINE_SHA256,
    INPUT_CLASS,
    build_candidate_krs_payload,
    verify_candidate_krs_execution,
)


def request(count=20000):
    return {
        "family_id": "JRA",
        "race_id": "KM-JRA-TKY-20261010-R05",
        "run_count": count,
        "seed": 2027011005,
        "krs_input_data": {"simulation": {"run_count": 5000, "master_seed": 1},
                           "horse_parameters": [{"runner_id": "1"}]},
    }


def executed(payload):
    count = payload["input_data"]["simulation"]["run_count"]
    return {"run_receipt": {"receipt": {
        "schema": "KM-KRS-RUN-RECEIPT-v1",
        "race_id": payload["race_id"],
        "status": "EXECUTED",
        "engine_sha256": ENGINE_SHA256,
        "mode": payload["mode"],
        "requested_run_count": count,
        "actual_run_count": count,
        "seed": payload["seed"],
        "input_class": INPUT_CLASS,
        "input_sha256": "a" * 64,
        "output_sha256": "b" * 64,
    }}}


class CandidateKRSConformanceTest(unittest.TestCase):
    def test_high_20k_chooses_sim_high_and_preserves_original(self):
        original = request()
        frozen = copy.deepcopy(original)
        payload = build_candidate_krs_payload(original)
        self.assertEqual(payload["mode"], "SIM-HIGH")
        self.assertEqual(payload["input_data"]["simulation"],
                         {"run_count": 20000, "master_seed": original["seed"]})
        self.assertEqual(original, frozen)
        self.assertEqual(verify_candidate_krs_execution(payload, executed(payload))
                         ["actual_run_count"], 20000)

    def test_std_5k_chooses_sim_std(self):
        payload = build_candidate_krs_payload(request(5000))
        self.assertEqual(payload["mode"], "SIM-STD")
        self.assertEqual(verify_candidate_krs_execution(payload, executed(payload))
                         ["actual_run_count"], 5000)

    def test_non_executable_counts_fail_before_external_call(self):
        for count in (None, 0, 4999, 6000, 19999, 20001, True, "20000"):
            with self.subTest(count=count):
                with self.assertRaisesRegex(CandidateKRSConformanceError,
                                            "KRS_RUN_COUNT_UNSUPPORTED_BY_RUNTIME"):
                    build_candidate_krs_payload(request(count))

    def test_invalid_family_or_seed_or_missing_simulation_rejected(self):
        bad = request()
        bad["family_id"] = "LOCAL"
        with self.assertRaisesRegex(CandidateKRSConformanceError, "JRA_ONLY"):
            build_candidate_krs_payload(bad)
        bad = request()
        bad["seed"] = None
        with self.assertRaisesRegex(CandidateKRSConformanceError, "KRS_SEED_INVALID"):
            build_candidate_krs_payload(bad)
        bad = request()
        del bad["krs_input_data"]["simulation"]
        with self.assertRaisesRegex(CandidateKRSConformanceError,
                                    "KRS_SIMULATION_INPUT_MISSING"):
            build_candidate_krs_payload(bad)

    def test_tokyo_r05_old_sim_std_receipt_is_rejected(self):
        payload = build_candidate_krs_payload(request())
        old = executed(payload)
        rr = old["run_receipt"]["receipt"]
        rr.update(mode="SIM-STD", requested_run_count=5000, actual_run_count=5000)
        with self.assertRaisesRegex(CandidateKRSConformanceError, "KRS_RECEIPT_MODE_MISMATCH"):
            verify_candidate_krs_execution(payload, old)

    def test_mismatched_seed_count_engine_and_input_class_are_rejected(self):
        payload = build_candidate_krs_payload(request())
        for field, value in (
            ("seed", 2026101005),
            ("actual_run_count", 5000),
            ("requested_run_count", 5000),
            ("engine_sha256", "wrong"),
            ("input_class", "PRODUCTION"),
            ("race_id", "OTHER_RACE"),
        ):
            with self.subTest(field=field):
                result = executed(payload)
                result["run_receipt"]["receipt"][field] = value
                with self.assertRaises(CandidateKRSConformanceError):
                    verify_candidate_krs_execution(payload, result)

    def test_missing_or_unsigned_execution_cannot_advance(self):
        payload = build_candidate_krs_payload(request())
        for response in ({}, {"run_receipt": {}}, {"run_receipt": {"receipt": {"status": "FAIL"}}}):
            with self.subTest(response=response):
                with self.assertRaises(CandidateKRSConformanceError):
                    verify_candidate_krs_execution(payload, response)
        result = executed(payload)
        result["run_receipt"]["receipt"].pop("output_sha256")
        with self.assertRaisesRegex(CandidateKRSConformanceError, "KRS_OUTPUT_SHA_MISSING"):
            verify_candidate_krs_execution(payload, result)


if __name__ == "__main__":
    unittest.main()
