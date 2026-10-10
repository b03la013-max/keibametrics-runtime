"""Offline contract tests for real-page structure diagnostics (never log in)."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(ROOT / "scripts"))

from jra_bloodb_mac_probe import probe_context, safe_structure
from jra_bloodb_mac_collector import BloodBError
from jra_bloodb_mac_acceptance import queue_spec
from jra_bloodb_signed_source_queue_sync import synchronize
from test_jra_bloodb_signed_source_queue_sync import fixture, NOW, RACE
from test_jra_bloodb_mac_automation import FakeBrowser
from test_jra_bloodb_mac_collector import HTML

INDEX = """<html><body><nav><div>京都 9R
<a href="/main.php?rcode=2026101101010609">9R 京都の出馬表</a>
</div></nav></body></html>"""
DETAIL = (HTML.replace("テストホース一号","血統テスト一号")
              .replace("テストホース二号","血統テスト二号"))
OFFICIAL = [{"horse_no":1,"name":"血統テスト一号"},
            {"horse_no":2,"name":"血統テスト二号"}]


def prepared(root: Path) -> dict:
    fixture(root)
    queue = root / "private" / "bloodb_queue.json"
    synchronize(root, queue, now=NOW)
    return queue_spec(queue, RACE)


class ProbeTests(unittest.TestCase):
    def test_genuine_signed_source_and_full_member_schema_no_paid_value_leakage(self):
        with tempfile.TemporaryDirectory() as folder:
            spec = prepared(Path(folder))
            result = probe_context(FakeBrowser(html=INDEX,detail=DETAIL),spec,clock=lambda: NOW)
            self.assertEqual(result["status"], "LOCAL_MEMBER_DOM_SCHEMA_COMPATIBLE")
            self.assertEqual(result["official_runner_count"],2)
            self.assertEqual(result["matched_runner_count"],2)
            self.assertEqual(result["observed_race_link_count"],1)
            self.assertEqual(result["parser_status"], "FULL_RUNNER_SCHEMA_MATCH")
            self.assertEqual(result["detail"]["tables_total"],1)
            self.assertEqual(result["detail"]["table_shapes"][0]["column_headers"],
                             ["馬名","血統評価","血統タイプ","相対指数","ローテ評価"])
            self.assertFalse(result["production_authority"])
            self.assertFalse(result["paid_content_persisted"])
            self.assertEqual(result["oos_increment"],0)
            report=json.dumps(result,ensure_ascii=False)
            for secret in ("血統テスト一号","血統テスト二号","タイプA","タイプB","72","65"):
                self.assertNotIn(secret,report)

    def test_no_link_still_reports_private_safe_page_structure(self):
        with tempfile.TemporaryDirectory() as folder:
            spec = prepared(Path(folder))
            result = probe_context(FakeBrowser(html="<html><div>会員のメニューのみ</div></html>"),
                                   spec,clock=lambda: NOW)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(result["observed_race_link_count"],0)
            self.assertEqual(result["block_reason"],"BLOODB_RACE_LINK_MISSING_OR_AMBIGUOUS")
            self.assertEqual(result["index"]["div"],1)
            self.assertIsNone(result["detail"])

    def test_dynamic_div_detail_does_not_fabricate_runner_coverage(self):
        with tempfile.TemporaryDirectory() as folder:
            spec = prepared(Path(folder))
            detail = """<html><div class="horse-data"><span>血統テスト一号</span>
                      <span>72</span></div><div>血統テスト二号</div></html>"""
            result = probe_context(FakeBrowser(html=INDEX,detail=detail),
                                   spec,clock=lambda: NOW)
            self.assertEqual(result["status"],"BLOCKED")
            self.assertEqual(result["parser_status"],"UNSUPPORTED_OR_INCOMPLETE")
            self.assertEqual(result["detail"]["tables_total"],0)
            self.assertEqual(result["detail"]["div"],2)
            self.assertEqual(result["block_reason"],"BLOODB_RUNNER_COVERAGE_UNVERIFIED")
            self.assertNotIn("72",json.dumps(result,ensure_ascii=False))

    def test_missing_source_and_cutoff_cannot_be_diagnostic_success(self):
        with tempfile.TemporaryDirectory() as folder:
            spec = prepared(Path(folder))
            broken=dict(spec, jra_signed_source_artifact_sha256="0"*64)
            with self.assertRaisesRegex(BloodBError,"HASH_MISMATCH"):
                probe_context(FakeBrowser(html=INDEX,detail=DETAIL),
                              broken,clock=lambda: NOW)
            with self.assertRaisesRegex(BloodBError,"CUTOFF_EXPIRED"):
                probe_context(FakeBrowser(html=INDEX,detail=DETAIL),
                              spec, clock=lambda: datetime.fromisoformat("2026-10-11T14:00:00+09:00"))

    def test_login_and_ambiguous_venue_are_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            spec = prepared(Path(folder))
            login = probe_context(FakeBrowser(html="<html><input type=password></html>"),
                                  spec, clock=lambda: NOW)
            self.assertEqual(login["block_reason"],"BLOODB_LOGIN_REQUIRED")
            self.assertEqual(login["observed_race_link_count"],0)
            index=INDEX.replace("京都 9R","東京 9R").replace("京都の出馬表","東京の出馬表")
            wrong=probe_context(FakeBrowser(html=index), spec,clock=lambda: NOW)
            self.assertEqual(wrong["status"],"BLOCKED")
            self.assertEqual(wrong["observed_race_link_count"],0)

    def test_header_is_schema_only_and_horse_name_column_is_redacted(self):
        html="<table><tr><th>馬名</th><th>血統テスト一号</th></tr><tr><td>血統テスト一号</td><td>72</td></tr></table>"
        s=safe_structure(html,OFFICIAL)
        self.assertEqual(s["table_shapes"][0]["column_headers"],["馬名","[REDACTED_OR_NOT_COLUMN]"])
        self.assertNotIn("72",json.dumps(s,ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
