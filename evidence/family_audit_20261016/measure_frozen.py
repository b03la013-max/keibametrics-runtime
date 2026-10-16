"""One-off read-only audit; not a runtime entry point, policy or validator.

Uses existing checkpoint, settlement, OOS and loss-owner implementations.
Writes derived evidence only in this directory. Never signs or submits a race.
"""
import base64
import collections
import datetime as dt
import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from execution_store import resolve_phase
from aki_adaptive_oos_tracker import scan_execution_store
from mec_r4_shadow import settle_ticket_list
from family_pfs_improvement import classify_dominant_pfs_loss_owner
from aki_adaptive_purchase_shadow import verify_signed_final_binding

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
STORE = ROOT / "runtime/executions"
# Observed from the existing canonical LOCAL runtime /health, 2026-10-16.
# This is the public trust anchor, never an envelope-supplied replacement key.
KEY = Ed25519PublicKey.from_public_bytes(base64.b64decode(
    "jqWqOYlmhXXmpv/nR7lx3c2n/S5shDYava/WJVxn4kE="))
SIGNER = "KM-LOCAL-RUNTIME-ED25519-20260922"

def read(p):
    return json.loads(p.read_text())

def canon(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()

def verify(e, race):
    r = e["receipt"]
    assert r["race_id"] == race, "RACE_IDENTITY_MISMATCH"
    expected = {"SOURCE": "SOURCE_FROZEN", "PRE_KRS": "PASS", "KRS_RUN": "EXECUTED", "FINAL": "PASS", "RESULT": "PASS"}
    assert r["status"] == expected[r["phase"]], "PHASE_STATUS_MISMATCH"
    assert e["signer_key_id"] == SIGNER and e["signature_alg"] == "Ed25519"
    assert hashlib.sha256(canon(e["artifact"])).hexdigest() == r["artifact_sha256"]
    assert hashlib.sha256(canon(r)).hexdigest() == e["receipt_sha256"]
    KEY.verify(base64.b64decode(e["signature"]), canon(r))
    return {"phase": r["phase"], "timestamp": r["timestamp"],
            "receipt_sha256": e["receipt_sha256"],
            "artifact_sha256": r["artifact_sha256"], "verified": True}

def drawdown(rows, arm):
    equity = peak = worst = 0
    for row in sorted(rows, key=lambda r: (r["race_day"], r["race_id"])):
        equity += row[arm]["profit_loss"]
        peak = max(peak, equity)
        worst = max(worst, peak - equity)
    return worst

def main():
    rows, errors = [], []
    for execution in sorted(STORE.glob("KM-LOCAL-KAW-2026101[345]-*")):
        row = {"execution_id": execution.name, "phases": {}, "receipts": [],
               "actual_purchase_pfs": "UNKNOWN", "user_delivery": "UNPROVEN"}
        rows.append(row)
        try:
            phases = {}
            for phase in ("SOURCE", "FORMAL", "OFFICIAL_RESULT", "RESULT"):
                p = resolve_phase(execution.name, phase, root=STORE)
                if not p:
                    continue
                phases[phase] = p
                row["phases"][phase] = {k: p["manifest"][k] for k in
                    ("run_id", "stored_at", "github_sha")}
                row["phases"][phase]["verified_file_count"] = len(p["manifest"]["files"])
                for f in p["run_dir"].glob("*receipt_envelope.json"):
                    if f.name.startswith("candidate_"):
                        continue  # Distinct shadow identities are not Production.
                    e = read(f)
                    row["receipts"].append(verify(e, execution.name))
            if "FORMAL" not in phases:
                row["status"] = "NO_CANONICAL_FINAL_IN_THIS_STORE"
                continue
            fdir = phases["FORMAL"]["run_dir"]
            final = read(fdir / "final_receipt_envelope.json")
            tickets = final["artifact"]["final_ticket"]["tickets"]
            row["final"] = verify(final, execution.name)
            row["ticket_count"] = len(tickets)
            row["investment"] = sum(t["stake"] for t in tickets)
            numeric_path = fdir / "numerical_materialization_summary.json"
            row["numeric_coverage"] = read(numeric_path).get("numeric_coverage") if numeric_path.exists() else None
            temporal = fdir / "final_before_post_verification.json"
            row["prestart_verification"] = read(temporal) if temporal.exists() else None
            row["capital_by_type"] = {}
            for bt in ("EXACTA", "TRIO", "TRIFECTA"):
                selected = [t for t in tickets if t["bet_type"] == bt]
                row["capital_by_type"][bt] = {"tickets": len(selected),
                    "investment": sum(t["stake"] for t in selected)}
            head, pair = collections.Counter(), collections.Counter()
            for t in tickets:
                if t["bet_type"] in ("EXACTA", "TRIFECTA"):
                    head[str(t["selection"][0])] += t["stake"]
                    pair[">".join(map(str, t["selection"][:2]))] += t["stake"]
            row["ordered_head_stake"] = dict(head)
            row["ordered_pair_stake"] = dict(pair)
            if "RESULT" not in phases:
                row["status"] = "SIGNED_FINAL_WITHOUT_CANONICAL_RESULT"
                continue
            result = read(phases["RESULT"]["run_dir"] / "result_receipt_envelope.json")
            a = result["artifact"]
            assert a["frozen_refs"]["final_receipt_sha256"] == final["receipt_sha256"]
            official = a["official_result"]
            row["official"] = official
            row["settlement"] = a["settlement"]
            # Refund/dead-heat outcomes need their authoritative settlement path.
            if official.get("refund_runner_ids") or len(official.get("winning_selections") or []) > 1:
                row["independent_settlement"] = "SPECIAL_OUTCOME_NOT_RECALCULATED"
            else:
                recalculated = settle_ticket_list(tickets, {"official_result": {
                    "top3": official["finish_order"][:3], "payouts": official["payouts"]}})
                assert recalculated["status"] == "SETTLED"
                for key in ("investment", "return"):
                    assert recalculated[key] == a["settlement"][key], key
                row["independent_settlement"] = recalculated
            review = a.get("automatic_post_result_review") or {}
            row["prediction"] = review.get("prediction")
            row["krs_utility"] = review.get("krs")
            row["mec"] = review.get("mec")
            row["conversion"] = review.get("conversion")
            row["first_material_failure"] = (review.get("failure_localization") or {}).get("first_material_failure")
            row["dominant_loss_owner_audit_only"] = classify_dominant_pfs_loss_owner(review)
            row["original_learning_present"] = bool(a.get("automatic_next_race_learning_state"))
            row["original_learning_has_dominant_field"] = "dominant_pfs_loss_owner" in canon(a.get("automatic_next_race_learning_state")).decode()
            shadow_path = fdir / "aki_adaptive_purchase_shadow_pre_result.json"
            if shadow_path.exists():
                shadow = read(shadow_path)
                binding = verify_signed_final_binding(final, shadow)
                attestation = read(fdir / "aki_adaptive_purchase_binding_attestation.json")
                assert all(attestation.get(k) == v for k,v in binding.items())
                measured = settle_ticket_list(shadow["candidate_tickets"], {"official_result": {
                    "top3": official["finish_order"][:3], "payouts": official["payouts"]}})
                row["original_aki_readonly_diagnostic"] = {
                    "status": "FROZEN_BINDING_VERIFIED_READONLY_COMPARISON",
                    "generated_at": shadow["generated_at"],
                    "shadow_sha256": shadow["sha256"],
                    "columns": shadow["selected_role_columns"],
                    "settlement": measured,
                    "forward_oos_credit": "UNCHANGED; canonical official checkpoint still required by tracker",
                    "new_forward_oos": 0}
            row["status"] = "FROZEN_FINAL_RESULT_SETTLEMENT_VERIFIED"
        except Exception as exc:
            row["status"] = "AUDIT_HOLD"
            errors.append({"execution_id": execution.name, "error": type(exc).__name__ + ":" + str(exc)})
    oos = scan_execution_store(STORE)
    oos["audit_max_drawdown"] = {arm: drawdown(oos["settled_rows"], arm) for arm in ("production", "adaptive")}
    (OUT / "aki_current_readonly_scan.json").write_text(json.dumps(oos, ensure_ascii=False, indent=2) + "\n")
    complete = [r for r in rows if r["status"] == "FROZEN_FINAL_RESULT_SETTLEMENT_VERIFIED"]
    index_cells = collections.defaultdict(list)
    for row in complete:
        phase = resolve_phase(row["execution_id"], "FORMAL", root=STORE)
        provenance = phase["run_dir"] / "index_provenance_manifest.json"
        if not provenance.exists():
            continue
        groups = collections.defaultdict(list)
        for cell in read(provenance)["rows"]:
            groups[cell["index"]].append(cell)
        for index, cells in groups.items():
            calculated = [c for c in cells if c["terminal_status"] == "CALCULATED"]
            observation = {"race_id": row["execution_id"], "calculated": len(calculated),
                           "ruled_neutral": sum(c["terminal_status"] == "RULED-NEUTRAL" for c in cells), "roles": {}}
            for role, rid in zip(("Winner", "P2", "P3"), row["official"]["finish_order"][:3]):
                target = next((c for c in cells if str(c["runner_id"]) == str(rid)), None)
                if not target or target["terminal_status"] != "CALCULATED":
                    observation["roles"][role] = {"status": target["terminal_status"] if target else "MISSING", "raw_rank_fraction": None}
                else:
                    v = target["value"]
                    mid = sum(c["value"] > v for c in calculated) + (sum(c["value"] == v for c in calculated)-1)/2
                    observation["roles"][role] = {"status": "CALCULATED", "raw_rank_fraction": mid/(len(calculated)-1) if len(calculated)>1 else None}
            index_cells[index].append(observation)
    index_report = {}
    for index, obs in sorted(index_cells.items()):
        item = {"races": len(obs), "calculated_cells": sum(o["calculated"] for o in obs),
                "neutral_cells": sum(o["ruled_neutral"] for o in obs), "roles": {}}
        for role in ("Winner", "P2", "P3"):
            vals = [o["roles"][role]["raw_rank_fraction"] for o in obs if o["roles"][role]["raw_rank_fraction"] is not None]
            item["roles"][role] = {"observed_races": len(vals), "mean_raw_descending_rank_fraction": sum(vals)/len(vals) if vals else None}
        index_report[index] = item
    (OUT / "numerical_observability.json").write_text(json.dumps({
        "method": "Post-result descriptive ranks of immutable FORMAL provenance; 0 is highest raw value, 1 lowest. No favorable-direction assumption, ablation, probability, EV, policy fitting or new Forward OOS. Correlated indices cannot establish causal contribution. Pair/Third conditional incremental utility remains unmeasured.",
        "production_consumption": "NOT_AUTHORIZED", "indices": index_report}, ensure_ascii=False, indent=2)+"\n")
    invest = sum(r["settlement"]["investment"] for r in complete)
    payout = sum(r["settlement"]["return"] for r in complete)
    report = {"observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_main": "1225349d64fdffdf87d6035db751d57be731e9dc",
        "method": "Read-only canonical checkpoint/Ed25519/hash/independent settlement reconciliation. No new Forward OOS, no source/final/result signing, no ledger mutation.",
        "cohort_limit": "Existing main canonical directories only; absent races may exist in PR archives. Not an all-day execution success denominator.",
        "canonical_directories": len(rows), "verified_final_result_races": len(complete),
        "investment": invest, "return": payout, "pfs": payout/invest*100 if invest else None,
        "wide_100plus": sum(r["ticket_count"] >= 100 for r in complete),
        "hit_but_loss": sum(0 < r["settlement"]["return"] < r["settlement"]["investment"] for r in complete),
        "total_loss": sum(r["settlement"]["return"] == 0 for r in complete),
        "first_material_failures": dict(collections.Counter(r["first_material_failure"] for r in complete)),
        "dominant_loss_owners_audit_only": dict(collections.Counter(r["dominant_loss_owner_audit_only"]["owner"] for r in complete)),
        "krs_post_result_classes": dict(collections.Counter(r["krs_utility"]["post_result_evaluation"]["classification"] for r in complete)),
        "krs_rescue_signals": sum(r["krs_utility"]["post_result_evaluation"]["rescue_count"] for r in complete),
        "static_role_capture": dict(collections.Counter(k for r in complete for k,v in r["prediction"]["role_capture"].items() if v)),
        "by_bet_type": {bt: {"investment": sum(r["independent_settlement"]["by_bet_type"][bt]["investment"] for r in complete),
                            "return": sum(r["independent_settlement"]["by_bet_type"][bt]["return"] for r in complete)} for bt in ("EXACTA", "TRIO", "TRIFECTA")},
        "rows": rows, "errors": errors}
    (OUT / "kaw_frozen_audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k:v for k,v in report.items() if k != "rows"}))
    print(json.dumps({k:oos[k] for k in ("status", "eligible_races", "days", "production", "adaptive", "audit_max_drawdown", "held", "errors")}))

if __name__ == "__main__":
    main()
