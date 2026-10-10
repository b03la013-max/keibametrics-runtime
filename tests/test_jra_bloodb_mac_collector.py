"""Tests for BloodB Mac collector: offline synthetic HTML, no subscriber access."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))
from jra_bloodb_mac_collector import (
    BloodBError,allowed_page,parse_rendered,capture_context,check_page_actual,
    official_universe
)

OFFICIAL=[{"runner_id":"1","name":"テストホース一号"},
          {"runner_id":"2","name":"テストホース二号"}]
URL="https://www.blood-b.com/main.php?rcode=2026080901010601"
HTML='''<html><body><h1>中央競馬 出馬表</h1><table>
<tr><th>馬名</th><th>血統評価</th><th>血統タイプ</th><th>相対指数</th><th>ローテ評価</th></tr>
<tr><td><a>テストホース一号</a></td><td>血</td><td>タイプA</td><td>72</td><td>良</td></tr>
<tr><td><a>テストホース二号</a></td><td>優</td><td>タイプB</td><td>65</td><td>普通</td></tr>
</table></body></html>'''

class Page:
    def __init__(self, html=HTML, status=200, url=URL):
        self.html,self.status,self.url=html,status,url
        self.closed=False
    def goto(self,url,**kwargs):
        return type("Response",(),{"status":self.status})()
    def content(self):
        return self.html
    def close(self):
        self.closed=True

class Context:
    def __init__(self, **kwargs):
        self.page=Page(**kwargs)
    def new_page(self):
        return self.page

class TestBloodBPrivate(unittest.TestCase):
    def test_url_allowlist_and_no_redirect(self):
        self.assertEqual(allowed_page("https://www.blood-b.com/allsel"),
                         "https://www.blood-b.com/allsel")
        self.assertEqual(allowed_page(URL),URL)
        for bad in ("http://www.blood-b.com/allsel",
                    "https://attacker.example.com/allsel",
                    "https://www.blood-b.com/wp/login/",
                    "https://www.blood-b.com/main.php?rcode=xxx",
                    "https://www.blood-b.com/main.php?rcode=2026080901010601&mode=admin"):
            with self.subTest(bad=bad):
                with self.assertRaises(BloodBError):
                    allowed_page(bad)
        with self.assertRaisesRegex(BloodBError,"REDIRECT"):
            check_page_actual("https://www.blood-b.com/wp/login/",URL)

    def test_exact_names_and_explicit_columns(self):
        result=parse_rendered(HTML,OFFICIAL)
        self.assertEqual(result["horse_count"],2)
        self.assertIn("血統評価",result["observed_labels"])
        self.assertEqual(result["observations"][0]["observed_labels"]["相対指数"],"72")
        self.assertEqual(result["observations"][1]["horse_no"],"2")
        with self.assertRaisesRegex(BloodBError,"COVERAGE"):
            parse_rendered(HTML.replace("テストホース二号","別馬"),OFFICIAL)
        with self.assertRaisesRegex(BloodBError,"LOGIN"):
            parse_rendered('<form><input type="password"></form>',OFFICIAL)
        with self.assertRaisesRegex(BloodBError,"DUPLICATE"):
            parse_rendered(HTML.replace("</table>","<tr><td>テストホース一号</td><td>血</td><td>?</td><td>50</td><td>?</td></tr></table>"),OFFICIAL)

    def test_local_immutable_pre_cutoff_and_not_production(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"secrets"
            when=(datetime.now(timezone.utc)+timedelta(minutes=15)).isoformat()
            ctx=Context()
            result=capture_context(ctx,race_url=URL,race_date="2026-10-11",
                            cutoff=when,official=OFFICIAL,output_root=p,
                            race_id="KM-JRA-KYO-20261011-R01")
            self.assertFalse(result["production_authority"])
            self.assertFalse(result["upload_to_github"])
            self.assertEqual(result["runner_count"],2)
            self.assertTrue(ctx.page.closed)
            target=p/"KM-JRA-KYO-20261011-R01"
            import json
            record=json.loads((target/"diagnostic.json").read_text())
            self.assertEqual(record["raw_sha256"],hashlib.sha256(HTML.encode()).hexdigest())
            self.assertFalse(record["signed_source"])
            self.assertFalse(record["bvi_population_authority"])
            self.assertEqual(record["oos_increment"],0)
            self.assertEqual(p.stat().st_mode & 0o077,0)
            self.assertEqual((target/"subscriber_page.html").stat().st_mode & 0o077,0)
            with self.assertRaisesRegex(BloodBError,"IMMUTABLE"):
                capture_context(Context(),race_url=URL,race_date="2026-10-11",
                                cutoff=when,official=OFFICIAL,output_root=p,
                                race_id="KM-JRA-KYO-20261011-R01")

    def test_expired_cutoff_and_redirect_cannot_leave_private_data(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"private"
            past=(datetime.now(timezone.utc)-timedelta(minutes=2)).isoformat()
            with self.assertRaisesRegex(BloodBError,"CUTOFF"):
                capture_context(Context(),race_url=URL,race_date="2026-10-11",
                                cutoff=past,official=OFFICIAL,output_root=p,
                                race_id="KM-JRA-KYO-20261011-R01")
            self.assertFalse(p.exists())
            later=(datetime.now(timezone.utc)+timedelta(minutes=20)).isoformat()
            with self.assertRaisesRegex(BloodBError,"REDIRECT"):
                capture_context(Context(url="https://www.blood-b.com/wp/login/"),
                                race_url=URL,race_date="2026-10-11",
                                cutoff=later,official=OFFICIAL,output_root=p,
                                race_id="KM-JRA-KYO-20261011-R01")
            self.assertFalse((p/"KM-JRA-KYO-20261011-R01").exists())

if __name__=="__main__":
    unittest.main()
