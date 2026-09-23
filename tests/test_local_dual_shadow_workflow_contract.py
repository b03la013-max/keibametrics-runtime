from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FORMAL=ROOT/".github/workflows/km-family-non-jra-formal-runner.yml"
RESULT=ROOT/".github/workflows/km-local-result-from-signed-final.yml"


def test_formal_dual_shadow_enforces_sim_std_and_truthful_pairing():
    text=FORMAL.read_text(encoding="utf-8")
    assert 'cand_runs=max(5000,min(20000,int(req.get("candidate_shadow_run_count") or 5000)))' in text
    assert '"paired_run_count_seed":paired_ok' in text
    assert '"paired_run_count_seed":True' not in text
    assert 'candidate_krs_v01_receipt_envelope.json' in text
    assert 'candidate_krs_v02_receipt_envelope.json' in text
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
