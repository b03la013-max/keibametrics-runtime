from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

PROFILE="KM-LOCAL-NUMERICAL-CANDIDATE-WALKFORWARD-v0.1-20260923"


class WalkForwardError(ValueError):
    pass


def _sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def _parse(s):
    if not s: return None
    s=str(s).replace("Z","+00:00")
    x=dt.datetime.fromisoformat(s)
    if x.tzinfo is None: x=x.replace(tzinfo=dt.timezone.utc)
    return x.astimezone(dt.timezone.utc)


def _rank_of(ranking, horse):
    try: return [str(x) for x in ranking].index(str(horse))+1
    except ValueError: return None


def evaluate(events: List[Dict[str,Any]], *, minimum_for_review: int=30) -> Dict[str,Any]:
    if not isinstance(events,list):
        raise WalkForwardError("EVENTS_LIST_REQUIRED")
    rows=[]
    seen=set()
    last_freeze=None
    for ev in sorted(events,key=lambda x:str(x.get("prediction_frozen_at") or "")):
        rid=str(ev.get("race_id") or "")
        if not rid or rid in seen: raise WalkForwardError("RACE_ID_INVALID_OR_DUPLICATE:"+rid)
        seen.add(rid)
        frozen=_parse(ev.get("prediction_frozen_at"))
        result_at=_parse(ev.get("result_available_at"))
        if frozen is None or result_at is None or not frozen<result_at:
            raise WalkForwardError("TEMPORAL_ORDER_INVALID:"+rid)
        if last_freeze and frozen<last_freeze:
            raise WalkForwardError("WALKFORWARD_ORDER_INVALID:"+rid)
        last_freeze=frozen
        pred=ev.get("candidate_prediction") or {}
        ranking=pred.get("ranking") or []
        W=set(map(str,pred.get("W") or [])); P2=set(map(str,pred.get("P2") or [])); P3=set(map(str,pred.get("P3") or []))
        actual=list(map(str,ev.get("actual_top3") or []))
        if len(actual)!=3: raise WalkForwardError("ACTUAL_TOP3_REQUIRED:"+rid)
        wr=_rank_of(ranking,actual[0]); p2r=_rank_of(ranking,actual[1]); p3r=_rank_of(ranking,actual[2])
        top3r=[_rank_of(ranking,x) for x in actual]
        row={
          "race_id":rid,
          "prediction_frozen_at":frozen.isoformat(),
          "result_available_at":result_at.isoformat(),
          "winner_rank":wr,"second_rank":p2r,"third_rank":p3r,
          "winner_capture":actual[0] in W,
          "p2_capture":actual[1] in P2,
          "p3_capture":actual[2] in P3,
          "top3_set_capture":all(x in P3 for x in actual),
          "top3_mean_rank":None if any(x is None for x in top3r) else sum(top3r)/3,
          "candidate_mapping_id":ev.get("candidate_mapping_id"),
          "source_snapshot_sha256":ev.get("source_snapshot_sha256"),
          "result_derived_feature_count":int(ev.get("result_derived_feature_count",0)),
        }
        if row["result_derived_feature_count"]!=0:
            raise WalkForwardError("RESULT_DERIVED_FEATURE_CONTAMINATION:"+rid)
        rows.append(row)

    n=len(rows)
    def rate(k): return None if n==0 else sum(bool(r[k]) for r in rows)/n
    winner_ranks=[r["winner_rank"] for r in rows if r["winner_rank"] is not None]
    mean_top3=[r["top3_mean_rank"] for r in rows if r["top3_mean_rank"] is not None]
    summary={
      "profile":PROFILE,
      "event_count":n,
      "winner_capture_rate":rate("winner_capture"),
      "p2_capture_rate":rate("p2_capture"),
      "p3_capture_rate":rate("p3_capture"),
      "top3_set_capture_rate":rate("top3_set_capture"),
      "mean_winner_rank":None if not winner_ranks else sum(winner_ranks)/len(winner_ranks),
      "mean_top3_mean_rank":None if not mean_top3 else sum(mean_top3)/len(mean_top3),
      "minimum_for_human_promotion_review":minimum_for_review,
      "promotion_review_ready":n>=minimum_for_review,
      "automatic_promotion":False,
      "status":"REVIEW_REQUIRED" if n>=minimum_for_review else "WAITING_R30",
      "rows":rows,
      "policy":"Time-ordered measurements only. This harness never trains on or rewrites the same race it scores."
    }
    summary["sha256"]=_sha(summary)
    return summary


def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("events_json")
    p.add_argument("--out")
    a=p.parse_args()
    events=json.load(open(a.events_json,encoding="utf-8"))
    result=evaluate(events)
    s=json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)
    if a.out: Path(a.out).write_text(s,encoding="utf-8")
    else: print(s)


if __name__=="__main__":
    main()
