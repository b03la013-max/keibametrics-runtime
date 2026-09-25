# Execution Gateway canary verification marker; no behavior change.
import pathlib

import pytest

from runtime.execution_gateway import (
    ExecutionGatewayError,
    artifact_name,
    assess_runtime_health,
    derive_execution_id,
    normalize_request,
    record_phase,
    repository_bundle,
)


def _gateway(tmp_path: pathlib.Path):
    runtime_dir = tmp_path / "runtime" / "local_physical"
    runtime_dir.mkdir(parents=True)
    files = {}
    for field, name in {
        "runtime_app_sha256": "app_v15.py",
        "legacy_runtime_app_sha256": "app.py",
        "source_acquisition_sha256": "source_acquisition.py",
    }.items():
        p = runtime_dir / name
        p.write_text(field, encoding="utf-8")
        files[field] = str(p.relative_to(tmp_path))
    return {
        "profile_id": "GW",
        "families": {
            "LOCAL": {
                "runtime_profile": "RUNTIME-V1",
                "runtime_git_revision": "pointer-rev",
                "external_endpoint": "https://example.invalid",
                "receipt_signer_key_id": "SIGNER",
                "engine_sha256": "ENGINE",
                "parameter_map_sha256": "PARAM",
                "required_capabilities": ["SOURCE_ACQUIRE", "PRE_KRS", "KRS_EXECUTE", "FINAL", "RESULT", "VERIFY"],
                "bundle_files": files,
                "artifact_prefix": "km-local-execution",
            }
        },
    }


def _health(gateway, tmp_path, revision="pointer-rev"):
    bundle = repository_bundle(gateway["families"]["LOCAL"], tmp_path)
    return {
        "status": "READY",
        "runtime_revision": "RUNTIME-V1",
        "github_revision": revision,
        "receipt_signer_key_id": "SIGNER",
        "engine_sha256": "ENGINE",
        "parameter_map_sha256": "PARAM",
        "capabilities": ["SOURCE_ACQUIRE", "PRE_KRS", "KRS_EXECUTE", "FINAL", "RESULT", "VERIFY"],
        **bundle,
    }


def test_request_runtime_revision_is_diagnostic_only(tmp_path):
    gateway = _gateway(tmp_path)
    req = {
        "family_id": "LOCAL",
        "race_id": "URW-20260926-R01",
        "runtime_expected_revision": "stale-request-value",
        "external_endpoint": "https://stale.invalid",
    }
    normalized, ctx = normalize_request(req, gateway)
    assert "runtime_expected_revision" not in normalized
    assert "external_endpoint" not in normalized
    assert normalized["resolved_runtime_profile"] == "RUNTIME-V1"
    assert normalized["resolved_external_endpoint"] == "https://example.invalid"
    assert ctx["request_diagnostics"]["runtime_expected_revision"] == "stale-request-value"


def test_stale_handoff_ids_are_diagnostic_only_by_default(tmp_path):
    gateway = _gateway(tmp_path)
    req = {
        "family_id": "LOCAL",
        "race_id": "URW-20260926-R01",
        "source_receipt_artifact_id": 123,
        "source_run_id": 456,
        "artifact_name": "stale-artifact",
    }
    normalized, ctx = normalize_request(req, gateway)
    assert "source_receipt_artifact_id" not in normalized
    assert "source_run_id" not in normalized
    assert "artifact_name" not in normalized
    assert ctx["request_diagnostics"]["request_source_receipt_artifact_id"] == 123
    assert ctx["request_diagnostics"]["request_source_run_id"] == 456
    assert ctx["request_diagnostics"]["request_artifact_name"] == "stale-artifact"
    assert ctx["legacy_handoff_override"] is False


def test_legacy_handoff_override_preserves_explicit_references(tmp_path):
    gateway = _gateway(tmp_path)
    req = {
        "family_id": "LOCAL",
        "race_id": "URW-20260926-R01",
        "legacy_handoff_override": True,
        "source_receipt_artifact_id": 123,
        "source_run_id": 456,
        "artifact_name": "historical-artifact",
    }
    normalized, ctx = normalize_request(req, gateway)
    assert normalized["source_receipt_artifact_id"] == 123
    assert normalized["source_run_id"] == 456
    assert normalized["artifact_name"] == "historical-artifact"
    assert ctx["legacy_handoff_override"] is True


def test_git_revision_mismatch_is_not_fatal_when_bundle_matches(tmp_path):
    gateway = _gateway(tmp_path)
    health = _health(gateway, tmp_path, revision="different-commit-same-bundle")
    result = assess_runtime_health(health, gateway=gateway, repo_root=tmp_path)
    assert result["status"] == "PASS"
    assert result["git_revision_match"] is False
    assert "GITHUB_REVISION_DIAGNOSTIC_MISMATCH_BUNDLE_COMPATIBLE" in result["warnings"]


def test_bundle_mismatch_is_fatal(tmp_path):
    gateway = _gateway(tmp_path)
    health = _health(gateway, tmp_path)
    health["runtime_app_sha256"] = "bad"
    result = assess_runtime_health(health, gateway=gateway, repo_root=tmp_path)
    assert result["status"] == "FAIL"
    assert "RUNTIME_BUNDLE_HASH_MISMATCH" in result["errors"]


def test_execution_id_and_artifact_names_are_stable(tmp_path):
    gateway = _gateway(tmp_path)
    req = {"family_id": "LOCAL", "race_id": "URW-20260926-R01"}
    eid = derive_execution_id(req)
    assert eid == "LOCAL-URW-20260926-R01-EXEC"
    assert artifact_name(eid, "SOURCE", gateway) == "km-local-execution-LOCAL-URW-20260926-R01-EXEC-SOURCE"


def test_lifecycle_transition_order():
    state = {
        "execution_id": "E",
        "race_id": "R",
        "family_id": "LOCAL",
        "gateway_profile": "GW",
        "current_phase": None,
        "status": "CREATED",
        "phases": {},
    }
    state = record_phase(state, "SOURCE", "SOURCE_VERIFIED")
    state = record_phase(state, "FORMAL", "FINAL_VERIFIED")
    state = record_phase(state, "RESULT", "RESULT_VERIFIED")
    assert state["current_phase"] == "RESULT"
    with pytest.raises(ExecutionGatewayError):
        record_phase({
            "execution_id": "E2", "race_id": "R2", "family_id": "LOCAL",
            "gateway_profile": "GW", "current_phase": None, "status": "CREATED", "phases": {}
        }, "FORMAL", "NO")
