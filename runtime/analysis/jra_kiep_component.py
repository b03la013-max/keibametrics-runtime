"""KIEP-JRA (KeibaMetrics Index Evolution Program, 中央版) - actual-consumer ablation, record only.

Owner request 2026-11-26 21:43 (ChatGPT KIEP v1.0, 中央版 part, 「永続的に実施してください」).
Production effect NONE. Known-result context only: nothing here is a forward result or a promotion.

Uses the real Production consumer (jra_evidence_to_base_production._weighted_index on the frozen
FORMAL request, then ZAI_WIN of the race's formula version), not an equal-weight proxy:
  * FEATURE ablation (KIEP-03): drop one evidence feature from every runner; each base index re-weights
    its remaining inputs exactly as Production does for a missing input.
  * INDEX ablation (KIEP-06): drop one base index from ZAI_WIN, remaining weights rescaled to sum 1.
Metric: paired top-3 mean rank and winner rank (ablated - Production; negative = removing it helps,
so the component is hurting), with a normal 95% interval, overall and by surface.

  python runtime/analysis/jra_kiep_component.py ablate --since 20261115
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime")); sys.path.insert(0, str(ROOT / "runtime/analysis"))
import jra_evidence_to_base_production as P  # noqa: E402
import jra_index_provenance_builder as B  # noqa: E402
import jra_feature_challenger as FC  # noqa: E402

OUT = ROOT / "runtime/jra_kiep"
PROFILE = "KM-JRA-KIEP-ABLATION-v1"


def _vals(req, mapping, drop_feature=None):
    out = {}
    for r in req["runners"]:
        feats = dict(r.get("evidence_features") or {})
        feats.pop(drop_feature, None)
        prof = P._profile_for_runner(r)
        out[str(r["runner_id"])] = {idx: P._weighted_index(idx, prof, feats, mapping,
                                    acquisition_failure=r.get("bvi_acquisition_failure") if idx == "BVI" else None)["value"]
                                    for idx in B.BASE}
    return out


def _rank(vals, weights):
    z = {k: B._weighted_left_sum(v, weights) for k, v in vals.items()}
    return sorted(z, key=lambda k: (-z[k], int(k) if k.isdigit() else k))


def _score(rk, top3):
    return (sum(rk.index(x) + 1 for x in top3 if x in rk) / 3, rk.index(top3[0]) + 1 if top3[0] in rk else len(rk))


def _ci(d):
    n = len(d)
    if n < 2:
        return {"n": n}
    m = sum(d) / n
    sd = (sum((x - m) ** 2 for x in d) / (n - 1)) ** 0.5
    return {"n": n, "mean": round(m, 4), "ci95": [round(m - 1.96 * sd / n ** .5, 4), round(m + 1.96 * sd / n ** .5, 4)]}


def ablate(since):
    mapping = FC._mapping()
    races = []
    for p in sorted(glob.glob(str(ROOT / "runtime/requests/KM-JRA-*-LIVE-R1-FORMAL.json"))):
        rid = Path(p).name.replace("-LIVE-R1-FORMAL.json", "")
        if re.search(r"-(\d{8})-R", rid).group(1) < since:
            continue
        t = FC._top3(rid)
        if not t:
            continue
        req = json.loads(Path(p).read_text())
        races.append((rid, req, [str(x) for x in t]))
    feats = sorted({f for _, q, _ in races for r in q["runners"] for f in (r.get("evidence_features") or {})})
    res = {"FEATURE": {f: {"top3": [], "win": [], "surface": {}} for f in feats},
           "INDEX": {i: {"top3": [], "win": [], "surface": {}} for i in B.BASE}}
    for rid, req, top3 in races:
        ver = B.zai_formula_version(rid)
        w = B.ZAI_WIN_WEIGHTS[ver]
        base_vals = _vals(req, mapping)
        b3, bw = _score(_rank(base_vals, w), top3)
        surf = str((req.get("race") or req.get("race_context") or {}).get("surface") or req.get("surface") or "UNKNOWN")
        present = {f for r in req["runners"] for f in (r.get("evidence_features") or {})}
        for f in feats:
            if f not in present:
                continue
            a3, aw = _score(_rank(_vals(req, mapping, f), w), top3)
            e = res["FEATURE"][f]; e["top3"].append(a3 - b3); e["win"].append(aw - bw)
            e["surface"].setdefault(surf, []).append(a3 - b3)
        for i in B.BASE:
            if not w.get(i):
                continue
            ww = {k: v / (1 - w[i]) for k, v in w.items() if k != i}
            a3, aw = _score(_rank(base_vals, ww), top3)
            e = res["INDEX"][i]; e["top3"].append(a3 - b3); e["win"].append(aw - bw)
            e["surface"].setdefault(surf, []).append(a3 - b3)
    out = {"profile": PROFILE, "kind": "KNOWN_RESULT_CONTEXT_ONLY", "production_effect": "NONE", "since": since,
           "races": len(races), "metric": "ablated - Production (negative = removing helps)"}
    for kind in ("FEATURE", "INDEX"):
        out[kind] = {k: {"top3_mean_rank": _ci(v["top3"]), "winner_rank": _ci(v["win"]),
                         "by_surface": {s: _ci(x) for s, x in v["surface"].items()}}
                     for k, v in res[kind].items() if v["top3"]}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"ablation_since_{since}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("ablate"); a.add_argument("--since", default="20261115")
    x = ap.parse_args()
    o = ablate(x.since)
    print(json.dumps({"races": o["races"], "features": len(o["FEATURE"]), "indices": len(o["INDEX"])}))


if __name__ == "__main__":
    main()
