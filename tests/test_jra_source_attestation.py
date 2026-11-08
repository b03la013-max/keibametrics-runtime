from email.message import Message
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
from urllib.error import HTTPError

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime" / "jra_source_runtime"))
import verify_source_attestation as attest


@pytest.fixture
def transport(monkeypatch, tmp_path):
    envelope = tmp_path / "source_receipt_envelope.json"
    envelope.write_text(json.dumps({"artifact": {"race_id": "JRA-TEST"}}))
    timestamp = [1_800_000_000.0]
    calls = []

    def sleep(delay):
        calls.append(("sleep", delay))
        timestamp[0] += delay

    monkeypatch.setattr(attest.time, "time", lambda: timestamp[0])
    monkeypatch.setattr(attest.time, "sleep", sleep)
    monkeypatch.setenv("GH_TOKEN", "test-installation-token")
    monkeypatch.setattr(attest, "verify_payload", lambda _: {
        "valid": True, "github_repository": attest.REPOSITORY, "github_sha": "1" * 40,
        "github_run_id": "123", "family": "JRA", "status": "PASS", "race_id": "JRA-TEST",
    })
    return envelope, calls, timestamp


def api(monkeypatch, calls, responses):
    class Opener:
        def open(self, request, *, timeout):
            calls.append(("request", request.full_url, timeout))
            response = next(responses)
            if isinstance(response, HTTPError):
                raise response
            return BytesIO(json.dumps(response).encode())
    monkeypatch.setattr(attest, "build_opener", lambda _: Opener())


def http_error(code, body="", **headers):
    values = Message()
    for key, value in headers.items():
        values[key.replace("_", "-")] = str(value)
    return HTTPError("https://api.github.com/", code, "", values, BytesIO(body.encode()))


def gh(monkeypatch, calls, *, run="123", failure=""):
    def run_verify(command, **kwargs):
        bundle = Path(command[command.index("--bundle") + 1])
        calls.append(("verify", json.loads(bundle.read_text())))
        assert command[command.index("--signer-workflow") + 1] == attest.WORKFLOW
        assert command[command.index("--source-ref") + 1] == attest.REF
        assert command[command.index("--source-digest") + 1] == "1" * 40
        assert command[command.index("--signer-digest") + 1] == "1" * 40
        assert command[command.index("--cert-oidc-issuer") + 1] == attest.ISSUER
        assert "--deny-self-hosted-runners" in command
        assert "--custom-trusted-root" not in command
        result = {"verificationResult": {
            "signature": {"certificate": {
                "subjectAlternativeName": f"https://github.com/{attest.WORKFLOW}@{attest.REF}",
                "sourceRepositoryIdentifier": attest.REPOSITORY_ID,
                "sourceRepositoryOwnerIdentifier": attest.OWNER_ID,
                "runInvocationURI": f"https://github.com/{attest.REPOSITORY}/actions/runs/{run}/attempts/1",
            }},
            "verifiedTimestamps": [{"timestamp": "2026-11-08T03:45:16Z"}],
        }}
        return subprocess.CompletedProcess(command, int(bool(failure)), json.dumps([result]), failure)
    monkeypatch.setattr(attest.subprocess, "run", run_verify)


def test_durable_bundle_uses_independent_policy_with_no_lookup(transport, monkeypatch):
    envelope, calls, _ = transport
    envelope.with_name(attest.BUNDLE_NAME).write_text('{"test": "durable"}')
    monkeypatch.delenv("GH_TOKEN")
    api(monkeypatch, calls, iter(()))
    gh(monkeypatch, calls)
    assert attest.verify(envelope)["attestation_verification"] == "PERSISTED_BUNDLE"
    assert calls == [("verify", {"test": "durable"})]


@pytest.mark.parametrize("limited,wait", [
    (http_error(403, "API rate limit exceeded for installation", X_RateLimit_Remaining=0,
                X_RateLimit_Reset=1_800_000_004), 4),
    (http_error(429, Retry_After=3), 3),
    (http_error(503), 1),
])
def test_legacy_bundle_retry_recovers_within_deadline(transport, monkeypatch, limited, wait):
    envelope, calls, clock = transport
    api(monkeypatch, calls, iter((limited, {"attestations": [{"bundle": {"test": "retrieved"}}]})))
    gh(monkeypatch, calls)
    assert attest.verify(envelope, deadline=clock[0] + 20)["attestation_verification"] == "GITHUB_API_BUNDLE"
    assert [call[0] for call in calls] == ["request", "sleep", "request", "verify"]
    assert calls[1] == ("sleep", wait)


