"""Practical JRA forecast displays only genuine frozen Candidate tickets."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
from jra_practical_candidate_forecast import make_forecast_brief,digest,PracticalForecastError

RECEIPT="a"*64
SNAP="b"*64
TS="2026-10-10T13:50:20+09:00"
POST="2026-10-10T15:45:00+09:00"

def frozen_fixture():
    ranking=["3","5","8","9","10","11"]
    pairs=[{"head":h,"second":s,"status":"PURCHASE"}
           for h in ("3","5") for s in ranking if s!=h]
    thirds=[{"head":h,"second":s,"third":t,"status":"PURCHASE"}
            for h in ("3","5") for s in ranking if s!=h for t in ranking if t not in (h,s)]
    tickets=[{"bet_type":"EXACTA","selection":[h,s],"stake":100}
             for h in (3,5) for s in (3,5,8,9,10,11) if s!=h]
    tickets += [{"bet_type":"TRIFECTA","selection":[h,s,t],"stake":100}
                for h in (3,5) for s in (3,5,8,9,10,11) if s!=h
                for t in (3,5,8,9,10,11) if t not in (h,s)]
    pre={
        "race_id":"KM-JRA-TKY-20261010-R11",
        "source_snapshot_sha256":SNAP,
        "ranking":ranking,
        "roles":{r:["W","P2","P3"] for r in ranking},
        "candidate_objective_trace":{"runners":{
            r:{"observed_feature_count":12,"missing_feature_count":59}
            for r in ranking
        }},
        "market_ranking":["5","8","3","9","11","10"],
        "pair_dispositions":pairs,
        "third_dispositions":thirds,
        "candidate_final_verified":True,
        "oos_eligible":True,
        "acceptance_only":False,
        "production_effect":"NONE",
        "frozen_at":TS,
        "candidate_final_receipt_sha256":RECEIPT,
        "candidate_final_receipt_timestamp":TS,
        "scheduled_post_at":POST,
    }
    pre["sha256"]=digest(pre)
    final={
        "candidate_only":True,
        "production_effect":"NONE",
        "race_id":pre["race_id"],
        "source_snapshot_sha256":SNAP,
        "oos_pre_result_record_sha256":pre["sha256"],
        "final_receipt":{"receipt_sha256":RECEIPT},
        "mec":{"ticket_count":len(tickets),
               "minimum_required_capital":100*len(tickets),
               "tickets":tickets},
        "capital":{"no_bet":False},
    }
    final["sha256"]=digest(final)
    return pre,final


class TestPracticalCandidateForecast(unittest.TestCase):
    def forecast(self,pre,final,*,generated="2026-10-10T14:20:00+09:00",budget=2000):
        return make_forecast_brief(pre,final,
            generated_at=generated,maximum_paper_budget_yen=budget)

    def test_frozen_real_semantics_yield_balanced_sane_paper_display(self):
        pre,final=frozen_fixture()
        before=deepcopy((pre,final))
        out=self.forecast(pre,final)
        self.assertEqual((pre,final),before)
        self.assertEqual(out["ranked_top6"],pre["ranking"][:6])
        self.assertEqual(out["candidate_primary_heads"],["3","5"])
        self.assertEqual(out["display_ticket_count"],20)
        self.assertEqual(out["display_paper_total_yen"],2000)
        self.assertEqual(set(out["display_tickets_by_head"]),{"3","5"})
        self.assertEqual(len(out["display_tickets_by_head"]["3"]),10)
        self.assertEqual(len(out["display_tickets_by_head"]["5"]),10)
        self.assertEqual(out["frozen_mec_ticket_count"],len(final["mec"]["tickets"]))
        self.assertLess(out["retained_ticket_fraction"],1)
        self.assertFalse(out["semantic_coverage_equivalence_claim"])
        self.assertFalse(out["winner_probability_calibrated"])
        self.assertFalse(out["new_final_generated"])
        self.assertEqual(out["display_temporal_class"],"PRE_START_PREVIEW")

    def test_prehashed_tampering_and_final_ticket_forgery_fail(self):
        pre,final=frozen_fixture()
        bad=deepcopy(pre);bad["ranking"][0]="999"
        with self.assertRaisesRegex(PracticalForecastError,"OOS_HASH_INVALID"):
            self.forecast(bad,final)
        bad=deepcopy(final);bad["mec"]["tickets"][0]["selection"]=[99,5]
        with self.assertRaisesRegex(PracticalForecastError,"FINAL_HASH_INVALID"):
            self.forecast(pre,bad)
        bad=deepcopy(final);bad["oos_pre_result_record_sha256"]="unrelated"
        bad["sha256"]=digest({k:v for k,v in bad.items() if k!="sha256"})
        with self.assertRaisesRegex(PracticalForecastError,"LINEAGE_INVALID"):
            self.forecast(pre,bad)
        bad=deepcopy(final);bad["mec"]["tickets"][0]["selection"]=[99,5]
        bad["sha256"]=digest({k:v for k,v in bad.items() if k!="sha256"})
        with self.assertRaisesRegex(PracticalForecastError,"TICKET_INVALID"):
            self.forecast(pre,bad)

    def test_cannot_label_reprint_as_forward_or_change_capital(self):
        pre,final=frozen_fixture()
        out=self.forecast(pre,final,generated="2026-10-10T16:30:00+09:00",budget=700)
        self.assertEqual(out["display_temporal_class"],"HISTORICAL_REPRINT_ONLY")
        self.assertEqual(out["display_paper_total_yen"],700)
        self.assertEqual(out["frozen_mec_capital_yen"],len(final["mec"]["tickets"])*100)
        for bad in (0,105,10001,"1000",True):
            with self.subTest(budget=bad),self.assertRaises(PracticalForecastError):
                self.forecast(pre,final,budget=bad)

    def test_candidate_non_oos_or_external_incomplete_never_displayed(self):
        pre,final=frozen_fixture()
        for k,v in (("oos_eligible",False),("candidate_final_verified",False),
                    ("acceptance_only",True),("production_effect","PRODUCTION")):
            bad=deepcopy(pre);bad[k]=v
            bad["sha256"]=digest({k:v for k,v in bad.items() if k!="sha256"})
            with self.subTest(k=k),self.assertRaises(PracticalForecastError):
                self.forecast(bad,final)

    def test_original_no_bet_is_not_overridden_by_hypothetical_display(self):
        pre,final=frozen_fixture()
        final["capital"]["no_bet"]=True
        final["sha256"]=digest({k:v for k,v in final.items() if k!="sha256"})
        out=self.forecast(pre,final)
        self.assertTrue(out["original_signed_candidate_final_no_bet"])
        self.assertEqual(out["display_scenario"],"MEC_HYPOTHETICAL_PAPER_SUBSET_OF_NO_BET")
        self.assertFalse(out["display_is_signed_final_ticket"])
        self.assertFalse(out["display_is_purchased_ticket"])
        self.assertFalse(out["new_final_generated"])
        self.assertEqual(out["display_paper_total_yen"],2000)


if __name__=="__main__":
    unittest.main()
