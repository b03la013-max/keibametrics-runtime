from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FORMAL_WORKFLOW=ROOT/".github/workflows/km-family-non-jra-formal-runner.yml"
RESULT_WORKFLOW=ROOT/".github/workflows/km-local-result-from-signed-final.yml"
FORMAL_RUNNER=ROOT/"runtime/non_jra_formal_runner.py"
RESULT_RUNNER=ROOT/"runtime/local_result_from_signed_final.py"


def test_formal_dual_shadow_enforces_sim_std_and_truthful_pairing():
    impl=FORMAL_RUNNER.read_text(encoding="utf-8")
    workflow=FORMAL_WORKFLOW.read_text(encoding="utf-8")
    assert 'cand_runs=max(5000,min(20000,int(req.get("candidate_shadow_run_count") or 5000)))' in impl
    assert '"paired_run_count_seed":paired_ok' in impl
    assert '"paired_run_count_seed":True' not in impl
    assert 'persist("candidate_krs_"+label.lower()+"_receipt_envelope.json",crun)' in impl
    assert 'run_candidate_krs_arm("V01"' in impl
    assert 'run_candidate_krs_arm("V02"' in impl
    assert "path: runtime_out/*.json" in workflow
    assert "python -m runtime.non_jra_formal_runner" in workflow


def test_result_closed_loop_loads_both_candidate_krs_envelopes_and_persists_oos():
    impl=RESULT_RUNNER.read_text(encoding="utf-8")
    workflow=RESULT_WORKFLOW.read_text(encoding="utf-8")
    assert 'candidate_krs_v01_receipt_envelope.json' in impl
    assert 'candidate_krs_v02_receipt_envelope.json' in impl
    assert 'candidate_dual_oos_measurement.json' in impl
    assert 'candidate_dual_oos_status.json' in impl
    assert 'runtime/local_candidate_dual_oos_measurements/*.json' in workflow
    assert "python -m runtime.local_result_from_signed_final" in workflow


def test_result_ledger_is_serializable_by_repository_commit():
    workflow=RESULT_WORKFLOW.read_text(encoding="utf-8")
    assert "group: km-local-result-oos-ledger" in workflow
    assert "cancel-in-progress: false" in workflow
    assert 'git add runtime/local_candidate_dual_oos_measurements/*.json runtime/local_candidate_dual_oos_status.json' in workflow
    assert 'git pull --rebase origin main' in workflow
    assert 'git push origin HEAD:main' in workflow


def test_formal_v03_shadow_is_pre_result_frozen_final_bound_and_krs_executed():
    impl=FORMAL_RUNNER.read_text(encoding="utf-8")
    assert "compile_candidate_evidence_v03" in impl
    assert 'candidate_numerical_v03_shadow_summary.json' in impl
    assert 'trace["numerical_candidate_v03_shadow"]' in impl
    assert 'run_candidate_krs_arm("V03"' in impl
    assert 'candidate_krs_triple_shadow_summary.json' in impl
    assert '"sbo_ability_index_weight":0' in impl
    assert '"automatic_promotion":False' in impl


def test_result_v03_requires_signed_final_binding_and_persists_separate_tracker():
    impl=RESULT_RUNNER.read_text(encoding="utf-8")
    workflow=RESULT_WORKFLOW.read_text(encoding="utf-8")
    assert 'candidate_numerical_v03_shadow_summary.json' in impl
    assert 'candidate_krs_v03_receipt_envelope.json' in impl
    assert 'candidate_v03_binding_valid=bool(' in impl
    assert 'signed_final_binding_valid=candidate_v03_binding_valid' in impl
    assert 'candidate_v03_oos_measurement.json' in impl
    assert 'candidate_v03_oos_status.json' in impl
    assert 'runtime/local_candidate_v03_oos_measurements/*.json runtime/local_candidate_v03_oos_status.json' in workflow
