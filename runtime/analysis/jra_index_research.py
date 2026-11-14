"""JRA 20-index autonomous reflection / research loop (research only).

Closed loop, reusing existing artefacts (no new prediction path):
  signed FINAL (frozen pre-race 13 base + 7 derived values)
  + official top3 (runtime/jra_static_owner_forward_oos/<race>/result_evaluation.json)
  + settlement (runtime/jra_race_day_status/<date>.json)
  + fast reflection (runtime/jra_fast_reflections/<race>.json)
  -> per-race reflection ledger (immutable)          [reflect]
  -> per-index error / discrimination / missing table [analyze]
  -> Challenger formulas generated from training data [candidates]
  -> walk-forward (train < test date) Champion-Challenger [walkforward]
  -> forward Shadow freeze from signed pre-race inputs, evaluation after result [freeze/evaluate]

States: RESEARCH -> CANDIDATE -> SHADOW -> OOS_EVALUATING -> PROMOTION_ELIGIBLE ->
OWNER_APPROVAL_PENDING -> APPROVED -> PRODUCTION | REJECTED/ARCHIVED.
This module can move a Challenger at most to PROMOTION_ELIGIBLE. It never edits
FINALs, never writes Production formulas and never delivers a Challenger.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
import jra_index_provenance_builder as B  # noqa: E402

OUT = "runtime/jra_index_research"
PROFILE = "KM-JRA-INDEX-RESEARCH-v1"
BASE = list(B.BASE)
DERIVED_KEYS = {"DCR": "dcr_score", "TPI": "tpi_final", "ZAI_WIN": "zai_win", "ZAI_PLACE": "zai_place",
                "SRI": "sri", "F3S": "f3s", "T3I": "t3i"}
ALL20 = BASE + list(DERIVED_KEYS)
MIN_TRAIN_RACES = 60
SHRINK = 0.5
PRE_REGISTERED = {
    "primary": "paired top3_mean_rank (Challenger - Champion), lower is better; 95% bootstrap CI upper bound < 0",
    "secondary": ["winner_pct (0=top, 0.5=random)", "winner_in_top3", "top3_in_top5", "ordered_pair_top2",
                  "exact_triple_top3"],
    "promotion_eligible": "forward OOS >= 100 eligible races AND primary CI upper < 0 AND winner_in_top3 not worse "
                          "by more than 2 points AND no condition (surface) with >= 30 races worse by > 0.3 rank",
    "degradation": "forward OOS >= 30 races with primary CI lower > 0 -> REJECTED",
    "pfs": "Challengers have no frozen tickets; counterfactual PFS is NOT computed (Production PFS only)",
}


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def file_sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def race_date(rid: str) -> str:
    return re.search(r"-(\d{8})-R\d{2}", rid).group(1)


# ---------------------------------------------------------------- manifest
def manifest(root: Path) -> dict:
    builder = root / "runtime/jra_index_provenance_builder.py"
    mapping_p = root / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json"
    mapping = json.loads(mapping_p.read_text())
    src = builder.read_text()
    derived = {}
    for name, pat in {"TPI_base": r"tpi_base = \((.*?)\)\n", "SRI": r"sri = (.*)\n", "F3S": r"f3s = (.*)\n",
                      "T3I": r"t3i = (.*)\n", "TPI": r"tpi = (.*)\n", "weak_penalty": r"weak = (.*)\n"}.items():
        m = re.search(pat, src, re.S)
        derived[name] = re.sub(r"\s+", " ", m.group(1)).strip() if m else None
    derived["DCR"] = {"score": "sum of six component points", "max": B.DCR_COMPONENT_MAX,
                      "factor": "0.70 + 0.30 * score / 100"}
    derived["ZAI_WIN"] = {v: B.ZAI_WIN_WEIGHTS[v] for v in B.ZAI_WIN_WEIGHTS}
    derived["ZAI_PLACE"] = {v: B.ZAI_PLACE_WEIGHTS[v] for v in B.ZAI_PLACE_WEIGHTS}
    derived["ZAI_version_selector"] = f"race date >= {B.ZAI_V11_EFFECTIVE_DATE} -> v1.1 else v1.0"
    base = {idx: {p: mapping["index_profiles"][p].get(idx) for p in mapping["index_profiles"]} for idx in BASE}
    return {"profile": PROFILE + "-MANIFEST", "generated_at": now(),
            "formula_registry": B.FORMULA_REGISTRY, "builder_sha256": file_sha(builder),
            "mapping_sha256": file_sha(mapping_p), "category_scale": mapping.get("category_scale"),
            "base13_feature_weights_by_profile": base, "derived7": derived,
            "missing_policy": "components weighted by observed coverage (coverage_weight / information_status in trace); "
                              "no fabricated values (source: builder + mapping)",
            "source": "read from code and mapping at generation time; no names or weights taken from documents"}


# ---------------------------------------------------------------- data access
def _conditions(root: Path, rid: str) -> dict:
    paths = sorted(glob.glob(str(root / f"runtime/executions/{rid}-LIVE-R1/SOURCE/runs/*/source_receipt_envelope.json")))
    for p in reversed(paths):
        try:
            a = json.loads(Path(p).read_text()).get("artifact") or {}
        except ValueError:
            continue
        c = a.get("jra_race_context") or a.get("jra_calendar_race_context") or {}
        cal = a.get("jra_calendar_race_context") or {}
        dist = c.get("distance_m") or cal.get("distance_m")
        return {"venue": rid.split("-")[2], "surface": c.get("surface") or cal.get("surface"),
                "distance_m": dist, "going": c.get("going"),
                "distance_band": None if not dist else ("S<=1400" if dist <= 1400 else "M<=1800" if dist <= 1800 else "L>1800"),
                "race_class": c.get("race_class") or cal.get("race_class")}
    return {"venue": rid.split("-")[2]}


def _settlement(root: Path, rid: str) -> dict | None:
    d = race_date(rid)
    p = root / f"runtime/jra_race_day_status/{d[:4]}-{d[4:6]}-{d[6:]}.json"
    if not p.exists():
        return None
    for r in json.loads(p.read_text()).get("races", []):
        if r.get("race_id") == rid or (rid.endswith(f"R{int(r.get('race_no', 0)):02d}") and rid.split("-")[2] in str(r.get("intent_path", ""))):
            s = r.get("settlement")
            if isinstance(s, dict) and s.get("total_investment") is not None:
                return {"investment": s["total_investment"], "payout": s["total_payout"]}
    return None


def _rank_pct(scores: dict, horse: str):
    order = sorted(scores, key=lambda k: (-scores[k], int(k)))
    if horse not in order:
        return None, None
    i = order.index(horse)
    return i + 1, i / max(1, len(order) - 1)


# ---------------------------------------------------------------- reflect
FAILURE_MAP = {"SOURCE": "A", "OBSERV": "B", "PREDICTION_ROLE_W": "D", "PREDICTION_ROLE": "E",
               "PAIR": "F", "THIRD": "F", "KRS": "G", "MEC": "G", "TICKET": "H", "CAPITAL": "H",
               "DELIVERY": "I", "RESULT": "I", "LEARN": "I"}


def reflect_one(root: Path, final_path: Path) -> dict | None:
    d = json.loads(final_path.read_text())
    rid = d["race_id"]
    out = root / OUT / "reflection" / f"{rid}.json"
    if out.exists():
        return json.loads(out.read_text())
    ev = root / "runtime/jra_static_owner_forward_oos" / rid / "result_evaluation.json"
    if not ev.exists():
        return None
    off = json.loads(ev.read_text())
    top3 = [str(x) for x in off["top3"]]
    runners = d["final_prediction_package"]["index_provenance_replay"]["runners"]
    if not all(t in runners for t in top3):
        return None
    per_index, missing = {}, {}
    for idx in ALL20:
        if idx in BASE:
            sc = {k: r["base_final_values"][idx] for k, r in runners.items()}
        else:
            sc = {k: r.get(DERIVED_KEYS[idx]) for k, r in runners.items()}
            if any(v is None for v in sc.values()):
                continue
        ranks = [_rank_pct(sc, t)[0] for t in top3]
        per_index[idx] = {"winner_pct": _rank_pct(sc, top3[0])[1], "winner_rank": ranks[0],
                          "top3_mean_rank": sum(ranks) / 3}
    for idx in BASE:
        req = pres = 0
        for r in runners.values():
            t = r["base_index_trace"].get(idx) or {}
            comps = t.get("components") or []
            cw = t.get("coverage_weight")
            if isinstance(cw, (int, float)):
                req += 1
                pres += float(cw)
            else:
                req += 1
                pres += 1.0 if comps else 0.0
        missing[idx] = round(1 - pres / max(1, req), 4)
    ranking = [str(x) for x in d["static_prediction"]["ranking"]]
    rank = {h: i + 1 for i, h in enumerate(ranking)}
    fr = root / "runtime/jra_fast_reflections" / f"{rid}.json"
    fmf = json.loads(fr.read_text()).get("first_material_failure") if fr.exists() else None
    tickets = (d.get("final_ticket") or {}).get("tickets") or []
    cls = None
    if fmf:
        cls = next((v for k, v in FAILURE_MAP.items() if k in str(fmf)), None)
    if cls is None:
        if rank.get(top3[0], 99) > 3:
            cls = "D"
        elif ranking[:2] != top3[:2]:
            cls = "F" if set(ranking[:3]) >= set(top3[:2]) else "E"
    body = {"profile": PROFILE + "-REFLECTION", "race_id": rid, "final_sha256": file_sha(final_path),
            "final_freeze_timestamp": d.get("final_freeze_timestamp"),
            "result_observed_at": off.get("observed_at"), "official_result_sha256": off.get("official_result_sha256"),
            "top3": top3, "field_size": len(runners), "conditions": _conditions(root, rid),
            "production": {"zai_version": B.zai_formula_version(rid), "winner_rank": rank.get(top3[0]),
                           "top3_ranks": [rank.get(t) for t in top3], "ordered_pair_top2": ranking[:2] == top3[:2],
                           "exact_triple_top3": ranking[:3] == top3, "tickets": len(tickets),
                           "settlement": _settlement(root, rid)},
            "per_index": per_index, "base_missing_rate": missing,
            "first_material_failure": fmf, "failure_class": cls,
            "frozen_base_values": {k: r["base_final_values"] for k, r in runners.items()},
            "reflected_at": now(), "production_effect": "NONE"}
    body["sha256"] = sha(body)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(body, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return body


def load_reflections(root: Path) -> list:
    rows = [json.loads(Path(p).read_text()) for p in sorted(glob.glob(str(root / OUT / "reflection" / "*.json")))]
    return sorted(rows, key=lambda r: (race_date(r["race_id"]), r["race_id"]))


# ---------------------------------------------------------------- analyze
def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def analyze(rows: list) -> dict:
    out = {"races": len(rows), "per_index": {}, "by_condition": {}, "failure_classes": {}, "correlation_with_zai": {}}
    for idx in ALL20:
        vals = [r["per_index"][idx] for r in rows if idx in r["per_index"]]
        if not vals:
            continue
        out["per_index"][idx] = {
            "races": len(vals), "winner_pct": _mean([v["winner_pct"] for v in vals]),
            "top3_mean_rank": _mean([v["top3_mean_rank"] for v in vals]),
            "missing_rate": _mean([r["base_missing_rate"].get(idx) for r in rows]) if idx in BASE else None}
    for key in ("surface", "distance_band", "venue", "going"):
        groups = {}
        for r in rows:
            g = r["conditions"].get(key)
            if g:
                groups.setdefault(g, []).append(r)
        out["by_condition"][key] = {g: {"races": len(rs), **{idx: _mean([x["per_index"][idx]["winner_pct"] for x in rs
                                                                         if idx in x["per_index"]])
                                                              for idx in ("ZAI_WIN", "BVI", "VMI", "HPI", "SSI", "CFI")}}
                                    for g, rs in groups.items()}
    for r in rows:
        c = r.get("failure_class") or "OK"
        out["failure_classes"][c] = out["failure_classes"].get(c, 0) + 1
    # overlap: share of races where index top-1 equals ZAI top-1 (crude redundancy signal)
    for idx in BASE:
        same = 0
        for r in rows:
            v = r["frozen_base_values"]
            top_i = max(v, key=lambda k: (v[k][idx], -int(k)))
            z = {k: B.zai_win_value(x, "v1.1") for k, x in v.items()}
            top_z = max(z, key=lambda k: (z[k], -int(k)))
            same += top_i == top_z
        out["correlation_with_zai"][idx] = round(same / max(1, len(rows)), 3)
    pfs = [r["production"]["settlement"] for r in rows if r["production"].get("settlement")]
    inv = sum(s["investment"] for s in pfs)
    out["production_pfs"] = {"races": len(pfs), "investment": inv, "payout": sum(s["payout"] for s in pfs),
                             "pfs": (sum(s["payout"] for s in pfs) / inv) if inv else None}
    return out


# ---------------------------------------------------------------- candidates
def _disc_weights(rows: list, champion: dict) -> dict:
    gain = {}
    for idx in BASE:
        pct = _mean([r["per_index"][idx]["winner_pct"] for r in rows if idx in r["per_index"]])
        gain[idx] = max(0.0, 0.5 - pct) if pct is not None else 0.0
    tot = sum(gain.values()) or 1.0
    disc = {k: v / tot for k, v in gain.items()}
    keys = sorted(set(champion) | set(disc))
    w = {k: (1 - SHRINK) * champion.get(k, 0.0) + SHRINK * disc.get(k, 0.0) for k in keys}
    s = sum(w.values())
    return {k: round(v / s, 6) for k, v in w.items() if v > 0}


def generate_candidates(train: list, train_window: list) -> list:
    champion = B.ZAI_WIN_WEIGHTS["v1.1"]
    parent = sha({"ZAI_WIN_v1.1": champion, "builder": "jra_index_provenance_builder"})
    pcts = {idx: _mean([r["per_index"][idx]["winner_pct"] for r in train if idx in r["per_index"]]) for idx in champion}
    weakest = max((k for k in champion if pcts.get(k) is not None), key=lambda k: pcts[k])
    ablate = {k: v for k, v in champion.items() if k != weakest}
    s = sum(ablate.values())
    ablate = {k: round(v / s, 6) for k, v in ablate.items()}
    cands = [
        {"hypothesis": f"{weakest} has the weakest standalone winner discrimination in training "
                       f"(winner_pct {pcts[weakest]:.3f}); removing it from ZAI-WIN reduces noise",
         "change": {"type": "ABLATE", "removed": weakest}, "weights": ablate},
        {"hypothesis": "re-weight ZAI-WIN toward indices with stronger standalone discrimination, shrunk 50% "
                       "toward the Champion to limit overfitting",
         "change": {"type": "DISCRIMINATION_REWEIGHT", "shrink": SHRINK}, "weights": _disc_weights(train, champion)},
    ]
    by_surface = {}
    for surf in ("芝", "ダ"):
        sub = [r for r in train if r["conditions"].get("surface") == surf]
        if len(sub) >= MIN_TRAIN_RACES // 2:
            by_surface[surf] = _disc_weights(sub, champion)
    if len(by_surface) == 2:
        cands.append({"hypothesis": "turf and dirt reward different abilities; surface-specific discrimination "
                                    "re-weighting (50% shrink) improves ranking",
                      "change": {"type": "SURFACE_SPLIT_REWEIGHT", "shrink": SHRINK}, "weights_by_surface": by_surface})
    out = []
    for c in cands:
        c.update({"parent_formula": "JRA-ZAI-WIN-v1.1", "parent_formula_sha256": parent,
                  "train_window": train_window, "train_races": len(train),
                  "expected_effect": "lower paired top3_mean_rank vs Champion",
                  "rejection": PRE_REGISTERED["degradation"], "pre_registered": PRE_REGISTERED})
        c["candidate_id"] = "CAND-ZAIW-" + sha({k: c[k] for k in c if k not in ("pre_registered",)})[:10]
        out.append(c)
    return out


def score_with(c: dict | None, vals: dict, cond: dict, version: str = "v1.1") -> dict:
    if c is None:
        w = B.ZAI_WIN_WEIGHTS[version]
    elif "weights_by_surface" in c:
        w = c["weights_by_surface"].get(cond.get("surface")) or B.ZAI_WIN_WEIGHTS["v1.1"]
    else:
        w = c["weights"]
    return {k: B._weighted_left_sum(v, w) for k, v in vals.items()}


def metrics(scores: dict, top3: list) -> dict:
    order = sorted(scores, key=lambda k: (-scores[k], int(k)))
    rank = {h: i + 1 for i, h in enumerate(order)}
    rk = [rank[t] for t in top3]
    return {"winner_pct": (rk[0] - 1) / max(1, len(order) - 1), "winner_rank": rk[0],
            "top3_mean_rank": sum(rk) / 3, "winner_in_top3": rk[0] <= 3,
            "top3_in_top5": sum(r <= 5 for r in rk) / 3, "ordered_pair_top2": order[:2] == top3[:2],
            "exact_triple_top3": order[:3] == top3}


def paired(rows: list, cand: dict, arm_key: str = "top3_mean_rank") -> dict:
    diffs, agg = [], {"champion": [], "challenger": []}
    for r in rows:
        v, cond, t3 = r["frozen_base_values"], r["conditions"], r["top3"]
        mc = metrics(score_with(None, v, cond), t3)
        mx = metrics(score_with(cand, v, cond), t3)
        agg["champion"].append(mc)
        agg["challenger"].append(mx)
        diffs.append(mx[arm_key] - mc[arm_key])
    if not diffs:
        return {"races": 0}
    rnd = random.Random(1115)
    bs = sorted(sum(rnd.choice(diffs) for _ in diffs) / len(diffs) for _ in range(2000))
    summ = {a: {k: _mean([float(m[k]) for m in agg[a]]) for k in agg[a][0]} for a in agg}
    return {"races": len(diffs), "paired_diff_mean": sum(diffs) / len(diffs),
            "ci95": [bs[50], bs[1949]], **summ}


def walkforward(rows: list) -> dict:
    dates = sorted({race_date(r["race_id"]) for r in rows})
    folds, pooled = [], {}
    for d in dates:
        train = [r for r in rows if race_date(r["race_id"]) < d]
        test = [r for r in rows if race_date(r["race_id"]) == d]
        if len(train) < MIN_TRAIN_RACES or not test:
            continue
        cands = generate_candidates(train, [race_date(train[0]["race_id"]), race_date(train[-1]["race_id"])])
        fold = {"test_date": d, "train_races": len(train), "test_races": len(test), "candidates": {}}
        for c in cands:
            kind = c["change"]["type"]
            res = paired(test, c)
            fold["candidates"][kind] = {"candidate_id": c["candidate_id"], **res}
            pooled.setdefault(kind, [])
            for r in test:
                v, cond, t3 = r["frozen_base_values"], r["conditions"], r["top3"]
                pooled[kind].append(metrics(score_with(c, v, cond), t3)["top3_mean_rank"]
                                    - metrics(score_with(None, v, cond), t3)["top3_mean_rank"])
        folds.append(fold)
    summary = {}
    for kind, diffs in pooled.items():
        rnd = random.Random(7)
        bs = sorted(sum(rnd.choice(diffs) for _ in diffs) / len(diffs) for _ in range(2000))
        summary[kind] = {"test_races": len(diffs), "paired_diff_mean": sum(diffs) / len(diffs), "ci95": [bs[50], bs[1949]]}
    return {"method": "expanding-window walk-forward by race date; train strictly earlier dates; "
                      "Champion = ZAI-WIN v1.1 on identical frozen inputs", "folds": folds, "pooled": summary}


# ---------------------------------------------------------------- registry / forward
def registry_path(root: Path) -> Path:
    return root / OUT / "candidate_registry.json"


def register_shadow(root: Path, rows: list) -> dict:
    """Generate Challengers from ALL reflected races so far and freeze them as SHADOW
    for future races only. Existing SHADOW candidates are kept (never overwritten)."""
    p = registry_path(root)
    reg = json.loads(p.read_text()) if p.exists() else {"profile": PROFILE + "-REGISTRY", "candidates": []}
    if len(rows) < MIN_TRAIN_RACES:
        return reg
    window = [race_date(rows[0]["race_id"]), race_date(rows[-1]["race_id"])]
    active_kinds = {c["change"]["type"] for c in reg["candidates"] if c["status"] in ("SHADOW", "OOS_EVALUATING")}
    for c in generate_candidates(rows, window):
        if c["change"]["type"] in active_kinds:
            continue
        c["status"] = "SHADOW"
        c["registered_at"] = now()
        c["forward_from_race_date"] = (dt.date(int(window[1][:4]), int(window[1][4:6]), int(window[1][6:]))
                                       + dt.timedelta(days=1)).strftime("%Y%m%d")
        reg["candidates"].append(c)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(reg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return reg


def freeze(root: Path, date8: str) -> dict:
    reg = json.loads(registry_path(root).read_text()) if registry_path(root).exists() else {"candidates": []}
    n = 0
    for fp in sorted(glob.glob(str(root / f"runtime/final_artifacts/KM-JRA-*-{date8}-R*.json"))):
        d = json.loads(Path(fp).read_text())
        rid = d["race_id"]
        vals = {k: r["base_final_values"] for k, r in d["final_prediction_package"]["index_provenance_replay"]["runners"].items()}
        for c in reg["candidates"]:
            if c["status"] not in ("SHADOW", "OOS_EVALUATING") or date8 < c["forward_from_race_date"]:
                continue
            if not d.get("final_freeze_timestamp") or c["registered_at"] >= d["final_freeze_timestamp"]:
                continue  # formula must be fixed before the race's own freeze
            out = root / OUT / "forward" / c["candidate_id"] / f"{rid}.pre.json"
            if out.exists():
                continue
            cond = {"surface": None}
            sc = score_with(c, vals, cond if "weights_by_surface" not in c else _conditions(root, rid))
            body = {"candidate_id": c["candidate_id"], "race_id": rid, "final_sha256": file_sha(Path(fp)),
                    "final_freeze_timestamp": d["final_freeze_timestamp"], "candidate_registered_at": c["registered_at"],
                    "frozen_at": now(), "ranking": sorted(sc, key=lambda k: (-sc[k], int(k))),
                    "champion_ranking": [str(x) for x in d["static_prediction"]["ranking"]]}
            body["sha256"] = sha(body)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(body, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            n += 1
    return {"frozen": n}


def evaluate_forward(root: Path) -> dict:
    p = registry_path(root)
    if not p.exists():
        return {"candidates": 0}
    reg = json.loads(p.read_text())
    report = {}
    for c in reg["candidates"]:
        pres = sorted(glob.glob(str(root / OUT / "forward" / c["candidate_id"] / "*.pre.json")))
        diffs, n = [], 0
        for pp in pres:
            pre = json.loads(Path(pp).read_text())
            ev = root / "runtime/jra_static_owner_forward_oos" / pre["race_id"] / "result_evaluation.json"
            if not ev.exists():
                continue
            top3 = [str(x) for x in json.loads(ev.read_text())["top3"]]
            def tmr(order):
                rank = {h: i + 1 for i, h in enumerate(order)}
                return sum(rank.get(t, len(order) + 1) for t in top3) / 3
            diffs.append(tmr(pre["ranking"]) - tmr(pre["champion_ranking"]))
            n += 1
        res = {"eligible_races": n}
        if diffs:
            rnd = random.Random(3)
            bs = sorted(sum(rnd.choice(diffs) for _ in diffs) / len(diffs) for _ in range(2000))
            res.update(paired_diff_mean=sum(diffs) / n, ci95=[bs[50], bs[1949]])
            if c["status"] == "SHADOW":
                c["status"] = "OOS_EVALUATING"
            if n >= 30 and bs[50] > 0:
                c["status"] = "REJECTED"
                c["rejected_reason"] = "forward OOS degradation (CI lower > 0)"
            elif n >= 100 and bs[1949] < 0:
                c["status"] = "PROMOTION_ELIGIBLE"  # Owner approval still required
        report[c["candidate_id"]] = {"status": c["status"], **res}
    p.write_text(json.dumps(reg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return report


# ---------------------------------------------------------------- run
def run_all(root: Path, date8: str | None, weekly: bool) -> dict:
    reflected = sum(1 for fp in sorted(glob.glob(str(root / "runtime/final_artifacts/KM-JRA-*-2026*-R*.json")))
                    if reflect_one(root, Path(fp)))
    rows = load_reflections(root)
    out = root / OUT
    out.mkdir(parents=True, exist_ok=True)
    (out / "formula_manifest.json").write_text(json.dumps(manifest(root), ensure_ascii=False, indent=1) + "\n")
    an = analyze(rows)
    (out / "index_analysis.json").write_text(json.dumps(an, ensure_ascii=False, indent=1) + "\n")
    summary = {"profile": PROFILE, "generated_at": now(), "reflected_races": len(rows), "new_reflections": reflected}
    if weekly or not (out / "walkforward.json").exists():
        wf = walkforward(rows)
        (out / "walkforward.json").write_text(json.dumps(wf, ensure_ascii=False, indent=1) + "\n")
        summary["walkforward"] = wf["pooled"]
    reg = register_shadow(root, rows)
    summary["candidates"] = [{k: c.get(k) for k in ("candidate_id", "status", "change", "forward_from_race_date")}
                             for c in reg.get("candidates", [])]
    if date8:
        summary["freeze"] = freeze(root, date8)
    summary["forward"] = evaluate_forward(root)
    summary["production_effect"] = "NONE"
    (out / "status.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1) + "\n")
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--date", help="YYYY-MM-DD to freeze forward Shadow for that day's FINALs")
    ap.add_argument("--weekly", action="store_true", help="recompute walk-forward")
    a = ap.parse_args(argv)
    s = run_all(Path(a.root), a.date.replace("-", "") if a.date else None, a.weekly)
    print(json.dumps({k: s[k] for k in s if k != "candidates"}, ensure_ascii=False)[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
