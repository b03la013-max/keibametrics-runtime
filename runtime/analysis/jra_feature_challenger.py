"""JRA feature-type Challenger slot (Owner 2026-11-21 13:13 / 2026-11-22 20:00 task).

Connects collected but unconnected information to the 13 base indices as CHALLENGER
features. Production weights, mapping, tickets and FINALs are not changed. For each race:
  PROD          frozen Production evidence features -> base13 -> ZAI_WIN ranking (replay must match)
  CH_<group>    PROD features + that group's challenger features (only features that are
                unobserved in Production are filled; observed Production features are never
                overwritten) -> same mapping weights -> ZAI_WIN ranking
Groups (band files under runtime/jra_challenger_features/<date>/, bands only, no raw text):
  KB4      keibabook_challenger_bands.json -> workout_load, workout_partner_level,
           workout_consistency, stable_readiness (rules profiles/KM_JRA_CHALLENGER_FEATURE_RULES_20261122_KB.json)
  EXPERT   tsl_expert_bands.json -> expert_support (TSL 推奨: 軸 STRONG / 本線 POSITIVE / 次点・おさえ NEUTRAL),
           taken only from the last TSL capture strictly before the post time
  EQUIP    JRA official equipment declaration in the frozen request -> equipment_effect
           (blinker declared POSITIVE; hypothesis KM-JRA-CH-EQUIP-BLINKER-v1)
  TSL / paddock band files are paid-source derived and stay in the PRIVATE repo
  (jra/<date>/challenger_bands/); public outputs carry rankings only.
  PADDOCK  kb_paddock_bands.json -> body_condition_comment (競馬ブック パドック評価 A STRONG / B・穴 POSITIVE),
           taken only from a capture strictly before the post time
  ALL      all groups
A4 (silent-failure detection): every provider / race / arm failure is counted as an ERROR
with a reason; any ERROR > 0 is printed as "A4 ERROR" and recorded in the freeze file.
A result annotation such as "(2着)" inside a pre-race capture is an ERROR (leak guard).

  python3 runtime/analysis/jra_feature_challenger.py bands  <date>   # private raw -> public bands (needs private repo)
  python3 runtime/analysis/jra_feature_challenger.py freeze <date>   # pre-race only (post time not yet passed)
  python3 runtime/analysis/jra_feature_challenger.py replay <date>   # known-result context (never counts as OOS)
  python3 runtime/analysis/jra_feature_challenger.py evaluate          # forward freezes with results, venue x surface
"""
from __future__ import annotations

import argparse
import copy
import glob
import gzip
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(ROOT / "runtime/analysis"))
import jra_evidence_to_base_production as P  # noqa: E402
import jra_index_provenance_builder as B  # noqa: E402
import jra_oos_strata as S  # noqa: E402

PROFILE = "KM-JRA-FEATURE-CHALLENGER-v1"
PRIVATE = Path("/home/claude/keibametrics-private-evidence")
FEAT_DIR = ROOT / "runtime/jra_challenger_features"
OUT = ROOT / "runtime/jra_feature_challenger"
JST = timezone(timedelta(hours=9))
GROUPS = {
    "KB4": ["workout_load", "workout_partner_level", "workout_consistency", "stable_readiness"],
    "EXPERT": ["expert_support"],
    "PADDOCK": ["body_condition_comment"],
    "EQUIP": ["equipment_effect"],
}
ARMS = ["PROD"] + [f"CH_{g}" for g in GROUPS] + ["CH_ALL"]
JRA_VENUE = {"01": "SAP", "02": "HKD", "03": "FKS", "04": "NGT", "05": "TKY", "06": "NKY",
             "07": "CHK", "08": "KYO", "09": "HSN", "10": "KKR"}
KB_VENUE = {"04": "TKY", "00": "KYO", "06": "FKS"}   # codes seen on Keibabook nittei pages; others fail closed (A4)
KB_RULES = json.loads((ROOT / "profiles/KM_JRA_CHALLENGER_FEATURE_RULES_20261122_KB.json").read_text())["feature_rules"]
CIRCLED = {chr(0x2460 + i): i + 1 for i in range(20)}


class A4:
    def __init__(self):
        self.errors = []

    def err(self, where, reason):
        self.errors.append({"where": where, "reason": str(reason)[:200]})


def sha(o):
    return hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def d8(date):
    return date.replace("-", "")


