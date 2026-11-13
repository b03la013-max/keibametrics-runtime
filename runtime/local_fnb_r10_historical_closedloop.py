"""Independent historical FNB SOURCE→FINAL→RESULT settlement witness.

Uses immutable repository check-points and a publicly archived LOCAL gateway
Ed25519 public key. A PASS verifies stored signatures and frozen 100-yen
recommendation settlement, NOT current remote trust, 2026-11-02 LIVE, a
personal delivery ACK, an actual purchase or forward OOS registration.
"""
from __future__ import annotations

import base64
from collections import Counter
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path

from runtime import formal_execution_orchestrator as o

EID = "LOCAL-KM-LOCAL-FNB-20261001-R06-LIVE-R1-EXEC"
RACE_ID = "KM-LOCAL-FNB-20261001-R06-LIVE-R1"
PROFILE = "KM-FNB-R10-HISTORICAL-SIGNED-SETTLEMENT-WITNESS-v1"
TRUST_FILE = "evidence/family_audit_20261016/runtime_health.json"


def _canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha(value) -> str:
    return sha256(_canonical(value)).hexdigest()


def _time(value):
    result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("R10_SIGNED_TIMESTAMP_TIMEZONE_REQUIRED")
    return result


def _assert_envelope(envelope, *, expected_phase, expected_status,
                     public_key, profile):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    receipt, artifact = envelope["receipt"], envelope["artifact"]
    if (receipt.get("family") != "LOCAL" or receipt.get("phase") != expected_phase
            or receipt.get("race_id") != RACE_ID
            or receipt.get("status") != expected_status or receipt.get("errors")
            or envelope.get("signer_key_id") != profile["receipt_signer_key_id"]
            or envelope.get("signature_alg") != "Ed25519"
            or receipt.get("engine_sha256") != profile["engine_sha256"]
            or receipt.get("parameter_map_sha256") != profile["parameter_map_sha256"]
            or _sha(receipt) != envelope.get("receipt_sha256")
            or _sha(artifact) != receipt.get("artifact_sha256")):
        raise ValueError("R10_SIGNED_ENVELOPE_ID_OR_HASH_MISMATCH:" + expected_phase)
    Ed25519PublicKey.from_public_bytes(public_key).verify(
        base64.b64decode(envelope["signature"], validate=True), _canonical(receipt))
    return receipt, artifact


