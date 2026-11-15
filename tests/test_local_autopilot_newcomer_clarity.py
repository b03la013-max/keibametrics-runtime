"""PAPER-only newcomer uncertainty cannot be mistaken for calibrated evidence."""
import unittest
from runtime.local_autopilot.run import paper_identifiability, render


def scenario(f3s=(51.0, 51.0), p=(0.5, 0.5), newcomers=2):
    order = []
    for no in (1, 2):
        order.append({
            "mark": "◎" if no == 1 else "○", "no": no, "name": f"test{no}",
            "jockey": "test", "win": None, "TPIF": 48.0, "SRI": 52.0,
            "EVI": 52.0, "NCI": 52.0, "T3I": 52.0, "F3S": f3s[no-1],
            "OPI": 52.0, "p_win": p[no-1], "role": "1着候補"
        })
    race = {
        "venue_name": "水沢", "race_no": 1, "post_current": "2026-11-15T11:45:00+09:00",
        "race_name": "新馬戦", "distance": 850, "newcomers": newcomers
    }
    pred = {
        "rows": [{"flags": []}, {"flags": []}], "order": order,
        "pace": "不明", "race_type": "未識別",
        "wci": 0, "fuan": -12, "fuan_reasons": ["過去走なし"],
        "reversal": 1, "gate": "不安あり", "tan_ev": None, "quad": 4,
        "aki": {"W": 0, "P": 0, "ASI": 0, "RSI": 0, "katai": 0,
                "total": 0, "type": "A", "form": "1-2-4"},
        "checks": {}, "tickets": [
            {"k": "ワイド", "b": "1-2", "pt": 1, "st": "小", "note": "test"}
        ]
    }
    return race, pred


class PaperNewcomerClarityTest(unittest.TestCase):
    def test_equal_newcomers_are_explicitly_unidentifiable(self):
        race, pred = scenario()
        original_tickets = [dict(t) for t in pred["tickets"]]
        self.assertEqual(paper_identifiability(race, pred), "ALL_NEWCOMER_TIE")
        output = render(race, pred, "朝版", "2026-11-14T21:02:00+09:00")
        self.assertIn("PAPER判定留保／NO-BET推奨", output)
        self.assertIn("| ワイド | 1-2 | 1 |", output)
        self.assertEqual(pred["tickets"], original_tickets)

    def test_all_newcomers_with_differences_still_show_low_evidence(self):
        race, pred = scenario(f3s=(51.0, 52.0), p=(0.45, 0.55))
        self.assertEqual(paper_identifiability(race, pred), "ALL_NEWCOMER_LOW_EVIDENCE")
        output = render(race, pred, "朝版", "2026-11-14T21:02:00+09:00")
        self.assertIn("PAPER低識別力", output)
        self.assertNotIn("PAPER判定留保／NO-BET推奨", output)

    def test_mixed_field_does_not_get_all_newcomer_warning(self):
        race, pred = scenario(newcomers=1)
        self.assertEqual(paper_identifiability(race, pred), "NOT_ALL_NEWCOMERS")
        output = render(race, pred, "朝版", "2026-11-14T21:02:00+09:00")
        self.assertNotIn("PAPER判定留保／NO-BET推奨", output)
        self.assertNotIn("PAPER低識別力", output)


if __name__ == "__main__":
    unittest.main()
