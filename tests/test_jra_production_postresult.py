import hashlib
import json
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from jra_production_postresult import (
    build_result_request, settle_final, verify_final, ProductionPostResultError, _sha,
)
from post_result_learning import build_post_result_review


def final(decision="EXECUTE_RECOMMENDATION_PORTFOLIO", receipt_ts="2026-10-11T06:30:00+00:00"):
    tickets = [
        {"bet_type": "EXACTA", "selection": [4, 2], "stake": 100},
        {"bet_type": "EXACTA", "selection": [2, 4], "stake": 100},
        {"bet_type": "TRIFECTA", "selection": [4, 2, 6], "stake": 100},
    ]
    f = {
        "race_id": "KM-JRA-TKY-20261011-R11", "family_id": "JRA",
        "temporal_mode": "FORMAL-PRE-RACE",
        "prediction_cutoff": "2026-10-11T06:20:00+00:00",
        "scheduled_post_at": "2026-10-11T06:45:00+00:00",
        "static_prediction": {"ranking": ["4", "2", "6", "1"]},
        "final_prediction_package": {"roles": {"4": ["W", "P2", "P3"], "2": ["W", "P2", "P3"], "6": ["P3"]},
                                     "validation_status": "UNVALIDATED"},
        "capital_policy_decision": {"decision": decision},
        "final_ticket": {"tickets": tickets, "total_investment": 300, "no_bet": False},
        "final_receipt": {"receipt": {"timestamp": receipt_ts}},
        "final_receipt_sha256": "f" * 64,
    }
    f["sha256"] = _sha(f)
    return f


OFFICIAL = {"top3": [4, 2, 6], "payouts": {
    "EXACTA": {"selection": [4, 2], "per_100_yen": 1230},
    "TRIO": {"selection": [2, 4, 6], "per_100_yen": 2210},
    "TRIFECTA": {"selection": [4, 2, 6], "per_100_yen": 9870}}}
EVIDENCE = {"parsed": {"runners": [{"horse_no": h, "finish": i + 1} for i, h in enumerate([4, 2, 6, 1])]},
            "url": "https://www.jra.go.jp/x", "sha256": "a" * 64, "captured_at": "2026-10-11T07:00:00+00:00"}


class TestProductionPostResult(unittest.TestCase):
    def test_settles_exact_frozen_tickets_and_separates_purchase(self):
        s = settle_final(final(), OFFICIAL)
        self.assertEqual(s["total_investment"], 300)
        self.assertEqual(s["total_payout"], 1230 + 9870)
        self.assertEqual(s["actual_purchase_status"], "NOT_PURCHASED_RECOMMENDATION_ONLY")
        self.assertEqual(len(s["winning_tickets"]), 2)

    def test_request_feeds_canonical_review(self):
        f = final()
        req = build_result_request(f, OFFICIAL, EVIDENCE)
        self.assertEqual(req["official_result"]["finish_order"], [4, 2, 6, 1])
        self.assertEqual(req["frozen_prediction_ref"]["immutable_final_sha256"], f["sha256"])
        review = build_post_result_review(req, f)
        self.assertEqual(review["race_id"], f["race_id"])

    def test_tampered_or_late_final_rejected(self):
        f = final()
        f["final_ticket"]["total_investment"] = 200
        with self.assertRaisesRegex(ProductionPostResultError, "HASH_INVALID"):
            verify_final(f)
        with self.assertRaisesRegex(ProductionPostResultError, "AFTER_POST"):
            verify_final(final(receipt_ts="2026-10-11T06:46:00+00:00"))


if __name__ == "__main__":
    unittest.main()