def _audit_tickets(tickets, official_result):
    order=tuple(int(x) for x in official_result["finish_order"])
    if len(order)!=3 or len(set(order))!=3:
        raise ValueError("R10_FINISH_ORDER_INVALID")
    payouts=official_result["payouts"]
    allowed={"EXACTA":2,"TRIO":3,"TRIFECTA":3}
    if set(payouts)!=set(allowed):
        raise ValueError("R10_OFFICIAL_RESULT_PAYOUT_SET_INVALID")
    per_bet=Counter()
    winners=Counter()
    keys=set()
    gross=0
    for ticket in tickets:
        kind=str(ticket["bet_type"]).upper()
        selection=tuple(int(x) for x in ticket["selection"])
        stake=ticket["stake"]
        if (kind not in allowed or len(selection)!=allowed[kind]
                or len(set(selection))!=len(selection)
                or type(stake) is not int or stake<=0 or stake%100):
            raise ValueError("R10_FROZEN_TICKET_CELL_INVALID")
        canonical=(kind, tuple(sorted(selection)) if kind=="TRIO" else selection)
        if canonical in keys:
            raise ValueError("R10_DUPLICATE_FROZEN_TICKET")
        keys.add(canonical)
        per_bet[kind]+=stake
        target=tuple(sorted(order)) if kind=="TRIO" else order[:allowed[kind]]
        hit=(canonical[1]==target)
        if hit:
            winners[kind]+=1
            gross+=(stake//100)*int(payouts[kind])
    return {"stake_per_type":dict(per_bet), "hit_count_per_type":dict(winners),
            "total_tickets":len(tickets), "total_stake":sum(per_bet.values()),
            "total_payout":gross, "win_order":list(order)}


def inspect_historical(root: Path|str|None=None):
    root=Path(root) if root is not None else Path(__file__).resolve().parents[1]
    phase={p:o.resolve_phase(EID,p) for p in ("SOURCE","FORMAL","RESULT")}
    if any(not phase[p] for p in phase):
        raise ValueError("R10_HISTORICAL_SIGNED_PHASE_NOT_OBSERVED")
    envelopes={p:o._load_checkpoint_json(
        phase[p], "source_receipt_envelope.json" if p=="SOURCE" else
        "final_receipt_envelope.json" if p=="FORMAL" else
        "result_receipt_envelope.json") for p in phase}
    health=json.loads((root/TRUST_FILE).read_text(encoding="utf-8"))
    gateway=json.loads((root/"profiles/current_execution_gateway.json").read_text(
        encoding="utf-8"))["families"]["LOCAL"]
    public=base64.b64decode(health["receipt_public_key_b64"],validate=True)
    if (health.get("receipt_signer_key_id") != gateway["receipt_signer_key_id"]
            or health.get("engine_sha256") != gateway["engine_sha256"]
            or health.get("parameter_map_sha256") != gateway["parameter_map_sha256"]):
        raise ValueError("R10_ARCHIVED_GATEWAY_TRUST_MISMATCH")
    receipts={}
    artifacts={}
    for phase_name, status in (("SOURCE","SOURCE_FROZEN"),("FORMAL","PASS"),("RESULT","PASS")):
        receipts[phase_name],artifacts[phase_name]=_assert_envelope(
            envelopes[phase_name],expected_phase="FINAL" if phase_name=="FORMAL" else phase_name,
            expected_status=status,public_key=public,profile=gateway)
    src,final,result=artifacts["SOURCE"],artifacts["FORMAL"],artifacts["RESULT"]
    if (src.get("source_race_context") or {}).get("venue_id")!="FNB":
        raise ValueError("R10_SOURCE_NOT_FNB")
    refs=result["frozen_refs"]
    if (refs.get("final_receipt_sha256") != envelopes["FORMAL"]["receipt_sha256"]
            or refs.get("final_ticket_sha256") != final["ticket_sha256"]
            or refs.get("final_freeze_timestamp") != final["final_freeze_timestamp"]
            or final.get("source_receipt_sha256") != envelopes["SOURCE"]["receipt_sha256"]):
        raise ValueError("R10_FROZEN_SOURCE_FINAL_RESULT_LINEAGE_MISMATCH")
    src_freeze=_time(src["source_freeze_at"])
    final_freeze=_time(final["final_freeze_timestamp"])
    receipt_final=_time(receipts["FORMAL"]["timestamp"])
    cutoff=_time(src["prediction_cutoff"])
    observed_result=_time(result["result_available_at"])
    signed_result=_time(receipts["RESULT"]["timestamp"])
    if not src_freeze<=final_freeze<=receipt_final<cutoff<observed_result<=signed_result:
        raise ValueError("R10_TEMPORAL_RESULT_HINDSIGHT_OR_FREEZE_INVALID")
    ticket=final["final_ticket"]
    if ticket.get("no_bet") is not False:
        raise ValueError("R10_HISTORIC_FROZEN_TICKET_NOT_A_VALID_SELECTED_PORTFOLIO")
    independent=_audit_tickets(ticket["tickets"],result["official_result"])
    settled=result["settlement"]
    if (independent["total_stake"]!=ticket["total_investment"]
            or independent["total_stake"]!=settled["investment"]
            or independent["total_payout"]!=settled["return"]
            or settled["profit_loss"]!=settled["return"]-settled["investment"]
            or settled["status"]!="COMPLETE"
            or settled["pfs_authority"]!="FROZEN-RECOMMENDATION"
            or abs(float(settled["pfs"]) - 100*settled["return"]/settled["investment"])>1e-5):
        raise ValueError("R10_SIGNED_SETTLEMENT_DOES_NOT_MATCH_FROZEN_TICKETS")
    learning=result.get("automatic_next_race_learning_state") or {}
    if (learning.get("race_id")!="KM-LOCAL-FNB-20261001-R06-LIVE-R1"
            or learning.get("production_change_authorized") is not False):
        raise ValueError("R10_FROZEN_NEXT_RACE_LEARNING_AUTHORITY_INVALID")
    return {
        "profile":PROFILE,
        "status":"RETROSPECTIVE_R06_CRYPTO_AND_FROZEN_SETTLEMENT_VERIFIED",
        "classification":"HISTORICAL_2026-10-01_FNB_R06_NOT_LIVE_2026-11-02",
        "race_id":learning["race_id"],"execution_id":EID,
        "source_receipt_sha256":envelopes["SOURCE"]["receipt_sha256"],
        "final_receipt_sha256":envelopes["FORMAL"]["receipt_sha256"],
        "result_receipt_sha256":envelopes["RESULT"]["receipt_sha256"],
        "archived_gateway_trust_basis":TRUST_FILE,
        "archived_health_key_fingerprint":sha256(public).hexdigest(),
        "all_three_stored_ed25519_signatures_verified_with_archived_key":True,
        "fresh_online_gateway_health_verified":False,
        "official_result_provider_issuer_independently_queried":False,
        "result_official_claim_from_signed_receipt":result["official_result"].get("source"),
        "ticket_audit":independent,
        "settled_pfs_percent":round(100*settled["return"]/settled["investment"],6),
        "settled_profit_loss":settled["profit_loss"],
        "next_race_learning_state_frozen":True,
        "next_race_actually_consumed_learning_verified":False,
        "actual_purchase_verified":False,
        "recipient_delivery_ack_verified":False,
        "new_2026_11_02_formal_prediction":False,
        "registered_forward_oos_increment":0,
        "production_changed":False
    }
