"""JRA conversion-stage Challengers (情報→点数の変換). Research / record only.

Task 2026-11-21 20:16 (ChatGPT proposal handled as research): find the weakest stage and add at
most two conversion challengers. Both were fixed from the TRAIN window only
(2026-10-11 .. 2026-11-09, 3,158 runners, known results) and are evaluated on later races:
  CV1_SIGN_FIX   drop the features whose category score correlates <= 0 with a top-3 finish in
                 the train window (market_mismatch -0.146, opponent_strength -0.048,
                 weight_load_fit -0.007). They become unobserved (Production rules for
                 unobserved features apply unchanged).
  CV2_ISO_SCALE  replace the shared category scale with the train-window empirical top-3
                 log-odds per category, rescaled linearly to the same 24..94 range.
  MARKET_BLIND   (ChatGPT 11/25 gap plan, Owner approval 2026-11-25 21:5x) "予想ファースト・オッズセカンド":
                 ZAI_WIN v1.1 without the market index VMI, the other weights rescaled by 1/0.95 so
                 their ratios are kept. v1.0 races have no VMI weight, so the arm equals PROD there.
                 Replays and freezes also record MARKET_VMI, the runners ordered by the pre-race
                 market index VMI alone (a market baseline the arm is compared against, not an arm).
Ranking = ZAI_WIN (Production composite), so only the conversion stage differs.
Metrics: paired top-3 mean rank, winner rank, top-3 capture inside the top 5 (same candidate
count for every arm). No arm outputs probabilities, so Brier / LogLoss are not applicable.

  python3 runtime/analysis/jra_conversion_challenger.py replay --since 20261110   # known results, context only
  python3 runtime/analysis/jra_conversion_challenger.py freeze <date>              # before post time only
"""
from __future__ import annotations

import argparse
import copy
import glob
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(ROOT / "runtime/analysis"))
import jra_evidence_to_base_production as P  # noqa: E402
import jra_index_provenance_builder as B  # noqa: E402
import jra_feature_challenger as FC  # noqa: E402

PROFILE = "KM-JRA-CONVERSION-CHALLENGER-v1"
OUT = ROOT / "runtime/jra_conversion_challenger"
TRAIN = ("20261011", "20261109")
CV1_DROP = ["market_mismatch", "opponent_strength", "weight_load_fit"]
CV2_SCALE = {"EXCEPTIONAL": 94.0, "VERY_STRONG": 85.1, "STRONG": 78.0, "POSITIVE": 73.4, "NEUTRAL": 68.0,
             "MIXED": 62.8, "CAUTION": 61.7, "WEAK": 44.8, "VERY_WEAK": 24.0}
ARMS = ["PROD", "CV1_SIGN_FIX", "CV2_ISO_SCALE", "MARKET_BLIND"]
BASELINES = ["MARKET_VMI"]


def _market_blind_weights(ver):
    w = dict(B.ZAI_WIN_WEIGHTS[ver])
    vmi = w.pop("VMI", 0.0)
    return {k: v / (1.0 - vmi) for k, v in w.items()} if vmi else w


def ranking(req, mapping, arm):
    m = mapping
    if arm == "CV2_ISO_SCALE":
        m = copy.deepcopy(mapping)
        m["category_scale"] = dict(CV2_SCALE)
    ver = B.zai_formula_version(req["race_id"])
    z = {}
    for r in req["runners"]:
        feats = r.get("evidence_features") or {}
        if arm == "CV1_SIGN_FIX":
            feats = {k: v for k, v in feats.items() if k not in CV1_DROP}
        prof = P._profile_for_runner(r)
        vals = {idx: P._weighted_index(idx, prof, feats, m,
                                       acquisition_failure=r.get("bvi_acquisition_failure") if idx == "BVI" else None)["value"]
                for idx in B.BASE}
        if arm == "MARKET_VMI":
            z[str(r["runner_id"])] = vals["VMI"]
        elif arm == "MARKET_BLIND":
            z[str(r["runner_id"])] = B._weighted_left_sum(vals, _market_blind_weights(ver))
        else:
            z[str(r["runner_id"])] = B.zai_win_value(vals, ver)
    return sorted(z, key=lambda k: (-z[k], int(k) if k.isdigit() else k))


