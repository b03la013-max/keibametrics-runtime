"""Regression for truly bounded JRA pedigree collection (no site credentials)."""
from datetime import date
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))
sys.path.insert(0,str(ROOT/"runtime/jra_source_runtime"))

from jra_pedigree_harvest import (
    horse_tokens_for_day, parse_horse_pedigree, _Client)
from scripts.jra_pedigree_backfill_cursor import advance

class FakeOfficial:
    def __init__(self):
        self.calls=[]
        self.day="pw01srl00052026040320261004/0A"
        self.races=[
            "pw01sde0105202604030120261004/0A",
            "pw01sde0105202604030220261004/0B",
        ]
    def get(self, url):
        self.calls.append(("GET",url))
        return "doAction('/JRADB/accessS.html','ROOT_TOKEN')"
    def post(self,path,token):
        self.calls.append(("POST",token))
        if token=="ROOT_TOKEN":
            return self.day
        if token==self.day:
            return " ".join(self.races)
        if token==self.races[0]:
            return '<a href="/JRADB/accessU.html?CNAME=pw01dudFIRST">A</a> ' \
                   '<a href="/JRADB/accessU.html?CNAME=pw01dudSECOND">B</a>'
        if token==self.races[1]:
            return '<a href="/JRADB/accessU.html?CNAME=pw01dudTHIRD">C</a>'
        raise ValueError("UNEXPECTED_POST_TOKEN")

class TestBoundedOfficialNavigation(unittest.TestCase):
    def test_quota_stops_before_second_race(self):
        c=FakeOfficial()
        got=horse_tokens_for_day(c,"2026-10-04",mode="results",stop_after=2)
        self.assertEqual(got,["pw01dudFIRST","pw01dudSECOND"])
        self.assertNotIn(("POST",c.races[1]),c.calls)
        self.assertEqual(c.scanned_race_count,2)

    def test_exact_race_window(self):
        c=FakeOfficial()
        got=horse_tokens_for_day(c,"2026-10-04",mode="results",
                                 start_race=1,max_races=1)
        self.assertEqual(got,["pw01dudTHIRD"])
        self.assertNotIn(("POST",c.races[0]),c.calls)

    def test_jra_template_markup_parent_cells(self):
        raw=('<span class="opt">競走馬情報</span> テスト競走馬 '
             '<span class="name_en">Test Horse</span>'
             '<dt class="label">父</dt><dd><a>種牡馬一号</a></dd>'
             '<dt class="label">母</dt><dd>母馬一号<span class="sanku">産駒</span></dd>'
             '<dt class="label">母の父</dt><dd>母父一号</dd>')
        got=parse_horse_pedigree(raw)
        self.assertEqual(got,{"horse_name":"テスト競走馬","sire":"種牡馬一号",
                              "dam":"母馬一号","damsire":"母父一号"})
        self.assertIsNone(parse_horse_pedigree("<p>not a profile</p>")["sire"])

    def test_client_rate_boundary(self):
        with self.assertRaisesRegex(ValueError,"RATE_TOO_FAST"):
            _Client(delay=0.2)

class TestBackfillCursor(unittest.TestCase):
    def test_race_windows_and_previous_weekend(self):
        state={"status":"ACTIVE","date":"2026-10-04","start_race":0,
               "race_batch_size":3,"earliest_date":"2023-01-01"}
        first=advance(state)
        self.assertEqual((first["date"],first["start_race"]),("2026-10-04",3))
        for _ in range(11):
            first=advance(first)
        self.assertEqual((first["date"],first["start_race"]),("2026-10-03",0))
        second=advance(first,exhausted=True)
        self.assertEqual((second["date"],second["start_race"]),("2026-09-27",0))
        self.assertEqual(first["completed_batch_count"],12)
