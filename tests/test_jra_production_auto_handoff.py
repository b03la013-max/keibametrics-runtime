"""Mechanics for JRA Production Full20 -> Static -> PRE_KRS cannot self-authorize."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

from jra_production_auto_handoff import (
    JRAProductionAutoHandoffError,
    compile_production_auto_handoff,
)
from jra_static_owner_executable import compile_static_owner, PROFILE, MAPPING
from jra_index_provenance_builder import BASE, DERIVED, FORMULA_REGISTRY

FREEZE = "2026-10-10T12:09:00+09:00"
CUTOFF = "2026-10-10T12:18:00+09:00"
POST = "2026-10-10T12:25:00+09:00"
DISPATCH = "2026-10-10T12:22:00+09:00"


def sha(data):
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def numerical_runner(num, score):
    scores = {x: float(score) for x in BASE + DERIVED}
    scores.update(ZAI_WIN=float(score), ZAI_PLACE=float(score), T3I=float(score))
    return {
        "runner_id": str(num), "name": f"H{num}",
        "canonical_components": {
            name: {
                "value": value,
                "rule_id": f"PRODUCTION-FORMULA-{name}",
                "mapping_version": MAPPING if name in BASE else FORMULA_REGISTRY,
                "evidence_refs": [f"SIGNED-JRA-TEST-{num}-{name}"],
                "source_fact": "Synthetic mechanical acceptance only, never live",
            } for name, value in scores.items()
        },
    }


def fixture():
    source = {
        "family_id": "JRA",
        "race_id": "KM-JRA-AUTO-SELFTEST",
        "prediction_cutoff": CUTOFF,
        "source_freeze_at": "2026-10-10T12:08:42+09:00",
        "formal_ready": True,
    }
    source["source_snapshot_sha256"] = sha(source)
    env = {"artifact": source, "receipt_sha256": "c"*64}
    nums = [numerical_runner(1, 90), numerical_runner(2, 86), numerical_runner(3, 84)]
    ledger = {
        "family_id": "JRA",
        "race_id": source["race_id"],
        "runners": nums,
        "index_provenance_ledger": {"formula_registry": FORMULA_REGISTRY, "runners": {}},
        "index_provenance_hash": "f"*64,
        "base_index_mapping_authority": {
            "mapping_id": MAPPING,
            "status": "PRODUCTION / JRA-WIDE / NUMERICAL",
            "production_authority": True,
        },
    }
    owner = compile_static_owner(
        ledger,
        source_snapshot_sha256=source["source_snapshot_sha256"],
        source_receipt_sha256=env["receipt_sha256"],
        frozen_at=FREEZE,
        prediction_cutoff=CUTOFF,
    )
    report = {
        "production_full_numerical_ready": True,
        "source_only_full_numerical_ready": True,
        "verified_full_index_count": 60,
        "required_index_count": 60,
        "prepared_numerical_request": ledger,
        "static_owner_executable_diagnostic": owner,
    }
    policy_sha = hashlib.sha256(
        (ROOT / "runtime/jra_static_owner_executable.py").read_bytes()
    ).hexdigest()
    authority = {"family_scoped_authority": {"JRA": {
        "production_static_owner_activation": {
            "profile": PROFILE,
            "status": "PRODUCTION_AUTHORIZED",
            "explicit_production_review": True,
            "automatic_promotion": False,
            "forward_oos_eligible_races": 30,
            "market_baseline_superiority_proven": True,
            "policy_source_sha256": policy_sha,
            "independent_review_receipt_sha256": "b"*64,
        },
    }}}
    intent = {
        "family_id": "JRA",
        "race_id": source["race_id"],
        "venue_id": "TKY",
        "race": {"venue": "東京", "surface": "芝", "distance": 1800, "course": "左", "class": "2歳新馬"},
        "prediction_cutoff": CUTOFF,
        "external_dispatch_deadline_at": DISPATCH,
        "scheduled_post_at": POST,
        "run_count": 20000,
        "seed": 2026101005,
        "orchestration_ref": {
            "authority": "BASE44",
            "execution_session_id": "SIGNED-TEST-SESSION",
            "session_nonce": "NONCE-TEST",
            "created_at": FREEZE,
        },
    }
    return intent, env, report, authority


class TestJRAProductionAutohandoff(unittest.TestCase):
    def submit(self, intent, source, report, authority):
        return compile_production_auto_handoff(
            intent, source, report, current_authority=authority,
            frozen_at=FREEZE, root=ROOT,
        )

    def test_mechanical_numeric_to_static_and_krs_bridge(self):
        intent, source, report, authority = fixture()
        original = deepcopy((intent, source, report, authority))
        result = self.submit(intent, source, report, authority)
        self.assertEqual(original, (intent, source, report, authority))
        self.assertTrue(result["static_prediction_frozen"])
        self.assertTrue(result["static_prediction"]["production_authority"])
        self.assertEqual(len(result["runners"]), 3)
        self.assertEqual(len(result["krs_input_data"]["horses"]), 3)
        self.assertEqual(result["numeric_calculation_requirement"], "FULL_REQUIRED")
        self.assertEqual(result["static_prediction"]["ranking"], ["1", "2", "3"])
        self.assertEqual(result["source_snapshot_sha256"], source["artifact"]["source_snapshot_sha256"])
        self.assertTrue(all(c["production_authority"] for c in result["role_registry"]))
        self.assertFalse(result.get("signed_final_verified", False))
        # Canonical Formal Runner contract fields.
        self.assertEqual(result["static_freeze_timestamp"], intent["prediction_cutoff"])
        self.assertEqual(result["static_computed_at"], FREEZE)
        self.assertEqual(len(result["engine_sha256"]), 64)
        self.assertEqual(result["jra_adapter_mode"], "EXPLICIT_ENGINE_HSV")
        fpp = result["final_prediction_package"]
        self.assertEqual(fpp["ranking"], result["static_prediction"]["ranking"])
        self.assertEqual(fpp["roles"], result["static_prediction"]["roles"])
        self.assertFalse(fpp["production_prediction_change"])

    def test_numeric_failure_precedes_independent_static_blocker(self):
        intent, source, report, _ = fixture()
        report["production_full_numerical_ready"] = False
        with self.assertRaisesRegex(JRAProductionAutoHandoffError, "FULL20_INCOMPLETE"):
            self.submit(intent, source, report, {})

    def test_no_authority_cannot_upgrade_static_even_with_full20(self):
        intent, source, report, authority = fixture()
        for patch in (
            {"status": "NOT READY"},
            {"forward_oos_eligible_races": 23},
            {"automatic_promotion": True},
            {"explicit_production_review": False},
            {"market_baseline_superiority_proven": False},
            {"policy_source_sha256": "x"*64},
            {"independent_review_receipt_sha256": ""},
        ):
            with self.subTest(patch=patch):
                bad = deepcopy(authority)
                bad["family_scoped_authority"]["JRA"]["production_static_owner_activation"].update(patch)
                with self.assertRaises(JRAProductionAutoHandoffError):
                    self.submit(intent, source, report, bad)

    def test_missing_source_only_and_candidate_numerics_fail(self):
        intent, source, report, authority = fixture()
        bad = deepcopy(report)
        bad["source_only_full_numerical_ready"] = False
        with self.assertRaisesRegex(JRAProductionAutoHandoffError, "FULL20_INCOMPLETE"):
            self.submit(intent, source, bad, authority)
        bad = deepcopy(report)
        bad["prepared_numerical_request"]["runners"][0]["canonical_components"]["HPI"]["candidate_only"] = True
        with self.assertRaises(Exception):
            self.submit(intent, source, bad, authority)

    def test_forged_static_and_changed_numeric_inputs_cannot_pass_auto_handoff(self):
        intent, source, report, authority = fixture()
        tampered = deepcopy(report)
        tampered["static_owner_executable_diagnostic"]["static_prediction"]["ranking"].reverse()
        with self.assertRaisesRegex(JRAProductionAutoHandoffError, "CONTENT_HASH_MISMATCH"):
            self.submit(intent, source, tampered, authority)

        different_numeric = deepcopy(report)
        different_numeric["prepared_numerical_request"]["runners"][0]["canonical_components"]["ZAI_WIN"]["value"] = 1.0
        with self.assertRaisesRegex(JRAProductionAutoHandoffError, "CONTENT_HASH_MISMATCH"):
            self.submit(intent, source, different_numeric, authority)

        forged_candidate = deepcopy(report)
        forged_candidate["prepared_numerical_request"]["runners"][0]["canonical_components"]["HPI"]["candidate_only"] = True
        with self.assertRaisesRegex(JRAProductionAutoHandoffError, "RECOMPUTE_FAILED"):
            self.submit(intent, source, forged_candidate, authority)

    def test_static_freeze_later_than_external_handoff_rejected(self):
        intent, source, report, authority = fixture()
        tampered = deepcopy(report)
        tampered["static_owner_executable_diagnostic"] = compile_static_owner(
            tampered["prepared_numerical_request"],
            source_snapshot_sha256=source["artifact"]["source_snapshot_sha256"],
            source_receipt_sha256=source["receipt_sha256"],
            frozen_at="2026-10-10T12:12:00+09:00",
            prediction_cutoff=CUTOFF,
        )
        with self.assertRaisesRegex(JRAProductionAutoHandoffError, "FREEZE_AFTER_CUTOFF"):
            self.submit(intent, source, tampered, authority)

    def test_source_sha_time_and_external_orchestration_mandatory(self):
        intent, source, report, authority = fixture()
        badsource = deepcopy(source)
        badsource["artifact"]["race_id"] = "OTHER"
        with self.assertRaisesRegex(JRAProductionAutoHandoffError, "SNAPSHOT_HASH_INVALID"):
            self.submit(intent, badsource, report, authority)
        intent2 = deepcopy(intent)
        intent2["orchestration_ref"] = {}
        with self.assertRaises(Exception):
            self.submit(intent2, source, report, authority)
        intent3 = deepcopy(intent)
        intent3["external_dispatch_deadline_at"] = "2026-10-10T12:28:00+09:00"
        with self.assertRaisesRegex(JRAProductionAutoHandoffError, "TIME_INVALID"):
            self.submit(intent3, source, report, authority)


if __name__ == "__main__":
    unittest.main()
