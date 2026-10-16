"""JRA Candidate closed-loop: verified official result -> frozen-ticket settlement -> learning.

This module never changes or backdates PRE_RESULT/FINAL. It does not confer
Production prediction, actual purchase, or signed RESULT authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "jra_source_runtime"))

from jra_source_candidate_oos import evaluate_result
from jra_source_candidate_promotion_gate import bind_result
from jra_same_day_results import _open_day, parse_result_detail
from jra_race_card_detail import _date8, _post
from source_acquisition import _decode, _html_text, utcnow

PROFILE = "KM-JRA-CANDIDATE-AUTOMATIC-POSTRESULT-CLOSEDLOOP-20261010-R1"
BET_KINDS = {"EXACTA": ("馬単", 2), "TRIO": ("3連複", 3), "TRIFECTA": ("3連単", 3)}


class PendingOfficialResult(ValueError):
    pass


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def _verified_pre_frozen(pre: dict, final: dict, race_id: str) -> None:
    if pre.get("race_id") != race_id or final.get("race_id") != race_id:
        raise ValueError("RACE_ID_BINDING_MISMATCH")
    if pre.get("oos_eligible") is not True or pre.get("candidate_final_verified") is not True:
        raise ValueError("PRE_START_CANDIDATE_FINAL_NOT_VERIFIED")
    if pre.get("source_snapshot_sha256") != final.get("source_snapshot_sha256"):
        raise ValueError("SOURCE_BASIS_MISMATCH")
    if pre.get("sha256") != canonical_sha({k:v for k,v in pre.items() if k != "sha256"}):
        raise ValueError("PRE_RESULT_HASH_INVALID")
    if final.get("sha256") != canonical_sha({k:v for k,v in final.items() if k != "sha256"}):
        raise ValueError("CANDIDATE_FINAL_HASH_INVALID")
    if pre.get("candidate_final_receipt_sha256") != (final.get("final_receipt") or {}).get("receipt_sha256"):
        raise ValueError("FINAL_RECEIPT_BINDING_MISMATCH")
    post = datetime.fromisoformat(str(pre["scheduled_post_at"]).replace("Z","+00:00"))
    ft = datetime.fromisoformat(str(pre["candidate_final_receipt_timestamp"]).replace("Z","+00:00"))
    if ft >= post:
        raise ValueError("FINAL_AFTER_SCHEDULED_POST")
    if final.get("candidate_only") is not True or final.get("production_effect") not in ("NONE", None):
        raise ValueError("CANDIDATE_AUTHORITY_LEAK")


def parse_official_payouts(text: str) -> dict:
    """Extract only unambiguous JRA payouts per 100 yen after the LAST 払戻金.

    All three issued bet types must be present. Duplicate, ambiguous, or
    malformed official payout entries fail closed, not silently marked zero.
    """
    if "払戻金" not in text:
        raise PendingOfficialResult("JRA_OFFICIAL_PAYOUT_SECTION_NOT_PUBLISHED")
    # JRA footer also contains 払戻金 (e.g., 払戻金の支払を受けた方へ).
    # Anchor the actual payout table by the adjacent first bet-type label.
    anchors = list(re.finditer(r"払戻金\s+単勝\s+", text))
    if len(anchors) != 1:
        raise PendingOfficialResult("JRA_OFFICIAL_PAYOUT_TABLE_NOT_UNIQUE")
    tail = "単勝 " + text[anchors[0].end():].split("勝馬の紹介",1)[0]
    out = {}
    for kind, (label, count) in BET_KINDS.items():
        pattern = re.escape(label) + r"\s+((?:\d{1,2}\s*-\s*){" + str(count - 1) + r"}\d{1,2})\s+([\d,]+)\s*円"
        matches = re.findall(pattern, tail)
        if len(matches) != 1:
            raise PendingOfficialResult("JRA_PAYOUT_MISSING_OR_AMBIGUOUS:" + kind)
        selection, yen = matches[0]
        nums = [int(x) for x in re.findall(r"\d+", selection)]
        amount = int(yen.replace(",", ""))
        if len(nums) != count or len(set(nums)) != count or amount <= 0:
            raise PendingOfficialResult("JRA_PAYOUT_FORMAT_INVALID:" + kind)
        out[kind] = {"selection": nums, "per_100_yen": amount}
    return out


def verify_official_result(parsed: dict, payout_text: str, frozen_runner_ids: list[str]) -> dict:
    rows = list(parsed.get("runners") or [])
    if parsed.get("official") is not True or not rows:
        raise PendingOfficialResult("JRA_OFFICIAL_RESULT_TABLE_MISSING")
    ids = [str(r.get("runner_id")) for r in rows]
    if len(set(ids)) != len(ids) or not set(ids).issubset(set(frozen_runner_ids)):
        raise ValueError("OFFICIAL_RESULT_RUNNER_UNIVERSE_MISMATCH")
    top = {}
    for r in rows:
        rank = r.get("finish")
        if rank in (1,2,3):
            if rank in top:
                raise PendingOfficialResult("JRA_DEAD_HEAT_MANUAL_ADJUDICATION_REQUIRED")
            top[rank] = int(r["horse_no"])
    if set(top) != {1,2,3}:
        raise PendingOfficialResult("JRA_TOP3_NOT_CONFIRMED")
    actual = [top[1], top[2], top[3]]
    payouts = parse_official_payouts(payout_text)
    for kind, spec in payouts.items():
        expected = actual[:2] if kind == "EXACTA" else sorted(actual) if kind == "TRIO" else actual
        found = sorted(spec["selection"]) if kind == "TRIO" else spec["selection"]
        if found != expected:
            raise PendingOfficialResult("OFFICIAL_PAYOUT_TOP3_MISMATCH:" + kind)
    return {"top3": actual, "payouts": payouts}


def settle_frozen_candidate(pre: dict, final: dict, official: dict, *, source_sha256: str, source_url: str) -> dict:
    race_id = str(pre.get("race_id") or "")
    _verified_pre_frozen(pre, final, race_id)
    actual = [int(x) for x in official["top3"]]
    prices = official["payouts"]
    tickets = list(((final.get("mec") or {}).get("tickets") or []))
    if not tickets:
        raise ValueError("FROZEN_MEC_TICKETS_MISSING")
    purchases = []
    seen = set()
    stake_total = 0
    return_total = 0
    for ticket in tickets:
        kind = str(ticket.get("bet_type") or "")
        if kind not in BET_KINDS:
            raise ValueError("UNKNOWN_BET_TYPE:" + kind)
        n = BET_KINDS[kind][1]
        sel = [int(x) for x in ticket.get("selection") or []]
        stake = ticket.get("stake")
        if len(sel) != n or len(set(sel)) != n or not isinstance(stake,int) or isinstance(stake,bool) or stake <= 0 or stake % 100:
            raise ValueError("FROZEN_TICKET_INVALID")
        key = (kind, tuple(sorted(sel)) if kind == "TRIO" else tuple(sel))
        if key in seen:
            raise ValueError("DUPLICATE_FROZEN_TICKET")
        seen.add(key)
        pay = prices[kind]
        winner = sorted(pay["selection"]) if kind == "TRIO" else pay["selection"]
        observed = sorted(sel) if kind == "TRIO" else sel
        amount = (stake // 100) * pay["per_100_yen"] if observed == winner else 0
        purchases.append({"bet_type":kind,"selection":sel,"stake":stake,"recommended_return":amount,
                          "win":amount>0})
        stake_total += stake
        return_total += amount
    required = int((final.get("capital") or {}).get("required_capital") or 0)
    if required != stake_total or int((final.get("mec") or {}).get("ticket_count") or 0) != len(purchases):
        raise ValueError("FROZEN_CAPITAL_CANONICAL_MISMATCH")
    evaluated = evaluate_result(pre, actual)
    bound = bind_result(pre, evaluated)
    if not evaluated["winner_capture"]: first = "W_HEAD_ZERO"
    elif not evaluated["p2_capture"]: first = "P2_SECOND_ZERO"
    elif not evaluated["p3_capture"]: first = "P3_THIRD_ZERO"
    elif not evaluated["ordered_pair_capture"]: first = "ORDERED_PAIR_MISSING"
    elif not evaluated["exact_capture"]: first = "PAIR_CONDITIONED_THIRD_MISSING"
    elif not any(x["win"] for x in purchases): first = "TICKET_CONVERSION_UNREACHABLE"
    elif return_total < stake_total: first = "CAPITAL_EFFICIENCY_LOSS"
    else: first = "NONE"
    owner = "NONE" if return_total >= stake_total else (
        "CAPITAL_EFFICIENCY" if any(x["win"] for x in purchases) else
        "PREDICTION_ROLE_ORDER" if first in {"W_HEAD_ZERO","P2_SECOND_ZERO","P3_THIRD_ZERO","ORDERED_PAIR_MISSING","PAIR_CONDITIONED_THIRD_MISSING"} else
        "TICKET_CONVERSION")
    report = {
        "profile": PROFILE, "race_id": race_id, "status":"SETTLED_FROZEN_CANDIDATE_RECOMMENDATION",
        "authority":"CANDIDATE / NON-PRODUCTION / NO-AUTO-PROMOTION",
        "official_result_source_sha256":source_sha256,
        "official_result_source_url":source_url,
        "frozen_pre_result_sha256":pre["sha256"],"frozen_candidate_final_sha256":final["sha256"],
        "actual_top3": actual, "official_payouts": prices, "purchased_ticket_count":len(purchases),
        "frozen_tickets":purchases, "recommended_stake_yen":stake_total,
        "recommended_return_yen":return_total,
        "recommended_profit_yen":return_total-stake_total,
        "frozen_recommendation_pfs_percent":round(100*return_total/stake_total,2),
        "actual_purchase_status":"UNVERIFIED","actual_pfs_status":"NOT_VERIFIED",
        "first_material_failure":first,"dominant_pfs_loss_owner":owner,
        "prediction_measurement":evaluated, "oos_eligible":pre["oos_eligible"],
        "result_receipt_status":"OFFICIAL_HTTP_SNAPSHOT_HASH_BOUND / SIGNED_RESULT_NOT_VERIFIED",
        "production_effect":"NONE","automatic_promotion":False,
    }
    report["sha256"] = canonical_sha(report)
    bound["settlement_sha256"] = report["sha256"]
    bound["official_result_source_sha256"] = source_sha256
    bound["sha256"] = canonical_sha({k:v for k,v in bound.items() if k!="sha256"})
    learning = {
        "profile":PROFILE,"race_id":race_id,"status":"LEARNING_OBSERVATION_RECORDED / NO_POLICY_AUTO_CHANGE",
        "previous_state_sha256":pre["sha256"],"settlement_sha256":report["sha256"],
        "first_material_failure":first,"dominant_pfs_loss_owner":owner,
        "next_action":("KEEP" if first=="NONE" else "TEST_NEXT"),
        "promotion_authority":False,"new_model_weights_applied":False,"learning_state":"N_PLUS_1_OBSERVATION",
    }
    learning["sha256"]=canonical_sha(learning)
    return {"result_evaluation":bound,"settlement":report,"learning":learning}


def fetch_jra_result(race_date: str, meeting_key: str, race_no: int) -> dict:
    opener, referer, day_html, key, d = _open_day(race_date, meeting_key)
    needle="pw01sde01"+key+f"{int(race_no):02d}"+d
    m=re.search(r"("+re.escape(needle)+r"/[0-9A-Fa-f]{2})",day_html)
    if not m:
        raise PendingOfficialResult("JRA_OFFICIAL_RESULT_RACE_NOT_PUBLISHED")
    fetched=utcnow()
    url,raw,headers=_post(opener,m.group(1),referer)
    parsed=parse_result_detail(raw,headers.get("content-type",""))
    return {"parsed":parsed,"text":_html_text(_decode(raw,headers.get("content-type",""))),
            "sha256":hashlib.sha256(raw).hexdigest(),"captured_at":fetched,
            "url":url, "source_authority":"JRA_OFFICIAL_POST_RESULT"}


def process(root:Path, race_id:str)->str:
    race_dir=root/"runtime"/"source_candidate_oos"/race_id
    result_path=race_dir/"result_evaluation.json"
    if result_path.exists(): return "ALREADY_SETTLED"
    pre_path=race_dir/"pre_result.json"; final_path=race_dir/"candidate_final.json"
    if not pre_path.exists() or not final_path.exists(): return "PRE_RESULT_NOT_FROZEN"
    pre=json.loads(pre_path.read_text(encoding="utf-8"))
    final=json.loads(final_path.read_text(encoding="utf-8"))
    _verified_pre_frozen(pre,final,race_id)
    post=datetime.fromisoformat(str(pre["scheduled_post_at"]).replace("Z","+00:00"))
    if datetime.now(timezone.utc)<=post+timedelta(minutes=1): return "RESULT_NOT_YET_DUE"
    # Repo commit identity is independent of in-file timestamps.
    import subprocess
    rel=pre_path.relative_to(root).as_posix()
    commit_time=subprocess.check_output(["git","log","-1","--format=%cI","--",rel],
                                       cwd=root,text=True).strip()
    if not commit_time or datetime.fromisoformat(commit_time)>=post:
        raise ValueError("NO_PRE_START_GIT_COMMIT_WITNESS")
    intent_path=root/"runtime"/"jra_formal_intents"/(race_id+"-LIVE-R1.json")
    if not intent_path.exists(): return "JRA_FORMAL_INTENT_MISSING"
    intent=json.loads(intent_path.read_text(encoding="utf-8"))
    if intent.get("race_id")!=race_id or intent.get("venue_id") not in {"KYO","TKY","NKY","HSN","CKY","NGT","FKU","KOK","SAP","HAK"}:
        raise ValueError("INTENT_RACE_OR_VENUE_MISMATCH")
    meeting_key=(intent.get("jra_source") or {}).get("jra_meeting_key")
    evidence=fetch_jra_result(intent["race_date"],meeting_key,int(intent["race_no"]))
    outcome=verify_official_result(evidence["parsed"],evidence["text"],pre["ranking"])
    artifacts=settle_frozen_candidate(pre,final,outcome,source_sha256=evidence["sha256"],source_url=evidence["url"])
    source_meta={"profile":PROFILE,"race_id":race_id,"status":"OFFICIAL_POST_RESULT_SNAPSHOT",
                 "raw_sha256":evidence["sha256"],"captured_at":evidence["captured_at"],
                 "url":evidence["url"],"result_top3":outcome["top3"],
                 "payouts":outcome["payouts"],"signed_result_receipt_verified":False}
    artifacts["official_result_observation"]=source_meta
    for key,obj in artifacts.items():
        p=race_dir/(key+".json")
        if p.exists():raise ValueError("RESULT_IMMUTABILITY_VIOLATION:"+key)
        p.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return "SETTLED_RECOMMENDATION"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",default=".")
    p.add_argument("--race-id")
    p.add_argument("--days",type=int,default=3)
    args=p.parse_args()
    if args.days < 1 or args.days>14:raise SystemExit("INVALID_DAYS_RANGE")
    root=Path(args.repo_root).resolve()
    dirs=[root/"runtime"/"source_candidate_oos"/args.race_id] if args.race_id else sorted(
        (root/"runtime"/"source_candidate_oos").glob("KM-JRA-*-R??"))
    today=datetime.now(timezone.utc)
    results=[]
    for d in dirs:
        pre=d/"pre_result.json"
        if not pre.exists():continue
        try:
            x=json.loads(pre.read_text(encoding="utf-8"))
            post=datetime.fromisoformat(str(x["scheduled_post_at"]).replace("Z","+00:00"))
            if not args.race_id and not (0 <= (today-post).total_seconds() <= args.days*86400):
                continue
            status=process(root,d.name)
        except PendingOfficialResult as exc:
            status="PENDING:"+str(exc)
        except Exception as exc:
            status="BLOCKED:"+type(exc).__name__+":"+str(exc)
        results.append({"race_id":d.name,"status":status})
    print(json.dumps({"profile":PROFILE,"processed":results},ensure_ascii=False))
    if args.race_id and results and results[0]["status"].startswith("BLOCKED:"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
