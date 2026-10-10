"""Synthetic observed-layout tests. No paid data or login fixture in git."""
from copy import deepcopy
from pathlib import Path
import json
import tempfile
from unittest.mock import patch
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from jra_bloodb_browser_bridge import snapshot_rows, evaluate_snapshot, evaluate_race
from jra_bloodb_mac_collector import BloodBError, parse_rendered
from jra_bloodb_mac_automation import discover_links, discover_race_url

HEAD = ["馬番", "馬名", "人気ランク", "推定人気", "相対指数", "血統評価", "CR", "GR",
        "血統タイプ", "前走ローテ", "異種", "父小系統", "母父小系統",
        "父母父小系統母母父小系統", "間隔", "前走", "間隔", "２走前", "間隔", "３走前", "騎手斤量", "調教師性齢"]
OFFICIAL = [{"horse_no": "1", "horse_name": "合成馬甲"}, {"horse_no": "2", "horse_name": "合成馬乙"}]


def fixture():
    rows = []
    for no, name in [("1", "合成馬甲"), ("2", "合成馬乙")]:
        cells = [no, name] + [""] * 23
        cells[2:6] = ["B", "1", "60", "注"]
        cells[8:12] = ["1", "2", "3", "4"]
        cells[14:17] = ["父表示\n父系", "母父表示\n母父系", "系統甲\n系統乙"]
        rows.append({"cells": cells, "links": [{"text": name, "url": f"https://www.blood-b.com/hinfo?hcode=202400000{no}"}]})
    return {"source": "https://www.blood-b.com/main.php?rcode=2026101105040401",
            "captured_at": "2026-10-10T14:00:00+00:00", "rows": rows}


def html():
    top = "<tr>" + "".join(f'<td colspan="4">{x}</td>' if x == "血統タイプ"
                             else f'<td rowspan="2">{x}</td>' for x in HEAD) + "</tr>"
    sub = "<tr>" + "".join(f"<td>{x}</td>" for x in "WPST") + "</tr>"
    body = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r["cells"]) + "</tr>" for r in fixture()["rows"])
    return "<table><tbody>" + top + sub + body + "</tbody></table>"