def post_times(date):
    p = ROOT / f"runtime/jra_race_day_status/{date}.json"
    out = {}
    if not p.exists():
        return out
    def walk(o):
        if isinstance(o, dict):
            rid, post = o.get("race_id"), o.get("post") or o.get("post_time")
            if isinstance(rid, str) and isinstance(post, str):
                m = re.search(r"(?:T|^)(\d{1,2}):(\d{2})", post)
                if m:
                    out[rid] = f"{int(m.group(1)):02d}:{m.group(2)}"
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(json.loads(p.read_text()))
    return out


def rid_of(venue, date, no):
    return f"KM-JRA-{venue}-{d8(date)}-R{int(no):02d}"


# ---------------- band builders (private raw -> public bands) ----------------
def _nums(s):
    return [int(x) for x in re.findall(r"(?<![\d(])(\d{1,2})(?![\d着])", re.sub(r"\(\d+着\)", "", s or ""))]


def build_tsl_bands(date, posts, a4):
    files = sorted(glob.glob(str(PRIVATE / f"jra/{date}/tsl_full/*.json.gz")))
    races = {}
    for f in files:
        hhmm = Path(f).name[:4]
        try:
            d = json.load(gzip.open(f))
        except Exception as e:
            a4.err(f"tsl:{Path(f).name}", e)
            continue
        for r in d.get("races") or []:
            m = re.match(r"(\d{2})\d{8}/(\d{2})", r.get("key") or "")
            if not m or m.group(1) not in JRA_VENUE:
                a4.err(f"tsl:{r.get('key')}", "UNKNOWN_VENUE_KEY")
                continue
            rid = rid_of(JRA_VENUE[m.group(1)], date, m.group(2))
            post = posts.get(rid)
            if not post:
                a4.err(f"tsl:{rid}", "NO_POST_TIME")
                continue
            if hhmm >= post.replace(":", "").zfill(4):
                continue                           # not strictly pre-race
            rec = r.get("rec") or {}
            if re.search(r"\(\d+着\)", rec.get("raw") or ""):
                a4.err(f"tsl:{rid}:{hhmm}", "RESULT_ANNOTATION_IN_PRE_RACE_CAPTURE")
                continue
            bands = {}
            for n in _nums(rec.get("cover")) + _nums(rec.get("second")):
                bands[n] = "NEUTRAL"
            for n in _nums(rec.get("main")):
                bands[n] = "POSITIVE"
            for n in _nums(rec.get("axis"))[:1]:
                bands[n] = "STRONG"
            if bands:
                races[rid] = {"capture": hhmm, "bands": {str(k): v for k, v in sorted(bands.items())}}
    return races


def build_paddock_bands(date, posts, a4):
    races = {}
    grade = {"A": "STRONG", "B": "POSITIVE", "穴": "POSITIVE"}
    for f in sorted(glob.glob(str(PRIVATE / f"jra/{date}/keibabook_pages_PD*.json.gz"))):
        hhmm = re.search(r"PD(\d{4})", f).group(1)
        try:
            d = json.load(gzip.open(f))
        except Exception as e:
            a4.err(f"paddock:{Path(f).name}", e)
            continue
        for r in d.get("races") or []:
            kb = str(r.get("kb_id") or "")
            v = KB_VENUE.get(kb[6:8])
            if not v:
                a4.err(f"paddock:{kb}", "UNKNOWN_KB_VENUE")
                continue
            rid = rid_of(v, date, kb[-2:])
            post = posts.get(rid)
            page = (r.get("pages") or {}).get("パドック情報") or {}
            if not post or page.get("unavailable") or not page.get("tables"):
                continue
            if hhmm >= post.replace(":", "").zfill(4):
                continue
            bands = {}
            for t in page["tables"]:
                for row in t.get("rows") or []:
                    if len(row) >= 2 and row[0] in grade and row[1][:1] in CIRCLED:
                        bands[str(CIRCLED[row[1][0]])] = grade[row[0]]
            if bands:
                races[rid] = {"capture": hhmm, "bands": bands}
    return races


def cmd_bands(a):
    a4 = A4()
    posts = post_times(a.date)
    out_dir = PRIVATE_BANDS(a.date)   # paid sources: bands stay private (no 1:1 recoverable marks in public)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, fn, rule in (("tsl_expert_bands.json", build_tsl_bands, "KM-JRA-CH-TSL-RECOMMEND-BAND-v1"),
                           ("kb_paddock_bands.json", build_paddock_bands, "KM-JRA-CH-KB-PADDOCK-GRADE-BAND-v1")):
        races = fn(a.date, posts, a4)
        rec = {"profile": PROFILE, "rule_id": rule, "date": a.date, "challenger_only": True,
               "production_effect": "NONE", "pre_race_only": "capture HHMM strictly before post time",
               "races": races}
        (out_dir / name).write_text(json.dumps(rec, ensure_ascii=False, indent=1))
        print(name, len(races), "races")
    _report_a4(a4)


