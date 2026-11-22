"""JRA information-gap challengers (research only, Owner approval 2026-11-22 17:08).

Case: KYO-20261122-R11 (Mile CS). The French-trained winner (no JRA starts, overseas
G1 winner) was frozen as career_starts=0 / newcomer=True because the JRA race card
career record reads 0.0.0.0 for foreign-trained horses. The NEWCOMER mapping then
dropped 24 domestic-only features and the DCR Art.3 rule shrank every low-coverage
index toward 50, so "information not published" became "low ability" (rank 18/18).

Arms (Production formulas, weights and mapping are NOT changed; nothing here is
delivered or bet):
  PROD        replay of the frozen Production base13 + ZAI_WIN ranking (must match FINAL)
  C1_FOREIGN  a runner whose career_starts == 0 but whose frozen features cite dated
              official pre-race history runs (JRA_OFFICIAL_HISTORY:<id>:<date>) is
              profiled by that history count (lower bound) instead of NEWCOMER.
              Classification only, no new weight.
  C2_UNCERT   an index whose acquired coverage is below the profile minimum keeps the
              acquired-feature mean (raw) instead of 50+(raw-50)*share; with no
              acquired feature it stays 50 (unknown). Uncertainty is recorded, not
              turned into rank loss.
  C12         C1 + C2.
Ranking = ZAI_WIN descending (same as Production static ranking).

Usage:
  python3 runtime/analysis/jra_info_gap_challenger.py race  KM-JRA-KYO-20261122-R11
  python3 runtime/analysis/jra_info_gap_challenger.py replay [--since 20261011]
  python3 runtime/analysis/jra_info_gap_challenger.py freeze <date>
"""
from __future__ import annotations

import argparse
import copy
import glob
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
import jra_evidence_to_base_production as P  # noqa: E402
import jra_index_provenance_builder as B  # noqa: E402

PROFILE = "KM-JRA-INFO-GAP-CHALLENGER-v1"
ARMS = ["PROD", "C1_FOREIGN", "C2_UNCERT", "C12"]
OUT = ROOT / "runtime/jra_info_gap_challenger"
HIST = re.compile(r"JRA_OFFICIAL_HISTORY(?:_[A-Z]+)?:(\w+):(\d{4}-\d{2}-\d{2})")


def sha(o) -> str:
    return hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def race_date(rid: str) -> str:
    d = re.search(r"-(\d{8})-R\d{2}", rid).group(1)
    return f"{d[:4]}-{d[4:6]}-{d[6:]}"


def history_starts(runner: dict, rdate: str) -> int:
    rid = str(runner["runner_id"])
    dates = set()
    for spec in (runner.get("evidence_features") or {}).values():
        for ref in (spec or {}).get("evidence_refs") or []:
            m = HIST.match(str(ref))
            if m and m.group(1) == rid and m.group(2) < rdate:
                dates.add(m.group(2))
    return len(dates)


def _c2_mapping(mapping: dict) -> dict:
    m = copy.deepcopy(mapping)
    for p in m["profiles"].values():
        p["minimum_index_coverage_weight"] = 1e-9   # covered>0 -> raw mean; covered==0 -> 50
    return m


def arm_values(req: dict, mapping: dict, arm: str) -> dict:
    rdate = race_date(req["race_id"])
    m = _c2_mapping(mapping) if arm in ("C2_UNCERT", "C12") else mapping
    ver = B.zai_formula_version(req["race_id"])
    out = {}
    for r in req["runners"]:
        r = copy.deepcopy(r)
        flagged = False
        if arm in ("C1_FOREIGN", "C12") and int(r.get("career_starts") or 0) == 0:
            n = history_starts(r, rdate)
            if n > 0:
                r["career_starts"], r["newcomer"], flagged = n, False, True
        prof = P._profile_for_runner(r)
        vals, low = {}, []
        for idx in B.BASE:
            c = P._weighted_index(idx, prof, r["evidence_features"], m,
                                  acquisition_failure=r.get("bvi_acquisition_failure") if idx == "BVI" else None)
            vals[idx] = c["value"]
            if c.get("information_status"):
                low.append(idx)
        out[str(r["runner_id"])] = {"profile": prof, "foreign_history_profiled": flagged,
                                    "zai_win": B.zai_win_value(vals, ver), "base": vals,
                                    "low_coverage_indices": low}
    order = sorted(out, key=lambda k: (-out[k]["zai_win"], int(k) if k.isdigit() else k))
    for i, k in enumerate(order, 1):
        out[k]["rank"] = i
    return {"ranking": order, "runners": out}


def load(rid: str):
    p = ROOT / f"runtime/requests/{rid}-LIVE-R1-FORMAL.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def frozen_check(req: dict, prod: dict) -> int:
    """Production replay must equal the frozen ledger base values."""
    led = (req.get("index_provenance_ledger") or {}).get("runners") or {}
    bad = 0
    for rid, row in prod["runners"].items():
        fb = (led.get(rid) or {}).get("base_indices") or {}
        for idx, v in row["base"].items():
            if idx in fb and abs(float(fb[idx]["value"]) - v) > 1e-6:
                bad += 1
    return bad


