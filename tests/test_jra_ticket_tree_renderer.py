import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from jra_ticket_tree_renderer import render_ticket_tree, TicketTreeError


def art(tickets, decision="EXECUTE_RECOMMENDATION_PORTFOLIO", no_bet=False, ranking=("4", "2", "6", "10", "1")):
    return {"static_prediction": {"ranking": list(ranking)},
            "capital_policy_decision": {"decision": decision},
            "final_prediction_package": {"validation_status": "UNVALIDATED"},
            "final_ticket": {"no_bet": no_bet, "tickets": tickets}}


def t(bet, *sel, stake=100):
    return {"bet_type": bet, "selection": list(sel), "stake": stake}


class TestTree(unittest.TestCase):
    def test_formation_exact_and_rank_order(self):
        tk = [t("EXACTA", 4, s) for s in (10, 2, 6)] + [t("EXACTA", 2, 4)]
        out = render_ticket_tree(art(tk))
        txt = out["text"]
        self.assertNotIn("①", txt)
        # Not rectangular -> per-head blocks, 本線 first, order by ranking.
        self.assertIn("馬単（本線）\n1着\n└─ 4\n2着\n├─ 2\n├─ 6\n└─ 10", txt)
        self.assertIn("馬単（押さえ）\n1着\n└─ 2\n2着\n└─ 4", txt)
        self.assertIn("合計　4点", txt)
        self.assertIn("400円", txt)
        self.assertIn("未検証", txt)

    def test_head_swap_formation(self):
        tk = [t("TRIFECTA", a, b, c) for a in (4, 2) for b in (4, 2, 6) for c in (4, 2, 6, 10)
              if len({a, b, c}) == 3]
        txt = render_ticket_tree(art(tk))["text"]
        self.assertIn("三連単（頭入替）", txt)
        self.assertIn(f"三連単　{len(tk)}点", txt)

    def test_trio_unordered_and_no_bet(self):
        txt = render_ticket_tree(art([t("TRIO", 6, 4, 2)]))["text"]
        self.assertIn("三連複（本線）\n1列目\n└─ 4\n2列目\n└─ 2\n3列目\n└─ 6", txt)
        nb = render_ticket_tree(art([], decision="PAPER", no_bet=True))["text"]
        self.assertIn("見送り", nb)

    def test_duplicate_rejected(self):
        with self.assertRaises(TicketTreeError):
            render_ticket_tree(art([t("EXACTA", 4, 2), t("EXACTA", 4, 2)]))


if __name__ == "__main__":
    unittest.main()
