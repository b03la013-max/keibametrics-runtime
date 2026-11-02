"""R12: real archived FNB KRS PRE_KRS→KRS_RUN→FINAL signed lineage.

An independent, read-only cryptographic witness against historical 2026-10-02
4R store. The recorded seed is NOT 1; candidate V01/V02/V03 are separate
SHADOW studies, not the user's approved Baseline/Candidate owner pair.
No OOS, current race-day KRS, licensed acquisition or purchased ticket claim.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
from datetime import datetime

from runtime import formal_execution_orchestrator as o

EID="LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"
RID="KM-LOCAL-FNB-20261002-R04-LIVE-R1"
KEY_PATH="evidence/family_audit_20261016/runtime_health.json"
PROFILE="KM-FNB-R12-ARCHIVED-CRYPTO-KRS-TO-FINAL-v1"


def _sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,
        separators=(",",":"),allow_nan=False).encode()).hexdigest()


def verify_envelope(envelope, *, race_id, phase, status, public, cfg):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    receipt=envelope["receipt"]
    artifact=envelope["artifact"]
    if (receipt.get("family")!="LOCAL" or receipt.get("phase")!=phase
            or receipt.get("race_id")!=race_id or
            receipt.get("status")!=status or receipt.get("errors")
            or receipt.get("engine_sha256")!=cfg["engine_sha256"]
            or receipt.get("parameter_map_sha256")!=cfg["parameter_map_sha256"]
            or envelope.get("signature_alg")!="Ed25519"
            or envelope.get("signer_key_id")!=cfg["receipt_signer_key_id"]
            or envelope.get("receipt_sha256")!=_sha(receipt)
            or receipt.get("artifact_sha256")!=_sha(artifact)):
        raise ValueError("R12_SIGNED_KRS_PHASE_IDENTITY_OR_SHA_INVALID:"+phase)
    Ed25519PublicKey.from_public_bytes(public).verify(
        base64.b64decode(envelope["signature"],validate=True),
        json.dumps(receipt,sort_keys=True,ensure_ascii=False,
                   separators=(",",":"),allow_nan=False).encode())
    return artifact


def attest_archived_krs(root:Path|None=None):
    root=Path(root) if root is not None else Path(__file__).resolve().parents[1]
    formal=o.resolve_phase(EID,"FORMAL")
    source=o.resolve_phase(EID,"SOURCE")
    if formal is None or source is None:
        raise ValueError("R12_KRS_FROZEN_SIGNED_PHASE_MISSING")
    src=o._load_checkpoint_json(source,"source_receipt_envelope.json")
    pre=o._load_checkpoint_json(formal,"pre_krs_receipt_envelope.json")
    executed=o._load_checkpoint_json(formal,"krs_receipt_envelope.json")
    final=o._load_checkpoint_json(formal,"final_receipt_envelope.json")
    frozen=o._load_checkpoint_json(formal,"static_prediction_freeze.json")
    trust=json.loads((root/KEY_PATH).read_text())
    gateway=json.loads((root/"profiles/current_execution_gateway.json").read_text())["families"]["LOCAL"]
    if (trust["receipt_signer_key_id"]!=gateway["receipt_signer_key_id"]
            or trust["engine_sha256"]!=gateway["engine_sha256"]
            or trust["parameter_map_sha256"]!=gateway["parameter_map_sha256"]):
        raise ValueError("R12_KRS_ARCHIVED_TRUST_BUNDLE_NOT_CANONICAL")
    public=base64.b64decode(trust["receipt_public_key_b64"],validate=True)
    raw=verify_envelope(src,race_id=RID,phase="SOURCE",
                        status="SOURCE_FROZEN",public=public,cfg=gateway)
    a=verify_envelope(pre,race_id=RID,phase="PRE_KRS",
                      status="PASS",public=public,cfg=gateway)
    b=verify_envelope(executed,race_id=RID,phase="KRS_RUN",
                      status="EXECUTED",public=public,cfg=gateway)
    c=verify_envelope(final,race_id=RID,phase="FINAL",
                      status="PASS",public=public,cfg=gateway)
    if (a.get("source_receipt_sha256")!=src["receipt_sha256"]
            or a.get("input_sha256")!=b.get("input_sha256")
            or c.get("krs_receipt_sha256")!=executed["receipt_sha256"]
            or c.get("source_receipt_sha256")!=src["receipt_sha256"]
            or frozen.get("source_receipt_sha256")!=src["receipt_sha256"]
            or frozen.get("race_id")!=RID or frozen.get("execution_id")!=EID):
        raise ValueError("R12_KRS_CHAIN_INTEGRITY_INVALID")
    freeze=datetime.fromisoformat(str(c["final_freeze_timestamp"]))
    cutoff=datetime.fromisoformat(str(raw["prediction_cutoff"]))
    completed=datetime.fromisoformat(str(b["completed_at"]))
    if (freeze.tzinfo is None or cutoff.tzinfo is None
            or completed.tzinfo is None or
            not completed<=freeze<cutoff):
        raise ValueError("R12_KRS_NOT_COMPLETED_BEFORE_FROZEN_CUTOFF")
    if (b.get("requested_run_count")!=5000 or
            b.get("actual_run_count")!=5000 or
            b.get("calibration_status")!="PROVISIONAL_UNCALIBRATED"
            or not isinstance(b.get("seed"),int)):
        raise ValueError("R12_KRS_COUNT_OR_SEED_EVIDENCE_INVALID")
    return {"profile":PROFILE,
            "status":"ARCHIVED_FNB_R04_KRS_SIGNED_LINEAGE_VERIFIED",
            "race_id":RID,"execution_id":EID,
            "signed_phase_envelopes_verified":["SOURCE","PRE_KRS","KRS_RUN","FINAL"],
            "pre_krs_receipt_sha256":pre["receipt_sha256"],
            "krs_receipt_sha256":executed["receipt_sha256"],
            "final_receipt_sha256":final["receipt_sha256"],
            "actual_run_count":b["actual_run_count"],
            "requested_run_count":b["requested_run_count"],
            "actual_seed":b["seed"],
            "seed_is_one":b["seed"]==1,
            "uncalibrated_simulation_occurrences_not_probabilities":True,
            "independent_baseline_and_candidate_fixed_owner_receipts_proven":False,
            "new_20261102_krs_executed":False,
            "active_runner_current_day_evidence_proven":False,
            "automatic_ticket_authority_granted":False,
            "actual_user_bet":False,
            "new_production_scope_granted":False,
            "current_gateway_live_signature_verified_here":False}
