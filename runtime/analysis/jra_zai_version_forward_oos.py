"""ZAI v1.1 (Production) vs ZAI v1.0 (Shadow) forward OOS ledger.

freeze   : for every signed FINAL of a race date, recompute both rankings from the
           FINAL's own frozen pre-race base values (no network, no result input)
           and write runtime/jra_zai_forward_oos/<race_id>/pre_result.json bound to
           the FINAL sha256 and its freeze time. Existing freezes are never rewritten.
evaluate : after the official top3 exists (jra_static_owner_forward_oos/<race>/
           result_evaluation.json), write result_evaluation.json with paired
           metrics. Never edits pre_result.json.
summary  : paired aggregate over all evaluated races with a bootstrap 95% CI.

Production effect: NONE (read-only on FINALs; Shadow arm is never delivered).
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
from jra_index_provenance_builder import zai_formula_version, zai_win_value  # noqa: E402

OUT = "runtime/jra_zai_forward_oos"
PROFILE = "KM-JRA-ZAI-VERSION-FORWARD-OOS-v1"


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def _order(scores):
    return sorted(scores, key=lambda k: (-scores[k], int(k)))


def freeze_one(final_path: Path, root: Path) -> dict | None:
    raw = final_path.read_bytes()
    d = json.loads(raw)
    rid = d["race_id"]
    if zai_formula_version(rid) != "v1.1":
        return None
    out = root / OUT / rid / "pre_result.json"
    if out.exists():
        return json.loads(out.read_text())
    runners = d["final_prediction_package"]["index_provenance_replay"]["runners"]
    vals = {k: r["base_final_values"] for k, r in runners.items()}
    prod = {k: r["zai_win"] for k, r in runners.items()}
    v11 = {k: zai_win_value(v, "v1.1") for k, v in vals.items()}
    v10 = {k: zai_win_value(v, "v1.0") for k, v in vals.items()}
    if any(abs(prod[k] - v11[k]) > 1e-6 for k in prod):
        status = "PRODUCTION_FORMULA_MISMATCH"
    else:
        status = "PRODUCTION_IS_V1_1"
    body = {
        "profile": PROFILE, "race_id": rid, "production_formula_check": status,
        "final_file_sha256": hashlib.sha256(raw).hexdigest(),
        "final_freeze_timestamp": d.get("final_freeze_timestamp"),
        "scheduled_post_at": d.get("scheduled_post_at"),
        "frozen_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "inputs": "FINAL final_prediction_package.index_provenance_replay.runners[*].base_final_values (pre-race, signed)",
        "production_v1_1_ranking": _order(v11), "shadow_v1_0_ranking": _order(v10),
        "production_static_ranking": d["static_prediction"]["ranking"],
        "ranking_changed": _order(v11) != _order(v10),
        "production_effect": "NONE",
    }
    body["sha256"] = _sha(body)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(body, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return body


def _metrics(order, top3):
    rank = {h: i + 1 for i, h in enumerate(order)}
    rk = [rank.get(h, len(order) + 1) for h in top3]
    pair = order[:2] == top3[:2]
    return {"winner_rank": rk[0], "p2_rank": rk[1], "p3_rank": rk[2],
            "top3_mean_rank": sum(rk) / 3, "winner_in_top3": rk[0] <= 3,
            "top3_capture_in_top5": sum(r <= 5 for r in rk),
            "ordered_pair_top2": pair, "exact_triple_top3": order[:3] == top3}


def evaluate_one(race_dir: Path, root: Path) -> dict | None:
    pre = json.loads((race_dir / "pre_result.json").read_text())
    ev = root / "runtime/jra_static_owner_forward_oos" / pre["race_id"] / "result_evaluation.json"
    if not ev.exists():
        return None
    off = json.loads(ev.read_text())
    top3 = [str(x) for x in off["top3"]]
    observed = off.get("observed_at")
    body = {"profile": PROFILE, "race_id": pre["race_id"], "pre_result_sha256": pre["sha256"],
            "official_result_sha256": off.get("official_result_sha256"), "top3": top3,
            "result_observed_at": observed,
            "freeze_before_result": bool(observed) and pre["final_freeze_timestamp"] < observed,
            "production_v1_1": _metrics(pre["production_v1_1_ranking"], top3),
            "shadow_v1_0": _metrics(pre["shadow_v1_0_ranking"], top3),
            "production_effect": "NONE"}
    body["sha256"] = _sha(body)
    (race_dir / "result_evaluation.json").write_text(json.dumps(body, ensure_ascii=False, indent=1) + "\n",
                                                     encoding="utf-8")
    return body


def summary(root: Path) -> dict:
    rows = [json.loads(Path(p).read_text()) for p in
            sorted(glob.glob(str(root / OUT / "*" / "result_evaluation.json")))]
    rows = [r for r in rows if r.get("freeze_before_result")]
    if not rows:
        return {"races": 0}
    def mean(arm, k):
        return sum(float(r[arm][k]) for r in rows) / len(rows)
    diff = [r["production_v1_1"]["top3_mean_rank"] - r["shadow_v1_0"]["top3_mean_rank"] for r in rows]
    rnd = random.Random(1115)
    bs = sorted(sum(rnd.choice(diff) for _ in diff) / len(diff) for _ in range(4000))
    keys = ["winner_rank", "top3_mean_rank", "winner_in_top3", "top3_capture_in_top5",
            "ordered_pair_top2", "exact_triple_top3"]
    return {"races": len(rows),
            "production_v1_1": {k: mean("production_v1_1", k) for k in keys},
            "shadow_v1_0": {k: mean("shadow_v1_0", k) for k in keys},
            "paired_top3_mean_rank_diff": sum(diff) / len(diff),
            "paired_diff_ci95": [bs[100], bs[3899]],
            "checkpoint": next((c for c in (300, 100, 30) if len(rows) >= c), "PRE_30"),
            "note": "negative diff = v1.1 better; no significance claim below 100 races"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["freeze", "evaluate", "summary"])
    ap.add_argument("--date", help="YYYY-MM-DD")
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args(argv)
    root = Path(a.root)
    if a.cmd == "freeze":
        d8 = a.date.replace("-", "")
        res = [freeze_one(Path(p), root) for p in
               sorted(glob.glob(str(root / f"runtime/final_artifacts/KM-JRA-*-{d8}-R*.json")))]
        res = [r for r in res if r]
        print(json.dumps({"frozen": len(res), "ranking_changed": sum(r["ranking_changed"] for r in res),
                          "formula_mismatch": sum(r["production_formula_check"] != "PRODUCTION_IS_V1_1" for r in res)}))
    elif a.cmd == "evaluate":
        res = [evaluate_one(Path(p).parent, root) for p in
               sorted(glob.glob(str(root / OUT / "*" / "pre_result.json")))]
        print(json.dumps({"evaluated": sum(1 for r in res if r)}))
    else:
        print(json.dumps(summary(root), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
