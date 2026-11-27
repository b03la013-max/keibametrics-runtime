"""JRA index evolution: candidates for every stage, generations, tried ledger, promotion packets.

Owner instruction 2026-11-21 22:39 (scheduled task fired 2026-11-27): the conversion from collected
information to points, each index's formula and the index composite are provisional and must keep
improving through a mechanism. Research only (production_effect NONE): nothing here edits a FINAL,
the mapping, the builder, a ticket or a delivery, and a candidate can at most become
PROMOTION_ELIGIBLE. Adoption is an Owner decision, registered afterwards as a new version with an
effective time (earlier predictions and results are never rewritten; rollback = the previous version).

Stages
  S1_CONVERSION       band -> points (mapping.category_scale): training-window isotonic refit, 50% shrink
  S2_INDEX_FORMULA    one base index's feature weights (index_profiles, ESTABLISHED profile): the
                      weakest index in training, feature discrimination re-weight (50% shrink) or
                      ablation of its weakest feature
  S3_COMPOSITE        ZAI-WIN weights (existing jra_index_research candidates; their ids are kept)
  S4_ROLE / S5_TICKET listed from their own pre-registrations (jra_role_candidate_replay,
                      jra_nobet_shadow); generated there, not here
Rules
  * time order: candidates are fitted on reflected races up to the training-window end; the forward
    comparison starts the next day and only counts races whose FINAL froze after registration
  * at most MAX_ACTIVE (3) candidates per stage are evaluated at once
  * generations: when an active candidate of a type has >= NEXT_GEN_AFTER (30) forward races and a slot
    is free, a child trained on the latest window is added (parent, generation, window recorded);
    a REJECTED type is re-fitted only on a newer training window
  * every generated candidate, registered or not, is appended to tried_ledger.json with the reason
  * decision rule (pre-registered): 30R interim, >= 100R and paired CI upper < 0 and winner_in_top3 not
    worse by > 2 points and no surface or venue x surface with >= 30 races worse by > 0.3 -> eligible;
    >= 30R with CI lower > 0 -> REJECTED; 300R confirmation is reported in the packet
  * features are frozen per race from the pre-race FORMAL request into reflection_features/ (once)
"""
from __future__ import annotations

import copy
import datetime as dt
import glob
import hashlib
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime")); sys.path.insert(0, str(ROOT / "runtime/analysis"))
import jra_evidence_to_base_production as P  # noqa: E402
import jra_index_provenance_builder as B  # noqa: E402
import jra_index_research as R  # noqa: E402

OUT = R.OUT
MAX_ACTIVE = 3
NEXT_GEN_AFTER = 30
MIN_TRAIN = 60
SHRINK = 0.5
ACTIVE = ("SHADOW", "OOS_EVALUATING")
RULE = {"interim": 30, "decision": 100, "confirm": 300, "winner_in_top3_max_drop_pts": 2.0,
        "stratum_min_races": 30, "stratum_max_worse_rank": 0.3,
        "primary": "paired top3_mean_rank (Challenger - Champion), lower is better",
        "note": "Challengers have no frozen tickets: max-payout-excluded PFS is reported for Production only"}


def _sha(o):
    return hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _mapping(root):
    return P.load_mapping(root / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")


# ------------------------------------------------------------------ (a) frozen features
def features_sidecar(root, rid):
    """Band values per runner from the pre-race FORMAL request, frozen once (immutable)."""
    out = root / OUT / "reflection_features" / f"{rid}.json"
    if out.exists():
        return json.loads(out.read_text())
    rq = root / "runtime/requests" / f"{rid}-LIVE-R1-FORMAL.json"
    if not rq.exists():
        return None
    req = json.loads(rq.read_text())
    mapping = _mapping(root)
    runners = {}
    for r in req.get("runners") or []:
        try:
            prof = P._profile_for_runner(r)
        except Exception:  # noqa: BLE001
            continue
        feats = {}
        for f, v in (r.get("evidence_features") or {}).items():
            try:  # keep only what the Production consumer itself would accept, as the band alone
                feats[f] = P._feature_score(f, {f: v}, mapping)["category"]
            except Exception:  # noqa: BLE001
                continue
        runners[str(r["runner_id"])] = {"profile": prof, "bvi_acquisition_failure": r.get("bvi_acquisition_failure"),
                                        "features": feats}
    body = {"race_id": rid, "source": f"runtime/requests/{rid}-LIVE-R1-FORMAL.json", "request_sha256": R.file_sha(rq),
            "frozen_at": _now(), "runners": runners}
    body["sha256"] = _sha(body)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(body, ensure_ascii=False, separators=(",", ":")) + "\n")
    return body


