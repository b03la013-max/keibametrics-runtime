"""KCP-JRA (KeibaMetrics KRS Calibration Program, 中央版) - CAL-05 probability calibration, record only.

Owner approval 2026-11-26 19:4x (「登録してよい（推奨）」, ChatGPT KCP v1.0 plan, 中央版 part).
Production effect NONE: SSR-W stays an uncalibrated frequency; nothing here is read by Role, MEC,
Capital, FINAL or Delivery, and no EV / Kelly use is allowed.

Inputs are only frozen pre-race artefacts: the signed FINAL (krs_prediction_utility.summary, SSR-W per
runner, KRS-Engine v1.1.0, parameter_map 0.1-provisional) and, after the race, the stored official
result. The transform of a frozen FINAL with a constant fixed here is itself fixed before the race, so
the forward ledger needs no separate freeze step: any FINAL of a race on or after FIRST_ELIGIBLE is
forward out-of-sample by construction.

Arms (KCP v1.0 numbering):
  KCP-B1  identity        SSR-W as published (already normalised to 1 per race)
  KCP-C2  temperature     p_i proportional to SSR-W_i ** (1/T), T = T_FIXED, fitted on the race days
                          before FIT_CUT (209 races) and never refitted inside the evaluation
Baselines: UNIFORM (1/N).

  python runtime/analysis/jra_krs_calibration.py baseline      # known-result context report
  python runtime/analysis/jra_krs_calibration.py forward       # races >= FIRST_ELIGIBLE only
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runtime/jra_krs_calibration"
PROFILE = "KM-JRA-KCP-CAL05-v1"
T_FIXED = 2.65
FIT_CUT = "20261108"          # fit used race days 20261011..20261107 (209 races)
FIRST_ELIGIBLE = "20261128"
EPS = 1e-6


def races(since: str = "00000000", until: str = "99999999") -> list[dict]:
    out = []
    for p in sorted(glob.glob(str(ROOT / "runtime/final_artifacts/KM-JRA-*.json"))):
        rid = Path(p).stem
        m = re.search(r"-(\d{8})-R\d+$", rid)
        if not m or not since <= m.group(1) < until:
            continue
        rp = ROOT / f"runtime/results/{rid}.json"
        if not rp.exists():
            continue
        try:
            final = json.loads(Path(p).read_text())
            res = json.loads(rp.read_text()).get("official_result") or {}
        except (OSError, ValueError):
            continue
        top3 = [str(x) for x in (res.get("top3") or [])]
        util = final.get("krs_prediction_utility") or {}
        summ = util.get("summary") or []
        w = {str(x["horse_no"]): float(x["SSR-W"]) for x in summ if "SSR-W" in x}
        if len(top3) < 1 or not w or top3[0] not in w:
            continue
        eng = util.get("engine") or {}
        out.append({"race_id": rid, "date": m.group(1), "venue": rid.split("-")[2], "ssr_w": w, "winner": top3[0],
                    "parameter_map_version": eng.get("parameter_map_version"),
                    "final_sha256": hashlib.sha256(Path(p).read_bytes()).hexdigest()})
    return out


def probs(w: dict, arm: str) -> dict:
    if arm == "UNIFORM":
        return {k: 1.0 / len(w) for k in w}
    t = 1.0 if arm == "KCP-B1" else T_FIXED
    z = {k: max(v, EPS) ** (1.0 / t) for k, v in w.items()}
    s = sum(z.values())
    return {k: v / s for k, v in z.items()}


def metrics(rows: list[dict], arm: str) -> dict:
    if not rows:
        return {"races": 0}
    brier = ll = 0.0
    n = 0
    bins = [[0, 0.0, 0.0] for _ in range(10)]
    for r in rows:
        p = probs(r["ssr_w"], arm)
        for k, v in p.items():
            y = 1.0 if k == r["winner"] else 0.0
            brier += (v - y) ** 2
            n += 1
            b = bins[min(9, int(v * 10))]
            b[0] += 1; b[1] += v; b[2] += y
        ll += -math.log(max(p[r["winner"]], EPS))
    return {"races": len(rows), "brier": round(brier / n, 5), "logloss_per_race": round(ll / len(rows), 4),
            "ece": round(sum(abs(b[1] - b[2]) for b in bins) / n, 4),
            "reliability": [{"bin": f"{i/10:.1f}", "n": b[0], "mean_p": round(b[1] / b[0], 3),
                             "win_rate": round(b[2] / b[0], 3)} for i, b in enumerate(bins) if b[0]]}


def paired_logloss_diff(rows: list[dict], a: str, b: str) -> dict:
    d = [-math.log(max(probs(r["ssr_w"], a)[r["winner"]], EPS)) + math.log(max(probs(r["ssr_w"], b)[r["winner"]], EPS))
         for r in rows]
    if len(d) < 2:
        return {"races": len(d)}
    mean = sum(d) / len(d)
    sd = (sum((x - mean) ** 2 for x in d) / (len(d) - 1)) ** 0.5
    return {"races": len(d), "mean": round(mean, 4), "ci95": [round(mean - 1.96 * sd / len(d) ** 0.5, 4),
                                                              round(mean + 1.96 * sd / len(d) ** 0.5, 4)]}


def report(rows: list[dict], kind: str) -> dict:
    arms = ["KCP-B1", "KCP-C2", "UNIFORM"]
    return {"profile": PROFILE, "kind": kind, "production_effect": "NONE", "t_fixed": T_FIXED, "fit_cut": FIT_CUT,
            "first_eligible": FIRST_ELIGIBLE, "races": len(rows),
            "parameter_map_versions": sorted({str(r["parameter_map_version"]) for r in rows}),
            "arms": {a: metrics(rows, a) for a in arms},
            "paired_logloss_C2_minus_B1": paired_logloss_diff(rows, "KCP-C2", "KCP-B1"),
            "races_list": [{"race_id": r["race_id"], "final_sha256": r["final_sha256"]} for r in rows]}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("baseline")
    sub.add_parser("forward")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.cmd == "baseline":
        rows = races(until=FIRST_ELIGIBLE)
        out = report(rows, "KNOWN_RESULT_CONTEXT_ONLY")
        out["fit_window"] = report([r for r in rows if r["date"] < FIT_CUT], "FIT_WINDOW")["arms"]
        out["after_fit_window"] = report([r for r in rows if r["date"] >= FIT_CUT], "AFTER_FIT_CONTEXT")
        out["after_fit_window"].pop("races_list")
        (OUT / "baseline.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    else:
        out = report(races(since=FIRST_ELIGIBLE), "FORWARD_OOS")
        (OUT / "forward_summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("kind", "races", "paired_logloss_C2_minus_B1")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