# ---------------- challenger features ----------------
def _spec(cat, ref, fact, rule):
    return {"category": cat, "evidence_refs": [ref], "source_fact": fact, "rule_id": rule, "result_derived": False}


def kb4_features(date, a4):
    p = FEAT_DIR / date / "keibabook_challenger_bands.json"
    out = {}
    if not p.exists():
        return out
    d = json.loads(p.read_text())
    for kb, s in d.get("races") or []:
        v = KB_VENUE.get(kb[6:8])
        if not v:
            a4.err(f"kb4:{kb}", "UNKNOWN_KB_VENUE")
            continue
        rid = rid_of(v, date, kb[-2:])
        for item in s.split(","):
            try:
                no, trend, load, partner, listed, ready = item.split(":")
            except ValueError:
                a4.err(f"kb4:{kb}", f"BAD_ITEM:{item}")
                continue
            f = {}
            ref = f"CH:KB-BANDS:{kb}:{no}"
            m = KB_RULES["workout_load"]["map"]
            if load in m:
                f["workout_load"] = _spec(m[load], ref, f"KB load={load}", "KM-JRA-CH-KB-WORKOUT-LOAD-v1")
            m = KB_RULES["workout_partner_level"]["map"]
            if partner in m:
                f["workout_partner_level"] = _spec(m[partner], ref, f"KB partner={partner}", "KM-JRA-CH-KB-PARTNER-v1")
            c = {"UP": "STRONG", "DOWN": "CAUTION"}.get(trend)
            if trend == "FLAT":
                c = "POSITIVE" if listed.isdigit() and int(listed) >= 3 else "NEUTRAL"
            if c:
                f["workout_consistency"] = _spec(c, ref, f"KB trend={trend} listed={listed}", "KM-JRA-CH-KB-CONSISTENCY-v1")
            m = KB_RULES["stable_readiness"]["map"]
            if ready in m:
                f["stable_readiness"] = _spec(m[ready], ref, f"KB readiness={ready}", "KM-JRA-CH-KB-READINESS-v1")
            if f:
                out.setdefault(rid, {})[no] = f
    return out


def PRIVATE_BANDS(date):
    return PRIVATE / f"jra/{date}/challenger_bands"


def band_features(date, name, feature, rule):
    p = PRIVATE_BANDS(date) / name
    out = {}
    if not p.exists():
        return out
    for rid, r in (json.loads(p.read_text()).get("races") or {}).items():
        for no, cat in r["bands"].items():
            out.setdefault(rid, {})[no] = {feature: _spec(cat, f"CH:{rule}:{rid}:{r['capture']}:{no}",
                                                          f"{feature} band={cat} (capture {r['capture']})", rule)}
    return out


def equip_features(req):
    """JRA official equipment declaration (blinker). Hypothesis KM-JRA-CH-EQUIP-BLINKER-v1:
    a declared blinker is an intended improvement -> POSITIVE; no declaration -> unobserved."""
    snap = ((req.get("source_snapshot") or {}).get("jra_official_equipment_declarations") or {})
    out = {}
    if not snap.get("complete"):
        return out
    for no, r in (snap.get("runners") or {}).items():
        if (r or {}).get("blinker_declared") is True:
            out[str(no)] = {"equipment_effect": _spec("POSITIVE", f"JRA_OFFICIAL_EQUIPMENT:{req['race_id']}:{no}",
                                                      "JRA公式 馬具申告 ブリンカー着用", "KM-JRA-CH-EQUIP-BLINKER-v1")}
    return out


def load_groups(date, a4):
    return {"KB4": kb4_features(date, a4),
            "EXPERT": band_features(date, "tsl_expert_bands.json", "expert_support", "KM-JRA-CH-TSL-RECOMMEND-BAND-v1"),
            "PADDOCK": band_features(date, "kb_paddock_bands.json", "body_condition_comment", "KM-JRA-CH-KB-PADDOCK-GRADE-BAND-v1")}


