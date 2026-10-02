import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runtime"))

import formal_execution_orchestrator as o
from formal_execution_orchestrator import orchestrate


def test_single_entry_missing_static_reaches_internal_prediction_owner(monkeypatch, tmp_path):
    phases=[]
    monkeypatch.setattr(o,"run_phase",lambda request,phase,**kw: phases.append(phase) or {"phase":phase,"status":"PASS"})
    def unavailable(intent, **kw):
        raise o.FormalOrchestrationError("PRODUCTION_PREDICTION_OWNER_NOT_REGISTERED")
    monkeypatch.setattr(o,"execute_prediction_owner",unavailable)
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
    assert phases == ["SOURCE"]
    assert report["status"] == "BLOCKED"
    assert report["dependency_failure"] == "PRODUCTION_PREDICTION_OWNER_NOT_REGISTERED"
    assert "SINGLE_ENTRY_STATIC_PREDICTION_REQUIRED" not in str(report)
