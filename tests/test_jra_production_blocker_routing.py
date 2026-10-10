"""First-blocker vs independent-blocker routing and terminal admissibility.

Covers the 2026-10-10 handoff acceptance matrix rows:
- real SOURCE, Full20 short       -> evidence NO_BET, Static blocker still listed
- Full20 Actual, Static unapproved -> distinct Static NO_BET (never evidence NO_BET)
- Full20 Actual, Static approved   -> Formal handoff (no NO_BET terminal admissible)
- manual and automatic Static entries meet the SAME Full20 / authority gate
- historical recomputation is never a LIVE / pre-cutoff decision
No test grants Production authority to a live Current Authority manifest.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(ROOT / "tests"))

from jra_execution_maturity_bridge import (
    JRAMaturityBridgeError, prepare_production_numerical, require_manual_static_parity,
    load_current_authority,
)
from jra_production_auto_handoff import JRAProductionAutoHandoffError
from jra_production_blocker_classifier import (
    ROUTE_EVIDENCE_NO_BET, ROUTE_FAIL_CLOSED, ROUTE_FORMAL, ROUTE_STATIC_NO_BET,
    STAGE_NUMERICAL, STAGE_OWNER_AUTH, STAGE_TEMPORAL, classify_production_blockers,
    owner_activation_status,
)
from jra_production_no_bet_terminal import (
    BASE, DERIVED, JRANoBetTerminalError, STATIC_PROFILE, build_no_bet_terminal,
    build_static_unauthorized_no_bet_terminal, digest, verify_no_bet_terminal,
)
import test_jra_production_auto_handoff as handoff_fixture

REAL = "KM-JRA-TKY-20261010-R12-FULLPIPELINE-VALIDATION-LIVE-R1"
UNAUTHORIZED = {"authorized": False, "reason": "JRA_PRODUCTION_STATIC_OWNER_NOT_AUTHORIZED"}
AUTHORIZED = {"authorized": True, "reason": None}


def real_inputs(eid=REAL):
    intent = json.loads((ROOT / "runtime/jra_formal_intents" / (eid + ".json")).read_text(encoding="utf-8"))
    runs = sorted((ROOT / "runtime/executions" / eid / "SOURCE/runs").glob("*/source_receipt_envelope.json"))
    if not runs:
        raise unittest.SkipTest("stored real SOURCE not present in this checkout")
    env = json.loads(runs[-1].read_text(encoding="utf-8"))
    return intent, env


def full20_report():
    """Actual Full20 Production ledger (mechanical fixture) wrapped as a report."""
    intent, env, report, authority = handoff_fixture.fixture()
    art = env["artifact"]
    ids = [r["runner_id"] for r in report["prepared_numerical_request"]["runners"]]
    report = deepcopy(report)
    report.update({
        "family_id": "JRA", "race_id": art["race_id"], "runner_universe": ids,
        "mapping_id": handoff_fixture.MAPPING,
        "numerical_closure_mode": "SOURCE_ONLY",
        "source_checkpoint_manifest": {
            "race_id": art["race_id"], "prediction_cutoff": art["prediction_cutoff"],
            "source_freeze_at": art["source_freeze_at"],
            "source_snapshot_sha256": art["source_snapshot_sha256"],
            "receipt_sha256": env["receipt_sha256"], "source_execution_id": "TEST", "sha256": "e" * 64,
        },
        "sha256": "d" * 64,
    })
    return intent, env, report, authority


class TestClassifierOnRealSource(unittest.TestCase):
    def test_real_source_first_stop_is_numerical_and_static_is_independent(self):
        intent, env = real_inputs()
        report = prepare_production_numerical(intent, env, source_execution_id=REAL)
        cls = report["production_blocker_classification"]
        self.assertEqual(report["verified_full_index_count"], 0)
        self.assertEqual(cls["first_actual_blocked_stage"], STAGE_NUMERICAL)
        self.assertEqual(cls["independent_blocker_stages"], [STAGE_NUMERICAL, STAGE_OWNER_AUTH])
        self.assertEqual(cls["terminal_route"], ROUTE_EVIDENCE_NO_BET)
        self.assertFalse(cls["authority_granted"])
        feas = report["structural_closure_feasibility"]
        # Evidence for the actual owner: even an optimistic evaluator upper
        # bound cannot close pedigree / stable / pace indices from this SOURCE.
        for index in ("BVI", "CSI", "PRI"):
            self.assertIn(index, feas["structurally_unclosable_indices"])
        self.assertFalse(feas["evaluator_work_alone_can_close_full20"])
        self.assertFalse(feas["proves_closable"])
        self.assertFalse(feas["threshold_or_weight_change"])
        self.assertEqual(cls["independent_blockers"][0]["subclass"], "STRUCTURAL_SOURCE_FACT_GAP")
        self.assertFalse(report["static_generation_ready"])
        self.assertFalse(report["production_full_pipeline_ready"])
        self.assertEqual(report["static_owner_activation_status"]["authorized"], False)

    def test_real_source_evidence_no_bet_is_historical_not_live(self):
        intent, env = real_inputs()
        report = prepare_production_numerical(intent, env, source_execution_id=REAL)
        with self.assertRaisesRegex(JRANoBetTerminalError, "AFTER_CUTOFF"):
            build_no_bet_terminal(intent, report, source_receipt_verified=True,
                                  created_at="2026-10-10T23:00:00+09:00", lineage="LIVE")
        t = build_no_bet_terminal(intent, report, source_receipt_verified=True,
                                  created_at="2026-10-10T23:00:00+09:00",
                                  lineage="HISTORICAL_DIAGNOSTIC")
        check = verify_no_bet_terminal(t)
        self.assertEqual(check["terminal_index_count"], report["required_index_count"])
        with self.assertRaises(JRANoBetTerminalError):
            verify_no_bet_terminal(t, require_live=True)
        with self.assertRaisesRegex(JRANoBetTerminalError, "OWNER_AUTHORIZED|FULL20_NOT_READY"):
            build_static_unauthorized_no_bet_terminal(
                intent, report, owner_status=UNAUTHORIZED, source_receipt_verified=True,
                created_at="2026-10-10T23:00:00+09:00", lineage="HISTORICAL_DIAGNOSTIC")

    def test_live_authority_has_no_static_owner_activation(self):
        status = owner_activation_status(load_current_authority(ROOT / "profiles"), root=str(ROOT))
        self.assertFalse(status["authorized"])
        self.assertIn("NOT_AUTHORIZED", status["reason"])


class TestFull20StaticBlockedRouting(unittest.TestCase):
    def test_full20_with_unapproved_owner_routes_to_static_no_bet(self):
        intent, env, report, _ = full20_report()
        cls = classify_production_blockers(report, owner_status=UNAUTHORIZED)
        self.assertEqual(cls["first_actual_blocked_stage"], STAGE_OWNER_AUTH)
        self.assertEqual(cls["terminal_route"], ROUTE_STATIC_NO_BET)
        # The evidence-insufficient builder must refuse an Actual Full20 race.
        with self.assertRaisesRegex(JRANoBetTerminalError, "FULL20_READY"):
            build_no_bet_terminal(intent, report, source_receipt_verified=True,
                                  created_at=handoff_fixture.FREEZE)
        t = build_static_unauthorized_no_bet_terminal(
            intent, report, owner_status=UNAUTHORIZED, source_receipt_verified=True,
            created_at=handoff_fixture.FREEZE, lineage="LIVE")
        self.assertEqual(t["profile"], STATIC_PROFILE)
        self.assertEqual(t["terminal_index_count"], 60)
        self.assertEqual(t["base_calculated_count"], 39)
        self.assertEqual(t["derived_calculated_count"], 21)
        self.assertEqual(t["base_held_count"] + t["derived_held_count"], 0)
        self.assertTrue(t["production_full20_ready"])
        self.assertFalse(t["static_prediction_issued"])
        self.assertNotIn("static_prediction", t)
        self.assertEqual((t["total_investment"], t["tickets"]), (0, []))
        check = verify_no_bet_terminal(t, require_live=True)
        self.assertTrue(check["actual_full20"])
        self.assertFalse(check["signed_final_verified"])

    def test_static_no_bet_tamper_is_rejected(self):
        intent, env, report, _ = full20_report()
        good = build_static_unauthorized_no_bet_terminal(
            intent, report, owner_status=UNAUTHORIZED, source_receipt_verified=True,
            created_at=handoff_fixture.FREEZE)
        cases = [
            ("total_investment", 100),
            ("tickets", [{"bet_type": "TRIO"}]),
            ("krs_executed", True),
            ("signed_final_verified", True),
            ("static_prediction_issued", True),
            ("production_full20_ready", False),
            ("decision_reason", "PRODUCTION_FULL20_EVIDENCE_INSUFFICIENT"),
        ]
        for key, value in cases:
            with self.subTest(key=key):
                bad = deepcopy(good)
                bad[key] = value
                bad["sha256"] = digest({k: v for k, v in bad.items() if k != "sha256"})
                with self.assertRaises(JRANoBetTerminalError):
                    verify_no_bet_terminal(bad)
        bad = deepcopy(good)
        first = next(iter(bad["index_universe"]))
        bad["index_universe"][first]["HPI"] = {"terminal_status": "RULED-HOLD", "value": None,
                                               "reason": "x"}
        bad["sha256"] = digest({k: v for k, v in bad.items() if k != "sha256"})
        with self.assertRaises(JRANoBetTerminalError):
            verify_no_bet_terminal(bad)

    def test_candidate_or_partial_numerics_cannot_make_static_no_bet(self):
        intent, env, report, _ = full20_report()
        for mutate in (
            lambda r: r["prepared_numerical_request"]["runners"][0]["canonical_components"]["ZAI_WIN"].update(candidate_only=True),
            lambda r: r["prepared_numerical_request"]["runners"][0]["canonical_components"].pop("T3I"),
            lambda r: r.update(verified_full_index_count=59),
            lambda r: r.update(production_full_numerical_ready=False),
        ):
            bad = deepcopy(report)
            mutate(bad)
            with self.assertRaises(JRANoBetTerminalError):
                build_static_unauthorized_no_bet_terminal(
                    intent, bad, owner_status=UNAUTHORIZED, source_receipt_verified=True,
                    created_at=handoff_fixture.FREEZE)

    def test_authorized_owner_routes_formal_and_forbids_no_bet(self):
        intent, env, report, _ = full20_report()
        cls = classify_production_blockers(report, owner_status=AUTHORIZED)
        self.assertEqual(cls["terminal_route"], ROUTE_FORMAL)
        self.assertIsNone(cls["first_actual_blocked_stage"])
        with self.assertRaisesRegex(JRANoBetTerminalError, "USE_FORMAL"):
            build_static_unauthorized_no_bet_terminal(
                intent, report, owner_status=AUTHORIZED, source_receipt_verified=True,
                created_at=handoff_fixture.FREEZE)

    def test_post_cutoff_ready_race_fails_closed_not_formal(self):
        intent, env, report, _ = full20_report()
        cls = classify_production_blockers(report, owner_status=AUTHORIZED, intent=intent,
                                           now="2026-10-10T12:30:00+09:00")
        self.assertEqual(cls["independent_blocker_stages"], [STAGE_TEMPORAL])
        self.assertEqual(cls["terminal_route"], ROUTE_FAIL_CLOSED)

    def test_unverified_source_never_terminalizes(self):
        intent, env, report, _ = full20_report()
        with self.assertRaisesRegex(JRANoBetTerminalError, "SIGNED_SOURCE"):
            build_static_unauthorized_no_bet_terminal(
                intent, report, owner_status=UNAUTHORIZED, source_receipt_verified=False,
                created_at=handoff_fixture.FREEZE)


class TestAutoHandoffDiagnosticOrder(unittest.TestCase):
    def test_numerical_gap_is_reported_first_with_owner_as_independent(self):
        intent, env, report, authority = handoff_fixture.fixture()
        bad = deepcopy(report)
        bad["production_full_numerical_ready"] = False
        missing = {"family_scoped_authority": {"JRA": {}}}
        with self.assertRaises(JRAProductionAutoHandoffError) as ctx:
            handoff_fixture.compile_production_auto_handoff(
                intent, env, bad, current_authority=missing,
                frozen_at=handoff_fixture.FREEZE, root=ROOT)
        msg = str(ctx.exception)
        self.assertTrue(msg.startswith("JRA_AUTHORIZED_FULL20_INCOMPLETE"), msg)
        self.assertIn("INDEPENDENT_BLOCKERS:JRA_PRODUCTION_STATIC_OWNER_NOT_AUTHORIZED", msg)
        self.assertEqual(ctx.exception.blockers, [
            "JRA_AUTHORIZED_FULL20_INCOMPLETE", "JRA_PRODUCTION_STATIC_OWNER_NOT_AUTHORIZED"])


class TestManualStaticParity(unittest.TestCase):
    def human_static(self, ids):
        return {"ranking": list(reversed(ids)),
                "roles": {ids[-1]: ["W", "P2", "P3"], ids[0]: ["P3"]},
                "status": "FROZEN-PRE-KRS"}

    def test_manual_static_cannot_skip_full20(self):
        intent, env = real_inputs()
        report = prepare_production_numerical(intent, env, source_execution_id=REAL)
        q = deepcopy(intent)
        q["static_prediction"] = self.human_static(report["runner_universe"])
        with self.assertRaisesRegex(JRAMaturityBridgeError, "MANUAL_STATIC_BLOCKED:JRA_AUTHORIZED_FULL20_INCOMPLETE"):
            require_manual_static_parity(q, report)

    def test_manual_static_cannot_relabel_unapproved_candidate_owner(self):
        intent, env, report, _ = full20_report()
        owner = report["static_owner_executable_diagnostic"]
        report = dict(report, static_owner_activation_status=UNAUTHORIZED)
        relabelled = deepcopy(owner["static_prediction"])
        relabelled.update(production_authority=True, status="FROZEN-PRE-KRS", authority="HUMAN")
        q = dict(intent, static_prediction=relabelled)
        with self.assertRaisesRegex(JRAMaturityBridgeError, "EQUALS_UNAUTHORIZED_CANDIDATE_OWNER"):
            require_manual_static_parity(q, report)
        q = dict(intent, static_prediction=deepcopy(owner["static_prediction"]))
        with self.assertRaisesRegex(JRAMaturityBridgeError, "CANDIDATE_OR_SHADOW_AUTHORITY_FORBIDDEN"):
            require_manual_static_parity(q, report)
        q = dict(intent, static_prediction=self.human_static(report["runner_universe"]),
                 role_registry=[{"runner_id": "1", "column": "W", "status": "CORE",
                                 "authority": "TSL-SHADOW"}])
        with self.assertRaisesRegex(JRAMaturityBridgeError, "CANDIDATE_OR_SHADOW"):
            require_manual_static_parity(q, report)

    def test_manual_static_with_actual_full20_passes_same_gate(self):
        intent, env, report, _ = full20_report()
        report = dict(report, static_owner_activation_status=UNAUTHORIZED)
        q = dict(intent, static_prediction=self.human_static(report["runner_universe"]))
        self.assertEqual(require_manual_static_parity(q, report)["status"], "PASS")

    def test_cli_manual_static_on_real_source_persists_gap_and_blocks(self):
        intent, env = real_inputs()
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            q = deepcopy(intent)
            q["static_prediction"] = {"ranking": ["1", "2"], "roles": {"1": ["W"]},
                                      "status": "FROZEN-PRE-KRS"}
            q["static_prediction_frozen"] = True
            (d / "intent.json").write_text(json.dumps(q, ensure_ascii=False))
            (d / "source.json").write_text(json.dumps(env, ensure_ascii=False))
            proc = subprocess.run(
                [sys.executable, str(ROOT / "runtime/jra_execution_maturity_bridge.py"),
                 "build-formal", "--intent", str(d / "intent.json"),
                 "--source-envelope", str(d / "source.json"), "--source-execution-id", REAL,
                 "--output", str(d / "formal.json"), "--gap-output", str(d / "gap.json")],
                cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse((d / "formal.json").exists())
            self.assertIn("MANUAL_STATIC_BLOCKED", proc.stderr)
            self.assertIn("FIRST=PRODUCTION_FEATURE_INDEX_CLOSURE", proc.stderr)
            gap = json.loads((d / "gap.json").read_text())
            self.assertEqual(gap["production_blocker_classification"]["terminal_route"],
                             ROUTE_EVIDENCE_NO_BET)


class TestPreparationReadinessIsNotHardcoded(unittest.TestCase):
    def setUp(self):
        import test_jra_single_entry_exact_gap as gap_tests
        case = gap_tests.ProductionPreparationTest("test_duplicate_official_universe_rejected")
        case.setUp()
        self.intent = case.intent
        self.env = case.env
        self.intent["acceptance_only"] = True
        self.intent["supplemental_evidence_pack"] = case.supplemental()

    def authority(self, authorized):
        policy_sha = hashlib.sha256((ROOT / "runtime/jra_static_owner_executable.py").read_bytes()).hexdigest()
        activation = {
            "profile": handoff_fixture.PROFILE, "status": "PRODUCTION_AUTHORIZED",
            "explicit_production_review": True, "automatic_promotion": False,
            "forward_oos_eligible_races": 30, "market_baseline_superiority_proven": True,
            "policy_source_sha256": policy_sha, "independent_review_receipt_sha256": "b" * 64,
        } if authorized else {}
        return {"manifest_id": "TEST-ONLY-NOT-A-PROFILE",
                "family_scoped_authority": {"JRA": {"production_static_owner_activation": activation}}}

    def test_flags_follow_the_same_gate_as_auto_handoff(self):
        unauthorized = prepare_production_numerical(self.intent, self.env,
                                                    current_authority=self.authority(False))
        self.assertTrue(unauthorized["production_full_numerical_ready"])
        self.assertFalse(unauthorized["static_generation_ready"])
        self.assertEqual(unauthorized["first_blocked_stage"], "PRODUCTION_STATIC_PREDICTION_OWNER")
        self.assertEqual(unauthorized["production_blocker_classification"]["terminal_route"],
                         ROUTE_STATIC_NO_BET)
        authorized = prepare_production_numerical(self.intent, self.env,
                                                  current_authority=self.authority(True))
        self.assertTrue(authorized["static_generation_ready"])
        self.assertTrue(authorized["production_full_pipeline_ready"])
        self.assertEqual(authorized["production_full_pipeline_ready_scope"], "LOCAL_PRE_KRS_HANDOFF_ONLY")
        self.assertEqual(authorized["first_blocked_stage"], "NONE_LOCAL_PRE_KRS_HANDOFF_READY")
        # Acceptance-only supplemental numerics still never become LIVE.
        with self.assertRaisesRegex(JRANoBetTerminalError, "ACCEPTANCE_ONLY"):
            build_static_unauthorized_no_bet_terminal(
                self.intent, unauthorized, owner_status=UNAUTHORIZED,
                source_receipt_verified=True, created_at="2099-01-01T09:59:00+09:00",
                lineage="LIVE")


if __name__ == "__main__":
    unittest.main()
