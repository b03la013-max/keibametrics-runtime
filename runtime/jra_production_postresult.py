"""JRA Production closed loop: signed FINAL -> official JRA result -> settlement -> RESULT request.

Builds ``runtime/results/<race_id>.json`` for the canonical Formal Result Runner
(which issues the signed RESULT receipt and runs review / learning / OOS).

Never mutates or backdates the immutable FINAL. Recommendation-only tickets are
settled as a frozen *recommendation* (virtual PFS); actual purchase is recorded
separately and is never inferred.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "jra_source_runtime"))

PROFILE = "KM-JRA-PRODUCTION-POSTRESULT-CLOSEDLOOP-20261010-R1"
BET_N = {"EXACTA": 2, "TRIO": 3, "TRIFECTA": 3}


class ProductionPostResultError(ValueError):
    pass


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def _dt(v):
    return datetime.fromisoformat(str(v).replace("Z", "+00:00"))


def verify_final(final: dict) -> None:
    body = {k: v for k, v in final.items() if k != "sha256"}
    if final.get("sha256") != _sha(body):
        raise ProductionPostResultError("IMMUTABLE_FINAL_HASH_INVALID")
    if final.get("family_id") != "JRA" or final.get("temporal_mode") != "FORMAL-PRE-RACE":
        raise ProductionPostResultError("NOT_JRA_FORMAL_PRE_RACE_FINAL")
    receipt = final.get("final_receipt") or {}
    ts = (receipt.get("receipt") or {}).get("timestamp")
    if not final.get("final_receipt_sha256") or not ts:
        raise ProductionPostResultError("SIGNED_FINAL_RECEIPT_MISSING")
    if _dt(ts) >= _dt(final["scheduled_post_at"]):
        raise ProductionPostResultError("FINAL_RECEIPT_AFTER_POST")


def settle_final(final: dict, official: dict) -> dict:
    """Settle exactly the frozen FINAL tickets against verified official payouts."""
    ft = final.get("final_ticket") or {}
    tickets = list(ft.get("tickets") or [])
    top3 = [int(x) for x in official["top3"]]
    prices = official["payouts"]
    refund_ids=official.get("refund_runner_ids") or []
    if (not isinstance(refund_ids,list) or any(type(x) is not int or not 1<=x<=18 for x in refund_ids)
            or len(refund_ids)!=len(set(refund_ids))):
        raise ProductionPostResultError("OFFICIAL_REFUND_RUNNER_INVALID")
    not_refundable={int(r["horse_no"]) for r in official.get("non_finishers") or []
                    if r.get("finish_status") in {"DID_NOT_FINISH","DISQUALIFIED"}}
    if set(refund_ids)&not_refundable:
        raise ProductionPostResultError("NONCANCELLATION_REFUND_FORBIDDEN")
    if set(refund_ids)&set(top3):
        raise ProductionPostResultError("OFFICIAL_REFUND_TOP3_CONFLICT")
    seen, wins, refunded_tickets, stake_total, ret_total, refund = set(), [], [], 0, 0, 0
    for t in tickets:
        kind = str(t.get("bet_type") or "").upper()
        if kind not in BET_N:
            raise ProductionPostResultError("UNKNOWN_BET_TYPE:" + kind)
        sel = list(t.get("selection") or [])
        if any(type(x) is not int or not 1 <= x <= 18 for x in sel):
            raise ProductionPostResultError("FROZEN_SELECTION_INVALID")
        stake = t.get("stake")
        if (len(sel) != BET_N[kind] or len(set(sel)) != len(sel) or not isinstance(stake, int)
                or isinstance(stake, bool) or stake <= 0 or stake % 100):
            raise ProductionPostResultError("FROZEN_TICKET_INVALID")
        key = (kind, tuple(sorted(sel)) if kind == "TRIO" else tuple(sel))
        if key in seen:
            raise ProductionPostResultError("DUPLICATE_FROZEN_TICKET")
        seen.add(key)
        stake_total += stake
        if set(sel)&set(refund_ids):
            refund += stake
            refunded_tickets.append({"bet_type":kind,"selection":sel,"stake":stake,
                                     "refund":stake,"reason":"OFFICIAL_WITHDRAWN_RUNNER"})
            continue
        pay = prices[kind]
        if (type(pay.get("per_100_yen")) is not int or pay["per_100_yen"] < 0
                or not isinstance(pay.get("selection"), list)
                or len(pay["selection"]) != BET_N[kind]
                or any(type(x) is not int or not 1 <= x <= 18 for x in pay["selection"])
                or len(set(pay["selection"])) != BET_N[kind]):
            raise ProductionPostResultError("OFFICIAL_PAYOUT_INVALID")
        win_sel = sorted(pay["selection"]) if kind == "TRIO" else list(pay["selection"])
        obs = sorted(sel) if kind == "TRIO" else sel
        amount = (stake // 100) * int(pay["per_100_yen"]) if obs == win_sel else 0
        ret_total += amount
        if amount:
            wins.append({"bet_type": kind, "selection": sel, "stake": stake,
                         "payout_per_100": int(pay["per_100_yen"]), "return": amount})
    if type(ft.get("total_investment")) is not int or stake_total != ft["total_investment"]:
        raise ProductionPostResultError("FROZEN_TOTAL_INVESTMENT_MISMATCH")
    decision = (final.get("capital_policy_decision") or {}).get("decision")
    recommendation_only = decision == "EXECUTE_RECOMMENDATION_PORTFOLIO"
    effective_investment=stake_total-refund
    return {
        "status": "SETTLED",
        "pfs_authority": "FROZEN-RECOMMENDATION-PFS",
        "total_investment": stake_total,
        "total_payout": ret_total,
        "refund": refund,
        "effective_investment":effective_investment,
        "profit_loss": ret_total + refund - stake_total,
        "pfs": (100.0 * ret_total / effective_investment) if effective_investment else None,
        "gross_stake_pfs":(100.0 * ret_total / stake_total) if stake_total else None,
        "pfs_denominator":"EFFECTIVE_INVESTMENT_EXCLUDING_OFFICIAL_REFUNDS",
        "winning_tickets": wins,
        "refunded_tickets":refunded_tickets,
        "no_bet": bool(ft.get("no_bet")),
        "capital_policy_decision": decision,
        "actual_purchase_status": ("NOT_PURCHASED_RECOMMENDATION_ONLY" if recommendation_only
                                   else "UNVERIFIED"),
        "actual_pfs_status": "NOT_VERIFIED",
        "note": "Settled frozen FINAL tickets at official JRA payouts. Recommendation PFS is virtual; actual purchase is recorded separately and never inferred.",
    }


def build_result_request(final: dict, official: dict, evidence: dict) -> dict:
    verify_final(final)
    settlement = settle_final(final, official)
    finish = [int(r["horse_no"]) for r in sorted(
        (r for r in (evidence.get("parsed") or {}).get("runners") or []
         if isinstance(r.get("finish"), int)), key=lambda r: r["finish"])]
    fpp = final.get("final_prediction_package") or {}
    req = {
        "race_id": final["race_id"],
        "result_lane": "PRODUCTION",
        "official_result": {
            "status": "OFFICIAL",
            "finish_order": finish,
            "top3": [int(x) for x in official["top3"]],
            "payouts": official["payouts"],
            "refund_runner_ids":official.get("refund_runner_ids") or [],
            "non_finishers":official.get("non_finishers") or [],
            "refund_declaration":official.get("refund_declaration"),
            "source": "JRA official result (www.jra.go.jp)",
            "source_url": evidence.get("url"),
            "raw_sha256": evidence.get("sha256"),
            "captured_at": evidence.get("captured_at"),
            "result_use": "POST-RACE",
        },
        "settlement": settlement,
        "frozen_prediction_ref": {
            "prediction_id": final["race_id"] + "-PRODUCTION",
            "immutable_final_sha256": final["sha256"],
            "final_receipt_sha256": final["final_receipt_sha256"],
            "source_cutoff": final.get("prediction_cutoff"),
            "final_freeze_timestamp": final.get("final_freeze_timestamp"),
            "final_status": "FORMAL-PRE-RACE / FULL_FORMAL_E2E_PASS",
            "validation_status": fpp.get("validation_status") or "VALIDATED",
        },
        "learning_event": {
            "status": "RECORDED",
            "profile": PROFILE,
            "event_type": "JRA_PRODUCTION_POST_RACE_REVIEW",
            "result_use": "PREQUENTIAL_TO_NEXT_RACE_ONLY",
            "numeric_recalibration": False,
            "new_model_weights_applied": False,
            "promotion_authority": False,
        },
    }
    return req


def build_settlement_correction(final:dict, original_result:dict, official:dict, evidence:dict,
                                *, audited_at:str)->dict:
    """Record a post-result correction separately; never rewrite signed inputs.

    This is an unsigned audit revision, not a newly signed RESULT receipt or
    an authorization to replace an old canonical result or Learning State.
    """
    verify_final(final)
    if original_result.get("race_id")!=final["race_id"]:
        raise ProductionPostResultError("CORRECTION_RACE_MISMATCH")
    if (original_result.get("frozen_prediction_ref") or {}).get("immutable_final_sha256")!=final["sha256"]:
        raise ProductionPostResultError("CORRECTION_FINAL_BINDING_MISMATCH")
    if (not isinstance(evidence.get("sha256"),str) or len(evidence["sha256"])!=64
            or any(c not in '0123456789abcdef' for c in evidence['sha256'])):
        raise ProductionPostResultError("CORRECTION_OFFICIAL_RAW_HASH_REQUIRED")
    when=_dt(audited_at)
    captured=_dt(evidence["captured_at"])
    if not when.tzinfo or not captured.tzinfo or not _dt(final["scheduled_post_at"])<captured<=when:
        raise ProductionPostResultError("CORRECTION_CHRONOLOGY_INVALID")
    corrected=settle_final(final,official)
    before=original_result["settlement"]
    fields=("total_investment","refund","effective_investment","total_payout","profit_loss","pfs")
    out={"race_id":final["race_id"],"profile":"JRA-EXISTING-SETTLEMENT-CORRECTION-AUDIT",
         "classification":"POSTRESULT_CORRECTION_AUDIT_NOT_SIGNED_RESULT_NOT_FORWARD_OOS",
         "audited_at":when.isoformat(),"original_result_sha256":_sha(original_result),
         "immutable_final_sha256":final["sha256"],"final_receipt_sha256":final["final_receipt_sha256"],
         "official_evidence":{"raw_sha256":evidence["sha256"],"captured_at":evidence["captured_at"],"url":evidence.get("url")},
         "official_refund_runner_ids":official.get("refund_runner_ids") or [],
         "original_settlement":before,"corrected_settlement":corrected,
         "changes":{k:{"before":before.get(k),"after":corrected.get(k)} for k in fields if before.get(k)!=corrected.get(k)},
         "signed_result_correction":"NOT_ISSUED","old_learning_unchanged":True,
         "original_frozen_prediction_unchanged":True,"actual_purchase_status":"UNVERIFIED"}
    out["sha256"]=_sha(out)
    return out


def _intent_for(root: Path, race_id: str) -> dict:
    hits = []
    for p in sorted((root / "runtime" / "jra_formal_intents").glob(race_id + "-*.json")):
        x = json.loads(p.read_text(encoding="utf-8"))
        if x.get("race_id") == race_id and (x.get("jra_source") or {}).get("jra_meeting_key"):
            hits.append(x)
    if not hits:
        raise ProductionPostResultError("JRA_FORMAL_INTENT_MISSING")
    keys = {(h["race_date"], h["jra_source"]["jra_meeting_key"], int(h["race_no"])) for h in hits}
    if len(keys) != 1:
        raise ProductionPostResultError("JRA_FORMAL_INTENT_AMBIGUOUS")
    return hits[-1]


def process(root: Path, race_id: str, *, now=None) -> str:
    out = root / "runtime" / "results" / (race_id + ".json")
    if out.exists():
        return "ALREADY_RESULTED"
    fpath = root / "runtime" / "final_artifacts" / (race_id + ".json")
    if not fpath.exists():
        return "NO_PRODUCTION_FINAL"
    final = json.loads(fpath.read_text(encoding="utf-8"))
    verify_final(final)
    post = _dt(final["scheduled_post_at"])
    now = now or datetime.now(timezone.utc)
    if now <= post + timedelta(minutes=1):
        return "RESULT_NOT_YET_DUE"
    rel = fpath.relative_to(root).as_posix()
    committed = subprocess.check_output(["git", "log", "--diff-filter=A", "-1", "--format=%cI", "--", rel],
                                        cwd=root, text=True).strip()
    if not committed or _dt(committed) >= post:
        raise ProductionPostResultError("NO_PRE_START_GIT_COMMIT_WITNESS")
    from jra_candidate_postresult_closedloop import fetch_jra_result, verify_official_result
    intent = _intent_for(root, race_id)
    evidence = fetch_jra_result(intent["race_date"], intent["jra_source"]["jra_meeting_key"],
                                int(intent["race_no"]))
    ranking = [str(x) for x in (final.get("static_prediction") or {}).get("ranking") or []]
    official = verify_official_result(evidence["parsed"], evidence["text"], ranking)
    req = build_result_request(final, official, evidence)
    cpre = root / "runtime" / "source_candidate_oos" / race_id / "pre_result.json"
    if cpre.exists():
        c = json.loads(cpre.read_text(encoding="utf-8"))
        req["candidate_shadow_ref"] = {"final_receipt_sha256": c.get("candidate_final_receipt_sha256"),
                                       "pre_result_sha256": c.get("sha256"),
                                       "production_effect": "NONE"}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(req, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return "RESULT_REQUEST_WRITTEN"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", default=".")
    p.add_argument("--race-id")
    p.add_argument("--days", type=int, default=3)
    a = p.parse_args()
    root = Path(a.repo_root).resolve()
    from jra_candidate_postresult_closedloop import PendingOfficialResult
    paths = ([root / "runtime" / "final_artifacts" / (a.race_id + ".json")] if a.race_id
             else sorted((root / "runtime" / "final_artifacts").glob("KM-JRA-*.json")))
    now = datetime.now(timezone.utc)
    results = []
    for f in paths:
        rid = f.stem
        try:
            if not a.race_id:
                fin = json.loads(f.read_text(encoding="utf-8"))
                age = (now - _dt(fin.get("scheduled_post_at"))).total_seconds()
                if not 0 <= age <= a.days * 86400:
                    continue
            status = process(root, rid, now=now)
        except PendingOfficialResult as e:
            status = "PENDING:" + str(e)
        except Exception as e:  # report, never fabricate
            status = "BLOCKED:" + type(e).__name__ + ":" + str(e)
        results.append({"race_id": rid, "status": status})
    print(json.dumps({"profile": PROFILE, "processed": results}, ensure_ascii=False))
    if a.race_id and results and results[0]["status"].startswith("BLOCKED:"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
