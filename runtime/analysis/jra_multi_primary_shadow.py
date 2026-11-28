"""JRA 複系主戦 (multi-combination primary) same-budget shadow, RECORD ONLY.

Owner 2026-11-28 19:10 (ChatGPT 11/28 review: 中央版の券面が単系偏重で、正本 v1.1 の複系主戦と食い違う)
and 19:1x answer 「まず同予算で並走（推奨）」. Production effect NONE: the signed FINAL (MEC tickets,
EXACTA/TRIO/TRIFECTA only) stays the only delivered and settled ticket. Nothing here is delivered, signed,
or read by Role, MEC, Capital or Delivery. No EV / Kelly, no probability claims.

Ticket rules are fixed from the canonical spec ケイバメトリクス中央版 v1.1 before any result is seen:
  * §42 axis table (official AKI-JRA v2.1 axes in the FINAL: ASI, P-AKI) selects the 三連複 type of §39/§40
    (1-2-4, 1-2-6, 1-3-7, 1-4-8, 2-3-6, 2-4-7, 5/6-head BOX); marks ◎○▲△☆×注穴抑 = Static ranking 1..9.
  * §68 bet-type allocation of the SAME budget as the Production FINAL: 三連複 50% / 馬連 25% /
    ワイド 15% / 複勝 10% (100-yen units, largest remainder).
  * 馬連・ワイド = axis x 2nd column (two axes: the three pairs of ◎○▲; BOX: pairs of the top 4 / top 3);
    複勝 = the axis horse(s) (BOX: ◎).
Arms:
  MP-A  複系のみ (above).
  MP-B  MP-A, plus when ASI >= 80 and W-AKI <= 29 (absolute, stable head; v1.1 象限②・§67.3) one third of the
        三連複 units moves to 馬単 ◎ -> 2nd column (単系は勝ち切りの根拠がある場合だけ).
Control: the Production FINAL tickets of the same race (same budget by construction).

Freeze: before post, by the race-day loop (and the research workflow); written once per race with frozen_at.
Settlement: after the Production RESULT exists, the JRA official result page is read again for all payouts
(単勝・複勝・馬連・ワイド・馬単・3連複・3連単) and kept under runtime/jra_multi_primary/payouts/.

  python runtime/analysis/jra_multi_primary_shadow.py freeze 2026-11-29 [--now ISO]
  python runtime/analysis/jra_multi_primary_shadow.py settle [--date 2026-11-29] [--backfill N]
  python runtime/analysis/jra_multi_primary_shadow.py summary
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import itertools
import json
import math
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
OUT = ROOT / "runtime/jra_multi_primary"
PROFILE = "KM-JRA-MULTI-PRIMARY-SHADOW-v1"
PREREG = "profiles/KM_JRA_FORWARD_OOS_PREREG_20261129_MULTI_PRIMARY.json"
FIRST_ELIGIBLE = "20261129"
JST = dt.timezone(dt.timedelta(hours=9))
ALLOC = (("TRIO", 50), ("QUINELLA", 25), ("WIDE", 15), ("PLACE", 10))   # v1.1 §68
ARMS = ("MP-A", "MP-B")
FREEZE_MARGIN = dt.timedelta(minutes=1)
LABELS = {"WIN": ("単勝", 1), "PLACE": ("複勝", 1), "QUINELLA": ("馬連", 2), "WIDE": ("ワイド", 2),
          "EXACTA": ("馬単", 2), "TRIO": ("3連複", 3), "TRIFECTA": ("3連単", 3)}
UNORDERED = {"PLACE", "QUINELLA", "WIDE", "TRIO", "WIN"}


def _j(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return None


def _sha(o):
    return hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def _key(kind, sel):
    sel = [int(x) for x in sel]
    return tuple(sorted(sel)) if kind in UNORDERED else tuple(sel)


# ---------------------------------------------------------------- ticket rules (fixed 2026-11-28)

def trio_type(asi: float, paki: float) -> str:
    """v1.1 §42 axis table -> §39/§40 type. ASI 65-79 = 1頭軸または二本柱分散 (二本柱 at P-AKI 30-49 / 65+)."""
    if asi >= 80:
        return "1-2-4" if paki < 30 else "1-2-6" if paki < 50 else "1-3-7" if paki < 65 else "1-4-8"
    if asi >= 65:
        return "1-2-4" if paki < 30 else "2-3-6" if paki < 50 else "1-3-7" if paki < 65 else "2-4-7"
    if asi >= 50:
        return "2-3-6" if paki < 50 else "2-4-7"
    return "BOX5" if paki < 50 else "BOX6"


SHAPES = {"1-2-4": (1, 3, 5), "1-2-6": (1, 3, 7), "1-3-7": (1, 4, 8), "1-4-8": (1, 5, 9),
          "2-3-6": (2, 3, 6), "2-4-7": (2, 4, 7)}


def trio_columns(kind: str, h: list) -> tuple:
    """Columns as ranked horse lists (column n includes the earlier marks, as in the v1.1 examples)."""
    if kind.startswith("BOX"):
        k = int(kind[3:])
        return h[:k], h[:k], h[:k]
    a, b, c = SHAPES[kind]
    if a == 1:
        return h[:1], h[1:b], h[1:c]
    return h[:a], h[:b], h[:c]


def trio_combos(cols: tuple) -> list:
    out = set()
    for x, y, z in itertools.product(*cols):
        if len({x, y, z}) == 3:
            out.add(tuple(sorted((x, y, z), key=int)))
    return sorted(out)


def build_arm(arm: str, ranking: list, asi: float, paki: float, wak: float, budget: int) -> dict:
    h = [str(x) for x in ranking]
    rank = {x: i for i, x in enumerate(h)}
    kind = trio_type(asi, paki)
    if len(h) < 5:
        kind = "BOX%d" % min(len(h), 4) if len(h) >= 3 else None
    cols = trio_columns(kind, h) if kind else ([], [], [])
    if kind and kind.startswith("BOX"):
        k = int(kind[3:])
        axis = h[:1]
        pairs = [p for p in itertools.combinations(h[:min(k, 4)], 2)] if paki >= 50 else \
            list(itertools.combinations(h[:3], 2))
        wide = list(itertools.combinations(h[:3], 2))
    elif kind and kind[0] == "2":
        axis = h[:2]
        pairs = wide = list(itertools.combinations(h[:3], 2))
    elif kind:
        axis = h[:1]
        pairs = wide = [(h[0], y) for y in cols[1]]
    else:
        axis, pairs, wide = h[:1], [], []
    combos = {
        "TRIO": trio_combos(cols) if kind else [],
        "QUINELLA": sorted({tuple(sorted(p, key=int)) for p in pairs}, key=lambda c: sorted(rank[x] for x in c)),
        "WIDE": sorted({tuple(sorted(p, key=int)) for p in wide}, key=lambda c: sorted(rank[x] for x in c)),
        "PLACE": [(x,) for x in axis],
    }
    combos["TRIO"].sort(key=lambda c: sorted(rank[x] for x in c))
    units = budget // 100
    alloc = _allocate(units, [(k, w) for k, w in ALLOC if combos[k]])
    order_used = False
    if arm == "MP-B" and asi >= 80 and wak <= 29 and alloc.get("TRIO", 0) >= 3 and kind and kind[0] == "1":
        move = alloc["TRIO"] // 3
        alloc["TRIO"] -= move
        alloc["EXACTA"] = move
        combos["EXACTA"] = [(h[0], y) for y in cols[1]]
        order_used = True
    tickets = []
    for bt, u in alloc.items():
        tickets += _spread(bt, combos[bt], u)
    return {"arm": arm, "trio_type": kind, "axis": axis, "columns": [list(c) for c in cols],
            "units": alloc, "exacta_order_rule_fired": order_used, "tickets": tickets,
            "investment": sum(t["stake"] for t in tickets)}


def _allocate(units: int, weights: list) -> dict:
    if not weights or units <= 0:
        return {}
    tot = sum(w for _, w in weights)
    raw = [(k, units * w / tot) for k, w in weights]
    out = {k: int(math.floor(v)) for k, v in raw}
    rest = units - sum(out.values())
    for k, v in sorted(raw, key=lambda kv: (-(kv[1] - math.floor(kv[1])), [k for k, _ in weights].index(kv[0]))):
        if rest <= 0:
            break
        out[k] += 1
        rest -= 1
    return {k: v for k, v in out.items() if v > 0}


def _spread(bt: str, combos: list, units: int) -> list:
    """Each kept combination >= 100 yen; extra units go to the best-ranked combinations first."""
    if units <= 0 or not combos:
        return []
    keep = combos[:units]
    base, extra = divmod(units, len(keep))
    return [{"bet_type": bt, "selection": [int(x) for x in c], "stake": 100 * (base + (1 if i < extra else 0))}
            for i, c in enumerate(keep)]


# ---------------------------------------------------------------- freeze

def _aki(final: dict) -> dict:
    calc = ((final.get("final_prediction_package") or {}).get("official_aki_verification") or {}).get("calculation") or {}
    ax = calc.get("axes") or {}
    return {"ASI": ax.get("ASI"), "W-AKI": ax.get("W-AKI"), "P-AKI": calc.get("P-AKI_compatibility_only"),
            "version": calc.get("version")}


def build(final: dict, now: dt.datetime) -> dict:
    fp = final.get("final_prediction_package") or {}
    ranking = [str(x) for x in fp.get("ranking") or []]
    ft = final.get("final_ticket") or {}
    prod = list(ft.get("tickets") or [])
    budget = sum(int(t.get("stake") or 0) for t in prod)
    aki = _aki(final)
    rec = {"profile": PROFILE, "prereg": PREREG, "race_id": final.get("race_id"), "record_only": True,
           "production_effect": "NONE", "frozen_at": now.isoformat(timespec="seconds"),
           "post": final.get("scheduled_post_at"), "rev1_final_sha256": final.get("sha256"),
           "ranking": ranking, "aki": aki, "budget": budget,
           "production": {"tickets": [{"bet_type": t.get("bet_type"), "selection": t.get("selection"),
                                       "stake": int(t.get("stake") or 0)} for t in prod]}}
    if ft.get("no_bet") or budget <= 0:
        rec["status"] = "PRODUCTION_NO_BET_SAME_BUDGET_ZERO"
    elif None in (aki["ASI"], aki["P-AKI"], aki["W-AKI"]) or len(ranking) < 3:
        rec["status"] = "AKI_OR_RANKING_MISSING"
    else:
        rec["status"] = "FROZEN"
        rec["arms"] = {a: build_arm(a, ranking, float(aki["ASI"]), float(aki["P-AKI"]), float(aki["W-AKI"]), budget)
                       for a in ARMS}
    rec["sha256"] = _sha(rec)
    return rec


def freeze(date: str, now=None) -> list:
    now = now or dt.datetime.now(JST)
    d8 = date.replace("-", "")
    done = []
    for p in sorted((ROOT / "runtime/final_artifacts").glob(f"KM-JRA-*-{d8}-R*.json")):
        dst = OUT / date / f"{p.stem}.json"
        if dst.exists():
            continue
        final = _j(p)
        if not final or not final.get("scheduled_post_at"):
            continue
        try:
            post = dt.datetime.fromisoformat(final["scheduled_post_at"].replace("Z", "+00:00"))
        except ValueError:
            continue
        if now >= post - FREEZE_MARGIN:
            continue  # never frozen at or after post; a missed race stays missing
        rec = build(final, now)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
        done.append({"race_id": p.stem, "status": rec["status"]})
    return done


# ---------------------------------------------------------------- official payouts

def parse_all_payouts(text: str) -> dict:
    """Every JRA bet type from the official result page text (dead heats give several entries)."""
    i = text.find("払戻金")
    m = re.search(r"(?<!\S)単勝\s+\d", text[i:] if i >= 0 else text)
    if not m:
        raise ValueError("PAYOUT_TABLE_NOT_FOUND")
    tail = (text[i:] if i >= 0 else text)[m.start():].split("勝馬の紹介", 1)[0].split("ページトップへ戻る", 1)[0]
    out = {}
    names = "|".join(re.escape(v[0]) for v in LABELS.values()) + "|枠連"
    for kind, (label, n) in LABELS.items():
        hits = list(re.finditer(r"(?<!\S)" + re.escape(label) + r"\s+", tail))
        if len(hits) != 1:
            continue
        block = tail[hits[0].end():]
        stop = re.search(r"(?<!\S)(?:" + names + r")\s+", block)
        block = block[:stop.start()] if stop else block
        pat = r"((?:\d{1,2}\s*-\s*){" + str(n - 1) + r"}\d{1,2})\s+([\d,]+)\s*円"
        rows = []
        for sel, yen in re.findall(pat, block):
            nums = [int(x) for x in re.findall(r"\d+", sel)]
            if len(nums) == n and all(1 <= x <= 18 for x in nums):
                rows.append({"selection": nums, "per_100_yen": int(yen.replace(",", ""))})
        if rows:
            out[kind] = rows
    if not {"TRIO", "EXACTA", "TRIFECTA"} <= out.keys():
        raise ValueError("PAYOUT_CORE_TYPES_MISSING")
    return out


def fetch_payouts(race_id: str) -> dict:
    from jra_production_postresult import _intent_for
    from jra_candidate_postresult_closedloop import fetch_jra_result
    it = _intent_for(ROOT, race_id)
    ev = fetch_jra_result(it["race_date"], it["jra_source"]["jra_meeting_key"], int(it["race_no"]))
    return {"profile": PROFILE + "-PAYOUTS", "race_id": race_id, "source": "JRA official result (www.jra.go.jp)",
            "url": ev.get("url"), "page_sha256": ev.get("sha256"), "captured_at": ev.get("captured_at"),
            "payouts": parse_all_payouts(ev["text"])}


def _check_against_production(pay: dict, res: dict) -> bool:
    """The re-read page must agree with the Production RESULT on the three Production bet types."""
    prod = (res.get("official_result") or {}).get("payouts") or {}
    for kind in ("EXACTA", "TRIO", "TRIFECTA"):
        v = prod.get(kind)
        rows = v if isinstance(v, list) else [v] if v else []
        want = {(_key(kind, r["selection"]), int(r["per_100_yen"])) for r in rows if isinstance(r, dict)}
        got = {(_key(kind, r["selection"]), r["per_100_yen"]) for r in pay["payouts"].get(kind, [])}
        if want and want != got:
            return False
    return True


# ---------------------------------------------------------------- settlement

def settle_tickets(tickets: list, payouts: dict, refund_ids) -> dict:
    refunds = {int(x) for x in refund_ids or [] if str(x).isdigit()}
    inv = pay = ref = 0
    by = {}
    missing = sorted({t["bet_type"] for t in tickets} - payouts.keys())
    if missing:
        return {"status": "PAYOUT_UNKNOWN", "missing": missing}
    for t in tickets:
        bt, st = t["bet_type"], int(t["stake"])
        b = by.setdefault(bt, {"points": 0, "investment": 0, "payout": 0})
        if refunds & {int(x) for x in t["selection"]}:
            ref += st
            continue
        k = _key(bt, t["selection"])
        win = sum(r["per_100_yen"] for r in payouts[bt] if _key(bt, r["selection"]) == k)
        got = st // 100 * win
        inv += st; pay += got
        b["points"] += 1; b["investment"] += st; b["payout"] += got
    return {"status": "SETTLED", "investment": inv, "payout": pay, "refund": ref, "profit_loss": pay - inv,
            "pfs": round(100 * pay / inv, 2) if inv else None, "hit": pay > 0, "by_type": by}


def _git_added_at(path: Path):
    try:
        s = subprocess.check_output(["git", "log", "--diff-filter=A", "-1", "--format=%cI", "--",
                                     path.relative_to(ROOT).as_posix()], cwd=ROOT, text=True).strip()
        return dt.datetime.fromisoformat(s) if s else None
    except (subprocess.SubprocessError, OSError, ValueError):
        return None


def settle(date=None, backfill: int = 0, fetch=fetch_payouts) -> list:
    done = []
    pre_paths = sorted(OUT.glob(f"{date or '*'}/KM-JRA-*.json"))
    targets = [p.stem for p in pre_paths]
    if backfill:
        # Known-result context only: past races get their payouts so the replay can be computed.
        targets += [p.stem for p in sorted((ROOT / "runtime/final_artifacts").glob("KM-JRA-*-2026*-R*.json"))
                    if p.stem[-12:-4] >= "20261011" and not (OUT / "payouts" / f"{p.stem}.json").exists()]
    fetched = 0
    for rid in dict.fromkeys(targets):
        res = _j(ROOT / f"runtime/results/{rid}.json")
        if not res or not (res.get("official_result") or {}).get("top3"):
            continue
        pp = OUT / "payouts" / f"{rid}.json"
        if not pp.exists():
            if backfill and fetched >= backfill and rid not in {p.stem for p in pre_paths}:
                continue
            try:
                pay = fetch(rid)
            except Exception as exc:  # noqa: BLE001 - research only, retried next run
                done.append({"race_id": rid, "error": str(exc)[:160]})
                continue
            pay["agrees_with_production_result"] = _check_against_production(pay, res)
            pp.parent.mkdir(parents=True, exist_ok=True)
            pp.write_text(json.dumps(pay, ensure_ascii=False, indent=1) + "\n")
            fetched += 1
            time.sleep(0.5)
        done.append({"race_id": rid, "payouts": True})
    return done


def evaluate_race(pre: dict, pay: dict, res: dict) -> dict:
    off = res.get("official_result") or {}
    refund = off.get("refund_runner_ids") or []
    row = {"race_id": pre["race_id"], "trio_type": None, "budget": pre.get("budget")}
    if not pay.get("agrees_with_production_result", False):
        row["status"] = "PAYOUT_PAGE_DISAGREES_WITH_PRODUCTION_RESULT"
        return row
    s = res.get("settlement") or {}
    row["production"] = {"investment": s.get("total_investment"), "payout": s.get("total_payout"),
                         "pfs": s.get("pfs"), "hit": (s.get("total_payout") or 0) > 0}
    row["production_recomputed"] = settle_tickets(pre["production"]["tickets"], pay["payouts"], refund)
    for a in ARMS:
        arm = (pre.get("arms") or {}).get(a)
        if arm:
            row[a] = settle_tickets(arm["tickets"], pay["payouts"], refund)
            row[a]["trio_type"] = arm["trio_type"]
            row["trio_type"] = arm["trio_type"]
    row["top3"] = off.get("top3")
    row["status"] = "EVALUATED"
    return row


def _agg(rows: list, key: str) -> dict:
    xs = [r[key] for r in rows if (r.get(key) or {}).get("status") == "SETTLED"]
    if not xs:
        return {"races": 0}
    inv = sum(x["investment"] for x in xs); pay = sum(x["payout"] for x in xs)
    pays = sorted((x["payout"] for x in xs), reverse=True)
    cum = peak = dd = 0
    for x in xs:
        cum += x["profit_loss"]; peak = max(peak, cum); dd = min(dd, cum - peak)
    by = {}
    for x in xs:
        for bt, b in (x.get("by_type") or {}).items():
            t = by.setdefault(bt, {"points": 0, "investment": 0, "payout": 0})
            for k in t:
                t[k] += b[k]
    for t in by.values():
        t["pfs"] = round(100 * t["payout"] / t["investment"], 1) if t["investment"] else None
    return {"races": len(xs), "investment": inv, "payout": pay, "pfs": round(100 * pay / inv, 1) if inv else None,
            "pfs_excl_top1": round(100 * (pay - pays[0]) / inv, 1) if inv else None,
            "hit_races": sum(x["hit"] for x in xs), "hit_rate": round(sum(x["hit"] for x in xs) / len(xs), 3),
            "losing_hits": sum(1 for x in xs if x["hit"] and x["profit_loss"] < 0),
            "max_drawdown": dd, "by_type": by}


def _paired(rows: list, a: str, b: str) -> dict:
    d = [r[a]["profit_loss"] - r[b]["profit_loss"] for r in rows
         if (r.get(a) or {}).get("status") == "SETTLED" and (r.get(b) or {}).get("status") == "SETTLED"]
    if len(d) < 2:
        return {"races": len(d)}
    m = sum(d) / len(d)
    sd = (sum((x - m) ** 2 for x in d) / (len(d) - 1)) ** 0.5
    half = 1.96 * sd / len(d) ** 0.5
    return {"races": len(d), "mean_profit_diff_yen": round(m, 1), "ci95": [round(m - half, 1), round(m + half, 1)]}


def summary() -> dict:
    fwd, ctx = [], []
    for p in sorted(OUT.glob("20*/KM-JRA-*.json")):
        pre = _j(p)
        if not pre or pre.get("status") != "FROZEN":
            continue
        pay = _j(OUT / "payouts" / f"{p.stem}.json"); res = _j(ROOT / f"runtime/results/{p.stem}.json")
        if not pay or not res:
            continue
        row = evaluate_race(pre, pay, res)
        post = dt.datetime.fromisoformat(pre["post"].replace("Z", "+00:00"))
        added = _git_added_at(p)
        row["forward_eligible"] = (p.stem[-12:-4] >= FIRST_ELIGIBLE and
                                   dt.datetime.fromisoformat(pre["frozen_at"]) < post and
                                   (added is None or added < post))
        row["git_added_at"] = added.isoformat() if added else None
        (fwd if row["forward_eligible"] else ctx).append(row)
    # Known-result context: past FINALs rebuilt with the same fixed rules (never forward evidence).
    for p in sorted((ROOT / "runtime/final_artifacts").glob("KM-JRA-*-2026*-R*.json")):
        if p.stem[-12:-4] >= FIRST_ELIGIBLE:
            continue
        pay = _j(OUT / "payouts" / f"{p.stem}.json"); res = _j(ROOT / f"runtime/results/{p.stem}.json")
        final = _j(p)
        if not pay or not res or not final:
            continue
        pre = build(final, dt.datetime.fromisoformat(final["scheduled_post_at"]) - dt.timedelta(minutes=5))
        if pre.get("status") == "FROZEN":
            ctx.append(evaluate_race(pre, pay, res) | {"forward_eligible": False, "replay": "KNOWN_RESULT_REBUILD"})
    out = {"profile": PROFILE + "-SUMMARY", "prereg": PREREG, "production_effect": "NONE",
           "first_eligible": FIRST_ELIGIBLE,
           "forward": {k: _agg([r for r in fwd if r["status"] == "EVALUATED"], k)
                       for k in ("production_recomputed", *ARMS)},
           "forward_paired_vs_production": {a: _paired(fwd, a, "production_recomputed") for a in ARMS},
           "known_result_context_only": {k: _agg([r for r in ctx if r["status"] == "EVALUATED"], k)
                                         for k in ("production_recomputed", *ARMS)},
           "excluded": [{"race_id": r["race_id"], "status": r["status"]} for r in fwd + ctx
                        if r["status"] != "EVALUATED"],
           "forward_races": fwd}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("freeze"); f.add_argument("date"); f.add_argument("--now")
    s = sub.add_parser("settle"); s.add_argument("--date"); s.add_argument("--backfill", type=int, default=0)
    sub.add_parser("summary")
    x = ap.parse_args()
    if x.cmd == "freeze":
        print(json.dumps(freeze(x.date, dt.datetime.fromisoformat(x.now) if x.now else None), ensure_ascii=False))
    elif x.cmd == "settle":
        r = settle(x.date, x.backfill)
        errors = [e for e in r if "error" in e]
        print(json.dumps({"races": len(r), "payouts": sum(1 for e in r if e.get("payouts")),
                          "errors": len(errors), "first_errors": errors[:10]}, ensure_ascii=False))
        if errors and not any(e.get("payouts") for e in r):
            sys.exit(2)  # every fetch failed: surface it instead of a silent green run
    else:
        o = summary()
        print(json.dumps({k: o[k] for k in ("forward", "forward_paired_vs_production")}, ensure_ascii=False)[:3000])


if __name__ == "__main__":
    main()
