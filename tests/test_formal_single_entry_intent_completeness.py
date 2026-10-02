import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runtime"))

import formal_execution_orchestrator as o
from formal_execution_orchestrator import orchestrate


def test_c1_single_entry_requires_explicit_frozen_static_before_source(monkeypatch, tmp_path):
    phases = []
    monkeypatch.setattr(
        o,
        "run_phase",
        lambda request, phase, **kw: phases.append(phase) or {"phase": phase, "status": "PASS"},
    )
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
    with pytest.raises(o.FormalOrchestrationError, match="SINGLE_ENTRY_STATIC_PREDICTION_REQUIRED"):
        orchestrate(
            intent,
            run_id="test",
            github_sha="test",
            runtime_out=tmp_path / "out",
            tmp_root=tmp_path / "tmp",
        )
    assert phases == []
