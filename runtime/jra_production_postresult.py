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
    seen, wins, stake_total, ret_total = set(), [], 0, 0
    for t in tickets:
        kind = str(t.get("bet_type") or "").upper()
        if kind not in BET_N:
            raise ProductionPostResultError("UNKNOWN_BET_TYPE:" + kind)
        sel = [int(x) for x in t.get("selection") or []]
        stake = t.get("stake")
        if (len(sel) != BET_N[kind] or len(set(sel)) != len(sel) or not isinstance(stake, int)
                or isinstance(stake, bool) or stake <= 0 or stake % 100):
            raise ProductionPostResultError("FROZEN_TICKET_INVALID")
        key = (kind, tuple(sorted(sel)) if kind == "TRIO" else tuple(sel))
        if key in seen:
            raise ProductionPostResultError("DUPLICATE_FROZEN_TICKET")
        seen.add(key)
        pay = prices[kind]
        win_sel = sorted(pay["selection"]) if kind == "TRIO" else list(pay["selection"])
        obs = sorted(sel) if kind == "TRIO" else sel
        amount = (stake // 100) * int(pay["per_100_yen"]) if obs == win_sel else 0
        stake_total += stake
        ret_total += amount
        if amount:
            wins.append({"bet_type": kind, "selection": sel, "stake": stake,
                         "payout_per_100": int(pay["per_100_yen"]), "return": amount})
    if stake_total != int(ft.get("total_investment") or 0):
        raise ProductionPostResultError("FROZEN_TOTAL_INVESTMENT_MISMATCH")
    decision = (final.get("capital_policy_decision") or {}).get("decision")
    recommendation_only = decision == "EXECUTE_RECOMMENDATION_PORTFOLIO"
    return {
        "status": "SETTLED",
        "pfs_authority": "FROZEN-RECOMMENDATION-PFS",
        "total_investment": stake_total,
        "total_payout": ret_total,
        "refund": 0,
        "profit_loss": ret_total - stake_total,
        "pfs": (100.0 * ret_total / stake_total) if stake_total else None,
        "winning_tickets": wins,
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
