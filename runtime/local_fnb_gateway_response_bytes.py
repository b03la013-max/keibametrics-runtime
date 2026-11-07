"""Preserve transport bytes before parsing; audit signatures, never admit SOURCE.

Capture provenance is caller supplied. DOM/forensic text is never relabelled as
original HTTP. A verified FAIL remains FAIL. No network, signer or model exists
here; a caller must still pass existing SOURCE/Owner/admission checks.
"""
from __future__ import annotations
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode()


def _preserve(root, name, data):
    root = Path(root).absolute()
    relative = Path(name)
    if relative.is_absolute() or not relative.parts or any(p in (".", "..") for p in relative.parts):
        raise ValueError("GATEWAY_RESPONSE_PRIVATE_PATH_INVALID")
    target = root / relative
    if any(p.is_symlink() or (p / ".git").exists() for p in (target, *target.parents)):
        raise ValueError("GATEWAY_RESPONSE_PRIVATE_STORE_REQUIRED")
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.chmod(temporary, 0o600)
        try:
            os.link(temporary, target)
        except FileExistsError:
            if target.is_symlink() or target.read_bytes() != data:
                raise ValueError("GATEWAY_RESPONSE_IMMUTABLE_BYTES_CONFLICT")
    finally:
        temporary.unlink(missing_ok=True)
    if target.read_bytes() != data:
        raise ValueError("GATEWAY_RESPONSE_PRIVATE_READBACK_FAILED")
    return {"path": str(target), "sha256": _sha(data), "bytes": len(data)}


def save_response_bytes(raw, *, private_root, name, metadata, trust_path,
                        trust_sha256, expected_race_id):
    """Save untouched bytes first; returned path/SHA is for independent consumers."""
    kinds = {"ORIGINAL_HTTP_RESPONSE_BODY", "DOM_TEXT_RECONSTRUCTION",
             "FORENSIC_RECONSTRUCTION", "TEST_SYNTHETIC_BYTES"}
    if type(raw) is not bytes or not raw or not isinstance(metadata, dict):
        raise ValueError("GATEWAY_RESPONSE_EXPLICIT_BYTES_AND_METADATA_REQUIRED")
    if metadata.get("capture_kind") not in kinds:
        raise ValueError("GATEWAY_RESPONSE_CAPTURE_PROVENANCE_REQUIRED")
    saved = _preserve(private_root, name, raw)  # Before JSON parse/normalization.
    capture = {**metadata, "source_admitted": False, "original_http_transport_proven_here": False}
    _preserve(private_root, name + ".capture.json", _canonical(capture) + b"\n")
    trust_bytes = Path(trust_path).read_bytes()
    if _sha(trust_bytes) != trust_sha256:
        raise ValueError("GATEWAY_RESPONSE_PINNED_TRUST_BYTES_MISMATCH")
    trust, envelope = json.loads(trust_bytes), json.loads(raw)
    receipt, artifact = envelope["receipt"], envelope["artifact"]
    if _sha(_canonical(receipt)) != envelope.get("receipt_sha256"):
        raise ValueError("GATEWAY_RESPONSE_RECEIPT_SHA_MISMATCH")
    if (envelope.get("signature_alg") != "Ed25519"
            or envelope.get("signer_key_id") != trust["receipt_signer_key_id"]):
        raise ValueError("GATEWAY_RESPONSE_SIGNER_OR_ALGORITHM_MISMATCH")
    Ed25519PublicKey.from_public_bytes(base64.b64decode(
        trust["receipt_public_key_b64"], validate=True)).verify(
        base64.b64decode(envelope["signature"], validate=True), _canonical(receipt))
    if _sha(_canonical(artifact)) != receipt.get("artifact_sha256"):
        raise ValueError("GATEWAY_RESPONSE_ARTIFACT_SHA_MISMATCH")
    if (receipt.get("race_id") != expected_race_id or artifact.get("race_id") != expected_race_id
            or receipt.get("family") != "LOCAL" or receipt.get("phase") != "SOURCE"
            or any(receipt.get(k) != trust[k] for k in ("engine_sha256", "parameter_map_sha256"))):
        raise ValueError("GATEWAY_RESPONSE_RACE_OR_RUNTIME_IDENTITY_MISMATCH")
    return {**saved, "capture_metadata": dict(metadata),
            "original_http_body_attested_by_caller": metadata["capture_kind"] == "ORIGINAL_HTTP_RESPONSE_BODY",
            "original_http_transport_proven_here": False, "signed_receipt_verified": True,
            "receipt_status": receipt["status"], "receipt_errors": receipt.get("errors"),
            "source_admitted": False, "owner_or_ticket_authority_granted": False}
