import copy
import datetime as dt
import hashlib
import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runtime"))
import openai_prediction_owner_candidate as owner
import formal_execution_orchestrator as orchestrator


@pytest.fixture
def sample(tmp_path):
    config = {"mode": "SHADOW", "production_authorized": False,
              "credential_owner_type": "service_account", "project_id": "project-test",
              "model_identifier": "test-model-snapshot"}
    for key in ("instruction", "venue_canon"):
        raw = ("existing frozen " + key).encode()
        (tmp_path / (key + ".txt")).write_bytes(raw)
        config[key] = {"path": key + ".txt", "sha256": hashlib.sha256(raw).hexdigest()}
    context = {"execution_id": "A-EXEC", "race_id": "A", "source_binding": {"source": "a"},
               "current_authority": {"manifest_id": "frozen-authority"},
               "source_verification": {"verified": True},
               "prediction_cutoff": "2030-01-01T01:00:00+00:00",
               "release_deadline_at": "2030-01-01T01:10:00+00:00",
               "signed_source": {"receipt": {"race_id": "A", "phase": "SOURCE"},
                                 "artifact": {"formal_ready": True,
                                              "source_freeze_at": "2030-01-01T00:59:00+00:00",
                                              "active_runner_universe": {"runner_count": 2,
                                                                         "runners": [{"runner_id": "1"}, {"runner_id": "2"}]}}}}
    prediction = {"ranking": ["1", "2"], "roles": [{"runner_id": "1", "columns": ["W"]},
                                                        {"runner_id": "2", "columns": ["P2"]}],
                  "role_registry": [{"runner_id": "1", "column": "W", "status": "CORE"},
                                    {"runner_id": "2", "column": "P2", "status": "CORE"}],
                  "pair_dispositions": [{"head": "1", "second": "2", "status": "PURCHASE", "reason": "evidence"}],
                  "third_dispositions": [], "uncertainty": {"level": "UNKNOWN", "reasons": ["missing"]},
                  "venue_prediction_context": {"interpretation": "frozen", "evidence_refs": ["SOURCE"]}}
    now = dt.datetime(2030, 1, 1, 1, 1, tzinfo=dt.timezone.utc)
    def call(payload, timeout):
        assert payload["store"] is False
        assert payload["text"]["format"]["strict"] is True
        assert "static_prediction" not in payload["input"]
        return {"id": "resp_test", "model": config["model_identifier"], "status": "completed",
                "output": [{"content": [{"type": "output_text", "text": json.dumps(prediction)}]}]}
    return context, config, prediction, call, now


def run(sample, tmp_path):
    context, config, _, call, now = sample
    return owner.execute(context, config, root=tmp_path, call=call, now=now)


def test_structured_owner_freezes_lineage_without_production_effect(sample, tmp_path):
    result = run(sample, tmp_path)
    assert result["promotion"] == "HOLD"
    assert result["production_authorized"] is False
    assert result["lineage"]["prediction_output_sha256"] == owner.digest(result["prediction"])
    for key in ("source_sha256", "venue_canon_sha256", "current_authority_sha256",
                "instruction_sha256", "schema_sha256", "model_identifier",
                "api_response_identifier", "freeze_timestamp"):
        assert result["lineage"][key]


@pytest.mark.parametrize("key,value", [("mode", "PRODUCTION"), ("production_authorized", True),
                                      ("credential_owner_type", "user"), ("project_id", "")])
def test_rejects_personal_key_metadata_and_promotion(sample, tmp_path, key, value):
    sample[1][key] = value
    with pytest.raises(owner.CandidateHold):
        run(sample, tmp_path)


@pytest.mark.parametrize("key", ["official_result", "finish_order", "payouts", "settlement",
                               "candidate_indices", "krs_ranking", "odds_ranking", "popularity_ranking"])
def test_outcome_or_substitute_ranking_never_enters_api(sample, tmp_path, key):
    sample[0]["signed_source"]["artifact"][key] = [1, 2]
    with pytest.raises(owner.CandidateHold, match="FORBIDDEN"):
        run(sample, tmp_path)


