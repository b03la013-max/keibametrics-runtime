"""Structural NO_BET terminal: 20 indices per runner, no fake numbers or bet."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
from jra_production_no_bet_terminal import (
    build_no_bet_terminal, verify_no_bet_terminal, JRANoBetTerminalError, BASE, DERIVED, digest,
)

CUTOFF="2026-10-10T12:18:00+09:00"
PRE="2026-10-10T12:10:00+09:00"
POST="2026-10-10T12:25:00+09:00"


def fixtures():
    ids=["1","2"]
    req={"family_id":"JRA","race_id":"KM-JRA-TKY-20261010-R05",
         "prediction_cutoff":CUTOFF,"scheduled_post_at":POST}
    rows={}
    for rid in ids:
        entries={}
        for name in BASE:
            entries[name]={
                "status":"BLOCKED", "value":None,
                "reason":"INDEX_EVIDENCE_COVERAGE_LOW:NEWCOMER:" + name
            }
        entries["VMI"]={
            "status":"CALCULATED","value":78.0,
            "rule_id":"OFFICIAL-MARKET-RANK-RULE",
            "evidence_refs":["SIGNED-JRA-OFFICIAL-MARKET"],
            "source_fact":"Observed official popularity rank"
        }
        rows[rid]={"indices":entries}
    report={
        "family_id":"JRA","race_id":req["race_id"],
        "runner_universe":ids,
        "mapping_id":"JRA-EVIDENCE-TO-BASE-MAPPING-v1.0-PRODUCTION-20260921",
        "source_checkpoint_manifest":{
            "race_id":req["race_id"],
            "source_execution_id":"KM-JRA-TKY-20261010-R05-LIVE-R1",
            "prediction_cutoff":CUTOFF,
            "source_freeze_at":"2026-10-10T12:08:42+09:00",
            "source_snapshot_sha256":"a"*64,
            "receipt_sha256":"b"*64,
            "sha256":"c"*64,
        },
        "partial_production_base_calculation":{
            "runners":rows,
            "calculated_base_cells":2,
            "blocked_base_cells":24
        },
        "production_full_numerical_ready":False,
        "source_only_full_numerical_ready":False,
        "first_blocked_stage":"PRODUCTION_FEATURE_INDEX_CLOSURE",
        "sha256":"d"*64
    }
    return req,report


class TestJraNoBetTerminal(unittest.TestCase):
    def test_complete_terminal_without_forging_predictions(self):
        req, report=fixtures()
        before=deepcopy((req,report))
        obj=build_no_bet_terminal(req,report,source_receipt_verified=True,created_at=PRE)
        self.assertEqual(before,(req,report))
        self.assertEqual(obj["required_index_count"],40)
        self.assertEqual(obj["terminal_index_count"],40)
        self.assertEqual(obj["base_calculated_count"],2)
        self.assertEqual(obj["base_held_count"],24)
        self.assertEqual(obj["derived_held_count"],14)
        self.assertEqual(obj["unresolved_count"],0)
        self.assertEqual(obj["decision"],"NO_BET")
        self.assertFalse(obj["formal_full_prediction_completed"])
        self.assertFalse(obj["purchase_authority"])
        self.assertFalse(obj["signed_final_verified"])
        self.assertEqual(obj["tickets"],[])
        self.assertEqual(obj["total_investment"],0)
        self.assertEqual(obj["index_universe"]["1"]["HPI"]["terminal_status"],"RULED-HOLD")
        self.assertIsNone(obj["index_universe"]["1"]["HPI"]["value"])
        self.assertEqual(obj["sha256"],digest({k:v for k,v in obj.items() if k!="sha256"}))

    def test_independent_decision_terminal_verifier(self):
        q,r=fixtures()
        good=build_no_bet_terminal(q,r,source_receipt_verified=True,created_at=PRE)
        check=verify_no_bet_terminal(good, race_id=q["race_id"],require_live=True)
        self.assertEqual(check["status"],"VERIFIED_ZERO_EXPOSURE_DECISION_ONLY")
        self.assertEqual(check["terminal_index_count"],40)
        self.assertEqual(check["total_investment"],0)
        self.assertFalse(check["signed_final_verified"])

    def test_terminal_verifier_rejects_changed_body_even_with_recomputed_hash(self):
        q,r=fixtures()
        good=build_no_bet_terminal(q,r,source_receipt_verified=True,created_at=PRE)
        mutations=(
            lambda o:o["index_universe"]["1"]["HPI"].update(value=50),
            lambda o:o["index_universe"]["1"]["VMI"].update(value=150),
            lambda o:o["index_universe"]["1"].pop("DCR"),
            lambda o:o.update(tickets=[{"stake":100}]),
            lambda o:o.update(total_investment=100),
            lambda o:o.update(krs_executed=True),
            lambda o:o.update(signed_final_verified=True),
            lambda o:o.update(base_calculated_count=400),
            lambda o:o.update(lineage="UNKNOWN"),
        )
        for mutation in mutations:
            with self.subTest(mutation=str(mutation)):
                bad=deepcopy(good)
                mutation(bad)
                bad["sha256"]=digest({k:v for k,v in bad.items() if k!="sha256"})
                with self.assertRaises(JRANoBetTerminalError):
                    verify_no_bet_terminal(bad)
        bad=deepcopy(good)
        bad["total_investment"]=100
        with self.assertRaisesRegex(JRANoBetTerminalError,"SHA256_MISMATCH"):
            verify_no_bet_terminal(bad)

    def test_source_must_have_independently_verified_receipt(self):
        q,r=fixtures()
        with self.assertRaisesRegex(JRANoBetTerminalError,"VERIFICATION_REQUIRED"):
            build_no_bet_terminal(q,r,source_receipt_verified=False,created_at=PRE)

    def test_unsafe_late_live_terminal_rejected(self):
        q,r=fixtures()
        with self.assertRaisesRegex(JRANoBetTerminalError,"AFTER_CUTOFF"):
            build_no_bet_terminal(q,r,source_receipt_verified=True,
                                  created_at="2026-10-10T13:00:00+09:00")
        d=build_no_bet_terminal(q,r,source_receipt_verified=True,
                                  created_at="2026-10-10T13:00:00+09:00",
                                  lineage="HISTORICAL_DIAGNOSTIC")
        self.assertEqual(d["temporal_classification"],"POST_CUTOFF_HISTORICAL")

    def test_faked_numeric_universe_or_missing_reason_rejected(self):
        q,r=fixtures()
        cases=(
            lambda z:z["partial_production_base_calculation"]["runners"]["1"]["indices"]["HPI"].update(value=50),
            lambda z:z["partial_production_base_calculation"]["runners"]["1"]["indices"]["VMI"].update(evidence_refs=[]),
            lambda z:z["partial_production_base_calculation"]["runners"].pop("2"),
            lambda z:z["partial_production_base_calculation"].update(blocked_base_cells=1),
            lambda z:z["source_checkpoint_manifest"].update(receipt_sha256=""),
        )
        for change in cases:
            with self.subTest(change=str(change)):
                bad=deepcopy(r)
                change(bad)
                with self.assertRaises(JRANoBetTerminalError):
                    build_no_bet_terminal(q,bad,source_receipt_verified=True,created_at=PRE)

    def test_do_not_substitute_no_bet_for_ready_formal(self):
        q,r=fixtures()
        r["production_full_numerical_ready"]=True
        r["source_only_full_numerical_ready"]=True
        with self.assertRaisesRegex(JRANoBetTerminalError,"USE_FORMAL_LIVE_PATH"):
            build_no_bet_terminal(q,r,source_receipt_verified=True,created_at=PRE)


if __name__=="__main__":
    unittest.main()