# ---------------- scoring ----------------
def rank_arm(req, mapping, add, a4, arm):
    ver = B.zai_formula_version(req["race_id"])
    rows = {}
    filled = 0
    for r in req["runners"]:
        no = str(r["runner_id"])
        feats = copy.deepcopy(r.get("evidence_features") or {})
        for k, spec in (add.get(no) or {}).items():
            if not (isinstance(feats.get(k), dict) and feats[k].get("category")):
                feats[k] = spec
                filled += 1
        prof = P._profile_for_runner(r)
        vals = {}
        for idx in B.BASE:
            try:
                vals[idx] = P._weighted_index(idx, prof, feats, mapping,
                                              acquisition_failure=r.get("bvi_acquisition_failure") if idx == "BVI" else None)["value"]
            except Exception as e:
                a4.err(f"{req['race_id']}:{arm}:{no}:{idx}", e)
                vals[idx] = 50.0
        rows[no] = B.zai_win_value(vals, ver)
    order = sorted(rows, key=lambda k: (-rows[k], int(k) if k.isdigit() else k))
    return order, filled


def race_arms(rid, mapping, groups, a4):
    p = ROOT / f"runtime/requests/{rid}-LIVE-R1-FORMAL.json"
    if not p.exists():
        return None
    req = json.loads(p.read_text())
    out = {"race_id": rid, "source_request_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
           "rankings": {}, "filled_features": {}}
    groups = dict(groups, EQUIP={rid: equip_features(req)})
    for arm in ARMS:
        if arm == "PROD":
            add = {}
        elif arm == "CH_ALL":
            add = {}
            for g in GROUPS:
                for no, f in (groups[g].get(rid) or {}).items():
                    add.setdefault(no, {}).update(f)
        else:
            add = groups[arm[3:]].get(rid) or {}
        order, filled = rank_arm(req, mapping, add, a4, arm)
        out["rankings"][arm], out["filled_features"][arm] = order, filled
    # PROD replay must equal the frozen Production ZAI_WIN ranking
    led = (req.get("static_prediction") or {}).get("ranking") or []
    frozen = [str(x.get("runner_id", x)) if isinstance(x, dict) else str(x) for x in led]
    if frozen and frozen != out["rankings"]["PROD"]:
        a4.err(f"{rid}:PROD", "PROD_REPLAY_RANKING_MISMATCH")
    return out


def _report_a4(a4):
    if a4.errors:
        print(f"A4 ERROR {len(a4.errors)}")
        for e in a4.errors[:20]:
            print("  ", e)
    else:
        print("A4 OK 0")


def _mapping():
    return P.load_mapping(ROOT / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")


def cmd_freeze(a, replay=False):
    a4 = A4()
    mapping, groups, posts = _mapping(), load_groups(a.date, a4), post_times(a.date)
    now = datetime.now(JST)
    n = 0
    for p in sorted(glob.glob(str(ROOT / f"runtime/requests/KM-JRA-*-{d8(a.date)}-R*-LIVE-R1-FORMAL.json"))):
        rid = Path(p).name.replace("-LIVE-R1-FORMAL.json", "")
        post = posts.get(rid)
        if not replay:
            if not post:
                a4.err(rid, "NO_POST_TIME")
                continue
            hh, mm = map(int, post.split(":"))
            if now >= now.replace(hour=hh, minute=mm, second=0, microsecond=0):
                continue                               # too late for a forward freeze
        dst = OUT / ("replay" if replay else "forward") / rid / "pre_result.json"
        if dst.exists() and not replay:
            continue                                   # forward freezes are immutable
        before = len(a4.errors)
        try:
            row = race_arms(rid, mapping, groups, a4)
        except Exception as e:
            a4.err(rid, e)
            continue
        if not row:
            continue
        row.update({"profile": PROFILE, "kind": "KNOWN_RESULT_REPLAY_CONTEXT_ONLY" if replay else "FORWARD_PRE_RESULT",
                    "frozen_at": now.isoformat(), "post_time": post, "a4_errors": a4.errors[before:]})
        row["sha256"] = sha(row)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(row, ensure_ascii=False, indent=1))
        n += 1
    print(json.dumps({"frozen": n, "kind": "replay" if replay else "forward"}))
    _report_a4(a4)


def _top3(rid):
    p = ROOT / f"runtime/results/{rid}.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    fo = ((d.get("official_result") or {}).get("finish_order")) or d.get("finish_order")
    if not fo:
        return None
    return [str(x.get("runner_id", x) if isinstance(x, dict) else x) for x in fo[:3]]


