"""AKI adaptive purchase shadow, real tickets and pre-result binding regression."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

from aki_adaptive_purchase_shadow import (
    AdaptivePurchaseError, _sha, build_shadow, bind_to_trace,
    settle_shadow, verify_signed_final_binding,
)

PRE = "2026-10-09T00:05:00+09:00"
POST = "2026-10-09T13:00:00+09:00"


def fixture(w=28, p2=30, p3=31, asi=78, rsi=25, acceptance=False):
    ranks = [1, 2, 3, 4, 5, 6]
    roles = {
        "1": ["W", "P2", "P3"], "2": ["P2", "P3"],
        "3": ["P3"], "4": ["W", "P2", "P3"],
        "5": ["P2", "P3"], "6": ["P3"],
    }
    rows = []
    for rid in ranks:
        for index, val in {"W-AKI": w, "P2-AKI": p2, "P3-AKI": p3,
                           "ASI": asi, "RSI": rsi}.items():
            rows.append({"runner_id": str(rid), "index": index,
                         "terminal_status": "CALCULATED", "production_authority": True,
                         "value": float(val), "rule_id": "FIXTURE",
                         "mapping_version": "PROD-NUMERICAL-EXECUTION_ONLY",
                         "evidence_refs": ["fixture"], "source_fact": "synthetic"})
    ledger = {"race_id": "FNB-FUTURE-TEST-R1", "rows": rows,
              "full_terminalization": True, "full_numerical_calculation": True}
    ledger["sha256"] = _sha(ledger)
    req = {
        "race_id": "FNB-FUTURE-TEST-R1",
        "family_id": "LOCAL", "temporal_mode": "FORMAL-PRE-RACE",
        "scheduled_post_at": POST,
        "acceptance_only": acceptance,
        "static_prediction": {"ranking": ranks, "roles": roles},
        "role_registry": [
            {"runner_id": "1", "column": "W", "status": "CORE"},
            {"runner_id": "4", "column": "W", "status": "CONDITIONAL"},
        ],
        "index_provenance_ledger": ledger, "index_provenance_hash": ledger["sha256"],
        "capital_policy": {"mode": "RECOMMENDATION_ONLY"},
    }
    tickets = []
    def add(bt, sel, tier="CORE"):
        tickets.append({"bet_type": bt, "selection": sel, "stake": 100,
                        "coverage_ids": [bt + ":" + "-".join(map(str, sel))],
                        "mec_tier": tier})
    for head in (1, 4):
        for second in (2, 5):
            add("EXACTA", [head, second])
            for third in (3, 6):
                add("TRIFECTA", [head, second, third])
                add("TRIO", [head, second, third], "TAIL")
    # No actual instrument other than frozen R3 tickets.
    ids = [x for t in tickets for x in t["coverage_ids"]]
    art = {"final_prediction_package": {"ranking": ranks, "roles": roles},
           "minimum_efficient_coverage": {
               "sha256": "FROZEN-MEC-R3", "coverage_units": [{"id": i} for i in ids],
           },
           "final_ticket": {"tickets": tickets, "no_bet": False}}
    return req, {"artifact": art}


def valid_shadow(**kw):
    req, artifact = fixture(**kw)
    return req, build_shadow(req, artifact, generated_at=PRE, basis_sha256="BASIS-1")


def fake_final(req, shadow):
    # Structural fixture only; this is NOT claimed to be a signed receipt.
    return {"receipt": {"phase": "FINAL", "status": "PASS",
                        "race_id": req["race_id"], "timestamp": "2026-10-09T01:00:00+09:00",
                        "artifact_sha256": "frozen_artifact"},
            "artifact": {"ticket_transport_trace": bind_to_trace({}, shadow)},
            "receipt_sha256": "fixture-final"}


def test_stable_aki_concentrates_columns_and_limits_capital():
    req, shadow = valid_shadow()
    assert shadow["regime"] == "STABLE"
    assert shadow["width"] == {"head": 1, "p2": 2, "p3": 2}
    assert shadow["selected_role_columns"]["W"] == [1]
    assert shadow["candidate_action"] == "PAPER"
    assert 0 < shadow["candidate_capital_yen"] <= 2000
    assert shadow["candidate_ticket_count"] < shadow["production_ticket_count"]
    assert all(t["bet_type"] in ("EXACTA", "TRIO", "TRIFECTA") for t in shadow["candidate_tickets"])
    assert all(t["stake"] == 100 for t in shadow["candidate_tickets"])
    assert all(t["selection"][0] == 1 for t in shadow["candidate_tickets"] if t["bet_type"] != "TRIO")
    assert shadow["production_effect"] == "NONE"
    assert shadow["expected_value"] is None and shadow["kelly"] is None
    assert shadow["actual_purchase"] is False
    assert shadow["unspent_ceiling_yen"] >= 0
    assert shadow["result_informed_selection"] is False
    assert shadow["forward_oos_candidate"] is True
    assert shadow["oos_exclusion_reason"] is None
    assert verify_signed_final_binding(fake_final(req, shadow), shadow)["valid"] is True


def test_pair_local_third_keeps_distinct_thirds_when_top_p3_are_head_and_second():
    req, sh = valid_shadow()
    # Global P3 top-two are 1 and 2. Under head 1 / second 2,
    # actual legal third candidates must become 3 and 4, not disappear.
    assert sh["pair_local_columns"]["thirds_by_pair"]["1>2"] == [3, 4]
    keyset = {(t["bet_type"], tuple(t["selection"])) for t in sh["candidate_tickets"]}
    assert ("TRIFECTA", (1, 2, 3)) in keyset
    assert ("TRIO", (1, 2, 3)) in keyset
    assert sh["unselected_semantic_unit_count"] >= 0


def test_volatile_prefers_unordered_set_hedge_before_exact_orientation():
    req, sh = valid_shadow(w=78, p2=70, p3=75, asi=55, rsi=42)
    assert sh["regime"] == "VOLATILE"
    assert sh["candidate_tickets"][0]["bet_type"] == "TRIO"
    assert sh["candidate_capital_yen"] <= 1000


def test_two_independent_core_w_horses_prevent_false_single_head():
    req, art = fixture(w=23, asi=90, rsi=20)
    req["role_registry"][1]["status"] = "CORE"
    sh = build_shadow(req, art, generated_at=PRE, basis_sha256="BASIS-1")
    assert sh["regime"] == "SELECTIVE"
    assert sh["width"]["head"] == 2
    assert sh["head_fix_guard"]["reason"] == "MULTIPLE_CORE_W"


def test_role_shift_rsi_prevents_aki_only_single_head():
    _, sh = valid_shadow(w=27, asi=85, rsi=80)
    assert sh["regime"] == "VOLATILE"
    assert sh["width"]["head"] == 2


def test_mixed_and_volatile_expand_only_justified_columns():
    req, mixed = valid_shadow(w=50, p2=71, p3=68, asi=65, rsi=40)
    assert mixed["regime"] == "SELECTIVE"
    assert mixed["width"] == {"head": 2, "p2": 4, "p3": 5}
    assert mixed["candidate_capital_yen"] <= 1500

    req, volatile = valid_shadow(w=76, p2=75, p3=74, asi=54, rsi=50)
    assert volatile["regime"] == "VOLATILE"
    assert volatile["width"]["head"] == 2   # only two valid W in this fixture
    assert volatile["candidate_capital_yen"] <= 1000
    assert volatile["candidate_action"] == "PAPER"


def test_fragile_volatility_is_real_no_bet_not_empty_profit():
    _, shadow = valid_shadow(w=85, p2=80, p3=85, asi=15, rsi=89)
    assert shadow["candidate_action"] == "NO_BET"
    assert shadow["candidate_capital_yen"] == 0
    assert shadow["candidate_tickets"] == []
    result = settle_shadow(
        shadow,
        {"finish_order": [1, 2, 3], "payouts": {"TRIO": 1000}},
        signed_final_verified=True, signed_result_verified=True,
        official_result_verified=True,
    )
    assert result["settlement"]["pfs"] is None
    assert result["settlement"]["profit_loss"] == 0
    assert result["oos_eligible"] is True


def test_stake_budget_cannot_be_bypassed_by_recommendation_only():
    req, art = fixture(w=76, p2=72, p3=74, asi=50)
    req["capital_policy"] = {"mode": "HARD_RACE_BUDGET", "max_race_capital":300}
    sh = build_shadow(req, art, generated_at=PRE, basis_sha256="BASIS-1")
    assert sh["candidate_capital_yen"] <= 300
    assert sh["capital_ceiling_yen"] == 300
    assert sh["discard_reasons"]["EXPOSURE_BUDGET_EXHAUSTED"] > 0

    req["capital_policy"] = {"mode": "HARD_RACE_BUDGET", "max_race_capital":0}
    zero = build_shadow(req, art, generated_at=PRE, basis_sha256="BASIS-1")
    assert zero["candidate_action"] == "NO_BET"
    assert zero["candidate_ticket_count"] == 0


def test_acceptance_only_never_acquires_oos_credit():
    _, sh = valid_shadow(acceptance=True)
    assert sh["forward_oos_candidate"] is False
    assert sh["acceptance_only"] is True
    result = settle_shadow(sh, {"finish_order": [1, 2, 3],
                               "payouts": {"TRIO": 1000, "EXACTA": 400, "TRIFECTA": 3000}},
                           signed_final_verified=True, signed_result_verified=True,
                           official_result_verified=True)
    assert result["oos_eligible"] is False
    assert result["status"].endswith("NOT-OOS")


def test_missing_aki_and_unverified_provenance_fail_closed():
    req, art = fixture()
    req["index_provenance_ledger"]["rows"][0]["terminal_status"] = "RULED-HOLD"
    req["index_provenance_ledger"]["sha256"] = _sha({k:v for k,v in req["index_provenance_ledger"].items() if k!="sha256"})
    req["index_provenance_hash"] = req["index_provenance_ledger"]["sha256"]
    with pytest.raises(AdaptivePurchaseError, match="AKI_NOT_CALCULATED"):
        build_shadow(req, art, generated_at=PRE, basis_sha256="BASIS-1")
    req["index_provenance_hash"] = "REWRITTEN"
    with pytest.raises(AdaptivePurchaseError, match="AKI_PROVENANCE_DIGEST_INVALID"):
        build_shadow(req, art, generated_at=PRE, basis_sha256="BASIS-1")


def test_invalid_temporal_or_result_bearing_input_never_oos():
    req, art = fixture()
    with pytest.raises(AdaptivePurchaseError, match="NOT_FROZEN_BEFORE_START"):
        build_shadow(req, art, generated_at=POST, basis_sha256="BASIS-1")
    req["post_result_after_final"] = {"finish_order": [1, 2, 3]}
    with pytest.raises(AdaptivePurchaseError, match="RESULT_BEARING_INPUT_FORBIDDEN"):
        build_shadow(req, art, generated_at=PRE, basis_sha256="BASIS-1")


def test_nonmaterial_bets_cannot_be_invented_or_duplicate():
    req, art = fixture()
    before = copy.deepcopy(art)
    _, sh = valid_shadow()
    assert art == before
    prod = {(x["bet_type"], tuple(sorted(x["selection"]) if x["bet_type"] == "TRIO" else x["selection"]))
            for x in art["artifact"]["final_ticket"]["tickets"]}
    assert all((t["bet_type"], tuple(t["selection"])) in prod for t in sh["candidate_tickets"])
    art["artifact"]["final_ticket"]["tickets"].append(
        copy.deepcopy(art["artifact"]["final_ticket"]["tickets"][0]))
    with pytest.raises(AdaptivePurchaseError, match="DUPLICATE_FROZEN_TICKET"):
        build_shadow(req, art, generated_at=PRE, basis_sha256="BASIS-1")


def test_signed_final_tamper_and_result_authority_refused():
    req, sh = valid_shadow()
    signed = fake_final(req, sh)
    signed["artifact"]["ticket_transport_trace"]["aki_adaptive_purchase_shadow_binding"]["shadow_sha256"] = "FORGED"
    with pytest.raises(AdaptivePurchaseError, match="SHADOW_FINAL_BINDING_MISMATCH"):
        verify_signed_final_binding(signed, sh)
    with pytest.raises(AdaptivePurchaseError, match="RESULT_AUTHORITY_NOT_VERIFIED"):
        settle_shadow(sh, {"finish_order": [1, 2, 3], "payouts": {}},
                      signed_final_verified=True, signed_result_verified=False,
                      official_result_verified=True)


def test_paper_portfolio_settles_only_with_verified_outcome_and_known_prices():
    _, sh = valid_shadow()
    data = {"finish_order": [1, 2, 3],
            "payouts": {"EXACTA": 300, "TRIFECTA": 1200, "TRIO": 800}}
    result = settle_shadow(sh, data, signed_final_verified=True,
                           signed_result_verified=True, official_result_verified=True)
    assert result["status"].startswith("FORWARD-OOS")
    assert result["settlement"]["investment"] == sh["candidate_capital_yen"]
    assert result["settlement"]["return"] is not None
    assert result["actual_purchase"] is False
    assert result["settlement"]["ticket_count"] == sh["candidate_ticket_count"]
    missing = copy.deepcopy(data)
    missing["payouts"] = {}
    with pytest.raises(AdaptivePurchaseError, match="SHADOW_PAYOUT_UNRESOLVED"):
        settle_shadow(sh, missing, signed_final_verified=True,
                      signed_result_verified=True, official_result_verified=True)
    with pytest.raises(AdaptivePurchaseError, match="SPECIAL_SETTLEMENT"):
        settle_shadow(sh, {**data, "refund_runner_ids": [5]},
                      signed_final_verified=True, signed_result_verified=True,
                      official_result_verified=True)
