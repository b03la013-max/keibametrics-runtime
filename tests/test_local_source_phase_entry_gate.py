"""2026-10-14 Kawasaki SOURCE bridge regression: signed SOURCE != signed FINAL."""
from pathlib import Path

import pytest

from runtime import formal_execution_orchestrator as o


@pytest.mark.parametrize("phase", ["SOURCE", "SOURCE_ONLY", "SOURCE_ACQUIRE", "SOURCE-FREEZE", "SOURCE_FREEZE"])
def test_explicit_source_never_requires_static_and_succeeds_as_only_phase(monkeypatch, tmp_path, phase):
    monkeypatch.setattr(o, "resolve_phase", lambda *_: None)
    calls = []

    def source_run(req, name, **kwargs):
        calls.append((req["execution_phase"], name))
        return {"phase": "SOURCE", "status": "PASS", "receipt_sha256": "verified-test-receipt"}

    monkeypatch.setattr(o, "run_phase", source_run)
    intent = {
        "family_id": "LOCAL",
        "race_id": "KM-LOCAL-KAW-20990101-R03-LIVE-R1",
        "execution_id": "KM-LOCAL-KAW-20990101-R03-LIVE-R1",
        "execution_phase": phase,
        "temporal_mode": "FORMAL-PRE-RACE",
        "prediction_cutoff": "2099-01-01T15:40:00+09:00",
        "scheduled_post_at": "2099-01-01T15:45:00+09:00",
    }
    report = o.orchestrate(
        intent, run_id="fixture", github_sha=None,
        runtime_out=tmp_path / "out", tmp_root=tmp_path / "tmp",
    )
    assert calls == [("SOURCE", "SOURCE")]
    assert report["status"] == "SOURCE_PASS"
    assert report["execution_class"] == "SOURCE_ONLY"
    assert report["signed_source_verified"] is True
    assert report["completion"] is False
    # The phase-scoped bridge may succeed without claiming FORMAL completion.
    assert o.phase_exit_code(report, intent) == 0
    assert o.completion_exit_code(report) != 0


def test_compatible_saved_source_is_read_back_not_reacquired(monkeypatch, tmp_path):
    req = {"family_id": "LOCAL", "race_id": "TEST-01", "execution_phase": "SOURCE"}
    resolved = {"run_dir": tmp_path}
    monkeypatch.setattr(o, "resolve_phase", lambda *a: resolved)
    monkeypatch.setattr(o, "source_checkpoint_compatibility", lambda *a: {"status": "PASS"})
    calls = []
    monkeypatch.setattr(o, "validate_source_checkpoint", lambda path, req: calls.append(("verify", path)))
    monkeypatch.setattr(o, "run_phase", lambda *a, **k: pytest.fail("reacquisition is forbidden"))
    report = o.orchestrate(req, run_id="fixture", github_sha=None)
    assert calls == [("verify", tmp_path)]
    assert report["status"] == "SOURCE_PASS"
    assert report["signed_source_verified"] is True
    assert report["completion"] is False
    assert o.phase_exit_code(report, req) == 0


def test_corrupt_source_checkpoint_never_returns_success(monkeypatch, tmp_path):
    req = {"family_id": "LOCAL", "race_id": "TEST-02", "execution_phase": "SOURCE"}
    monkeypatch.setattr(o, "resolve_phase", lambda *a: {"run_dir": tmp_path})
    monkeypatch.setattr(o, "source_checkpoint_compatibility", lambda *a: {"status": "FAIL"})
    with pytest.raises(o.FormalOrchestrationError, match="SOURCE_CHECKPOINT_INCOMPATIBLE"):
        o.orchestrate(req, run_id="fixture", github_sha=None)


@pytest.mark.parametrize("status,verified,completion", [
    ("SOURCE_PASS", False, False),
    ("SOURCE_PASS", None, False),
    ("SOURCE_PASS", True, True),
    ("FORMAL_INCOMPLETE", True, False),
    ("BLOCKED", True, False),
])
def test_unverified_or_incomplete_source_does_not_fake_phase_success(status, verified, completion):
    req = {"family_id": "LOCAL", "execution_phase": "SOURCE"}
    report = {"status": status, "phase": "SOURCE", "execution_class": "SOURCE_ONLY",
              "signed_source_verified": verified, "completion": completion}
    assert o.phase_exit_code(report, req) != 0


def test_formal_request_never_inherits_source_success_gate():
    source_report = {"status": "SOURCE_PASS", "phase": "SOURCE",
                     "execution_class": "SOURCE_ONLY", "signed_source_verified": True,
                     "completion": False}
    assert o.phase_exit_code(source_report, {"execution_phase": "FORMAL"}) != 0
    assert o.phase_exit_code(source_report, {"execution_phase": "AUTO"}) != 0
    with pytest.raises(o.FormalOrchestrationError, match="SINGLE_ENTRY_STATIC_PREDICTION_REQUIRED"):
        o.normalize_single_entry_intent({"family_id": "LOCAL", "execution_phase": "FORMAL"})


def test_source_deadline_remains_fail_closed(monkeypatch, tmp_path):
    req = {"family_id": "LOCAL", "race_id": "TEST-03", "execution_phase": "SOURCE",
           "scheduled_post_at": "2026-10-14T15:45:00+09:00",
           "prediction_cutoff": "2026-10-14T15:40:00+09:00"}
    monkeypatch.setattr(o, "resolve_phase", lambda *a: None)
    monkeypatch.setattr(o, "run_phase", lambda *a, **k: pytest.fail("must not run after cutoff"))
    with pytest.raises(o.FormalOrchestrationError, match="DEADLINE_HOLD"):
        o.orchestrate(req, run_id="fixture", github_sha=None, runtime_out=tmp_path/"out")
