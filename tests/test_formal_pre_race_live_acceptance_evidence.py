import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "runtime/acceptance_reports/KM-LOCAL-FORMAL-SINGLE-ENTRY-R2-PRE-RACE-20260929-T03.json"
EXECUTION_ID = "LOCAL-FNB-20260929-R01-PREFLIGHT-T03"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_t03_evidence_matches_durable_checkpoints():
    e = load(EVIDENCE)
    assert e["status"].startswith("PASS / FORMAL-PRE-RACE")
    assert e["classification"]["acceptance_only"] is True
    assert e["classification"]["oos_eligible"] is False
    assert e["classification"]["unknown_future_prediction_evidence"] is False
    assert e["classification"]["official_result_used"] is False
    assert e["formal_single_entry_profile"] == "KM-FAMILY-FORMAL-SINGLE-ENTRY-20260929-R2"

    source_latest = load(ROOT / f"runtime/executions/{EXECUTION_ID}/SOURCE/LATEST.json")
    formal_latest = load(ROOT / f"runtime/executions/{EXECUTION_ID}/FORMAL/LATEST.json")
    assert source_latest["manifest_sha256"] == e["fresh_execution"]["source"]["manifest_sha256"]
    assert formal_latest["manifest_sha256"] == e["fresh_execution"]["formal"]["manifest_sha256"]

    source_dir = ROOT / f"runtime/executions/{EXECUTION_ID}/SOURCE/runs/{e['fresh_execution']['source']['run_id']}"
    formal_dir = ROOT / f"runtime/executions/{EXECUTION_ID}/FORMAL/runs/{e['fresh_execution']['formal']['run_id']}"

    source_env = load(source_dir / "source_receipt_envelope.json")
    assert source_env["receipt_sha256"] == e["fresh_execution"]["source"]["receipt_sha256"]
    assert source_env["artifact"]["source_snapshot_sha256"] == e["fresh_execution"]["source"]["snapshot_sha256"]
    assert source_env["artifact"]["official_runner_universe"]["runner_count"] == 12

    basis = load(formal_dir / "formal_checkpoint_basis.json")
    assert basis["semantic_basis_sha256"] == e["fresh_execution"]["formal"]["semantic_basis_sha256"]
    assert basis["source_binding"]["source_receipt_sha256"] == e["fresh_execution"]["source"]["receipt_sha256"]
    assert basis["source_binding"]["source_snapshot_sha256"] == e["fresh_execution"]["source"]["snapshot_sha256"]

    numerical = load(formal_dir / "numerical_materialization_summary.json")
    cov = numerical["numeric_coverage"]
    assert numerical["full_numerical_calculation"] is False
    assert numerical["full_terminalization"] is True
    assert cov["required_count"] == 348
    assert cov["terminalized_count"] == 348
    assert cov["calculated_count"] == 0
    assert cov["ruled_hold_count"] == 348
    assert cov["unresolved_count"] == 0

    krs = load(formal_dir / "krs_receipt_envelope.json")
    assert krs["receipt_sha256"] == e["fresh_execution"]["formal"]["krs_receipt_sha256"]
    assert krs["artifact"]["actual_run_count"] == 5000

    mec = load(formal_dir / "mec_plan.json")
    assert mec["profile"] == "KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R3"
    assert mec["sha256"] == e["fresh_execution"]["formal"]["mec_sha256"]

    capital = load(formal_dir / "capital_decision.json")
    assert capital["profile"] == "KM-FAMILY-CAPITAL-COMPATIBILITY-v1.0-20260921"
    assert capital["sha256"] == e["fresh_execution"]["formal"]["capital_decision_sha256"]

    final = load(formal_dir / "final_receipt_envelope.json")
    assert final["receipt_sha256"] == e["fresh_execution"]["formal"]["final_receipt_sha256"]

    identity = load(formal_dir / "race_identity_preflight.json")
    assert identity["official_start_time"] == "14:30"
    assert identity["delta_seconds"] == 0

    fast = load(formal_dir / "race_day_fast_path_release_report.json")
    assert fast["final_release"]["critical_path_seconds"] == e["latency"]["production_critical_path_seconds"]
    assert fast["final_release"]["target_met"] is True
    assert fast["final_release"]["hard_slo_met"] is True
    assert fast["final_release"]["purchase_reserve_target_met"] is True


def test_t03_acceptance_cannot_promote_prediction_or_numerical_authority():
    e = load(EVIDENCE)
    assert e["classification"]["production_prediction_change"] is False
    assert e["classification"]["production_numerical_change"] is False
    assert e["classification"]["krs_physics_change"] is False
    assert e["classification"]["parameter_map_change"] is False
    assert e["classification"]["mec_r3_change"] is False
    assert e["classification"]["capital_policy_change"] is False
    assert e["classification"]["venue_canon_change"] is False
    assert e["numerical_truthfulness"]["strict_full_numerical_claim"] is False
    assert e["numerical_truthfulness"]["authority_status"].startswith("NOT_READY")
    assert e["immutable_retry"]["status"] == "ALREADY_COMPLETE / REUSED_IMMUTABLE"
    assert e["immutable_retry"]["source_rerun"] is False
    assert e["immutable_retry"]["krs_rerun"] is False
