"""JRA official point-in-time pedigree corpus BVI evidence regressions.

No synthetic evidence is granted Production authority. These tests ensure real
SIGNED SOURCE fields remain available to the *existing* owner-authorized
pedigree rules and contradictory pedigree identity is never pooled.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from jra_pedigree_corpus import _clean_runs, _source_horses_from_verified_artifact


def run(*, weight=478, when="2026-09-22", surface="ダ"):
    return {
        "date": when, "venue": "京都", "surface": surface,
        "distance_m": 1200, "race_name": "2勝クラス",
        "finish": 2, "field_size": 12, "body_weight": weight,
    }


class CorpusObservedBodyweightTests(unittest.TestCase):
    def test_retains_real_historical_bodyweight_for_existing_physical_bvi_rule(self):
        rows = _clean_runs([run(weight=478)], date(2026, 10, 11))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["body_weight"], 478)
        self.assertEqual(rows[0]["surface"], "ダ")
        self.assertEqual(rows[0]["distance_m"], 1200)

    def test_unknown_or_impossible_bodyweight_is_not_neutral_filled(self):
        for value in (None, "", "unknown", -1, 0, 999):
            with self.subTest(value=value):
                rows = _clean_runs([run(weight=value)], date(2026, 10, 11))
                self.assertEqual(rows[0]["body_weight"], None)

    def test_future_race_excluded_from_production_pedigree_population(self):
        rows = _clean_runs([run(when="2026-10-11"), run(when="2026-10-12"),
                            run(when="2026-10-10")], date(2026, 10, 11))
        self.assertEqual([r["date"] for r in rows], ["2026-10-10"])


class SignedSourcePedigreeIdentityTests(unittest.TestCase):
    def artifact(self, card, pedigree=None, *, history_name=None):
        return {
            "jra_official_race_card_detail": {
                "runners": [{"horse_no": 7, "horse_name": "架空の検証馬",
                             **card, "recent_runs": [run(weight=470)]}]
            },
            "jra_official_horse_history": {
                "runners": {
                    "7": {"horse_name": history_name or "架空の検証馬",
                          "pedigree": pedigree or {},
                          "runs": [run(weight=478)]}
                }
            },
        }

    def test_use_official_horse_profile_for_missing_card_parents(self):
        art = self.artifact({"sire": "父A", "dam": "", "damsire": ""},
                            {"sire": "父A", "dam": "母B", "damsire": "母父C"})
        horses = _source_horses_from_verified_artifact(art)
        self.assertEqual(len(horses), 1)
        self.assertEqual((horses[0]["sire"], horses[0]["dam"],
                          horses[0]["damsire"]), ("父A", "母B", "母父C"))
        self.assertEqual(horses[0]["runs"][0]["body_weight"], 478)

    def test_reject_conflicting_sire_dam_damsire_or_name(self):
        card = {"sire": "父A", "dam": "母B", "damsire": "母父C"}
        base = {"sire": "父A", "dam": "母B", "damsire": "母父C"}
        for field in ("sire", "dam", "damsire"):
            bad = dict(base)
            bad[field] = "別の親"
            with self.subTest(field=field):
                self.assertEqual(_source_horses_from_verified_artifact(
                    self.artifact(card, bad)), [])
        self.assertEqual(_source_horses_from_verified_artifact(
            self.artifact(card, base, history_name="別の馬")), [])

    def test_missing_parent_does_not_create_invented_offspring_sample(self):
        horses = _source_horses_from_verified_artifact(
            self.artifact({"sire": "父A", "dam": ""},
                          {"sire": "父A", "dam": ""}))
        self.assertEqual(horses, [])

    def test_no_non_jra_pedigree_field_or_unsourced_identity_inserted(self):
        art = self.artifact({"sire": "", "dam": ""},
                            {"sire": "", "dam": ""})
        art["untrusted_third_party_parent"] = {"sire": "父A", "dam": "母B"}
        self.assertEqual(_source_horses_from_verified_artifact(art), [])


if __name__ == "__main__":
    unittest.main()
