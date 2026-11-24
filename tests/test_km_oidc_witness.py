"""Current Authority R55: GitHub OIDC token witness (private repository capable)."""
import base64, json, sys
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(ROOT / "runtime/jra_source_runtime"))
import km_oidc_witness as W  # noqa: E402

KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
OTHER = rsa.generate_private_key(public_exponent=65537, key_size=2048)


def b64(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def jwk(key, kid="k1"):
    n = key.public_key().public_numbers()
    return {"kty": "RSA", "alg": "RS256", "kid": kid, "use": "sig",
            "n": b64(n.n.to_bytes((n.n.bit_length() + 7) // 8, "big")), "e": b64(n.e.to_bytes(3, "big"))}


def token(claims, key=KEY, kid="k1"):
    h = b64(json.dumps({"alg": "RS256", "kid": kid, "typ": "JWT"}).encode())
    p = b64(json.dumps(claims).encode())
    sig = key.sign(f"{h}.{p}".encode(), padding.PKCS1v15(), hashes.SHA256())
    return f"{h}.{p}.{b64(sig)}"


def claims(aud, **over):
    c = {"iss": W.ISSUER, "aud": aud, "repository": W.REPOSITORY, "repository_id": W.REPOSITORY_ID,
         "repository_owner_id": W.OWNER_ID, "ref": W.REF, "sha": "a" * 40, "run_id": "77",
         "workflow_ref": f"{W.REPOSITORY}/.github/workflows/km-jra-source-first-runner.yml@{W.REF}",
         "runner_environment": "github-hosted", "event_name": "push", "iat": 1_800_000_000}
    c.update(over)
    return c


def jwks_fetch(*keys):
    return lambda url: {"keys": list(keys)}


@pytest.fixture
def art(tmp_path):
    p = tmp_path / "source_receipt_envelope.json"
    p.write_text('{"x":1}')
    return p


def mint(art, out, **over):
    aud = W.audience(W._digest(art), "JRA_SOURCE")
    return W.mint(art, out, "JRA_SOURCE", request_token=lambda a: token(claims(a, **over)),
                  fetch=jwks_fetch(jwk(KEY)))


def test_mint_and_verify_bind_digest_identity_and_time(art, tmp_path):
    w = tmp_path / "source_oidc_witness.json"
    mint(art, w)
    r = W.verify(art, w, workflow="km-jra-source-first-runner.yml", purpose="JRA_SOURCE", sha="a" * 40,
                 run_id="77", not_before=1_799_999_999.5, not_after=1_800_000_001, fetch=jwks_fetch(jwk(KEY)))
    assert r["key_source"] == "GITHUB_LIVE_JWKS" and r["witnessed_at"].startswith("2027-01-15")


def test_rotated_key_uses_stored_key_and_unreachable_jwks_too(art, tmp_path):
    w = tmp_path / "w.json"
    mint(art, w)
    assert W.verify(art, w, workflow="km-jra-source-first-runner.yml",
                    fetch=jwks_fetch(jwk(OTHER, "k2")))["key_source"] == "HISTORIC_STORED_KEY"
    def down(url):
        raise OSError("offline")
    assert W.verify(art, w, workflow="km-jra-source-first-runner.yml", fetch=down)["key_source"] == "HISTORIC_STORED_KEY"


@pytest.mark.parametrize("over,code", [
    ({"repository": "evil/fork"}, "CLAIM_MISMATCH"),
    ({"repository_id": "1"}, "CLAIM_MISMATCH"),
    ({"workflow_ref": f"{W.REPOSITORY}/.github/workflows/other.yml@{W.REF}"}, "CLAIM_MISMATCH"),
    ({"ref": "refs/heads/feature"}, "CLAIM_MISMATCH"),
    ({"runner_environment": "self-hosted"}, "CLAIM_MISMATCH"),
    ({"sha": "b" * 40}, "CLAIM_MISMATCH"),
    ({"iss": "https://evil"}, "ISSUER_INVALID"),
])
def test_identity_claims_are_strict(art, tmp_path, over, code):
    w = tmp_path / "w.json"
    aud = W.audience(W._digest(art), "JRA_SOURCE")
    good = mint(art, w)
    good["token"] = token(claims(aud, **over))
    w.write_text(json.dumps(good))
    with pytest.raises(W.WitnessError, match=code):
        W.verify(art, w, workflow="km-jra-source-first-runner.yml", sha="a" * 40, fetch=jwks_fetch(jwk(KEY)))


def test_changed_bytes_forged_key_window_and_purpose_are_refused(art, tmp_path):
    w = tmp_path / "w.json"
    good = mint(art, w)
    art.write_text('{"x":2}')
    with pytest.raises(W.WitnessError, match="DIGEST_MISMATCH"):
        W.verify(art, w, workflow="km-jra-source-first-runner.yml", fetch=jwks_fetch(jwk(KEY)))
    art.write_text('{"x":1}')
    forged = dict(good, token=token(claims(good["audience"]), key=OTHER), jwk=jwk(OTHER))
    w.write_text(json.dumps(forged))
    # live JWKS still publishes k1 with a different modulus than the stored (forged) one
    with pytest.raises(W.WitnessError, match="STORED_KEY_MISMATCH"):
        W.verify(art, w, workflow="km-jra-source-first-runner.yml", fetch=jwks_fetch(jwk(KEY)))
    w.write_text(json.dumps(good))
    with pytest.raises(W.WitnessError, match="AFTER_NOT_AFTER"):
        W.verify(art, w, workflow="km-jra-source-first-runner.yml", not_after=1_799_999_000, fetch=jwks_fetch(jwk(KEY)))
    with pytest.raises(W.WitnessError, match="BEFORE_NOT_BEFORE"):
        W.verify(art, w, workflow="km-jra-source-first-runner.yml", not_before=1_800_000_100, fetch=jwks_fetch(jwk(KEY)))
    with pytest.raises(W.WitnessError, match="PURPOSE_MISMATCH"):
        W.verify(art, w, workflow="km-jra-source-first-runner.yml", purpose="JRA_NO_BET_TERMINAL", fetch=jwks_fetch(jwk(KEY)))


def test_mint_refuses_without_id_token_permission(art, tmp_path, monkeypatch):
    monkeypatch.delenv("ACTIONS_ID_TOKEN_REQUEST_URL", raising=False)
    with pytest.raises(W.WitnessError, match="PERMISSION_MISSING"):
        W.mint(art, tmp_path / "w.json", "JRA_SOURCE", fetch=jwks_fetch(jwk(KEY)))


def test_source_attestation_prefers_witness_and_keeps_freeze_order(art, tmp_path, monkeypatch):
    import verify_source_attestation as A
    monkeypatch.setattr(A, "verify_payload", lambda _: {
        "valid": True, "github_repository": A.REPOSITORY, "github_sha": "a" * 40, "github_run_id": "77",
        "family": "JRA", "status": "PASS", "race_id": "JRA-TEST"})
    monkeypatch.setattr(A.time, "time", lambda: 1_800_000_010)
    real = W.verify
    monkeypatch.setattr(W, "verify", lambda *a, **k: real(*a, **k, fetch=jwks_fetch(jwk(KEY))))
    mint(art, tmp_path / A.WITNESS_NAME)
    out = A.verify(art)
    assert out["attestation_verification"] == "GITHUB_OIDC_WITNESS:GITHUB_LIVE_JWKS"
    # the witness time is still checked against the SOURCE freeze time
    monkeypatch.setattr(A, "verify_payload", lambda _: {
        "valid": True, "github_repository": A.REPOSITORY, "github_sha": "a" * 40, "github_run_id": "77",
        "family": "JRA", "status": "PASS", "race_id": "JRA-TEST"})
    art.write_text(json.dumps({"artifact": {"source_freeze_at": "2027-01-15T08:00:05+00:00"}}))
    mint(art, tmp_path / A.WITNESS_NAME)
    with pytest.raises(RuntimeError, match="SIGNED_BEFORE_SOURCE_FREEZE"):
        A.verify(art)
    (tmp_path / A.WITNESS_NAME).write_text("{}")
    with pytest.raises(RuntimeError, match="OIDC_WITNESS_INVALID"):
        A.verify(art)


def test_pedigree_corpus_accepts_witness_sidecars(art, tmp_path, monkeypatch):
    import jra_pedigree_corpus as C
    real = W.verify
    monkeypatch.setattr(W, "verify", lambda *a, **k: real(*a, **k, fetch=jwks_fetch(jwk(KEY))))
    assert C._oidc_witnessed(art, signer=None, not_after=None) is None
    mint(art, tmp_path / "source_oidc_witness.json")
    assert C._attested(art) is True
    assert C._attested(art, signer="km-jra-source-first-runner.yml") is True
    harvest = tmp_path / "batch.json"
    harvest.write_text("{}")
    W.mint(harvest, tmp_path / "batch.oidc_witness.json", "JRA_PEDIGREE_HARVEST",
           request_token=lambda a: token(claims(a, workflow_ref=f"{W.REPOSITORY}/.github/workflows/km-jra-pedigree-corpus-harvest.yml@{W.REF}")),
           fetch=jwks_fetch(jwk(KEY)))
    assert C._attested(harvest, signer="km-jra-pedigree-corpus-harvest.yml") is True
    assert C._attested(harvest, signer="km-jra-pedigree-verified-backfill.yml") is False