@pytest.mark.parametrize("case", ["source_partial", "verification", "race", "cutoff", "deadline", "canon_hash"])
def test_invalid_authority_temporal_and_source_hold(sample, tmp_path, case):
    context, config, _, _, _ = sample
    if case == "source_partial": context["signed_source"]["artifact"]["formal_ready"] = False
    if case == "verification": context["source_verification"]["verified"] = False
    if case == "race": context["signed_source"]["receipt"]["race_id"] = "OTHER"
    if case == "cutoff": context["signed_source"]["artifact"]["source_freeze_at"] = "2030-01-01T01:02:00+00:00"
    if case == "deadline": context["release_deadline_at"] = "2030-01-01T01:00:00+00:00"
    if case == "canon_hash": config["venue_canon"]["sha256"] = "bad"
    with pytest.raises(owner.CandidateHold): run(sample, tmp_path)


@pytest.mark.parametrize("case", ["duplicate_rank", "outside_universe", "schema_extra", "roles", "self_pair", "secret"])
def test_invalid_response_rejected_before_artifact(sample, tmp_path, case, monkeypatch):
    prediction = sample[2]
    if case == "duplicate_rank": prediction["ranking"] = ["1", "1"]
    if case == "outside_universe": prediction["ranking"] = ["1", "3"]
    if case == "schema_extra": prediction["candidate_score"] = 100
    if case == "roles": prediction["role_registry"] = []
    if case == "self_pair": prediction["pair_dispositions"][0]["second"] = "1"
    if case == "secret":
        monkeypatch.setenv("OPENAI_API_KEY", "test-private-value")
        prediction["uncertainty"]["reasons"] = ["test-private-value"]
    with pytest.raises(owner.CandidateHold): run(sample, tmp_path)


def test_comparison_requires_identical_source_and_never_promotes(sample, tmp_path):
    result = run(sample, tmp_path)
    p = sample[2]
    baseline = {"static_prediction": {"ranking": p["ranking"], "roles": {"1": ["W"], "2": ["P2"]},
                                      "uncertainty": p["uncertainty"]},
                **{key: p[key] for key in ("role_registry", "pair_dispositions", "third_dispositions", "venue_prediction_context")}}
    comparison = owner.compare(result, baseline, sample[0]["source_binding"])
    assert comparison["status"] == "STRUCTURAL_MATCH"
    assert comparison["production_equivalence"] == "UNPROVEN"
    with pytest.raises(owner.CandidateHold, match="SOURCE_BASIS"):
        owner.compare(result, baseline, {"source": "changed"})
    baseline["static_prediction"]["ranking"] = ["2", "1"]
    assert owner.compare(result, baseline, sample[0]["source_binding"])["status"] == "SEMANTIC_DIFFERENCE"


def test_runtime_secret_absent_does_not_create_personal_key_or_leak(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(owner.CandidateHold, match="SERVICE_ACCOUNT_RUNTIME_SECRET_MISSING"):
        owner.responses_call({}, timeout=1)


def test_shadow_hold_is_nonblocking_and_diagnostic_is_sanitized(tmp_path, monkeypatch):
    monkeypatch.setattr(orchestrator, "ROOT", tmp_path)
    def fail(*args, **kwargs):
        raise RuntimeError("SECRET MUST NOT BE SAVED")
    monkeypatch.setattr(owner, "pinned_text", fail)
    report = orchestrator.execute_prediction_owner_shadow(
        {"openai_prediction_owner_candidate_config": {}}, run_id="test", github_sha="sha", tmp_root=tmp_path)
    assert report == {"status": "HOLD", "code": "SHADOW_RUNTIME_HOLD", "production_effect": "NONE", "promotion": "HOLD"}


@pytest.mark.parametrize("case", ["refusal", "incomplete", "model", "missing_id"])
def test_provider_response_integrity(sample, tmp_path, case):
    context, config, _, original, now = sample
    def altered(payload, timeout):
        response = original(payload, timeout)
        if case == "refusal": response["output"][0]["content"] = [{"type": "refusal", "refusal": "no"}]
        if case == "incomplete": response["status"] = "incomplete"
        if case == "model": response["model"] = "different-model"
        if case == "missing_id": response.pop("id")
        return response
    with pytest.raises(owner.CandidateHold):
        owner.execute(context, config, root=tmp_path, call=altered, now=now)


def test_shadow_reserves_production_deadline_budget(sample, tmp_path):
    sample[0]["release_deadline_at"] = "2030-01-01T01:02:00+00:00"
    with pytest.raises(owner.CandidateHold, match="PROTECT_PRODUCTION"):
        run(sample, tmp_path)
