#!/usr/bin/env python3
"""Enumerate all LOCAL execution attempts, preserve failures, dedupe race IDs.

Retrospective policy evaluation only. Missing records never become successes.
"""
import json
from pathlib import Path
from collections import Counter, defaultdict
import datetime as dt
from copy import deepcopy
import base64
import hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from local_aki_columns import build, decision, sha, LocalAKIError
from local_fullnumerical_production import materialize_production
from mec_r4_shadow import settle_ticket_list


def load(p):
    return json.loads(p.read_text()) if p.exists() else None


def audit():
    attestation = load(ROOT / "evidence/local_aki_columns_20261012/destination_verification.json")
    key = Ed25519PublicKey.from_public_bytes(base64.b64decode(attestation["health"]["receipt_public_key_b64"]))
    intents = {}
    for root in ("runtime/formal_intents", "runtime/family_requests"):
        for p in (ROOT / root).glob("*.json"):
            q = load(p)
            if q.get("family_id") == "LOCAL":
                intents.setdefault(q.get("race_id"), []).append((p, q))
    attempts = []
    grouped = defaultdict(list)
    for p in sorted((ROOT / "runtime/executions").glob("*/FORMAL/runs/*")):
        files = {f.name for f in p.glob("*.json")}
        if not files:
            continue
        context = load(p / "execution_context.json") or {}
        source = load(p / "source_receipt_envelope.json") or {}
        final = load(p / "final_receipt_envelope.json") or {}
        receipt = final.get("receipt") or source.get("receipt") or {}
        rid = receipt.get("race_id") or context.get("execution_id") or p.parents[2].name
        if receipt.get("family", context.get("family_id")) != "LOCAL" and "LOCAL" not in str(rid):
            continue
        fail = load(p / "fail_closed.json") or load(p / "failure.json") or {}
        record = {"race_id": rid, "path": str(p.relative_to(ROOT)),
                  "final_status": final.get("receipt", {}).get("status", "MISSING"),
                  "source": bool(source), "source_receipt_sha256": source.get("receipt_sha256"),
                  "static": "static_prediction_freeze.json" in files,
                  "provenance": "index_provenance_manifest.json" in files,
                  "krs": "krs_receipt_envelope.json" in files,
                  "mec": "mec_plan.json" in files, "capital": "capital_decision.json" in files,
                  "failure": fail, "files": sorted(files),
                  "signed_at": receipt.get("timestamp", "")}
        attempts.append(record)
        grouped[rid].append(record)
    races = []
    for rid in sorted(set(grouped) | set(intents)):
        records = grouped[rid]
        # Deterministic latest attempt, irrespective of its success status.
        latest = max(records, key=lambda r: (r["signed_at"], r["path"])) if records else None
        row = {"race_id": rid, "attempt_count": len(records), "attempt_paths": [r["path"] for r in records],
               "latest": latest, "replay_status": "NOT_ELIGIBLE", "replay_oos_count": 0,
               "missing": [], "actual_purchase": "UNCONFIRMED"}
        if intents.get(rid):
            identity_req = intents[rid][-1][1]
            race = identity_req.get("race") or {}
            row["identity"] = [identity_req.get("venue_id") or race.get("venue_id"),
                               identity_req.get("race_date") or race.get("race_date"),
                               identity_req.get("race_no") or race.get("race_no")]
            row["acceptance_only"] = bool(identity_req.get("acceptance_only"))
        if not latest:
            row["missing"].append("FORMAL_ATTEMPT")
            races.append(row)
            continue
        folder = ROOT / latest["path"]
        for k in ("source", "static", "provenance", "krs", "mec", "capital"):
            if not latest[k]: row["missing"].append(k.upper())
        if latest["final_status"] != "PASS": row["missing"].append("SIGNED_FINAL_PASS")
        source = load(folder / "source_receipt_envelope.json")
        result_files = sorted((folder.parents[2] / "RESULT").rglob("result_receipt_envelope.json"))
        result = load(result_files[-1]) if result_files else None
        row["result_path"] = str(result_files[-1].relative_to(ROOT)) if result_files else None
        if not result: row["missing"].append("OFFICIAL_RESULT_SETTLEMENT_LEARNING")
        intent_candidates = intents.get(rid, [])
        if not intent_candidates or not source:
            row["missing"].append("RECONSTRUCTIBLE_INTENT_AND_SOURCE")
            races.append(row)
            continue
        # Source must identify this exact race and have been frozen pre-start.
        ip, req = intent_candidates[-1]
        row["intent_path"] = str(ip.relative_to(ROOT))
        row["venue"] = req.get("venue_id")
        row["race_date"] = req.get("race_date")
        row["class"] = req.get("race", {}).get("class")
        row["distance"] = req.get("race", {}).get("distance")
        art = source["artifact"]
        try:
            if source["receipt"]["race_id"] != rid: raise LocalAKIError("SOURCE_RACE_MISMATCH")
            if sha(art) != source["receipt"]["artifact_sha256"]: raise LocalAKIError("SOURCE_ARTIFACT_HASH_INVALID")
            receipt_bytes = json.dumps(source["receipt"],ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
            if hashlib.sha256(receipt_bytes).hexdigest() != source["receipt_sha256"]:
                raise LocalAKIError("SOURCE_RECEIPT_HASH_INVALID")
            key.verify(base64.b64decode(source["signature"]),receipt_bytes)
            row["source_signature_verified"] = True
            parse = lambda v: dt.datetime.fromisoformat(v.replace("Z", "+00:00"))
            if parse(art["source_freeze_at"]) >= parse(req["scheduled_post_at"]):
                raise LocalAKIError("SOURCE_NOT_PRE_START")
            req["source_snapshot_sha256"] = art["source_snapshot_sha256"]
            q = materialize_production(art, req, req["required_indices"])
            x = build(q, art)
            d = decision(q, x)
            row.update(replay_status=x["status"], runner_count=len(q["runners"]),
                       columns=x["columns"], diagnostics=x["column_diagnostics"],
                       terminal_reasons=x["terminal_reasons"], selection_sha256=x["sha256"],
                       numerical_coverage=q["numeric_coverage"],
                       candidate_counts=dict(Counter(t["bet_type"] for t in d["paper_tickets"])),
                       candidate_ticket_count=d["mec"]["ticket_count"],
                       candidate_investment=d["mec"]["minimum_required_capital"],
                       candidate_capital=d["capital"]["decision"])
            row["paper_tickets"] = d["paper_tickets"]
            prod = load(folder / "canonical_ticket.json") or {}
            row["production_counts"] = dict(Counter(t["bet_type"] for t in prod.get("tickets", [])))
            row["production_investment"] = prod.get("total_investment")
            if result and result["receipt"]["status"] == "PASS":
                official = result["artifact"]["official_result"]
                row["official_finish"] = official["finish_order"]
                row["capture"] = {c: str(official["finish_order"][i]) in x["columns"][c]["selected"]
                                  for i, c in enumerate(("W", "P2", "P3"))}
                normalized_result = deepcopy(result["artifact"])
                normalized_result["official_result"]["top3"] = official["finish_order"][:3]
                row["candidate_settlement"] = settle_ticket_list(d["paper_tickets"], normalized_result)
                row["production_settlement"] = settle_ticket_list(prod.get("tickets", []), normalized_result)
                row["original_learning_available"] = bool(result["artifact"].get("learning_event"))
                row["comparison_scope"] = "SAME_SOURCE_RETROSPECTIVE_REPLAY_NOT_OOS"
        except (ValueError, KeyError, TypeError) as exc:
            row.update(replay_status="HOLD", exclusion_reason=type(exc).__name__ + ":" + str(exc))
        races.append(row)
    identities = defaultdict(list)
    for r in races:
        identity = r.get("identity")
        if identity and all(v is not None for v in identity):
            identities[tuple(identity)].append(r["race_id"])
    summary = {"status": "RETROSPECTIVE_REPLAY_ONLY", "attempt_count": len(attempts),
               "race_id_count": len(races), "duplicate_attempt_count": sum(max(0, r["attempt_count"] - 1) for r in races),
               "identified_race_count":len(identities),
               "race_identity_aliases":[{"identity":list(k),"execution_ids":v} for k,v in identities.items() if len(v)>1],
               "unidentified_execution_id_count":sum(not r.get("identity") or not all(v is not None for v in r["identity"]) for r in races),
               "replay_statuses": dict(Counter(r["replay_status"] for r in races)),
               "missing_counts": dict(Counter(k for r in races for k in r["missing"])),
               "unknown_future_oos_count": 0, "actual_purchase_performance": "UNAVAILABLE"}
    return {"summary": summary, "attempts": attempts, "races": races}


if __name__ == "__main__":
    result = audit()
    out = ROOT / "research/local_aki_columns_20261012"
    out.mkdir(parents=True, exist_ok=True)
    (out / "corpus_audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result["summary"], ensure_ascii=False))
