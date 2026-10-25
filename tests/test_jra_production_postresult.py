import hashlib
import json
import sys
from pathlib import Path
import unittest
from copy import deepcopy
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from jra_production_postresult import (
    build_result_request, build_settlement_correction, settle_final, verify_final, ProductionPostResultError, _sha,
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

WITHDRAWAL_OFFICIAL={"top3":[4,2,1],"refund_runner_ids":[6],"payouts":{
    "EXACTA":{"selection":[4,2],"per_100_yen":1230},
    "TRIO":{"selection":[1,2,4],"per_100_yen":2210},
    "TRIFECTA":{"selection":[4,2,1],"per_100_yen":9870}}}


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


def test_refunds_use_official_withdrawn_runner_and_net_risk_denominator():
    f=final(); before=deepcopy(f)
    official={**deepcopy(WITHDRAWAL_OFFICIAL),"non_finishers":[
        {"horse_no":6,"finish_status":"EXCLUDED"}]}
    # The affected trifecta must be returned once, never both won and returned.
    s=settle_final(f,official)
    assert s['total_investment']==300 and s['refund']==100
    assert s['effective_investment']==200 and s['total_payout']==1230
    assert s['profit_loss']==1030 and s['pfs']==615
    assert len(s['refunded_tickets'])==1 and len(s['winning_tickets'])==1
    assert f==before
    req=build_result_request(f,official,EVIDENCE)
    review=build_post_result_review(req,f)
    assert review['capital']['refund']==100 and review['capital']['effective_investment']==200
    assert review['capital']['profit_loss']==1030 and review['capital']['pfs']==615


def test_wholly_refunded_or_zero_stake_has_undefined_pfs():
    f=final();f['final_ticket'].update(tickets=[f['final_ticket']['tickets'][-1]],total_investment=100)
    s=settle_final(f,WITHDRAWAL_OFFICIAL)
    assert s['refund']==100 and s['effective_investment']==0
    assert s['total_payout']==0 and s['profit_loss']==0 and s['pfs'] is None
    f=final();f['final_ticket'].update(tickets=[],total_investment=0,no_bet=True)
    s=settle_final(f,OFFICIAL)
    assert s['pfs'] is None and s['gross_stake_pfs'] is None


@pytest.mark.parametrize('status',['DID_NOT_FINISH','DISQUALIFIED'])
def test_noncompletion_and_disqualification_are_not_withdrawal_refunds(status):
    official={**OFFICIAL,'refund_runner_ids':[6],
              'non_finishers':[{'horse_no':6,'finish_status':status}]}
    with pytest.raises(ProductionPostResultError,match='NONCANCELLATION_REFUND_FORBIDDEN'):
        settle_final(final(),official)


def test_refund_correction_is_a_separate_audit_and_keeps_original_bytes():
    f=final(); original=build_result_request(f,OFFICIAL,EVIDENCE)
    unchanged=json.dumps([f,original],ensure_ascii=False,sort_keys=True)
    corrected=WITHDRAWAL_OFFICIAL
    audit=build_settlement_correction(f,original,corrected,EVIDENCE,
                                    audited_at='2026-10-11T07:10:00+00:00')
    assert audit['corrected_settlement']['refund']==100
    assert audit['original_settlement']['refund']==0
    assert audit['signed_result_correction']=='NOT_ISSUED'
    assert audit['old_learning_unchanged'] and audit['original_frozen_prediction_unchanged']
    assert audit['sha256']==_sha({k:v for k,v in audit.items() if k!='sha256'})
    assert json.dumps([f,original],ensure_ascii=False,sort_keys=True)==unchanged
    with pytest.raises(ProductionPostResultError,match='CHRONOLOGY'):
        build_settlement_correction(f,original,corrected,EVIDENCE,
                                    audited_at='2026-10-11T06:59:59+00:00')


def test_legacy_zero_refund_review_hash_is_unchanged_by_refund_support():
    req=build_result_request(final(),OFFICIAL,EVIDENCE)
    req['settlement'].pop('effective_investment')
    review=build_post_result_review(req,final())
    assert 'refund' not in review['capital'] and 'effective_investment' not in review['capital']
