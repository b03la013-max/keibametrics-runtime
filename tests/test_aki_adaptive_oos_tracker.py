"""Canonical official result, signed binding, and abstention opportunity-cost tests."""
from __future__ import annotations
import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(ROOT / "tests"))

from test_aki_adaptive_purchase_shadow import fixture, PRE
from aki_adaptive_purchase_shadow import (
    AdaptivePurchaseError, _sha, build_shadow, bind_to_trace, verify_signed_final_binding,
)
from aki_adaptive_oos_tracker import _summary, evaluate_canonical, scan_execution_store
from mec_r4_shadow import settle_ticket_list


def canonical_fixture(no_bet=False):
    params = {"w": 85, "p2": 80, "p3": 85, "asi": 15, "rsi": 89} if no_bet else {}
    req, art = fixture(**params)
    sh = build_shadow(req, art, generated_at=PRE, basis_sha256="FROZEN-BASIS")
    fa = {"ticket_transport_trace": bind_to_trace({}, sh),
          "final_ticket": copy.deepcopy(art["artifact"]["final_ticket"])}
    fr = {
        "phase": "FINAL", "status": "PASS", "race_id": req["race_id"],
        "timestamp": "2026-10-09T01:00:00+09:00",
        "artifact_sha256": _sha(fa),
    }
    final = {"artifact": fa, "receipt": fr, "receipt_sha256": _sha(fr)}
    attestation = verify_signed_final_binding(final, sh)
    official = {
        "finish_order": [1, 2, 3],
        "payouts": {"EXACTA": 500, "TRIO": 900, "TRIFECTA": 2000},
    }
    p_settled = settle_ticket_list(fa["final_ticket"]["tickets"], {
        "official_result": {"top3": official["finish_order"], "payouts": official["payouts"]}
    })
    assert p_settled["status"] == "SETTLED"
    ra = {"official_result": official,
          "frozen_refs": {"final_receipt_sha256": final["receipt_sha256"]},
          "result_available_at": "2026-10-09T14:00:00+09:00",
          "settlement": {"status": "COMPLETE", "pfs_authority": "FROZEN-RECOMMENDATION",
                         "investment": p_settled["investment"],
                         "return": p_settled["return"]}}
    rr = {"phase": "RESULT", "status": "PASS", "race_id": req["race_id"],
          "artifact_sha256": _sha(ra)}
    result = {"artifact": ra, "receipt": rr, "receipt_sha256": _sha(rr)}
    official_req = {"race_id": req["race_id"],
                    "official_result_verified": True,
                    "acceptance_only": False,
                    "official_result_verification_ref": "https://nar.test/official#sha256=FIXTURE",
                    **official}
    fflags = {"FINAL": True}
    rflags = {"FINAL": True, "RESULT": True}
    return sh, attestation, final, result, official_req, fflags, rflags


def test_frozen_realistic_result_settlement_is_result_bound():
    vals = canonical_fixture()
    x = evaluate_canonical(*vals)
    assert x["oos_eligible"] is True
    assert x["paper_only"] is True
    assert x["actual_purchase"] is False
    assert x["adaptive"]["investment"] < x["production"]["investment"]
    assert x["adaptive"]["pfs"] is not None
    assert x["production_effect"] == "NONE"
    summary = _summary([x], [], [])
    assert summary["eligible_races"] == 1
    assert summary["automatic_promotion"] is False
    assert summary["production_change_authorized"] is False
    assert summary["status"] == "WAITING_FORWARD_OOS"
    assert summary["actual_purchase_pfs"] is None


def test_no_bet_has_null_pfs_and_tracks_opportunity_cost():
    x = evaluate_canonical(*canonical_fixture(no_bet=True))
    assert x["adaptive"]["investment"] == 0
    assert x["adaptive"]["pfs"] is None
    summary = _summary([x], [], [])
    assert summary["abstention_races"] == 1
    assert summary["adaptive"]["pfs"] is None
    assert (summary["avoided_production_losses_on_abstentions_hindsight"] +
            summary["missed_production_gains_on_abstentions_hindsight"]) >= 0


