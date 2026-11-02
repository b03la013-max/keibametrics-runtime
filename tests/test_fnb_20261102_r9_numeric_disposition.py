"""R9: signed lifecycle vs frozen numerical validity must remain separate."""
from __future__ import annotations

from pathlib import Path
import inspect

from runtime import formal_execution_orchestrator as o
from runtime.local_fnb_r6_numeric_readback import frozen_numeric_readback
from runtime.local_fnb_r9_numeric_disposition import classify
from runtime.local_race_key_gate import certify

ROOT=Path(__file__).resolve().parents[1]
OLD="LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"


def test_r9_real_historical_signed_final_stays_numeric_degraded():
    formal=o.resolve_phase(OLD,"FORMAL")
    assert formal is not None
    report=frozen_numeric_readback(OLD,formal,ROOT)
    grade=report["fnb_numerical_disposition"]
    assert grade["grade"]=="FROZEN_NUMERICAL_HELD_NOT_A_CALCULATED_FULL29"
    assert grade["calculated_count"]==0
    assert grade["ruled_hold_count"]==348
    assert grade["frozen_counts_consistent"] is True
    assert grade["user_delivery_ack_verified"] is False
    assert grade["consumer_authorized"] is False


def test_r9_fake_all_calculated_counts_do_not_bypass_frozen_mismatch():
    alleged={"status":"NUMERICAL_ALL_CALCULATED_REPORTED",
             "required_count":348,"calculated_count":348,
             "ruled_hold_count":0}
    mismatched={"status":"NUMERICAL_FROZEN_COUNTS_MISMATCH",
                "consistency_verified":False}
    grade=classify(alleged,mismatched)
    assert grade["grade"]=="NUMERIC_REPORT_FROZEN_EVIDENCE_NOT_CONSISTENT"
    assert grade["consumer_authorized"] is False
    assert grade["independent_source_feature_calculation_verified"] is False


def test_r9_numerical_overlay_present_only_for_explicit_fnb_entry():
    source=inspect.getsource(certify)
    assert 'request.get("venue_id")=="FNB"' in source
    assert 'report["fnb_numerical_disposition"]' in source
    assert 'report["fnb_complete_prediction_delivery_proven"]=False' in source
    assert 'return {**report, "status": "FULL_LIFECYCLE_EXECUTION_PASS"' in source
