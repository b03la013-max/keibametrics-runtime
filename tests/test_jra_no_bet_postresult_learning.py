"""Source-bound JRA no-bet result-learning never becomes a PFS/prediction claim."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import json
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_jra_production_no_bet_terminal import fixtures, PRE
from jra_production_no_bet_terminal import build_no_bet_terminal, digest
from jra_no_bet_postresult_learning import (
    build_no_bet_learning,JRANoBetLearningError,_hash
)

SHA="a"*64

def build_input():
    req,report=fixtures()
    report["runner_universe"].append("3")
    report["partial_production_base_calculation"]["runners"]["3"]=deepcopy(
        report["partial_production_base_calculation"]["runners"]["2"]
    )
    report["partial_production_base_calculation"]["calculated_base_cells"]=3
    report["partial_production_base_calculation"]["blocked_base_cells"]=36
    terminal=build_no_bet_terminal(
        req,report,source_receipt_verified=True,created_at=PRE
    )
    result={
        "profile":"JRA-OFFICIAL-RESULT-DETAIL-v1",
        "official":True,"production_fact_authority":True,
        "result_derived":True,"runner_count":3,
        "runners":[
            {"runner_id":"2","horse_no":2,"finish":1},
            {"runner_id":"3","horse_no":3,"finish":2},
            {"runner_id":"1","horse_no":1,"finish":3},
        ],
    }
    result["sha256"]=_hash(result)
    result["source_snapshot_sha256"]=SHA
    result["race_no"]=5
    return terminal,result

def run(terminal,result):
    return build_no_bet_learning(
        terminal,result,race_no=5,acquired_at="2026-10-10T13:00:00+09:00",
        result_source_snapshot_sha256=SHA,official_capture_verified=True
    )

class TestZeroStakeOfficialResultLearning(unittest.TestCase):
    def test_closed_zero_bet_learns_availability_not_prediction_pfs(self):
        terminal,result=build_input()
        t,r=deepcopy((terminal,result))
        out=run(terminal,result)
        self.assertEqual((terminal,result),(t,r))
        self.assertEqual(out["official_top3"],["2","3","1"])
        self.assertEqual(out["decision_lineage_sha256"],terminal["sha256"])
        self.assertEqual(out["investment"],0)
        self.assertEqual(out["payout"],0)
        self.assertEqual(out["profit_loss"],0)
        self.assertIsNone(out["pfs"])
        self.assertFalse(out["eligible_for_market_superiority_promotion"])
        self.assertFalse(out["eligible_for_production_prediction_kpi"])
        self.assertFalse(out["signed_final_verified"])
        self.assertEqual(out["sha256"],digest({k:v for k,v in out.items() if k!="sha256"}))

    def test_unverified_capture_does_not_settle(self):
        t,r=build_input()
        with self.assertRaisesRegex(JRANoBetLearningError,"CAPTURE_NOT_VERIFIED"):
            build_no_bet_learning(t,r,race_no=5,
                acquired_at="2026-10-10T13:00:00+09:00",
                result_source_snapshot_sha256=SHA,
                official_capture_verified=False)

    def test_forged_final_or_no_bet_content_fails(self):
        t,r=build_input()
        bad=deepcopy(t);bad["signed_final_verified"]=True
        bad["sha256"]=digest({k:v for k,v in bad.items() if k!="sha256"})
        with self.assertRaisesRegex(JRANoBetLearningError,"TERMINAL_INVALID"):
            run(bad,r)
        bad=deepcopy(t);bad["tickets"]=[{"stake":100}]
        with self.assertRaises(JRANoBetLearningError):
            run(bad,r)

    def test_result_hash_and_universe_and_time_are_bound(self):
        t,r=build_input()
        for change in (
            lambda x:x.update(race_no=6),
            lambda x:x["runners"][0].update(finish=2),
            lambda x:x["runners"][0].update(runner_id="99"),
            lambda x:x.update(result_derived=False),
            lambda x:x.update(sha256="tampered"),
        ):
            with self.subTest(change=str(change)):
                bad=deepcopy(r);change(bad)
                with self.assertRaises(JRANoBetLearningError):
                    run(t,bad)
        with self.assertRaisesRegex(JRANoBetLearningError,"CHRONOLOGY"):
            build_no_bet_learning(t,r,race_no=5,
                acquired_at="2026-10-10T12:09:00+09:00",
                result_source_snapshot_sha256=SHA,
                official_capture_verified=True)

    def test_historical_no_bet_must_not_be_promoted_to_forward_oos(self):
        t,r=build_input()
        t["lineage"]="HISTORICAL_DIAGNOSTIC"
        t["sha256"]=digest({k:v for k,v in t.items() if k!="sha256"})
        with self.assertRaises(JRANoBetLearningError):
            run(t,r)

if __name__=="__main__":
    unittest.main()
