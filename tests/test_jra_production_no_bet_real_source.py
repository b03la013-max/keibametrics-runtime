"""Historical Tokyo R05 real-source gap is all-runner terminalized as NO_BET.

Does NOT use a fake numeric input or upgrade historical race to forward OOS.
Independent SOURCE signature was verified in its original SOURCE workflow.
This regression only checks stored receipt-linked gap classification.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))
from jra_production_no_bet_terminal import build_no_bet_terminal


class TestRealTokyoEvidenceGap(unittest.TestCase):
    def test_exact_real_source_gap_is_240_terminal_without_fake_purchases(self):
        race="KM-JRA-TKY-20261010-R05-LIVE-R1"
        intent_path=ROOT/"runtime/jra_formal_intents"/(race+".json")
        gap_path=ROOT/"runtime/exact_gaps"/(race+".json")
        if not gap_path.exists():
            self.skipTest("Historical exact gap not present in this checkout")
        intent=json.loads(intent_path.read_text(encoding="utf-8"))
        gap=json.loads(gap_path.read_text(encoding="utf-8"))
        out=build_no_bet_terminal(
            intent,gap,source_receipt_verified=True,
            lineage="HISTORICAL_DIAGNOSTIC",
            created_at="2026-10-10T13:25:00+09:00"
        )
        self.assertEqual(out["source_snapshot_sha256"],
                         "634ff84d156f35af45ee0968ce2509cbe07b02ff7b08578e681e14ba93910c06")
        self.assertEqual(len(out["index_universe"]),12)
        self.assertEqual(out["terminal_index_count"],240)
        self.assertEqual(out["required_index_count"],240)
        self.assertGreater(out["base_held_count"],0)
        self.assertEqual(out["base_calculated_count"]+out["base_held_count"],156)
        self.assertEqual(out["derived_held_count"],84)
        self.assertEqual(out["total_investment"],0)
        self.assertEqual(out["tickets"],[])
        self.assertFalse(out["formal_full_prediction_completed"])
        self.assertEqual(out["temporal_classification"],"POST_CUTOFF_HISTORICAL")
        self.assertEqual(out["decision"],"NO_BET")


if __name__=="__main__":
    unittest.main()
