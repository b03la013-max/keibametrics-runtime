"""Verify official frozen RESULT; settle signed PAPER companion separately.

The canonical signed FINAL has no purchase tickets. Its external settlement
stays zero-capital, with undefined PFS. PAPER performance never becomes actual
purchase performance or future OOS. Preserve every original receipt.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import urllib.request
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from local_aki_columns import sha
from mec_r4_shadow import settle_ticket_list
from post_result_learning import build_post_result_review, build_learning_state


def run(acceptance_path, original_result_path):
    directory = Path(acceptance_path).resolve().parent
    acceptance = json.loads(Path(acceptance_path).read_text())
    final = json.loads((directory / "final_receipt.json").read_text())
    original = json.loads(Path(original_result_path).read_text())
    attestation = json.loads((ROOT / "evidence/local_aki_columns_20261012/destination_verification.json").read_text())
    endpoint = attestation["endpoint"]
    key = Ed25519PublicKey.from_public_bytes(base64.b64decode(attestation["health"]["receipt_public_key_b64"]))
    def save(name, obj):
        p = directory / (name + ".json")
        encoded = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
        if p.exists() and p.read_text() != encoded:
            raise RuntimeError("IMMUTABLE_POSTRESULT_CONFLICT:" + name)
        p.write_text(encoded)
        return obj
    def signed(envelope, phase):
        raw = json.dumps(envelope["receipt"],ensure_ascii=False,sort_keys=True,separators=(",", ":")).encode()
        key.verify(base64.b64decode(envelope["signature"]), raw)
        if (sha(envelope["artifact"]) != envelope["receipt"]["artifact_sha256"]
                or hashlib.sha256(raw).hexdigest() != envelope["receipt_sha256"]
                or envelope["receipt"]["race_id"] != acceptance["race_id"]
                or envelope["receipt"]["phase"] != phase
                or envelope["receipt"]["status"] != ("SOURCE_FROZEN" if phase == "SOURCE" else "PASS")):
            raise RuntimeError("POSTRESULT_RECEIPT_BINDING_INVALID")
    def call(path, payload, name):
        p = directory / (name + ".json")
        if p.exists(): return json.loads(p.read_text())
        request = urllib.request.Request(endpoint + path, data=json.dumps(payload,ensure_ascii=False).encode(),
                                         headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(request,timeout=120) as response:
            return save(name,json.load(response))
    signed(final, "FINAL")
    phase = original["receipt"]["phase"]
    if phase == "SOURCE":
        signed(original, "SOURCE")
        from formal_execution_orchestrator import parse_official_result_snapshot
        from local_physical.nar_source_manifest import _result_source, LOCAL_BABA_CODES
        artifact = original["artifact"]
        context = artifact["source_race_context"]
        expected = _result_source(context["venue_id"],LOCAL_BABA_CODES[context["venue_id"]],
                                 context["race_date"].replace("-","/"),int(context["race_no"]))
        sources = artifact["sources"]
        if len(sources) != 1 or sources[0]["final_url"] != expected["url"]:
            raise RuntimeError("OFFICIAL_RESULT_SOURCE_SCOPE_MISMATCH")
        # Result-only raw acquisition is never reused as pre-start evidence.
        saved_input = json.loads((directory / "signed_source_input.json").read_text())
        frozen_context = saved_input["artifact"]["source_race_context"]
        if any(str(context[k]).replace("/","-") != str(frozen_context[k]).replace("/","-")
               for k in ("venue_id","race_date","race_no")):
            raise RuntimeError("OFFICIAL_RESULT_FROZEN_RACE_MISMATCH")
        runners = saved_input["artifact"]["active_runner_universe"]["runners"]
        order, payouts = parse_official_result_snapshot(sources[0],context,[r["runner_id"] for r in runners])
        official = {"finish_order":order,"payouts":payouts,"source":expected["url"],
                    "official_result_verified":True,
                    "official_result_verification_ref":expected["url"]+"#sha256="+sources[0]["raw_sha256"]}
        available_at = sources[0]["fetched_at"]
        save("official_result_source_receipt",original)
    else:
        signed(original, "RESULT")
        save("original_official_result_receipt", original)
        official = original["artifact"]["official_result"]
        available_at = original["artifact"]["result_available_at"]
    fpp = final["artifact"]["final_prediction_package"]
    selected = fpp["aki_selection"]["columns"]
    for rid, roles in fpp.get("selected_roles", fpp["roles"]).items():
        expected = [c for c in ("W","P2","P3") if rid in selected[c]["selected"]]
        if roles != expected: raise RuntimeError("FINAL_ROLE_PROJECTION_MISMATCH")
    payload = save("replay_result_payload", {
        "family_id":"LOCAL", "race_id":acceptance["race_id"], "final_receipt":final,
        "official_result":official, "result_available_at":available_at,
        "settlement":{"status":"COMPLETE", "investment":0, "return":0, "actual_purchase":False},
        "pfs_authority":"REPLAY_ZERO_CAPITAL / NO_ACTUAL_PURCHASE / NOT_OOS",
        "krs_prediction_utility":fpp["krs_prediction_utility_shadow"]})
    result = call("/result",payload,"replay_result_receipt")
    signed(result,"RESULT")
    verified = call("/verify",result,"replay_result_verification")
    if verified.get("valid") is not True: raise RuntimeError("EXTERNAL_RESULT_VERIFY_FAILED")
    if result["artifact"]["frozen_refs"]["final_receipt_sha256"] != final["receipt_sha256"]:
        raise RuntimeError("RESULT_FINAL_LINEAGE_MISMATCH")
    facts = {"official_result":{**official,"top3":official["finish_order"][:3]}}
    settlement = settle_ticket_list(fpp["paper_tickets"],facts)
    save("paper_settlement",settlement)
    capital_arm = fpp.get("capital_paper_arm")
    if capital_arm and capital_arm["allocation"].get("tickets") is not None:
        save("capital_arm_settlement",settle_ticket_list(capital_arm["allocation"]["tickets"],facts))
    # This is a transparent projection of signed companion tickets, never a
    # modified/re-signed canonical purchase FINAL.
    projection = {"race_id":acceptance["race_id"],"final_receipt_sha256":final["receipt_sha256"],
                  "final_prediction_package":fpp,
                  "krs_prediction_utility":fpp["krs_prediction_utility_shadow"],
                  "minimum_efficient_coverage":final["artifact"]["minimum_efficient_coverage"],
                  "final_ticket":{"tickets":fpp["paper_tickets"],"total_investment":settlement["investment"]},
                  "scope":"PAPER_COMPANION_PROJECTION / NOT_PURCHASE_FINAL"}
    projection["sha256"] = sha(projection)
    save("paper_projection",projection)
    review = build_post_result_review({"race_id":acceptance["race_id"],
        "official_result":{"top3":official["finish_order"][:3]},
        "frozen_prediction_ref":{"final_receipt_sha256":final["receipt_sha256"],"final_status":"REPLAY_PAPER"},
        "settlement":{"status":"COMPLETE","investment":settlement["investment"],
                      "return":settlement["return"],"pfs_authority":"REPLAY_PAPER / NOT_OOS"}},projection)
    save("paper_reflection",review)
    save("paper_learning",build_learning_state(review))
    summary = {"status":"EXTERNAL_RESULT_REFLECTION_LEARNING_PASS / REPLAY_PAPER",
               "execution_id":acceptance["execution_id"],"race_id":acceptance["race_id"],
               "final_receipt_sha256":final["receipt_sha256"],"result_receipt_sha256":result["receipt_sha256"],
               "paper_investment":settlement["investment"],"paper_return":settlement["return"],
               "paper_pfs":settlement["pfs"],
               "actual_purchase":"NONE / NOT_EXECUTED", "canonical_zero_capital_pfs":result["artifact"]["settlement"]["pfs"],
               "first_paper_failure":review["failure_localization"]["first_material_failure"],
               "unknown_future_oos_count":0,"production_change_authorized":False}
    return save("postresult_acceptance",summary)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--acceptance",required=True)
    p.add_argument("--original-result",required=True)
    a = p.parse_args()
    print(json.dumps(run(a.acceptance,a.original_result),ensure_ascii=False))
