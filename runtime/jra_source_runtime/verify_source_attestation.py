"""Verify a durable JRA SOURCE envelope against the official GitHub OIDC trust chain."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
from http.client import HTTPException
import json
import math
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
import time
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from cryptography.exceptions import InvalidSignature

from verify_source_envelope import verify_payload


REPOSITORY = "b03la013-max/keibametrics-runtime"
REPOSITORY_ID = "1373764421"
OWNER_ID = "284565719"
REF = "refs/heads/main"
WORKFLOW = REPOSITORY + "/.github/workflows/km-jra-source-first-runner.yml"
ISSUER = "https://token.actions.githubusercontent.com"
BUNDLE_NAME = "source_attestation_bundle.json"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


class _NoRedirect(HTTPRedirectHandler):
    # The installation token belongs only on the canonical API origin.
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _timestamp(value: str) -> float:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("JRA_SOURCE_ATTESTATION_TIMEZONE_REQUIRED")
    return parsed.timestamp()


def request_deadline(request: dict) -> float | None:
    if (request.get("temporal_mode") or "FORMAL-PRE-RACE") != "FORMAL-PRE-RACE":
        return None
    value = (request.get("external_dispatch_deadline_at") or request.get("release_deadline_at")
             or request.get("scheduled_post_at"))
    return _timestamp(value) if value else None


def _seconds_left(deadline: float) -> float:
    remaining = deadline - time.time()
    if remaining <= 0:
        raise RuntimeError("JRA_SOURCE_ATTESTATION_DEADLINE_EXCEEDED")
    return remaining


def _numeric_header(headers, name):
    value = headers.get(name, "")
    return int(value) if re.fullmatch(r"[0-9]{1,12}", value) else None


def _fetch_bundles(envelope: Path, deadline: float, destination: Path) -> None:
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise RuntimeError("JRA_SOURCE_ATTESTATION_API_CREDENTIAL_MISSING")
    digest = hashlib.sha256(envelope.read_bytes()).hexdigest()
    url = (
        f"https://api.github.com/repos/{REPOSITORY}/attestations/sha256:{digest}"
        "?per_page=30&predicate_type=https%3A%2F%2Fslsa.dev%2Fprovenance%2Fv1"
    )
    request = Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    opener = build_opener(_NoRedirect())
    for attempt in range(3):
        try:
            with opener.open(request, timeout=min(10, _seconds_left(deadline))) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
            break
        except HTTPError as error:
            code = error.code
            with error:
                message = error.read(4096).lower()
            headers = error.headers
            retry_after = _numeric_header(headers, "Retry-After")
            exhausted = headers.get("X-RateLimit-Remaining") == "0"
            if code == 429 or code == 403 and (
                exhausted or retry_after is not None or b"rate limit exceeded" in message
                or b"exceeded a secondary rate limit" in message
            ):
                reason = "RATE_LIMIT"
                delay = retry_after if retry_after is not None else 60
                reset = _numeric_header(headers, "X-RateLimit-Reset")
                if exhausted and reset is not None:
                    delay = max(retry_after or 0, reset - time.time())
            elif code in (401, 403):
                raise RuntimeError(f"JRA_SOURCE_ATTESTATION_API_AUTHORIZATION_HTTP_{code}") from None
            elif code == 404:
                raise RuntimeError("JRA_SOURCE_ATTESTATION_BUNDLE_NOT_FOUND_HTTP_404") from None
            elif 500 <= code <= 599:
                reason, delay = f"API_TRANSIENT_HTTP_{code}", retry_after or 2 ** attempt
            else:
                raise RuntimeError(f"JRA_SOURCE_ATTESTATION_API_HTTP_{code}") from None
        except (URLError, TimeoutError, OSError, HTTPException):
            reason, delay = "API_TRANSPORT", 2 ** attempt
        delay = max(1, delay)
        if attempt == 2 or delay >= deadline - time.time():
            raise RuntimeError(f"JRA_SOURCE_ATTESTATION_{reason}:RETRY_BUDGET_EXHAUSTED")
        time.sleep(delay)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise RuntimeError("JRA_SOURCE_ATTESTATION_API_RESPONSE_TOO_LARGE")
    try:
        records = json.loads(raw)["attestations"]
        if not isinstance(records, list):
            raise TypeError
        bundles = [record["bundle"] for record in records]
        if any(not isinstance(bundle, dict) for bundle in bundles):
            raise TypeError
    except (KeyError, TypeError, ValueError) as error:
        raise RuntimeError("JRA_SOURCE_ATTESTATION_API_RESPONSE_INVALID") from error
    if not bundles:
        raise RuntimeError("JRA_SOURCE_ATTESTATION_BUNDLE_NOT_FOUND")
    destination.write_text("".join(json.dumps(bundle) + "\n" for bundle in bundles), encoding="utf-8")


def _source_context(source: dict) -> tuple[str, str]:
    revision = str(source.get("github_sha") or "")
    run = str(source.get("github_run_id") or "")
    if source.get("github_repository") != REPOSITORY or not (
        re.fullmatch(r"[0-9a-f]{40}", revision) and re.fullmatch(r"[1-9][0-9]*", run)
    ):
        raise RuntimeError("JRA_SOURCE_ATTESTATION_ENVELOPE_CONTEXT_INVALID")
    return revision, run


def _verify_bundle(envelope: Path, bundle: Path, revision: str, run: str, deadline: float) -> str:
    try:
        result = subprocess.run(
            [
                "gh", "attestation", "verify", str(envelope), "--repo", REPOSITORY,
                "--hostname", "github.com",
                "--bundle", str(bundle), "--signer-workflow", WORKFLOW,
                "--cert-oidc-issuer", ISSUER, "--source-ref", REF,
                "--source-digest", revision, "--signer-digest", revision,
                "--deny-self-hosted-runners", "--format", "json",
            ],
            capture_output=True, text=True, timeout=_seconds_left(deadline), check=False,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("JRA_SOURCE_ATTESTATION_DEADLINE_EXCEEDED") from None
    except OSError as error:
        raise RuntimeError("JRA_SOURCE_ATTESTATION_VERIFIER_UNAVAILABLE") from error
    if result.returncode:
        if "error creating Sigstore verifier:" in result.stderr:
            raise RuntimeError("JRA_SOURCE_ATTESTATION_TRUST_ROOT_UNAVAILABLE:" + result.stderr[-600:])
        raise RuntimeError("JRA_SOURCE_ATTESTATION_SIGNATURE_OR_POLICY_INVALID:" + result.stderr[-800:])
    try:
        verified = [record["verificationResult"] for record in json.loads(result.stdout)]
        invocation = f"https://github.com/{REPOSITORY}/actions/runs/{run}/attempts/"
        for record in verified:
            cert = record["signature"]["certificate"]
            if (cert.get("subjectAlternativeName") != f"https://github.com/{WORKFLOW}@{REF}"
                    or cert.get("sourceRepositoryIdentifier") != REPOSITORY_ID
                    or cert.get("sourceRepositoryOwnerIdentifier") != OWNER_ID
                    or not re.fullmatch(re.escape(invocation) + r"[1-9][0-9]*", cert.get("runInvocationURI") or "")):
                continue
            timestamp = min((entry["timestamp"] for entry in record["verifiedTimestamps"]), key=_timestamp)
            _seconds_left(deadline)
            return timestamp
    except (KeyError, TypeError, ValueError) as error:
        raise RuntimeError("JRA_SOURCE_ATTESTATION_VERIFIER_RESPONSE_INVALID") from error
    raise RuntimeError("JRA_SOURCE_ATTESTATION_CERTIFICATE_CONTEXT_MISMATCH")


def verify(envelope: Path | str, *, request: dict | None = None, deadline: float | None = None) -> dict:
    envelope = Path(envelope)
    request = request or {}
    requested_deadline = request_deadline(request)
    if requested_deadline is not None:
        deadline = min(deadline, requested_deadline) if deadline is not None else requested_deadline
    verification_deadline = min(deadline, time.time() + 90) if deadline is not None else time.time() + 90
    _seconds_left(verification_deadline)
    payload = json.loads(envelope.read_text(encoding="utf-8"))
    try:
        source = verify_payload(payload)
    except InvalidSignature:
        raise RuntimeError("JRA_SOURCE_ATTESTATION_ENVELOPE_SIGNATURE_INVALID") from None
    if (source.get("valid"), source.get("family"), source.get("status")) != (True, "JRA", "PASS"):
        raise RuntimeError("JRA_SOURCE_ATTESTATION_ENVELOPE_NOT_JRA_PASS")
    artifact = payload.get("artifact") or {}
    expected_race = request.get("race_id")
    if expected_race and (source.get("race_id") != expected_race or artifact.get("race_id") != expected_race):
        raise RuntimeError("JRA_SOURCE_ATTESTATION_REQUEST_RACE_MISMATCH")
    cutoff = request.get("prediction_cutoff")
    frozen_at = artifact.get("source_freeze_at")
    if requested_deadline is not None and cutoff:
        if (artifact.get("prediction_cutoff") != cutoff or not frozen_at
                or _timestamp(frozen_at) > _timestamp(cutoff)):
            raise RuntimeError("JRA_SOURCE_ATTESTATION_SOURCE_FREEZE_INVALID")
    revision, run = _source_context(source)
    bundle = envelope.with_name(BUNDLE_NAME)
    if bundle.is_symlink() or (bundle.exists() and not bundle.is_file()):
        raise RuntimeError("JRA_SOURCE_ATTESTATION_BUNDLE_PATH_INVALID")
    if bundle.is_file():
        if not 0 < bundle.stat().st_size <= MAX_RESPONSE_BYTES:
            raise RuntimeError("JRA_SOURCE_ATTESTATION_BUNDLE_SIZE_INVALID")
        timestamp = _verify_bundle(envelope, bundle, revision, run, verification_deadline)
        method = "PERSISTED_BUNDLE"
    else:
        with TemporaryDirectory() as directory:
            fetched = Path(directory) / "attestations.jsonl"
            _fetch_bundles(envelope, verification_deadline, fetched)
            timestamp = _verify_bundle(envelope, fetched, revision, run, verification_deadline)
        method = "GITHUB_API_BUNDLE"
    witnessed = _timestamp(timestamp)
    # Transparency logs may record only whole seconds.
    if frozen_at and witnessed < math.floor(_timestamp(frozen_at)):
        raise RuntimeError("JRA_SOURCE_ATTESTATION_SIGNED_BEFORE_SOURCE_FREEZE")
    if deadline is not None and witnessed > deadline:
        raise RuntimeError("JRA_SOURCE_ATTESTATION_SIGNED_AFTER_DEADLINE")
    return {**source, "attestation_verification": method, "attestation_verified_timestamp": timestamp}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("envelope", type=Path)
    parser.add_argument("--request", type=Path)
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8")) if args.request else None
    print(json.dumps(verify(args.envelope, request=request), sort_keys=True))
