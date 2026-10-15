"""Regression: JRA Kyoto R10 2026-10-12 was a WIN but negative-PFS race.

A chat reader relying on the day-status index must see the frozen EXACTA
5>2, 360 yen return and 51.428571% virtual PFS, not a spurious 0% or
an unverified actual purchase claim.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime" / "jra_source_runtime"))
from jra_race_day_autopilot import race_status
from jra_race_day_resolver import JST


def test_r10_signed_result_pfs_and_winning_ticket_are_not_dropped(tmp_path):
    rid = "KM-JRA-KYO-20261012-R10"
    final_file = tmp_path / "runtime" / "final_artifacts" / (rid + ".json")
    result_file = tmp_path / "runtime" / "results" / (rid + ".json")
    final_file.parent.mkdir(parents=True)
    result_file.parent.mkdir(parents=True)
    final_file.write_text(json.dumps({
        "final_receipt_sha256": "signed-final-identity",
        "sha256": "immutable-final-identity",
    }))
    result_file.write_text(json.dumps({
        "official_result": {"top3": [5, 2, 9]},
        "settlement": {
            "pfs_authority": "FROZEN-RECOMMENDATION-PFS",
            "pfs": 360 / 700 * 100,
            "total_investment": 700,
            "total_payout": 360,
            "profit_loss": -340,
            "winning_tickets": [{
                "bet_type": "EXACTA", "selection": [5, 2],
                "stake": 100, "payout_per_100": 360, "return": 360,
            }],
            "actual_purchase_status": "UNVERIFIED",
            "actual_pfs_status": "NOT_VERIFIED",
        },
    }))
    row = race_status(
        tmp_path, rid,
        {"post": "2026-10-12T15:10:00+09:00", "title": "堀川特別",
         "venue": "京都", "race_no": 10},
        {}, dt.datetime(2026, 10, 12, 17, 0, tzinfo=JST),
    )
    assert row["state"] == "SETTLED"
    assert row["official_top3"] == [5, 2, 9]
    settlement = row["settlement"]
    assert settlement["pfs"] == 360 / 700 * 100
    assert settlement["total_investment"] == 700
    assert settlement["total_payout"] == 360
    assert settlement["profit_loss"] == -340
    assert settlement["winning_tickets"] == [{
        "bet_type": "EXACTA", "selection": [5, 2],
        "stake": 100, "payout_per_100": 360, "return": 360,
    }]
    assert settlement["pfs_authority"] == "FROZEN-RECOMMENDATION-PFS"
    assert settlement["actual_purchase_status"] == "UNVERIFIED"
    assert settlement["actual_pfs_status"] == "NOT_VERIFIED"
