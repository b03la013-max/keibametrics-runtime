from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FORMAL=ROOT/"runtime/non_jra_formal_runner.py"
RESULT=ROOT/"runtime/local_result_from_signed_final.py"


def test_formal_dual_shadow_enforces_sim_std_and_truthful_pairing():
    text=FORMAL.read_text(encoding="utf-8")
    assert 'cand_runs=max(5000,min(20000,int(req.get("candidate_shadow_run_count") or 5000)))' in text
    assert '"paired_run_count_seed":paired_ok' in text
    assert '"paired_run_count_seed":True' not in text
    assert 'persist("candidate_krs_"+label.lower()+"_receipt_envelope.json",crun)' in text
    assert 'run_candidate_krs_arm("V01"' in text
    assert 'run_candidate_krs_arm("V02"' in text
    assert "path: runtime_out/*.json" in text


def test_result_closed_loop_loads_both_candidate_krs_envelopes_and_persists_oos():
    text=RESULT.read_text(encoding="utf-8")
    assert 'candidate_krs_v01_receipt_envelope.json' in text
    assert 'candidate_krs_v02_receipt_envelope.json' in text
    assert 'candidate_dual_oos_measurement.json' in text
    assert 'candidate_dual_oos_status.json' in text
    assert 'runtime/local_candidate_dual_oos_measurements/*.json' in text


def test_result_ledger_is_serializable_by_repository_commit():
    text=RESULT.read_text(encoding="utf-8")
    assert "group: km-local-result-oos-ledger" in text
    assert "cancel-in-progress: false" in text
    assert 'git add runtime/local_candidate_dual_oos_measurements/*.json runtime/local_candidate_dual_oos_status.json' in text
    assert 'git pull --rebase origin main' in text
    assert 'git push origin HEAD:main' in text


def test_formal_v03_shadow_is_pre_result_frozen_final_bound_and_krs_executed():
    text=FORMAL.read_text(encoding="utf-8")
    assert "compile_candidate_evidence_v03" in text
    assert 'candidate_numerical_v03_shadow_summary.json' in text
    assert 'trace["numerical_candidate_v03_shadow"]' in text
    assert 'run_candidate_krs_arm("V03"' in text
    assert 'candidate_krs_triple_shadow_summary.json' in text
    assert '"sbo_ability_index_weight":0' in text
    assert '"automatic_promotion":False' in text


def test_result_v03_requires_signed_final_binding_and_persists_separate_tracker():
    text=RESULT.read_text(encoding="utf-8")
    assert 'candidate_numerical_v03_shadow_summary.json' in text
    assert 'candidate_krs_v03_receipt_envelope.json' in text
    assert 'candidate_v03_binding_valid=bool(' in text
    assert 'signed_final_binding_valid=candidate_v03_binding_valid' in text
    assert 'candidate_v03_oos_measurement.json' in text
    assert 'candidate_v03_oos_status.json' in text
    assert 'runtime/local_candidate_v03_oos_measurements/*.json runtime/local_candidate_v03_oos_status.json' in text
