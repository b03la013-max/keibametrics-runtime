from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

from post_result_learning import _coverage
from race_day_fast_reflection import build_fast_reflection

FIXTURE = ROOT / "research/common/KM-FAMILY-OHI-20261008-DAY-REGRESSION-R1.json"


def test_ohi_20261008_verified_regression_cohort_is_immutable_and_adds_no_oos_credit():
    manifest = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert manifest["status"].startswith("REGRESSION-EVIDENCE / NON-PRODUCTION")
    assert manifest["production_freeze"]["automatic_promotion"] is False
    assert manifest["excluded"]["R03"]["oos_credit"] is False
    assert manifest["excluded"]["R12"]["oos_credit"] is False
    assert manifest["existing_forward_shadow_status_at_basis_main"]["mec_r5"]["eligible_races"] == 30
    assert manifest["existing_forward_shadow_status_at_basis_main"]["mec_r4"]["eligible_races"] == 8
    records = manifest["verified_result_records"]
    assert len(records) == 10
    assert len({x["race_id"] for x in records}) == 10
    assert sum(x["investment_yen"] for x in records) == 317000
    assert sum(x["return_yen"] for x in records) == 71870
    assert (317000 - 71870) == manifest["day_totals"]["loss_yen"]

    actual_failure_counts = {}
    hit_races = 0
    for expected in records:
        source = ROOT / expected["result_summary_path"]
        assert source.is_file(), source
        summary = json.loads(source.read_text(encoding="utf-8"))
        assert summary["verified"] is True
        assert summary["investment"] == expected["investment_yen"]
        assert summary["return"] == expected["return_yen"]
        review = summary["automatic_post_result_review"]
        assert review["race_id"] == expected["race_id"]
        ff = review["failure_localization"]["first_material_failure"]
        assert ff == expected["first_material_failure"]
        actual_failure_counts[ff] = actual_failure_counts.get(ff, 0) + 1
        hit_races += int(bool(summary["winning_tickets"]))

        # Use the verified signed RESULT fields as they actually existed at the
        # basis commit. Never mutate historical Signed RESULT or recalculate OOS.
        signed_source = {
            "race_id": expected["race_id"],
            "automatic_post_result_review": review,
            "learning_event": summary.get("learning_event"),
            "failure_localization": summary.get("failure_localization"),
            "settlement": {
                "investment": summary["investment"],
                "return": summary["return"],
                "profit_loss": summary["profit_loss"],
                "pfs": summary["pfs"],
                "status": "COMPLETE",
            },
        }
        unchanged = copy.deepcopy(signed_source)
        reflected = build_fast_reflection(signed_source)
        assert signed_source == unchanged
        assert reflected["first_material_failure"] == ff
        assert reflected["hit_but_loss"] == (summary["return"] > 0)
        assert reflected["dominant_pfs_loss_owner"] == (
            "PREDICTION_ROLE" if ff == "PREDICTION_ROLE_W" and summary["return"] == 0
            else "CAPITAL"
        )
        assert reflected["dominant_pfs_loss_owner_source"] == "DERIVED_FROM_SIGNED_REVIEW"
        assert reflected["conversion"]["purchased_trio_ticket_coverage"] is expected["expected_purchased_trio"]
        assert reflected["conversion"]["ordered_pair_ticket_coverage"] is expected["expected_ordered_pair"]
        assert reflected["conversion"]["ordered_exact_ticket_coverage"] is expected["expected_ordered_exact"]
        assert reflected["production_change_authorized"] is False
    assert hit_races == 9
    assert actual_failure_counts == manifest["first_failure_counts"]


def test_top3_unordered_purchased_trio_is_independent_from_exact_oriented_set():
    template = {"race_id": "T", "final_ticket": {"total_investment": 100}}
    def coverage(bt, selection):
        return _coverage({
            **template, "final_ticket": {
                "total_investment": 100,
                "tickets": [{"bet_type": bt, "selection": selection, "stake": 100}],
            },
        }, [2, 6, 3])

    ordered = coverage("TRIFECTA", [2, 6, 3])
    assert ordered["top3_set_ticket_coverage"] is True
    assert ordered["exact_oriented_top3_set_coverage"] is True
    assert ordered["purchased_trio_ticket_coverage"] is False
    assert ordered["purchased_exacta_ticket_coverage"] is False
    assert ordered["ordered_pair_ticket_coverage"] is True

    other_orientation = coverage("TRIFECTA", [6, 2, 3])
    assert other_orientation["top3_set_ticket_coverage"] is True
    assert other_orientation["exact_oriented_top3_set_coverage"] is True
    assert other_orientation["ordered_pair_ticket_coverage"] is False
    assert other_orientation["ordered_exact_ticket_coverage"] is False

    trio = coverage("TRIO", [3, 2, 6])
    assert trio["top3_set_ticket_coverage"] is True
    assert trio["purchased_trio_ticket_coverage"] is True
    assert trio["exact_oriented_top3_set_coverage"] is False

    other = coverage("TRIO", [1, 2, 6])
    assert other["purchased_trio_ticket_coverage"] is False
    assert other["top3_set_ticket_coverage"] is False


def test_fast_reflection_signed_learning_precedence_and_unknown_no_fabrication():
    signed = {
        "race_id": "E",
        "automatic_post_result_review": {
            "race_id": "E",
            "failure_localization": {"first_material_failure": "CAPITAL_EFFICIENCY"},
            "capital": {"pfs": 12.4, "hit": True, "hit_but_loss": True},
            "conversion": {"matching_ticket_types": ["TRIFECTA"]},
        },
        "learning_event": {
            "reference_metrics": {
                "dominant_pfs_loss_owner": "TICKET",
                "hit_but_loss": False,
            }
        },
    }
    x = build_fast_reflection(signed)
    assert x["dominant_pfs_loss_owner"] == "TICKET"
    assert x["dominant_pfs_loss_owner_source"] == "SIGNED_LEARNING"
    assert x["hit_but_loss"] is False
    assert x["conversion"]["purchased_trio_ticket_coverage"] is False

    unknown = build_fast_reflection({"race_id": "U"})
    assert unknown["dominant_pfs_loss_owner"] is None
    assert unknown["dominant_pfs_loss_owner_source"] == "UNAVAILABLE"
    assert unknown["hit_but_loss"] is None
    assert unknown["conversion"]["purchased_trio_ticket_coverage"] is None
