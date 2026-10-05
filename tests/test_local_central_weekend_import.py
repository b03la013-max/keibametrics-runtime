from __future__ import annotations

import copy
import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))

from formal_execution_orchestrator import _official_result_identity_matches
from local_krs_bridge_candidate import build_candidate_prediction_structure_derived
from minimum_efficient_coverage import build_mec_plan


def _idx(value):
    return {"value":float(value)}


def _runner(rid, *, w, p2, p3, coverage):
    # Set the role-specific ingredients so W and P2 can disagree materially.
    return {
        "runner_id":str(rid),
        "name":f"R{rid}",
        "candidate_feature_coverage_ratio":float(coverage),
        "candidate_missing_count":int(round((1-float(coverage))*20)),
        "canonical_components":{
            "ZAI-WIN":_idx(w),
            "SRI-L":_idx(50),
            "WCI":_idx(w),
            "ASI":_idx(70),
            "W-AKI":_idx(100-w),
            "ZAI-PLACE":_idx(p2),
            "F3S-L":_idx(p2),
            "P2-AKI":_idx(100-p2),
            "T3I-L":_idx(p3),
            "P3-AKI":_idx(100-p3),
        },
    }


def _structure_request(cap=5000):
    return {
        "candidate_full_numerical_summary":{
            "mapping_id":"LOCAL-FULL-NUMERICAL-MAPPING-v0.3-CANDIDATE-20260925-EVIDENCE-ROUTING",
            "production_authority":False,
        },
        "capital_policy":{"total_budget":cap},
        "runners":[
            _runner(1,w=96,p2=25,p3=40,coverage=.30),
            _runner(2,w=35,p2=97,p3=80,coverage=.95),
            _runner(3,w=62,p2=72,p3=96,coverage=.80),
            _runner(4,w=30,p2=35,p3=70,coverage=.70),
            _runner(5,w=20,p2=25,p3=25,coverage=.65),
        ],
    }


def test_local_structure_width_is_budget_independent_and_p2_is_independent():
    a=build_candidate_prediction_structure_derived(_structure_request(3000))
    b=build_candidate_prediction_structure_derived(_structure_request(30000))
    pa=a["candidate_static_prediction"]; pb=b["candidate_static_prediction"]
    assert (pa["W"],pa["P2"],pa["P3"])==(pb["W"],pb["P2"],pb["P3"])
    assert pa["role_width_policy"]["budget_input_used"] is False
    assert pa["role_width_policy"]["fixed_w_width"] is None
    assert "2" in pa["P2"]
    assert "2" not in pa["W"]
    assert pa["independent_p2_review"].startswith("P2 ACTIVE SET")
    assert pa["production_authority"] is False


def test_local_structure_score_and_evidence_confidence_are_separate():
    out=build_candidate_prediction_structure_derived(_structure_request())
    pred=out["candidate_static_prediction"]
    # Runner 1 has deliberately low evidence coverage but remains a W candidate
    # because confidence is reported, not silently converted into weakness.
    assert "1" in pred["W"]
    assert pred["evidence_confidence"]["1"]["classification"]=="LOW"
    assert pred["evidence_confidence"]["1"]["score_effect"]=="NONE / CONFIDENCE_REPORTED_SEPARATELY"
    assert pred["score_confidence_rule"]=="SCORE != EVIDENCE_CONFIDENCE; UNKNOWN != WEAK"
    assert pred["role_width_policy"]["future_multiplicity"] in {"CONCENTRATED","ASYMMETRIC","DIVERSE"}


def test_nar_result_identity_uses_visible_result_header_not_h4_wrapper():
    context={"venue_id":"FNB","race_date":"2026-10-02","race_no":11}
    assert _official_result_identity_matches(
        "2026年10月2日（金）　船　橋　第11競走　競走成績　千葉ダートマイル",
        context,
    )
    assert not _official_result_identity_matches(
        "2026年10月2日（金）　船　橋　第10競走　競走成績",
        context,
    )
    # Unrelated page tokens are not accepted unless they form the ordered result header.
    assert not _official_result_identity_matches(
        "2026年10月2日（金） 船橋 メニュー 第11競走 発走 競走成績一覧",
        context,
    )


def test_mec_exposes_exact_to_trio_gap_without_adding_ticket():
    req={
        "family_id":"LOCAL",
        "race_id":"LOCAL-TEST-R01",
        "role_registry":[
            {"runner_id":"1","column":"W","status":"CORE"},
            {"runner_id":"2","column":"P2","status":"CORE"},
            {"runner_id":"3","column":"P3","status":"CORE"},
        ],
        "pair_dispositions":[
            {"head":"1","second":"2","status":"PURCHASE","reason":"TEST_PAIR"}
        ],
        "third_dispositions":[
            {"head":"1","second":"2","third":"3","status":"PURCHASE","reason":"TEST_THIRD"}
        ],
        "available_bet_types":["EXACTA","TRIO","TRIFECTA"],
    }
    plan=build_mec_plan(req)
    diag=plan["cross_ticket_continuity_diagnostic"]
    assert diag["status"]=="GAP_DETECTED"
    assert diag["exact_sets_without_equivalent_trio"]==[["1","2","3"]]
    assert diag["automatic_ticket_addition"] is False
    assert not any(t["bet_type"]=="TRIO" for t in plan["tickets"])
    assert any(t["bet_type"]=="TRIFECTA" for t in plan["tickets"])