def _restore(category):
    return {"category": category, "evidence_refs": ["FROZEN_REFLECTION_FEATURE"], "source_fact": "frozen band",
            "rule_id": "FROZEN"}


def base_values(side, mapping):
    out = {}
    for h, r in side["runners"].items():
        feats = {f: _restore(v) for f, v in r["features"].items()}
        try:
            out[h] = {idx: P._weighted_index(idx, r["profile"], feats, mapping,
                                             acquisition_failure=r.get("bvi_acquisition_failure") if idx == "BVI" else None)["value"]
                      for idx in B.BASE}
        except Exception:  # noqa: BLE001 - a runner the Production mapping would reject is left out
            continue
    return out


def ranking(vals, weights=None):
    w = weights or B.ZAI_WIN_WEIGHTS["v1.1"]
    z = {k: B._weighted_left_sum(v, w) for k, v in vals.items()}
    return sorted(z, key=lambda k: (-z[k], int(k) if k.isdigit() else k))


def apply(mapping, cand):
    m = copy.deepcopy(mapping)
    if cand["stage"] == "S1_CONVERSION":
        m["category_scale"] = dict(cand["category_scale"])
    elif cand["stage"] == "S2_INDEX_FORMULA":
        m["index_profiles"][cand["profile"]][cand["index"]] = dict(cand["feature_weights"])
    return m


# ------------------------------------------------------------------ generators (S1, S2)
def _train_rows(root, rows):
    out = []
    for r in rows:
        side = features_sidecar(root, r["race_id"])
        if side and side["runners"]:
            out.append((r, side))
    return out


def _pava(xs):
    """Pool-adjacent-violators for a non-decreasing fit; xs = [(value, weight)]."""
    blocks = [[v, w, 1] for v, w in xs]
    i = 0
    while i < len(blocks) - 1:
        if blocks[i][0] > blocks[i + 1][0]:
            a, b = blocks[i], blocks[i + 1]
            w = a[1] + b[1]
            blocks[i] = [(a[0] * a[1] + b[0] * b[1]) / w if w else 0, w, a[2] + b[2]]
            del blocks[i + 1]
            i = max(0, i - 1)
        else:
            i += 1
    out = []
    for v, _, n in blocks:
        out += [v] * n
    return out


def gen_s1(train, mapping):
    scale = mapping["category_scale"]
    cats = sorted(scale, key=lambda c: scale[c])
    hit = {c: [0, 0] for c in cats}
    for r, side in train:
        top3 = set(r["top3"])
        for h, x in side["runners"].items():
            for c in x["features"].values():
                c = str(c or "").upper()
                if c in hit:
                    hit[c][0] += h in top3
                    hit[c][1] += 1
    rates = [(hit[c][0] / hit[c][1] if hit[c][1] else 0.0, hit[c][1]) for c in cats]
    fit = _pava(rates)
    lo, hi = min(scale.values()), max(scale.values())
    flo, fhi = min(fit), max(fit)
    new = {}
    for c, f in zip(cats, fit):
        target = lo + (hi - lo) * ((f - flo) / (fhi - flo) if fhi > flo else 0.5)
        new[c] = round((1 - SHRINK) * scale[c] + SHRINK * target, 2)
    return [{"stage": "S1_CONVERSION", "type": "CATEGORY_SCALE_ISOTONIC",
             "hypothesis": "band points follow the training top-3 rate of each band (isotonic, 50% shrink)",
             "category_scale": new, "training_band_counts": {c: hit[c][1] for c in cats}}]


