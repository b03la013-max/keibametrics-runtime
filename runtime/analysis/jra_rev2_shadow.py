"""JRA T-10 pre-post re-check (Revision 2), RECORD ONLY.

Owner approval 2026-11-21 10:19 (implementation from 11/26; record only from the 11/28 card).
Production effect NONE: Revision 1 (the signed FINAL) stays the only delivered and settled version.
Nothing here is delivered, signed as Production, or read by Role, MEC, Capital or Delivery.

At post-12..post-0 minutes, for every race with a signed FINAL (Revision 1), the JRA official
開催お知らせ (runtime/jra_official_daily/<date>.json, refreshed with force=True by the race-day loop
just before this check) is compared with Revision 1:
  * 出走取消 / 競走除外 of a Revision-1 runner  -> material; Revision 2 = Revision 1 minus the
    withdrawn runners (ranking, roles and tickets; JRA refunds tickets that contain them), budget
    not reallocated. This is the lightweight recompute; no MEC re-run, no KRS.
  * 騎手変更 / 発走時刻変更 -> recorded, not material (no index here reads them after FINAL).
  * body weight / odds at T-10 -> NOT OBSERVED by this version (needs an official odds / 馬体重
    reader; recorded as such so the audit never claims it).
Revision 1 is never modified. Output: runtime/jra_rev2_shadow/<date>/<race_id>.json (one per race,
written once, at the first check inside the window).

  python runtime/analysis/jra_rev2_shadow.py check 2026-11-28 [--now ISO]
  python runtime/analysis/jra_rev2_shadow.py audit 2026-11-28
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
OUT = ROOT / "runtime/jra_rev2_shadow"
PROFILE = "KM-JRA-REV2-SHADOW-v1"
JST = dt.timezone(dt.timedelta(hours=9))
WINDOW_MIN = 12
NAME = {"札幌": "SPP", "函館": "HKD", "福島": "FKS", "新潟": "NGT", "東京": "TKY", "中山": "NKY",
        "中京": "CHK", "京都": "KYO", "阪神": "HSN", "小倉": "KKR"}
WITHDRAW = ("出走取消", "競走除外")


def _j(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return None


def _sha(o):
    return hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def schedule(date):
    st = _j(ROOT / f"runtime/jra_race_day_status/{date}.json") or {}
    races = st.get("races") or []
    races = races if isinstance(races, list) else list(races.values())
    return {r["race_id"]: r.get("post") for r in races if r.get("race_id") and r.get("post")}


def notices_for(date, race_id):
    """(observed_at, [notice]) from the latest official observation for this race, or (None, None)."""
    doc = _j(ROOT / f"runtime/jra_official_daily/{date}.json") or {}
    obs = [o for o in doc.get("observations") or [] if o.get("notices")]
    if not obs:
        return None, None
    last = obs[-1]
    venue, rno = race_id.split("-")[2], str(int(race_id.rsplit("-R", 1)[1]))
    for m in last["notices"].get("meetings") or []:
        name = re.sub(r"^\d+回|\d+日$", "", m.get("meeting") or "")
        if NAME.get(name) == venue:
            return last.get("last_seen_at") or last.get("observed_at"), list((m.get("races") or {}).get(rno) or [])
    return last.get("last_seen_at") or last.get("observed_at"), []


def build(race_id, final, observed_at, notices, now):
    fp = final.get("final_prediction_package") or {}
    ranking = [str(x) for x in fp.get("ranking") or []]
    roles = {str(k): list(v) for k, v in (fp.get("roles") or {}).items()}
    tickets = list((final.get("final_ticket") or {}).get("tickets") or [])
    withdrawn = sorted({int(n["horse_no"]) for n in notices or []
                        if n.get("type") in WITHDRAW and isinstance(n.get("horse_no"), int)
                        and str(n["horse_no"]) in ranking})
    other = [n for n in notices or [] if n.get("type") not in WITHDRAW]
    rec = {"profile": PROFILE, "race_id": race_id, "record_only": True, "production_effect": "NONE",
           "checked_at": now.isoformat(timespec="seconds"), "post": final.get("scheduled_post_at"),
           "rev1_final_sha256": final.get("sha256"), "rev1_frozen_at": (final.get("final_ticket") or {}).get("frozen_at"),
           "official_notices_observed_at": observed_at, "notices": notices,
           "withdrawn": withdrawn, "other_changes": other,
           "body_weight_odds": "NOT_OBSERVED_BY_V1",
           "material": bool(withdrawn)}
    if withdrawn:
        out = {str(x) for x in withdrawn}
        kept = [t for t in tickets if not out & {str(s) for s in t.get("selection") or []}]
        rec["rev2"] = {"method": "REV1_MINUS_WITHDRAWN_NO_REALLOCATION",
                       "ranking": [x for x in ranking if x not in out],
                       "roles": {k: v for k, v in roles.items() if k not in out},
                       "tickets": kept,
                       "removed_tickets": len(tickets) - len(kept),
                       "investment": sum(int(t.get("stake") or 0) for t in kept),
                       "rev1_investment": sum(int(t.get("stake") or 0) for t in tickets)}
    rec["sha256"] = _sha(rec)
    return rec


def check(date, now=None):
    now = now or dt.datetime.now(JST)
    done = []
    for rid, post in sorted(schedule(date).items()):
        try:
            p = dt.datetime.fromisoformat(post.replace("Z", "+00:00"))
        except ValueError:
            continue
        if not (p - dt.timedelta(minutes=WINDOW_MIN) <= now < p):
            continue
        dst = OUT / date / f"{rid}.json"
        final = _j(ROOT / f"runtime/final_artifacts/{rid}.json")
        if dst.exists() or not final or (final.get("final_ticket") or {}).get("no_bet"):
            continue
        observed_at, notices = notices_for(date, rid)
        if observed_at is None:
            continue  # no official observation yet; the next loop iteration retries inside the window
        rec = build(rid, final, observed_at, notices, now)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
        done.append({"race_id": rid, "material": rec["material"]})
    return done


def _settle(final, tickets, official):
    from jra_production_postresult import settle_final
    f = copy.deepcopy(final)
    f["final_ticket"]["tickets"] = tickets
    s = settle_final(f, official)
    return {k: s.get(k) for k in ("total_investment", "total_payout", "refund", "profit_loss", "pfs")}


def audit(date):
    rows = []
    for p in sorted((OUT / date).glob("KM-JRA-*.json")):
        rec = _j(p)
        res = _j(ROOT / f"runtime/results/{rec['race_id']}.json")
        final = _j(ROOT / f"runtime/final_artifacts/{rec['race_id']}.json")
        row = {"race_id": rec["race_id"], "material": rec["material"], "withdrawn": rec["withdrawn"]}
        if res and final and (res.get("official_result") or {}).get("top3"):
            off = res["official_result"]
            win = str(off["top3"][0])
            r1 = [str(x) for x in (final.get("final_prediction_package") or {}).get("ranking") or []]
            r2 = (rec.get("rev2") or {}).get("ranking") or r1
            roles1 = (final.get("final_prediction_package") or {}).get("roles") or {}
            roles2 = (rec.get("rev2") or {}).get("roles") or roles1
            row.update(winner=win, winner_rank_rev1=r1.index(win) + 1 if win in r1 else None,
                       winner_rank_rev2=r2.index(win) + 1 if win in r2 else None,
                       winner_in_w_rev1="W" in (roles1.get(win) or []), winner_in_w_rev2="W" in (roles2.get(win) or []))
            try:
                row["settle_rev1"] = _settle(final, (final.get("final_ticket") or {}).get("tickets") or [], off)
                if rec.get("rev2"):
                    row["settle_rev2"] = _settle(final, rec["rev2"]["tickets"], off)
            except Exception as e:  # noqa: BLE001 - audit only
                row["settle_error"] = str(e)[:200]
        rows.append(row)
    out = {"profile": PROFILE + "-AUDIT", "race_date": date, "record_only": True, "races": rows,
           "summary": {"checked": len(rows), "material": sum(r["material"] for r in rows)}}
    (OUT / date).mkdir(parents=True, exist_ok=True)
    (OUT / date / "audit.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("date"); c.add_argument("--now")
    a = sub.add_parser("audit"); a.add_argument("date")
    x = ap.parse_args()
    if x.cmd == "check":
        print(json.dumps(check(x.date, dt.datetime.fromisoformat(x.now) if x.now else None), ensure_ascii=False))
    else:
        print(json.dumps(audit(x.date)["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
