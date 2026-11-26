"""KSP-JRA (KeibaMetrics Survival Program, 中央版) - long-run risk of the frozen recommendations. Record only.

Owner request 2026-11-26 22:03 (ChatGPT KDP/KSP/KAP v1.0, 中央版 part, 「永続的に実施してください」).
Virtual settlement of the signed FINAL recommendation tickets (runtime/results/*.json settlement,
FROZEN-RECOMMENDATION-PFS). Actual purchases are UNVERIFIED and never inferred. Nothing here changes
a ticket, a budget or a capital rule.

PFS = total payout / effective investment (refunds excluded); races with zero effective investment
(NO_BET) are counted separately and never given a PFS.

  python runtime/analysis/jra_ksp_risk.py report [--since 20261011]
"""
from __future__ import annotations

import argparse
import glob
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runtime/jra_ksp"
PROFILE = "KM-JRA-KSP-RISK-v1"


def rows(since="00000000"):
    out = []
    for p in sorted(glob.glob(str(ROOT / "runtime/results/KM-JRA-*.json"))):
        rid = Path(p).stem
        m = re.search(r"-([A-Z]{3})-(\d{8})-R(\d+)$", rid)
        if not m or m.group(2) < since:
            continue
        try:
            s = json.loads(Path(p).read_text()).get("settlement") or {}
        except ValueError:
            continue
        if s.get("pfs_authority") != "FROZEN-RECOMMENDATION-PFS":
            continue
        inv = int(s.get("effective_investment") or 0)
        pay = int(s.get("total_payout") or 0)
        out.append({"race_id": rid, "venue": m.group(1), "date": m.group(2), "race_no": int(m.group(3)),
                    "investment": inv, "payout": pay, "no_bet": bool(s.get("no_bet")) or inv == 0})
    out.sort(key=lambda r: (r["date"], r["race_no"], r["venue"]))
    return out


def _pfs(rs):
    inv = sum(r["investment"] for r in rs)
    return round(100 * sum(r["payout"] for r in rs) / inv, 1) if inv else None


def metrics(rs):
    bet = [r for r in rs if not r["no_bet"]]
    if not bet:
        return {"races": len(rs), "bet_races": 0}
    cum = peak = 0
    mdd = dd_start = 0
    dur = longest_dur = 0
    streak = longest = 0
    for r in bet:
        cum += r["payout"] - r["investment"]
        if cum >= peak:
            peak, dur = cum, 0
        else:
            dur += 1
            longest_dur = max(longest_dur, dur)
        mdd = max(mdd, peak - cum)
        streak = streak + 1 if r["payout"] == 0 else 0
        longest = max(longest, streak)
    pays = sorted((r["payout"] for r in bet), reverse=True)
    inv = sum(r["investment"] for r in bet)
    hits = [r for r in bet if r["payout"] > 0]
    nets = sorted(r["payout"] - r["investment"] for r in bet)
    k = max(1, len(nets) // 20)
    days = sorted({r["date"] for r in bet})
    return {
        "races": len(rs), "bet_races": len(bet), "no_bet_races": len(rs) - len(bet),
        "investment": inv, "payout": sum(pays), "net": sum(pays) - inv, "pfs": _pfs(bet),
        "pfs_ex_top1": round(100 * sum(pays[1:]) / inv, 1), "pfs_ex_top3": round(100 * sum(pays[3:]) / inv, 1),
        "largest_win_share": round(pays[0] / sum(pays), 3) if sum(pays) else None,
        "hit_races": len(hits), "hit_rate": round(len(hits) / len(bet), 3),
        "hit_but_loss": sum(1 for r in hits if r["payout"] < r["investment"]),
        "max_drawdown_yen": mdd, "longest_drawdown_races": longest_dur, "longest_losing_streak": longest,
        "race_var95_yen": -nets[k - 1], "race_cvar95_yen": round(-sum(nets[:k]) / k),
        "days": len(days), "pfs_by_day": {d: _pfs([r for r in bet if r["date"] == d]) for d in days},
        "pfs_by_venue": {v: _pfs([r for r in bet if r["venue"] == v]) for v in sorted({r["venue"] for r in bet})},
    }


def block_bootstrap(rs, n=4000, seed=20261126):
    """Resample whole race days (dependence inside a card kept). Returns the PFS 2.5/50/97.5 percentiles."""
    bet = [r for r in rs if not r["no_bet"]]
    days = sorted({r["date"] for r in bet})
    by = {d: [r for r in bet if r["date"] == d] for d in days}
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        pick = [r for _ in days for r in by[rnd.choice(days)]]
        inv = sum(r["investment"] for r in pick)
        if inv:
            out.append(100 * sum(r["payout"] for r in pick) / inv)
    out.sort()
    q = lambda p: round(out[int(p * (len(out) - 1))], 1)
    return {"resamples": len(out), "unit": "race_day", "pfs_p2_5": q(.025), "pfs_p50": q(.5), "pfs_p97_5": q(.975),
            "share_above_100": round(sum(x >= 100 for x in out) / len(out), 3)}


def report(since):
    rs = rows(since)
    out = {"profile": PROFILE, "production_effect": "NONE", "actual_purchase": "UNVERIFIED", "since": since,
           "all": metrics(rs), "bootstrap": block_bootstrap(rs) if any(not r["no_bet"] for r in rs) else None}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "risk.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report"); r.add_argument("--since", default="20261011")
    a = ap.parse_args()
    o = report(a.since)
    m = o["all"]
    print(json.dumps({k: m.get(k) for k in ("bet_races", "pfs", "pfs_ex_top1", "net", "max_drawdown_yen", "longest_losing_streak")}
                     | {"bootstrap": o["bootstrap"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
