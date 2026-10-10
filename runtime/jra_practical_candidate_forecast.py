"""Practical, strictly separate display of an immutable JRA Candidate forecast.

Selection is an explicitly budgeted PAPER view *over existing frozen purchased
tickets*, not a new semantic prediction, official FINAL, or Production capital
allocation. Missing evidence cannot be converted to probability/EV.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json


PROFILE = "KM-JRA-CANDIDATE-HUMAN-FORECAST-DISPLAY-v0.1-20261010"
BET_LENGTHS = {"EXACTA": 2, "TRIO": 3, "TRIFECTA": 3}


class PracticalForecastError(ValueError):
    pass


def digest(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode()).hexdigest()


def timestamp(value):
    try:
        z=datetime.fromisoformat(str(value).replace("Z","+00:00"))
        return z.astimezone(timezone.utc) if z.tzinfo else None
    except (ValueError, TypeError):
        return None


def make_forecast_brief(pre, final, *, generated_at=None,
                        maximum_paper_budget_yen=2000, max_heads=2):
    """Show selected tickets only if each existed in the frozen Candidate MEC.

    The complete frozen semantic/ticket universe remains authoritative for
    OOS measurement. This view cannot be used to claim it was the original
    capital decision, or that narrowed tickets have equivalent coverage.
    """
    if not isinstance(pre, dict) or not isinstance(final, dict):
        raise PracticalForecastError("FROZEN_CANDIDATE_INPUT_REQUIRED")
    if pre.get("sha256") != digest({k:v for k,v in pre.items() if k!="sha256"}):
        raise PracticalForecastError("FROZEN_OOS_HASH_INVALID")
    if final.get("sha256") != digest({k:v for k,v in final.items() if k!="sha256"}):
        raise PracticalForecastError("FROZEN_FINAL_HASH_INVALID")
    if (pre.get("oos_eligible") is not True
            or pre.get("candidate_final_verified") is not True
            or pre.get("acceptance_only") is True
            or pre.get("production_effect") != "NONE"):
        raise PracticalForecastError("FORWARD_CANDIDATE_UNVERIFIED")
    if (final.get("candidate_only") is not True
            or final.get("production_effect") != "NONE"
            or final.get("race_id") != pre.get("race_id")
            or final.get("source_snapshot_sha256") != pre.get("source_snapshot_sha256")
            or final.get("oos_pre_result_record_sha256") != pre.get("sha256")
            or (final.get("final_receipt") or {}).get("receipt_sha256")
               != pre.get("candidate_final_receipt_sha256")):
        raise PracticalForecastError("FROZEN_CANDIDATE_LINEAGE_INVALID")

    now=timestamp(generated_at or datetime.now(timezone.utc).isoformat())
    post=timestamp(pre.get("scheduled_post_at"))
    final_ts=timestamp(pre.get("candidate_final_receipt_timestamp"))
    if not all((now,post,final_ts)) or final_ts>=post or now<final_ts:
        raise PracticalForecastError("FORECAST_TIME_INVALID")

    if (type(maximum_paper_budget_yen) is not int
            or maximum_paper_budget_yen < 100
            or maximum_paper_budget_yen > 10000
            or maximum_paper_budget_yen % 100
            or type(max_heads) is not int or not 1<=max_heads<=3):
        raise PracticalForecastError("PAPER_DISPLAY_CAP_INVALID")

    ranking=[str(i) for i in (pre.get("ranking") or [])]
    if len(ranking)<3 or len(ranking)!=len(set(ranking)):
        raise PracticalForecastError("RANKING_UNIVERSE_INVALID")
    roles=pre.get("roles") or {}
    heads=[i for i in ranking if "W" in (roles.get(i) or [])][:max_heads]
    if not heads:
        raise PracticalForecastError("NO_FROZEN_CANDIDATE_HEADS")
    pairs={(str(x.get("head")),str(x.get("second")))
           for x in pre.get("pair_dispositions") or []
           if x.get("status")=="PURCHASE"}
    thirds={(str(x.get("head")),str(x.get("second")),str(x.get("third")))
            for x in pre.get("third_dispositions") or []
            if x.get("status")=="PURCHASE"}
    mec=final.get("mec") or {}
    original=mec.get("tickets") or []
    capital=final.get("capital") or {}
    if capital.get("no_bet") is True:
        raise PracticalForecastError("FROZEN_CANDIDATE_ORIGINAL_NO_BET")
    if not isinstance(original,list) or not original:
        raise PracticalForecastError("CANONICAL_MEC_TICKETS_MISSING")
    frozen_total=sum(int(t.get("stake",0)) for t in original)
    if (mec.get("ticket_count")!=len(original)
            or frozen_total != mec.get("minimum_required_capital")):
        raise PracticalForecastError("FROZEN_MEC_CAPITAL_MISMATCH")

    allowed=set(ranking)
    seen=set()
    candidates=[]
    for t in original:
        bet=str(t.get("bet_type") or "").upper()
        selection=tuple(str(x) for x in (t.get("selection") or []))
        stake=t.get("stake")
        if (bet not in BET_LENGTHS or len(selection)!=BET_LENGTHS[bet]
                or len(set(selection))!=len(selection)
                or not set(selection).issubset(allowed)
                or type(stake) is not int or stake<=0 or stake%100):
            raise PracticalForecastError("FROZEN_TICKET_INVALID")
        normalized=(bet, tuple(sorted(selection)) if bet=="TRIO" else selection)
        if normalized in seen:
            raise PracticalForecastError("FROZEN_DUPLICATE_TICKET")
        seen.add(normalized)
        if bet=="TRIO":
            # The unordered trio's top-ranked horse must be an actual W head;
            # existing pair and third semantics remain frozen, not recomputed.
            seq=sorted(selection,key=ranking.index)
            valid=(seq[0] in heads and
                   any(tuple(sorted((h,s,t)))==tuple(sorted(selection))
                       for h,s,t in thirds if h in heads and (h,s) in pairs))
        elif bet=="EXACTA":
            valid=(selection[0] in heads and selection in pairs)
        else:
            valid=(selection[0] in heads and selection[:2] in pairs and selection in thirds)
        if valid:
            # Display priority is a predeclared rank-order heuristic, NOT
            # win probability, EV, Kelly or proven forecast utility.
            score=sum((12 if j==0 else 4 if j==1 else 1)*ranking.index(r)
                      for j,r in enumerate(selection))
            candidates.append((score,0 if bet=="EXACTA" else 1 if bet=="TRIFECTA" else 2,
                               bet,selection,stake))

    candidates.sort(key=lambda z:(z[0],z[1],z[2],z[3]))
    # Avoid converting a wide W universe into a 20-ticket monoculture:
    # split only the visual advisory across the two leading actual W heads.
    buckets={h:[] for h in heads}
    for item in candidates:
        bet,selection=item[2:4]
        head=selection[0] if bet!="TRIO" else min(selection,key=ranking.index)
        if head in buckets:
            buckets[head].append(item)
    selected=[]
    remaining=maximum_paper_budget_yen
    while remaining>=100 and any(buckets.values()):
        progressed=False
        for head in heads:
            if remaining<100:break
            if not buckets[head]:continue
            _,__,bet,selection,original_stake=buckets[head].pop(0)
            stake=min(100,remaining,original_stake)
            if stake<100:continue
            selected.append({"bet_type":bet,"selection":list(selection),
                             "paper_stake_yen":stake,
                             "frozen_ticket_stake_yen":original_stake})
            remaining-=stake
            progressed=True
        if not progressed:break

    if not selected:
        raise PracticalForecastError("NO_VALID_BUDGETED_FROZEN_TICKETS")
    per_head={}
    for t in selected:
        first=t["selection"][0] if t["bet_type"]!="TRIO" else sorted(t["selection"],key=ranking.index)[0]
        per_head.setdefault(first,[]).append(t)
    observed=(pre.get("candidate_objective_trace") or {}).get("runners") or {}
    count_by_runner={
        rid:{
            "observed_feature_count":(observed.get(rid) or {}).get("observed_feature_count"),
            "missing_feature_count":(observed.get(rid) or {}).get("missing_feature_count"),
        } for rid in ranking[:6]
    }
    selected_total=sum(x["paper_stake_yen"] for x in selected)
    out={
        "profile":PROFILE,"race_id":pre["race_id"],
        "display_time":now.isoformat(),
        "display_temporal_class":"PRE_START_PREVIEW" if now<post else "HISTORICAL_REPRINT_ONLY",
        "original_candidate_frozen_at":pre["frozen_at"],
        "candidate_final_receipt_timestamp":pre["candidate_final_receipt_timestamp"],
        "scheduled_post_at":pre["scheduled_post_at"],
        "pre_result_sha256":pre["sha256"],
        "candidate_final_sha256":final["sha256"],
        "signed_candidate_final_receipt_sha256":pre["candidate_final_receipt_sha256"],
        "source_snapshot_sha256":pre["source_snapshot_sha256"],
        "ranking":ranking,"ranked_top6":ranking[:6],
        "candidate_primary_heads":heads,
        "market_top3":(pre.get("market_ranking") or [])[:3],
        "top6_evidence_observability":count_by_runner,
        "display_tickets_by_head":per_head,
        "display_ticket_count":len(selected),
        "display_paper_total_yen":selected_total,
        "paper_display_cap_yen":maximum_paper_budget_yen,
        "frozen_mec_ticket_count":len(original),
        "frozen_mec_capital_yen":frozen_total,
        "retained_ticket_fraction":round(len(selected)/len(original),6),
        "semantic_coverage_equivalence_claim":False,
        "winner_probability_calibrated":False,
        "ev_calibrated":False,
        "scope":"HUMAN-READABLE CANDIDATE SUBSET / PAPER ONLY / NON-PRODUCTION",
        "authority":"NON-PRODUCTION / NO AUTO-PURCHASE / NO PROMOTION",
        "production_effect":"NONE",
        "new_final_generated":False,
        "original_pre_result_mutated":False,
        "original_candidate_final_mutated":False,
    }
    out["sha256"]=digest(out)
    return out
