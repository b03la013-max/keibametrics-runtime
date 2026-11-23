import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from world_coverage import Ticket, world, candidate_tickets, coverage, optimize, brute_force, worlds_from_frozen


class CoverageTests(unittest.TestCase):
    def test_world_rejects_repeat_and_invalid_identity(self):
        for value in [(1, 1, 2), (True, 2, 3), (0, 2, 3), (1, 19, 3), (1, 2)]:
            with self.subTest(value=value), self.assertRaises((ValueError, TypeError)):
                world(value)

    def test_trio_does_not_claim_ordered_pair_or_exact(self):
        ws = ((1, 2, 3), (3, 2, 1))
        measured = coverage([Ticket("TRIO", (3, 1, 2))], ws)
        self.assertEqual(measured["ANY_WIN"], 2)
        self.assertEqual(measured["TOP3_SET"], 2)
        self.assertEqual(measured["ORDERED_PAIR"], 0)
        self.assertEqual(measured["EXACT_TRIPLE"], 0)

    def test_exact_direction_and_pair_third_are_not_interchangeable(self):
        ws = ((1, 2, 3), (1, 2, 4), (2, 1, 3))
        self.assertEqual(coverage([Ticket("EXACTA", (1, 2))], ws)["ANY_WIN"], 2)
        self.assertEqual(coverage([Ticket("TRIFECTA", (1, 2, 3))], ws)["EXACT_TRIPLE"], 1)

    def test_solver_matches_exhaustive_small_cases(self):
        ws = ((1, 2, 3), (1, 3, 2), (3, 1, 2), (1, 2, 4))
        for mode in ("ANY_WIN", "ORDERED_PAIR", "TOP3_SET", "EXACT_TRIPLE"):
            ts = candidate_tickets(ws)
            for budget in (None, 0, 100, 200, 300):
                with self.subTest(mode=mode, budget=budget):
                    oracle = brute_force(ws, ts, mode=mode, budget=budget)
                    result = optimize(ws, ts, mode=mode, budget=budget)
                    self.assertTrue(result["optimal"])
                    key = ((result["cost"],) if budget is None else
                           (-result["importance_covered"], result["cost"]))
                    self.assertEqual(key, oracle[0])

    def test_full_exact_protection_can_exceed_same_budget(self):
        ws = ((1, 2, 3), (3, 2, 1))
        ts = candidate_tickets(ws)
        minimum = optimize(ws, ts, mode="EXACT_TRIPLE")
        capped = optimize(ws, ts, mode="EXACT_TRIPLE", budget=100)
        self.assertEqual(minimum["cost"], 200)
        self.assertEqual(capped["coverage"]["EXACT_TRIPLE"], 1)
        self.assertLessEqual(capped["cost"], 100)

    def test_uniform_importance_does_not_force_budget_spending(self):
        ws = ((1, 2, 3), (3, 2, 1))
        result = optimize(ws, candidate_tickets(ws), mode="TOP3_SET", budget=10000)
        self.assertEqual(result["cost"], 100)

    def test_no_future_result_can_enter_selection(self):
        with self.assertRaises(TypeError):
            optimize(((1, 2, 3),), (), mode="ANY_WIN", actual_top3=(1, 2, 3))

    def test_frozen_worlds_keep_head_and_pair_conditioned_third(self):
        final = {"final_prediction_package": {"roles": {"1": ["W"], "2": ["P2"], "3": ["P3"], "4": ["P3"]}},
                 "pair_dispositions": [{"head": "1", "second": "2", "status": "PURCHASE"}],
                 "third_dispositions": [{"head": "1", "second": "2", "third": "3", "status": "PURCHASE"},
                                        {"head": "1", "second": "2", "third": "4", "status": "EXCLUDED"}]}
        saved = copy.deepcopy(final)
        ws = worlds_from_frozen(final)
        self.assertEqual(ws, ((1, 2, 3),))
        self.assertEqual(final, saved)
        # A horse outside W cannot be rescued by ticket selection alone.
        self.assertFalse(any(w[0] == 3 for w in ws))

    def test_float_precision_boundary_is_rejected_not_called_optimal(self):
        ws = ((1, 2, 3), (3, 2, 1))
        ts = candidate_tickets(ws, ("TRIFECTA",))
        with self.assertRaisesRegex(ValueError, "INTEGER_RANGE"):
            optimize(ws, ts, mode="EXACT_TRIPLE", budget=100,
                     weights={ws[0]: 2**54, ws[1]: 2**54 + 1})
        with self.assertRaisesRegex(ValueError, "BUDGET_INVALID"):
            optimize(ws, ts, mode="EXACT_TRIPLE", budget=2**54 * 100)
        with self.assertRaisesRegex(ValueError, "INTEGER_RANGE"):
            optimize(ws, (Ticket("TRIFECTA", ws[0], 2**54 * 100),), mode="EXACT_TRIPLE")

    def test_predefined_integer_importance_is_used_before_cost_tie_break(self):
        ws = ((1, 2, 3), (3, 2, 1))
        ts = candidate_tickets(ws, ("TRIFECTA",))
        out = optimize(ws, ts, mode="EXACT_TRIPLE", budget=100,
                       weights={ws[0]: 1, ws[1]: 2})
        self.assertEqual(out["tickets"], (Ticket("TRIFECTA", ws[1]),))
        self.assertEqual(out["importance_covered"], 2)

    def test_protected_orientation_scope_is_opt_in_not_production_promotion(self):
        final = {"final_prediction_package": {"roles": {"1": ["W"], "2": ["P2"], "3": ["P3"]}},
                 "pair_dispositions": [{"head": "1", "second": "2", "status": "PURCHASE"}],
                 "third_dispositions": [{"head": "1", "second": "2", "third": "3", "status": "PROTECT"}]}
        self.assertEqual(worlds_from_frozen(final), ())
        self.assertEqual(worlds_from_frozen(final, include_protected=True), ((1, 2, 3),))
        final["third_dispositions"][0]["status"] = "EXCLUDED"
        self.assertEqual(worlds_from_frozen(final, include_protected=True), ())

    def test_tie_break_timeout_without_incumbent_is_not_optimal(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        import numpy as np
        ws = ((1, 2, 3), (3, 2, 1))
        ts = candidate_tickets(ws, ("TRIFECTA",))
        first = SimpleNamespace(status=0, x=np.array([1, 0, 1, 0]))
        second = SimpleNamespace(status=1, x=None)
        with patch("scipy.optimize.milp", side_effect=[first, second]):
            out = optimize(ws, ts, mode="EXACT_TRIPLE", budget=100)
        self.assertFalse(out["optimal"])
        self.assertEqual(out["second_solver_status"], 1)
        self.assertFalse(out["minimum_spend_tie_break_proven"])
        self.assertEqual(out["status"], "FEASIBLE_LIMIT_NOT_OPTIMAL")
        self.assertEqual(out["cost"], 100)

    def test_invalid_budget_weights_kind_and_duplicate_rejected(self):
        ws = ((1, 2, 3),)
        ts = candidate_tickets(ws)
        for kwargs in ({"budget": -100}, {"budget": 99}, {"weights": {ws[0]: .2}},
                       {"weights": {ws[0]: 0}}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                optimize(ws, ts, mode="ANY_WIN", **kwargs)
        with self.assertRaises(ValueError):
            Ticket("WIN", (1,))
        with self.assertRaises(ValueError):
            optimize(ws, (ts[0], ts[0]), mode="ANY_WIN")


if __name__ == "__main__":
    unittest.main()