def test_receipt_tampering_and_missing_authorities_fail_closed():
    x = canonical_fixture()
    cases = [
        (2, lambda d: d["receipt"].update({"artifact_sha256": "BAD"}), "ARTIFACT_HASH"),
        (3, lambda d: d["artifact"]["frozen_refs"].update({"final_receipt_sha256": "BAD"}), "ARTIFACT_HASH"),
        (4, lambda d: d.update({"official_result_verified": False}), "OFFICIAL_RESULT_AUTHORITY"),
        (5, lambda d: d.update({"FINAL": False}), "EXTERNAL_RECEIPT_VERIFICATION"),
        (6, lambda d: d.update({"RESULT": False}), "EXTERNAL_RECEIPT_VERIFICATION"),
    ]
    for position, mutate, message in cases:
        inputs = copy.deepcopy(x)
        mutate(inputs[position])
        with pytest.raises(AdaptivePurchaseError, match=message):
            evaluate_canonical(*inputs)


def test_signed_settlement_mismatch_is_not_hidden():
    x = canonical_fixture()
    result = x[3]
    result["artifact"]["settlement"]["return"] += 1
    result["receipt"]["artifact_sha256"] = _sha(result["artifact"])
    result["receipt_sha256"] = _sha(result["receipt"])
    with pytest.raises(AdaptivePurchaseError, match="PRODUCTION_SIGNED_SETTLEMENT_CONFLICT"):
        evaluate_canonical(*x)


def test_history_is_not_silently_backfilled(tmp_path):
    r = scan_execution_store(tmp_path / "nonexistent")
    assert r["eligible_races"] == 0
    assert r["settled_rows"] == []
    assert r["adaptive"]["pfs"] is None
    assert r["actual_purchase_pfs"] is None


def test_real_ohi_20261009_seven_receipt_bound_replay():
    """Read-only 7-race actual Signed FINAL/RESULT replay, not synthetic evidence.

    This must NOT mutate the original 2026-10-09 OOS status. If any real
    Receipt/official-result/settlement binding is broken, fail closed.
    """
    root = ROOT / "runtime" / "executions"
    expected = {
        "KM-LOCAL-OHI-20261009-R04-LIVE-R2": (16500, 3050),
        "KM-LOCAL-OHI-20261009-R05-LIVE-R1": (46000, 36840),
        "KM-LOCAL-OHI-20261009-R06-LIVE-R1": (70400, 39120),
        "KM-LOCAL-OHI-20261009-R07-LIVE-R1": (25400, 10310),
        "KM-LOCAL-OHI-20261009-R08-LIVE-R1": (22800, 1370),
        "KM-LOCAL-OHI-20261009-R09-LIVE-R1": (38000, 52800),
        "KM-LOCAL-OHI-20261009-R10-LIVE-R1": (46000, 5240),
    }
    # The historical Git-tracked execution store is the test's external
    # evidence basis; do not silently PASS an empty or sparse checkout.
    for race_id in expected:
        assert (root / race_id).is_dir(), f"MISSING_REAL_EXECUTION:{race_id}"

    original_status = ROOT / "runtime" / "aki_adaptive_oos_status.json"
    original_bytes = original_status.read_bytes()
    report = scan_execution_store(root)
    assert report["errors"] == [], report["errors"]
    assert report["eligible_races"] == 7, report
    assert report["days"] == 1, report
    assert report["status"] == "WAITING_FORWARD_OOS"
    assert report["automatic_promotion"] is False
    assert report["production_change_authorized"] is False
    assert report["actual_purchase_pfs"] is None

    by_id = {x["race_id"]: x for x in report["settled_rows"]}
    assert set(by_id) == set(expected), set(by_id)
    for race_id, (investment, returned) in expected.items():
        item = by_id[race_id]
        assert (item["production"]["investment"], item["production"]["return"]) == (investment, returned)
        assert item["oos_eligible"] is True
        assert item["candidate_action"] == "PAPER"
        assert item["regime"] == "SELECTIVE"
        assert item["paper_only"] is True
        assert item["actual_purchase"] is False
        assert item["production_effect"] == "NONE"
        assert item["shadow_sha256"] and item["final_receipt_sha256"] and item["result_receipt_sha256"]
    assert report["production"]["investment"] == 265100
    assert report["production"]["return"] == 148730
    assert original_status.read_bytes() == original_bytes, "ORIGINAL_HOLD_LEDGER_WAS_MUTATED"