def top3(rid: str):
    p = ROOT / f"runtime/results/{rid}.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    fo = ((d.get("official_result") or {}).get("finish_order")) or d.get("finish_order")
    if not fo:
        return None
    return [str(x.get("runner_id", x) if isinstance(x, dict) else x) for x in fo[:3]]


def race(rid: str, mapping: dict, with_result=True) -> dict | None:
    req = load(rid)
    if req is None or not req.get("runners"):
        return None
    arms = {a: arm_values(req, mapping, a) for a in ARMS}
    row = {"race_id": rid, "formula_mismatch": frozen_check(req, arms["PROD"]),
           "foreign_profiled": sorted(k for k, v in arms["C1_FOREIGN"]["runners"].items()
                                      if v["foreign_history_profiled"]),
           "rankings": {a: arms[a]["ranking"] for a in ARMS}}
    if with_result:
        t = top3(rid)
        if t:
            row["top3"] = t
            row["winner_rank"] = {a: arms[a]["runners"][t[0]]["rank"] for a in ARMS if t[0] in arms[a]["runners"]}
            row["top3_mean_rank"] = {a: sum(arms[a]["runners"][x]["rank"] for x in t if x in arms[a]["runners"]) / 3
                                     for a in ARMS}
            row["winner_in_top3"] = {a: row["winner_rank"].get(a, 99) <= 3 for a in ARMS}
    return row, arms


def cmd_race(a, mapping):
    row, arms = race(a.race_id, mapping)
    print(json.dumps({k: v for k, v in row.items() if k != "rankings"}, ensure_ascii=False))
    for arm in ARMS:
        print(arm, " ".join(arms[arm]["ranking"]))
    for k in row["foreign_profiled"] or []:
        for arm in ARMS:
            x = arms[arm]["runners"][k]
            print(f"  runner {k} {arm}: profile={x['profile']} rank={x['rank']} zai_win={x['zai_win']:.2f} "
                  f"low={x['low_coverage_indices']}")


def cmd_replay(a, mapping):
    rows = []
    for p in sorted(glob.glob(str(ROOT / "runtime/requests/KM-JRA-*-LIVE-R1-FORMAL.json"))):
        rid = Path(p).name.replace("-LIVE-R1-FORMAL.json", "")
        if race_date(rid).replace("-", "") < a.since:
            continue
        try:
            r = race(rid, mapping)
        except Exception as e:  # keep going; record the failure
            rows.append({"race_id": rid, "error": str(e)[:200]})
            continue
        if r:
            rows.append(r[0])
    ev = [r for r in rows if "top3" in r]
    summ = {"races": len(rows), "with_result": len(ev),
            "errors": sum(1 for r in rows if "error" in r),
            "formula_mismatch_races": sum(1 for r in rows if r.get("formula_mismatch")),
            "foreign_profiled_races": [r["race_id"] for r in rows if r.get("foreign_profiled")]}
    for arm in ARMS:
        summ[arm] = {
            "top3_mean_rank": round(sum(r["top3_mean_rank"][arm] for r in ev) / max(1, len(ev)), 3),
            "winner_in_top3_pct": round(100 * sum(r["winner_in_top3"][arm] for r in ev) / max(1, len(ev)), 1),
            "winner_mean_rank": round(sum(r["winner_rank"].get(arm, 0) for r in ev) / max(1, len(ev)), 3),
        }
    out = {"profile": PROFILE, "kind": "KNOWN_RESULT_REPLAY_CONTEXT_ONLY_NOT_OOS", "since": a.since,
           "summary": summ, "rows": rows}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"replay_since_{a.since}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps(summ, ensure_ascii=False, indent=1))


def cmd_freeze(a, mapping):
    d8 = a.date.replace("-", "")
    n = 0
    for p in sorted(glob.glob(str(ROOT / f"runtime/requests/KM-JRA-*-{d8}-R*-LIVE-R1-FORMAL.json"))):
        rid = Path(p).name.replace("-LIVE-R1-FORMAL.json", "")
        dst = OUT / "forward" / rid / "pre_result.json"
        if dst.exists():
            continue   # immutable once frozen
        r = race(rid, mapping, with_result=False)
        if not r:
            continue
        rec = {"profile": PROFILE, "race_id": rid, "rankings": r[0]["rankings"],
               "foreign_profiled": r[0]["foreign_profiled"], "formula_mismatch": r[0]["formula_mismatch"],
               "source_request_sha256": hashlib.sha256(Path(p).read_bytes()).hexdigest()}
        rec["sha256"] = sha(rec)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(rec, ensure_ascii=False, indent=1))
        n += 1
    print(json.dumps({"frozen": n}))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("race"); s.add_argument("race_id")
    s = sub.add_parser("replay"); s.add_argument("--since", default="20261011")
    s = sub.add_parser("freeze"); s.add_argument("date")
    a = ap.parse_args()
    mapping = P.load_mapping(ROOT / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")
    {"race": cmd_race, "replay": cmd_replay, "freeze": cmd_freeze}[a.cmd](a, mapping)


if __name__ == "__main__":
    main()
