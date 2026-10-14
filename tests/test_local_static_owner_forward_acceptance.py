"""Read-only operational audit of genuinely future KAW R10/R11 Static-owner runs.

Checks immutable pre-post timeline and signed external FINAL checkpoint.
This does NOT measure predictive skill or claim actual purchased tickets.
"""
from datetime import datetime
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "governance/KM-LOCAL-PRODUCTION-STATIC-OWNER-FORWARD-ACCEPTANCE-20261014.json"


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_two_independent_genuine_forward_final_acceptances():
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    races = audit["unknown_future_signed_cases"]
    assert len(races) == 2 and len({x["execution_id"] for x in races}) == 2
    assert audit["venue_scope"] == ["KAW"]
    assert audit["numerical_prediction_consumption"] is False
    assert audit["model_empirically_calibrated"] is False
    assert audit["formal_result_settlement_verified"] is False
    for case in races:
        eid = case["execution_id"]
        run = case["github_run"]
        base = f"runtime/executions/{eid}/FORMAL/runs/race-key-{run}-formal"
        owner = load(f"runtime/local_production_static_owner_records/{eid}.json")
        final = load(f"{base}/final_receipt_envelope.json")
        temporal = load(f"{base}/final_before_post_verification.json")
        flags = load(f"{base}/receipt_verifications.json")
        numeric = load(f"{base}/numerical_materialization_summary.json")
        freeze = load(f"{base}/static_prediction_freeze.json")
        assert owner["profile"] == audit["owner_profile"]
        assert owner["sha256"] == case["static_owner_sha256"]
        assert owner["source_receipt_sha256"] == case["source_receipt_sha256"]
        assert owner["frozen_at"] == case["owner_static_frozen_at"]
        assert owner["result_consumed"] is False and owner["odds_consumed"] is False
        assert owner["numerical_prediction_consumption"] is False
        assert len(owner["full_universe"]) == case["runner_count"]
        assert datetime.fromisoformat(owner["frozen_at"]) < datetime.fromisoformat(temporal["final_timestamp"])
        assert datetime.fromisoformat(temporal["final_timestamp"]) < datetime.fromisoformat(case["official_post_at"])
        assert final["receipt_sha256"] == case["signed_final_sha256"]
        assert final["receipt"]["status"] == "PASS" and final["receipt"]["race_id"] == eid
        assert temporal["verified"] is True and temporal["final_receipt_sha256"] == final["receipt_sha256"]
        assert temporal["race_id"] == temporal["execution_id"] == eid
        assert temporal["scheduled_post_at"] == case["official_post_at"]
        assert all(flags.get(k) is True for k in case["required_receipt_flags"])
        coverage = numeric["numeric_coverage"]
        assert coverage["required_count"] == case["full_numeric_required"]
        assert coverage["numeric_value_count"] == case["full_numeric_closed"]
        assert coverage["unresolved_count"] == 0
        assert freeze["static_prediction_frozen"] is True
        assert set(freeze["static_prediction"]["ranking"]) == set(owner["full_universe"])
        assert freeze["source_receipt_sha256"] == owner["source_receipt_sha256"]
        assert "UNVALIDATED" in freeze["static_prediction"]["status"]