def test_rate_limit_past_deadline_is_technical_failure(transport, monkeypatch):
    envelope, calls, clock = transport
    api(monkeypatch, calls, iter((http_error(403, "API rate limit exceeded for installation"),)))
    with pytest.raises(RuntimeError, match="RATE_LIMIT:RETRY_BUDGET_EXHAUSTED"):
        attest.verify(envelope, deadline=clock[0] + 5)
    assert [call[0] for call in calls] == ["request"]


@pytest.mark.parametrize("response,reason", [
    (http_error(401), "API_AUTHORIZATION_HTTP_401"),
    (http_error(403), "API_AUTHORIZATION_HTTP_403"),
    (http_error(404), "BUNDLE_NOT_FOUND_HTTP_404"),
    ({"attestations": []}, "BUNDLE_NOT_FOUND"),
])
def test_authorization_and_absent_bundles_are_distinct(transport, monkeypatch, response, reason):
    envelope, calls, _ = transport
    api(monkeypatch, calls, iter((response,)))
    with pytest.raises(RuntimeError, match=reason):
        attest.verify(envelope)
    assert [call[0] for call in calls] == ["request"]


def test_expired_race_never_calls_api_or_verifier(transport, monkeypatch):
    envelope, calls, clock = transport
    api(monkeypatch, calls, iter(()))
    gh(monkeypatch, calls)
    with pytest.raises(RuntimeError, match="DEADLINE_EXCEEDED"):
        attest.verify(envelope, deadline=clock[0])
    assert not calls


def test_signed_fail_cannot_enter_attestation_gate(transport, monkeypatch):
    envelope, calls, _ = transport
    api(monkeypatch, calls, iter(()))
    verify_payload = attest.verify_payload
    monkeypatch.setattr(attest, "verify_payload", lambda data: {**verify_payload(data), "status": "FAIL"})
    with pytest.raises(RuntimeError, match="ENVELOPE_NOT_JRA_PASS"):
        attest.verify(envelope)
    assert not calls


def test_source_must_match_request_race_before_lookup(transport, monkeypatch):
    envelope, calls, _ = transport
    api(monkeypatch, calls, iter(()))
    with pytest.raises(RuntimeError, match="REQUEST_RACE_MISMATCH"):
        attest.verify(envelope, request={"race_id": "OTHER-RACE"})
    assert not calls


def test_attestation_cannot_predate_signed_source_freeze(transport, monkeypatch):
    envelope, calls, _ = transport
    envelope.write_text(json.dumps({"artifact": {"source_freeze_at": "2026-11-08T03:45:17Z"}}))
    envelope.with_name(attest.BUNDLE_NAME).write_text('{}')
    api(monkeypatch, calls, iter(()))
    gh(monkeypatch, calls)
    with pytest.raises(RuntimeError, match="SIGNED_BEFORE_SOURCE_FREEZE"):
        attest.verify(envelope)
    assert calls == [("verify", {})]


@pytest.mark.parametrize("run,failure,reason", [
    ("999", "", "CERTIFICATE_CONTEXT_MISMATCH"),
    ("123", "signature verification failed", "SIGNATURE_OR_POLICY_INVALID"),
    ("123", "error creating Sigstore verifier: trust store unavailable", "TRUST_ROOT_UNAVAILABLE"),
])
def test_present_invalid_bundle_fails_closed_without_lookup(transport, monkeypatch, run, failure, reason):
    envelope, calls, _ = transport
    envelope.with_name(attest.BUNDLE_NAME).write_text('{"test": "present"}')
    api(monkeypatch, calls, iter(()))
    gh(monkeypatch, calls, run=run, failure=failure)
    with pytest.raises(RuntimeError, match=reason):
        attest.verify(envelope)
    assert calls == [("verify", {"test": "present"})]
