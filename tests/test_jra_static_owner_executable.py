"""Static Owner executes deterministically but cannot self-promote to Production."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))
from jra_static_owner_executable import (
    compile_static_owner, JRAStaticOwnerError, MAPPING,
)
from jra_index_provenance_builder import BASE, DERIVED, FORMULA_REGISTRY


def runner(rid, win, place, third):
    values={name:65.0 for name in BASE+DERIVED}
    values.update(ZAI_WIN=float(win),ZAI_PLACE=float(place),T3I=float(third))
    return {
        "runner_id":str(rid),
        "name":str(rid),
        "canonical_components":{
            name:{"value":value,"rule_id":"AUTHORITATIVE-TEST-RULE",
                  "mapping_version":MAPPING if name in BASE else FORMULA_REGISTRY,
                  "evidence_refs":["EXTERNAL-SIGNED-SOURCE"],
                  "source_fact":"mechanical acceptance fixture, not LIVE evidence"}
            for name,value in values.items()
        },
    }


def request():
    return {"family_id":"JRA","race_id":"TEST-JRA",
            "base_index_mapping_authority":{
                "mapping_id":MAPPING,"production_authority":True,
                "status":"PRODUCTION / UNCALIBRATED"
            },
            "runners":[runner(1,91,82,80),runner(2,87,89,87),runner(3,65,70,71)]}


def evaluate(req):
    return compile_static_owner(req,source_snapshot_sha256="a"*64,
                                source_receipt_sha256="b"*64,
                                frozen_at="2026-10-10T11:18:00+09:00",
                                prediction_cutoff="2026-10-10T11:20:00+09:00")


class TestStaticOwner(unittest.TestCase):
    def test_deterministic_owner_preserves_source_and_excludes_candidate_promotion(self):
        req=request()
        before=deepcopy(req)
        out=evaluate(req)
        self.assertEqual(req,before)
        self.assertEqual(out,evaluate(req))
        self.assertEqual(out["static_prediction"]["ranking"],["1","2","3"])
        self.assertEqual(out["full_index_count"],60)
        self.assertEqual(len(out["role_registry"]),9)
        self.assertTrue(out["pair_dispositions"])
        self.assertTrue(out["third_dispositions"])
        self.assertFalse(out["production_authority"])
        self.assertFalse(out["purchase_authority"])
        self.assertFalse(out["static_prediction"]["production_authority"])
        self.assertTrue(all(not x["production_authority"] for x in out["role_registry"]))

    def test_rejects_missing_and_candidate_and_corrupted_numeric(self):
        cases=[
            ("missing",lambda x:x["runners"][0]["canonical_components"].pop("HPI")),
            ("candidate",lambda x:x["runners"][0]["canonical_components"]["HPI"].update(candidate_only=True)),
            ("provenance",lambda x:x["runners"][0]["canonical_components"]["HPI"].update(evidence_refs=[])),
            ("nan",lambda x:x["runners"][0]["canonical_components"]["ZAI_WIN"].update(value=float("nan"))),
            ("dup",lambda x:x["runners"][1].update(runner_id="1")),
            ("mapping",lambda x:x["base_index_mapping_authority"].update(production_authority=False)),
        ]
        for label, mutate in cases:
            with self.subTest(label=label):
                req=request()
                mutate(req)
                with self.assertRaises(JRAStaticOwnerError):
                    evaluate(req)

    def test_rejects_late_freeze(self):
        with self.assertRaisesRegex(JRAStaticOwnerError,"STATIC_FREEZE_AFTER"):
            compile_static_owner(request(),source_snapshot_sha256="a"*64,
                source_receipt_sha256="b"*64,
                frozen_at="2026-10-10T11:25:00+09:00",
                prediction_cutoff="2026-10-10T11:20:00+09:00")

    def test_never_consumes_candidate_provenance_or_non_jra(self):
        req=request()
        req["family_id"]="LOCAL"
        with self.assertRaisesRegex(JRAStaticOwnerError,"JRA_ONLY"):
            evaluate(req)
        req=request()
        req["runners"][0]["canonical_components"]["ZAI_PLACE"]["production_authority"]=False
        with self.assertRaisesRegex(JRAStaticOwnerError,"CANDIDATE_NUMERICAL_FORBIDDEN"):
            evaluate(req)


if __name__=="__main__":
    unittest.main()