def race(rid, mapping):
    p = ROOT / f"runtime/requests/{rid}-LIVE-R1-FORMAL.json"
    if not p.exists():
        return None
    req = json.loads(p.read_text())
    out = {"race_id": rid, "rankings": {a: ranking(req, mapping, a) for a in ARMS + BASELINES},
           "source_request_sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
    frozen = [str(x) for x in ((req.get("static_prediction") or {}).get("ranking") or [])]
    out["prod_replay_matches_frozen"] = (not frozen) or frozen == out["rankings"]["PROD"]
    return out


def score(row, top3):
    res = {}
    for a in ARMS + BASELINES:
        rk = row["rankings"][a]
        res[a] = {"top3_mean_rank": sum(rk.index(x) + 1 for x in top3 if x in rk) / 3,
                  "winner_rank": rk.index(top3[0]) + 1 if top3[0] in rk else None,
                  "top3_in_top5": sum(1 for x in top3 if x in rk[:5])}
    return res


def cmd_replay(a, mapping):
    rows = []
    for p in sorted(glob.glob(str(ROOT / "runtime/requests/KM-JRA-*-LIVE-R1-FORMAL.json"))):
        rid = Path(p).name.replace("-LIVE-R1-FORMAL.json", "")
        d8 = re.search(r"-(\d{8})-R", rid).group(1)
        if d8 < a.since:
            continue
        t = FC._top3(rid)
        if not t:
            continue
        r = race(rid, mapping)
        if r:
            r["metrics"] = score(r, t)
            rows.append(r)
    n = len(rows)
    summ = {"kind": "KNOWN_RESULT_REPLAY_CONTEXT_ONLY", "since": a.since, "races": n,
            "prod_replay_mismatch": sum(1 for r in rows if not r["prod_replay_matches_frozen"])}
    for arm in ARMS + BASELINES:
        summ[arm] = {"top3_mean_rank": round(sum(r["metrics"][arm]["top3_mean_rank"] for r in rows) / max(1, n), 3),
                     "winner_mean_rank": round(sum(r["metrics"][arm]["winner_rank"] or 0 for r in rows) / max(1, n), 3),
                     "top3_in_top5_pct": round(100 * sum(r["metrics"][arm]["top3_in_top5"] for r in rows) / max(1, 3 * n), 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"replay_since_{a.since}.json").write_text(json.dumps({"summary": summ, "rows": rows}, ensure_ascii=False, indent=1))
    print(json.dumps(summ, ensure_ascii=False, indent=1))


def cmd_freeze(a, mapping):
    posts, now, n = FC.post_times(a.date), datetime.now(FC.JST), 0
    for p in sorted(glob.glob(str(ROOT / f"runtime/requests/KM-JRA-*-{a.date.replace('-', '')}-R*-LIVE-R1-FORMAL.json"))):
        rid = Path(p).name.replace("-LIVE-R1-FORMAL.json", "")
        post = posts.get(rid)
        dst = OUT / "forward" / rid / "pre_result.json"
        if not post or dst.exists():
            continue
        hh, mm = map(int, post.split(":"))
        if now >= now.replace(hour=hh, minute=mm, second=0, microsecond=0):
            continue
        r = race(rid, mapping)
        if not r:
            continue
        r.update({"profile": PROFILE, "frozen_at": now.isoformat(), "post_time": post})
        r["sha256"] = FC.sha(r)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(r, ensure_ascii=False, indent=1))
        n += 1
    print(json.dumps({"frozen": n}))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("replay"); s.add_argument("--since", default="20261110")
    s = sub.add_parser("freeze"); s.add_argument("date")
    a = ap.parse_args()
    mapping = FC._mapping()
    {"replay": cmd_replay, "freeze": cmd_freeze}[a.cmd](a, mapping)


if __name__ == "__main__":
    main()