def cmd_evaluate(a):
    kind = "replay" if a.replay else "forward"
    rows = []
    for p in sorted(glob.glob(str(OUT / kind / "*/pre_result.json"))):
        d = json.loads(Path(p).read_text())
        t = _top3(d["race_id"])
        if not t:
            continue
        mr = {arm: sum(d["rankings"][arm].index(x) + 1 for x in t if x in d["rankings"][arm]) / 3 for arm in ARMS}
        rows.append({"race_id": d["race_id"], "mean_rank": mr,
                     "winner_rank": {arm: d["rankings"][arm].index(t[0]) + 1 for arm in ARMS if t[0] in d["rankings"][arm]},
                     "filled": d["filled_features"], "a4": len(d.get("a4_errors") or []),
                     "strata": S.keys(d["race_id"], S.conditions(ROOT, d["race_id"]))})
    summ = {"kind": kind, "races": len(rows), "a4_error_races": sum(1 for r in rows if r["a4"])}
    for arm in ARMS[1:]:
        eff = [r["mean_rank"]["PROD"] - r["mean_rank"][arm] for r in rows]   # + = challenger better
        changed = sum(1 for r in rows if r["filled"].get(arm))
        sp = S.split([dict(r, strata=r["strata"]) for r in rows], lambda r, arm=arm: r["mean_rank"]["PROD"] - r["mean_rank"][arm])
        summ[arm] = {"races_with_filled_features": changed,
                     "mean_top3_rank_gain": round(sum(eff) / max(1, len(eff)), 4),
                     "venue_rule": S.venue_rule(sp)["verdict"], "venue_surface": sp["venue_surface"]}
    summ["PROD_top3_mean_rank"] = round(sum(r["mean_rank"]["PROD"] for r in rows) / max(1, len(rows)), 3)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"evaluation_{kind}.json").write_text(json.dumps({"summary": summ, "rows": rows}, ensure_ascii=False, indent=1))
    print(json.dumps(summ, ensure_ascii=False, indent=1)[:4000])


def coverage_weights(req, mapping, add):
    """Per index: mean share of the profile's mapping weight that is observed (0..1)."""
    acc = {}
    for r in req["runners"]:
        feats = dict(r.get("evidence_features") or {})
        for k, v in (add.get(str(r["runner_id"])) or {}).items():
            if not (isinstance(feats.get(k), dict) and feats[k].get("category")):
                feats[k] = v
        prof = P._profile_for_runner(r)
        for idx, w in (mapping["index_profiles"].get(prof) or {}).items():
            tot = sum(w.values()) or 1
            obs = sum(x for f, x in w.items() if isinstance(feats.get(f), dict) and feats[f].get("category"))
            acc.setdefault(idx, []).append(obs / tot)
    return {k: sum(v) / len(v) for k, v in acc.items()}


def cmd_coverage(a):
    a4 = A4()
    mapping, groups = _mapping(), load_groups(a.date, a4)
    prod, ch = {}, {}
    n = 0
    for p in sorted(glob.glob(str(ROOT / f"runtime/requests/KM-JRA-*-{d8(a.date)}-R*-LIVE-R1-FORMAL.json"))):
        req = json.loads(Path(p).read_text())
        rid = req["race_id"]
        add = {}
        for g in list(GROUPS)[:-1]:
            for no, f in (groups[g].get(rid) or {}).items():
                add.setdefault(no, {}).update(f)
        for no, f in equip_features(req).items():
            add.setdefault(no, {}).update(f)
        for dst, ad in ((prod, {}), (ch, add)):
            for k, v in coverage_weights(req, mapping, ad).items():
                dst.setdefault(k, []).append(v)
        n += 1
    rows = sorted(prod)
    lines = [f"# 指数ごとの観測重み {a.date}（{n}R、本番 → 挑戦者 CH_ALL）", "",
             "| 指数 | 本番 | 挑戦者込み | 差 |", "|---|---|---|---|"]
    out = {}
    for k in rows:
        pv, cv = sum(prod[k]) / len(prod[k]), sum(ch[k]) / len(ch[k])
        out[k] = {"production": round(pv, 3), "with_challengers": round(cv, 3)}
        lines.append(f"| {k} | {pv:.0%} | {cv:.0%} | {cv - pv:+.0%} |")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"coverage_{a.date}.md").write_text("\n".join(lines) + "\n")
    (OUT / f"coverage_{a.date}.json").write_text(json.dumps({"date": a.date, "races": n, "indices": out}, ensure_ascii=False, indent=1))
    print("\n".join(lines))
    _report_a4(a4)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("bands", "freeze", "replay", "coverage"):
        s = sub.add_parser(c)
        s.add_argument("date")
    s = sub.add_parser("evaluate")
    s.add_argument("--replay", action="store_true")
    a = ap.parse_args()
    if a.cmd == "bands":
        cmd_bands(a)
    elif a.cmd == "freeze":
        cmd_freeze(a)
    elif a.cmd == "replay":
        cmd_freeze(a, replay=True)
    elif a.cmd == "coverage":
        cmd_coverage(a)
    else:
        cmd_evaluate(a)


if __name__ == "__main__":
    main()
