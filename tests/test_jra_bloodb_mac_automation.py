"""Mac Blood-B automation: synthetic member page only; never access paid server."""
from datetime import datetime,timedelta,timezone
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
from jra_bloodb_mac_automation import (
  BloodBError,discover_links,discover_race_url,run_one,process_queue,
)
from test_jra_bloodb_mac_collector import HTML, URL, OFFICIAL, Context, Page

DATE="2026-08-09"
CUTOFF="2026-08-09T15:00:00+09:00"
CLOCK=lambda: datetime.fromisoformat("2026-08-09T10:00:00+09:00")
INDEX='''<html><body><h1>東京 9R</h1><section>
<div>東京 9R <a href="/main.php?rcode=2026080901010609">9R 夏の出走表</a></div>
</section></body></html>'''
OTHER='''<html><body>
<div>京都 9R <a href="/main.php?rcode=2026080901010609">9R京都</a></div>
<div>東京 9R <a href="/main.php?rcode=2026080901020609">9R東京</a></div>
</body></html>'''

class FakeBrowser:
    def __init__(self,html=INDEX,detail=HTML):
        self.calls=[]
        self.html=html
        self.detail=detail
    def new_page(self):
        browser=self
        class P:
            url="https://www.blood-b.com/allsel"
            def goto(self,u,**kw):
                self.url=u
                browser.calls.append(u)
                return type("Response",(),{"status":200})()
            def content(self):
                return browser.html if self.url.endswith("/allsel") else browser.detail
            def close(self):pass
        return P()

