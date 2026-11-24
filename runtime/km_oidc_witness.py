"""GitHub Actions OIDC witness for artifacts, usable in a private personal repository.

Owner approval 2026-11-21 10:46 (Current Authority R55). `actions/attest` /
`gh attestation verify` need GitHub artifact attestations, which are not available
for private repositories on a personal plan. This module gives the same two
guarantees without Sigstore's public log:

1. *Who*: an OIDC token minted by GitHub for this exact workflow run
   (repository id, owner id, workflow file at refs/heads/main, head sha, run id,
   GitHub-hosted runner) and signed with GitHub's published RS256 key.
2. *What and when*: the token's audience binds the SHA-256 of the artifact bytes,
   and its `iat` is GitHub's own issue time, used as the independent witness time.

`mint` runs inside the workflow (needs `permissions: id-token: write`). It stores the
token together with the public JWK that signed it, fetched from GitHub's JWKS.
`verify` checks the RS256 signature (against GitHub's live JWKS when the key is still
published, otherwise against the stored JWK, reported as HISTORIC_STORED_KEY), every
identity claim, the artifact digest and the time window. Token expiry is deliberately
ignored: the witness is a signed statement about the past, not a credential.

  python runtime/km_oidc_witness.py mint <artifact> <witness.json> --purpose JRA_SOURCE
  python runtime/km_oidc_witness.py verify <artifact> <witness.json> --workflow km-jra-source-first-runner.yml
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

PROFILE = "KM-OIDC-WITNESS-v1"
ISSUER = "https://token.actions.githubusercontent.com"
JWKS_URL = ISSUER + "/.well-known/jwks"
REPOSITORY = "b03la013-max/keibametrics-runtime"
REPOSITORY_ID = "1373764421"
OWNER_ID = "284565719"
REF = "refs/heads/main"
AUDIENCE_PREFIX = "km-witness:sha256:"
MAX_BYTES = 64 * 1024


class WitnessError(RuntimeError):
    pass


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _digest(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audience(digest: str, purpose: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{64}", digest) or not re.fullmatch(r"[A-Z0-9_]{1,40}", purpose):
        raise WitnessError("KM_OIDC_WITNESS_AUDIENCE_INPUT_INVALID")
    return f"{AUDIENCE_PREFIX}{digest}:{purpose}"


def _get_json(url: str, headers: dict | None = None, timeout: float = 10) -> dict:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise WitnessError("KM_OIDC_WITNESS_RESPONSE_TOO_LARGE")
    return json.loads(raw)


def live_jwks(fetch=None) -> list[dict]:
    data = fetch(JWKS_URL) if fetch else _get_json(JWKS_URL)
    keys = data.get("keys")
    if not isinstance(keys, list):
        raise WitnessError("KM_OIDC_WITNESS_JWKS_INVALID")
    return keys


def _request_token(aud: str) -> str:
    url, token = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL"), os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
    if not url or not token:
        raise WitnessError("KM_OIDC_WITNESS_ID_TOKEN_PERMISSION_MISSING")
    sep = "&" if "?" in url else "?"
    last = None
    for attempt in range(3):
        try:
            value = _get_json(url + sep + "audience=" + urllib.parse.quote(aud, safe=""),
                              {"Authorization": "Bearer " + token}).get("value")
            if value:
                return value
            last = "EMPTY"
        except (OSError, ValueError) as e:  # transport only; GitHub has no refusal mode here we could fix
            last = type(e).__name__
        time.sleep(2 ** attempt)
    raise WitnessError("KM_OIDC_WITNESS_ID_TOKEN_UNAVAILABLE:" + str(last))


def mint(artifact: Path, out: Path, purpose: str, *, request_token=None, fetch=None) -> dict:
    digest = _digest(artifact)
    aud = audience(digest, purpose)
    jwt = (request_token or _request_token)(aud)
    header = json.loads(_b64d(jwt.split(".")[0]))
    keys = [k for k in live_jwks(fetch) if k.get("kid") == header.get("kid")]
    if len(keys) != 1:
        raise WitnessError("KM_OIDC_WITNESS_SIGNING_KEY_NOT_PUBLISHED")
    witness = {"profile": PROFILE, "purpose": purpose, "artifact_name": Path(artifact).name,
               "artifact_sha256": digest, "audience": aud, "token": jwt, "jwk": keys[0]}
    # Prove the stored witness verifies before anyone relies on it.
    verify_token(witness, digest, jwks=[keys[0]])
    Path(out).write_text(json.dumps(witness, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    return witness


def _public_key(jwk: dict):
    if jwk.get("kty") != "RSA" or jwk.get("alg", "RS256") != "RS256":
        raise WitnessError("KM_OIDC_WITNESS_KEY_TYPE_INVALID")
    n = int.from_bytes(_b64d(jwk["n"]), "big")
    e = int.from_bytes(_b64d(jwk["e"]), "big")
    if n.bit_length() < 2048:
        raise WitnessError("KM_OIDC_WITNESS_KEY_TOO_SMALL")
    return rsa.RSAPublicNumbers(e, n).public_key()


def verify_token(witness: dict, digest: str, *, jwks: list[dict]) -> dict:
    try:
        h64, p64, s64 = witness["token"].split(".")
        header, claims = json.loads(_b64d(h64)), json.loads(_b64d(p64))
    except (KeyError, ValueError) as e:
        raise WitnessError("KM_OIDC_WITNESS_TOKEN_MALFORMED") from e
    if header.get("alg") != "RS256":
        raise WitnessError("KM_OIDC_WITNESS_ALG_INVALID")
    keys = [k for k in jwks if k.get("kid") == header.get("kid")]
    if len(keys) != 1:
        raise WitnessError("KM_OIDC_WITNESS_KEY_NOT_FOUND")
    try:
        _public_key(keys[0]).verify(_b64d(s64), f"{h64}.{p64}".encode(), padding.PKCS1v15(), hashes.SHA256())
    except InvalidSignature:
        raise WitnessError("KM_OIDC_WITNESS_SIGNATURE_INVALID") from None
    aud = claims.get("aud")
    if isinstance(aud, list):
        aud = aud[0] if len(aud) == 1 else None
    if claims.get("iss") != ISSUER:
        raise WitnessError("KM_OIDC_WITNESS_ISSUER_INVALID")
    if not (isinstance(aud, str) and aud.startswith(AUDIENCE_PREFIX + digest + ":") and aud == witness.get("audience")):
        raise WitnessError("KM_OIDC_WITNESS_ARTIFACT_DIGEST_MISMATCH")
    return claims


def verify(artifact: Path, witness_path: Path, *, workflow: str, purpose: str | None = None,
           sha: str | None = None, run_id: str | None = None, not_before: float | None = None,
           not_after: float | None = None, fetch=None) -> dict:
    """Return {'witnessed_at': ISO, 'key_source': ..., 'claims': {...}} or raise WitnessError."""
    wp = Path(witness_path)
    if wp.is_symlink() or not wp.is_file() or not 0 < wp.stat().st_size <= MAX_BYTES:
        raise WitnessError("KM_OIDC_WITNESS_FILE_INVALID")
    witness = json.loads(wp.read_text(encoding="utf-8"))
    if witness.get("profile") != PROFILE:
        raise WitnessError("KM_OIDC_WITNESS_PROFILE_INVALID")
    if purpose and witness.get("purpose") != purpose:
        raise WitnessError("KM_OIDC_WITNESS_PURPOSE_MISMATCH")
    digest = _digest(artifact)
    try:
        published = live_jwks(fetch)
        key_source = "GITHUB_LIVE_JWKS"
    except (OSError, ValueError, WitnessError):
        published = []
    kid = json.loads(_b64d(witness["token"].split(".")[0])).get("kid")
    if not any(k.get("kid") == kid for k in published):
        # Rotated out (or JWKS unreachable): the key stored at mint time, which was
        # verified against the live JWKS then, is the only remaining evidence.
        published, key_source = [witness.get("jwk") or {}], "HISTORIC_STORED_KEY"
    elif witness.get("jwk") and [k for k in published if k.get("kid") == kid][0].get("n") != witness["jwk"].get("n"):
        raise WitnessError("KM_OIDC_WITNESS_STORED_KEY_MISMATCH")
    c = verify_token(witness, digest, jwks=published)
    expected_wf = f"{REPOSITORY}/.github/workflows/{workflow}@{REF}"
    checks = {
        "repository": c.get("repository") == REPOSITORY,
        "repository_id": str(c.get("repository_id")) == REPOSITORY_ID,
        "repository_owner_id": str(c.get("repository_owner_id")) == OWNER_ID,
        "workflow_ref": c.get("workflow_ref") == expected_wf,
        "ref": c.get("ref") == REF,
        "runner_environment": c.get("runner_environment") == "github-hosted",
        "sha": sha is None or c.get("sha") == sha,
        "run_id": run_id is None or str(c.get("run_id")) == str(run_id),
    }
    bad = [k for k, ok in checks.items() if not ok]
    if bad:
        raise WitnessError("KM_OIDC_WITNESS_CLAIM_MISMATCH:" + ",".join(bad))
    iat = c.get("iat")
    if not isinstance(iat, (int, float)):
        raise WitnessError("KM_OIDC_WITNESS_IAT_MISSING")
    if not_before is not None and iat < int(not_before):  # iat has whole-second precision
        raise WitnessError("KM_OIDC_WITNESS_BEFORE_NOT_BEFORE")
    if not_after is not None and iat > not_after:
        raise WitnessError("KM_OIDC_WITNESS_AFTER_NOT_AFTER")
    return {"witnessed_at": datetime.fromtimestamp(iat, timezone.utc).isoformat(), "key_source": key_source,
            "claims": {k: c.get(k) for k in ("repository", "workflow_ref", "sha", "run_id", "run_attempt",
                                             "event_name", "runner_environment", "iat")}}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("mint"); m.add_argument("artifact", type=Path); m.add_argument("out", type=Path)
    m.add_argument("--purpose", required=True)
    v = sub.add_parser("verify"); v.add_argument("artifact", type=Path); v.add_argument("witness", type=Path)
    v.add_argument("--workflow", required=True); v.add_argument("--purpose"); v.add_argument("--sha"); v.add_argument("--run-id")
    a = ap.parse_args()
    if a.cmd == "mint":
        w = mint(a.artifact, a.out, a.purpose)
        print(json.dumps({"status": "MINTED", "artifact_sha256": w["artifact_sha256"], "purpose": a.purpose}))
    else:
        print(json.dumps(verify(a.artifact, a.witness, workflow=a.workflow, purpose=a.purpose,
                                sha=a.sha, run_id=a.run_id), sort_keys=True))


if __name__ == "__main__":
    main()
