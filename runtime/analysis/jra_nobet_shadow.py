"""JRA PAPER / NO-BET classification and shadow tickets (Owner 2026-11-22 21:43). Record only.

Separates "could not predict" from "predicted but chose not to bet", and scores the skip decisions.
Classes per race (from the race-day status, the signed FINAL and the no-bet terminal):
  BET                 FINAL with tickets
  PAPER_POLICY        FINAL exists, no tickets, held by an unvalidated policy gate
                      (e.g. NEWCOMER_ROLE_POLICY_UNVALIDATED) -> system not ready yet (to be resolved)
  SELECTIVE_RULE      evaluated, then not bet by an evidence rule (AKI_* support rules, e.g.
                      AKI_SINGLE_HEAD_FORBIDDEN) -> keep, but score whether the skip was right
  TECHNICAL           no prediction because of SOURCE / cutoff / pipeline problems -> P0
  OTHER_NO_BET        any other no-bet reason (listed so nothing is hidden)
Metrics: prediction completion rate, technical no-bet rate, selective no-bet rate,
policy-hold rate, bet coverage, recommendation PFS.
Shadow tickets (frozen before post, never delivered or bought):
  PAPER_POLICY   the Production MEC on the frozen FINAL's W/P2/P3 (build_mec_plan)
  SELECTIVE_RULE a fixed reference shape from the frozen AKI columns, Static order filling
                 empty columns: EXACTA W x P2, TRIO W x P2 x P3 (W <= 2, P2 <= 4, P3 <= 6)
Settlement uses Production settle_final at official payouts when runtime/results/<race>.json
exists; otherwise PENDING_PAYOUT (no payouts are guessed).

  python3 runtime/analysis/jra_nobet_shadow.py classify <date>
  python3 runtime/analysis/jra_nobet_shadow.py freeze <date>     # before post only
  python3 runtime/analysis/jra_nobet_shadow.py replay <date>     # known results, context only
  python3 runtime/analysis/jra_nobet_shadow.py evaluate [--replay]
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "runtime"), str(ROOT / "runtime/jra_source_runtime"), str(ROOT / "runtime/analysis")]
from minimum_efficient_coverage import build_mec_plan  # noqa: E402
from jra_production_postresult import settle_final  # noqa: E402
import jra_role_candidate_replay as R  # noqa: E402

PROFILE = "KM-JRA-NOBET-SHADOW-v1"
OUT = ROOT / "runtime/jra_nobet_shadow"
TECHNICAL_STATES = ("SOURCE_FAILED", "MISSED", "CUTOFF", "ERROR", "BLOCKED", "SCOPE_HOLD")


def sha(o):
    return hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _status(date):
    p = ROOT / f"runtime/jra_race_day_status/{date}.json"
    return json.loads(p.read_text()) if p.exists() else None


def _final(rid):
    p = ROOT / f"runtime/final_artifacts/{rid}.json"
    return json.loads(p.read_text()) if p.exists() else None


def _paper_reason(final):
    reasons = []
    for d in ((final.get("final_ticket") or {}).get("bet_type_dispositions") or {}).values() \
            if isinstance((final.get("final_ticket") or {}).get("bet_type_dispositions"), dict) else \
            ((final.get("final_ticket") or {}).get("bet_type_dispositions") or []):
        r = (d or {}).get("reason") if isinstance(d, dict) else None
        if r:
            reasons.append(str(r))
    return sorted(set(reasons))


def classify_race(r):
    rid, state = r["race_id"], str(r.get("state") or "")
    final = _final(rid)
    if final and ((final.get("final_ticket") or {}).get("tickets")):
        return {"race_id": rid, "class": "BET", "state": state}
    if final:
        reasons = _paper_reason(final)
        cls = "PAPER_POLICY" if any("UNVALIDATED" in x or "POLICY" in x for x in reasons) else "OTHER_NO_BET"
        return {"race_id": rid, "class": cls, "state": state, "reasons": reasons}
    reason = str(r.get("decision_reason") or (r.get("aki_selection_failure") or {}).get("code") or "")
    if state == "AKI_NO_BET" or reason.startswith("AKI_"):
        return {"race_id": rid, "class": "SELECTIVE_RULE", "state": state, "reasons": [reason]}
    if any(x in state for x in TECHNICAL_STATES) or r.get("execution_error"):
        return {"race_id": rid, "class": "TECHNICAL", "state": state,
                "reasons": [str(r.get("first_blocked_stage") or r.get("execution_error") or state)]}
    return {"race_id": rid, "class": "PENDING" if state in ("WAITING", "DISPATCHED_RUNNING") else "OTHER_NO_BET",
            "state": state, "reasons": [reason] if reason else []}


def metrics(classes):
    n = len(classes)
    c = {k: sum(1 for x in classes if x["class"] == k) for k in
         ("BET", "PAPER_POLICY", "SELECTIVE_RULE", "TECHNICAL", "OTHER_NO_BET", "PENDING")}
    pct = lambda k: round(100 * k / n, 1) if n else None
    return {"races": n, "counts": c,
            "prediction_completion_pct": pct(n - c["TECHNICAL"] - c["PENDING"]),
            "technical_no_bet_pct": pct(c["TECHNICAL"]),
            "policy_hold_pct": pct(c["PAPER_POLICY"]),
            "selective_no_bet_pct": pct(c["SELECTIVE_RULE"]),
            "bet_coverage_pct": pct(c["BET"])}


def cmd_classify(a):
    st = _status(a.date)
    if not st:
        print(json.dumps({"date": a.date, "status": "NO_RACE_DAY_STATUS"}))
        return
    classes = [classify_race(r) for r in st["races"]]
    out = {"profile": PROFILE, "date": a.date, "metrics": metrics(classes), "races": classes}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"classes_{a.date}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps(out["metrics"], ensure_ascii=False))


def _static_order(rid):
    p = ROOT / f"runtime/requests/{rid}-LIVE-R1-FORMAL.json"
    if not p.exists():
        return []
    rk = ((json.loads(p.read_text()).get("static_prediction") or {}).get("ranking")) or []
    return [str(x.get("runner_id", x)) if isinstance(x, dict) else str(x) for x in rk]


def _fill(col, order, n):
    out = [str(x) for x in col][:n]
    for x in order:
        if len(out) >= n:
            break
        if x not in out:
            out.append(x)
    return out


def reference_tickets(columns, order):
    """Fixed reference shape for SELECTIVE_RULE skips (not a Production rule)."""
    w = _fill(columns.get("W") or [], order, 2)
    p2 = _fill(list(dict.fromkeys((columns.get("P2") or []) + w)), order, 4)
    p3 = _fill(list(dict.fromkeys((columns.get("P3") or []) + p2)), order, 6)
    tk = []
    for h in w:
        for s in p2:
            if s != h:
                tk.append({"bet_type": "EXACTA", "selection": [int(h), int(s)], "stake": 100})
    trios = set()
    for h in w:
        for s in p2:
            for t in p3:
                if len({h, s, t}) == 3:
                    trios.add(tuple(sorted((int(h), int(s), int(t)))))
    tk += [{"bet_type": "TRIO", "selection": list(t), "stake": 100} for t in sorted(trios)]
    return {"W": w, "P2": p2, "P3": p3}, tk


def shadow_for(c, r):
    rid = c["race_id"]
    if c["class"] == "PAPER_POLICY":
        final = _final(rid)
        mec = build_mec_plan(final)
        return {"source": "PRODUCTION_MEC_ON_FROZEN_ROLES", "roles": {k: R._live(final, k) for k in ("W", "P2", "P3")},
                "tickets": mec["tickets"], "investment": mec["minimum_required_capital"]}
    if c["class"] == "SELECTIVE_RULE":
        cols = ((r.get("aki_selection_failure") or {}).get("columns")) or {}
        roles, tk = reference_tickets(cols, _static_order(rid))
        return {"source": "REFERENCE_SHAPE_FROM_FROZEN_AKI_COLUMNS", "roles": roles, "tickets": tk,
                "investment": 100 * len(tk)}
    return None


def cmd_freeze(a, replay=False):
    st = _status(a.date)
    if not st:
        print(json.dumps({"frozen": 0, "status": "NO_RACE_DAY_STATUS"}))
        return
    now = dt.datetime.now(dt.timezone.utc)
    n, errors = 0, []
    for r in st["races"]:
        c = classify_race(r)
        if c["class"] not in ("PAPER_POLICY", "SELECTIVE_RULE"):
            continue
        dst = OUT / ("replay" if replay else "forward") / c["race_id"] / "pre_result.json"
        if not replay:
            post = r.get("post")
            if dst.exists() or not post or now >= dt.datetime.fromisoformat(post):
                continue
        try:
            sh = shadow_for(c, r)
        except Exception as e:  # recorded, never silent (A4)
            errors.append({"race_id": c["race_id"], "error": str(e)[:200]})
            continue
        body = {"profile": PROFILE, "race_id": c["race_id"], "class": c["class"], "reasons": c.get("reasons"),
                "kind": "KNOWN_RESULT_REPLAY_CONTEXT_ONLY" if replay else "FORWARD_PRE_RESULT",
                "post": r.get("post"), "frozen_at": now.isoformat(), "production_effect": "NONE", "shadow": sh}
        body["sha256"] = sha(body)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(body, ensure_ascii=False, indent=1))
        n += 1
    print(json.dumps({"frozen": n, "a4_errors": errors}, ensure_ascii=False))
    if errors:
        print(f"A4 ERROR {len(errors)}")


def cmd_evaluate(a):
    kind = "replay" if a.replay else "forward"
    rows = []
    for p in sorted(glob.glob(str(OUT / kind / "*/pre_result.json"))):
        d = json.loads(Path(p).read_text())
        rp = ROOT / f"runtime/results/{d['race_id']}.json"
        row = {"race_id": d["race_id"], "class": d["class"], "investment": d["shadow"]["investment"]}
        if rp.exists():
            off = json.loads(rp.read_text())["official_result"]
            tk = d["shadow"]["tickets"]
            s = settle_final({"final_ticket": {"tickets": tk, "total_investment": sum(int(t.get("stake", 100)) for t in tk)}}, off)
            row.update({"settled": True, "investment": s.get("effective_investment", s.get("total_investment", 0)) or 0,
                        "payout": s.get("total_payout", 0) or 0})
        else:
            row.update({"settled": False, "status": "PENDING_PAYOUT"})
        rows.append(row)
    summ = {"kind": kind}
    for cls in ("PAPER_POLICY", "SELECTIVE_RULE"):
        s = [r for r in rows if r["class"] == cls and r.get("settled")]
        inv, pay = sum(r["investment"] for r in s), sum(r["payout"] for r in s)
        summ[cls] = {"races": sum(1 for r in rows if r["class"] == cls), "settled": len(s),
                     "pending_payout": sum(1 for r in rows if r["class"] == cls and not r.get("settled")),
                     "shadow_investment": inv, "shadow_payout": pay,
                     "shadow_pfs_pct": round(100 * pay / inv, 1) if inv else None,
                     "loss_avoided_yen": inv - pay}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"evaluation_{kind}.json").write_text(json.dumps({"summary": summ, "rows": rows}, ensure_ascii=False, indent=1))
    print(json.dumps(summ, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("classify", "freeze", "replay"):
        sub.add_parser(c).add_argument("date")
    sub.add_parser("evaluate").add_argument("--replay", action="store_true")
    a = ap.parse_args()
    if a.cmd == "classify":
        cmd_classify(a)
    elif a.cmd == "freeze":
        cmd_freeze(a)
    elif a.cmd == "replay":
        cmd_freeze(a, replay=True)
    else:
        cmd_evaluate(a)


if __name__ == "__main__":
    main()