class Tests(unittest.TestCase):
    def test_links_only_from_observed_index_url(self):
        self.assertEqual(discover_links(INDEX,date_text=DATE,race_no=9,venue="東京")[0]["url"],
          "https://www.blood-b.com/main.php?rcode=2026080901010609")
        self.assertEqual(discover_links(INDEX,date_text=DATE,race_no=10),[])
        self.assertEqual(discover_links(INDEX,date_text="2026-08-08",race_no=9),[])
        with self.assertRaisesRegex(BloodBError,"AMBIGUOUS"):
            discover_race_url(FakeBrowser(OTHER),date_text=DATE,race_no=9)
        self.assertTrue(discover_race_url(FakeBrowser(OTHER),
                        date_text=DATE,race_no=9,venue="京都").endswith("0609"))

    def test_selector_option_explicit_url_is_discoverable_without_id_guess(self):
        menu='''<html><select>
          <option value="/main.php?rcode=2026080901010609">東京 9R</option>
          <option value="2026080901020609">数字だけのIDはURLではない</option>
          </select></html>'''
        got=discover_links(menu,date_text=DATE,race_no=9,venue="東京")
        self.assertEqual(len(got),1)
        self.assertIn("2026080901010609",got[0]["url"])

    def test_unknown_venue_and_auth_redirect_fail(self):
        with self.assertRaisesRegex(BloodBError,"VENUE_UNKNOWN"):
            discover_links(INDEX,date_text=DATE,race_no=9,venue="地球")
        with self.assertRaisesRegex(BloodBError,"LOGIN_OR_ACCESS"):
            class Redirect(FakeBrowser):
                def new_page(self):
                    p=super().new_page()
                    old=p.goto
                    def goto(u,**kw):
                        response=old(u,**kw)
                        p.url="https://www.blood-b.com/wp/login/"
                        return response
                    p.goto=goto
                    return p
            discover_race_url(Redirect(),date_text=DATE,race_no=9)

    def test_queue_skips_cutoff_and_future_without_fetching(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d)
            official=directory/"jra_official.json"
            official.write_text(json.dumps(OFFICIAL))
            far=(datetime.now(timezone.utc)+timedelta(days=3)).isoformat()
            past=(datetime.now(timezone.utc)-timedelta(minutes=30)).isoformat()
            q=directory/"queue.json"
            q.write_text(json.dumps([
                {"race_id":"KM-ALPHA","race_date":DATE,"race_no":9,
                 "official_runners_path":str(official),"prediction_cutoff":far},
                {"race_id":"KM-BETA","race_date":DATE,"race_no":9,
                 "official_runners_path":str(official),"prediction_cutoff":past}
            ]))
            ctx=FakeBrowser()
            results=process_queue(ctx,q,private_root=directory/"private")
            self.assertEqual(results["not_due"],["KM-ALPHA"])
            self.assertEqual(results["past_cutoff"],["KM-BETA"])
            self.assertEqual(ctx.calls,[])

    def test_limit_subscriber_traffic_and_duplicate_queue_ids(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d)
            official=directory/"jra_official.json"
            official.write_text(json.dumps(OFFICIAL))
            queue=[]
            for i in range(1,6):
                queue.append({"race_id":"KM-QU-"+str(i),"race_date":DATE,"race_no":9,
                  "venue":"東京","official_runners_path":str(official),
                  "prediction_cutoff":CUTOFF})
            q=directory/"queue.json"
            q.write_text(json.dumps(queue))
            browser=FakeBrowser()
            result=process_queue(browser,q,private_root=directory/"private",clock=CLOCK)
            self.assertEqual(len(result["completed"]),3)
            self.assertEqual(len(result["deferred"]),2)
            self.assertEqual(len(browser.calls),6) # index + detail for each
            queue[1]["race_id"]=queue[0]["race_id"]
            q.write_text(json.dumps(queue))
            # Existing immutable collected race takes priority; duplicate
            # then explicitly fails instead of trusting duplicate queue facts.
            second=process_queue(FakeBrowser(),q,private_root=directory/"private",clock=CLOCK)
            self.assertTrue(any("DUPLICATE_RACE_ID" in x["reason"] for x in second["failed"]))

    def test_real_link_required_and_unverified_official_marked(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d)
            official=directory/"official.json"
            official.write_text(json.dumps(OFFICIAL))
            future=CUTOFF
            spec={"race_id":"KM-JRA-TKY-20260809-R09",
                "race_date":DATE,"race_no":9,"venue":"東京",
                "official_runners_path":str(official),
                "prediction_cutoff":future}
            # The collector must verify the actual page horse universe, not
            # 'pass' a synthetic unrelated/mismatched chosen race link.
            correct=HTML
            context=FakeBrowser(html=INDEX,detail=correct)
            result=run_one(context,spec,private_root=directory/"private",clock=CLOCK)
            self.assertEqual(result["status"],"PRIVATE_DIAGNOSTIC_CAPTURED")
            self.assertFalse(result["production_authority"])
            self.assertIn("UNATTESTED",result["source_binding"])
            self.assertEqual(result["runner_count"],2)
            sidecar=json.loads((directory/"private"/spec["race_id"]/
                              "jra_source_binding.json").read_text())
            self.assertFalse(sidecar["bvi_population_authority"])
            self.assertEqual(sidecar["oos_increment"],0)
            with self.assertRaisesRegex(BloodBError,"IMMUTABLE"):
                run_one(context,spec,private_root=directory/"private",clock=CLOCK)

    def test_reject_past_race_attached_to_future_cutoff(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            official=root/"official.json"
            official.write_text(json.dumps(OFFICIAL))
            spec={"race_id":"KM-JRA-TKY-20260809-R09","race_date":DATE,"race_no":9,
                  "official_runners_path":str(official),
                  "prediction_cutoff":"2026-10-11T14:00:00+09:00"}
            with self.assertRaisesRegex(BloodBError,"CUTOFF_JST_DAY_MISMATCH"):
                run_one(FakeBrowser(),spec,private_root=root/"private",clock=CLOCK)

    def test_no_bypass_of_ambiguous_race_even_when_other_horses_exist(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            official=root/"official.json"
            official.write_text(json.dumps(OFFICIAL))
            future=CUTOFF
            spec={"race_id":"KM-JRA-TKY-20260809-R09","race_date":DATE,"race_no":9,
                  "official_runners_path":str(official),
                  "prediction_cutoff":future}
            with self.assertRaisesRegex(BloodBError,"AMBIGUOUS"):
                run_one(FakeBrowser(html=OTHER),spec,private_root=root/"private",clock=CLOCK)
            self.assertFalse((root/"private"/spec["race_id"]).exists())

if __name__=="__main__":
    unittest.main()
