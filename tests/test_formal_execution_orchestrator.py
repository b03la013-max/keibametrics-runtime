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
        lambda execution_id, intent=None: {
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
        lambda execution_id, intent=None: {
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


def test_import_closure_failure_is_classified_before_source(monkeypatch, tmp_path):
    def broken(entry):
        raise o.FormalImportClosureError("FORMAL_IMPORT_CLOSURE_FAILED:runtime/broken.py:SyntaxError")
    monkeypatch.setattr(o, "build_closure", broken)
    report = o.orchestrate(
        base_intent(),
        run_id="123",
        github_sha="abc",
        runtime_out=tmp_path / "out",
        tmp_root=tmp_path / "tmp",
        plan_only=False,
    )
    assert report["status"] == "FAIL_CLOSED"
    assert report["first_failed_phase"] == "BOOTSTRAP"
    assert report["first_failed_code"] == "FORMAL_IMPORT_CLOSURE_FAILED"
    assert report["first_failed_class"] == "INFRASTRUCTURE_COMPATIBILITY"
    assert report["resume_hint"] == "REPAIR_CODE_THEN_RETRY_SAME_EXECUTION_ID"



def test_archived_acceptance_cannot_claim_formal_pre_race(tmp_path):
    intent = base_intent()
    intent["acceptance_only"] = True
    intent["source_adapter_acceptance_mode"] = "ARCHIVED-NAR-SOURCE-FIXTURE"
    report = o.orchestrate(
        intent,
        run_id="123",
        github_sha="abc",
        runtime_out=tmp_path / "out",
        tmp_root=tmp_path / "tmp",
        plan_only=True,
    )
    assert report["status"] == "FAIL_CLOSED"
    assert report["first_failed_code"] == "ARCHIVED_ACCEPTANCE_MUST_USE_POST_START_REPLAY"
    assert report["first_failed_class"] == "TEMPORAL_TRUTHFULNESS"
    assert report["resume_hint"] == "CLASSIFY_ARCHIVED_ACCEPTANCE_AS_POST_START_REPLAY_NO_OOS"


def test_source_checkpoint_basis_ignores_static_reforecast_fields():
    a = base_intent()
    b = base_intent()
    b["temporal_mode"] = "POST-START-REPLAY"
    b["race"] = {"going": "不良"}
    b["static_prediction"] = {"ranking": [2, 1, 3]}
    assert o.source_checkpoint_basis(a) == o.source_checkpoint_basis(b)


def test_source_checkpoint_legacy_compatibility_passes_for_same_source_basis(tmp_path):
    intent = base_intent()
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    envelope = {
        "receipt": {
            "family": "LOCAL",
            "race_id": intent["race_id"],
        },
        "artifact": {
            "race_id": intent["race_id"],
            "prediction_cutoff": intent["prediction_cutoff"],
            "source_race_context": {
                "venue_id": intent["venue_id"],
                "race_date": intent["race_date"],
                "race_no": intent["race_no"],
            },
            "required_source_manifest_sha256": "abc",
        },
    }
    (run_dir / "source_receipt_envelope.json").write_text(
        json.dumps(envelope), encoding="utf-8"
    )
    comp = o.source_checkpoint_compatibility(intent, {"run_dir": run_dir})
    assert comp["status"] == "PASS"
    assert comp["basis_source"] == "LEGACY_SIGNED_SOURCE_DERIVATION"


def test_source_checkpoint_reuse_rejects_changed_cutoff(tmp_path):
    intent = base_intent()
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    basis = o.source_checkpoint_basis(intent)
    (run_dir / "source_checkpoint_basis.json").write_text(
        json.dumps(basis), encoding="utf-8"
    )
    changed = dict(intent)
    changed["prediction_cutoff"] = "2099-01-01T11:40:00+09:00"
    comp = o.source_checkpoint_compatibility(changed, {"run_dir": run_dir})
    assert comp["status"] == "INCOMPATIBLE"
    assert "prediction_cutoff" in comp["mismatches"]


def test_source_checkpoint_reuse_rejects_changed_race_identity(tmp_path):
    intent = base_intent()
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    basis = o.source_checkpoint_basis(intent)
    (run_dir / "source_checkpoint_basis.json").write_text(
        json.dumps(basis), encoding="utf-8"
    )
    changed = dict(intent)
    changed["race_no"] = 2
    comp = o.source_checkpoint_compatibility(changed, {"run_dir": run_dir})
    assert comp["status"] == "INCOMPATIBLE"
    assert "race_no" in comp["mismatches"]



def _source_resolved_for_basis(tmp_path, intent):
    run_dir = tmp_path / "source-run"
    run_dir.mkdir(parents=True, exist_ok=True)
    envelope = {
        "receipt_sha256": "source-receipt-sha",
        "receipt": {
            "family": "LOCAL",
            "race_id": intent["race_id"],
        },
        "artifact": {
            "race_id": intent["race_id"],
            "prediction_cutoff": intent["prediction_cutoff"],
            "source_snapshot_sha256": "source-snapshot-sha",
            "source_race_context": {
                "venue_id": intent["venue_id"],
                "race_date": intent["race_date"],
                "race_no": intent["race_no"],
            },
        },
    }
    (run_dir / "source_receipt_envelope.json").write_text(
        json.dumps(envelope), encoding="utf-8"
    )
    return {
        "run_dir": run_dir,
        "latest": {"manifest_sha256": "source-manifest-sha"},
        "manifest": {"run_id": "source-run-1"},
    }


def test_formal_basis_ignores_retry_metadata_only(tmp_path):
    intent = base_intent()
    intent["static_prediction"] = {"ranking": [1, 2, 3]}
    intent["capital_policy"] = {"mode": "RECOMMENDATION_ONLY"}
    source = _source_resolved_for_basis(tmp_path, intent)
    a = o.formal_checkpoint_basis(intent, source)

    retry = json.loads(json.dumps(intent))
    retry["execution_attempt"] = 9
    retry["retry_reason"] = "RETRY_AFTER_NETWORK"
    retry["retry_repair_sha"] = "abc123"
    retry["execution_phase"] = "FORMAL"
    retry["phase"] = "FORMAL"
    b = o.formal_checkpoint_basis(retry, source)

    assert a["semantic_basis_sha256"] == b["semantic_basis_sha256"]
    assert a["source_binding"] == b["source_binding"]


@pytest.mark.parametrize(
    "mutator",
    [
        lambda x: x.update({"seed": 999}),
        lambda x: x.update({"run_count": 20000}),
        lambda x: x.update({"static_prediction": {"ranking": [2, 1, 3]}}),
        lambda x: x.update({"capital_policy": {"mode": "OTHER"}}),
        lambda x: x.update({"local_krs_bridge": {"bridge_id": "CHANGED", "family": "LOCAL"}}),
    ],
)
def test_formal_basis_changes_for_semantic_execution_changes(tmp_path, mutator):
    intent = base_intent()
    intent.update(
        {
            "seed": 1,
            "run_count": 5000,
            "static_prediction": {"ranking": [1, 2, 3]},
            "capital_policy": {"mode": "RECOMMENDATION_ONLY"},
            "local_krs_bridge": {"bridge_id": "B1", "family": "LOCAL"},
        }
    )
    source = _source_resolved_for_basis(tmp_path, intent)
    before = o.formal_checkpoint_basis(intent, source)

    changed = json.loads(json.dumps(intent))
    mutator(changed)
    after = o.formal_checkpoint_basis(changed, source)

    assert before["semantic_basis_sha256"] != after["semantic_basis_sha256"]


def test_formal_checkpoint_compatibility_passes_with_matching_basis(tmp_path):
    intent = base_intent()
    intent["static_prediction"] = {"ranking": [1, 2, 3]}
    source = _source_resolved_for_basis(tmp_path, intent)
    formal_dir = tmp_path / "formal-run"
    formal_dir.mkdir()
    basis = o.formal_checkpoint_basis(intent, source)
    (formal_dir / "formal_checkpoint_basis.json").write_text(
        json.dumps(basis), encoding="utf-8"
    )
    comp = o.formal_checkpoint_compatibility(
        intent,
        {"run_dir": formal_dir},
        source,
    )
    assert comp["status"] == "PASS"
    assert comp["mismatches"] == {}


def test_formal_checkpoint_compatibility_rejects_changed_static(tmp_path):
    intent = base_intent()
    intent["static_prediction"] = {"ranking": [1, 2, 3]}
    source = _source_resolved_for_basis(tmp_path, intent)
    formal_dir = tmp_path / "formal-run"
    formal_dir.mkdir()
    basis = o.formal_checkpoint_basis(intent, source)
    (formal_dir / "formal_checkpoint_basis.json").write_text(
        json.dumps(basis), encoding="utf-8"
    )

    changed = json.loads(json.dumps(intent))
    changed["static_prediction"] = {"ranking": [2, 1, 3]}
    comp = o.formal_checkpoint_compatibility(
        changed,
        {"run_dir": formal_dir},
        source,
    )
    assert comp["status"] == "INCOMPATIBLE"
    assert "semantic_basis_sha256" in comp["mismatches"]


def test_formal_checkpoint_without_basis_is_legacy_unbound(tmp_path):
    intent = base_intent()
    source = _source_resolved_for_basis(tmp_path, intent)
    formal_dir = tmp_path / "formal-run"
    formal_dir.mkdir()
    comp = o.formal_checkpoint_compatibility(
        intent,
        {"run_dir": formal_dir},
        source,
    )
    assert comp["status"] == "UNBOUND_LEGACY"
    assert "formal_checkpoint_basis" in comp["mismatches"]


@pytest.mark.parametrize(
    "formal_status,resume_from",
    [
        ("UNBOUND_LEGACY", "NEW_EXECUTION_ID_REQUIRED_FORMAL_LEGACY"),
        ("INCOMPATIBLE", "NEW_EXECUTION_ID_REQUIRED_FORMAL_BASIS"),
    ],
)
def test_resume_plan_never_silently_reuses_unbound_or_changed_formal(
    monkeypatch, formal_status, resume_from
):
    monkeypatch.setattr(
        o,
        "checkpoint_status",
        lambda execution_id, intent=None: {
            "execution_id": execution_id,
            "source": {"status": "COMPLETE"},
            "formal": {"status": formal_status},
        },
    )
    plan = o.resume_plan("LOCAL-FNB-EXEC", base_intent())
    assert plan["action"] == "FAIL_CLOSED"
    assert plan["resume_from"] == resume_from



def test_bind_formal_request_to_source_injects_exact_signed_source(monkeypatch, tmp_path):
    intent = base_intent()
    intent["static_prediction"] = {"ranking": [1, 2, 3]}
    source = _source_resolved_for_basis(tmp_path, intent)
    monkeypatch.setattr(o, "resolve_phase", lambda execution_id, phase: source)

    req = o.build_phase_request(intent, "FORMAL")
    bound = o.bind_formal_request_to_source(req)

    assert bound["single_entry_source_binding_required"] is True
    assert bound["source_receipt_sha256"] == "source-receipt-sha"
    assert bound["source_snapshot_sha256"] == "source-snapshot-sha"
    assert bound["single_entry_source_checkpoint_manifest_sha256"] == "source-manifest-sha"
    assert bound["static_prediction"]["source_basis_receipt_sha256"] == "source-receipt-sha"
    assert bound["static_prediction"]["source_basis_snapshot_sha256"] == "source-snapshot-sha"
    assert bound["static_prediction"]["source_checkpoint_manifest_sha256"] == "source-manifest-sha"


def test_bind_formal_request_to_source_rejects_preexisting_mismatch(monkeypatch, tmp_path):
    intent = base_intent()
    intent["static_prediction"] = {
        "ranking": [1, 2, 3],
        "source_basis_receipt_sha256": "wrong",
    }
    source = _source_resolved_for_basis(tmp_path, intent)
    monkeypatch.setattr(o, "resolve_phase", lambda execution_id, phase: source)

    with pytest.raises(o.FormalOrchestrationError, match="STATIC_SOURCE_BASIS_RECEIPT_MISMATCH_BEFORE_FORMAL"):
        o.bind_formal_request_to_source(o.build_phase_request(intent, "FORMAL"))


def test_formal_semantic_basis_is_independent_of_derived_source_binding_fields(tmp_path):
    intent = base_intent()
    intent["static_prediction"] = {"ranking": [1, 2, 3]}
    source = _source_resolved_for_basis(tmp_path, intent)
    a = o.formal_checkpoint_basis(intent, source)

    bound = json.loads(json.dumps(intent))
    bound["source_receipt_sha256"] = "source-receipt-sha"
    bound["source_snapshot_sha256"] = "source-snapshot-sha"
    bound["single_entry_source_binding_required"] = True
    bound["single_entry_source_checkpoint_manifest_sha256"] = "source-manifest-sha"
    bound["static_prediction"]["source_basis_receipt_sha256"] = "source-receipt-sha"
    bound["static_prediction"]["source_basis_snapshot_sha256"] = "source-snapshot-sha"
    bound["static_prediction"]["source_checkpoint_manifest_sha256"] = "source-manifest-sha"
    b = o.formal_checkpoint_basis(bound, source)

    assert a["semantic_basis_sha256"] == b["semantic_basis_sha256"]
    assert a["semantic_components"]["static_prediction_sha256"] == b["semantic_components"]["static_prediction_sha256"]


def test_current_single_entry_profile_resolves_gateway_authority(monkeypatch):
    monkeypatch.setattr(
        o,
        "load_gateway",
        lambda: {"formal_single_entry": {"profile": "KM-FAMILY-FORMAL-SINGLE-ENTRY-20260929-R2"}},
    )
    assert o.current_single_entry_profile() == "KM-FAMILY-FORMAL-SINGLE-ENTRY-20260929-R2"



def test_single_entry_canonicalizes_explicit_frozen_static_status():
    intent = base_intent()
    intent["static_prediction"] = {
        "ranking": ["4", "12", "3"],
        "status": "FROZEN-LIVE-PRE-RACE / RESULT-BLIND",
    }
    normalized, changes = o.normalize_single_entry_intent(intent)
    assert normalized["static_prediction_frozen"] is True
    assert changes[0]["code"] == "STATIC_FREEZE_CANONICALIZED_FROM_STATIC_STATUS"
    assert normalized["static_prediction"]["ranking"] == ["4", "12", "3"]


def test_single_entry_does_not_invent_freeze_for_unfrozen_static():
    intent = base_intent()
    intent["static_prediction"] = {
        "ranking": ["4", "12", "3"],
        "status": "DRAFT / NOT-FROZEN",
    }
    with pytest.raises(o.FormalOrchestrationError, match="SINGLE_ENTRY_STATIC_PREDICTION_FREEZE_REQUIRED"):
        o.normalize_single_entry_intent(intent)


def test_single_entry_rejects_conflicting_explicit_false_freeze():
    intent = base_intent()
    intent["static_prediction"] = {
        "ranking": ["4", "12", "3"],
        "status": "FROZEN-LIVE-PRE-RACE / RESULT-BLIND",
    }
    intent["static_prediction_frozen"] = False
    with pytest.raises(o.FormalOrchestrationError, match="STATIC_PREDICTION_FREEZE_DECLARATION_CONFLICT"):
        o.normalize_single_entry_intent(intent)


def _signed_source_with_start_time(tmp_path, start_time):
    run_dir = tmp_path / "source-official-time"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "source_receipt_envelope.json").write_text(
        json.dumps({
            "receipt_sha256": "signed-source-sha",
            "receipt": {"family": "LOCAL", "race_id": "FNB-20260929-R01"},
            "artifact": {
                "race_id": "FNB-20260929-R01",
                "source_snapshot_sha256": "source-snapshot-sha",
                "source_race_context": {
                    "venue_id": "FNB",
                    "race_date": "2099-01-01",
                    "race_no": 1,
                },
                "normalized_evidence": {
                    "start_time": {"value": start_time}
                },
            },
        }),
        encoding="utf-8",
    )
    return {
        "run_dir": run_dir,
        "latest": {"manifest_sha256": "manifest-sha"},
        "manifest": {"run_id": "source-run"},
    }


def test_signed_source_small_post_time_shift_is_reconciled_before_formal(tmp_path):
    intent = base_intent()
    intent["static_prediction"] = {
        "ranking": ["4", "12", "3"],
        "status": "FROZEN-LIVE-PRE-RACE / RESULT-BLIND",
    }
    intent["scheduled_post_at"] = "2099-01-01T12:00:00+09:00"
    intent["prediction_cutoff"] = "2099-01-01T11:50:00+09:00"
    source = _signed_source_with_start_time(tmp_path, "12:01")
    reconciled, change = o.reconcile_formal_request_with_signed_source(intent, source)
    assert reconciled["scheduled_post_at"] == "2099-01-01T12:01:00+09:00"
    assert change["code"] == "OFFICIAL_POST_TIME_REBASED_FROM_SIGNED_SOURCE"
    assert change["delta_seconds"] == 60.0
    assert change["prediction_change"] is False
    assert change["numerical_change"] is False


def test_signed_source_large_post_time_shift_still_fails_closed(tmp_path):
    intent = base_intent()
    intent["static_prediction"] = {
        "ranking": ["4", "12", "3"],
        "status": "FROZEN-LIVE-PRE-RACE / RESULT-BLIND",
    }
    intent["scheduled_post_at"] = "2099-01-01T12:00:00+09:00"
    source = _signed_source_with_start_time(tmp_path, "12:10")
    with pytest.raises(o.FormalOrchestrationError, match="OFFICIAL_POST_TIME_MISMATCH"):
        o.reconcile_formal_request_with_signed_source(intent, source)


def test_r6_live_intent_regression_missing_duplicate_boolean_is_repaired():
    intent = json.loads(
        Path("runtime/formal_intents/KM-LOCAL-FNB-20260929-R06-LIVE-R1.json").read_text(
            encoding="utf-8"
        )
    )
    assert "static_prediction_frozen" not in intent
    normalized, changes = o.normalize_single_entry_intent(intent)
    assert normalized["static_prediction_frozen"] is True
    assert any(x["code"] == "STATIC_FREEZE_CANONICALIZED_FROM_STATIC_STATUS" for x in changes)


def test_r7_live_identity_regression_one_minute_official_shift_is_repairable(tmp_path):
    intent = json.loads(
        Path("runtime/formal_intents/KM-LOCAL-FNB-20260929-R07-LIVE-R1.json").read_text(
            encoding="utf-8"
        )
    )
    # Preserve the frozen semantic payload; exercise only the source-authoritative
    # identity reconciliation that failed live at 17:45 vs official 17:46.
    intent["race_date"] = "2099-01-01"
    intent["scheduled_post_at"] = "2099-01-01T17:45:00+09:00"
    intent["prediction_cutoff"] = "2099-01-01T17:39:00+09:00"
    source = _signed_source_with_start_time(tmp_path, "17:46")
    reconciled, change = o.reconcile_formal_request_with_signed_source(intent, source)
    assert reconciled["scheduled_post_at"] == "2099-01-01T17:46:00+09:00"
    assert change["delta_seconds"] == 60.0



def test_final_prediction_package_is_losslessly_derived_from_frozen_static():
    intent = base_intent()
    intent["static_prediction"] = {
        "ranking": ["4", "12", "3"],
        "roles": {"4": ["W"], "12": ["P2"], "3": ["P3"]},
        "alternative_winner": ["12"],
        "status": "FROZEN-LIVE-PRE-RACE / RESULT-BLIND",
    }
    normalized, changes = o.normalize_single_entry_intent(intent)
    fpp = normalized["final_prediction_package"]
    assert fpp["ranking"] == intent["static_prediction"]["ranking"]
    assert fpp["roles"] == intent["static_prediction"]["roles"]
    assert fpp["alternative_winner"] == ["12"]
    assert fpp["source"] == "CANONICALIZED_FROM_FROZEN_STATIC_SINGLE_ENTRY"
    assert fpp["production_prediction_change"] is False
    assert any(
        x["code"] == "FINAL_PREDICTION_PACKAGE_CANONICALIZED_FROM_FROZEN_STATIC"
        for x in changes
    )


def test_explicit_final_prediction_package_is_preserved():
    intent = base_intent()
    intent["static_prediction"] = {
        "ranking": ["4", "12", "3"],
        "roles": {"4": ["W"], "12": ["P2"], "3": ["P3"]},
        "status": "FROZEN-LIVE-PRE-RACE / RESULT-BLIND",
    }
    intent["static_prediction_frozen"] = True
    intent["final_prediction_package"] = {
        "ranking": ["4", "12", "3"],
        "roles": {"4": ["W"], "12": ["P2"], "3": ["P3"]},
        "source": "EXPLICIT",
    }
    normalized, changes = o.normalize_single_entry_intent(intent)
    assert normalized["final_prediction_package"] == intent["final_prediction_package"]
    assert not any(
        x["code"] == "FINAL_PREDICTION_PACKAGE_CANONICALIZED_FROM_FROZEN_STATIC"
        for x in changes
    )


def test_r6_live_intent_also_derives_final_prediction_package():
    intent = json.loads(
        Path("runtime/formal_intents/KM-LOCAL-FNB-20260929-R06-LIVE-R1.json").read_text(
            encoding="utf-8"
        )
    )
    assert "final_prediction_package" not in intent
    normalized, changes = o.normalize_single_entry_intent(intent)
    assert normalized["final_prediction_package"]["ranking"] == intent["static_prediction"]["ranking"]
    assert normalized["final_prediction_package"]["roles"] == intent["static_prediction"]["roles"]
    assert any(
        x["code"] == "FINAL_PREDICTION_PACKAGE_CANONICALIZED_FROM_FROZEN_STATIC"
        for x in changes
    )
