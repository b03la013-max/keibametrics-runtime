import copy
import unittest
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))

from post_result_learning import LearningError, build_post_result_review, build_learning_state


def inputs(capture=(True, False, False), paper=False):
    roles={str(i):([r] if yes else []) for i,r,yes in zip((1,2,3),("W","P2","P3"),capture)}
    tickets=[] if paper else [{"bet_type":"EXACTA","selection":[1,2],"stake":100}]
    final={"family_id":"JRA","race_id":"KM-JRA-TKY-20261031-R08",
           "final_prediction_package":{"roles":roles,"ranking":["1","2","3"]},
           "final_ticket":{"tickets":tickets,"total_investment":0 if paper else 100,"no_bet":paper},
           "capital_policy_decision":{"decision":"PAPER" if paper else "EXECUTE_FULL_MEC"}}
    result={"race_id":final["race_id"],"official_result":{"top3":[1,2,3]},
            "settlement":{"status":"COMPLETE","total_investment":0 if paper else 100,"total_payout":0}}
    return result,final


class LearningV3Tests(unittest.TestCase):
    def test_secondary_p3_and_p2_survive_without_false_winner_route(self):
        r,f=inputs();review=build_post_result_review(r,f,review_semantics="DECISION_AWARE_V3")
        state=build_learning_state(review,effective_time="2026-11-01T00:00:00+09:00")
        self.assertEqual(review["failure_localization"]["first_material_failure"],"PREDICTION_ROLE_P2")
        self.assertEqual(review["failure_localization"]["secondary_independent_role_failures"],["PREDICTION_ROLE_P3"])
        self.assertNotIn("WINNER_ROLE_MIGRATION",state["shadow_candidates"])
        self.assertIn("HEAD_LOCAL_P2_REAUDIT",state["shadow_candidates"])
        self.assertIn("PAIR_CONDITIONED_THIRD_REAUDIT",state["shadow_candidates"])
        self.assertEqual(state["prediction_use"],"SHADOW_REVIEW_CONTEXT_ONLY")

    def test_w_and_secondary_failures_are_all_preserved(self):
        r,f=inputs((False,False,False));v=build_post_result_review(r,f,review_semantics="DECISION_AWARE_V3")
        self.assertEqual(v["failure_localization"]["independent_role_failures"],["PREDICTION_ROLE_W","PREDICTION_ROLE_P2","PREDICTION_ROLE_P3"])
        self.assertTrue(v["failure_localization"]["dependent_conversion_failures"])
        self.assertFalse(v["failure_localization"]["independent_conversion_failures"])

    def test_pair_success_is_preserved(self):
        r,f=inputs((True,True,True));v=build_post_result_review(r,f,review_semantics="DECISION_AWARE_V3")
        self.assertTrue(v["conversion"]["ordered_pair_ticket_coverage"])
        self.assertNotIn("ORDERED_PAIR_CONVERSION",v["failure_localization"]["independent_conversion_failures"])

    def test_missing_pair_does_not_create_independent_exact_failure(self):
        r,f=inputs((True,True,True));f['final_ticket']['tickets'][0]['selection']=[2,1]
        v=build_post_result_review(r,f,review_semantics="DECISION_AWARE_V3")
        self.assertIn("ORDERED_PAIR_CONVERSION",v["failure_localization"]["independent_conversion_failures"])
        self.assertIn("EXACT_ORIENTATION",v["failure_localization"]["dependent_conversion_failures"])
        self.assertNotIn("EXACT_ORIENTATION",v["failure_localization"]["independent_conversion_failures"])

    def test_paper_has_no_capital_failure_or_pfs_zero(self):
        r,f=inputs((True,True,True),True);v=build_post_result_review(r,f,review_semantics="DECISION_AWARE_V3")
        self.assertIsNone(v["capital"]["pfs"])
        self.assertEqual(v["capital"]["status"],"NOT_APPLICABLE_PAPER")
        self.assertFalse(v["failure_localization"]["independent_conversion_failures"])

    def test_v3_rejects_other_family(self):
        r,f=inputs();f["family_id"]="LOCAL"
        with self.assertRaisesRegex(LearningError,"JRA_ONLY"):
            build_post_result_review(r,f,review_semantics="DECISION_AWARE_V3")

    def test_default_and_v2_not_rewritten(self):
        r,f=inputs();a=build_post_result_review(r,f);b=build_post_result_review(r,f,review_semantics="LEGACY")
        self.assertEqual(a,b)
        v2=build_post_result_review(r,f,review_semantics="DECISION_AWARE_V2")
        self.assertNotIn("independent_role_failures",v2["failure_localization"])
        self.assertIn("WINNER_ROLE_MIGRATION",v2["pfs_improvement"]["test_next_tracks"])

    def test_dead_heat_role_any_does_not_imply_joint_conversion_eligibility(self):
        r,f=inputs((True,True,True))
        f['final_prediction_package']['roles']={'1':['W','P2'],'2':[],'3':['P3'],'4':['P2']}
        f['final_ticket']['tickets'][0]['selection']=[1,4]
        r['official_result'].update(top3=[1,2,3],top3_orders=[[1,2,3],[2,1,3]],
            finish_groups=[{'finish':1,'horse_numbers':[1,2]},{'finish':3,'horse_numbers':[3]}])
        v=build_post_result_review(r,f,review_semantics="DECISION_AWARE_V3")
        self.assertTrue(all(v['prediction']['role_capture'].values()))
        self.assertFalse(v['failure_localization']['joint_pair_role_capture_any_valid_order'])
        self.assertFalse(v['failure_localization']['joint_all_role_capture_any_valid_order'])
        self.assertEqual(v['failure_localization']['independent_conversion_failures'],[])
        self.assertEqual(v['failure_localization']['dependent_conversion_failures'],
                         ['ORDERED_PAIR_CONVERSION','THIRD_SET_COVERAGE','EXACT_ORIENTATION'])
        state=build_learning_state(v)
        self.assertNotIn('ORDERED_PAIR_CONVERSION',state['shadow_candidates'])
        self.assertNotIn('PAIR_RESIDUAL',state['shadow_candidates'])

    def test_inputs_immutable(self):
        r,f=inputs();before=copy.deepcopy((r,f));build_post_result_review(r,f,review_semantics="DECISION_AWARE_V3")
        self.assertEqual((r,f),before)

    def test_v4_trio_hit_survives_ordered_winner_miss(self):
        r, f = inputs((False, True, True))
        f["final_prediction_package"]["roles"]["1"] = ["P3"]
        trio = {"bet_type": "TRIO", "selection": [3, 1, 2], "stake": 100}
        f["minimum_efficient_coverage"] = {
            "coverage_units": [{"kind": "TAIL_SET", "parts": ["1", "2", "3"]}],
            "tickets": [trio],
        }
        f["final_ticket"]["tickets"].append(trio)
        f["final_ticket"]["total_investment"] = 200
        r["settlement"].update(total_investment=200, total_payout=180, refund=0,
                               winning_tickets=[{**trio, "return": 180}])
        old = build_post_result_review(r, f, review_semantics="DECISION_AWARE_V3")
        new = build_post_result_review(r, f, review_semantics="DECISION_AWARE_V4")
        for key in old.keys() - {"review_semantics", "sha256"}:
            self.assertEqual(new[key], old[key])
        state = build_learning_state(new)
        self.assertEqual(state["source_review_sha256"], new["sha256"])
        self.assertEqual(state["reference_metrics"]["trio_reachability"]["trio_pfs"], 180)
        reach = new["trio_reachability"]
        self.assertEqual(reach["trio_profit_loss"], 80)
        self.assertEqual(reach["by_valid_unordered_set"][0]["first_trio_failure"], "NONE")
        self.assertEqual(new["failure_localization"]["first_material_failure"], "PREDICTION_ROLE_W")

    def test_v4_ordered_set_is_evidence_without_trio_candidate(self):
        r, f = inputs((True, True, True))
        ordered = {"bet_type": "TRIFECTA", "selection": [2, 1, 3], "stake": 100}
        f["minimum_efficient_coverage"] = {
            "coverage_units": [{"kind": "EXACT_THIRD", "parts": ["2", "1", "3"]}],
            "tickets": [ordered],
        }
        f["final_ticket"].update(tickets=[ordered], total_investment=100)
        review = build_post_result_review(r, f, review_semantics="DECISION_AWARE_V4")
        trio = review["trio_reachability"]["by_valid_unordered_set"][0]
        self.assertTrue(review["conversion"]["top3_set_ticket_coverage"])
        self.assertFalse(trio["final_trio_ticket_coverage"])
        self.assertFalse(trio["mec_trio_candidate_reachable"])
        self.assertEqual(trio["mec_joint_set_evidence"], ["EXACT_THIRD"])
        self.assertEqual(trio["first_trio_failure"], "MEC_TRIO_NOT_GENERATED")

    def test_v4_dead_heat_preserves_each_unordered_set_and_refund(self):
        r, f = inputs((True, True, True))
        r["official_result"].update(
            top3_orders=[[1, 2, 3], [1, 2, 4]],
            finish_groups=[{"finish": 1, "horse_numbers": [1]},
                           {"finish": 2, "horse_numbers": [2]},
                           {"finish": 3, "horse_numbers": [3, 4]}],
        )
        tickets = [{"bet_type": "TRIO", "selection": [1, 2, x], "stake": 100}
                   for x in (3, 4, 5)]
        f["final_ticket"].update(tickets=tickets, total_investment=300)
        r["settlement"].update(
            total_investment=300, total_payout=180, refund=100,
            winning_tickets=[{**tickets[0], "return": 110}, {**tickets[1], "return": 70}],
            refunded_tickets=[{**tickets[2], "refund": 100}],
        )
        reach = build_post_result_review(r, f, review_semantics="DECISION_AWARE_V4")["trio_reachability"]
        self.assertEqual(reach["effective_trio_investment"], 200)
        self.assertEqual(reach["trio_pfs"], 90)
        self.assertEqual(reach["shared_final_trio_ticket_members"], [1, 2])
        self.assertEqual([row["settled_trio_return"] for row in reach["by_valid_unordered_set"]], [110, 70])
        self.assertTrue(all(row["all_shared_ticket_members_survive"]
                            for row in reach["by_valid_unordered_set"]))

    def test_v4_paper_retains_prediction_evidence_without_pfs(self):
        r, f = inputs((True, True, True), paper=True)
        reach = build_post_result_review(r, f, review_semantics="DECISION_AWARE_V4")["trio_reachability"]
        self.assertIsNone(reach["trio_pfs"])
        self.assertEqual(reach["by_valid_unordered_set"][0]["first_trio_failure"],
                         "NOT_APPLICABLE_ZERO_EXPOSURE")


if __name__=="__main__":unittest.main()
