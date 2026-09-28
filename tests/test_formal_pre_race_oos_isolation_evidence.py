import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXECUTION_ID="LOCAL-FNB-20260929-R01-PREFLIGHT-T04"
FORMAL_RUN="36491419788-formal"
FORMAL_DIR=ROOT/f"runtime/executions/{EXECUTION_ID}/FORMAL/runs/{FORMAL_RUN}"


def load(name):
    return json.loads((FORMAL_DIR/name).read_text(encoding="utf-8"))


def test_t04_candidate_krs_acceptance_is_not_oos():
    for name in (
        "candidate_krs_shadow_summary.json",
        "candidate_krs_v02_shadow_summary.json",
        "candidate_krs_v03_shadow_summary.json",
    ):
        x=load(name)
        assert x["status"]=="EXECUTED"
        assert x["acceptance_only"] is True
        assert x["request_oos_eligible"] is False
        assert x["pre_post_complete"] is True
        assert x["oos_temporal_eligible"] is False
        assert x["oos_exclusion_reason"]=="ACCEPTANCE_ONLY"
        assert x["production_authority"] is False


def test_t04_mec_acceptance_exclusion_is_signed_into_final():
    r4=load("mec_r4_shadow_pre_result.json")
    r5=load("local_mec_r5_shadow_pre_result.json")
    assert r4["acceptance_only"] is True
    assert r4["oos_eligible_if_signed_final_bound"] is False
    assert r4["oos_exclusion_reason"]=="ACCEPTANCE_ONLY"
    assert "NOT-OOS" in r4["temporal_class"]
    assert r5["acceptance_only"] is True
    assert r5["forward_oos_candidate"] is False
    assert r5["oos_exclusion_reason"]=="ACCEPTANCE_ONLY"
    assert "NOT-OOS" in r5["temporal_class"]

    final=load("final_receipt_envelope.json")
    assert final["receipt"]["status"]=="PASS"
    trace=final["artifact"]["ticket_transport_trace"]
    b4=trace["mec_r4_shadow_binding"]
    b5=trace["local_mec_r5_shadow_binding"]
    assert b4["acceptance_only"] is True
    assert b4["oos_eligible_if_signed_final_bound"] is False
    assert b4["oos_exclusion_reason"]=="ACCEPTANCE_ONLY"
    assert b5["acceptance_only"] is True
    assert b5["forward_oos_candidate"] is False
    assert b5["oos_exclusion_reason"]=="ACCEPTANCE_ONLY"


def test_t04_full_lifecycle_stays_truthful_and_fast():
    num=load("numerical_materialization_summary.json")
    assert num["full_numerical_calculation"] is False
    assert num["full_terminalization"] is True
    cov=num["numeric_coverage"]
    assert cov["required_count"]==348
    assert cov["terminalized_count"]==348
    assert cov["calculated_count"]==0
    assert cov["ruled_hold_count"]==348
    assert cov["unresolved_count"]==0

    krs=load("krs_receipt_envelope.json")
    assert krs["receipt"]["status"]=="EXECUTED"
    assert krs["artifact"]["actual_run_count"]==5000

    fast=load("race_day_fast_path_release_report.json")["final_release"]
    assert fast["target_met"] is True
    assert fast["hard_slo_met"] is True
    assert fast["purchase_reserve_target_met"] is True
    assert fast["critical_path_seconds"] < 300