def _feature_score_vals(side, feature, mapping):
    out = {}
    for h, x in side["runners"].items():
        c = str(x["features"].get(feature) or "").upper()
        if c in mapping["category_scale"]:
            out[h] = mapping["category_scale"][c]
    return out


def gen_s2(train, mapping):
    prof = "ESTABLISHED"
    pct = {}
    for idx in B.BASE:
        if idx == "VMI":
            continue
        xs = [r["per_index"][idx]["winner_pct"] for r, _ in train if idx in r.get("per_index", {})]
        if xs:
            pct[idx] = sum(xs) / len(xs)
    if not pct:
        return []
    weakest = max(pct, key=pct.get)
    w = mapping["index_profiles"][prof][weakest]
    disc = {}
    for f in w:
        xs = []
        for r, side in train:
            sc = _feature_score_vals(side, f, mapping)
            if r["top3"][0] in sc and len(sc) > 1:
                order = sorted(sc, key=lambda k: -sc[k])
                xs.append(order.index(r["top3"][0]) / (len(order) - 1))
        disc[f] = (sum(xs) / len(xs), len(xs)) if xs else (0.5, 0)
    gain = {f: max(0.0, 0.5 - p) for f, (p, _) in disc.items()}
    tot = sum(gain.values()) or 1.0
    rw = {f: (1 - SHRINK) * w[f] + SHRINK * gain[f] / tot * sum(w.values()) for f in w}
    rw = {f: round(v, 6) for f, v in rw.items() if v > 0}
    worst = max(disc, key=lambda f: disc[f][0])
    ab = {f: v for f, v in w.items() if f != worst}
    base = {"stage": "S2_INDEX_FORMULA", "profile": prof, "index": weakest,
            "training_index_winner_pct": round(pct[weakest], 4),
            "training_feature_winner_pct": {f: [round(p, 4), n] for f, (p, n) in disc.items()}}
    return [dict(base, type=f"INDEX_FEATURE_REWEIGHT:{weakest}", feature_weights=rw,
                 hypothesis=f"{weakest} is the weakest base index in training; re-weight its features by their own "
                            f"winner discrimination (50% shrink)"),
            dict(base, type=f"INDEX_FEATURE_ABLATE:{weakest}", feature_weights=ab, removed=worst,
                 hypothesis=f"{weakest}'s weakest feature {worst} adds noise; drop it (remaining weights re-normalised "
                            f"by Production's coverage rule)")]


# ------------------------------------------------------------------ registry with generations
def _reg_path(root):
    return root / OUT / "evolution_registry.json"


def _load(p, default):
    return json.loads(p.read_text()) if p.exists() else default


def _day_after(d8):
    return (dt.date(int(d8[:4]), int(d8[4:6]), int(d8[6:])) + dt.timedelta(days=1)).strftime("%Y%m%d")


