#!/usr/bin/env python3
"""Replay real frozen SOURCE through the existing external LOCAL endpoints.

Never overwrites a Production execution. Uses a content-addressed checkpoint
directory, verifies receipts, and marks post-result execution as REPLAY/PAPER.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
import sys
import urllib.request
import base64
import hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from local_aki_columns import build, decision, verify, sha
from local_fullnumerical_production import materialize_production
from local_krs_technical_proxy_from_source import build as proxy
from local_krs_input_builder_production import build as krs_input
from krs_prediction_utility import build_krs_prediction_utility


def run(intent_path, source_path, out_root):
    req = json.loads(Path(intent_path).read_text())
    source = json.loads(Path(source_path).read_text())
    gateway = json.loads((ROOT / "profiles/current_execution_gateway.json").read_text())
    endpoint = gateway["families"]["LOCAL"]["external_endpoint"]
    digest = sha({"intent": req, "source_receipt": source["receipt_sha256"],
                  "implementation": Path(ROOT / "runtime/local_aki_columns.py").read_text(),
                  "policy": (ROOT / "profiles/local_aki_columns_20261012_R1.json").read_text()})
    out = Path(out_root).resolve() / req["race_id"] / digest[:16]
    out.mkdir(parents=True, exist_ok=True)
    if (out / "acceptance.json").exists():
        return json.loads((out / "acceptance.json").read_text())
    def save(name, obj):
        path = out / (name + ".json")
        text = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
        if path.exists() and path.read_text() != text:
            raise RuntimeError("IMMUTABLE_CHECKPOINT_CONFLICT:" + name)
        path.write_text(text)
        return obj
    def call(path, payload, name, timeout=60):
        checkpoint = out / (name + ".json")
        # Cache only signed responses; all dependency hashes enter out's key.
        if checkpoint.exists():
            return json.loads(checkpoint.read_text())
        data = json.dumps(payload, ensure_ascii=False).encode()
        request = urllib.request.Request(endpoint + path, data=data,
                                         headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return save(name, json.load(response))
    def signed(envelope, label, status):
        # Independently validate cached/raw artifacts as well as external /verify.
        attestation = json.loads((ROOT / "evidence/local_aki_columns_20261012/destination_verification.json").read_text())
        if attestation["status"] != "PASS" or attestation["endpoint"] != endpoint:
            raise RuntimeError("DESTINATION_ATTESTATION_MISMATCH")
        public = Ed25519PublicKey.from_public_bytes(base64.b64decode(attestation["health"]["receipt_public_key_b64"]))
        raw = json.dumps(envelope["receipt"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        public.verify(base64.b64decode(envelope["signature"]), raw)
        if (hashlib.sha256(raw).hexdigest() != envelope["receipt_sha256"]
                or sha(envelope["artifact"]) != envelope["receipt"]["artifact_sha256"]):
            raise RuntimeError("RECEIPT_OR_ARTIFACT_HASH_INVALID")
        result = call("/verify", envelope, label + "_verification")
        if result.get("valid") is not True or envelope["receipt"]["status"] != status:
            raise RuntimeError("SIGNED_RECEIPT_INVALID:" + label)
        if envelope["receipt"]["race_id"] != req["race_id"]:
            raise RuntimeError("SIGNED_RACE_ID_MISMATCH")
    signed(source, "source", "SOURCE_FROZEN")
    art = source["artifact"]
    req["source_snapshot_sha256"] = art["source_snapshot_sha256"]
    q = materialize_production(art, req, req["required_indices"])
    save("numerical_summary", q["production_numerical_summary"])
    # Save full, reconstructible 29-index provenance, not just aggregate scores.
    save("signed_source_input", source)
    save("numerical_runners", q["runners"])
    selected = save("selection", build(q, art))
    save("pre_krs_recomputation", verify(q, art, selected))
    # The enacted KRS proxy remains in force; numerical-to-KRS authority is
    # not granted by this PAPER experiment. Only candidate role labels change.
    q["local_krs_bridge"] = proxy(q, art)
    q = krs_input(q)
    inp = q["krs_input_data"]
    count = max(20000, int(req.get("run_count", 5000)))
    inp["simulation"]["run_count"] = count
    inp["simulation"]["master_seed"] = int(req.get("seed", 1))
    for h in inp["horses"]:
        rid = str(h["horse_no"])
        h["static_roles"] = [c for c, v in selected["columns"].items() if rid in v["selected"]]
    inp["aki_column_experiment"] = {"profile": selected["profile"], "selection_sha256": selected["sha256"],
                                    "production_authority": False, "temporal_mode": "REPLAY"}
    save("krs_input", inp)
    pre = call("/pre-krs", {"family_id": "LOCAL", "race_id": req["race_id"],
               "source_receipt": source, "required_index_unresolved": 0,
               "full_terminalization": q["full_terminalization"],
               "full_numerical_calculation": False, "krs_input_mode": "TECHNICAL_PROXY_DIAGNOSTIC",
               "static_prediction_frozen": True, "krs_input_data": inp}, "pre_krs_receipt")
    signed(pre, "pre_krs", "PASS")
    # High uncertainty acceptance uses SIM-HIGH; no invented local run counts.
    run_receipt = call("/krs/execute", {"family_id": "LOCAL", "race_id": req["race_id"],
                        "krs_input_data": inp, "run_count": count, "seed": int(req.get("seed", 1))},
                       "krs_receipt", 600)
    signed(run_receipt, "krs", "EXECUTED")
    if run_receipt["artifact"]["actual_run_count"] < count:
        raise RuntimeError("KRS_RUN_SHORT")
    if run_receipt["artifact"]["input_sha256"] != sha(inp):
        raise RuntimeError("KRS_INPUT_BINDING_MISMATCH")
    utility = save("krs_utility", build_krs_prediction_utility(q, {"status": "EXECUTED",
                           "output": run_receipt["artifact"]["raw_output"]}))
    d = save("decision", decision(q, selected, utility))
    save("post_ticket_recomputation", verify(q, art, selected))
    fpp = {"profile": selected["profile"], "temporal_mode": "REPLAY", "production_authority": False,
           "purchase_authority": False, "validation_status": "UNVALIDATED_RULE_BASED",
           "aki_selection": selected, "paper_tickets": d["paper_tickets"],
           "krs_utility": utility, "source_snapshot_sha256": art["source_snapshot_sha256"]}
    trace = {"fpp_sha256": sha(fpp), "mec_sha256": d["mec"]["sha256"],
             "candidate_count": d["mec"]["ticket_count"], "selected_count": 0,
             "capital_decision_sha256": d["capital"]["sha256"],
             "aki_columns_sha256": selected["sha256"], "temporal_mode": "REPLAY",
             "purchase_authority": False, "execution_id": "LOCAL-AKI-REPLAY-" + digest[:16]}
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    stages = [{"stage": x, "timestamp": now, "temporal_mode": "REPLAY"} for x in
              ("SOURCE_FREEZE", "RUNNER_UNIVERSE", "NUMERICAL_MATERIALIZATION", "INDEX_PROVENANCE",
               "STATIC_FREEZE", "PRE_KRS", "KRS", "KRS_UTILITY", "MEC", "CAPITAL", "FINAL_TICKET_FREEZE")]
    payload = save("final_payload", {"family_id": "LOCAL", "race_id": req["race_id"],
               "source_receipt": source, "krs_run_receipt": run_receipt, "final_prediction_package": fpp,
               "final_ticket": {"finalized": True, "no_bet": True, "total_investment": 0,
                                "tickets": [], "frozen_at": now},
               "minimum_efficient_coverage": d["mec"], "capital_policy_decision": d["capital"],
               "ticket_transport_trace": trace, "execution_stage_manifest": stages, "final_freeze_timestamp": now})
    final = call("/final", payload, "final_receipt", 180)
    signed(final, "final", "PASS")
    final_art = final["artifact"]
    if (final_art["ticket_transport_trace"] != trace or final_art["final_prediction_package"] != fpp
            or final_art["minimum_efficient_coverage"]["sha256"] != d["mec"]["sha256"]):
        raise RuntimeError("SIGNED_FINAL_ROUNDTRIP_MISMATCH")
    return save("acceptance", {"status": "EXTERNAL_REPLAY_PAPER_PASS", "execution_id": trace["execution_id"],
               "actual_run_count": run_receipt["artifact"]["actual_run_count"], "race_id": req["race_id"],
               "final_receipt_sha256": final["receipt_sha256"], "selection_sha256": selected["sha256"],
               "paper_ticket_count": d["mec"]["ticket_count"], "capital_decision": d["capital"]["decision"],
               "purchase_authority": False, "unknown_future_oos_count": 0, "path": str(out.relative_to(ROOT))})


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--intent", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--out", default="evidence/local_aki_columns_20261012/external")
    a = p.parse_args()
    print(json.dumps(run(a.intent, a.source, a.out), ensure_ascii=False))
