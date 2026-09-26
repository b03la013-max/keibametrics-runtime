from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict

PROFILE="KM-JRA-SOURCE-DERIVED-CANDIDATE-OOS-TRACKER-v0.1-20260926"

def _sha(x:Any)->str:
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()

def _dt(v):
    if not v:
        return None
    return datetime.fromisoformat(str(v).replace("Z","+00:00")).astimezone(timezone.utc)

def pre_result_record(candidate:Dict[str,Any])->Dict[str,Any]:
    mode=str(candidate.get("temporal_mode") or "")
    frozen=_dt(candidate.get("candidate_frozen_at"))
    post=_dt(candidate.get("scheduled_post_at"))
    final_ts=_dt(candidate.get("candidate_final_receipt_timestamp"))
    final_verified=candidate.get("candidate_final_verified") is True
    acceptance=bool(candidate.get("acceptance_only"))
    temporal_ok=bool(
        mode=="FORMAL-PRE-RACE"
        and not acceptance
        and frozen is not None and post is not None and frozen < post
        and final_ts is not None and final_ts < post
        and final_verified
    )
    x={
      "profile":PROFILE,
      "race_id":candidate.get("race_id"),
      "prediction_id":candidate.get("prediction_id"),
      "source_snapshot_sha256":candidate.get("source_snapshot_sha256"),
      "candidate_numerical_profile":(candidate.get("candidate_numerical_summary") or {}).get("profile"),
      "candidate_semantic_profile":(candidate.get("candidate_semantic_freeze") or {}).get("profile"),
      "candidate_semantic_freeze_sha256":(candidate.get("candidate_semantic_freeze") or {}).get("sha256"),
      "ranking":(candidate.get("static_prediction") or {}).get("ranking"),
      "roles":(candidate.get("static_prediction") or {}).get("roles"),
      "pair_dispositions":candidate.get("pair_dispositions"),
      "third_dispositions":candidate.get("third_dispositions"),
      "temporal_mode":mode,
      "scheduled_post_at":candidate.get("scheduled_post_at"),
      "frozen_at":candidate.get("candidate_frozen_at"),
      "candidate_final_receipt_sha256":candidate.get("candidate_final_receipt_sha256"),
      "candidate_final_receipt_timestamp":candidate.get("candidate_final_receipt_timestamp"),
      "candidate_final_verified":final_verified,
      "acceptance_only":acceptance,
      "production_effect":"NONE",
      "automatic_promotion":False,
      "oos_eligible":temporal_ok,
      "oos_temporal_rule":"candidate_freeze < signed_candidate_final < scheduled_post; FORMAL-PRE-RACE; not acceptance-only",
    }
    x["sha256"]=_sha(x)
    return x

def evaluate_result(record:Dict[str,Any],actual_top3:list[int])->Dict[str,Any]:
    a=[str(int(x)) for x in actual_top3]
    ranking=[str(x) for x in record.get("ranking") or []]
    roles={str(k):set(v or []) for k,v in (record.get("roles") or {}).items()}
    pairs={(str(x["head"]),str(x["second"])):x.get("status") for x in record.get("pair_dispositions") or []}
    thirds={(str(x["head"]),str(x["second"]),str(x["third"])):x.get("status") for x in record.get("third_dispositions") or []}
    out={
      "profile":PROFILE,
      "race_id":record.get("race_id"),
      "pre_result_record_sha256":record.get("sha256"),
      "actual_top3":[int(x) for x in a],
      "winner_capture":"W" in roles.get(a[0],set()),
      "p2_capture":"P2" in roles.get(a[1],set()),
      "p3_capture":"P3" in roles.get(a[2],set()),
      "ordered_pair_capture":pairs.get((a[0],a[1])) in {"PURCHASE","PROTECT"},
      "exact_capture":thirds.get((a[0],a[1],a[2])) in {"PURCHASE","PROTECT"},
      "winner_static_rank":ranking.index(a[0])+1 if a[0] in ranking else None,
      "top3_set_capture":all(x in set(ranking[:6]) for x in a),
      "oos_eligible":bool(record.get("oos_eligible")),
      "production_effect":"NONE",
      "automatic_promotion":False,
    }
    out["sha256"]=_sha(out)
    return out