def register(root, rows, forward):
    reg = _load(_reg_path(root), {"profile": R.PROFILE + "-EVOLUTION", "rule": RULE, "candidates": []})
    tried_p = root / OUT / "tried_ledger.json"
    tried = _load(tried_p, {"profile": R.PROFILE + "-TRIED", "entries": []})
    train = _train_rows(root, rows)
    if len(train) < MIN_TRAIN:
        return reg, {"registered": 0, "reason": f"TRAINING_RACES_{len(train)}_BELOW_{MIN_TRAIN}"}
    window = [R.race_date(train[0][0]["race_id"]), R.race_date(train[-1][0]["race_id"])]
    mapping = _mapping(root)
    made = 0
    for c in gen_s1(train, mapping) + gen_s2(train, mapping):
        same = [x for x in reg["candidates"] if x["type"] == c["type"]]
        active = [x for x in same if x["status"] in ACTIVE]
        stage_active = [x for x in reg["candidates"] if x["stage"] == c["stage"] and x["status"] in ACTIVE]
        parent = max(same, key=lambda x: x["generation"]) if same else None
        reason = None
        if parent and parent["train_window"][1] >= window[1]:
            reason = "NO_NEWER_TRAINING_WINDOW"
        elif active and forward.get(active[-1]["candidate_id"], {}).get("eligible_races", 0) < NEXT_GEN_AFTER:
            reason = f"ACTIVE_PARENT_BELOW_{NEXT_GEN_AFTER}R"
        elif len(stage_active) >= MAX_ACTIVE:
            reason = f"STAGE_CAP_{MAX_ACTIVE}"
        c.update({"generation": (parent["generation"] + 1) if parent else 1,
                  "parent_candidate_id": parent["candidate_id"] if parent else None,
                  "train_window": window, "train_races": len(train), "rule": RULE,
                  "parent_formula": "JRA-MAPPING-v1.0_20260921 + ZAI-WIN-v1.1",
                  "parent_formula_sha256": R.file_sha(root / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")})
        c["candidate_id"] = "CAND-EVO-" + _sha({k: v for k, v in c.items() if k != "rule"})[:10]
        c["formula_sha256"] = _sha({k: c.get(k) for k in ("category_scale", "feature_weights", "profile", "index")})
        tried["entries"].append({"candidate_id": c["candidate_id"], "stage": c["stage"], "type": c["type"],
                                 "generation": c["generation"], "parent": c["parent_candidate_id"],
                                 "train_window": window, "at": _now(),
                                 "outcome": "REGISTERED" if not reason else "NOT_REGISTERED:" + reason})
        if reason or any(x["candidate_id"] == c["candidate_id"] for x in reg["candidates"]):
            continue
        c.update({"status": "SHADOW", "registered_at": _now(), "forward_from_race_date": _day_after(window[1])})
        reg["candidates"].append(c)
        made += 1
    _reg_path(root).parent.mkdir(parents=True, exist_ok=True)
    _reg_path(root).write_text(json.dumps(reg, ensure_ascii=False, indent=1) + "\n")
    tried_p.write_text(json.dumps(tried, ensure_ascii=False, indent=1) + "\n")
    return reg, {"registered": made, "train_window": window, "train_races": len(train)}


# ------------------------------------------------------------------ forward freeze / evaluation (S1, S2)
def freeze(root, date8, reg):
    mapping = _mapping(root)
    n = 0
    for fp in sorted(glob.glob(str(root / f"runtime/final_artifacts/KM-JRA-*-{date8}-R*.json"))):
        d = json.loads(Path(fp).read_text())
        rid, fz = d["race_id"], d.get("final_freeze_timestamp")
        side = features_sidecar(root, rid)
        if not side or not fz:
            continue
        champ = None
        for c in reg["candidates"]:
            if c["status"] not in ACTIVE or date8 < c["forward_from_race_date"] or c["registered_at"] >= fz:
                continue
            out = root / OUT / "forward" / c["candidate_id"] / f"{rid}.pre.json"
            if out.exists():
                continue
            champ = champ or ranking(base_values(side, mapping))
            body = {"candidate_id": c["candidate_id"], "race_id": rid, "final_sha256": R.file_sha(Path(fp)),
                    "final_freeze_timestamp": fz, "candidate_registered_at": c["registered_at"], "frozen_at": _now(),
                    "ranking": ranking(base_values(side, apply(mapping, c))), "champion_ranking": champ,
                    "champion": "Production mapping + ZAI-WIN v1.1 on the same frozen bands"}
            body["sha256"] = _sha(body)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(body, ensure_ascii=False, indent=1) + "\n")
            n += 1
    return n


def _tmr(order, top3):
    rank = {h: i + 1 for i, h in enumerate(order)}
    return sum(rank.get(t, len(order) + 1) for t in top3) / 3


def _boot(d, seed):
    rnd = random.Random(seed)
    bs = sorted(sum(rnd.choice(d) for _ in d) / len(d) for _ in range(2000))
    return [bs[50], bs[1949]]


def evaluate(root, candidate_id, conditions):
    rows = []
    for pp in sorted(glob.glob(str(root / OUT / "forward" / candidate_id / "*.pre.json"))):
        pre = json.loads(Path(pp).read_text())
        top3 = R.official_top3(root, pre["race_id"])
        if not top3:
            continue
        cond = conditions.get(pre["race_id"]) or R._conditions(root, pre["race_id"])
        rows.append({"race_id": pre["race_id"], "d": _tmr(pre["ranking"], top3) - _tmr(pre["champion_ranking"], top3),
                     "w_c": pre["ranking"].index(top3[0]) < 3 if top3[0] in pre["ranking"] else False,
                     "w_p": pre["champion_ranking"].index(top3[0]) < 3 if top3[0] in pre["champion_ranking"] else False,
                     "surface": cond.get("surface"), "venue": cond.get("venue")})
    res = {"eligible_races": len(rows)}
    if not rows:
        return res, rows
    d = [r["d"] for r in rows]
    res.update(paired_diff_mean=sum(d) / len(d), ci95=_boot(d, 11))
    return res, rows


def strata(rows):
    out = {}
    for key in ("surface", "venue_surface"):
        g = {}
        for r in rows:
            k = r["surface"] if key == "surface" else f"{r['venue']}x{r['surface']}"
            g.setdefault(str(k), []).append(r["d"])
        out[key] = {k: {"races": len(v), "mean": round(sum(v) / len(v), 4)} for k, v in g.items()}
    return out


def decide(c, res, rows):
    """Apply the pre-registered rule. Returns (status, packet or None)."""
    n = res.get("eligible_races", 0)
    if not n:
        return c["status"], None
    lo, hi = res["ci95"]
    if n >= RULE["interim"] and lo > 0:
        return "REJECTED", None
    if n < RULE["decision"] or hi >= 0:
        return "OOS_EVALUATING", None
    w_drop = 100 * (sum(r["w_p"] for r in rows) - sum(r["w_c"] for r in rows)) / n
    st = strata(rows)
    worse = [f"{k}:{s}" for k in st for s, v in st[k].items()
             if v["races"] >= RULE["stratum_min_races"] and v["mean"] > RULE["stratum_max_worse_rank"]]
    packet = {"candidate_id": c["candidate_id"], "stage": c.get("stage"), "type": c.get("type") or (c.get("change") or {}).get("type"),
              "races": n, "paired_diff_mean": round(res["paired_diff_mean"], 4), "ci95": [round(lo, 4), round(hi, 4)],
              "winner_in_top3_change_pts": round(-w_drop, 2), "strata": st, "worse_strata": worse,
              "confirmation_300R": n >= RULE["confirm"], "rule": RULE,
              "what_changes": {k: c.get(k) for k in ("category_scale", "feature_weights", "index", "profile", "weights",
                                                     "weights_by_surface", "change") if c.get(k) is not None},
              "adoption": "Owner decision; registered as a new version with an effective time; earlier predictions "
                          "and results are never rewritten; rollback = return to the previous version"}
    ok = w_drop <= RULE["winner_in_top3_max_drop_pts"] and not worse
    packet["eligible"] = ok
    return ("PROMOTION_ELIGIBLE" if ok else "OOS_EVALUATING"), packet


# ------------------------------------------------------------------ ledger + unified view
def update_formula_ledger(root, evo, s3):
    p = root / OUT / "formula_ledger.json"
    if not p.exists():
        return
    led = json.loads(p.read_text())
    ev = {}
    for c in evo["candidates"]:
        idx = c.get("index") or "ALL_BASE"
        ev.setdefault(idx, []).append({"candidate_id": c["candidate_id"], "stage": c["stage"], "status": c["status"],
                                       "generation": c["generation"], "forward_races": c.get("forward", {}).get("eligible_races", 0)})
    for c in s3:
        ev.setdefault("ZAI_WIN", []).append({"candidate_id": c["candidate_id"], "stage": "S3_COMPOSITE",
                                             "status": c["status"], "forward_races": c.get("eligible_races", 0)})
    for idx, info in led.get("indices", {}).items():
        items = ev.get(idx, []) + ev.get("ALL_BASE", [])
        n = max([i["forward_races"] for i in items] or [0])
        info["research_evidence_stage"] = ("FORWARD_OOS" if n else "WALK_FORWARD" if items else info.get("stage"))
        info["research_candidates"] = items
    led["research_evidence_updated_at"] = _now()
    led["research_evidence_note"] = ("Production formulas keep their own 'stage'; research_evidence_stage is the "
                                     "strongest evidence any candidate touching the index has reached")
    p.write_text(json.dumps(led, ensure_ascii=False, indent=1) + "\n")


def downstream(root):
    out = []
    for p in sorted(glob.glob(str(root / "profiles/KM_JRA_FORWARD_OOS_PREREG_*.json"))):
        name = Path(p).name
        stage = ("S5_TICKET" if re.search(r"NOBET|CAP|TICKET|BUDGET", name) else
                 "S4_ROLE" if re.search(r"ROLE|W_WIDTH|P2|P3|AKI", name) else
                 "S1_CONVERSION" if "CONVERSION" in name else "OTHER")
        out.append({"profile": name, "stage": stage})
    return out


def run(root, rows, date8=None):
    s3 = json.loads((root / OUT / "status.json").read_text()).get("forward", {}) if (root / OUT / "status.json").exists() else {}
    reg = _load(_reg_path(root), {"candidates": []})
    conditions = {r["race_id"]: r.get("conditions") or {} for r in rows}
    fwd = {}
    for c in reg.get("candidates", []):
        fwd[c["candidate_id"]], _ = evaluate(root, c["candidate_id"], conditions)
    reg, reg_out = register(root, rows, fwd)
    frozen = freeze(root, date8, reg) if date8 else 0
    packets = []
    for c in reg["candidates"]:
        res, rws = evaluate(root, c["candidate_id"], conditions)
        c["forward"] = res
        if c["status"] in ACTIVE + ("PROMOTION_ELIGIBLE",):
            c["status"], pk = decide(c, res, rws)
            if pk:
                packets.append(pk)
    # S3 (existing ZAI-WIN candidates): same decision rule and packet, status kept in their own registry
    s3reg_p = R.registry_path(root)
    s3list = []
    if s3reg_p.exists():
        s3reg = json.loads(s3reg_p.read_text())
        for c in s3reg["candidates"]:
            res, rws = evaluate(root, c["candidate_id"], conditions)
            s3list.append({"candidate_id": c["candidate_id"], "status": c["status"], **res})
            if c["status"] in ("OOS_EVALUATING", "PROMOTION_ELIGIBLE") and res.get("eligible_races", 0) >= RULE["decision"]:
                st, pk = decide(dict(c, stage="S3_COMPOSITE"), res, rws)
                if pk:
                    packets.append(pk)
                if c["status"] == "PROMOTION_ELIGIBLE" and st != "PROMOTION_ELIGIBLE":
                    c["status"] = "OOS_EVALUATING"
                    c["promotion_blocked"] = (pk or {}).get("worse_strata") or "winner_in_top3 or CI"
        s3reg_p.write_text(json.dumps(s3reg, ensure_ascii=False, indent=1) + "\n")
    _reg_path(root).write_text(json.dumps(reg, ensure_ascii=False, indent=1) + "\n")
    pk_dir = root / OUT / "promotion_packets"
    for pk in packets:
        pk_dir.mkdir(parents=True, exist_ok=True)
        (pk_dir / f"{pk['candidate_id']}.json").write_text(json.dumps(pk, ensure_ascii=False, indent=1) + "\n")
    update_formula_ledger(root, reg, s3list)
    view = {"profile": R.PROFILE + "-STAGES", "generated_at": _now(), "production_effect": "NONE",
            "stages": {s: [{k: c.get(k) for k in ("candidate_id", "type", "generation", "parent_candidate_id",
                                                     "train_window", "status", "forward")}
                           for c in reg["candidates"] if c["stage"] == s] for s in ("S1_CONVERSION", "S2_INDEX_FORMULA")},
            "S3_COMPOSITE": s3list, "downstream_prereg": downstream(root),
            "promotion_packets": [p["candidate_id"] for p in packets if p.get("eligible")]}
    (root / OUT / "stages_status.json").write_text(json.dumps(view, ensure_ascii=False, indent=1) + "\n")
    return {"registered": reg_out, "frozen": frozen, "packets": len(packets),
            "eligible": view["promotion_packets"], "s3_seen": len(s3)}
