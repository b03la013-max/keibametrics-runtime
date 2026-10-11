"""Targeted rare-sire JRA corpus acquisition must remain bounded and source-verified."""
from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))
sys.path.insert(0,str(ROOT/"runtime"/"jra_source_runtime"))
from jra_pedigree_targeted_harvest import acquire


class FakeOfficialClient:
    def __init__(self):
        self.fetched = []
    def raw_get(self,path):
        self.fetched.append(path)
        return b"official-jra-bounded-sample", "text/html"


def manifest():
    return {"source":"JRA_OFFICIAL","cohort_id":"kyo-r09-test-20261011",
            "cohort_date":"2026-10-11", "target_sires":["Mor Spirit"],
            "official_horse_profile_tokens":["pw01dud002021110147/AE"]}


class TestTargetedJraCorpus(unittest.TestCase):
    def test_only_real_official_parent_can_enter_signed_harvest_candidate(self):
        fake = FakeOfficialClient()
        ped = {"horse_name":"オルゴーリオ","sire":"Mor Spirit",
               "dam":"Holy Wow","damsire":"Put It Back"}
        with patch("jra_pedigree_targeted_harvest._decode",return_value="<official/>"), \
             patch("jra_pedigree_targeted_harvest.parse_horse_pedigree",return_value=ped), \
             patch("jra_pedigree_targeted_harvest.parse_horse_history",return_value={"runs":[]}), \
             patch("jra_pedigree_targeted_harvest._sha",return_value="1"*64):
            j = acquire(manifest(),client=fake,
                        now=datetime(2026,10,11,5,45,tzinfo=timezone.utc))
        self.assertEqual(j["horse_count"],1)
        self.assertEqual(j["errors"],[])
        self.assertEqual(j["horses"][0]["dam"],"Holy Wow")
        self.assertEqual(j["mode"],"targeted_official_horse_profiles")
        self.assertEqual(len(fake.fetched),1)
        self.assertTrue(fake.fetched[0].startswith("/JRADB/accessU.html?CNAME="))

    def test_no_arbitrary_external_url_or_future_cohort(self):
        m = manifest()
        m["official_horse_profile_tokens"]=["https://hostile.invalid/horse"]
        with self.assertRaisesRegex(ValueError,"TOKEN_SCOPE"):
            acquire(m,client=FakeOfficialClient())
        m = manifest()
        with self.assertRaisesRegex(ValueError,"FUTURE_COHORT"):
            acquire(m,client=FakeOfficialClient(),
                    now=datetime(2026,10,10,1,0,tzinfo=timezone.utc))

    def test_mismatched_official_sire_adds_no_fake_bvi_sample(self):
        fake=FakeOfficialClient()
        ped={"horse_name":"別馬","sire":"Unknown Sire","dam":"Test Dam","damsire":"Test"}
        with patch("jra_pedigree_targeted_harvest._decode",return_value="<official/>"), \
             patch("jra_pedigree_targeted_harvest.parse_horse_pedigree",return_value=ped):
            j=acquire(manifest(),client=fake,
                      now=datetime(2026,10,11,5,45,tzinfo=timezone.utc))
        self.assertEqual(j["horse_count"],0)
        self.assertEqual(j["coverage_class"],"PARTIAL_WITH_EXPLICIT_MISSINGNESS")
        self.assertIn("JRA_TARGETED_SIRE_UNEXPECTED",j["errors"][0])
        self.assertFalse(j["horse_count"]/j["horse_token_count"]>=0.9)


if __name__=="__main__":
    unittest.main()
