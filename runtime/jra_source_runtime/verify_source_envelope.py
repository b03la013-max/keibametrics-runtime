from __future__ import annotations
import base64,hashlib,json,pathlib,sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def _jdump(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")

def sha_obj(x):
    return hashlib.sha256(_jdump(x)).hexdigest()

def verify(path):
    p=pathlib.Path(path)
    env=json.loads(p.read_text(encoding="utf-8"))
    rec=env.get("receipt") or {}
    art=env.get("artifact") or {}
    pub_b64=str(env.get("receipt_public_key_b64") or "")
    sig_b64=str(env.get("signature") or "")
    if not pub_b64: raise ValueError("SOURCE_RECEIPT_PUBLIC_KEY_MISSING")
    if not sig_b64: raise ValueError("SOURCE_RECEIPT_SIGNATURE_MISSING")
    rb=_jdump(rec)
    if hashlib.sha256(rb).hexdigest()!=str(env.get("receipt_sha256") or ""):
        raise ValueError("SOURCE_RECEIPT_SHA_MISMATCH")
    if sha_obj(art)!=str(rec.get("artifact_sha256") or ""):
        raise ValueError("SOURCE_ARTIFACT_SHA_MISMATCH")
    Ed25519PublicKey.from_public_bytes(base64.b64decode(pub_b64)).verify(base64.b64decode(sig_b64),rb)
    trust=str(env.get("signer_trust_class") or "")
    if trust!="GITHUB_ACTIONS_EPHEMERAL_ED25519_PLUS_GITHUB_OIDC_ATTESTATION":
        raise ValueError("SOURCE_TRUST_CLASS_INVALID:"+trust)
    out={
      "valid":True,
      "receipt_sha256":env.get("receipt_sha256"),
      "artifact_sha256":rec.get("artifact_sha256"),
      "race_id":rec.get("race_id"),
      "family":rec.get("family"),
      "status":rec.get("status"),
      "github_repository":env.get("github_repository"),
      "github_sha":env.get("github_sha"),
      "github_run_id":env.get("github_run_id"),
      "signer_trust_class":trust,
    }
    return out

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: verify_source_envelope.py <envelope.json>")
    print(json.dumps(verify(sys.argv[1]),ensure_ascii=False,sort_keys=True))
