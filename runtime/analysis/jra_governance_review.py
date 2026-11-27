"""KAG-JRA post-result three-team review (Blue / Red / Purple), research only.

Owner request 2026-11-27 22:49 (ChatGPT KAG v1.0, 中央版 part, 「永続的に実施してください」), restoring the
2026-09 Adversarial Governance BLUE / RED / PURPLE v1.0-CANDIDATE (Candidate, not Current Authority).
Production effect NONE: post-result only, nothing here edits a FINAL, a ticket or a rule, and a
disposition is never an Owner decision. Independence: every challenge below is LEVEL-1 (deterministic
machine check on frozen originals). LEVEL-3 (another AI, e.g. the ChatGPT audit relayed by the Owner)
is recorded only when it actually took place.

Inputs per race: signed FINAL (Blue's frozen prediction: ranking, roles, tickets, KRS shadow), the
stored official result and settlement, and the pre-race frozen bands (jra_index_research
reflection_features). Hindsight is never credited to a pre-race challenge.

RED layers (pre-defined, severity fixed here, never tuned after results):
  RED-1 Evidence     FREEZE_AFTER_POST (P0), WINNER_NOT_IN_FROZEN_FIELD (P0), LOW_BAND_COVERAGE (P2)
  RED-2 Prediction   INDEPENDENT_WINNER_MISSING (winner Static rank >= 7, P1)
  RED-3 Role         TOP3_WINNER_NOT_W (P1), KRS_SIGNAL_NOT_IN_ROLE (KRS SSR-W rank <= 2 but not W, P1),
                     SECOND_NOT_P2 / THIRD_NOT_P3 (P1)
  RED-4 Decision     W_CORRECT_NO_WINNING_TICKET (P1), HIT_BUT_LOSS (P2), NO_BET_WITH_WINNER_IN_W (P2)
  RED-5 Meta         OPEN_CANDIDATES_ABOVE_CAP, RESEARCH_WITHOUT_DECISIONS (weekly, from the registries)
BLUE response (machine default, refined by the daily review session): EXISTING when a registered
candidate addresses the layer, else UNKNOWN.
PURPLE disposition (rule): P0 -> REGRESSION-ONLY; a P1 code recurring on >= 3 races of the card with
an existing candidate -> EXISTING-RULE-ABSORBED, without one -> SHADOW (propose a candidate);
otherwise NO-CHANGE. ADOPT-BEFORE-FREEZE is not available post-result.

  python runtime/analysis/jra_governance_review.py day 2026-11-28
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runtime/jra_governance"
PROFILE = "KM-JRA-KAG-POSTRESULT-v1"
SEVERITY = {"FREEZE_AFTER_POST": "P0", "WINNER_NOT_IN_FROZEN_FIELD": "P0", "LOW_BAND_COVERAGE": "P2",
            "INDEPENDENT_WINNER_MISSING": "P1", "TOP3_WINNER_NOT_W": "P1", "KRS_SIGNAL_NOT_IN_ROLE": "P1",
            "SECOND_NOT_P2": "P1", "THIRD_NOT_P3": "P1", "W_CORRECT_NO_WINNING_TICKET": "P1",
            "HIT_BUT_LOSS": "P2", "NO_BET_WITH_WINNER_IN_W": "P2"}
LAYER = {"FREEZE_AFTER_POST": "RED-1", "WINNER_NOT_IN_FROZEN_FIELD": "RED-1", "LOW_BAND_COVERAGE": "RED-1",
         "INDEPENDENT_WINNER_MISSING": "RED-2", "TOP3_WINNER_NOT_W": "RED-3", "KRS_SIGNAL_NOT_IN_ROLE": "RED-3",
         "SECOND_NOT_P2": "RED-3", "THIRD_NOT_P3": "RED-3", "W_CORRECT_NO_WINNING_TICKET": "RED-4",
         "HIT_BUT_LOSS": "RED-4", "NO_BET_WITH_WINNER_IN_W": "RED-4"}
# which research stage would absorb a recurring challenge (KIEP S1/S2/S3, KCP, KDP S4/S5)
ABSORB = {"RED-1": ("S1_CONVERSION",), "RED-2": ("S2_INDEX_FORMULA", "S3_COMPOSITE"),
          "RED-3": ("S4_ROLE",), "RED-4": ("S5_TICKET",)}


def _j(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return None


def _ts(s):
    return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00")) if s else None


def _won(t, top3):
    sel = [str(x) for x in t.get("selection") or []]
    bt = t.get("bet_type")
    if bt == "EXACTA":
        return sel == top3[:2]
    if bt == "QUINELLA":
        return set(sel) == set(top3[:2])
    if bt == "TRIFECTA":
        return sel == top3[:3]
    if bt == "TRIO":
        return set(sel) == set(top3[:3])
    if bt == "WIN":
        return sel == top3[:1]
    return False


def challenges(root, rid):
    final = _j(root / f"runtime/final_artifacts/{rid}.json")
    res = _j(root / f"runtime/results/{rid}.json")
    if not final or not res or not (res.get("official_result") or {}).get("top3"):
        return None
    top3 = [str(x) for x in res["official_result"]["top3"]]
    fp = final.get("final_prediction_package") or {}
    ranking = [str(x) for x in fp.get("ranking") or []]
    roles = {str(k): v for k, v in (fp.get("roles") or {}).items()}
    tickets = (final.get("final_ticket") or {}).get("tickets") or []
    no_bet = bool((final.get("final_ticket") or {}).get("no_bet"))
    st = res.get("settlement") or {}
    out = []

    def add(code, evidence):
        out.append({"code": code, "layer": LAYER[code], "severity": SEVERITY[code], "evidence": evidence,
                    "independence": "LEVEL-1"})

    post, fz = _ts(final.get("scheduled_post_at")), _ts(final.get("final_freeze_timestamp"))
    if post and fz and fz >= post:
        add("FREEZE_AFTER_POST", {"freeze": fz.isoformat(), "post": post.isoformat()})
    if ranking and top3[0] not in ranking:
        add("WINNER_NOT_IN_FROZEN_FIELD", {"winner": top3[0]})
    side = _j(root / f"runtime/jra_index_research/reflection_features/{rid}.json")
    if side and side.get("runners"):
        n = [len(r.get("features") or {}) for r in side["runners"].values()]
        mx = max(n) or 1
        low = sum(1 for x in n if x < 0.5 * mx)
        if low >= max(2, len(n) // 4):
            add("LOW_BAND_COVERAGE", {"runners_below_half_of_max_bands": low, "runners": len(n)})
    rank = {h: i + 1 for i, h in enumerate(ranking)}
    w = top3[0]
    if rank.get(w, 99) >= 7:
        add("INDEPENDENT_WINNER_MISSING", {"winner": w, "static_rank": rank.get(w)})
    if rank.get(w, 99) <= 3 and "W" not in roles.get(w, []):
        add("TOP3_WINNER_NOT_W", {"winner": w, "static_rank": rank[w], "roles": roles.get(w)})
    krs = {str(x["horse_no"]): (x.get("ranks") or {}).get("SSR-W") for x in
           ((final.get("krs_prediction_utility") or {}).get("summary") or [])}
    if krs.get(w) and krs[w] <= 2 and "W" not in roles.get(w, []):
        add("KRS_SIGNAL_NOT_IN_ROLE", {"winner": w, "krs_ssr_w_rank": krs[w], "static_rank": rank.get(w),
                                       "roles": roles.get(w)})
    if len(top3) > 1 and "P2" not in roles.get(top3[1], []):
        add("SECOND_NOT_P2", {"second": top3[1], "roles": roles.get(top3[1])})
    if len(top3) > 2 and "P3" not in roles.get(top3[2], []):
        add("THIRD_NOT_P3", {"third": top3[2], "roles": roles.get(top3[2])})
    in_w = "W" in roles.get(w, [])
    if no_bet:
        if in_w:
            add("NO_BET_WITH_WINNER_IN_W", {"winner": w})
    else:
        if in_w and not any(_won(t, top3) for t in tickets):
            add("W_CORRECT_NO_WINNING_TICKET", {"winner": w, "tickets": len(tickets),
                                                "bet_types": sorted({t.get("bet_type") for t in tickets})})
        inv, pay = int(st.get("effective_investment") or 0), int(st.get("total_payout") or 0)
        if 0 < pay < inv:
            add("HIT_BUT_LOSS", {"investment": inv, "payout": pay,
                                 "winning_tickets": [t.get("orientation") or t.get("selection") for t in tickets if _won(t, top3)]})
    return {"race_id": rid, "final_sha256": final.get("sha256"), "top3": top3, "challenges": out}


def _existing_stages(root):
    s = _j(root / "runtime/jra_index_research/stages_status.json") or {}
    have = set()
    for stg, items in (s.get("stages") or {}).items():
        if any(i.get("status") in ("SHADOW", "OOS_EVALUATING", "PROMOTION_ELIGIBLE") for i in items):
            have.add(stg)
    if any(i.get("status") in ("OOS_EVALUATING", "PROMOTION_ELIGIBLE") for i in s.get("S3_COMPOSITE") or []):
        have.add("S3_COMPOSITE")
    for p in s.get("downstream_prereg") or []:
        have.add(p.get("stage"))
    return have


def day(root, date):
    d8 = date.replace("-", "")
    races = [r for r in (challenges(root, Path(p).stem)
                         for p in sorted(glob.glob(str(root / f"runtime/final_artifacts/KM-JRA-*-{d8}-R*.json")))) if r]
    have = _existing_stages(root)
    counts = {}
    for r in races:
        for c in r["challenges"]:
            counts[c["code"]] = counts.get(c["code"], 0) + 1
    for r in races:
        for c in r["challenges"]:
            absorbed = [s for s in ABSORB.get(c["layer"], ()) if s in have]
            c["blue_response"] = {"response": "EXISTING" if absorbed else "UNKNOWN",
                                  "basis": absorbed or "no registered candidate for this layer",
                                  "by": "machine default; the daily review session refines it with evidence"}
            if c["severity"] == "P0":
                disp = "REGRESSION-ONLY"
            elif c["severity"] == "P1" and counts[c["code"]] >= 3:
                disp = "EXISTING-RULE-ABSORBED" if absorbed else "SHADOW"
            else:
                disp = "NO-CHANGE"
            c["purple"] = {"disposition": disp, "card_count": counts[c["code"]],
                           "authority": "research disposition only; any Production change needs the Owner"}
    summary = {"races": len(races), "challenges": sum(counts.values()), "by_code": counts,
               "by_layer": {}, "p0": sum(v for k, v in counts.items() if SEVERITY[k] == "P0"),
               "shadow_proposals": sorted({c["code"] for r in races for c in r["challenges"]
                                           if c["purple"]["disposition"] == "SHADOW"})}
    for k, v in counts.items():
        summary["by_layer"][LAYER[k]] = summary["by_layer"].get(LAYER[k], 0) + v
    out = {"profile": PROFILE, "race_date": date, "production_effect": "NONE", "independence": "LEVEL-1",
           "inherits": "Adversarial Governance BLUE / RED / PURPLE v1.0-CANDIDATE (2026-09, Candidate)",
           "summary": summary, "races": races}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{date}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("day"); a.add_argument("date")
    x = ap.parse_args()
    print(json.dumps(day(ROOT, x.date)["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
