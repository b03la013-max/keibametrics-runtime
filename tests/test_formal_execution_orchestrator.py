import json
from pathlib import Path

import pytest

from runtime import formal_execution_orchestrator as o


def base_intent():
    return {
        "family_id": "LOCAL",
        "race_id": "FNB-20260929-R01",
        "execution_mode": "AUTO",
        "temporal_mode": "FORMAL-PRE-RACE",
        "scheduled_post_at": "2099-01-01T12:00:00+09:00",
        "prediction_cutoff": "2099-01-01T11:50:00+09:00",
        "venue_id": "FNB",
        "race_date": "2099-01-01",
        "race_no": 1,
    }


def test_build_phase_request_preserves_truthful_numerical_boundary():
    src = base_intent()
    out = o.build_phase_request(src, "FORMAL")
    assert out["execution_id"] == "LOCAL-FNB-20260929-R01-EXEC"
    assert out["execution_phase"] == "FORMAL"
    assert out["phase"] == "FORMAL"
    assert out["require_full_numerical_authority"] is False
    assert "execution_mode" not in out
    assert "execution_mode" in src


def test_explicit_strict_numerical_request_is_not_silently_downgraded():
    src = base_intent()
    src["require_full_numerical_authority"] = True
    out = o.build_phase_request(src, "FORMAL")
    assert out["require_full_numerical_authority"] is True


@pytest.mark.parametrize(
    "source_status,formal_status,action,resume",
    [
        ("MISSING", "MISSING", "RUN_SOURCE_THEN_FORMAL", "SOURCE"),
        ("COMPLETE", "MISSING", "RESUME_FORMAL", "FORMAL"),
        ("COMPLETE", "COMPLETE", "RETURN_IMMUTABLE_FORMAL", "COMPLETE"),
        ("CORRUPT", "MISSING", "FAIL_CLOSED", "SOURCE_CHECKPOINT_REPAIR_REQUIRED"),
    ],
)
def test_resume_plan(monkeypatch, source_status, formal_status, action, resume):
    monkeypatch.setattr(
        o,
        "checkpoint_status",
        lambda execution_id: {
            "execution_id": execution_id,
            "source": {"status": source_status},
            "formal": {"status": formal_status},
        },
    )
    plan = o.resume_plan("LOCAL-FNB-EXEC")
    assert plan["action"] == action
    assert plan["resume_from"] == resume


def test_plan_only_has_no_production_policy_change(monkeypatch, tmp_path):
    monkeypatch.setattr(
        o,
        "resume_plan",
        lambda execution_id: {
            "action": "RUN_SOURCE_THEN_FORMAL",
            "resume_from": "SOURCE",
            "checkpoints": {
                "source": {"status": "MISSING"},
                "formal": {"status": "MISSING"},
            },
        },
    )
    report = o.orchestrate(
        base_intent(),
        run_id="123",
        github_sha="abc",
        runtime_out=tmp_path / "out",
        tmp_root=tmp_path / "tmp",
        plan_only=True,
    )
    assert report["status"] == "PLANNED"
    assert report["production_prediction_change"] is False
    assert report["production_numerical_change"] is False
    assert report["krs_physics_change"] is False
    assert report["mec_change"] is False
    assert report["capital_change"] is False


def test_failure_diagnostic_is_exposed(tmp_path):
    out = tmp_path / "runtime_out"
    out.mkdir()
    (out / "failure_diagnostic.json").write_text(
        json.dumps(
            {
                "code": "RUNTIME_GATEWAY_COMPATIBILITY_FAILED",
                "failure_class": "INFRASTRUCTURE_COMPATIBILITY",
                "last_successful_stage": "SOURCE_FREEZE",
                "resume_hint": "RETRY_SAME_EXECUTION_ID_FROM_LAST_DURABLE_PHASE",
            }
        ),
        encoding="utf-8",
    )
    f = o._phase_failure(out, "FORMAL", 1, "stdout", "stderr")
    assert f["code"] == "RUNTIME_GATEWAY_COMPATIBILITY_FAILED"
    assert f["failure_class"] == "INFRASTRUCTURE_COMPATIBILITY"
    assert f["last_successful_stage"] == "SOURCE_FREEZE"
