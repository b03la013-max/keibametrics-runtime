import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runtime"))

from formal_execution_orchestrator import orchestrate


def test_single_entry_rejects_source_only_shell_before_external_source(tmp_path):
    intent = {
        "family_id": "LOCAL",
        "execution_mode": "AUTO",
        "temporal_mode": "FORMAL-PRE-RACE",
        "race_id": "KM-LOCAL-FNB-20990101-R01-TEST",
        "venue_id": "FNB",
        "race_date": "2099-01-01",
        "race_no": 1,
        "prediction_cutoff": "2099-01-01T12:00:00+09:00",
        "scheduled_post_at": "2099-01-01T12:10:00+09:00",
    }
    report = orchestrate(
        intent,
        run_id="test",
        github_sha="test",
        runtime_out=tmp_path / "out",
        tmp_root=tmp_path / "tmp",
    )
    assert report["status"] == "FAIL_CLOSED"
    assert report["first_failed_phase"] == "BOOTSTRAP"
    assert report["first_failed_code"] == "SINGLE_ENTRY_STATIC_PREDICTION_REQUIRED"
    assert report["first_failed_class"] == "INTENT_COMPLETENESS"
    assert report["resume_from"] == "INTENT_COMPLETION"
