"""Regression: JRA Formal 20k cannot run as default SIM-STD 5k."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
from jra_production_krs_contract import (
    JRAProductionKRSContractError, production_krs_payload,
    assert_production_krs_receipt
)

ENGINE="9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421"


def request(count=20000):
    return {
        "family_id":"JRA",
        "race_id":"KM-JRA-TKY-20261010-R05",
        "run_count":count,
        "seed":2026101005,
        "jra_adapter_mode":"EXPLICIT_ENGINE_HSV",
        "base_index_mapping_authority":{"production_authority":True},
        "krs_input_data":{
            "race":{"class":"1勝クラス"},
            "simulation":{"run_count":5000,"master_seed":1},
            "horses":[{"horse_no":1},{"horse_no":2}]
        }
    }


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def executed(payload):
    sim=payload["input_data"]["simulation"]
    output={"summary":[{"horse_no":1,"name":"テスト馬"}]}
    return {"output":output,"run_receipt":{
        "receipt_sha256":"c"*64,
        "receipt":{
            "status":"EXECUTED",
            "race_id":payload["race_id"],
            "mode":payload["mode"],
            "seed":payload["seed"],
            "requested_run_count":sim["run_count"],
            "actual_run_count":sim["run_count"],
            "engine_sha256":ENGINE,
            "input_class":payload["input_class"],
            "input_sha256":digest(payload["input_data"]),
            "output_sha256":digest(output),
        }
    }}


class TestJRAProductionKRSContract(unittest.TestCase):
    def test_twenty_thousand_mode_high_and_exact(self):
        r=request()
        old=deepcopy(r)
        k=production_krs_payload(r)
        self.assertEqual(r,old)
        self.assertEqual(k["mode"],"SIM-HIGH")
        self.assertEqual(k["input_data"]["simulation"],{
            "run_count":20000,"master_seed":2026101005
        })
        self.assertEqual(k["input_data"]["race"]["prediction_id"],r["race_id"])
        x=assert_production_krs_receipt(k,executed(k),expected_engine_sha256=ENGINE)
        self.assertEqual(x["actual_run_count"],20000)

    def test_standard_five_thousand(self):
        p=production_krs_payload(request(5000))
        self.assertEqual(p["mode"],"SIM-STD")
        self.assertEqual(assert_production_krs_receipt(
            p,executed(p),expected_engine_sha256=ENGINE
        )["actual_run_count"],5000)

    def test_formal_cannot_request_20k_as_sim_std(self):
        req=request()
        req["mode"]="SIM-STD"
        with self.assertRaisesRegex(JRAProductionKRSContractError,
                                    "MODE_COUNT_CONFLICT"):
            production_krs_payload(req)

    def test_invalid_modes_counts_and_candidate_leakage(self):
        for count in (4999,5001,10000,19999,20001,"20000",True,None):
            with self.subTest(count=count):
                req=request(count)
                with self.assertRaises(JRAProductionKRSContractError):
                    production_krs_payload(req)
        req=request()
        req["candidate_only"]=True
        with self.assertRaisesRegex(JRAProductionKRSContractError,"CANDIDATE"):
            production_krs_payload(req)
        req=request()
        req["seed"]=None
        with self.assertRaisesRegex(JRAProductionKRSContractError,"SEED"):
            production_krs_payload(req)

    def test_wrong_external_receipt_is_rejected_before_verify_or_mec(self):
        p=production_krs_payload(request())
        for field,value in [
            ("mode","SIM-STD"),("actual_run_count",5000),
            ("requested_run_count",5000),("seed",123),
            ("race_id","OTHER"),("engine_sha256","wrong"),
            ("input_class","CANDIDATE-SOURCE-DERIVED-NON-PRODUCTION"),
            ("input_sha256",None),("output_sha256","bad"),
        ]:
            with self.subTest(field=field):
                rr=executed(p)
                rr["run_receipt"]["receipt"][field]=value
                with self.assertRaises(JRAProductionKRSContractError):
                    assert_production_krs_receipt(p,rr,expected_engine_sha256=ENGINE)

    def test_missing_or_unexecuted_or_unsigned_receipt_fails(self):
        p=production_krs_payload(request())
        for x in ({},{"run_receipt":{}},{"run_receipt":{"receipt":{"status":"ERROR"}}}):
            with self.subTest(value=x):
                with self.assertRaises(JRAProductionKRSContractError):
                    assert_production_krs_receipt(p,x,expected_engine_sha256=ENGINE)
        unsigned=executed(p)
        unsigned["run_receipt"]["receipt_sha256"]=""
        with self.assertRaisesRegex(JRAProductionKRSContractError,"HASH_MISSING"):
            assert_production_krs_receipt(p,unsigned,expected_engine_sha256=ENGINE)

    def test_reject_other_inputs_or_outputs_even_when_receipt_hashes_are_well_formed(self):
        p=production_krs_payload(request(5000))
        r=executed(p)
        p["input_data"]["horses"][0]["hsv"]={"surface_fit":72}
        with self.assertRaisesRegex(JRAProductionKRSContractError,"INPUT_SHA256_MISMATCH"):
            assert_production_krs_receipt(p,r,expected_engine_sha256=ENGINE)
        r=executed(p)
        r["output"]["summary"][0]["horse_no"]=2
        with self.assertRaisesRegex(JRAProductionKRSContractError,"OUTPUT_SHA256_MISMATCH"):
            assert_production_krs_receipt(p,r,expected_engine_sha256=ENGINE)


if __name__=="__main__":
    unittest.main()