class BridgeTests(unittest.TestCase):
    def test_observed_td_two_tier_header(self):
        result = parse_rendered(html(), OFFICIAL)
        self.assertEqual(result["horse_count"], 2)
        row = result["observations"][0]
        self.assertEqual(row["observed_labels"]["血統タイプ"], "1 | 2 | 3 | 4")
        self.assertEqual(row["observed_labels"]["父小系統"], "父表示\n父系")

    def test_number_mismatch_and_broken_subheader(self):
        for h in [html().replace("<td>1</td><td>合成馬甲", "<td>2</td><td>合成馬甲"),
                  html().replace("<td>W</td>", "<td>?</td>")]:
            with self.assertRaises(BloodBError):
                parse_rendered(h, OFFICIAL)

    def test_snapshot_no_source_never_generates_bvi(self):
        r = evaluate_snapshot({"races": [fixture()]}, root=Path("/no-sources"))
        self.assertEqual(r["blocked_bvi_count"], 2)
        self.assertEqual(r["calculated_bvi_count"], 0)
        self.assertFalse(r["bvi_authority"])
        self.assertTrue(all(x["value"] is None for x in r["races"][0]["bvi"].values()))

    def test_snapshot_tamper_and_duplicate(self):
        for mutation in ["width", "name", "id", "url", "time", "duplicate"]:
            r = deepcopy(fixture())
            if mutation == "width": r["rows"][0]["cells"].pop()
            if mutation == "name": r["rows"][0]["cells"][1] = "別馬"
            if mutation == "id": r["rows"][0]["links"][0]["url"] = "https://other.invalid/hinfo?hcode=2024000001"
            if mutation == "url": r["source"] = "https://other.invalid/main.php?rcode=2026101105040401"
            if mutation == "time": r["captured_at"] = "2026-10-10T14:00:00"
            if mutation == "duplicate": r["rows"].append(r["rows"][0])
            with self.assertRaises(BloodBError): snapshot_rows(r)

    def test_venue_from_table_heading_not_numeric_code(self):
        h = '<table><tr><td>4回東京4日目</td></tr><tr><td><a href="/main.php?rcode=2026101105040401">1R</a></td></tr></table>'
        rows = discover_links(h, date_text="2026-10-11", race_no=1, venue="東京")
        self.assertEqual(rows[0]["observed_venue"], "東京")
        self.assertEqual(discover_links(h, date_text="2026-10-11", race_no=1, venue="京都"), [])

    def test_real_day_link_navigation(self):
        index = '<a href="/racesel?rdate=20261011">10月11日</a>'
        detail = '<table><tr><td>4回東京4日目</td></tr><tr><td><a href="/main.php?rcode=2026101105040401">1R</a></td></tr></table>'
        class Page:
            def goto(self, url, **kw):
                self.url = url
                self.raw = detail if "/racesel?" in url else index
                return type("Response", (), {"status": 200})()
            def content(self): return self.raw
            def close(self): pass
        class Browser:
            def new_page(self): return Page()
        self.assertEqual(discover_race_url(Browser(), date_text="2026-10-11", race_no=1, venue="東京"),
                         "https://www.blood-b.com/main.php?rcode=2026101105040401")

    def test_existing_production_formula_without_paid_label_injection(self):
        # Isolated boundary mocks only; this does not claim live JRA signing.
        art = {"race_id": "KM-JRA-TKY-20261011-R01", "source_race_context": {
            "race_date": "2026-10-11", "venue_id": "TKY", "race_no": 1},
            "source_freeze_at": "2026-10-10T13:00:00+00:00",
            "prediction_cutoff": "2026-10-11T00:55:00+00:00"}
        feats = {name: {"category": category, "rule_id": "SYNTHETIC-UNIT-RULE",
                       "evidence_refs": ["SYNTHETIC-UNIT-FACT"], "source_fact": "synthetic"}
                 for name, category in [("pedigree_surface", "STRONG"), ("pedigree_distance", "POSITIVE")]}
        compiled = {"pedigree_corpus_manifest": {"synthetic": True}, "runners": {
            rid: {"factual_runner_updates": {"career_starts": 5, "newcomer": False},
                  "generated_production_features": deepcopy(feats)} for rid in ["1", "2"]}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.json"
            path.write_text(json.dumps({"artifact": art}))
            with patch("jra_bloodb_browser_bridge._verified_source", return_value={"valid": True}), \
                 patch("jra_bloodb_browser_bridge.load_official", return_value=(OFFICIAL, {})), \
                 patch("jra_bloodb_browser_bridge._attested", return_value=False), \
                 patch("jra_bloodb_browser_bridge.compile_source_to_features", return_value=compiled) as compiler:
                result = evaluate_race(fixture(), root=ROOT, source_path=path)
                expected = round((82 * .30 + 74 * .24) / .54, 6)
                self.assertEqual(result["bvi"]["1"]["value"], expected)
                self.assertFalse(result["bvi_authority"])
                self.assertEqual(compiler.call_args.args[0], art)
                # Blood-B can change while JRA-generated BVI stays identical.
                changed = fixture(); changed["rows"][0]["cells"][5] = "9999"
                self.assertEqual(evaluate_race(changed, root=ROOT, source_path=path)["bvi"], result["bvi"])
                wrong = fixture(); wrong["rows"][0]["cells"][0] = "3"
                with self.assertRaisesRegex(BloodBError, "UNIVERSE_MISMATCH"):
                    evaluate_race(wrong, root=ROOT, source_path=path)
                late = fixture(); late["captured_at"] = art["prediction_cutoff"]
                with self.assertRaisesRegex(BloodBError, "TEMPORAL_BINDING"):
                    evaluate_race(late, root=ROOT, source_path=path)
                compiled["runners"]["1"]["generated_production_features"] = {}
                held = evaluate_race(fixture(), root=ROOT, source_path=path)
                self.assertIsNone(held["bvi"]["1"]["value"])
                self.assertEqual(held["status"], "PARTIAL_DIAGNOSTIC")


if __name__ == "__main__": unittest.main()
